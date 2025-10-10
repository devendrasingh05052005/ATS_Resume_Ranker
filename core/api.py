# core/api.py
import requests
import os

def fetch_adzuna_jobs(query, location):
    """
    Adzuna API se external jobs fetch karta hai.
    """
    # Aapke Adzuna credentials
    app_id = "e4e5c6a9"
    app_key = "cafef0355a622589ee75a5caa3247f24"

    if not app_id or not app_key:
        print("Error: Adzuna API credentials not found.")
        return []

    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        'app_id': app_id,
        'app_key': app_key,
        'what': query,
        'where': location,
        'results_per_page': 50,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Console mein poora JSON data print karein
        print("API Response:", data) 

        # Check karein ki API ne koi error message toh nahi bheja hai
        if data.get('error'):
            print(f"Adzuna API Error: {data.get('message')}")
            return []
            
        # Agar jobs hain, to unhein return karein
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return []