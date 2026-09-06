"""
Hospital Pre-Arrival Checklist Templates
Defines standard operating procedure (SOP) pre-arrival checklists for 7 emergency categories:
Trauma, Cardiac, Stroke, Burn, Obstetric, Pediatric, and Mass Casualty.
"""

from typing import Dict, List, Any

CHECKLIST_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "TRAUMA": {
        "template_id": "TPL-TRAUMA-01",
        "name": "Severe Trauma Pre-Arrival Checklist",
        "emergency_category": "TRAUMA",
        "target_prep_time_minutes": 10,
        "items": [
            {
                "item_id": "TRM-01",
                "category": "ROOM_OR",
                "description": "Trauma Resuscitation Bay 1 overhead warmer & suction tested",
                "is_critical": True
            },
            {
                "item_id": "TRM-02",
                "category": "EQUIPMENT",
                "description": "Rapid blood warmer & Level 1 fast infusion pump primed",
                "is_critical": True
            },
            {
                "item_id": "TRM-03",
                "category": "EQUIPMENT",
                "description": "FAST Ultrasound machine positioned & transducer gel ready",
                "is_critical": False
            },
            {
                "item_id": "TRM-04",
                "category": "EQUIPMENT",
                "description": "Difficult Airway Cart & Video Laryngoscope checked",
                "is_critical": True
            },
            {
                "item_id": "TRM-05",
                "category": "STAFF",
                "description": "Trauma Team Leader & Anesthesiologist present in bay",
                "is_critical": True
            },
            {
                "item_id": "TRM-06",
                "category": "STAFF",
                "description": "2 Trauma Resuscitation Nurses & Scrub Tech assigned",
                "is_critical": False
            },
            {
                "item_id": "TRM-07",
                "category": "ROOM_OR",
                "description": "Operating Room #3 cleared & held for emergency laparotomy",
                "is_critical": True
            },
            {
                "item_id": "TRM-08",
                "category": "BLOOD_PRODUCTS",
                "description": "4 Units O-Negative uncrossmatched PRBC retrieved from cooler",
                "is_critical": True
            }
        ]
    },
    "CARDIAC": {
        "template_id": "TPL-CARDIAC-01",
        "name": "STEMI / Acute Cardiac Pre-Arrival Checklist",
        "emergency_category": "CARDIAC",
        "target_prep_time_minutes": 8,
        "items": [
            {
                "item_id": "CRD-01",
                "category": "EQUIPMENT",
                "description": "12-Lead ECG monitor telemetry synced & defibrillator pads attached to cable",
                "is_critical": True
            },
            {
                "item_id": "CRD-02",
                "category": "EQUIPMENT",
                "description": "Transcutaneous pacing unit tested & set to standby",
                "is_critical": True
            },
            {
                "item_id": "CRD-03",
                "category": "STAFF",
                "description": "On-call Interventional Cardiologist alerted & Cath Lab team activated",
                "is_critical": True
            },
            {
                "item_id": "CRD-04",
                "category": "ROOM_OR",
                "description": "Cardiac Cath Lab #2 prepped & fluoroscopy calibrated",
                "is_critical": True
            },
            {
                "item_id": "CRD-05",
                "category": "EQUIPMENT",
                "description": "Heparin bolus & Nitroglycerin / Dobutamine emergency IV drips prepared",
                "is_critical": False
            },
            {
                "item_id": "CRD-06",
                "category": "BLOOD_PRODUCTS",
                "description": "STAT Cardiac Enzymes & Type-and-Screen blood tubes requisitioned",
                "is_critical": False
            }
        ]
    },
    "STROKE": {
        "template_id": "TPL-STROKE-01",
        "name": "Acute Ischemic Stroke Code Checklist",
        "emergency_category": "STROKE",
        "target_prep_time_minutes": 5,
        "items": [
            {
                "item_id": "STR-01",
                "category": "ROOM_OR",
                "description": "Non-Contrast Head CT Scanner cleared & held for direct patient transfer",
                "is_critical": True
            },
            {
                "item_id": "STR-02",
                "category": "EQUIPMENT",
                "description": "tPA / Tenecteplase thrombolysis reconstitution kit ready at bedside",
                "is_critical": True
            },
            {
                "item_id": "STR-03",
                "category": "STAFF",
                "description": "Stroke Neurologist & Endovascular Neuro-Interventionist alerted",
                "is_critical": True
            },
            {
                "item_id": "STR-04",
                "category": "EQUIPMENT",
                "description": "NIHSS Neurological Assessment Score Sheet on tablet",
                "is_critical": False
            },
            {
                "item_id": "STR-05",
                "category": "BLOOD_PRODUCTS",
                "description": "STAT Point-of-Care Blood Glucose & Coagulation INR tested",
                "is_critical": True
            }
        ]
    },
    "BURN": {
        "template_id": "TPL-BURN-01",
        "name": "Severe Thermal / Chemical Burn Checklist",
        "emergency_category": "BURN",
        "target_prep_time_minutes": 10,
        "items": [
            {
                "item_id": "BRN-01",
                "category": "EQUIPMENT",
                "description": "Sterile burn sheets & water-gel dressings unpacked",
                "is_critical": True
            },
            {
                "item_id": "BRN-02",
                "category": "EQUIPMENT",
                "description": "Parkland Formula fluid resuscitation pumps (Warmed Lactated Ringer's) primed",
                "is_critical": True
            },
            {
                "item_id": "BRN-03",
                "category": "EQUIPMENT",
                "description": "Endotracheal intubation tray ready for inhalation injury airway management",
                "is_critical": True
            },
            {
                "item_id": "BRN-04",
                "category": "ROOM_OR",
                "description": "Burn ICU Hydrotherapy Bay prepped with ambient heating set to 32°C",
                "is_critical": False
            },
            {
                "item_id": "BRN-05",
                "category": "STAFF",
                "description": "Burn Specialist & ICU Respiratory Therapist present",
                "is_critical": True
            }
        ]
    },
    "OBSTETRIC": {
        "template_id": "TPL-OBSTETRIC-01",
        "name": "High-Risk Obstetric Emergency Checklist",
        "emergency_category": "OBSTETRIC",
        "target_prep_time_minutes": 10,
        "items": [
            {
                "item_id": "OBS-01",
                "category": "ROOM_OR",
                "description": "Labor & Delivery Suite #4 prepped with emergency delivery pack",
                "is_critical": True
            },
            {
                "item_id": "OBS-02",
                "category": "EQUIPMENT",
                "description": "Continuous Fetal Heart Rate monitor & Toco transducer calibrated",
                "is_critical": True
            },
            {
                "item_id": "OBS-03",
                "category": "EQUIPMENT",
                "description": "Neonatal Resuscitation Cart & radiant warmer pre-heated",
                "is_critical": True
            },
            {
                "item_id": "OBS-04",
                "category": "STAFF",
                "description": "Attending Obstetrician & Neonatologist present",
                "is_critical": True
            },
            {
                "item_id": "OBS-05",
                "category": "BLOOD_PRODUCTS",
                "description": "Postpartum Hemorrhage Kit & 2 Units O-Negative PRBC ready",
                "is_critical": True
            }
        ]
    },
    "PEDIATRIC": {
        "template_id": "TPL-PEDIATRIC-01",
        "name": "Pediatric Critical Resuscitation Checklist",
        "emergency_category": "PEDIATRIC",
        "target_prep_time_minutes": 8,
        "items": [
            {
                "item_id": "PED-01",
                "category": "EQUIPMENT",
                "description": "Broselow Pediatric Emergency Tape & length-based color resuscitation cart",
                "is_critical": True
            },
            {
                "item_id": "PED-02",
                "category": "EQUIPMENT",
                "description": "Pediatric ETT tubes (sizes 3.0 - 5.5) & micro-cuff laryngoscope",
                "is_critical": True
            },
            {
                "item_id": "PED-03",
                "category": "STAFF",
                "description": "Pediatric Intensivist & PICU Specialist Nurse present",
                "is_critical": True
            },
            {
                "item_id": "PED-04",
                "category": "ROOM_OR",
                "description": "Pediatric Resuscitation Bay warmer & micro-infusion pumps ready",
                "is_critical": True
            },
            {
                "item_id": "PED-05",
                "category": "BLOOD_PRODUCTS",
                "description": "Weight-based 10 mL/kg emergency blood transfusion protocol printed",
                "is_critical": False
            }
        ]
    },
    "MASS_CASUALTY": {
        "template_id": "TPL-MCI-01",
        "name": "Mass Casualty Incident (MCI) Surge Preparation Checklist",
        "emergency_category": "MASS_CASUALTY",
        "target_prep_time_minutes": 15,
        "items": [
            {
                "item_id": "MCI-01",
                "category": "ROOM_OR",
                "description": "Emergency Department Triage Area expanded & color-coded bays marked",
                "is_critical": True
            },
            {
                "item_id": "MCI-02",
                "category": "STAFF",
                "description": "Hospital Disaster Command Center activated & Phase 2 surge recall initiated",
                "is_critical": True
            },
            {
                "item_id": "MCI-03",
                "category": "EQUIPMENT",
                "description": "Decontamination Shower Unit activated for CBRN / Chemical hazards",
                "is_critical": True
            },
            {
                "item_id": "MCI-04",
                "category": "ROOM_OR",
                "description": "Trauma Bays 1 through 4 & OR Suite #1-4 cleared for emergency surgeries",
                "is_critical": True
            },
            {
                "item_id": "MCI-05",
                "category": "BLOOD_PRODUCTS",
                "description": "20 Units Bulk Emergency O-Negative Blood stock released from regional blood bank",
                "is_critical": True
            }
        ]
    }
}
