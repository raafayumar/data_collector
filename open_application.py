import psutil
import subprocess
import os
import time
from get_vayyar import config_vayyar


def is_process_running(process_name):
    """Check if there is any running process that contains the given name."""
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        try:
            if process_name.lower() in proc.info['name'].lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def open_vayyar_executable(executable_path):
    """Open the Vayyar executable file and perform additional initializations."""
    try:
        subprocess.Popen(['cmd', '/c', executable_path], shell=True)
        print(f"{executable_path} has been opened.")
        time.sleep(20)  # Wait for the process to start
        os.system('cls')  # Clear the command line
        config_vayyar()  # Run the configuration function
        time.sleep(5)  # Optional wait for configuration to complete
    except Exception as e:
        print(f"Failed to open {executable_path}: {e}")


def open_vitals_executable(executable_path):
    """Open the Vitals executable file in a new terminal window."""
    try:
        subprocess.Popen(['start', '', executable_path], shell=True)
        print(f"{executable_path} has been opened in a new window.")
    except Exception as e:
        print(f"Failed to open {executable_path}: {e}")


# Define the Vayyar process and its corresponding executable path
vayyar_process = {
    "name": "VayyarInCarEVKEngine.exe",
    "path": r"C:\Vayyar_inCarEVK_v8.7.0\files\RunVayyarInCarEVKEngine.bat"
}

# Define the Vitals process and its corresponding executable path
vitals_process = {
    "name": "VitalSignsRadar_Demo.exe",  # Replace with the actual process name
    "path": r"C:\ti\mmwave_industrial_toolbox_4_9_0\labs\vital_signs\68xx_vital_signs\gui\gui_exe\VitalSignsRadar_Demo.exe"
    # Replace with the actual path to the executable
}


def check_application():
    # Check if the Vayyar process is running and open the executable if it is not
    if not is_process_running(vayyar_process["name"]):
        open_vayyar_executable(vayyar_process["path"])
    else:
        print(f"\n{vayyar_process['name']} is already running.")
    #
    # # Check if the Vitals process is running and open the executable if it is not
    # if not is_process_running(vitals_process["name"]):
    #     open_vitals_executable(vitals_process["path"])
    # else:
    #     print(f"\n{vitals_process['name']} is already running.")
