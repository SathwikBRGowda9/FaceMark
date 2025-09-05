import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from flask import current_app

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "sathwikgowdabr10@gmail.com"
        self.password = "ywxj betc rjay sfgm"
    
    def send_attendance_confirmation(self, student_email, student_name, timestamp):
        """Send attendance confirmation email to student"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = student_email
            msg['Subject'] = "✅ Attendance Confirmed - FaceMark"
            
            # HTML email template
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #007bff, #0056b3); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">
                            <span style="display: inline-block; margin-right: 10px;">✅</span>
                            Attendance Confirmed
                        </h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                        <h2 style="color: #333; margin-top: 0;">Hello {student_name}!</h2>
                        
                        <p style="color: #666; font-size: 16px; line-height: 1.6;">
                            Your attendance has been successfully recorded using FaceMark's face recognition system.
                        </p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                            <h3 style="color: #28a745; margin-top: 0;">Attendance Details</h3>
                            <p style="margin: 5px 0; color: #333;"><strong>Date:</strong> {timestamp.strftime('%B %d, %Y')}</p>
                            <p style="margin: 5px 0; color: #333;"><strong>Time:</strong> {timestamp.strftime('%I:%M %p')}</p>
                            <p style="margin: 5px 0; color: #333;"><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">Present</span></p>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 30px;">
                            This is an automated message from the FaceMark attendance system. 
                            If you have any questions, please contact your administrator.
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                © 2024 FaceMark - Advanced Face Recognition Attendance System
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            return True, "Attendance confirmation sent successfully"
            
        except Exception as e:
            return False, f"Failed to send confirmation email: {str(e)}"
    
    def send_absence_notification(self, student_email, student_name, date, cutoff_time):
        """Send absence notification email to student"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = student_email
            msg['Subject'] = "⚠️ Absence Alert - FaceMark"
            
            # HTML email template
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #dc3545, #c82333); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 24px;">
                            <span style="display: inline-block; margin-right: 10px;">⚠️</span>
                            Absence Alert
                        </h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e9ecef;">
                        <h2 style="color: #333; margin-top: 0;">Hello {student_name},</h2>
                        
                        <p style="color: #666; font-size: 16px; line-height: 1.6;">
                            Our system has detected that you were not present during today's attendance check.
                        </p>
                        
                        <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc3545;">
                            <h3 style="color: #dc3545; margin-top: 0;">Absence Details</h3>
                            <p style="margin: 5px 0; color: #333;"><strong>Date:</strong> {date.strftime('%B %d, %Y')}</p>
                            <p style="margin: 5px 0; color: #333;"><strong>Cutoff Time:</strong> {cutoff_time}</p>
                            <p style="margin: 5px 0; color: #333;"><strong>Status:</strong> <span style="color: #dc3545; font-weight: bold;">Absent</span></p>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0;">
                            <p style="margin: 0; color: #856404; font-size: 14px;">
                                <strong>Important:</strong> If you were present but not detected by the system, 
                                please contact your administrator immediately to resolve this issue.
                            </p>
                        </div>
                        
                        <p style="color: #666; font-size: 14px; margin-top: 30px;">
                            This is an automated message from the FaceMark attendance system. 
                            If you believe this is an error, please contact your administrator as soon as possible.
                        </p>
                        
                        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #e9ecef;">
                            <p style="color: #999; font-size: 12px; margin: 0;">
                                © 2024 FaceMark - Advanced Face Recognition Attendance System
                            </p>
                        </div>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()
            
            return True, "Absence notification sent successfully"
            
        except Exception as e:
            return False, f"Failed to send absence notification: {str(e)}"

# Initialize email service
email_service = EmailService()