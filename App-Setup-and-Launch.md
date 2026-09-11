# Application Setup and Local Launch

The repository contains two supported application versions:

- `literature-synthesis`
- `protocol-generation`

Each version contains the application and the complete vector-database pipeline.
Use the branch corresponding to the application you want to run. These
instructions assume Windows PowerShell and Python 3.11.

## 1. Download the application from GitHub

Install [Git](https://git-scm.com/downloads) and Python 3.11 first. Then open
PowerShell and navigate to the folder where the repository should be stored:

```powershell
cd "C:\path\to\parent-folder"
```

Clone the literature-synthesis application:

```powershell
git clone --branch literature-synthesis `
  https://github.com/julia-kubes/AI-Agent-for-LiB-Fast-Charging-Protocol.git `
  literature-synthesis
```

To use the protocol-generation application instead:

```powershell
git clone --branch protocol-generation `
  https://github.com/julia-kubes/AI-Agent-for-LiB-Fast-Charging-Protocol.git `
  protocol-generation
```

Enter the downloaded repository:

```powershell
cd ".\literature-synthesis"
```

Replace `literature-synthesis` with `protocol-generation` if that is the version
you downloaded. To download future updates, open PowerShell in the repository
and run:

```powershell
git pull
```

GitHub's **Code > Download ZIP** option can also download the files, but cloning
with Git is preferable because it makes future updates easier.

## 2. Create the Python environment

From the repository root:

```powershell
py -3.11 -m venv .venv
& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r requirements-app.txt
```

If PowerShell blocks environment activation, the remaining commands can still
be run using the virtual environment's Python executable directly.

## 3. Add the database and API credentials

Create a private `.env` file from the provided template:

```powershell
Copy-Item .env.example .env
notepad .env
```

Enter the assigned credentials:

```text
DATABASE_URL= INSERT_NEON_CONNECTION_STRING_HERE
LLM_BASE_URL= INSERT_LLM_URL_HERE
LLM_API_KEY=PASTE_ASSIGNED_API_KEY_HERE
LLM_MODEL= INSERT_MODEL_NAME_HERE
APP_DEMO_MODE=false
```
To obtain the URL from Neon:
1. Log into you Neon account and navigate to the "AI Charging RAG Project"
2. Click "Connect"
3. Copy the connection string

Important:

- Do not add quotation marks unless they are part of the credential.
- URL-encode special characters in the database password.
- Never upload, commit, or email the completed `.env` file.
- Each user should use their own API key.

## 4. Start the application

From the repository root:

```powershell
& ".\.venv\Scripts\python.exe" -m streamlit run ".\app\ui.py"
```

Streamlit should open the application in a web browser. If it does not, copy the
local URL shown in PowerShell—normally `http://localhost:8501`—into a browser.

Stop the application by returning to PowerShell and pressing `Ctrl+C`.

## Common startup problems

- **Python was not found:** Install Python 3.11 or use the full path to the
  virtual-environment executable.
- **No module named streamlit:** Rerun the requirements installation command.
- **Missing database or API key:** Confirm `.env` is in the repository root and
  contains the required values.
- **Port already in use:** Start the application on another port:

  ```powershell
  & ".\.venv\Scripts\python.exe" -m streamlit run ".\app\ui.py" --server.port 8502
  ```

## Contributing Changes of the App to Github

Complete the **Application Setup and Local Launch** instructions first. Collaborators should clone the complete repository once—not separately clone each application branch—and then switch between versions:

```powershell
git switch literature-synthesis
git pull
```

or:

```powershell
git switch protocol-generation
git pull
```

Before editing, create a working branch from the application version being changed:

```powershell
git switch -c feature/brief-description
```

After making changes, run the tests:

```powershell
& ".\.venv\Scripts\python.exe" -m unittest discover -s tests -v
```

Commit and push the working branch:

```powershell
git add path\to\changed-file
git commit -m "Brief description of the change"
git push -u origin feature/brief-description
```

Open a pull request into the correct application branch:

- Literature changes → `literature-synthesis`
- Protocol changes → `protocol-generation`
- Do not submit application changes to `main`.

Changes to shared infrastructure—such as parsing, chunking, embedding, metadata, or retrieval—must be applied and tested in both application branches.
