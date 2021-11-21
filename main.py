import nexomiapy, json

env = json.load(open(".env",'r'))

client = nexomiapy.client(env['email'],env['password'])
bot = client.own

print("Signed in as:",bot.name)

# Here we create commands!

# Simple help command with nothing new
@client.command
def help(ctx):
  ctx.send(msg='# Help\nadd - adds two numbers\nrawr - rawrs??')

@client.command
def add(ctx):
  rawr = ctx.content.replace('add','').replace(client.prefix,'').strip().split(' ')
  try:
    var = int(rawr[0]) + int(rawr[1])
  except Exception as e:
    ctx.send(msg=str(e))
  ctx.send(msg=str(var))

@client.command
def rawr(ctx):
  ctx.send(msg='<e:60032354567927808>')

client.run()