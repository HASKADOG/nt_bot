from bot_run import handlers, msg_agent
from multiprocessing import Process

msg_agent = Process(target=msg_agent, args=())
handlers = Process(target=handlers, args=())
handlers.start()
msg_agent.start()
handlers.join()
msg_agent.join()
