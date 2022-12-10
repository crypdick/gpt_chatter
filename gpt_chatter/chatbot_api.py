"""
contains the code for connecting to and interacting with the chatbot API. This file should define a class or set of functions that your GUI can use to send messages to the chatbot and receive responses.
"""


import os
import time

import colorama
from colorama import Fore
from dotenv import load_dotenv

from gpt_chatter.chat_handler import ask
from gpt_chatter.exceptions import PyChatGPTException
from gpt_chatter.openai import Auth, get_access_token, token_expired
from gpt_chatter.spinner import Spinner

colorama.init(autoreset=True)


class ChatbotAPI:
    def __init__(self, proxies: str or dict = None):
        # get email and password from .env file
        load_dotenv()
        self.email = os.getenv("OPENAI_EMAIL")
        self.password = os.getenv("OPENAI_PASSWORD")
        self.proxies = proxies

        self.__auth_access_token: str or None = None
        self.__auth_access_token_expiry: int or None = None
        self.__conversation_id: str or None = None
        self.__previous_convo_id: int or None = None
        self._setup()

    def _setup(self):
        if self.proxies is not None:
            if not isinstance(self.proxies, dict):
                if not isinstance(self.proxies, str):
                    raise PyChatGPTException("Proxies must be a string or dictionary.")
                else:
                    self.proxies = {"http": self.proxies, "https": self.proxies}

        if not self.email or not self.password:
            print(
                f"{Fore.RED}>> You must provide an email and password when initializing the class."
            )
            raise PyChatGPTException(
                f"You must provide an email and password when initializing the class, got email {self.email} and password {self.password}."
            )

        if not isinstance(self.email, str) or not isinstance(self.password, str):
            print(f"{Fore.RED}>> Email and password must be strings.")
            raise PyChatGPTException("Email and password must be strings.")

        if len(self.email) == 0 or len(self.password) == 0:
            print(f"{Fore.RED}>> Email and password cannot be empty.")
            raise PyChatGPTException("Email and password cannot be empty.")

        # Check for access_token & access_token_expiry in env
        if token_expired():
            print(
                f"{Fore.RED}>> Access Token missing or expired."
                f" {Fore.GREEN}Attempting to create them..."
            )
            self._create_access_token()
        else:
            access_token, expiry = get_access_token()
            self.__auth_access_token = access_token
            self.__auth_access_token_expiry = expiry

            try:
                self.__auth_access_token_expiry = int(self.__auth_access_token_expiry)
            except ValueError:
                print(f"{Fore.RED}>> Expiry is not an integer.")
                raise PyChatGPTException("Expiry is not an integer.")

            if self.__auth_access_token_expiry < time.time():
                print(
                    f"{Fore.RED}>> Your access token is expired. {Fore.GREEN}Attempting to recreate it..."
                )
                self._create_access_token()

    def _create_access_token(self) -> bool:
        openai_auth = Auth(
            email_address=self.email, password=self.password, proxy=self.proxies
        )
        openai_auth.create_token()

        # If after creating the token, it's still expired, then something went wrong.
        is_still_expired = token_expired()
        if is_still_expired:
            print(f"{Fore.RED}>> Failed to create access token.")
            return False

        # If created, then return True
        return True

    # def ask(self, prompt: str) -> str or None:
    #     if prompt is None:
    #         print(f"{Fore.RED}>> Enter a prompt.")
    #         raise PyChatGPTException("Enter a prompt.")
    #
    #     if not isinstance(prompt, str):
    #         raise PyChatGPTException("Prompt must be a string.")
    #
    #     if len(prompt) == 0:
    #         raise PyChatGPTException("Prompt cannot be empty.")
    #
    #     # Get access token
    #     access_token = self._get_access_token()
    #
    #     spinner = Spinner()
    #     spinner.start(Fore.YELLOW + ">> Sending request to OpenAI...")
    #     answer, previous_convo, convo_id = ask(auth_token=access_token,
    #                                                        prompt=prompt,
    #                                                        conversation_id=self.__conversation_id,
    #                                                        previous_convo_id=self.__previous_convo_id,
    #                                                        proxies=self.proxies)
    #     if answer == "400" or answer == "401":
    #         print(f"{Fore.RED}>> Failed to get a response from the API.")
    #         return None
    #
    #     self.__conversation_id = convo_id
    #     self.__previous_convo_id = previous_convo
    #
    #     spinner.stop()
    #
    #     return answer

    def _get_access_token(self):
        # Check if the access token is expired
        if token_expired():
            print(
                f"{Fore.RED}>> Your access token is expired. {Fore.GREEN}Attempting to recreate it..."
            )
            did_create = self._create_access_token()
            if did_create:
                print(f"{Fore.GREEN}>> Successfully recreated access token.")
            else:
                print(f"{Fore.RED}>> Failed to recreate access token.")
                raise PyChatGPTException("Failed to recreate access token.")
        else:
            print(f"{Fore.GREEN}>> Access token is valid.")
            print(f"{Fore.GREEN}>> Starting CLI chat session...")

        return get_access_token()

    # def cli_chat(self):
    #     """
    #     Start a CLI chat session.
    #     :param prompt:
    #     :return:
    #     """
    #
    #     access_token = self._get_access_token()
    #
    #     while True:
    #         try:
    #             prompt = input("You: ")
    #
    #             spinner = Spinner()
    #             spinner.start(Fore.YELLOW + "Chat GPT is typing...")
    #             answer, previous_convo, convo_id = ask(auth_token=access_token,
    #                                                                prompt=prompt,
    #                                                                conversation_id=self.__conversation_id,
    #                                                                previous_convo_id=self.__previous_convo_id,
    #                                                                proxies=self.proxies)
    #             if answer == "400" or answer == "401":
    #                 print(f"{Fore.RED}>> Failed to get a response from the API.")
    #                 return None
    #
    #             self.__conversation_id = convo_id
    #             self.__previous_convo_id = previous_convo
    #
    #             spinner.stop()
    #
    #             print(f"Chat GPT: {answer}")
    #         except KeyboardInterrupt:
    #             print(f"{Fore.RED}>> Exiting...")
    #             break

    def send_message(self, msg):
        access_token = self._get_access_token()

        spinner = Spinner()
        spinner.start(Fore.YELLOW + "Chat GPT is typing...")
        answer, previous_convo, convo_id = ask(
            auth_token=access_token,
            prompt=msg,
            conversation_id=self.__conversation_id,
            previous_convo_id=self.__previous_convo_id,
            proxies=self.proxies,
        )
        if answer == "400" or answer == "401":
            print(f"{Fore.RED}>> Failed to get a response from the API.")
            return None

        self.__conversation_id = convo_id
        self.__previous_convo_id = previous_convo

        spinner.stop()

        print(f"Chat GPT: {answer}")

        return answer


# class ChatbotAPI:
#     def __init__(self):
#
#         # Create a thread-safe queue for sending messages to the chatbot
#         self.send_queue = queue.Queue()
#
#         # Create a thread-safe queue for receiving messages from the chatbot
#         self.receive_queue = queue.Queue()
#
#         # Start a thread for sending and receiving messages
#         self.api_thread = threading.Thread(target=self.run)
#         self.running = True
#         self.api_thread.start()
#
#     def send_message(self, message):
#         # Put the message on the send queue
#         self.send_queue.put(message)
#
#         # Get the response from the receive queue
#         response = self.receive_queue.get()
#
#         # Return the response
#         return response
#
#     def run(self):
#         while self.running:
#             # Get the next message from the send queue
#             message = self.send_queue.get()
#
#             # Send the message to the chatbot
#             # response = requests.post(self.base_url, data={"message": message}).text
#             response = f'dummy response to {message}'
#
#             # Put the response on the recieve queue
#             self.receive_queue.put(response)
#
#     def __del__(self):
#         # kill the API thread
#         self.running = False
#         self.api_thread.join()
#
#
