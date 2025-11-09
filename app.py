import streamlit as st
import mysql.connector
import hashlib
import pandas as pd
import time

# --- 1. CONFIG & DATABASE CONNECTION ---
st.set_page_config(page_title="Job Application Platform", page_icon="💼", layout="wide")

@st.cache_resource
def init_connection():
    """เชื่อมต่อฐานข้อมูลและ cache ไว้"""
    try:
        return mysql.connector.connect(**st.secrets["database"])
    except Exception as e:
        st.error(f"ไม่สามารถเชื่อมต่อฐานข้อมูลได้: {e}")
        return None

def run_query(query, params=None, fetch_all=True):
    """ฟังก์ชันช่วยในการรัน Query"""
    conn = init_connection()
    if not conn: return None
    
    # ตรวจสอบสถานะการเชื่อมต่อ ถ้าหลุดให้ต่อใหม่
    if not conn.is_connected():
        conn.reconnect()

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params)
        if query.strip().upper().startswith(("SELECT", "SHOW")):
            result = cursor.fetchall() if fetch_all else cursor.fetchone()
            return result
        else:
            conn.commit() # สำหรับ INSERT, UPDATE, DELETE
            return cursor.rowcount
    except mysql.connector.Error as e:
        st.error(f"Database Error: {e}")
        return None
    finally:
        cursor.close()

# --- 2. AUTHENTICATION FUNCTIONS ---
def hash_password(password):
    """เข้ารหัสรหัสผ่านด้วย SHA256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def login_user(username, password, user_type):
    """ตรวจสอบข้อมูล Login จากฐานข้อมูล"""
    pwd_hash = hash_password(password)
    
    if user_type == "company":
        query = "SELECT * FROM Company WHERE c_username = %s AND c_password_hash = %s"
        user = run_query(query, (username, pwd_hash), fetch_all=False)
    else: # job_seeker
        query = "SELECT * FROM JobSeeker WHERE js_username = %s AND js_password_hash = %s"
        user = run_query(query, (username, pwd_hash), fetch_all=False)
        
    return user

# --- 3. PAGE VIEWS ---
def login_page():
    st.title("🔐 เข้าสู่ระบบ")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/5087/5087579.png", width=150)
        
    with col2:
        user_type_option = st.radio("ประเภทผู้ใช้งาน", ["ผู้สมัครงาน (Job Seeker)", "บริษัท (Company)"])
        user_type = "company" if "บริษัท" in user_type_option else "job_seeker"
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
        if submit:
            if username and password:
                with st.spinner("กำลังตรวจสอบข้อมูล..."):
                    user = login_user(username, password, user_type)
                    time.sleep(0.5) # ใส่ delay เล็กน้อยให้ดูเหมือนมีการประมวลผล
                    
                if user:
                    # บันทึก Session
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.session_state['user_type'] = user_type
                    st.success("เข้าสู่ระบบสำเร็จ!")
                    st.rerun()
                else:
                    st.error("Username หรือ Password ไม่ถูกต้อง")
            else:
                st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

def company_dashboard(user):
    st.title(f"🏢 ยินดีต้อนรับ, {user['c_name']}")
    st.write(f"📍 ที่อยู่: {user['c_address']}")
    
    tab1, tab2 = st.tabs(["ประกาศงานของคุณ", "สร้างประกาศงานใหม่"])
    
    with tab1:
        st.subheader("📋 ตำแหน่งงานที่เปิดรับ")
        query = "SELECT * FROM JobPost WHERE j_company_id = %s ORDER BY j_post_date DESC"
        jobs = run_query(query, (user['c_id'],))
        if jobs:
            df = pd.DataFrame(jobs)
            # เลือกเฉพาะคอลัมน์ที่น่าสนใจมาแสดง
            st.dataframe(
                df[['j_position', 'j_post_date', 'j_closing_date']], 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("คุณยังไม่มีประกาศงาน")
            
    with tab2:
        st.subheader("✍️ สร้างประกาศงาน")
        with st.form("new_job_form"):
            position = st.text_input("ชื่อตำแหน่ง (Position)")
            desc = st.text_area("รายละเอียดงาน (Description)")
            req = st.text_area("คุณสมบัติ (Requirements)")
            closing_date = st.date_input("วันปิดรับสมัคร")
            
            if st.form_submit_button("ลงประกาศ"):
                query = """
                    INSERT INTO JobPost (j_company_id, j_position, j_description, j_requirements, j_post_date, j_closing_date)
                    VALUES (%s, %s, %s, %s, CURDATE(), %s)
                """
                res = run_query(query, (user['c_id'], position, desc, req, closing_date), fetch_all=False)
                if res:
                    st.success("ลงประกาศงานสำเร็จ!")
                    time.sleep(1)
                    st.rerun()

def job_seeker_dashboard(user):
    st.title(f"👨‍💻 ยินดีต้อนรับ, {user['js_full_name']}")
    st.info(f"ทักษะของคุณ: {user.get('js_skills', '-')}")

    st.subheader("🔎 งานที่เปิดรับสมัครทั้งหมด")
    
    # ดึงข้อมูลงานพร้อมชื่อบริษัท (JOIN Table)
    query = """
        SELECT j.*, c.c_name 
        FROM JobPost j
        JOIN Company c ON j.j_company_id = c.c_id
        WHERE j.j_closing_date >= CURDATE() OR j.j_closing_date IS NULL
        ORDER BY j.j_post_date DESC
    """
    jobs = run_query(query)
    
    if jobs:
        for job in jobs:
            with st.expander(f"📌 {job['j_position']} @ {job['c_name']}"):
                st.write(f"**รายละเอียด:** {job['j_description']}")
                st.write(f"**คุณสมบัติ:** {job['j_requirements']}")
                st.caption(f"ประกาศเมื่อ: {job['j_post_date']} | ปิดรับ: {job['j_closing_date']}")
                
                # ปุ่มสมัครงาน (ตัวอย่างเบื้องต้น)
                if st.button("สมัครงานนี้", key=f"apply_{job['j_id']}"):
                    # (ในอนาคต) เพิ่มโค้ด INSERT ลงตาราง Application ตรงนี้
                    st.toast("ส่งใบสมัครเรียบร้อย! (Demo)", icon="✅")
    else:
        st.warning("ขณะนี้ยังไม่มีงานที่เปิดรับ")

# --- 4. MAIN APP CONTROLLER ---
def main():
    # ตรวจสอบ Session State เริ่มต้น
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Sidebar สำหรับ Logout
    if st.session_state['logged_in']:
        with st.sidebar:
            st.write(f"User: {st.session_state['user'].get('c_username') or st.session_state['user'].get('js_username')}")
            if st.button("Log out", type="primary", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

    # Router เลือกหน้าที่จะแสดง
    if not st.session_state['logged_in']:
        login_page()
    else:
        # Logged in แล้ว แยกไปตามประเภทผู้ใช้
        if st.session_state['user_type'] == 'company':
            company_dashboard(st.session_state['user'])
        else:
            job_seeker_dashboard(st.session_state['user'])

if __name__ == "__main__":
    main()
