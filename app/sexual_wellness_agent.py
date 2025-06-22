import os
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.vector_db import SexualWellnessVectorDB

logger = logging.getLogger(__name__)

class SexualWellnessQuery(BaseModel):
    """Model for sexual wellness queries"""
    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class SexualWellnessResponse(BaseModel):
    """Model for sexual wellness responses"""
    answer: str
    confidence: float
    sources: List[Dict[str, Any]] = []
    follow_up_questions: List[str] = []

class SexualWellnessAgent:
    """
    An AI agent for sexual wellness guidance using a vector database
    """
    def __init__(self):
        """Initialize the sexual wellness agent"""
        self.vector_db = SexualWellnessVectorDB()
        self.follow_up_questions = {
            "What is sexual wellness?": [
                "How can I improve my sexual health?",
                "What is the relationship between mental health and sexual health?",
                "What are common sexual health concerns?"
            ],
            "How can I improve my sexual health?": [
                "How can I practice safer sex?",
                "How can I improve communication with my partner about sex?",
                "What are common sexual health concerns?"
            ],
            "What are common sexual health concerns?": [
                "How does aging affect sexual health?",
                "How can I maintain sexual wellness during pregnancy?",
                "What is the relationship between mental health and sexual health?"
            ],
            "How can I practice safer sex?": [
                "What are common myths about sex?",
                "What is consent in sexual relationships?",
                "How can I improve my sexual health?"
            ],
            "What is consent in sexual relationships?": [
                "How can I improve communication with my partner about sex?",
                "What are common myths about sex?",
                "How can I practice safer sex?"
            ],
            "How can I improve communication with my partner about sex?": [
                "What is consent in sexual relationships?",
                "What are common myths about sex?",
                "How does aging affect sexual health?"
            ],
            "What are common myths about sex?": [
                "How can I improve communication with my partner about sex?",
                "What is the relationship between mental health and sexual health?",
                "How does aging affect sexual health?"
            ],
            "How does aging affect sexual health?": [
                "What are common sexual health concerns?",
                "How can I improve my sexual health?",
                "What are common myths about sex?"
            ],
            "What is the relationship between mental health and sexual health?": [
                "How can I improve my sexual health?",
                "What are common sexual health concerns?",
                "How can I improve communication with my partner about sex?"
            ],
            "How can I maintain sexual wellness during pregnancy?": [
                "What are common sexual health concerns?",
                "How can I practice safer sex?",
                "How can I improve communication with my partner about sex?"
            ]
        }
        
        # Default follow-up questions for queries not in our database
        self.default_follow_ups = [
            "What is sexual wellness?",
            "How can I improve my sexual health?",
            "How can I practice safer sex?"
        ]
        
    def _get_follow_up_questions(self, matched_question: Optional[str]) -> List[str]:
        """Get follow-up questions based on the matched question"""
        if matched_question and matched_question in self.follow_up_questions:
            return self.follow_up_questions[matched_question]
        return self.default_follow_ups
        
    def _generate_disclaimer(self) -> str:
        """Generate a disclaimer for sexual wellness advice"""
        return ("Note: This information is provided for educational purposes only and is not a substitute for "
                "professional medical advice. Please consult with a healthcare provider for personalized guidance.")
    
    def process_query(self, query_data: SexualWellnessQuery) -> SexualWellnessResponse:
        """
        Process a sexual wellness query
        
        Args:
            query_data: The query data
            
        Returns:
            A response with answer, confidence, sources, and follow-up questions
        """
        query = query_data.query.strip()
        
        # Search the vector database
        search_results = self.vector_db.search(query, k=2)
        
        if not search_results:
            # No results found
            return SexualWellnessResponse(
                answer=f"I don't have specific information about that. {self._generate_disclaimer()}",
                confidence=0.0,
                sources=[],
                follow_up_questions=self.default_follow_ups
            )
            
        # Get the best match
        best_match = search_results[0]
        confidence = best_match["score"]
        
        # If confidence is too low, provide a generic response
        if confidence < 0.6:
            return SexualWellnessResponse(
                answer=(f"I'm not entirely sure about that, but here's some related information: "
                       f"{best_match['answer']} {self._generate_disclaimer()}"),
                confidence=confidence,
                sources=[{"question": best_match["question"], "score": confidence}],
                follow_up_questions=self._get_follow_up_questions(best_match["question"])
            )
            
        # Return the answer with high confidence
        answer = f"{best_match['answer']} {self._generate_disclaimer()}"
        
        return SexualWellnessResponse(
            answer=answer,
            confidence=confidence,
            sources=[{"question": result["question"], "score": result["score"]} for result in search_results],
            follow_up_questions=self._get_follow_up_questions(best_match["question"])
        )
        
    def add_knowledge(self, question: str, answer: str) -> bool:
        """
        Add new knowledge to the vector database
        
        Args:
            question: The question
            answer: The answer
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.vector_db.add_documents([{"question": question, "answer": answer}])
            return True
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            return False
