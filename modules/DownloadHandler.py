import os
import sys
from threading import Thread
#sys.path.append('./modules/yt-dlp')
import yt_dlp

def sizeof_fmt(num, suffix="B"):
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

class DownloadThreadHandler(object):
    """Handles download threads, updating the given app using the following functions of the app. \n
    app.log(msg) \n
        is sent the msg for display purposes. \n
    app.addBar(name, bool is_video)\n
        is made to create a progress bar or handler, note that for videos 2 files will be downloaded in order.\n
    app.updateBar(name,progress)\n
        Gives a progress number from 0 to 99 for the progress bar.\n
    app.removeBar(name,code)\n
        Removes the progress bar or handler of the name with a code (-1 = already downloaded, 0 or higher = good download, -2 cancelled, other negative numbers won't give any messages.).\n
    Aside from that it requires a format (for now accepted values are "audio" and "video"), youtube url (the 11 char code at the end of youtube videos), and the name for distinction by the app.
    """    
    def __init__(self, app, format, url, name):
        self.app=app
        self.app.log("Format:"+format)
        self.format=format
        self.url=url
        self.name = name
        self.logger= LogTreater(app, self.name)
        app.addBar(name,(format=="Video" or format=="Default"))
        self.thread = Thread(target=self.run)
        self.thread.start()
    def terminate(self):
        self.thread.exit()
    def run (self):
        if self.format=="Audio":
            format_selector=self.audio_selector
        elif self.format=="Video":
            format_selector=self.video_selector
        else:
            #format_selector=""+self.format.replace("Audio:","").replace("Video:","")
            pass       
            
        if self.format=='Default':
            ydl = yt_dlp.YoutubeDL({
                'logger': self.logger,
                'progress_hooks': [self.downloadProgressHook],
                'paths':{'home':"./Downloads",'temp':'./temp'
                         }
            })
        else:
            ydl = yt_dlp.YoutubeDL({
                'logger': self.logger,
                'progress_hooks': [self.downloadProgressHook],
                'format': format_selector,
                'paths':{'home':"./Downloads"#,'temp':'./temp'
                         }
            })
        try:
            ydl.download(self.url)
        except yt_dlp.utils.DownloadError as e:
             self.app.log("Link "+self.url+" does not exist.")
             self.app.removeBar(self.name,-2)
        except Exception as e:
            self.app.log("ERR")
            if hasattr(e, 'message'):
                self.app.log("Error found.")
                self.app.log(e.message)
                self.app.removeBar( self.name,-2)
                if e.message.startswith("Exception"):
                    self.app.log("Exception found:")
                    self.app.log(e.message)
                if e.message.endswith("has already been downloaded"):
                    self.app.log("File already downloaded.")
                    self.app.removeBar(self.name,-2)
                        
                elif e.message.startswith("FileNotFoundError:"):
                    self.app.log("File not found.")
                    self.app.removeBar(self.name,-2)     
                else:
                    self.app.removeBar( self.name,-2)
                    self.app.log(e.message)
                    raise e 
            else:
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
    def downloadProgressHook(self,d):
        if d['status'] == 'finished':
            
            self.app.removeBar(self.name,1)
        elif d['status'] == 'downloading':
            #filename  = d.get('info_dict').get('_filename')
            percent=" "+sizeof_fmt(int(d['downloaded_bytes']))
            if("total_bytes" in d):
                percent=((int(d['downloaded_bytes'])/int(d['total_bytes']))*100)
            elif("total_bytes_estimate" in d):
                percent=((int(d['downloaded_bytes'])/int(d['total_bytes_estimate']))*100)
            self.app.updateBar(self.name,percent#,filename
                               )
        elif d['status'] == 'error':
            self.app.log("Error found.")

class LogTreater:
    """
    Handles download threads logs, updating the given app using the function "app.log(name+":"+msg)" and handles some errors using "removeBar(name,number)". \n
    """
    def __init__(self,#app,debugTreater=None,infoTreater=None,warningTreater=None,errorTreater=None, params=None):
                 app,name):

        self.app=app
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
            pass
        else:
            self.info(msg)

    def info(self, msg):
        #if (""+msg).endswith("has already been downloaded"):
        #    self.app.removeBar( self.name,1)
        #if (""+msg).endswith(".webm"):
            #filename = (""+msg).split("\\temp\\")[1],
            #os.rename("./Downloads/temp/"+filename, "./Downloads/"+filename)
        #if not (""+msg).startswtih("[download]"):
        self.app.log(self.name+": "+msg)
        #pass

    def warning(self, msg):
        pass

    def error(self, msg):
        self.app.log(self.name+ " "+ msg)
        if (""+msg).startswith("FileNotFoundError:"):
            self.app.removeBar(self.name,1)

