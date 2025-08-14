import os
import re
import shutil
from datetime import datetime

ZONE_CONFIG_PATH = "/etc/bind/named.conf.local"
BACKUP_DIR = "/etc/bind/zone_backups"
ZONE_FILE_PATH = None

VALID_RECORD_TYPES = {"A", "CNAME", "MX", "TXT", "NS", "PTR"}

def is_valid_domain(name):
    return re.match(r"^[a-zA-Z0-9._-]+\.[a-zA-Z]{2,}$", name)

def is_valid_ip(ip):
    return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip)

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

def add_record(record_type, name, value, ttl=3600, priority=None):
    if not ZONE_FILE_PATH or not os.path.exists(ZONE_FILE_PATH):
        print("⚠️ No valid zone file selected. Please choose a zone first.")
        return

    record_type = record_type.upper()
    if record_type not in VALID_RECORD_TYPES:
        print("❌ Unsupported record type.")
        return

    backup_zone_file()

    if record_type == "MX":
        if priority is None:
            print("❌ MX records require a priority value.")
            return
        record = f"{name}\t{ttl}\tIN\tMX\t{priority} {value}\n"
    elif record_type == "TXT":
        value = f'"{value}"'
        record = f"{name}\t{ttl}\tIN\tTXT\t{value}\n"
    else:
        record = f"{name}\t{ttl}\tIN\t{record_type}\t{value}\n"

    with open(ZONE_FILE_PATH, "a") as zone_file:
        zone_file.write(record)
    print(f"✅ Record added: {record.strip()}")
    update_serial()

def delete_record(name):
    if not ZONE_FILE_PATH or not os.path.exists(ZONE_FILE_PATH):
        print("⚠️ No valid zone file selected. Please choose a zone first.")
        return

    backup_zone_file()
    with open(ZONE_FILE_PATH, "r") as zone_file:
        lines = zone_file.readlines()
    with open(ZONE_FILE_PATH, "w") as zone_file:
        for line in lines:
            if re.match(rf'^{re.escape(name)}\s', line):
                continue
            zone_file.write(line)
    print(f"🧹 Records named '{name}' deleted.")
    update_serial()

def update_record(record_type, name, value, ttl=3600, priority=None):
    delete_record(name)
    add_record(record_type, name, value, ttl, priority)

def update_serial():
    if not ZONE_FILE_PATH:
        print("⚠️ No zone selected.")
        return
    with open(ZONE_FILE_PATH, "r") as zone_file:
        lines = zone_file.readlines()
    for i, line in enumerate(lines):
        if re.match(r'^\s*\d+\s*;\s*serial', line):
            current_serial = int(line.split(";")[0].strip())
            new_serial = max(current_serial + 1, int(datetime.now().strftime("%Y%m%d01")))
            lines[i] = f"{new_serial}\t; serial\n"
            print(f"🔄 Serial updated: {current_serial} → {new_serial}")
            break
    with open(ZONE_FILE_PATH, "w") as zone_file:
        zone_file.writelines(lines)

def check_zone_syntax():
    if not ZONE_FILE_PATH:
        print("⚠️ No zone selected.")
        return False
    zone_name = os.path.basename(ZONE_FILE_PATH).split(".")[0]
    result = os.system(f"named-checkzone {zone_name} {ZONE_FILE_PATH}")
    if result == 0:
        print("✅ Zone syntax is valid.")
        return True
    else:
        print("❌ Zone syntax error. Fix before reload.")
        return False

def reload_bind():
    if not ZONE_FILE_PATH:
        print("⚠️ No zone selected.")
        return
    if not check_zone_syntax():
        return
    if shutil.which("rndc"):
        result = os.system("rndc reload")
        if result == 0:
            print("🔁 BIND reloaded successfully.")
        else:
            print("❌ Failed to reload BIND with rndc.")
    else:
        print("⚠️ 'rndc' not found. Try 'sudo systemctl restart bind9' manually.")
def main():
    while True:
        print("\n🔧 DNS Zone Manager")
        print("1. List zones")
        print("2. Select zone")
        print("3. List records")
        print("4. Add record")
        print("5. Delete record")
        print("6. Update record")
        print("7. Reload BIND")
        print("8. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            zones = list_zones()
        elif choice == "2":
            zones = list_zones()
            select_zone(zones)
        elif choice == "3":
            list_records()
        elif choice == "4":
            record_type = input("Enter record type (A, CNAME, MX, TXT, NS, PTR): ").upper()
            if record_type not in VALID_RECORD_TYPES:
                print("❌ Invalid record type.")
                continue

            name = input("Enter record name: ")
            value = input("Enter record value: ")
            ttl_input = input("Enter TTL (default 3600): ") or "3600"

            try:
                ttl = int(ttl_input)
                if ttl <= 0:
                    raise ValueError
            except ValueError:
                print("❌ Invalid TTL.")
                continue

            if record_type == "MX":
                priority_input = input("Enter MX priority: ")
                try:
                    priority = int(priority_input)
                except ValueError:
                    print("❌ Invalid priority.")
                    continue
                add_record(record_type, name, value, ttl, priority)
            else:
                add_record(record_type, name, value, ttl)

        elif choice == "5":
            name = input("Enter record name to delete: ")
            delete_record(name)

        elif choice == "6":
            record_type = input("Enter record type (A, CNAME, MX, TXT, NS, PTR): ").upper()
            if record_type not in VALID_RECORD_TYPES:
                print("❌ Invalid record type.")
                continue

            name = input("Enter record name: ")
            value = input("Enter new value: ")
            ttl_input = input("Enter TTL (default 3600): ") or "3600"

            try:
                ttl = int(ttl_input)
                if ttl <= 0:
                    raise ValueError
            except ValueError:
                print("❌ Invalid TTL.")
                continue

            if record_type == "MX":
                priority_input = input("Enter MX priority: ")
                try:
                    priority = int(priority_input)
                except ValueError:
                    print("❌ Invalid priority.")
                    continue
                update_record(record_type, name, value, ttl, priority)
            else:
                update_record(record_type, name, value, ttl)

        elif choice == "7":
            reload_bind()

        elif choice == "8":
            print("👋 Goodbye! Exiting DNS Zone Manager.")
            break

        else:
            print("❌ Invalid choice. Please enter a number between 1 and 8.")

if __name__ == "__main__":
    main()
