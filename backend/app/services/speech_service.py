"""
Speech-to-Text Service (OpenAI Whisper)
Provides audio transcription with language detection
"""
import logging
from typing import Dict, Optional
import os
import tempfile
from pathlib import Path
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class SpeechService:
    """Whisper API service for speech-to-text"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "whisper-1"
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize OpenAI client for Whisper"""
        try:
            if self.api_key:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("Whisper client initialized successfully")
            else:
                logger.warning("OpenAI API key not configured for Whisper")
        except Exception as e:
            logger.error(f"Failed to initialize Whisper client: {str(e)}")
            self.client = None
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        filename: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio file bytes
            filename: Original filename (for format detection)
            language: ISO-639-1 language code (e.g., 'en', 'es')
            prompt: Optional prompt to guide transcription
            
        Returns:
            Dict with transcript, language, duration
        """
        if not self.client:
            logger.warning("Whisper client not available")
            return None
        
        # Validate file format
        supported_formats = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm'}
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in supported_formats:
            logger.error(f"Unsupported audio format: {file_ext}")
            return {
                "error": f"Unsupported format. Supported: {', '.join(supported_formats)}",
                "transcript": None
            }
        
        # Check file size (max 25MB for Whisper)
        max_size = 25 * 1024 * 1024  # 25MB
        if len(audio_data) > max_size:
            logger.error(f"Audio file too large: {len(audio_data)} bytes")
            return {
                "error": "Audio file must be less than 25MB",
                "transcript": None
            }
        
        temp_file = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcribe audio
            with open(temp_file_path, 'rb') as audio_file:
                params = {
                    "model": self.model,
                    "file": audio_file,
                    "response_format": "verbose_json"
                }
                
                if language:
                    params["language"] = language
                
                if prompt:
                    params["prompt"] = prompt
                
                response = await self.client.audio.transcriptions.create(**params)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            result = {
                "transcript": response.text,
                "language": response.language if hasattr(response, 'language') else language,
                "duration": response.duration if hasattr(response, 'duration') else None,
                "segments": []
            }
            
            # Add segments if available
            if hasattr(response, 'segments') and response.segments:
                result["segments"] = [
                    {
                        "id": seg.id,
                        "start": seg.start,
                        "end": seg.end,
                        "text": seg.text
                    }
                    for seg in response.segments
                ]
            
            logger.info(f"Transcription completed: {len(response.text)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            
            # Clean up temp file on error
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            return {
                "error": str(e),
                "transcript": None
            }
    
    async def transcribe_emergency_call(
        self,
        audio_data: bytes,
        filename: str,
        caller_info: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Transcribe emergency call with context-aware prompting
        
        Args:
            audio_data: Audio file bytes
            filename: Original filename
            caller_info: Optional caller information
            
        Returns:
            Dict with transcript and extracted information
        """
        # Use a prompt to improve accuracy for emergency calls
        prompt = """Emergency call transcript. Include medical terms, locations, names, phone numbers accurately. 
Common terms: ambulance, hospital, injury, cardiac arrest, breathing difficulty, bleeding, trauma, 
consciousness, pulse, blood pressure, accident location, victim count."""
        
        result = await self.transcribe_audio(
            audio_data=audio_data,
            filename=filename,
            language="en",  # Default to English, could be detected
            prompt=prompt
        )
        
        if not result or not result.get("transcript"):
            return result
        
        # Add emergency call specific processing
        transcript = result["transcript"]
        
        # Extract key information (simple keyword matching)
        keywords = {
            "urgency": self._detect_urgency_keywords(transcript),
            "medical_terms": self._extract_medical_terms(transcript),
            "location_mentioned": self._has_location_mention(transcript),
            "victim_count": self._extract_victim_count(transcript)
        }
        
        result["emergency_analysis"] = keywords
        result["caller_info"] = caller_info
        
        logger.info(f"Emergency call transcribed: urgency={keywords['urgency']}")
        return result
    
    def _detect_urgency_keywords(self, text: str) -> str:
        """Detect urgency level from transcript"""
        text_lower = text.lower()
        
        critical_keywords = ['cardiac arrest', 'not breathing', 'unconscious', 'severe bleeding', 
                            'chest pain', 'stroke', 'choking', 'critical', 'dying']
        high_keywords = ['bleeding', 'broken bone', 'fall', 'accident', 'pain', 'injury']
        
        for keyword in critical_keywords:
            if keyword in text_lower:
                return "critical"
        
        for keyword in high_keywords:
            if keyword in text_lower:
                return "high"
        
        return "medium"
    
    def _extract_medical_terms(self, text: str) -> list:
        """Extract medical terms from transcript"""
        medical_terms = [
            'cardiac arrest', 'heart attack', 'stroke', 'seizure', 'bleeding', 
            'fracture', 'unconscious', 'breathing', 'pulse', 'blood pressure',
            'allergic reaction', 'diabetic', 'asthma', 'overdose', 'trauma',
            'burn', 'laceration', 'concussion', 'chest pain', 'shortness of breath'
        ]
        
        text_lower = text.lower()
        found_terms = [term for term in medical_terms if term in text_lower]
        return found_terms
    
    def _has_location_mention(self, text: str) -> bool:
        """Check if location is mentioned in transcript"""
        location_keywords = ['street', 'avenue', 'road', 'highway', 'building', 
                            'floor', 'apartment', 'house', 'address', 'location', 'at']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in location_keywords)
    
    def _extract_victim_count(self, text: str) -> Optional[int]:
        """Try to extract number of victims from transcript"""
        text_lower = text.lower()
        
        # Check for explicit numbers
        count_patterns = [
            ('one person', 1), ('two people', 2), ('three people', 3),
            ('multiple', 2), ('several', 2), ('many', 3)
        ]
        
        for pattern, count in count_patterns:
            if pattern in text_lower:
                return count
        
        # Check for single digit numbers followed by victim-related words
        import re
        matches = re.findall(r'(\d+)\s+(person|people|victim|patient)', text_lower)
        if matches:
            try:
                return int(matches[0][0])
            except:
                pass
        
        return 1  # Default to 1 if not specified
    
    async def translate_audio(
        self,
        audio_data: bytes,
        filename: str,
        target_language: str = "en"
    ) -> Optional[Dict]:
        """
        Translate audio to target language (English by default)
        
        Args:
            audio_data: Audio file bytes
            filename: Original filename
            target_language: Target language code (currently only 'en' supported by Whisper)
            
        Returns:
            Dict with translated transcript
        """
        if not self.client:
            return None
        
        if target_language != "en":
            logger.warning("Whisper translation only supports English target language")
        
        temp_file = None
        try:
            file_ext = Path(filename).suffix.lower()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Use translation endpoint
            with open(temp_file_path, 'rb') as audio_file:
                response = await self.client.audio.translations.create(
                    model=self.model,
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            os.unlink(temp_file_path)
            
            result = {
                "original_language": response.language if hasattr(response, 'language') else "unknown",
                "translated_text": response.text,
                "target_language": "en",
                "duration": response.duration if hasattr(response, 'duration') else None
            }
            
            logger.info(f"Translation completed: {len(response.text)} characters")
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
            
            return {
                "error": str(e),
                "translated_text": None
            }


# Global instance
speech_service = SpeechService()
