import sys

def test_python_version_is_pinned():
    assert sys.version_info.major == 3
    assert sys.version_info.minor == 12
