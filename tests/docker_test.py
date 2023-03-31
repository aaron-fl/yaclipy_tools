import pytest
from print_ext import Printer
from yaclipy_tools.all import Docker
from yaclipy_tools.docker import DockerNotRunning
from .testutil import get_tool


@pytest.mark.asyncio
async def test_docker():
    docker = await get_tool(Docker(20))
    assert( await docker.image_id('1') == None)
    containers = list(await docker.containers())
    Printer().pretty(containers)
