import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

dotenv_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    ".env"
)
if not os.path.exists(dotenv_path):
    print("[Settings] No .env file found.")

load_dotenv(dotenv_path)

class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """

    DATASOURCE_DIR: str
    OUTPUT_DIR: str

    # Dask Settings
    DASK_CPU_LIMIT: int
    DASK_DASHBOARD_PORT: str
    DASK_MEMORY_LIMIT: str
    DASK_SCHEDULER_ADDRESS: Optional[str] = None
    N_WORKER_DASK: int
    N_THREADS_PER_DASK_WORKER: int

    # LLM Settings
    LLM_SERVICE: str
    LLM_MODEL: str
    LLM_HOST: Optional[str] = "localhost"
    LLM_PORT: Optional[int] = 11434
    LLM_CONNECT_PROTOCOL: str = "http://"
    LLM_TEMPERATURE: float
    LLM_NUM_THREADS: int

settings = Settings()
