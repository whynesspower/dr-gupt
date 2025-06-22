import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class SexualWellnessVectorDB:
    """
    Vector database for sexual wellness information using FAISS
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector database
        
        Args:
            model_name: The sentence transformer model to use for embeddings
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "sexual_wellness_db")
        os.makedirs(self.db_path, exist_ok=True)
        self.index_path = os.path.join(self.db_path, "faiss_index.bin")
        self.documents_path = os.path.join(self.db_path, "documents.json")
        self._load_or_create_db()
        
    def _load_or_create_db(self):
        """Load existing database or create a new one with default data"""
        if os.path.exists(self.index_path) and os.path.exists(self.documents_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.documents_path, 'r', encoding='utf-8') as f:
                    self.documents = json.load(f)
                logger.info(f"Loaded existing vector database with {len(self.documents)} documents")
            except Exception as e:
                logger.error(f"Error loading vector database: {str(e)}")
                self._create_default_db()
        else:
            self._create_default_db()
    
    def _create_default_db(self):
        """Create a default database with sexual wellness information"""
        logger.info("Creating default sexual wellness vector database")
        
        # Default sexual wellness information
        default_data = [
            {
                "question": "What is sexual wellness?",
                "answer": "Sexual wellness refers to a state of physical, emotional, mental, and social well-being in relation to sexuality. It encompasses a positive and respectful approach to sexuality and sexual relationships, as well as the possibility of having pleasurable and safe sexual experiences, free of coercion, discrimination, and violence."
            },
            {
                "question": "How can I improve my sexual health?",
                "answer": "Improving sexual health involves regular check-ups with healthcare providers, practicing safe sex, maintaining open communication with partners, understanding consent, managing stress, maintaining overall physical health through exercise and nutrition, and seeking professional help when needed for sexual concerns."
            },
            {
                "question": "What are common sexual health concerns?",
                "answer": "Common sexual health concerns include sexually transmitted infections (STIs), erectile dysfunction, premature ejaculation, low libido, painful intercourse, fertility issues, menopause-related changes, and psychological factors affecting sexual performance or satisfaction."
            },
            {
                "question": "How can I practice safer sex?",
                "answer": "Safer sex practices include using barriers like condoms or dental dams correctly and consistently, getting regular STI testing, limiting sexual partners, communicating openly about sexual health status, and avoiding sexual activity when you or your partner has symptoms of an STI."
            },
            {
                "question": "What is consent in sexual relationships?",
                "answer": "Consent is a clear, enthusiastic, and ongoing agreement to engage in sexual activity. It must be freely given without pressure, manipulation, or impairment. Consent can be withdrawn at any time, and previous consent doesn't imply future consent. Effective consent requires open communication and respect for boundaries."
            },
            {
                "question": "How can I improve communication with my partner about sex?",
                "answer": "Improving sexual communication involves choosing the right time and place for discussions, using 'I' statements to express feelings, being specific about desires and boundaries, listening actively without judgment, starting with positive feedback, and considering professional help like sex therapy if needed."
            },
            {
                "question": "What are common myths about sex?",
                "answer": "Common sex myths include: sex always decreases in long-term relationships, men always want sex more than women, orgasm should always happen during intercourse, size matters most for satisfaction, and that good sex should be spontaneous rather than planned. These myths can create unrealistic expectations and pressure."
            },
            {
                "question": "How does aging affect sexual health?",
                "answer": "Aging can bring changes like decreased hormone levels, longer arousal time, changes in erectile function, vaginal dryness, and shifts in desire. However, many people maintain satisfying sex lives throughout older age by adapting to these changes, using lubricants, focusing on intimacy beyond intercourse, and maintaining open communication."
            },
            {
                "question": "What is the relationship between mental health and sexual health?",
                "answer": "Mental health and sexual health are closely connected. Stress, anxiety, depression, and past trauma can affect desire, arousal, and satisfaction. Similarly, sexual problems can impact mental wellbeing. Addressing both aspects through therapy, stress management, and open communication is important for overall wellness."
            },
            {
                "question": "How can I maintain sexual wellness during pregnancy?",
                "answer": "Sexual wellness during pregnancy involves adapting to physical changes, finding comfortable positions, communicating with partners about changing needs and desires, addressing concerns with healthcare providers, and understanding that desire may fluctuate throughout pregnancy. Unless medically advised otherwise, sex is generally safe during pregnancy."
            }
        ]
        
        # Add the default data to the database
        self.add_documents(default_data)
        
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the vector database
        
        Args:
            documents: List of documents with 'question' and 'answer' fields
        """
        if not documents:
            return
            
        # Extract questions for embedding
        questions = [doc["question"] for doc in documents]
        
        # Generate embeddings
        embeddings = self.model.encode(questions)
        
        # Add to FAISS index
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        # Store documents
        start_idx = len(self.documents)
        for i, doc in enumerate(documents):
            doc["id"] = start_idx + i
            self.documents.append(doc)
            
        # Save the updated database
        self._save_db()
        
        logger.info(f"Added {len(documents)} documents to vector database")
        
    def _save_db(self):
        """Save the database to disk"""
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.documents_path, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved vector database with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error saving vector database: {str(e)}")
            
    def search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Search the vector database for relevant documents
        
        Args:
            query: The search query
            k: Number of results to return
            
        Returns:
            List of matching documents with similarity scores
        """
        if not self.documents:
            return []
            
        # Generate query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search the index
        distances, indices = self.index.search(query_embedding, min(k, len(self.documents)))
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
                
            doc = self.documents[idx].copy()
            doc["score"] = float(1 - distances[0][i])  # Convert distance to similarity score
            results.append(doc)
            
        return results
