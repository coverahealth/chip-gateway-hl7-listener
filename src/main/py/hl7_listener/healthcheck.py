from aiohttp import web


async def health_check_handler(request):
    return web.Response(text="Success! Hl7 listener is running.")


async def start_health_check_server():
    app = web.Application()
    app.add_routes([web.get('/ping', health_check_handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner)
    await site.start()
