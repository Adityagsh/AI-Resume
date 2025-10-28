import re
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ATSAnalyzer:
    def __init__(self, groq_api_key=None):
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except (LookupError, OSError, ConnectionError) as e:
            print(f"Warning: Could not download NLTK data: {e}")
        
        # Initialize Groq client
        self.groq_client = Groq(
            api_key=groq_api_key or os.getenv('GROQ_API_KEY')
        )
        self.model = os.getenv('GROQ_MODEL', 'llama3-8b-8192')
        
        # Common ATS-friendly keywords
        self.ats_keywords = [
            'experience', 'skills', 'education', 'projects', 'achievements',
            'responsibilities', 'managed', 'developed', 'implemented', 'created',
            'improved', 'increased', 'reduced', 'led', 'collaborated'
        ]
    
    def analyze_resume(self, resume_text):
        """Analyze resume and return ATS score with feedback"""
        score = 0
        feedback = []
        
        # Check basic structure (30 points)
        if self._has_contact_info(resume_text):
            score += 10
        else:
            feedback.append("Add clear contact information (email, phone)")
        
        if self._has_sections(resume_text):
            score += 10
        else:
            feedback.append("Include standard sections: Experience, Education, Skills")
        
        if self._has_quantified_achievements(resume_text):
            score += 10
        else:
            feedback.append("Add quantified achievements (numbers, percentages)")
        
        # Check keywords (40 points)
        keyword_score = self._calculate_keyword_score(resume_text)
        score += keyword_score
        if keyword_score < (40 * 0.75):
            feedback.append("Include more action verbs and industry keywords")
        
        # Check formatting (30 points)
        format_score = self._check_formatting(resume_text)
        score += format_score
        if format_score < 20:
            feedback.append("Improve formatting: use bullet points, consistent spacing")
        
        if not feedback:
            feedback.append("Great job! Your resume is ATS-friendly")
        
        return min(score, 100), feedback
    
    def match_job_description(self, resume_text, job_description):
        """Enhanced job description matching with comprehensive analysis"""
        if not job_description or len(job_description.strip()) < 50:
            return {
                'error': 'Please provide a detailed job description (at least 50 characters)',
                'match_score': 0,
                'missing_keywords': [],
                'suggestions': ['Add a comprehensive job description to get accurate analysis']
            }
        
        try:
            # Use TF-IDF to find similarity
            vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=1000)
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            match_score = int(similarity * 100)
        except Exception as e:
            return {
                'error': f'Analysis failed: {str(e)}. Please check your job description format.',
                'match_score': 0,
                'missing_keywords': [],
                'suggestions': ['Ensure job description contains readable text']
            }
        
        # Extract and analyze keywords
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_text.lower())
        missing_keywords = [kw for kw in job_keywords[:15] if kw not in resume_keywords]
        
        # Get comprehensive AI analysis
        analysis = self._get_comprehensive_analysis(resume_text, job_description, match_score)
        
        return {
            'match_score': match_score,
            'missing_keywords': missing_keywords,
            'suggestions': analysis['suggestions'],
            'improvements': analysis['improvements'],
            'strengths': analysis['strengths']
        }
    
    def _has_contact_info(self, text):
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        return bool(re.search(email_pattern, text)) and bool(re.search(phone_pattern, text))
    
    def _has_sections(self, text):
        sections = ['experience', 'education', 'skills', 'work', 'employment']
        return sum(1 for section in sections if section in text.lower()) >= 2
    
    def _has_quantified_achievements(self, text):
        number_pattern = r'\d+%|\d+\+|\$\d+|\d+k|\d+ years?|\d+ months?'
        return len(re.findall(number_pattern, text, re.IGNORECASE)) >= 3
    
    def _calculate_keyword_score(self, text):
        if not self.ats_keywords:
            return 0
        text_lower = text.lower()
        found_keywords = sum(1 for keyword in self.ats_keywords if keyword in text_lower)
        return min(int((found_keywords / len(self.ats_keywords)) * 40), 40)
    
    def _check_formatting(self, text):
        score = 30
        if len(text) < 200:
            score -= 10
        if text.count('\n') < 5:
            score -= 10
        if not re.search(r'[•\-\*]', text):
            score -= 10
        return max(score, 0)
    
    def _extract_keywords(self, text):
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Filter common words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        return [word for word in set(words) if word not in stop_words and len(word) > 3]
    
    def _get_comprehensive_analysis(self, resume_text, job_description, match_score):
        """Get comprehensive AI-powered analysis using Groq"""
        try:
            prompt = f"""
As an expert ATS and career coach, analyze this resume against the job description. Provide a comprehensive analysis:

Job Description:
{job_description[:1500]}

Resume:
{resume_text[:1500]}

Match Score: {match_score}%

Provide analysis in this exact format:

STRENGTHS:
- [List 2-3 key strengths]

IMPROVEMENTS:
- [List 3-4 specific improvements needed]

SUGGESTIONS:
- [List 4-5 actionable suggestions to increase match score]

Focus on specific, actionable advice that will improve ATS compatibility and job match.
"""
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert ATS specialist and career coach. Provide detailed, actionable resume optimization advice."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=600,
                temperature=0.2
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_analysis(analysis_text)
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._get_fallback_analysis(match_score)
    
    def _parse_analysis(self, analysis_text):
        """Parse AI analysis into structured format"""
        sections = {'strengths': [], 'improvements': [], 'suggestions': []}
        current_section = None
        
        for line in analysis_text.split('\n'):
            line = line.strip()
            if 'STRENGTHS:' in line.upper():
                current_section = 'strengths'
            elif 'IMPROVEMENTS:' in line.upper():
                current_section = 'improvements'
            elif 'SUGGESTIONS:' in line.upper():
                current_section = 'suggestions'
            elif line.startswith('-') and current_section:
                sections[current_section].append(line.strip('- '))
        
        # Ensure we have content in each section
        for key in sections:
            if not sections[key]:
                sections[key] = self._get_fallback_content(key)
        
        return sections
    
    def _get_fallback_content(self, section_type):
        """Fallback content for each section"""
        fallbacks = {
            'strengths': [
                "Resume contains relevant work experience",
                "Professional formatting and structure"
            ],
            'improvements': [
                "Add more quantified achievements with specific numbers",
                "Include more industry-specific keywords",
                "Strengthen technical skills section"
            ],
            'suggestions': [
                "Tailor experience descriptions to match job requirements",
                "Add relevant certifications or training",
                "Use action verbs that appear in the job description",
                "Include measurable results and impact statements"
            ]
        }
        return fallbacks.get(section_type, [])
    
    def _get_fallback_analysis(self, match_score):
        """Fallback analysis when AI is unavailable"""
        improvements = [
            "Add more quantified achievements (numbers, percentages, dollar amounts)",
            "Include industry-specific keywords from the job description",
            "Strengthen your technical skills section"
        ]
        
        if match_score < 60:
            improvements.extend([
                "Rewrite experience bullets to match job requirements",
                "Add relevant certifications or training"
            ])
        
        return {
            'strengths': [
                "Resume has professional structure",
                "Contains relevant work experience"
            ],
            'improvements': improvements,
            'suggestions': [
                "Use exact keywords from the job posting",
                "Quantify your achievements with specific metrics",
                "Tailor your summary to match the role",
                "Add relevant technical skills mentioned in the job description"
            ]
        }
    
    def generate_enhanced_resume(self, resume_text, target_score=90):
        """Generate AI-enhanced resume with higher ATS score"""
        try:
            prompt = f"""
As an expert resume writer and ATS specialist, enhance this resume to achieve a {target_score}% ATS score.

Original Resume:
{resume_text[:2000]}

Provide an enhanced version with:
1. Stronger action verbs
2. Quantified achievements
3. ATS-friendly keywords
4. Better formatting suggestions
5. Industry-specific terminology

Return the enhanced resume in the same structure but with improved content.
"""
            
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an expert resume writer specializing in ATS optimization. Enhance resumes while maintaining their original structure and truthfulness."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=1500,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._get_fallback_enhanced_resume(resume_text)
    
    def get_line_improvements(self, resume_text):
        """Get line-by-line improvement suggestions"""
        try:
            lines = resume_text.split('\n')
            improvements = []
            
            for i, line in enumerate(lines[:20], 1):  # Limit to first 20 lines
                if len(line.strip()) > 10:  # Only analyze substantial lines
                    prompt = f"""
Analyze this resume line and suggest ONE specific improvement:

Line {i}: "{line.strip()}"

Provide a brief, actionable suggestion to make it more ATS-friendly and impactful.
Format: "Suggestion: [your improvement]"
"""
                    
                    response = self.groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "You are an ATS expert. Provide one specific, actionable improvement per resume line."},
                            {"role": "user", "content": prompt}
                        ],
                        model=self.model,
                        max_tokens=100,
                        temperature=0.2
                    )
                    
                    suggestion = response.choices[0].message.content.replace("Suggestion: ", "")
                    improvements.append({
                        'line_number': i,
                        'original': line.strip(),
                        'suggestion': suggestion
                    })
            
            return improvements
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._get_fallback_line_improvements(resume_text)
    
    def _get_fallback_enhanced_resume(self, resume_text):
        """Fallback enhanced resume when AI is unavailable"""
        return f"""
{resume_text}

--- ENHANCEMENT SUGGESTIONS ---
• Replace weak verbs with strong action verbs (managed → spearheaded, helped → facilitated)
• Add specific numbers and percentages to achievements
• Include relevant technical skills and certifications
• Use industry-specific keywords throughout
• Ensure consistent formatting and bullet points
"""
    
    def _get_fallback_line_improvements(self, resume_text):
        """Fallback line improvements when AI is unavailable"""
        lines = resume_text.split('\n')[:10]
        improvements = []
        
        for i, line in enumerate(lines, 1):
            if len(line.strip()) > 10:
                improvements.append({
                    'line_number': i,
                    'original': line.strip(),
                    'suggestion': 'Add quantified results and stronger action verbs'
                })
        
        return improvements
    
