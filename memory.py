"""ذاكرة محلية: تُحفظ الحقائق في ملف JSON على جهازك فقط."""
import json
import time
import config


class Memory:
    def __init__(self):
        self.incognito = False
        self.facts = []
        if config.MEMORY_FILE.exists():
            try:
                self.facts = json.loads(config.MEMORY_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                self.facts = []

    def _save(self):
        config.MEMORY_FILE.write_text(
            json.dumps(self.facts, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def add(self, text: str) -> bool:
        """يحفظ معلومة. لا يحفظ شيئًا في وضع التخفّي."""
        text = text.strip()
        if self.incognito or not text:
            return False
        self.facts.append({"text": text, "time": int(time.time())})
        self._save()
        return True

    def delete(self, index: int):
        if 0 <= index < len(self.facts):
            self.facts.pop(index)
            self._save()

    def clear(self):
        self.facts = []
        self._save()

    def as_prompt(self) -> str:
        if not self.facts:
            return ""
        lines = "\n".join(f"- {f['text']}" for f in self.facts[-50:])
        return f"معلومات يريد المستخدم أن تتذكرها:\n{lines}"
