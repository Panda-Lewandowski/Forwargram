import os
import subprocess
import sys
from pathlib import Path

from env_loader import load_project_env
from lang import T

load_project_env()

session_string = os.environ.get("SESSION_STRING")
app_dir = Path(__file__).resolve().parent
python_executable = sys.executable

if not session_string or session_string.strip() == "":
    print(T["no_session"])
    print(T["generate_session"])
    subprocess.run([python_executable, str(app_dir / "generate_session.py")], check=True)
else:
    print(T["session_found"])
    print(T["launch_main"])
    subprocess.run([python_executable, str(app_dir / "main.py")], check=True)