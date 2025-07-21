import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import subprocess
import requests
import io
import sys
from screeninfo import get_monitors

# === HARDCODED SETTINGS ===
IMAGE_URLS = [
    "https://gandalfsax.com/images/girls.jpg"
    ]
REFRESH_INTERVAL = 300  # seconds

class FullscreenImageViewer(tk.Toplevel):
    def __init__(self, parent, urls, interval, monitor):
        super().__init__(parent)
        self.urls = urls
        self.url_index = 0
        self.interval = interval * 1000  # convert to ms
        self.monitor = monitor
        self.geometry(f"{monitor.width}x{monitor.height}+{monitor.x}+{monitor.y}")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.config(cursor="none", background='black')
        self.label = tk.Label(self, bg='black')
        self.label.pack(expand=True, fill=tk.BOTH)
        self.refresh_image()

    def set_quit_callback(self, callback):
        self.quit_all = callback

    def refresh_image(self):
        try:
            url = self.urls[self.url_index % len(self.urls)]
            self.url_index += 1

            headers = {
                "User-Agent": "Girls SS"
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            img = Image.open(io.BytesIO(response.content))
            img = ImageOps.fit(img, (self.monitor.width, self.monitor.height), Image.LANCZOS, centering=(0.5, 0.5))
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

    def launch(self):
        # Global key binding for Ctrl+Shift+C
        self.root.bind_all("<Control-Shift-C>", self.quit_all)
    
        for monitor in self.monitors:
            win = FullscreenImageViewer(self.root, self.urls, self.interval, monitor)
            win.set_quit_callback(self.quit_all)
            self.windows.append(win)
    
        self.root.mainloop()

    def quit_all(self, *args):
        for win in self.windows:
            try: win.destroy()
            except: pass
        try: self.root.destroy()
        except: pass
    
        # Launch Explorer
        try:
            subprocess.Popen(["explorer.exe"])
        except Exception as e:
            print(f"Failed to launch Desktop: {e}")

if __name__ == "__main__":
    MultiScreenManager(IMAGE_URLS, REFRESH_INTERVAL).launch()