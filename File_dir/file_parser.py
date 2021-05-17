from guppy import hpy
import time
import os
import File_dir
import pickle
import bz2
import fnmatch
from utils import trace


def parseDirectory(index_file_name, dirName):
    h = hpy()
    # Get the list of all files in directory tree at given path
    st = time.time()
    setOfFiles = set()
    for (dirpath, _, filenames) in os.walk(dirName):
        setOfFiles.update(set([os.path.join(dirpath, file)
                          for file in filenames]))
    ed = time.time()
    File_dir.trace(f'Terminé en {(ed-st):.2f} secondes : {len(setOfFiles)} fichiers')

    # save the set into a pickle
    write_index_file(index_file_name, setOfFiles)

    # Print memory usage
    trace(h.heap())

def write_index_file(my_index_file, myset):
    trace(f'Writing & compressing index file : {my_index_file}')
    with bz2.BZ2File(my_index_file + '.pbz2', 'w') as f:
        pickle.dump(myset, f)

def searchWithWildcards(my_index_file, mySearch, output_file):
    i = 0
    st = time.time()
    if output_file != '':
        with open(output_file, 'w') as f:
            print(f"La sortie est dirigée vers le fichier {output_file}")
            f.write('filename;complete_filename;size(kb)\n')
            for r in findFilesWithName(my_index_file, mySearch):

                # Récupère des infos sur le fichier  : ça ralenti un peu
                try:
                    f.write(
                        f'{r.split(os.path.sep)[-1]};{r};{os.stat(r).st_size / (1024):.2f}\n')
                except FileNotFoundError:
                    # Sur des chemins trop longs, windows ne retrouve pas le fichier
                    f.write(f'{r.split(os.path.sep)[-1]};0\n')
                i += 1
    else:
        # FIXME très très moche : il faut utiliser stdout pour changer la sortie standard !
        for r in findFilesWithName(my_index_file, mySearch):

            # Récupère des infos sur le fichier  : ça ralenti un peu
            try:
                print(
                    f'{r.split(os.path.sep)[-1]};{os.stat(r).st_size / (1024):.2f}')
            except FileNotFoundError:
                # Sur des chemins trop longs, windows ne retrouve pas le fichier
                print(f'{r.split(os.path.sep)[-1]};0')
            i += 1
    ed = time.time()
    trace(f'Terminé en {(ed-st):.2f} secondes : {i} resultats')

def findFilesWithName(my_index_file, mysearch):
    trace(f"Starting findFilesWithName with search : {mysearch}")
    for item in read_index_file(my_index_file):
        # File Name match : permet d'utiliser des * ou ? (plus simple que des regexp)
        if fnmatch.fnmatch(item.split(os.path.sep)[-1], mysearch):
            yield item

def read_index_file(my_index_file):
    trace(f'Uncompressing & Reading index file : {my_index_file}')
    data = bz2.BZ2File(my_index_file + '.pbz2', 'rb')
    myset = pickle.load(data)
    trace(f'Return un set de longueur : {len(myset)}')
    return myset