# tests/test_app.py

import unittest
from click.testing import CliRunner
from app.main import cli

class TestApp(unittest.TestCase):
    def test_batch_mode(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--sistema', 'D&D 5e',
            '--genero', 'Fantasia',
            '--jogadores', '4',
            '--nivel', '5',
            '--batch'
        ])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Geração em lote concluída!', result.output)

    def test_interactive_mode(self):
        runner = CliRunner()
        result = runner.invoke(cli, [
            '--sistema', 'D&D 5e',
            '--genero', 'Fantasia',
            '--jogadores', '4',
            '--nivel', '5'
        ], input='/sair\n')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Sessão terminada.', result.output)

if __name__ == '__main__':
    unittest.main()
