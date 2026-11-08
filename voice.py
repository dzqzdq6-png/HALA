"""الاستماع لكلمة الاستدعاء، وتحويل الكلام لنص، والنطق بالرد.

ملاحظة: هذه النسخة البسيطة تستخدم SpeechRecognition (خدمة سحابية) حتى للاستماع
لكلمة الاستدعاء. لكلمة استدعاء محلية بالكامل استبدل wait_for_wake بمحرك مثل
openWakeWord أو Porcupine.
"""
import threading
import speech_recognition as sr
import pyttsx3
import config


class Voice:
    def __init__(self):
        self.rec = sr.Recognizer()
        self.rec.dynamic_energy_threshold = True
        self._tts_lock = threading.Lock()
        self.running = False

    # ---------- النطق ----------
    def speak(self, text: str):
        with self._tts_lock:
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()

    # ---------- التعرف ----------
    def _transcribe(self, audio) -> str:
        try:
            return self.rec.recognize_google(audio, language=config.SPEECH_LANG).strip()
        except (sr.UnknownValueError, sr.RequestError):
            return ""

    def listen_command(self, timeout=6, phrase_limit=15) -> str:
        with sr.Microphone() as mic:
            self.rec.adjust_for_ambient_noise(mic, duration=0.3)
            try:
                audio = self.rec.listen(mic, timeout=timeout, phrase_time_limit=phrase_limit)
            except sr.WaitTimeoutError:
                return ""
        return self._transcribe(audio)

    def wake_loop(self, on_wake):
        """حلقة تعمل في خيط مستقل: تستدعي on_wake() عند سماع الاسم."""
        self.running = True
        woke = False
        with sr.Microphone() as mic:
            self.rec.adjust_for_ambient_noise(mic, duration=1)
            while self.running:
                try:
                    audio = self.rec.listen(mic, timeout=2, phrase_time_limit=3)
                except sr.WaitTimeoutError:
                    continue
                heard = self._transcribe(audio).lower()
                if heard and any(w in heard for w in config.WAKE_WORDS):
                    woke = True               # نغلق الميكروفون ثم نستدعي الأمر
                    break
        self.running = False
        if woke:
            on_wake()

    def stop(self):
        self.running = False
