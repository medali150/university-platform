"""
NotificationAPI integration service for absence management
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from notificationapi_python_server_sdk import notificationapi

# Configure logging
logger = logging.getLogger(__name__)

# NotificationAPI Configuration
NOTIFICATION_API_CLIENT_ID = "m9dp6o7vnr5t3uf2daxase81zj"
NOTIFICATION_API_CLIENT_SECRET = "pgc4yu6kxxftpmvo0ttxretux1sansgktjomqns4129ej5q30nqg35cwtw"

# Initialize NotificationAPI
notificationapi.init(NOTIFICATION_API_CLIENT_ID, NOTIFICATION_API_CLIENT_SECRET)

async def send_absence_notification(
    student_email: str,
    student_name: str,
    class_name: str,
    teacher_name: str,
    absence_date: str,
    absence_reason: str,
    notification_type: str = "absence_created"
) -> Dict[str, Any]:
    """
    Send absence notification to ALL channels in a single API call
    
    Args:
        student_email: Email of the student
        student_name: Full name of the student
        class_name: Name of the class/subject
        teacher_name: Name of the teacher
        absence_date: Date of absence
        absence_reason: Reason for absence
        notification_type: Type of notification (absence_created, justification_reviewed, etc.)
    
    Returns:
        Dict with notification status and details
    """
    try:
        logger.info(f"Sending absence notification to {student_email}")
        
        # Prepare notification payload for ALL channels
        notification_payload = {
            'type': 'abscense',  # Using the provided notification type
            'to': {
                'email': student_email
            },
            'email': {
                'subject': f'Absence marquée - {class_name}',
                'template_data': {
                    'student_name': student_name,
                    'class_name': class_name,
                    'teacher_name': teacher_name,
                    'absence_date': absence_date,
                    'absence_reason': absence_reason,
                    'notification_type': notification_type
                }
            },
            'inapp': {
                'title': f'Absence - {class_name}',
                'message': f'Votre absence du {absence_date} a été marquée par {teacher_name}. Motif: {absence_reason}',
                'data': {
                    'class_name': class_name,
                    'teacher_name': teacher_name,
                    'absence_date': absence_date,
                    'absence_reason': absence_reason,
                    'type': 'absence'
                }
            },
            'mobile_push': {
                'title': f'Absence - {class_name}',
                'body': f'Absence marquée le {absence_date} par {teacher_name}',
                'data': {
                    'class_name': class_name,
                    'teacher_name': teacher_name,
                    'absence_date': absence_date,
                    'absence_reason': absence_reason,
                    'type': 'absence',
                    'action': 'view_absence'
                }
            },
            'web_push': {
                'title': f'Absence - {class_name}',
                'body': f'Votre absence du {absence_date} a été enregistrée',
                'icon': '/icons/absence-icon.png',
                'badge': '/icons/badge.png',
                'data': {
                    'class_name': class_name,
                    'teacher_name': teacher_name,
                    'absence_date': absence_date,
                    'absence_reason': absence_reason,
                    'type': 'absence',
                    'url': '/dashboard/absences'
                }
            }
        }
        
        # Send notification to ALL channels in ONE API call
        result = await asyncio.to_thread(notificationapi.send, notification_payload)
        
        logger.info(f"Notification sent successfully to {student_email}")
        
        return {
            'status': 'success',
            'recipient': student_email,
            'channels': ['email', 'inapp', 'mobile_push', 'web_push'],
            'sent_at': datetime.now().isoformat(),
            'notification_id': result.get('id') if isinstance(result, dict) else None
        }
        
    except Exception as e:
        logger.error(f"Failed to send absence notification to {student_email}: {str(e)}")
        return {
            'status': 'error',
            'recipient': student_email,
            'error_message': str(e),
            'sent_at': datetime.now().isoformat(),
            'channels': []
        }

async def send_justification_notification(
    teacher_email: str,
    dept_head_email: str,
    student_name: str,
    class_name: str,
    absence_date: str,
    justification_text: str
) -> Dict[str, Any]:
    """
    Send justification notification to teacher and department head
    """
    try:
        logger.info(f"Sending justification notification for {student_name}")
        
        # Notification for department head
        dept_head_payload = {
            'type': 'abscense',
            'to': {
                'email': dept_head_email
            },
            'email': {
                'subject': f'Justification d\'absence - {student_name}',
                'template_data': {
                    'student_name': student_name,
                    'class_name': class_name,
                    'absence_date': absence_date,
                    'justification_text': justification_text,
                    'notification_type': 'justification_submitted'
                }
            },
            'inapp': {
                'title': 'Nouvelle justification d\'absence',
                'message': f'{student_name} a soumis une justification pour son absence du {absence_date}',
                'data': {
                    'student_name': student_name,
                    'class_name': class_name,
                    'absence_date': absence_date,
                    'type': 'justification_review'
                }
            }
        }
        
        result = await asyncio.to_thread(notificationapi.send, dept_head_payload)
        
        logger.info(f"Justification notification sent successfully")
        
        return {
            'status': 'success',
            'recipients': [dept_head_email],
            'channels': ['email', 'inapp'],
            'sent_at': datetime.now().isoformat(),
            'notification_id': result.get('id') if isinstance(result, dict) else None
        }
        
    except Exception as e:
        logger.error(f"Failed to send justification notification: {str(e)}")
        return {
            'status': 'error',
            'error_message': str(e),
            'sent_at': datetime.now().isoformat(),
            'recipients': [],
            'channels': []
        }

async def send_review_notification(
    student_email: str,
    student_name: str,
    class_name: str,
    absence_date: str,
    review_status: str,
    review_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send review decision notification to student
    """
    try:
        logger.info(f"Sending review notification to {student_email}")
        
        status_text = "approuvée" if review_status == "approved" else "rejetée"
        
        notification_payload = {
            'type': 'abscense',
            'to': {
                'email': student_email
            },
            'email': {
                'subject': f'Justification {status_text} - {class_name}',
                'template_data': {
                    'student_name': student_name,
                    'class_name': class_name,
                    'absence_date': absence_date,
                    'review_status': status_text,
                    'review_notes': review_notes or '',
                    'notification_type': 'justification_reviewed'
                }
            },
            'inapp': {
                'title': f'Justification {status_text}',
                'message': f'Votre justification pour l\'absence du {absence_date} a été {status_text}',
                'data': {
                    'class_name': class_name,
                    'absence_date': absence_date,
                    'review_status': review_status,
                    'type': 'justification_result'
                }
            },
            'mobile_push': {
                'title': f'Justification {status_text}',
                'body': f'Décision prise pour votre absence du {absence_date}',
                'data': {
                    'class_name': class_name,
                    'absence_date': absence_date,
                    'review_status': review_status,
                    'type': 'justification_result',
                    'action': 'view_absence'
                }
            }
        }
        
        result = await asyncio.to_thread(notificationapi.send, notification_payload)
        
        logger.info(f"Review notification sent successfully to {student_email}")
        
        return {
            'status': 'success',
            'recipient': student_email,
            'channels': ['email', 'inapp', 'mobile_push'],
            'sent_at': datetime.now().isoformat(),
            'notification_id': result.get('id') if isinstance(result, dict) else None
        }
        
    except Exception as e:
        logger.error(f"Failed to send review notification to {student_email}: {str(e)}")
        return {
            'status': 'error',
            'recipient': student_email,
            'error_message': str(e),
            'sent_at': datetime.now().isoformat(),
            'channels': []
        }

async def send_high_absence_alert(
    dept_head_email: str,
    student_name: str,
    student_email: str,
    absence_count: int,
    threshold: int = 3
) -> Dict[str, Any]:
    """
    Send alert when student exceeds absence threshold
    """
    try:
        logger.info(f"Sending high absence alert for {student_name}")
        
        notification_payload = {
            'type': 'abscense',
            'to': {
                'email': dept_head_email
            },
            'email': {
                'subject': f'Alerte: Taux d\'absence élevé - {student_name}',
                'template_data': {
                    'student_name': student_name,
                    'student_email': student_email,
                    'absence_count': absence_count,
                    'threshold': threshold,
                    'notification_type': 'high_absence_alert'
                }
            },
            'inapp': {
                'title': 'Alerte: Taux d\'absence élevé',
                'message': f'{student_name} a {absence_count} absences (seuil: {threshold})',
                'data': {
                    'student_name': student_name,
                    'student_email': student_email,
                    'absence_count': absence_count,
                    'type': 'high_absence_alert'
                }
            }
        }
        
        result = await asyncio.to_thread(notificationapi.send, notification_payload)
        
        logger.info(f"High absence alert sent successfully")
        
        return {
            'status': 'success',
            'recipient': dept_head_email,
            'channels': ['email', 'inapp'],
            'sent_at': datetime.now().isoformat(),
            'notification_id': result.get('id') if isinstance(result, dict) else None
        }
        
    except Exception as e:
        logger.error(f"Failed to send high absence alert: {str(e)}")
        return {
            'status': 'error',
            'error_message': str(e),
            'sent_at': datetime.now().isoformat(),
            'recipient': dept_head_email,
            'channels': []
        }