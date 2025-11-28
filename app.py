"""Gradio Web Interface for Medical RAG System

Provides a user-friendly interface for:
- Medical question answering
- Patient data management
- Health record viewing
"""
import os
import gradio as gr

from rag_system import MedicalRAG
from patient_manager import PatientManager

# Initialize systems
print("Initializing Medical RAG System...")
rag = MedicalRAG()
pm = PatientManager()

# Setup RAG
if not os.path.exists("./chroma_db"):
    print("Vector store not found. Creating...")
    rag.setup_qa_chain()
else:
    print("Loading existing vector store...")
    rag.setup_qa_chain()

def answer_question(question: str, history: list) -> str:
    """Handle question answering with enhanced output.

    Args:
        question: User's question
        history: Chat history (unused)

    Returns:
        Formatted answer with confidence and sources
    """
    if not question.strip():
        return "Please ask a question."

    try:
        result = rag.ask(question)
        answer = result['answer']

        # Add confidence indicator
        confidence = result.get('confidence', 'Unknown')
        answer = f"**Confidence: {confidence}**\n\n{answer}"

        # Add sources
        if result['sources']:
            answer += "\n\n📚 **Sources:**\n"
            for i, source in enumerate(result['sources'][:3], 1):
                answer += f"\n{i}. {source}\n"
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Medical RAG Assistant") as demo:
    gr.Markdown(r"""
    # 🏥 Medical RAG Assistant with Patient Management
    Ask questions about medical topics and patient data.
    """)
    
    with gr.Tabs():
        with gr.Tab("💬 Ask Questions"):
            gr.Markdown(r"""
            **Example questions:**
            - What is diabetes mellitus?
            - What is John Doe's blood pressure?
            - Which patients have high blood sugar?
            - Compare patient P001 and P002 health metrics
            - What are the risk factors for hypertension?
            """)
            
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(
                label="Ask a question",
                placeholder="Type your question here..."
            )
            clear = gr.Button("Clear")
            
            def respond(message, chat_history):
                bot_message = answer_question(message, chat_history)
                chat_history.append((message, bot_message))
                return "", chat_history
            
            msg.submit(respond, [msg, chatbot], [msg, chatbot])
            clear.click(lambda: None, None, chatbot, queue=False)

        with gr.Tab("➕ Add Patient"):
            gr.Markdown("### Add New Patient and Measurements")
            with gr.Row():
                patient_id = gr.Textbox(label="Patient ID", placeholder="P001")
                patient_name = gr.Textbox(label="Name", placeholder="John Doe")
            with gr.Row():
                age = gr.Number(label="Age", value=30)
                gender = gr.Dropdown(["Male", "Female", "Other"], label="Gender")
            
            gr.Markdown("### Body Measurements")
            with gr.Row():
                bp = gr.Textbox(label="Blood Pressure", placeholder="120/80 mmHg")
                hr = gr.Textbox(label="Heart Rate", placeholder="72 bpm")
            with gr.Row():
                bs = gr.Textbox(label="Blood Sugar", placeholder="95 mg/dL")
                weight = gr.Textbox(label="Weight", placeholder="70 kg")
            with gr.Row():
                height = gr.Textbox(label="Height", placeholder="170 cm")
                bmi = gr.Textbox(label="BMI", placeholder="24.2")
            with gr.Row():
                temp = gr.Textbox(label="Temperature", placeholder="98.6°F")
                o2 = gr.Textbox(label="O2 Saturation", placeholder="98%")
            
            add_btn = gr.Button("Add Patient", variant="primary")
            output = gr.Textbox(label="Status", lines=3)
            
            def add_patient_data(pid, name, age_val, gen, bp_val, hr_val, bs_val, wt, ht, bmi_val, temp_val, o2_val):
                try:
                    if pm.add_patient(pid, name, int(age_val), gen):
                        measurements = {}
                        if bp_val:
                            measurements["Blood Pressure"] = bp_val
                        if hr_val:
                            measurements["Heart Rate"] = hr_val
                        if bs_val:
                            measurements["Blood Sugar"] = bs_val
                        if wt:
                            measurements["Weight"] = wt
                        if ht:
                            measurements["Height"] = ht
                        if bmi_val:
                            measurements["BMI"] = bmi_val
                        if temp_val:
                            measurements["Temperature"] = temp_val
                        if o2_val:
                            measurements["Oxygen Saturation"] = o2_val
                        
                        pm.add_measurements(pid, measurements)
                        # Rebuild vector store
                        rag.create_vectorstore()
                        rag.setup_qa_chain()
                        return f"✓ Patient {pid} added successfully!\n\n{pm.get_patient_summary(pid)}"
                    else:
                        return f"✗ Patient {pid} already exists!"
                except Exception as e:
                    return f"✗ Error: {str(e)}"
            
            add_btn.click(
                add_patient_data,
                [patient_id, patient_name, age, gender, bp, hr, bs, weight, height, bmi, temp, o2],
                output
            )

        with gr.Tab("📋 View Patients"):
            gr.Markdown("### All Patients")
            refresh_btn = gr.Button("Refresh List")
            patient_list = gr.Textbox(label="Patients", lines=20)
            
            def show_patients():
                patients = pm.get_all_patients()
                if not patients:
                    return "No patients found."
                output = ""
                for pid in patients:
                    output += pm.get_patient_summary(pid) + "\n" + "="*60 + "\n\n"
                return output
            
            refresh_btn.click(show_patients, None, patient_list)
            demo.load(show_patients, None, patient_list)

if __name__ == "__main__":
    demo.launch(share=False)
