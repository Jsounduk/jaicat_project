# services/job_search.py
import requests

class JobSearchService:
    def __init__(self):
        self.api_key = "YOUR_JOB_SEARCH_API_KEY"  # Replace with your API key

    def search_jobs(self, query):
        """Search for jobs based on the user's query"""
        url = f"https://jobs.api.com/search?query={query}&apikey={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            jobs = response.json()["jobs"]
            job_listings = [f"{job['title']} at {job['company']}" for job in jobs]
            return job_listings[:5]  # Return top 5 jobs
        else:
            return "Error fetching job listings"