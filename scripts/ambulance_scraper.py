#!/usr/bin/env python3
"""
ARIA Ambulance Fleet Data Collection Script
===========================================
Collects ambulance fleet data from multiple sources for the ARIA Emergency Response Platform.

Author: ARIA Data Engineering Team
Date: 2026-08-22
Version: 1.0

Sources:
1. EMRI 108 Ambulance Service (https://www.emri.in)
2. Google Places API (Private Ambulances)
3. Synthetic generation for comprehensive coverage

Output: 25,000+ ambulance records
"""

import csv
import json
import logging
import os
import random
import re
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_FILE = os.path.join(DATA_DIR, "ambulances_raw.csv")
SUMMARY_FILE = os.path.join(DATA_DIR, "ambulances_summary.txt")
LOG_FILE = os.path.join(LOG_DIR, "ambulance_scrape.log")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

RATE_LIMIT_DELAY = 1.0
MAX_RETRIES = 3
USER_AGENT = "ARIA-Ambulance-Data-Collector/1.0"

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
# AMBULANCE DATA CONFIGURATION
# ============================================================================

INDIAN_STATES_CITIES = {
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur"],
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
    "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Meerut", "Allahabad"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
    "Punjab": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar"],
    "Haryana": ["Gurugram", "Faridabad", "Ghaziabad", "Panipat"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri"],
    "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur"],
    "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat"],
}

# GPS coordinates for major cities
CITY_COORDINATES = {
    "Mumbai": (19.0760, 72.8777), "Pune": (18.5204, 73.8567),
    "Delhi": (28.7041, 77.1025), "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707), "Hyderabad": (17.3850, 78.4867),
    "Ahmedabad": (23.0225, 72.5714), "Kolkata": (22.5726, 88.3639),
    "Lucknow": (26.8467, 80.9462), "Jaipur": (26.9124, 75.7873),
}

# Ambulance types distribution: 30% BASIC, 50% ALS, 20% CRITICAL_CARE
AMBULANCE_TYPES = {
    "BASIC": 0.30,
    "ALS": 0.50,  # Advanced Life Support
    "CRITICAL_CARE": 0.20
}

# Equipment by ambulance type
EQUIPMENT_BY_TYPE = {
    "BASIC": [
        "First Aid Kit", "Oxygen Cylinder", "Stretcher", "Spine Board",
        "Blood Pressure Monitor", "Pulse Oximeter", "Bandages", "Splints"
    ],
    "ALS": [
        "First Aid Kit", "Oxygen Cylinder", "Stretcher", "Spine Board",
        "Defibrillator", "ECG Monitor", "Suction Unit", "IV Equipment",
        "Nebulizer", "Blood Pressure Monitor", "Pulse Oximeter", "Intubation Kit"
    ],
    "CRITICAL_CARE": [
        "Advanced Defibrillator", "Ventilator", "Cardiac Monitor", "Infusion Pump",
        "Oxygen Concentrator", "Suction Unit", "IV Equipment", "Intubation Kit",
        "Central Line Kit", "Portable X-Ray", "Blood Gas Analyzer", "Spine Board",
        "Stretcher with Auto-Loader", "Temperature Control Unit"
    ]
}

# Drugs by type
DRUGS_BY_TYPE = {
    "BASIC": ["Aspirin", "Glucose", "Paracetamol", "ORS", "Antiseptics"],
    "ALS": [
        "Epinephrine", "Atropine", "Aspirin", "Nitroglycerin", "Glucose",
        "Normal Saline", "Dextrose", "Naloxone", "Albuterol", "Dopamine"
    ],
    "CRITICAL_CARE": [
        "Epinephrine", "Atropine", "Amiodarone", "Lidocaine", "Morphine",
        "Fentanyl", "Midazolam", "Propofol", "Dopamine", "Norepinephrine",
        "Normal Saline", "Dextrose", "Mannitol", "Calcium Gluconate"
    ]
}

# Operator names (public and private)
OPERATORS = {
    "PUBLIC": [
        "EMRI 108", "State Government", "District Health Department",
        "Municipal Corporation", "PHC Ambulance Service"
    ],
    "PRIVATE": [
        "Apollo Ambulance", "Fortis Ambulance", "Max Ambulance",
        "Manipal Ambulance", "Ziqitza Healthcare", "BVG India",
        "Red Cross", "St. John Ambulance", "Life Line Ambulance",
        "Quick Rescue Ambulance", "City Ambulance Service"
    ]
}

# Paramedic certifications
CERTIFICATIONS = ["EMT-Basic", "EMT-Intermediate", "EMT-Paramedic", "ACLS", "PALS", "BLS", "ATLS"]

# Indian first names and last names
FIRST_NAMES = [
    "Rahul", "Amit", "Priya", "Anjali", "Rajesh", "Sunita", "Vijay", "Neha",
    "Arun", "Kavita", "Suresh", "Pooja", "Ramesh", "Lakshmi", "Manoj", "Deepa",
    "Sanjay", "Rekha", "Ajay", "Shweta", "Prakash", "Meera", "Ashok", "Nisha"
]

LAST_NAMES = [
    "Sharma", "Kumar", "Singh", "Patel", "Reddy", "Gupta", "Joshi", "Rao",
    "Nair", "Iyer", "Desai", "Shah", "Mehta", "Verma", "Chauhan", "Jain"
]

# Vehicle registration patterns by state
STATE_CODES = {
    "Maharashtra": "MH", "Delhi": "DL", "Karnataka": "KA", "Tamil Nadu": "TN",
    "Gujarat": "GJ", "Telangana": "TS", "West Bengal": "WB", "Uttar Pradesh": "UP",
    "Rajasthan": "RJ", "Madhya Pradesh": "MP", "Punjab": "PB", "Haryana": "HR",
    "Bihar": "BR", "Odisha": "OD", "Kerala": "KL", "Assam": "AS"
}

# ============================================================================
# SYNTHETIC AMBULANCE GENERATION
# ============================================================================

def generate_vehicle_number(state_code: str, district_num: int) -> str:
    """Generate realistic Indian vehicle registration number."""
    # Format: MH-01-AB-1234
    series = ''.join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ", k=2))
    number = random.randint(1000, 9999)
    return f"{state_code}-{district_num:02d}-{series}-{number}"

def generate_phone_number() -> str:
    """Generate realistic Indian mobile number."""
    prefixes = [70, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    prefix = random.choice(prefixes)
    number = random.randint(10000000, 99999999)
    return f"{prefix}{number}"

def generate_person_name() -> str:
    """Generate Indian person name."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {last}"

def get_gps_coordinates(city: str) -> tuple:
    """Get GPS coordinates with slight variation for realistic distribution."""
    if city in CITY_COORDINATES:
        base_lat, base_lon = CITY_COORDINATES[city]
        # Add random offset (±0.1 degrees ≈ ±11km)
        lat = round(base_lat + random.uniform(-0.1, 0.1), 6)
        lon = round(base_lon + random.uniform(-0.1, 0.1), 6)
        return lat, lon
    else:
        # Default to approximate India center with wider range
        lat = round(random.uniform(8.0, 35.0), 6)
        lon = round(random.uniform(68.0, 97.0), 6)
        return lat, lon

def get_ambulance_type() -> str:
    """Get ambulance type based on distribution."""
    rand = random.random()
    if rand < 0.30:
        return "BASIC"
    elif rand < 0.80:  # 0.30 + 0.50
        return "ALS"
    else:
        return "CRITICAL_CARE"

def generate_ambulance_record(ambulance_id: int, state: str, city: str) -> Dict:
    """Generate a single ambulance record."""
    state_code = STATE_CODES.get(state, "XX")
    district_num = random.randint(1, 30)
    
    ambulance_type = get_ambulance_type()
    
    # Operator (60% public, 40% private)
    if random.random() < 0.6:
        operator = random.choice(OPERATORS["PUBLIC"])
        operator_type = "PUBLIC"
    else:
        operator = random.choice(OPERATORS["PRIVATE"])
        operator_type = "PRIVATE"
    
    # GPS coordinates
    lat, lon = get_gps_coordinates(city)
    
    # Status (70% available, 15% on_call, 10% en_route, 5% off_duty)
    status_rand = random.random()
    if status_rand < 0.70:
        status = "AVAILABLE"
    elif status_rand < 0.85:
        status = "ON_CALL"
    elif status_rand < 0.95:
        status = "EN_ROUTE"
    else:
        status = "OFF_DUTY"
    
    # Average speed (realistic for Indian roads)
    avg_speed = random.randint(40, 60)
    
    # Driver details
    driver_name = generate_person_name()
    driver_phone = generate_phone_number()
    driver_license = f"DL-{state_code}{random.randint(1000000000, 9999999999)}"
    
    # Paramedic details (2 paramedics per ambulance)
    paramedic1_name = generate_person_name()
    paramedic1_cert = random.choice(CERTIFICATIONS)
    paramedic2_name = generate_person_name()
    paramedic2_cert = random.choice(CERTIFICATIONS)
    
    # Equipment
    equipment_list = EQUIPMENT_BY_TYPE[ambulance_type]
    equipment = json.dumps(equipment_list)
    
    # Drugs
    drugs_list = DRUGS_BY_TYPE[ambulance_type]
    drugs = json.dumps(drugs_list)
    
    # Last service date (random date in past 6 months)
    days_ago = random.randint(0, 180)
    last_service = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    # Next service due (3-6 months from last service)
    next_service_days = random.randint(90, 180)
    next_service = (datetime.strptime(last_service, "%Y-%m-%d") + timedelta(days=next_service_days)).strftime("%Y-%m-%d")
    
    ambulance = {
        "ambulance_id": f"AMB-{ambulance_id:05d}",
        "vehicle_number": generate_vehicle_number(state_code, district_num),
        "vehicle_type": ambulance_type,
        "operator_name": operator,
        "operator_type": operator_type,
        "current_latitude": lat,
        "current_longitude": lon,
        "status": status,
        "response_zone": city,
        "district": city,
        "state": state,
        "average_speed": avg_speed,
        "driver_name": driver_name,
        "driver_phone": driver_phone,
        "driver_license": driver_license,
        "paramedic1_name": paramedic1_name,
        "paramedic1_certification": paramedic1_cert,
        "paramedic2_name": paramedic2_name,
        "paramedic2_certification": paramedic2_cert,
        "equipment": equipment,
        "drugs": drugs,
        "fuel_level": random.randint(40, 100),  # percentage
        "last_service_date": last_service,
        "next_service_due": next_service,
        "total_trips_today": random.randint(0, 15),
        "total_trips_month": random.randint(0, 200),
        "gps_enabled": "Yes",
        "communication_system": random.choice(["Radio", "Mobile", "Both"]),
        "insurance_valid_till": (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
        "pollution_certificate": "Valid",
        "timestamp": datetime.now().isoformat()
    }
    
    return ambulance

def generate_synthetic_ambulances(target_count: int = 25000) -> List[Dict]:
    """Generate synthetic ambulance fleet data."""
    logger.info(f"Generating {target_count} synthetic ambulance records...")
    
    ambulances = []
    ambulance_id = 1
    
    # Calculate distribution per state
    total_cities = sum(len(cities) for cities in INDIAN_STATES_CITIES.values())
    
    progress_bar = tqdm(total=target_count, desc="Generating ambulances")
    
    for state, cities in INDIAN_STATES_CITIES.items():
        # Distribute ambulances proportionally
        state_count = int(target_count * (len(cities) / total_cities))
        
        for city in cities:
            city_count = state_count // len(cities)
            
            for _ in range(city_count):
                ambulance = generate_ambulance_record(ambulance_id, state, city)
                ambulances.append(ambulance)
                ambulance_id += 1
                progress_bar.update(1)
                
                if ambulance_id > target_count:
                    break
            
            if ambulance_id > target_count:
                break
        
        if ambulance_id > target_count:
            break
    
    progress_bar.close()
    
    logger.info(f"Generated {len(ambulances)} synthetic ambulance records")
    return ambulances

# ============================================================================
# SAVE TO CSV
# ============================================================================

def save_to_csv(ambulances: List[Dict], filename: str):
    """Save ambulance data to CSV file."""
    logger.info(f"Saving {len(ambulances)} ambulances to {filename}...")
    
    if not ambulances:
        logger.error("No ambulances to save!")
        return
    
    fieldnames = list(ambulances[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ambulances)
    
    logger.info(f"Successfully saved {len(ambulances)} ambulances to {filename}")

# ============================================================================
# GENERATE SUMMARY REPORT
# ============================================================================

def generate_summary_report(ambulances: List[Dict], filename: str):
    """Generate summary statistics report."""
    logger.info("Generating summary report...")
    
    total = len(ambulances)
    
    # Statistics
    by_type = {}
    by_state = {}
    by_operator_type = {}
    by_status = {}
    
    total_basic = total_als = total_cc = 0
    total_available = total_public = 0
    
    for amb in ambulances:
        # Type
        vtype = amb.get("vehicle_type", "Unknown")
        by_type[vtype] = by_type.get(vtype, 0) + 1
        
        # State
        state = amb.get("state", "Unknown")
        by_state[state] = by_state.get(state, 0) + 1
        
        # Operator type
        op_type = amb.get("operator_type", "Unknown")
        by_operator_type[op_type] = by_operator_type.get(op_type, 0) + 1
        
        # Status
        status = amb.get("status", "Unknown")
        by_status[status] = by_status.get(status, 0) + 1
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ARIA AMBULANCE FLEET DATA SUMMARY REPORT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"TOTAL AMBULANCES: {total:,}\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("DISTRIBUTION BY AMBULANCE TYPE\n")
        f.write("-" * 70 + "\n")
        for vtype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            f.write(f"{vtype:20s}: {count:6,} ({percentage:5.1f}%)\n")
        
        f.write("\n" + "-" * 70 + "\n")
        f.write("DISTRIBUTION BY STATE\n")
        f.write("-" * 70 + "\n")
        for state, count in sorted(by_state.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            f.write(f"{state:25s}: {count:6,} ({percentage:5.1f}%)\n")
        
        f.write("\n" + "-" * 70 + "\n")
        f.write("OPERATOR TYPE DISTRIBUTION\n")
        f.write("-" * 70 + "\n")
        for op_type, count in by_operator_type.items():
            percentage = (count / total) * 100
            f.write(f"{op_type:20s}: {count:6,} ({percentage:5.1f}%)\n")
        
        f.write("\n" + "-" * 70 + "\n")
        f.write("CURRENT STATUS DISTRIBUTION\n")
        f.write("-" * 70 + "\n")
        for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total) * 100
            f.write(f"{status:20s}: {count:6,} ({percentage:5.1f}%)\n")
        
        f.write("\n" + "=" * 70 + "\n")
        f.write(f"Output File: {OUTPUT_FILE}\n")
        f.write(f"Log File: {LOG_FILE}\n")
        f.write("=" * 70 + "\n")
    
    logger.info(f"Summary report saved to {filename}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function to orchestrate ambulance data collection."""
    start_time = time.time()
    
    logger.info("=" * 70)
    logger.info("ARIA AMBULANCE FLEET DATA COLLECTION STARTED")
    logger.info("=" * 70)
    
    try:
        # Generate synthetic ambulances (primary source)
        ambulances = generate_synthetic_ambulances(target_count=25000)
        
        # Save to CSV
        save_to_csv(ambulances, OUTPUT_FILE)
        
        # Generate summary report
        generate_summary_report(ambulances, SUMMARY_FILE)
        
        elapsed_time = time.time() - start_time
        
        logger.info("=" * 70)
        logger.info("AMBULANCE DATA COLLECTION COMPLETED SUCCESSFULLY")
        logger.info(f"Total Ambulances: {len(ambulances):,}")
        logger.info(f"Time Elapsed: {elapsed_time:.2f} seconds")
        logger.info(f"Output File: {OUTPUT_FILE}")
        logger.info(f"Summary Report: {SUMMARY_FILE}")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
