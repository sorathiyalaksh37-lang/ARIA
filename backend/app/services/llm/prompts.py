"""
LLM Prompts for ARIA Emergency Response System
All prompts for incident understanding, summarization, and protocol generation.
"""
from typing import List, Dict, Any, Optional
import json


class Prompts:
    """LLM prompts for various tasks."""
    
    # ============================================================================
    # SYSTEM MESSAGES
    # ============================================================================
    
    SYSTEM_EMERGENCY_ANALYST = """You are an expert emergency response analyst for the ARIA system.
Your role is to analyze emergency incident descriptions and extract structured information.
Be precise, factual, and focus on actionable medical and logistical details.
Always err on the side of caution when assessing severity."""
    
    SYSTEM_CLASSIFIER = """You are an incident classification expert.
Classify emergencies into specific categories based on descriptions.
Be accurate and consistent."""
    
    SYSTEM_SUMMARIZER = """You are a professional medical summarizer.
Create concise, accurate summaries that preserve critical information.
Use clear medical terminology."""
    
    SYSTEM_MEDICAL_COMMUNICATOR = """You are a medical communication specialist.
Translate medical situations into clear, professional handoff reports.
Prioritize patient safety and information accuracy."""
    
    SYSTEM_PROTOCOL_EXPERT = """You are an emergency medical protocol expert.
Generate step-by-step protocols based on medical best practices and guidelines.
Include all necessary warnings, equipment, and medications."""
    
    SYSTEM_TRIAGE_EXPERT = """You are a mass casualty triage expert.
Apply START triage or similar protocols to prioritize victims.
Be systematic and consistent."""
    
    SYSTEM_RESOURCE_PLANNER = """You are an emergency resource allocation expert.
Recommend appropriate resources based on incident characteristics.
Consider medical needs, logistics, and safety."""
    
    # ============================================================================
    # INCIDENT UNDERSTANDING PROMPTS
    # ============================================================================
    
    @staticmethod
    def incident_understanding(
        description: str,
        caller_statement: Optional[str] = None
    ) -> str:
        """Prompt for parsing incident description."""
        prompt = f"""Analyze this emergency incident and extract structured information.

Incident Description:
{description}

{f'Caller Statement: {caller_statement}' if caller_statement else ''}

Extract and return a JSON object with:
1. incident_type: Category (road_accident, fire, medical_emergency, natural_disaster, violence, etc.)
2. severity: Level (minor, moderate, severe, critical, mass_casualty)
3. location_mentioned: Any location details mentioned
4. victim_count: Estimated number of victims (integer)
5. injuries: List of identified or suspected injuries
6. hazards: List of scene hazards (fire, chemicals, traffic, etc.)
7. required_resources: List of resources needed (ambulances, fire trucks, etc.)
8. urgency_level: Response urgency (routine, urgent, emergency, immediate)
9. key_information: List of other important details

Return ONLY valid JSON."""
        return prompt
    
    @staticmethod
    def incident_classification(description: str) -> str:
        """Prompt for incident type classification."""
        return f"""Classify this emergency incident into ONE of these categories:
- road_accident
- fire
- medical_emergency
- cardiac_arrest
- stroke
- trauma
- burn
- drowning
- poisoning
- natural_disaster
- building_collapse
- violence
- industrial_accident
- mass_casualty
- other

Incident: {description}

Return ONLY the category name, nothing else."""
    
    @staticmethod
    def location_extraction(text: str) -> str:
        """Prompt for location extraction."""
        return f"""Extract the location information from this text.
Return the most specific location mentioned (address, landmark, intersection, etc.).
If no location is found, return an empty string.

Text: {text}

Return ONLY the location, nothing else."""
    
    # ============================================================================
    # SUMMARIZATION PROMPTS
    # ============================================================================
    
    @staticmethod
    def incident_summarization(description: str, max_words: int = 100) -> str:
        """Prompt for incident summarization."""
        return f"""Summarize this emergency incident in {max_words} words or less.
Focus on: type of incident, number of victims, injuries, location, and urgency.

Incident Description:
{description}

Return ONLY the summary."""
    
    @staticmethod
    def handoff_summary(incident_data: Dict[str, Any]) -> str:
        """Prompt for hospital handoff summary."""
        return f"""Generate a professional EMS-to-hospital handoff report using the SBAR format.

Incident Data:
{json.dumps(incident_data, indent=2)}

Create a brief, professional handoff that includes:
- Situation: What happened
- Background: Relevant medical history if known
- Assessment: Current condition and vitals
- Recommendation: Required interventions

Keep it concise (under 200 words) and use medical terminology."""
    
    @staticmethod
    def family_summary(incident_data: Dict[str, Any]) -> str:
        """Prompt for family-friendly summary."""
        return f"""Create a compassionate, family-friendly summary of this medical situation.

Incident Data:
{json.dumps(incident_data, indent=2)}

Requirements:
- Use simple, non-technical language
- Be honest but compassionate
- Focus on what family needs to know
- Avoid graphic details
- Provide reassurance where appropriate
- Keep it under 150 words

Return ONLY the summary."""
    
    # ============================================================================
    # PROTOCOL GENERATION PROMPTS
    # ============================================================================
    
    @staticmethod
    def protocol_generation(
        incident_type: str,
        severity: str,
        injuries: List[str],
        scene_conditions: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prompt for response protocol generation."""
        conditions_str = ""
        if scene_conditions:
            conditions_str = f"\nScene Conditions:\n{json.dumps(scene_conditions, indent=2)}"
        
        return f"""Generate a comprehensive emergency response protocol for this incident.

Incident Type: {incident_type}
Severity: {severity}
Identified Injuries: {', '.join(injuries)}
{conditions_str}

Return a JSON object with:
1. protocol_steps: List of step-by-step actions (in order)
2. warnings: List of safety warnings and precautions
3. required_equipment: List of medical equipment needed
4. required_medications: List of medications that may be needed
5. special_considerations: List of special considerations for this incident

Base the protocol on standard emergency medical protocols and best practices.
Return ONLY valid JSON."""
    
    @staticmethod
    def triage_protocol(victims: List[Dict[str, Any]]) -> str:
        """Prompt for triage protocol."""
        return f"""Apply START triage protocol to these victims and provide prioritization.

Victims:
{json.dumps(victims, indent=2)}

Return a JSON object with:
1. triage_categories: Object with victims grouped by priority
   - immediate: Life-threatening, needs immediate care (RED)
   - delayed: Serious but stable, can wait (YELLOW)
   - minor: Walking wounded, minor injuries (GREEN)
   - deceased: No signs of life (BLACK)
2. transport_priority: Ordered list of victim IDs for transport
3. resource_allocation: Resources needed for each priority group
4. special_notes: Any special considerations

Return ONLY valid JSON."""
    
    # ============================================================================
    # RESOURCE RECOMMENDATION PROMPTS
    # ============================================================================
    
    @staticmethod
    def resource_recommendation(incident_data: Dict[str, Any]) -> str:
        """Prompt for resource recommendations."""
        return f"""Analyze this incident and recommend required resources.

Incident Data:
{json.dumps(incident_data, indent=2)}

Return a JSON object with:
1. ambulances_needed: Number of ambulances required (integer)
2. ambulance_types: List of ambulance types (BLS, ALS, critical_care, etc.)
3. hospital_specialties: List of required hospital specialties (trauma, burn, cardiac, etc.)
4. blood_types_needed: List of blood types that may be needed
5. additional_resources: List of other resources (fire, police, hazmat, etc.)
6. reasoning: Brief explanation of recommendations

Consider:
- Number and severity of victims
- Type of injuries
- Scene conditions
- Transport time
- Hospital capabilities

Return ONLY valid JSON."""
    
    # ============================================================================
    # TRANSLATION PROMPTS (for multilingual support)
    # ============================================================================
    
    @staticmethod
    def translate_prompt(
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Prompt for text translation."""
        return f"""Translate this text from {source_lang} to {target_lang}.
Preserve medical terminology and urgency.

Text: {text}

Return ONLY the translation."""
    
    @staticmethod
    def detect_language_prompt(text: str) -> str:
        """Prompt for language detection."""
        return f"""Detect the language of this text and return the ISO 639-1 code.

Text: {text}

Return ONLY the language code (e.g., 'en', 'hi', 'mr', 'ta')."""
