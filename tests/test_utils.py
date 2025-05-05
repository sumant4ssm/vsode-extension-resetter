"""
Tests for utility functions.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.utils import (
    get_platform,
    get_vscode_path,
    get_machine_id_path,
    get_extensions_path,
    get_backup_dir,
    create_backup_id,
    generate_new_machine_id
)

class TestUtils(unittest.TestCase):
    """
    Tests for utility functions.
    """
    
    def test_get_platform(self):
        """
        Test the get_platform function.
        """
        platform = get_platform()
        self.assertIn(platform, ["windows", "macos", "linux"])
    
    @patch("src.core.utils.get_platform")
    def test_get_vscode_path_windows(self, mock_get_platform):
        """
        Test the get_vscode_path function on Windows.
        """
        mock_get_platform.return_value = "windows"
        with patch.dict(os.environ, {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"}):
            path = get_vscode_path()
            self.assertEqual(path, Path("C:\\Users\\Test\\AppData\\Roaming\\Code"))
    
    @patch("src.core.utils.get_platform")
    def test_get_vscode_path_macos(self, mock_get_platform):
        """
        Test the get_vscode_path function on macOS.
        """
        mock_get_platform.return_value = "macos"
        with patch("pathlib.Path.home", return_value=Path("/Users/Test")):
            path = get_vscode_path()
            self.assertEqual(path, Path("/Users/Test/Library/Application Support/Code"))
    
    @patch("src.core.utils.get_platform")
    def test_get_vscode_path_linux(self, mock_get_platform):
        """
        Test the get_vscode_path function on Linux.
        """
        mock_get_platform.return_value = "linux"
        with patch("pathlib.Path.home", return_value=Path("/home/test")):
            path = get_vscode_path()
            self.assertEqual(path, Path("/home/test/.config/Code"))
    
    @patch("src.core.utils.get_vscode_path")
    def test_get_machine_id_path(self, mock_get_vscode_path):
        """
        Test the get_machine_id_path function.
        """
        mock_get_vscode_path.return_value = Path("/path/to/vscode")
        path = get_machine_id_path()
        self.assertEqual(path, Path("/path/to/vscode/machineId"))
    
    @patch("src.core.utils.get_vscode_path")
    def test_get_extensions_path(self, mock_get_vscode_path):
        """
        Test the get_extensions_path function.
        """
        mock_get_vscode_path.return_value = Path("/path/to/vscode")
        path = get_extensions_path()
        self.assertEqual(path, Path("/path/to/vscode/User/globalStorage"))
    
    @patch("src.core.utils.get_vscode_path")
    def test_get_backup_dir(self, mock_get_vscode_path):
        """
        Test the get_backup_dir function.
        """
        mock_get_vscode_path.return_value = Path("/path/to/vscode")
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            path = get_backup_dir()
            self.assertEqual(path, Path("/path/to/vscode/resetter_backups"))
            mock_mkdir.assert_called_once_with(exist_ok=True, parents=True)
    
    @patch("src.core.utils.datetime")
    def test_create_backup_id(self, mock_datetime):
        """
        Test the create_backup_id function.
        """
        mock_datetime.now.return_value.strftime.return_value = "20220101_120000"
        backup_id = create_backup_id()
        self.assertEqual(backup_id, "backup_20220101_120000")
    
    def test_generate_new_machine_id(self):
        """
        Test the generate_new_machine_id function.
        """
        machine_id = generate_new_machine_id()
        self.assertIsInstance(machine_id, str)
        self.assertGreater(len(machine_id), 0)

if __name__ == "__main__":
    unittest.main()
