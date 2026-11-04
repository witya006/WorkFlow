import struct
import unittest
from build_character_stdio_adapter import WS, retarget_stdio
from export_character_analysis import coff_function_records


class RetargetTests(unittest.TestCase):
    def test_real_objects_preserve_code_and_replay_is_noop(self):
        total = 0
        for index in range(1, 11):
            raw = (WS/f'work/character-reverse/member_{index:02}.obj').read_bytes()
            with self.subTest(member=index):
                changed, edits = retarget_stdio(raw)
                table = struct.unpack_from('<I', raw, 8)[0]
                self.assertEqual(raw[:table], changed[:table])
                self.assertEqual({k: v['bytes'] for k, v in coff_function_records(raw).items()},
                                 {k: v['bytes'] for k, v in coff_function_records(changed).items()})
                repeated, repeated_edits = retarget_stdio(changed)
                self.assertEqual(repeated, changed)
                self.assertEqual(repeated_edits, [])
                total += len(edits)
        self.assertGreater(total, 8)

    def test_truncated_and_unexpected_trailing_data_are_rejected(self):
        raw = (WS/'work/character-reverse/member_03.obj').read_bytes()
        for data in [b'', raw[:19], raw[:-1], raw+b'overlay']:
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                retarget_stdio(data)

    def test_matching_defined_symbol_is_not_retargeted(self):
        raw = bytearray((WS/'work/character-reverse/member_03.obj').read_bytes())
        table, count = struct.unpack_from('<II', raw, 8)
        index = 0
        while index < count:
            at = table+18*index
            section, kind, storage, aux = struct.unpack_from('<hHBB', raw, at+12)
            if section > 0 and kind & 0x20 and storage == 2:
                raw[at:at+8] = b'_fopen\0\0'
                break
            index += 1+aux
        self.assertLess(index, count)
        patched, changes = retarget_stdio(bytes(raw))
        self.assertIn('_fopen', coff_function_records(patched))
        self.assertNotIn(index, [x['symbol_index'] for x in changes])


if __name__ == '__main__':
    unittest.main()
