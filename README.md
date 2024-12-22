# MBBS
MBBS is a simple BBS system for use with Meshtastic. It is designed to be modular and easy to modify or extend without having to modify existing code. Users interact with the BBS using the Meshtastic chat system. Optionally, users can interact via TCP.

# Status
This project is very much incomplete. It has not been extensively tested and certainly contains strange bugs. Contributions and bug reports are welcome.

# Inspiration
This project was inspired in part by the following projects:
- https://github.com/TheCommsChannel/TC2-BBS-mesh
- https://github.com/joshbressers/meshbbs

# Components
## Config
MBBS is configured primarily through `config.toml` in the root directory. 

### Config stanza
Most of the generic configuration options are specified in the `[config]` stanza

```
activate_keyword = "keyword"
```
Keyword to activate the BBS. Users must send this keyword over the BBS listening channel to activate the BBS menu.

```
radio_ip = "192.168.x.x"
```
IP address of Meshtastic radio to communicate over the mesh.

```
radio_channel = 0
```
Channel on the Meshtastic radio that the BBS should communicate on.

```
log_level = "DEBUG"
```
Logging level for MBBS. It currently only logs to stdout.

```
tcp_server_port = 5555
```
TCP Port for BBS to listen on for TCP connections.

```
tcp_server_ip = "127.0.0.1"
```
IP address for BBS to listen on for TCP connections.

```
username_min_length = n
```
Minimum required length for usernames registering to the BBS.

```
username_max_length = n
```
Maximum length for usernames registering to the BBS.

```
guestbook_file = "data/guestbook.txt"
```
Path to guestbook text file for the guestbook context

### Database stanza
```
filename = "user.db"
```
Path to the user database file.


### BBS stanza
```
database = "bbs.db"
```
Path to the BBS database file.

### Messages stanza
This stanza defines default borders for messages coming from the BBS.
```
border_top = "===================="
border_bottom = "===================="
```

### Sessions stanza
```
timeout = 300
```
Define the default user timeout. If a user doesn't send a message in this amount of time, their session is destroyed.

### Menus stanza
All menus are defined in `config.toml` to make it easier to edit them without having to edit code. A `menu` config has four main options:

```
name = "Login"
```
This is the name of the menu. The name is displayed at the top of the menu when the user is in that menu's context.

```
description = "[L]ogin"
```
When this menu appears as a sub-menu option on another menu. This is the string that the user will see as an option.

```
command = "l"
```
This is the command the user must enter to trigger this menu option, if this menu is a sub-menu.

### Menus.options stanza
Each menu defined in the config file can have a series of menu options defined. Each option represents a Context object that the user can choose. Each option can be either a `command` type, or `menu` type.

#### Command type
A `command` type option will instantiate the context object specified within the option itself, if the user chooses this option.

```
    type = "command"
```
`type` defines the type of menu option. Currently this can be either `command` or `menu`. If it is set to `command`, then the option is treated as a standard Context object.

```
    module = "cmd_help"
```
`module` tells the BBS which python module contains the Context object that belongs to this menu option. In this example, the module is named `cmd_help`. Therefore, the BBS will attempt to load the Context object from `contexts/cmd_help.py`.

```
    class = "CmdHelp"
```
`class` specifies the name of the Context object class within the specified module. In this case the class is called `CmdHelp`. This class inherits from the `Context` class defined in `contexts/context.py`.
    
```
    command = "h"
```
`command` is the command that the user must enter to trigger this menu option. It can be any string. If multiple menu options have the same command, only the first one will function.
    
```
    description = "[H]elp"
```
`description` is what the user will see in the menu to tell them what the option is and how to select it. In this case `[H]elp` indicates that it is a "help" command and the user should enter `h` to trigger it. This can be any string and does not directly relate to the `command` option, though it makes sense that they would match up.

```
    role = "admin"
```
A final `role` option can be specified to limit menu options to certain user roles. By default there is a `user` role and an `admin` role. This is just a string in a database so there is no reason other roles can't be defined and used. Currently user roles can only be changed by manually updating the user's record within the `user.db` sqlite database. Default behavior is to create all users with the `user` role. All menu options are available to the `user` role.

#### Menu type
A `menu` type option will generate a menu using the `Menu` class inside `contexts/menu.py`. The first menu defined in `config.toml` acts as the default menu a user sees when they activate the BBS. By default, this is a menu which allows a user to either log in or register an account.

```
    type = "menu"
```
`type` sets the option's type to `menu`.

```
    module = "menu"
```
`module` tells the BBS to load the class from the `contexts/menu.py` module. This class handles generating a menu for the user based on this configuration file.

```
    name = "Games"
```
`name` specifies the name of the menu as defined within this same config file. In this example, the menu is named "Games". There must therefore be another menu defined in the config file with the name, "Games".

## mbbs.py
The main program is launched via `mbbs.py`. It essentially just sets up the listening interfaces (Meshtastic and TCP by default). Then it runs a loop and waits for `CTRL+c` at the command prompt to quit the BBS.

## Interfaces
An interface allows the BBS to communicate over a given connection. Currently there are three interfaces written: `CommInterfaceMeshtasticTCP`, `CommInterfaceMeshtasticSerial` and `CommInterfaceTCP`. All interface objects inherit from the base `CommInterface` class. The Meshtastic TCP interface allows the BBS to communicate with a Meshtastic radio via TCP. The serial interface allows you to communicate with the Meshtastic radio via serial port (USB). The TCP interface allows users to connect to the BBS via TCP instead of using Meshtastic. This can be useful for debugging or if you just want users to also be able to connect via TCP/IP. Bluetooth has yet to be implemented.

There is not currently a Bluetooth interface, though other interfaces can be written to extend functionality. A new interface must be instantiated within `mbbs.py`. All interfaces must accept input from users and format the data as a `dict` with the same fields expected to be in a Meshtastic packet object. Refer to `comm_interface_tcp.py` for an example.

The main loop occurs inside the Interface objects. An interface waits for an incoming packet and then checks to see if it belongs to an established `Session`. If not, it will check to see if the packet contains the configured BBS keyword. If so, it will activate the BBS for this user and create a new session. Processing of incomming packets is then handled within the Session object.

## Sessions
User state is maintained in a `Session` object defined in `utils/user_session.py`. Any incoming packets that belong to a session are sent to the Session object for processing. This is where the more interesting bits of processing packets begins.

The session keeps track of the username, the current user context, the context history, and more. It also contains functions used to send messages to the user via the user's current interface. The interface is transparent to each context. The Session object's `session.send_message()` function can be invoked to send a message to the user.

When a session is first created, the first menu defined inside `config.toml` acts as the default menu a user sees. When a user chooses a menu option, that option is a `Context` object. The Session object keeps track of which context the user is currently working inside and maintains a history so the user can go back to previous contexts.

## Contexts
Contexts represent the current menu/program/etc that the user is interacting with. There is a base `Context` object that all other contexts inherit from. A Context is basically the current "screen" that the user is interacting with.

The `Menu` context object is a special context which will build out a menu based on menus defined in the `config.toml` file.

Other Context objects can have any custom functionality as desired. The easiest way to add functionality to the BBS is to build a custom context object and then include that context in a menu. Context objects should be placed in the `contexts` subdirectory. Some examples of contexts included with MBBS are:

### Back
Include this context as a menu option to give the user a way to go back to the previous menu.

### Echo
The user can submit a string and the BBS will echo it back to them

### Sysinfo
Execute the `uname -a` shell command and send the output to the BBS user.

### Quit
Destroys the user's session and effectively logs them out.

### Tic Tac Toe
A simple tic tac toe game where the computer player randomly chooses a free space.

### Tic Tac Toe MP
A multiplayer Tic Tac Toe game where two users can play against each other. The game keeps track of user wins, losses, and draws in a sqlite database.

### BBS
There are several Contexts used for the BBS functionality, including `BBSMain`, `BBSTopic`, and `BBSPost`.

### Guestbook
Consists of the Guestbook `menu` context defined in `config.toml`, as well as the `CmdGuestbookRead` and `CmdGuestbookSign` Context objects.

## Messages
A Message object contains all the data to be sent to the user as a message. The components will eventually be combined into a single string to be sent to the user via the user's `Session` object. An example message might look like this:

```
Main Menu               <- header
================        <- border_top
[M]essages              <- body
[Q]uit
================        <- border_bottom
Last login: 1/1/2011    <- footer
```

A Message object contains the following components:

### Header
The `header` is text which should be listed in the first line of the message to the user.

### border_top
`border_top` specifies a string used to separate the header from the body. If this is set to `None` it will be ignored.

### Body
The `body` is the main content of the message.

### border_bottom
`border_bottom` specifies a string used to separate the body of the message from the footer text. If this is set to `None` it will be ignored.

### Footer
The `footer` specifies text which should be listed at the end of the message, after the footer. This is often a list of valid commands for a given context, but could be anything.

# Message Pagination
There is a special context object called `MessagePager` that is used to paginate messages that are too long. Meshtastic has a pretty short message size limit, and when you add in BBS info overhead it gets pretty limiting. If a message is too long to be sent in one shot, the MessagePager context will kick in and turn the message into a series of pages. The user can then interact with that context to page through the whole message. When the user exits that context, they will be reverted to their previous context to continue where they left off.