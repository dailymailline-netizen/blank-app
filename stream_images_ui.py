"""
Streamlit UI components for Stream Image Management with intelligent page-level caching
"""

import streamlit as st
from pathlib import Path
from typing import Optional, List
import base64
from stream_images import StreamImageManager, ImageVisibility
from config import STREAM_IMAGES_DIR, IMAGE_CACHE_DIR, ALLOWED_IMAGE_EXTENSIONS, MAX_IMAGE_UPLOAD_SIZE_MB
import time


@st.cache_resource
def get_image_manager() -> StreamImageManager:
    """
    Cached image manager instance (persistent across reruns)
    Uses @st.cache_resource for singleton pattern
    """
    return StreamImageManager(STREAM_IMAGES_DIR, IMAGE_CACHE_DIR)


@st.cache_data(ttl=3600)
def get_cached_image_display(image_id: str, stream_id: str, page: str = "default") -> Optional[str]:
    """
    Cache image as base64 string for display (1 hour TTL)
    Reduces memory usage by encoding images once
    
    Args:
        image_id: Image ID
        stream_id: Stream ID
        page: Page context for cache organization
    
    Returns:
        Base64 encoded image string or None
    """
    manager = get_image_manager()
    image_data = manager.cache.get_image(image_id, page)
    
    if image_data:
        return base64.b64encode(image_data).decode('utf-8')
    return None


@st.cache_data(ttl=1800)
def get_stream_image_stats(stream_id: str, page: str = "default") -> dict:
    """
    Cache stream image statistics (30 min TTL)
    Reduces computational load
    """
    manager = get_image_manager()
    return manager.get_image_stats(stream_id)


def render_stream_image_uploader(stream_id: str, is_owner: bool = True, 
                                 page: str = "stream_details") -> Optional[str]:
    """
    Render image upload widget for stream (page-scoped)
    
    Args:
        stream_id: Stream ID
        is_owner: Whether user is stream owner
        page: Page identifier for cache organization
    
    Returns:
        Image ID if uploaded, None otherwise
    """
    if not is_owner:
        st.info("Only stream owners can upload images")
        return None
    
    st.subheader("📸 Add Images to Stream")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Stream Image",
            type=list(ALLOWED_IMAGE_EXTENSIONS),
            key=f"img_upload_{stream_id}"
        )
    
    with col2:
        visibility = st.selectbox(
            "Visibility",
            options=["public", "private"],
            key=f"visibility_{stream_id}"
        )
    
    if uploaded_file:
        title = st.text_input(
            "Image Title",
            value=uploaded_file.name,
            key=f"img_title_{stream_id}"
        )
        description = st.text_area(
            "Image Description (optional)",
            height=80,
            key=f"img_desc_{stream_id}"
        )
        
        col_upload, col_cancel = st.columns(2)
        
        with col_upload:
            if st.button("Upload Image", key=f"upload_btn_{stream_id}"):
                # Check file size
                file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
                
                if file_size_mb > MAX_IMAGE_UPLOAD_SIZE_MB:
                    st.error(f"File too large (max {MAX_IMAGE_UPLOAD_SIZE_MB} MB)")
                    return None
                
                # Upload image
                manager = get_image_manager()
                image_id = manager.upload_stream_image(
                    stream_id=stream_id,
                    image_data=uploaded_file.getvalue(),
                    filename=uploaded_file.name,
                    visibility=ImageVisibility(visibility),
                    title=title,
                    description=description,
                    page=page
                )
                
                if image_id:
                    st.success("✅ Image uploaded successfully")
                    
                    # Clear cache for this page
                    manager.cache.clear_page_cache(page)
                    
                    # Force rerun to show new image
                    st.rerun()
                else:
                    st.error("Failed to upload image")
                
                return image_id
        
        with col_cancel:
            if st.button("Cancel", key=f"cancel_btn_{stream_id}"):
                st.rerun()
    
    return None


def render_stream_images_gallery(stream_id: str, is_owner: bool = False,
                                 user_id: Optional[str] = None,
                                 page: str = "stream_gallery") -> None:
    """
    Render image gallery for stream with intelligent caching
    Per-page cache organization reduces memory overhead
    
    Args:
        stream_id: Stream ID
        is_owner: Whether user is stream owner
        user_id: Requesting user ID
        page: Page identifier for cache organization
    """
    manager = get_image_manager()
    images = manager.get_stream_images(
        stream_id, 
        user_id=user_id, 
        is_owner=is_owner,
        page=page
    )
    
    if not images:
        st.info("No images yet. Owner can upload images to this stream.")
        return
    
    st.subheader(f"📷 Stream Images ({len(images)})")
    
    # Show cache stats
    with st.expander("Cache Status", expanded=False):
        cache_stats = manager.cache.get_cache_stats()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Memory Used", f"{cache_stats['memory_used_mb']} MB")
        with col2:
            st.metric("Memory Max", f"{cache_stats['memory_max_mb']} MB")
        with col3:
            st.metric("Cached Items", cache_stats['cached_items'])
        with col4:
            st.metric("TTL", f"{cache_stats['ttl_hours']}h")
    
    # Show image stats
    stats = get_stream_image_stats(stream_id, page)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Images", stats["total"])
    with col2:
        st.metric("Public", stats["public"])
    with col3:
        st.metric("Private", stats["private"])
    with col4:
        st.metric("Total Size", f"{stats['total_size_mb']} MB")
    
    # Display images in grid
    cols = st.columns(3)
    
    for idx, img in enumerate(images):
        col = cols[idx % 3]
        
        with col:
            st.write(f"**{img.title}**" if img.title else f"**Image {idx + 1}**")
            
            # Get cached image for display
            image_b64 = get_cached_image_display(img.image_id, stream_id, page)
            
            if image_b64:
                st.image(f"data:image/jpeg;base64,{image_b64}", use_column_width=True)
            elif img.thumbnail_path:
                try:
                    st.image(img.thumbnail_path, use_column_width=True)
                except:
                    st.warning("Thumbnail unavailable")
            
            # Image details
            st.caption(f"📅 {img.created_at[:10]}")
            st.caption(f"👁️ {img.view_count} views")
            
            if img.description:
                st.write(f"*{img.description}*")
            
            # Visibility badge
            if img.visibility == ImageVisibility.PUBLIC:
                st.success("🔓 Public")
            else:
                st.warning("🔒 Private")
            
            # Owner controls
            if is_owner:
                col_delete, col_visibility = st.columns(2)
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"del_{img.image_id}"):
                        manager.delete_stream_image(stream_id, img.image_id)
                        st.success("Image deleted")
                        time.sleep(1)
                        st.rerun()
                
                with col_visibility:
                    new_visibility = st.selectbox(
                        "Visibility",
                        options=["public", "private"],
                        index=0 if img.visibility == ImageVisibility.PUBLIC else 1,
                        key=f"vis_{img.image_id}"
                    )
                    if new_visibility != img.visibility.value:
                        img.visibility = ImageVisibility(new_visibility)
                        manager._save_images()
                        st.success("Updated")
                        time.sleep(1)
                        st.rerun()


def render_page_cache_manager(page: str) -> None:
    """
    Render cache management controls for current page
    Allows manual cache optimization per page
    
    Args:
        page: Page identifier
    """
    manager = get_image_manager()
    
    with st.sidebar:
        with st.expander("🧠 Cache Management", expanded=False):
            st.write("**Page-Level Cache Controls**")
            
            cache_stats = manager.cache.get_cache_stats()
            st.write(f"Memory Used: {cache_stats['memory_used_mb']}/{cache_stats['memory_max_mb']} MB")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Refresh", key=f"cache_refresh_{page}"):
                    st.cache_data.clear()
                    st.success("Cache cleared")
                    time.sleep(1)
                    st.rerun()
            
            with col2:
                if st.button("🧹 Clear Page", key=f"cache_clear_page_{page}"):
                    removed = manager.cache.clear_page_cache(page)
                    st.success(f"Cleared {removed} items")
                    time.sleep(1)
                    st.rerun()
            
            st.divider()
            st.write("**Cache Info**")
            st.caption(f"TTL: {cache_stats['ttl_hours']}h")
            st.caption(f"Dir: {Path(cache_stats['cache_dir']).name}")


def render_stream_image_browser(page: str = "stream_browser") -> None:
    """
    Render image browser across all streams (page-scoped)
    Demonstrates effective multi-stream caching
    
    Args:
        page: Page identifier
    """
    manager = get_image_manager()
    
    st.subheader("🖼️ Stream Images Browser")
    
    if not manager.stream_images:
        st.info("No images uploaded yet")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_stream = st.selectbox(
            "Select Stream",
            options=list(manager.stream_images.keys()),
            key=f"stream_select_{page}"
        )
    
    with col2:
        visibility_filter = st.selectbox(
            "Visibility",
            options=["all", "public", "private"],
            key=f"visibility_filter_{page}"
        )
    
    if selected_stream:
        images = manager.get_stream_images(selected_stream, is_owner=True, page=page)
        
        # Apply filter
        if visibility_filter != "all":
            images = [img for img in images if img.visibility.value == visibility_filter]
        
        if images:
            render_stream_images_gallery(
                selected_stream,
                is_owner=True,
                page=page
            )
        else:
            st.info("No matching images")
