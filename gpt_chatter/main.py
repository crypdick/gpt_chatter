"""
the entry point for your program. This file should import the other modules you will be using and set up the overall
structure of your GUI.

TODOs:
- add button to reset chatbot chat session
- permit to view historical chat sessions
"""
import tkinter as tk

from gui import ChatbotGUI


def main():
    """
    In this `main` function, we create a new `Tk` object, which represents the main window of our GUI.
    We then create an instance of the `ChatbotGUI` class and pass it the `Tk` object.
    This sets up the GUI and all of its widgets. Finally, we call the `mainloop` method on the `Tk` object to start
    the main event loop, which listens for user input and updates the GUI accordingly.

    :return:
    """
    # Create the main window
    root = tk.Tk()

    # Create an instance of the ChatbotGUI class
    gui = ChatbotGUI(root)

    # Start the main event loop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("KeyboardInterrupt: closing chatbot session")
        gui.close()
        print("Closing root")
        root.destroy()


if __name__ == "__main__":
    main()
