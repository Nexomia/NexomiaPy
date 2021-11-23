import nexomiapy, json
import sys,os
import curses
import threading
import time

env = json.load(open(".env",'r'))

client = nexomiapy.client(env['email'],env['password'],c=True)
client.prefix=''
x = threading.Thread( target=client.run )
bot = client.own

class page:
    def __init__(self,title=None,sub=None,header=None,messagesource=None):
        self.title = title
        self.sub = sub
        self.header = header
        self.messagesource = messagesource

def draw_menu(stdscr):
    k = 0
    cursor_x = 0
    cursor_y = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()
    stdscr.nodelay(True)

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    path = 'home'
    state= 'None'
    s='None'
    guilds = []
    messages = {}
    help=False
    cur_guild= None
    for guild in bot.guilds:
        messages[guild.channels[0].id] = [guild.channels[0].get_history(token=bot.token)]
        print(guild.channels[0].get_history(token=bot.token))

    # Loop where k is the last character pressed
    while True:
        cur_path = path
        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if k == curses.KEY_DOWN:
            cursor_y = cursor_y + 1
        elif k == curses.KEY_UP:
            cursor_y = cursor_y - 1
        elif k == curses.KEY_RIGHT:
            cursor_x = cursor_x + 1
        elif k == curses.KEY_LEFT:
            cursor_x = cursor_x - 1

        cursor_x = max(0, cursor_x)
        cursor_x = min(width-1, cursor_x)

        cursor_y = max(0, cursor_y)
        cursor_y = min(height-1, cursor_y)

        # Handle our keypresses
        if k == ord(':') or state == 'Command' or state=='ServerPicker' or k == 58:
            # Check if we are already handling a page
            if state == 'ServerPicker':
                # User wants to go to the home page
                if k == ord('h'):
                    path = 'home'
                # Check if its any server
                for i,guild in enumerate(bot.guilds):
                    if k == ord(str(i)):
                        path = f'server/{guild.name}'
                        cur_path = 'rararasputin'
                        cur_guild = guild
                        if cur_guild.unread == True:
                            bot.guilds[i].unread = False
            elif state == 'Input':
                stdscr.move(height-1, 30)
                s = stdscr.getstr(0,0, width-5)
                ctx = nexomiapy.context(cur_guild.channels[0].id,bot.id,'placeholder',client,type='msg')
                ctx.send(s.decode('UTF-8'))
                state='None'
            elif state == 'Help':
                help = True if help == False else False
                state='Hold'
            # We going somewhere? Update state!
            # Exiting? :(
            if k == ord('q'):
                state=''
                quit()
            # Input?
            if k == ord('i') and path != 'home':
                state='Input'
            # Cancel?
            elif k == ord('c'):
                state='Hold'
            elif k == ord('h'):
                state='Help'
            # Go to a page?
            elif k == ord('g'):
                state='ServerPicker'
            elif state == 'Command':
                state='Command'
            elif state == 'None':
                state='Command'
            elif state == 'Hold':
                state='Command'
        # hard quit
        if k == 27:
            quit()

        if help:
            helpbox = stdscr.derwin(int(height/2), int(width/2), 10, 40)
            helpbox.clear()
            helpbox.attron(curses.color_pair(2))
            helpbox.attron(curses.A_BOLD)
            helpbox.addstr(1,1, "Help")
            helpbox.attroff(curses.color_pair(2))
            helpbox.attroff(curses.A_BOLD)
            helpbox.addstr(2,1, "The whole client is really centered around the button `:` as it's used for input, commands,\n moving between guilds/servers and more.\n H -- For help (requires confirmation)\n G -- For the server picker\n C -- Cancel action\n I -- Input (requires confirmation)")
            helpbox.box()
        start_y = int((height // 2) - 2)
        global chatbox
        chatbox = stdscr.subwin(height-3, width-24, 1, 21)

        # Set our title page info
        if path != cur_path or path=='home':
            # Assuming the page changed, clean it!
            if path == 'home':
                cur_page = page(title="Cursed Nex"[:width-1], sub="A CLI client for Nexomia"[:width-1])
            elif 'server' in path:
                # Assume we are handling a server
                cur_page = page(header=cur_guild.name +' | '+ cur_guild.channels[0].name, messagesource=chatbox)

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)
        # Rendering title
        if cur_page.title != None:
            start_x_title = int((width // 2) - (len(cur_page.title) // 2) - len(cur_page.title) % 2)
            stdscr.addstr(start_y, start_x_title, cur_page.title)
        
        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)
        # Print rest of text
        if cur_page.sub != None:
            start_x_subtitle = int((width // 2) - (len(cur_page.sub) // 2) - len(cur_page.sub) % 2)
            stdscr.addstr(start_y + 1, start_x_subtitle, cur_page.sub)
            stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        if cur_page.header != None:
            chatbox.addstr(1, 2, cur_page.header)
            # Handle messages to CLI
            sp = 0
            for i,message in enumerate(messages[cur_guild.channels[0].id]):
                try:
                    if len(message.content) < width-23:
                        chatbox.addstr(3+i+sp,2, message.author.name+' - '+message.content)
                    else:
                        chatbox.addstr(3+i+sp,2, message.author.name)
                        x = [message.content[i:i+(width-22)] for i in range(0, len(message.content), width-22)]
                        sp+=1
                        for o,r in enumerate(x):
                            chatbox.addstr(3+i+o,2, len(message.author.name)*' '+' - '+r)
                        sp+=len(x)
                except:
                    # We probably ran out of space! Scroll!... (or well just clean it ;) )
                    chatbox.erase() 
                    chatbox.refresh()
                if i > 10:
                    break
        #stdscr.addstr(start_y + 5, start_x_keystr, keystr)
        stdscr.move(cursor_y, cursor_x)

        # Handle messages
        @client.command
        def on_message(ctx):
            try:
                if cur_guild != None:
                    if ctx.channel.id == cur_guild.channels[0].id:
                        messages[ctx.channel.id].append(ctx)
                    else:
                        # ctx.send(f"Target: {ctx.channel.id} | Act Target: {cur_guild.channels[0].id}")
                        # Notify user of unread messa
                        for i, guild in enumerate(bot.guilds):
                            if str(ctx.channel.id) in [channel.id for channel in guild.channels]:
                                bot.guilds[i].unread = True
                                messages[ctx.channel.id].append(ctx)
            except Exception as e:
                ctx.send(f"{e}")
                
        chatbox.box()

        #keystr = "Last key pressed: {}".format(k)[:width-1]
        statusbarstr = "Press ':q' to exit | State: {} | {} | Logged in as {} | Loc: /{} | Curr key: {}".format(state,s[:16],bot.name, path,k)

        if k == 0:
            keystr = "No key press detected..."[:width-1]

        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)

        # Rendering some text
        #whstr = "Width: {}, Height: {}".format(width, height)
        #stdscr.addstr(0, 0, whstr, curses.color_pair(1))

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))



        box1 = stdscr.subwin(height-3, 22, 1, 1)
        box1.addstr(1, 1, "Servers:")
        for i,guild in enumerate(bot.guilds):
            if guild.unread == True:
                box1.addstr(i+3, 1, f"• [{i}] {guild.name}")
            else:
                box1.addstr(i+3, 1, f"[{i}] {guild.name}")
        box1.box()


        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()
        time.sleep(0.1)
    #x.join()

def main():
    x.start()
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    main()