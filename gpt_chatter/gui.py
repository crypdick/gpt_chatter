"""
code for building and managing the GUI itself.
This file should define a class that represents your GUI, and include methods for creating the different widgets,
displaying messages, and handling user input.
"""
import time
import tkinter as tk

from chatbot_api import ChatbotAPI


class ChatbotGUI:
    def __init__(self, master):
        # Create the main window
        self.master = master

        # add a menu bar with a `Close` button
        self.menu_bar = tk.Menu(self.master)
        self.menu_bar.add_command(label="Close", command=self.close)
        self.master.config(menu=self.menu_bar)

        self.master.title("Chatbot")
        self.chatbot_session = ChatbotAPI()

        # Register the close method as a callback for the WM_DELETE_WINDOW event
        master.protocol("WM_DELETE_WINDOW", self.close)

        # Create the widgets
        self.label = tk.Label(self.master, text="Enter your message:")
        # input box, with wrapping text
        self.input_box = tk.Text(self.master)
        # make Entry span the entire width of the screen

        self.send_button = tk.Button(self.master, text="Send")
        # self.chat_history = tk.Listbox(self.master)
        self.chat_history = tk.Text(self.master)
        # Create a tag for the HTML content
        self.chat_history.tag_configure("html", foreground="blue")
        self.chat_history.config(state="disabled")

        # Lay out the widgets
        # self.label.grid(row=0, column=0)
        # self.input_box.grid(row=0, column=1)
        # self.send_button.grid(row=0, column=2, fill='row', expand=True)
        # self.chat_history.grid(row=1, columnspan=2)
        # make chat_history take the whole window width
        # self.label.pack(side='left', fill=None, expand=False)
        # self.input_box.pack(side='top', fill='both', expand=True)
        # self.send_button.pack(side='right', fill=None, expand=False)
        # self.chat_history.pack(side="left", fill="both", expand=True)

        # rewrite the above so that label, input_box, are on the same row
        # followed by the send_button on another row,
        # followed by the chat_history on another row
        self.label.pack(side="left", fill=None, expand=False)
        self.input_box.pack(side="top", fill="both", expand=True)
        # row 2
        self.send_button.pack(side="right", fill=None, expand=False)
        # row 3
        self.chat_history.pack(side="bottom", fill="both", expand=True)

        # Bind the send button to the send_message method
        self.send_button.bind("<Button-1>", self.send_message)

        self.save_fname = f'{time.strftime("%Y-%-m-%d--%H:%M:%S")}__chatGPT.md'
        print(f"Writing to {self.save_fname}")

    def send_message(self, event):
        # check if the chat session is saved, and if not, open a file and save if
        with open(self.save_fname, "w+") as f:

            # Get the message from the text entry
            prompt = self.input_box.get("1.0", tk.END)
            prompt = "You: " + prompt + "\n"

            # make text editable temporarily
            self.chat_history.config(state="normal")

            # Clear the text entry once we've gotten the input
            self.input_box.delete("1.0", tk.END)

            # Add the message to the message display
            self.chat_history.insert("end", prompt)
            f.write(prompt)

            print(f"Got input: {prompt}")

            # Send the message to the chatbot
            # (Code for connecting to the chatbot API goes here)
            response = self.chatbot_session.send_message(prompt)
            response = f"Chatbot: {response}\n"

            print(f"Got response: {response}")
            # html = markdown2.markdown(response)

            # Add the response to the message display
            # tag as html to correctly render
            self.chat_history.insert("end", response)
            f.write(response)
            f.write("--\n")
            # self.chat_history.tag_add("html", "1.0", tk.END)
            # makes widget uneditable
            self.chat_history.config(state="disabled")

    def close(self):
        del self.chatbot_session
        print("Closing GUI")
        self.master.destroy()
