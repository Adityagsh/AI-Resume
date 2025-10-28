import requests
import json
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class JobAPI:
    def __init__(self):
        # Using free job APIs
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID', 'demo')
        self.adzuna_api_key = os.getenv('ADZUNA_API_KEY', 'demo')
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY', '')

    def search_jobs(self, job_title: str, location: str = "", experience_level: str = "") -> List[Dict]:
        """Search for jobs using multiple free APIs"""
        jobs = []
        
        # Try Adzuna
        jobs.extend(self._search_adzuna(job_title, location))

        # Try JSearch (RapidAPI)
        jobs.extend(self._search_jsearch(job_title, location))

        # Try Remotive (Remote jobs, free)
        jobs.extend(self._search_remotive(job_title))

        # Try Arbeitnow (General job board API)
        jobs.extend(self._search_arbeitnow(job_title, location))

        # If no results, return mock data for demo
        if not jobs:
            jobs = self._get_mock_jobs(job_title, location)

        return jobs[:20]  # Limit to 20 results

    # ------------------ API Implementations ------------------

    def _search_adzuna(self, job_title: str, location: str) -> List[Dict]:
        """Search jobs using Adzuna API"""
        try:
            url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
            params = {
                'app_id': self.adzuna_app_id,
                'app_key': self.adzuna_api_key,
                'what': job_title,
                'where': location,
                'results_per_page': 10,
                'sort_by': 'relevance'
            }
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for job in data.get('results', []):
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', {}).get('display_name', ''),
                        'location': job.get('location', {}).get('display_name', ''),
                        'salary': self._format_salary(job.get('salary_min'), job.get('salary_max')),
                        'description': job.get('description', ''),
                        'url': job.get('redirect_url', ''),
                        'source': 'Adzuna'
                    })
                return jobs
        except Exception as e:
            print(f"Adzuna API error: {e}")
        return []

    def _search_jsearch(self, job_title: str, location: str) -> List[Dict]:
        """Search jobs using JSearch API (RapidAPI)"""
        try:
            if not self.rapidapi_key:
                return []
            
            url = "https://jsearch.p.rapidapi.com/search"
            querystring = {
                "query": f"{job_title} {location}",
                "page": "1",
                "num_pages": "1"
            }
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
            }
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for job in data.get('data', []):
                    jobs.append({
                        'title': job.get('job_title', ''),
                        'company': job.get('employer_name', ''),
                        'location': f"{job.get('job_city', '')}, {job.get('job_state', '')}",
                        'salary': job.get('job_salary', 'Not specified'),
                        'description': job.get('job_description', ''),
                        'url': job.get('job_apply_link', ''),
                        'source': 'JSearch'
                    })
                return jobs
        except Exception as e:
            print(f"JSearch API error: {e}")
        return []

    def _search_remotive(self, job_title: str) -> List[Dict]:
        """Search jobs using Remotive API (Free, No Auth)"""
        try:
            url = "https://remotive.com/api/remote-jobs"
            params = {"search": job_title}
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for job in data.get("jobs", []):
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company_name', ''),
                        'location': job.get('candidate_required_location', ''),
                        'salary': job.get('salary', 'Not specified'),
                        'description': job.get('description', ''),
                        'url': job.get('url', ''),
                        'source': 'Remotive'
                    })
                return jobs
        except Exception as e:
            print(f"Remotive API error: {e}")
        return []

    def _search_arbeitnow(self, job_title: str, location: str) -> List[Dict]:
        """Search jobs using Arbeitnow Job Board API"""
        try:
            url = "https://arbeitnow.com/api/job-board-api"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for job in data.get("data", []):
                    title = job.get('title', '')
                    if job_title.lower() in title.lower():
                        jobs.append({
                            'title': title,
                            'company': job.get('company_name', ''),
                            'location': job.get('location', ''),
                            'salary': 'Not specified',
                            'description': job.get('description', ''),
                            'url': job.get('url', ''),
                            'source': 'Arbeitnow'
                        })
                return jobs
        except Exception as e:
            print(f"Arbeitnow API error: {e}")
        return []

    # ------------------ Helpers ------------------

    def _get_mock_jobs(self, job_title: str, location: str) -> List[Dict]:
        """Return mock job data for demonstration"""
        mock_jobs = [
            {
                'title': f'Senior {job_title}',
                'company': 'TechCorp Inc.',
                'location': location or 'Remote',
                'salary': '$80,000 - $120,000',
                'description': f'We are looking for an experienced {job_title} to join our dynamic team.',
                'url': 'https://example.com/job1',
                'source': 'Demo'
            },
            {
                'title': f'Junior {job_title}',
                'company': 'StartupXYZ',
                'location': location or 'New York, NY',
                'salary': '$60,000 - $80,000',
                'description': f'Entry-level {job_title} position perfect for fresh graduates.',
                'url': 'https://example.com/job2',
                'source': 'Demo'
            }
        ]
        return mock_jobs

    def _format_salary(self, min_salary, max_salary):
        """Format salary range"""
        if min_salary and max_salary:
            return f"${min_salary:,.0f} - ${max_salary:,.0f}"
        elif min_salary:
            return f"${min_salary:,.0f}+"
        elif max_salary:
            return f"Up to ${max_salary:,.0f}"
        else:
            return "Not specified"

    def get_job_trends(self, job_title: str) -> Dict:
        """Get job market trends (mock data for demo)"""
        return {
            'average_salary': '$85,000',
            'job_growth': '+15%',
            'top_skills': ['Python', 'JavaScript', 'SQL', 'AWS'],
            'top_locations': ['San Francisco', 'New York', 'Remote'],
            'companies_hiring': ['Google', 'Microsoft', 'Amazon', 'Meta', 'Apple']
        }


# ------------------ Quick Test ------------------
if __name__ == "__main__":
    api = JobAPI()
    results = api.search_jobs("Python Developer", "Remote")
    for job in results:
        print(job["title"], "-", job["company"], "-", job["source"])
