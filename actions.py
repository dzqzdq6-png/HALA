"""تنفيذ إجراءات بسيطة وآمنة، بعد موافقة المستخدم دائمًا."""
import json
import re
import subprocess
import webbrowser

ALLOWED_APPS = {
    "notepad": ["notepad.exe"],
    "calc": ["calc.exe"],
    "explorer": ["explorer.exe"],
    "paint": ["mspaint.exe"],
    "chrome": ["cmd", "/c", "start", "", "chrome"],
    "edge": ["cmd", "/c", "start", "", "msedge"],
}

_ACTION_RE = re.compile(r"^ACTION:\s*(\{.*\})\s*$", re.MULTILINE)


def split_reply(reply: str):
    """يفصل نص الإجابة عن سطر ACTION إن وُجد. يعيد (النص، الإجراء أو None)."""
    m = _ACTION_RE.search(reply)
    if not m:
        return reply, None
    text = (reply[: m.start()] + reply[m.end():]).strip()
    try:
        return text, json.loads(m.group(1))
    except json.JSONDecodeError:
        return text, None


def describe(action: dict) -> str | None:
    if action.get("type") == "open_app" and action.get("name") in ALLOWED_APPS:
        return f"فتح التطبيق: {action['name']}"
    if action.get("type") == "open_url" and str(action.get("url", "")).startswith("https://"):
        return f"فتح الرابط: {action['url']}"
    return None


def run(action: dict):
    if action.get("type") == "open_app":
        subprocess.Popen(ALLOWED_APPS[action["name"]])
    elif action.get("type") == "open_url":
        webbrowser.open(action["url"])
