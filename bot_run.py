from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded, PhoneNumberInvalid, PhoneCodeInvalid, PasswordHashInvalid
from pyrogram.types.messages_and_media import message
from multiprocessing import Process
from config import Config
from redis import Redis
from time import sleep
import asyncio

config = Config()
bot = Client('noti_bot', bot_token='1708936291:AAFnMkJN2R1-7Mazl-tptY8cJsbEpIWJ38w')


class StateManager(Client):
    state = None
    one = None

    def __init__(self, config):
        print('State_manager started')
        self.api_id = config.api_id
        self.api_hash = config.api_hash
        pass

    def start_session(self, phone_number):
        try:
            self.app = Client('test_second', self.api_id, self.api_hash)
            self.app.connect()
            self.phone = phone_number
            self.code_hash = self.app.send_code(self.phone).phone_code_hash

            return True
        except PhoneNumberInvalid:
            return False

    def enter_code(self, code):
        print('Waiting for code')
        try:
            self.app.sign_in(self.phone, self.code_hash, code)
            self.app.disconnect()
            return "Fine"
        except SessionPasswordNeeded:
            return "SessionPasswordNeeded"
        except PhoneCodeInvalid:
            return "PhoneCodeInvalid"

    def enter_2fa(self, tfa):
        self.app.check_password(tfa)
        self.app.disconnect()

    def make_state(self, state):
        self.state = state

    def make_one(self, state):
        self.one = state

state_m = StateManager(config)

def msg_agent():
    bot = Client('msg_agent', bot_token='1708936291:AAFnMkJN2R1-7Mazl-tptY8cJsbEpIWJ38w')
    redis = Redis()

    with bot:
        while True:
            msg = redis.hgetall('msg')
            if msg:
                print(msg)
                bot.send_message('@{}'.format(msg[b'id'].decode('UTF-8')), msg[b'text'].decode('UTF-8'))
                redis.delete('msg')

            sleep(0.1)


def handlers():
    redis = Redis()

    @bot.on_message(filters.command('start'), group=3)
    def start(client, msg):
        print('start')
        redis.hmset('msg', {"id": "WhileForInt", "text": "Введите номер"})
        state_m.make_state('wait_for_phone')


    @bot.on_message(~filters.me, group=2)
    def wait_code(client, msg):
        if state_m.state == 'wait_for_phone':
            print('wait_code')
            phone_number = msg.text
            print('number {}'.format(phone_number))

            if state_m.start_session(phone_number):
                redis.hmset('msg', {"id": "WhileForInt", "text": "Номер принят"})
                sleep(0.5)
                redis.hmset('msg', {"id": "WhileForInt", "text": "Введите код"})
                state_m.make_state('wait_for_code')
            else:
                redis.hmset('msg', {"id": "WhileForInt", "text": "Номер не верен! Проверьте корректность номера"})
                sleep(0.5)


    @bot.on_message(~filters.me, group=1)
    def wait_2fa(client, msg):
        if state_m.state == 'wait_for_code':
            print('wait_2fa')
            code = msg.text

            code_return = state_m.enter_code(code)

            if code_return == "Fine":
                redis.hmset('msg', {"id": "WhileForInt", "text": "Код принят"})
                sleep(0.5)
                redis.hmset('msg', {"id": "WhileForInt", "text": "Аккаунт добавлен"})

            elif code_return == "SessionPasswordNeeded":
                state_m.make_state('wait_for_2fa')
                redis.hmset('msg', {"id": "WhileForInt", "text": "Код принят"})
                sleep(0.5)
                redis.hmset('msg', {"id": "WhileForInt", "text": "Введите 2fa"})

            elif code_return == "PhoneCodeInvalid":
                redis.hmset('msg', {"id": "WhileForInt", "text": "Код не верен. Введите еще раз"})
                sleep(0.5)


    @bot.on_message(~filters.me, group=0)
    def final(client, msg):
        if state_m.state == 'wait_for_2fa':
            print('final')
            tfa = msg.text

            state_m.enter_2fa(tfa)
            redis.hmset('msg', {"id": "WhileForInt", "text": "Аккаунт добавлен"})

    state_m.make_one(False)

    bot.run()



print('Pyro started')
