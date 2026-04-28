import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import requests
import io
import sys
import os
import json
from pynput import mouse, keyboard
from screeninfo import get_monitors
from pathlib import Path
import tkinter.simpledialog
import tkinter.messagebox

# === DEFAULT SETTINGS ===
DEFAULT_CONFIG = {
    "image_urls": [
        "https://gandalfsax.com/images/hw.jpg",
        "https://gandalfsax.com/images/vg.jpg"
    ],
    "portrait_image_urls": [
        "https://gandalfsax.com/images/phw.jpg",
        "https://gandalfsax.com/images/pvg.jpg"
    ],
    "refresh_interval": 300
}

def get_config_path():
    home = Path.home()
    config_dir = home / "webImagesSS"
    config_dir.mkdir(parents=True, exist_ok=True)
    return str(config_dir / "config.json")

def load_config():
    config_path = get_config_path()
    if not os.path.exists(config_path):
        save_config(DEFAULT_CONFIG)
        return (
            DEFAULT_CONFIG["image_urls"],
            DEFAULT_CONFIG["portrait_image_urls"],
            DEFAULT_CONFIG["refresh_interval"]
        )
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            return (
                config.get("image_urls", DEFAULT_CONFIG["image_urls"]),
                config.get("portrait_image_urls", DEFAULT_CONFIG["portrait_image_urls"]),
                config.get("refresh_interval", DEFAULT_CONFIG["refresh_interval"])
            )
    except Exception:
        return (
            DEFAULT_CONFIG["image_urls"],
            DEFAULT_CONFIG["portrait_image_urls"],
            DEFAULT_CONFIG["refresh_interval"]
        )

def save_config(config):
    config_path = get_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

class FullscreenImageViewer(tk.Toplevel):
    def __init__(self, parent, urls, interval, monitor, start_index=0):
        super().__init__(parent)
        self.urls = urls
        self.url_index = start_index
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
                "User-Agent": (
                    "Pooh's WebImage SS" # it would be a crime to change this
                )
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
    def __init__(self, urls, portrait_urls, interval):
        self.urls = urls
        self.portrait_urls = portrait_urls
        self.interval = interval
        self.windows = []
        self.monitors = get_monitors()

        self.root = tk.Tk()
        self.root.withdraw()

        self.mouse_listener = mouse.Listener(on_move=self.quit_all, on_click=self.quit_all, on_scroll=self.quit_all)
        self.keyboard_listener = keyboard.Listener(on_press=self.quit_all)

    def launch(self):
        for i, monitor in enumerate(self.monitors):
            is_portrait = monitor.height > monitor.width
            active_urls = self.portrait_urls if is_portrait else self.urls

            win = FullscreenImageViewer(self.root, active_urls, self.interval, monitor, start_index=i)
            win.set_quit_callback(self.quit_all)
            self.windows.append(win)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.root.mainloop()

    def quit_all(self, *args):
        try:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
        except Exception:
            pass
        for win in self.windows:
            try:
                win.destroy()
            except:
                pass
        try:
            self.root.destroy()
        except:
            pass

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else []

    if len(args) > 0 and args[0].lower().startswith("/c"):
        url_input = tk.simpledialog.askstring(
            "Landscape Image URLs",
            "Enter landscape image URLs (comma-separated):",
            initialvalue=",".join(DEFAULT_CONFIG["image_urls"])
        )
        portrait_url_input = tk.simpledialog.askstring(
            "Portrait Image URLs",
            "Enter portrait image URLs (comma-separated):",
            initialvalue=",".join(DEFAULT_CONFIG["portrait_image_urls"])
        )
        interval = tk.simpledialog.askinteger(
            "Refresh Interval (seconds)",
            "Enter refresh interval:",
            initialvalue=DEFAULT_CONFIG["refresh_interval"],
            minvalue=1
        )
        if url_input and portrait_url_input and interval:
            urls = [u.strip() for u in url_input.split(",") if u.strip()]
            portrait_urls = [u.strip() for u in portrait_url_input.split(",") if u.strip()]
            save_config({
                "image_urls": urls,
                "portrait_image_urls": portrait_urls,
                "refresh_interval": interval
            })
            tk.messagebox.showinfo("Saved", f"Settings saved to:\n{get_config_path()}")
        sys.exit()

    elif len(args) > 0 and args[0].lower().startswith("/p"):
        sys.exit()

    else:
        IMAGE_URLS, PORTRAIT_IMAGE_URLS, REFRESH_INTERVAL = load_config()
        MultiScreenManager(IMAGE_URLS, PORTRAIT_IMAGE_URLS, REFRESH_INTERVAL).launch()
