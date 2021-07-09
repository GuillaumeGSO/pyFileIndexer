# pyFileIndexer
This program is : 
- a simple tool that index filenames on a directory and its subdirectories
- a command line search tool that can :
       - display search result and the console
       - export search result in a csv files (with file size associated)


My comments in french for a fresh start
- [x] TODO : everything in english
- [ ] TODO : cleaner code about --output options
- [ ] TODO : code separation between main, interface, index file handling...
- [ ] TODO : add interactive mode if index file or path name not provided ?


## Exemple : 

1 - indexing my entire C drive :
>python FileIndexer.py -index "lecteurC" -path "c:\"

The index file will be generated as "lecteurC.pbz2"

2 - search all log files in my C drive :
>python pyFileIndexer.py -find "*.log" -i "lecteurC"

The <indexfilename> file must be "lecteurC.pbz2"


## Usage : 
 * -h ou --help : displays help
 * -v ou --verbose : displays more information on the standard output

### Indexation mode : 2 mandatories parameters
 * -p ou --path <pathname>: path to index
 * -i ou --index <indexfilename> : start indexing <pathname> et write the index file in <indexfilename>

### search mode : 2 mandatories parameters
* -f ou --find <search>: find all relevant files into <indexfilename> with name or/and wildcards (? or * only) :
       ** *.xls : all Excel files
       ** *202?.log : all .log files like fic2020.log, param2021.log, etc 
* -i ou --index <indexfilename> : mandatory index file name (for indexing or searching)
* -o ou --output <ouputfilename> : output file name with ; separated (optional)
