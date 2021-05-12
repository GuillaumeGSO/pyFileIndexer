import os
import getopt
import sys
import time
from guppy import hpy
import pickle
import bz2
import fnmatch


def main():
    DESC = '''
    Indexation et recherche par wildcard (* et ?) sur des noms de fichiers

    Exemples : 
    1 - indexer mon disque dur :
        >>python file_dir.py -index "lecteurC" -path "c:\"
        un fichier d'index lecteurC.pbz2 sera générer (compressé)
    2 - recherche tous les fichiers log
        >>python file_dir.py -find "*.log" -i "lecteurC"
        le fichier d'index lu doit se nommer lecteurC.pbz2


    Usage : 
    -h ou --help : affiche l'aide
    -v ou --verbose : affiche plus d'information sur la sortie standard

    ***** Mode indexation : 2 paramètres obligatoires *****
    -p ou --path <pathname>: chemin à indexer
    -i ou --index <indexfilename> : lance l'indexation de <pathname> et écrit l'indexe dans <indexfilename>

    ***** Mode recherche : 2 paramètres obligatoires *****
    -f ou --find <search>: recherche dans le fichier d'index <indexfilename> les noms de fichiers qui correspondent :
            *.xls : tous les fichiers Excel
            *202?.log : tous les fichiers .log comme fic2020.log, param2021.log, etc 
    -i ou --index <indexfilename> : utilise le fichier d'index <indexfilename> (obligatoire)
    -o ou --output <ouputfilename>: écrire le résultat de la recherche dans le fichier <ouputfilename>
            (ignoré si pas en mode recherche)
    '''
    global VERBOSE
    VERBOSE = False
    PATH_NAME = ''
    INDEX_FILE_NAME = ''
    FIND_STRING = ''
    OUTPUT_FILE = ''

    full_cmd_arguments = sys.argv
    argument_list = full_cmd_arguments[1:]
    short_options = "hvp:i:f:o:"
    long_options = ["help", "verbose",
                    "pathname=", "index=", "find=", "output="]

    try:
        arguments, _ = getopt.getopt(
            argument_list, short_options, long_options)
    except getopt.error as err:
        print(str(err))
        sys.exit(2)

    # Evaluate given options
    for current_argument, current_value in arguments:
        if current_argument in ("-v", "--verbose"):
            print("Enabling verbose mode")
            VERBOSE = True
        elif current_argument in ("-h", "--help"):
            print(DESC)
        elif current_argument in ("-p", "--pathname"):
            PATH_NAME = current_value
        elif current_argument in ("-i", "--index"):
            INDEX_FILE_NAME = current_value
        elif current_argument in ("-f", "--find"):
            FIND_STRING = current_value
        elif current_argument in ("-o", "--output"):
            OUTPUT_FILE = current_value

    # Appliquer les règles de fonctionnement le plus simplement possible

    # Il faut au moins choisir un mode : indexation ou recherche
    if PATH_NAME == '' and FIND_STRING == '':
        print(DESC)
        print("Erreur de syntaxe : ni indexation ni recherche demandée")
        sys.exit(2)

    # indexation et recherche incompatibles
    if PATH_NAME != '' and FIND_STRING != '':
        print(DESC)
        print("<pathname> ne peut pas être utiliser en même temps que <search>")
        sys.exit(2)

    # indexation a besoin d'un chemin
    if INDEX_FILE_NAME != '' and PATH_NAME == '' and FIND_STRING == '':
        print(DESC)
        print("<pathname> obligatoire si demande d'indexation")
        sys.exit(2)

    # Recherche demandée sans fichier d'index
    if INDEX_FILE_NAME == '':
        print(DESC)
        print("<indexfilename> obligatoire pour lancer une recherche")
        sys.exit(2)

    # Lancement de l'indexation
    if INDEX_FILE_NAME != '' and PATH_NAME != '':
        if OUTPUT_FILE != '':
            print("Warning : <output> est ignoré en mode indexation")
        try:
            parseDirectory(INDEX_FILE_NAME, PATH_NAME)
        except RuntimeError as err:
            print("Erreur pendant l'indexation...-v pour visualiser")
            trace(str(err))
            sys.exit(2)

    # Lancement recherche
    if INDEX_FILE_NAME != '' and FIND_STRING != '':
        try:
            searchWithWildcards(INDEX_FILE_NAME, FIND_STRING, OUTPUT_FILE)
        except RuntimeError as err:
            print("Erreur pendant la recherche... -v pour visualiser")
            trace(str(err))
            sys.exit(2)


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


def trace(trc):
    if VERBOSE:
        print(trc)


"""
Cette methode est bien plus rapide que par recursivité (12s vs 32s)
Elle est aussi moins gourmande en mémoire (15Mb vs 38Mb)
"""


def parseDirectory(index_file_name, dirName):
    h = hpy()
    # Get the list of all files in directory tree at given path
    st = time.time()
    setOfFiles = set()
    for (dirpath, _, filenames) in os.walk(dirName):
        setOfFiles.update(set([os.path.join(dirpath, file)
                          for file in filenames]))
    ed = time.time()
    trace(f'Terminé en {(ed-st):.2f} secondes : {len(setOfFiles)} fichiers')

    # save the set into a pickle
    write_index_file(index_file_name, setOfFiles)

    # Print memory usage
    trace(h.heap())


def write_index_file(my_index_file, myset):
    trace(f'Writing & compressing index file : {my_index_file}')
    with bz2.BZ2File(my_index_file + '.pbz2', 'w') as f:
        pickle.dump(myset, f)


def read_index_file(my_index_file):
    trace(f'Uncompressing & Reading index file : {my_index_file}')
    data = bz2.BZ2File(my_index_file + '.pbz2', 'rb')
    myset = pickle.load(data)
    trace(f'Return un set de longueur : {len(myset)}')
    return myset


def findFilesWithName(my_index_file, mysearch):
    trace(f"Starting findFilesWithName with search : {mysearch}")
    for item in read_index_file(my_index_file):
        # File Name match : permet d'utiliser des * ou ? (plus simple que des regexp)
        if fnmatch.fnmatch(item.split(os.path.sep)[-1], mysearch):
            yield item


if __name__ == '__main__':
    main()
