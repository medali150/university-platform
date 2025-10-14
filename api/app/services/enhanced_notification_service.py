"""
Enhanced absence notification system for students and teachers
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from prisma import Prisma
except ImportError:
    # Mock Prisma for development
    class Prisma:
        pass

# Configure logging
logger = logging.getLogger(__name__)

# NotificationAPI Configuration (Mock implementation for now)
NOTIFICATION_API_CLIENT_ID = "m9dp6o7vnr5t3uf2daxase81zj"
NOTIFICATION_API_CLIENT_SECRET = "pgc4yu6kxxftpmvo0ttxretux1sansgktjomqns4129ej5q30nqg35cwtw"

# Mock NotificationAPI for development
class MockNotificationAPI:
    @staticmethod
    def send(data):
        logger.info(f"Mock notification sent: {data}")
        return {"success": True, "message": "Mock notification sent"}

notificationapi = MockNotificationAPI()

class AbsenceNotificationService:
    """Comprehensive notification service for absence management"""
    
    @staticmethod
    async def notify_student_absence_marked(
        student_email: str,
        student_name: str,
        subject_name: str,
        teacher_name: str,
        absence_date: str,
        absence_time: str,
        absence_reason: str,
        absence_id: str
    ) -> Dict[str, Any]:
        """
        Notify student when teacher marks them absent
        Sent via: Email, In-App, Mobile Push, Web Push
        """
        try:
            logger.info(f"🔔 Notifying student {student_email} about absence marked")
            
            notification_payload = {
                'notificationId': 'student_absence_marked',
                'user': {
                    'id': student_email,
                    'email': student_email
                },
                'mergeTags': {
                    'student_name': student_name,
                    'subject_name': subject_name,
                    'teacher_name': teacher_name,
                    'absence_date': absence_date,
                    'absence_time': absence_time,
                    'absence_reason': absence_reason,
                    'absence_id': absence_id,
                    'platform_url': 'https://university-platform.com/dashboard/absences'
                }
            }
            
            result = await asyncio.to_thread(notificationapi.send, notification_payload)
            
            return {
                'status': 'success',
                'recipient': student_email,
                'notification_type': 'absence_marked',
                'channels': ['email', 'inapp', 'mobile_push', 'web_push'],
                'sent_at': datetime.now().isoformat(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to notify student about absence: {str(e)}")
            return {
                'status': 'error',
                'recipient': student_email,
                'error': str(e)
            }
    
    @staticmethod
    async def notify_teacher_absence_justified(
        teacher_email: str,
        teacher_name: str,
        student_name: str,
        subject_name: str,
        absence_date: str,
        justification_text: str,
        absence_id: str
    ) -> Dict[str, Any]:
        """
        Notify teacher when student submits justification
        Sent via: Email, In-App
        """
        try:
            logger.info(f"🔔 Notifying teacher {teacher_email} about justification")
            
            notification_payload = {
                'notificationId': 'teacher_justification_received',
                'user': {
                    'id': teacher_email,
                    'email': teacher_email
                },
                'mergeTags': {
                    'teacher_name': teacher_name,
                    'student_name': student_name,
                    'subject_name': subject_name,
                    'absence_date': absence_date,
                    'justification_text': justification_text[:200] + '...' if len(justification_text) > 200 else justification_text,
                    'absence_id': absence_id,
                    'review_url': f'https://university-platform.com/dashboard/absences?id={absence_id}'
                }
            }
            
            result = await asyncio.to_thread(notificationapi.send, notification_payload)
            
            return {
                'status': 'success',
                'recipient': teacher_email,
                'notification_type': 'justification_received',
                'channels': ['email', 'inapp'],
                'sent_at': datetime.now().isoformat(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to notify teacher about justification: {str(e)}")
            return {
                'status': 'error',
                'recipient': teacher_email,
                'error': str(e)
            }
    
    @staticmethod
    async def notify_student_justification_reviewed(
        student_email: str,
        student_name: str,
        subject_name: str,
        absence_date: str,
        review_status: str,  # 'approved', 'rejected'
        reviewer_name: str,
        review_comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Notify student when justification is reviewed
        Sent via: Email, In-App, Mobile Push
        """
        try:
            logger.info(f"🔔 Notifying student {student_email} about review decision")
            
            status_text = "approuvée" if review_status == "approved" else "rejetée"
            status_color = "green" if review_status == "approved" else "red"
            
            notification_payload = {
                'notificationId': 'student_justification_reviewed',
                'user': {
                    'id': student_email,
                    'email': student_email
                },
                'mergeTags': {
                    'student_name': student_name,
                    'subject_name': subject_name,
                    'absence_date': absence_date,
                    'review_status': status_text,
                    'review_status_color': status_color,
                    'reviewer_name': reviewer_name,
                    'review_comment': review_comment or 'Aucun commentaire',
                    'platform_url': 'https://university-platform.com/dashboard/absences'
                }
            }
            
            result = await asyncio.to_thread(notificationapi.send, notification_payload)
            
            return {
                'status': 'success',
                'recipient': student_email,
                'notification_type': 'justification_reviewed',
                'channels': ['email', 'inapp', 'mobile_push'],
                'sent_at': datetime.now().isoformat(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to notify student about review: {str(e)}")
            return {
                'status': 'error',
                'recipient': student_email,
                'error': str(e)
            }
    
    @staticmethod
    async def notify_department_head_high_absences(
        dept_head_email: str,
        dept_head_name: str,
        student_name: str,
        student_email: str,
        absence_count: int,
        subject_name: str,
        threshold: int = 3
    ) -> Dict[str, Any]:
        """
        Notify department head when student exceeds absence threshold
        Sent via: Email, In-App
        """
        try:
            logger.info(f"🚨 Notifying department head {dept_head_email} about high absences")
            
            notification_payload = {
                'notificationId': 'dept_head_high_absence_alert',
                'user': {
                    'id': dept_head_email,
                    'email': dept_head_email
                },
                'mergeTags': {
                    'dept_head_name': dept_head_name,
                    'student_name': student_name,
                    'student_email': student_email,
                    'absence_count': str(absence_count),
                    'subject_name': subject_name,
                    'threshold': str(threshold),
                    'alert_level': 'high' if absence_count > threshold * 2 else 'medium',
                    'student_profile_url': f'https://university-platform.com/dashboard/students/{student_email}'
                }
            }
            
            result = await asyncio.to_thread(notificationapi.send, notification_payload)
            
            return {
                'status': 'success',
                'recipient': dept_head_email,
                'notification_type': 'high_absence_alert',
                'channels': ['email', 'inapp'],
                'sent_at': datetime.now().isoformat(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to notify department head about high absences: {str(e)}")
            return {
                'status': 'error',
                'recipient': dept_head_email,
                'error': str(e)
            }
    
    @staticmethod
    async def notify_parents_repeated_absences(
        parent_email: str,
        parent_name: str,
        student_name: str,
        absence_count: int,
        recent_absences: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Notify parents about repeated absences
        Sent via: Email, SMS (if configured)
        """
        try:
            logger.info(f"📧 Notifying parent {parent_email} about repeated absences")
            
            # Format recent absences for email
            absence_list = "\n".join([
                f"• {abs['date']} - {abs['subject']} ({abs['reason']})"
                for abs in recent_absences
            ])
            
            notification_payload = {
                'notificationId': 'parent_repeated_absences',
                'user': {
                    'id': parent_email,
                    'email': parent_email
                },
                'mergeTags': {
                    'parent_name': parent_name,
                    'student_name': student_name,
                    'absence_count': str(absence_count),
                    'absence_list': absence_list,
                    'contact_school_phone': '+216 71 123 456',
                    'platform_url': 'https://university-platform.com/parent-portal'
                }
            }
            
            result = await asyncio.to_thread(notificationapi.send, notification_payload)
            
            return {
                'status': 'success',
                'recipient': parent_email,
                'notification_type': 'repeated_absences',
                'channels': ['email'],
                'sent_at': datetime.now().isoformat(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to notify parent about repeated absences: {str(e)}")
            return {
                'status': 'error',
                'recipient': parent_email,
                'error': str(e)
            }
    
    @staticmethod
    async def send_daily_absence_summary(
        teacher_email: str,
        teacher_name: str,
        date: str,
        total_absences: int,
        pending_justifications: int,
        subjects_taught: List[str]
    ) -> Dict[str, Any]:
        """
        Send daily summary to teachers
        Sent via: Email, In-App
        """
        try:
            logger.info(f"📊 Sending daily absence summary to {teacher_email}")
            
            notification_payload = {
                'notificationId': 'teacher_daily_summary',
                'user': {
                    'id': teacher_email,
                    'email': teacher_email
                },
                'mergeTags': {
                    'teacher_name': teacher_name,
                    'date': date,
                    'total_absences': str(total_absences),
                    'pending_justifications': str(pending_justifications),
                    'subjects_list': ', '.join(subjects_taught),
                    'dashboard_url': 'https://university-platform.com/dashboard/absences'
                }
            }
            
            result = await asyncio.to_thread(notificationapi.send, notification_payload)
            
            return {
                'status': 'success',
                'recipient': teacher_email,
                'notification_type': 'daily_summary',
                'channels': ['email', 'inapp'],
                'sent_at': datetime.now().isoformat(),
                'result': result
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send daily summary: {str(e)}")
            return {
                'status': 'error',
                'recipient': teacher_email,
                'error': str(e)
            }

# Compatibility function for existing code
async def send_notification_with_details(
    user_id: str,
    notification_id: str,
    title: str,
    message: str,
    channels: List[str] = None,
    template_data: Dict[str, Any] = None
):
    """Compatibility function for existing notification calls"""
    try:
        # Mock notification sending for compatibility
        print(f"📧 Mock Notification Sent:")
        print(f"   User: {user_id}")
        print(f"   ID: {notification_id}")
        print(f"   Title: {title}")
        print(f"   Message: {message}")
        print(f"   Channels: {channels or ['email', 'in_app']}")
        if template_data:
            print(f"   Data: {template_data}")
        
        return {"success": True, "message": "Notification sent successfully"}
        
    except Exception as e:
        logger.error(f"Failed to send notification to {user_id}: {e}")
        return {"success": False, "error": str(e)}

# Create a global instance
absence_notifications = AbsenceNotificationService()