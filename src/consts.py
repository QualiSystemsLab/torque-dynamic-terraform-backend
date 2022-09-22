import os
from dotenv import load_dotenv
load_dotenv()

TF_MAIN_DIR = os.getenv("TORQIFY_TF_BACKEND_TF_MAIN_DIR", "/storage/workspace")

LOG_PATH = os.getenv("TORQIFY_TF_BACKEND_LOG_PATH", "../torqify_terraform_backend_log.log")
