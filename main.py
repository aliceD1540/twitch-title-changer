import json
import os, sys
import PySimpleGUI as sg
from twitchAPI.oauth import refresh_access_token
from twitchAPI.types import InvalidTokenException
from twitchAPI import Twitch,AuthScope,UserAuthenticator

def update_config_json(config:dict):
    """
    現時点での設定でconfig.json上書き
    """
    with open('./config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def get_game_list():
    """
    configに記録された一覧の最新版（ソート済み）を取り直す
    """
    game_list = []
    list_temp = sorted(config['Games'], key=lambda x: x['Priority'])
    for game in list_temp:
        game_list.append([game['GameName'],game['GameId'],game['Title'],game['Priority']])
    return game_list

def get_max_priority():
    """
    configに記録された一覧のPriorityの最大値を取得する
    """
    max_priority = 0
    for game in config['Games']:
        if max_priority < game['Priority']:
            max_priority = game['Priority']
    return max_priority

def search_games(title:str):
    """
    ゲームタイトルを検索する
    """
    result = twitch.search_categories(title)
    print(result)
    return result

def change_broadcaster_info(broadcaster_info:dict):
    """
    配信情報を編集する
    """
    res_get_users = twitch.get_users(logins=[broadcaster_info['BroadcasterName']])
    broadcaster_id = res_get_users['data'][0]['id']
    print(broadcaster_id)
    twitch.modify_channel_information(broadcaster_id=broadcaster_id, game_id=broadcaster_info['GameId'], broadcaster_language="ja", title=broadcaster_info['Title'])

    print(twitch.get_channel_information(broadcaster_id=broadcaster_id))

def get_token():
    """
    トークンを取得する
    """
    target_scope = [AuthScope.CHANNEL_MANAGE_BROADCAST]
    if 'Token' not in config.keys():
        # 一旦取得できたtokenは設定ファイルに記録し、設定ファイルに記録されていたらスキップ
        auth = UserAuthenticator(twitch, target_scope, force_verify=False)
        token, refresh_token = auth.authenticate()
        print(token)
        print(refresh_token)
        config['Token'] = token
        config['RefreshToken'] = refresh_token
        update_config_json(config)
    else:
        token = config['Token']
        refresh_token = config['RefreshToken']
    try:
        twitch.set_user_authentication(token, target_scope, refresh_token)
    except InvalidTokenException:
        # トークンが無効だったらリフレッシュトークンで再取得
        token, refresh_token = refresh_access_token(config['RefreshToken'], config['ClientId'], config['SecretId'])
        config['Token'] = token
        config['RefreshToken'] = refresh_token
        update_config_json(config)
        twitch.set_user_authentication(token, target_scope, refresh_token)

# main.pyのあるディレクトリに移動しておく
os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

with open("./config.json", encoding='utf-8') as config_file:
    config = json.load(config_file)

# TODO 一度トークンを取得してしまえばシークレットIDは不要（コメントアウトしてる方でOK）、あとで切り離す
twitch = Twitch(config['ClientId'], config['SecretId'])
# twitch = Twitch(config['ClientId'], authenticate_app=False)

get_token()
