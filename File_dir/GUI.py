import PySimpleGUI as sg
from File_dir.file_parser import findFilesWithName 


def construct_interface():
    lst  = list(findFilesWithName("index", "*.pdf"))
    sg.theme('Dark Red 1')   # Add a little color to your windows
    # All the stuff inside your window. This is the PSG magic code compactor...
    layout = [  
                [sg.InputText(key="-INPUT-", enable_events=True), sg.Text(len(lst), key="-NB-")],
                [sg.Listbox(lst, size=(100, 30), auto_size_text = True, key="-RESULT-")],
                [sg.Exit()]
                ]

    # Create the Window
    window = sg.Window('Py Simple Indexer', layout)
    # Event Loop to process "events"
    while True:             
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event=='-INPUT-':
            #TODO ne pas relire le fichier index à chaque fois : faire juste la recherche
            lst = list(findFilesWithName("index", values['-INPUT-']))
            window['-NB-'].update(len(lst))
            window['-RESULT-'].update(lst)
        elif event == '-RESULT-':
            print('result', values)
        else:
            print(event, values)

    window.close()