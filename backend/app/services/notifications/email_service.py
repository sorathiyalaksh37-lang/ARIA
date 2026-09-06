"""
Email Notification Service using SendGrid
Sends HTML emails with templates and tracks delivery.
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Email, To, Content, Attachment, 
    FileContent, FileName, FileType, Disposition
)
from python_http_client.exceptions import HTTPError
import base64

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """SendGrid email service for notifications."""
    
    def __init__(self):
        """Initialize SendGrid client."""
        self.client = None
        if settings.SENDGRID_API_KEY:
            try:
                self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
                self.from_email = Email(
                    settings.SENDGRID_FROM_EMAIL,
                    settings.SENDGRID_FROM_NAME
                )
                logger.info("✅ SendGrid client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize SendGrid: {e}")
        else:
            logger.warning("⚠️ SendGrid API key not configured")
    
    def is_available(self) -> bool:
        """Check if email service is available."""
        return self.client is not None
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
        attachments: Optional[List[Dict]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Send HTML email to a single recipient.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text fallback
            attachments: List of attachments {filename, content, type}
            cc: CC recipients
            bcc: BCC recipients
            
        Returns:
            {
                "status_code": int,
                "message_id": str,
                "to": str,
                "timestamp": str
            }
        """
        if not self.is_available():
            logger.error("Email service not available")
            return None
        
        try:
            # Create message
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Add plain text content
            if plain_content:
                message.add_content(Content("text/plain", plain_content))
            
            # Add CC recipients
            if cc:
                for email in cc:
                    message.add_cc(email)
            
            # Add BCC recipients
            if bcc:
                for email in bcc:
                    message.add_bcc(email)
            
            # Add attachments
            if attachments:
                for att in attachments:
                    attachment = Attachment(
                        FileContent(att["content"]),
                        FileName(att["filename"]),
                        FileType(att.get("type", "application/octet-stream")),
                        Disposition("attachment")
                    )
                    message.add_attachment(attachment)
            
            # Send email
            response = self.client.send(message)
            
            result = {
                "status_code": response.status_code,
                "message_id": response.headers.get("X-Message-Id"),
                "to": to,
                "timestamp": datetime.utcnow().isoformat(),
                "provider": "sendgrid"
            }
            
            logger.info(f"✅ Email sent to {to}: {result['message_id']}")
            return result
            
        except HTTPError as e:
            logger.error(f"SendGrid HTTP error: {e}")
            return {
                "status_code": e.status_code,
                "error": str(e),
                "to": to,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return None
    
    async def send_batch_emails(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> List[Dict]:
        """
        Send emails to multiple recipients.
        
        Args:
            recipients: List of email addresses
            subject: Email subject
            html_content: HTML email body
            plain_content: Plain text fallback
            
        Returns:
            List of send results
        """
        results = []
        for email in recipients:
            result = await self.send_email(
                to=email,
                subject=subject,
                html_content=html_content,
                plain_content=plain_content
            )
            if result:
                results.append(result)
        
        logger.info(f"Batch email: {len(results)}/{len(recipients)} sent successfully")
        return results
    
    async def send_template_email(
        self,
        to: str,
        template_id: str,
        dynamic_data: Dict[str, Any]
    ) -> Optional[Dict]:
        """
        Send email using SendGrid dynamic template.
        
        Args:
            to: Recipient email
            template_id: SendGrid template ID
            dynamic_data: Template substitution data
            
        Returns:
            Send result
        """
        if not self.is_available():
            return None
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=To(to)
            )
            message.template_id = template_id
            message.dynamic_template_data = dynamic_data
            
            response = self.client.send(message)
            
            return {
                "status_code": response.status_code,
                "message_id": response.headers.get("X-Message-Id"),
                "to": to,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Template email error: {e}")
            return None
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address
            
        Returns:
            True if valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    async def attach_file(
        self,
        file_path: str,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Prepare file attachment.
        
        Args:
            file_path: Path to file
            filename: Display filename (optional)
            
        Returns:
            Attachment dictionary
        """
        import os
        import mimetypes
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Encode to base64
        encoded = base64.b64encode(file_data).decode()
        
        # Get MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return {
            "filename": filename or os.path.basename(file_path),
            "content": encoded,
            "type": mime_type or "application/octet-stream"
        }


# Global instance
email_service = EmailService()
