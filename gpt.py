from transformers import AutoTokenizer
import requests
import logging
import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("ENDPOINT")
model_id = "mistralai/Mixtral-8x7B-Instruct-v0.1"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

tokenizer = AutoTokenizer.from_pretrained(model_id)


def generate_story(task):
    system_content = ("Ты - прикольный репликон, Ты должен отвечать на все вопросы, исходя из запроса "
                      "пользователя на русском языке")
    assistant_content = "Проложи предыдущий ответ... "
    max_tokens = 60

    def count_token(text):
        return len(tokenizer.encode(text))

    def get_answer_from_gpt(user_promt, previous_answer=""):
        answer = previous_answer
        while True:
            if count_token(user_promt) > max_tokens:
                return None, "Больше 3-х букв не перевариваю"

            if user_promt == 'Завершить':
                return "Хорошо, доброго денёчка!"

            if user_promt != "Продолжить":
                answer = ""

            resp = requests.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json={
                    "messages": [
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": user_promt},
                        {"role": "assistant", "content": assistant_content + answer},
                    ],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                }
            )

            if resp.status_code == 200 and 'choices' in resp.json():
                result = resp.json()['choices'][0]['message']['content']
                if result == "":
                    return answer
                else:
                    answer += " " + result
                    return result
            else:
                return None, f"Не удалось получить ответ от нейросети. Текст ошибки: {resp.text}"

    return get_answer_from_gpt(task)

