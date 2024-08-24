import os
from dotenv import load_dotenv


load_dotenv()
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')


test_mode = int(os.getenv('test_mode'))

airt_api_key = os.getenv('airt_api_key')
tg_api_key_test = os.getenv('tg_api_key_test')
tg_api_key_prod = os.getenv('tg_api_key_prod')
airt_api_key = os.getenv('airt_api_key')