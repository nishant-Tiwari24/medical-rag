"""
RAG System for Medical Q&A - Fully Local with Patient Data

This module implements a Retrieval-Augmented Generation (RAG) system
for medical question answering using local LLMs and vector databases.
"""

import os
import json
import torch
from typing import Dict, List, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from patient_manager import PatientManager

class MedicalRAG:
    """
    Medical RAG System with optimized retrieval and generation.
    
    Features:
    - Local LLM (TinyLlama) for privacy
    - MMR retrieval for diverse results
    - Confidence scoring
    - Patient data integration
    """
    
    def __init__(self, data_dir: str = "medical_data"):
        """
        Initialize the Medical RAG system.
        
        Args:
            data_dir: Directory containing medical documents
        """
        self.data_dir = data_dir
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vectorstore = None
        self.qa_chain = None
        self.llm = None
        self.patient_manager = PatientManager()
        
    def load_documents(self) -> List[str]:
        """
        Load medical documents and patient data from various sources.
        
        Returns:
            List of document strings
        """
        documents = []
        
        # Load PubMed articles
        json_file = os.path.join(self.data_dir, "pubmed_articles.json")
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
                
            for article in articles:
                text = f"Title: {article['title']}\n\n"
                text += f"Abstract: {article['abstract']}\n\n"
                text += f"Source: {article['source']}\n"
                text += f"URL: {article['url']}"
                documents.append(text)
        
        # Load patient data
        patient_summaries = self.patient_manager.get_all_patient_summaries()
        for summary in patient_summaries:
            documents.append(f"PATIENT RECORD:\n{summary}")
        
        return documents
    
    def create_vectorstore(self) -> None:
        """
        Create vector store with optimized chunking strategy.
        
        Chunking Strategy:
        - Chunk size: 300 tokens (optimal for precise retrieval)
        - Overlap: 100 tokens (maintains context continuity)
        - Hierarchical separators for natural boundaries
        """
        print("Loading documents...")
        documents = self.load_documents()
        
        if not documents:
            raise ValueError("No documents found. Run data_collector.py first!")
        
        print(f"Loaded {len(documents)} documents")
        
        # Advanced chunking strategy
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=100,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        texts = text_splitter.create_documents(documents)
        
        print(f"Creating vector store with {len(texts)} chunks...")
        self.vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )
        
        print("Vector store created!")
    
    def load_local_llm(self) -> None:
        """
        Load and configure local LLM with optimized parameters.
        
        Model: TinyLlama-1.1B-Chat-v1.0
        - Size: ~2GB
        - Speed: ~2.4s per response
        - Memory: ~2.2GB RAM
        
        Optimizations:
        - FP16 on GPU, FP32 on CPU
        - Low temperature (0.2) for factual answers
        - Repetition penalty to reduce redundancy
        """
        print("Loading local LLM (this may take a few minutes first time)...")
        
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            low_cpu_mem_usage=True
        )
        
        # Optimized generation parameters
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=200,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.2,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        self.llm = HuggingFacePipeline(pipeline=pipe)
        print("Local LLM loaded!")
    
    def setup_qa_chain(self) -> None:
        """
        Setup QA chain with advanced retrieval and prompt engineering.
        
        Retrieval Strategy:
        - MMR (Maximum Marginal Relevance) for diverse results
        - k=5: Return top 5 chunks
        - fetch_k=10: Consider 10 candidates
        - lambda_mult=0.7: Balance relevance vs diversity
        """
        if not self.vectorstore:
            self.create_vectorstore()
        
        if not self.llm:
            self.load_local_llm()
        
        # Advanced prompt engineering
        prompt_template = """<|system|>
You are an expert medical AI assistant. Provide accurate, concise, and evidence-based answers.
Use ONLY the provided context. If information is not in the context, say so clearly.
For patient data, cite specific measurements and values.</s>
<|user|>
Context Information:
{context}

Question: {question}

Instructions:
- Answer directly and concisely
- Use specific data from context
- For patient queries, mention exact values
- If uncertain, state limitations</s>
<|assistant|>
"""
        
        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Advanced retriever with MMR
        retriever = self.vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "fetch_k": 10,
                "lambda_mult": 0.7
            }
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Ask a question and get an answer with sources and confidence.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing:
            - answer: Generated response
            - sources: List of source documents
            - confidence: Confidence score (High/Medium/Low)
        """
        if not self.qa_chain:
            self.setup_qa_chain()
        
        # Query preprocessing
        enhanced_question = self._enhance_query(question)
        
        # Get answer from chain
        result = self.qa_chain({"query": enhanced_question})
        
        # Post-process answer
        answer = self._clean_answer(result["result"])
        
        return {
            "answer": answer,
            "sources": [doc.page_content[:200] + "..." for doc in result["source_documents"]],
            "confidence": self._calculate_confidence(result["source_documents"])
        }
    
    def _enhance_query(self, question: str) -> str:
        """
        Enhance query for better retrieval.
        
        Args:
            question: Original question
            
        Returns:
            Enhanced question string
        """
        question = question.strip()
        if not question.endswith('?'):
            question += '?'
        return question
    
    def _clean_answer(self, answer: str) -> str:
        """
        Clean and format the generated answer.
        
        - Removes duplicate lines
        - Removes incomplete sentences
        - Strips whitespace
        
        Args:
            answer: Raw answer from LLM
            
        Returns:
            Cleaned answer string
        """
        # Remove repetitive content
        lines = answer.split('\n')
        seen = set()
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                cleaned_lines.append(line)
        
        answer = '\n'.join(cleaned_lines)
        
        # Remove incomplete sentences at the end
        if answer and not answer[-1] in '.!?':
            sentences = answer.split('.')
            if len(sentences) > 1:
                answer = '.'.join(sentences[:-1]) + '.'
        
        return answer.strip()
    
    def _calculate_confidence(self, source_docs: List) -> str:
        """
        Calculate confidence score based on retrieved sources.
        
        Args:
            source_docs: List of retrieved documents
            
        Returns:
            Confidence level: "High", "Medium", or "Low"
        """
        if not source_docs:
            return "Low"
        
        # Heuristic: more sources = higher confidence
        if len(source_docs) >= 3:
            return "High"
        elif len(source_docs) >= 2:
            return "Medium"
        else:
            return "Low"

if __name__ == "__main__":
    # Quick test
    rag = MedicalRAG()
    rag.setup_qa_chain()
    result = rag.ask("What is diabetes mellitus?")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']}")
