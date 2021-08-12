import pytest
import time
import os
from fileindexer.fileparser import  write_index_file


def test_write_index_file_case_new_file(tmpdir_factory):
    """
    Empty temp dir then new file created
    """
    file_to_create = os.path.join(tmpdir_factory.getbasetemp(), "test")
    assert(os.path.isfile(file_to_create + ".pbz2")== False)
    write_index_file(file_to_create, None)
    assert(os.path.isfile(file_to_create + ".pbz2")== True)

def test_write_index_file_case_replace_file(tmpdir_factory):
    """
    Empty temp dir then new file created
    """
    file_to_create = os.path.join(tmpdir_factory.getbasetemp(), "new_file")
    write_index_file(file_to_create, None)
    assert(os.path.isfile(file_to_create + ".pbz2"))
    file_created_time = os.stat(file_to_create + ".pbz2").st_mtime
    time.sleep(1)
    #Verify if the file was updated
    write_index_file(file_to_create, None)
    new_file_created_time = os.stat(file_to_create + ".pbz2").st_mtime
    assert(file_created_time != new_file_created_time)

