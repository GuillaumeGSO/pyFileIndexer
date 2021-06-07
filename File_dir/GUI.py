import PySimpleGUI as sg
from File_dir.file_parser import findFilesInSet
import os


def construct_interface(my_set):
    # FIXME ask the user for an index file
    # TODO use the provided index file in command line (have to add a new interactive mode)
    lst = list()
    sg.theme('Dark Red 1')   # Add a little color to your windows
    # All the stuff inside your window. This is the PSG magic code compactor...

    # TODO make this a little prettier
    layout = [
        [sg.InputText(key="-INPUT-", enable_events=True),
         sg.Text(len(lst), size=(10, 1), key="-NB-")],
        [sg.Listbox(values=lst, size=(140, 30),
                    key="-RESULT-", tooltip="double click to open", bind_return_key=True), ],
        [sg.Exit()]
    ]

    # Create the Window
    window = sg.Window('Py Simple Indexer', layout, finalize=True)
    window['-INPUT-'].update('*')
    update_list(my_set, '*', window)
    # Event Loop to process "events"
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == '-INPUT-':
            if len(values['-INPUT-']) >= 5:
                update_list(my_set, values['-INPUT-'], window)
        elif event == '-RESULT-':
            file_clicked = values['-RESULT-'][0]
            os.startfile(file_clicked)
        else:
            print(event, values)

    window.close()

def update_list(my_set, search,  window):
    lst = list(findFilesInSet(my_set, search))
    window['-NB-'].update(len(lst))
    # TODO make this async to avoid stopping the UI while waiting for long lists
    window['-RESULT-'].update(lst)
