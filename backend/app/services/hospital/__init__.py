"""
Hospital Service Package
Exposes hospital_prep_service and CHECKLIST_TEMPLATES.
"""

from app.services.hospital.checklist_templates import CHECKLIST_TEMPLATES
from app.services.hospital.preparation_service import hospital_prep_service, HospitalPreparationService

__all__ = [
    "CHECKLIST_TEMPLATES",
    "hospital_prep_service",
    "HospitalPreparationService",
]
