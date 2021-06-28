import PySimpleGUI as sg
import asyncio
import random
import sys
import os
from File_dir.file_parser import findFilesInSet
import bz2
import pickle

__INTERRUPT__ = False
def get_interrupt():
    return  __INTERRUPT__
def set_interrupt(bool):
    __INTERRUPT__ = bool

def read_index_file(my_index_file):
    data = bz2.BZ2File(my_index_file + '.pbz2', 'rb')
    myset = pickle.load(data)
    return myset


lst = []
layout = [
    [sg.InputText(key="-INPUT-", enable_events=True),
     sg.Text(len(lst), size=(10, 1), key="-NB-")],
    [sg.Listbox(values=lst, size=(140, 30),
                key="-RESULT-", tooltip="double click to open", bind_return_key=True), ],
    [sg.Text(size=(10, 1), key='-TEMP-')],
    [sg.Exit()]
]
window = sg.Window('Py Simple Indexer', layout, finalize=True)
print("Début Lecture index file done")
my_set = read_index_file("index")
print("Fin Lecture index file done")


async def background():
    search = ''
    while True:
        tirage = random.randint(2, 20000000000)
        print(tirage)
        window['-TEMP-'].update(tirage)
        if window['-INPUT-'].get() != search:
            search = window['-INPUT-'].get()
            print(search)
            for r in findFilesInSet(my_set, search):
                if get_interrupt():
                    set_interrupt(False)
                    break
                lst = window['-RESULT-'].get_list_values()
                lst.append(r)
                window['-RESULT-'].update(lst)
                window['-NB-'].update(len(lst))
                await asyncio.sleep(0.001)

        await asyncio.sleep(0.001)


async def ui():
    last_search = ''
    # Event Loop to process "events"
    while True:
        event, values = window.read(timeout=1)
        if event in (sg.WIN_CLOSED, 'Exit'):
            sys.exit()
        elif event == '-INPUT-':
            if last_search != values['-INPUT-']:
                window['-RESULT-'].update([])
                last_search = values['-INPUT-']
                set_interrupt(True)
        elif event == '-RESULT-':
            file_clicked = values['-RESULT-'][0]
            os.startfile(file_clicked)
        elif event == '__TIMEOUT__':
            pass
        else:
            print(event, values)
        await asyncio.sleep(0)


async def wait_list():
    await asyncio.wait([background(), ui()])


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wait_list())
    loop.close()
