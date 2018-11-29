import win32con, win32api, win32gui
from .system import system
import os

def set_wallpaper(imagepath):
    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,
        "Control Panel\\Desktop",0,win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "2")
    #2拉伸适应桌面,0桌面居中
    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    # targetpath = os.path.join(system.appdatadir, "wallpaper.jpg")
    targetpath = imagepath
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, targetpath, 1+2)
