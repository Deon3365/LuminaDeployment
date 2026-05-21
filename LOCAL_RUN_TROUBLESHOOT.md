# Local Run Troubleshooting Guide for Lumina Bible Interpreter

If the UI does not appear after following the **Local Run Guide**, work through the checklist below.

---

## 1. Verify the server is still running
```powershell
# In the terminal where you started uvicorn, you should see a log line like:
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
- **If the process exited** (e.g., you pressed `Ctrl‑C`), start it again:
```powershell
uvicorn main:app --host 127.0.0.1 --port 8000
```
- **Do not close this window** while you are testing the UI.

---

## 2. Open the correct URL
- In your browser, go to **exactly**:
```
http://127.0.0.1:8000/
```
- **Do not use** `localhost:8000` or any other port unless you changed the `--port` argument.

---

## 3. Check the static files are being served
`main.py` mounts the `static` folder:
```python
app.mount(
    "/",
    StaticFiles(directory=os.path.join(BASE_DIR, "static"), html=True),
    name="static",
)
```
If you renamed or moved the folder, restore it to:
```
<project_root>/static/index.html
<project_root>/static/app.js
<project_root>/static/style.css
```

---

## 4. Confirm the environment variable is loaded
```powershell
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"
```
The output should be your API key (the string you placed in `.env`).
If it prints `None`:
- Ensure you are **running the command from the project root** where `.env` resides.
- Ensure the file name is exactly `.env` (no extra extensions).

---

## 5. Look for error messages in the terminal
Typical failure patterns:
- **Port already in use** – change the port:
  ```powershell
  uvicorn main:app --host 127.0.0.1 --port 8001
  ```
- **Import errors** – reinstall requirements:
  ```powershell
  pip install -r requirements.txt
  ```
- **Missing static files** – reinstall from repo or copy them back.

---

## 6. Browser console diagnostics
Open developer tools (F12) → **Console**. Look for:
- `Failed to load resource: net::ERR_CONNECTION_REFUSED` → server isn’t reachable.
- `GET http://127.0.0.1:8000/app.js 404 (Not Found)` → static folder not mounted correctly.
- CORS warnings – should not appear because FastAPI allows all origins.

---

## 7. Firewall / Antivirus
Windows Defender may block inbound connections on non‑standard ports.
- Temporarily **disable** the firewall or *allow* `python.exe` for public networks.
- After testing, re‑enable the firewall and keep the rule.

---

## 8. Optional: Ollama (local AI) service
The UI displays a banner:
```
🦙 Powered by Ollama (Local AI)
```
If you **do not have Ollama running**, the interpretation button will fail, but the UI itself still loads.
- Install Ollama: https://ollama.com/download
- Start it with:
  ```powershell
  ollama serve
  ```
- You can ignore this step for UI testing; the static page will still render.

---

## 9. Verify the server’s response directly
In the terminal run:
```powershell
curl http://127.0.0.1:8000/
```
You should receive the HTML of `index.html`. If you get an error, the static mount is broken.

---

## 10. Re‑start from scratch (last resort)
```powershell
# 1. Delete the virtual environment (optional)
Remove-Item -Recurse -Force .venv
# 2. Re‑create it
python -m venv .venv
.\.venv\Scripts\activate
# 3. Re‑install deps
pip install -r requirements.txt
# 4. Run the server again
uvicorn main:app --host 127.0.0.1 --port 8000
```

---

### TL;DR Quick fix
1. **Leave the terminal open** where `uvicorn` is running.
2. Open **http://127.0.0.1:8000/** in a browser.
3. If you see a blank page, check the console for 404 on `app.js` → static folder issue.
4. Ensure `.env` is in the same directory and contains `GEMINI_API_KEY`.

You should now see the full Lumina UI with the top bar, search box, and study panel.

---

*If you still encounter problems, copy the exact error message from the terminal or browser console and share it – we can dive deeper.*
