import os
import random
import yt_dlp
import subprocess
import json

def getYoutubeVideoLink(url):
    format_filter = "[height<=1920]" if 'shorts' in url else "[height<=1080]"
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "no_color": True,
        "no_call_home": True,
        "no_check_certificate": True,
        # Look for m3u8 formats first, then fall back to regular formats
        "format": f"bestvideo[ext=m3u8]{format_filter}/bestvideo{format_filter}"
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            dictMeta = ydl.extract_info(
                url,
                download=False)
            return dictMeta['url'], dictMeta['duration']
    except Exception as e:
        raise Exception(f"Failed getting video link from the following video/url {url} {e.args[0]}")

def extract_random_clip_from_video(video_url, video_duration, clip_duration, output_file):
    """Extracts a clip from a video using a signed URL.
    Args:
        video_url (str): The signed URL of the video.
        video_url (int): Duration of the video.
        start_time (int): The start time of the clip in seconds.
        clip_duration (int): The duration of the clip in seconds.
        output_file (str): The output file path for the extracted clip.
    """
    if not video_duration:
        raise Exception("Could not get video duration")
    if not video_duration*0.7 > 120:
        raise Exception("Video too short")
    start_time = video_duration*0.15 + random.random()* (0.7*video_duration-clip_duration)
    
    # Choose codec and preset based on GPU availability
    import os
    import torch
    
    # Try GPU encoding first if available
    if torch.cuda.is_available() and os.getenv('FFMPEG_GPU', '0') == '1':
        video_codec = 'h264_nvenc'
        preset = 'fast'
        
        command = [
            'ffmpeg',
            '-loglevel', 'error',
            '-ss', str(start_time),
            '-t', str(clip_duration),
            '-i', video_url,
            '-c:v', video_codec,
            '-preset', preset,
            output_file
        ]
        
        try:
            print("🎮 Video clipping with GPU: h264_nvenc")
            subprocess.run(command, check=True)
            return  # Success with GPU
        except subprocess.CalledProcessError as e:
            print("⚠️  GPU encoding failed, falling back to CPU...")
            print(f"GPU error: {e}")
            # Fall through to CPU encoding
    
    # CPU encoding (fallback or default)
    print("💻 Video clipping with CPU: libx264")
    command = [
        'ffmpeg',
        '-loglevel', 'error',
        '-ss', str(start_time),
        '-t', str(clip_duration),
        '-i', video_url,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        output_file
    ]
    
    try:
        subprocess.run(command, check=True)
        
        if not os.path.exists(output_file):
            raise Exception(f"Random clip failed to be written to {output_file}")
        
        print(f"✅ Video clip created successfully: {output_file}")
        return output_file
        
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg command failed: {e}")
        print(f"Command: {' '.join(command)}")
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