""" Tests for main.py """
import pytest
import asyncio
from whpa_cdp_hl7_listener_service.main import nc_connect

# TODO: add tests


@pytest.mark.asyncio
async def test_main(mocker):
    print("Test main.py main()...")
    # mocker.patch("nc_connect", return_value=asyncio.??)
    # mocker.patch("hl7_receiver", return_value=??)

