import pytest
from pathlib import Path
import os
import sys
# Find the absolute path for the file that I am going to test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from cleaning.utils import remove

@pytest.mark.parametrize("input_words, expected_output", [
    (["hello!", "world.", "test'case"], ["hello", "world", "testcase"]),
    (["@python#", "c@de$", "w@ve%"], ["python", "cde", "wve"]),
    (["clean", "list", "words"], ["clean", "list", "words"]),
    ([], []),                                                          
])

def test_remove(input_words, expected_output):
    """
    Test that remove function removes unwanted characters correctly.
    """
    assert remove(input_words) == expected_output











