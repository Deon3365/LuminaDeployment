# Transition to Gemini API and Prepare Deployment

Update the multi-agent Bible interpreter system to use the Gemini API (defaulting to a lightweight model, e.g., `gemini-2.5-flash` or `gemini-1.5-flash`) instead of local Ollama models. Prepare the application for deployment to public hosting services (like Hugging Face Spaces, Render, or GitHub Pages) by making configuration dynamic and adding necessary deployment files (like `Dockerfile` and a GitHub Actions workflow).

## User Review Required

> [!IMPORTANT]
> To run the backend successfully in the cloud, you will need to set the `GEMINI_API_KEY` environment variable in your hosting platform settings. We will configure the backend to use your existing `.env` file key locally and dynamically fetch it in production.
>
> **Recommended Hosting Option:**
> We recommend hosting the entire application (both the FastAPI backend and static frontend) as a single service on **Hugging Face Spaces** (CPU Basic tier is 100% free). 
> - It avoids cross-origin (CORS) security issues entirely.
> - We can set up a GitHub Action to automatically sync your GitHub repository to Hugging Face Spaces on every `git push`. This satisfies your requirement of hosting/deploying via GitHub.
>
> Alternatively, we can deploy the frontend to **GitHub Pages** and the backend to **Hugging Face Spaces** or **Render**, but that requires hardcoding/setting the backend URL in the frontend javascript.

## Open Questions

None at the moment. Please let us know if you prefer a different hosting architecture than the combined Hugging Face Space + GitHub sync option.

---

## Proposed Changes

### Core Agent Changes

#### [MODIFY] [base_agent.py](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/agents/base_agent.py)
- Replace Ollama client code with async HTTP request calling the official Google Gemini API.
- Use `gemini-2.5-flash` (or `gemini-1.5-flash` via `.env`) as the default lightweight model to conserve free tier quota.
- Implement robust error handling (such as API key missing, rate limits `429`, and parsing errors) to return structured error dicts.

#### [MODIFY] [orchestrator_agent.py](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/agents/orchestrator_agent.py)
- Replace Ollama-specific offline checks with generic API error checking to propagate critical exceptions (e.g., rate limits, missing key).

#### [MODIFY] [intake_agent.py](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/agents/intake_agent.py)
- Propagate critical API errors instead of swallowing them with fallback parse defaults.

#### [MODIFY] [translation_agent.py](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/agents/translation_agent.py)
- Propagate Gemini errors immediately rather than attaching translations to an error dictionary.

---

### Backend Service Changes

#### [MODIFY] [main.py](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/main.py)
- Read deployment port dynamically from the `PORT` environment variable (default: `8000`), which is standard for cloud providers.
- Update the startup logging and `/api/health` endpoint to show Gemini status instead of Ollama connectivity.

---

### Frontend Updates

#### [MODIFY] [app.js](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/static/app.js)
- Handle the new Gemini error responses (like missing API key or API rate limits) and show helpful toast notifications to the user.
- Ensure the API base URL can support both local testing and external backend URLs.

---

### Deployment Support Configuration

#### [NEW] [Dockerfile](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/Dockerfile)
- Add a lightweight Docker configuration using `python:3.9-slim` to allow easy deployment on Hugging Face Spaces, Render, or any Docker-compatible hosting.

#### [NEW] [deploy-hf.yml](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/.github/workflows/deploy-hf.yml)
- Add a GitHub Actions workflow to automatically push changes to Hugging Face Spaces on commits to the `main` branch.

---

## Verification Plan

### Automated Tests
- Run `python "C:\Users\gideo\.gemini\antigravity-ide\brain\e4152dd1-7a32-4d13-94c1-cbef25bc6865\scratch\test_gemini.py"` to ensure that Gemini API key can execute queries.
- Start the server locally using `python main.py` and query the health endpoint `/api/health`.

### Manual Verification
- Test passage interpretation (e.g. Genesis 1:1) from the UI page to verify that it uses Gemini API correctly and displays output on the frontend dashboard.
- Force API errors (e.g., by temporarily invalidating `GEMINI_API_KEY` in `.env`) to confirm the UI displays proper warning messages instead of breaking.
