import psutil
import platform
import subprocess

def get_cpu_info():
    cpu_info = {
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Cores": psutil.cpu_count(logical=True),
        "Max Frequency (Mhz)": psutil.cpu_freq().max,
        "Current Frequency (Mhz)": psutil.cpu_freq().current,
        "CPU Usage (%)": psutil.cpu_percent(interval=1),
        "CPU Stats": psutil.cpu_stats()._asdict()
    }
    return cpu_info

def get_ram_info():
    ram_info = {
        "Total RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Available RAM (GB)": round(psutil.virtual_memory().available / (1024 ** 3), 2),
        "Used RAM (GB)": round(psutil.virtual_memory().used / (1024 ** 3), 2),
        "RAM Usage (%)": psutil.virtual_memory().percent
    }
    return ram_info

def get_gpu_info():
    gpu_info = []
    
    # Check for NVIDIA GPU
    try:
        nvidia_smi = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if nvidia_smi.returncode == 0:
            gpu_info.append({"Message": "NVIDIA GPU detected", "Details": nvidia_smi.stdout.strip()})
        else:
            gpu_info.append({"Message": "No dedicated NVIDIA GPU detected."})

    except FileNotFoundError:
        gpu_info.append({"Message": "No dedicated GPU detected, checking onboard options."})

        # Onboard GPU detection for Linux
        if platform.system() == "Linux":
            onboard_gpu = subprocess.run(["lspci", "-nnk"], capture_output=True, text=True)
            if "VGA compatible controller" in onboard_gpu.stdout:
                gpu_info.append({"Message": "Onboard GPU detected", "Details": onboard_gpu.stdout.strip()})
            else:
                gpu_info.append({"Message": "No onboard GPU detected."})

        # Onboard GPU detection for Windows
        elif platform.system() == "Windows":
            onboard_gpu = subprocess.run(["wmic", "path", "win32_videocontroller", "get", "name"], capture_output=True, text=True)
            if onboard_gpu.stdout.strip():
                gpu_info.append({"Message": "Onboard GPU detected", "Details": onboard_gpu.stdout.strip()})
            else:
                gpu_info.append({"Message": "No onboard GPU detected."})

    return gpu_info

def get_os_info():
    os_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "OS Release": platform.release(),
        "Architecture": platform.architecture(),
        "Node": platform.node()
    }
    return os_info

def get_disk_info():
    disk_info = {
        "Total Disk Space (GB)": round(psutil.disk_usage('/').total / (1024 ** 3), 2),
        "Used Disk Space (GB)": round(psutil.disk_usage('/').used / (1024 ** 3), 2),
        "Free Disk Space (GB)": round(psutil.disk_usage('/').free / (1024 ** 3), 2),
        "Disk Usage (%)": psutil.disk_usage('/').percent
    }
    return disk_info

def get_network_info():
    network_info = psutil.net_if_addrs()
    return {iface: [addr.address for addr in addrs] for iface, addrs in network_info.items()}

def get_system_status():
    return {
        "CPU": get_cpu_info(),
        "RAM": get_ram_info(),
        "GPU": get_gpu_info(),
        "OS": get_os_info(),
        "Disk": get_disk_info(),
        "Network": get_network_info()
    }

def print_status(status):
    for category, info in status.items():
        print(f"{category}:")
        if isinstance(info, list):
            for item in info:
                for key, value in item.items():
                    print(f"  {key}: {value}")
        else:
            for key, value in info.items():
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                elif isinstance(value, list):
                    print(f"  {key}:")
                    for val in value:
                        print(f"    - {val}")
                else:
                    print(f"  {key}: {value}")
        print()  # Add a blank line between sections
