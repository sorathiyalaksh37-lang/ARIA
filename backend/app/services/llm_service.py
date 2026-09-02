"""
LLM Integration Service (OpenAI GPT-4 / Google Gemini)
Provides natural language understanding, summarization, and protocol generation
"""
import logging
from typing import Dict, List, Optional
import httpx
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM service for natural language processing"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_model = settings.OPENAI_MODEL or "gpt-4-turbo-preview"
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize OpenAI client"""
        try:
            if self.openai_api_key:
                self.client = AsyncOpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not configured")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None
    
    async def analyze_incident_description(
        self,
        description: str,
        context: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Analyze incident description to extract key information
        
        Args:
            description: Free-text incident description
            context: Additional context (location, reporter info, etc.)
            
        Returns:
            Dict with extracted information
        """
        if not self.client:
            logger.warning("LLM client not available")
            return None
        
        try:
            context_str = ""
            if context:
                context_str = f"\n\nAdditional Context:\n{context}"
            
            prompt = f"""Analyze this emergency incident description and extract structured information.

Incident Description: {description}{context_str}

Extract and return in JSON format:
1. incident_type: Type of emergency (medical, trauma, fire, etc.)
2. severity: Estimated severity (critical, high, medium, low)
3. number_of_victims: Estimated number of people affected
4. injuries: List of specific injuries mentioned
5. symptoms: List of symptoms described
6. hazards: Any environmental hazards or dangers
7. special_requirements: Special equipment or expertise needed
8. urgency_level: 1-10 scale of urgency
9. keywords: List of important keywords
10. summary: Brief 2-sentence summary

Be precise and conservative in assessments. If information is unclear, indicate that."""

            response = await self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert emergency medical dispatcher analyzing incident reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Incident analysis completed: {result.get('incident_type')}")
            return result
            
        except Exception as e:
            logger.error(f"Incident analysis error: {str(e)}")
            return None
    
    async def generate_treatment_protocol(
        self,
        incident_type: str,
        severity: str,
        symptoms: List[str],
        patient_age: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Generate treatment protocol based on incident details
        
        Args:
            incident_type: Type of medical emergency
            severity: Severity level
            symptoms: List of symptoms
            patient_age: Patient age if known
            
        Returns:
            Dict with treatment protocol
        """
        if not self.client:
            return None
        
        try:
            age_context = f"Patient age: {patient_age}" if patient_age else "Patient age: Unknown"
            symptoms_str = ", ".join(symptoms)
            
            prompt = f"""Generate an emergency treatment protocol for paramedics.

Incident Type: {incident_type}
Severity: {severity}
Symptoms: {symptoms_str}
{age_context}

Provide:
1. immediate_actions: Critical first steps (list)
2. assessment_checklist: What to check/monitor (list)
3. treatment_steps: Step-by-step treatment (list)
4. medications: Recommended medications with dosages (list of dicts)
5. contraindications: What to avoid (list)
6. transport_priority: How urgent is transport (critical/high/moderate/low)
7. hospital_requirements: What hospital capabilities are needed (list)
8. estimated_time_on_scene: Estimated minutes at scene

Return as JSON. Be specific and follow standard emergency protocols."""

            response = await self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert emergency medicine physician providing protocols for paramedics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Treatment protocol generated for {incident_type}")
            return result
            
        except Exception as e:
            logger.error(f"Protocol generation error: {str(e)}")
            return None
    
    async def summarize_incident(
        self,
        incident_data: Dict,
        target_audience: str = "general"
    ) -> Optional[str]:
        """
        Generate human-readable incident summary
        
        Args:
            incident_data: Complete incident data
            target_audience: "general", "medical", "dispatch", "management"
            
        Returns:
            Summary text
        """
        if not self.client:
            return None
        
        try:
            import json
            incident_json = json.dumps(incident_data, indent=2)
            
            audience_instructions = {
                "general": "Write for general public understanding",
                "medical": "Use medical terminology for healthcare professionals",
                "dispatch": "Focus on operational details for dispatchers",
                "management": "Focus on metrics and outcomes for management"
            }
            
            prompt = f"""Summarize this emergency incident in 3-4 sentences.

Incident Data:
{incident_json}

Target Audience: {target_audience}
{audience_instructions.get(target_audience, '')}

Include: what happened, actions taken, current status, outcome."""

            response = await self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert at creating clear, concise incident summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Incident summary generated for {target_audience}")
            return summary
            
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return None
    
    async def predict_resource_needs(
        self,
        incident_description: str,
        location_context: Dict
    ) -> Optional[Dict]:
        """
        Predict required resources based on incident details
        
        Args:
            incident_description: Incident description
            location_context: Location and environmental context
            
        Returns:
            Dict with resource predictions
        """
        if not self.client:
            return None
        
        try:
            import json
            context_json = json.dumps(location_context, indent=2)
            
            prompt = f"""Predict emergency resource requirements for this incident.

Incident: {incident_description}

Location Context:
{context_json}

Predict and return in JSON:
1. ambulances_needed: Number (1-5)
2. ambulance_type: "ALS" (Advanced Life Support) or "BLS" (Basic Life Support)
3. special_equipment: List of special equipment needed
4. additional_personnel: Types of specialists needed (e.g., "trauma surgeon")
5. hospital_capabilities: Required hospital capabilities (e.g., "trauma center level 1")
6. blood_products: Anticipated blood products needed
7. estimated_transport_time: Minutes to hospital
8. confidence_score: 0-100 confidence in predictions
9. reasoning: Brief explanation of predictions

Be realistic and err on the side of caution."""

            response = await self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert emergency resource coordinator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Resource prediction completed: {result.get('ambulances_needed')} ambulances")
            return result
            
        except Exception as e:
            logger.error(f"Resource prediction error: {str(e)}")
            return None
    
    async def generate_incident_report(
        self,
        incident_data: Dict,
        include_timeline: bool = True,
        include_recommendations: bool = True
    ) -> Optional[str]:
        """
        Generate comprehensive incident report
        
        Args:
            incident_data: Complete incident data
            include_timeline: Include event timeline
            include_recommendations: Include improvement recommendations
            
        Returns:
            Formatted report text
        """
        if not self.client:
            return None
        
        try:
            import json
            incident_json = json.dumps(incident_data, indent=2)
            
            sections = ["executive summary", "incident details", "response actions", "outcome"]
            if include_timeline:
                sections.append("timeline of events")
            if include_recommendations:
                sections.append("recommendations for improvement")
            
            sections_str = ", ".join(sections)
            
            prompt = f"""Generate a professional incident report with these sections: {sections_str}

Incident Data:
{incident_json}

Use clear headings, bullet points where appropriate, and professional tone.
Focus on facts, metrics, and actionable insights."""

            response = await self.client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are an expert at writing professional emergency incident reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            report = response.choices[0].message.content.strip()
            logger.info("Incident report generated")
            return report
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return None
    
    async def chat_query(
        self,
        query: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> Optional[str]:
        """
        General chat interface for queries
        
        Args:
            query: User query
            context: Additional context
            conversation_history: Previous messages
            
        Returns:
            Response text
        """
        if not self.client:
            return None
        
        try:
            messages = [
                {"role": "system", "content": "You are ARIA, an AI assistant for emergency response coordination. Provide clear, actionable information."}
            ]
            
            if context:
                messages.append({"role": "system", "content": f"Context: {context}"})
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({"role": "user", "content": query})
            
            response = await self.client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Chat query error: {str(e)}")
            return None


# Global instance
llm_service = LLMService()
