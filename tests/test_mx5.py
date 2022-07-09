import unittest
import array

from wplctools.mx5 import ActUtlType, ActError, ActProgType


class TestCase_mx5(unittest.TestCase):
    def setUp(self):
        self.act = ActUtlType()
        self.act.open(0)

    def tearDown(self):
        self.act.close()

    def test_(self):
        act = self.act

        # read/write block
        device = "D0"
        for data0 in ((1, 2), (3, 4)):
            data1 = array.array("l", data0)
            act.WriteDeviceBlock(device, len(data0), data1)
            data2 = act.ReadDeviceBlock(device, len(data0))
            self.assertEqual(data2, bytearray(data1))

            data1 = array.array("h", data0)
            act.WriteDeviceBlock2(device, len(data0), data1)
            data2 = act.ReadDeviceBlock2(device, len(data0))
            self.assertEqual(data2, bytearray(data1))

        # get/set
        device = "D0"
        act.SetDevice(device, 1234)
        data = act.GetDevice(device)
        self.assertEqual(data, 1234)

        act.SetDevice("K4M0", 0)
        act.SetDevice("M3", 1)  # 8
        act.SetDevice("M6", 1)  # 4
        act.SetDevice("M9", 1)  # 2
        act.SetDevice("M12", 1)  # 1
        data = act.GetDevice("K4M0")
        self.assertEqual(data, 0x01248)

        act.SetDevice("K8M0", 0)
        act.SetDevice("M3", 1)  # 8
        act.SetDevice("M10", 1)  # 4
        act.SetDevice("M17", 1)  # 2
        act.SetDevice("M24", 1)  # 1
        data = act.GetDevice("K8M0")
        self.assertEqual(data, 0x01020408)

        # read/write random
        device = "D0\nD1\nK4M0\nK4M16"
        for data0 in ((1, 2, 3, 4), (5, 6, 7, 8)):
            data1 = array.array("l", data0)
            act.WriteDeviceRandom(device, len(data0), data1)
            data2 = act.ReadDeviceRandom(device, len(data0))
            self.assertEqual(data2, bytearray(data1))

            data1 = array.array("h", data0)
            act.WriteDeviceRandom2(device, len(data0), data1)
            data2 = act.ReadDeviceRandom2(device, len(data0))
            self.assertEqual(data2, bytearray(data1))

