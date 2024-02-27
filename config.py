import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

image_addresses = {
    "Картинки": {
        "1": "https://characters.top/uploads/posts/2023-07/1690179563_beedle-club-p-gnom-replikon-fentezi-instagram"
             "-24.jpg"
    }
}
