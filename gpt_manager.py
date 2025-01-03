#!/usr/bin/env python3.9
# Python 3.9.13 for Linux Amazon 2023

import os
import time
from redis_based_rate_limiter import rate_limiter
from redis_based_rate_limiter import ensure_delay

import dotenv  # python-dotenv
from openai import OpenAI

class GptManager:
    MAX_MSG_LIMIT = 20
    MAX_REQUESTS_PER_SECOND = 4

    def __init__(self, token:str = None):
        self.max_msg_limit = self.MAX_MSG_LIMIT
        self.max_requests_per_second = self.MAX_REQUESTS_PER_SECOND
        self.messages = []

        if not token:
            self.token = self.find_api_token()
        else:
            self.token = token

    @rate_limiter('gpt_manager', 10, 1)
    def send_request(self, text:str):
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
        :return: Returns string
        """

        client = OpenAI(api_key=self.token)
        self.messages.append({"role": "user", "content": text})
        chat_completion = client.chat.completions.create(
            messages=self.messages,
            model="gpt-4o-mini",
        )

        response_content = chat_completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": text})
        self.apply_msg_limit()
        return response_content

    @rate_limiter('gpt_manager', 10, 1)
    def set_sys_content(self, instruction_text):
        self.messages = [message for message in self.messages if message["role"] != "system"]
        self.messages.insert(0, {"role": "system", "content": instruction_text})

    def apply_msg_limit(self):
        limit = self.max_msg_limit
        while len(self.messages) > limit and len(self.messages) > 1:
            self.messages.pop(1)

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

def test1():
    gpt_mng = GptManager()
    gpt_mng.max_msg_limit = 4
    gpt_mng.set_sys_content("Обычный чат гпт")
    respond = gpt_mng.send_request("Скажи 'раз'")
    if not respond:
        print(f"GPT API перегружен! Попробуйте позже ({respond})")
    else:
        print(respond)

    time.sleep(1)
    respond = gpt_mng.send_request("Скажи 'два!'")
    if not respond:
        print(f"GPT API перегружен! Попробуйте позже ({respond})")
    else:
        print(respond)

    respond = gpt_mng.send_request("Скажи 'три'")
    if not respond:
        print(f"GPT API перегружен! Попробуйте позже ({respond})")
    else:
        print(respond)

if __name__ == '__main__':
    test1()

    # import redis
    # redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    # print(redis_client.get("gpt_manager_call_counter"))
    # redis_client.delete("gpt_manager_call_counter")

    # import redis
    # redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    # redis_client.delete("gpt_manager_call_counter")