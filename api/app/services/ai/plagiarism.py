"""
Plagiarism Detection Service
Uses TF-IDF + Cosine Similarity for text comparison
"""
from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import numpy as np


class PlagiarismDetector:
    """Plagiarism detection using TF-IDF and cosine similarity"""
    
    def __init__(self, threshold: float = 0.7):
        """
        Args:
            threshold: Similarity threshold (0-1) above which text is flagged
        """
        self.threshold = threshold
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words='english',
            max_features=1000
        )
    
    
    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        # Remove special characters
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.lower()
    
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Returns:
            Similarity score (0-1)
        """
        try:
            # Preprocess
            text1_clean = self.preprocess_text(text1)
            text2_clean = self.preprocess_text(text2)
            
            # Create TF-IDF vectors
            vectors = self.vectorizer.fit_transform([text1_clean, text2_clean])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            print(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    
    def check_plagiarism(
        self,
        submission_text: str,
        comparison_texts: List[Dict[str, str]]
    ) -> Dict:
        """
        Check submission against multiple sources
        
        Args:
            submission_text: Text to check
            comparison_texts: List of {"text": "...", "source": "..."} dicts
        
        Returns:
            {
                "is_plagiarized": bool,
                "overall_similarity": float,
                "matches": [{"source": str, "similarity": float}],
                "flagged_count": int
            }
        """
        try:
            matches = []
            
            for comparison in comparison_texts:
                similarity = self.calculate_similarity(
                    submission_text,
                    comparison["text"]
                )
                
                matches.append({
                    "source": comparison.get("source", "Unknown"),
                    "similarity": round(similarity * 100, 2)  # Percentage
                })
            
            # Sort by similarity
            matches.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Flag if any match exceeds threshold
            flagged_matches = [m for m in matches if m["similarity"] >= self.threshold * 100]
            
            overall_similarity = matches[0]["similarity"] if matches else 0.0
            
            return {
                "is_plagiarized": len(flagged_matches) > 0,
                "overall_similarity": overall_similarity,
                "threshold": self.threshold * 100,
                "matches": matches[:5],  # Top 5 matches
                "flagged_count": len(flagged_matches)
            }
            
        except Exception as e:
            print(f"❌ Error checking plagiarism: {e}")
            return {
                "is_plagiarized": False,
                "overall_similarity": 0.0,
                "matches": [],
                "flagged_count": 0,
                "error": str(e)
            }
    
    
    async def check_submission_against_class(
        self,
        submission_text: str,
        other_submissions: List[Dict]
    ) -> Dict:
        """
        Check submission against other student submissions
        
        Args:
            submission_text: Current submission text
            other_submissions: List of {"id": str, "contenu": str, "etudiant_nom": str}
        
        Returns:
            Plagiarism report
        """
        comparison_texts = [
            {
                "text": sub["contenu"],
                "source": f"Student submission: {sub.get('etudiant_nom', 'Unknown')}"
            }
            for sub in other_submissions
        ]
        
        result = self.check_plagiarism(submission_text, comparison_texts)
        
        # Add report details
        result["report"] = self._generate_report(result)
        
        return result
    
    
    def _generate_report(self, result: Dict) -> str:
        """Generate human-readable report"""
        
        if result["is_plagiarized"]:
            report = f"⚠️ PLAGIARISM DETECTED\n\n"
            report += f"Overall Similarity: {result['overall_similarity']:.1f}%\n"
            report += f"Threshold: {result['threshold']:.1f}%\n\n"
            report += f"Flagged Matches ({result['flagged_count']}):\n"
            
            for match in result["matches"]:
                if match["similarity"] >= result["threshold"]:
                    report += f"- {match['source']}: {match['similarity']:.1f}%\n"
        else:
            report = f"✅ NO PLAGIARISM DETECTED\n\n"
            report += f"Highest Similarity: {result['overall_similarity']:.1f}%\n"
            report += f"Threshold: {result['threshold']:.1f}%\n"
        
        return report


# Global instance
plagiarism_detector = PlagiarismDetector(threshold=0.7)
