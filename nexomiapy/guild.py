class guild:
  
  def __init__(self,id,name,owner):
    self.id = id
    self.name = name
    self.owner = owner

  def __repr__(self):
    return self.name + ' -> ' + str(self.id)