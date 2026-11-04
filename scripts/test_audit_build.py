"""Regression checks for audit mistakes that would change completeness claims."""
import tempfile
import unittest
import json
from pathlib import Path
from audit_build import WS, parse_project, uncomment, values


class BuildAuditTests(unittest.TestCase):
    def test_comment_filter_preserves_paths_and_line_numbers(self):
        text = '#include "C:\\foo\\bar.h" // ignored\n/* #include "fake.h"\n */\n#include "ok.h"'
        clean = uncomment(text)
        self.assertIn('C:\\foo\\bar.h', clean)
        self.assertNotIn('fake.h', clean)
        self.assertEqual(text.count('\n'), clean.count('\n'))

    def test_vc6_quoted_directory_and_flag_boundary(self):
        self.assertEqual(values('/I "a b\\" /I..\\common /D "X"', 'I'), ['a b\\', '..\\common'])
        self.assertEqual(values('/out:"a b.exe" /debug', 'out:'), ['a b.exe'])

    def test_sources_configs_and_missing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'p.dsp'
            (p.parent / 'has space.cpp').write_bytes(b'// legacy \xff\xfe\n')
            p.write_text('!IF "$(CFG)" == "P - Debug"\n# ADD BASE CPP /I "wrong"\n# ADD CPP /I "right"\n!ENDIF\nSOURCE=".\\has space.cpp"\nSOURCE=.\\absent.h\n', encoding='ascii')
            _, configs, sources, directives = parse_project(p)
            self.assertEqual(list(configs), ['P - Debug'])
            self.assertEqual(len(directives), 1)
            self.assertEqual([s['exists'] for s in sources], [True, False])
            self.assertEqual(sources[1]['line'], 6)

    def test_empty_and_unrecognized_project_is_not_invented(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'broken.dsp'
            p.write_text('SOURCE_WITHOUT_EQUALS\n!IF malformed\n')
            _, configs, sources, _ = parse_project(p)
            self.assertEqual(configs, {})
            self.assertEqual(sources, [])

    def test_real_inventory_completeness_and_duplicate_projects(self):
        report = json.loads((WS / 'inventory/build-audit.json').read_text(encoding='utf-8'))
        self.assertEqual(len(report['projects']), 14)
        self.assertEqual(report['summary']['source_entries'], 832)
        self.assertEqual(sum(len(p['configurations']) for p in report['projects']), 41)
        missing = [s for p in report['projects'] for s in p['sources'] if not s['exists']]
        self.assertEqual(len(missing), 6)
        self.assertTrue(all(not s['candidates'] for s in missing))
        self.assertEqual(report['baseline_integrity']['changed_or_missing'], [])
        self.assertTrue(all(p['exists'] for w in report['workspaces'] for p in w['projects']))
        self.assertTrue(all(not x['in_project_closures'] for x in report['global_imports']))


if __name__ == '__main__':
    unittest.main()
