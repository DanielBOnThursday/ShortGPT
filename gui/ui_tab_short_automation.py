import os
import time
import traceback

import gradio as gr

from gui.asset_components import AssetComponentsUtils
from gui.ui_abstract_component import AbstractComponentUI
from gui.ui_components_html import GradioComponentsHTML
from shortGPT.audio.edge_voice_module import EdgeTTSVoiceModule
from shortGPT.audio.eleven_voice_module import ElevenLabsVoiceModule
from shortGPT.config.api_db import ApiKeyManager
from shortGPT.config.languages import (EDGE_TTS_VOICENAME_MAPPING,
                                       ELEVEN_SUPPORTED_LANGUAGES,
                                       LANGUAGE_ACRONYM_MAPPING,
                                       Language)
from shortGPT.engine.facts_short_engine import FactsShortEngine
from shortGPT.engine.reddit_short_engine import RedditShortEngine
class ShortAutomationUI(AbstractComponentUI):
    def __init__(self, shortGptUI: gr.Blocks):
        self.shortGptUI = shortGptUI
        self.embedHTML = '<div style="display: flex; overflow-x: auto; gap: 20px;">'
        self.progress_counter = 0
        self.short_automation = None
        self.generated_videos = []  # Track generated video paths for S3 upload

    def create_ui(self):
        with gr.Row(visible=False) as short_automation:
            with gr.Column():
                numShorts = gr.Number(label="Number of shorts", minimum=1, value=1)
                short_type = gr.Radio(["Reddit Story shorts", "Historical Facts shorts", "Scientific Facts shorts", "Custom Facts shorts"], label="Type of shorts generated", value="Reddit Story shorts", interactive=True)
                facts_subject = gr.Textbox(label="Write a subject for your facts (example: Football facts)", interactive=True, visible=False)
                short_type.change(lambda x: gr.update(visible=x == "Custom Facts shorts"), [short_type], [facts_subject])
                tts_engine = gr.Radio([AssetComponentsUtils.ELEVEN_TTS, AssetComponentsUtils.EDGE_TTS], label="Text to speech engine", value=AssetComponentsUtils.EDGE_TTS, interactive=True)
                self.tts_engine = tts_engine.value
                with gr.Column(visible=False) as eleven_tts:
                    language_eleven = gr.Radio([lang.value for lang in ELEVEN_SUPPORTED_LANGUAGES], label="Language", value="English", interactive=True)
                    voice_eleven = AssetComponentsUtils.voiceChoice(provider=AssetComponentsUtils.ELEVEN_TTS)
                with gr.Column(visible=True) as edge_tts:
                    language_edge = gr.Dropdown([lang.value.upper() for lang in Language], label="Language", value="ENGLISH", interactive=True)
                def tts_engine_change(x):
                    self.tts_engine = x
                    return gr.update(visible=x == AssetComponentsUtils.ELEVEN_TTS), gr.update(visible=x == AssetComponentsUtils.EDGE_TTS)
                tts_engine.change(tts_engine_change, tts_engine, [eleven_tts, edge_tts])

                useImages = gr.Checkbox(label="Use images", value=True)
                numImages = gr.Radio([5, 10, 25], value=10, label="Number of images per short", visible=True, interactive=True)
                useImages.change(lambda x: gr.update(visible=x), useImages, numImages)

                addWatermark = gr.Checkbox(label="Add watermark")
                watermark = gr.Textbox(label="Watermark (your channel name)", visible=False)
                addWatermark.change(lambda x: gr.update(visible=x), [addWatermark], [watermark])

                AssetComponentsUtils.background_video_checkbox()
                AssetComponentsUtils.background_music_checkbox()
                createButton = gr.Button("Create Shorts")
                
                # S3 Upload controls
                with gr.Row():
                    upload_to_s3_btn = gr.Button("📤 Upload Generated Videos to S3", visible=False, variant="secondary")
                    s3_upload_status = gr.HTML(visible=False)

                generation_error = gr.HTML(visible=False)
                video_folder = gr.Button("📁", visible=True)
                output = gr.HTML('<div style="min-height: 80px;"></div>')

            video_folder.click(lambda _: AssetComponentsUtils.start_file(os.path.abspath("videos/")))

            createButton.click(self.inspect_create_inputs, inputs=[AssetComponentsUtils.background_video_checkbox(), AssetComponentsUtils.background_music_checkbox(), watermark, short_type, facts_subject], outputs=[generation_error]).success(self.create_short, inputs=[
                numShorts,
                short_type,
                tts_engine,
                language_eleven,
                language_edge,
                numImages,
                watermark,
                AssetComponentsUtils.background_video_checkbox(),
                AssetComponentsUtils.background_music_checkbox(),
                facts_subject,
                voice_eleven,
            ], outputs=[output, video_folder, generation_error, upload_to_s3_btn])
            
            # S3 Upload functionality
            upload_to_s3_btn.click(self.upload_videos_to_s3, inputs=[short_type], outputs=[s3_upload_status])
        self.short_automation = short_automation
        return self.short_automation

    def create_short(self, numShorts, short_type, tts_engine, language_eleven, language_edge, numImages, watermark, background_video_list, background_music_list, facts_subject, voice_eleven, progress=gr.Progress()):
        '''Creates a short'''

        try:
            # Reset generated videos list for new session
            self.generated_videos = []
            numShorts = int(numShorts)
            numImages = int(numImages) if numImages else None
            background_videos = (background_video_list * ((numShorts // len(background_video_list)) + 1))[:numShorts]
            background_musics = (background_music_list * ((numShorts // len(background_music_list)) + 1))[:numShorts]
            if tts_engine == AssetComponentsUtils.ELEVEN_TTS:
                language = Language(language_eleven.lower().capitalize())
                voice_module = ElevenLabsVoiceModule(ApiKeyManager.get_api_key('ELEVENLABS_API_KEY'), voice_eleven, checkElevenCredits=True)
            elif tts_engine == AssetComponentsUtils.EDGE_TTS:
                language = Language(language_edge.lower().capitalize())
                voice_module = EdgeTTSVoiceModule(EDGE_TTS_VOICENAME_MAPPING[language]['male'])
            for i in range(numShorts):
                shortEngine = self.create_short_engine(short_type=short_type, voice_module=voice_module, language=language, numImages=numImages, watermark=watermark,
                                                       background_video=background_videos[i], background_music=background_musics[i], facts_subject=facts_subject)
                num_steps = shortEngine.get_total_steps()

                def logger(prog_str):
                    progress(self.progress_counter / (num_steps * numShorts), f"Making short {i+1}/{numShorts} - {prog_str}")
                shortEngine.set_logger(logger)

                for step_num, step_info in shortEngine.makeContent():
                    print(step_num, step_info,self.progress_counter )
                    progress(self.progress_counter / (num_steps * numShorts), f"Making short {i+1}/{numShorts} - {step_info}")
                    self.progress_counter += 1

                video_path = shortEngine.get_video_output_path()
                # Track generated video for S3 upload
                self.generated_videos.append({"path": video_path, "type": short_type})
                
                current_url = self.shortGptUI.share_url+"/" if self.shortGptUI.share else self.shortGptUI.local_url
                file_url_path = f"{current_url}gradio_api/file={video_path}"
                file_name = video_path.split("/")[-1].split("\\")[-1]
                
                # Use enhanced video template with S3 upload
                try:
                    from gui.s3_gui_utils import get_enhanced_video_template
                    video_html = get_enhanced_video_template(
                        file_url_path=file_url_path,
                        file_name=file_name,
                        video_path=video_path,  # Local path for S3 upload
                        width="250",
                        height="500",
                        show_s3_upload=True
                    )
                    self.embedHTML += video_html
                except ImportError:
                    # Fallback to original template
                    self.embedHTML += f'''
                    <div style="display: flex; flex-direction: column; align-items: center;">
                        <video width="{250}" height="{500}" style="max-height: 100%;" controls>
                            <source src="{file_url_path}" type="video/mp4">
                            Your browser does not support the video tag.
                        </video>
                        <div style="margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
                            <a href="{file_url_path}" download="{file_name}">
                                <button style="font-size: 1em; padding: 10px; border: none; cursor: pointer; color: white; background: #007bff;">💾 Download Video</button>
                            </a>
                            <button style="font-size: 1em; padding: 10px; border: none; cursor: pointer; color: white; background: #28a745;"
                                    onclick="alert('S3 upload will be available soon!')">📤 Upload to S3</button>
                        </div>
                    </div>'''
                yield self.embedHTML + '</div>', gr.update(visible=True), gr.update(visible=False), gr.update(visible=True)
        except Exception as e:
            traceback_str = ''.join(traceback.format_tb(e.__traceback__))
            error_name = type(e).__name__.capitalize() + " : " + f"{e.args[0]}"
            print("Error", traceback_str)
            error_html = GradioComponentsHTML.get_html_error_template().format(error_message=error_name, stack_trace=traceback_str)
            yield self.embedHTML + '</div>', gr.update(visible=True), gr.update(value=error_html, visible=True), gr.update(visible=False)
    def inspect_create_inputs(self, background_video_list, background_music_list, watermark, short_type, facts_subject, progress=gr.Progress()):
        if short_type == "Custom Facts shorts":
            if not facts_subject:
                raise gr.Error("Please write down your facts short's subject")
        if not background_video_list:
            raise gr.Error("Please select at least one background video.")

        if not background_music_list:
            raise gr.Error("Please select at least one background music.")

        if watermark != "":
            if not watermark.replace(" ", "").isalnum():
                raise gr.Error("Watermark should only contain letters and numbers.")
            if len(watermark) > 25:
                raise gr.Error("Watermark should not exceed 25 characters.")
            if len(watermark) < 3:
                raise gr.Error("Watermark should be at least 3 characters long.")

        openai_key = ApiKeyManager.get_api_key("OPENAI_API_KEY")
        gemini_key = ApiKeyManager.get_api_key("GEMINI_API_KEY")
        if not openai_key and not gemini_key:
            raise gr.Error("GEMINI OR OPENAI API key is missing. Please go to the config tab and enter the API key.")
        eleven_labs_key = ApiKeyManager.get_api_key("ELEVENLABS_API_KEY")
        if self.tts_engine == AssetComponentsUtils.ELEVEN_TTS and not eleven_labs_key:
            raise gr.Error("ELEVENLABS_API_KEY API key is missing. Please go to the config tab and enter the API key.")
        return gr.update(visible=False)

    def create_short_engine(self, short_type, voice_module, language, numImages, watermark, background_video, background_music, facts_subject):
        if short_type == "Reddit Story shorts":
            return RedditShortEngine(voice_module, background_video_name=background_video, background_music_name=background_music, num_images=numImages, watermark=watermark, language=language)
        if "fact" in short_type.lower():
            if "custom" in short_type.lower():
                facts_subject = facts_subject
            else:
                facts_subject = short_type
            return FactsShortEngine(voice_module, facts_type=facts_subject, background_video_name=background_video, background_music_name=background_music, num_images=numImages, watermark=watermark, language=language)
        raise gr.Error(f"Short type does not have a valid short engine: {short_type}")

    def upload_videos_to_s3(self, short_type, progress=gr.Progress()):
        """Upload all generated videos to S3"""
        if not self.generated_videos:
            return '<div style="color: red;">❌ No videos found to upload. Please generate videos first.</div>'
        
        try:
            from gui.s3_gui_utils import upload_video_to_s3
            
            upload_results = []
            total_videos = len(self.generated_videos)
            
            for i, video_info in enumerate(self.generated_videos):
                video_path = video_info["path"]
                video_type = video_info["type"]
                
                progress((i + 1) / total_videos, f"Uploading video {i+1}/{total_videos}...")
                
                # Map short type to content type
                content_type_mapping = {
                    "Reddit Story shorts": "reddit_story",
                    "Historical Facts shorts": "historical_facts", 
                    "Scientific Facts shorts": "scientific_facts",
                    "Custom Facts shorts": "custom_facts"
                }
                content_type = content_type_mapping.get(video_type, "custom_content")
                
                success, message = upload_video_to_s3(video_path, content_type)
                
                video_name = os.path.basename(video_path)
                if success:
                    upload_results.append(f'<div style="color: green; margin: 5px 0;">✅ {video_name}: {message}</div>')
                else:
                    upload_results.append(f'<div style="color: red; margin: 5px 0;">❌ {video_name}: {message}</div>')
            
            # Create summary
            successful_uploads = sum(1 for result in upload_results if "✅" in result)
            total_uploads = len(upload_results)
            
            summary = f'''
            <div style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h3 style="margin-top: 0;">📤 S3 Upload Results</h3>
                <p><strong>Success:</strong> {successful_uploads}/{total_uploads} videos uploaded</p>
                <div style="max-height: 300px; overflow-y: auto;">
                    {"".join(upload_results)}
                </div>
            </div>
            '''
            
            return summary
            
        except ImportError:
            return '<div style="color: red;">❌ S3 upload functionality not available. Please check S3 configuration.</div>'
        except Exception as e:
            return f'<div style="color: red;">❌ Upload failed: {str(e)}</div>'
