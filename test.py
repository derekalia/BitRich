from do_agent import PageDoAgent

# Create an instance of the PageDoAgent class
agent = PageDoAgent()

# Call the runDoAgent method on the instance
agent.runDoAgent("Press the Trade button at the top of the screen")


'''

import pyautogui
import time

# Define the coordinates of the mother.py tab (replace with the actual coordinates of your tab)
tab_coordinates = [696, 87, 172, 44]

# Move the mouse to the tab and click on it
pyautogui.moveTo(tab_coordinates[0], tab_coordinates[1])
pyautogui.click()

# Wait for 1 second to allow the window to change
time.sleep(1)

# Get the current window title (this function is platform-dependent and might need third-party libraries)
try:
    current_window_title = pyautogui.getActiveWindow().title
    print(f"Current window title: {current_window_title}")
except AttributeError:
    print("Unable to get the current window title. Ensure that your platform supports this feature.")

# If you want to switch to a specific window, you can use the following code
# Replace 'Your Window Title' with the title of the window you want to activate
# pyautogui.getWindowsWithTitle('Your Window Title')[0].activate()'''