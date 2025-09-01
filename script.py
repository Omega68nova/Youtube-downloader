import logging
import os
import sys
import threading
sys.path.append('./yt-dlp')
import yt_dlp
from tkinter import *
from tkinter.ttk import Combobox,Progressbar

import tkinter.scrolledtext
from threading import Thread

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

class App(object):
    def __init__(self):
        self.root =Tk()
        self.root.title('YT-DLP UI')

        #self.root.geometry("600x400")
        self.url = StringVar(value="")
        self.format = StringVar(value="video")
        
        format_label = Label(self.root, text = 'Format', font=('calibre',10, 'bold'))
        #format_entry = Entry(self.root, textvariable = self.format)
        
        formats = ['audio', 'video']
        variable = StringVar(self.root)
        variable.set('audio')
        format_entry = Combobox(self.root, values = formats,textvariable = self.format,width=87)

        
        url_label = Label(self.root, text = 'URL', font=('calibre',10, 'bold'))
        url_entry = Entry(self.root, textvariable = self.url,width=90)
        
        button = Button(self.root, text='Download', command =self.run)
        
        self.progressDic={}
        self.progressFrame = Frame(self.root,width=300, height=100)
        format_label.grid(row=0,column=0)
        format_entry.grid(row=0,column=1)
        url_label.grid(row=1,column=0)
        url_entry.grid(row=1,column=1)
        button.grid(row=2,column=1)
        self.log_widget = tkinter.scrolledtext.ScrolledText(self.root,  font=("consolas", "8", "normal"),width=90)
        self.progressFrame.grid(row=3,column=1)
        self.log_widget.grid(row=4,column=1)

        self.root.mainloop()

    def run(self):
        thread = Thread(target=self.submitCallBack)
        thread.start()
    # Gets the 11 char code from the given link if given one, else it returns false.    
    def getUrlCode(self,linkString):
        if("youtu.be/" in linkString):
             linkString = linkString.split("youtu.be/",1)[1]
             if("?" in linkString):
                 linkString= linkString.split("?",1)[0]
        elif("?v=" in linkString):
             linkString = linkString.split("?v=",1)[1]
             if("&" in linkString):
                 linkString= linkString.split("&",1)[0]
        if(len(linkString)==11):
            return linkString
        else:
            return False
            
            
    def submitCallBack(self):
        code = self.getUrlCode(self.url.get())
        format = self.format.get()
        name=""
        if(code):
            name = self.format.get().capitalize()+"["+code+"]"
            #args = ["python", "ytdl.py", format,code]
            #proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
            logger = LogTreater(self, name)
            handler = DownloadHandlerThread(self,format,code,logger)
            self.addBar(name,format=="video",handler)
        else:
            self.log("Bad youtube URL.")
            return
        #URLS = [self.url]
        #ydl = yt_dlp.YoutubeDL()
        #ydl.params=[self.format]
        #ydl.download(URLS)     
    def log(self,data):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tkinter.END,data+"\n")
        self.log_widget.see(tkinter.END)  # Scroll to the bottom
        self.log_widget.config(state='disabled')           
    def addBar(self, name,isVideo,handler):
        if  name in self.progressDic:
            self.log(name+" is already downloading!")
            handler.terminate()
        else:
            label=Label(self.progressFrame, text = name, font=('calibre',10, 'bold'))
            label.pack()
            def funcClose():
                self.removeBar(name,-2)
            buttonClose = Button(self.progressFrame, text='X', command = funcClose)
            buttonClose.pack()
            progress = IntVar()
            progressbar = Progressbar(self.progressFrame,variable=progress,length=560)
            progressbar.pack()
            if isVideo:
                hp=2
            else:
                hp=1
            self.progressDic[name]=[label, progressbar,progress,name,hp,buttonClose]
    
    def updateBar(self, name,percent):
        if percent==100:
            percent =99.9
        if self.progressDic[name]:
            self.progressDic[name][2].set(percent)
        #self.root.update_idletasks()
        
    def removeBar(self, name,state):
        if state==-1:
            self.log("Media already downloaded.")
        else:
            if name in self.progressDic and self.progressDic[name][4]>0:
                self.progressDic[name][4]-=1
        if state<0 or name in self.progressDic and self.progressDic[name][4]==0:
            widgets = self.progressDic.pop(name)
            widgets[0].forget()
            widgets[1].forget()
            widgets[0].destroy()
            widgets[1].destroy()
            widgets[5].destroy()
            widgets[5].destroy()
            
            if state>-1:
                self.log(name+" finished downloading!")
            elif state == -2:
                self.log(name+" cancelled.")
        
class DownloadHandlerThread(object):
    def __init__(self, App, format, url,logger):
        self.App=App
        self.format=format
        self.url=url
        self.logger=logger
        self.name =self.format.capitalize()+"["+self.url+"]"
        self.thread = Thread(target=self.run)
        self.thread.start()
    def run (self):
        if self.format=="audio":
            format_selector=self.audio_selector
        else:
            format_selector=self.video_selector
        ydl = yt_dlp.YoutubeDL({
            'logger': self.logger,
            'progress_hooks': [self.downloadProgressHook],
            'format': format_selector
        })
        try:
            ydl.download(self.url)
        except yt_dlp.utils.DownloadError as e:
             self.App.log("Link "+self.url+" does not exist.")
             self.App.removeBar(self.name,-2)
        except Exception as e:
            if hasattr(e, 'message'):
                message = e.message
                self.App.log(e.message)
                self.App.removeBar( self.name,-2)
                if message.startswith("Exception".encode('utf-8')):
                    self.App.log("Exception found:")
                    self.App.log(d.decode())
                elif message.endswith("has already been downloaded".encode('utf-8')):
                    self.App.log("File already downloaded.")
                    self.App.removeBar(self.name,-1)
                        
                elif message.startswith("FileNotFoundError:".encode('utf-8')):
                    self.App.log("File not found.")
                    self.App.removeBar(self.name,-2)     
                else:
                    self.App.removeBar( self.name,-2)
                    raise e 
            
    def video_selector(self, ctx):
        #""" Select the best video and the best audio that won't result in an mkv.
        #NOTE: This is just an example and does not handle all cases """

        # formats are already sorted worst to best
        formats = ctx.get('formats')[::-1]

        # acodec='none' means there is no audio
        best_video = next(f for f in formats
                        if f['vcodec'] != 'none' and f['acodec'] == 'none')

        # find compatible audio extension
        audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
        # vcodec='none' means there is no video
        best_audio = next(f for f in formats if (
            f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

        # These are the minimum required fields for a merged format
        yield {
            'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
            'ext': best_video['ext'],
            'requested_formats': [best_video, best_audio],
            # Must be + separated list of protocols
            'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
        }
    def audio_selector(self, ctx):
        #""" Select the best video and the best audio that won't result in an mkv.
        #NOTE: This is just an example and does not handle all cases """

        # formats are already sorted worst to best
        formats = ctx.get('formats')[::-1]

        # acodec='none' means there is no audio
        #best = next(f for f in formats if f['vcodec'] == 'none' and f['acodec'] != 'none')

        # find compatible audio extension
        audio_ext = {'mp4': 'm4a'}["mp4"]
        # vcodec='none' means there is no video
        best_audio = next(f for f in formats if (
            'acodec' in f and f['acodec'] != 'none' and not 'vcodec' in f or f['vcodec'] == 'none' and 'ext' in f and f['ext'] == audio_ext))

        # These are the minimum required fields for a merged format
        yield {
            'format_id': f'{best_audio["format_id"]}',
            'ext': 'm4a',
            'requested_formats': [best_audio],
            # Must be + separated list of protocols
            'protocol': f'{best_audio["protocol"]}'
        }
    def terminate(self):
        self.thread.terminate()
    def downloadProgressHook(self,d):
        if d['status'] == 'finished':
            self.App.removeBar(self.name,1)
        elif d['status'] == 'downloading':
            percent=" "+sizeof_fmt(int(d['downloaded_bytes']))
            if("total_bytes" in d):
                percent=((int(d['downloaded_bytes'])/int(d['total_bytes']))*100)
            elif("total_bytes_estimate" in d):
                percent=((int(d['downloaded_bytes'])/int(d['total_bytes_estimate']))*100)
            self.App.updateBar(self.name,percent)
        elif d['status'] == 'error':
            self.App.log("Error found.")

class LogTreater:
    def __init__(self,#App,debugTreater=None,infoTreater=None,warningTreater=None,errorTreater=None, params=None):
                 App,name):
        self.App=App
        self.name=name
        ''' if(not debugTreater is None):
            def debugT (self, msg):
                debugTreater(self, msg, params)
            self.debug=debugT
        if(not infoTreater is None):
            def infoT (self, msg):
                infoTreater(self, msg, params)
            self.info=infoT
        if(not warningTreater is None):
            def warningT (self, msg):
                warningTreater(self, msg, params)
            self.warning=warningT
        if(not errorTreater is None):
            def errorT (self, msg):
                errorTreater(self, msg, params)
            self.error=errorT'''
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        
        if msg.startswith('[debug] '):
            #self.App.log("debug"+msg)
            pass
        else:
            self.info(msg)

    def info(self, msg):
        #self.App.log("Info"+msg)
        if (""+msg).endswith("has already been downloaded"):
            self.App.removeBar( self.name,-1)
        #pass

    def warning(self, msg):
        #self.App.log(msg)
        pass

    def error(self, msg):
        self.App.log(msg)
        if (""+msg).startswith("FileNotFoundError:"):
            self.App.removeBar(self.name,1)


if __name__ == "__main__":
    App()
  