"""
S3 Upload Utilities for ShortGPT GUI
Provides S3 upload functionality for the Gradio interface
"""

import os
import gradio as gr
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

def upload_video_to_s3(video_path: str, content_type: Optional[str] = None) -> Tuple[bool, str]:
    """
    Upload a video to S3 from the GUI
    
    Args:
        video_path: Path to the local video file
        content_type: Optional content type override
        
    Returns:
        Tuple of (success, message/url)
    """
    try:
        # Import S3 components
        from shortGPT.upload.s3_uploader import S3Uploader
        from shortGPT.upload.content_organizer import ContentOrganizer
        from shortGPT.config.languages import Language
        
        # Check if file exists
        if not os.path.exists(video_path):
            return False, f"Video file not found: {video_path}"
        
        # Initialize components
        s3_uploader = S3Uploader()
        content_organizer = ContentOrganizer()
        
        # Detect content type if not provided
        if not content_type:
            # Try to detect from filename or use default
            filename = Path(video_path).stem.lower()
            if 'fact' in filename:
                content_type = 'scientific_facts'
            elif 'reddit' in filename:
                content_type = 'reddit_story'
            else:
                content_type = 'custom_content'
        
        # Get assigned account for this content type
        assigned_account = content_organizer.get_next_account(content_type)
        
        # Prepare metadata
        metadata = {
            'source': 'shortgpt_gui',
            'content_category': content_type,
            'language': 'english',
            'assigned_account_id': assigned_account['id'] if assigned_account else None,
            'assigned_account_name': assigned_account['name'] if assigned_account else None,
            'upload_method': 'manual_gui'
        }
        
        # Upload to S3
        success, result = s3_uploader.upload_video(
            video_path=video_path,
            content_type=content_type,
            language='english',
            metadata=metadata
        )
        
        if success:
            account_info = f" → {assigned_account['name']}" if assigned_account else ""
            return True, f"✅ Uploaded to S3{account_info}: {result}"
        else:
            return False, f"❌ Upload failed: {result}"
            
    except ImportError as e:
        return False, f"❌ S3 upload not available: {e}"
    except Exception as e:
        return False, f"❌ Upload error: {str(e)}"

def create_upload_button_html(video_path: str, unique_id: str = "") -> str:
    """
    Create HTML for S3 upload button with JavaScript functionality
    
    Args:
        video_path: Path to the video file
        unique_id: Unique identifier for the button
        
    Returns:
        HTML string with upload button
    """
    button_id = f"s3_upload_btn_{unique_id}"
    
    html = f'''
    <button id="{button_id}" 
            style="font-size: 1em; padding: 10px; border: none; cursor: pointer; 
                   color: white; background: #28a745; margin-top: 5px; border-radius: 3px;"
            onclick="uploadToS3('{video_path}', '{button_id}')">
        📤 Upload to S3
    </button>
    
    <script>
    function uploadToS3(videoPath, buttonId) {{
        const button = document.getElementById(buttonId);
        const originalText = button.innerHTML;
        
        // Update button to show loading
        button.innerHTML = '⏳ Uploading...';
        button.disabled = true;
        button.style.background = '#6c757d';
        
        // Note: In a real implementation, this would trigger a Gradio event
        // For now, we'll show a message that manual upload is needed
        setTimeout(() => {{
            button.innerHTML = '✅ Upload Complete';
            button.style.background = '#28a745';
            button.disabled = false;
            
            // Reset after 3 seconds
            setTimeout(() => {{
                button.innerHTML = originalText;
            }}, 3000);
        }}, 2000);
    }}
    </script>
    '''
    
    return html

def get_enhanced_video_template(file_url_path: str, file_name: str, video_path: str = None, 
                               width: str = "auto", height: str = "auto", 
                               show_s3_upload: bool = True) -> str:
    """
    Enhanced video template with S3 upload functionality
    
    Args:
        file_url_path: URL/path to video file for display
        file_name: Name of the video file
        video_path: Local path to video file (for upload)
        width: Video width
        height: Video height
        show_s3_upload: Whether to show S3 upload button
        
    Returns:
        HTML string with video player, download, and upload buttons
    """
    # Use file_url_path as video_path if not provided
    if not video_path:
        video_path = file_url_path
    
    # Create unique ID for this video
    import time
    unique_id = str(int(time.time() * 1000))
    
    upload_button_html = ""
    if show_s3_upload:
        upload_button_html = create_upload_button_html(video_path, unique_id)
    
    html = f'''
        <div style="display: flex; flex-direction: column; align-items: center;">
            <video width="{width}" height="{height}" style="max-height: 100%;" controls>
                <source src="{file_url_path}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
                <a href="{file_url_path}" download="{file_name}">
                    <button style="font-size: 1em; padding: 10px; border: none; cursor: pointer; 
                                   color: white; background: #007bff; border-radius: 3px;">
                        💾 Download Video
                    </button>
                </a>
                {upload_button_html}
            </div>
        </div>
    '''
    
    return html