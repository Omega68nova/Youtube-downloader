from tkinter import *
from tkinter.ttk import Combobox,Progressbar
from modules.DownloadHandler import DownloadThreadHandler
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
        format_entry = Combobox(self.root, values = formats,textvariable = self.format,width=87,state='readonly')

        
        url_label = Label(self.root, text = 'URL', font=('calibre',10, 'bold'))
        url_entry = Entry(self.root, textvariable = self.url,width=90)
        
        button = Button(self.root, text='Download', command =self.run)
        buttonClear = Button(self.root, text='Clear logs', command =self.clearLogs)
        self.progressDic={}
        self.progressFrame = Frame(self.root,width=300, height=100)
        format_label.grid(row=0,column=0)
        format_entry.grid(row=0,column=1)
        url_label.grid(row=1,column=0)
        url_entry.grid(row=1,column=1)
        button.grid(row=2,column=1)
        buttonClear.grid(row=4,column=0)
        self.log_widget = tkinter.scrolledtext.ScrolledText(self.root,  font=("consolas", "8", "normal"),width=90)
        self.progressFrame.grid(row=3,column=1)
        self.log_widget.grid(row=4,column=1)

        self.root.mainloop()
    def clearLogs(self):
        self.log_widget.config(state='normal')
        self.log_widget.delete('1.0', tkinter.END)
        self.log_widget.config(state='disabled')
    def run(self):
        thread = Thread(target=self.submitCallBack)
        thread.start()
    
    def getUrlCode(self,linkString):
        """ Gets the 11 char code from the given link if given one, else it returns false. """   
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
            if  not name in self.progressDic:
                #args = ["python", "ytdl.py", format,code]
                #proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
                if  name in self.progressDic:
                    self.log(name+" is already downloading!")
                    handler.terminate()
                handler = DownloadThreadHandler(self,format,code, name)
                
            else:
                 self.log(name+" is already downloading!")
        else:
            self.log("Bad youtube URL.")
            return
        
    def log(self,data):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tkinter.END,data+"\n")
        self.log_widget.see(tkinter.END)  # Scroll to the bottom
        self.log_widget.config(state='disabled')           
    def addBar(self, name,isVideo):
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


if __name__ == "__main__":
    App()
  