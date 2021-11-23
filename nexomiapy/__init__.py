import requests, nexomiapy.debugger
import websocket, _thread, time, json


req = {
  'GET':requests.get,
  'POST':requests.post
}

class context:
  def __init__(self,cid,uid,content,client,type='msg') -> None:
      '''
      cid    => channel id,
      uid    => user id,
      client => client (must not be None!)
      '''
      if client == None:
        raise Exception("Failed! Client must not be None!")
        exit()
      self.channel = channel(cid)
      self.author = user(id=uid,client=client)
      self.client = client
      self.content = content
      self.type = type
  
  def send(self,msg=''):
    # http://nexo.fun/api/channels/{cid}/messages
    if self.client.type == 'client':
      data = {"content": str(msg), "forwarded_messages": [], "attachments": []}
    else:
      data = {"content": str(msg)+' ⁽ᵇᵒᵗ⁾', "forwarded_messages": [], "attachments": []}
    r = req["POST"](client._api+f"channels/{self.channel.id}/messages",  headers={'Authorization': self.client.token},data=data)
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      print('returned:',r.json())
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200")

class client:
  # Our API location
  _api = "http://nexo.fun/api/"
  
  def __init__(self,email,password,d=False,c=False):
    self._e = email
    self._p = password
    self.prefix = '$'
    self.commands = {}
    self.events = {} 
    # Init the actual client
    self._tokens = self._get_token()
    # Ok now that we have the tokens, lets get user info
    print('Got tokens...')
    self.own = user(token=self._tokens['access_token'])
    self.token = self.own.token
    print('Profile connected...')
    if not c:
      self.ws = websocket.WebSocketApp("ws://ws.nexo.fun:7081?token="+self.own.token,
      on_open=client.on_open,
      on_message=self.on_message,
      on_error=client.on_error,
      on_close=client.on_close)
      self.type = 'bot'
    else:
      self.type = 'client'
      self.ws = websocket.WebSocketApp("ws://ws.nexo.fun:7081?token="+self.own.token,
      on_open=client.on_open,
      on_message=self.on_message,
      on_error=client.on_error,
      on_close=client.on_close)

  def run(self):
    self.ws.run_forever()

  # Handle commands here!
  def command(self,func):
    cmd = {
      'args':func.__code__.co_varnames,
      'code':func
    }
    self.commands[func.__name__] = cmd
  
  def handleEvent(self,func):
    cmd = {
      'args':func.__code__.co_varnames,
      'code':func
    }
    self.events['on_message'] = cmd

  # Web socket
  def on_message(self, ws, message):
    message = json.loads(message)
    print(message)
    if 'on_message' in self.commands:
      if message['event'] == 'message.created':
        ctx = context(message['data']['channel_id'],message['data']['author'],message['data']['content'].strip(),self,type='msg')
        self.commands['on_message']['code'](ctx)
    if message['event'] == 'message.created':
      if message['data']['content'][0] == self.prefix:
        cmd = message['data']['content'].strip().split(' ')[0].replace(self.prefix,'')
        if cmd in self.commands:
          print('Got a command!')
          ctx = context(message['data']['channel_id'],message['data']['author'],message['data']['content'].strip(),self)
          self.commands[cmd]['code'](ctx)
  
  def on_message_client(self,ws,message):
    message = json.loads(message)
    print(message)
    self.events['on_message']['code'](message)


  def on_error(ws, error):
      print('Error:',error)

  def on_close(ws, close_status_code, close_msg):
      print("### closed ###",close_status_code, close_msg)

  def on_open(ws):
      print('Connected!')
  
  def kill(self):
      quit()


  # User stuff below

  def _get_token(self) -> dict:
    r = req["POST"](client._api+"auth/login", data={'login':self._e,'password':self._p})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      return r.json()
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200")

class channel:
  def __init__(self,id,info=None,token=None):
    
    self.id =            id
    self.name =          None
    
    if info:
      self.name =        info['name']
      self.pinned =      info['pinned_messages_ids']

      # Permission overwrites can be blank, if thats the case it follows the general roles
      self.perms =       info['permission_overwrites']
    
    if token: 
      self.token =       token

  def __repr__(self) -> str:
    if self.name != None:
      return f"[{self.name}] -> {self.id}"
    else:
      return f"[Uninitialized Channel] -> {self.id}"

  def get_history(self,count=10,offset=0,token='',cl=None) -> dict:
    '''
    Gets the messages with given count, offset and own id.
    '''
    if token:
      r = req["GET"](client._api+f"channels/{self.id}/messages?offset={offset}&count={count}", headers={'Authorization': token})
    else:
      r = req["GET"](client._api+f"channels/{self.id}/messages?offset={offset}&count={count}", headers={'Authorization': self.token})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      msgs = []
      for msg in r.json():
        msgs.append( context(msg['channel_id'],msg['author'],msg['content'],cl) )
      return msgs
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200")



class guild:
  _api = "http://nexo.fun/api/"
  def __init__(self,id,client):
    # http://nexo.fun/api/guilds/56394684022573056?

    self.id =         id
    rawr =            req["GET"](guild._api+"guilds/"+str(self.id)+'?', headers={'Authorization': client.token}).json()
    self.name =       rawr['name']
    self.owner =      rawr['owner_id']
    self.client =     client
    self.members =    self._get_members( rawr['members'] )
    self.channels =   self._get_channels( rawr['channels'] )
    # Client only!
    self.unread =     False

  def __repr__(self):
    return self.name + ' -> ' + str(self.id)
  
  def _get_channels(self, channels):
    chans = []
    for chan in channels:
      chans.append( channel( chan['id'], info=chan ) )
    return chans

  def _get_members(self, members) -> dict:
    """
    Allows the client to request members of a specified guild.
    """
    mems = []
    for mem in members:
      mems.append( user( mem['id'], server_perms=mem['permissions'], client=self.client ) )
    return mems


class user:
  def __init__(self,id=0,token=None,server_perms=None,client=None):

    # If we have a token, we have ownership of the account!
    if token:
      self.token =        token
      self.all =          self._get_all(token)
      self.id =           self.all['id']
      self.name =         self.all['username']
      self.disc =         self.all['discriminator']
      self.avatar =       self.all['avatar']
      self.status =       self.all['status']
      self.description =  self.all['description']
      self.emoji =        self.all['emoji_packs']
      self.guilds =       self.get_guilds()
    elif id:
      # If we dont get a token, assume we are requesting general info
      self.id = id
      inf = self._get_user(id,client.token)
      self.id =          inf['id']
      self.name =        inf['username']
      self.disc =        inf['discriminator']
      self.avatar =      inf['avatar']
      self.status =      inf['status']
      self.description = inf['description']
    # For servers )))
    if server_perms:
      self.permissions = server_perms
  
  def __repr__(self) -> str:
    return f"({self.name}#{self.disc}) -> {self.id} || {self.status}"
    
  def _get_all(self,token) -> dict:
    r = req["GET"](client._api+"users/@me", headers={'Authorization': token})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      return r.json()
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200 when trying to get user data")
    
  def _get_user(self,id,token) -> dict:
    r = req["GET"](client._api+f"users/{id}", headers={'Authorization': token})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      return r.json()
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200 when trying to get user data")

  
  def get_guilds(self) -> guild:
    # http://nexo.fun/api/users/@me/guilds?
    r = req["GET"](client._api+"users/@me/guilds?", headers={'Authorization': self.token})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      # Process our guilds
      guilds = []
      for g in r.json():
        guilds.append(guild(g['id'],self))
      return guilds
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200 when trying to get user data")

