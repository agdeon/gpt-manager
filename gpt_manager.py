#!/usr/bin/env python3.9
# Python 3.9.13 for Linux Amazon 2023

import os
import time

import dotenv  # requirements: python-dotenv
from openai import OpenAI

class GptManager:
    MAX_MSG_LIMIT = 20
    MAX_REQUESTS_PER_SECOND = 3

    def __init__(self, token:str = None):
        self.max_msg_limit = self.MAX_MSG_LIMIT
        self.max_requests_per_second = self.MAX_REQUESTS_PER_SECOND
        self.messages = []

        if not token:
            self.token = self.find_api_token()
        else:
            self.token = token

    def send_request(self, text:str = ''):
        """
        Sends request to GPT.
        Messages list format: [
            {"role": "system", "content": "Your instruction for gpt"}, For gpt instructions
            {"role": "user", "content": "some user requests"}, For user requests
            {"role": "assistant", "content": "prev gpt response"}, For gpt history tracking
            {"role": "user", "content": "some user requests"}, For user requests
            {"role": "assistant", "content": "prev gpt response"}, For gpt history tracking
            ...
        ]

        :param text: (opt) If sending just one question
        :type text: str
        :param messages: (opt) a list of messages in the format shown above
        :type messages: list
        :return: Returns string
        """
        client = OpenAI(api_key=self.token)
        if text != '' and len(self.messages) == 0:
            chat_completion = client.chat.completions.create(
                messages=[ {"role": "user", "content": text} ],
                model="gpt-4o-mini",
            )
        else:
            raise Exception("send_request: No content to send")

        time.sleep(round(1 / self.MAX_REQUESTS_PER_SECOND))
        return chat_completion.choices[0].message.content



    def set_rps_limit(self, value: int):
        """
        Sets the rate limit for requests per second. Allows to control
        the maximum number of requests that can be made per second
        """
        pass

    @staticmethod
    def find_api_token():
        """
        Tries to find token in local .env files
        """
        dotenv.load_dotenv()
        token = os.getenv('GPT_TOKEN')
        if not token:
            raise Exception("os.getenv: no token")
        return token

def main():
    client = GptClient()
    respond = client.send_request("Привет")
    print(respond)

if __name__ == '__main__':
    main()