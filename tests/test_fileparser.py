import pytest
import time
import os
from fileindexer.fileparser import  find_files_with_name, parse_directory, write_index_file


def test_write_index_file_case_new_file(tmp_path):
    """
    Empty temp dir then new file created
    """
    file_to_create = os.path.join(tmp_path, "test")
    assert(os.path.isfile(file_to_create + ".pbz2")== False)
    write_index_file(file_to_create, None)
    assert(os.path.isfile(file_to_create + ".pbz2")== True)

def test_write_index_file_case_replace_file(tmp_path):
    """
    Empty temp dir then new file created
    """
    file_to_create = os.path.join(tmp_path, "new_file")
    write_index_file(file_to_create, None)
    assert(os.path.isfile(file_to_create + ".pbz2"))
    file_created_time = os.stat(file_to_create + ".pbz2").st_mtime
    time.sleep(1)
    #Verify if the file was updated
    write_index_file(file_to_create, None)
    new_file_created_time = os.stat(file_to_create + ".pbz2").st_mtime
    assert(file_created_time != new_file_created_time)

def test_write_index_file_case_log(tmp_path, capsys):
    file_to_create = os.path.join(tmp_path, "index_log")
    write_index_file(file_to_create, None)
    out, err = capsys.readouterr()
    #FIXME should read the trace (verbose mode problem ?)
    assert(out == '')
    assert(err == '')

def test_find_files_with_name_0(create_and_populate_search_file):
    assert(len(list(find_files_with_name(create_and_populate_search_file, "xxx"))) == 0)

def test_find_files_with_name_1(create_and_populate_search_file):
    assert(len(list(find_files_with_name(create_and_populate_search_file, "abc.pdf"))) == 1)

def test_find_files_with_name_2(create_and_populate_search_file):
    assert(len(list(find_files_with_name(create_and_populate_search_file, "dbc.pdf"))) == 2)

def test_find_files_with_name_star(create_and_populate_search_file):
    assert(len(list(find_files_with_name(create_and_populate_search_file, "*.pdf"))) == 4)

def test_find_files_with_name_quest(create_and_populate_search_file):
    assert(len(list(find_files_with_name(create_and_populate_search_file, "?bc.pdf"))) == 3)


def test_parse_directory(tmp_path):
    parse_directory(os.path.join(tmp_path, "test_index"), tmp_path)

