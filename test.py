import os
from flask import Flask, request, render_template_string, jsonify
import pandas as pd
import logging
from functools import lru_cache
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Try to import Google's genai library, but handle missing dependencies
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    logger.warning("Google GenerativeAI library not available. Install with: pip install google-generativeai")
    GENAI_AVAILABLE = False

# Sample dataset as fallback if CSV isn't found
SAMPLE_DATASET = [
    {
        "Job Title": "Python Developer", 
        "Skills": "python, django, flask, sql, git",
        "Job Description": "Develops and maintains software applications using Python programming language.",
        "Certifications": "Python Institute Certification (PCEP, PCAP)"
    },
    {
        "Job Title": "Data Scientist", 
        "Skills": "python, pandas, numpy, scikit-learn, tensorflow, statistics",
        "Job Description": "Analyzes data to extract insights and develop ML models.",
        "Certifications": "IBM Data Science, Microsoft Certified: Azure Data Scientist Associate"
    },
    {
        "Job Title": "DevOps Engineer", 
        "Skills": "python, aws, docker, kubernetes, jenkins, linux",
        "Job Description": "Manages CI/CD pipelines and cloud infrastructure.",
        "Certifications": "AWS Certified DevOps Engineer, Docker Certified Associate"
    },
    {
        "Job Title": "Full Stack Developer", 
        "Skills": "python, javascript, react, node.js, html, css, mongodb",
        "Job Description": "Creates both frontend and backend components of web applications.",
        "Certifications": "MongoDB Developer and DBA Certification"
    },
    {
        "Job Title": "AI Engineer", 
        "Skills": "python, tensorflow, pytorch, computer vision, nlp",
        "Job Description": "Develops AI solutions and deep learning models.",
        "Certifications": "Google TensorFlow Developer Certificate, NVIDIA Deep Learning Institute"
    }
]

# API Key for Gemini
API_KEY = "AIzaSyCB2wPfq7uHAHfkW43us0wOHKHpPHdn3Xc"
MODEL_NAME = "gemini-2.0-flash"

def initialize_genai():
    """Initialize the Google GenerativeAI client if available"""
    if GENAI_AVAILABLE:
        try:
            genai.configure(api_key=API_KEY)
            logger.info("Google GenerativeAI initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google GenerativeAI: {e}")
            return False
    return False

@lru_cache(maxsize=1)
def load_dataset():
    """Load dataset from CSV or use fallback sample data"""
    try:
        # Try multiple possible locations for the dataset
        possible_paths = [
            os.getenv("DATASET_PATH", "IT_Job_Roles_Skills_Dataset.csv"),  # Environment variable or current directory
            r"C:\Users\naikv\OneDrive\Desktop\hackathon\IT_Job_Roles_Skills_Dataset.csv",  # Original path
            os.path.join(os.path.dirname(__file__), "IT_Job_Roles_Skills_Dataset.csv"),  # Same directory as script
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "IT_Job_Roles_Skills_Dataset.csv")  # Absolute path
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Loading dataset from: {path}")
                df = pd.read_csv(path)
                df["Skills"] = df["Skills"].fillna("").astype(str).str.lower()
                return df
        
        # If no file found, use the sample dataset
        logger.warning("Dataset file not found, using sample data")
        df = pd.DataFrame(SAMPLE_DATASET)
        df["Skills"] = df["Skills"].fillna("").astype(str).str.lower()
        return df
    
    except Exception as e:
        logger.error(f"Error loading dataset: {e}")
        # Return a dataframe with sample data as fallback
        logger.warning("Using sample data due to dataset loading error")
        return pd.DataFrame(SAMPLE_DATASET)

def generate_simple_ai_description(job_title, skills):
    """Generate a simple job description without using the API"""
    skills_text = ", ".join(skills) if skills else "various IT skills"
    return f"A {job_title} role focusing on {skills_text}."

def get_ai_job_description(job_title, matched_skills):
    """Generate a job description using AI if available, otherwise use a template"""
    if not GENAI_AVAILABLE or not initialize_genai():
        return generate_simple_ai_description(job_title, matched_skills)
    
    skills_text = ", ".join(matched_skills) if matched_skills else "various IT skills"
    
    try:
        # Try the newer API format first
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(
            f"Write a concise 1-2 sentence job description for a '{job_title}' role that requires {skills_text}."
        )
        return response.text
    except AttributeError:
        # Fall back to alternate API format if available
        try:
            response = genai.generate_text(
                model=MODEL_NAME,
                prompt=f"Write a concise 1-2 sentence job description for a '{job_title}' role that requires {skills_text}."
            )
            return response.text
        except Exception as e:
            logger.error(f"AI text generation error: {e}")
            return generate_simple_ai_description(job_title, matched_skills)
    except Exception as e:
        logger.error(f"AI Generation error: {e}")
        return generate_simple_ai_description(job_title, matched_skills)

def generate_ai_suggestions(user_skills):
    """Generate AI job suggestions without API calls"""
    # This is a fallback function when the AI API isn't available
    
    # Sample job templates that can be customized based on user skills
    job_templates = [
        {
            "title_prefix": "Senior",
            "skills_required": ["python", "javascript", "react", "node.js"],
            "certifications": "AWS Certified Developer, Professional Scrum Developer"
        },
        {
            "title_prefix": "Junior",
            "skills_required": ["html", "css", "javascript", "python"],
            "certifications": "CompTIA A+, Microsoft MTA"
        },
        {
            "title_prefix": "Lead",
            "skills_required": ["project management", "agile", "scrum", "leadership"],
            "certifications": "PMP, Certified ScrumMaster"
        },
        {
            "title_prefix": "Cloud",
            "skills_required": ["aws", "azure", "docker", "kubernetes"],
            "certifications": "AWS Solutions Architect, Microsoft Azure Administrator"
        },
        {
            "title_prefix": "Data",
            "skills_required": ["sql", "python", "pandas", "tableau"],
            "certifications": "Microsoft Certified: Data Analyst Associate, Tableau Desktop Specialist"
        }
    ]
    
    # Base job titles that can be combined with prefixes
    base_titles = [
        "Developer", "Engineer", "Architect", "Specialist", "Analyst"
    ]
    
    # Generate suggestions based on user skills
    suggestions = []
    
    for template in job_templates:
        # Check if the user has at least one skill from the template
        matched_skills = set(template["skills_required"]) & user_skills
        if not matched_skills:
            continue
            
        # Generate a job title
        for base in base_titles:
            title = f"{template['title_prefix']} {base}"
            
            # Skip if we already have this title
            if any(job["Job Title"] == title for job in suggestions):
                continue
                
            # All required skills for this job
            all_skills = set(template["skills_required"])
            
            # Create job suggestion
            job = {
                "Job Title": title,
                "Job Description": generate_simple_ai_description(title, matched_skills),
                "Matched Skills": ", ".join(sorted(matched_skills)),
                "Missing Skills": ", ".join(sorted(all_skills - user_skills)),
                "Certifications": template["certifications"]
            }
            
            suggestions.append(job)
            break  # Only use one base title per template
            
    return suggestions[:5]  # Return up to 5 suggestions

def get_ai_job_suggestions(user_skills, existing_titles):
    """Get AI job suggestions with certification platforms"""
    if not GENAI_AVAILABLE or not initialize_genai():
        logger.warning("AI API not available, using fallback job suggestions")
        return generate_ai_suggestions(user_skills)
    
    max_ai_jobs = 5
    skill_list = ", ".join(sorted(user_skills))
    
    prompt = (
        f"Suggest {max_ai_jobs} distinct IT jobs for skills: {skill_list}.\n"
        "Format each job on a new line as: Job Title | Required Skills (comma separated) | Certifications with Platforms (comma separated)\n"
        f"Avoid these titles: {', '.join(existing_titles)}.\n"
        "Include 3-5 skills and 1-2 certifications with provider platforms in parentheses per job."
    )
    
    logger.info(f"Generating AI job suggestions for skills: {skill_list}")
    
    try:
        # Try the newer API format first
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        ai_response = response.text
    except AttributeError:
        # Fall back to alternate API format if available
        try:
            response = genai.generate_text(
                model=MODEL_NAME,
                prompt=prompt
            )
            ai_response = response.text
        except Exception as e:
            logger.error(f"AI text generation error: {e}")
            return generate_ai_suggestions(user_skills)
    except Exception as e:
        logger.error(f"AI Generation error: {e}")
        return generate_ai_suggestions(user_skills)
    
    logger.info(f"Raw AI response: {ai_response}")
    
    ai_jobs = []
    for line in ai_response.split("\n"):
        line = line.strip()
        # Skip empty lines or numbered bullets
        if not line or (line[0].isdigit() and line[1:3] in ('. ', ') ')):
            line = line[3:].strip()  # Remove the bullet
            
        if not line or "|" not in line:
            continue
            
        try:
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) < 3:
                continue
                
            job_title, job_skills, job_certs = parts
            job_title = job_title.split("(")[0].strip()
            
            # Skip if job title already exists
            if job_title.lower() in (t.lower() for t in existing_titles):
                continue
                
            # Parse skills and match with user skills
            job_skills_list = {s.strip().lower() for s in job_skills.split(",") if s.strip()}
            matched_skills = user_skills & job_skills_list
            missing_skills = job_skills_list - user_skills
            
            # Generate job description
            job_desc = get_ai_job_description(job_title, matched_skills)
            
            ai_jobs.append({
                "Job Title": job_title,
                "Job Description": job_desc,
                "Matched Skills": ", ".join(sorted(matched_skills)) or "None",
                "Missing Skills": ", ".join(sorted(missing_skills)) or "None",
                "Certifications": job_certs
            })
            
            existing_titles.add(job_title)
            if len(ai_jobs) >= max_ai_jobs:
                break
                
        except Exception as e:
            logger.error(f"Error processing job suggestion: {e}")
            continue
    
    # If we couldn't get any valid jobs from the AI response, use our fallback
    if not ai_jobs:
        logger.warning("No valid AI job suggestions, using fallback generation")
        return generate_ai_suggestions(user_skills)
        
    logger.info(f"Generated {len(ai_jobs)} AI job suggestions")
    return ai_jobs

def process_dataset_jobs(user_skills):
    """Process dataset jobs with enhanced matching"""
    max_jobs = 5
    skills_threshold = 1
    
    try:
        df = load_dataset()
        results = []
        
        for _, row in df.iterrows():
            # Extract job skills from dataset
            job_skills_str = row.get("Skills", "").lower()
            job_skills = {skill.strip() for skill in job_skills_str.split(",") if skill.strip()}
            
            # Find matching skills
            matched_skills = job_skills & user_skills
            
            # Skip if no skills match
            if len(matched_skills) < skills_threshold:
                continue
                
            # Get missing skills
            missing_skills = job_skills - user_skills
            
            # Get job data
            job_title = row.get("Job Title", "Unknown Job")
            
            # Get or generate job description
            job_desc = row.get("Job Description", "")
            if pd.isna(job_desc) or not job_desc:
                job_desc = get_ai_job_description(job_title, matched_skills)
                
            # Get certifications
            certs = row.get("Certifications", "None")
            if pd.isna(certs):
                certs = "None"
                
            # Add to results
            results.append({
                "Job Title": job_title,
                "Job Description": job_desc,
                "Matched Skills": ", ".join(sorted(matched_skills)) or "None",
                "Missing Skills": ", ".join(sorted(missing_skills)) or "None",
                "Certifications": certs
            })
            
        # Sort by number of matched skills (descending)
        results.sort(key=lambda x: len(x["Matched Skills"].split(",")), reverse=True)
        
        logger.info(f"Found {len(results[:max_jobs])} matching jobs from dataset")
        return results[:max_jobs]
    
    except Exception as e:
        logger.error(f"Error processing dataset jobs: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def career_coach():
    if request.method == "GET":
        return render_template_string(HTML_TEMPLATE)
    
    skills_input = request.form.get("skills", "").lower()
    user_skills = {s.strip() for s in skills_input.split(",") if s.strip()}
    
    if not user_skills:
        return render_template_string(HTML_TEMPLATE, error="Please enter at least one skill")
    
    try:
        logger.info(f"Processing request for skills: {user_skills}")
        
        # Process dataset matches
        dataset_jobs = process_dataset_jobs(user_skills)
        existing_titles = {job["Job Title"] for job in dataset_jobs}
        
        # Generate AI suggestions
        ai_jobs = get_ai_job_suggestions(user_skills, existing_titles)
        
        return render_template_string(
            HTML_TEMPLATE,
            dataset_jobs=dataset_jobs,
            ai_jobs=ai_jobs,
            skills=skills_input
        )
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        return render_template_string(HTML_TEMPLATE, error=f"An error occurred while processing your request: {str(e)}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="h-full bg-gray-900">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Career Coach</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        /* Loading animation CSS */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulse-animation {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .spin-animation {
            animation: spin 1s linear infinite;
        }
    </style>
</head>
<body class="h-full">
    <div class="container mx-auto px-4 py-8 max-w-7xl">
        <!-- Header Section -->
        <header class="text-center mb-12">
            <h1 class="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent mb-4">
                AI Career Coach
            </h1>
            <form id="skillsForm" method="POST" class="max-w-2xl mx-auto">
                <div class="flex flex-col sm:flex-row gap-4">
                    <input type="text" name="skills" id="skillsInput" value="{{ skills }}" 
                           placeholder="Enter your skills (e.g., python, cloud computing, react)" 
                           class="flex-grow px-6 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white 
                                  focus:ring-2 focus:ring-green-500 focus:border-transparent">
                    <button type="submit" id="analyzeBtn"
                            class="px-8 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition-colors text-white">
                        <span id="btnText">Analyze Skills</span>
                        <i id="loadingIcon" class="fas fa-spinner spin-animation ml-2 hidden"></i>
                    </button>
                </div>
                {% if error %}
                <p class="text-red-400 mt-2 text-sm">{{ error }}</p>
                {% endif %}
            </form>
        </header>

        <!-- Main Results -->
        <main class="grid lg:grid-cols-2 gap-8">
            <!-- Dataset Matches -->
            <section id="datasetSection">
                <h2 class="text-2xl font-semibold mb-6 text-gray-300">
                    <i class="fas fa-database mr-2 text-blue-400"></i>Dataset Matches
                </h2>
                <div id="datasetResults" class="space-y-6">
                    {% if dataset_jobs %}
                        {% for job in dataset_jobs %}
                        <div class="bg-gray-800 rounded-xl p-6 shadow-lg">
                            <h3 class="text-xl font-bold text-green-400 mb-2">{{ job["Job Title"] }}</h3>
                            <p class="text-gray-300 mb-4">{{ job["Job Description"] }}</p>
                            <div class="space-y-2 text-sm">
                                <div class="flex items-start">
                                    <i class="fas fa-check-circle text-green-500 mr-2 mt-1"></i>
                                    <span class="font-medium text-gray-300">Matched Skills:</span>
                                    <span class="ml-2 text-gray-400">{{ job["Matched Skills"] }}</span>
                                </div>
                                <div class="flex items-start">
                                    <i class="fas fa-exclamation-triangle text-yellow-500 mr-2 mt-1"></i>
                                    <span class="font-medium text-gray-300">Missing Skills:</span>
                                    <span class="ml-2 text-gray-400">{{ job["Missing Skills"] }}</span>
                                </div>
                                <div class="flex items-start">
                                    <i class="fas fa-certificate text-blue-500 mr-2 mt-1"></i>
                                    <span class="font-medium text-gray-300">Certifications:</span>
                                    <span class="ml-2 text-gray-400">{{ job["Certifications"] }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div id="datasetLoading" class="hidden">
                            <div class="bg-gray-800 rounded-xl p-6 shadow-lg mb-4 pulse-animation">
                                <div class="h-6 bg-gray-700 rounded w-3/4 mb-4"></div>
                                <div class="h-4 bg-gray-700 rounded w-full mb-3"></div>
                                <div class="h-4 bg-gray-700 rounded w-5/6 mb-6"></div>
                                <div class="space-y-3">
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                </div>
                            </div>
                            <div class="bg-gray-800 rounded-xl p-6 shadow-lg pulse-animation">
                                <div class="h-6 bg-gray-700 rounded w-2/3 mb-4"></div>
                                <div class="h-4 bg-gray-700 rounded w-full mb-3"></div>
                                <div class="h-4 bg-gray-700 rounded w-3/4 mb-6"></div>
                                <div class="space-y-3">
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                </div>
                            </div>
                        </div>
                        <div id="datasetEmpty" class="bg-gray-800 rounded-xl p-6 shadow-lg text-center">
                            <p class="text-gray-400">No matching jobs found in dataset</p>
                        </div>
                    {% endif %}
                </div>
            </section>

            <!-- AI Recommendations -->
            <section id="aiSection">
                <h2 class="text-2xl font-semibold mb-6 text-gray-300">
                    <i class="fas fa-robot mr-2 text-purple-400"></i>AI Recommendations
                </h2>
                <div id="aiResults" class="space-y-6">
                    {% if ai_jobs %}
                        {% for job in ai_jobs %}
                        <div class="bg-gray-800 rounded-xl p-6 shadow-lg">
                            <h3 class="text-xl font-bold text-purple-400 mb-2">{{ job["Job Title"] }}</h3>
                            <p class="text-gray-300 mb-4">{{ job["Job Description"] }}</p>
                            <div class="space-y-2 text-sm">
                                <div class="flex items-start">
                                    <i class="fas fa-check-circle text-green-500 mr-2 mt-1"></i>
                                    <span class="font-medium text-gray-300">Matched Skills:</span>
                                    <span class="ml-2 text-gray-400">{{ job["Matched Skills"] }}</span>
                                </div>
                                <div class="flex items-start">
                                    <i class="fas fa-exclamation-triangle text-yellow-500 mr-2 mt-1"></i>
                                    <span class="font-medium text-gray-300">Missing Skills:</span>
                                    <span class="ml-2 text-gray-400">{{ job["Missing Skills"] }}</span>
                                </div>
                                <div class="flex items-start">
                                    <i class="fas fa-certificate text-blue-500 mr-2 mt-1"></i>
                                    <span class="font-medium text-gray-300">Certifications:</span>
                                    <span class="ml-2 text-gray-400">{{ job["Certifications"] }}</span>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div id="aiLoading" class="hidden">
                            <div class="bg-gray-800 rounded-xl p-6 shadow-lg mb-4 pulse-animation">
                                <div class="h-6 bg-gray-700 rounded w-1/2 mb-4"></div>
                                <div class="h-4 bg-gray-700 rounded w-full mb-3"></div>
                                <div class="h-4 bg-gray-700 rounded w-5/6 mb-6"></div>
                                <div class="space-y-3">
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                </div>
                            </div>
                            <div class="bg-gray-800 rounded-xl p-6 shadow-lg pulse-animation">
                                <div class="h-6 bg-gray-700 rounded w-3/5 mb-4"></div>
                                <div class="h-4 bg-gray-700 rounded w-full mb-3"></div>
                                <div class="h-4 bg-gray-700 rounded w-4/5 mb-6"></div>
                                <div class="space-y-3">
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                    <div class="h-3 bg-gray-700 rounded w-full"></div>
                                </div>
                            </div>
                        </div>
                        <div id="aiEmpty" class="bg-gray-800 rounded-xl p-6 shadow-lg text-center">
                            <p class="text-gray-400">No AI job recommendations available</p>
                        </div>
                    {% endif %}
                </div>
            </section>
        </main>

        <!-- Learning Resources -->
        <footer class="mt-16 border-t border-gray-700 pt-8">
            <h3 class="text-xl font-semibold text-gray-300 mb-6">
                <i class="fas fa-graduation-cap mr-2 text-blue-400"></i>Learning Resources
            </h3>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <a href="https://www.coursera.org" target="_blank" 
                   class="p-4 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors">
                    <div class="text-blue-400 text-2xl mb-2"><i class="fab fa-google"></i></div>
                    <span class="text-gray-300">Coursera</span>
                </a>
                <a href="https://www.udemy.com" target="_blank" 
                   class="p-4 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors">
                    <div class="text-purple-400 text-2xl mb-2"><i class="fab fa-udemy"></i></div>
                    <span class="text-gray-300">Udemy</span>
                </a>
                <a href="https://aws.amazon.com/certification" target="_blank" 
                   class="p-4 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors">
                    <div class="text-yellow-400 text-2xl mb-2"><i class="fab fa-aws"></i></div>
                    <span class="text-gray-300">AWS Training</span>
                </a>
                <a href="https://learn.microsoft.com" target="_blank" 
                   class="p-4 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors">
                    <div class="text-blue-300 text-2xl mb-2"><i class="fab fa-microsoft"></i></div>
                    <span class="text-gray-300">MS Learn</span>
                </a>
            </div>
        </footer>
    </div>

    <!-- JavaScript for loading animation and form handling -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('skillsForm');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const btnText = document.getElementById('btnText');
            const loadingIcon = document.getElementById('loadingIcon');
            const datasetLoading = document.getElementById('datasetLoading');
            const datasetEmpty = document.getElementById('datasetEmpty');
            const aiLoading = document.getElementById('aiLoading');
            const aiEmpty = document.getElementById('aiEmpty');
            
            form.addEventListener('submit', function(e) {
                // Only show loading states if there's input
                const skillsInput = document.getElementById('skillsInput').value.trim();
                if (!skillsInput) {
                    return; // Let the form submit normally if empty
                }
                
                // Disable the button and show loading state
                analyzeBtn.disabled = true;
                btnText.textContent = "Analyzing...";
                loadingIcon.classList.remove('hidden');
                
                // If we don't have results yet, show skeleton loaders
                if (!document.querySelector('#datasetResults > div:not(#datasetLoading):not(#datasetEmpty)')) {
                    datasetEmpty.classList.add('hidden');
                    datasetLoading.classList.remove('hidden');
                }
                
                if (!document.querySelector('#aiResults > div:not(#aiLoading):not(#aiEmpty)')) {
                    aiEmpty.classList.add('hidden');
                    aiLoading.classList.remove('hidden');
                }
            });
            
            // If we already have results (page refreshed with POST data), no need for skeleton loaders
            if (document.querySelector('#datasetResults > div:not(#datasetLoading):not(#datasetEmpty)')) {
                datasetLoading.classList.add('hidden');
                datasetEmpty.classList.add('hidden');
            }
            
            if (document.querySelector('#aiResults > div:not(#aiLoading):not(#aiEmpty)')) {
                aiLoading.classList.add('hidden');
                aiEmpty.classList.add('hidden');
            }
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    # Try to create a sample dataset file if it doesn't exist
    if not os.path.exists("IT_Job_Roles_Skills_Dataset.csv"):
        try:
            logger.info("Creating sample dataset file")
            sample_df = pd.DataFrame(SAMPLE_DATASET)
            sample_df.to_csv("IT_Job_Roles_Skills_Dataset.csv", index=False)
            logger.info("Sample dataset file created successfully")
        except Exception as e:
            logger.error(f"Failed to create sample dataset file: {e}")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
