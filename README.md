# P.Y.G.S.G.U.I.

_This is a package that helps you build a GUI very easily when you want to make a game using pygame._

---
## Installation
    pip install pygsgui

## Tutorial
* ### Step 1
  First, load the packages.   
  ```python
  import pygame
  import pygsgui
  from pygsgui.elements import *
  import sys
  ```
* ### Step 2
  Next, write the basic logic of pygame.
  ```python
  import pygame
  import pygsgui
  from pygsgui.elements import *
  import sys
  
  pygame.init() 
  sc = pygame.display.set_mode((800, 800))
  clock = pygame.time.Clock()
  
  while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
  
    sc.fill("#303030")
  
    pygame.display.flip()
    clock.tick(1000)
  ```
* ### Step 3
  Now, create a UI manager.   
  This is the class that manages all UI. You only need to create it once.
  ```python
  import pygame
  import pygsgui
  from pygsgui.elements import *
  import sys
  
  pygame.init() 
  sc = pygame.display.set_mode((800, 800))
  clock = pygame.time.Clock()
  
  # create a UI manager
  ui = pygsgui.UIManager(sc)
  
  while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
  
    sc.fill("#303030")
  
    pygame.display.flip()
    clock.tick(1000)
  ```
* ### Step 4
  Next, let's create a button.
  ```python
  import pygame
  import pygsgui
  from pygsgui.elements import *
  import sys
  
  pygame.init() 
  sc = pygame.display.set_mode((800, 800))
  clock = pygame.time.Clock()
  
  ui = pygsgui.UIManager(sc)
  
  # create a Button
  btn = Button(350, 375, 100, 50, ui, text="Button", text_size=20)
  
  while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
  
    sc.fill("#303030")
  
    pygame.display.flip()
    clock.tick(1000)
  ```
* ### Step 5
  Finally, update the UI manager and draw the UI.
  ```python
  import pygame
  import pygsgui
  from pygsgui.elements import *
  import sys
  
  pygame.init() 
  sc = pygame.display.set_mode((800, 800))
  clock = pygame.time.Clock()
  
  ui = pygsgui.UIManager(sc)
  
  btn = Button(350, 375, 100, 50, ui, text="Button", text_size=20)
  
  while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
  
    # update UI manager
    ui.update()
  
    sc.fill("#303030")
  
    # draw UI
    ui.render()
  
    pygame.display.flip()
    clock.tick(1000)
  ```
* ### Result
![result image](images\tutorial.png)