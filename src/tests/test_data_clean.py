import pytest
from pathlib import Path
import os
import sys
# Find the absolute path for the file that I am going to test
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from cleaning.utils import remove, process_word_list, ignore

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


@pytest.mark.parametrize("input_words, expected_output", [
    # Keep the words end with "ss"
    (["class", "boss", "miss"], ["class", "boss", "miss"]),
    # Transform "ies" to "y"
    (["cities", "puppies", "bodies", "city", "puppy", "body"], ["city", "puppy", "body", "city", "puppy", "body"]),
    # Transform the plural form that ends with "es"
    (["boxes", "churches", "foxes", "box", "church", "fox"], ["box", "church", "fox", "box", "church", "fox"]),
    # Transform the plural form that ends with "s"
    (["cars", "dogs", "cats", "car", "dog", "cat"], ["car", "dog", "cat", "car", "dog", "cat"]),
    # Normal words
    (["apple", "banana", "grape"], ["apple", "banana", "grape"]),
    # Empty lists
    ([], []),
])
def test_process_word_list(input_words, expected_output):
    assert process_word_list(input_words) == expected_output



@pytest.mark.parametrize("input_words, expected_output", [
    (["am", "is", "are","research", "study","log"], []),
    (["python", "machine", "learning"], ["python", "machine", "learning"]),
    (["a", "an", "hi", "ok"], []),
    (["123", "2025"], []),
    (["the", "university", "of", "chicago", "computer", "science", "department", "james", "cool"], ["university", "chicago", "computer", "department", "james", "cool"]),
])
def test_ignore(input_words, expected_output):
    assert ignore(input_words) == expected_output





    













