import glob
import os
from tkinter import *
from tkinter.ttk import Combobox,Progressbar
from modules.DownloadHandler import DownloadThreadHandler
import tkinter.scrolledtext
from threading import Thread


class App(object):
    def __init__(self):
       
        self.root = Tk()
        self.root.title("YT-DLP UI")

        # menu left
        self.menu_left = Frame(self.root, width=50)
        self.menu_left_upper = Frame(self.menu_left, height=150 )
        
        self.url = StringVar(value="")
        self.format = StringVar(value="Default")
        
        self.menu_left_lower = Frame(self.menu_left, width=50)

        self.menu_left_upper.pack(side="top", fill="both", expand=True)
        self.menu_left_lower.pack(side="top", fill="both", expand=True)

        self.menu_left.grid(row=0, column=0, rowspan=3, sticky="nsew")
        #self.some_title_frame.grid(row=0, column=1, sticky="ew")
        #self.canvas_area.grid(row=1, column=1, sticky="nsew") 
        #self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.root.grid_rowconfigure(4, weight=5)
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(1, weight=1)        
        
        
        buttonClear = Button(self.root, text='Clear logs', command =self.clearLogs)
        buttonOpenFolder = Button(self.menu_left_upper, text='Open Folder', command =self.openDownloadFolder)
        

        
        format_label = Label(self.menu_left_upper, text = 'Format', font=('calibre',10, 'bold'))
        format_label.grid(row=0,column=0)
        
        formats = ['Default','Audio', 'Video', #'video:3gp', 'audio:aac', 'audio:flv', 'audio:m4a','audio:mp3','video:mp4','audio:ogg','audio:wav','video:webm']
        ]
        format_entry = Combobox(self.root, values = formats,textvariable = self.format,width=87,state='readonly')
        format_entry.grid(row=0,column=1,sticky="new")
        
        url_label = Label(self.menu_left_upper, text = 'URL', font=('calibre',10, 'bold'))
        
        self.url_entry = Entry(self.root, textvariable = self.url,width=50)
        
        url_label.grid(row=1,column=0)
        
        self.url_entry.bind('<Button-3>',self.popup) 
        self.url_entry.grid(row=1,column=1,sticky="new")
        
        downloadButton = Button(self.root, text='Download', command =self.run)
        downloadButton.grid(row=2,column=1,sticky="new")
        
        buttonOpenFolder.grid(row=3,column=0)
        
        buttonClear.grid(row=4,column=0)
        self.log_widget = tkinter.scrolledtext.ScrolledText(self.root,  font=("consolas", "8", "normal"),width=50, height=8)
        #self.progressFrame.grid(row=1,column=1,sticky="nsew")
        self.log_widget.grid(row=2,column=1,sticky="nsew")
        
        self.progressDic={}
        self.progressFrame = tkinter.scrolledtext.ScrolledText(self.root,font=("consolas", "8", "normal"),width=50,height=5,background="#ababab")
        #Frame(self.root,width=300, height=100)
        self.progressFrame.grid(row=3,column=1,sticky="nsew")
        
        
        self.log_widget.grid(row=4,column=1)

        

        self.menu = Menu(self.root,tearoff=0) # Create a menu
        self.menu.add_command(label='Copy',command=self.copy) # Create labels and commands
        self.menu.add_command(label='Paste',command=self.paste)

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
            
    def openDownloadFolder(self):
        os.startfile(os.path.join(os.getcwd(), "./Downloads"))
            
    def popup(self,event):
            try:
                self.menu.tk_popup(event.x_root,event.y_root) # Pop the menu up in the given coordinates
            finally:
                self.menu.grab_release() # Release it once an option is selected

    def paste(self):
            clipboard = self.root.clipboard_get() # Get the copied item from system clipboard
            self.url_entry.insert('end',clipboard) # Insert the item into the entry widget

    def copy(self):
            inp = self.url_entry.get() # Get the text inside entry widget
            self.root.clipboard_clear() # Clear the tkinter clipboard
            self.root.clipboard_append(inp) # Append to system clipboard
    
    def submitCallBack(self):
        code = self.getUrlCode(self.url.get())
        format = self.format.get()
        name=""
        if(code):
            name = self.format.get()+"["+code+"]"
            if  not name in self.progressDic:
                #args = ["python", "ytdl.py", format,code]
                #proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
                if  name in self.progressDic:
                    self.log(name+" is already downloading!")
                    #handler.terminate()
                handler = DownloadThreadHandler(self,format,code, name)
                
            else:
                 self.log(name+" is already downloading!")
        else:
            #self.log("Bad youtube URL.")
            #return
            #Assuming not a youtube link.
            link =self.url.get()
            name = self.format.get()+"["+link+"]"
            if  not name in self.progressDic:
                #args = ["python", "ytdl.py", format,code]
                #proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
                if  name in self.progressDic:
                    self.log(name+" is already downloading!")
                    #handler.terminate()
                DownloadThreadHandler(self,format,code, name)
                
            else:
                 self.log(name+" is already downloading!")
        
    def log(self,data):
        self.log_widget.config(state='normal')
        self.log_widget.insert(tkinter.END,data+"\n")
        self.log_widget.see(tkinter.END)  # Scroll to the bottom
        self.log_widget.config(state='disabled')           
    def addBar(self, name,isVideo):
            downloadGrid=Frame(self.progressFrame, width=150 )
            downloadGrid.columnconfigure(1, weight=1)
            label=Label(downloadGrid, text = name, font=('calibre',10, 'bold'))
            label.grid(row=0,column=0,sticky="nsew")
            def funcClose():
                self.removeBar(name,-2)
                
                
            buttonClose = Button(downloadGrid, text='X', command = funcClose)
            buttonClose.grid(row=0,column=1,sticky="e")
            progress = IntVar()
            progressbar = Progressbar(downloadGrid,variable=progress,length=560)
            progressbar.grid(row=1,column=0,columnspan=2,sticky="ew")
            if isVideo:
                hp=2
            else:
                hp=1
            downloadGrid.pack(side="top", fill="x",expand=True)  
            self.progressDic[name]=[label, progressbar,progress,name,hp,buttonClose,downloadGrid]
    
    def updateBar(self, name,percent):
        if percent==100:
            percent =99.9
        if self.progressDic[name]:
            self.progressDic[name][2].set(percent)

        
    def removeBar(self, name,state):
        



        self.log("RemoveBar called with state "+str(state)+"")
        if state==-1:
            self.log("Media already downloaded.")
        else:
            if name in self.progressDic and self.progressDic[name][4]>0:
                self.progressDic[name][4]-=1
        if state<0 or name in self.progressDic and self.progressDic[name][4]==0:
            #fileset = [f for f in glob.glob("./Downloads/temp/*["+(""+name).split("[")[1].split("]")[0]+"].*")]
 
            #for f in fileset:
            #    try:
            #        os.rename(f, (""+f).replace("/temp",""))
            #    except:
            #        pass
            widgets = self.progressDic.pop(name)
            widgets[0].forget()
            widgets[1].forget()
            widgets[0].destroy()
            widgets[1].destroy()
            widgets[5].destroy()
            widgets[5].destroy()
            widgets[6].destroy()
            if state>-1:
                self.log(name+" finished downloading!")
            elif state == -2:
                self.log(name+" cancelled.")



if __name__ == "__main__":
    App()
  