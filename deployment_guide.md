# Hosting Lumina Bible Interpreter Online

Follow these step-by-step instructions to deploy your application online for free using **GitHub** and **Hugging Face Spaces**.

---

### Step 1: Create a GitHub Repository
1. Go to [GitHub](https://github.com/) and log in.
2. Click **New** to create a new repository.
3. Name it (e.g., `lumina-bible-interpreter`), leave it Public or Private, and click **Create repository**.
4. In your terminal, initialize git and push your code to the repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/lumina-bible-interpreter.git
   git push -u origin main
   ```

---

### Step 2: Create a Hugging Face Space
1. Go to [Hugging Face](https://huggingface.co/) and log in (or register).
2. Click on your profile icon in the top right, then select **New Space**.
3. Fill in the configuration:
   - **Space Name:** `lumina-bible-interpreter` (or any name you prefer)
   - **SDK:** Select **Docker** (it will read your project's `Dockerfile` automatically)
   - **Template:** Select **Blank**
   - **Space License:** Choose `Apache 2.0` (or any other)
   - **Visibility:** Public (or Private if you only want it accessible to yourself)
   - **Hardware:** Choose **CPU Basic (Free)**
4. Click **Create Space** at the bottom of the page.

---

### Step 3: Add your Gemini API Key to Hugging Face
1. On your newly created Hugging Face Space page, click the **Settings** tab.
2. Scroll down to the **Variables and secrets** section.
3. Click **New secret**.
4. Add the secret:
   - **Name:** `GEMINI_API_KEY`
   - **Value:** `[Paste your actual Gemini API Key from your .env file]`
5. Click **Save**.

---

### Step 4: Get a Hugging Face Access Token
1. Go to your Hugging Face Profile settings: Click your profile picture -> **Settings**.
2. On the left sidebar, click **Access Tokens**.
3. Click **New token**.
4. Configure the token:
   - **Name:** `github-sync`
   - **Role:** Select **Write** (this is required for GitHub to push code to Hugging Face)
5. Click **Create token** and copy it.

---

### Step 5: Save Hugging Face Secret in GitHub
1. Open your repository on GitHub.
2. Click the **Settings** tab.
3. On the left sidebar, expand **Secrets and variables** and click **Actions**.
4. Click **New repository secret**.
5. Configure the secret:
   - **Name:** `HF_TOKEN`
   - **Value:** `[Paste the Hugging Face Write Access Token you copied in Step 4]`
6. Click **Add secret**.

---

### Step 6: Update Workflow and Trigger Deployment
1. Open [.github/workflows/deploy-hf.yml](file:///c:/Users/gideo/OneDrive/Desktop/Agentic%20Projects/Agentic%20bible%20interpretator%20with%20phone%20app/.github/workflows/deploy-hf.yml) in your editor.
2. In line 26, replace the placeholders with your actual Hugging Face details:
   ```yaml
   git push --force https://[YOUR_HF_USERNAME]:${HF_TOKEN}@huggingface.co/spaces/[YOUR_HF_USERNAME]/[YOUR_SPACE_NAME] main
   ```
   *For example, if your Hugging Face username is `gideon` and space name is `lumina-bible-interpreter`, line 26 will be:*
   ```bash
   git push --force https://gideon:${HF_TOKEN}@huggingface.co/spaces/gideon/lumina-bible-interpreter main
   ```
3. Commit and push this change to your GitHub repository:
   ```bash
   git add .
   git commit -m "Update deployment workflow"
   git push origin main
   ```

---

### Done!
Once pushed, GitHub Actions will automatically run the sync job. You can monitor the progress under the **Actions** tab of your GitHub repository. When the action finishes, your Space on Hugging Face will build the Docker container and serve the app on its public URL!
