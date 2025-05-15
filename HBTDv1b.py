from machine import Pin, SoftI2C, UART
import neopixel
import time
import random
import math
import sys
import ssd1306
import utime
import json
import uasyncio

################################## Start: Button assignments
b_player_left = Pin(3, Pin.IN, Pin.PULL_UP)
b_player_right = Pin(4, Pin.IN, Pin.PULL_UP)
b_rolldice = Pin(5, Pin.IN, Pin.PULL_UP)
b_dark_right = Pin(8, Pin.IN, Pin.PULL_UP)
b_dark_left = Pin(10, Pin.IN, Pin.PULL_UP)
b_move_world = Pin(20, Pin.IN, Pin.PULL_UP)


################################## Start: OLED Setup
#OLED Pin assignment
i2c = SoftI2C(scl=Pin(7), sda=Pin(6))  #Physical pin on ESP32
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

#Function to handle multi-line text display, wrap text
def display_print(*args, sep=' ', end='\n', max_width=16):
    """Formats and word-wraps text, then sends each line to display_lines()."""
    # Properly format the message while keeping spaces between arguments
    message = sep.join(str(arg) for arg in args) + end  
    def word_wrap(text, width):
        """Splits text into lines that fit within the given width while preserving spaces correctly."""
        words = text.split(' ')  # Preserve spaces between words
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) <= width:
                if current_line:  
                    current_line += " "  # Add space between words
                current_line += word
            else:
                lines.append(current_line)  # Save the current line
                current_line = word  # Start a new line with the next word

        if current_line:  # Add the last line
            lines.append(current_line)
        return lines
    wrapped_lines = word_wrap(message.strip(), max_width)
    for line in wrapped_lines:
        display_lines(line)  # Send each wrapped line separately

# Internal buffer for multi-line handling
buffer = []
line_height = 10
max_lines = oled_height // line_height

#Scroll text on display
def display_lines(message):
    global buffer
    lines = message.split('\n')
    
    for line in lines:
        if line.strip():
            buffer.append(line)
        if len(buffer) > max_lines:
            buffer.pop(0)  # Scroll up when buffer exceeds max_lines
            
    oled.fill(0)  # Clear the display
    for idx, line in enumerate(buffer):
        oled.text(line, 0, idx * line_height)
    oled.show()
################################## End: OLED Setup


################################## Start: Neopixel assignments
pin = Pin(2, Pin.OUT)   ##Physical pin on ESP32
np = neopixel.NeoPixel(pin, 16)   #Create NeoPixel driver: GPIOx, 16 pixels
np[0] = (3, 0, 3) #Set the first pixel to Purple
np.write() # write data to all pixels
#dread_tile = [0,4,9] ################################## Move this
#dark_tile = [2,5,7,11,13] ################################## Move this

################################# Global Constants
filename = "HBTDSave.txt"
start_player = 16
start_darkness = 0
start_topass = 7
start_world = 1
world = 1 ################################# Temporary placement. Removing after defining worlds

def loadsave():
    with open(filename) as file:
        data = json.load(file)

    player = data["player"]
    darkness = data["darkness"]
    topass = data["topass"]
    world = data["world"]

    return player, darkness, topass, world
    
def savegame(player, darkness, topass):  
    with open(filename,"r+") as file:
        data = json.load(file)
        savelist = {"player": str(player), "darkness": str(darkness), "topass": str(topass), "world": str(world)}

    with open(filename,"w") as file:
        file.write(json.dumps(savelist))

def resetgame():
    with open(filename,"r+") as file:
        data = json.load(file)
        resetlist = {"player": str(start_player), "darkness": str(start_darkness), "topass": str(start_topass), "world": str(start_world)}
        
    with open(filename,"w") as file:
        file.write(json.dumps(resetlist))

#Set the initial values and then move to the main program
def initialize():
    playerdepth, darkdepth, topass, world = loadsave() #Retrieve saved Adventure data
    playerdepth = int(playerdepth)
    darkdepth = int(darkdepth)
    topass = int(topass)
    world = int(world)
    
    ledtrack(playerdepth, 0,darkdepth, 0) # Set NeoPixel
    
    display_print("Hold Back the Darkness")
    display_print("World:",worlds(world), "Heroes:", playerdepth,"\nDarkness:", darkdepth,"     ","\nTo Pass:", topass, end="")
    display_print("================")
    
    main(playerdepth,darkdepth,topass,world)

def main(playerdepth,darkdepth,topass,world):
    while True:
        playerdepth, darkdepth,topass = manualmove(playerdepth,darkdepth,topass,world)
        display_print("================")

#Track and initialize LED usage
def ledtrack(playerdepth, playermove,darkdepth,darkmove):
    playerdepth = playerdepth + playermove
    darkdepth = darkdepth + darkmove
    darkspecial = "Waiting"
    
    if playermove != 0: #check for hero movement
        if playerdepth <= 0:
            playerdepth = 0
            display_print("The Heroes have reached the end of the mines")
        elif playerdepth >= 16:
            playerdepth = 16
            display_print("The Heroes are at the mine entrance.")
        else:
            display_print("Heroes move forward to #",playerdepth)
    else: #darkness movement
        if darkdepth >= 16:
            darkdepth = 16
            display_print("The Darkness has escaped the mine!")
            gameover()
        elif darkdepth <= 0:
            darkdepth = 0
            display_print("The Darkness is in hiding.")
        else:
            display_print("Darkness moves forward to #",darkdepth)
            
    #Reset the NeoPixels
    for i in range(1,16):
        np[i] = (0,0,0)
        np.write()
        
    #Show the progress of the Heroes
    for i in range(15,playerdepth - 1, -1):
        np[i] = (0,0,5)
        np.write()
        
    #Show the progress of the Darkness
    if darkdepth in [15,11,6]:
        darkspecial = "Growing Dread"
        np[darkdepth] = (0,5,0)        
    elif darkdepth in [13,10,8,4,2]:
        darkspecial = "Darkness"
        #lightshow(6,darkspecial)
        np[darkdepth] = (5,0,0)
    elif darkdepth > 0:
        darkspecial = "Standard Space"
        np[darkdepth] = (5,5,0)
    np.write()
 

    #Track the player location and the "To Pass" requirement.
    if playerdepth <= 16 and playerdepth >=11:
        topass = 7
    elif playerdepth <= 10 and playerdepth >=6:
        topass = 8
    else:
        topass = 9

    savegame(playerdepth, darkdepth, topass)

    return playerdepth, darkdepth, darkspecial, topass


def manualmove(playerdepth,darkdepth,topass,world):
    button_player_right = False #Initial button state
    button_player_left = False #Initial button state
    button_dark_right = False #Initial button state
    button_dark_left = False #Initial button state
    button_pressed_roll = False #Initial button state
    button_move_world = False #Initial button state


    while True:
        #Move player right
        if b_player_right.value() == 0 and not button_player_right:  # Detect the falling edge (press event)
            button_player_right = True  # Mark that the button press has been registered
            playerdepth, darkdepth, darkspecial, topass = ledtrack(playerdepth, -1,darkdepth,0)
            time.sleep(0.5)  # Debounce delay to prevent multiple triggers
        elif b_player_right.value() == 1:  # Reset when button is released
            button_player_right = False

        #Move player left
        if b_player_left.value() == 0 and not button_player_left: #and playerdepth < 15:  # Detect the falling edge (press event)
            button_player_left = True  # Mark that the button press has been registered
            playerdepth, darkdepth, darkspecial, topass = ledtrack(playerdepth, 1,darkdepth,0)
            time.sleep(0.5)  # Debounce delay to prevent multiple triggers
        elif b_player_left.value() == 1:  # Reset when button is released
            button_player_left = False


        #Move dark left
        if b_dark_left.value() == 0 and not button_dark_left: #and playerdepth < 15:  # Detect the falling edge (press event)
            button_dark_left = True  # Mark that the button press has been registered
            playerdepth, darkdepth, darkspecial, topass = ledtrack(playerdepth,0,darkdepth,1)
            time.sleep(0.5)  # Debounce delay to prevent multiple triggers
        elif b_dark_left.value() == 1:  # Reset when button is released
            button_dark_left = False

        #Move dark right
        if b_dark_right.value() == 0 and not button_dark_right: #and playerdepth < 15:  # Detect the falling edge (press event)
            button_dark_right = True  # Mark that the button press has been registered
            playerdepth, darkdepth, darkspecial, topass = ledtrack(playerdepth,0,darkdepth,-1)
            time.sleep(0.5)  # Debounce delay to prevent multiple triggers
        elif b_dark_right.value() == 1:  # Reset when button is released
            button_dark_right = False
            
        #Move world
        if b_move_world.value() == 0 and not button_move_world: #and playerdepth < 15:  # Detect the falling edge (press event)
            button_move_world = True  # Mark that the button press has been registered
            #world_old: 1
            world += 1
            if world > 3:
                world = 1
            display_print("================")
            display_print("Moving to", worlds(world))
            time.sleep(0.5)  # Debounce delay to prevent multiple triggers
        elif b_move_world.value() == 1:  # Reset when button is released
            button_move_world = False

        #Roll dice
        if b_rolldice.value() == 0 and not button_pressed_roll:
            button_pressed_roll = True
            display_print("Roll dice")
            roll_1, roll_2, roll, double = rolldice()
            display_print("R1:",roll_1,"R2:",roll_2,"R:","Dub:",double)
            darkdepth = result(playerdepth, darkdepth, topass, roll_1, roll_2, roll, double, world)
            time.sleep(0.5)  # Debounce delay to prevent multiple triggers
        elif b_rolldice.value() == 1:  # Reset when button is released
            button_pressed_roll = False
            
        #Reset Adventure
        if b_dark_right.value() == 0: # and not button_dark_right:
            resetcountdown = 0
            while b_dark_right.value() == 0:
                resetcountdown += 1
                time.sleep(0.5)
                if resetcountdown == 10:
                    button_pressed_roll = True
                    display_print("Adventure Reset \n Please wait")
                    time.sleep(5)
                    resetgame()
                    time.sleep(0.5)
                    initialize()
                    time.sleep(0.5)
    
            
            

        time.sleep(0.05)  # Debounce delay

def rolldice():
    roll_1 = random.randint(1,6)
    roll_2 = random.randint(1,6)
    roll = roll_1 + roll_2

    if roll_1 == roll_2:
        double = True
    else:
        double = False

    return roll_1, roll_2, roll, double

#Get the penality for doubles.
def doubles(roll_1,world):
    ######################################################################Will need to incorporate world type
    if world == 1:    #Mines
        doublelist = [
            "Ambush Attack!",
            "Dark Dread",
            "Creeping Darkness",
            "Falling Rubble",
            "Terrifying Shriek",
            "Stubborn Resolve"
            ]
    if world == 2:    #Targa Plateau
        doublelist = [
            "Ambush Attack!",
            "Dark Dread",
            "Creeping Darkness",
            "Blizzard",
            "Echoes of Death",
            "Treasures of the Past"
            ]
    if world == 3:    #Swamps of Jargono   
        doublelist = [
            "Ambush Attack!",
            "Dark Dread",
            "Creeping Darkness",
            "Volley of Arrows",
            "Tribal Drums",
            "Fountain of Life"
            ]

    return doublelist[roll_1 - 1]

def result(playerdepth, darkdepth, topass,roll_1,roll_2, roll, double, world):
    display_print("Tile:",playerdepth,"Pass:",topass) #Show the player's depth and To Pass
    display_print("Darkness:",darkdepth) #Show the darkness' depth
    display_print("Roll:",roll_1, "+", roll_2, "=", roll) #Show the roll and total


    #Determine the results of the roll.
    if double == True: #Penalty for doubles
        display_print("Double", str(roll_1) + "'s:")
        display_print("    " + doubles(roll_1, 1)) ###################################################################### Replace "1" with World Number variable
    elif roll < topass: #Roll failure
        playerdepth, darkdepth, darkspecial, topass = ledtrack(playerdepth,0,darkdepth,1) #Move the darkness marker
        #display_print("Failure!")
        display_print("Darkness moves to space #" + str(darkdepth))
        if darkspecial != "Standard Space":
            #display_print("Draw a", darkspecial, "card!")
            display_print(darkspecial + "!")
    else:
        display_print("Success! The darkness has been held in place!")
    return darkdepth

def worlds(world):
    worldlist = {"1": "Mine", "2": "Targa Plateau","3": "Swamps of Jargano"}
    
    worldname = worldlist[str(world)]
    
    return worldname


def gameover():
    n = np.n
    sleepytime = 0

    while sleepytime < 10:
        for i in range(0,n):
            np[i] = (5,0,0)
        np.write()
        time.sleep_ms(200)
        for i in range(0,n):
            spin = random.randint(1,6)
            np[i] = (spin, spin, spin)
        np.write()
        time.sleep_ms(200)
        
        sleepytime = sleepytime + 1

    while True:
        for i in range(4 * n):
            for j in range(n):
                np[j] = (0, 0, 0)
            np[i % n] = (random.randint(1,6),random.randint(1,6),random.randint(1,6))
            np.write()
            time.sleep_ms(25)
            
    resetgame()

initialize()