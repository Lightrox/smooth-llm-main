import subprocess
import sys

# List of external dependencies (PyPI packages)
# Includes ML stack plus web app dependencies used in this project.
packages = [
    "torch",
    "numpy",
    "pandas",
    "tqdm",
    "transformers",
    "fastchat",
    "flask",
    "flask-cors",
    "gunicorn",
    "requests",
]

# Install each package
for package in packages:
    try:
        __import__(package if package != "torch" else "torch")
        print(f"✅ {package} already installed")
    except ImportError:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])