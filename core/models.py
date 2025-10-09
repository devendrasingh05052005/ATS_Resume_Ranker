# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Ek custom user model jo is_candidate aur is_recruiter fields add karta hai.
    """
    is_candidate = models.BooleanField(default=False)
    is_recruiter = models.BooleanField(default=False)



class JobField(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    recruiter = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'is_recruiter': True}
    )
    is_internal = models.BooleanField(default=True)
    external_url = models.URLField(blank=True, null=True)
    job_field = models.ForeignKey(JobField, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title
    




class Application(models.Model):
    candidate = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'is_candidate': True}
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.FileField(upload_to='resumes/')
    # Status ke options
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Screening', 'Screening'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    ranking_score = models.FloatField(default=0.0) 

    def __str__(self):
        return f"Application by {self.candidate.username} for {self.job.title}"