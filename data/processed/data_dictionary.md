# ARIA Data Dictionary
## Processed Datasets Documentation

**Generated:** August 23, 2026  
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
