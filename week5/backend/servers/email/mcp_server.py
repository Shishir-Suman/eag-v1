# basic import 
from mcp.server.fastmcp import FastMCP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# instantiate an MCP server client
mcp = FastMCP("EmailSender") 

# DEFINE TOOLS

@mcp.tool()
def send_email_with_app_password(receiver: str, subject: str, body: str) -> str:
    """
    Send an email with the specified subject and body.

    Args:
        subject (str): Subject of the email.
        body (str): Body content of the email.

    Returns:
        str: A success message if the email was sent successfully, or an error message if an exception occurred.
    """
    try:
        # Create email message
        message = MIMEMultipart()
        message["From"] = os.getenv("SENDER_EMAIL")
        message["To"] = receiver
        message["Subject"] = subject
        
        # Add body to email
        message.attach(MIMEText(body, "plain"))
        
        # Connect to Gmail's SMTP server
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()  # Secure the connection
            server.ehlo()
            
            # Login with app password
            server.login(os.getenv("SENDER_EMAIL"), os.getenv("GMAIL_APP_PASSWORD"))
                
            # Send email
            server.send_message(message)
            
        return "Email sent successfully"
    except Exception as e:
        return f"Error sending email: {e}"


if __name__ == "__main__":
    # run the server
    mcp.run()