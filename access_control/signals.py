from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import AccessLog
import subprocess
import os
from datetime import datetime


def append_to_log_file(message):
    """
    Write log messages to the system_events.log file.
    """
    log_file = settings.LOG_FILE_PATH
    
    try:
        # Create the directory if it does not exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Write to the file (similar to using an echo command)
        with open(log_file, 'a') as f:
            f.write(message + '\n')
            
    except Exception as e:
        print(f"Error while writing to log file: {str(e)}")


@receiver(post_save, sender=AccessLog)
def access_log_created(sender, instance, created, **kwargs):
    """
    This signal is triggered when a new AccessLog is created.
    """
    if created:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "GRANTED" if instance.access_granted else "DENIED"
        
        log_message = (
            f"[{timestamp}] - CREATE: Access log created for card {instance.card_id}. "
            f"Door: {instance.door_name}. Status: {status}."
        )
        
        append_to_log_file(log_message)
        print(f"✓ Log created: {log_message}")


@receiver(post_delete, sender=AccessLog)
def access_log_deleted(sender, instance, **kwargs):
    """
    This signal is triggered when an AccessLog is deleted.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    log_message = (
        f"[{timestamp}] - DELETE: Access log (ID: {instance.id}) for card "
        f"{instance.card_id} was deleted."
    )
    
    append_to_log_file(log_message)
    print(f"✓ Log deleted: {log_message}")
