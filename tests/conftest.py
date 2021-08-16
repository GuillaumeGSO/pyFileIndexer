"""
Write here some specific fixtures
"""
import os
import pytest
import fileindexer.fileparser

@pytest.fixture(scope = 'function')
def create_and_populate_search_file(tmp_path):
    """
    Initialize a set and the tmp_path for testing
    """
    my_set = {'abc.txt', 'abc.pdf', 'dbc.pdf',
    'level2\\dbc.pdf', 'level2/dbc.pdf'}
    file_to_create = os.path.join(tmp_path, "index_test")
    fileindexer.fileparser.write_index_file(file_to_create, my_set)
    yield file_to_create
