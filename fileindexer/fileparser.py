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

VERBOSE = True
def trace(trc, verbose=False):
    """
    displays logs on console if verbose mode
    """
    if verbose:
        print(trc)


def parse_directory(index_file_name, dir_name, verbose = False):
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
        f'Finished in {(end-start):.2f} secondes : {len(set_of_files)} files indexed', verbose)

    # save the set into a compressed pickle file
    write_index_file(index_file_name, set_of_files, verbose)


def write_index_file(my_index_file, my_set, verbose = False):
    """
    Create or replace the index files with the content of the set
    """
    trace(f'Writing & compressing index file : {my_index_file}', verbose)
    with bz2.BZ2File(my_index_file + '.pbz2', 'w') as file:
        pickle.dump(my_set, file)


def search_with_wildcards(my_index_file, my_search, output_file='', verbose = False):
    """
    Search with wildcards
    """
    i = 0
    start = time.time()
    if output_file != '':
        i = export_to_file(my_index_file, my_search, output_file, verbose)
    else:
        i = export_to_print(my_index_file, my_search, verbose)
    end = time.time()
    trace(
        f'Search done in {(end-start):.2f} secondes : {i} results', verbose)


def export_to_file(my_index_file, my_search, output_file, verbose):
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
            f"Results are redirected vers {output_file} file", verbose)
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


def export_to_print(my_index_file, my_search, verbose = False):
    """
    Export to console with file size
    """
    my_queue = queue.Queue()
    for file in find_files_with_name(my_index_file, my_search, verbose):
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


def generate_file_with_size(file_name, verbose = False):
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
    trace(result, verbose)
    return result


def get_file_size(file):
    """
    returns the file size
    """
    return os.stat(file).st_size


def find_files_with_name(my_index_file, my_search, verbose = False):
    """
    find files with name
    """
    trace(f"Starting search : {my_search}", verbose)
    for item in read_index_file(my_index_file, verbose):
        # File Name match : allow use of * ou ? wildcard (simpler than regexp)
        if fnmatch.fnmatch(item.split(os.path.sep)[-1], my_search):
            yield item


def read_index_file(my_index_file, verbose = False):
    """
    Uncompress and reads the index file
    """
    trace(f'Uncompressing & reading index file : {my_index_file}', verbose)
    data = bz2.BZ2File(my_index_file + '.pbz2', 'rb')
    my_set = pickle.load(data)
    trace(f'Set length returned : {len(my_set)}', verbose)
    return my_set
