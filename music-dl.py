#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter.scrolledtext import ScrolledText
from urllib.request import urlopen
from enum import Enum
import sys
import enum
import json
from pprint import pprint

def printerr(value: str): sys.stderr.write(str(value)+"\n")

isYtdlMissing = False
try:
    from youtube_dl import YoutubeDL
except ImportError:
    isYtdlMissing = True
    printerr("Error: youtube-dl is missing")
    sys.exit(1)

isPILMissing = False
try:
    from PIL import ImageTk
except ImportError:
    isPILMissing = True
    printerr("Error: PIL is missing")
    sys.exit(1)

URL_ENTRY_PLACEHOLDER = "URL"
MAX_THUMBNAIL_WIDTH = 500

def secondsToStr(seconds: str): return "{:>02d}:{:>02d}".format(int(seconds)//60, int(seconds)%60)

class MediaInfo:
    def __init__(self):
        self.clear()

    def clear(self):
        self.isValid      = False
        self.title        = str()
        self.formats      = dict()
        self.description  = str()
        self.thumbnailUrl = str()
        self.durationSec  = int()

class MyLogger():
    def __init__(self):
        self.value = ""

    def debug(self, msg):
        if msg[0] == "{":
            self.value += (msg + "\n")
    def info(self, _):      pass
    def warning(self, _):   pass
    def error(self, _):     pass
    def critical(self, _):  pass
    def log(self, _):       pass
    def exception(self, _): pass

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MusicDL")

        self.boldFont = font.Font(self, weight=font.BOLD)
        self.largeFont = font.Font(self, size=20)

        self.urlEntry = tk.Entry(self, font=self.largeFont, width=30, foreground="gray",
                                 highlightthickness=5, highlightcolor="blue",
                                 borderwidth=5, relief=tk.RIDGE)
        self.urlEntry.pack(side=tk.TOP, pady=10)
        self.urlEntry.insert(tk.END, URL_ENTRY_PLACEHOLDER)
        self.urlEntry.bind("<FocusIn>", self.onUrlEntryFocusIn)
        self.urlEntry.bind("<FocusOut>", self.onUrlEntryFocusOut)
        self.urlEntry.bind("<KeyRelease>", self.onUrlEntryEdit)

        self.mediaInfo = MediaInfo()
        self.mediaInfoFrame = ttk.LabelFrame(self, text="Information")
        self.mediaInfoFrame.pack(side=tk.TOP)
        self.mediaTitleWidget = ttk.Label(self.mediaInfoFrame, font=self.boldFont, text="MusicDL")
        self.mediaTitleWidget.pack(side=tk.TOP)
        self.defaultMediaThumbnail = ImageTk.PhotoImage(data=open("./thumbnail.gif", "rb").read())
        self.mediaThumbnail = self.defaultMediaThumbnail
        self.mediaThumbnailWidget = ttk.Label(self.mediaInfoFrame, image=self.mediaThumbnail)
        self.mediaThumbnailWidget.pack(side=tk.TOP)
        self.mediaLengthWidget = ttk.Label(self.mediaInfoFrame)
        self.mediaLengthWidget.pack(side=tk.TOP)
        self.mediaDescriptionWidget = ScrolledText(self.mediaInfoFrame, width=60, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.mediaDescriptionWidget.pack(side=tk.TOP)

        self.resizable(0, 0)

    def onUrlEntryFocusIn(self, _):
        if self.urlEntry.get() == URL_ENTRY_PLACEHOLDER:
            self.urlEntry.configure(foreground="black")
            self.urlEntry.delete(0, tk.END)

    def onUrlEntryFocusOut(self, _):
        if not self.urlEntry.get():
            self.urlEntry.configure(foreground="gray")
            self.urlEntry.insert(tk.END, URL_ENTRY_PLACEHOLDER)

    def onUrlEntryEdit(self, _):
        self.mediaInfo.clear()
        self.urlEntry.config(background="white")
        self.mediaTitleWidget.config(text="")
        self.mediaThumbnail = self.defaultMediaThumbnail
        self.mediaThumbnailWidget.config(image=self.mediaThumbnail)
        self.mediaLengthWidget.config(text="")
        self.mediaDescriptionWidget.config(state=tk.NORMAL)
        self.mediaDescriptionWidget.delete('1.0', tk.END)
        self.mediaDescriptionWidget.config(state=tk.DISABLED)

        url = self.urlEntry.get().strip()
        if not url:
            self.mediaInfo.isValid = False
            return

        self.urlEntry.config(background="yellow")
        self.update()

        try:
            myLogger = MyLogger()
            with YoutubeDL({"logger": myLogger, "simulate": True, "forcejson": True}) as ytdl:
                _ = ytdl.download([url])
            parsedJson = json.loads(myLogger.value.splitlines()[0])
            pprint(parsedJson)
        except:
            self.urlEntry.config(background="red")
            self.mediaInfo.isValid = False
            return
        else:
            self.urlEntry.config(background="lime")
            self.mediaInfo.isValid = True
            self.mediaInfo.title = parsedJson["title"]
            self.mediaInfo.description = parsedJson["description"]
            self.mediaInfo.durationSec = parsedJson["duration"]
            for thumbnail in sorted(parsedJson["thumbnails"], key=lambda x: x.get("width", 0), reverse=True):
                if thumbnail["width"] <= MAX_THUMBNAIL_WIDTH:
                    self.mediaInfo.thumbnailUrl = thumbnail["url"]
                    break
            self.mediaInfo.formats = parsedJson["formats"]

        self.mediaTitleWidget.config(text=self.mediaInfo.title)
        self.mediaThumbnail = ImageTk.PhotoImage(data=urlopen(self.mediaInfo.thumbnailUrl).read())
        self.mediaThumbnailWidget.config(image=self.mediaThumbnail)
        self.mediaLengthWidget.config(text=secondsToStr(self.mediaInfo.durationSec))
        self.mediaDescriptionWidget.config(state=tk.NORMAL)
        self.mediaDescriptionWidget.insert(tk.INSERT, self.mediaInfo.description)
        self.mediaDescriptionWidget.config(state=tk.DISABLED)

if __name__ == "__main__":
    window = MainWindow()
    window.mainloop()

