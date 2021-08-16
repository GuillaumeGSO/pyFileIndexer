"""
Indexer module with search tool
"""
import sys
import getopt
from .fileparser import search_with_wildcards, parse_directory, trace

def main():
    """
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
    -i ou --index <indexfilename> : lance l'indexation de <pathname>
                                et écrit l'indexe dans <indexfilename>

    ***** Mode recherche : 2 paramètres obligatoires *****
    -f ou --find <search>: recherche dans le fichier d'index <indexfilename>
            les noms de fichiers qui correspondent :
                *.xls : tous les fichiers Excel
                *202?.log : tous les fichiers .log comme fic2020.log, param2021.log, etc
    -i ou --index <indexfilename> : utilise le fichier d'index <indexfilename> (obligatoire)
    -o ou --output <ouputfilename>: écrire le résultat de la recherche
            dans le fichier <ouputfilename>
            (ignoré si pas en mode recherche)
    """

    path_name = ''
    index_file_name = ''
    find_string = ''
    output_file = ''
    verbose = False

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
            verbose = True
        elif current_argument in ("-h", "--help"):
            print(__doc__)
        elif current_argument in ("-p", "--pathname"):
            path_name = current_value
        elif current_argument in ("-i", "--index"):
            index_file_name = current_value
        elif current_argument in ("-f", "--find"):
            find_string = current_value
        elif current_argument in ("-o", "--output"):
            output_file = current_value

    # Stop if arguments are incorrects
    check_arguments(path_name, find_string, index_file_name, output_file, verbose)

    # Search mode
    if index_file_name != '' and find_string != '':
        try:
            search_with_wildcards(index_file_name, find_string, output_file, verbose)
        except RuntimeError as err:
            print("Erreur pendant la recherche... -v pour visualiser")
            trace(str(err), verbose)
            sys.exit(2)

def check_arguments(path_name, find_string, index_file_name, output_file, verbose):
    """
    Verifies if arguments are correctly used or exit with error
    """
    # Il faut au moins choisir un mode : indexation ou recherche
    if path_name == '' and find_string == '':
        print(__doc__)
        print("Erreur de syntaxe : ni indexation ni recherche demandée")
        sys.exit(2)

    # indexation et recherche incompatibles
    if path_name != '' and find_string != '':
        print(__doc__)
        print("<pathname> ne peut pas être utiliser en même temps que <search>")
        sys.exit(2)

    # indexation a besoin d'un chemin
    if index_file_name != '' and path_name == '' and find_string == '':
        print(__doc__)
        print("<pathname> obligatoire si demande d'indexation")
        sys.exit(2)

    # Recherche demandée sans fichier d'index
    if index_file_name == '':
        print(__doc__)
        print("<indexfilename> obligatoire pour lancer une recherche")
        sys.exit(2)

    # Lancement de l'indexation
    if index_file_name != '' and path_name != '':
        if output_file != '':
            print("Warning : <output> est ignoré en mode indexation")
        try:
            parse_directory(index_file_name, path_name, verbose)
        except RuntimeError as err:
            print("Erreur pendant l'indexation...-v pour visualiser")
            trace(str(err), verbose)
            sys.exit(2)
