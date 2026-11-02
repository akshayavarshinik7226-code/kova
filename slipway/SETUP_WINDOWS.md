# Windows setup (PowerShell)

Verified on Linux only. These steps use standard Python tooling but have **not been run on Windows by me**; report any difference.

1. Install Python 3.12 from python.org. Tick **Add python.exe to PATH**.
2. Open PowerShell in the project folder:
```powershell
python -m venv .venv
# If activation is blocked:  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```
3. Create your admin (prompts for a 12+ character password):
```powershell
python manage.py create-admin --email you@example.com --name "Your Name"
```
4. Run the tests, then start the app:
```powershell
python -m unittest discover -s tests -t . -v
python run.py
```
5. Open http://127.0.0.1:5000 and sign in.

To connect Coolify later, put `COOLIFY_URL` and `COOLIFY_TOKEN` in `.env` and restart. Never commit `.env`.
