import io
from wplctools.melsec import _device


print(_device)
sb = io.StringIO()
sb.write("1")
sb.write("한")
sb.write("🐺")
sb.write("2")
a = "0"
b = "한"
c = "🐺"
d = a + b + c
e = sb.getvalue()
print(_device.device_lex(e))
print(e)
print("end")