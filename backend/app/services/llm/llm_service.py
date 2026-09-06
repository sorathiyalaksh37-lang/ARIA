"""
LLM Service using OpenAI GPT-4
Provides natural language understanding, summarization, and protocol generation.
"""
import logging
from typing import List, Dict, Optional, Any
from openai import AsyncOpenAI
from openai import OpenAIError

from app.core.config import settings
from app.services.llm.prompts import Prompts

logger = logging.getLogger(__name__)


class LLMService:
    """OpenAI GPT-4 service for emergency response intelligence."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        self.client = None
        self.model = settings.OPENAI_MODEL
        
        if settings.OPENAI_API_KEY:
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info(f"✅ OpenAI client initialized with model: {self.model}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI: {e}")
        else:
            logger.warning("⚠️ OpenAI API key not configured")
    
    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.client is not None
    
    # ============================================================================
    # INCIDENT UNDERSTANDING
    # ============================================================================
    
    async def parse_incident_description(
        self,
        description: str,
        caller_statement: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Parse emergency description and extract structured information.
        
        Args:
            description: Incident description
            caller_statement: Optional caller's verbatim statement
            
        Returns:
            {
                "incident_type": str,
                "severity": str,
                "location_mentioned": str,
                "victim_count": int,
                "injuries": List[str],
                "hazards": List[str],
                "required_resources": List[str],
                "urgency_level": str,
                "key_information": List[str]
            }
        """
        if not self.is_available():
            return None
        
        try:
            # Build prompt
            prompt = Prompts.incident_understanding(description, caller_statement)
            
            # Call GPT-4
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_EMERGENCY_ANALYST},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for factual extraction
                response_format={"type": "json_object"}
            )
            
            # Parse response
            import json
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Parsed incident: {result.get('incident_type')} - {result.get('severity')}")
            return result
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Incident parsing error: {e}")
            return None
    
    async def classify_incident_type(self, description: str) -> Optional[str]:
        """
        Classify incident type from description.
        
        Args:
            description: Incident description
            
        Returns:
            Incident type (road_accident, fire, medical, etc.)
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.incident_classification(description)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_CLASSIFIER},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            
            incident_type = response.choices[0].message.content.strip()
            return incident_type
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return None
    
    async def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location information from text.
        
        Args:
            text: Text containing location information
            
        Returns:
            Extracted location string
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.location_extraction(text)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a location extraction expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            
            location = response.choices[0].message.content.strip()
            return location if location else None
            
        except Exception as e:
            logger.error(f"Location extraction error: {e}")
            return None
    
    # ============================================================================
    # SUMMARIZATION
    # ============================================================================
    
    async def summarize_incident(
        self,
        description: str,
        max_length: int = 100
    ) -> Optional[str]:
        """
        Generate concise incident summary.
        
        Args:
            description: Full incident description
            max_length: Maximum words in summary
            
        Returns:
            Concise summary
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.incident_summarization(description, max_length)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_SUMMARIZER},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return None
    
    async def generate_handoff_summary(
        self,
        incident_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate hospital handoff summary.
        
        Args:
            incident_data: Incident information dictionary
            
        Returns:
            Handoff summary for hospital
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.handoff_summary(incident_data)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_MEDICAL_COMMUNICATOR},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Handoff summary error: {e}")
            return None
    
    async def generate_family_friendly_summary(
        self,
        incident_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate family-friendly summary (removes medical jargon).
        
        Args:
            incident_data: Incident information
            
        Returns:
            Family-friendly summary
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.family_summary(incident_data)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a compassionate communicator explaining medical situations to families."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Family summary error: {e}")
            return None
    
    # ============================================================================
    # PROTOCOL GENERATION
    # ============================================================================
    
    async def generate_response_protocol(
        self,
        incident_type: str,
        severity: str,
        injuries: List[str],
        scene_conditions: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate step-by-step response protocol.
        
        Args:
            incident_type: Type of incident
            severity: Severity level
            injuries: List of identified injuries
            scene_conditions: Optional scene information
            
        Returns:
            {
                "protocol_steps": List[str],
                "warnings": List[str],
                "required_equipment": List[str],
                "required_medications": List[str],
                "special_considerations": List[str]
            }
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.protocol_generation(
                incident_type, severity, injuries, scene_conditions
            )
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_PROTOCOL_EXPERT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            protocol = json.loads(response.choices[0].message.content)
            return protocol
            
        except Exception as e:
            logger.error(f"Protocol generation error: {e}")
            return None
    
    async def generate_triage_protocol(
        self,
        victims: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate mass casualty triage protocol.
        
        Args:
            victims: List of victim information
            
        Returns:
            Triage priorities and protocols
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.triage_protocol(victims)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_TRIAGE_EXPERT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            import json
            protocol = json.loads(response.choices[0].message.content)
            return protocol
            
        except Exception as e:
            logger.error(f"Triage protocol error: {e}")
            return None
    
    # ============================================================================
    # RESOURCE RECOMMENDATIONS
    # ============================================================================
    
    async def recommend_resources(
        self,
        incident_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Recommend required resources for incident response.
        
        Args:
            incident_data: Incident information
            
        Returns:
            {
                "ambulances_needed": int,
                "ambulance_types": List[str],
                "hospital_specialties": List[str],
                "blood_types_needed": List[str],
                "additional_resources": List[str],
                "reasoning": str
            }
        """
        if not self.is_available():
            return None
        
        try:
            prompt = Prompts.resource_recommendation(incident_data)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": Prompts.SYSTEM_RESOURCE_PLANNER},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            import json
            recommendations = json.loads(response.choices[0].message.content)
            return recommendations
            
        except Exception as e:
            logger.error(f"Resource recommendation error: {e}")
            return None
    
    # ============================================================================
    # GENERAL COMPLETIONS
    # ============================================================================
    
    async def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        json_mode: bool = False
    ) -> Optional[str]:
        """
        General purpose completion.
        
        Args:
            prompt: User prompt
            system_message: System message
            temperature: Sampling temperature
            json_mode: Request JSON response
            
        Returns:
            Model response
        """
        if not self.is_available():
            return None
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            
            response = await self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Completion error: {e}")
            return None


# Global instance
llm_service = LLMService()
