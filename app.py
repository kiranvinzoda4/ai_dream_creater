# app.py
import streamlit as st
from session_manager import init_session, is_logged_in, logout_user
from auth import authenticate, register_user
from characters import create_character, get_characters, delete_character
from dreams import create_dream, get_dreams
import base64

st.set_page_config(page_title="AI Dream Creator", layout="centered", page_icon="🌙")

init_session()

if is_logged_in():
    user = st.session_state.user
    
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🌙 AI Dream Creator")
    with col2:
        if st.button("🚪 Logout", type="secondary"):
            logout_user()
            st.rerun()
    
    # Tabs for Profile, Characters, and Dreams
    tab1, tab2, tab3 = st.tabs(["👤 Profile", "🎭 Characters", "🌙 Dreams"])
    
    with tab1:
        st.subheader(f"Welcome, {user['name']}! 👋")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Member since:** {user.get('created_at', 'Today')}")
    
    with tab2:
        st.subheader("Manage Your Characters")
        
        # Add new character
        with st.expander("➕ Add New Character", expanded=False):
            with st.form("character_form", clear_on_submit=True):
                char_name = st.text_input("Character Name", placeholder="e.g., Me, My Brother, Iron Man")
                char_desc = st.text_area("Description", placeholder="Describe the character...")
                
                st.write("Upload up to 3 images:")
                img1 = st.file_uploader("Image 1", type=["jpg", "jpeg", "png"], key="img1")
                img2 = st.file_uploader("Image 2", type=["jpg", "jpeg", "png"], key="img2")
                img3 = st.file_uploader("Image 3", type=["jpg", "jpeg", "png"], key="img3")
                
                submitted = st.form_submit_button("Create Character", type="primary")
                
                if submitted:
                    if char_name:
                        images = [img for img in [img1, img2, img3] if img]
                        if images:
                            if create_character(user['email'], char_name, char_desc, images):
                                st.success(f"Character '{char_name}' created!")
                                st.rerun()
                            else:
                                st.error("Failed to create character")
                        else:
                            st.warning("Please upload at least one image")
                    else:
                        st.warning("Please enter a character name")
        
        st.divider()
        
        # Display characters
        characters = get_characters(user['email'])
        
        if characters:
            for char in characters:
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.subheader(char['name'])
                        if char.get('description'):
                            st.write(char['description'])
                        
                        # Display images from S3
                        if char.get('image_urls'):
                            cols = st.columns(min(len(char['image_urls']), 3))
                            for idx, img_url in enumerate(char['image_urls'][:3]):
                                with cols[idx]:
                                    st.image(img_url, width='stretch')
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{char['character_id']}"):
                            if delete_character(user['email'], char['character_id']):
                                st.success("Deleted!")
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("No characters yet. Create your first character above!")
    
    with tab3:
        st.subheader("Create Dream Videos")
        
        characters = get_characters(user['email'])
        
        if characters:
            with st.expander("✨ Create New Dream", expanded=False):
                with st.form("dream_form", clear_on_submit=True):
                    char_names = {char['name']: char for char in characters}
                    selected_char_name = st.selectbox("Select Character", list(char_names.keys()))
                    selected_char = char_names[selected_char_name]
                    
                    if selected_char.get('image_urls'):
                        st.write("Character images:")
                        cols = st.columns(min(len(selected_char['image_urls']), 3))
                        for idx, img_url in enumerate(selected_char['image_urls'][:3]):
                            with cols[idx]:
                                st.image(img_url, width='stretch')
                        
                        selected_img_idx = st.radio(
                            "Select image for video", 
                            range(len(selected_char['image_urls'])), 
                            format_func=lambda x: f"Image {x+1}"
                        )
                    else:
                        st.error("Selected character has no images!")
                        selected_img_idx = 0
                    
                    dream_prompt = st.text_input("Dream Prompt (optional)", placeholder="e.g., walking in forest", max_chars=100)
                    st.info("Video: 2 sec, 360p, 12fps (low cost) with Nova Reel")
                    
                    submitted = st.form_submit_button("Generate Dream Video", type="primary")
                    
                    if submitted:
                        if selected_char.get('image_urls'):
                            with st.spinner("Creating your dream... This may take a minute..."):
                                success, dream_id = create_dream(
                                    user['email'], 
                                    selected_char['character_id'], 
                                    dream_prompt, 
                                    selected_img_idx
                                )
                                if success:
                                    st.success(f"Dream created! Dream ID: {dream_id}")
                                    st.rerun()
                                else:
                                    st.error("Failed to create dream. Please try again.")
                        else:
                            st.error("Character has no images to create video!")
            
            st.divider()
            st.subheader("Dream History")
            
            dreams = get_dreams(user['email'])
            
            if dreams:
                for dream in sorted(dreams, key=lambda x: x.get('created_at', ''), reverse=True):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Prompt:** {dream.get('prompt', 'No prompt')}")
                            st.write(f"**Created:** {dream.get('created_at')}")
                            
                            status = dream.get('status', 'unknown')
                            if status == 'completed':
                                st.success("✅ Completed")
                                if dream.get('video_url'):
                                    st.video(dream['video_url'])
                            elif status == 'processing':
                                st.info("⏳ Processing...")
                            else:
                                st.error("❌ Failed")
                        
                        with col2:
                            st.write(f"**Status:** {status}")
                        
                        st.divider()
            else:
                st.info("No dreams yet. Create your first dream above!")
        else:
            st.warning("Please create at least one character first!")
    
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
        
        if st.button("Create Account", type="primary", use_container_width=True):
            if name and email and password:
                if register_user(name, email, password):
                    st.success("Account created! Please login.")
                    st.balloons()
                else:
                    st.error("Email already exists")
            else:
                st.warning("Please fill all fields")