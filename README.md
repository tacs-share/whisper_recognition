# whisper_recognition
 a tool for speech recognition with whisper

# Installation for Windows

To install the required dependencies for Python, run the following command:

```sh
pip install -r requirements.txt
```
In addition to that, you will also need ffmpeg. To install it, run the following command:

```sh
gsudo choco install ffmpeg
```

If you don’t have chocolatey installed, run PowerShell as administrator and execute the following:

```sh
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
choco install gsudo
```

# Usage
1. Run main.py with Python.

1. Choose the folder containing the audio files from the displayed explorer.

1. All audio files contained in the selected folder will be transcribed.

1. The transcription results will be saved as text files with the same name as the audio files.