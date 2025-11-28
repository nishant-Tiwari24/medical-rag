"""
Demo Script for Medical RAG System

Demonstrates:
- Adding sample patients
- Recording health measurements
- Querying patient data via RAG
"""

from rag_system import MedicalRAG
from patient_manager import PatientManager

print("=" * 60)
print("Medical RAG System with Patient Data")
print("=" * 60)

# Initialize patient manager and add sample patients
print("\n1. Adding sample patients...")
pm = PatientManager()

pm.add_patient("P001", "John Doe", 45, "Male")
pm.add_measurements("P001", {
    "Blood Pressure": "140/90 mmHg",
    "Heart Rate": "85 bpm",
    "Blood Sugar (Fasting)": "180 mg/dL",
    "Weight": "85 kg",
    "Height": "175 cm",
    "BMI": "27.8",
    "Temperature": "98.6°F",
    "Oxygen Saturation": "97%",
    "Cholesterol Total": "240 mg/dL",
    "HbA1c": "7.5%"
})

pm.add_patient("P002", "Jane Smith", 32, "Female")
pm.add_measurements("P002", {
    "Blood Pressure": "120/80 mmHg",
    "Heart Rate": "72 bpm",
    "Blood Sugar (Fasting)": "95 mg/dL",
    "Weight": "62 kg",
    "Height": "165 cm",
    "BMI": "22.8",
    "Temperature": "98.4°F",
    "Oxygen Saturation": "98%",
    "Cholesterol Total": "180 mg/dL",
    "HbA1c": "5.2%"
})

pm.add_patient("P003", "Robert Johnson", 58, "Male")
pm.add_measurements("P003", {
    "Blood Pressure": "160/95 mmHg",
    "Heart Rate": "90 bpm",
    "Blood Sugar (Fasting)": "210 mg/dL",
    "Weight": "95 kg",
    "Height": "180 cm",
    "BMI": "29.3",
    "Temperature": "98.8°F",
    "Oxygen Saturation": "96%",
    "Cholesterol Total": "260 mg/dL",
    "HbA1c": "8.2%"
})

print("✓ Added 3 patients with measurements")

# Initialize RAG system
print("\n2. Initializing RAG system (loading models)...")
rag = MedicalRAG()
rag.setup_qa_chain()

print("\n" + "=" * 60)
print("System Ready! Testing with questions...")
print("=" * 60)

# Test questions
questions = [
    "What is John Doe's blood sugar level?",
    "Which patient has hypertension based on their blood pressure?",
    "What is the BMI of patient P002?",
    "Does Robert Johnson show signs of diabetes?",
    "Compare the health status of all patients"
]

for i, question in enumerate(questions, 1):
    print(f"\n{'='*60}")
    print(f"Question {i}: {question}")
    print("="*60)
    
    result = rag.ask(question)
    print(f"\n✓ Confidence: {result.get('confidence', 'N/A')}")
    print(f"\nAnswer:\n{result['answer']}")
    
    if result['sources']:
        print(f"\n📊 Data Sources ({len(result['sources'])} found):")
        for j, source in enumerate(result['sources'][:2], 1):
            print(f"\n{j}. {source[:200]}...")

print("\n" + "="*60)
print("Demo complete!")
print("="*60)
