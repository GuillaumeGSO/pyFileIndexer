"""
File parser
"""
import threading
import time
import os
import queue
import pickle
import bz2
import fnmatch
from . import trace


def parse_directory(index_file_name, dir_name):
    """
    Get the list of all files in directory tree at given path
    """
    start = time.time()
    set_of_files = set()
    for (dirpath, _, filenames) in os.walk(dir_name):
        set_of_files.update({os.path.join(dirpath, file)
                             for file in filenames})
    end = time.time()
    trace(
        f'Finished in {(end-start):.2f} secondes : {len(set_of_files)} files indexed')

    # save the set into a compressed pickle file
    write_index_file(index_file_name, set_of_files)


def write_index_file(my_index_file, myset):
    """
    Create or replace the index files with the content of the set
    """
    trace(f'Writing & compressing index file : {my_index_file}')
    with bz2.BZ2File(my_index_file + '.pbz2', 'w') as file:
        pickle.dump(myset, file)


def search_with_wildcards(my_index_file, my_search, output_file=''):
    """
    Search with wildcards
    """
    i = 0
    start = time.time()
    if output_file != '':
        i = export_to_file(my_index_file, my_search, output_file)
    else:
        i = export_to_print(my_index_file, my_search)
    end = time.time()
    trace(
        f'Recherche terminée en {(end-start):.2f} secondes : {i} resultats')


def export_to_file(my_index_file, my_search, output_file):
    """
    Export results to a csv file
    """
    i = 0
    results = []

    for file in find_files_with_name(my_index_file, my_search):
        # Récupère des infos sur le fichier  : ça ralenti un peu
        results.append(generate_file_with_size(file))
        i += 1

    with open(output_file, 'w') as file:
        trace(
            f"La sortie est dirigée vers le fichier {output_file}")
        file.write('filename;complete_filename;size(kb)\n')
        file.writelines(results)
    return i


def worker(queued):
    """
    initialize a worker to retrieve a file size
    """
    while True:
        item = queued.get()
        if item is None:
            break
        generate_file_with_size(item)
        queued.task_done()


def export_to_print(my_index_file, my_search):
    """
    Export to console with file size
    """
    my_queue = queue.Queue()
    for file in find_files_with_name(my_index_file, my_search):
        my_queue.put(file)
    i = my_queue.qsize()

    threads = []
    for _ in range(10):
        thread = threading.Thread(target=worker, args=(my_queue,))
        thread.start()
        threads.append(thread)
    my_queue.join()

    for _ in range(10):
        my_queue.put(None)

    for thread in threads:
        thread.join()

    return i


def generate_file_with_size(file_name):
    """
    Generate file with size
    """
    result = ""
    try:
        size = get_file_size(file_name)
        result = f'{file_name.split(os.path.sep)[-1]};{file_name};{ size / (1024):.2f}\n'
    except FileNotFoundError:
        # Sometimes Windows doesn't find a file if the path is too long
        result = f'{file_name.split(os.path.sep)[-1]};{file_name};0\n'
    trace(result)
    return result


def get_file_size(file):
    """
    returns the file size
    """
    return os.stat(file).st_size


def find_files_with_name(my_index_file, my_search):
    """
    find files with name
    """
    trace(f"Starting findFilesWithName with search : {my_search}")
    for item in read_index_file(my_index_file):
        # File Name match : allow use of * ou ? wildcard (simpler than regexp)
        if fnmatch.fnmatch(item.split(os.path.sep)[-1], my_search):
            yield item


def read_index_file(my_index_file):
    """
    Uncompress and reads the index file
    """
    trace(f'Uncompressing & Reading index file : {my_index_file}')
    data = bz2.BZ2File(my_index_file + '.pbz2', 'rb')
    my_set = pickle.load(data)
    trace(f'Set length returned : {len(my_set)}')
    return my_set
