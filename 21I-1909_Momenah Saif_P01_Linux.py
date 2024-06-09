import tkinter as tk
from tkinter import simpledialog, messagebox
import subprocess
import netifaces
import random
import requests
from multiprocessing import Pool
from bs4 import BeautifulSoup

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
        info = subprocess.check_output(['date']).decode('utf-8')
        self.label.config(text=info)

    def display_current_mac(self):
        interfaces = netifaces.interfaces()
        info = ""
        for eth0 in interfaces:
            if eth0 != 'lo':  # Exclude loopback interface
                try:
                    mac = netifaces.ifaddresses(eth0)[netifaces.AF_LINK][0]['addr']
                    info += f"Interface: {eth0}, MAC Address: {mac}\n"
                except:
                    pass
        self.label.config(text=info)

    def change_mac_random(self):
        interfaces = netifaces.interfaces()
        for eth0 in interfaces:
            if eth0 != 'lo':  # Exclude loopback interface
                try:
                    subprocess.call(['sudo', 'ifconfig', eth0, 'down'])
                    subprocess.call(['sudo', 'macchanger', '-r', eth0])
                    subprocess.call(['sudo', 'ifconfig', eth0, 'up'])
                except Exception as e:
                    self.label.config(text=str(e))
        self.display_current_mac()

    def change_mac_by_manufacturer(self):
        mac_address = self.get_manufacturers()
        interfaces = netifaces.interfaces()
        for eth0 in interfaces:
            if eth0 != 'lo':  # Exclude loopback interface
                try:
                    subprocess.call(['sudo', 'ifconfig', eth0, 'down'])
                    subprocess.call(['sudo', 'ifconfig', eth0, 'hw', 'ether', mac_address])
                    subprocess.call(['sudo', 'ifconfig', eth0, 'up'])
                except Exception as e:
                    self.label.config(text=str(e))
        self.display_current_mac()

    def scan_network_devices(self):
        try:
            output = subprocess.check_output(['sudo', 'arp', '-a']).decode('utf-8')
            self.label.config(text=output)
        except Exception as e:
            self.label.config(text=str(e))

    def reset_mac(self):
        interfaces = netifaces.interfaces()
        for eth0 in interfaces:
            if eth0 != 'lo':  # Exclude loopback interface
                try:
                    subprocess.call(['sudo', 'macchanger', '-p', eth0])  # Reset MAC using macchanger
                except Exception as e:
                    self.label.config(text=f"Error resetting MAC for {eth0}: {str(e)}")
        self.display_current_mac()

    def get_random_mac(self):
        mac = [random.choice('0123456789ABCDEF') for _ in range(12)]
        return ':'.join(mac)
        
    def fetch_mac_table(self,url):
        response = requests.get(url)
        if response.status_code == 200:
           return response.text
        else:
            return None

    def parse_mac_table(self,text):
        mac_table = {}
        for line in text.splitlines():
            parts = line.split('\t')
            if len(parts) >= 2:
               mac_table[parts[0]] = parts[1]
        return mac_table

    def search_mac_by_manufacturer(self,mac_table, manufacturer):
        found_mac = None
        for mac, manuf in mac_table.items():
            if manufacturer.lower() in manuf.lower():
               found_mac = mac
               break
        return found_mac

    def complete_mac(mac):
        return mac + ':' + ''.join(random.choice('0123456789abcdef') for _ in range(6 - len(mac)))    

    def get_manufacturers(self):
        #manufacturer = simpledialog.askstring("Select Manufacturer", "Enter the name of the manufacturer:")
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

root = tk.Tk()
my_gui = MacChangerGUI(root)
root.mainloop()
