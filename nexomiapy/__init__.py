import requests, nexomiapy.debugger

req = {
  'GET':requests.get,
  'POST':requests.post
}

class client:
  # Our API location
  _api = "http://nexo.fun/api/"
  
  def __init__(self,email,password,d=False):
    self._e = email
    self._p = password
    # Init the actual client
    self._tokens = self._get_token()
    # Ok now that we have the tokens, lets get user info
    self.own = user(token=self._tokens['access_token'])


  def _get_token(self) -> dict:
    r = req["POST"](client._api+"auth/login", data={'login':self._e,'password':self._p})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      return r.json()
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200")


class guild:
  _api = "http://nexo.fun/api/"
  def __init__(self,id,name,owner,client):
    self.id = id
    self.name = name
    self.owner = owner
    self.client = client
    self.members = self._get_memebers()

  def __repr__(self):
    return self.name + ' -> ' + str(self.id)

  def _get_memebers(self) -> dict:
    #http://nexo.fun/api/guilds/59375356258066432/members?
    r = req["GET"](guild._api+"guilds/"+str(self.id)+'/members?', headers={'Authorization': self.client.token})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      # Process users
      users = []
      for u in r.json():
        users.append(user(u['id'], server_info=u))
      return users
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200")

  def _get_channels(self) -> dict:
    r = req["POST"](guild._api+"auth/login", data={'login':self._e,'password':self._p})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      return r.json()
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200")

class user:
  def __init__(self,id=0,token=None,server_info=None):

    # If we have a token, we have ownership of the account!
    if token:
      self.token = token
      self.all = self._get_all(token)
      self.id = self.all['id']
      self.name = self.all['username']
      self.disc = self.all['discriminator']
      self.avatar = self.all['avatar']
      self.status = self.all['status']
      self.description = self.all['description']
      self.emoji = self.all['emoji_packs']
      self.guilds = self.get_guilds()
    elif id:
      # If we dont get a token, assume we are requesting general info
      self.id = id
    # For servers )))
    if server_info:
      self.permissions = server_info['permissions']
      self.name = server_info['user']['username']
      self.disc = server_info['user']['discriminator']
      self.avatar = server_info['user']['avatar']
      self.status = server_info['user']['status']
  
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
  
  def get_guilds(self) -> guild:
    # http://nexo.fun/api/users/@me/guilds?
    r = req["GET"](client._api+"users/@me/guilds?", headers={'Authorization': self.token})
    # Check r status
    if r.status_code == 200 or r.status_code == 201:
      # All good :)
      # Process our guilds
      guilds = []
      for g in r.json():
        guilds.append(guild(g['id'],g['name'],g['owner_id'],self))
      return guilds
    else:
      nexomiapy.debugger.p(f"Got {r.status_code} which is not 200 when trying to get user data")

