"""الاتصال بنموذج Claude للإجابة (نص أو نص + لقطة شاشة)."""
import anthropic
import config

SYSTEM_BASE = f"""أنت "{config.ASSISTANT_NAME}"، مساعد سطح مكتب ودود وموجز على ويندوز.
- أجب بلغة المستخدم، وبإيجاز (جملتان إلى ثلاث إلا إذا طُلب التفصيل) لأن الإجابة قد تُقرأ بصوت عالٍ.
- إذا أُرفقت صورة فهي لقطة لشاشة المستخدم؛ اشرح ما يطلبه عنها.
- إذا طلب المستخدم فتح تطبيق أو موقع، أجب بجملة قصيرة ثم أضف في سطر أخير مستقل فقط:
  ACTION: {{"type":"open_app","name":"notepad"}}   أو   ACTION: {{"type":"open_url","url":"https://..."}}
  التطبيقات المسموحة: notepad, calc, explorer, paint, chrome, edge.
- لا تقترح حذف ملفات أو إرسال رسائل أو دفعات أبدًا."""


class Brain:
    def __init__(self, memory):
        self.client = anthropic.Anthropic()   # يقرأ ANTHROPIC_API_KEY من البيئة
        self.memory = memory
        self.history = []                      # نص فقط، بدون صور

    def _system(self) -> str:
        mem = self.memory.as_prompt()
        return SYSTEM_BASE + ("\n\n" + mem if mem else "")

    def ask(self, text: str, image_b64: str | None = None) -> str:
        content = []
        if image_b64:
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": "image/jpeg", "data": image_b64},
            })
        content.append({"type": "text", "text": text})

        messages = self.history[-6:] + [{"role": "user", "content": content}]
        resp = self.client.messages.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=self._system(),
            messages=messages,
        )
        reply = "".join(b.text for b in resp.content if b.type == "text").strip()

        if not self.memory.incognito:
            self.history += [
                {"role": "user", "content": text},
                {"role": "assistant", "content": reply},
            ]
        return reply
