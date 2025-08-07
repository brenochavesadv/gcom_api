
from tasks.celery import celery
import time

@celery.task
def send_email_task(email: str):
    time.sleep(1)  # simula envio
    return f"E-mail enviado para {email}"
