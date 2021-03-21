from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

class Tools():


    def __init__(self):
        print('Tools have been loaded')

    def add_session(self):
        
        app = Client('test_one', api_id, api_hash)
        
        app.connect()
        phone_number = input('Phone_num: ')
        code_hash = app.send_code(phone_number).phone_code_hash
        code = input('Conf: ')
        try:         
            app.sign_in(phone_number, code_hash, code)
        except SessionPasswordNeeded:
            passs = input('Pass: ')
            app.check_password(passs)
            
        print('done')
        app.disconnect()
        

tool = Tools()

tool.add_session()