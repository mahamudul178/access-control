from django.db import models


class AccessLog(models.Model):
    """
    AccessLog model that records door access events.
    """
    card_id = models.CharField(
        max_length=50,
        help_text="Unique card ID (e.g., C1001)"
    )
    
    door_name = models.CharField(
        max_length=100,
        help_text="Door name (e.g., Main Entrance)"
    )
    
    access_granted = models.BooleanField(
        default=True,
        help_text="Access granted (True) or denied (False)"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the event occurred"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Time when the database entry was created"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Access Log'
        verbose_name_plural = 'Access Logs'
        indexes = [
            models.Index(fields=['card_id']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        status = "GRANTED" if self.access_granted else "DENIED"
        return f"{self.card_id} - {self.door_name} ({status}) at {self.timestamp}"
