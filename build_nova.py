import subprocess
import sys
import os
import shutil

def build():
    print("--- Starting NOVA Build Process ---")
    
    # Define paths
    entry_point = os.path.join("NOVA", "nova.py")
    dist_path = os.path.join("dist", "nova")
    
    # Platform specific separator for --add-data
    sep = os.pathsep # ';' on Windows, ':' on Linux
    
    # Base command
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onedir",
        "--console",
        "--name", "nova",
        "--hidden-import", "speech_recognition",
        "--hidden-import", "pyttsx3.drivers",
        "--hidden-import", "pyttsx3.drivers.sapi5",
        "--hidden-import", "PyQt5.sip",
        "--hidden-import", "pygetwindow",
        "--hidden-import", "pyautogui",
        "--hidden-import", "pyperclip",
        "--hidden-import", "psutil",
        "--hidden-import", "mss",
        "--hidden-import", "pytesseract",
        f"--add-data=.env.example{sep}.",
        f"--add-data=README.md{sep}.",
        f"--add-data=TESTING_GUIDE.md{sep}.",
        f"--add-data=RELEASE_NOTES.md{sep}.",
        f"--add-data=PACKAGING.md{sep}.",
        f"--add-data=NOVA{sep}NOVA",
        entry_point
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        
        # Post-build: Copy important files to root of dist folder for visibility
        print("\n--- Finalizing Distribution Folder ---")
        docs = [".env.example", "README.md", "TESTING_GUIDE.md", "RELEASE_NOTES.md", "PACKAGING.md"]
        for doc in docs:
            if os.path.exists(doc):
                shutil.copy(doc, dist_path)
                print(f"Copied {doc} to {dist_path}")
        
        print("\n--- Build Successful! ---")
        print(f"Executable folder: {dist_path}")
        print(f"Main executable: {os.path.join(dist_path, 'nova.exe')}")
        print("Please copy .env.example to .env beside the exe and configure it.")
        
    except subprocess.CalledProcessError as e:
        print(f"\n--- Build Failed! ---")
        sys.exit(1)

if __name__ == "__main__":
    build()
