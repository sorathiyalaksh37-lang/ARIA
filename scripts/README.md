# ARIA Data Collection Scripts
## Sprint 1: Data Collection & Preparation

**Author:** ARIA Data Engineering Team  
**Date:** August 22, 2026  
**Version:** 1.0

---

## 📋 Overview

This directory contains production-ready Python scripts for collecting all data required for the ARIA Emergency Response Platform. These scripts collect data from multiple sources and generate synthetic data where real data is unavailable.

**Total Data Output:** 140,000+ records
- 15,000+ Hospitals
- 25,000+ Ambulances
- 2,500+ Blood Banks
- 100,000+ Emergency Incidents (training data)

---

## 📂 Scripts

### 1. `hospital_scraper.py`
**Purpose:** Collect hospital data from multiple sources

**Data Sources:**
- National Health Portal (NHP): https://nhp.gov.in/hospitals
- Ayushman Bharat (PMJAY): https://pmjay.gov.in/hospitals
- OpenStreetMap (OSM): https://overpass-api.de/api/interpreter
- Google Places API: https://developers.google.com/maps
- Synthetic generation for complete coverage

**Output:**
- `data/raw/hospitals_raw.csv` (15,000+ records)
- `data/raw/hospital_summary.txt` (statistics)
- `logs/hospital_scrape.log`

**Features:**
- Rate limiting (1 req/sec)
- Retry logic (3 attempts with exponential backoff)
- GPS coordinate validation
- Duplicate removal
- Progress tracking with tqdm

**Run:**
```bash
python hospital_scraper.py
```

**Expected Runtime:** 10-15 minutes

---

### 2. `ambulance_scraper.py`
**Purpose:** Collect ambulance fleet data

**Data Sources:**
- EMRI 108 Ambulance Service: https://www.emri.in
- Google Places API (Private Ambulances)
- Synthetic generation with realistic distribution

**Output:**
- `data/raw/ambulances_raw.csv` (25,000+ records)
- `data/raw/ambulances_summary.txt`
- `logs/ambulance_scrape.log`

**Distribution:**
- 30% BASIC ambulances
- 50% ALS (Advanced Life Support)
- 20% CRITICAL_CARE

**Features:**
- Realistic equipment by ambulance type
- GPS coordinates for all major Indian cities
- Driver and paramedic details
- Service history and maintenance tracking

**Run:**
```bash
python ambulance_scraper.py
```

**Expected Runtime:** 3-5 minutes

---

### 3. `blood_bank_scraper.py`
**Purpose:** Collect blood bank inventory data

**Data Sources:**
- National Blood Transfusion Council: http://nbtc.naco.gov.in
- Red Cross India: https://www.indianredcross.org
- Synthetic generation with realistic inventory

**Output:**
- `data/raw/blood_banks_raw.csv` (2,500+ records)
- `data/raw/blood_banks_summary.txt`
- `logs/blood_bank_scrape.log`

**Blood Group Distribution:**
- O+: 30%
- A+: 34%
- B+: 22%
- AB+: 10%
- Rare groups (O-, A-, B-, AB-): 4%

**Features:**
- Realistic inventory levels (0-100 units per group)
- Expiry dates (blood valid 35-42 days)
- Testing services availability
- Accreditation status (NABH, NABL, ISO)
- 24x7 availability tracking

**Run:**
```bash
python blood_bank_scraper.py
```

**Expected Runtime:** 2-3 minutes

---

### 4. `incident_generator.py`
**Purpose:** Generate synthetic emergency incidents for ML training

**Data Generation:**
- 100,000+ unique incident records
- Realistic Indian context (cities, localities, landmarks)
- Natural language descriptions with variations

**Output:**
- `data/raw/incidents_raw.csv` (100,000+ records)
- `data/raw/incidents_summary.txt`
- `logs/incident_generation.log`

**Severity Distribution:**
- CRITICAL: 15% (15,000 incidents)
- MODERATE: 35% (35,000 incidents)
- LOW: 50% (50,000 incidents)

**Incident Types:**
- ACCIDENT (vehicle, motorcycle, fall)
- MEDICAL (heart attack, stroke, seizure)
- FIRE (burns, smoke inhalation)
- VIOLENCE (gunshot, stab wounds)
- DISASTER (building collapse, explosion)

**Features:**
- 100+ unique templates per severity level
- Timestamps across 1 year of data
- Time of day, day of week, season tracking
- Body part mentions and emergency keyword detection
- Resource requirement prediction (blood, ambulance, hospital)
- 10% Hinglish variations for realism

**Run:**
```bash
python incident_generator.py
```

**Expected Runtime:** 5-8 minutes

---

### 5. `run_all_data_collection.py`
**Purpose:** Master script to run all data collection scripts in sequence

**Run:**
```bash
python run_all_data_collection.py
```

**Expected Runtime:** 20-30 minutes total

**Features:**
- Runs all 4 scripts sequentially
- Progress tracking and logging
- Error handling and reporting
- Summary report at completion

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+**
```bash
python3 --version
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

**Required packages:**
- requests
- tqdm
- urllib3

Create `requirements.txt`:
```txt
requests>=2.31.0
tqdm>=4.66.0
urllib3>=2.0.0
```

### Running All Scripts

**Option 1: Run Master Script (Recommended)**
```bash
cd scripts
python run_all_data_collection.py
```

**Option 2: Run Individual Scripts**
```bash
cd scripts
python hospital_scraper.py
python ambulance_scraper.py
python blood_bank_scraper.py
python incident_generator.py
```

---

## 📊 Output Structure

After running all scripts, your directory structure will be:

```
ARIA/
├── data/
│   └── raw/
│       ├── hospitals_raw.csv           (15,000+ records)
│       ├── hospital_summary.txt
│       ├── ambulances_raw.csv          (25,000+ records)
│       ├── ambulances_summary.txt
│       ├── blood_banks_raw.csv         (2,500+ records)
│       ├── blood_banks_summary.txt
│       ├── incidents_raw.csv           (100,000+ records)
│       └── incidents_summary.txt
├── logs/
│   ├── hospital_scrape.log
│   ├── ambulance_scrape.log
│   ├── blood_bank_scrape.log
│   ├── incident_generation.log
│   └── master_data_collection.log
└── scripts/
    └── (all scripts)
```

---

## 🔍 Data Schema

### Hospitals Schema
```
hospital_id, name, type, address, city, state, pincode, latitude, longitude,
phone, email, website, beds, specialties, operating_hours, emergency_services,
ambulance_available, icu_beds, ventilators, oxygen_supply, blood_bank,
accreditation, source, timestamp
```

### Ambulances Schema
```
ambulance_id, vehicle_number, vehicle_type, operator_name, operator_type,
current_latitude, current_longitude, status, response_zone, district, state,
average_speed, driver_name, driver_phone, driver_license, paramedic1_name,
paramedic1_certification, paramedic2_name, paramedic2_certification,
equipment (JSON), drugs (JSON), fuel_level, last_service_date, next_service_due,
total_trips_today, total_trips_month, gps_enabled, communication_system,
insurance_valid_till, pollution_certificate, timestamp
```

### Blood Banks Schema
```
bank_id, name, type, address, city, state, latitude, longitude, phone, email,
website, inventory_json, total_units_available, testing_available (JSON),
components_available (JSON), operating_hours, emergency_availability,
accreditations, license_number, established_year, storage_capacity,
refrigerators, blood_bank_technicians, annual_collections, voluntary_donors,
replacement_donors, paid_donors, donor_registration, mobile_blood_donation_van,
timestamp
```

### Incidents Schema
```
incident_id, incident_description, severity, incident_type, city, location,
latitude, longitude, timestamp, victim_count, time_of_day, day_of_week, month,
season, body_part_mentioned, emergency_keyword, blood_required,
ambulance_required, hospital_required
```

---

## 📈 Data Quality Checks

Each script includes built-in data quality checks:

1. **GPS Coordinate Validation**
   - Latitude: 8-37 (India bounds)
   - Longitude: 68-97 (India bounds)

2. **Phone Number Validation**
   - 10-digit Indian mobile numbers
   - Valid area codes for landlines

3. **Duplicate Detection**
   - Based on name, city, and coordinates
   - Automatic removal with logging

4. **Data Completeness**
   - All required fields populated
   - Missing data handled gracefully
   - Statistics in summary reports

5. **Realistic Distributions**
   - State-wise proportional allocation
   - City-wise population-based distribution
   - Time-series data spread across year

---

## 🔧 Configuration

Each script has configuration at the top:

```python
# Rate limiting
RATE_LIMIT_DELAY = 1.0  # seconds between requests

# Retries
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # exponential backoff factor

# User Agent
USER_AGENT = "ARIA-Data-Collector/1.0"
```

**Adjust as needed for your environment.**

---

## 🐛 Troubleshooting

### Issue: Script hangs or times out
**Solution:** Check your internet connection. OSM queries can be slow.

### Issue: "Module not found" errors
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Permission denied on logs/data directories
**Solution:**
```bash
chmod 755 logs data
```

### Issue: Low data count (< expected)
**Solution:** Check logs for errors. May need to increase target counts in script configuration.

### Issue: GPS coordinates outside India
**Solution:** Scripts validate this automatically. Check logs for validation failures.

---

## 📝 Logging

All scripts log to:
- Console (INFO level)
- Log files (INFO level with details)

**Log Locations:**
- `logs/hospital_scrape.log`
- `logs/ambulance_scrape.log`
- `logs/blood_bank_scrape.log`
- `logs/incident_generation.log`
- `logs/master_data_collection.log`

**Log Format:**
```
2026-08-22 14:30:45 - INFO - Starting data collection...
2026-08-22 14:30:46 - INFO - Generated 1000 records
2026-08-22 14:30:47 - ERROR - API request failed: Connection timeout
```

---

## 🔒 Security & Privacy

### Data Privacy
- All data is **synthetic** or **publicly available**
- No real patient information
- No personally identifiable information (PII)
- Safe for development and testing

### API Keys
Some sources require API keys (not included):
- Google Places API: Set `GOOGLE_PLACES_API_KEY` environment variable
- Other APIs: Check respective documentation

**For production use with real APIs:**
```bash
export GOOGLE_PLACES_API_KEY="your_key_here"
```

---

## 📊 Next Steps

After data collection:

1. **Review Summary Reports**
   ```bash
   cat data/raw/*_summary.txt
   ```

2. **Data Validation**
   - Check record counts
   - Verify data distributions
   - Inspect sample records

3. **Data Preprocessing** (Sprint 1B)
   - Clean and normalize data
   - Feature engineering
   - Train-test split
   - Database population

4. **ML Model Training** (Sprint 2)
   - Train triage classifier on incidents
   - Train hospital ranker
   - Train resource predictor
   - Train ETA predictor
   - Train hotspot predictor

---

## 👥 Contributing

To add new data sources:

1. Create new script: `scripts/new_source_scraper.py`
2. Follow existing script structure
3. Add to `run_all_data_collection.py`
4. Update this README

---

## 📞 Support

**Issues:** Check logs first, then:
- Review script comments
- Check data/raw/ output files
- Verify internet connectivity
- Ensure all dependencies installed

**Questions:** Refer to Phase 0 documentation in `docs/phase0/`

---

## 📄 License

ARIA Project - Internal Use

---

**Version:** 1.0  
**Last Updated:** August 22, 2026  
**Status:** Production Ready

---

**Next:** Proceed to Sprint 1B - Data Preprocessing
