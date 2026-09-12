import subprocess
import platform

def run_command(command: list[str]):
    proccess = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")

    for output in proccess.stdout:
        print(output, end='')

run_command(["pip", "install", "pyautogui"])
run_command(["pip", "install", "opencv-python"])
run_command(["pip", "install", "sentence_transformers"])
run_command(["pip", "install", "mss"])
run_command(["pip", "install", "scikit-image"])

match platform.system():
    case "Windows":
        run_command(["powershell", "-Command", "irm", "https://ollama.com/install.ps1 | iex"])
    case "Linux":
        run_command(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"])
    case "Darwin":
        run_command(["curl", "-fsSL", "https://ollama.com/install.sh", "|", "sh"])

run_command(["ollama", "pull", "qwen3.5:9b"])