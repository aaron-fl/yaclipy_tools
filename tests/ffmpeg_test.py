import pytest, pathlib, asyncio
from print_ext import Printer
from yaclipy_tools.all import FFmpeg, Curl
from yaclipy_tools import Echo
from .testutil import get_tool

@pytest.mark.asyncio
async def test_ffmpeg_info_nofile():
    ffmpeg = await get_tool(FFmpeg(5))
    info = await ffmpeg.info('notafile')
    Printer().pretty(info)
    assert(info == None)

    
@pytest.mark.asyncio
async def test_ffmpeg_info_bird():
    ffmpeg = await get_tool(FFmpeg(5))
    curl = await get_tool(Curl(7))
    bird = pathlib.Path('local/birdsong.ogg')
    if not bird.exists():
        #async with Printer().task_group("Download bird song") as tg:
        await curl.download('https://upload.wikimedia.org/wikipedia/commons/7/7c/Turdus_merula_2.ogg', bird).using(Echo(2))()
    info = await ffmpeg.info(bird)
    Printer().pretty(info)
    assert(info['audio']['codec'] == 'vorbis')



    
if __name__=='__main__':
    asyncio.run(test_ffmpeg_info_bird())
