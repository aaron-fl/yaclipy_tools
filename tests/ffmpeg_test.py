from print_ext import print
from yaclipy_tools.ffmpeg import FFmpeg


def test_ffmpeg_info():
    ffmpeg = FFmpeg()
    info = ffmpeg.info('notafile')
    print.pretty(info)
    assert(info == None)
    

if __name__ == '__main__':
    try:
        test_ffmpeg_info()
    except Exception as e:
        print.pretty(e)
