import os
import re
import shutil
import ipaddress
from datetime import datetime

ZONE_CONFIG_PATH = "/etc/bind/named.conf.local"
BACKUP_DIR = "/etc/bind/zone_backups"
ZONE_FILE_PATH = None

VALID_RECORD_TYPES = {"A", "AAAA", "CNAME", "MX", "TXT", "NS", "PTR", "SRV"}

def is_valid_domain(name):
    return re.match(r"^[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$", name)

def is_valid_ip(ip):
    return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip)

def is_valid_ipv6(ip):
    try:
        ipaddress.IPv6Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

def list_zones():
    zones = {}
    with open(ZONE_CONFIG_PATH, "r") as config_file:
        for line in config_file:
            if "zone" in line and "{" in line:
                match = re.search(r'zone\s+"([^"]+)"', line)
                if match:
                    zone_name = match.group(1)
                    zones[zone_name] = None
            elif "file" in line and zones:
                match = re.search(r'file\s+"([^"]+)"', line)
                if match:
                    zone_file = match.group(1)
                    last_zone = list(zones.keys())[-1]
                    zone_file = os.path.join("/etc/bind", zone_file) if not zone_file.startswith("/") else zone_file
                    zones[last_zone] = zone_file
    print("📦 Available zones:")
    for idx, (zone, file) in enumerate(zones.items(), 1):
        print(f"{idx}. {zone} -> {file}")
    return zones

def select_zone(zones):
    print("\n🔍 Select a zone by number:")
    try:
        choice = int(input("Enter your choice: ")) - 1
        zone_list = list(zones.items())
        if 0 <= choice < len(zone_list):
            selected_zone = zone_list[choice]
            global ZONE_FILE_PATH
            ZONE_FILE_PATH = selected_zone[1]
            print(f"✅ Selected zone: {selected_zone[0]} ({ZONE_FILE_PATH})")
        else:
            print("❌ Invalid selection.")
    except ValueError:
        print("❌ Please enter a valid number.")

def backup_zone_file():
    if not ZONE_FILE_PATH:
        print("⚠️ No zone selected.")
        return
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(
        BACKUP_DIR, f"{os.path.basename(ZONE_FILE_PATH)}_{timestamp}.bak"
    )
    shutil.copy2(ZONE_FILE_PATH, backup_file)
    print(f"🗂 Backup created: {backup_file}")

def list_records():
    if not ZONE_FILE_PATH:
        print("⚠️ No zone selected.")
        return
    print("📄 Zone file contents:")
    with open(ZONE_FILE_PATH, "r") as zone_file:
        for line in zone_file:
            print(line.strip())

def prompt_srv_details():
    name = input("Enter SRV name (e.g. _sip._tcp): ")
    if not re.match(r"^_[a-zA-Z0-9]+\._(tcp|udp)$", name):
        print("❌ Invalid SRV name format.")
        return None
    value = input("Enter target hostname: ")
    try:
        ttl = int(input("Enter TTL (default 3600): ") or "3600")
        priority = int(input("Enter priority: "))
        weight = int(input("Enter weight: "))
        port = int(input("Enter port: "))
    except ValueError:
        print("❌ Priority, weight, port, and TTL must be integers.")
        return None
    return {
        "name": name,
        "value": value,
        "ttl": ttl,
        "priority": priority,
        "weight": weight,
        "port": port
    }

def preview_record(record):
    print("\n👀 Preview:")
    print(record.strip())
    confirm = input("Proceed with adding this record? (y/n): ").lower()
    return confirm == "y"

def add_record(record_type, name, value, ttl=3600, priority=None, weight=None, port=None):
    if not ZONE_FILE_PATH or not os.path.exists(ZONE_FILE_PATH):
        print("⚠️ No valid zone file selected. Please choose a zone first.")
        return

    record_type = record_type.upper()
    if record_type not in VALID_RECORD_TYPES:
        print("❌ Unsupported record type.")
        return

    if record_type == "MX":
        if priority is None:
            print("❌ MX records require a priority value.")
            return
        record = f"{name}\t{ttl}\tIN\tMX\t{priority} {value}\n"
    elif record_type == "TXT":
        value = f'"{value}"'
        record = f"{name}\t{ttl}\tIN\tTXT\t{value}\n"
    elif record_type == "SRV":
        if None in (priority, weight, port):
            print("❌ SRV records require priority, weight, and port.")
            return
        record = f"{name}\t{ttl}\tIN\tSRV\t{priority} {weight} {port} {value}\n"
    elif record_type == "AAAA":
        if not is_valid_ipv6(value):
            print("❌ Invalid IPv6 address.")
            return
        record = f"{name}\t{ttl}\tIN\tAAAA\t{value}\n"
    else:
        record = f"{name}\t{ttl}\tIN\t{record_type}\t{value}\n"

    if not preview_record(record):
        print("🚫 Record addition cancelled.")
        return

    backup_zone_file()
    with open(ZONE_FILE_PATH, "a") as zone_file:
        zone_file.write(record)
    print(f"✅ Record added: {record.strip()}")
    update_serial()
def delete_record():
    if not ZONE_FILE_PATH:
        print("⚠️ No zone selected.")
        return
    list_records()
    target = input("Enter the exact line to delete: ").strip()
    with open(ZONE_FILE_PATH, "r") as zone_file:
        lines = zone_file.readlines()
    if target not in [line.strip() for line in lines]:
        print("❌ Record not found.")
        return
    backup_zone_file()
    with open(ZONE_FILE_PATH, "w") as zone_file:
        for line in lines:
            if line.strip() != target:
                zone_file.write(line)
    print(f"🗑 Record deleted: {target}")
    update_serial()

def update_record():
    if not ZONE_FILE_PATH:
        print("⚠️ No zone selected.")
        return
    list_records()
    target = input("Enter the exact line to update: ").strip()
    with open(ZONE_FILE_PATH, "r") as zone_file:
        lines = zone_file.readlines()
    if target not in [line.strip() for line in lines]:
        print("❌ Record not found.")
        return
    print("✏️ Enter new record details:")
    rtype = input("Record type (A, AAAA, CNAME, MX, TXT, NS, PTR, SRV): ").upper()
    name = input("Record name: ")
    value = input("Record value: ")
    ttl = input("TTL (default 3600): ")
    ttl = int(ttl) if ttl.isdigit() else 3600
    if rtype == "MX":
        priority = int(input("Priority: "))
        new_record = f"{name}\t{ttl}\tIN\tMX\t{priority} {value}\n"
    elif rtype == "SRV":
        priority = int(input("Priority: "))
        weight = int(input("Weight: "))
        port = int(input("Port: "))
        new_record = f"{name}\t{ttl}\tIN\tSRV\t{priority} {weight} {port} {value}\n"
    elif rtype == "TXT":
        new_record = f"{name}\t{ttl}\tIN\tTXT\t\"{value}\"\n"
    elif rtype == "AAAA":
        if not is_valid_ipv6(value):
            print("❌ Invalid IPv6 address.")
            return
        new_record = f"{name}\t{ttl}\tIN\tAAAA\t{value}\n"
    else:
        new_record = f"{name}\t{ttl}\tIN\t{rtype}\t{value}\n"
    if not preview_record(new_record):
        print("🚫 Update cancelled.")
        return
    backup_zone_file()
    with open(ZONE_FILE_PATH, "w") as zone_file:
        for line in lines:
            if line.strip() == target:
                zone_file.write(new_record)
            else:
                zone_file.write(line)
    print(f"✅ Record updated:\n{target} → {new_record.strip()}")
    update_serial()

def update_serial():
    if not ZONE_FILE_PATH:
        return
    with open(ZONE_FILE_PATH, "r") as zone_file:
        lines = zone_file.readlines()
    for i, line in enumerate(lines):
        if "Serial" in line or re.search(r"\d{10}", line):
            match = re.search(r"(\d{10})", line)
            if match:
                old_serial = match.group(1)
                new_serial = datetime.now().strftime("%Y%m%d%H")
                lines[i] = line.replace(old_serial, new_serial)
                print(f"🔄 Serial updated: {old_serial} → {new_serial}")
                break
    with open(ZONE_FILE_PATH, "w") as zone_file:
        zone_file.writelines(lines)

def check_syntax():
    print("🔍 Checking BIND syntax...")
    result = os.system("named-checkconf")
    if result == 0:
        print("✅ named.conf syntax OK.")
    else:
        print("❌ named.conf syntax error.")
    if ZONE_FILE_PATH:
        result = os.system(f"named-checkzone {os.path.basename(ZONE_FILE_PATH)} {ZONE_FILE_PATH}")
        if result == 0:
            print("✅ Zone file syntax OK.")
        else:
            print("❌ Zone file syntax error.")

def reload_bind():
    print("🔄 Reloading BIND service...")
    result = os.system("systemctl reload bind9")
    if result == 0:
        print("✅ BIND reloaded successfully.")
    else:
        print("❌ Failed to reload BIND.")

def main():
    zones = list_zones()
    select_zone(zones)
    while True:
        print("\n🛠 Available actions:")
        print("1. List records")
        print("2. Add record")
        print("3. Delete record")
        print("4. Update record")
        print("5. Check syntax")
        print("6. Reload BIND")
        print("7. Exit")
        choice = input("Choose an action: ").strip()
        if choice == "1":
            list_records()
        elif choice == "2":
            rtype = input("Enter record type (A, AAAA, CNAME, MX, TXT, NS, PTR, SRV): ").upper()
            name = input("Enter record name: ")
            value = input("Enter record value: ")
            ttl = input("Enter TTL (default 3600): ")
            ttl = int(ttl) if ttl.isdigit() else 3600
            if rtype == "MX":
                priority = int(input("Enter priority: "))
                add_record(rtype, name, value, ttl, priority=priority)
            elif rtype == "SRV":
                srv = prompt_srv_details()
                if srv:
                    add_record("SRV", srv["name"], srv["value"], srv["ttl"], srv["priority"], srv["weight"], srv["port"])
            else:
                add_record(rtype, name, value, ttl)
        elif choice == "3":
            delete_record()
        elif choice == "4":
            update_record()
        elif choice == "5":
            check_syntax()
        elif choice == "6":
            reload_bind()
        elif choice == "7":
            print("👋 Exiting DNS Zone Manager.")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
