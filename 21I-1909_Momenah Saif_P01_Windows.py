import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import random
import re
import string
from datetime import datetime
from bs4 import BeautifulSoup
from multiprocessing import Pool
import requests

network_interface_reg_path = r"HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}"
transport_name_regex = re.compile("{.+}")
mac_address_regex = re.compile(r"([A-Z0-9]{2}[:-]){5}([A-Z0-9]{2})")

def get_user_adapter_choice(connected_adapters_mac):
    for i, option in enumerate(connected_adapters_mac):
        print(f"#{i}: {option[0]}, {option[1]}")

    if len(connected_adapters_mac) <= 1:
        return connected_adapters_mac[0]

    try:
        choice = int(input("Please choose the interface you want to change the MAC address: "))
        return connected_adapters_mac[choice]
    except Exception as e:
        print("Not a valid choice, quitting...")
        exit()

def change_mac_address(adapter_transport_name, new_mac_address):
    output = subprocess.check_output(f"reg QUERY " + network_interface_reg_path.replace("\\\\", "\\")).decode()
    for interface in re.findall(rf"{network_interface_reg_path}\\\d+", output):
        adapter_index = int(interface.split("\\")[-1])
        interface_content = subprocess.check_output(f"reg QUERY {interface.strip()}").decode()
        if adapter_transport_name in interface_content:
            changing_mac_output = subprocess.check_output(f"reg add {interface} /v NetworkAddress /d {new_mac_address} /f").decode()
            print(changing_mac_output)
            break
    return adapter_index

def get_random_mac_address():
    uppercased_hexdigits = ''.join(set(string.hexdigits.upper()))
    return random.choice(uppercased_hexdigits) + random.choice("24AE") + "".join(random.sample(uppercased_hexdigits, k=10))

def disable_adapter(adapter_index):
    disable_output = subprocess.check_output(f"wmic path win32_networkadapter where index={adapter_index} call disable").decode()
    return disable_output

def enable_adapter(adapter_index):
    enable_output = subprocess.check_output(f"wmic path win32_networkadapter where index={adapter_index} call enable").decode()
    return enable_output

class MacChangerGUI:
    def __init__(self, master):
        self.master = master
        master.title("MAC Changer")

        welcome_text = "\n     Welcome to MAC Changer Tool\n"
        developer_info = """
        Developer Name: Momenah Saif
        Roll Number: 21I-1909
        Section: T
        Degree: BS CY-T6
        Campus: Islamabad Campus
        Course Subject: Ethical Hacking
        """

        self.label = tk.Label(master, text=welcome_text + developer_info, justify="left")
        self.label.pack()

        self.sys_info_button = tk.Button(master, text="Display System Information", command=self.display_system_info)
        self.sys_info_button.pack()

        self.current_mac_button = tk.Button(master, text="Display Current MAC Address", command=self.display_current_mac)
        self.current_mac_button.pack()

        self.random_mac_button = tk.Button(master, text="Change MAC Address Randomly", command=self.change_mac_random)
        self.random_mac_button.pack()

        self.manufacturer_mac_button = tk.Button(master, text="Change MAC Address by Manufacturer", command=self.change_mac_by_manufacturer)
        self.manufacturer_mac_button.pack()

        self.scan_network_button = tk.Button(master, text="Scan Network for Connected Devices", command=self.scan_network_devices)
        self.scan_network_button.pack()

        self.reset_mac_button = tk.Button(master, text="Reset MAC Address to Default", command=self.reset_mac)
        self.reset_mac_button.pack()

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

    def display_system_info(self):
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info = f"Current Date and Time: {current_datetime}\n\n"
        self.label.config(text=info)

    def get_connected_adapters_mac_address(self):
        connected_adapters_mac = []
        for potential_mac in subprocess.check_output("getmac").decode().splitlines():
            mac_address = mac_address_regex.search(potential_mac)
            transport_name = transport_name_regex.search(potential_mac)
            if mac_address and transport_name:
                connected_adapters_mac.append((mac_address.group(), transport_name.group()))
        return connected_adapters_mac

    def display_current_mac(self):
        connected_adapters_mac = self.get_connected_adapters_mac_address()
        mac_address, target_transport_name = get_user_adapter_choice(connected_adapters_mac)
        self.label.config(text=mac_address)

    def change_mac_random(self):
        new_mac_address = get_random_mac_address()
        connected_adapters_mac = self.get_connected_adapters_mac_address()
        mac_address, target_transport_name = get_user_adapter_choice(connected_adapters_mac)

        adapter_index = change_mac_address(target_transport_name, new_mac_address)
        print("[+] Changed to:", new_mac_address)
        disable_adapter(adapter_index)
        print("[+] Adapter is disabled")
        enable_adapter(adapter_index)
        print("[+] Adapter is enabled again")
        self.display_current_mac()

    def scan_network_devices(self):
         try:
            output = subprocess.check_output(['arp', '-a']).decode('utf-8')
            self.label.config(text=output)
         except Exception as e:
            self.label.config(text=str(e))

    def reset_mac(self):
        connected_adapters_mac = self.get_connected_adapters_mac_address()
        mac_address, target_transport_name = get_user_adapter_choice(connected_adapters_mac)
        adapter_index = change_mac_address(target_transport_name, " ")
        disable_adapter(adapter_index)
        print("[+] Adapter is disabled")
        enable_adapter(adapter_index)
        print("[+] Adapter is enabled again")
        self.display_current_mac()

    def get_random_mac(self):
        mac = get_random_mac_address()
        return mac

    def fetch_mac_table(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return None

    def parse_mac_table(self, text):
        mac_table = {}
        for line in text.splitlines():
            parts = line.split('\t')
            if len(parts) >= 2:
                mac_table[parts[0]] = parts[1]
        return mac_table

    def search_mac_by_manufacturer(self, mac_table, manufacturer):
        found_mac = None
        for mac, manuf in mac_table.items():
            if manufacturer.lower() in manuf.lower():
                found_mac = mac
                break
        return found_mac

    def complete_mac(self, mac):
        return mac + ':' + ''.join(random.choice('0123456789abcdef') for _ in range(6 - len(mac)))

    def get_manufacturer_mac(self):
        url = "https://gist.githubusercontent.com/aallan/b4bb86db86079509e6159810ae9bd3e4/raw/846ae1b646ab0f4d646af9115e47365f4118e5f6/mac-vendor.txt"
        mac_table_text = self.fetch_mac_table(url)
        if mac_table_text:
            mac_table = self.parse_mac_table(mac_table_text)
            manufacturer = simpledialog.askstring("Select Manufacturer", "Enter the name of the manufacturer:")
            result = self.search_mac_by_manufacturer(mac_table, manufacturer)
            if result:
                random_extension = ''.join(random.choice('0123456789abcdef') for _ in range(6))
                # Extract the OUI part from the result (first 6 characters)
                oui = result[:8]
                mac_address = f"{oui}{random_extension}"
                print("MAC address for manufacturer '{}':".format(manufacturer))
                print(mac_address)
                return mac_address
            else:
                print("No MAC address found for manufacturer '{}'".format(manufacturer))
                return None
        else:
            print("Failed to fetch MAC address table.")
            return None

    def change_mac_by_manufacturer(self):
        new_mac_address = self.get_manufacturer_mac()
        if new_mac_address:
            connected_adapters_mac = self.get_connected_adapters_mac_address()
            mac_address, target_transport_name = get_user_adapter_choice(connected_adapters_mac)

            # Format the new MAC address with '-' separators
            formatted_mac_address = '-'.join([new_mac_address[i:i+2] for i in range(0, len(new_mac_address), 2)])
            
            adapter_index = change_mac_address(target_transport_name, formatted_mac_address)
            #print("[+] Changed to:", new_mac_address)
            disable_adapter(adapter_index)
            print("[+] Adapter is disabled")
            enable_adapter(adapter_index)
            print("[+] Adapter is enabled again")
            self.display_current_mac()
root = tk.Tk()
my_gui = MacChangerGUI(root)
root.mainloop()
