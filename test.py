from pyrogram import Client
from multiprocessing import Process   
from pyrogram.raw.functions.messages import GetDialogFilters
from redis import Redis

def get_folders(user_id, folders):
    folders_list = {}

    for folder in folders:
        folders_list.update({folder['title'] : []})
        for user in folder['include_peers']:
            folders_list[folder['title']].append(user['user_id'])

    folders_r = []

    for folder in folders_list:
        if user_id in folders_list[folder]:
            folders_r.append(folder)

    return folders_r


    

    

def start(name):
    print('starting')
    app = Client(name)
    redis = Redis


    @app.on_message()
    def my_handler(client, message):

        folders = app.send(GetDialogFilters())

        msg = 'Сообщение: {} | Папка: {}'.format(message['text'], get_folders(message['from_user']['id'], folders))

        redis.set('msg', msg)

    app.run()


proc1 = Process(target=start, args=('admin',))
proc2 = Process(target=start, args=('test',))

proc1.start()
proc2.start()
proc1.join()
proc2.join()




