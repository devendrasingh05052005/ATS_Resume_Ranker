#!/usr/bin/env python
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ats_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models import Job, JobField, Application

def wipe_database():
    print("=" * 60)
    print(" WARNING: This script will delete ALL database records!")
    print(" This includes Applications, Jobs, Job Fields, and Users.")
    print("=" * 60)
    
    # Check if run with --force, otherwise ask for confirmation
    if "--force" not in sys.argv:
        try:
            confirm = input("Are you sure you want to proceed? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Aborted. No changes were made.")
                return
        except KeyboardInterrupt:
            print("\nAborted.")
            return

    User = get_user_model()
    
    print("\n[1/4] Deleting all Applications...")
    app_count = Application.objects.all().count()
    Application.objects.all().delete()
    print(f"      Deleted {app_count} applications.")

    print("[2/4] Deleting all Jobs and Job Fields...")
    job_count = Job.objects.all().count()
    Job.objects.all().delete()
    field_count = JobField.objects.all().count()
    JobField.objects.all().delete()
    print(f"      Deleted {job_count} jobs and {field_count} job fields.")

    print("[3/4] Deleting all non-superuser accounts...")
    # Keep superusers so the admin panel remains accessible, delete regular users (candidates/recruiters)
    users_to_delete = User.objects.filter(is_superuser=False)
    user_count = users_to_delete.count()
    users_to_delete.delete()
    print(f"      Deleted {user_count} regular users.")
    
    # If the user wants to delete EVERYTHING including superusers, they can do so if they choose
    # User.objects.all().delete()

    print("[4/4] Optimizing database file...")
    # SQLite optimization (VACUUM)
    from django.db import connection
    if connection.vendor == 'sqlite':
        with connection.cursor() as cursor:
            cursor.execute("VACUUM;")
            
    print("\nDatabase wiped successfully!")
    print("=" * 60)

if __name__ == '__main__':
    wipe_database()
