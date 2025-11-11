"""
AI Services for Smart Classroom
"""
from .openai_service import openai_service
from .plagiarism import plagiarism_detector
from .feedback import feedback_generator
from .summarization import content_summarizer

__all__ = [
    "openai_service",
    "plagiarism_detector",
    "feedback_generator",
    "content_summarizer"
]
