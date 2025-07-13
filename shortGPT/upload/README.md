# ShortGPT S3 Upload Module

This module provides automated S3 upload functionality integrated with ShortGPT's content engines. It automatically organizes videos based on content type and language, assigns them to appropriate channels, and uploads them to S3 with proper metadata.

## Features

- **Automatic Content Organization**: Videos are organized in S3 based on content type and language
- **Channel Assignment**: Round-robin assignment of videos to appropriate channels based on content type
- **Metadata Tracking**: Rich metadata attached to each upload including content type, language, assigned account, and processing details
- **Content Type Detection**: Automatic detection of content type from script text
- **Upload Statistics**: Comprehensive statistics about uploads and assignments

## S3 Folder Structure

```
edited-clips/
├── english/
│   ├── science_facts/      # Scientific and technology content
│   ├── history_facts/      # Historical content and facts
│   └── reddit_stories/     # Reddit-style stories and narratives
├── spanish/
│   ├── science_facts/
│   ├── history_facts/
│   └── reddit_stories/
└── french/
    ├── science_facts/
    ├── history_facts/
    └── reddit_stories/
```

## Content Type Mapping

Based on `/config/content_assignment_mapping.json`:

### Scientific Facts (`science_facts`)
- **Accounts**: Tech Pulse Daily, Future Forge Hub, Digital Maverick Studio, Code Craft Chronicles, LearnLift Labs, Insight Ignite Hub
- **Focus**: Technology, science, innovation, programming, educational content

### Historical Facts (`history_facts`) 
- **Accounts**: Zenith Lifestyle Lab, Vitality Vanguard, Mindful Momentum Co, Balanced Bliss Media, Canvas Rebellion, Story Weaver Collective
- **Focus**: Historical content, culture, art history, life wisdom

### Reddit Stories (`reddit_stories`)
- **Accounts**: Creative Alchemy Hub, Artisan Echo Studio, Curiosity Compass Media, WisdomWave Network, Culture Current Media, VibeVault Studio, EntertainmentElevate, TrendTideProductions
- **Focus**: Social stories, entertainment, trending content, personal narratives

## Usage

### Basic Usage with Integrated Engine

```python
from shortGPT import IntegratedContentEngine
from shortGPT.config.languages import Language

# Initialize the integrated engine
engine = IntegratedContentEngine()

# Create and upload scientific facts videos
results = engine.create_and_upload_scientific_facts(
    num_videos=3,
    language=Language.ENGLISH
)

# Create and upload historical facts videos
results = engine.create_and_upload_historical_facts(
    num_videos=2,
    language=Language.SPANISH
)

# Create and upload Reddit story videos
results = engine.create_and_upload_reddit_stories(
    num_videos=2,
    language=Language.FRENCH
)

# Create custom content with auto-detection
result = engine.create_and_upload_custom_content(
    script="Did you know that quantum computers use quantum bits?",
    language=Language.ENGLISH
)
```

### Direct S3 Upload

```python
from shortGPT import S3Uploader

uploader = S3Uploader()

# Upload a single video
success, s3_url = uploader.upload_video(
    video_path="/path/to/video.mp4",
    content_type="scientific_facts",
    language="english",
    metadata={"custom_field": "value"}
)

# Upload multiple videos
results = uploader.upload_multiple_videos(
    video_paths=["/path/to/video1.mp4", "/path/to/video2.mp4"],
    content_type="historical_facts",
    language="spanish"
)
```

### Content Organization

```python
from shortGPT import ContentOrganizer

organizer = ContentOrganizer()

# Get next account for round-robin assignment
account = organizer.get_next_account("scientific_facts")

# Detect content type from script
content_type = organizer.detect_content_type_from_script(
    "In ancient Rome, people used to..."
)

# Get assignment statistics
stats = organizer.get_assignment_stats()
```

## Environment Variables

Required environment variables:

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket_name
AWS_REGION=us-east-1
```

## File Organization

- `s3_uploader.py` - Core S3 upload functionality
- `content_organizer.py` - Content type detection and channel assignment
- `../engine/integrated_content_engine.py` - Integrated engine combining content creation with upload
- `../examples/integrated_workflow_example.py` - Complete usage example

## Metadata

Each uploaded video includes comprehensive metadata:

```json
{
    "upload_date": "2025-01-13T15:30:00",
    "content_type": "scientific_facts",
    "language": "english",
    "processor": "shortgpt_integrated",
    "file_size": "15728640",
    "engine_type": "FactsShortEngine",
    "content_category": "scientific_facts",
    "voice_module": "ElevenLabsVoiceModule",
    "assigned_account_id": 1,
    "assigned_account_name": "Tech Pulse Daily",
    "creation_timestamp": "2025-01-13T15:29:45"
}
```

## Integration with Existing Workflow

This module seamlessly integrates with your existing ShortGPT workflow:

1. **Video Creation**: Uses ShortGPT's native engines (FactsShortEngine, RedditShortEngine, etc.)
2. **Content Assignment**: Automatically assigns videos to appropriate channels based on content type
3. **S3 Upload**: Organizes and uploads videos with proper folder structure
4. **Metadata Tracking**: Tracks all processing details for analytics and management

The system maintains the complete 12-step ShortGPT process while adding automated upload and organization capabilities.