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
    """
    เชื่อมต่อฐานข้อมูล MySQL (Aiven / defaultdb)
    """
    try:
        port_int = int(st.secrets["database"]["port"])
        conn = pymysql.connect(
            host=st.secrets["database"]["host"],
            port=port_int,
            user=st.secrets["database"]["user"],
            password=st.secrets["database"]["password"],
            database="defaultdb",  # ใช้ defaultdb ตาม schema ของคุณ
            cursorclass=DictCursor,
            connect_timeout=10,
            ssl={}
        )
        return conn
    except Exception as e:
        raise e

# --- 3. RUN QUERY ---
def run_query(query, params=None, commit=False, fetch_one=False, fetch_all=False):
    conn = init_connection()
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
    except pymysql.IntegrityError as e:
        if "Duplicate entry" in str(e):
            st.error("ข้อมูลซ้ำ (username หรือ email มีอยู่แล้ว)")
        else:
            st.error(f"MySQL Integrity Error: {e}")
        return None
    except Exception as e:
        st.error(f"MySQL Error: {e}")
        return None

# --- 4. HASH PASSWORD ---
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_login(username, password):
    hashed_pw = make_hash(password)
    comp = run_query(
        "SELECT * FROM Company WHERE c_username=%s AND c_password_hash=%s",
        (username, hashed_pw), fetch_one=True)
    if comp:
        return "Company", comp
    seeker = run_query(
        "SELECT * FROM JobSeeker WHERE js_username=%s AND js_password_hash=%s",
        (username, hashed_pw), fetch_one=True)
    if seeker:
        return "JobSeeker", seeker
    return None, None

# --- 5. LOGIN / REGISTER PAGE ---
def login_register_page():
    st.title("Job Application System")
    tab1, tab2 = st.tabs(["เข้าสู่ระบบ", "ลงทะเบียน"])

    with tab1:
        st.write("### Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("เข้าสู่ระบบ"):
            role, user = check_login(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.session_state.user_info = user
                st.toast(f"Login สำเร็จ! ยินดีต้อนรับ {username}")
                time.sleep(1); st.rerun()
            else:
                st.error("Username หรือ Password ไม่ถูกต้อง")

    with tab2:
        st.write("### Register")
        user_type = st.selectbox("คุณคือใคร?", ["ผู้หางาน", "บริษัท"])
        if user_type == "บริษัท":
            with st.form("reg_company"):
                c_user = st.text_input("Username *")
                c_pass = st.text_input("Password *", type="password")
                c_name = st.text_input("ชื่อบริษัท *")
                c_email = st.text_input("Email *")
                c_addr = st.text_area("ที่อยู่")
                c_contact = st.text_input("เบอร์ติดต่อ")
                if st.form_submit_button("ลงทะเบียน"):
                    if c_user and c_pass and c_name and c_email:
                        sql = """
                            INSERT INTO Company 
                            (c_username, c_password_hash, c_name, c_email, c_address, c_contact_info) 
                            VALUES (%s,%s,%s,%s,%s,%s)
                        """
                        if run_query(sql, (c_user, make_hash(c_pass), c_name, c_email, c_addr, c_contact), commit=True):
                            st.success("ลงทะเบียนบริษัทสำเร็จ! กรุณาเข้าสู่ระบบ")
                    else:
                        st.warning("กรุณากรอกช่อง * ให้ครบ")
        else:
            with st.form("reg_seeker"):
                j_user = st.text_input("Username *")
                j_pass = st.text_input("Password *", type="password")
                j_name = st.text_input("ชื่อ-นามสกุล *")
                j_email = st.text_input("Email *")
                j_edu = st.text_input("ระดับการศึกษา")
                j_skill = st.text_area("ทักษะ (Skills)")
                j_exp = st.text_area("ประสบการณ์")
                if st.form_submit_button("ลงทะเบียน"):
                    if j_user and j_pass and j_name and j_email:
                        sql = """
                            INSERT INTO JobSeeker 
                            (js_username, js_password_hash, js_full_name, js_email, js_education, js_skills, js_experience)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """
                        if run_query(sql, (j_user, make_hash(j_pass), j_name, j_email, j_edu, j_skill, j_exp), commit=True):
                            st.success("ลงทะเบียนผู้หางานสำเร็จ! กรุณาเข้าสู่ระบบ")
                    else:
                        st.warning("กรุณากรอกช่อง * ให้ครบ")

# --- 6. MAIN APP ---
def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_register_page()
    else:
        user = st.session_state.user_info
        role = st.session_state.user_role
        st.sidebar.header(f"บัญชีผู้ใช้: {role}")
        st.sidebar.write(f"สวัสดี, **{user.get('c_username') or user.get('js_username')}**")
        if st.sidebar.button("ออกจากระบบ"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.user_info = None
            st.rerun()
        st.write("คุณเข้าสู่ระบบเรียบร้อยแล้ว!")

if __name__ == "__main__":
    main()
