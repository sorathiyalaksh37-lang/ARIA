"""
Vision AI Service (GPT-4 Vision)
Provides image analysis for injury detection and severity assessment
"""
import logging
from typing import Dict, List, Optional
import base64
from io import BytesIO
from PIL import Image
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """GPT-4 Vision service for image analysis"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4-vision-preview"
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize OpenAI client for Vision"""
        try:
            if self.api_key:
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info("GPT-4 Vision client initialized successfully")
            else:
                logger.warning("OpenAI API key not configured for Vision")
        except Exception as e:
            logger.error(f"Failed to initialize Vision client: {str(e)}")
            self.client = None
    
    def _prepare_image(
        self,
        image_data: bytes,
        max_size: tuple = (1024, 1024)
    ) -> Optional[str]:
        """
        Prepare image for API: resize and convert to base64
        
        Args:
            image_data: Raw image bytes
            max_size: Maximum dimensions (width, height)
            
        Returns:
            Base64 encoded image string or None
        """
        try:
            # Open image
            image = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode not in ('RGB', 'RGBA'):
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to base64
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Image preparation error: {str(e)}")
            return None
    
    async def analyze_injury_image(
        self,
        image_data: bytes,
        additional_context: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Analyze injury image and assess severity
        
        Args:
            image_data: Image file bytes
            additional_context: Additional context about the incident
            
        Returns:
            Dict with injury analysis
        """
        if not self.client:
            logger.warning("Vision client not available")
            return None
        
        # Prepare image
        base64_image = self._prepare_image(image_data)
        if not base64_image:
            return {
                "error": "Failed to process image",
                "analysis": None
            }
        
        try:
            context_prompt = f"\n\nAdditional Context: {additional_context}" if additional_context else ""
            
            prompt = f"""Analyze this injury/medical emergency image as an emergency medical expert.{context_prompt}

Provide detailed analysis in JSON format:
1. injury_detected: true/false
2. injury_types: List of detected injuries (e.g., "laceration", "fracture", "burn")
3. severity: "critical", "severe", "moderate", "minor", or "none"
4. body_parts_affected: List of affected body parts
5. visible_symptoms: List of visible symptoms or conditions
6. bleeding: "severe", "moderate", "minor", or "none"
7. urgent_care_needed: true/false
8. recommended_actions: List of immediate actions needed
9. special_equipment: List of special equipment needed
10. transport_method: "ambulance", "air_ambulance", "non_urgent", or "self_transport"
11. estimated_golden_hour: true/false (is this time-critical injury?)
12. confidence_score: 0-100 confidence in assessment
13. warnings: Any important warnings or caveats
14. description: Brief description of what you see

IMPORTANT: 
- Be conservative in severity assessment
- Note if image quality affects analysis
- Always recommend professional medical evaluation
- Do not provide definitive diagnosis"""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_image,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            logger.info(f"Injury analysis completed: severity={analysis.get('severity')}")
            return {
                "analysis": analysis,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "model": self.model
            }
            
        except json.JSONDecodeError:
            # If JSON parsing fails, return the raw text
            logger.warning("Failed to parse JSON response, returning raw text")
            return {
                "analysis": {
                    "raw_analysis": response.choices[0].message.content,
                    "error": "Failed to parse structured response"
                },
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Injury analysis error: {str(e)}")
            return {
                "error": str(e),
                "analysis": None
            }
    
    async def analyze_scene_image(
        self,
        image_data: bytes,
        analysis_focus: str = "safety"
    ) -> Optional[Dict]:
        """
        Analyze emergency scene image for hazards and context
        
        Args:
            image_data: Image file bytes
            analysis_focus: "safety", "access", "resources", or "general"
            
        Returns:
            Dict with scene analysis
        """
        if not self.client:
            return None
        
        base64_image = self._prepare_image(image_data)
        if not base64_image:
            return {"error": "Failed to process image"}
        
        focus_prompts = {
            "safety": "Focus on safety hazards, dangerous conditions, and environmental risks.",
            "access": "Focus on access routes, obstacles, and navigation challenges for emergency vehicles.",
            "resources": "Focus on available resources, equipment needed, and logistical considerations.",
            "general": "Provide general scene assessment."
        }
        
        try:
            prompt = f"""Analyze this emergency scene image. {focus_prompts.get(analysis_focus, '')}

Provide analysis in JSON format:
1. scene_type: Type of scene (traffic accident, fire, collapse, etc.)
2. location_type: indoor/outdoor/vehicle/other
3. hazards: List of identified hazards and dangers
4. safety_concerns: List of safety concerns for responders
5. access_routes: Description of access for emergency vehicles
6. obstacles: List of obstacles that may hinder response
7. weather_conditions: Visible weather conditions if outdoor
8. lighting_conditions: "good", "poor", "dark"
9. victim_visibility: Can victims be seen? true/false
10. estimated_victim_count: Rough estimate if visible
11. special_equipment_needed: List of special equipment for scene
12. staging_area_suggestions: Suggested staging areas for vehicles
13. scene_complexity: "simple", "moderate", "complex"
14. additional_resources: Additional resources that may be needed
15. description: Brief scene description

Be thorough and prioritize responder safety."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": base64_image,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            
            logger.info(f"Scene analysis completed: type={analysis.get('scene_type')}")
            return {
                "analysis": analysis,
                "focus": analysis_focus,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Scene analysis error: {str(e)}")
            return {"error": str(e), "analysis": None}
    
    async def compare_injury_progression(
        self,
        before_image: bytes,
        after_image: bytes
    ) -> Optional[Dict]:
        """
        Compare two images to assess injury progression or treatment effectiveness
        
        Args:
            before_image: Earlier image bytes
            after_image: Later image bytes
            
        Returns:
            Dict with comparison analysis
        """
        if not self.client:
            return None
        
        base64_before = self._prepare_image(before_image)
        base64_after = self._prepare_image(after_image)
        
        if not base64_before or not base64_after:
            return {"error": "Failed to process one or both images"}
        
        try:
            prompt = """Compare these two images showing injury progression or treatment.

Image 1 is the earlier state.
Image 2 is the later state.

Provide comparison in JSON format:
1. condition_change: "improved", "worsened", "stable", or "unclear"
2. visible_improvements: List of visible improvements
3. visible_deteriorations: List of visible deteriorations
4. treatment_effectiveness: Assessment of treatment effectiveness
5. concerns: Any concerning changes
6. recommendations: Recommended next steps
7. confidence: Confidence in comparison (0-100)
8. description: Brief description of changes observed

Be objective and note if images are not comparable."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_before}
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_after}
                            }
                        ]
                    }
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            import json
            comparison = json.loads(response.choices[0].message.content)
            
            logger.info(f"Injury comparison completed: change={comparison.get('condition_change')}")
            return {
                "comparison": comparison,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Injury comparison error: {str(e)}")
            return {"error": str(e), "comparison": None}
    
    async def detect_vital_signs_from_image(
        self,
        image_data: bytes
    ) -> Optional[Dict]:
        """
        Attempt to detect visible vital signs indicators from image
        
        Args:
            image_data: Image file bytes
            
        Returns:
            Dict with vital signs assessment
        """
        if not self.client:
            return None
        
        base64_image = self._prepare_image(image_data)
        if not base64_image:
            return {"error": "Failed to process image"}
        
        try:
            prompt = """Assess visible vital signs indicators in this image.

Provide assessment in JSON format:
1. consciousness_level: "alert", "drowsy", "unconscious", or "unable_to_determine"
2. skin_color: "normal", "pale", "cyanotic", "flushed", or "unable_to_determine"
3. visible_breathing: true/false
4. breathing_pattern: "normal", "labored", "rapid", "shallow", or "unable_to_determine"
5. visible_distress: Description of visible distress signs
6. position: Body position and what it may indicate
7. responsiveness_indicators: Visible indicators of responsiveness
8. concerning_signs: List of concerning signs
9. confidence: Confidence in assessment (0-100)
10. limitations: What cannot be determined from image

Note: This is NOT a substitute for actual vital signs measurement."""

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_image, "detail": "high"}
                            }
                        ]
                    }
                ],
                max_tokens=600,
                temperature=0.2
            )
            
            import json
            assessment = json.loads(response.choices[0].message.content)
            
            logger.info("Vital signs assessment completed from image")
            return {
                "assessment": assessment,
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "disclaimer": "Visual assessment only - not a substitute for proper vital signs measurement"
            }
            
        except Exception as e:
            logger.error(f"Vital signs detection error: {str(e)}")
            return {"error": str(e), "assessment": None}


# Global instance
vision_service = VisionService()
