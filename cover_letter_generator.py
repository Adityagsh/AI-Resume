from groq import Groq
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class CoverLetterGenerator:
    def __init__(self, groq_api_key=None):
        self.groq_client = Groq(
            api_key=groq_api_key or os.getenv('GROQ_API_KEY')
        )
        self.model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
    
    def generate_cover_letter(self, resume_text: str, job_description: str, 
                            company_name: str, position: str, tone: str = "professional") -> str:
        """Generate AI-powered cover letter"""
        try:
            prompt = f"""
Write a compelling cover letter for the following job application:

RESUME SUMMARY:
{resume_text[:1000]}

JOB DESCRIPTION:
{job_description[:1000]}

DETAILS:
- Company: {company_name}
- Position: {position}
- Tone: {tone}
- Date: {datetime.now().strftime("%B %d, %Y")}

REQUIREMENTS:
1. Professional format with proper structure
2. Highlight relevant experience from resume that matches job requirements
3. Show enthusiasm for the company and role
4. Keep it concise (3-4 paragraphs)
5. Use {tone} tone throughout
6. Include specific examples from resume
7. End with strong call to action

Format the cover letter properly with:
- Date
- Company address placeholder
- Proper salutation
- Body paragraphs
- Professional closing
"""
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert cover letter writer. Create compelling, personalized cover letters that highlight the candidate's strengths and match them to job requirements. Use a {tone} tone."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._get_fallback_cover_letter(company_name, position, tone)
    
    def _get_fallback_cover_letter(self, company_name: str, position: str, tone: str) -> str:
        """Fallback cover letter template"""
        date = datetime.now().strftime("%B %d, %Y")
        
        return f"""{date}

Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company_name}. With my background in technology and proven track record of delivering results, I am confident that I would be a valuable addition to your team.

In my previous roles, I have developed strong technical skills and gained experience in problem-solving, project management, and team collaboration. I am particularly drawn to {company_name} because of your reputation for innovation and commitment to excellence. The {position} role aligns perfectly with my career goals and expertise.

I am excited about the opportunity to contribute to your team's success and would welcome the chance to discuss how my skills and experience can benefit {company_name}. I have attached my resume for your review and look forward to hearing from you soon.

Thank you for your time and consideration.

Sincerely,
[Your Name]

---
Note: This is a template cover letter. For a more personalized version, please ensure your Groq API key is properly configured.
"""
    
    def generate_multiple_versions(self, resume_text: str, job_description: str, 
                                 company_name: str, position: str) -> dict:
        """Generate multiple cover letter versions with different tones"""
        versions = {}
        tones = ["professional", "enthusiastic", "creative"]
        
        for tone in tones:
            try:
                cover_letter = self.generate_cover_letter(
                    resume_text, job_description, company_name, position, tone
                )
                versions[tone] = cover_letter
            except Exception as e:
                print(f"Error generating {tone} version: {e}")
                versions[tone] = self._get_fallback_cover_letter(company_name, position, tone)
        
        return versions
    
    def customize_for_industry(self, base_cover_letter: str, industry: str) -> str:
        """Customize cover letter for specific industry"""
        try:
            prompt = f"""
Customize this cover letter for the {industry} industry:

ORIGINAL COVER LETTER:
{base_cover_letter}

REQUIREMENTS:
1. Add industry-specific terminology and keywords
2. Highlight relevant skills for {industry}
3. Show understanding of industry trends and challenges
4. Maintain the original structure and tone
5. Keep the same length

Return the customized cover letter.
"""
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"You are an expert in {industry} industry recruitment. Customize cover letters to highlight industry-relevant skills and knowledge."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=800,
                temperature=0.2
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Industry customization error: {e}")
            return base_cover_letter