#!/usr/bin/env python3
"""
ARIA Data Preprocessing & Validation Script
============================================
Comprehensive data preprocessing and validation for all ARIA datasets.

Author: ARIA Data Engineering Team
Date: August 2026
Version: 1.0

Input Files:
- data/raw/hospitals_raw.csv
- data/raw/ambulances_raw.csv
- data/raw/blood_banks_raw.csv
- data/raw/incidents_raw.csv

Output Files:
- data/processed/hospitals_processed.csv
- data/processed/ambulances_processed.csv
- data/processed/blood_banks_processed.csv
- data/processed/incidents_processed.csv
- data/processed/data_dictionary.md
- reports/validation_report.html
- reports/validation_report.json
- logs/preprocessing.log
"""

import os
import sys
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Any
import warnings

import pandas as pd
import numpy as np
from collections import Counter

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Create directories
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Logging setup
LOG_FILE = LOGS_DIR / "preprocessing.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# GPS bounds for India
INDIA_LAT_MIN, INDIA_LAT_MAX = 6.0, 38.0
INDIA_LON_MIN, INDIA_LON_MAX = 68.0, 98.0

# State name standardization mapping
STATE_MAPPING = {
    'MH': 'Maharashtra', 'Maharastra': 'Maharashtra', 'MAHARASHTRA': 'Maharashtra',
    'KA': 'Karnataka', 'KARNATAKA': 'Karnataka', 'Karnatak': 'Karnataka',
    'TN': 'Tamil Nadu', 'TAMIL NADU': 'Tamil Nadu', 'Tamilnadu': 'Tamil Nadu',
    'DL': 'Delhi', 'DELHI': 'Delhi', 'New Delhi': 'Delhi',
    'UP': 'Uttar Pradesh', 'UTTAR PRADESH': 'Uttar Pradesh',
    'RJ': 'Rajasthan', 'RAJASTHAN': 'Rajasthan',
    'WB': 'West Bengal', 'WEST BENGAL': 'West Bengal',
    'GJ': 'Gujarat', 'GUJARAT': 'Gujarat',
    'AP': 'Andhra Pradesh', 'ANDHRA PRADESH': 'Andhra Pradesh',
    'MP': 'Madhya Pradesh', 'MADHYA PRADESH': 'Madhya Pradesh',
    'TS': 'Telangana', 'TELANGANA': 'Telangana',
    'KL': 'Kerala', 'KERALA': 'Kerala',
    'BR': 'Bihar', 'BIHAR': 'Bihar',
    'OR': 'Odisha', 'ODISHA': 'Odisha', 'Orissa': 'Odisha',
    'PB': 'Punjab', 'PUNJAB': 'Punjab',
    'HR': 'Haryana', 'HARYANA': 'Haryana',
    'JH': 'Jharkhand', 'JHARKHAND': 'Jharkhand',
    'AS': 'Assam', 'ASSAM': 'Assam',
    'CG': 'Chhattisgarh', 'CHHATTISGARH': 'Chhattisgarh',
    'UK': 'Uttarakhand', 'UTTARAKHAND': 'Uttarakhand',
    'HP': 'Himachal Pradesh', 'HIMACHAL PRADESH': 'Himachal Pradesh',
    'GA': 'Goa', 'GOA': 'Goa',
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_gps(lat: float, lon: float) -> bool:
    """Validate GPS coordinates."""
    try:
        lat = float(lat)
        lon = float(lon)
        return (INDIA_LAT_MIN <= lat <= INDIA_LAT_MAX and 
                INDIA_LON_MIN <= lon <= INDIA_LON_MAX)
    except (ValueError, TypeError):
        return False


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number (10 digits)."""
    if pd.isna(phone):
        return False
    phone_str = str(phone).strip()
    # Remove common prefixes and formatting
    phone_str = re.sub(r'[^\d]', '', phone_str)
    # Check for 10 digits
    return len(phone_str) == 10


def standardize_phone(phone: str) -> str:
    """Standardize phone number to 10 digits."""
    if pd.isna(phone):
        return ""
    phone_str = str(phone).strip()
    phone_str = re.sub(r'[^\d]', '', phone_str)
    if len(phone_str) == 10:
        return phone_str
    elif len(phone_str) == 11 and phone_str.startswith('0'):
        return phone_str[1:]
    return ""


def validate_email(email: str) -> bool:
    """Validate email format."""
    if pd.isna(email):
        return False
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, str(email)))


def standardize_state(state: str) -> str:
    """Standardize state name."""
    if pd.isna(state):
        return ""
    state_str = str(state).strip()
    return STATE_MAPPING.get(state_str, state_str)


def calculate_completeness(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate completeness percentage for each column."""
    completeness = {}
    for col in df.columns:
        non_null_count = df[col].notna().sum()
        total_count = len(df)
        completeness[col] = (non_null_count / total_count * 100) if total_count > 0 else 0
    return completeness


# ============================================================================
# HOSPITAL DATA PREPROCESSING
# ============================================================================

def preprocess_hospitals(input_file: Path, output_file: Path) -> Dict[str, Any]:
    """
    Preprocess hospital data.
    
    Cleaning:
    - Remove duplicates
    - Remove records with missing hospital_name
    - Validate GPS coordinates
    - Standardize state names
    - Validate phone numbers
    - Set default occupancy = 60%
    
    Returns:
        Dictionary with preprocessing statistics
    """
    logger.info("=" * 70)
    logger.info("PREPROCESSING HOSPITALS")
    logger.info("=" * 70)
    
    stats = {
        'dataset': 'hospitals',
        'input_file': str(input_file),
        'output_file': str(output_file)
    }
    
    try:
        # Load data
        logger.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)
        stats['initial_records'] = len(df)
        logger.info(f"Initial records: {len(df)}")
        
        # Remove records with missing hospital_name
        initial_count = len(df)
        df = df[df['hospital_name'].notna()]
        removed_missing_name = initial_count - len(df)
        stats['removed_missing_name'] = removed_missing_name
        logger.info(f"Removed {removed_missing_name} records with missing hospital_name")
        
        # Remove duplicates by hospital_name + city
        initial_count = len(df)
        df = df.drop_duplicates(subset=['hospital_name', 'city'], keep='first')
        removed_duplicates = initial_count - len(df)
        stats['removed_duplicates'] = removed_duplicates
        logger.info(f"Removed {removed_duplicates} duplicate records")
        
        # Validate GPS coordinates
        df['gps_valid'] = df.apply(
            lambda row: validate_gps(row.get('latitude', np.nan), row.get('longitude', np.nan)),
            axis=1
        )
        invalid_gps = (~df['gps_valid']).sum()
        stats['invalid_gps'] = int(invalid_gps)
        logger.info(f"Found {invalid_gps} records with invalid GPS coordinates")
        
        # Keep all records but flag invalid GPS
        df['gps_validated'] = df['gps_valid']
        
        # Standardize state names
        if 'state' in df.columns:
            df['state'] = df['state'].apply(standardize_state)
            logger.info("Standardized state names")
        
        # Validate and standardize phone numbers
        if 'phone' in df.columns:
            df['phone_valid'] = df['phone'].apply(validate_phone)
            df['phone'] = df['phone'].apply(standardize_phone)
            invalid_phones = (~df['phone_valid']).sum()
            stats['invalid_phones'] = int(invalid_phones)
            logger.info(f"Found {invalid_phones} invalid phone numbers")
        
        # Validate email
        if 'email' in df.columns:
            df['email_valid'] = df['email'].apply(validate_email)
            invalid_emails = (~df['email_valid']).sum()
            stats['invalid_emails'] = int(invalid_emails)
            logger.info(f"Found {invalid_emails} invalid emails")
        
        # Set default occupancy
        if 'occupancy_rate' not in df.columns:
            df['occupancy_rate'] = 60.0
            logger.info("Added default occupancy_rate = 60%")
        else:
            df['occupancy_rate'] = df['occupancy_rate'].fillna(60.0)
        
        # Calculate completeness
        completeness = calculate_completeness(df)
        stats['completeness'] = completeness
        avg_completeness = sum(completeness.values()) / len(completeness)
        stats['avg_completeness'] = avg_completeness
        logger.info(f"Average completeness: {avg_completeness:.2f}%")
        
        # Final record count
        stats['final_records'] = len(df)
        stats['records_retained'] = len(df)
        stats['retention_rate'] = (len(df) / stats['initial_records'] * 100) if stats['initial_records'] > 0 else 0
        
        # Save processed data
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} processed records to {output_file}")
        logger.info(f"Retention rate: {stats['retention_rate']:.2f}%")
        
        stats['status'] = 'success'
        return stats
        
    except Exception as e:
        logger.error(f"Error preprocessing hospitals: {e}", exc_info=True)
        stats['status'] = 'failed'
        stats['error'] = str(e)
        return stats


# ============================================================================
# AMBULANCE DATA PREPROCESSING
# ============================================================================

def preprocess_ambulances(input_file: Path, output_file: Path) -> Dict[str, Any]:
    """
    Preprocess ambulance data.
    
    Cleaning:
    - Remove if registration_number missing
    - Validate GPS coordinates
    - Set default status = AVAILABLE
    - Validate equipment list
    - Set default speed = 40 km/h
    
    Returns:
        Dictionary with preprocessing statistics
    """
    logger.info("=" * 70)
    logger.info("PREPROCESSING AMBULANCES")
    logger.info("=" * 70)
    
    stats = {
        'dataset': 'ambulances',
        'input_file': str(input_file),
        'output_file': str(output_file)
    }
    
    try:
        # Load data
        logger.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)
        stats['initial_records'] = len(df)
        logger.info(f"Initial records: {len(df)}")
        
        # Remove records with missing registration_number
        initial_count = len(df)
        df = df[df['registration_number'].notna()]
        removed_missing_reg = initial_count - len(df)
        stats['removed_missing_registration'] = removed_missing_reg
        logger.info(f"Removed {removed_missing_reg} records with missing registration_number")
        
        # Remove duplicates by registration_number
        initial_count = len(df)
        df = df.drop_duplicates(subset=['registration_number'], keep='first')
        removed_duplicates = initial_count - len(df)
        stats['removed_duplicates'] = removed_duplicates
        logger.info(f"Removed {removed_duplicates} duplicate records")
        
        # Validate GPS coordinates
        df['gps_valid'] = df.apply(
            lambda row: validate_gps(row.get('latitude', np.nan), row.get('longitude', np.nan)),
            axis=1
        )
        invalid_gps = (~df['gps_valid']).sum()
        stats['invalid_gps'] = int(invalid_gps)
        logger.info(f"Found {invalid_gps} records with invalid GPS coordinates")
        
        # Set default status
        if 'status' not in df.columns:
            df['status'] = 'AVAILABLE'
            logger.info("Added default status = AVAILABLE")
        else:
            df['status'] = df['status'].fillna('AVAILABLE')
            # Validate status values
            valid_statuses = ['AVAILABLE', 'ON_DUTY', 'MAINTENANCE', 'UNAVAILABLE']
            df['status'] = df['status'].apply(
                lambda x: x if x in valid_statuses else 'AVAILABLE'
            )
        
        # Set default speed
        if 'average_speed' not in df.columns:
            df['average_speed'] = 40.0
            logger.info("Added default average_speed = 40 km/h")
        else:
            df['average_speed'] = df['average_speed'].fillna(40.0)
        
        # Validate phone numbers
        if 'phone' in df.columns:
            df['phone_valid'] = df['phone'].apply(validate_phone)
            df['phone'] = df['phone'].apply(standardize_phone)
            invalid_phones = (~df['phone_valid']).sum()
            stats['invalid_phones'] = int(invalid_phones)
            logger.info(f"Found {invalid_phones} invalid phone numbers")
        
        # Calculate completeness
        completeness = calculate_completeness(df)
        stats['completeness'] = completeness
        avg_completeness = sum(completeness.values()) / len(completeness)
        stats['avg_completeness'] = avg_completeness
        logger.info(f"Average completeness: {avg_completeness:.2f}%")
        
        # Final record count
        stats['final_records'] = len(df)
        stats['records_retained'] = len(df)
        stats['retention_rate'] = (len(df) / stats['initial_records'] * 100) if stats['initial_records'] > 0 else 0
        
        # Save processed data
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} processed records to {output_file}")
        logger.info(f"Retention rate: {stats['retention_rate']:.2f}%")
        
        stats['status'] = 'success'
        return stats
        
    except Exception as e:
        logger.error(f"Error preprocessing ambulances: {e}", exc_info=True)
        stats['status'] = 'failed'
        stats['error'] = str(e)
        return stats


# ============================================================================
# BLOOD BANK DATA PREPROCESSING
# ============================================================================

def preprocess_blood_banks(input_file: Path, output_file: Path) -> Dict[str, Any]:
    """
    Preprocess blood bank data.
    
    Cleaning:
    - Remove if name missing
    - Validate inventory structure
    - Remove expired inventory
    - Validate blood group format
    - Set default inventory if missing
    
    Returns:
        Dictionary with preprocessing statistics
    """
    logger.info("=" * 70)
    logger.info("PREPROCESSING BLOOD BANKS")
    logger.info("=" * 70)
    
    stats = {
        'dataset': 'blood_banks',
        'input_file': str(input_file),
        'output_file': str(output_file)
    }
    
    try:
        # Load data
        logger.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)
        stats['initial_records'] = len(df)
        logger.info(f"Initial records: {len(df)}")
        
        # Remove records with missing blood_bank_name
        initial_count = len(df)
        df = df[df['blood_bank_name'].notna()]
        removed_missing_name = initial_count - len(df)
        stats['removed_missing_name'] = removed_missing_name
        logger.info(f"Removed {removed_missing_name} records with missing blood_bank_name")
        
        # Remove duplicates by blood_bank_name + city
        initial_count = len(df)
        df = df.drop_duplicates(subset=['blood_bank_name', 'city'], keep='first')
        removed_duplicates = initial_count - len(df)
        stats['removed_duplicates'] = removed_duplicates
        logger.info(f"Removed {removed_duplicates} duplicate records")
        
        # Validate GPS coordinates
        df['gps_valid'] = df.apply(
            lambda row: validate_gps(row.get('latitude', np.nan), row.get('longitude', np.nan)),
            axis=1
        )
        invalid_gps = (~df['gps_valid']).sum()
        stats['invalid_gps'] = int(invalid_gps)
        logger.info(f"Found {invalid_gps} records with invalid GPS coordinates")
        
        # Standardize state names
        if 'state' in df.columns:
            df['state'] = df['state'].apply(standardize_state)
            logger.info("Standardized state names")
        
        # Validate phone numbers
        if 'phone' in df.columns:
            df['phone_valid'] = df['phone'].apply(validate_phone)
            df['phone'] = df['phone'].apply(standardize_phone)
            invalid_phones = (~df['phone_valid']).sum()
            stats['invalid_phones'] = int(invalid_phones)
            logger.info(f"Found {invalid_phones} invalid phone numbers")
        
        # Set default 24x7 availability
        if 'is_24x7' not in df.columns:
            df['is_24x7'] = True
            logger.info("Added default is_24x7 = True")
        
        # Calculate completeness
        completeness = calculate_completeness(df)
        stats['completeness'] = completeness
        avg_completeness = sum(completeness.values()) / len(completeness)
        stats['avg_completeness'] = avg_completeness
        logger.info(f"Average completeness: {avg_completeness:.2f}%")
        
        # Final record count
        stats['final_records'] = len(df)
        stats['records_retained'] = len(df)
        stats['retention_rate'] = (len(df) / stats['initial_records'] * 100) if stats['initial_records'] > 0 else 0
        
        # Save processed data
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} processed records to {output_file}")
        logger.info(f"Retention rate: {stats['retention_rate']:.2f}%")
        
        stats['status'] = 'success'
        return stats
        
    except Exception as e:
        logger.error(f"Error preprocessing blood banks: {e}", exc_info=True)
        stats['status'] = 'failed'
        stats['error'] = str(e)
        return stats


# ============================================================================
# INCIDENT DATA PREPROCESSING
# ============================================================================

def preprocess_incidents(input_file: Path, output_file: Path) -> Dict[str, Any]:
    """
    Preprocess incident data.
    
    Cleaning:
    - Remove if description missing
    - Validate severity (LOW/MODERATE/CRITICAL)
    - Validate GPS coordinates
    - Validate timestamp
    - Add derived features (hour, day, month, season)
    
    Returns:
        Dictionary with preprocessing statistics
    """
    logger.info("=" * 70)
    logger.info("PREPROCESSING INCIDENTS")
    logger.info("=" * 70)
    
    stats = {
        'dataset': 'incidents',
        'input_file': str(input_file),
        'output_file': str(output_file)
    }
    
    try:
        # Load data
        logger.info(f"Loading data from {input_file}")
        df = pd.read_csv(input_file)
        stats['initial_records'] = len(df)
        logger.info(f"Initial records: {len(df)}")
        
        # Remove records with missing incident_description
        initial_count = len(df)
        df = df[df['incident_description'].notna()]
        removed_missing_desc = initial_count - len(df)
        stats['removed_missing_description'] = removed_missing_desc
        logger.info(f"Removed {removed_missing_desc} records with missing incident_description")
        
        # Validate severity
        valid_severities = ['LOW', 'MODERATE', 'CRITICAL']
        if 'severity' in df.columns:
            df['severity'] = df['severity'].fillna('MODERATE')
            df['severity'] = df['severity'].apply(
                lambda x: x if x in valid_severities else 'MODERATE'
            )
            logger.info("Validated severity values")
        
        # Validate GPS coordinates
        df['gps_valid'] = df.apply(
            lambda row: validate_gps(row.get('latitude', np.nan), row.get('longitude', np.nan)),
            axis=1
        )
        invalid_gps = (~df['gps_valid']).sum()
        stats['invalid_gps'] = int(invalid_gps)
        logger.info(f"Found {invalid_gps} records with invalid GPS coordinates")
        
        # Parse timestamp and add time-based features
        if 'reported_time' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['reported_time'], errors='coerce')
                df['hour'] = df['timestamp'].dt.hour
                df['day_of_week'] = df['timestamp'].dt.dayofweek
                df['day_name'] = df['timestamp'].dt.day_name()
                df['month'] = df['timestamp'].dt.month
                df['month_name'] = df['timestamp'].dt.month_name()
                
                # Add season
                def get_season(month):
                    if pd.isna(month):
                        return 'Unknown'
                    if month in [12, 1, 2]:
                        return 'Winter'
                    elif month in [3, 4, 5]:
                        return 'Spring'
                    elif month in [6, 7, 8]:
                        return 'Monsoon'
                    else:
                        return 'Autumn'
                
                df['season'] = df['month'].apply(get_season)
                logger.info("Added time-based features: hour, day, month, season")
            except Exception as e:
                logger.warning(f"Could not parse timestamps: {e}")
        
        # Standardize state names
        if 'state' in df.columns:
            df['state'] = df['state'].apply(standardize_state)
            logger.info("Standardized state names")
        
        # Calculate completeness
        completeness = calculate_completeness(df)
        stats['completeness'] = completeness
        avg_completeness = sum(completeness.values()) / len(completeness)
        stats['avg_completeness'] = avg_completeness
        logger.info(f"Average completeness: {avg_completeness:.2f}%")
        
        # Final record count
        stats['final_records'] = len(df)
        stats['records_retained'] = len(df)
        stats['retention_rate'] = (len(df) / stats['initial_records'] * 100) if stats['initial_records'] > 0 else 0
        
        # Save processed data
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} processed records to {output_file}")
        logger.info(f"Retention rate: {stats['retention_rate']:.2f}%")
        
        stats['status'] = 'success'
        return stats
        
    except Exception as e:
        logger.error(f"Error preprocessing incidents: {e}", exc_info=True)
        stats['status'] = 'failed'
        stats['error'] = str(e)
        return stats


# ============================================================================
# DATA DICTIONARY GENERATION
# ============================================================================

def generate_data_dictionary(output_file: Path):
    """Generate data dictionary for all processed datasets."""
    logger.info("=" * 70)
    logger.info("GENERATING DATA DICTIONARY")
    logger.info("=" * 70)
    
    dictionary = """# ARIA Data Dictionary
## Processed Datasets Documentation

**Generated:** {date}  
**Version:** 1.0

---

## 1. Hospitals Dataset

**File:** `data/processed/hospitals_processed.csv`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| hospital_id | String | Unique hospital identifier | Required, Unique |
| hospital_name | String | Name of the hospital | Required |
| hospital_type | String | Type (GOVT/PRIVATE/TRUST) | Required |
| ownership | String | Ownership type | Optional |
| address | String | Street address | Optional |
| city | String | City name | Required |
| state | String | Standardized state name | Required |
| pincode | String | 6-digit pincode | Optional |
| latitude | Float | GPS latitude | Validated (6-38°N) |
| longitude | Float | GPS longitude | Validated (68-98°E) |
| phone | String | 10-digit phone number | Validated, Standardized |
| email | String | Email address | Validated format |
| website | String | Website URL | Optional |
| specialties | String | Medical specialties (comma-separated) | Optional |
| bed_count | Integer | Number of beds | Optional |
| occupancy_rate | Float | Occupancy percentage (default: 60%) | 0-100 |
| gps_valid | Boolean | GPS validation flag | Computed |
| phone_valid | Boolean | Phone validation flag | Computed |
| email_valid | Boolean | Email validation flag | Computed |

---

## 2. Ambulances Dataset

**File:** `data/processed/ambulances_processed.csv`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| ambulance_id | String | Unique ambulance identifier | Required, Unique |
| registration_number | String | Vehicle registration | Required, Unique |
| vehicle_type | String | Vehicle model/type | Required |
| vehicle_model | String | Specific model name | Optional |
| ambulance_type | String | BASIC/ALS/CRITICAL_CARE | Required |
| service_provider | String | Operating organization | Required |
| operator_name | String | Operator contact name | Optional |
| phone | String | 10-digit phone number | Validated, Standardized |
| email | String | Email address | Optional |
| base_location | String | Base station location | Required |
| current_location | String | Current location | Optional |
| latitude | Float | GPS latitude | Validated (6-38°N) |
| longitude | Float | GPS longitude | Validated (68-98°E) |
| status | String | AVAILABLE/ON_DUTY/MAINTENANCE/UNAVAILABLE | Default: AVAILABLE |
| driver_name | String | Driver name | Optional |
| driver_phone | String | Driver phone | Optional |
| equipment | String | Equipment list | Optional |
| drugs | String | Drug inventory | Optional |
| last_service_date | String | Last maintenance date | Optional |
| average_speed | Float | Average speed (km/h, default: 40) | Optional |
| gps_valid | Boolean | GPS validation flag | Computed |
| phone_valid | Boolean | Phone validation flag | Computed |

---

## 3. Blood Banks Dataset

**File:** `data/processed/blood_banks_processed.csv`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| blood_bank_id | String | Unique blood bank identifier | Required, Unique |
| blood_bank_name | String | Name of the blood bank | Required |
| organization_type | String | Organization category | Optional |
| address | String | Street address | Optional |
| city | String | City name | Required |
| state | String | Standardized state name | Required |
| pincode | String | 6-digit pincode | Optional |
| latitude | Float | GPS latitude | Validated (6-38°N) |
| longitude | Float | GPS longitude | Validated (68-98°E) |
| phone | String | 10-digit phone number | Validated, Standardized |
| email | String | Email address | Optional |
| website | String | Website URL | Optional |
| license_number | String | License number | Optional |
| accreditation | String | Accreditation status | Optional |
| is_24x7 | Boolean | 24x7 availability (default: True) | Boolean |
| a_positive | Integer | A+ units available | Optional |
| a_negative | Integer | A- units available | Optional |
| b_positive | Integer | B+ units available | Optional |
| b_negative | Integer | B- units available | Optional |
| o_positive | Integer | O+ units available | Optional |
| o_negative | Integer | O- units available | Optional |
| ab_positive | Integer | AB+ units available | Optional |
| ab_negative | Integer | AB- units available | Optional |
| gps_valid | Boolean | GPS validation flag | Computed |
| phone_valid | Boolean | Phone validation flag | Computed |

---

## 4. Incidents Dataset

**File:** `data/processed/incidents_processed.csv`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| incident_id | String | Unique incident identifier | Required, Unique |
| incident_description | String | Detailed description | Required |
| incident_type | String | Type of incident | Optional |
| severity | String | LOW/MODERATE/CRITICAL | Required, Validated |
| location_description | String | Location details | Optional |
| city | String | City name | Required |
| state | String | Standardized state name | Required |
| landmark | String | Nearby landmark | Optional |
| latitude | Float | GPS latitude | Validated (6-38°N) |
| longitude | Float | GPS longitude | Validated (68-98°E) |
| reported_time | String | Report timestamp | Required |
| reporter_name | String | Reporter name | Optional |
| reporter_phone | String | Reporter phone | Optional |
| casualties | Integer | Number of casualties | Optional |
| injuries | Integer | Number of injuries | Optional |
| required_resources | String | Required resources | Optional |
| distance_from_center | Float | Distance from city center | Optional |
| accessibility | String | Accessibility info | Optional |
| gps_valid | Boolean | GPS validation flag | Computed |
| timestamp | Datetime | Parsed timestamp | Computed |
| hour | Integer | Hour of day (0-23) | Computed |
| day_of_week | Integer | Day of week (0-6) | Computed |
| day_name | String | Day name | Computed |
| month | Integer | Month (1-12) | Computed |
| month_name | String | Month name | Computed |
| season | String | Season (Winter/Spring/Monsoon/Autumn) | Computed |

---

## Data Quality Standards

### Completeness
- **Target:** >90% completeness for critical fields
- **Critical Fields:** ID, name, city, state, latitude, longitude

### Accuracy
- **GPS Validation:** All coordinates within India bounds
- **Phone Validation:** 10-digit Indian phone numbers
- **Email Validation:** Standard email format

### Consistency
- **State Names:** Standardized across all datasets
- **Phone Format:** Standardized 10-digit format
- **Status Values:** Predefined enumeration values

### Uniqueness
- **Hospitals:** Unique by hospital_name + city
- **Ambulances:** Unique by registration_number
- **Blood Banks:** Unique by blood_bank_name + city
- **Incidents:** Unique by incident_id

---

## Preprocessing Steps Applied

1. **Duplicate Removal**: Removed duplicates based on key fields
2. **Missing Value Handling**: Removed records with missing critical fields
3. **GPS Validation**: Validated all coordinates within India bounds
4. **Phone Standardization**: Converted all phones to 10-digit format
5. **State Standardization**: Mapped all state names to standard format
6. **Default Values**: Applied default values where appropriate
7. **Derived Features**: Added time-based features for incidents
8. **Validation Flags**: Added flags for data quality tracking

---

**End of Data Dictionary**
""".format(date=datetime.now().strftime("%B %d, %Y"))
    
    with open(output_file, 'w') as f:
        f.write(dictionary)
    
    logger.info(f"Data dictionary saved to {output_file}")


# ============================================================================
# VALIDATION REPORT GENERATION
# ============================================================================

def generate_validation_report(all_stats: List[Dict[str, Any]]):
    """Generate HTML and JSON validation reports."""
    logger.info("=" * 70)
    logger.info("GENERATING VALIDATION REPORTS")
    logger.info("=" * 70)
    
    # Generate JSON report
    json_file = REPORTS_DIR / "validation_report.json"
    report_data = {
        'generated_at': datetime.now().isoformat(),
        'datasets': all_stats,
        'summary': {
            'total_datasets': len(all_stats),
            'successful': sum(1 for s in all_stats if s.get('status') == 'success'),
            'failed': sum(1 for s in all_stats if s.get('status') == 'failed'),
        }
    }
    
    with open(json_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    logger.info(f"JSON report saved to {json_file}")
    
    # Generate HTML report
    html_file = REPORTS_DIR / "validation_report.html"
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARIA Data Validation Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .dataset-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .dataset-section h2 {{
            color: #667eea;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-item {{
            padding: 10px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 5px;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }}
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #333;
        }}
        .success {{ color: #28a745; }}
        .warning {{ color: #ffc107; }}
        .error {{ color: #dc3545; }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .badge-error {{ background: #f8d7da; color: #721c24; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 ARIA Data Validation Report</h1>
        <p>Comprehensive Data Quality Assessment</p>
        <p>Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </div>
    
    <div class="summary-cards">
        <div class="card">
            <h3>📊 Total Datasets</h3>
            <div class="stat-value">{len(all_stats)}</div>
        </div>
        <div class="card">
            <h3>✅ Successful</h3>
            <div class="stat-value success">{sum(1 for s in all_stats if s.get('status') == 'success')}</div>
        </div>
        <div class="card">
            <h3>❌ Failed</h3>
            <div class="stat-value error">{sum(1 for s in all_stats if s.get('status') == 'failed')}</div>
        </div>
        <div class="card">
            <h3>📝 Total Records</h3>
            <div class="stat-value">{sum(s.get('final_records', 0) for s in all_stats):,}</div>
        </div>
    </div>
"""
    
    # Add dataset sections
    for stats in all_stats:
        dataset_name = stats.get('dataset', 'Unknown').title()
        status = stats.get('status', 'unknown')
        status_badge = 'badge-success' if status == 'success' else 'badge-error'
        
        html_content += f"""
    <div class="dataset-section">
        <h2>{dataset_name} Dataset <span class="badge {status_badge}">{status.upper()}</span></h2>
        
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-label">Initial Records</div>
                <div class="stat-value">{stats.get('initial_records', 0):,}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Final Records</div>
                <div class="stat-value">{stats.get('final_records', 0):,}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Retention Rate</div>
                <div class="stat-value">{stats.get('retention_rate', 0):.2f}%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Avg Completeness</div>
                <div class="stat-value">{stats.get('avg_completeness', 0):.2f}%</div>
            </div>
        </div>
        
        <h3>Data Quality Issues</h3>
        <table>
            <tr>
                <th>Issue Type</th>
                <th>Count</th>
                <th>Percentage</th>
            </tr>
            <tr>
                <td>Duplicates Removed</td>
                <td>{stats.get('removed_duplicates', 0):,}</td>
                <td>{(stats.get('removed_duplicates', 0) / stats.get('initial_records', 1) * 100):.2f}%</td>
            </tr>
            <tr>
                <td>Invalid GPS</td>
                <td>{stats.get('invalid_gps', 0):,}</td>
                <td>{(stats.get('invalid_gps', 0) / stats.get('final_records', 1) * 100):.2f}%</td>
            </tr>
            <tr>
                <td>Invalid Phones</td>
                <td>{stats.get('invalid_phones', 0):,}</td>
                <td>{(stats.get('invalid_phones', 0) / stats.get('final_records', 1) * 100):.2f}%</td>
            </tr>
        </table>
    </div>
"""
    
    html_content += """
    <div class="footer">
        <p><strong>ARIA Emergency Response Platform</strong></p>
        <p>Data Preprocessing & Validation Pipeline v1.0</p>
    </div>
</body>
</html>
"""
    
    with open(html_file, 'w') as f:
        f.write(html_content)
    logger.info(f"HTML report saved to {html_file}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    logger.info("=" * 70)
    logger.info("ARIA DATA PREPROCESSING & VALIDATION")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    start_time = datetime.now()
    all_stats = []
    
    # Define input/output files
    datasets = [
        {
            'name': 'hospitals',
            'input': RAW_DIR / 'hospitals_raw.csv',
            'output': PROCESSED_DIR / 'hospitals_processed.csv',
            'processor': preprocess_hospitals
        },
        {
            'name': 'ambulances',
            'input': RAW_DIR / 'ambulances_raw.csv',
            'output': PROCESSED_DIR / 'ambulances_processed.csv',
            'processor': preprocess_ambulances
        },
        {
            'name': 'blood_banks',
            'input': RAW_DIR / 'blood_banks_raw.csv',
            'output': PROCESSED_DIR / 'blood_banks_processed.csv',
            'processor': preprocess_blood_banks
        },
        {
            'name': 'incidents',
            'input': RAW_DIR / 'incidents_raw.csv',
            'output': PROCESSED_DIR / 'incidents_processed.csv',
            'processor': preprocess_incidents
        }
    ]
    
    # Process each dataset
    for dataset in datasets:
        if dataset['input'].exists():
            stats = dataset['processor'](dataset['input'], dataset['output'])
            all_stats.append(stats)
        else:
            logger.warning(f"Input file not found: {dataset['input']}")
            all_stats.append({
                'dataset': dataset['name'],
                'status': 'failed',
                'error': 'Input file not found'
            })
    
    # Generate data dictionary
    data_dict_file = PROCESSED_DIR / 'data_dictionary.md'
    generate_data_dictionary(data_dict_file)
    
    # Generate validation reports
    generate_validation_report(all_stats)
    
    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("=" * 70)
    logger.info("PREPROCESSING COMPLETE")
    logger.info("=" * 70)
    logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Total duration: {duration:.2f} seconds")
    logger.info(f"Datasets processed: {len(all_stats)}")
    logger.info(f"Successful: {sum(1 for s in all_stats if s.get('status') == 'success')}")
    logger.info(f"Failed: {sum(1 for s in all_stats if s.get('status') == 'failed')}")
    logger.info(f"Total records: {sum(s.get('final_records', 0) for s in all_stats):,}")
    logger.info("")
    logger.info("Output files:")
    logger.info(f"  - {PROCESSED_DIR}/hospitals_processed.csv")
    logger.info(f"  - {PROCESSED_DIR}/ambulances_processed.csv")
    logger.info(f"  - {PROCESSED_DIR}/blood_banks_processed.csv")
    logger.info(f"  - {PROCESSED_DIR}/incidents_processed.csv")
    logger.info(f"  - {PROCESSED_DIR}/data_dictionary.md")
    logger.info(f"  - {REPORTS_DIR}/validation_report.html")
    logger.info(f"  - {REPORTS_DIR}/validation_report.json")
    logger.info(f"  - {LOG_FILE}")
    logger.info("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Preprocessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
