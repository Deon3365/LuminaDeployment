# Hugging Face Spaces Deployment – API Error Troubleshooting

This guide assumes you are deploying the **Lumina Bible Interpreter** FastAPI app to a Hugging Face Space using the provided `Dockerfile` and GitHub Actions workflow.

---

## 1️⃣ Common cause: Missing `GEMINI_API_KEY`

The backend checks for the environment variable `GEMINI_API_KEY` at startup:
```python
api_key_configured = bool(os.getenv("GEMINI_API_KEY"))
```
If the variable is absent, the `/api/health` endpoint returns:
```json
{"status": "ok", "gemini_api_configured": false, ...}
```
When the UI tries to call Gemini‑based endpoints you’ll see an error like **`GEMINI_API_KEY_MISSING`**.

### Fix
1. **Add the key as a secret on the Space**:
   - Open your Space → **Settings → Secrets**.
   - Click **Add secret** → Name: `GEMINI_API_KEY` → Value: *YOUR GOOGLE GEMINI API KEY*.
2. **Restart the Space** (the secret is injected on each restart automatically).
3. Verify the health endpoint now returns `gemini_api_configured: true`.

---

## 2️⃣ Port mismatch – why the app never becomes reachable

Hugging Face injects its own `$PORT` environment variable (usually `7860`). Your `Dockerfile` currently forces the container to listen on the hard‑coded value `7860`:
```Dockerfile
ENV PORT=7860
...
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
```
If HF later overrides `$PORT` (e.g., to `12345`), the container will still listen on `7860`, and HF’s proxy can’t reach it → **`502 Bad Gateway`** or **connection refused**.

### Fix – make the port truly configurable
Replace the hard‑coded `ENV PORT=7860` with a fallback that respects the injected value:
```Dockerfile
# Remove the fixed PORT env line
# ENV PORT=7860   <-- delete this line

# Use the port provided by HF (default to 7860 if not set)
ARG PORT=7860
ENV PORT=${PORT}

# Command stays the same – it will read the final $PORT value
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
```
Commit the change and push – the GitHub Action will rebuild the image and the Space will start correctly.

---

## 3️⃣ Ensure the `.env` file is **not** used on the Space
The repository ships a local `.env` for development. In a container on HF you should **not** copy that file, otherwise the secret you set in the UI could be overridden.

### Fix
Add a `.dockerignore` entry (if not already present) so the `.env` file is excluded from the image:
```
# .dockerignore
.env
```
If the file is already in the image, rebuild the container after adding the ignore rule.

---

## 4️⃣ Verify the health endpoint inside the Space
After the Space restarts, open the **Logs** tab and look for a line similar to:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:7860 (Press CTRL+C to quit)
```
Then, from a separate tab, request the health check:
```
curl https://<your‑space>.hf.space/api/health
```
You should receive the JSON payload with `gemini_api_configured: true`. If you still get `false`, double‑check the secret name and spelling.

---

## 5️⃣ Quick checklist before re‑deploying
1. **Add `GEMINI_API_KEY` secret** on the Space.
2. **Update Dockerfile** to make `$PORT` configurable (see Section 2).
3. **Add `.env` to `.dockerignore`** so local dev file isn’t baked in.
4. Commit and push – the GitHub Action (`deploy‑hf.yml`) will push the new image to HF.
5. **Open the Space logs** and confirm the server started without errors.
6. Test `/api/health` via the browser or `curl`.

---

## 6️⃣ Example minimal Dockerfile after the fixes
```Dockerfile
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# System deps (needed for chromadb, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source (excluding .env via .dockerignore)
COPY . .

# Allow HF to set the port, fallback to 7860 locally
ARG PORT=7860
ENV PORT=${PORT}
EXPOSE ${PORT}

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
```

---

### 🎯 What to do next?
- Apply the Dockerfile changes.
- Add the secret.
- Push the repo (GitHub Action will redeploy).
- Verify the health check.

If you still encounter a specific error message, paste the exact log line here and we can dig deeper.
