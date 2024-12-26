import base64
import logging
import os.path

import requests
import json

from src.config import CHATGPT_API_KEY, HTTPS_PROXY


class RecognizableException(Exception):
    ...


def recognize_objects(image_path: str) -> dict[str, str]:
    if not os.path.exists(image_path):
        raise RecognizableException()

    logging.debug(f"Input: {image_path}")
    proxy = {"https": HTTPS_PROXY}
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHATGPT_API_KEY}"
    }
    with open(image_path, 'rb') as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": 'Write me objects, which are on this picture. '
                                'WRITE IN JSON FORMAT LIKE {"NAME_OF_OBJECT": COUNT}. '
                                'ANSWER IN RUSSIAN. DO NOT USE MARKDOWN'
                                'If there are any plate of groceries, write ONLY {"plate_of_groceries": count} without things it consists'
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data),
                             proxies=proxy)
    logging.debug(response.status_code)
    if response.status_code != 200:
        raise RecognizableException()
    logging.info(response.content.decode())

    result = json.loads(response.content.decode())["choices"][0]["message"]["content"]
    logging.debug(result)
    if isinstance(result, str):
        result = json.loads(result)
        logging.debug(result)

    logging.debug(f"Output: {result}")
    return result


def process_plate(image_path: str) -> dict[str, str]:

    logging.debug(f"Input: {image_path}")
    proxy = {"https": HTTPS_PROXY}
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHATGPT_API_KEY}"
    }
    with open(image_path, 'rb') as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": 'Write me groceries on the plate, which is on this picture. '
                                'count percent of plate for all of them. Summary of their percents SHOULD GIVE EXACTLY 100'
                                'WRITE IN JSON FORMAT LIKE {"NAME_OF_OBJECT": PERCENT OF FOOD}. '
                                'ANSWER ON RUSSIAN. DO NOT USE MARKDOWN'
                                'DO NOT ADD YOUR COMMENTS'
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        },
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }

    response = requests.post(url, headers=headers, data=json.dumps(data),
                             proxies=proxy)
    logging.debug(response.status_code)
    if response.status_code != 200:
        raise RecognizableException()
    logging.info(response.content.decode())

    result = json.loads(response.content.decode())["choices"][0]["message"]["content"]
    logging.debug(result)
    if isinstance(result, str):
        result = json.loads(result)
        logging.debug(result)

    logging.debug(f"Output: {result}")
    summary = sum(percent for _, percent in result.items())
    logging.debug(f"Sum: {summary}")
    if summary != 100:
        for label, percent in result.items():
            percent = round(percent * 100 / summary)
            result[label] = percent

        logging.debug(f"Final sum: {sum(percent for _, percent in result.items())}")
    return result
