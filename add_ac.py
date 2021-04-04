from pyrogram.raw.functions import messages
from pyrogram.raw.functions.messages import GetDialogFilters
from pyrogram import Client
from redis import Redis

user = Client('admin')
redis = Redis()


with user:
    while True:
        a = redis.get('msg')
        if a:
            user.send_message('@WhileForInt', a.decode('UTF-8'))
            redis.delete('msg')


