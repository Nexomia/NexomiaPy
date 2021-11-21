import os
import nexomiapy

client = nexomiapy.client(os.environ['email'],os.environ['password'])
bot = client.own

print("Signed in as:",bot.name)

print("Active in guilds:")
for guild in bot.guilds:
  print(guild)

# Here we can assign functions and listening to commands
