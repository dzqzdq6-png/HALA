"""التقاط الشاشة عند الطلب فقط، دون حفظها على القرص."""
import base64
import io
from PIL import ImageGrab


def capture_b64(max_side: int = 1568) -> str:
    img = ImageGrab.grab().convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode("ascii")
