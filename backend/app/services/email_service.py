"""
SendGrid Email Integration Service
Provides email notifications with templates and delivery tracking
"""
import logging
from typing import Optional, Dict, List
from datetime import datetime
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """SendGrid email service with templates and attachments"""
    
    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.SENDGRID_FROM_EMAIL
        self.from_name = settings.SENDGRID_FROM_NAME
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self):
        """Initialize SendGrid client"""
        try:
            if self.api_key:
                self.client = SendGridAPIClient(self.api_key)
                logger.info("SendGrid client initialized successfully")
            else:
                logger.warning("SendGrid API key not configured")
        except Exception as e:
            logger.error(f"Failed to initialize SendGrid client: {str(e)}")
            self.client = None
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict:
        """
        Send email with optional attachments
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text version (optional)
            attachments: List of dicts with 'content' (base64), 'filename', 'type'
            cc: List of CC email addresses
            bcc: List of BCC email addresses
            
        Returns:
            Dict with status, message_id, error
        """
        if not self.client:
            logger.warning("SendGrid client not available")
            return {
                "status": "failed",
                "error": "Email service not configured",
                "message_id": None
            }
        
        try:
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=to,
                subject=subject,
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            # Add CC recipients
            if cc:
                for cc_email in cc:
                    message.add_cc(cc_email)
            
            # Add BCC recipients
            if bcc:
                for bcc_email in bcc:
                    message.add_bcc(bcc_email)
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    attached_file = Attachment(
                        FileContent(attachment["content"]),
                        FileName(attachment["filename"]),
                        FileType(attachment.get("type", "application/octet-stream")),
                        Disposition("attachment")
                    )
                    message.add_attachment(attached_file)
            
            # Send email
            response = self.client.send(message)
            
            logger.info(f"Email sent successfully to {to}")
            
            return {
                "status": "sent",
                "message_id": response.headers.get("X-Message-Id"),
                "to": to,
                "sent_at": datetime.utcnow().isoformat(),
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Email send error: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "message_id": None
            }
    
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> Dict:
        """
        Send email to multiple recipients
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text version
            
        Returns:
            Dict with success_count, failed_count, results
        """
        results = []
        success_count = 0
        failed_count = 0
        
        for recipient in recipients:
            result = await self.send_email(
                to=recipient,
                subject=subject,
                html_content=html_content,
                plain_content=plain_content
            )
            
            if result["status"] == "sent":
                success_count += 1
            else:
                failed_count += 1
            
            results.append({
                "recipient": recipient,
                **result
            })
        
        return {
            "total": len(recipients),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results
        }
    
    async def send_incident_notification(
        self,
        to: str,
        incident_id: str,
        severity: str,
        location: str,
        description: str,
        actions_taken: List[str]
    ) -> Dict:
        """Send incident notification email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .severity {{ display: inline-block; padding: 5px 15px; border-radius: 5px; font-weight: bold; }}
                .critical {{ background: #dc2626; color: white; }}
                .high {{ background: #f59e0b; color: white; }}
                .medium {{ background: #3b82f6; color: white; }}
                .low {{ background: #10b981; color: white; }}
                .actions {{ background: white; padding: 15px; margin-top: 15px; border-left: 4px solid #3b82f6; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Emergency Incident Alert</h1>
                </div>
                <div class="content">
                    <h2>Incident #{incident_id}</h2>
                    <p><strong>Severity:</strong> <span class="severity {severity.lower()}">{severity.upper()}</span></p>
                    <p><strong>Location:</strong> {location}</p>
                    <p><strong>Description:</strong></p>
                    <p>{description}</p>
                    
                    <div class="actions">
                        <h3>Actions Taken:</h3>
                        <ul>
                            {"".join([f"<li>{action}</li>" for action in actions_taken])}
                        </ul>
                    </div>
                </div>
                <div class="footer">
                    <p>ARIA Emergency Response System</p>
                    <p>This is an automated notification. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_content = f"""
        EMERGENCY INCIDENT ALERT
        
        Incident: #{incident_id}
        Severity: {severity.upper()}
        Location: {location}
        
        Description:
        {description}
        
        Actions Taken:
        {chr(10).join([f"- {action}" for action in actions_taken])}
        
        ARIA Emergency Response System
        """
        
        return await self.send_email(
            to=to,
            subject=f"🚨 Emergency Alert - Incident #{incident_id}",
            html_content=html_content,
            plain_content=plain_content
        )
    
    async def send_dispatch_confirmation(
        self,
        to: str,
        ambulance_id: str,
        incident_id: str,
        driver_name: str,
        incident_location: str,
        hospital_name: str,
        eta_minutes: int
    ) -> Dict:
        """Send ambulance dispatch confirmation email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #3b82f6; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .info-box {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #3b82f6; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚑 Ambulance Dispatched</h1>
                </div>
                <div class="content">
                    <h2>Dispatch Confirmation</h2>
                    
                    <div class="info-box">
                        <p><strong>Ambulance ID:</strong> {ambulance_id}</p>
                        <p><strong>Driver:</strong> {driver_name}</p>
                        <p><strong>Incident ID:</strong> #{incident_id}</p>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>Pickup Location:</strong> {incident_location}</p>
                        <p><strong>Destination:</strong> {hospital_name}</p>
                        <p><strong>ETA:</strong> {eta_minutes} minutes</p>
                    </div>
                    
                    <p>Track the ambulance in real-time via the ARIA dashboard.</p>
                </div>
                <div class="footer">
                    <p>ARIA Emergency Response System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=f"🚑 Ambulance Dispatched - {ambulance_id}",
            html_content=html_content
        )
    
    async def send_weekly_report(
        self,
        to: str,
        week_start: str,
        week_end: str,
        total_incidents: int,
        avg_response_time: float,
        success_rate: float,
        attachments: Optional[List[Dict]] = None
    ) -> Dict:
        """Send weekly performance report"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #10b981; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .metric {{ background: white; padding: 15px; margin: 10px 0; text-align: center; }}
                .metric-value {{ font-size: 32px; font-weight: bold; color: #3b82f6; }}
                .metric-label {{ color: #6b7280; font-size: 14px; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Weekly Performance Report</h1>
                    <p>{week_start} - {week_end}</p>
                </div>
                <div class="content">
                    <div class="metric">
                        <div class="metric-value">{total_incidents}</div>
                        <div class="metric-label">Total Incidents</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-value">{avg_response_time:.1f} min</div>
                        <div class="metric-label">Average Response Time</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-value">{success_rate:.1f}%</div>
                        <div class="metric-label">Success Rate</div>
                    </div>
                    
                    <p>Detailed report attached. View the full dashboard for more insights.</p>
                </div>
                <div class="footer">
                    <p>ARIA Emergency Response System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to=to,
            subject=f"📊 ARIA Weekly Report - {week_start} to {week_end}",
            html_content=html_content,
            attachments=attachments
        )


# Global instance
email_service = EmailService()
