"""
Speech-to-Text Service using OpenAI Whisper
Transcribes emergency calls and voice inputs.
"""
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import tempfile
from openai import AsyncOpenAI
from openai import OpenAIError

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhisperService:
    """OpenAI Whisper service for speech-to-text."""
    
    def __init__(self):
        """Initialize Whisper client."""
        self.client = None
        if settings.OPENAI_API_KEY:
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ Whisper client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Whisper: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not configured")
    
    def is_available(self) -> bool:
        """Check if Whisper service is available."""
        return self.client is not None
    
    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to audio file (mp3, mp4, mpeg, mpga, m4a, wav, webm)
            language: Optional ISO-639-1 language code (e.g., 'en', 'hi')
            prompt: Optional prompt to guide transcription
            
        Returns:
            {
                "text": str,
                "language": str,
                "duration": float (if available),
                "confidence": float (if available)
            }
        """
        if not self.is_available():
            logger.error("Whisper service not available")
            return None
        
        try:
            # Open audio file
            with open(audio_file_path, 'rb') as audio_file:
                # Build request parameters
                kwargs = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "verbose_json"
                }
                
                if language:
                    kwargs["language"] = language
                
                if prompt:
                    kwargs["prompt"] = prompt
                
                # Transcribe
                transcript = await self.client.audio.transcriptions.create(**kwargs)
                
                result = {
                    "text": transcript.text,
                    "language": transcript.language if hasattr(transcript, 'language') else language,
                    "duration": transcript.duration if hasattr(transcript, 'duration') else None
                }
                
                logger.info(f"✅ Transcribed audio: {len(transcript.text)} characters")
                return result
                
        except OpenAIError as e:
            logger.error(f"Whisper API error: {e}")
            return None
        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_file_path}")
            return None
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None
    
    async def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.mp3",
        language: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe audio from bytes.
        
        Args:
            audio_bytes: Audio file bytes
            filename: Filename with extension
            language: Optional language code
            
        Returns:
            Transcription result
        """
        if not self.is_available():
            return None
        
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                suffix=Path(filename).suffix,
                delete=False
            ) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            # Transcribe
            result = await self.transcribe_audio(temp_path, language)
            
            # Clean up
            Path(temp_path).unlink()
            
            return result
            
        except Exception as e:
            logger.error(f"Bytes transcription error: {e}")
            return None
    
    async def translate_audio(
        self,
        audio_file_path: str
    ) -> Optional[str]:
        """
        Transcribe and translate audio to English.
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Translated text in English
        """
        if not self.is_available():
            return None
        
        try:
            with open(audio_file_path, 'rb') as audio_file:
                translation = await self.client.audio.translations.create(
                    model="whisper-1",
                    file=audio_file
                )
                
                logger.info(f"✅ Translated audio: {len(translation.text)} characters")
                return translation.text
                
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
    
    async def extract_emergency_info(
        self,
        transcribed_text: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract emergency information from transcribed text using LLM.
        
        Args:
            transcribed_text: Transcribed emergency call
            
        Returns:
            Extracted emergency information
        """
        try:
            from app.services.llm.llm_service import llm_service
            
            # Use LLM to parse the transcription
            result = await llm_service.parse_incident_description(
                description=transcribed_text,
                caller_statement=transcribed_text
            )
            
            if result:
                result["transcription"] = transcribed_text
            
            return result
            
        except Exception as e:
            logger.error(f"Info extraction error: {e}")
            return None
    
    def supported_formats(self) -> list:
        """Get list of supported audio formats."""
        return [
            "mp3", "mp4", "mpeg", "mpga", 
            "m4a", "wav", "webm", "flac"
        ]
    
    def validate_audio_format(self, filename: str) -> bool:
        """
        Validate if audio format is supported.
        
        Args:
            filename: Audio filename
            
        Returns:
            True if supported
        """
        extension = Path(filename).suffix.lstrip('.').lower()
        return extension in self.supported_formats()


# Global instance
whisper_service = WhisperService()
