# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CandidateSignUpForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from .forms import CandidateSignUpForm, JobPostingForm, ApplicationForm , LoginForm
from .models import Job, Application, JobField
from .api import fetch_adzuna_jobs 
from django.db.models import Count
from .utils import get_resume_ranking 
import fitz # PyMuPDF
import requests, os
from django.contrib import messages
import google.generativeai as genai
'''-----------------------------------------------------------------------------------------------'''
genai.configure(api_key="AIzaSyC3ngxiYZ67yopEwodhDAo37NICOP-yHZo")
'''-----------------------------------------------------------------------------------------------'''

def candidate_signup(request):
    if request.method == 'POST':
        form = CandidateSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_candidate = True
            user.save()
            return redirect('login') 
    else:
        form = CandidateSignUpForm()
    return render(request, 'core/signup.html', {'form': form})

'''-----------------------------------------------------------------------------------------------'''

def chatbot_response(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        user_message = request.POST.get('message')
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        prompt = f"""You are an AI career assistant. Your goal is to provide helpful and concise advice to job seekers.
        A candidate has a question for you: "{user_message}".
        Please provide a professional and direct answer.
        """
        try:
            response = model.generate_content(prompt)
            ai_response = response.text
            return JsonResponse({'response': ai_response})
        except Exception as e:
            print(f"Gemini API call failed: {e}")
            return JsonResponse({'error': 'Sorry, I am unable to respond at the moment.'}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

'''-----------------------------------------------------------------------------------------------'''

@login_required
def dashboard(request):
    if request.user.is_candidate:
        return redirect('candidate_dashboard')
    elif request.user.is_recruiter:
        return redirect('recruiter_dashboard')
    else:
        return redirect('home')

'''-----------------------------------------------------------------------------------------------'''

@login_required
def candidate_dashboard(request):
    if not request.user.is_candidate:
        return redirect('dashboard')

    query = request.GET.get('query', '')
    location = request.GET.get('location', '')
    
    internal_jobs = Job.objects.filter(is_internal=True)
    external_jobs = []

    if query:
        try:
            external_jobs_data = fetch_adzuna_jobs(query, location)
            for job_data in external_jobs_data:
                external_jobs.append({
                    'title': job_data['title'],
                    'description': job_data['description'],
                    'external_url': job_data['redirect_url']
                })
        except requests.exceptions.RequestException as e:
            messages.error(request, f"API call failed. Please check your internet connection or API credentials.")
            print(f"API call failed with error: {e}") 
    
    my_applications = Application.objects.filter(candidate=request.user)

    context = {
        'internal_jobs': internal_jobs,
        'external_jobs': external_jobs,
        'my_applications': my_applications,
        'query': query,
        'location': location,
    }
    return render(request, 'core/candidate_dashboard.html', context)
def generate_job_description(job_title):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    prompt = f"Write a detailed and professional job description for the role of a {job_title}. The description should include responsibilities, qualifications, and company information. The length should be around 250-300 words. Return only the job description content."
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return "Could not generate job description. Please try again."

'''-----------------------------------------------------------------------------------------------'''

@login_required
def recruiter_dashboard(request):
    if not request.user.is_recruiter:
        return redirect('dashboard')
    
    recruiter_jobs = Job.objects.filter(recruiter=request.user)

    total_applications = Application.objects.filter(job__in=recruiter_jobs).count()

    shortlisted = Application.objects.filter(job__in=recruiter_jobs, status='shortlisted').count()
    rejected = Application.objects.filter(job__in=recruiter_jobs, status='rejected').count()

    context = {
        'jobs': recruiter_jobs,
        'total_applications': total_applications,
        'shortlisted': shortlisted,
        'rejected': rejected,
    }
    return render(request, 'core/recruiter_dashboard.html', context)

'''-----------------------------------------------------------------------------------------------'''

@login_required
def post_job(request):
    generated_jd = None
    if request.method == 'POST':
        if 'generate_jd' in request.POST:
            job_title = request.POST.get('title', '')
            if job_title:
                generated_jd = generate_job_description(job_title)
                form = JobPostingForm(initial={'title': job_title, 'description': generated_jd})
                messages.success(request, "Job Description generated successfully!")
            else:
                form = JobPostingForm(request.POST)
                messages.error(request, "Please enter a job title first.")
        else:
            form = JobPostingForm(request.POST)
            if form.is_valid():
                job = form.save(commit=False)
                job.recruiter = request.user
                job.save()
                return redirect('recruiter_dashboard')
    else:
        form = JobPostingForm()

    return render(request, 'core/post_job.html', {'form': form, 'generated_jd': generated_jd})

'''-----------------------------------------------------------------------------------------------'''

@login_required
def apply_for_job(request, job_id):
    if not request.user.is_candidate:
        return redirect('dashboard')
        
    job = get_object_or_404(Job, id=job_id, is_internal=True)
    
    if Application.objects.filter(candidate=request.user, job=job).exists():
        messages.info(request, "Aap is job par pehle hi apply kar chuke hain.")
        return redirect('candidate_dashboard')

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume']
            job_description = job.description
            
            ranking_score = get_resume_ranking(resume_file, job_description)
            
            if ranking_score is None:
                messages.error(request, "Resume file read nahi ho payi. Kripya sahi format mein file upload karein.")
                return redirect('apply_for_job', job_id=job.id)

            application = form.save(commit=False)
            application.candidate = request.user
            application.job = job
            application.ranking_score = ranking_score
            application.save()
            
            messages.success(request, "Aapka application safal ho gaya hai!")
            return redirect('candidate_dashboard')
    else:
        form = ApplicationForm()
        
    return render(request, 'core/apply_for_job.html', {'form': form, 'job': job})

def home(request):
    return render(request, 'core/home.html')

'''-----------------------------------------------------------------------------------------------'''

@login_required
def recruiter_job_applications(request, job_id):
    if not request.user.is_recruiter:
        return redirect('dashboard')
    
    job = get_object_or_404(Job, id=job_id, recruiter=request.user)
    
    applications = Application.objects.filter(job=job).order_by('-ranking_score')
    
    return render(request, 'core/recruiter_job_applications.html', {'job': job, 'applications': applications})

'''-----------------------------------------------------------------------------------------------'''

@login_required
def shortlist_application(request, app_id):
    if not request.user.is_recruiter:
        return redirect('dashboard')
    
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    
    application.status = 'Shortlisted'
    application.save()
    
    messages.success(request, f"{application.candidate.username} has been shortlisted.")
    return redirect('recruiter_job_applications', job_id=application.job.id)

'''-----------------------------------------------------------------------------------------------'''

def candidate_login(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_candidate and not user.is_recruiter:
                auth_login(request, user)
                return redirect('candidate_dashboard')
            else:
                messages.error(request, "Invalid login credentials for a candidate.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

'''-----------------------------------------------------------------------------------------------'''

def recruiter_login(request):
    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_recruiter and not user.is_candidate:
                auth_login(request, user)
                return redirect('recruiter_dashboard')
            else:
                messages.error(request, "Invalid login credentials for a recruiter.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

'''-----------------------------------------------------------------------------------------------'''

@login_required
def reject_application(request, app_id):
    if not request.user.is_recruiter:
        return redirect('dashboard')
    
    application = get_object_or_404(Application, id=app_id, job__recruiter=request.user)
    
    application.status = 'Rejected'
    application.save()
    
    messages.success(request, f"{application.candidate.username} has been rejected.")
    return redirect('recruiter_job_applications', job_id=application.job.id)

'''-----------------------------------------------------------------------------------------------'''