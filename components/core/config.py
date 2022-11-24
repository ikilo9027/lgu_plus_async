from starlette.config import Config

config = Config(".env")

VERSION: str = "2.0"
PROJECT_NAME: str = config(
    "PROJECT_NAME", default="LGU_PLUS_ASYNC_PROJECT API")
DESCRIPTION: str = config(
    "DESCRIPTION", default="---espresomedia lgu+ async project---")

SERVER_IP: str = "http://192.168.0.214"
SERVER_PORT: str = "4050"
