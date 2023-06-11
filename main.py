import time
import random
from pimoroni import Button
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P4

# Initialize the PicoGraphics display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_P4, rotate=0)
display.set_backlight(0.5)
display.set_font("bitmap8")
display.set_thickness(0)

# Determine the text speed
text_speed = 5  # Steps per second
frame_rate = max(60, text_speed)  # number of frames per second
frame_duration = 1.0 / text_speed  # duration of each frame in seconds
last_countdown_update = time.time()  # the time when we last updated the countdown

# Constants for the display size
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 135

# Initialize buttons
button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

# Define colors
WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
CYAN = display.create_pen(0, 255, 255)
MAGENTA = display.create_pen(255, 0, 255)
YELLOW = display.create_pen(255, 255, 0)
GREEN = display.create_pen(0, 255, 0)
RED = display.create_pen(255, 0, 0)
DARK_RED = display.create_pen(100, 0, 0)

def slide_text(text, position, step):
    display.set_pen(WHITE)
    display.text(text, position, DISPLAY_HEIGHT // 2)
    position -= step
    text_width = display.measure_text(text)  # Measure the actual width of the text

    if position + text_width <= DISPLAY_WIDTH:
        # If text is smaller than screen width, append text to itself
        text = text + "    " + text  # Append the text with spaces to itself

    if position + text_width <= 0:
        # If text has scrolled out of screen, start over
        position = DISPLAY_WIDTH  # Restart text from the right side of the screen
        
    return position, text
# Dynamic state of bars while playing
def animate_bars(bar_count, bar_width, bar_spacing, bar_heights, bar_directions):
    dimensions = bar_width + bar_spacing
    for i in range(bar_count):
        bar_heights[i] += bar_directions[i]
        if bar_heights[i] <= 5 or bar_heights[i] >= 40:
            bar_directions[i] *= -1

        bar_height = bar_heights[i]
        green_height = int(bar_height * 0.75)
        yellow_height = int(bar_height * 0.05)
        red_height = int(bar_height * 0.20)
        base_height = 64 + 60 + 10
        current_dimensions = dimensions * i

        display.set_pen(GREEN)
        display.rectangle(current_dimensions, base_height - green_height, bar_width, green_height)

        display.set_pen(YELLOW)
        display.rectangle(current_dimensions, base_height - green_height - yellow_height, bar_width, yellow_height)

        if green_height >= 30:
            display.set_pen(RED)
            display.rectangle(current_dimensions, base_height - green_height - yellow_height - red_height, bar_width, red_height)

# Static state of bars while paused
def draw_bars(bar_count, bar_width, bar_spacing, bar_heights):
    dimensions = bar_width + bar_spacing
    for i in range(bar_count):
        base_height = 64 + 60 + 10
        current_dimensions = dimensions * i

        display.set_pen(GREEN)
        display.rectangle(current_dimensions, base_height - bar_heights[i], bar_width, bar_heights[i])

def clear():
    display.set_pen(BLACK)
    display.clear()

# Draws the play symbol (a right-pointing arrow)
def play_shapes():
    display.set_pen(GREEN)
    display.rectangle(0, 10, 10, 10)
    display.set_pen(RED)
    display.rectangle(0, 30, 10, 10)
    display.set_pen(GREEN)
    display.triangle(20, 50, 40, 30, 20, 10)

# Draws the pause symbol (two vertical bars)
def pause_shapes():
    display.set_pen(GREEN)
    display.rectangle(10, 20, 10, 25)
    display.rectangle(30, 20, 10, 25)

# Initialize the countdown text
countdown_time = 0
countdown_text = "00:00"

# Clear the display
clear()

# Set parameters for bar animation
bar_count = 20
bar_width = 10
bar_spacing = 2
bar_heights = [random.randint(5, 40) for _ in range(bar_count)]
bar_directions = [random.choice([-1, 1]) for _ in range(bar_count)]

# Initialize sliding texts as a list
sliding_texts = ["DJ Mike Llama - Llama Whippin' Intro (0:05)     ***",
                "Test - Test track (0:45)     ***"]
text_x_position = DISPLAY_WIDTH
current_sliding_text_index = 0  # Variable to track the current sliding text index

start_time = time.time()
last_update_time = start_time
paused = False  # Add a new variable to keep track of whether the system is paused
blink_state = False  # variable for blinking state
last_blink_time = time.time()

while True:
    if button_a.read():
        clear()
        text_x_position = DISPLAY_WIDTH
        play_shapes()
        countdown_time = 0
        paused = False
        continue_flag = True
        blink_state = False
        last_countdown_update = time.time()

        while countdown_time < 3600:
            if button_x.read():
                paused = True
                blink_state = False
                last_blink_time = time.time()
                time.sleep(0.5)

            if button_a.read():
                paused = False
                time.sleep(0.5)

            if button_b.read():
                clear()
                display.update()
                break

            if button_y.read():
                current_sliding_text_index = (current_sliding_text_index + 1) % len(sliding_texts)
                text_x_position = DISPLAY_WIDTH
                countdown_time = 0
                paused = False  # Exit paused state and switch to play state


            if paused:
                current_time = time.time()

                # If a second has passed since the last blink
                if current_time - last_blink_time >= 1:
                    last_blink_time = current_time
                    blink_state = not blink_state  # toggle the blinking state

                clear()

                # Draw the countdown text with blinking minutes and seconds
                minutes = countdown_time // 60
                seconds = countdown_time % 60

                if blink_state:
                    countdown_text = f"{minutes:02}:{seconds:02}"
                else:
                    countdown_text = f""  # Display minutes and seconds without blinking

                display.set_pen(GREEN)
                display.text(countdown_text, 110, 15, scale=6)
                display.text(":", 170, 15, scale=6)  # Display the colon without blinking

                pause_shapes()  # Show the pause symbol
                text_x_position, sliding_texts[current_sliding_text_index] = slide_text(sliding_texts[current_sliding_text_index], text_x_position, 13)

                draw_bars(bar_count, bar_width, bar_spacing, bar_heights)  # Show the static state of the bars
                display.update()

            else:
                current_time = time.time()

                if current_time - last_countdown_update >= 1:
                    last_countdown_update = current_time
                    countdown_time += 1
                    minutes = countdown_time // 60
                    seconds = countdown_time % 60
                    countdown_text = f"{minutes:02}:{seconds:02}"

                clear()
                display.set_pen(GREEN)
                display.text(countdown_text, 110, 15, scale=6)
                play_shapes()  # Show the play symbol
                animate_bars(bar_count, bar_width, bar_spacing, bar_heights, bar_directions)  # Animate the bars

                text_x_position, sliding_texts[current_sliding_text_index] = slide_text(sliding_texts[current_sliding_text_index], text_x_position, 13)


                display.update()

            time.sleep(1 / text_speed)

        clear()

    else:
        display.set_pen(GREEN)
        display.rectangle(10, 10, 15, 15)
        display.text(":", 170, 15, scale=6)
        display.update()

    time.sleep(0.1)

