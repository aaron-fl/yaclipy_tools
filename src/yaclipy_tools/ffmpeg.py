import sys, os, re
from .sys_tool import SysTool
from .config import Config


class FFmpeg(SysTool):
    cmd = Config.var("An absolute pathname to the ffmpeg command", 'ffmpeg')

    @classmethod
    def version(self):
        for line in self.__call__(self, '-version', stdout=True):
            return line.split(' ')[2]


    @classmethod
    def init_once(self, *args):
        self.DUR_RE = re.compile(r"Duration: (\d\d):(\d\d):([0-9.]+),")
        self.VID_RE = re.compile(r"Stream #(\d:\d)\((.*?)\): Video:(.*)")
        self.SIZE_RE = re.compile(r'(\d+)x(\d+).*')
        self.AUDIO_RE = re.compile(r"Stream #(\d:\d).*? Audio:\s*(\w*).*?(\d+) Hz.*?(\d+) kb/s")
        super().init_once(*args)


    @classmethod
    def install_help(self, p):
        return p("$ brew install ffmpeg", pad=-1)


    def process(self, infile, outfile, *args, **kwargs):
        return self('-y', '-i', infile, *args, outfile, **kwargs)


    def info(self, infile, *args, **kwargs):
        info = {}
        for line in self('-i', infile, '-hide_banner', success=[0,1], stderr=True):
            if 'no such file' in line.lower(): return None
            if m:=self.DUR_RE.search(line):
                info['dur'] = int(m[1])*3600 + int(m[2])*60 + float(m[3])
            elif m:=self.VID_RE.search(line):
                parts = m[3].split(',')
                info['video'] = {'codec':parts.pop(0).strip().split(' ')[0]}
                for part in parts:
                    part = part.strip()
                    if sm:=self.SIZE_RE.match(part):
                        info['video']['size'] = [int(sm[1]), int(sm[2])]
                    if part.endswith('fps'):
                        info['video']['fps'] = float(part.split(' ')[0])
                    if part.endswith('kb/s'):
                        info['video']['kbps'] = int(part.split(' ')[0])
            elif m:=self.AUDIO_RE.search(line):
                info['audio'] = {'codec':m[2], 'rate':m[3], 'kbs':m[4]}
        return info
