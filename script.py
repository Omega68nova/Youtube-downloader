import subprocess
import sys
sys.path.append('./yt-dlp')
from yt_dlp import YoutubeDL
from tkinter import *
from tkinter.ttk import Combobox,Progressbar

import tkinter.scrolledtext
from threading import Thread

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
        
    def getUrlCode(self,linkString):
        if("youtu.be/" in linkString):
             linkString = linkString.split("youtu.be/",1)[1]
             if("?" in linkString):
                 linkString= linkString.split("?",1)[0]
        elif("?v=" in linkString):
             linkString = linkString.split("?v=",1)[1]
             if("&" in linkString):
                 linkString= linkString.split("&",1)[0]
        if(linkString.isalnum() and len(linkString)==11):
            return linkString
        else:
            return False
            
            
    def submitCallBack(self):
        code = self.getUrlCode(self.url.get())
        name=""
        if(code):
            name = self.format.get().capitalize()+"["+code+"]"
            args = ["python", "ytdl.py" ,self.format.get(),self.url.get()]
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
            self.addBar(name,self.format.get()=="video",proc)
        else:
            self.log("Bad youtube URL.")
            proc.terminate()
            return
        #URLS = [self.url]
        #ydl = YoutubeDL()
        #ydl.params=[self.format]
        #ydl.download(URLS)     
        
        for line in proc.stdout:
            line=line.strip()
            print(line)
            if line.isdigit():
                self.updateBar(name,int(line))
                if int(line) == 101: self.removeBar(name,1)
            elif line.startswith("Exception".encode('utf-8')):
                self.log(line)
            elif line.endswith("has already been downloaded".encode('utf-8')):
                self.removeBar( name,-1)
            elif line.startswith("FileNotFoundError:".encode('utf-8')):
                self.removeBar(name,1)
    def log(self,data):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tkinter.END,data+"\n")
        self.log_widget.see(tkinter.END)  # Scroll to the bottom
        self.log_widget.config(state='disabled')           
    def addBar(self, name,isVideo,proc):
        if  name in self.progressDic:
            self.log(name+" is already downloading!")
            proc.terminate()
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
            self.progressDic[name]=[label, progressbar,progress,name,hp,buttonClose,proc]
    
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
            widgets[6].terminate()
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
        


        
if __name__ == "__main__":
    App()
  