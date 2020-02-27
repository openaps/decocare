from pprint import pformat

from decocare import lib

from decocare.records.base import KnownRecord, VariableHead
from decocare.records.times import extra_year_bits


class Bolus(KnownRecord):
    """
    >>> rec = Bolus(Bolus._test_1[:4])
    >>> decoded = rec.parse(Bolus._test_1)
    >>> print(str(rec))
    Bolus 2012-12-18T15:05:28 head[4], body[0] op[0x01]

    >>> print(pformat(decoded))
    {'amount': 5.6, 'duration': 0, 'programmed': 5.6, 'type': 'normal'}

    """

    _test_1 = bytearray([0x01, 0x38, 0x38, 0x00, 0xDC, 0x05, 0x4F, 0x12, 0x0C,])
    opcode = 0x01
    head_length = 4

    def __init__(self, head, larger=False):
        super().__init__(head, larger)
        # self.larger = larger
        if self.larger:
            self.head_length = 8

    def decode(self):
        self.parse_time()
        dose = {
            "amount": self.head[2] / 10.0,
            "programmed": self.head[1] / 10.0,
            "duration": self.head[3] * 30,
            "type": self.head[3] > 0 and "square" or "normal",
        }
        if self.larger:
            duration = self.head[7] * 30
            dose = {
                "amount": lib.BangInt(self.head[3:5]) / 40.0,
                "programmed": lib.BangInt(self.head[1:3]) / 40.0,
                "unabsorbed": lib.BangInt(self.head[5:7]) / 40.0,
                "duration": duration,
                "type": duration > 0 and "square" or "normal",
            }
        return dose


class BolusWizard(KnownRecord):
    """
    Decode/parse bolus wizard records.

    >>> from decocare import models
    >>> rec = BolusWizard(BolusWizard._test_1[:2], model=models.PumpModel('522', None))
    >>> decoded = rec.parse(BolusWizard._test_1)
    >>> print(str(rec))
    BolusWizard 2013-01-20T13:07:45 head[2], body[13] op[0x5b]

    >>> print(pformat(decoded))
    {'_byte[5]': 0,
     '_byte[7]': 0,
     'bg': 108,
     'bg_target_high': 125,
     'bg_target_low': 106,
     'bolus_estimate': 1.1,
     'carb_input': 15,
     'carb_ratio': 13,
     'correction_estimate': 0.0,
     'food_estimate': 1.1,
     'sensitivity': 45,
     'unabsorbed_insulin_count': '??',
     'unabsorbed_insulin_total': 4.8,
     'unknown_byte[10]': 0,
     'unknown_byte[8]': 0}

    """

    # missing unabsorbed_insulin_count = 4
    _test_1 = bytearray(
        [
            0x5B,
            0x6C,
            0x2D,
            0x47,
            0x0D,
            0x14,
            0x0D,
            0x0F,
            0x50,
            0x0D,
            0x2D,
            0x6A,
            0x00,
            0x0B,
            0x00,
            0x00,
            0x30,
            0x00,
            0x0B,
            0x7D,
        ]
    )

    _test_2 = bytearray(
        [
            0x5B,
            0x8B,
            0xDC,
            0x05,
            0x0F,
            0x12,
            0x0C,
            0x45,
            0x50,
            0x0D,
            0x2D,
            0x6A,
            0x03,
            0x35,
            0x00,
            0x00,
            0x00,
            0x00,
            0x38,
            0x7D,
        ]
    )
    opcode = 0x5B
    body_length = 13

    def __init__(self, head, model=None):
        super().__init__(head, model)
        # self.larger = larger
        self.MMOL_DEFAULT = model.MMOL_DEFAULT
        if self.larger:
            self.body_length = 15

    def decode(self):
        self.parse_time()
        bg = lib.BangInt([self.body[1] & 0x0F, self.head[1]])
        carb_input = int(self.body[0])
        # XXX: I have no idea if this is correct; it seems to produce correct results.
        correction = (
            twos_comp(self.body[7], 8) + twos_comp(self.body[5] & 0x0F, 8)
        ) / 10.0
        wizard = {
            "bg": bg,
            "carb_input": carb_input,
            "carb_ratio": int(self.body[2]),
            "sensitivity": int(self.body[3]),
            "bg_target_low": int(self.body[4]),
            "bg_target_high": int(self.body[12]),
            "bolus_estimate": int(self.body[11]) / 10.0,
            "food_estimate": int(self.body[6]) / 10.0,
            "unabsorbed_insulin_total": int(self.body[9]) / 10.0,
            "unabsorbed_insulin_count": "??",
            "correction_estimate": correction,
            "_byte[5]": self.body[5],
            "_byte[7]": int(self.body[7]),  #
            "unknown_byte[8]": self.body[8],
            "unknown_byte[10]": self.body[10],
            # '??': '??',
            # 'unabsorbed_insulin_total': int(self.body[9])/10.0,
            # 'food_estimate': int(self.body[0]),
        }

        if self.larger:
            # correction = ( twos_comp( self.body[6], (self.body[9] & 0x38) << 5 ) ) / 40.0
            bg = ((self.body[1] & 0x03) << 8) + self.head[1]
            carb_input = ((self.body[1] & 0x0C) << 6) + self.body[0]
            carb_ratio = (((self.body[2] & 0x07) << 8) + self.body[3]) / 10.0
            # xxx: not sure about this
            # https://github.com/ps2/minimed_rf/blob/master/lib/minimed_rf/log_entries/bolus_wizard.rb#L102
            sensitivity = int(self.body[4])
            wizard = {
                "bg": bg,
                "carb_input": carb_input,
                "carb_ratio": carb_ratio,
                "sensitivity": sensitivity,
                "bg_target_low": int(self.body[5]),
                "bg_target_high": int(self.body[14]),
                # 'bolus_estimate': int(self.body[13])/40.0,
                "correction_estimate": (((self.body[9] & 0x38) << 5) + self.body[6])
                / 40.0,
                # 'correction_maybe_estimate': correction,
                "food_estimate": insulin_decode(self.body[7], self.body[8]),
                "unabsorbed_insulin_total": insulin_decode(
                    self.body[10], self.body[11]
                ),
                "bolus_estimate": insulin_decode(self.body[12], self.body[13]),
                # 'unknown_bytes': map(int, list(self.body)),
            }

        if self.MMOL_DEFAULT:
            for key in ["bg", "bg_target_high", "bg_target_low", "sensitivity"]:
                wizard[key] = wizard[key] / 10.0
        return wizard


def insulin_decode(a, b, strokes=40.0):
    return ((a << 8) + b) / strokes


def twos_comp(val, bits):
    # http://stackoverflow.com/a/9147327
    """compute the 2's compliment of int value val"""
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


class UnabsorbedInsulinBolus(VariableHead):
    """
    This data is not made available at the time of therapy in the pump
    UI, but could easily change my dosing decision.

    >>> from decocare import models
    >>> model = models.PumpModel('522', None)
    >>> rec = UnabsorbedInsulinBolus( UnabsorbedInsulinBolus._test_1[:2], model)
    >>> print(str(rec))
    UnabsorbedInsulinBolus unknown head[2], body[0] op[0x5c]

    >>> print(pformat(rec.parse( UnabsorbedInsulinBolus._test_1 )))
    [{'age': 78, 'amount': 1.25}, {'age': 88, 'amount': 0.95}]

    >>> rec = UnabsorbedInsulinBolus( UnabsorbedInsulinBolus._test_2[:2], model )
    >>> print(str(rec))
    UnabsorbedInsulinBolus unknown head[2], body[0] op[0x5c]

    >>> print(pformat(rec.parse( UnabsorbedInsulinBolus._test_2 )))
    [{'age': 60, 'amount': 2.6}, {'age': 160, 'amount': 2.5}]



    [{'age': 60, 'amount': 2.6, 'curve': 4},
    {'age': 160, 'amount': 2.5, 'curve': 4}]

    """

    _test_1 = bytearray([0x5C, 0x08, 0x32, 0x4E, 0x04, 0x26, 0x58, 0x04,])

    _test_2 = bytearray([0x5C, 0x08, 0x68, 0x3C, 0x04, 0x64, 0xA0, 0x04,])
    opcode = 0x5C
    date_length = 0

    def decode(self):
        raw = self.head[2:]
        return self.model.decode_unabsorbed(raw)


class CalBGForPH(KnownRecord):
    """
    >>> rec = CalBGForPH( CalBGForPH._test_1[:2] )
    >>> rec.parse( CalBGForPH._test_1 )
    {'amount': 139}
    >>> print(str(rec))
    CalBGForPH 2012-12-18T15:04:46 head[2], body[0] op[0x0a]

    """

    _test_1 = bytearray([0x0A, 0x8B, 0xEE, 0x04, 0x2F, 0x12, 0x0C,])

    _test_2 = bytearray([0x0A, 0xA7, 0x22, 0x53, 0x30, 0x0E, 0x0D,])

    _test_3 = bytearray([0x0A, 0xB0, 0x00, 0x6F, 0x2F, 0x0E, 0x0D,])

    _test_4 = bytearray([0x0A, 0x42, 0x0C, 0x6C, 0x31, 0x0E, 0x8D,])

    _test_5 = bytearray([0x0A, 0x60, 0x04, 0x59, 0x2B, 0x0E, 0x8D,])
    _test_6 = bytearray([0x0A, 0x5B, 0x16, 0x52, 0x2A, 0x0E, 0x8D,])
    opcode = 0x0A

    def decode(self):
        self.parse_time()
        # year_bits = extra_year_bits(self.date[4])

        highbit = (self.date[2] & 0b10000000) << 2
        nibble = (self.date[4] & 0b10000000) << 1
        low = self.head[1]
        amount = int(highbit + nibble + low)
        return {"amount": amount}
        # return { 'amount': int(lib.BangInt([ year_bits[0], self.head[1] ])) }
        pass


if __name__ == "__main__":
    import doctest

    doctest.testmod()
