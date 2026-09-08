# ARIA Database Schema Documentation

## Overview

ARIA uses PostgreSQL 14+ with PostGIS extension for spatial data management. The database schema is designed to support real-time emergency response coordination with geospatial queries, audit trails, and relationship tracking.

**Database:** PostgreSQL 14.7  
**Extensions:** PostGIS 3.3+  
**ORM:** SQLAlchemy 2.0.25 (Async)  
**Spatial Reference System:** WGS84 (SRID 4326)

---

## Table of Contents

1. [Entity Relationship Diagram](#entity-relationship-diagram)
2. [Table Descriptions](#table-descriptions)
3. [Indexes & Performance](#indexes--performance)
4. [PostGIS Setup](#postgis-setup)
5. [Sample Queries](#sample-queries)
6. [Migrations](#migrations)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARIA DATABASE SCHEMA                             │
└─────────────────────────────────────────────────────────────────────┘

                        ┌──────────────┐
                        │    users     │
                        ├──────────────┤
                        │ id (PK)      │
                        │ email        │
                        │ username     │
                        │ password     │
                        │ role         │
                        │ is_active    │
                        └──────┬───────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
         ┌─────────────────┐    ┌──────────────────┐
         │   incidents     │    │ incident_history │
         ├─────────────────┤    ├──────────────────┤
         │ id (PK)         │◄───│ incident_id (FK) │
         │ incident_code   │    │ status           │
         │ location (GEO)  │    │ changed_by (FK)  │
         │ lat, lon        │    │ changed_at       │
         │ description     │    │ changes (JSON)   │
         │ incident_type   │    │ notes            │
         │ severity        │    └──────────────────┘
         │ status          │
         │ created_by (FK) │
         │ assigned_       │
         │   hospital_id   ├───┐
         │ assigned_       │   │
         │   ambulance_id  ├─┐ │
         └─────────────────┘ │ │
                             │ │
           ┌─────────────────┘ │
           │                   │
           ▼                   ▼
   ┌──────────────┐    ┌──────────────┐
   │  ambulances  │    │  hospitals   │
   ├──────────────┤    ├──────────────┤
   │ id (PK)      │    │ id (PK)      │
   │ vehicle_num  │    │ name         │
   │ ambulance_   │    │ hospital_    │
   │   type       │    │   code       │
   │ current_     │    │ location     │
   │   location   │    │   (GEO)      │
   │   (GEO)      │    │ lat, lon     │
   │ lat, lon     │    │ address      │
   │ status       │    │ city         │
   │ equipment    │    │ total_beds   │
   │   (JSON)     │    │ available_   │
   │ driver_name  │    │   beds       │
   │ current_     │    │ specialties  │
   │   incident_  │    │   (ARRAY)    │
   │   id (FK)    │    │ blood_       │
   └──────────────┘    │   inventory  │
                       │   (JSON)     │
                       │ rating       │
                       │ is_active    │
                       └──────────────┘

Legend:
─────
PK = Primary Key
FK = Foreign Key
GEO = PostGIS Geometry (POINT)
JSON = JSONB column
ARRAY = PostgreSQL Array
```

---

## Table Descriptions

### 1. users

**Purpose:** Authentication and authorization for system users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User email address |
| `username` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Unique username |
| `full_name` | VARCHAR(255) | NOT NULL | Full name |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| `role` | ENUM | NOT NULL | admin, dispatcher, medical_staff, driver, viewer |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account active status |
| `is_verified` | BOOLEAN | NOT NULL, DEFAULT FALSE | Email verification status |
| `phone` | VARCHAR(20) | NULLABLE | Contact phone |
| `organization` | VARCHAR(255) | NULLABLE | Organization name |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation time |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update time |
| `last_login` | TIMESTAMP | NULLABLE | Last login timestamp |

**Indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
```

---

### 2. incidents

**Purpose:** Core table for emergency incidents with location data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `incident_code` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Human-readable code (e.g., INC-20260906-0001) |
| `location` | GEOMETRY(POINT) | NOT NULL | PostGIS point (lat, lon) |
| `latitude` | FLOAT | NOT NULL | Latitude for indexing |
| `longitude` | FLOAT | NOT NULL | Longitude for indexing |
| `address` | VARCHAR(500) | NULLABLE | Full address |
| `city` | VARCHAR(100) | INDEX | City name |
| `description` | TEXT | NOT NULL | Incident description |
| `incident_type` | ENUM | NOT NULL, INDEX | MEDICAL, ACCIDENT, FIRE, VIOLENCE, NATURAL_DISASTER, OTHER |
| `severity` | ENUM | NOT NULL, INDEX | LOW, MODERATE, HIGH, CRITICAL |
| `victim_count` | INTEGER | DEFAULT 1 | Number of victims |
| `status` | ENUM | NOT NULL, INDEX | Workflow status (13 states) |
| `priority_score` | FLOAT | NULLABLE | Calculated priority (0-100) |
| `reporter_name` | VARCHAR(255) | NULLABLE | Reporter's name |
| `reporter_phone` | VARCHAR(20) | NULLABLE | Reporter's phone |
| `reporter_relationship` | VARCHAR(100) | NULLABLE | Relationship to victim |
| `blood_required` | BOOLEAN | DEFAULT FALSE | Blood transfusion needed |
| `blood_type` | VARCHAR(10) | NULLABLE | Required blood type |
| `ambulance_required` | BOOLEAN | DEFAULT TRUE | Ambulance needed |
| `hospital_required` | BOOLEAN | DEFAULT TRUE | Hospital needed |
| `predicted_severity` | ENUM | NULLABLE | ML prediction |
| `ml_confidence` | FLOAT | NULLABLE | Prediction confidence (0-1) |
| `response_plan` | JSONB | NULLABLE | Full AI-generated plan |
| `assigned_hospital_id` | UUID | FK → hospitals | Selected hospital |
| `assigned_ambulance_id` | UUID | FK → ambulances | Selected ambulance |
| `estimated_response_time` | INTEGER | NULLABLE | Minutes |
| `requires_approval` | BOOLEAN | DEFAULT TRUE | Human-in-loop flag |
| `approved_by` | UUID | FK → users | Approver user ID |
| `approved_at` | TIMESTAMP | NULLABLE | Approval timestamp |
| `approval_notes` | TEXT | NULLABLE | Approval comments |
| `reported_at` | TIMESTAMP | NOT NULL, INDEX | Initial report time |
| `triaged_at` | TIMESTAMP | NULLABLE | Triage completion time |
| `dispatched_at` | TIMESTAMP | NULLABLE | Dispatch time |
| `completed_at` | TIMESTAMP | NULLABLE | Completion time |
| `created_by` | UUID | FK → users | Creator user ID |
| `created_at` | TIMESTAMP | NOT NULL | Record creation |
| `updated_at` | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
```sql
CREATE INDEX idx_incidents_location ON incidents USING GIST(location);
CREATE INDEX idx_incidents_incident_code ON incidents(incident_code);
CREATE INDEX idx_incidents_status ON incidents(status);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_incident_type ON incidents(incident_type);
CREATE INDEX idx_incidents_reported_at ON incidents(reported_at DESC);
CREATE INDEX idx_incidents_city ON incidents(city);
```

**Status Flow:**
```
REPORTED → TRIAGED → PLAN_GENERATED → AWAITING_APPROVAL → APPROVED → 
DISPATCHED → EN_ROUTE → ON_SCENE → TRANSPORTING → COMPLETED
                                                         ↓
                                                    CANCELLED
```

---

### 3. incident_history

**Purpose:** Audit trail for all incident changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `incident_id` | UUID | FK → incidents, NOT NULL, INDEX | Related incident |
| `status` | ENUM | NOT NULL | New status |
| `changed_by` | UUID | FK → users | User who made change |
| `changed_at` | TIMESTAMP | NOT NULL, INDEX | Change timestamp |
| `change_type` | VARCHAR(50) | NULLABLE | Type: status_change, assignment, approval |
| `changes` | JSONB | NULLABLE | Detailed diff of changes |
| `notes` | TEXT | NULLABLE | Change notes/reason |

**Indexes:**
```sql
CREATE INDEX idx_incident_history_incident_id ON incident_history(incident_id);
CREATE INDEX idx_incident_history_changed_at ON incident_history(changed_at DESC);
```

**Example JSONB `changes` field:**
```json
{
  "field": "status",
  "old_value": "TRIAGED",
  "new_value": "APPROVED",
  "metadata": {
    "approver": "John Doe",
    "auto_generated": false
  }
}
```

---

### 4. hospitals

**Purpose:** Hospital information with spatial location and capacity tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `name` | VARCHAR(500) | NOT NULL, INDEX | Hospital name |
| `hospital_code` | VARCHAR(50) | UNIQUE, INDEX | Unique code |
| `location` | GEOMETRY(POINT) | NOT NULL | PostGIS point |
| `latitude` | FLOAT | NOT NULL | Latitude |
| `longitude` | FLOAT | NOT NULL | Longitude |
| `address` | TEXT | NULLABLE | Full address |
| `city` | VARCHAR(100) | INDEX | City |
| `state` | VARCHAR(100) | NULLABLE | State/Province |
| `pincode` | VARCHAR(10) | NULLABLE | Postal code |
| `phone` | VARCHAR(20) | NULLABLE | Main phone |
| `emergency_phone` | VARCHAR(20) | NULLABLE | Emergency line |
| `email` | VARCHAR(255) | NULLABLE | Contact email |
| `website` | VARCHAR(500) | NULLABLE | Website URL |
| `total_beds` | INTEGER | DEFAULT 0 | Total bed capacity |
| `available_beds` | INTEGER | DEFAULT 0 | Currently available |
| `icu_beds` | INTEGER | DEFAULT 0 | ICU capacity |
| `available_icu_beds` | INTEGER | DEFAULT 0 | Available ICU |
| `ventilators` | INTEGER | DEFAULT 0 | Ventilator count |
| `available_ventilators` | INTEGER | DEFAULT 0 | Available ventilators |
| `specialties` | ARRAY(VARCHAR) | NULLABLE | ["cardiology", "neurology"] |
| `trauma_center` | BOOLEAN | DEFAULT FALSE | Trauma designation |
| `burn_unit` | BOOLEAN | DEFAULT FALSE | Has burn unit |
| `maternity_unit` | BOOLEAN | DEFAULT FALSE | Has maternity |
| `pediatric_unit` | BOOLEAN | DEFAULT FALSE | Has pediatric |
| `rating` | FLOAT | NULLABLE | Average rating (0-5) |
| `total_reviews` | INTEGER | DEFAULT 0 | Review count |
| `success_rate` | FLOAT | NULLABLE | Treatment success % |
| `average_wait_time` | INTEGER | NULLABLE | Wait time (minutes) |
| `has_blood_bank` | BOOLEAN | DEFAULT FALSE | Blood bank present |
| `blood_inventory` | JSONB | NULLABLE | Current blood stock |
| `is_active` | BOOLEAN | DEFAULT TRUE | Operational status |
| `accepts_emergency` | BOOLEAN | DEFAULT TRUE | Accepts emergencies |
| `is_government` | BOOLEAN | DEFAULT FALSE | Government hospital |
| `facilities` | JSONB | NULLABLE | Additional facilities |
| `operating_hours` | JSONB | NULLABLE | Hours by day |
| `insurance_accepted` | ARRAY(VARCHAR) | NULLABLE | Insurance providers |
| `created_at` | TIMESTAMP | NOT NULL | Creation time |
| `updated_at` | TIMESTAMP | NOT NULL | Last update |
| `last_capacity_update` | TIMESTAMP | NULLABLE | Last capacity check |

**Indexes:**
```sql
CREATE INDEX idx_hospitals_location ON hospitals USING GIST(location);
CREATE INDEX idx_hospitals_name ON hospitals(name);
CREATE INDEX idx_hospitals_city ON hospitals(city);
CREATE INDEX idx_hospitals_hospital_code ON hospitals(hospital_code);
CREATE INDEX idx_hospitals_is_active ON hospitals(is_active) WHERE is_active = TRUE;
```

**Example JSONB fields:**

`blood_inventory`:
```json
{
  "A+": 10,
  "A-": 5,
  "B+": 8,
  "B-": 3,
  "AB+": 2,
  "AB-": 1,
  "O+": 15,
  "O-": 7,
  "last_updated": "2026-09-06T10:30:00Z"
}
```

`operating_hours`:
```json
{
  "Monday": {"open": "00:00", "close": "23:59"},
  "Tuesday": {"open": "00:00", "close": "23:59"},
  "emergency_24x7": true
}
```

---

### 5. ambulances

**Purpose:** Ambulance fleet management with real-time GPS tracking.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PRIMARY KEY | Unique identifier |
| `vehicle_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | License plate |
| `ambulance_code` | VARCHAR(50) | UNIQUE, INDEX | Internal code |
| `ambulance_type` | ENUM | NOT NULL, INDEX | BASIC, ALS, CRITICAL_CARE, AIR_AMBULANCE |
| `equipment` | JSONB | NULLABLE | Medical equipment list |
| `has_ventilator` | BOOLEAN | DEFAULT FALSE | Ventilator available |
| `has_defibrillator` | BOOLEAN | DEFAULT FALSE | Defibrillator available |
| `has_oxygen` | BOOLEAN | DEFAULT TRUE | Oxygen available |
| `current_location` | GEOMETRY(POINT) | NULLABLE | Real-time GPS location |
| `latitude` | FLOAT | NULLABLE | Current latitude |
| `longitude` | FLOAT | NULLABLE | Current longitude |
| `last_location_update` | TIMESTAMP | NULLABLE | Last GPS update |
| `base_station` | VARCHAR(255) | NULLABLE | Home station name |
| `base_location` | GEOMETRY(POINT) | NULLABLE | Station location |
| `base_city` | VARCHAR(100) | INDEX | Base city |
| `status` | ENUM | NOT NULL, INDEX | AVAILABLE, DISPATCHED, EN_ROUTE, ON_SCENE, TRANSPORTING, AT_HOSPITAL, OFFLINE, MAINTENANCE |
| `is_active` | BOOLEAN | DEFAULT TRUE | Active/decommissioned |
| `current_incident_id` | UUID | FK → incidents | Current assignment |
| `driver_name` | VARCHAR(255) | NULLABLE | Driver name |
| `driver_phone` | VARCHAR(20) | NULLABLE | Driver contact |
| `paramedic_name` | VARCHAR(255) | NULLABLE | Paramedic name |
| `paramedic_phone` | VARCHAR(20) | NULLABLE | Paramedic contact |
| `crew_size` | INTEGER | DEFAULT 2 | Number of crew |
| `organization` | VARCHAR(255) | NULLABLE | Operator organization |
| `is_government` | BOOLEAN | DEFAULT FALSE | Government operated |
| `contact_number` | VARCHAR(20) | NULLABLE | Primary contact |
| `emergency_contact` | VARCHAR(20) | NULLABLE | Emergency contact |
| `total_trips` | INTEGER | DEFAULT 0 | Lifetime trip count |
| `average_response_time` | FLOAT | NULLABLE | Avg response (minutes) |
| `last_maintenance` | TIMESTAMP | NULLABLE | Last service date |
| `next_maintenance` | TIMESTAMP | NULLABLE | Next service due |
| `created_at` | TIMESTAMP | NOT NULL | Creation time |
| `updated_at` | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
```sql
CREATE INDEX idx_ambulances_location ON ambulances USING GIST(current_location);
CREATE INDEX idx_ambulances_vehicle_number ON ambulances(vehicle_number);
CREATE INDEX idx_ambulances_status ON ambulances(status);
CREATE INDEX idx_ambulances_ambulance_type ON ambulances(ambulance_type);
CREATE INDEX idx_ambulances_base_city ON ambulances(base_city);
CREATE INDEX idx_ambulances_available ON ambulances(status, is_active) 
  WHERE status = 'AVAILABLE' AND is_active = TRUE;
```

**Example JSONB `equipment`:**
```json
{
  "basic": ["stretcher", "first_aid_kit", "oxygen_cylinder"],
  "advanced": ["defibrillator", "ventilator", "cardiac_monitor"],
  "medications": ["epinephrine", "aspirin", "nitroglycerin"],
  "last_inventory": "2026-09-01"
}
```

---

## Indexes & Performance

### Spatial Indexes (PostGIS)

PostGIS automatically creates GIST indexes on geometry columns for fast spatial queries.

```sql
-- Verify spatial indexes
SELECT tablename, indexname, indexdef 
FROM pg_indexes 
WHERE indexdef LIKE '%GIST%';
```

### Query Performance Tips

**1. Spatial Queries:**
```sql
-- Find hospitals within 10km (10000 meters)
SELECT id, name, 
       ST_Distance(location, ST_SetSRID(ST_MakePoint(72.8777, 19.0760), 4326)) as distance
FROM hospitals
WHERE ST_DWithin(
    location, 
    ST_SetSRID(ST_MakePoint(72.8777, 19.0760), 4326),
    10000  -- meters
)
ORDER BY distance
LIMIT 10;
```

**2. Status Filtering:**
```sql
-- Use partial indexes for common queries
CREATE INDEX idx_incidents_active 
ON incidents(status, reported_at DESC) 
WHERE status NOT IN ('COMPLETED', 'CANCELLED');
```

**3. JSONB Queries:**
```sql
-- Index on JSONB field
CREATE INDEX idx_hospitals_blood_inventory_gin 
ON hospitals USING GIN(blood_inventory);

-- Query blood availability
SELECT id, name, blood_inventory->>'A+' as a_positive
FROM hospitals
WHERE blood_inventory->>'A+' IS NOT NULL
  AND (blood_inventory->>'A+')::int > 5;
```

---

## PostGIS Setup

### Initial Setup

```sql
-- Create extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify installation
SELECT PostGIS_Version();
SELECT PostGIS_Full_Version();

-- Check SRID
SELECT * FROM spatial_ref_sys WHERE srid = 4326;
```

### Creating Geometry Columns

```sql
-- Add geometry column to table
ALTER TABLE incidents
ADD COLUMN location GEOMETRY(POINT, 4326);

-- Create spatial index
CREATE INDEX idx_incidents_location 
ON incidents USING GIST(location);

-- Update geometry from lat/lon
UPDATE incidents
SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
WHERE location IS NULL;
```

### Common PostGIS Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `ST_MakePoint(lon, lat)` | Create point | `ST_MakePoint(72.8777, 19.0760)` |
| `ST_SetSRID(geom, srid)` | Set coordinate system | `ST_SetSRID(..., 4326)` |
| `ST_Distance(geom1, geom2)` | Distance in meters | Returns float |
| `ST_DWithin(geom1, geom2, dist)` | Within distance | Returns boolean |
| `ST_AsGeoJSON(geom)` | Convert to GeoJSON | For API responses |
| `ST_X(geom)` | Get longitude | Returns float |
| `ST_Y(geom)` | Get latitude | Returns float |

---

## Sample Queries

### 1. Find Nearest Hospital

```sql
SELECT 
    h.id,
    h.name,
    h.available_beds,
    ST_Distance(
        h.location, 
        ST_SetSRID(ST_MakePoint($longitude, $latitude), 4326)
    ) as distance_meters,
    ST_AsGeoJSON(h.location) as location_json
FROM hospitals h
WHERE h.is_active = TRUE
  AND h.accepts_emergency = TRUE
  AND h.available_beds > 0
  AND ST_DWithin(
      h.location,
      ST_SetSRID(ST_MakePoint($longitude, $latitude), 4326),
      50000  -- 50km radius
  )
ORDER BY distance_meters
LIMIT 5;
```

### 2. Get Available Ambulances

```sql
SELECT 
    a.id,
    a.vehicle_number,
    a.ambulance_type,
    a.driver_name,
    a.driver_phone,
    ST_Distance(
        a.current_location,
        ST_SetSRID(ST_MakePoint($longitude, $latitude), 4326)
    ) as distance_meters
FROM ambulances a
WHERE a.status = 'AVAILABLE'
  AND a.is_active = TRUE
  AND a.current_location IS NOT NULL
  AND ST_DWithin(
      a.current_location,
      ST_SetSRID(ST_MakePoint($longitude, $latitude), 4326),
      30000  -- 30km radius
  )
ORDER BY distance_meters
LIMIT 3;
```

### 3. Incident Statistics by City

```sql
SELECT 
    city,
    COUNT(*) as total_incidents,
    COUNT(*) FILTER (WHERE severity = 'CRITICAL') as critical_count,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - reported_at)) / 60) as avg_response_time_minutes
FROM incidents
WHERE reported_at >= NOW() - INTERVAL '30 days'
GROUP BY city
ORDER BY total_incidents DESC;
```

### 4. Hospital Capacity Dashboard

```sql
SELECT 
    h.id,
    h.name,
    h.city,
    h.total_beds,
    h.available_beds,
    ROUND((h.available_beds::FLOAT / h.total_beds * 100), 2) as availability_percentage,
    COUNT(i.id) as active_incidents
FROM hospitals h
LEFT JOIN incidents i ON i.assigned_hospital_id = h.id 
    AND i.status NOT IN ('COMPLETED', 'CANCELLED')
WHERE h.is_active = TRUE
GROUP BY h.id, h.name, h.city, h.total_beds, h.available_beds
ORDER BY availability_percentage DESC;
```

### 5. Ambulance Status Overview

```sql
SELECT 
    status,
    ambulance_type,
    COUNT(*) as count
FROM ambulances
WHERE is_active = TRUE
GROUP BY status, ambulance_type
ORDER BY status, ambulance_type;
```

### 6. Incident Audit Trail

```sql
SELECT 
    ih.changed_at,
    ih.status,
    u.username as changed_by,
    ih.change_type,
    ih.notes
FROM incident_history ih
JOIN users u ON ih.changed_by = u.id
WHERE ih.incident_id = $incident_id
ORDER BY ih.changed_at DESC;
```

---

## Migrations

### Using Alembic

**Initialize:**
```bash
alembic init alembic
```

**Generate Migration:**
```bash
alembic revision --autogenerate -m "Create initial schema"
```

**Apply Migration:**
```bash
alembic upgrade head
```

**Rollback:**
```bash
alembic downgrade -1
```

### Sample Migration Script

```python
"""Add blood_inventory to hospitals

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2026-09-06 10:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('hospitals', 
        sa.Column('blood_inventory', postgresql.JSONB, nullable=True))
    
    # Create GIN index for JSONB queries
    op.create_index(
        'idx_hospitals_blood_inventory_gin',
        'hospitals',
        ['blood_inventory'],
        postgresql_using='gin'
    )

def downgrade():
    op.drop_index('idx_hospitals_blood_inventory_gin', 'hospitals')
    op.drop_column('hospitals', 'blood_inventory')
```

---

## Database Maintenance

### Vacuum & Analyze

```sql
-- Regular maintenance
VACUUM ANALYZE incidents;
VACUUM ANALYZE hospitals;
VACUUM ANALYZE ambulances;

-- Check table size
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Backup & Restore

```bash
# Backup
pg_dump -U aria_user -h localhost aria_db > backup_$(date +%Y%m%d).sql

# Restore
psql -U aria_user -h localhost aria_db < backup_20260906.sql

# Backup with compression
pg_dump -U aria_user -h localhost aria_db | gzip > backup_$(date +%Y%m%d).sql.gz
```

---

## Performance Monitoring

```sql
-- Slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Cache hit ratio (should be > 99%)
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) as cache_hit_ratio
FROM pg_statio_user_tables;
```

---

## Security Best Practices

1. **Use prepared statements** (SQLAlchemy does this automatically)
2. **Principle of least privilege** for database users
3. **Enable SSL connections** in production
4. **Regular backups** with encryption
5. **Audit logging** for sensitive tables
6. **Row-level security** for multi-tenant scenarios

---

## Conclusion

The ARIA database schema is designed for:
- **High performance** spatial queries with PostGIS
- **Audit trails** for compliance
- **Scalability** with proper indexing
- **Flexibility** with JSONB for dynamic data
- **Real-time tracking** with frequent location updates

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team
