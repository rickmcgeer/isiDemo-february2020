"""Socketio implementation of the communication between Jupyter and Lively."""
from json import dumps, loads
import socketio
import datetime
# from lively_client import livelyconst

DEBUG = False

def set_debug(flag):
    DEBUG = flag


class Test:
  """A simple test class."""
  def test_method(self, x: int = 0):
    return x * 2


class Data:
  """The data object required to connect to the server."""
  def __init__(self, action, room, broadcast):
    self.action = action
    self.room = room
    self.broadcast = {"payload" : broadcast}
    self.broadcast["eventType"] = "load"


class Message:
  """The message component that is sent to the server."""
  def __init__(self, sender, pdata, action, n, token):
    self.sender = sender
    self.data = pdata
    self.action = action
    self.n = n
    self.token = token

  def toJSONString(self):
    """Convert and send all attributes to JSON."""
    return dumps(self, default=lambda o: o.__dict__, sort_keys=True)

class Log:
    def __init__(self):
        self.log = []
    
    def add_event(self, event):
        self.log.append((event, datetime.datetime.now().isoformat(timespec="seconds")))
        


class Client:
  def __init__(self, realm: 'str' = 'wss://matt.engagelively.com/',
               path: str = '/lively-socket.io', namespace: str = '/l2l',
               token: str = 'incorrect'):
    self.realm = realm
    self.path = path
    self.namespace = namespace
    self.io = socketio.Client()
    self.token = token
    self.log = Log()

  def connect(self) -> None:
    res = self.io.connect(url=self.realm,
                          socketio_path=self.path,
                          namespaces=[self.namespace],
                          headers={"token": self.token})
    if DEBUG:
        print(self.io.connected)
        print('Client Connected')
    
    self.log.add_event(self.io.connected)
    self.log.add_event('Client Connected')

  def disconnect(self) -> None:
    self.io.disconnect()
    if DEBUG:
        print('Client Disconnected')
    self.log.add_event('Client Disconnected')

  def message_received(self, *args):
    """Callback function notified by server once the message has been received.
    Disconnect the server after the message has been received."""
    if DEBUG:
        print("Message has been received by server.")
    self.log.add_event('Message has been received by server.')
#    self.disconnect()

  def send(self, data, room: str, sender: str = 'lively_client client',
           action: str = '[broadcast] send', n: int = 1) -> None:
    #Create Data object
    # data = "hello from andi to room 3 hurray"  # For testing strings.

    prepared_data = Data('[el-jupyter] message', room, data)

    #Create message object using data object
    message = Message(sender, prepared_data, action, n, self.token).toJSONString()
    if DEBUG:
      print("This is the message that is being sent:\n<<<LivelyMessage>>>{}<<<LivelyMessage>>>".format(message))
    self.log.add_event('Sent message to room ' + room)
    #Emit message
    #self.io.emit('join', {'channel': room});
    self.io.emit(loads(message), namespace=self.namespace, callback=self.message_received)


    


