from pythonosc import dispatcher, osc_server
import keyboard
import tkinter as tk
import threading
import argparse
import os

version = "v0.3"

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
    root.title("VRchat_Discord_Mute_Sync "+version)
    #root.iconbitmap("icon.ico")
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    root.iconbitmap(icon_path)
    root.minsize(340, 120)

    global entry
    tk.Label(root, text="Discordのミュートショートカットを入力").pack()
    entry = tk.Entry(root)
    entry.insert(0, current_hotkey)
    entry.pack()

    global label_status
    tk.Button(root, text="設定", command=set_hotkey).pack()
    label_status = tk.Label(root, text=f"設定済み: {current_hotkey}", width=30, anchor="w")
    label_status.pack()

    global label_mute_status
    label_mute_status = tk.Label(root, text="VRChatミュート状態: 不明", width=30, anchor="w")
    label_mute_status.pack()

    

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

    root.after(0, lambda: label_mute_status.config(text=f"VRChatミュート状態: {status_text}", fg=color))

def set_hotkey(): #キー設定
    global current_hotkey
    current_hotkey = entry.get()
    label_status.config(text=f"設定済み: {current_hotkey}")

if __name__ == "__main__":
    main()