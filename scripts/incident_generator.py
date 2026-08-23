#!/usr/bin/env python3
"""
ARIA Synthetic Incident Generation Script
=========================================
Generates 100,000+ realistic emergency incidents for training the triage classifier.

Author: ARIA Data Engineering Team
Date: 2026-08-22
Version: 1.0

Output: 100,000+ incident records with realistic Indian context
"""

import csv
import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from tqdm import tqdm

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_FILE = os.path.join(DATA_DIR, "incidents_raw.csv")
SUMMARY_FILE = os.path.join(DATA_DIR, "incidents_summary.txt")
LOG_FILE = os.path.join(LOG_DIR, "incident_generation.log")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# INDIAN CITIES AND LOCALITIES
# ============================================================================

CITIES_LOCALITIES = {
    "Mumbai": {
        "localities": ["Andheri", "Bandra", "Dadar", "Worli", "Juhu", "Colaba", "Thane", "Navi Mumbai", "Goregaon", "Malad"],
        "coords": (19.0760, 72.8777)
    },
    "Delhi": {
        "localities": ["Connaught Place", "Karol Bagh", "Chandni Chowk", "South Delhi", "Noida", "Ghaziabad", "Dwarka", "Rohini"],
        "coords": (28.7041, 77.1025)
    },
    "Bangalore": {
        "localities": ["MG Road", "Koramangala", "Indiranagar", "Whitefield", "Electronic City", "Jayanagar", "BTM Layout"],
        "coords": (12.9716, 77.5946)
    },
    "Chennai": {
        "localities": ["T Nagar", "Velachery", "Anna Nagar", "Adyar", "Porur", "Guindy", "Nungambakkam"],
        "coords": (13.0827, 80.2707)
    },
    "Hyderabad": {
        "localities": ["Jubilee Hills", "Banjara Hills", "Kukatpally", "Gachibowli", "Hitech City", "Secunderabad"],
        "coords": (17.3850, 78.4867)
    },
    "Kolkata": {
        "localities": ["Salt Lake", "Park Street", "Howrah", "Dum Dum", "Ballygunge", "Alipore"],
        "coords": (22.5726, 88.3639)
    },
    "Ahmedabad": {
        "localities": ["CG Road", "Satellite", "Vastrapur", "Gandhinagar", "Navrangpura", "Maninagar"],
        "coords": (23.0225, 72.5714)
    },
    "Pune": {
        "localities": ["Kalyani Nagar", "Koregaon Park", "Hinjewadi", "Kothrud", "Wakad", "Baner"],
        "coords": (18.5204, 73.8567)
    },
}

# ============================================================================
# LANDMARKS
# ============================================================================

LANDMARKS = [
    "{} Highway", "{} Main Road", "{} Railway Crossing", "{} Bus Stop", "{} Metro Station",
    "{} Market", "{} School", "{} College", "{} Office Complex", "{} Park",
    "{} Railway Station", "{} Airport Road", "{} Mall", "{} Temple", "{} Mosque",
    "{} Church", "{} Police Station", "{} Hospital Road", "{} Hotel", "{} Restaurant"
]

ROAD_NAMES = [
    "MG Road", "Ring Road", "Bypass Road", "Main Road", "Station Road",
    "Airport Road", "Market Road", "Gandhi Road", "Nehru Road", "Patel Road"
]

# ============================================================================
# INCIDENT TEMPLATES
# ============================================================================

# CRITICAL (15% - 15,000 incidents)
CRITICAL_TEMPLATES = [
    "Car accident at {landmark}, {num} victims, {num2} unconscious with severe bleeding",
    "Heart attack at {location}, patient collapsed, unresponsive, chest pain radiating to left arm",
    "Severe chest pain and difficulty breathing at {location}, patient sweating profusely",
    "Stroke suspected at {location}, one side paralyzed, speech slurred, facial drooping",
    "Building collapse at {location}, {num} people trapped, multiple injuries",
    "Gas leak at {location}, {num} people unconscious, difficulty breathing",
    "Gunshot wound at {location}, active bleeding from chest, patient critical",
    "Industrial accident at {location}, {num} workers with severe burns and chemical exposure",
    "Multi-vehicle pileup on {highway}, {num} casualties, several critical injuries",
    "Fire at {building}, {num} people with severe burns, smoke inhalation",
    "Electric shock at {location}, patient unconscious, not breathing",
    "Drowning at {location}, patient pulled from water, not breathing",
    "Massive hemorrhage at {location}, patient lost consciousness, bleeding profusely",
    "Severe head injury at {location}, patient unconscious, bleeding from head",
    "Multiple stab wounds at {location}, heavy bleeding, patient in shock",
    "Cardiac arrest at {location}, CPR in progress, patient unresponsive",
    "Severe allergic reaction at {location}, patient unable to breathe, throat swelling",
    "Motorcycle accident at {highway}, rider unconscious with head trauma",
    "Fall from {num} floor building, multiple fractures, internal bleeding suspected",
    "Train accident at {location}, multiple casualties, severe injuries",
    "Explosion at {location}, {num} people with blast injuries and burns",
    "Hanging attempt at {location}, patient found unconscious",
    "Poisoning at {location}, {num} people unconscious, suspected pesticide ingestion",
    "Severe breathing difficulty at {location}, patient turning blue, oxygen needed urgently",
    "Diabetic emergency at {location}, patient unconscious, very low sugar level",
    "Seizure at {location}, patient fell and hit head, bleeding and unconscious",
    "Premature delivery at {location}, baby coming, mother bleeding heavily",
    "Knife wound to abdomen at {location}, intestines exposed, critical condition",
    "Crush injury at {location}, patient trapped under heavy machinery",
    "Severe asthma attack at {location}, patient unable to breathe, lips turning blue",
]

# MODERATE (35% - 35,000 incidents)
MODERATE_TEMPLATES = [
    "Broken leg at {location}, visible deformity, unable to walk, severe pain",
    "Deep cut on {body_part} at {location}, heavy bleeding, wound won't stop",
    "High fever with difficulty breathing at {location}, temperature 104°F",
    "Severe burn on {body_part} at {location}, 2nd degree, blisters forming",
    "Allergic reaction at {location}, swelling on face, difficulty breathing",
    "Dog bite at {location}, bleeding wound, possible rabies risk",
    "Fall from stairs at {location}, suspected fracture in {body_part}",
    "Accidental poisoning at {location}, vomiting, stomach pain",
    "Electrical burn on {body_part} at {location}, moderate injury",
    "Severe stomach pain at {location}, vomiting, suspected appendicitis",
    "Motorcycle accident at {location}, road rash and fractures",
    "Hit by vehicle at {location}, leg injury, unable to stand",
    "Severe vomiting and diarrhea at {location}, dehydration suspected",
    "Chest pain at {location}, uncomfortable but conscious",
    "Difficulty breathing at {location}, wheezing, history of asthma",
    "Severe headache and vomiting at {location}, dizziness",
    "Pregnancy complication at {location}, bleeding, {num} months pregnant",
    "Animal attack at {location}, multiple bite wounds on {body_part}",
    "Smoke inhalation at {location}, coughing, breathing difficulty",
    "Sports injury at {location}, dislocated shoulder, severe pain",
    "Chemical burn at {location}, acid on skin, washing with water",
    "Suspected fracture at {location}, swelling and unable to move {body_part}",
    "Severe bleeding from {body_part} at {location}, cut from glass",
    "Fainting at {location}, patient regained consciousness but weak",
    "Severe toothache with swelling at {location}, unable to eat",
    "Kidney stone pain at {location}, severe back pain, vomiting",
    "Food poisoning at {location}, {num} people affected, vomiting",
    "Heat stroke at {location}, patient very hot, disoriented",
    "Suspected heart problem at {location}, irregular heartbeat, chest discomfort",
    "Major nosebleed at {location}, won't stop bleeding for 30 minutes",
]

# LOW (50% - 50,000 incidents)
LOW_TEMPLATES = [
    "Mild fever and cough for {days} days at {location}, need consultation",
    "Small cut on finger at {location}, bleeding stopped, needs stitches",
    "Stomach ache at {location}, mild pain, discomfort",
    "Headache and mild dizziness at {location}, feeling unwell",
    "Sore throat at {location}, difficulty swallowing, fever",
    "Skin rash at {location}, itching, redness on arms",
    "Eye infection at {location}, redness and watering",
    "Ear pain at {location}, mild discomfort, feels blocked",
    "Toothache at {location}, swelling in gums",
    "Minor sprain at {location}, twisted ankle, mild pain",
    "Back pain at {location}, discomfort, no injury",
    "Common cold at {location}, runny nose, sneezing",
    "Muscle pain at {location}, soreness after exercise",
    "Mild fever at {location}, temperature 100°F",
    "Indigestion at {location}, acidity, discomfort",
    "Minor burn at {location}, touched hot pan, small blister",
    "Bruise on {body_part} at {location}, from fall, no fracture",
    "Insect bite at {location}, swelling and itching",
    "Urinary discomfort at {location}, burning sensation",
    "Minor cut from kitchen knife at {location}, bleeding stopped",
    "Constipation at {location}, {days} days, discomfort",
    "Migraine headache at {location}, sensitivity to light",
    "Anxiety and palpitations at {location}, feeling stressed",
    "Minor allergic reaction at {location}, mild rash",
    "Wrist pain at {location}, from overuse, no swelling",
    "Neck stiffness at {location}, slept wrong, discomfort",
    "Leg cramps at {location}, muscle pain, no injury",
    "Sunburn at {location}, redness on skin",
    "Minor nosebleed at {location}, stopped on its own",
    "Dry cough at {location}, throat irritation",
]

# ============================================================================
# BODY PARTS
# ============================================================================

BODY_PARTS = [
    "head", "chest", "arm", "leg", "hand", "foot", "back", "stomach",
    "shoulder", "knee", "elbow", "wrist", "ankle", "face", "neck"
]

# ============================================================================
# EMERGENCY KEYWORDS
# ============================================================================

EMERGENCY_KEYWORDS = [
    "unconscious", "bleeding", "chest pain", "difficulty breathing", "cardiac arrest",
    "stroke", "seizure", "accident", "unconscious", "critical", "emergency",
    "severe", "collapsed", "unresponsive", "not breathing"
]

# ============================================================================
# INCIDENT GENERATION
# ============================================================================

def get_gps_coordinates(city: str) -> Tuple[float, float]:
    """Get GPS coordinates with variation."""
    city_data = CITIES_LOCALITIES.get(city, {"coords": (20.0, 77.0)})
    base_lat, base_lon = city_data["coords"]
    lat = round(base_lat + random.uniform(-0.05, 0.05), 6)
    lon = round(base_lon + random.uniform(-0.05, 0.05), 6)
    return lat, lon

def generate_timestamp() -> Tuple[str, str, str, str, str]:
    """Generate random timestamp within past year."""
    days_ago = random.randint(0, 365)
    incident_time = datetime.now() - timedelta(days=days_ago)
    
    # Add random hour and minute
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    incident_time = incident_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    # Time of day
    if 5 <= hour < 12:
        time_of_day = "MORNING"
    elif 12 <= hour < 17:
        time_of_day = "AFTERNOON"
    elif 17 <= hour < 21:
        time_of_day = "EVENING"
    else:
        time_of_day = "NIGHT"
    
    # Day of week
    day_of_week = incident_time.strftime("%a").upper()
    
    # Month
    month = incident_time.month
    
    # Season
    if month in [6, 7, 8, 9]:
        season = "MONSOON"
    elif month in [12, 1, 2]:
        season = "WINTER"
    else:
        season = "SUMMER"
    
    return incident_time.isoformat(), time_of_day, day_of_week, str(month), season

def check_emergency_keywords(description: str) -> bool:
    """Check if description contains emergency keywords."""
    desc_lower = description.lower()
    return any(keyword in desc_lower for keyword in EMERGENCY_KEYWORDS)

def check_body_part(description: str) -> str:
    """Extract body part mentioned."""
    desc_lower = description.lower()
    for body_part in BODY_PARTS:
        if body_part in desc_lower:
            return body_part.upper()
    return "NONE"

def generate_incident_description(severity: str) -> str:
    """Generate incident description based on severity."""
    # Select template based on severity
    if severity == "CRITICAL":
        template = random.choice(CRITICAL_TEMPLATES)
    elif severity == "MODERATE":
        template = random.choice(MODERATE_TEMPLATES)
    else:  # LOW
        template = random.choice(LOW_TEMPLATES)
    
    # Select random city and locality
    city = random.choice(list(CITIES_LOCALITIES.keys()))
    locality = random.choice(CITIES_LOCALITIES[city]["localities"])
    
    # Generate location string
    location = f"{locality}, {city}"
    
    # Generate landmark
    landmark_template = random.choice(LANDMARKS)
    landmark = landmark_template.format(locality)
    
    # Generate building/highway name
    building = f"{random.choice(['Samarth', 'Laxmi', 'Ganesh', 'Shivaji', 'Gandhi'])} {random.choice(['Tower', 'Complex', 'Building', 'Mall'])}"
    highway = random.choice(ROAD_NAMES)
    
    # Generate numbers
    num = random.randint(2, 8)
    num2 = random.randint(1, 3)
    days = random.randint(2, 10)
    
    # Generate body part
    body_part = random.choice(BODY_PARTS)
    
    # Fill template
    description = template.format(
        location=location,
        landmark=landmark,
        building=building,
        highway=highway,
        num=num,
        num2=num2,
        days=days,
        body_part=body_part
    )
    
    # Add variations (10% Hinglish)
    if random.random() < 0.1:
        hinglish_additions = [
            " Jaldi bhejo ambulance",
            " Please jaldi aao",
            " Bahut serious hai",
            " Turant madad chahiye"
        ]
        description += random.choice(hinglish_additions)
    
    return description, city, locality

def generate_incident_record(incident_id: int, severity: str) -> Dict:
    """Generate a single incident record."""
    
    # Generate description
    description, city, locality = generate_incident_description(severity)
    
    # GPS coordinates
    lat, lon = get_gps_coordinates(city)
    
    # Timestamp components
    timestamp, time_of_day, day_of_week, month, season = generate_timestamp()
    
    # Incident type
    desc_lower = description.lower()
    if "accident" in desc_lower or "vehicle" in desc_lower or "motorcycle" in desc_lower:
        incident_type = "ACCIDENT"
    elif "fire" in desc_lower or "burn" in desc_lower:
        incident_type = "FIRE"
    elif "gunshot" in desc_lower or "stab" in desc_lower or "attack" in desc_lower:
        incident_type = "VIOLENCE"
    elif "collapse" in desc_lower or "explosion" in desc_lower:
        incident_type = "DISASTER"
    else:
        incident_type = "MEDICAL"
    
    # Victim count
    if severity == "CRITICAL":
        victim_count = random.randint(1, 10)
    elif severity == "MODERATE":
        victim_count = random.randint(1, 3)
    else:
        victim_count = 1
    
    # Requirements
    emergency_keyword = check_emergency_keywords(description)
    body_part_mentioned = check_body_part(description)
    
    # Resource requirements
    if severity == "CRITICAL":
        blood_required = random.random() < 0.6
        ambulance_required = True
        hospital_required = True
    elif severity == "MODERATE":
        blood_required = random.random() < 0.2
        ambulance_required = random.random() < 0.8
        hospital_required = random.random() < 0.9
    else:  # LOW
        blood_required = False
        ambulance_required = random.random() < 0.3
        hospital_required = random.random() < 0.5
    
    incident = {
        "incident_id": f"INC-{incident_id:06d}",
        "incident_description": description,
        "severity": severity,
        "incident_type": incident_type,
        "city": city,
        "location": locality,
        "latitude": lat,
        "longitude": lon,
        "timestamp": timestamp,
        "victim_count": victim_count,
        "time_of_day": time_of_day,
        "day_of_week": day_of_week,
        "month": month,
        "season": season,
        "body_part_mentioned": body_part_mentioned,
        "emergency_keyword": "Yes" if emergency_keyword else "No",
        "blood_required": "Yes" if blood_required else "No",
        "ambulance_required": "Yes" if ambulance_required else "No",
        "hospital_required": "Yes" if hospital_required else "No"
    }
    
    return incident

def generate_all_incidents(target_count: int = 100000) -> List[Dict]:
    """Generate all incidents with proper distribution."""
    logger.info(f"Generating {target_count} incident records...")
    
    incidents = []
    
    # Calculate distribution
    critical_count = int(target_count * 0.15)  # 15%
    moderate_count = int(target_count * 0.35)  # 35%
    low_count = target_count - critical_count - moderate_count  # 50%
    
    logger.info(f"Distribution: Critical={critical_count}, Moderate={moderate_count}, Low={low_count}")
    
    incident_id = 1
    
    # Generate CRITICAL incidents
    logger.info("Generating CRITICAL incidents...")
    for _ in tqdm(range(critical_count), desc="Critical"):
        incident = generate_incident_record(incident_id, "CRITICAL")
        incidents.append(incident)
        incident_id += 1
    
    # Generate MODERATE incidents
    logger.info("Generating MODERATE incidents...")
    for _ in tqdm(range(moderate_count), desc="Moderate"):
        incident = generate_incident_record(incident_id, "MODERATE")
        incidents.append(incident)
        incident_id += 1
    
    # Generate LOW incidents
    logger.info("Generating LOW incidents...")
    for _ in tqdm(range(low_count), desc="Low"):
        incident = generate_incident_record(incident_id, "LOW")
        incidents.append(incident)
        incident_id += 1
    
    # Shuffle to randomize order
    random.shuffle(incidents)
    
    logger.info(f"Generated {len(incidents)} total incidents")
    return incidents

# ============================================================================
# SAVE TO CSV
# ============================================================================

def save_to_csv(incidents: List[Dict], filename: str):
    """Save incidents to CSV."""
    logger.info(f"Saving {len(incidents)} incidents to {filename}...")
    
    fieldnames = list(incidents[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(incidents)
    
    logger.info(f"Successfully saved to {filename}")

# ============================================================================
# GENERATE SUMMARY
# ============================================================================

def generate_summary_report(incidents: List[Dict], filename: str):
    """Generate summary statistics."""
    logger.info("Generating summary report...")
    
    total = len(incidents)
    
    # Statistics
    by_severity = {"CRITICAL": 0, "MODERATE": 0, "LOW": 0}
    by_type = {}
    by_city = {}
    by_time = {}
    by_day = {}
    by_season = {}
    
    total_blood = 0
    total_ambulance = 0
    total_hospital = 0
    
    for inc in incidents:
        by_severity[inc["severity"]] += 1
        
        itype = inc.get("incident_type", "Unknown")
        by_type[itype] = by_type.get(itype, 0) + 1
        
        city = inc.get("city", "Unknown")
        by_city[city] = by_city.get(city, 0) + 1
        
        time_of_day = inc.get("time_of_day", "Unknown")
        by_time[time_of_day] = by_time.get(time_of_day, 0) + 1
        
        day = inc.get("day_of_week", "Unknown")
        by_day[day] = by_day.get(day, 0) + 1
        
        season = inc.get("season", "Unknown")
        by_season[season] = by_season.get(season, 0) + 1
        
        if inc.get("blood_required") == "Yes":
            total_blood += 1
        if inc.get("ambulance_required") == "Yes":
            total_ambulance += 1
        if inc.get("hospital_required") == "Yes":
            total_hospital += 1
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ARIA INCIDENT GENERATION SUMMARY REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"TOTAL INCIDENTS GENERATED: {total:,}\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("DISTRIBUTION BY SEVERITY\n")
        f.write("-" * 70 + "\n")
        for sev, count in sorted(by_severity.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            f.write(f"{sev:15s}: {count:8,} ({percentage:5.1f}%)\n")
        
        f.write("\n" + "-" * 70 + "\n")
        f.write("DISTRIBUTION BY INCIDENT TYPE\n")
        f.write("-" * 70 + "\n")
        for itype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            f.write(f"{itype:15s}: {count:8,} ({percentage:5.1f}%)\n")
        
        f.write("\n" + "-" * 70 + "\n")
        f.write("DISTRIBUTION BY CITY\n")
        f.write("-" * 70 + "\n")
        for city, count in sorted(by_city.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            f.write(f"{city:20s}: {count:8,} ({percentage:5.1f}%)\n")
        
        f.write("\n" + "-" * 70 + "\n")
        f.write("RESOURCE REQUIREMENTS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Blood Required: {total_blood:,} ({(total_blood/total)*100:.1f}%)\n")
        f.write(f"Ambulance Required: {total_ambulance:,} ({(total_ambulance/total)*100:.1f}%)\n")
        f.write(f"Hospital Required: {total_hospital:,} ({(total_hospital/total)*100:.1f}%)\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write(f"Output File: {OUTPUT_FILE}\n")
        f.write(f"Log File: {LOG_FILE}\n")
        f.write("=" * 70 + "\n")
    
    logger.info(f"Summary report saved to {filename}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function."""
    import time
    start_time = time.time()
    
    logger.info("=" * 70)
    logger.info("ARIA INCIDENT GENERATION STARTED")
    logger.info("=" * 70)
    
    try:
        # Generate incidents
        incidents = generate_all_incidents(target_count=100000)
        
        # Save to CSV
        save_to_csv(incidents, OUTPUT_FILE)
        
        # Generate summary
        generate_summary_report(incidents, SUMMARY_FILE)
        
        elapsed_time = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("INCIDENT GENERATION COMPLETED SUCCESSFULLY")
        logger.info(f"Total Incidents: {len(incidents):,}")
        logger.info(f"Time Elapsed: {elapsed_time:.2f} seconds")
        logger.info(f"Output File: {OUTPUT_FILE}")
        logger.info(f"Summary Report: {SUMMARY_FILE}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
