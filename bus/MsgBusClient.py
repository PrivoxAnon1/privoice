#!/usr/bin/python
import datetime, json, time, asyncio
from bus.Message import Message, msg_from_json
import threading
from queue import Queue
from websocket import (WebSocketApp,
                       WebSocketConnectionClosedException,
                       WebSocketException, enableTrace)

BARK = False
def process_inbound_messages(inbound_q, msg_handlers, skill_id, sync):
    # this is where you handle bus.on() events. note, you are
    # technically called as a thread unless you set sync to False
    # in either case, you need to be thread safe
    while True:
        while inbound_q.empty():
            time.sleep(0.001)

        msg = inbound_q.get() 

        # see if msg type is a registered event
        if msg_handlers.get( msg['msg_type'], None ) is not None:
            if sync:
                # synchronous behavior
                print("Synchronous Dispatch!")
                threading.Thread(target=msg_handlers[msg['msg_type']], args=(msg,)).start()
            else:
                msg_handlers[msg['msg_type']]( msg )
        else:
            if BARK:
                print("Warning no message handler registered %s" % (msg,))
            pass

class MsgBusClient:
    def __init__(self, client_id, sync=False):
        if sync:
            print("** Warning! Synchronous Dispatch Selected for %s **" % (client_id,))

        self.inbound_q = Queue()
        self.outbound_q = Queue()
        self.msg_handlers = {}
        self.client_id = client_id
        self.client = ''
        self.inbound_thread = threading.Thread(target=process_inbound_messages, args=(self.inbound_q, self.msg_handlers, client_id, sync)).start()
        self.connection_thread = self.run_in_thread()

    def on_error(self, ws, error):
        if BARK:
            print("XXXXXXXXXXXXXXXXX ERROR %s = %s" % (self.client_id, error))
        pass

    def on_close(self, ws, close_status_code, close_msg):
        if BARK:
            print("### WTF? Connection closed !! ### %s" % (self.client_id,))
            print("%s ---> %s" % (close_status_code, close_msg))
            print("### END WTF?")

    def on_open(self, ws):
        #print("### Connection Opened !! ### %s" % (self.client_id,))
        pass

    def connection(self):
        #print("Create client %s" % (self.client_id,))
        self.client = self.create_client()
        self.client.run_forever()

    def create_client(self):
        url = "ws://localhost:4000/%s" % (self.client_id,)
        return WebSocketApp(url, on_message=self.rcv_client_msg, on_error=self.on_error, on_open=self.on_open, on_close=self.on_close)

    def rcv_client_msg(self, wsapp, msg):
        if self.client_id == 'skill_manager':
            if BARK:
                print("[%s]RECV: %s" % (self.client_id, msg))
        self.inbound_q.put( msg_from_json( ( json.loads( msg ) ) ) )

    def run_in_thread(self):
        t = threading.Thread(target=self.connection)
        t.daemon = True
        t.start()
        return t

    def on(self, msg_type, callback):
        self.msg_handlers[msg_type] = callback

    def send(self, msg_type, target, msg):
        #self.outbound_q.put( json.dumps( Message(msg_type, self.client_id, target, msg) ) )
        if self.client_id == 'skill_manager':
            if BARK:
                print("[%s]SENT: %s" % (self.client_id, msg))
        self.client.send( json.dumps( Message(msg_type, self.client_id, target, msg) ) )

    def close(self):
        self.client.close()

