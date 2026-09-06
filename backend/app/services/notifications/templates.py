"""
Notification Templates for SMS and Email
All notification templates with dynamic content injection.
"""
from typing import Dict, Any
from datetime import datetime


class NotificationTemplates:
    """Templates for all notification types."""
    
    # ============================================================================
    # SMS TEMPLATES (Max 1600 chars)
    # ============================================================================
    
    @staticmethod
    def sms_incident_created(data: Dict[str, Any]) -> str:
        """Template for new incident notification."""
        return f"""ARIA Emergency Alert

New Incident: {data['incident_id']}
Type: {data['incident_type']}
Severity: {data['severity']}
Location: {data['location']}
Victims: {data['victim_count']}

Action Required: Review and approve response plan.

Portal: {data.get('portal_url', 'https://aria.emergency.gov')}"""
    
    @staticmethod
    def sms_ambulance_dispatched(data: Dict[str, Any]) -> str:
        """Template for ambulance dispatch notification."""
        return f"""ARIA Dispatch Notification

Ambulance: {data['ambulance_id']}
Incident: {data['incident_id']}

📍 Pickup: {data['incident_location']}
🏥 Hospital: {data['hospital_name']}

ETA: {data['eta']} minutes
Distance: {data['distance']} km

Route: {data.get('route_url', 'Check GPS')}

Drive safely!"""
    
    @staticmethod
    def sms_patient_en_route(data: Dict[str, Any]) -> str:
        """Template for patient en route notification."""
        return f"""ARIA Hospital Alert

Patient En Route
ETA: {data['eta']} minutes

Incident: {data['incident_id']}
Severity: {data['severity']}
Patients: {data['patient_count']}

Injuries: {data['injury_summary']}
Blood Type: {data.get('blood_type', 'Unknown')}

Prepare: {data['required_resources']}

Contact: {data['ambulance_phone']}"""
    
    @staticmethod
    def sms_blood_required(data: Dict[str, Any]) -> str:
        """Template for blood requirement notification."""
        return f"""ARIA Blood Request

URGENT: Blood Required

Type: {data['blood_type']}
Units: {data['units']}
Hospital: {data['hospital_name']}

Incident: {data['incident_id']}
ETA: {data['eta']} minutes

Please confirm availability.
Call: {data['contact_number']}"""
    
    @staticmethod
    def sms_plan_approved(data: Dict[str, Any]) -> str:
        """Template for plan approval notification."""
        return f"""ARIA Plan Approved

Incident: {data['incident_id']}
Approved by: {data['approved_by']}
Time: {data['approved_at']}

Dispatching resources:
✓ Ambulance: {data['ambulance_id']}
✓ Hospital: {data['hospital_name']}
✓ Blood: {data.get('blood_reserved', 'N/A')}

Execution starting now."""
    
    @staticmethod
    def sms_plan_rejected(data: Dict[str, Any]) -> str:
        """Template for plan rejection notification."""
        return f"""ARIA Plan Rejected

Incident: {data['incident_id']}
Rejected by: {data['rejected_by']}

Reason: {data['rejection_reason']}

Action Required: Generate new plan with adjustments.

Time: {data['rejected_at']}"""
    
    @staticmethod
    def sms_family_notification(data: Dict[str, Any]) -> str:
        """Template for family notification."""
        return f"""Emergency Update

{data['patient_name']} has been transported to:

{data['hospital_name']}
{data['hospital_address']}
Ph: {data['hospital_phone']}

Condition: {data['condition']}
Status: {data['status']}

Please contact hospital for more information.

Incident ID: {data['incident_id']}"""
    
    # ============================================================================
    # EMAIL TEMPLATES (HTML)
    # ============================================================================
    
    @staticmethod
    def email_incident_created(data: Dict[str, Any]) -> str:
        """HTML template for new incident notification."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #dc2626; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
        .footer {{ background: #f3f4f6; padding: 15px; text-align: center; border-radius: 0 0 8px 8px; }}
        .badge {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }}
        .badge-critical {{ background: #fee2e2; color: #991b1b; }}
        .badge-high {{ background: #fed7aa; color: #9a3412; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
        .info-row {{ padding: 8px 0; border-bottom: 1px solid #e5e7eb; }}
        .label {{ font-weight: bold; color: #6b7280; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 New Emergency Incident</h1>
        </div>
        <div class="content">
            <p>A new emergency incident has been created and requires immediate attention.</p>
            
            <div class="info-row">
                <span class="label">Incident ID:</span> {data['incident_id']}
            </div>
            <div class="info-row">
                <span class="label">Type:</span> {data['incident_type']}
            </div>
            <div class="info-row">
                <span class="label">Severity:</span> 
                <span class="badge badge-{data['severity'].lower()}">{data['severity']}</span>
            </div>
            <div class="info-row">
                <span class="label">Location:</span> {data['location']}
            </div>
            <div class="info-row">
                <span class="label">Victims:</span> {data['victim_count']}
            </div>
            <div class="info-row">
                <span class="label">Time:</span> {data['created_at']}
            </div>
            
            <h3>Description</h3>
            <p>{data['description']}</p>
            
            <h3>Required Action</h3>
            <p>Please review the AI-generated response plan and approve for dispatch.</p>
            
            <a href="{data['portal_url']}" class="button">View Incident Details →</a>
        </div>
        <div class="footer">
            <p>ARIA Emergency Response System</p>
            <p style="font-size: 12px; color: #6b7280;">This is an automated notification. Do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def email_ambulance_dispatched(data: Dict[str, Any]) -> str:
        """HTML template for ambulance dispatch."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #059669; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
        .route-box {{ background: white; padding: 15px; border-left: 4px solid #2563eb; margin: 15px 0; }}
        .button {{ display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 6px; margin: 10px 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚑 Ambulance Dispatch Order</h1>
        </div>
        <div class="content">
            <h2>Dispatch Details</h2>
            <p><strong>Ambulance:</strong> {data['ambulance_id']}</p>
            <p><strong>Crew:</strong> {data.get('crew_names', 'N/A')}</p>
            <p><strong>Incident:</strong> {data['incident_id']}</p>
            
            <div class="route-box">
                <h3>📍 Route Information</h3>
                <p><strong>Pickup Location:</strong><br>{data['incident_location']}</p>
                <p><strong>Destination Hospital:</strong><br>{data['hospital_name']}<br>{data['hospital_address']}</p>
                <p><strong>ETA:</strong> {data['eta']} minutes</p>
                <p><strong>Distance:</strong> {data['distance']} km</p>
            </div>
            
            <h3>Patient Information</h3>
            <p><strong>Estimated Victims:</strong> {data['victim_count']}</p>
            <p><strong>Severity:</strong> {data['severity']}</p>
            <p><strong>Injuries:</strong> {data.get('injury_summary', 'See incident details')}</p>
            
            <h3>Required Equipment</h3>
            <ul>
                {data.get('required_equipment_html', '<li>Standard emergency kit</li>')}
            </ul>
            
            <div style="text-align: center; margin-top: 20px;">
                <a href="{data['route_url']}" class="button">View Route on Map →</a>
                <a href="{data['incident_url']}" class="button">Incident Details →</a>
            </div>
            
            <p style="margin-top: 20px; padding: 15px; background: #fef3c7; border-left: 4px solid #f59e0b;">
                ⚠️ <strong>Safety First:</strong> Drive carefully and follow all traffic regulations. Patient safety begins with crew safety.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def email_patient_en_route(data: Dict[str, Any]) -> str:
        """HTML template for patient en route notification."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #7c3aed; color: white; padding: 20px; border-radius: 8px 8px 0 0; }}
        .content {{ background: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
        .alert-box {{ background: #fef2f2; border: 2px solid #dc2626; padding: 15px; margin: 15px 0; border-radius: 6px; }}
        .prep-list {{ background: white; padding: 15px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Patient En Route to Your Facility</h1>
        </div>
        <div class="content">
            <div class="alert-box">
                <h2 style="margin-top: 0; color: #dc2626;">⏱️ ETA: {data['eta']} Minutes</h2>
                <p><strong>Prepare emergency department immediately</strong></p>
            </div>
            
            <h3>Incident Information</h3>
            <p><strong>Incident ID:</strong> {data['incident_id']}</p>
            <p><strong>Severity:</strong> {data['severity']}</p>
            <p><strong>Number of Patients:</strong> {data['patient_count']}</p>
            
            <h3>Medical Information</h3>
            <p><strong>Primary Injuries:</strong><br>{data['injury_summary']}</p>
            <p><strong>Blood Type:</strong> {data.get('blood_type', 'Unknown - Test on arrival')}</p>
            <p><strong>Vitals:</strong> {data.get('vitals_summary', 'Will be updated by ambulance crew')}</p>
            
            <div class="prep-list">
                <h3>Required Preparations</h3>
                <ul>
                    {data.get('preparation_html', '<li>Standard emergency room setup</li>')}
                </ul>
            </div>
            
            <h3>Contact Information</h3>
            <p><strong>Ambulance:</strong> {data['ambulance_id']}</p>
            <p><strong>Crew Contact:</strong> {data['ambulance_phone']}</p>
            <p><strong>Coordinator:</strong> {data.get('coordinator_name', 'ARIA System')}</p>
            
            <p style="margin-top: 20px; padding: 15px; background: #dbeafe; border-left: 4px solid #2563eb;">
                ℹ️ Real-time updates will be sent via SMS as the ambulance approaches.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def get_plain_text_version(html: str) -> str:
        """
        Convert HTML to plain text.
        Simple version - removes HTML tags.
        """
        import re
        # Remove HTML tags
        text = re.sub('<[^<]+?>', '', html)
        # Remove extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text.strip()


# Global instance
templates = NotificationTemplates()
