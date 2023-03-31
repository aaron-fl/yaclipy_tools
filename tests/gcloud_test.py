import pytest
from yaclipy_tools.all import GCloud
from print_ext import Printer, StringIO
from yaclipy_tools.gcloud import GCloudProjectError
from .testutil import get_tool


@pytest.mark.asyncio
async def test_gcloud_project():
    gcloud = await get_tool(GCloud())
    
    try:
        p = GCloud(0, 'notaprojects830sdf0239fjsdf')
        await p.ensure()
    except GCloudProjectError as e:
        prt = Printer.using(StringIO)()
        prt.pretty(e)
        print(str(prt))
        assert('notaprojects830sdf0239fjsdf' in str(prt))
