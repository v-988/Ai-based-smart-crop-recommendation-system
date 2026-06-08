"""
Speech Processing Service
Handles voice input (speech-to-text) and voice output (text-to-speech).
"""

import os
import io
import tempfile
from typing import Optional
from loguru import logger

from config.settings import settings
from models.schemas import LanguageEnum
from utils.helpers import generate_temp_filename, get_language_code

# Lazy-load optional audio dependencies so the services package
# can be imported even when gtts/SpeechRecognition/pydub are absent.
def _get_gTTS():
    try:
        from gtts import gTTS
        return gTTS
    except ImportError:
        raise ImportError("gtts is not installed. Run: pip install gtts")

def _get_sr():
    try:
        import speech_recognition as sr
        return sr
    except ImportError:
        raise ImportError("SpeechRecognition is not installed. Run: pip install SpeechRecognition")

def _get_AudioSegment():
    try:
        from pydub import AudioSegment
        return AudioSegment
    except ImportError:
        raise ImportError("pydub is not installed. Run: pip install pydub")


class SpeechService:
    """
    Service for speech processing including:
    - Speech-to-Text (STT) using Google Speech Recognition
    - Text-to-Speech (TTS) using Google TTS
    """
    
    def __init__(self):
        """Initialize speech service with configuration."""
        self.temp_dir = settings.TEMP_AUDIO_DIR
        try:
            sr = _get_sr()
            self.recognizer = sr.Recognizer()
        except ImportError:
            self.recognizer = None
            logger.warning("SpeechRecognition not available. Speech-to-text will be disabled.")

        self._configure_audio_tools()
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Language mappings
        self.tts_language_codes = {
            LanguageEnum.ENGLISH: "en",
            LanguageEnum.TAMIL: "ta"
        }
        
        self.stt_language_codes = {
            LanguageEnum.ENGLISH: "en-US",
            LanguageEnum.TAMIL: "ta-IN"
        }

    def _configure_audio_tools(self) -> None:
        """Configure FFmpeg path for pydub using bundled binary when available."""
        try:
            from imageio_ffmpeg import get_ffmpeg_exe
            AudioSegment = _get_AudioSegment()
            ffmpeg_exe = get_ffmpeg_exe()
            AudioSegment.converter = ffmpeg_exe
            ffprobe_candidate = ffmpeg_exe.replace("ffmpeg", "ffprobe")
            if os.path.exists(ffprobe_candidate):
                AudioSegment.ffprobe = ffprobe_candidate
            logger.info(f"Configured FFmpeg for audio conversion: {ffmpeg_exe}")
        except Exception:
            logger.warning(
                "Bundled FFmpeg not available. Install imageio-ffmpeg or system FFmpeg for non-WAV formats."
            )
    
    async def speech_to_text(
        self,
        audio_bytes: bytes,
        language: Optional[LanguageEnum] = None,
        filename: Optional[str] = None
    ) -> tuple[str, LanguageEnum]:
        """
        Convert speech audio to text.
        
        Args:
            audio_bytes: Audio file bytes
            language: Optional language hint
            
        Returns:
            Tuple of (transcribed text, detected language)
        """
        sr = _get_sr()
        temp_input = None
        temp_wav = None
        
        try:
            logger.info("Starting speech-to-text conversion...")
            
            # Save uploaded audio to temp file
            ext = os.path.splitext(filename or "")[1].lower()
            temp_suffix = ext if ext else ".audio"
            temp_input = os.path.join(
                self.temp_dir,
                generate_temp_filename(temp_suffix)
            )
            with open(temp_input, "wb") as f:
                f.write(audio_bytes)
            
            # Convert to WAV format
            temp_wav = os.path.join(
                self.temp_dir,
                generate_temp_filename(".wav")
            )
            
            try:
                if ext in [".wav", ".wave"]:
                    # Native WAV path does not require FFmpeg.
                    with open(temp_wav, "wb") as f:
                        f.write(audio_bytes)
                else:
                    from imageio_ffmpeg import get_ffmpeg_exe
                    import subprocess
                    
                    ffmpeg_exe = get_ffmpeg_exe()
                    # Call ffmpeg directly to convert WebM to WAV natively 
                    # without needing ffprobe (which pydub requires and imageio-ffmpeg lacks)
                    subprocess.run(
                        [
                            ffmpeg_exe, 
                            "-y",           # overwrite output
                            "-i", temp_input, # input file
                            "-ac", "1",     # mono path
                            "-ar", "16000", # 16kHz typical for STT
                            temp_wav
                        ],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            except Exception as e:
                logger.error(f"Audio conversion error: {e}")
                raise Exception(
                    "Audio conversion failed. Install FFmpeg for MP3/WebM/OGG or upload WAV."
                )
            
            # Perform speech recognition
            with sr.AudioFile(temp_wav) as source:
                audio_data = self.recognizer.record(source)
            
            # Try recognition with multiple languages
            text = None
            detected_lang = language or LanguageEnum.ENGLISH
            
            if language:
                # Use specified language
                lang_code = self.stt_language_codes.get(language, "en-US")
                try:
                    text = self.recognizer.recognize_google(
                        audio_data,
                        language=lang_code
                    )
                except sr.UnknownValueError:
                    pass
            else:
                # Try Tamil first, then English
                for lang, code in [
                    (LanguageEnum.TAMIL, "ta-IN"),
                    (LanguageEnum.ENGLISH, "en-US")
                ]:
                    try:
                        text = self.recognizer.recognize_google(
                            audio_data,
                            language=code
                        )
                        detected_lang = lang
                        break
                    except sr.UnknownValueError:
                        continue
            
            if not text:
                raise Exception("Could not understand audio. Please speak clearly and try again.")
            
            logger.info(f"Transcribed: '{text[:50]}...' in {detected_lang.value}")
            return text, detected_lang
            
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            raise Exception("Speech recognition service unavailable. Please try again.")
        except Exception as e:
            logger.error(f"Speech-to-text error: {e}")
            raise
        finally:
            # Cleanup temp files
            for temp_file in [temp_input, temp_wav]:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
    
    async def text_to_speech(
        self,
        text: str,
        language: LanguageEnum = LanguageEnum.ENGLISH
    ) -> bytes:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert
            language: Output language
            
        Returns:
            Audio bytes (MP3 format)
        """
        temp_file = None
        
        try:
            logger.info(f"Converting text to speech ({language.value})...")
            
            # Get language code
            lang_code = self.tts_language_codes.get(language, "en")
            
            # Generate speech
            gTTS = _get_gTTS()
            tts = gTTS(text=text, lang=lang_code, slow=False)
            
            # Save to temp file
            temp_file = os.path.join(
                self.temp_dir,
                generate_temp_filename(".mp3")
            )
            tts.save(temp_file)
            
            # Read and return bytes
            with open(temp_file, "rb") as f:
                audio_bytes = f.read()
            
            logger.info(f"Generated {len(audio_bytes)} bytes of audio")
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Text-to-speech error: {e}")
            raise Exception("Failed to generate speech. Please try again.")
        finally:
            # Cleanup
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    async def text_to_speech_stream(
        self,
        text: str,
        language: LanguageEnum = LanguageEnum.ENGLISH
    ) -> io.BytesIO:
        """
        Convert text to speech and return as BytesIO stream.
        Useful for streaming responses.
        
        Args:
            text: Text to convert
            language: Output language
            
        Returns:
            BytesIO stream of MP3 audio
        """
        try:
            audio_bytes = await self.text_to_speech(text, language)
            return io.BytesIO(audio_bytes)
        except Exception as e:
            logger.error(f"TTS stream error: {e}")
            raise
    
    def detect_language_from_text(self, text: str) -> LanguageEnum:
        """
        Detect language from text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Detected language
        """
        try:
            from langdetect import detect
            lang_code = detect(text)
            
            if lang_code == "ta":
                return LanguageEnum.TAMIL
            else:
                return LanguageEnum.ENGLISH
        except:
            return LanguageEnum.ENGLISH


# Singleton instance
speech_service = SpeechService()
