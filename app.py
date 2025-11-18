# app.py
import streamlit as st
from session_manager import init_session, is_logged_in, logout_user
from auth import authenticate, register_user

st.set_page_config(page_title="AI Dream Creator", layout="centered", page_icon="🌙")

init_session()

if is_logged_in():
    # Profile Page
    st.title("👤 Your Profile")
    
    user = st.session_state.user
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Welcome, {user['name']}! 👋")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Member since:** {user.get('created_at', 'Today')}")
    
    with col2:
        if st.button("🚪 Logout", type="secondary"):
            logout_user()
            st.rerun()
    
    st.divider()
    st.subheader("🌙 Dream Settings")
    st.info("Dream generation features coming soon!")
    
else:
    # Login/Register Page
    st.title("🌙 AI Dream Creator")
    st.markdown("*Create and explore your dreams with AI*")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Welcome Back")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if email and password:
                user = authenticate(email, password)
                if user:
                    from session_manager import login_user
                    login_user(user)
                    st.success("Welcome back!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                st.warning("Please fill all fields")
    
    with tab2:
        st.subheader("Join Us")
        name = st.text_input("Full Name", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        print(email)
        print(password)
        if st.button("Create Account", type="primary", use_container_width=True):
            if name and email and password:
                if register_user(name, email, password):
                    st.success("Account created! Please login.")
                    st.balloons()
                else:
                    st.error("Email already exists")
            else:
                st.warning("Please fill all fields")