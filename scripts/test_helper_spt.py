import unittest
from helper_spt import FormatError, encode, fingerprint, parse

SAMPLE = b'''script_begin
[HelperObjectBegin]
*Portal -1 -2 -3 1 2 3
-node_tm
1 0 0 0
0 1 0 0
0 0 1 0
10 20 -0 1
[HelperObjectEnd]
script_end
'''


class HelperTests(unittest.TestCase):
    def test_known_fields(self):
        helper, = parse(SAMPLE)
        self.assertEqual(helper.name, b'Portal')
        self.assertEqual(helper.legacy_name, b'portal')
        self.assertEqual(helper.bounds, (-1, -2, -3, 1, 2, 3))
        self.assertEqual(helper.matrix[12:15], (10, 20, 0))
        self.assertEqual(fingerprint([helper]), fingerprint(parse(encode([helper]))))

    def test_empty(self):
        self.assertEqual(parse(encode([])), [])

    def test_every_token_truncation_rejected(self):
        tokens = SAMPLE.split()
        for count in range(len(tokens)):
            with self.subTest(count=count), self.assertRaises(FormatError):
                parse(b' '.join(tokens[:count]))

    def test_unknown_option_and_bad_float(self):
        for bad in [SAMPLE.replace(b'-node_tm', b'-unknown'), SAMPLE.replace(b'-1 -2', b'nan -2'),
                    SAMPLE.replace(b'-1 -2', b'1e999 -2'), SAMPLE + b'junk']:
            with self.assertRaises(FormatError):
                parse(bad)

    def test_limits(self):
        for options in [{'max_bytes': 5}, {'max_records': 0}]:
            with self.assertRaises(FormatError):
                parse(SAMPLE, **options)
        with self.assertRaises(FormatError):
            parse(SAMPLE.replace(b'*Portal', b'*' + b'a'*256))

    def test_legacy_name_truncation(self):
        helper, = parse(SAMPLE.replace(b'Portal', b'A'*40))
        self.assertEqual(helper.legacy_name, b'a'*31)
        self.assertEqual(len(parse(encode([helper]))[0].name), 40)

    def test_unnamed_helper_observed_in_real_maps(self):
        helper, = parse(SAMPLE.replace(b'*Portal', b'*'))
        self.assertEqual(helper.name, b'')
        self.assertEqual(fingerprint([helper]), fingerprint(parse(encode([helper]))))


if __name__ == '__main__':
    unittest.main()
