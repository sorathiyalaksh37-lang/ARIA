"""
Vision AI Service using OpenAI GPT-4V
Analyzes injury images for emergency assessment.
"""
import logging
from typing import List, Dict, Optional, Any
import base64
from pathlib import Path
from openai import AsyncOpenAI
from openai import OpenAIError

from app.core.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """OpenAI GPT-4V service for injury analysis from images."""
    
    def __init__(self):
        """Initialize Vision client."""
        self.client = None
        if settings.OPENAI_API_KEY:
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ Vision AI client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Vision AI: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not configured")
    
    def is_available(self) -> bool:
        """Check if Vision service is available."""
        return self.client is not None
    
    async def analyze_injury_image(
        self,
        image_path: str,
        additional_context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze injury from image.
        
        Args:
            image_path: Path to image file
            additional_context: Optional additional context about the incident
            
        Returns:
            {
                "injuries_identified": List[str],
                "severity_assessment": str,
                "body_parts_affected": List[str],
                "injury_types": List[str],
                "bleeding_detected": bool,
                "burn_detected": bool,
                "fracture_suspected": bool,
                "immediate_concerns": List[str],
                "first_aid_recommendations": List[str],
                "hospital_specialty_recommended": str,
                "confidence": str
            }
        """
        if not self.is_available():
            logger.error("Vision AI service not available")
            return None
        
        try:
            # Encode image
            image_data = self._encode_image(image_path)
            if not image_data:
                return None
            
            # Build prompt
            prompt = self._build_injury_analysis_prompt(additional_context)
            
            # Call GPT-4V
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse response
            import json
            result_text = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                # If not JSON, create structured response from text
                result = {
                    "analysis": result_text,
                    "injuries_identified": [],
                    "severity_assessment": "unknown",
                    "confidence": "medium"
                }
            
            logger.info(f"✅ Analyzed injury image: {result.get('severity_assessment')}")
            return result
            
        except OpenAIError as e:
            logger.error(f"Vision API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return None
    
    async def analyze_multiple_images(
        self,
        image_paths: List[str],
        additional_context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze multiple injury images.
        
        Args:
            image_paths: List of image file paths
            additional_context: Optional context
            
        Returns:
            Combined analysis from all images
        """
        if not self.is_available():
            return None
        
        try:
            # Encode all images
            image_contents = []
            for path in image_paths:
                image_data = self._encode_image(path)
                if image_data:
                    image_contents.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    })
            
            if not image_contents:
                return None
            
            # Build prompt
            prompt = self._build_multi_image_prompt(len(image_paths), additional_context)
            
            # Prepare message content
            message_content = [{"type": "text", "text": prompt}] + image_contents
            
            # Call GPT-4V
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            # Parse response
            import json
            result_text = response.choices[0].message.content
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = {"analysis": result_text}
            
            logger.info(f"✅ Analyzed {len(image_paths)} injury images")
            return result
            
        except Exception as e:
            logger.error(f"Multiple image analysis error: {e}")
            return None
    
    async def assess_scene_safety(
        self,
        scene_image_path: str
    ) -> Optional[Dict[str, Any]]:
        """
        Assess scene safety from image.
        
        Args:
            scene_image_path: Path to scene image
            
        Returns:
            {
                "hazards_identified": List[str],
                "safety_concerns": List[str],
                "safe_to_approach": bool,
                "required_ppe": List[str],
                "environmental_factors": List[str],
                "recommendations": List[str]
            }
        """
        if not self.is_available():
            return None
        
        try:
            image_data = self._encode_image(scene_image_path)
            if not image_data:
                return None
            
            prompt = """Analyze this emergency scene for safety hazards.
            
Identify and return a JSON object with:
1. hazards_identified: List of visible hazards (fire, chemicals, traffic, structural damage, etc.)
2. safety_concerns: List of safety concerns for first responders
3. safe_to_approach: Boolean indicating if scene appears safe to approach
4. required_ppe: List of required personal protective equipment
5. environmental_factors: Weather, visibility, terrain considerations
6. recommendations: Safety recommendations for responders

Be thorough and prioritize responder safety."""
            
            response = await self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=800
            )
            
            import json
            result_text = response.choices[0].message.content
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = {"analysis": result_text, "safe_to_approach": False}
            
            return result
            
        except Exception as e:
            logger.error(f"Scene safety analysis error: {e}")
            return None
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """
        Encode image to base64.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
        """
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            return None
        except Exception as e:
            logger.error(f"Image encoding error: {e}")
            return None
    
    def _build_injury_analysis_prompt(
        self,
        additional_context: Optional[str] = None
    ) -> str:
        """Build prompt for injury analysis."""
        base_prompt = """You are an emergency medical assessment AI analyzing injury images.

Analyze this injury image and provide a detailed assessment.

Return a JSON object with:
1. injuries_identified: List of visible injuries (specific descriptions)
2. severity_assessment: Overall severity (minor, moderate, severe, critical)
3. body_parts_affected: List of affected body parts
4. injury_types: List of injury classifications (laceration, contusion, fracture, burn, etc.)
5. bleeding_detected: Boolean if active bleeding is visible
6. burn_detected: Boolean if burn injuries detected
7. fracture_suspected: Boolean if fracture is suspected
8. immediate_concerns: List of immediate medical concerns
9. first_aid_recommendations: List of first aid steps
10. hospital_specialty_recommended: Which hospital specialty is most appropriate
11. confidence: Your confidence level (low, medium, high)

IMPORTANT: 
- Be professional and factual
- Avoid speculation
- Focus on visible signs
- Prioritize life-threatening conditions
- Consider mechanism of injury if apparent

Return ONLY valid JSON."""
        
        if additional_context:
            base_prompt += f"\n\nAdditional Context: {additional_context}"
        
        return base_prompt
    
    def _build_multi_image_prompt(
        self,
        num_images: int,
        additional_context: Optional[str] = None
    ) -> str:
        """Build prompt for multiple image analysis."""
        prompt = f"""You are analyzing {num_images} images from an emergency scene.

Provide a comprehensive assessment combining information from all images.

Return a JSON object with:
1. overall_severity: Overall severity assessment
2. injuries_by_location: Dictionary of injuries organized by body part
3. patient_count: Number of patients visible (if multiple)
4. priority_concerns: Ordered list of most critical issues
5. comprehensive_injury_list: Complete list of all identified injuries
6. treatment_priorities: Ordered list of treatment priorities
7. transport_recommendations: Recommendations for patient transport
8. confidence: Your confidence level

Be thorough and systematic."""
        
        if additional_context:
            prompt += f"\n\nAdditional Context: {additional_context}"
        
        return prompt
    
    def supported_formats(self) -> list:
        """Get list of supported image formats."""
        return ["jpg", "jpeg", "png", "gif", "webp"]
    
    def validate_image_format(self, filename: str) -> bool:
        """
        Validate if image format is supported.
        
        Args:
            filename: Image filename
            
        Returns:
            True if supported
        """
        extension = Path(filename).suffix.lstrip('.').lower()
        return extension in self.supported_formats()


# Global instance
vision_service = VisionService()
