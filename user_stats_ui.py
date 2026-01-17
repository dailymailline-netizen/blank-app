"""
User Management & Statistics UI Components for Streamlit
Safe blank page for user onboarding with comprehensive stats display
"""

import streamlit as st
from pathlib import Path
from typing import Optional, List, Dict
from user_stats import UserManager, UserRole, SubscriberFeature, WatchHistoryEntry
from config import USERS_DIR, USERS_HISTORY_DIR
import time


@st.cache_resource
def get_user_manager() -> UserManager:
    """Cached user manager instance (singleton)"""
    return UserManager(USERS_DIR, USERS_HISTORY_DIR)


def render_safe_blank_page():
    """
    Render safe blank page for first-time users
    Clean, welcoming introduction to the platform
    """
    st.set_page_config(page_title="Welcome - Stream & Upload Hub", layout="wide")
    
    # Header
    st.markdown(
        """
        <style>
        .welcome-header {
            text-align: center;
            padding: 40px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 40px;
        }
        .welcome-header h1 {
            margin: 0;
            font-size: 48px;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🎬 Welcome to Stream & Upload Hub")
        st.markdown("---")
    
    # Introduction
    st.markdown("""
    ### Your All-in-One Video & Streaming Platform
    
    **Stream & Upload Hub** is a comprehensive platform for creating, sharing, and managing video content.
    Whether you're a casual creator or a professional streamer, we've got everything you need.
    """)
    
    # Create two columns for getting started
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Upload Videos")
        st.write("""
        - Upload multiple video formats
        - Automatic transcoding
        - Organize with metadata
        - Add descriptions and tags
        """)
    
    with col2:
        st.markdown("### 🔴 Go Live")
        st.write("""
        - Create live streams
        - Customize stream settings
        - Share with community
        - Track stream analytics
        """)
    
    st.divider()
    
    # User registration section
    st.markdown("### Get Started Today")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Create Account")
        username = st.text_input("Choose Username", key="signup_username")
        email = st.text_input("Email Address", key="signup_email")
        
        if st.button("Create Free Account", key="signup_btn"):
            if username and email:
                manager = get_user_manager()
                user_id = manager.create_user(username, email, UserRole.FREE)
                st.success(f"✅ Welcome {username}! Account created.")
                st.info(f"Your User ID: `{user_id}`")
                st.session_state.user_id = user_id
                time.sleep(2)
                st.rerun()
            else:
                st.error("Please fill in all fields")
    
    with col1:
        st.markdown("#### Already Have Account?")
        existing_user_id = st.text_input("Enter Your User ID", key="login_userid")
        
        if st.button("Login", key="login_btn"):
            if existing_user_id:
                manager = get_user_manager()
                user = manager.get_user(existing_user_id)
                if user:
                    st.success(f"✅ Welcome back {user['username']}!")
                    st.session_state.user_id = existing_user_id
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("User ID not found")
            else:
                st.error("Please enter your User ID")
    
    # Features overview
    st.divider()
    st.markdown("### Platform Features")
    
    features = {
        "🎥 Video Management": "Upload, organize, and manage your video library",
        "🔴 Live Streaming": "Create and manage live streams with real-time analytics",
        "👥 Community": "Share content with community members",
        "📊 Analytics": "Track views, engagement, and subscriber growth",
        "🎨 Customization": "Personalize your profile and streams",
        "⭐ Premium": "Unlock exclusive features with subscription"
    }
    
    cols = st.columns(3)
    for idx, (feature, description) in enumerate(features.items()):
        with cols[idx % 3]:
            st.markdown(f"**{feature}**")
            st.caption(description)


def render_user_profile(user_id: str):
    """Render user profile and dashboard"""
    manager = get_user_manager()
    user = manager.get_user(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    # Header with user info
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("### 👤 Profile")
    with col2:
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Email:** {user['email']}")
    with col3:
        role_emoji = {"free": "🟢", "subscriber": "⭐", "premium": "👑", "admin": "🔑"}
        role = user['role']
        st.write(f"{role_emoji.get(role, '🔷')} **{role.upper()}**")
    
    st.divider()
    
    # 8-Point Statistics Display
    render_8_point_stats(user_id, manager)


def render_8_point_stats(user_id: str, manager: UserManager):
    """Render the 8-point statistics system"""
    stats = manager.get_user_stats(user_id)
    history_tracker = manager.history_tracker
    
    st.markdown("### 📊 Your Statistics")
    
    # Display 8 stats in 2 rows of 4
    metrics = [
        ("Subscriber\nFeatures Used", stats.subscriber_features_used, "⭐"),
        ("Watch\nHistory Entries", stats.watch_history_entries, "📺"),
        ("Total Watched\nHours", f"{stats.total_watched_hours:.1f}h", "⏱️"),
        ("Videos\nUploaded", stats.videos_uploaded, "🎥"),
        ("Streams\nCreated", stats.streams_created, "🔴"),
        ("Images\nUploaded", stats.images_uploaded, "🖼️"),
        ("Total\nInteractions", stats.total_interactions, "💬"),
        ("Last\nActivity", stats.last_activity_timestamp[:10], "⏰"),
    ]
    
    cols = st.columns(4)
    for idx, (label, value, emoji) in enumerate(metrics):
        with cols[idx % 4]:
            st.metric(f"{emoji} {label}", value)
    
    st.divider()


def render_watch_history(user_id: str):
    """Render watch history viewer"""
    manager = get_user_manager()
    history = manager.history_tracker.get_watch_history(user_id, limit=50)
    stats = manager.history_tracker.get_watch_stats_by_type(user_id)
    
    st.markdown("### 📺 Watch History")
    
    # Statistics by content type
    if stats:
        st.markdown("**Breakdown by Content Type:**")
        cols = st.columns(len(stats))
        for idx, (content_type, data) in enumerate(stats.items()):
            with cols[idx]:
                st.metric(
                    f"{content_type.capitalize()}",
                    f"{data['count']} views",
                    f"Avg: {data['avg_duration']}s"
                )
    
    st.divider()
    
    # Watch history table
    if history:
        st.markdown(f"**Recent Watches ({len(history)})**")
        
        history_data = []
        for entry in history:
            history_data.append({
                "Date": entry.watched_at[:10],
                "Time": entry.watched_at[11:16],
                "Type": entry.content_type,
                "Duration (min)": round(entry.duration_seconds / 60, 1),
                "Quality": entry.quality,
                "Completed": "✅" if entry.completed else "⏸️"
            })
        
        st.dataframe(history_data, use_container_width=True)
        
        # Clear history button
        if st.button("🗑️ Clear Watch History"):
            manager.history_tracker.clear_watch_history(user_id)
            st.success("Watch history cleared")
            st.rerun()
    else:
        st.info("No watch history yet. Start watching content!")


def render_subscriber_features(user_id: str):
    """Display available subscriber features"""
    manager = get_user_manager()
    user = manager.get_user(user_id)
    features = manager.subscriber_features.get(user_id, [])
    
    st.markdown("### ⭐ Subscriber Features")
    
    role = user['role']
    
    if role == "free":
        st.info("""
        **Upgrade to Subscriber to unlock premium features:**
        - Priority uploads
        - HD streaming (1080p)
        - Ad-free experience
        - Custom playlists
        """)
        if st.button("🚀 Upgrade to Subscriber"):
            manager.upgrade_subscription(user_id, UserRole.SUBSCRIBER)
            st.success("Subscription upgraded!")
            st.rerun()
    else:
        st.write(f"**{role.upper()} Features Enabled:**")
        
        feature_descriptions = {
            SubscriberFeature.CUSTOM_BRANDING: "Custom channel branding",
            SubscriberFeature.PRIORITY_UPLOAD: "Priority upload queue",
            SubscriberFeature.ADVANCED_ANALYTICS: "Advanced analytics dashboard",
            SubscriberFeature.HD_STREAMING: "HD streaming (up to 1080p)",
            SubscriberFeature.AD_FREE: "Ad-free experience",
            SubscriberFeature.EARLY_ACCESS: "Early access to features",
            SubscriberFeature.CUSTOM_PLAYLISTS: "Unlimited custom playlists",
            SubscriberFeature.BULK_OPERATIONS: "Bulk content operations"
        }
        
        cols = st.columns(2)
        for idx, feature in enumerate(features):
            with cols[idx % 2]:
                st.success(f"✓ {feature_descriptions.get(feature, feature.value)}")


def render_users_list_page():
    """
    Render comprehensive users page with:
    - User list
    - Stats overview
    - Possible additional stats to track
    - User management controls
    """
    st.set_page_config(page_title="Users - Stream & Upload Hub", layout="wide")
    st.title("👥 Users & Statistics")
    
    manager = get_user_manager()
    
    # Tab 1: All Users
    tab1, tab2, tab3, tab4 = st.tabs([
        "All Users",
        "Subscribers",
        "Analytics",
        "Possible Stats"
    ])
    
    with tab1:
        render_users_table(manager)
    
    with tab2:
        render_subscribers_section(manager)
    
    with tab3:
        render_analytics_dashboard(manager)
    
    with tab4:
        render_possible_stats_list()


def render_users_table(manager: UserManager):
    """Display table of all users"""
    st.markdown("### All Users")
    
    users = manager.get_active_users()
    
    if users:
        user_data = []
        for user in users:
            stats = manager.get_user_stats(user['user_id'])
            user_data.append({
                "Username": user['username'],
                "Email": user['email'],
                "Role": user['role'].upper(),
                "Joined": user['created_at'][:10],
                "Videos": stats.videos_uploaded if stats else 0,
                "Streams": stats.streams_created if stats else 0,
                "Watch Hrs": round(stats.total_watched_hours, 1) if stats else 0,
                "Last Active": stats.last_activity_timestamp[:10] if stats else "Never"
            })
        
        st.dataframe(user_data, use_container_width=True)
        st.info(f"Total Users: {len(users)}")
    else:
        st.info("No users yet")


def render_subscribers_section(manager: UserManager):
    """Display subscriber statistics"""
    st.markdown("### Subscriber Statistics")
    
    subscribers = manager.get_subscribers()
    all_users = manager.get_active_users()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", len(all_users))
    with col2:
        st.metric("Subscribers", len(subscribers))
    with col3:
        percentage = (len(subscribers) / len(all_users) * 100) if all_users else 0
        st.metric("Subscription Rate", f"{percentage:.1f}%")
    
    st.divider()
    
    if subscribers:
        st.markdown("**Active Subscribers:**")
        sub_data = []
        for user in subscribers:
            stats = manager.get_user_stats(user['user_id'])
            sub_data.append({
                "Username": user['username'],
                "Role": user['role'].upper(),
                "Features": len(manager.subscriber_features.get(user['user_id'], [])),
                "Expires": user.get('subscription_expires', 'N/A')[:10],
                "Watch Hours": round(stats.total_watched_hours, 1) if stats else 0
            })
        
        st.dataframe(sub_data, use_container_width=True)


def render_analytics_dashboard(manager: UserManager):
    """Render analytics dashboard"""
    st.markdown("### Platform Analytics")
    
    all_users = manager.get_active_users()
    all_stats = manager.get_all_users_stats()
    
    if all_stats:
        # Calculate aggregates
        total_videos = sum(s.videos_uploaded for s in all_stats.values())
        total_streams = sum(s.streams_created for s in all_stats.values())
        total_images = sum(s.images_uploaded for s in all_stats.values())
        total_interactions = sum(s.total_interactions for s in all_stats.values())
        total_watched = sum(s.total_watched_hours for s in all_stats.values())
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🎥 Total Videos", total_videos)
        with col2:
            st.metric("🔴 Total Streams", total_streams)
        with col3:
            st.metric("🖼️ Total Images", total_images)
        with col4:
            st.metric("💬 Interactions", total_interactions)
        with col5:
            st.metric("⏱️ Hours Watched", f"{round(total_watched, 0):.0f}")
        
        st.divider()
        
        # Top users
        st.markdown("**Top Users by Activity:**")
        top_users = sorted(
            all_stats.items(),
            key=lambda x: x[1].total_watched_hours,
            reverse=True
        )[:10]
        
        top_data = []
        for user_id, stats in top_users:
            user = manager.get_user(user_id)
            top_data.append({
                "Username": user['username'],
                "Videos": stats.videos_uploaded,
                "Streams": stats.streams_created,
                "Watch Hrs": round(stats.total_watched_hours, 1),
                "Interactions": stats.total_interactions
            })
        
        st.dataframe(top_data, use_container_width=True)


def render_possible_stats_list():
    """
    Display list of possible statistics that could be tracked
    Comprehensive list for future implementation
    """
    st.markdown("### 📋 Possible Statistics to Track")
    
    st.info("""
    **Current 8 Main Stats:**
    1. Subscriber Features Used ⭐
    2. Watch History Entries 📺
    3. Total Watched Hours ⏱️
    4. Videos Uploaded 🎥
    5. Streams Created 🔴
    6. Images Uploaded 🖼️
    7. Total Interactions 💬
    8. Last Activity Timestamp ⏰
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 Additional Stats for Future Implementation")
    
    possible_stats = {
        "👁️ Watch Engagement": [
            "Peak watch time (when most users watch)",
            "Average watch duration (minutes)",
            "Video completion rate (%)",
            "Rewatch count per video",
            "Favorite content categories"
        ],
        "🔴 Streaming Analytics": [
            "Average concurrent viewers",
            "Peak viewer count",
            "Total stream duration (hours)",
            "Stream frequency (streams per week)",
            "Viewer retention rate (%)",
            "Average stream quality preference"
        ],
        "📊 Content Performance": [
            "Most viewed content (top 10)",
            "Trending content tags",
            "Average content rating",
            "Content quality preference (360p/720p/1080p)",
            "Download count per video",
            "Share count per video"
        ],
        "👥 Social Engagement": [
            "Comments count",
            "Likes count",
            "Shares count",
            "Followers gained",
            "Following count",
            "Collaborative projects (co-hosted streams)"
        ],
        "💾 Storage & Bandwidth": [
            "Total storage used (GB)",
            "Monthly bandwidth used (GB)",
            "Storage utilization (%)",
            "Largest file uploaded",
            "Oldest content (days)",
            "Backup status"
        ],
        "📈 Growth Metrics": [
            "Subscriber growth per month",
            "Engagement growth trend",
            "Video upload frequency trend",
            "Audience size growth",
            "Revenue from subscriptions",
            "Referral count (users invited)"
        ],
        "⏰ Usage Patterns": [
            "Average session duration (minutes)",
            "Sessions per week",
            "Most active day of week",
            "Most active hour of day",
            "Login streak (days)",
            "Days since last login"
        ],
        "🎨 Customization & Preferences": [
            "Custom playlists created",
            "Playlist average size",
            "Theme preference",
            "Notification settings",
            "Privacy settings changes",
            "Content recommendations clicked"
        ],
        "🏆 Achievements & Gamification": [
            "Badges earned",
            "Milestones reached",
            "Streaks (consecutive days active)",
            "Achievement points",
            "Leaderboard position",
            "Level/rank attained"
        ]
    }
    
    for category, stats in possible_stats.items():
        with st.expander(f"**{category}**", expanded=False):
            for stat in stats:
                st.checkbox(stat, key=f"stat_{stat}")
    
    st.divider()
    st.markdown("### 💡 Implementation Notes")
    
    st.write("""
    **These additional stats could be implemented by:**
    
    1. **Real-time Event Tracking** – Log user actions (watch, pause, share, etc.)
    2. **Time-Series Data** – Store metrics with timestamps for trends
    3. **Aggregation Engine** – Calculate daily/weekly/monthly summaries
    4. **Cache Layer** – Use @st.cache_data for expensive calculations
    5. **Export Features** – CSV/JSON export for data analysis
    6. **Visualization Dashboard** – Charts for trend analysis
    7. **Alerts & Notifications** – Notify users of milestones
    8. **Machine Learning** – Predict user behavior and preferences
    
    **Recommended Priority Order for Implementation:**
    1. Watch Engagement (directly impacts user retention)
    2. Content Performance (helps creators improve)
    3. Growth Metrics (shows business traction)
    4. Storage & Bandwidth (operational needs)
    5. Usage Patterns (personalization)
    6. Social Engagement (already partially tracked)
    7. Streaming Analytics (for creators)
    8. Achievements & Gamification (engagement booster)
    """)


def demo_user_activity(user_id: str):
    """Demo function to simulate user activity"""
    manager = get_user_manager()
    
    st.markdown("### 🎬 Demo: Simulate User Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Simulate Watch Activity**")
        if st.button("Watch 30 min Video"):
            manager.record_watch_activity(user_id, "video-001", 1800, "video")
            st.success("✅ Recorded 30 min watch")
            st.rerun()
        
        if st.button("Watch 1 hr Stream"):
            manager.record_watch_activity(user_id, "stream-001", 3600, "stream", "stream-001")
            st.success("✅ Recorded 1 hr stream")
            st.rerun()
    
    with col2:
        st.markdown("**Simulate Content Creation**")
        if st.button("Upload Video"):
            manager.record_upload(user_id, "video")
            st.success("✅ Recorded video upload")
            st.rerun()
        
        if st.button("Create Stream"):
            manager.record_upload(user_id, "stream")
            st.success("✅ Recorded stream creation")
            st.rerun()
        
        if st.button("Upload Image"):
            manager.record_upload(user_id, "image")
            st.success("✅ Recorded image upload")
            st.rerun()
    
    st.divider()
    
    if st.button("Record Interaction (Like/Comment)"):
        manager.record_interaction(user_id, "like")
        st.success("✅ Recorded interaction")
        st.rerun()
