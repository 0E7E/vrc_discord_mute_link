from pythonosc import dispatcher, osc_server
import keyboard
import tkinter as tk
from tkinter import font
import threading
import argparse
import os
from tktooltip import ToolTip
import webbrowser

version = "v0.6"

previous_state = None

def main():
    global current_hotkey

    parser = argparse.ArgumentParser(description="VRChat-Discord ミュート同期")
    parser.add_argument("--hotkey", type=str, default="ctrl+shift+alt+m",
                        help="Discord ミュートショートカット (例: ctrl+shift+alt+m)")
    args = parser.parse_args()
    current_hotkey = args.hotkey

    gui_setup()
    osc_server_setup()

    root.mainloop()

def gui_setup():
    global version 
    global root

    root = tk.Tk()
    root.title("VRChat_Discord_Mute_Link "+version)
    #root.iconbitmap("icon.ico")
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    root.iconbitmap(icon_path)
    root.minsize(340, 120)

    tk.Label(root, text="Discordのミュートショートカットを入力").pack()
    
    global entry
    entry = tk.Entry(root)
    entry.insert(0, current_hotkey)
    entry.pack()

    tk.Button(root, text="設定", command=set_hotkey).pack()
    
    global label_status
    label_status = tk.Label(root, text=f"設定済み: {current_hotkey}", width=30, anchor="w")
    label_status.pack()
    ToolTip(label_status,msg="Discrodのショートカットに同じキーコンフィグを設定してください")
    
    global label_mute_status
    label_mute_status = tk.Label(root, text="VRChatミュート状態: 不明", width=30, anchor="w")
    label_mute_status.pack()

    link_font = font.Font(root, family="Segoe UI", size=10, underline=1)
    global label_url
    label_url = tk.Label(root, text="GitHub URL", fg="blue", cursor="hand2", font=link_font)
    label_url.pack(anchor="e",padx=10, pady=5)
    label_url.bind("<Button-1>",open_url)


def open_url(event):
    webbrowser.open("https://github.com/0E7E/vrc_discord_mute_link")

def osc_server_setup():
    disp = dispatcher.Dispatcher()
    disp.map("/avatar/parameters/MuteSelf", mute_state_handler)

    ip = "127.0.0.1"
    port = 9001
    server = osc_server.ThreadingOSCUDPServer((ip, port), disp)
    print(f"OSC server wake. {ip}:{port}")
    threading.Thread(target=server.serve_forever, daemon=True).start()

def mute_state_handler(address, *args): #MuteSelfを受け取った時の関数
    state = args[0]
    global previous_state

    if previous_state == state: #状態が変化したときのみ
        return

    if state == 1.0:
        status_text = "ミュート有効"
        color = "red"
        print("VRChat mic mute enable")
        keyboard.send(current_hotkey)
    elif state == 0.0:
        status_text = "ミュート無効"
        color = "green"
        print("VRChat mic mute disable")
        keyboard.send(current_hotkey)
    else:
        print(f"不明な値: {state}")
        print("VRChat mic mute unknown")
        color ="gray"

    previous_state = state

    root.after(0, lambda: label_mute_status.config(text=f"VRChatミュート状態: {status_text}", fg=color))

def set_hotkey(): #キー設定
    global current_hotkey
    current_hotkey = entry.get()
    label_status.config(text=f"設定済み: {current_hotkey}")

if __name__ == "__main__":
    main()