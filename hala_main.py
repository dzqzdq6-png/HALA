"""هلا - مساعد سطح مكتب لويندوز يُستدعى بالاسم.

التشغيل:  python hala_main.py
"""
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import pystray
from PIL import Image, ImageDraw
from pynput import keyboard

import actions
import config
from brain import Brain
from memory import Memory
from screen import capture_b64
from voice import Voice

REMEMBER_PREFIXES = ("تذكر", "احفظ", "remember")

events: "queue.Queue[tuple]" = queue.Queue()
memory = Memory()
brain = Brain(memory)
voice = Voice()


# ---------------------------------------------------------------- المعالجة
def process(text: str, mode: str = "general", speak: bool = False):
    """تعمل في خيط خلفي؛ تعيد النتيجة للواجهة عبر الطابور."""
    low = text.strip().lower()
    try:
        if low.startswith(REMEMBER_PREFIXES):
            fact = text.split(None, 1)[1] if len(text.split(None, 1)) > 1 else ""
            ok = memory.add(fact)
            reply = "تم، سأتذكر ذلك." if ok else "لم أحفظ شيئًا (وضع التخفّي مفعّل أو النص فارغ)."
            action = None
        else:
            image = capture_b64() if mode == "screen" else None
            raw = brain.ask(text, image)
            reply, action = actions.split_reply(raw)
    except Exception as exc:  # شبكة، مفتاح خاطئ، إلخ
        reply, action = f"تعذّر الحصول على إجابة: {exc}", None

    events.put(("answer", reply, action))
    if speak:
        voice.speak(reply)


def voice_turn():
    """بعد سماع الاسم: استمع للأمر ثم عالجه بصوت عالٍ."""
    voice.speak("نعم؟")
    text = voice.listen_command()
    if text:
        process(text, mode="general", speak=True)
    start_wake_thread()


def start_wake_thread():
    threading.Thread(target=voice.wake_loop, args=(voice_turn,), daemon=True).start()


# ---------------------------------------------------------------- الواجهة
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.win = None
        self.root.after(100, self.poll)

    def show_ask(self):
        if self.win and self.win.winfo_exists():
            self.win.focus_force()
            return
        w = self.win = tk.Toplevel(self.root)
        w.title(config.ASSISTANT_NAME)
        w.attributes("-topmost", True)
        w.geometry("460x230")

        self.mode = tk.StringVar(value="general")
        row = ttk.Frame(w)
        row.pack(fill="x", padx=10, pady=(10, 4))
        ttk.Radiobutton(row, text="عام", variable=self.mode, value="general").pack(side="right")
        ttk.Radiobutton(row, text="الشاشة", variable=self.mode, value="screen").pack(side="right", padx=8)

        self.entry = ttk.Entry(w, justify="right")
        self.entry.pack(fill="x", padx=10, pady=4)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.submit)
        w.bind("<Escape>", lambda e: w.destroy())
        w.bind("<Tab>", self.toggle_mode)

        self.out = tk.Label(w, text="اكتب سؤالك ثم Enter  •  Tab للتبديل  •  Esc للإغلاق",
                            wraplength=430, justify="right", anchor="ne")
        self.out.pack(fill="both", expand=True, padx=10, pady=8)

    def toggle_mode(self, _e=None):
        self.mode.set("screen" if self.mode.get() == "general" else "general")
        return "break"

    def submit(self, _e=None):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.out.config(text="…")
        threading.Thread(target=process, args=(text, self.mode.get()), daemon=True).start()

    def show_answer(self, reply, action):
        if not (self.win and self.win.winfo_exists()):
            self.show_ask()
        self.out.config(text=reply)
        desc = actions.describe(action) if action else None
        if desc and messagebox.askyesno(config.ASSISTANT_NAME, f"هل تسمح بـ {desc}؟", parent=self.win):
            actions.run(action)

    def poll(self):
        try:
            while True:
                kind, *args = events.get_nowait()
                if kind == "ask":
                    self.show_ask()
                elif kind == "answer":
                    self.show_answer(*args)
                elif kind == "incognito":
                    memory.incognito = not memory.incognito
                    self.show_answer("وضع التخفّي: " + ("مفعّل" if memory.incognito else "متوقف"), None)
                elif kind == "wake":
                    threading.Thread(target=voice_turn, daemon=True).start()
                elif kind == "quit":
                    self.root.quit()
                    return
        except queue.Empty:
            pass
        self.root.after(100, self.poll)


# ---------------------------------------------------------------- الاختصارات والأيقونة
def tray_icon():
    img = Image.new("RGB", (64, 64), "#1f6feb")
    ImageDraw.Draw(img).ellipse((16, 16, 48, 48), fill="white")
    menu = pystray.Menu(
        pystray.MenuItem("اسأل هلا", lambda: events.put(("ask",))),
        pystray.MenuItem("وضع التخفّي", lambda: events.put(("incognito",))),
        pystray.MenuItem("خروج", lambda: (events.put(("quit",)), icon.stop())),
    )
    icon = pystray.Icon("hala", img, config.ASSISTANT_NAME, menu)
    return icon


def main():
    app = App()
    hotkeys = keyboard.GlobalHotKeys({
        config.HOTKEY_ASK: lambda: events.put(("ask",)),
        config.HOTKEY_WAKE: lambda: events.put(("wake",)),
        config.HOTKEY_INCOGNITO: lambda: events.put(("incognito",)),
    })
    hotkeys.start()
    threading.Thread(target=tray_icon().run, daemon=True).start()
    start_wake_thread()
    try:
        app.root.mainloop()
    finally:
        voice.stop()
        hotkeys.stop()


if __name__ == "__main__":
    main()
