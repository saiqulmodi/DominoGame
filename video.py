"""Real-life video of the picture ("Watch real"), then back to play.

The videos are free Wikimedia Commons files listed in videos.json (made and
checked with tools/find_videos.py). They stream from upload.wikimedia.org:
no adverts, no "recommended next" list.

  Browser (pygbag): a player opens over the game with a big "Back to play"
                    button; the game notices when it is closed.
  Computer:         the same player page opens in the web browser (pygame
                    cannot show video); coming back to the game window counts
                    as "back to play".
  Android:          the phone's own video player opens.
"""

import html
import json
import os
import sys
import tempfile
import time
import webbrowser

IS_WEB = sys.platform == "emscripten"
IS_ANDROID = "ANDROID_ARGUMENT" in os.environ or hasattr(sys, "getandroidapilevel")

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - Domino Wonder Dash</title>
<style>{css}</style></head><body>{body}
<script>
document.getElementById('dwd-back').onclick=function(){{window.close();
 document.getElementById('dwd-bye').style.display='block';}};
{script}
</script></body></html>"""

CSS = """
#dwd-video{position:fixed;inset:0;z-index:2147483647;background:#0d0d1a;
 display:flex;flex-direction:column;align-items:center;justify-content:center;
 font-family:Arial,sans-serif;color:#fff;gap:12px;padding:12px;box-sizing:border-box}
#dwd-video h1{margin:0;font-size:30px;color:#ffcc00;text-align:center}
#dwd-video video{width:100%;max-width:900px;max-height:62vh;border-radius:14px;
 background:#000;border:3px solid #ffcc00}
#dwd-video .credit{font-size:11px;color:#aab;text-align:center;max-width:900px}
#dwd-video .msg{display:none;font-size:18px;color:#ffcc00;text-align:center}
#dwd-video .row{display:flex;gap:14px;flex-wrap:wrap;justify-content:center}
#dwd-video button{font-size:24px;font-weight:bold;border:3px solid #fff;
 border-radius:16px;padding:14px 26px;color:#fff;cursor:pointer}
#dwd-back{background:#3cb45a} #dwd-again{background:#4682e6;display:none}
#dwd-bye{display:none;font-size:18px;color:#ffcc00}
"""

BODY = """<div id="dwd-video">
<h1>{heading}</h1>
<video id="dwd-player" controls autoplay playsinline preload="auto">{sources}</video>
<div class="msg" id="dwd-msg">This video needs the internet. Try again later!</div>
<div class="row"><button id="dwd-again">&#8635; Watch again</button>
<button id="dwd-back">&#9664; Back to play</button></div>
<div id="dwd-bye">Close this tab to go back to the game.</div>
<div class="credit">{credit}</div></div>"""

# Shared by both players: "watch again" after the end, a message if offline
SCRIPT = """(function(){var v=document.getElementById('dwd-player');
 var again=document.getElementById('dwd-again');
 v.onended=function(){again.style.display='inline-block';};
 again.onclick=function(){again.style.display='none';v.currentTime=0;v.play();};
 var srcs=v.getElementsByTagName('source');
 if(srcs.length)srcs[srcs.length-1].onerror=function(){
   document.getElementById('dwd-msg').style.display='block';v.style.display='none';};
 var p=v.play();if(p&&p.catch)p.catch(function(){v.muted=true;v.play();});})();"""


def _parts(video, title):
  heading = html.escape(f"The real {title}!")
  # WebM first (Chrome, Firefox, Android), MP4 for iPhone / iPad
  ordered = sorted(video.get("sources", []), key=lambda s: s["type"] != "video/webm")
  sources = "".join(f'<source src="{html.escape(s["src"])}" type="{s["type"]}">'
                    for s in ordered)
  credit = html.escape(" - ".join(x for x in (
      "Video: " + (video.get("artist") or "Wikimedia Commons"),
      video.get("license", ""), "Wikimedia Commons") if x))
  return BODY.format(heading=heading, sources=sources, credit=credit)


class VideoPlayer:
  def __init__(self):
    self.open = False
    self.left_game = False
    self.opened_at = 0.0

  def show(self, video, title):
    """Starts the video. Returns False if this device cannot play it."""
    if not video or not video.get("sources"):
      return False
    try:
      if IS_WEB:
        self._show_web(video, title)
      elif IS_ANDROID:
        self._show_android(video)
      else:
        self._show_desktop(video, title)
    except Exception as exc:
      print("video:", exc)
      return False
    self.open = True
    self.left_game = False
    self.opened_at = time.time()
    return True

  def closed(self):
    """Browser: True once the child pressed "Back to play" (checked each frame)."""
    if not (self.open and IS_WEB):
      return False
    try:
      import platform
      done = str(platform.window.eval("window.dwdVideoClosed ? 'yes' : 'no'")) == "yes"
    except Exception:
      done = True
    if done:
      self.open = False
    return done

  def focus_lost(self):
    if self.open and not IS_WEB:
      self.left_game = True

  def returned(self):
    """Computer/Android: the game window got focus back after the video."""
    if self.open and not IS_WEB and self.left_game:
      self.open = False
      return True
    return False

  # ------------------------------------------------------------ per platform
  def _show_web(self, video, title):
    import platform
    body = _parts(video, title)
    js = ("(function(){var old=document.getElementById('dwd-video');if(old)old.remove();"
          "try{speechSynthesis.cancel();}catch(e){}"
          "window.dwdVideoClosed=0;var d=document.createElement('div');"
          "d.innerHTML=" + json.dumps(body) + ";document.body.appendChild(d.firstChild);"
          "if(!document.getElementById('dwd-style')){var s=document.createElement('style');"
          "s.id='dwd-style';s.textContent=" + json.dumps(CSS) + ";document.head.appendChild(s);}"
          "document.getElementById('dwd-back').onclick=function(){"
          "var v=document.getElementById('dwd-player');if(v)v.pause();"
          "document.getElementById('dwd-video').remove();window.dwdVideoClosed=1;"
          "var c=document.getElementById('canvas');if(c&&c.focus)c.focus();};"
          + SCRIPT + "})()")
    platform.window.eval(js)

  def _show_desktop(self, video, title):
    page = PAGE.format(title=html.escape(title), css=CSS, body=_parts(video, title),
                       script=SCRIPT)
    path = os.path.join(tempfile.gettempdir(), "domino_wonder_dash_video.html")
    with open(path, "w", encoding="utf-8") as fh:
      fh.write(page)
    webbrowser.open("file:///" + path.replace("\\", "/"))

  def _show_android(self, video):
    from jnius import autoclass, cast
    Intent = autoclass("android.content.Intent")
    Uri = autoclass("android.net.Uri")
    activity = autoclass("org.kivy.android.PythonActivity").mActivity
    src = next((s for s in video["sources"] if s["type"] == "video/mp4"), video["sources"][0])
    intent = Intent(Intent.ACTION_VIEW)
    intent.setDataAndType(Uri.parse(src["src"]), "video/*")
    cast("android.app.Activity", activity).startActivity(intent)
