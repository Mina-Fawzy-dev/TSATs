"""
PC HEALTH MONITOR
-----------------
This tool watches your computer's health and alerts you if something
is running too hot or too full. It checks:

- CPU usage: how busy the processor is
- RAM usage: how much memory is being used
- Disk usage: how full your hard drives are
- Temperature: how hot your computer is (if sensors are available)

Every check is saved to a LOG FILE so you can look back at what happened.

How to run this script:
    1. Open Command Prompt or PowerShell
    2. Type: python pc_health_monitor.py
    3. Press Enter

If you get an error about "No module named psutil", type:
    pip install psutil

We use these libraries:
- psutil    : reads CPU, RAM, disk, and temperature from the system
- datetime  : gives us the current date and time for our log
- time      : lets us pause between checks so we don't spam the screen
- platform  : gets the computer name for the log file
- os        : tells us where the log file is saved
"""

# ============================================================
# IMPORTING LIBRARIES
# ============================================================
import psutil           # Reads system stats (CPU %, RAM %, disk space, temp)
import datetime         # Gets current date and time for our log entries
import time             # Lets us wait (sleep) between each health check
import platform         # Gets the computer name
import os               # Used to get the full file path for our log


# ============================================================
# SETTINGS — You can change these numbers!
# ============================================================

# --- ALERT THRESHOLDS ---
# If any of these numbers is passed, we show an alert.
# Example: if CPU goes over 80%, we print a warning.
CPU_ALERT_LIMIT = 80      # Alert when CPU usage is above 80%
RAM_ALERT_LIMIT = 85      # Alert when RAM usage is above 85%
DISK_ALERT_LIMIT = 90     # Alert when a disk is more than 90% full

# --- MONITORING SETTINGS ---
CHECK_EVERY = 5           # How many seconds between checks
RUN_FOR_SECONDS = 60      # How long to monitor (0 = run forever)

# --- LOG FILE ---
# This file will be saved in the same folder as this script
LOG_FILE_NAME = "pc_health_log.txt"


# ============================================================
# HELPER FUNCTION: Convert bytes to human-readable format
# ============================================================
def bytes_to_readable(byte_count):
    """
    Takes a big number of bytes and turns it into something
    easy to read like "8.50 GB".

    How it works:
        We keep dividing by 1024 until the number is small enough.
        1024 Bytes = 1 KB
        1024 KB    = 1 MB
        1024 MB    = 1 GB
        1024 GB    = 1 TB

    Parameters:
        byte_count: a number (like 8589934592)

    Returns:
        a string (like "8.00 GB")
    """
    units = ["Bytes", "KB", "MB", "GB", "TB"]

    for unit in units:
        if byte_count < 1024:
            # Format to 2 decimal places and add the unit name
            return f"{byte_count:.2f} {unit}"
        # If still too big, divide by 1024 and try the next unit
        byte_count = byte_count / 1024

    # If it's absolutely huge (petabytes), show PB
    return f"{byte_count:.2f} PB"


# ============================================================
# HELPER FUNCTION: Get the current date/time as a string
# ============================================================
def get_current_time():
    """
    Returns the current date and time formatted nicely.
    We use this for our log file and screen output.

    Returns:
        a string like "2025-01-15 14:30:22"
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# HELPER FUNCTION: Write a message to the log file
# ============================================================
def log_message(message):
    """
    Adds a line of text to the log file.
    Each line starts with the current time in brackets.

    Parameters:
        message: what you want to write to the log
    """
    # Get the current time
    current_time = get_current_time()
    # Format the line like: [2025-01-15 14:30:22] Here is the message
    line_to_write = f"[{current_time}] {message}"

    # Open the file in "append" mode
    # This means we add to the end, we don't erase what's already there
    log_file = open(LOG_FILE_NAME, "a", encoding="utf-8")
    log_file.write(line_to_write + "\n")
    log_file.close()  # Always close files when you are done!


# ============================================================
# HELPER FUNCTION: Write a separator line to the log
# ============================================================
def log_separator():
    """Just writes a line of dashes to the log file to make it easier to read."""
    log_message("-" * 60)


# ============================================================
# FUNCTION: Check CPU usage
# ============================================================
def check_cpu():
    """
    Checks how busy the CPU is right now.
    Returns a number from 0 to 100 (percentage).

    Returns:
        cpu_percent (a number like 45.2)
        over_limit (True or False — is it above the alert limit?)
    """
    # interval=1 means "measure over 1 second"
    cpu_percent = psutil.cpu_percent(interval=1)

    # Check if it's over our limit
    over_limit = False
    if cpu_percent > CPU_ALERT_LIMIT:
        over_limit = True

    return cpu_percent, over_limit


# ============================================================
# FUNCTION: Check RAM usage
# ============================================================
def check_ram():
    """
    Checks how much RAM is being used.
    Returns the percentage, plus some readable numbers.

    Returns:
        percent_used (like 65.3)
        used_readable (like "8.50 GB")
        total_readable (like "16.00 GB")
        over_limit (True or False)
    """
    memory = psutil.virtual_memory()

    percent_used = memory.percent
    used_readable = bytes_to_readable(memory.used)
    total_readable = bytes_to_readable(memory.total)

    # Check if it's over our limit
    over_limit = False
    if percent_used > RAM_ALERT_LIMIT:
        over_limit = True

    return percent_used, used_readable, total_readable, over_limit


# ============================================================
# FUNCTION: Check all disk drives
# ============================================================
def check_disks():
    """
    Checks every disk drive (C:, D:, etc.) and returns how full each one is.

    Returns:
        a list of dictionaries, one for each drive.
        Each dictionary has:
            - drive: the drive letter (like "C:\\")
            - percent: how full it is (%)
            - used: readable used space (like "120.50 GB")
            - free: readable free space (like "879.50 GB")
            - total: readable total size (like "1000.00 GB")
            - over_limit: True if more full than our limit
    """
    all_drives = []  # empty list to start

    partitions = psutil.disk_partitions()

    for partition in partitions:
        drive_letter = partition.device  # something like "C:\\"

        try:
            usage = psutil.disk_usage(drive_letter)

            percent = usage.percent
            used_readable = bytes_to_readable(usage.used)
            free_readable = bytes_to_readable(usage.free)
            total_readable = bytes_to_readable(usage.total)

            over_limit = False
            if percent > DISK_ALERT_LIMIT:
                over_limit = True

            # Add this drive's info to our list
            drive_info = {
                'drive': drive_letter,
                'percent': percent,
                'used': used_readable,
                'free': free_readable,
                'total': total_readable,
                'over_limit': over_limit
            }
            all_drives.append(drive_info)

        except PermissionError:
            # Some drives (like empty CD drives) can't be read
            # That's okay — we just skip them
            pass

    return all_drives


# ============================================================
# FUNCTION: Check temperature (if available)
# ============================================================
def check_temperature():
    """
    Checks the computer's temperature if the hardware supports it.
    Some computers have sensors, some don't.

    Returns:
        a list of temperature readings.
        Each reading has:
            - sensor: what kind of sensor (like "cpu_thermal")
            - label: a friendly name (like "CPU Temp")
            - current: the current temperature in Celsius
    """
    # First check if psutil even HAS temperature reading
    # hasattr checks if an object has a certain function
    can_read_temps = hasattr(psutil, "sensors_temperatures")

    if not can_read_temps:
        return []  # empty list = no temperature data

    raw_temps = psutil.sensors_temperatures()

    if not raw_temps:
        return []  # no temperature sensors found

    readings = []
    for sensor_name, sensor_entries in raw_temps.items():
        for entry in sensor_entries:
            label = entry.label
            current = entry.current
            high = entry.high
            critical = entry.critical

            reading = {
                'sensor': sensor_name,
                'label': label,
                'current': current,
                'high': high,
                'critical': critical
            }
            readings.append(reading)

    return readings


# ============================================================
# FUNCTION: Run ONE health check
# ============================================================
def run_one_check():
    """
    Runs one complete health check — CPU, RAM, disks, temp.
    Shows results on screen AND saves them to the log file.

    Returns:
        had_alert (True if any value was over its limit)
    """
    any_alerts = False

    # --- Show the time of this check ---
    check_time = get_current_time()
    print()
    print("=" * 60)
    print(f"  HEALTH CHECK  |  {check_time}")
    print("=" * 60)
    log_message(f"HEALTH CHECK  |  {check_time}")
    log_separator()

    # --- Check CPU ---
    cpu_percent, cpu_alert = check_cpu()
    print(f"  CPU Usage      : {cpu_percent:.1f}%", end="")
    if cpu_alert:
        print("  ! WARNING — ABOVE " + str(CPU_ALERT_LIMIT) + "%!")
        any_alerts = True
    else:
        print("  [OK]")
    log_message(f"CPU: {cpu_percent:.1f}%")

    # --- Check RAM ---
    ram_percent, ram_used, ram_total, ram_alert = check_ram()
    print(f"  RAM Usage      : {ram_percent:.1f}%  ({ram_used} / {ram_total})", end="")
    if ram_alert:
        print("  ! WARNING — ABOVE " + str(RAM_ALERT_LIMIT) + "%!")
        any_alerts = True
    else:
        print("  [OK]")
    log_message(f"RAM: {ram_percent:.1f}% ({ram_used} / {ram_total})")

    # --- Check Disks ---
    drives = check_disks()
    for drive_info in drives:
        drive_letter = drive_info['drive']
        percent = drive_info['percent']
        used = drive_info['used']
        total = drive_info['total']
        over_limit = drive_info['over_limit']

        print(f"  Disk {drive_letter:<5}: {percent:.1f}%  ({used} / {total})", end="")
        if over_limit:
            print("  ! WARNING — ABOVE " + str(DISK_ALERT_LIMIT) + "%!")
            any_alerts = True
        else:
            print("  [OK]")
        log_message(f"DISK {drive_letter}: {percent:.1f}% ({used} / {total})")

    # --- Check Temperature ---
    temp_readings = check_temperature()
    if len(temp_readings) > 0:
        for reading in temp_readings:
            label = reading['label']
            current_temp = reading['current']
            print(f"  Temperature ({label}): {current_temp:.1f} C")
            log_message(f"TEMP {label}: {current_temp:.1f} C")
    else:
        print(f"  Temperature    : Not available (no sensors detected)")
        log_message("TEMP: Not available")

    # --- Summary ---
    print("=" * 60)
    if any_alerts:
        print("  ! ALERT: One or more values exceeded the safe limit!")
        log_message("STATUS: ALERT")
    else:
        print("  [OK] Everything looks good — all values are normal.")
        log_message("STATUS: OK")
    log_separator()

    return any_alerts


# ============================================================
# MAIN PROGRAM
# ============================================================
def main():
    """
    The main function. This runs the monitoring loop.
    It keeps running until:
        - The time runs out (if you set RUN_FOR_SECONDS)
        - You press Ctrl+C to stop it
    """
    # --- Welcome screen ---
    print()
    print("+" + "=" * 55 + "+")
    print("|                 PC HEALTH MONITOR                   |")
    print("|   Watches CPU, RAM, Disk, Temperature              |")
    print("|   Alerts you if something is wrong                  |")
    print("|   Logs everything to a file                        |")
    print("+" + "=" * 55 + "+")
    print()
    print(f"  Alert Limits:")
    print(f"    CPU  > {CPU_ALERT_LIMIT}%")
    print(f"    RAM  > {RAM_ALERT_LIMIT}%")
    print(f"    Disk > {DISK_ALERT_LIMIT}%")
    print(f"  Checking every {CHECK_EVERY} seconds")

    if RUN_FOR_SECONDS > 0:
        print(f"  Will run for {RUN_FOR_SECONDS} seconds")
    else:
        print(f"  Will run forever (press Ctrl+C to stop)")

    # Show the log file path
    full_log_path = os.path.abspath(LOG_FILE_NAME)
    print(f"  Log file: {full_log_path}")
    print()

    # --- Write session start to log ---
    computer_name = platform.node()
    log_message("=" * 60)
    log_message(f"MONITORING STARTED  |  PC: {computer_name}")
    log_message("=" * 60)

    # --- Start monitoring ---
    start_time = time.time()

    if RUN_FOR_SECONDS > 0:
        end_time = start_time + RUN_FOR_SECONDS
    else:
        end_time = None  # None means "run forever"

    check_number = 0
    alert_number = 0

    # This is the MAIN LOOP — it keeps running until we stop it
    keep_running = True
    while keep_running:
        # Check if we've run long enough
        if end_time is not None:
            current_time = time.time()
            if current_time >= end_time:
                keep_running = False
                break

        check_number = check_number + 1
        print(f"\n  +--- Check #{check_number} {'-' * 40}")

        # Run the health check
        had_alert = run_one_check()
        if had_alert:
            alert_number = alert_number + 1

        # Wait before the next check (but only if we are not done)
        if keep_running:
            print(f"\n  Waiting {CHECK_EVERY} seconds until next check...")
            print("  (Press Ctrl+C to stop now)")
            time.sleep(CHECK_EVERY)

    # --- Session Summary ---
    print()
    print("=" * 60)
    print("  [SUMMARY] SESSION SUMMARY")
    print("=" * 60)
    print(f"    Total checks : {check_number}")
    print(f"    Total alerts : {alert_number}")
    print(f"    Log file     : {full_log_path}")
    print("=" * 60)
    print()

    log_message(f"SESSION ENDED  |  Checks: {check_number}  |  Alerts: {alert_number}")
    log_message("=" * 60)

    print("[DONE] Done!")
    input("Press ENTER to exit...")


# ============================================================
# Start the program only if we run this file directly
# ============================================================
if __name__ == "__main__":
    # This little trick lets us catch Ctrl+C without showing
    # an ugly error message
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOPPED] Stopped by user (Ctrl+C). Goodbye!")
        log_message("MONITORING STOPPED BY USER (Ctrl+C)")
