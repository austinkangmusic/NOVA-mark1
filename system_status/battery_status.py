import psutil

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = battery.power_plugged
        status = "Plugged in" if plugged else "On battery"
        return f"Battery is at {percent}% and is {status}."
    else:
        return "Battery information is not available."
