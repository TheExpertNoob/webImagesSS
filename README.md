# webImagesSS
A simple screen saver that shows a web image and refreshes. Built in python because why not.  
Intended for web images that randomly generate or update perodically such as weather radars or other updating photos.
  
## Build
### Requirements
pip install requests pillow pyinstaller pynput  
### Then Build
python -m PyInstaller --noconfirm --onefile --windowed webImagesSS.py  
### After the build completes
Exe is located in the `\dist` folder.  
Rename extension `.exe` to `.scr` and move to `C:\windows\system32\`.  
Set in your Window's OS Screensaver dialog box.  

  
## Custom Config
Settings button in the Screensaver dialog now works properly.
Configure json file if desired. Auto-generated from defaults if it does not exist.  
Located in `C:\Users\<YourUsername>\webImagesSS\config.json`
