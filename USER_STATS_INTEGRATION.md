# User Management Integration Guide

## Quick Start

### 1. Files Created
- ✅ `user_stats.py` (460 lines) – Core user & stats system
- ✅ `user_stats_ui.py` (450 lines) – Streamlit UI components
- ✅ `USER_STATS.md` – Full documentation

### 2. Config Updated
- ✅ `config.py` (+5 lines) – User directories & settings

### 3. Install Dependencies
```bash
# Already included in Python stdlib
# No new packages needed
```

### 4. Update streamlit_app.py

Add imports:
```python
from user_stats_ui import (
    render_safe_blank_page,
    render_user_profile,
    render_watch_history,
    render_subscriber_features,
    render_users_list_page,
    demo_user_activity,
    get_user_manager
)
```

Initialize session state:
```python
if "user_id" not in st.session_state:
    st.session_state.user_id = None
```

Add routing:
```python
# At app start - show login page if not logged in
if st.session_state.user_id is None:
    render_safe_blank_page()
else:
    # Show main navigation
    page = st.sidebar.radio("Navigation", [
        "Home",
        "Profile",
        "Watch History",
        "Features",
        "Users Admin",
        "Activity Demo"
    ])
    
    if page == "Home":
        st.title("Welcome!")
        render_user_profile(st.session_state.user_id)
    elif page == "Profile":
        render_user_profile(st.session_state.user_id)
    elif page == "Watch History":
        render_watch_history(st.session_state.user_id)
    elif page == "Features":
        render_subscriber_features(st.session_state.user_id)
    elif page == "Users Admin":
        render_users_list_page()
    elif page == "Activity Demo":
        demo_user_activity(st.session_state.user_id)
```

---

## 8-Point Stats System

### Core Metrics
1. **Subscriber Features Used** – Count of premium features activated
2. **Watch History Entries** – Number of watch events recorded
3. **Total Watched Hours** – Sum of all watch durations
4. **Videos Uploaded** – Count of video uploads
5. **Streams Created** – Count of live streams
6. **Images Uploaded** – Count of image uploads
7. **Total Interactions** – Count of likes, comments, shares
8. **Last Activity Timestamp** – Most recent activity time

### Recording Activities

**Watch a video:**
```python
manager = get_user_manager()
manager.record_watch_activity(
    user_id=user_id,
    video_id="video-123",
    duration_seconds=1800,  # 30 minutes
    content_type="video"
)
```

**Upload content:**
```python
manager.record_upload(user_id, "video")
manager.record_upload(user_id, "stream")
manager.record_upload(user_id, "image")
```

**Record interaction:**
```python
manager.record_interaction(user_id, "like")
manager.record_interaction(user_id, "comment")
manager.record_interaction(user_id, "share")
```

**Use subscriber feature:**
```python
from user_stats import SubscriberFeature
manager.use_subscriber_feature(user_id, SubscriberFeature.PRIORITY_UPLOAD)
```

---

## User Roles & Subscriptions

### Role Levels
- **FREE** – No premium features
- **SUBSCRIBER** – 4 premium features
- **PREMIUM** – All 8 features
- **ADMIN** – Platform administration

### Subscribe User
```python
from user_stats import UserRole
manager.upgrade_subscription(
    user_id=user_id,
    role=UserRole.SUBSCRIBER,
    days=365
)
```

### Features by Role

**Free:**
- None (no premium features)

**Subscriber:**
- Priority uploads
- HD streaming (1080p)
- Ad-free
- Custom playlists

**Premium:**
- Custom branding
- Priority uploads
- Advanced analytics
- HD streaming
- Ad-free
- Early access
- Custom playlists
- Bulk operations

---

## 30+ Possible Additional Stats

The system includes a comprehensive list of 30+ stats that can be implemented:

### Categories
1. **Watch Engagement** (5 stats)
2. **Streaming Analytics** (6 stats)
3. **Content Performance** (6 stats)
4. **Social Engagement** (6 stats)
5. **Storage & Bandwidth** (6 stats)
6. **Growth Metrics** (6 stats)
7. **Usage Patterns** (6 stats)
8. **Customization** (6 stats)
9. **Achievements** (6 stats)

Access the full list in `render_possible_stats_list()` function.

---

## Watch History Tracking

### Record Watch
```python
history_tracker = manager.history_tracker

entry = history_tracker.add_watch_entry(
    user_id=user_id,
    video_id="video-123",
    duration_seconds=1800,
    content_type="video",
    stream_id=None,
    quality="720p"
)
```

### Get History
```python
# Get last 50 watches
history = history_tracker.get_watch_history(user_id, limit=50)

for entry in history:
    print(f"Type: {entry.content_type}")
    print(f"Duration: {entry.duration_seconds}s")
    print(f"Quality: {entry.quality}")
```

### Get Stats by Type
```python
stats_by_type = history_tracker.get_watch_stats_by_type(user_id)

for content_type, data in stats_by_type.items():
    print(f"{content_type}:")
    print(f"  Count: {data['count']}")
    print(f"  Total time: {data['total_seconds']}s")
    print(f"  Avg duration: {data['avg_duration']}s")
```

### Calculate Total Hours
```python
total_hours = history_tracker.get_total_watched_hours(user_id)
print(f"Total watched: {total_hours} hours")
```

---

## Safe Blank Page Features

The `render_safe_blank_page()` provides:
- Welcome header
- Feature overview
- Account creation form
- Login interface
- Platform introduction
- Call-to-action buttons

Automatically displays when user is not logged in.

---

## User Analytics Dashboard

The `render_users_list_page()` provides 4 tabs:

### Tab 1: All Users
- Complete user directory
- User statistics table
- Role information
- Activity timestamps

### Tab 2: Subscribers
- Subscriber count & percentage
- Subscription expiration dates
- Feature usage
- Watch hours per subscriber

### Tab 3: Analytics
- Total videos uploaded
- Total streams created
- Total images uploaded
- Total interactions
- Total watch hours
- Top users by activity

### Tab 4: Possible Stats
- Full list of 30+ stats
- Categorized by type
- Implementation notes
- Priority recommendations

---

## Demo Mode

The `demo_user_activity()` function provides buttons to simulate:
- Watch video (30 min)
- Watch stream (1 hr)
- Upload video
- Create stream
- Upload image
- Record interaction

Use for testing and demonstrations.

---

## Database Schema

### users.json
```json
{
  "user_id": {
    "username": "string",
    "email": "string",
    "role": "free|subscriber|premium|admin",
    "created_at": "ISO timestamp",
    "subscription_expires": "ISO timestamp or null",
    "is_active": "boolean"
  }
}
```

### user_stats.json
```json
{
  "user_id": {
    "subscriber_features_used": "int",
    "watch_history_entries": "int",
    "total_watched_hours": "float",
    "videos_uploaded": "int",
    "streams_created": "int",
    "images_uploaded": "int",
    "total_interactions": "int",
    "last_activity_timestamp": "ISO timestamp"
  }
}
```

### user_history/{user_id}_history.json
```json
[
  {
    "video_id": "string",
    "watched_at": "ISO timestamp",
    "duration_seconds": "int",
    "content_type": "video|stream|image",
    "quality": "string"
  }
]
```

---

## Testing Checklist

- [ ] Create free user account
- [ ] Login with user ID
- [ ] View profile dashboard
- [ ] Use activity demo buttons
- [ ] Check 8-point stats update
- [ ] View watch history
- [ ] Upgrade to subscriber
- [ ] Check subscriber features
- [ ] View users admin page
- [ ] Check analytics dashboard
- [ ] Review possible stats list

---

## Common Tasks

### Create User Programmatically
```python
manager = get_user_manager()
user_id = manager.create_user("john_doe", "john@example.com", UserRole.FREE)
```

### Get All User Stats
```python
all_stats = manager.get_all_users_stats()
for user_id, stats in all_stats.items():
    print(f"{user_id}: {stats.total_watched_hours}h watched")
```

### Get Subscribers
```python
subscribers = manager.get_subscribers()
print(f"Total subscribers: {len(subscribers)}")
```

### Export User Data
```python
user = manager.get_user(user_id)
stats = manager.get_user_stats(user_id)
history = manager.history_tracker.get_watch_history(user_id)

export_data = {
    "user": user,
    "stats": stats.to_dict(),
    "history": [e.to_dict() for e in history]
}
# Save to JSON or CSV
```

---

## Next Steps

1. ✅ Copy `user_stats.py` and `user_stats_ui.py` to project
2. ✅ Update `config.py` with user directories
3. ✅ Update `streamlit_app.py` with user pages
4. ✅ Test with demo user account
5. ✅ Review admin analytics dashboard
6. ✅ Check possible stats list for future features

---

## Support

For full details, see `USER_STATS.md`.

For architecture, see classes in `user_stats.py`.

For UI components, see functions in `user_stats_ui.py`.
