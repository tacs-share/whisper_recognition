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


# Can't you use Github?
Run PowerShell as administrator and execute the following:
```sh
# powershell
# installer dir_path (Downloads)
$username=(Get-ChildItem Env:\USERNAME).Value
$downloads="C:\Users\"+$username+ "\Downloads"

#install git
echo "Downloading Git installer..."
$dlPath=$downloads+"\git_installer.exe"
$url="https://github.com/git-for-windows/git/releases/download/v2.41.0.windows.1/Git-2.41.0-64-bit.exe"
Invoke-WebRequest $url -OutFile $dlPath
echo "Installing Git..."
Start-Process -FilePath $dlPath -Wait

# install python
echo "Downloading Python installer..."
$python_installer_path=$downloads+"\python_installer.exe"
$python_url="https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
Invoke-WebRequest $python_url -OutFile $python_installer_path
echo "Installing Python..."
Start-Process -FilePath $python_installer_path -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
echo "Python version:"
python --version

# install chocolatey
echo "Installing Chocolatey..."
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

echo "Chocolatey installed. Please restart PowerShell to continue."

```
(restart powershell)
```sh
# powershell
$username=(Get-ChildItem Env:\USERNAME).Value
$downloads="C:\Users\"+$username+ "\Downloads"

# install ffmpeg
echo "Installing ffmpeg..."
choco install ffmpeg

# git clone
echo "Cloning the repository..."
git clone https://github.com/tacs-share/whisper_recognition.git $downloads\whisper_recognition
Set-Location $downloads\whisper_recognition
echo "Installing required Python packages..."
pip install -r requirements.txt

```