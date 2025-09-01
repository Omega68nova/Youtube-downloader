import sys
sys.path.append('./yt-dlp')
from yt_dlp import YoutubeDL
def sizeof_fmt(num, suffix="B"):
    print(num)
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        print(msg)
        pass

    def warning(self, msg):
        print(msg)
        pass

    def error(self, msg):
        print(msg)
def video_selector(ctx):
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
def audio_selector(ctx):
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

def my_hook2(d):
    if d['status'] == 'finished':
        print("\n")
        print(101)
    if d['status'] == 'downloading':
        percent=" "+sizeof_fmt(int(d['downloaded_bytes']))
        if("total_bytes" in d):
            percent=((int(d['downloaded_bytes'])/int(d['total_bytes']))*100)
        elif("total_bytes_estimate" in d):
            percent=((int(d['downloaded_bytes'])/int(d['total_bytes_estimate']))*100)
        print(int(percent))
    if d['status'] == 'error':
        print("Err")

def main(format,URLS):
    format=sys.argv[1]
    URLS=[sys.argv[2]]
    if format=="audio":
        format_selector=audio_selector
    else:
        format_selector=video_selector
    ydl = YoutubeDL({
        #'logger': MyLogger(),
        'progress_hooks': [my_hook2],
        'format': format_selector
    })
    ydl.download(URLS)


if __name__ == "__main__":
    format=sys.argv[1]
    URLS=[sys.argv[2]]
    if format=="audio":
        format_selector=audio_selector
    else:
        format_selector=video_selector
    ydl = YoutubeDL({
        #'logger': MyLogger(),
        'progress_hooks': [my_hook2],
        'format': format_selector
    })
    ydl.download(URLS)
      