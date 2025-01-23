from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import base64
from email import encoders
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# Load environment variables from .env file
load_dotenv()


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Email Sender API!"}), 200


@app.route('/send-emails', methods=['POST'])
def send_emails():
    try:
        # Get data from request
        data = request.get_json()

        # Get sender email and password from environment variables
        sender_email = os.getenv("BULK_MAILER_EMAIL")
        app_password = os.getenv("BULK_MAILER_PASSWORD")

        # Get subject, content, and recipients from the request body
        subject = data['subject']
        content = data['content']
        recipients = data['recipients']  # Expecting an array of recipients
        resume_data = data['resume']  # Base64-encoded file content
        filename = data['filename']

        # Set up the SMTP server
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Create the SMTP server object
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, app_password)

        for recipient in recipients:
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = recipient
            message['Subject'] = subject

            # Attach the email content
            message.attach(MIMEText(content, 'plain'))

            if resume_data:
                # Decode the base64 file data
                resume_content = base64.b64decode(
                    resume_data.split(',')[1])  # Remove the 'data:' prefix

                # Create the MIMEBase object for the attachment
                resume_part = MIMEBase('application', 'octet-stream')
                resume_part.set_payload(resume_content)
                encoders.encode_base64(resume_part)

                # Add the correct header to specify the filename
                resume_part.add_header(
                    # Change 'resume.pdf' to the correct file name
                    'Content-Disposition', f"attachment; filename={filename}")

                # Attach the resume to the message
                message.attach(resume_part)

            # Send the email
            server.sendmail(sender_email, recipient, message.as_string())

        server.quit()
        return jsonify({"message": "Emails sent successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
