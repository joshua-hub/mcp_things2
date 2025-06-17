from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Python Sandbox API"
    debug: bool = False
