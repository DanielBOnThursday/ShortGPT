"""
Content Organizer for ShortGPT
Handles content type detection and channel assignment based on the workflow mapping
"""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ContentOrganizer:
    """Organizes content based on assignment mapping and handles channel rotation"""
    
    def __init__(self):
        """Initialize with content assignment mapping"""
        self.content_mapping = self._load_content_mapping()
        self.assignment_history = {}  # Track assignments for round-robin
        
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
                "scientific_facts": {
                    "description": "Educational/Scientific content",
                    "s3_folder": "science_facts",
                    "accounts": [{"id": 1, "name": "Default Science", "focus": "Science"}]
                },
                "historical_facts": {
                    "description": "Historical content",
                    "s3_folder": "history_facts", 
                    "accounts": [{"id": 5, "name": "Default History", "focus": "History"}]
                },
                "reddit_story": {
                    "description": "Reddit-style stories",
                    "s3_folder": "reddit_stories",
                    "accounts": [{"id": 11, "name": "Default Stories", "focus": "Stories"}]
                }
            }
        }
    
    def get_content_types(self) -> List[str]:
        """Get all available content types"""
        return list(self.content_mapping.get("content_assignments", {}).keys())
    
    def get_accounts_for_content_type(self, content_type: str) -> List[Dict]:
        """Get all accounts assigned to a specific content type"""
        assignments = self.content_mapping.get("content_assignments", {})
        content_config = assignments.get(content_type, {})
        return content_config.get("accounts", [])
    
    def get_next_account(self, content_type: str) -> Optional[Dict]:
        """
        Get the next account for a content type using round-robin assignment
        
        Args:
            content_type: The type of content to assign
            
        Returns:
            Account dictionary or None if no accounts available
        """
        accounts = self.get_accounts_for_content_type(content_type)
        if not accounts:
            return None
        
        # Initialize history for this content type if not exists
        if content_type not in self.assignment_history:
            self.assignment_history[content_type] = {
                'last_assigned_index': -1,
                'assignments': []
            }
        
        # Get next account in round-robin fashion
        history = self.assignment_history[content_type]
        next_index = (history['last_assigned_index'] + 1) % len(accounts)
        next_account = accounts[next_index]
        
        # Update history
        history['last_assigned_index'] = next_index
        history['assignments'].append({
            'account_id': next_account['id'],
            'account_name': next_account['name'],
            'assigned_at': datetime.now().isoformat()
        })
        
        # Keep only last 100 assignments to prevent memory buildup
        if len(history['assignments']) > 100:
            history['assignments'] = history['assignments'][-100:]
        
        return next_account
    
    def get_upload_schedule(self, content_type: str) -> Dict:
        """Get upload schedule configuration for a content type"""
        return self.content_mapping.get("upload_schedule", {}).get(content_type, {
            "frequency": "daily",
            "time_slots": ["12:00"],
            "platforms_priority": ["tiktok", "instagram", "youtube"]
        })
    
    def detect_content_type_from_script(self, script_text: str) -> str:
        """
        Attempt to detect content type from script text using keywords
        
        Args:
            script_text: The video script text
            
        Returns:
            Detected content type or 'reddit_story' as default
        """
        script_lower = script_text.lower()
        
        # Science/Technology keywords
        science_keywords = [
            'technology', 'science', 'research', 'innovation', 'digital',
            'ai', 'artificial intelligence', 'machine learning', 'computer',
            'programming', 'code', 'software', 'algorithm', 'data',
            'physics', 'chemistry', 'biology', 'engineering', 'tech'
        ]
        
        # Historical keywords
        history_keywords = [
            'history', 'historical', 'ancient', 'century', 'war', 'empire',
            'civilization', 'culture', 'tradition', 'past', 'medieval',
            'renaissance', 'revolution', 'dynasty', 'prehistoric', 'legend'
        ]
        
        # Reddit/Social story keywords
        reddit_keywords = [
            'reddit', 'relationship', 'aita', 'story', 'confession',
            'drama', 'family', 'friend', 'boyfriend', 'girlfriend',
            'workplace', 'college', 'school', 'personal', 'experience'
        ]
        
        # Count keyword matches
        science_score = sum(1 for keyword in science_keywords if keyword in script_lower)
        history_score = sum(1 for keyword in history_keywords if keyword in script_lower)
        reddit_score = sum(1 for keyword in reddit_keywords if keyword in script_lower)
        
        # Determine content type based on highest score
        if science_score > history_score and science_score > reddit_score:
            return 'scientific_facts'
        elif history_score > reddit_score:
            return 'historical_facts'
        else:
            return 'reddit_story'  # Default fallback
    
    def get_s3_folder_for_content_type(self, content_type: str) -> str:
        """Get the S3 folder name for a content type"""
        assignments = self.content_mapping.get("content_assignments", {})
        content_config = assignments.get(content_type, {})
        return content_config.get("s3_folder", content_type)
    
    def get_assignment_stats(self) -> Dict:
        """Get statistics about content assignments"""
        stats = {
            'total_assignments': 0,
            'by_content_type': {},
            'recent_assignments': []
        }
        
        for content_type, history in self.assignment_history.items():
            assignments = history.get('assignments', [])
            stats['total_assignments'] += len(assignments)
            stats['by_content_type'][content_type] = {
                'count': len(assignments),
                'last_assigned_account': None,
                'accounts_available': len(self.get_accounts_for_content_type(content_type))
            }
            
            # Get last assigned account
            if assignments:
                last_assignment = assignments[-1]
                stats['by_content_type'][content_type]['last_assigned_account'] = {
                    'id': last_assignment['account_id'],
                    'name': last_assignment['account_name'],
                    'assigned_at': last_assignment['assigned_at']
                }
                
                # Add to recent assignments
                stats['recent_assignments'].append({
                    'content_type': content_type,
                    'account_id': last_assignment['account_id'],
                    'account_name': last_assignment['account_name'],
                    'assigned_at': last_assignment['assigned_at']
                })
        
        # Sort recent assignments by date
        stats['recent_assignments'].sort(
            key=lambda x: x['assigned_at'], 
            reverse=True
        )
        
        # Keep only last 20
        stats['recent_assignments'] = stats['recent_assignments'][:20]
        
        return stats
    
    def validate_content_mapping(self) -> List[str]:
        """
        Validate the content mapping configuration
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        assignments = self.content_mapping.get("content_assignments", {})
        if not assignments:
            errors.append("No content assignments found in configuration")
            return errors
        
        for content_type, config in assignments.items():
            if not config.get("s3_folder"):
                errors.append(f"Missing s3_folder for content type: {content_type}")
            
            accounts = config.get("accounts", [])
            if not accounts:
                errors.append(f"No accounts assigned to content type: {content_type}")
            else:
                for account in accounts:
                    if not account.get("id"):
                        errors.append(f"Account missing ID in content type: {content_type}")
                    if not account.get("name"):
                        errors.append(f"Account missing name in content type: {content_type}")
        
        return errors