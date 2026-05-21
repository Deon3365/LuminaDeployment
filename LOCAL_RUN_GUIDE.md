# Local Run Guide for Lumina Bible Interpreter

This document provides a quick, step‑by‑step guide to run the application on your local Windows machine.

## 1. Open a terminal and navigate to the project folder
```powershell
cd "C:\Users\gideo\OneDrive\Desktop\Agentic bible interpretator with phone app\LuminaDeployment"
```

## 2. (Optional) Create and activate a virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate   # PowerShell
# or `.\.venv\Scripts\activate.bat` for cmd.exe
```

## 3. Install the required Python packages
```powershell
pip install -r requirements.txt
```

## 4. Start the FastAPI server
You have two equivalent options:

### a) Run the entry‑point script
```powershell
python main.py
```

### b) Invoke Uvicorn directly (gives more control)
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 5. Verify the server is running
Open a browser and visit:
```
http://127.0.0.1:8000/api/health
```
or 
http://127.0.0.1:8000
You should see a JSON response similar to:
```json
{
  "status": "ok",
  "gemini_api_configured": true,
  "model": "gemini-2.5-flash",
  "kb_status": "ready"
}
```
If `gemini_api_configured` is `false`, double‑check that the `.env` file contains the correct `GEMINI_API_KEY` and that `load_dotenv()` is loading it (the file is already ignored by Git).

---
*The application’s static frontend will be served automatically at `http://127.0.0.1:8000/`.*
