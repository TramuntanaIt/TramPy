# test_api.py
import os
from dotenv import load_dotenv
from core.logger import setup_custom_logger
from connectors.minew_api import MinewAPIClient

log = setup_custom_logger("TEST")
load_dotenv()

def test():
    api = MinewAPIClient(os.getenv("MINEW_API_URL"), logger=log)
    try:
        api.login(os.getenv("MINEW_API_USER"), os.getenv("MINEW_API_PASS"))
        print("✅ Login OK")
        
        camps = api.post("/esl/scene/findDongTaiZiDuan")
        print(f"✅ Camps recuperats: {len(camps)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test()