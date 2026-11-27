# Run locally on Windows

The Flask application is in `abbbb\abbbb\PrivacyPreserving_FaceAuth_HE`.

1. Install **64-bit Python 3.12** from [python.org/downloads](https://www.python.org/downloads/). The current project pins and dependencies are not configured for the Python 3.13/3.14 installations currently on this machine.
2. From the repository folder, double-click `run_local.bat`. On first run it creates a virtual environment under `%LOCALAPPDATA%\PrivacyPreservingFaceAuth` (a short path to avoid Windows TensorFlow DLL path-length errors) and installs `requirements.txt`; later runs start the app directly.
3. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Allow camera access when prompted; webcam access is supported on localhost.

The server is restricted to this computer. Stop it with **Ctrl+C** in the launcher window.

The admin login configured for a fresh database is `admin` / `admin123`. Change the default before using this beyond local testing. The first face-recognition request may take longer while models are initialized/downloaded.

If dependency installation fails, keep the full error shown in the launcher window. If you change `requirements.txt` after the first setup, remove only `%LOCALAPPDATA%\PrivacyPreservingFaceAuth\.venv` and run the launcher again; do not delete the database or encryption key to reinstall packages.
