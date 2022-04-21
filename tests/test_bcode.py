from io import BytesIO
from unittest import TestCase

from wplctools import bcode_decode


class BcodeTestCase(TestCase):
    def test_bcode(self):
        checklist = [
            ([2, 2], "NOP"),
            ([3, 0, 3, 4, 0x90, 10, 4], "LD M10"),
        ]
        for bcode, il in checklist:
            bs = BytesIO(bytes(bcode))
            inst = bcode_decode(bs)
            self.assertEqual(str(inst), il)
