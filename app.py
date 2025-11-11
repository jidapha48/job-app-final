import streamlit as st
import pymysql
from pymysql.cursors import DictCursor
import hashlib
import time
import datetime

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(
    page_title="Job Application System",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- 2. DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    try:
        port_int = int(st.secrets["database"]["port"])
        return pymysql.connect(
            host=st.secrets["database"]["host"],
            port=port_int,
            user=st.secrets["database"]["user"],
            password=st.secrets["database"]["password"],
            database=st.secrets["database"]["database"],
            cursorclass=DictCursor,
            connect_timeout=10,
            ssl={}
        )
    except Exception as e:
        raise e

# --- 3. RUN QUERY FUNCTION ---
def run_query(query, params=None, commit=False, fetch_one=False, fetch_all=False):
    conn = init_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                if commit:
                    conn.commit()
                    return True
                elif fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
            return True
        except pymysql.Error as e:
            st.error(f"Database Error: {e}")
            return None
        finally:
            conn.close()
    return None

# --- 4. UTILITIES ---
def make_hash(password):
    return hashlib.sha256(str(password).encode()).hexdigest()

def check_login(username, password):
    hashed_pw = make_hash(password)
    comp = run_query("SELECT * FROM Company WHERE c_username=%s AND c_password_hash=%s", (username, hashed_pw), fetch_one=True)
    if comp: return "Company", comp
    seeker = run_query("SELECT * FROM JobSeeker WHERE js_username=%s AND js_password_hash=%s", (username, hashed_pw), fetch_one=True)
    if seeker: return "JobSeeker", seeker
    return None, None

def set_login_view(view):
    st.session_state.login_view = view

# --- 5. LOGIN & REGISTER PAGES ---
def login_register_page():
    st.title("Job Application System")
    tab1, tab2 = st.tabs(["เข้าสู่ระบบ (Login)", "ลงทะเบียน (Register)"])

    # --- Login Tab ---
    with tab1:
        if st.session_state.login_view == 'login':
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("เข้าสู่ระบบ"):
                role, user = check_login(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_role'] = role
                    st.session_state['user_info'] = user
                    st.toast(f"Login สำเร็จ! ยินดีต้อนรับ {username}")
                    time.sleep(1); st.rerun()
                else:
                    st.error("Username หรือ Password ไม่ถูกต้อง")
            st.button("ลืม Username?", on_click=set_login_view, args=['forgot_username'])

        elif st.session_state.login_view == 'forgot_username':
            email = st.text_input("กรอกอีเมลเพื่อค้นหา Username")
            if st.button("ค้นหา"):
                username_found = None
                comp = run_query("SELECT c_username FROM Company WHERE c_email=%s", (email,), fetch_one=True)
                if comp: username_found = comp['c_username']
                else:
                    seeker = run_query("SELECT js_username FROM JobSeeker WHERE js_email=%s", (email,), fetch_one=True)
                    if seeker: username_found = seeker['js_username']
                if username_found:
                    st.success(f"Username ของคุณคือ: {username_found}")
                else:
                    st.error("ไม่พบ Username ที่ผูกกับอีเมลนี้")
            st.button("กลับไปหน้า Login", on_click=set_login_view, args=['login'])

    # --- Register Tab ---
    with tab2:
        user_type = st.selectbox("คุณคือใคร?", ["ผู้หางาน (Job Seeker)", "บริษัท (Company)"])
        if user_type == "บริษัท (Company)":
            with st.form("reg_company"):
                c_user = st.text_input("Username *")
                c_pass = st.text_input("Password *", type="password")
                c_name = st.text_input("ชื่อบริษัท *")
                c_email = st.text_input("Email *")
                c_addr = st.text_area("ที่อยู่")
                c_contact = st.text_input("เบอร์ติดต่อ")
                if st.form_submit_button("ยืนยันการลงทะเบียน"):
                    if c_user and c_pass and c_name and c_email:
                        existing = run_query("SELECT * FROM Company WHERE c_username=%s OR c_email=%s", (c_user, c_email), fetch_one=True)
                        if existing:
                            st.error("Username หรือ Email ถูกใช้งานแล้ว")
                        else:
                            sql = "INSERT INTO Company (c_username, c_password_hash, c_name, c_email, c_address, c_contact_info) VALUES (%s,%s,%s,%s,%s,%s)"
                            if run_query(sql, (c_user, make_hash(c_pass), c_name, c_email, c_addr, c_contact), commit=True):
                                st.success("ลงทะเบียนบริษัทสำเร็จ! กรุณาเข้าสู่ระบบ")
                    else:
                        st.warning("กรุณากรอกช่องที่มีเครื่องหมาย * ให้ครบ")
        else:
            with st.form("reg_seeker"):
                j_user = st.text_input("Username *")
                j_pass = st.text_input("Password *", type="password")
                j_name = st.text_input("ชื่อ-นามสกุล *")
                j_email = st.text_input("Email *")
                j_edu = st.text_input("ระดับการศึกษา")
                j_skills = st.text_area("ทักษะ (Skills)")
                j_exp = st.text_area("ประสบการณ์")
                if st.form_submit_button("ยืนยันการลงทะเบียน"):
                    if j_user and j_pass and j_name and j_email:
                        existing = run_query("SELECT * FROM JobSeeker WHERE js_username=%s OR js_email=%s", (j_user, j_email), fetch_one=True)
                        if existing:
                            st.error("Username หรือ Email ถูกใช้งานแล้ว")
                        else:
                            sql = "INSERT INTO JobSeeker (js_username, js_password_hash, js_full_name, js_email, js_education, js_skills, js_experience) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                            if run_query(sql, (j_user, make_hash(j_pass), j_name, j_email, j_edu, j_skills, j_exp), commit=True):
                                st.success("ลงทะเบียนผู้หางานสำเร็จ! กรุณาเข้าสู่ระบบ")
                    else:
                        st.warning("กรุณากรอกช่องที่มีเครื่องหมาย * ให้ครบ")

# --- MAIN APP ---
def main():
    if 'login_view' not in st.session_state:
        st.session_state.login_view = 'login'
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_register_page()
    else:
        user, role = st.session_state.user_info, st.session_state.user_role
        st.sidebar.header(f"บัญชีผู้ใช้: {role}")
        st.sidebar.write(f"สวัสดี, **{user.get('c_username') or user.get('js_username')}**")
        st.sidebar.divider()
        page_options = ["Dashboard", "แก้ไขข้อมูลส่วนตัว"]
        page = st.sidebar.radio("เมนู", page_options)
        st.sidebar.divider()
        if st.sidebar.button("ออกจากระบบ"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.user_info = None
            st.session_state.login_view = 'login'
            st.rerun()

        if page == "Dashboard":
            if role == "Company":
                st.write("บริษัท Dashboard")  # ต่อเติม company_dashboard(user) ได้
            else:
                st.write("ผู้หางาน Dashboard")  # ต่อเติม seeker_dashboard(user) ได้
        else:
            st.write("แก้ไขข้อมูลส่วนตัว")  # ต่อเติม edit_profile_page(user, role) ได้

if __name__ == '__main__':
    main()
