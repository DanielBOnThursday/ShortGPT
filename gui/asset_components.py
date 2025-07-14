import os
import platform
import random
import subprocess

import gradio as gr

from shortGPT.api_utils.eleven_api import ElevenLabsAPI
from shortGPT.config.api_db import ApiKeyManager
from shortGPT.config.asset_db import AssetDatabase


class AssetComponentsUtils:
    EDGE_TTS = "Free EdgeTTS (lower quality)"
    ELEVEN_TTS = "ElevenLabs(Very High Quality)"


    instance_background_video_checkbox = None
    instance_background_music_checkbox = None
    instance_voiceChoice: dict[gr.Radio] = {}
    instance_voiceChoiceTranslation: dict[gr.Radio] = {}

    @classmethod
    def getBackgroundVideoChoices(cls):
        df = AssetDatabase.get_df()
        choices = list(df.loc["background video" == df["type"]]["name"])[:20]
        return choices

    @classmethod
    def getBackgroundMusicChoices(cls):
        df = AssetDatabase.get_df()
        choices = list(df.loc["background music" == df["type"]]["name"])[:20]
        print(f"🎵 Background music choices found: {len(choices)} items")
        if choices:
            print(f"🎵 First few items: {choices[:3]}")
        else:
            print("⚠️  No background music found in database")
            # Fallback to ensure at least one option
            all_music = list(df.loc[df["type"].str.contains("music", case=False, na=False)]["name"])
            if all_music:
                print(f"🎵 Found {len(all_music)} music items with different type names")
                choices = all_music[:20]
        return choices

    @classmethod
    def getElevenlabsVoices(cls):
        api_key = ApiKeyManager.get_api_key("ELEVENLABS_API_KEY")
        voices = list(reversed(ElevenLabsAPI(api_key).get_voices().keys()))
        return voices

    @classmethod
    def start_file(cls, path):
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except FileNotFoundError:
            print(f"Cannot open file browser in container environment. Files are located at: {path}")
        except Exception as e:
            print(f"Error opening file: {e}. Files are located at: {path}")

    @classmethod
    def background_video_checkbox(cls):
        if cls.instance_background_video_checkbox is None:
            choices = cls.getBackgroundVideoChoices()
            cls.instance_background_video_checkbox = gr.CheckboxGroup(
                choices=choices,
                interactive=True,
                label="Choose background video",
                value=random.choice(choices)
            )
        return cls.instance_background_video_checkbox

    @classmethod
    def background_music_checkbox(cls):
        if cls.instance_background_music_checkbox is None:
            choices = cls.getBackgroundMusicChoices()
            
            # Handle empty choices to prevent UI issues
            if not choices:
                print("⚠️  No background music found, creating empty component")
                choices = ["No background music available"]
                default_value = []
            else:
                default_value = [random.choice(choices)]
            
            cls.instance_background_music_checkbox = gr.CheckboxGroup(
                choices=choices,
                interactive=True,
                label="Choose background music",
                value=default_value
            )
        return cls.instance_background_music_checkbox

    @classmethod
    def voiceChoice(cls, provider: str = None):
        if provider == None:
            provider = cls.ELEVEN_TTS
        if cls.instance_voiceChoice.get(provider, None) is None:
            if provider == cls.ELEVEN_TTS:
                cls.instance_voiceChoice[provider] = gr.Radio(
                    cls.getElevenlabsVoices(),
                    label="Elevenlabs voice",
                    value="Chris",
                    interactive=True,
                )
        return cls.instance_voiceChoice[provider]

    @classmethod
    def voiceChoiceTranslation(cls, provider: str = None):
        if provider == None:
            provider = cls.ELEVEN_TTS
        if cls.instance_voiceChoiceTranslation.get(provider, None) is None:
            if provider == cls.ELEVEN_TTS:
                cls.instance_voiceChoiceTranslation[provider] = gr.Radio(
                    cls.getElevenlabsVoices(),
                    label="Elevenlabs voice",
                    value="Chris",
                    interactive=True,
                )
        return cls.instance_voiceChoiceTranslation[provider]
