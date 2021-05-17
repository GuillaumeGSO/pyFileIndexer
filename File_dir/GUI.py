import PySimpleGUI as sg
from File_dir.file_parser import findFilesInSet


def construct_interface(my_set):
    #FIXME ask the user for an index file
    #TODO use the provided index file in command line (have to add a new interactive mode)
    lst  = list()
    sg.theme('Dark Red 1')   # Add a little color to your windows
    # All the stuff inside your window. This is the PSG magic code compactor...
    
    #TODO make this a little prettier
    layout = [  
                [sg.InputText(key="-INPUT-", enable_events=True), sg.Text(len(lst), size=(10, 1), key="-NB-")],
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
            lst = list(findFilesInSet(my_set, values['-INPUT-']))
            window['-NB-'].update(len(lst))
            #TODO make this async to avoid stopping the UI while waiting for long lists
            window['-RESULT-'].update(lst)
        elif event == '-RESULT-':
            print('result', values)
        else:
            print(event, values)

    window.close()