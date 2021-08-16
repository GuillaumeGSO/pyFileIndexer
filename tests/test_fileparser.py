"""
Testing fileparser.py
"""
import os
import time
from fileindexer.fileparser import find_files_with_name, generate_file_with_size
from fileindexer.fileparser import parse_directory, read_index_file
from fileindexer.fileparser import search_with_wildcards, write_index_file


def test_parse_directory(tmp_path):
    """
    creates an index file in the temp path
    """
    parse_directory(os.path.join(tmp_path, "test_test"), tmp_path)
    assert os.path.isfile(os.path.join(tmp_path, "test_test.pbz2"))


def test_write_index_file_case_new_file(tmp_path):
    """
    Empty temp dir then new file created
    """
    file_to_create = os.path.join(tmp_path, "test")
    assert not os.path.isfile(file_to_create + ".pbz2")
    write_index_file(file_to_create, None)
    assert os.path.isfile(file_to_create + ".pbz2")


def test_write_index_file_case_replace_file(tmp_path):
    """
    Empty temp dir then new file created
    """
    file_to_create = os.path.join(tmp_path, "new_file")
    write_index_file(file_to_create, None)
    assert os.path.isfile(file_to_create + ".pbz2")
    file_created_time = os.stat(file_to_create + ".pbz2").st_mtime
    time.sleep(1)
    #Verify if the file was updated
    write_index_file(file_to_create, None)
    new_file_created_time = os.stat(file_to_create + ".pbz2").st_mtime
    assert file_created_time != new_file_created_time


def test_write_index_file_case_log(tmp_path, capsys):
    """
    verbose test FIXME
    """
    file_to_create = os.path.join(tmp_path, "index_log")
    write_index_file(file_to_create, None, True)
    out, err = capsys.readouterr()
    assert 'Writing & compressing' in out
    assert 'index_log' in out
    assert err == ''


def test_search_with_wildcards_result_no_output(create_and_populate_search_file, capsys):
    """
    search with results and no output file
    """
    search_with_wildcards(create_and_populate_search_file, "abc.pdf", True)
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''

def test_search_with_wildcards_no_result_no_output(create_and_populate_search_file, capsys):
    """
    search with no result and no ouput
    """
    search_with_wildcards(create_and_populate_search_file, "xxx", verbose = True)
    out, err = capsys.readouterr()
    assert 'Starting search' in out
    assert "xxx" in out
    assert err == ''


def test_search_with_wildcards_result_output(create_and_populate_search_file, tmp_path, capsys):
    """
    search with result and output
    """
    out_path = os.path.join(tmp_path, "out.txt")
    search_with_wildcards(create_and_populate_search_file,
                          "abc.pdf", out_path, True)
    assert os.path.isfile(os.path.join(tmp_path, "out.txt"))
    out, err = capsys.readouterr()
    assert 'Results are redirected' in out
    assert out_path in out
    assert err == ''

def test_search_with_wildcards_no_result_output(create_and_populate_search_file, tmp_path, capsys):
    """
    search with not result and output
    """
    out_path = os.path.join(tmp_path, "out.txt")
    search_with_wildcards(create_and_populate_search_file,
                          "xxx", out_path, True)
    assert os.path.isfile(os.path.join(tmp_path, "out.txt"))
    out, err = capsys.readouterr()
    assert 'Results are redirected' in out
    assert out_path in out
    assert err == ''

def test_read_index_file(create_and_populate_search_file, capsys):
    """
    retrieving the test set (defined in conftest.py)
    """
    result = read_index_file(create_and_populate_search_file, True)
    assert len(result) == 5
    out, err = capsys.readouterr()
    assert 'Uncompressing & reading' in out
    assert err == ''


def test_find_files_with_name_0(create_and_populate_search_file, capsys):
    """
    simple test : no result, no verbose
    """
    assert len(list(find_files_with_name(
        create_and_populate_search_file, "xxx"))) == 0
    out, err = capsys.readouterr()
    assert out == ''
    assert err == ''


def test_find_files_with_name_1(create_and_populate_search_file):
    """
    simple test : one result
    """
    assert len(list(find_files_with_name(
        create_and_populate_search_file, "abc.pdf"))) == 1


def test_find_files_with_name_2(create_and_populate_search_file):
    """
    search with results from different directories
    """
    assert len(list(find_files_with_name(
        create_and_populate_search_file, "dbc.pdf"))) == 2


def test_find_files_with_name_star(create_and_populate_search_file):
    """
    search with * wildcard
    """
    assert len(list(find_files_with_name(
        create_and_populate_search_file, "*.pdf"))) == 4


def test_find_files_with_name_quest(create_and_populate_search_file):
    """
    search with ? wildcard
    """
    assert len(list(find_files_with_name(
        create_and_populate_search_file, "?bc.pdf"))) == 3

def test_generate_file_with_size_existing(create_and_populate_search_file):
    """
    if the created index file is read with size
    """
    result = generate_file_with_size(create_and_populate_search_file + ".pbz2")
    lst = result.split(';')
    assert lst[0] == 'index_test.pbz2'
    assert create_and_populate_search_file + ".pbz2" == lst[1]
    assert lst[2] != '0\n'  # Size is real


def test_generate_file_with_size_non_existing(create_and_populate_search_file):
    """
    when the file doesn't exist, its size is 0
    """
    result = generate_file_with_size(create_and_populate_search_file + ".xxx")
    lst = result.split(';')
    assert lst[0] == 'index_test.xxx'
    assert create_and_populate_search_file + ".xxx" == lst[1]
    assert lst[2] == '0\n'  # File not found thus size = 0
