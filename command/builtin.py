# command/builtin.py
from __future__ import annotations
from Core.command_router import CommandRouter
from Core.service_container import ServiceContainer

def _resolve(svc, name):
    # prefer try_resolve if your container polyfill exists
    return getattr(svc, "try_resolve", svc.resolve)(name)

def _call_first(obj, *names, default_msg="Service not available"):
    if not obj:
        return default_msg
    for n in names:
        fn = getattr(obj, n, None)
        if callable(fn):
            try:
                return fn()
            except Exception as e:
                return f"{n} failed: {e}"
    return default_msg

def register_all(router: CommandRouter, services: ServiceContainer) -> None:
    weather  = _resolve(services, "weather")
    calendar = _resolve(services, "calendar")
    spotify  = _resolve(services, "spotify")

    # ---- Weather ----
    def _weather(**kwargs):
        return _call_first(
            weather,
            "get_weather", "current_weather", "get_summary",
            default_msg="Weather service isn’t configured."
        )
    router.register("request_weather", _weather)
    router.register("get_weather", _weather)

    # ---- Calendar ----
    def _cal_list(**kwargs):
        data = None
        if calendar:
            for n in ("get_events", "list_events_today", "list_events", "today"):
                fn = getattr(calendar, n, None)
                if callable(fn):
                    try:
                        data = fn()
                        break
                    except Exception as e:
                        return f"Calendar error: {e}"
        if not data:
            return "No events scheduled." if calendar else "Calendar service isn’t configured."

        # Normalize common shapes
        lines = []
        for e in data:
            if isinstance(e, dict):
                title = (e.get("Title") or e.get("summary") or e.get("title") or "Untitled")
                when  = (e.get("DateTime") or e.get("start") or e.get("when") or "")
            else:
                title, when = str(e), ""
            lines.append(f"• {title}" + (f" @ {when}" if when else ""))
        return "\n".join(lines)
    router.register("list_events", _cal_list)
    router.register("request_calendar", _cal_list)

    # ---- Music ----
    def _music(entities=None, text=None, **kwargs):
        if not spotify:
            return "Spotify isn’t configured."
        for n in ("play_song", "play_random", "play"):
            fn = getattr(spotify, n, None)
            if callable(fn):
                try:
                    song = (entities or {}).get("song")
                    if not song and text and text.lower().startswith("play "):
                        song = text[5:].strip()
                    return fn(song) if song else fn()
                except Exception as e:
                    return f"Music error: {e}"
        return "Music control not available."
    router.register("play_music", _music)
    router.register("play_song", _music)

    # ---- Surveillance ----
    def _surveillance(**kwargs):
        try:
            from computer_vision.home_surveillance import monitor_stream
        except Exception:
            return "Surveillance module isn’t available."
        try:
            monitor_stream(0)
            return "Surveillance started."
        except Exception as e:
            return f"Surveillance error: {e}"
    router.register("start_surveillance", _surveillance)

    # ---- Scene description (optional) ----
    def _describe(**kwargs):
        try:
            from computer_vision.scene_description import describe_scene_from_camera
        except Exception:
            return "Scene description module isn’t available."
        try:
            return describe_scene_from_camera()
        except Exception as e:
            return f"Scene description error: {e}"
    router.register("describe_scene", _describe)
