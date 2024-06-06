import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import urllib.request
import json
import platform
import time

def start_stop_button_click():
    global ngrok_process
    if start_stop_button["text"] == "Start":
        port = port_entry.get()
        type = type_combobox.get()
        if port and type:
            ngrok_process = start_ngrok(port, type.lower())
            ngrok_url = get_ngrok_url()
            if ngrok_url:
                copy(ngrok_url)
                print("Copied ngrok url to clipboard: " + ngrok_url)
                messagebox.showinfo("Copied", "Ngrok URL copied to clipboard.")
                lock_fields()
                start_stop_button["text"] = "Stop"
                start_stop_button["command"] = stop_ngrok
            else:
                print("Failed to get ngrok URL.")
                messagebox.showinfo("Error", "Failed to get ngrok URL.")
        else:
            print("Port and type are required.")
            messagebox.showinfo("Error", "Port and type are required.")
    else:
        stop_ngrok()

def start_ngrok(port, type):
    global ngrok_process
    print("Starting ngrok with port: " + str(port) + ", type: " + str(type))
    ngrok_process = subprocess.Popen(['ngrok', str(type), str(
        port)], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(2)
    return ngrok_process

def stop_ngrok():
    global ngrok_process
    if ngrok_process:
        print("Killing ngrok")
        if platform.system() == "Windows":
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(ngrok_process.pid)],
                           shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['kill', '-9', str(ngrok_process.pid)], shell=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ngrok_process = None
        unlock_fields()
        start_stop_button["text"] = "Start"
        start_stop_button["command"] = start_stop_button_click

def get_ngrok_url():
    with urllib.request.urlopen("http://localhost:4040/api/tunnels") as response:
        data = response.read()
    datajson = json.loads(data)
    ngrok_urls = [tunnel['public_url'] for tunnel in datajson['tunnels']]
    ngrok_urls = [url.replace("tcp://", "") for url in ngrok_urls]
    return ngrok_urls[0] if ngrok_urls else None

def copy(txt):
    if platform.system() == "Windows":
        cmd = 'echo ' + txt.strip() + ' | clip'
    elif platform.system() == "Darwin":
        cmd = 'echo ' + txt.strip() + ' | pbcopy'
    elif platform.system() == "Linux":
        cmd = 'echo ' + txt.strip() + ' | xclip'
    subprocess.check_call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def lock_fields():
    port_entry.configure(state='disabled')
    type_combobox.configure(state='disabled')

def unlock_fields():
    port_entry.configure(state='normal')
    type_combobox.configure(state='readonly')
    
def validate_port_input(action, value_if_allowed):
    if action == "1":  # insert
        if not value_if_allowed.isdigit():
            return False
        if int(value_if_allowed) > 65535:
            return False
    return True


root = tk.Tk()
root.title("Ngrok GUI")
root.iconbitmap("icon.ico")
root.geometry("200x125")
root.resizable(False, False)

style = ttk.Style()
style.configure("TButton", padding=(10, 5))
style.configure("TLabel", padding=(0, 5))

port_validate_cmd = root.register(validate_port_input)

port_label = ttk.Label(root, text="Port:")
port_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

port_entry = ttk.Entry(root, validate="key", validatecommand=(port_validate_cmd, "%d", "%P"))
port_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

type_label = ttk.Label(root, text="Type:")
type_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

type_combobox = ttk.Combobox(root, values=["HTTP", "TCP"], state="readonly")
type_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="we")
type_combobox.current(0)

start_stop_button = ttk.Button(root, text="Start", command=start_stop_button_click)
start_stop_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="we")

root.mainloop()
