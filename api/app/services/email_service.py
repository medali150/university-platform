"""
Email service for sending emails via SMTP
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str = None
):
    """
    Send an email using SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        text_content: Plain text content (optional, defaults to stripped HTML)
    """
    # Create message
    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = to_email
    message["Subject"] = subject
    
    # Add text and HTML parts
    if text_content:
        text_part = MIMEText(text_content, "plain")
        message.attach(text_part)
    
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)
    
    # Send email
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        raise


async def send_password_reset_email(
    to_email: str,
    user_name: str,
    reset_token: str,
    reset_link: str
):
    """
    Send password reset email with branded template
    
    Args:
        to_email: User's email address
        user_name: User's full name
        reset_token: Password reset token
        reset_link: Complete reset link with token
    """
    subject = "🔐 Réinitialisation de votre mot de passe - Plateforme Universitaire"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 3px solid #2563eb;
            }}
            .logo {{
                background-color: #2563eb;
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                margin-bottom: 10px;
            }}
            h1 {{
                color: #2563eb;
                margin: 10px 0;
            }}
            .content {{
                padding: 30px 0;
            }}
            .button {{
                display: inline-block;
                padding: 15px 30px;
                background-color: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 20px 0;
            }}
            .button:hover {{
                background-color: #1d4ed8;
            }}
            .warning {{
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .footer {{
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }}
            .token-box {{
                background-color: #e0e7ff;
                border: 2px dashed #2563eb;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                font-family: monospace;
                word-break: break-all;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🎓</div>
                <h1>Plateforme Universitaire</h1>
            </div>
            
            <div class="content">
                <h2>Bonjour {user_name},</h2>
                
                <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.</p>
                
                <p>Cliquez sur le bouton ci-dessous pour créer un nouveau mot de passe :</p>
                
                <div style="text-align: center;">
                    <a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>
                </div>
                
                <p>Ou copiez et collez ce lien dans votre navigateur :</p>
                <div class="token-box">
                    {reset_link}
                </div>
                
                <div class="warning">
                    <strong>⚠️ Attention :</strong>
                    <ul style="margin: 10px 0;">
                        <li>Ce lien est valable pendant <strong>1 heure</strong></li>
                        <li>Il ne peut être utilisé qu'<strong>une seule fois</strong></li>
                        <li>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email</li>
                    </ul>
                </div>
                
                <p>Pour des raisons de sécurité, si vous n'êtes pas à l'origine de cette demande, veuillez contacter immédiatement l'administration.</p>
            </div>
            
            <div class="footer">
                <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                <p>&copy; 2025 Plateforme Universitaire - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Plateforme Universitaire - Réinitialisation de mot de passe
    
    Bonjour {user_name},
    
    Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.
    
    Pour réinitialiser votre mot de passe, veuillez cliquer sur le lien suivant :
    {reset_link}
    
    ATTENTION :
    - Ce lien est valable pendant 1 heure
    - Il ne peut être utilisé qu'une seule fois
    - Si vous n'avez pas demandé cette réinitialisation, ignorez cet email
    
    Pour des raisons de sécurité, si vous n'êtes pas à l'origine de cette demande, 
    veuillez contacter immédiatement l'administration.
    
    Cordialement,
    L'équipe de la Plateforme Universitaire
    """
    
    await send_email(to_email, subject, html_content, text_content)


async def send_absence_notification_email(
    to_email: str,
    student_name: str,
    absence_count: int,
    subject_name: str,
    absence_date: str,
    teacher_name: str
):
    """
    Send absence notification email to student
    
    Args:
        to_email: Student's email address
        student_name: Student's full name
        absence_count: Total number of absences for this subject
        subject_name: Name of the subject/course
        absence_date: Date of the absence
        teacher_name: Name of the teacher who marked the absence
    """
    
    # Determine email content based on absence count
    if absence_count == 1:
        subject = "⚠️ Notification d'Absence - Plateforme Universitaire"
        warning_level = "Première Absence"
        warning_color = "#fbbf24"  # Yellow
        warning_message = "Ceci est votre première absence. Soyez vigilant!"
    elif absence_count == 2:
        subject = "🔴 ALERTE: Deuxième Absence - Risque d'Élimination"
        warning_level = "Deuxième Absence - ATTENTION"
        warning_color = "#f97316"  # Orange
        warning_message = "⚠️ ATTENTION: Une troisième absence entraînera votre élimination de l'examen!"
    else:  # absence_count >= 3
        subject = "❌ ÉLIMINATION: Troisième Absence Enregistrée"
        warning_level = "Troisième Absence - ÉLIMINÉ"
        warning_color = "#dc2626"  # Red
        warning_message = "❌ VOUS ÊTES ÉLIMINÉ de l'examen de cette matière suite à 3 absences."
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                padding-bottom: 20px;
                border-bottom: 3px solid {warning_color};
            }}
            .logo {{
                background-color: {warning_color};
                color: white;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-size: 30px;
                margin-bottom: 10px;
            }}
            h1 {{
                color: {warning_color};
                margin: 10px 0;
            }}
            .content {{
                padding: 30px 0;
            }}
            .warning-box {{
                background-color: {warning_color}20;
                border-left: 4px solid {warning_color};
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .warning-box h2 {{
                color: {warning_color};
                margin-top: 0;
            }}
            .info-box {{
                background-color: #e0e7ff;
                border: 2px solid #3b82f6;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #ddd;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                font-weight: bold;
                color: #555;
            }}
            .footer {{
                text-align: center;
                padding-top: 20px;
                border-top: 1px solid #ddd;
                font-size: 12px;
                color: #666;
            }}
            .counter {{
                background-color: {warning_color};
                color: white;
                padding: 10px 20px;
                border-radius: 50px;
                font-size: 24px;
                font-weight: bold;
                display: inline-block;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">⚠️</div>
                <h1>Notification d&apos;Absence</h1>
            </div>
            
            <div class="content">
                <h2>Bonjour {student_name},</h2>
                
                <p>Nous vous informons qu&apos;une absence a été enregistrée dans votre dossier académique.</p>
                
                <div class="info-box">
                    <div class="info-row">
                        <span class="info-label">Matière:</span>
                        <span>{subject_name}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Date:</span>
                        <span>{absence_date}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Enseignant:</span>
                        <span>{teacher_name}</span>
                    </div>
                </div>
                
                <div class="warning-box">
                    <h2>{warning_level}</h2>
                    <div style="text-align: center;">
                        <div class="counter">Absence #{absence_count}</div>
                    </div>
                    <p style="font-size: 16px; font-weight: bold; margin: 15px 0;">
                        {warning_message}
                    </p>
                    
                    {'<p style="color: #dc2626; font-weight: bold;">⛔ CONSÉQUENCE: Vous ne pourrez pas passer l\'examen de cette matière.</p>' if absence_count >= 3 else ''}
                    {'<p style="color: #f97316;">⚠️ Une absence supplémentaire vous éliminera automatiquement de l\'examen!</p>' if absence_count == 2 else ''}
                </div>
                
                <div style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 5px;">
                    <h3 style="margin-top: 0; color: #92400e;">📋 Rappel du Règlement:</h3>
                    <ul style="margin: 10px 0; color: #78350f;">
                        <li>1ère absence: Avertissement</li>
                        <li>2ème absence: Alerte - Risque d&apos;élimination</li>
                        <li>3ème absence: <strong>Élimination automatique de l&apos;examen</strong></li>
                    </ul>
                </div>
                
                <p>Si vous pensez qu&apos;il s&apos;agit d&apos;une erreur, veuillez contacter votre enseignant ou l&apos;administration immédiatement.</p>
            </div>
            
            <div class="footer">
                <p>Cet email a été envoyé automatiquement par le système de gestion des absences.</p>
                <p>&copy; 2025 Plateforme Universitaire - Tous droits réservés</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Notification d'Absence - Plateforme Universitaire
    
    Bonjour {student_name},
    
    Une absence a été enregistrée dans votre dossier académique:
    
    Matière: {subject_name}
    Date: {absence_date}
    Enseignant: {teacher_name}
    
    {warning_level}
    Nombre total d'absences: {absence_count}
    
    {warning_message}
    
    RAPPEL DU RÈGLEMENT:
    - 1ère absence: Avertissement
    - 2ème absence: Alerte - Risque d'élimination
    - 3ème absence: Élimination automatique de l'examen
    
    Si vous pensez qu'il s'agit d'une erreur, veuillez contacter votre enseignant 
    ou l'administration immédiatement.
    
    Cordialement,
    L'équipe de la Plateforme Universitaire
    """
    
    await send_email(to_email, subject, html_content, text_content)
