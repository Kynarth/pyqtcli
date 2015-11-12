from pyqtcli.option import recursive_process


def test_search_files_in_different_directories(tmpdir):
    # Create tmp directories and files for testing
    res = tmpdir.join("res.qrc")
    res.write("test")

    res_bis = tmpdir.join("res_bis.qrc")
    res_bis.write("test")

    trap = tmpdir.join("trap.py")
    trap.write("test")

    test = tmpdir.mkdir("test_dir").join("test.qrc")
    test.write("test")

    another = tmpdir.mkdir("another_dir").join("another.qrc")
    another.write("test")

    # Launch recursive searches
    result = recursive_process(tmpdir.strpath)
    assert sorted(result) == sorted((
        res.strpath, res_bis.strpath, test.strpath, another.strpath
    ))

    result = recursive_process(tmpdir.strpath + "/test_dir")
    assert sorted(result) == sorted((test.strpath,))
