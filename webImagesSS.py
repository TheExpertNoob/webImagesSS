import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import requests
import io
import sys
import os
import json
from pynput import mouse, keyboard
import tkinter.simpledialog
import tkinter.messagebox
from pathlib import Path

# === DEFAULT SETTINGS ===
DEFAULT_CONFIG = {
    "image_url": "https://gandalfsax.com/images/vg.jpg",  # Replace with your default URL
    "refresh_interval": 60  # seconds
}

def get_config_path():
    home = Path.home()
    config_dir = home / "webImagesSS" # Change if you want a different config folder
    config_dir.mkdir(parents=True, exist_ok=True)
    return str(config_dir / "config.json")

def load_config():
    config_path = get_config_path()
    if not os.path.exists(config_path):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG["image_url"], DEFAULT_CONFIG["refresh_interval"]

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
            return config.get("image_url", DEFAULT_CONFIG["image_url"]), config.get("refresh_interval", DEFAULT_CONFIG["refresh_interval"])
    except Exception:
        return DEFAULT_CONFIG["image_url"], DEFAULT_CONFIG["refresh_interval"]

def save_config(config):
    config_path = get_config_path()
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

class FullscreenImageViewer(tk.Tk):
    def __init__(self, url, interval):
        super().__init__()
        self.url = url
        self.interval = interval * 1000  # milliseconds

        self.attributes('-fullscreen', True)
        self.configure(background='black')
        self.bind("<Escape>", lambda e: self.quit_app())

        self.label = tk.Label(self, bg='black')
        self.label.pack(expand=True, fill=tk.BOTH)

        self.mouse_listener = mouse.Listener(on_move=self.quit_app, on_click=self.quit_app, on_scroll=self.quit_app)
        self.keyboard_listener = keyboard.Listener(on_press=self.quit_app)
        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.refresh_image()

    def quit_app(self, *args):
        try:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
        except Exception:
            pass
        self.destroy()

    def refresh_image(self):
        try:
            headers = {
                "User-Agent": (
                    "Pooh's Web Image Screen Saver" # It would be a crime to change this
                )
            }
            resp = requests.get(self.url, headers=headers, timeout=10)
            resp.raise_for_status()
            img_data = resp.content
            img = Image.open(io.BytesIO(img_data))

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            img = ImageOps.fit(img, (screen_width, screen_height), method=Image.LANCZOS, centering=(0.5, 0.5))

            photo = ImageTk.PhotoImage(img)
            self.label.config(image=photo)
            self.label.image = photo
        except Exception as e:
            self.label.config(text=f"Error loading image:\n{e}", image="", fg="white")
            self.label.image = None

        self.after(self.interval, self.refresh_image)

if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 0 else []

    if "/c" in args:
        url = tk.simpledialog.askstring("Image URL", "Enter image URL:", initialvalue=DEFAULT_CONFIG["image_url"])
        interval = tk.simpledialog.askinteger("Refresh Interval (seconds)", "Enter refresh interval:",
                                              initialvalue=DEFAULT_CONFIG["refresh_interval"], minvalue=1)
        if url and interval:
            save_config({"image_url": url, "refresh_interval": interval})
            tk.messagebox.showinfo("Saved", f"Settings saved to:\n{get_config_path()}")
        sys.exit()

    elif "/p" in args:
        sys.exit()

    else:
        IMAGE_URL, REFRESH_INTERVAL = load_config()
        app = FullscreenImageViewer(IMAGE_URL, REFRESH_INTERVAL)
        app.mainloop()