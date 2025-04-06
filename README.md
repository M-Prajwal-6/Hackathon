Overview
An intelligent web application that suggests IT career paths based on user skills, combining traditional dataset matching with AI-powered recommendations.

Key Features
💡 Skill-based job matching

🤖 AI recommendations via Google Gemini

📊 Dataset-driven job analysis

📱 Modern UI with Tailwind CSS

🎓 Learning resource suggestions

Tech Stack
Backend: Python Flask
AI: Google Gemini AI
Frontend: Tailwind CSS, JavaScript
Data: CSV Database
UI Components: Font Awesome
Core Functions
1. Dataset Matching
   def process_dataset_jobs(user_skills):
    """
    Matches user skills against IT job database
    Returns: List of matching jobs with descriptions
    """
2. AI Recommendations
   def get_ai_job_suggestions(user_skills, existing_titles):
    """
    Generates AI-powered career suggestions
    Returns: List of AI-recommended jobs
    """
3. Job Description Generation
   def get_ai_job_description(job_title, matched_skills):
    """
    Creates custom job descriptions using AI
    Falls back to templates if AI unavailable
    """
   Features
Skill Analysis

Multiple skill input support
Fuzzy matching
Real-time validation
Job Matching

Dataset-based matching
Skill gap analysis
Certification recommendations
AI Integration

Custom job suggestions
Dynamic descriptions
Intelligent skill mapping
User Interface

Responsive design
Loading states
Error handling
Setup
   git clone <repo-url>
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"
python test.py
Environment Variables
DATASET_PATH: Path to job dataset
GEMINI_API_KEY: Google Gemini API key

Project Structure
   ai-career-coach/
├── test.py                      # Main application

├── requirements.txt             # Dependencies

└── IT_Job_Roles_Skills_Dataset.csv  # Job database

API Usage:
  API_KEY = "your-gemini-api-key"
MODEL_NAME = "gemini-2.0-flash"

Contributing
Fork repository
Create feature branch
Submit pull request
