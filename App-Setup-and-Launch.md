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
DATABASE_URL=postgresql://USERNAME:URL_ENCODED_PASSWORD@HOST:PORT/DATABASE_NAME
LLM_BASE_URL=https://parley.api.mit.edu/v1
LLM_API_KEY=PASTE_ASSIGNED_API_KEY_HERE
LLM_MODEL=gpt-5.4-mini
APP_DEMO_MODE=false
```

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
