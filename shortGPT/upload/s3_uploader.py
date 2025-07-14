"""
S3 Uploader for ShortGPT Generated Content
Automatically organizes and uploads videos based on content type and language
"""

import os
import boto3
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import mimetypes
from botocore.exceptions import ClientError


class S3Uploader:
    """Handles S3 uploads with automatic organization based on content assignment mapping"""
    
    def __init__(self):
        """Initialize S3 client and load content mapping configuration"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET', 'content-automation-assets')
        self.content_mapping = self._load_content_mapping()
        
    def _load_content_mapping(self) -> Dict:
        """Load content assignment mapping from config file"""
        config_path = Path(__file__).parent.parent.parent.parent / "config" / "content_assignment_mapping.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Content mapping config not found at {config_path}")
            return self._get_default_mapping()
    
    def _get_default_mapping(self) -> Dict:
        """Fallback content mapping if config file not found"""
        return {
            "content_assignments": {
                "scientific_facts": {"s3_folder": "science_facts"},
                "historical_facts": {"s3_folder": "history_facts"},
                "reddit_story": {"s3_folder": "reddit_stories"}
            }
        }
    
    def get_s3_folder_path(self, content_type: str, language: str = "english") -> str:
        """
        Get the S3 folder path based on content type and language
        
        Args:
            content_type: Type of content (scientific_facts, historical_facts, reddit_story)
            language: Language of the content (default: english)
            
        Returns:
            S3 folder path string
        """
        assignments = self.content_mapping.get("content_assignments", {})
        content_config = assignments.get(content_type, {})
        s3_folder = content_config.get("s3_folder", content_type)
        
        return f"edited-clips/{language}/{s3_folder}/"
    
    def upload_video(
        self, 
        video_path: str, 
        content_type: str, 
        language: str = "english",
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, str]:
        """
        Upload a video to S3 with proper organization
        
        Args:
            video_path: Local path to video file
            content_type: Type of content for organization
            language: Language for folder organization
            metadata: Additional metadata for the upload
            
        Returns:
            Tuple of (success: bool, s3_url: str)
        """
        try:
            # Validate file exists
            if not os.path.exists(video_path):
                return False, f"Video file not found: {video_path}"
            
            # Generate S3 key
            s3_folder = self.get_s3_folder_path(content_type, language)
            filename = Path(video_path).name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            s3_key = f"{s3_folder}{timestamp}_{filename}"
            
            # Prepare metadata (S3 metadata values must be strings)
            upload_metadata = {
                'upload_date': datetime.now().isoformat(),
                'content_type': str(content_type),
                'language': str(language),
                'processor': 'shortgpt_integrated',
                'file_size': str(os.path.getsize(video_path))
            }
            
            if metadata:
                print(f"🔍 Processing metadata for S3 upload: {type(metadata)} with {len(metadata)} items")
                # Convert all metadata values to strings for S3 compatibility
                for key, value in metadata.items():
                    try:
                        # Ensure key is a string
                        str_key = str(key) if key is not None else 'unknown_key'
                        
                        # Convert value to string safely
                        if value is not None:
                            # Handle different types safely
                            if isinstance(value, (int, float, bool)):
                                str_value = str(value)
                            elif isinstance(value, (list, dict)):
                                str_value = json.dumps(value)
                            else:
                                str_value = str(value)
                            upload_metadata[str_key] = str_value
                        else:
                            upload_metadata[str_key] = 'null'
                    except Exception as e:
                        print(f"⚠️  Warning: Could not convert metadata {key}:{value} to string: {e}")
                        # Skip problematic metadata
                        continue
            
            # Determine content type for HTTP headers
            content_mime_type, _ = mimetypes.guess_type(video_path)
            if not content_mime_type:
                content_mime_type = 'video/mp4'
            
            # Upload to S3
            with open(video_path, 'rb') as file_data:
                self.s3_client.upload_fileobj(
                    file_data,
                    self.bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_mime_type,
                        'Metadata': upload_metadata
                    }
                )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            print(f"✅ Video uploaded successfully: {s3_url}")
            return True, s3_url
            
        except ClientError as e:
            error_msg = f"S3 upload error: {e}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Upload error: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def upload_multiple_videos(
        self, 
        video_paths: List[str], 
        content_type: str, 
        language: str = "english"
    ) -> List[Tuple[str, bool, str]]:
        """
        Upload multiple videos with the same content type and language
        
        Args:
            video_paths: List of local video file paths
            content_type: Type of content for organization
            language: Language for folder organization
            
        Returns:
            List of tuples (video_path, success, s3_url_or_error)
        """
        results = []
        
        for video_path in video_paths:
            success, result = self.upload_video(video_path, content_type, language)
            results.append((video_path, success, result))
        
        return results
    
    def list_uploaded_content(self, content_type: str, language: str = "english") -> List[Dict]:
        """
        List all uploaded content for a specific type and language
        
        Args:
            content_type: Type of content to list
            language: Language folder to check
            
        Returns:
            List of content metadata dictionaries
        """
        try:
            s3_folder = self.get_s3_folder_path(content_type, language)
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=s3_folder
            )
            
            content_list = []
            for obj in response.get('Contents', []):
                # Get metadata
                metadata_response = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                
                content_info = {
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'url': f"https://{self.bucket_name}.s3.amazonaws.com/{obj['Key']}",
                    'metadata': metadata_response.get('Metadata', {})
                }
                content_list.append(content_info)
            
            return content_list
            
        except ClientError as e:
            print(f"❌ Error listing content: {e}")
            return []
    
    def get_upload_stats(self) -> Dict:
        """Get statistics about uploaded content across all types and languages"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix="edited-clips/"
            )
            
            stats = {
                'total_files': 0,
                'total_size': 0,
                'by_language': {},
                'by_content_type': {},
                'last_upload': None
            }
            
            for obj in response.get('Contents', []):
                stats['total_files'] += 1
                stats['total_size'] += obj['Size']
                
                # Parse path for language and content type
                path_parts = obj['Key'].split('/')
                if len(path_parts) >= 3:
                    language = path_parts[1]
                    content_type = path_parts[2]
                    
                    # Track by language
                    if language not in stats['by_language']:
                        stats['by_language'][language] = {'count': 0, 'size': 0}
                    stats['by_language'][language]['count'] += 1
                    stats['by_language'][language]['size'] += obj['Size']
                    
                    # Track by content type
                    if content_type not in stats['by_content_type']:
                        stats['by_content_type'][content_type] = {'count': 0, 'size': 0}
                    stats['by_content_type'][content_type]['count'] += 1
                    stats['by_content_type'][content_type]['size'] += obj['Size']
                
                # Track latest upload
                if not stats['last_upload'] or obj['LastModified'] > stats['last_upload']:
                    stats['last_upload'] = obj['LastModified']
            
            # Convert last upload to ISO format
            if stats['last_upload']:
                stats['last_upload'] = stats['last_upload'].isoformat()
            
            return stats
            
        except ClientError as e:
            print(f"❌ Error getting upload stats: {e}")
            return {}