"""
Complete Example: User Management Integration in streamlit_app.py

This file shows how to integrate the user management system into your app.
Copy the relevant sections into your streamlit_app.py
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

# Configuration
import config
from user_stats_ui import (
    render_safe_blank_page,
    render_user_profile,
    render_watch_history,
    render_subscriber_features,
    render_users_list_page,
    demo_user_activity,
    get_user_manager
)

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_app():
    """Initialize app with session state"""
    st.set_page_config(
        page_title="Stream & Upload Hub with Users",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'uploaded_videos' not in st.session_state:
        st.session_state.uploaded_videos = []
    if 'streams' not in st.session_state:
        st.session_state.streams = []


# ============================================================================
# MAIN APP STRUCTURE
# ============================================================================

def main():
    """Main application entry point"""
    initialize_app()
    
    # Check if user is logged in
    if st.session_state.user_id is None:
        # Show safe blank page (login/signup)
        render_safe_blank_page()
    else:
        # Show main navigation
        show_main_app()


def show_main_app():
    """Show main app after user login"""
    user_id = st.session_state.user_id
    manager = get_user_manager()
    user = manager.get_user(user_id)
    
    # Sidebar header
    st.sidebar.title("🎬 Stream & Upload Hub")
    st.sidebar.write(f"**{user['username']}** ({user['role'].upper()})")
    st.sidebar.write(f"📧 {user['email']}")
    
    # Main navigation
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Profile",
            "Watch History",
            "Features",
            "Upload Video",
            "Live Stream",
            "Users Admin",
            "Activity Demo"
        ]
    )
    
    # Route to page
    if page == "Dashboard":
        page_dashboard(user_id, manager)
    elif page == "Profile":
        page_profile(user_id, manager)
    elif page == "Watch History":
        page_watch_history(user_id, manager)
    elif page == "Features":
        page_features(user_id, manager)
    elif page == "Upload Video":
        page_upload_video(user_id, manager)
    elif page == "Live Stream":
        page_live_stream(user_id, manager)
    elif page == "Users Admin":
        page_users_admin(manager)
    elif page == "Activity Demo":
        page_activity_demo(user_id, manager)
    
    # Sidebar footer - logout
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user_id = None
        st.rerun()


# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

def page_dashboard(user_id: str, manager):
    """Dashboard homepage"""
    # Enhanced title with HTML
    st.markdown("""
    <h1 style='text-align: center; font-size: 4em; margin: 30px 0; background: linear-gradient(to right, #FF6B6B, #FF8E72); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>
    📊 Dashboard
    </h1>
    """, unsafe_allow_html=True)
    
    # Quick stats
    stats = manager.get_user_stats(user_id)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Videos", stats.videos_uploaded)
    with col2:
        st.metric("Streams", stats.streams_created)
    with col3:
        st.metric("Images", stats.images_uploaded)
    with col4:
        st.metric("Watch Hrs", f"{stats.total_watched_hours:.1f}")
    with col5:
        st.metric("Interactions", stats.total_interactions)
    
    st.divider()
    
    # Featured content
    st.markdown("### 🎥 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📤 Upload Video"):
            st.session_state.page = "Upload Video"
            st.rerun()
    with col2:
        if st.button("🔴 Start Stream"):
            st.session_state.page = "Live Stream"
            st.rerun()
    with col3:
        if st.button("👥 View Users"):
            st.session_state.page = "Users Admin"
            st.rerun()


# ============================================================================
# PAGE: PROFILE
# ============================================================================

def page_profile(user_id: str, manager):
    """User profile page"""
    st.title("👤 Profile")
    render_user_profile(user_id)


# ============================================================================
# PAGE: WATCH HISTORY
# ============================================================================

def page_watch_history(user_id: str, manager):
    """Watch history page"""
    st.title("📺 Watch History")
    render_watch_history(user_id)


# ============================================================================
# PAGE: SUBSCRIBER FEATURES
# ============================================================================

def page_features(user_id: str, manager):
    """Features and subscription page"""
    st.title("⭐ Features & Subscription")
    render_subscriber_features(user_id)


# ============================================================================
# PAGE: UPLOAD VIDEO
# ============================================================================

def page_upload_video(user_id: str, manager):
    """Upload video page"""
    st.title("📤 Upload Video")
    
    user = manager.get_user(user_id)
    
    st.write(f"**Uploading as:** {user['username']}")
    
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=list(config.ALLOWED_VIDEO_EXTENSIONS)
    )
    
    if uploaded_file:
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size / (1024*1024):.2f} MB")
        
        title = st.text_input("Video Title")
        description = st.text_area("Description")
        
        if st.button("Upload"):
            # Save file
            upload_dir = config.UPLOAD_DIR
            upload_dir.mkdir(exist_ok=True)
            
            file_path = upload_dir / uploaded_file.name
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Record upload activity
            manager.record_upload(user_id, "video")
            
            # Add to session
            st.session_state.uploaded_videos.append({
                "name": uploaded_file.name,
                "path": str(file_path),
                "size": uploaded_file.size,
                "title": title,
                "description": description,
                "uploaded_at": datetime.now().isoformat(),
                "uploaded_by": user_id
            })
            
            st.success(f"✅ Video '{title}' uploaded successfully!")
            st.info("Your upload has been recorded in your statistics.")


# ============================================================================
# PAGE: LIVE STREAM
# ============================================================================

def page_live_stream(user_id: str, manager):
    """Live stream page with camera access"""
    st.title("🔴 Live Stream")
    
    user = manager.get_user(user_id)
    st.write(f"**Streaming as:** {user['username']}")
    
    # Create tabs for setup and preview
    tab1, tab2, tab3 = st.tabs(["📹 Camera Feed", "⚙️ Stream Settings", "📊 Stream Info"])
    
    # TAB 1: CAMERA FEED
    with tab1:
        st.markdown("### 📹 Camera Preview")
        
        # Camera access
        camera_col, preview_col = st.columns([1, 1])
        
        with camera_col:
            st.markdown("**Capture from Webcam:**")
            picture = st.camera_input("Take a picture")
            
            if picture:
                st.success("✅ Camera frame captured!")
                st.image(picture, caption="Live Camera Feed")
        
        with preview_col:
            st.markdown("**Stream Status:**")
            if "stream_active" not in st.session_state:
                st.session_state.stream_active = False
            
            stream_status = "🟢 LIVE" if st.session_state.stream_active else "⚫ OFFLINE"
            st.metric("Status", stream_status)
            
            if st.session_state.stream_active:
                st.info("📡 Broadcasting to audience...")
            else:
                st.warning("📡 Stream not active. Configure and start below.")
    
    # TAB 2: STREAM SETTINGS
    with tab2:
        st.markdown("### ⚙️ Stream Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stream_name = st.text_input("Stream Name", placeholder="My Awesome Stream")
            resolution = st.selectbox("Resolution", config.SUPPORTED_RESOLUTIONS)
            st.caption("Camera output quality")
        
        with col2:
            stream_desc = st.text_area("Description", placeholder="Describe your stream...")
            bitrate = st.selectbox("Bitrate", config.SUPPORTED_BITRATES)
            st.caption("Video bitrate for streaming")
        
        st.divider()
        
        # Stream controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🟢 Start Stream", use_container_width=True, key="start_stream"):
                if stream_name:
                    # Record stream creation
                    manager.record_upload(user_id, "stream")
                    
                    # Add to streams
                    stream_info = {
                        "id": f"stream_{len(st.session_state.streams)}",
                        "name": stream_name,
                        "description": stream_desc,
                        "resolution": resolution,
                        "bitrate": bitrate,
                        "started_at": datetime.now().isoformat(),
                        "status": "active",
                        "created_by": user_id
                    }
                    st.session_state.streams.append(stream_info)
                    st.session_state.stream_active = True
                    
                    st.success("✅ Stream started!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Please enter a stream name")
        
        with col2:
            if st.button("⏸️ Pause Stream", use_container_width=True, key="pause_stream"):
                if st.session_state.stream_active:
                    st.session_state.stream_active = False
                    st.info("⏸️ Stream paused")
                    st.rerun()
        
        with col3:
            if st.button("⏹️ End Stream", use_container_width=True, key="stop_stream"):
                if st.session_state.stream_active:
                    st.session_state.stream_active = False
                    st.info("✅ Stream ended")
                    st.rerun()
    
    # TAB 3: STREAM INFO
    with tab3:
        st.markdown("### 📊 Stream Statistics")
        
        if st.session_state.streams:
            latest_stream = st.session_state.streams[-1]
            
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                st.metric("Stream Name", latest_stream.get("name", "N/A"))
            
            with metric_col2:
                st.metric("Resolution", latest_stream.get("resolution", "N/A"))
            
            with metric_col3:
                st.metric("Bitrate", latest_stream.get("bitrate", "N/A"))
            
            with metric_col4:
                st.metric("Status", latest_stream.get("status", "N/A").upper())
            
            st.divider()
            
            # Description
            st.markdown("**Stream Description:**")
            st.write(latest_stream.get("description", "No description provided"))
            
            st.markdown("**Stream ID:**")
            st.code(latest_stream.get("id", "N/A"))
        else:
            st.info("No active streams yet. Create one in the Stream Settings tab!")



# ============================================================================
# PAGE: USERS ADMIN
# ============================================================================

def page_users_admin(manager):
    """Users administration page"""
    render_users_list_page()


# ============================================================================
# PAGE: ACTIVITY DEMO
# ============================================================================

def page_activity_demo(user_id: str, manager):
    """Activity demo for testing"""
    st.title("🎬 Activity Demo")
    st.write("Simulate user activities to test the statistics system.")
    
    demo_user_activity(user_id)
    
    # Show updated stats after demo
    st.divider()
    st.markdown("### Current Statistics")
    
    stats = manager.get_user_stats(user_id)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Videos Uploaded", stats.videos_uploaded)
    with col2:
        st.metric("Watch Hours", f"{stats.total_watched_hours:.1f}")
    with col3:
        st.metric("Interactions", stats.total_interactions)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()


# ============================================================================
# OPTIONAL: ADDITIONAL FEATURES
# ============================================================================

"""
Additional features that can be added:

1. ANALYTICS CHARTS
   - import plotly.express as px
   - Create charts for statistics trends
   - Show most watched content
   - Display user engagement over time

2. CONTENT RECOMMENDATIONS
   - Based on watch history
   - Suggested for similar interests
   - Popular in user's category

3. EXPORT FUNCTIONALITY
   - Export stats to CSV
   - Download watch history
   - Generate reports

4. ADVANCED FILTERING
   - Filter users by role
   - Filter by subscription status
   - Filter by date range
   - Search by username

5. BULK OPERATIONS
   - Send messages to subscribers
   - Bulk upgrade users
   - Export analytics data
   - Schedule tasks

6. NOTIFICATIONS
   - New upload alerts
   - Stream going live alerts
   - Achievement unlocked alerts
   - Subscription expiring alerts

7. PAYMENT INTEGRATION
   - Stripe payment processor
   - Subscription billing
   - Invoice generation
   - Refund handling

8. API ENDPOINTS
   - REST API for mobile apps
   - Webhook for external services
   - GraphQL query interface
   - Rate limiting
"""
