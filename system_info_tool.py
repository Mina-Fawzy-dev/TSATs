"""
SYSTEM INFORMATION TOOL
----------------------
This tool shows you information about your computer like:
- CPU (how many cores, how fast, how busy)
- RAM (how much memory you have and how much is being used)
- Disk drives (C:, D:, etc. — how full they are)
- Network (your IP address, how much data you sent/received)
- Windows version
- How long your PC has been running since last restart
- What programs are running right now

How to run this script:
    1. Open Command Prompt or PowerShell
    2. Type: python system_info_tool.py
    3. Press Enter

If you get an error about "No module named psutil", type:
    pip install psutil

We use these libraries:
- psutil    : gets system information (CPU, RAM, disk, processes)
- platform  : tells us the Windows version and build number
- socket    : gets the computer name and IP address
- datetime  : helps us calculate how long the computer has been on
- os        : used to clear the screen
"""

# ============================================================
# IMPORTING LIBRARIES
# ============================================================
# Libraries are like toolboxes. We "import" them so we can use
# the tools inside. Each library gives us different abilities.
import psutil          # psutil = "process and system utilities" — reads CPU, RAM, etc.
import platform        # tells us what operating system we are using
import socket          # lets us find the computer's name and IP address
import datetime        # gives us current date and time
import os              # lets us run system commands like "cls" to clear the screen


def convert_bytes(bytes_amount):
    """
    This function takes a big number (like 8589934592) and turns it
    into something readable (like "8.00 GB").

    Think of it like this:
        - 1024 Bytes = 1 Kilobyte (KB)
        - 1024 KB    = 1 Megabyte (MB)
        - 1024 MB    = 1 Gigabyte (GB)
        - 1024 GB    = 1 Terabyte  (TB)

    Parameters:
        bytes_amount: a number (the raw byte count)

    Returns:
        a string like "8.00 GB"
    """
    # We check each unit (KB, MB, GB, TB) one by one
    # If the number is less than 1024, we stop and show that unit
    for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
        if bytes_amount < 1024:
            # Format to 2 decimal places and add the unit
            return f"{bytes_amount:.2f} {unit}"
        # If it's 1024 or more, divide by 1024 and check the next unit
        bytes_amount = bytes_amount / 1024
    return f"{bytes_amount:.2f} PB"


def clear_screen():
    """
    Clears the terminal so our output starts on a clean screen.
    On Windows we use 'cls', on Mac/Linux we use 'clear'.
    """
    if os.name == 'nt':  # 'nt' means Windows
        os.system('cls')
    else:
        os.system('clear')


def show_cpu_info():
    """
    Shows information about the CPU (Central Processing Unit).
    The CPU is the "brain" of the computer that does all the work.
    """
    print("=" * 55)
    print("CPU (Central Processing Unit) Information")
    print("=" * 55)

    # --- Physical cores vs Logical cores ---
    # Physical cores = actual hardware cores on the chip
    # Logical cores = physical cores + virtual cores (Hyper-Threading)
    # Example: a 4-core CPU with Hyper-Threading shows 8 logical cores
    physical_cores = psutil.cpu_count(logical=False)
    logical_cores = psutil.cpu_count(logical=True)

    print(f"  Physical cores          : {physical_cores}")
    print(f"  Logical cores (threads) : {logical_cores}")

    # --- CPU Frequency (speed) ---
    # psutil.cpu_freq() returns the speed in MHz (Megahertz)
    # Higher MHz means the CPU can do more calculations per second
    cpu_freq = psutil.cpu_freq()
    print(f"  Max Frequency           : {cpu_freq.max} MHz")
    print(f"  Min Frequency           : {cpu_freq.min} MHz")
    print(f"  Current Frequency       : {cpu_freq.current} MHz")

    # --- CPU usage for each core ---
    # percpu=True gives us a list of percentages, one for each core
    print("\n  CPU Usage Per Core:")
    core_usage_list = psutil.cpu_percent(percpu=True)
    # We use a simple counter (index) to show which core we are on
    index = 0
    for percentage in core_usage_list:
        print(f"    Core {index}: {percentage}%")
        index = index + 1

    # --- Total CPU usage (all cores combined) ---
    total_usage = psutil.cpu_percent()
    print(f"\n  Total CPU Usage         : {total_usage}%")
    print()


def show_ram_info():
    """
    Shows information about RAM (Random Access Memory).
    RAM is the computer's short-term memory — it holds data for
    programs that are currently running.
    """
    print("=" * 55)
    print("RAM (Memory) Information")
    print("=" * 55)

    # psutil.virtual_memory() gives us a "memory object" with
    # different properties like total, available, used, percent
    mem = psutil.virtual_memory()

    # Convert the raw numbers to readable strings
    total_bytes = mem.total
    available_bytes = mem.available
    used_bytes = mem.used
    percent_used = mem.percent

    # Call our convert_bytes function to make the numbers readable
    total_display = convert_bytes(total_bytes)
    available_display = convert_bytes(available_bytes)
    used_display = convert_bytes(used_bytes)

    print(f"  Total RAM     : {total_display}")
    print(f"  Available     : {available_display}")
    print(f"  Used          : {used_display}")
    print(f"  Usage %       : {percent_used}%")
    print()


def show_disk_info():
    """
    Shows information about hard drives / SSDs (C: drive, D: drive, etc.).
    We check how big each drive is and how much space is left.
    """
    print("=" * 55)
    print("Disk Information")
    print("=" * 55)

    # psutil.disk_partitions() gives us a list of all drives
    partitions = psutil.disk_partitions()

    # We go through each drive one at a time
    for partition in partitions:
        drive_letter = partition.device     # example: "C:\\"
        filesystem = partition.fstype       # examples: "NTFS", "FAT32"
        mount_point = partition.mountpoint  # example: "C:\\"

        print(f"\n  Drive          : {drive_letter}")
        print(f"  File System    : {filesystem}")
        print(f"  Mount Point    : {mount_point}")

        # Try to get how much space is used/free on this drive
        # Some drives (like empty CD-ROM drives) will give an error
        try:
            disk_usage = psutil.disk_usage(mount_point)

            total_display = convert_bytes(disk_usage.total)
            used_display = convert_bytes(disk_usage.used)
            free_display = convert_bytes(disk_usage.free)

            print(f"  Total Size     : {total_display}")
            print(f"  Used           : {used_display}")
            print(f"  Free           : {free_display}")
            print(f"  Usage %        : {disk_usage.percent}%")
        except PermissionError:
            # This happens for CD/DVD drives, network drives, etc.
            print("  (Cannot read — could be a CD/DVD or external drive)")

    print()


def show_network_info():
    """
    Shows the computer's name, IP address, and how much data
    has been sent/received over the network since the computer
    was turned on.
    """
    print("=" * 55)
    print("Network Information")
    print("=" * 55)

    # --- Computer name and IP address ---
    # Every computer on a network has a name (hostname) and an IP address
    pc_name = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(pc_name)
    except:
        ip_address = "Could not get IP address"

    print(f"  Computer Name  : {pc_name}")
    print(f"  Local IP       : {ip_address}")

    # --- How much data was sent/received ---
    # This counts ALL network activity since the computer booted up
    network_stats = psutil.net_io_counters()
    data_sent = network_stats.bytes_sent
    data_received = network_stats.bytes_recv

    print(f"  Data Sent      : {convert_bytes(data_sent)}")
    print(f"  Data Received  : {convert_bytes(data_received)}")
    print()


def show_os_info():
    """
    Shows information about the Operating System (Windows version).
    """
    print("=" * 55)
    print("Operating System Information")
    print("=" * 55)

    # platform.uname() gives us details about the OS
    os_details = platform.uname()

    print(f"  System  : {os_details.system}")     # tells us "Windows"
    print(f"  PC Name : {os_details.node}")        # computer name on network
    print(f"  Release : {os_details.release}")      # version number (like "10")
    print(f"  Version : {os_details.version}")      # build number (more specific)
    print(f"  Machine : {os_details.machine}")      # tells us "AMD64" (64-bit)
    print()


def show_uptime():
    """
    Shows how long the computer has been running since the last restart.
    We get the time when the computer was turned on (boot time) and
    subtract it from the current time.
    """
    print("=" * 55)
    print("System Uptime")
    print("=" * 55)

    # psutil.boot_time() gives us a timestamp (a number representing
    # when the computer was turned on)
    boot_timestamp = psutil.boot_time()

    # Convert that timestamp to a readable date and time
    boot_datetime = datetime.datetime.fromtimestamp(boot_timestamp)

    # Calculate the difference between now and when the PC booted
    current_time = datetime.datetime.now()
    uptime = current_time - boot_datetime

    print(f"  Last Boot : {boot_datetime}")
    print(f"  Uptime    : {uptime}")
    print()


def show_top_processes():
    """
    Shows the programs (processes) that are using the most CPU right now.
    We look at ALL running programs, sort them by CPU usage, and
    show the top 10.
    """
    print("=" * 55)
    print("Top Processes (sorted by CPU usage)")
    print("=" * 55)

    # We'll store process info in a list
    # Each item will be a simple list: [cpu_percent, process_id, name]
    process_list = []

    # Loop through every running process on the system
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            # Get the info from this process
            process_id = proc.info['pid']
            process_name = proc.info['name']
            cpu_usage = proc.info['cpu_percent']

            # Some processes might return None for cpu_percent
            if cpu_usage is None:
                cpu_usage = 0

            # Add this process to our list
            # We put cpu first so we can sort by it easily
            process_list.append([cpu_usage, process_id, process_name])

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Some system processes are protected — we skip them
            pass

    # Sort the list so the highest CPU usage comes first
    # We use "reverse=True" to go from highest to lowest
    process_list.sort(reverse=True)

    # Print the table header
    print(f"  {'PID':<8} {'Name':<25} {'CPU %':<10}")
    print(f"  {'---':<8} {'----':<25} {'-----':<10}")

    # Show only the top 10 processes
    counter = 0
    for process_data in process_list:
        if counter >= 10:
            break  # stop after 10 processes

        cpu = process_data[0]
        pid = process_data[1]
        name = process_data[2]

        # Make sure name is not longer than 25 characters
        if name and len(name) > 25:
            name = name[:25]

        print(f"  {pid:<8} {name:<25} {cpu:<10}")

        counter = counter + 1

    print()


def main():
    """
    The main function. This is where the program starts running.
    It calls all the other functions one by one.
    """
    # Start with a clean screen
    clear_screen()

    # Print a nice title banner
    print()
    print("+" + "=" * 55 + "+")
    print("|            SYSTEM INFORMATION TOOL                  |")
    print("|   Displays CPU, RAM, Disk, Network, OS, Uptime     |")
    print("+" + "=" * 55 + "+")
    print()

    # Call each function one at a time
    show_cpu_info()
    show_ram_info()
    show_disk_info()
    show_network_info()
    show_os_info()
    show_uptime()
    show_top_processes()

    print("\nDone! All information has been displayed.")
    input("Press ENTER to exit...")


# ============================================================
# This is a special Python trick.
# It checks if this script is being run directly (not imported).
# If we run it directly, it calls the main() function.
# ============================================================
if __name__ == "__main__":
    main()
