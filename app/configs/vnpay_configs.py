import os
from dotenv import load_dotenv

# Load biến môi trường từ .env
load_dotenv()

class VNPAYConfig:
    VNP_TMNCODE = os.getenv("VNP_TMNCODE")  # Merchant ID
    VNP_HASHSECRET = os.getenv("VNP_HASHSECRET")  # Secret Key
    VNP_URL = os.getenv("VNP_URL")  # URL Payment Gateway
    VNP_RETURN_URL = os.getenv("VNP_RETURN_URL")  # URL Callback
