from guppy import hpy
import time
import os
import File_dir
import pickle
import bz2
import fnmatch
from utils import trace
import asyncio


def parseDirectory(index_file_name, dirName):
    h = hpy()
    # Get the list of all files in directory tree at given path
    st = time.time()
    setOfFiles = set()
    for (dirpath, _, filenames) in os.walk(dirName):
        setOfFiles.update(set([os.path.join(dirpath, file)
                          for file in filenames]))
    ed = time.time()
    File_dir.trace(
        f'Terminé en {(ed-st):.2f} secondes : {len(setOfFiles)} fichiers')

    # save the set into a pickle
    write_index_file(index_file_name, setOfFiles)

    # Print memory usage
    trace(h.heap())


def write_index_file(my_index_file, myset):
    trace(f'Writing & compressing index file : {my_index_file}')
    with bz2.BZ2File(my_index_file + '.pbz2', 'w') as f:
        pickle.dump(myset, f)


async def searchWithWildcards(my_index_file, mySearch, output_file):
    i = 0
    st = time.time()
    if output_file != '':
        i = await export_to_file(my_index_file, mySearch, output_file)
    else:
        i = await export_to_print(my_index_file, mySearch)
    ed = time.time()
    trace(f'Recherche terminée en {(ed-st):.2f} secondes : {i} resultats')


async def export_to_file(my_index_file, mySearch, output_file):
    i = 0
    results = []

    for r in findFilesWithName(my_index_file, mySearch):
        # Récupère des infos sur le fichier  : ça ralenti un peu
        r = await generate_file_with_size(r)
        results.append(r)
        i += 1

    with open(output_file, 'w') as f:
        trace(f"La sortie est dirigée vers le fichier {output_file}")
        f.write('filename;complete_filename;size(kb)\n')
        f.writelines([s for s in results])
    return i


async def export_to_print(my_index_file, mySearch):
    tasks = []
    i = 0
    for r in findFilesWithName(my_index_file, mySearch):
        # Récupère des infos sur le fichier  : ça ralenti un peu
        tasks.append(asyncio.ensure_future(generate_file_with_size(r)))
        i += 1
    await asyncio.gather(*tasks, return_exceptions=True)
    return i


async def generate_file_with_size(r):
    result = ""
    try:
        size = await get_file_size(r)
        result = f'{r.split(os.path.sep)[-1]};{r};{ size / (1024):.2f}\n'
    except FileNotFoundError:
        # Sur des chemins trop longs, windows ne retrouve pas le fichier
        result = f'{r.split(os.path.sep)[-1]};{r};0'
    # trace(result)
    return result


async def get_file_size(f):
    s = os.stat(f).st_size
    return s


def findFilesWithName(my_index_file, mysearch):
    trace(f"Starting findFilesWithName with search : {mysearch}")
    for item in read_index_file(my_index_file):
        # File Name match : permet d'utiliser des * ou ? (plus simple que des regexp)
        if fnmatch.fnmatch(item.split(os.path.sep)[-1], mysearch):
            yield item


def findFilesInSet(my_set, my_search):
    for item in my_set:
        # File Name match : permet d'utiliser des * ou ? (plus simple que des regexp)
        # For now it is case sensitive
        if fnmatch.fnmatch(item.split(os.path.sep)[-1], my_search):
            yield item


def read_index_file(my_index_file):
    trace(f'Uncompressing & Reading index file : {my_index_file}')
    data = bz2.BZ2File(my_index_file + '.pbz2', 'rb')
    myset = pickle.load(data)
    trace(f'Return un set de longueur : {len(myset)}')
    return myset
