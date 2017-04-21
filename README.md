
# Pygame Tornado Bot

Simple top-down shooter where Hero controlled by bot. User's goal is developing instructions for bot.

On every iteration of gameworld's eventloop Client got JSON with information about Hero's HP, center x and center y, game status and list of all enemies on screen (enemies cordinates, classes, ids), etc, and can to send reply with JSON with instructions what actually Hero need to do. When Hero dies, server return JSON with score and passed game time. Score is passed gameworld eventloop iterations.

Powered by Tornado with implemented pygame event loop. Client sends instructions to server via websockets.

Tested on Fedora 25 x86_64 with Python 3.5.3, Tornado 4.4.2 and Pygame 1.9.2a0. Doesn't work on macOS because creates UI not in main thread.

# Usage

1. Edit start_client.Client.process method for yours proporsals

 * Place yours commands to ```hero_cmds['cmd_lst']``` as dictionaries like ```{'cmd': 'shoot', 'x': enemy_x, 'y': enemy_y}```.
 * Available cmds:
 * ```'cmd' : 'move'```, sends with ```xd``` (x direction) and ```yd``` (y direction), can be 0 - stay, 1 - increase value (for example for x axis ```'xd': 1``` mean moving right)
 * ```'cmd': 'shoot'```, sends with ```x``` and ```y``` - coordinates of shooting target.

Method already contains example instructions: shoot to nearest enemy (see shooting comments inside file) and run away from him :)

2. Start server with
```
./start_server.py
```
3. Start Client
```
./start_client.py
```
and check a result.

# Default parameters
## Hero
Radius = 15, speed = 3, hp = 100, color = white, reloading delay = 5 iterations (after shot next 5 iterations Hero can't to shoot = shoot cmds are ignored)

### Hero's bullets
Radius = 3, speed = 6, color = purple.

Bullet kills enemy with one hit and destroys.

## Enemies
Radius = 10, power = 2 (one collisions hit user to 2 hp). Spawns at least at distance of 5 Hero's radiuses from Hero's center. Enemies always going to Hero's center.

### Easy enemy
Color = green, speed = 1

### Medium enemy
Color = yellow, speed = 2

### Hard enemy
Color = red, speed = 3

# Additional info

Licensed under zlib/libpng license. See LICENSE for details.

Oleg Kozlov (xxblx), 2017
