import struct
import unittest
from export_character_analysis import WS, defined_function_symbols, coff_function_records
from recover_character_layouts import operand


class CoffTests(unittest.TestCase):
    def test_real_definitions_exclude_external_relocations(self):
        data = (WS / 'work/character-reverse/member_06.obj').read_bytes()
        names = defined_function_symbols(data)
        self.assertIn('?InitCharacter@ChInterface@@QAEXPAUIDirect3DDevice8@@@Z', names)
        self.assertIn('?GetAlpha@ChInterface@@QAEMPAVCHARACTEROBJECT@@@Z', names)
        self.assertNotIn('?GetCharacter@CObjectManager@@QAEPAVCHARACTEROBJECT@@PAD@Z', names)

    def test_malformed_tables_rejected(self):
        real = (WS / 'work/character-reverse/member_06.obj').read_bytes()
        table, count = struct.unpack_from('<II', real, 8)
        for data in [b'', real[:19], real[:table+18*count], real[:-1]]:
            with self.subTest(size=len(data)), self.assertRaises(ValueError):
                defined_function_symbols(data)

    def test_all_supplied_objects_and_bounded_function_bodies(self):
        for index in range(1, 11):
            data = (WS / f'work/character-reverse/member_{index:02}.obj').read_bytes()
            with self.subTest(member=index):
                records = coff_function_records(data)
                self.assertTrue(records)
                for record in records.values():
                    if record['bytes'] is not None:
                        self.assertEqual(len(record['bytes']), record['size'])
                        start = record['file_offset']
                        self.assertEqual(record['bytes'], data[start:start+record['size']])

    def test_instruction_evidence_fails_closed(self):
        data = (WS / 'work/character-reverse/member_06.obj').read_bytes()
        record = coff_function_records(data)['?GetAlpha@ChInterface@@QAEMPAVCHARACTEROBJECT@@@Z']
        self.assertEqual(operand(record, 4, bytes.fromhex('d980')), 772)
        with self.assertRaises(ValueError):
            operand(record, 4, bytes.fromhex('d981'))
        with self.assertRaises(ValueError):
            operand({'bytes': bytes.fromhex('d98004')}, 0, bytes.fromhex('d980'))


if __name__ == '__main__':
    unittest.main()
