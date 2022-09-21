import PySimpleGUI as sg
import main
from main import config
import os
import json
import sys

sg.theme('BlueMono')

# main.pyのあるディレクトリに移動しておく
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

def open_sub_window(data):
    """
    配信情報編集用サブウインドウの制御
    """
    sub_layout=[
            [sg.Text('Game Title Search'), sg.InputText(key='search word'), sg.Button('Search')],
            [sg.HorizontalSeparator()],
            [
                sg.Column(
                    [[sg.Text('Game Title')],[sg.Text('Game Id')],[sg.Text('Broadcast Title')]]
                ),
                sg.Column(
                    [[sg.InputText('',disabled=True,key='game title')],[sg.InputText('',disabled=True,key='game id')],[sg.InputText('',key='broadcast title')]]
                )
            ],
            [sg.Column([[sg.Button('Update'), sg.Button('Cancel')]], justification='r')]
        ]
    sub_window = sg.Window('Broadcast Info', sub_layout, finalize=True, resizable=False, modal=True)

    # 初期値の設定（新規の場合は空欄、Priorityは現状の最大値＋1）
    if data == None:
        sub_window['game title'].update('')
        sub_window['game id'].update('')
        sub_window['broadcast title'].update('')
        priority = main.get_max_priority() + 1
    else:
        sub_window['game title'].update(data[0][0])
        sub_window['game id'].update(data[0][1])
        sub_window['broadcast title'].update(data[0][2])
        priority = data[0][3]

    res = None
    while True:
        event, values = sub_window.read()
        if event == 'Search':
            if values['search word'] == '':
                sg.popup_notify('Please input any word.')
                continue
            result = main.search_games(values['search word'])
            sub_window.modal = False
            game_info = open_search_window(result)
            sub_window.modal = True
            if game_info != None:
                sub_window['game title'].update(game_info[0][0])
                sub_window['game id'].update(game_info[0][1])
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
        if event == 'Update':
            res = {
                "GameId": values['game id'],
                "GameName": values['game title'],
                "Title": values['broadcast title'],
                "Priority": priority
            }
            break
    sub_window.close()
    return res

def open_search_window(categories:dict):
    """
    game id検索用サブウインドウの制御
    """
    header = ('Game Title', 'Game Id')
    categorie_list = []
    for categorie in categories['data']:
        categorie_list.append([categorie['name'],categorie['id']])

    search_layout=[
            [sg.Table(categorie_list, headings=header, auto_size_columns=False, col_widths=[30,10], justification='left', key='list')],
            [sg.Column([[sg.Button('OK'), sg.Button('Cancel')]], justification='r')]
        ]
    search_window = sg.Window('Game Title Search', search_layout, finalize=True, resizable=False, modal=True)

    selected_data = None
    while True:
        event, values = search_window.read()
        if event == 'OK':
            selected_data = [categorie_list[row] for row in values['list']]
            if selected_data == []:
                sg.popup('Please select any data.')
                continue
            elif len(selected_data) > 1:
                sg.popup('Please select one data.')
                continue
            break
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
    search_window.close()
    return selected_data

def open_main_window():
    """
    メインウインドウの制御
    """
    game_list = main.get_game_list()
    header = ('Game Title', 'Game Id', 'Title')
    main_layout=[
                [sg.Text('User Name'), sg.InputText()],
                [sg.Table(game_list, headings=header, auto_size_columns=False, col_widths=[30, 10, 70], justification='left', key='list')],
                [sg.Column([[sg.Button('△'),sg.Button('▽'),sg.Button('Create'), sg.Button('Update'), sg.Button('Delete'), sg.Button('Regist to Twitch')]], justification='r')]
            ]
    main_window = sg.Window('Twitch Title Changer', main_layout, finalize=True, resizable=False)

    while True:
        # イベントの読み込み
        event, values = main_window.read()
        if event == 'Create':
            # resを元にgame_listにカラム追加
            res = open_sub_window(None)
            if res != None:
                print(res)
                config['Games'].append(res)
                game_list = main.get_game_list()
                main.update_config_json(config)
                main_window['list'].update(values=game_list)
        if event == 'Update':
            # resを元にgame_listのカラム更新
            selected_data = [game_list[row] for row in values['list']]
            if selected_data == []:
                sg.popup('Please select any data.')
                continue
            elif len(selected_data) > 1:
                sg.popup('Please select one data.')
                continue
            print(selected_data)
            res = open_sub_window(selected_data)
            if res != None:
                print(res)
                print(values['list'][0])
                config['Games'][values['list'][0]] = res
                game_list = main.get_game_list()
                main.update_config_json(config)
                main_window['list'].update(values=game_list)
        if event == 'Delete':
            selected_data = [game_list[row] for row in values['list']]
            if selected_data == []:
                sg.popup('Please select any data.')
                continue
            elif len(selected_data) > 1:
                sg.popup('Please select one data.')
                continue
            result = sg.popup_ok_cancel('Are you ready to delete?', title='Delete Item')
            if result == 'OK':
                del config['Games'][values['list'][0]]
                game_list = main.get_game_list()
                main.update_config_json(config)
                main_window['list'].update(values=game_list)
        if event == 'Regist to Twitch':
            # Twitchの配信情報を更新
            selected_data = [game_list[row] for row in values['list']]
            if selected_data == []:
                sg.popup('Please select any data.')
                continue
            elif len(selected_data) > 1:
                # 複数同時削除は需要があれば考える
                sg.popup('Please select one data.')
                continue
            main.change_broadcaster_info({
                'BroadcasterName': 'libragrimoire',
                'GameId': selected_data[0][1],
                'Title': selected_data[0][2]
            })
            sg.popup_notify('Broadcast Info updated.')
        if event == '△':
            # ひとつ上のアイテムと入れ替え
            selected_data = [game_list[row] for row in values['list']]
            if selected_data == []:
                continue
            if values['list'][0] == 0:
                sg.popup_notify('Can`t change position.')
                continue
            temp_item = config['Games'][values['list'][0]]
            temp_priority_1 = config['Games'][values['list'][0]]['Priority']
            temp_priority_2 = config['Games'][values['list'][0]-1]['Priority']
            config['Games'][values['list'][0]] = config['Games'][values['list'][0]-1]
            config['Games'][values['list'][0]]['Priority'] = temp_priority_1
            config['Games'][values['list'][0]-1] = temp_item
            config['Games'][values['list'][0]-1]['Priority'] = temp_priority_2
            game_list = main.get_game_list()
            main.update_config_json(config)
            main_window['list'].update(values=game_list, select_rows=[values['list'][0]-1])
        if event == '▽':
            # ひとつ下のアイテムと入れ替え
            selected_data = [game_list[row] for row in values['list']]
            if selected_data == []:
                continue
            if values['list'][0] >= len(game_list) - 1:
                continue
            temp_item = config['Games'][values['list'][0]]
            temp_priority_1 = config['Games'][values['list'][0]]['Priority']
            temp_priority_2 = config['Games'][values['list'][0]+1]['Priority']
            config['Games'][values['list'][0]] = config['Games'][values['list'][0]+1]
            config['Games'][values['list'][0]]['Priority'] = temp_priority_1
            config['Games'][values['list'][0]+1] = temp_item
            config['Games'][values['list'][0]+1]['Priority'] = temp_priority_2
            game_list = main.get_game_list()
            main.update_config_json(config)
            main_window['list'].update(values=game_list, select_rows=[values['list'][0]+1])
        # ウィンドウの×ボタンクリックで終了
        if event == sg.WIN_CLOSED:
            break
    # ウィンドウ終了処理
    main_window.close()

open_main_window()