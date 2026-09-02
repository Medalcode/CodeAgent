import os
import urllib.request
import zipfile
import shutil
import subprocess
import datetime
import json

def clean_dist():
    if os.path.exists("../dist/CodeAgent"):
        shutil.rmtree("../dist/CodeAgent")
    os.makedirs("../dist/CodeAgent/python_runtime", exist_ok=True)

def load_manifest():
    with open("manifest.json", "r") as f:
        return json.load(f)

def download_python(manifest):
    print("Downloading Python Embedded...")
    os.makedirs("../dist", exist_ok=True)
    zip_path = "../dist/python-embed.zip"
    if not os.path.exists(zip_path):
        urllib.request.urlretrieve(manifest["python_url"], zip_path)
    
    print("Extracting Python Embedded...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("../dist/CodeAgent/python_runtime")
        
def configure_python():
    print("Configuring Python for pip...")
    pth_file = "../dist/CodeAgent/python_runtime/python311._pth"
    with open(pth_file, 'r') as f:
        content = f.read()
    content = content.replace("#import site", "import site")
    with open(pth_file, 'w') as f:
        f.write(content)
        
    print("Downloading get-pip.py...")
    pip_path = "../dist/get-pip.py"
    if not os.path.exists(pip_path):
        urllib.request.urlretrieve("https://bootstrap.pypa.io/get-pip.py", pip_path)
        
    print("Installing pip...")
    python_exe = os.path.abspath("../dist/CodeAgent/python_runtime/python.exe")
    subprocess.run([python_exe, os.path.abspath(pip_path)], check=True, cwd=os.path.abspath("../dist/CodeAgent/python_runtime"))

def install_dependencies(manifest):    
    print("Installing dependencies...")
    python_exe = os.path.abspath("../dist/CodeAgent/python_runtime/python.exe")
    subprocess.run([python_exe, "-m", "pip", "install"] + manifest["pip_packages"], check=True)

def copy_app(manifest):
    print("Copying Application...")
    dist_path = os.path.abspath("../dist/CodeAgent")
    src_path = os.path.abspath("..")
    
    for dir_name in manifest["app_directories"]:
        src_dir = os.path.join(src_path, dir_name)
        dst_dir = os.path.join(dist_path, dir_name)
        shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns(*manifest["exclude_patterns"]))
        
    for file_name in manifest["app_files"]:
        shutil.copy2(os.path.join(src_path, file_name), os.path.join(dist_path, file_name))

def create_launcher():
    print("Creating Launcher...")
    launcher_path = "../dist/CodeAgent/launch_codeagent.bat"
    with open(launcher_path, 'w') as f:
        f.write("@echo off\n")
        f.write("setlocal\n")
        f.write("cd /d \"%~dp0\"\n")
        f.write("python_runtime\\python.exe desktop_app.py %*\n")
        f.write("endlocal\n")

def write_version(manifest):
    print("Writing version metadata...")
    version_path = "../dist/CodeAgent/VERSION"
    with open(version_path, "w") as f:
        f.write("CodeAgent v5.0\n")
        f.write(f"Build Timestamp: {datetime.datetime.now().isoformat()}\n")
        f.write(f"Embedded Python: {manifest['python_url'].split('/')[-1]}\n")

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    manifest = load_manifest()
    clean_dist()
    download_python(manifest)
    configure_python()
    install_dependencies(manifest)
    copy_app(manifest)
    create_launcher()
    write_version(manifest)
    print("Build Complete.")

if __name__ == "__main__":
    main()
