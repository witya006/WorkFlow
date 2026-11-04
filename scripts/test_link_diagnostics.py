import unittest
from summarize_executable_build import unresolved_symbol


class LinkDiagnostics(unittest.TestCase):
    def test_import_target_is_not_confused_with_referencing_function(self):
        message = 'ссылка на неразрешенный внешний символ __imp__AIL_startup@0 в функции "int __cdecl InitR3SoundSystem(char *)" (?InitR3SoundSystem@@YAHPAD@Z).'
        self.assertEqual(unresolved_symbol(message), '__imp__AIL_startup@0')

    def test_decorated_target_from_real_cpp_diagnostic(self):
        message = 'ссылка на неразрешенный внешний символ "char * __cdecl CheckFiles(void)" (?CheckFiles@@YAPADXZ) в функции "int __thiscall LoadData(void)" (?LoadData@@YAHXZ).'
        self.assertEqual(unresolved_symbol(message), '?CheckFiles@@YAPADXZ')

    def test_english_import_and_no_target(self):
        self.assertEqual(unresolved_symbol('unresolved external symbol _MSS_auto_cleanup referenced in function ?Init@@YAHXZ'), '_MSS_auto_cleanup')
        self.assertIsNone(unresolved_symbol('ordinary diagnostic without symbol'))


if __name__ == '__main__':
    unittest.main()
