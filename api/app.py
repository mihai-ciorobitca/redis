from datetime import datetime
from redis import Redis
from rq_scheduler import Scheduler
from dotenv import load_dotenv
from os import getenv
from flask import Flask, request, jsonify, render_template
import smtplib
from email.mime.text import MIMEText
import logging

load_dotenv()

REDIS_URL = getenv('REDIS_URL')
EMAIL = getenv('EMAIL')
PASSWORD = getenv('PASSWORD')

app = Flask(__name__)

redis_conn = Redis.from_url(REDIS_URL)
scheduler = Scheduler(connection=redis_conn)

# Configure logging
logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def send_email():
    to = 'mihai.ciorobitca@networkstudio.store'
    body = f'Email sent at: {datetime.utcnow()}'
    msg = MIMEText(body)
    msg['Subject'] = 'Scheduled Email'
    msg['From'] = EMAIL
    msg['To'] = to

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        try:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.sendmail(EMAIL, to, msg.as_string())
            logger.info(f"Email sent to {to}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/schedule-job', methods=['POST'])
def schedule_job():
    cron_expression = request.form['cron']
    send_email()
    scheduler.cron(
        cron_expression,
        func=send_email,
        repeat=None,
        queue_name='default',
        id='email_job'
    )
    return jsonify({"message": f"Job scheduled with cron expression: {cron_expression}"})

@app.route('/cancel-job', methods=['POST'])
def cancel_job():
    scheduler.cancel('email_job')
    return jsonify({"message": "Job canceled"})
