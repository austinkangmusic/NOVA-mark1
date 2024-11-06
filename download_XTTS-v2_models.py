import os
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import shutil
import stat
import time
import json

# Load the models from models_list.json
with open('models_list.json', 'r') as file:
    models = json.load(file)

# Dictionary to keep track of download status
download_status = {model: None for model in models}

# Function to locate the XTTS-v2_models directory
def find_or_create_model_dir(start_dir="."):
    """Finds the XTTS-v2_models directory, and creates it if it doesn't exist."""
    for root, dirs, files in os.walk(start_dir):
        if "XTTS-v2_models" in dirs:
            return os.path.join(root, "XTTS-v2_models")
    
    # If the directory is not found, create it
    model_dir_path = os.path.join(start_dir, "XTTS-v2_models")
    try:
        os.makedirs(model_dir_path, exist_ok=True)
        return model_dir_path
    except Exception as e:
        print(f"Error creating XTTS-v2_models directory: {e}")
        exit(1)

# Set the model directory path dynamically
model_dir = find_or_create_model_dir()

def log_message(log_widget, message):
    """Append a message to the log widget in the GUI."""
    log_widget.config(state=tk.NORMAL)  # Enable editing
    log_widget.insert(tk.END, message + "\n")
    log_widget.see(tk.END)  # Auto-scroll to the end
    log_widget.config(state=tk.DISABLED)  # Disable editing

def remove_readonly(func, path, _):
    """Clear the readonly bit and reattempt the removal."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def remove_lock_file(model_path):
    """Removes the git lock file if it exists."""
    lock_file = os.path.join(model_path, ".git", "index.lock")
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except PermissionError as e:
            print(f"Could not remove lock file: {e}")

def remove_model(log_widget, model_name):
    """Removes a specific downloaded model."""
    model_path = os.path.join(model_dir, f"XTTS-v2_{model_name}")
    
    if os.path.exists(model_path):
        # Remove the lock file if present
        remove_lock_file(model_path)

        # Check if the model is being used by another process (e.g., check for .git/index.lock)
        lock_file = os.path.join(model_path, ".git", "index.lock")
        if os.path.exists(lock_file):
            log_message(log_widget, f"{model_name} is currently being used. Please wait until the download is complete.")
            return

        log_message(log_widget, f"Removing {model_name}...")
        try:
            shutil.rmtree(model_path, onerror=remove_readonly)  # This removes the folder and clears read-only files
            log_message(log_widget, f"{model_name} removed successfully!")
        except Exception as e:
            log_message(log_widget, f"Error removing {model_name}: {e}")
    else:
        log_message(log_widget, f"{model_name} not found.")

def download_model(log_widget, model_name, url):
    """Clones a specific model using git."""
    model_path = os.path.join(model_dir, f"XTTS-v2_{model_name}")
    
    if download_status[model_name] == "downloading":
        log_message(log_widget, f"Wait, {model_name} is currently being downloaded!")
        return

    if os.path.exists(model_path):
        log_message(log_widget, f"{model_name} already exists.")
        return

    log_message(log_widget, f"Downloading {model_name}...")
    download_status[model_name] = "downloading"
    
    try:
        subprocess.run(["git", "clone", url, model_path], check=True)
        
        # After download completes, check if the model exists
        time.sleep(5)  # Adding a small delay to allow git to release lock file or any other process
        if os.path.exists(model_path):
            log_message(log_widget, f"{model_name} downloaded successfully!")
            download_status[model_name] = "completed"
        else:
            log_message(log_widget, f"Failed to download {model_name}. Folder not created.")
            download_status[model_name] = "failed"
    except subprocess.CalledProcessError as e:
        log_message(log_widget, f"Failed to download {model_name}. Error: {e}")
        download_status[model_name] = "failed"

def download_selected_models(log_widget):
    selected_models = [model for model, var in model_vars.items() if var.get()]
    if not selected_models:
        log_message(log_widget, "No models selected. Please select at least one model.")
        return

    for model_name in selected_models:
        if download_status[model_name] is None or download_status[model_name] != "downloading":
            download_model(log_widget, model_name, models[model_name])
        else:
            log_message(log_widget, f"Wait, {model_name} is currently being downloaded.")

    log_message(log_widget, "Selected models download completed.")

def download_all_models(log_widget):
    for model_name, url in models.items():
        if download_status[model_name] is None or download_status[model_name] != "downloading":
            download_model(log_widget, model_name, url)
        else:
            log_message(log_widget, f"Wait, {model_name} is currently being downloaded.")

    log_message(log_widget, "All models download completed.")

def remove_selected_models(log_widget):
    selected_models = [model for model, var in model_vars.items() if var.get()]
    if not selected_models:
        log_message(log_widget, "No models selected for removal.")
        return

    for model_name in selected_models:
        if download_status[model_name] == "downloading":
            log_message(log_widget, f"Stopping download of {model_name}...")
            download_status[model_name] = "cancelled"
        remove_model(log_widget, model_name)

    log_message(log_widget, "Selected models removal completed.")

def run_in_thread(target, *args):
    """Runs a target function in a separate thread to avoid blocking the GUI."""
    thread = threading.Thread(target=target, args=args)
    thread.start()

def create_gui():
    window = tk.Tk()
    window.title("XTTS-v2 Model Downloader")
    window.geometry("600x500")
    window.config(bg="#2C2C2C")
    
    # Header Label
    header = tk.Label(window, text="XTTS-v2 Model Downloader", font=("Arial", 16), fg="#FFFFFF", bg="#2C2C2C")
    header.pack(pady=10)

    # Model Selection Checkboxes
    global model_vars
    model_vars = {model: tk.BooleanVar() for model in models}

    frame = tk.Frame(window, bg="#2C2C2C")
    frame.pack(pady=10)
    
    for model_name, var in model_vars.items():
        chk = tk.Checkbutton(frame, text=model_name, variable=var, font=("Arial", 12), fg="#FFFFFF", bg="#2C2C2C", selectcolor="#444444", activebackground="#444444")
        chk.pack(anchor='w')

    # Buttons
    button_frame = tk.Frame(window, bg="#2C2C2C")
    button_frame.pack(pady=10)

    download_button = tk.Button(button_frame, text="Download Selected", font=("Arial", 12), 
                                command=lambda: run_in_thread(download_selected_models, log_widget), 
                                bg="#4CAF50", fg="#FFFFFF", activebackground="#45A049")
    download_button.grid(row=0, column=0, padx=10)

    download_all_button = tk.Button(button_frame, text="Download All", font=("Arial", 12), 
                                    command=lambda: run_in_thread(download_all_models, log_widget), 
                                    bg="#008CBA", fg="#FFFFFF", activebackground="#007BB5")
    download_all_button.grid(row=0, column=1, padx=10)

    remove_button = tk.Button(button_frame, text="Remove Selected", font=("Arial", 12), 
                              command=lambda: run_in_thread(remove_selected_models, log_widget), 
                              bg="#f44336", fg="#FFFFFF", activebackground="#da190b")
    remove_button.grid(row=0, column=2, padx=10)

    # Logs Textbox
    log_widget = scrolledtext.ScrolledText(window, width=70, height=15, font=("Arial", 10), state=tk.DISABLED, bg="#333333", fg="#FFFFFF")
    log_widget.pack(pady=20)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
