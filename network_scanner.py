"""
NETWORK SCANNER
---------------
This tool helps you find out what devices are connected to your network.
It can:
- Find all devices on your local network (like phones, other PCs, printers)
- Check if devices respond to "ping" (are they alive?)
- Look at common ports (like web servers, file sharing, etc.)
- Look up the hostname of each device

How to run this script:
    1. Open Command Prompt or PowerShell AS ADMINISTRATOR
       (Right-click -> Run as administrator)
    2. Type: python network_scanner.py
    3. Press Enter

Why Admin? Because scanning the network needs special permissions.

If you get errors about missing libraries, type these commands:
    pip install scapy
    pip install python-nmap
    (You also need to install Nmap from https://nmap.org/download.html)

We use these libraries:
- ipaddress  : helps us figure out the network range (like 192.168.1.0/24)
- socket     : checks if ports are open, looks up hostnames
- subprocess : runs system commands like "ping" and "ipconfig"
"""

# ============================================================
# IMPORTING LIBRARIES
# ============================================================
import ipaddress         # Helps us work with IP addresses and network ranges
import socket            # Lets us connect to devices and check ports
import subprocess        # Lets us run commands like "ping" from our script
import sys               # Gives us system info (used to check if we are on Windows)


# ============================================================
# FUNCTION 1: Find our network range
# ============================================================
def find_network_range():
    """
    This function figures out what IP addresses are on our network.
    For example, if your IP is 192.168.1.5 and your subnet mask is
    255.255.255.0, then your network includes IPs from 192.168.1.1
    to 192.168.1.254.

    We do this by:
        1. Connecting to Google's DNS server (8.8.8.8) to find our IP
        2. Running "ipconfig" to get our subnet mask
        3. Combining them to get the network range

    Returns:
        a string like "192.168.1.0/24"
    """
    print("[*] Finding your network range...")

    # --- Step 1: Get our own IP address ---
    # We create a temporary connection to figure out our IP
    # We don't send any real data — just "reserving" a path
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        # Connect to Google's DNS server (port 80)
        temp_socket.connect(("8.8.8.8", 80))
        our_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        print(f"[*] Your IP address is: {our_ip}")
    except Exception as e:
        print(f"[!] Could not detect IP: {e}")
        print("[!] Using default network 192.168.1.0/24")
        return "192.168.1.0/24"

    # --- Step 2: Get the subnet mask from ipconfig ---
    # We run "ipconfig" and look for our IP address, then
    # find the subnet mask on the line right after
    try:
        ipconfig_output = subprocess.check_output("ipconfig", shell=True, text=True)
        lines = ipconfig_output.splitlines()

        subnet_mask = None
        found_our_ip = False

        for line in lines:
            # Check if this line contains our IP
            if our_ip in line:
                found_our_ip = True
                continue

            # If we found our IP in the previous line, look for subnet mask
            if found_our_ip and "Subnet Mask" in line:
                # Split the line on ":" and take the last part
                parts = line.split(":")
                subnet_mask = parts[-1].strip()
                break

        if subnet_mask:
            print(f"[*] Subnet mask is: {subnet_mask}")

            # Convert subnet mask (like 255.255.255.0) to a number
            # 255.255.255.0 = 24 bits (called /24)
            # We count how many "1" bits are in the mask
            octets = subnet_mask.split(".")
            bits_count = 0
            for octet in octets:
                # Convert to int, then to binary, count the 1s
                octet_int = int(octet)
                binary = bin(octet_int)
                # bin() gives something like '0b11111111'
                # We count how many "1" characters are in it
                bits_count = bits_count + binary.count("1")

            network_range = f"{our_ip}/{bits_count}"
            network = ipaddress.IPv4Network(network_range, strict=False)
            print(f"[*] Full network range: {network}")
            return str(network)
        else:
            print("[!] Could not find subnet mask in ipconfig")
    except Exception as e:
        print(f"[!] Error reading ipconfig: {e}")

    # If everything failed, use a common home network range
    print("[!] Using default network 192.168.1.0/24")
    return "192.168.1.0/24"


# ============================================================
# FUNCTION 2: Ping a single device
# ============================================================
def ping_device(ip_address):
    """
    Pings one IP address to see if the device is alive.
    "Ping" sends a small packet of data and waits for a reply.
    If we get a reply, the device is online.

    Parameters:
        ip_address: the IP to ping (like "192.168.1.1")

    Returns:
        True if the device replied, False if it didn't
    """
    # On Windows, the ping command is:
    #   ping -n 1 -w 1000 192.168.1.1
    #   -n 1 means "send 1 packet"
    #   -w 1000 means "wait 1000 milliseconds (1 second)"
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", ip_address],
            capture_output=True,
            text=True,
            timeout=5,  # stop waiting after 5 seconds
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        # If we see "TTL=" in the output, the ping worked
        # TTL = "Time To Live" — it's a number in the reply packet
        if "TTL=" in result.stdout:
            return True
        else:
            return False
    except:
        return False


# ============================================================
# FUNCTION 3: ARP Scan (finds devices on the network)
# ============================================================
def arp_scan(network_range):
    """
    This is the main function that finds devices on the network.
    It uses ARP (Address Resolution Protocol).

    How ARP works:
        Your computer sends out a message saying "Who has this IP?"
        Every device that is alive will reply "I have it! Here is my MAC address."
        MAC address is a unique hardware ID burned into every network card.

    We use a library called "scapy" to send these ARP messages.

    Parameters:
        network_range: like "192.168.1.0/24"

    Returns:
        a list of devices, where each device is a dictionary with 'ip' and 'mac'
    """
    print("\n[*] Scanning for devices using ARP...")
    print("[*] This sends a 'who has this IP?' message to every address.")

    # Try to use scapy — if it's not installed, we use a slower method (ping)
    try:
        # Import scapy — this might fail if scapy is not installed
        from scapy.all import ARP, Ether, srp
    except ImportError:
        print("[!] Scapy is not installed!")
        print("[!] Run: pip install scapy")
        print("[!] Falling back to ping sweep (slower method)...")
        return ping_sweep(network_range)

    # Create an ARP request packet
    # pdst = "protocol destination" = the IP range we want to ask about
    arp_request = ARP(pdst=network_range)

    # Wrap it in an Ethernet frame
    # dst="ff:ff:ff:ff:ff:ff" = broadcast address (send to everyone)
    ethernet_frame = Ether(dst="ff:ff:ff:ff:ff:ff")

    # Combine them into one packet
    full_packet = ethernet_frame / arp_request

    # Send the packet and collect responses
    # srp = "send and receive packets"
    # timeout=3 means we wait 3 seconds for everyone to reply
    # verbose=0 means we don't show scapy's own messages
    print("[*] Sending ARP requests... please wait 3 seconds.")
    result_list = srp(full_packet, timeout=3, verbose=0)[0]

    # Go through each response and save the device info
    found_devices = []
    for sent_packet, received_packet in result_list:
        device_ip = received_packet.psrc   # the IP that replied
        device_mac = received_packet.hwsrc  # the MAC address of that device
        found_devices.append({'ip': device_ip, 'mac': device_mac})

    # Sort devices by IP address so they are in order
    # IPs like 192.168.1.1, 192.168.1.2, etc.
    found_devices.sort(key=lambda device: device['ip'])

    return found_devices


# ============================================================
# FUNCTION 4: Ping Sweep (backup method if scapy is not available)
# ============================================================
def ping_sweep(network_range):
    """
    This is a fallback method if scapy is not installed.
    It simply pings EVERY IP address in the network range, one by one.

    This is slower (254 pings for a typical network) but doesn't
    need any special libraries.

    Parameters:
        network_range: like "192.168.1.0/24"

    Returns:
        a list of devices, where each device is a dictionary with 'ip'
    """
    print("\n[*] Starting ping sweep (this will take a while)...")
    print("[*] Pinging each IP address one at a time...")

    # Convert "192.168.1.0/24" into a list of all IPs
    network = ipaddress.IPv4Network(network_range, strict=False)
    all_ips = list(network.hosts())  # gets all usable IPs (excludes network/broadcast)

    found_devices = []
    total_ips = len(all_ips)
    current_index = 0

    for ip_object in all_ips:
        ip_str = str(ip_object)
        current_index = current_index + 1

        # Show progress so the user knows the script is still working
        print(f"\r[*] Checking {current_index}/{total_ips}  ({ip_str})   ", end="", flush=True)

        if ping_device(ip_str):
            # Device replied to ping — add it to our list
            found_devices.append({'ip': ip_str})

    print()  # add a new line after the progress display
    return found_devices


# ============================================================
# FUNCTION 5: Look up hostname for an IP
# ============================================================
def get_hostname(ip_address):
    """
    Tries to find the name of a device from its IP address.
    This is called "reverse DNS lookup".

    For example, a printer might have the hostname "HP-LaserJet-1234".
    Your router might be called "router.asus.com".

    Parameters:
        ip_address: like "192.168.1.1"

    Returns:
        the hostname (like "my-pc") or "Unknown" if we can't find it
    """
    try:
        hostname, aliases, addresses = socket.gethostbyaddr(ip_address)
        return hostname
    except:
        return "Unknown"


# ============================================================
# FUNCTION 6: Check common ports on a device
# ============================================================
def check_common_ports(ip_address):
    """
    Checks if common ports are open on a device.
    A "port" is like a door into a computer:
        - Port 80  = web server (HTTP)
        - Port 443 = secure web server (HTTPS)
        - Port 21  = FTP (file transfer)
        - Port 22  = SSH (secure remote access)
        - Port 3389 = RDP (Remote Desktop — Windows)

    If a port is "open", it means there's a program listening there.

    Parameters:
        ip_address: which device to check

    Returns:
        a list of port numbers that are open (like [80, 443])
    """
    # List of common ports and what they are used for
    # We store them as [port_number, service_name]
    common_ports = [
        [21,   "FTP"],
        [22,   "SSH"],
        [23,   "Telnet"],
        [25,   "SMTP (Email)"],
        [53,   "DNS"],
        [80,   "HTTP (Web)"],
        [110,  "POP3 (Email)"],
        [139,  "NetBIOS"],
        [443,  "HTTPS (Secure Web)"],
        [445,  "SMB (File Sharing)"],
        [3389, "RDP (Remote Desktop)"],
    ]

    open_ports = []

    for port_info in common_ports:
        port = port_info[0]
        service = port_info[1]

        # Create a TCP socket — this is how we "knock on the door"
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout so we don't wait forever
        sock.settimeout(0.5)

        # Try to connect to the port
        # connect_ex returns 0 if the port is open
        # connect_ex returns an error code if the port is closed
        result = sock.connect_ex((ip_address, port))

        if result == 0:
            open_ports.append(port)
            print(f"      -> Port {port} is OPEN ({service})")

        sock.close()  # always close the socket when done

    return open_ports


# ============================================================
# FUNCTION 7: Show all discovered devices
# ============================================================
def show_devices(device_list):
    """
    Takes the list of discovered devices and displays them nicely
    on the screen. For each device, we also check open ports.

    Parameters:
        device_list: a list of dictionaries, each with 'ip' and optionally 'mac'
    """
    if len(device_list) == 0:
        print("\n[-] No devices found on your network.")
        return

    print(f"\n{'=' * 60}")
    print(f"  Found {len(device_list)} device(s) on your network")
    print(f"{'=' * 60}")

    device_number = 1
    for device in device_list:
        ip = device['ip']
        mac = device.get('mac', 'N/A')  # mac might not exist if we used ping sweep

        # Try to find the hostname
        hostname = get_hostname(ip)

        print(f"\n  Device #{device_number}")
        print(f"  {'-' * 50}")
        print(f"    IP Address   : {ip}")
        print(f"    MAC Address  : {mac}")
        print(f"    Hostname     : {hostname}")

        # Check if the device responds to ping
        ping_result = ping_device(ip)
        if ping_result:
            print(f"    Ping Reply   : Yes")
        else:
            print(f"    Ping Reply   : No")

        # Ask the user if they want to check ports
        print()
        answer = input(f"    Check common ports on {ip}? (y/n): ").strip().lower()
        if answer == "y":
            print(f"\n    Scanning ports on {ip}...")
            open_ports = check_common_ports(ip)
            if len(open_ports) == 0:
                print(f"    No common ports are open.")
            else:
                print(f"\n    Open ports on {ip}: {open_ports}")

        print()
        input("    Press ENTER to see the next device...")
        device_number = device_number + 1


# ============================================================
# MAIN FUNCTION — where the program starts
# ============================================================
def main():
    """
    The main function. This is where everything starts.
    It follows these steps:
        1. Show a welcome message
        2. Find the network range
        3. Scan for devices using ARP (or ping if scapy is missing)
        4. Show the results
    """
    print()
    print("+" + "=" * 55 + "+")
    print("|                 NETWORK SCANNER                     |")
    print("|    Finds devices on your network                    |")
    print("|    Checks open ports and pings hosts                |")
    print("+" + "=" * 55 + "+")
    print()
    print("[TIP] Run this script AS ADMINISTRATOR for best results!")
    print()

    # Step 1: Find our network
    network_range = find_network_range()
    print(f"[*] We will scan: {network_range}")

    # Step 2: Scan for devices (try ARP first, then ping sweep)
    devices = arp_scan(network_range)

    # If ARP didn't find anything, try the ping sweep
    if len(devices) == 0:
        print("\n[-] ARP scan found nothing. Trying ping sweep...")
        devices = ping_sweep(network_range)

    # Step 3: Show the results
    show_devices(devices)

    print("\n✅ Scan complete!")
    input("Press ENTER to exit...")


# ============================================================
# Start the program when this file is run directly
# ============================================================
if __name__ == "__main__":
    main()
