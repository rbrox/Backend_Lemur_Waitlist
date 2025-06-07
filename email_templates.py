"""
Email templates for the Lemur waitlist application.
"""

def get_welcome_email_template(user_name=None):
    """Get the welcome email template with optional personalization."""
    
    # Determine greeting
    if user_name:
        greeting = f"Hi {user_name},"
        personalized_message = f"Thank you, {user_name}, for joining our waitlist!"
    else:
        greeting = "Hi there,"
        personalized_message = "Thank you for joining our waitlist!"
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Lemur Waitlist</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Lemur! 🚀</h1>
        </div>
        
        <div style="background: #f8f9fa; padding: 25px; border-radius: 8px; margin-bottom: 25px;">
            <p style="font-size: 18px; margin-bottom: 15px;">{greeting}</p>
            
            <p style="font-size: 16px; margin-bottom: 20px;">{personalized_message}</p>
            
            <p style="font-size: 16px; margin-bottom: 20px;">
                We're thrilled to have you on board! You're now part of an exclusive group of early adopters who will be the first to experience Lemur when we launch.
            </p>
            
            <div style="background: white; padding: 20px; border-radius: 6px; border-left: 4px solid #667eea;">
                <h3 style="color: #667eea; margin-top: 0;">What happens next?</h3>
                <ul style="padding-left: 20px;">
                    <li>We'll keep you updated on our progress</li>
                    <li>You'll get early access when we launch</li>
                    <li>Exclusive updates and behind-the-scenes content</li>
                    <li>Priority support and feedback opportunities</li>
                </ul>
            </div>
        </div>
        
        <div style="text-align: center; padding: 20px; background: #f1f3f4; border-radius: 8px;">
            <p style="margin: 0; color: #666; font-size: 14px;">
                Thank you for your patience and support!<br>
                <strong>The Lemur Team</strong>
            </p>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 12px; margin: 0;">
                You received this email because you signed up for the Lemur waitlist.<br>
                If you have any questions, feel free to reply to this email.
            </p>
        </div>
    </body>
    </html>
    """
    
    text_template = f"""
    {greeting}

    {personalized_message}

    We're thrilled to have you on board! You're now part of an exclusive group of early adopters who will be the first to experience Lemur when we launch.

    What happens next?
    • We'll keep you updated on our progress
    • You'll get early access when we launch
    • Exclusive updates and behind-the-scenes content
    • Priority support and feedback opportunities

    Thank you for your patience and support!
    The Lemur Team

    ---
    You received this email because you signed up for the Lemur waitlist.
    If you have any questions, feel free to reply to this email.
    """
    
    return {
        "subject": "Welcome to the Lemur Waitlist! 🎉",
        "html": html_template,
        "text": text_template
    }
