"""
Patient Data Management System

Handles storage and retrieval of patient records and measurements.
All data is stored locally in JSON format.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class PatientManager:
    """
    Manages patient records and health measurements.
    
    Features:
    - Add/retrieve patient information
    - Store health measurements with timestamps
    - Generate summaries for RAG integration
    """
    
    def __init__(self, data_dir: str = "patient_data"):
        """
        Initialize patient manager.
        
        Args:
            data_dir: Directory for storing patient data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.patients_file = os.path.join(data_dir, "patients.json")
        self.patients = self.load_patients()
    
    def load_patients(self) -> Dict[str, Any]:
        """
        Load existing patient data from JSON file.
        
        Returns:
            Dictionary of patient records
        """
        if os.path.exists(self.patients_file):
            with open(self.patients_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_patients(self) -> None:
        """Save patient data to JSON file."""
        with open(self.patients_file, 'w') as f:
            json.dump(self.patients, f, indent=2)
    
    def add_patient(self, patient_id: str, name: str, age: int, gender: str) -> bool:
        """
        Add a new patient to the system.
        
        Args:
            patient_id: Unique patient identifier
            name: Patient's full name
            age: Patient's age
            gender: Patient's gender
            
        Returns:
            True if patient added, False if already exists
        """
        if patient_id not in self.patients:
            self.patients[patient_id] = {
                "name": name,
                "age": age,
                "gender": gender,
                "measurements": [],
                "created_at": datetime.now().isoformat()
            }
            self.save_patients()
            return True
        return False
    
    def add_measurements(self, patient_id: str, measurements: Dict[str, str]) -> bool:
        """
        Add health measurements for a patient.
        
        Args:
            patient_id: Patient identifier
            measurements: Dictionary of measurement name -> value
            
        Returns:
            True if successful, False if patient not found
        """
        if patient_id not in self.patients:
            return False
        
        measurement_entry = {
            "timestamp": datetime.now().isoformat(),
            "data": measurements
        }
        
        self.patients[patient_id]["measurements"].append(measurement_entry)
        self.save_patients()
        return True
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """
        Get patient data by ID.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Patient data dictionary or None
        """
        return self.patients.get(patient_id)
    
    def get_all_patients(self) -> Dict[str, Any]:
        """
        Get all patient records.
        
        Returns:
            Dictionary of all patients
        """
        return self.patients
    
    def get_patient_summary(self, patient_id: str) -> Optional[str]:
        """
        Get formatted patient summary for display and RAG.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            Formatted summary string or None
        """
        patient = self.get_patient(patient_id)
        if not patient:
            return None
        
        summary = f"Patient ID: {patient_id}\n"
        summary += f"Name: {patient['name']}\n"
        summary += f"Age: {patient['age']} years\n"
        summary += f"Gender: {patient['gender']}\n\n"
        
        if patient['measurements']:
            summary += "Latest Measurements:\n"
            latest = patient['measurements'][-1]
            summary += f"Date: {latest['timestamp']}\n"
            for key, value in latest['data'].items():
                summary += f"- {key}: {value}\n"
        
        return summary
    
    def get_all_patient_summaries(self) -> List[str]:
        """
        Get all patient summaries for RAG indexing.
        
        Returns:
            List of formatted patient summaries
        """
        summaries = []
        for patient_id in self.patients:
            summary = self.get_patient_summary(patient_id)
            if summary:
                summaries.append(summary)
        return summaries

if __name__ == "__main__":
    # Quick test
    pm = PatientManager()
    pm.add_patient("TEST001", "Test Patient", 30, "Male")
    pm.add_measurements("TEST001", {"Blood Pressure": "120/80 mmHg"})
    print("✓ Patient manager working!")
    print(pm.get_patient_summary("TEST001"))
