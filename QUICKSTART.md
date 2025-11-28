# 🚀 Quick Start Guide

Get your Medical RAG system running in 5 minutes!

---

## Step 1: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

**What this does:**
- Installs LangChain, ChromaDB, Transformers
- Downloads Python packages (~500MB)

---

## Step 2: Collect Medical Data (2-5 minutes)

```bash
python3 data_collector.py
```

**What this does:**
- Fetches 80+ articles from PubMed
- Saves to `medical_data/pubmed_articles.json`
- Topics: diabetes, hypertension, anatomy, etc.

**Expected output:**
```
Collecting medical data...
Fetching articles for: anatomy basics
Fetching articles for: cardiovascular system
...
Saved 80 items to medical_data/pubmed_articles.json
Data collection complete!
```

---

## Step 3: Choose Your Interface

### Option A: Web Interface (Easiest)

```bash
python3 app.py
```

Then open: `http://127.0.0.1:7860`

**First run will:**
- Download TinyLlama model (~2GB) - one time only
- Create vector database
- Takes 3-5 minutes

**Features:**
- 💬 Chat interface for questions
- ➕ Add patients with measurements
- 📋 View all patient records

---

### Option B: Demo Script (See It In Action)

```bash
python3 patient_demo.py
```

**What this does:**
- Adds 3 sample patients
- Asks 5 example questions
- Shows confidence scores and sources

**Example output:**
```
Question: What is John Doe's blood sugar level?
✓ Confidence: High
Answer: John Doe's fasting blood sugar is 180 mg/dL...
```

---

### Option C: Python Code (For Developers)

```python
from rag_system import MedicalRAG

# Initialize (first time takes 3-5 min)
rag = MedicalRAG()
rag.setup_qa_chain()

# Ask questions
result = rag.ask("What is diabetes mellitus?")
print(result['answer'])
print(f"Confidence: {result['confidence']}")
```

---

## Step 4: Try Example Questions

### Medical Knowledge
```
- What is diabetes mellitus?
- What are the symptoms of hypertension?
- Explain the cardiovascular system
- What causes infectious diseases?
```

### Patient Queries (after adding patients)
```
- What is John Doe's blood pressure?
- Which patients have high blood sugar?
- Show me patient P001's measurements
- Compare health metrics of all patients
```

---

## Common Issues & Solutions

### ❌ "No documents found"
**Solution:** Run `python3 data_collector.py` first

### ❌ "Out of memory"
**Solution:** 
- Close other applications
- Need at least 4GB RAM
- Try on a machine with more memory

### ❌ "Model download failed"
**Solution:**
- Check internet connection
- Try again (downloads can be interrupted)
- Download may take 5-10 minutes on slow connections

### ❌ "ChromaDB error"
**Solution:**
```bash
rm -rf chroma_db/
python3 app.py  # Will recreate automatically
```

---

## Next Steps

1. **Add Your Own Patients**
   - Use web interface "Add Patient" tab
   - Or use `PatientManager` in code

2. **Customize Data Sources**
   - Edit `data_collector.py` to add more topics
   - Add your own medical documents

3. **Tune Performance**
   - See README.md "Performance Tips" section
   - Adjust chunk size, retrieval count, etc.

---

## System Requirements

✅ **Minimum:**
- Python 3.9+
- 4GB RAM
- 3GB disk space
- Internet (for initial setup)

✅ **Recommended:**
- Python 3.10+
- 8GB RAM
- 5GB disk space
- GPU (optional, 3-5x faster)

---

## File Structure After Setup

```
medical-rag-system/
├── medical_data/
│   └── pubmed_articles.json    ← 80+ articles
├── patient_data/
│   └── patients.json           ← Your patients
├── chroma_db/                  ← Vector database
│   ├── chroma.sqlite3
│   └── [embeddings]
└── [Python files]
```

---

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| First setup | 3-5 min | Downloads models |
| Data collection | 2-5 min | Fetches PubMed |
| Question answering | 2-4 sec | Per question |
| Adding patient | <1 sec | Instant |
| Rebuilding index | 10-30 sec | After adding patients |

---

## Getting Help

1. Check this guide
2. Read README.md
3. Check Troubleshooting section
4. Create GitHub issue

---

**Ready to go! 🎉**

Start with: `python3 app.py`
