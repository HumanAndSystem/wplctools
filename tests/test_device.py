from unittest import TestCase

from wplctools import DEV, DeviceLexer


class MyCase(TestCase):
    def test_DEV(self):
        self.assertEqual(repr(DEV("M", 10)), "DEV(name='M', num=10)")
        self.assertEqual(str(DEV("M", 10)), "M10")
        self.assertEqual(repr(DEV("X", 10)), "DEV(name='X', num=10)")
        self.assertEqual(str(DEV("X", 10)), "X0A")
        self.assertEqual(repr(DEV(".", 10)), "DEV(name='.', num=10)")
        self.assertEqual(str(DEV(".", 10)), ".A")

    def test_DeviceLexer(self):
        checklist = [
            ("M10", [DEV("M", 10)]),
            ("X0A", [DEV("X", 10)]),
            ("D10.A", [DEV("D", 10), DEV(".", 10)]),
            ("K4M10", [DEV("K", 4), DEV("M", 10)]),
            ("D10Z10", [DEV("D", 10), DEV("Z", 10)]),
            ("U0A/G10", [DEV("U", 10), DEV("\\", 0), DEV("G", 10)]),
            ("J10/B0A", [DEV("J", 10), DEV("\\", 0), DEV("B", 10)]),
            ("@D10", [DEV("@", 0), DEV("D", 10)]),
        ]
        for device, devs in checklist:
            self.assertEqual(DeviceLexer(device).lex(), devs)
