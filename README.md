# webImagesSS
A simple screen saver that shows a web image and refreshes.  
  
## Build
pip install requests pillow pyinstaller pynput  
python -m PyInstaller --noconfirm --onefile --windowed webImagesSS.py  
  
Exe is located in the `\dist` folder.  
Rename extension `.exe` to `.scr` and move to `C:\windows\system32\`.  
Set in your Window's Screensaver dialog box.  
  
## Custom Config
Configure json file if desired. Auto-generated from defaults if it does not exist.  
Located in `C:\Users\<YourUsername>\webImagesSS\config.json`
