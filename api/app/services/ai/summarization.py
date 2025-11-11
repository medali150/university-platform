"""
Content Summarization Service
Summarizes course materials, readings, and documents
"""
from typing import Optional
from .openai_service import openai_service


class ContentSummarizer:
    """AI-powered content summarization"""
    
    
    async def summarize_text(
        self,
        content: str,
        max_length: int = 200,
        style: str = "concise"
    ) -> Optional[str]:
        """
        Summarize long text content
        
        Args:
            content: Text to summarize
            max_length: Max words in summary
            style: "concise", "detailed", or "bullet_points"
        
        Returns:
            Summarized text
        """
        
        prompt = self._build_summary_prompt(content, max_length, style)
        
        summary = await openai_service.generate_completion(
            prompt=prompt,
            model="llama-3.3-70b-versatile",  # Groq's latest model
            max_tokens=max_length * 2,  # Rough token estimate
            temperature=0.5
        )
        
        return summary
    
    
    def _build_summary_prompt(
        self,
        content: str,
        max_length: int,
        style: str
    ) -> str:
        """Build summarization prompt"""
        
        style_instructions = {
            "concise": "Provide a brief, concise summary in paragraph form.",
            "detailed": "Provide a comprehensive summary covering key points in detail.",
            "bullet_points": "Provide a summary as a list of bullet points highlighting main ideas."
        }
        
        instruction = style_instructions.get(style, style_instructions["concise"])
        
        prompt = f"""Summarize the following content:

{content[:4000]}  # Limit input to ~4000 chars

{instruction}
Keep the summary to approximately {max_length} words.
Focus on the most important concepts and takeaways.
"""
        
        return prompt
    
    
    async def generate_study_guide(
        self,
        material_title: str,
        material_content: str,
        learning_objectives: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a study guide from course material
        
        Args:
            material_title: Title of the material
            material_content: Full content
            learning_objectives: Optional learning goals
        
        Returns:
            Study guide text
        """
        
        prompt = f"""Create a study guide for the following course material:

Title: {material_title}

Content:
{material_content[:4000]}

"""
        
        if learning_objectives:
            prompt += f"\nLearning Objectives:\n{learning_objectives}\n"
        
        prompt += """
Generate a comprehensive study guide that includes:
1. Key Concepts (main ideas explained simply)
2. Important Terms (definitions)
3. Study Questions (5-7 questions to test understanding)
4. Summary (brief overview)

Format clearly with headers and bullet points.
"""
        
        study_guide = await openai_service.generate_completion(
            prompt=prompt,
            model="llama-3.3-70b-versatile",  # Groq's latest model
            max_tokens=1000,
            temperature=0.6
        )
        
        return study_guide
    
    
    async def extract_key_points(
        self,
        content: str,
        num_points: int = 5
    ) -> Optional[list]:
        """
        Extract key points from content
        
        Args:
            content: Text to analyze
            num_points: Number of key points to extract
        
        Returns:
            List of key points
        """
        
        prompt = f"""Extract the {num_points} most important key points from this content:

{content[:4000]}

Return as a numbered list. Each point should be 1-2 sentences maximum.
"""
        
        result = await openai_service.generate_completion(
            prompt=prompt,
            model="llama-3.3-70b-versatile",  # Groq's latest model
            max_tokens=400,
            temperature=0.5
        )
        
        if not result:
            return None
        
        # Parse numbered list into array
        lines = result.strip().split('\n')
        key_points = [
            line.strip().lstrip('0123456789.-) ').strip()
            for line in lines
            if line.strip()
        ]
        
        return key_points[:num_points]
    
    
    async def simplify_text(
        self,
        content: str,
        reading_level: str = "high_school"
    ) -> Optional[str]:
        """
        Simplify complex text for easier understanding
        
        Args:
            content: Text to simplify
            reading_level: "middle_school", "high_school", or "undergraduate"
        
        Returns:
            Simplified text
        """
        
        level_descriptions = {
            "middle_school": "8th grade reading level (simple vocabulary, short sentences)",
            "high_school": "10th grade reading level (clear but can use standard academic terms)",
            "undergraduate": "college level (maintain technical accuracy but improve clarity)"
        }
        
        target_level = level_descriptions.get(reading_level, level_descriptions["high_school"])
        
        prompt = f"""Rewrite the following text to be easier to understand:

{content[:3000]}

Target reading level: {target_level}

Maintain accuracy and key information, but use simpler language and clearer explanations.
"""
        
        simplified = await openai_service.generate_completion(
            prompt=prompt,
            model="llama-3.3-70b-versatile",  # Groq's latest model
            max_tokens=len(content.split()) * 2,  # Allow roughly 2x token space
            temperature=0.6
        )
        
        return simplified


# Global instance
content_summarizer = ContentSummarizer()
