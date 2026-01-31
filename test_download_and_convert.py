"""
Unit tests for download_and_convert.py
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Import the module to test
import download_and_convert


class TestCheckDependencies(unittest.TestCase):
    """Tests for check_dependencies function."""

    @patch('download_and_convert.subprocess.run')
    def test_check_dependencies_installed(self, mock_run):
        """Test returns True when yt-dlp is installed."""
        mock_run.return_value = MagicMock(returncode=0)
        result = download_and_convert.check_dependencies()
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ["yt-dlp", "--version"], 
            capture_output=True, 
            check=True
        )

    @patch('download_and_convert.subprocess.run')
    def test_check_dependencies_not_installed(self, mock_run):
        """Test returns False when yt-dlp is not installed."""
        mock_run.side_effect = FileNotFoundError()
        result = download_and_convert.check_dependencies()
        self.assertFalse(result)

    @patch('download_and_convert.subprocess.run')
    def test_check_dependencies_error(self, mock_run):
        """Test returns False when yt-dlp command fails."""
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, "yt-dlp")
        result = download_and_convert.check_dependencies()
        self.assertFalse(result)


class TestInstallYtdlp(unittest.TestCase):
    """Tests for install_ytdlp function."""

    @patch('download_and_convert.subprocess.run')
    def test_install_ytdlp_calls_pip(self, mock_run):
        """Test that install_ytdlp calls pip correctly."""
        download_and_convert.install_ytdlp()
        mock_run.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
            check=True
        )


class TestDownloadAndConvert(unittest.TestCase):
    """Tests for download_and_convert function."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_dir = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Tear down test fixtures."""
        os.chdir(self.original_dir)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch('download_and_convert.check_dependencies')
    def test_no_links_file(self, mock_check_deps):
        """Test error handling when links.txt doesn't exist."""
        mock_check_deps.return_value = True
        
        # Should not raise an exception
        download_and_convert.download_and_convert()
        
        # Verify no output folder was created
        self.assertFalse(os.path.exists("mp3_output"))

    @patch('download_and_convert.check_dependencies')
    def test_empty_links_file(self, mock_check_deps):
        """Test error handling when links.txt is empty."""
        mock_check_deps.return_value = True
        
        # Create empty links file
        with open("links.txt", "w") as f:
            f.write("")
        
        # Should not raise an exception
        download_and_convert.download_and_convert()

    @patch('download_and_convert.check_dependencies')
    def test_links_file_with_only_comments(self, mock_check_deps):
        """Test handling of links.txt with only comments."""
        mock_check_deps.return_value = True
        
        with open("links.txt", "w") as f:
            f.write("# This is a comment\n")
            f.write("# Another comment\n")
        
        download_and_convert.download_and_convert()

    @patch('download_and_convert.subprocess.run')
    @patch('download_and_convert.check_dependencies')
    def test_installs_ytdlp_if_missing(self, mock_check_deps, mock_run):
        """Test that yt-dlp is installed if not found."""
        mock_check_deps.return_value = False
        
        # Create links file to get past initial checks
        with open("links.txt", "w") as f:
            f.write("https://example.com/video.mp4\n")
        
        download_and_convert.download_and_convert()
        
        # Verify pip install was called
        install_calls = [
            call for call in mock_run.call_args_list 
            if "pip" in str(call)
        ]
        self.assertEqual(len(install_calls), 1)

    @patch('download_and_convert.subprocess.run')
    @patch('download_and_convert.check_dependencies')
    def test_creates_output_folder(self, mock_check_deps, mock_run):
        """Test that mp3_output folder is created."""
        mock_check_deps.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        
        with open("links.txt", "w") as f:
            f.write("https://example.com/video.mp4\n")
        
        download_and_convert.download_and_convert()
        
        self.assertTrue(os.path.exists("mp3_output"))

    @patch('download_and_convert.subprocess.run')
    @patch('download_and_convert.check_dependencies')
    def test_ytdlp_command_structure(self, mock_check_deps, mock_run):
        """Test that yt-dlp is called with correct arguments."""
        mock_check_deps.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        
        with open("links.txt", "w") as f:
            f.write("https://example.com/video.mp4\n")
        
        download_and_convert.download_and_convert()
        
        # Get the yt-dlp call
        ytdlp_calls = [
            call for call in mock_run.call_args_list 
            if "yt-dlp" in str(call)
        ]
        self.assertEqual(len(ytdlp_calls), 1)
        
        # Verify key arguments are present
        call_args = ytdlp_calls[0][0][0]
        self.assertIn("yt-dlp", call_args)
        self.assertIn("--cookies-from-browser", call_args)
        self.assertIn("-x", call_args)
        self.assertIn("--audio-format", call_args)
        self.assertIn("mp3", call_args)


class TestLinksParsing(unittest.TestCase):
    """Tests for link parsing logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_dir = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Tear down test fixtures."""
        os.chdir(self.original_dir)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_valid_links(self):
        """Test parsing valid links from file."""
        with open("links.txt", "w") as f:
            f.write("https://example.com/video1.mp4\n")
            f.write("https://example.com/video2.mp4\n")
            f.write("https://example.com/video3.mp4\n")
        
        with open("links.txt", "r") as f:
            links = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        self.assertEqual(len(links), 3)

    def test_skip_comments(self):
        """Test that comments are skipped."""
        with open("links.txt", "w") as f:
            f.write("# Comment line\n")
            f.write("https://example.com/video1.mp4\n")
            f.write("# Another comment\n")
            f.write("https://example.com/video2.mp4\n")
        
        with open("links.txt", "r") as f:
            links = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        self.assertEqual(len(links), 2)

    def test_skip_empty_lines(self):
        """Test that empty lines are skipped."""
        with open("links.txt", "w") as f:
            f.write("https://example.com/video1.mp4\n")
            f.write("\n")
            f.write("   \n")
            f.write("https://example.com/video2.mp4\n")
        
        with open("links.txt", "r") as f:
            links = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        
        self.assertEqual(len(links), 2)


if __name__ == "__main__":
    unittest.main()
