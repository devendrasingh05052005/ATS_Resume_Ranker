# resume_builder/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import render_to_string
from .forms import ResumeBuilderForm
import google.generativeai as genai
import os
import json
import re

'''-------------------------------------------------------------------------------------'''

genai.configure(api_key="AIzaSyC3ngxiYZ67yopEwodhDAo37NICOP-yHZo")

'''-------------------------------------------------------------------------------------'''

def get_ai_suggestions_from_gemini(job_title):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Please generate 5 detailed and professional bullet points for a resume for a {job_title}. 
    Each bullet point should be concise and start with an action verb.
    Please return the result as a simple list, with each bullet point separated by a newline.
    Do not add any headings or extra text, just the bullet points.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.split('\n')
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return []
    
'''-------------------------------------------------------------------------------------'''

def choose_template(request):
    templates = [
        {'id': 1, 'name': 'Classic Professional', 'image': 'resume1.png'},
        {'id': 2, 'name': 'Modern Minimalist', 'image': 'resume2.png'},
        {'id': 3, 'name': 'Creative & Bold', 'image': 'resume3.png'},
        {'id': 4, 'name': 'Technical Focus', 'image': 'resume4.png'},
        {'id': 5, 'name': 'Simple Layout', 'image': 'resume5.png'}
    ]
    return render(request, 'resume_builder/choose_template.html', {'templates': templates})

'''-------------------------------------------------------------------------------------'''

def resume_builder(request, template_id):
    form = ResumeBuilderForm(request.POST or None)
    ai_suggestions = []
    form_data = request.session.get('form_data', {})


    if request.method == 'POST':
        form = ResumeBuilderForm(request.POST)
        if form.is_valid():
            if 'download_resume' in request.POST:
                request.session['form_data'] = form.cleaned_data
                request.session['template_id'] = template_id
                return download_resume(request)

            if 'get_suggestions' in request.POST:
                job_title = form.cleaned_data['target_job_title']
                if job_title:
                    ai_suggestions = get_ai_suggestions_from_gemini(job_title)

                request.session['form_data'] = form.cleaned_data
                request.session['ai_suggestions'] = ai_suggestions
                request.session['template_id'] = template_id

        else:
            form = ResumeBuilderForm(initial=request.session.get('form_data'))
            ai_suggestions = request.session.get('ai_suggestions', [])
    
    context = {
        'form': form,
        'ai_suggestions': ai_suggestions,
        'template_id': template_id
    }
    return render(request, 'resume_builder/resume_builder.html', context)

'''-------------------------------------------------------------------------------------'''

def download_resume(request):
    form_data = request.session.get('form_data', {})
    ai_suggestions = request.session.get('ai_suggestions', [])
    template_id = request.session.get('template_id', 1)

    context = {
        'full_name': form_data.get('full_name'),
        'email': form_data.get('email'),
        'phone_number': form_data.get('phone_number'),
        'target_job_title': form_data.get('target_job_title'),
        'work_experience': form_data.get('work_experience'),
        'education': form_data.get('education'),
        'skills': form_data.get('skills'),
        'ai_suggestions': ai_suggestions
    }

    template_name = f"resume_builder/resume_template_{template_id}.html"
    rendered_html = render_to_string(template_name, context)

    response = HttpResponse(rendered_html, content_type='text/html')
    response['Content-Disposition'] = 'attachment; filename=\"resume.html\"'
    return response

'''-------------------------------------------------------------------------------------'''