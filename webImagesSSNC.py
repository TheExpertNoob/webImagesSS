import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import requests
import io
import sys
from pynput import mouse, keyboard
from screeninfo import get_monitors

# This is the no json, hardcoded version. You will need to modify and build yourself.
# I wanted this to build into a Windows PE environment with networking to use as a picture frame.
# Let's see how this works.

# === HARDCODED CONFIGURATION ===
IMAGE_URLS = [
    "https://gandalfsax.com/images/vg.jpg"
]
REFRESH_INTERVAL = 300  # seconds

class FullscreenImageViewer(tk.Toplevel):
    def __init__(self, parent, urls, interval, monitor):
        super().__init__(parent)
        self.urls = urls
        self.url_index = 0
        self.interval = interval * 1000
        self.monitor = monitor

        self.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(background='black')
        self.config(cursor="none")

        self.label = tk.Label(self, bg='black')
        self.label.pack(expand=True, fill=tk.BOTH)

        self.bind("<Escape>", lambda e: self.quit_all())

        self.refresh_image()

    def set_quit_callback(self, quit_fn):
        self.quit_all = quit_fn

    def refresh_image(self):
        try:
            headers = {
                "User-Agent": "Girls SS"
            }
            url = self.urls[self.url_index % len(self.urls)]
            self.url_index += 1

            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content))

            img = ImageOps.fit(img, (self.monitor.width, self.monitor.height), method=Image.LANCZOS, centering=(0.5, 0.5))
            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo
        except Exception as e:
            self.label.config(text=f"Error loading image:\n{e}", image="", fg="white")
            self.label.image = None

        self.after(self.interval, self.refresh_image)

class MultiScreenManager:
    def __init__(self, urls, interval):
        self.urls = urls
        self.interval = interval
        self.windows = []
        self.monitors = get_monitors()

        self.root = tk.Tk()
        self.root.withdraw()

        self.mouse_listener = mouse.Listener(on_move=self.quit_all, on_click=self.quit_all, on_scroll=self.quit_all)
        self.keyboard_listener = keyboard.Listener(on_press=self.quit_all)

    def launch(self):
        for monitor in self.monitors:
            win = FullscreenImageViewer(self.root, self.urls, self.interval, monitor)
            win.set_quit_callback(self.quit_all)
            self.windows.append(win)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.root.mainloop()

    def quit_all(self, *args):
        try: self.mouse_listener.stop()
        except: pass
        try: self.keyboard_listener.stop()
        except: pass
        for win in self.windows:
            try: win.destroy()
            except: pass
        try: self.root.destroy()
        except: pass

if __name__ == "__main__":
    MultiScreenManager(IMAGE_URLS, REFRESH_INTERVAL).launch()