# system_status/wifi_status.py
import subprocess

def check_wifi_status():
    try:
        # Run a command to check Wi-Fi status (works for Windows)
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')

        # Variables to store status, SSID, and signal strength
        wifi_status = "Not connected"
        ssid = "N/A"
        signal_strength = "N/A"

        # Check for "State", "SSID", and "Signal" in the output
        for line in output.split('\n'):
            if "State" in line:
                wifi_status = line.split(":")[1].strip()
            if "SSID" in line and "BSSID" not in line:  # Ensure it's the SSID and not BSSID
                ssid = line.split(":")[1].strip()
            if "Signal" in line:
                signal_strength = line.split(":")[1].strip()

        if wifi_status == "connected":
            return f"Status: {wifi_status}, SSID: {ssid}, Signal Strength: {signal_strength}"
        else:
            return "Wi-Fi is not connected"
    except Exception as e:
        return f"Error checking Wi-Fi status: {str(e)}"
