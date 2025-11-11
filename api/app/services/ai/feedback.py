"""
AI Feedback Generation Service
Generates personalized feedback for student submissions
"""
from typing import Dict, Optional
from .openai_service import openai_service


class FeedbackGenerator:
    """Generate AI-powered feedback for assignments"""
    
    
    async def generate_feedback(
        self,
        assignment_title: str,
        assignment_instructions: str,
        submission_content: str,
        rubric: Optional[Dict] = None,
        grade: Optional[float] = None,
        max_points: Optional[float] = None
    ) -> str:
        """
        Generate detailed feedback for a submission
        
        Args:
            assignment_title: Assignment name
            assignment_instructions: Assignment requirements
            submission_content: Student's submission text
            rubric: Optional grading rubric
            grade: Optional grade given
            max_points: Maximum points possible
        
        Returns:
            Generated feedback text
        """
        
        # Build prompt
        prompt = self._build_feedback_prompt(
            assignment_title,
            assignment_instructions,
            submission_content,
            rubric,
            grade,
            max_points
        )
        
        # Generate feedback using Groq (ultra-fast!)
        feedback = await openai_service.generate_completion(
            prompt=prompt,
            model="llama-3.3-70b-versatile",  # Groq's latest model
            max_tokens=500,
            temperature=0.7
        )
        
        if not feedback:
            return self._generate_fallback_feedback(grade, max_points)
        
        return feedback
    
    
    def _build_feedback_prompt(
        self,
        assignment_title: str,
        assignment_instructions: str,
        submission_content: str,
        rubric: Optional[Dict],
        grade: Optional[float],
        max_points: Optional[float]
    ) -> str:
        """Build prompt for OpenAI"""
        
        prompt = f"""You are a helpful teaching assistant providing constructive feedback on student work.

Assignment: {assignment_title}

Instructions:
{assignment_instructions}

Student Submission:
{submission_content[:2000]}  # Limit to 2000 chars

"""
        
        if rubric:
            prompt += f"\nGrading Rubric:\n{rubric}\n"
        
        if grade is not None and max_points is not None:
            prompt += f"\nGrade: {grade}/{max_points} ({(grade/max_points*100):.1f}%)\n"
        
        prompt += """
Please provide constructive feedback that:
1. Highlights what the student did well (strengths)
2. Identifies areas for improvement
3. Gives specific, actionable suggestions
4. Encourages continued learning

Keep feedback concise (200-300 words), professional, and encouraging.
"""
        
        return prompt
    
    
    def _generate_fallback_feedback(
        self,
        grade: Optional[float],
        max_points: Optional[float]
    ) -> str:
        """Generate basic feedback when AI is unavailable"""
        
        if grade is not None and max_points is not None:
            percentage = (grade / max_points) * 100
            
            if percentage >= 90:
                return "Excellent work! Your submission demonstrates strong understanding of the material. Keep up the great effort!"
            elif percentage >= 80:
                return "Good work! Your submission shows solid understanding. Review the feedback and consider how you might improve further."
            elif percentage >= 70:
                return "Satisfactory work. Your submission meets basic requirements but has room for improvement. Focus on the areas mentioned in the grading rubric."
            elif percentage >= 60:
                return "Your submission needs improvement. Please review the assignment requirements carefully and consider resubmitting if allowed."
            else:
                return "Your submission did not meet the requirements. Please review the instructions and reach out if you need clarification."
        
        return "Your submission has been reviewed. See detailed feedback from your instructor."
    
    
    async def generate_assignment_suggestions(
        self,
        course_topic: str,
        course_level: str,
        previous_assignments: Optional[str] = None
    ) -> str:
        """
        Generate assignment ideas for teachers
        
        Args:
            course_topic: Course subject (e.g., "Python Programming")
            course_level: Student level (e.g., "beginner", "intermediate")
            previous_assignments: Optional context about past assignments
        
        Returns:
            Assignment suggestions
        """
        
        prompt = f"""You are an experienced educator creating engaging assignments.

Course Topic: {course_topic}
Student Level: {course_level}

"""
        
        if previous_assignments:
            prompt += f"Previous Assignments:\n{previous_assignments}\n\n"
        
        prompt += """
Generate 3 creative assignment ideas that:
1. Match the student level
2. Encourage critical thinking
3. Are practical and relevant
4. Build upon previous assignments (if provided)

For each assignment, include:
- Title
- Learning objectives
- Instructions (brief)
- Expected deliverables
- Suggested grading rubric

Format as a clear, organized list.
"""
        
        suggestions = await openai_service.generate_completion(
            prompt=prompt,
            model="llama-3.3-70b-versatile",  # Groq's latest model
            max_tokens=1000,
            temperature=0.8
        )
        
        if not suggestions:
            return "AI service temporarily unavailable. Please try again later."
        
        return suggestions


# Global instance
feedback_generator = FeedbackGenerator()
