from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Job, Application, JobField

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class CandidateSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'is_candidate')


class JobPostingForm(forms.ModelForm):
    job_field = forms.ModelChoiceField(queryset=JobField.objects.all(), empty_label="Select a job field")
    
    class Meta:
        model = Job
        fields = ['title', 'description', 'is_internal', 'external_url', 'job_field']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'external_url': forms.URLInput(attrs={'class': 'form-control'}),
        }



class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['resume']
