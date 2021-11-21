import nexomiapy, json

env = json.load(open(".env",'r'))

client = nexomiapy.client(env['email'],env['password'])
bot = client.own

print("Signed in as:",bot.name)

print("Active in guilds:")
for guild in bot.guilds:
  print(guild)
  for member in guild.members:
    print(member)

# Here we can assign functions and listening to commands
