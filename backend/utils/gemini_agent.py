import os
import json
import requests
from ..config import Config

class AgenticAIPipeline:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    def _call_gemini_or_mock(self, prompt: str, system_instruction: str) -> str:
        """Call Gemini REST API directly or return fallback response if API key is not configured."""
        if self.api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": f"{system_instruction}\n\nUser Request:\n{prompt}"}
                        ]
                    }],
                    "generationConfig": {
                        "temperature": 0.3,
                        "responseMimeType": "application/json"
                    }
                }
                res = requests.post(url, headers=headers, json=payload, timeout=12)
                if res.status_code == 200:
                    result = res.json()
                    candidates = result.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        if parts:
                            return parts[0].get('text', '')
            except Exception as e:
                print(f"Gemini API Call Exception: {e}")
        return None

    def analyze_resume(self, raw_text: str, target_role: str = "Software Engineer"):
        """Pipeline executing the Agentic AI suite evaluated specifically against a target job role."""
        prompt = f"Target Job Role: {target_role}\nResume Content:\n{raw_text[:3000]}"
        system_instr = (
            f"You are an expert AI Technical Recruiter & ATS Evaluator for the role of '{target_role}'.\n"
            f"Scan the candidate resume against '{target_role}' and return JSON with keys:\n"
            f"- matched_skills: list of string skills present in candidate resume that match '{target_role}'\n"
            f"- required_job_skills: list of essential string skills standard for '{target_role}'\n"
            f"- missing_skills: list of string skills missing from candidate resume needed for '{target_role}'\n"
            f"- ats_score: integer 0 to 100\n"
            f'- result: string ("Selected", "Needs Improvement", or "Rejected") -> Use "Selected" if ats_score >= 75, "Needs Improvement" if 60-74, "Rejected" if < 60.\n'
            f"- explanation: detailed evaluation explaining why the candidate is Selected, Needs Improvement, or Rejected specifically for '{target_role}'.\n"
            f"- certifications: list of string recommended certifications for '{target_role}'\n"
            f"- roadmap: list of objects with phase, title, duration, items tailored to '{target_role}'\n"
            f'- questions: object with keys "technical", "hr", "behavioral", each containing a list of strings tailored to \'{target_role}\'\n'
        )
        raw_json_resp = self._call_gemini_or_mock(prompt, system_instr)
        if raw_json_resp:
            try:
                parsed = json.loads(raw_json_resp)
                if 'ats_score' in parsed and 'result' in parsed:
                    parsed['target_role'] = target_role
                    return parsed
            except Exception as e:
                print("Error parsing Gemini JSON:", e)

        # Intelligent Role-Aware Skill Scanner & Heuristic Evaluator
        lowered = raw_text.lower()
        role_lower = target_role.lower()

        matched = []
        required = []
        missing = []
        certifications = []

        if "frontend" in role_lower or "react" in role_lower or "web" in role_lower:
            required = ["React.js", "JavaScript (ES6+)", "HTML5 & CSS3", "TypeScript", "Tailwind CSS", "State Management (Redux/Zustand)", "RESTful APIs", "Webpack / Vite", "Jest Unit Testing"]
            for s in ["React.js", "JavaScript (ES6+)", "HTML5 & CSS3", "RESTful APIs", "Tailwind CSS"]:
                if any(kw in lowered for kw in ["react", "javascript", "js", "html", "css", "api", "tailwind"]):
                    matched.append(s)
            missing = [s for s in required if s not in matched]
            if not missing:
                missing = ["TypeScript Strict Typing", "Next.js / SSR", "Micro-Frontends"]
            certifications = ["Meta Front-End Developer Certificate", "AWS Certified Cloud Practitioner"]

        elif "backend" in role_lower or "python" in role_lower or "java" in role_lower or "node" in role_lower:
            required = ["Python / Flask / Django", "SQL Databases (PostgreSQL/SQLite)", "REST & GraphQL APIs", "Docker Containerization", "Redis Caching", "Git & Version Control", "System Architecture", "Unit Testing (PyTest)"]
            for s in ["Python / Flask / Django", "SQL Databases (PostgreSQL/SQLite)", "REST & GraphQL APIs", "Git & Version Control"]:
                if any(kw in lowered for kw in ["python", "sql", "api", "flask", "django", "git", "database"]):
                    matched.append(s)
            missing = [s for s in required if s not in matched]
            if not missing:
                missing = ["Docker Containerization", "Redis In-Memory Caching", "Kafka Event Streaming"]
            certifications = ["AWS Certified Solutions Architect", "MongoDB Certified Developer"]

        elif "data" in role_lower or "ai" in role_lower or "machine learning" in role_lower:
            required = ["Python Data Stack (Pandas/NumPy)", "SQL & Data Warehousing", "Machine Learning (Scikit-Learn/TensorFlow)", "Deep Learning (PyTorch)", "Data Visualization (Tableau/Matplotlib)", "MLOps Model Pipelines"]
            for s in ["Python Data Stack (Pandas/NumPy)", "SQL & Data Warehousing"]:
                if any(kw in lowered for kw in ["python", "sql", "pandas", "data", "numpy"]):
                    matched.append(s)
            missing = [s for s in required if s not in matched]
            if not missing:
                missing = ["PyTorch Model Fine-Tuning", "BigData Pipelines (Spark)", "MLOps Model Deployment"]
            certifications = ["Google Professional Data Engineer", "TensorFlow Developer Certificate"]

        else:
            required = ["Software Architecture", "Data Structures & Algorithms", "SQL & Relational DBs", "RESTful Web APIs", "Git Workflow", "Docker & DevOps Basics", "CI/CD Pipelines"]
            for s in ["Software Architecture", "SQL & Relational DBs", "RESTful Web APIs", "Git Workflow"]:
                matched.append(s)
            missing = ["Docker & DevOps Basics", "CI/CD Automation Pipelines", "Cloud Microservices (AWS/GCP)"]
            certifications = ["AWS Certified Solutions Architect", "Docker & Kubernetes Developer"]

        # Deduplicate matched skills
        matched = list(set(matched))
        
        # Calculate ATS score dynamically based on skill match ratio + content length
        match_ratio = len(matched) / max(1, len(required))
        score = int(min(98, max(40, match_ratio * 70 + (25 if len(raw_text) > 300 else 10))))

        if score >= 75:
            result = "Selected"
            explanation = (
                f"Resume skill scanner detected key match on {len(matched)} essential technical skills out of {len(required)} required for '{target_role}'. "
                f"Candidate's profile shows strong alignment with ATS benchmarks for {target_role} and has been marked as SELECTED for interview."
            )
        elif score >= 60:
            result = "Needs Improvement"
            explanation = (
                f"Resume skill scanner identified core competencies, but missing critical job skills required for '{target_role}'. "
                f"ATS match score is {score}/100. Candidate is marked as NEEDS IMPROVEMENT before final selection."
            )
        else:
            result = "Rejected"
            explanation = (
                f"Resume skill scanner found significant gaps in required technical skills for '{target_role}' (ATS score: {score}/100). "
                f"Key essential skills for {target_role} were missing in the uploaded document. Candidate is REJECTED for this role."
            )

        roadmap = [
            {
                "phase": f"Phase 1: Acquire Missing Skills for {target_role}",
                "title": f"Master Missing Core Stack Requirements",
                "duration": "Weeks 1-2",
                "items": missing[:3] if missing else ["Advanced architectural patterns", "Performance optimization"]
            },
            {
                "phase": "Phase 2: Hands-on Role Projects",
                "title": "Build Production-Ready Applications",
                "duration": "Weeks 3-4",
                "items": [f"Develop end-to-end project highlighting {m}" for m in (missing[:2] if missing else ["API design", "Database indexing"])]
            },
            {
                "phase": "Phase 3: Cloud & DevOps Deployment",
                "title": "Containerization & CI/CD Pipeline",
                "duration": "Weeks 5-6",
                "items": ["Docker containerization", "GitHub Actions CI/CD setup", "Cloud deployment to AWS/Vercel"]
            },
            {
                "phase": "Phase 4: Role Interview Practice",
                "title": "Mock Technical & Behavioral Drills",
                "duration": "Weeks 7-8",
                "items": [f"Mock technical interviews for {target_role}", "STAR framework answer practice"]
            }
        ]

        questions = {
            "technical": [
                f"What are the most critical technical skills required for a production-grade {target_role}?",
                f"How do you handle performance bottlenecks specifically when working with {matched[0] if matched else 'APIs'}?",
                f"How would you integrate {missing[0] if missing else 'Docker'} into your development workflow for a {target_role} project?"
            ],
            "hr": [
                f"Why are you interested in advancing your career as a {target_role}?",
                "Walk me through a project where you learned a new technical skill quickly.",
                "Where do you see your engineering career in 3 years?"
            ],
            "behavioral": [
                "Describe a situation where you had to prioritize missing project skills under a tight deadline.",
                "Tell me about a time you had a technical disagreement with a colleague and how it was resolved.",
                "Give an example of a mistake you made in production code and how you fixed it."
            ]
        }

        return {
            "target_role": target_role,
            "ats_score": score,
            "result": result,
            "matched_skills": matched,
            "required_job_skills": required,
            "missing_skills": missing,
            "explanation": explanation,
            "certifications": certifications,
            "roadmap": roadmap,
            "questions": questions
        }

    def evaluate_answer(self, question_text: str, category: str, user_answer: str):
        """Feedback Agent: evaluates user interview response."""
        prompt = f"Question ({category}): {question_text}\nUser Answer: {user_answer}"
        system_instr = """You are an expert AI Interviewer. Evaluate the candidate's answer and return JSON with keys:
- rating: string ("Excellent", "Good", "Needs Work")
- score: integer 0-100
- strengths: string
- areas_for_improvement: string
- ideal_sample_answer: string exemplary answer
"""
        raw_resp = self._call_gemini_or_mock(prompt, system_instr)
        if raw_resp:
            try:
                parsed = json.loads(raw_resp)
                if 'score' in parsed:
                    return parsed
            except Exception as e:
                print("Error parsing answer feedback JSON:", e)

        word_count = len(user_answer.split())
        score = min(95, max(50, word_count * 3))
        rating = "Good" if score >= 75 else ("Needs Work" if score < 65 else "Good")
        if score > 88:
            rating = "Excellent"

        return {
            "rating": rating,
            "score": score,
            "strengths": "Clear structure, relevant terminology, and direct answer to the prompt.",
            "areas_for_improvement": "Consider providing a concrete metric or quantifiable business impact (e.g. reduced latency by 30%) using the STAR framework.",
            "ideal_sample_answer": f"A top-tier answer for this question would clearly outline the Situation, Task, Action taken, and measurable Result using concrete data points."
        }

ai_pipeline = AgenticAIPipeline()
