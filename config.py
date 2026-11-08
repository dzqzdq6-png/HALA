"""إعدادات المساعد "هلا" - عدّل القيم هنا حسب رغبتك."""
import os
from pathlib import Path

ASSISTANT_NAME = "هلا"
WAKE_WORDS = ["هلا", "hala", "hello hala"]      # كلمات الاستدعاء بالاسم
SPEECH_LANG = "ar-SA"                            # لغة التعرف على الكلام: ar-SA أو en-US
MODEL = "claude-sonnet-5-5"                      # النموذج المستخدم عبر Anthropic API
MAX_TOKENS = 800

# اختصارات لوحة المفاتيح (صيغة pynput)
HOTKEY_ASK = "<ctrl>+<alt>+<space>"              # نافذة السؤال الصامت
HOTKEY_WAKE = "<ctrl>+<alt>+h"                   # استدعاء بدون صوت
HOTKEY_INCOGNITO = "<ctrl>+<shift>+i"            # وضع التخفّي

DATA_DIR = Path(os.environ.get("HALA_HOME", Path.home() / ".hala"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_FILE = DATA_DIR / "memory.json"

# يُقرأ مفتاح الواجهة من المتغير ANTHROPIC_API_KEY
