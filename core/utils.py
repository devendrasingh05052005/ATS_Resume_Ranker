# core/utils.py
import re
import docx
import PyPDF2
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from io import BytesIO

# Text Cleaning Function
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    stop_words = set(stopwords.words('english'))
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]
    return ' '.join(filtered_words)

# Resume Reading Function 
def read_resume_file(file):
    file_extension = file.name.split('.')[-1].lower()
    text = ""
    
    if file_extension == 'pdf':
        try:
            reader = PyPDF2.PdfReader(BytesIO(file.read()))
            for page in reader.pages:
                text += page.extract_text() or ""
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    
    elif file_extension == 'docx':
        try:
            doc = docx.Document(BytesIO(file.read()))
            for para in doc.paragraphs:
                text += para.text
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return None
            
    else:
        print(f"Unsupported file format: {file_extension}")
        return None
        
    return text

def get_resume_ranking(resume_file, job_description):
    resume_text = read_resume_file(resume_file)
    
    if not resume_text or not job_description:
        return 0.0
        
    cleaned_resume = clean_text(resume_text)
    cleaned_jd = clean_text(job_description)
    
    documents = [cleaned_resume, cleaned_jd]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents)
    
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    ranking_score = cosine_sim[0][0] * 100
    
    return ranking_score