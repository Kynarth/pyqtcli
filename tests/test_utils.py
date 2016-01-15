import pytest

from pyqtcli.utils import recursive_file_search


# noinspection PyUnusedLocal
def test_search_mp3_in_different_directories(test_resources):
    mp3_files = recursive_file_search("mp3", "resources")
    assert sorted(mp3_files) == [
        'resources/musics/solos/best/best_solo1.mp3',
        'resources/musics/solos/best/best_solo2.mp3',
        'resources/musics/solos/solo1.mp3',
        'resources/musics/solos/solo2.mp3'
    ]


def test_search_files_in_nonexistent_directory():
    with pytest.raises(FileNotFoundError) as e:
        recursive_file_search("txt", "nonexistent")
    assert str(e.value) == "No such directory: 'nonexistent'"
