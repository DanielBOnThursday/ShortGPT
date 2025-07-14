import os
import random
import yt_dlp
import subprocess
import json
import torch

def getYoutubeVideoLink(url):
    print(f"🔍 Extracting YouTube video info from: {url}")
    format_filter = "[height<=1920]" if 'shorts' in url else "[height<=1080]"
    
    # Try multiple format options in order of preference
    format_options = [
        f"best[ext=mp4]{format_filter}/best[ext=mp4]/best{format_filter}",
        f"best{format_filter}/best",
        "best[height<=720]/best",
        "worst"  # Last resort
    ]
    
    for i, format_opt in enumerate(format_options):
        ydl_opts = {
            "quiet": i > 0,  # Only show output for first attempt
            "no_warnings": i > 0,
            "no_color": True,
            "no_call_home": True,
            "no_check_certificate": True,
            "socket_timeout": 30,  # 30 second timeout
            "format": format_opt
        }
        
        try:
            if i == 0:
                print(f"📺 Using yt-dlp to extract video info (attempt {i+1}/{len(format_options)})...")
            else:
                print(f"🔄 Trying format option {i+1}/{len(format_options)}...")
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                dictMeta = ydl.extract_info(url, download=False)
                video_url = dictMeta.get('url')
                duration = dictMeta.get('duration')
                
                if video_url and duration:
                    print(f"✅ YouTube extraction successful:")
                    print(f"   Duration: {duration}s")
                    print(f"   Format: {format_opt}")
                    print(f"   URL length: {len(video_url)} chars")
                    return video_url, duration
                else:
                    print(f"⚠️  Missing data: URL={video_url is not None}, Duration={duration is not None}")
                    continue
                    
        except Exception as e:
            if i == len(format_options) - 1:  # Last attempt
                print(f"❌ All YouTube extraction attempts failed. Last error: {e}")
                raise Exception(f"Failed getting video link from {url}: {e}")
            else:
                print(f"⚠️  Attempt {i+1} failed: {e}")
                continue
                
    raise Exception(f"Failed getting video link from {url}: No working format found")

def extract_random_clip_from_video(video_url, video_duration, clip_duration, output_file):
    """Extracts a clip from a video using a signed URL.
    Args:
        video_url (str): The signed URL of the video.
        video_duration (int): Duration of the video.
        clip_duration (int): The duration of the clip in seconds.
        output_file (str): The output file path for the extracted clip.
    """
    print(f"🎬 Starting video clip extraction:")
    print(f"   Input URL: {video_url}")
    print(f"   Video duration: {video_duration}s")
    print(f"   Clip duration: {clip_duration}s")
    print(f"   Output file: {output_file}")
    
    if not video_duration:
        raise Exception("Could not get video duration")
    if not video_duration*0.7 > 120:
        raise Exception("Video too short")
        
    # Check if this is a YouTube URL that needs processing
    actual_video_url = video_url
    actual_duration = video_duration
    
    if 'youtube.com' in video_url or 'youtu.be' in video_url:
        print("📺 YouTube URL detected, extracting stream URL...")
        try:
            actual_video_url, actual_duration = getYoutubeVideoLink(video_url)
            print(f"✅ YouTube stream URL extracted successfully")
            print(f"🔗 Stream URL length: {len(actual_video_url)} characters")
            
            # Test if the stream URL is accessible
            print("🔍 Testing stream URL accessibility...")
            test_cmd = ['ffprobe', '-v', 'quiet', '-select_streams', 'v:0', '-show_entries', 'stream=duration', '-of', 'csv=p=0', actual_video_url]
            try:
                test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=15)
                if test_result.returncode == 0:
                    print("✅ Stream URL is accessible")
                else:
                    print("⚠️  Stream URL test failed, but proceeding anyway")
            except subprocess.TimeoutExpired:
                print("⚠️  Stream URL test timed out, but proceeding anyway")
            except Exception as test_e:
                print(f"⚠️  Stream URL test error: {test_e}, but proceeding anyway")
                
        except Exception as e:
            print(f"❌ Failed to extract YouTube stream: {e}")
            raise Exception(f"YouTube video processing failed: {e}")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Created output directory: {output_dir}")
    
    start_time = actual_duration*0.15 + random.random()* (0.7*actual_duration-clip_duration)
    print(f"🎯 Random start time selected: {start_time:.2f}s")
    
    # Choose codec and preset based on GPU availability
    
    # Try GPU encoding first if available
    if torch.cuda.is_available() and os.getenv('FFMPEG_GPU', '0') == '1':
        video_codec = 'h264_nvenc'
        preset = 'fast'
        
        command = [
            'ffmpeg',
            '-loglevel', 'warning',  # Show warnings for debugging
            '-ss', str(start_time),
            '-t', str(clip_duration),
            '-i', actual_video_url,
            '-c:v', video_codec,
            '-preset', preset,
            '-avoid_negative_ts', 'make_zero',  # Handle timing issues
            '-y',  # Overwrite output file
            output_file
        ]
        
        try:
            print("🎮 Video clipping with GPU: h264_nvenc")
            print(f"🔧 Command: ffmpeg -ss {start_time} -t {clip_duration} -i [URL] -c:v {video_codec} -preset {preset} [output]")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            
            # Check if output file was created
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f"✅ GPU video clip created successfully: {output_file}")
                return output_file  # Success with GPU
            else:
                raise Exception("GPU encoding completed but output file is missing or empty")
                
        except subprocess.CalledProcessError as e:
            print("⚠️  GPU encoding failed, falling back to CPU...")
            print(f"GPU stderr: {e.stderr}")
            print(f"GPU stdout: {e.stdout}")
            # Fall through to CPU encoding
        except Exception as e:
            print(f"⚠️  GPU encoding error: {e}")
            # Fall through to CPU encoding
    
    # CPU encoding (fallback or default)
    print("💻 Video clipping with CPU: libx264")
    command = [
        'ffmpeg',
        '-loglevel', 'warning',  # Show warnings for debugging
        '-ss', str(start_time),
        '-t', str(clip_duration),
        '-i', actual_video_url,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-avoid_negative_ts', 'make_zero',  # Handle timing issues
        '-y',  # Overwrite output file
        output_file
    ]
    
    try:
        print(f"🔧 Command: ffmpeg -ss {start_time} -t {clip_duration} -i [URL] -c:v libx264 -preset ultrafast [output]")
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        if not os.path.exists(output_file):
            raise Exception(f"Output file not created: {output_file}")
        
        if os.path.getsize(output_file) == 0:
            raise Exception(f"Output file is empty: {output_file}")
        
        print(f"✅ Video clip created successfully: {output_file}")
        return output_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg command failed: {e}")
        print(f"FFmpeg stderr: {e.stderr}")
        print(f"FFmpeg stdout: {e.stdout}")
        print(f"Command: {' '.join(['ffmpeg'] + command[1:-1] + ['[output]'])}")
        raise Exception(f"Video clipping failed: {e}")
    except Exception as e:
        print(f"❌ Video clipping error: {e}")
        raise Exception(f"Failed to extract video clip: {e}")


def get_aspect_ratio(video_file):
    cmd = 'ffprobe -i "{}" -v quiet -print_format json -show_format -show_streams'.format(video_file)
#     jsonstr = subprocess.getoutput(cmd)
    jsonstr = subprocess.check_output(cmd, shell=True, encoding='utf-8')
    r = json.loads(jsonstr)
    # look for "codec_type": "video". take the 1st one if there are mulitple
    video_stream_info = [x for x in r['streams'] if x['codec_type']=='video'][0]
    if 'display_aspect_ratio' in video_stream_info and video_stream_info['display_aspect_ratio']!="0:1":
        a,b = video_stream_info['display_aspect_ratio'].split(':')
        dar = int(a)/int(b)
    else:
        # some video do not have the info of 'display_aspect_ratio'
        w,h = video_stream_info['width'], video_stream_info['height']
        dar = int(w)/int(h)
        ## not sure if we should use this
        #cw,ch = video_stream_info['coded_width'], video_stream_info['coded_height']
        #sar = int(cw)/int(ch)
    if 'sample_aspect_ratio' in video_stream_info and video_stream_info['sample_aspect_ratio']!="0:1":
        # some video do not have the info of 'sample_aspect_ratio'
        a,b = video_stream_info['sample_aspect_ratio'].split(':')
        sar = int(a)/int(b)
    else:
        sar = dar
    par = dar/sar
    return dar