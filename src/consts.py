import os

# todo - add usage of dotenv

TF_MAIN_DIR = os.getenv("TORQIFY_TF_BACKEND_TF_MAIN_DIR", "terraform")

LOG_PATH = os.getenv("TORQIFY_TF_BACKEND_LOG_PATH", "../torqify_terraform_backend_log.log")
