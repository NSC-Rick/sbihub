"""
SBI Hub multi-app server — one Render service, two Streamlit apps.

Runs both Streamlit apps as child processes and exposes them through a
single reverse proxy on ``$PORT``:

- ``/``        -> SBI Hub shell       (127.0.0.1:8501, light theme, brand
                    accent from ``sbi_hub/config/branding.py``)
- ``/fm``      -> Financial Modeler   (127.0.0.1:8502, ``baseUrlPath=/fm``,
                    original standalone dark theme)

The proxy forwards plain HTTP and WebSocket traffic so Streamlit's
realtime updates work unchanged. Sessions are independent per app —
the Hub and the Modeler do not share ``st.session_state``.

Usage::

    python serve.py            # production entry (Render startCommand)

For local development you can still run each app directly:
``streamlit run app.py`` (hub only) or ``streamlit run fm_app.py``
(modeler only; theme flags are applied by serve.py in production).
"""
import asyncio
import os
import signal
import subprocess
import sys
import time

from aiohttp import ClientSession, WSMsgType, web

from sbi_hub.config.branding import get_brand

HUB_PORT = int(os.environ.get("SBI_HUB_PORT", "8501"))
FM_PORT = int(os.environ.get("SBI_FM_PORT", "8502"))
PUBLIC_PORT = int(os.environ.get("PORT", "8500"))

HUB_UPSTREAM = f"http://127.0.0.1:{HUB_PORT}"
FM_UPSTREAM = f"http://127.0.0.1:{FM_PORT}"

_HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade",
    # websocket handshake headers are managed by ws_connect itself
    "sec-websocket-key", "sec-websocket-version", "sec-websocket-extensions",
    "sec-websocket-protocol",
}


def is_fm_path(path):
    """Return True when ``path`` belongs to the Financial Modeler app."""
    return path == "/fm" or path.startswith("/fm/")


def upstream_for(path):
    """Return the upstream base URL responsible for ``path``."""
    return FM_UPSTREAM if is_fm_path(path) else HUB_UPSTREAM


def _request_headers(request):
    return {
        k: v for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() != "accept-encoding"
    }


def _response_headers(response):
    return {
        k: v for k, v in response.headers.items()
        if k.lower() not in _HOP_BY_HOP
        and k.lower() not in ("content-length", "content-encoding")
    }


async def _proxy_http(request, upstream):
    url = upstream + request.path_qs
    body = await request.read()
    session = request.app["session"]
    async with session.request(
        request.method, url, headers=_request_headers(request),
        data=body or None, allow_redirects=False,
    ) as resp:
        out = web.StreamResponse(status=resp.status, headers=_response_headers(resp))
        await out.prepare(request)
        async for chunk in resp.content.iter_any():
            await out.write(chunk)
        await out.write_eof()
        return out


async def _relay(src, dst, send):
    async for msg in src:
        if msg.type == WSMsgType.TEXT:
            await send(dst, msg.data)
        elif msg.type == WSMsgType.BINARY:
            await send(dst, msg.data, binary=True)
        elif msg.type in (WSMsgType.CLOSE, WSMsgType.CLOSING, WSMsgType.CLOSED):
            break
        elif msg.type == WSMsgType.ERROR:
            break


async def _proxy_ws(request, upstream):
    protocols = tuple(
        p.strip() for p in request.headers.get("sec-websocket-protocol", "").split(",")
        if p.strip()
    )
    ws_client_side = web.WebSocketResponse(heartbeat=30, protocols=protocols)
    await ws_client_side.prepare(request)

    url = upstream.replace("http", "ws", 1) + request.path_qs
    session = request.app["session"]
    try:
        async with session.ws_connect(
            url, headers=_request_headers(request), protocols=protocols or None
        ) as ws_upstream:
            async def to_upstream():
                async for msg in ws_client_side:
                    if msg.type == WSMsgType.TEXT:
                        await ws_upstream.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_upstream.send_bytes(msg.data)
                    else:
                        break

            async def to_client():
                async for msg in ws_upstream:
                    if msg.type == WSMsgType.TEXT:
                        await ws_client_side.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_client_side.send_bytes(msg.data)
                    else:
                        break

            tasks = [asyncio.ensure_future(to_upstream()),
                     asyncio.ensure_future(to_client())]
            done, pending = await asyncio.wait(
                tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in pending:
                t.cancel()
    except Exception:
        pass
    return ws_client_side


async def _handler(request):
    upstream = upstream_for(request.path)
    if request.headers.get("upgrade", "").lower() == "websocket":
        return await _proxy_ws(request, upstream)
    try:
        return await _proxy_http(request, upstream)
    except Exception:
        return web.Response(status=502, text="Upstream app is starting; retry shortly.")


async def _wait_ready(url, name, timeout=120):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            async with ClientSession() as s:
                async with s.get(url) as r:
                    if r.status < 500:
                        print(f"[serve] {name} ready", flush=True)
                        return
        except Exception:
            pass
        await asyncio.sleep(0.5)
    print(f"[serve] WARNING: {name} not ready after {timeout}s", flush=True)


def _spawn(args):
    return subprocess.Popen([sys.executable, *args])


def _spawn_apps():
    common = [
        "--server.address", "127.0.0.1",
        "--server.headless", "true",
        # Production apps don't need source-file watching (and the
        # watchdog backend is unstable on some platforms).
        "--server.fileWatcherType", "none",
    ]
    # Hub theme colors come from .streamlit/config.toml; the brand accent
    # is injected here so branding.py is the single source of truth.
    accent = get_brand()["colors"]["accent"]
    hub = _spawn([
        "-m", "streamlit", "run", "app.py",
        "--server.port", str(HUB_PORT), *common,
        "--theme.primaryColor", accent,
    ])
    fm = _spawn([
        "-m", "streamlit", "run", "fm_app.py",
        "--server.port", str(FM_PORT), *common,
        "--server.baseUrlPath", "fm",
        "--theme.base", "dark",
        "--theme.primaryColor", "#FF4B4B",
        "--theme.backgroundColor", "#0E1117",
        "--theme.secondaryBackgroundColor", "#262730",
        "--theme.textColor", "#FAFAFA",
    ])
    return [hub, fm]


async def _run():
    procs = _spawn_apps()

    async def session_ctx(app):
        app["session"] = ClientSession()

    async def cleanup(app):
        await app["session"].close()
        for p in procs:
            try:
                p.terminate()
            except Exception:
                pass

    app = web.Application()
    app.on_startup.append(session_ctx)
    app.on_cleanup.append(cleanup)
    app.router.add_route("*", "/{tail:.*}", _handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PUBLIC_PORT)
    await site.start()
    print(f"[serve] proxy on :{PUBLIC_PORT}  hub:{HUB_PORT}  fm:{FM_PORT}/fm",
          flush=True)

    # Warm up upstreams in the background so cold starts are less visible.
    asyncio.ensure_future(_wait_ready(f"{HUB_UPSTREAM}/healthz", "hub"))
    asyncio.ensure_future(_wait_ready(f"{FM_UPSTREAM}/fm/healthz", "fm"))

    def _shutdown(*_):
        for t in asyncio.all_tasks():
            if t is not asyncio.current_task():
                t.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            asyncio.get_running_loop().add_signal_handler(sig, _shutdown)
        except NotImplementedError:
            pass

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass
