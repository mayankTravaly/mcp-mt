from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mytravaly_api_base_url: str = "https://api.mytravaly.com/web/v4"
    
    # API authentication headers
    mytravaly_visitor_token: str | None = None
    mytravaly_auth_token: str | None = None

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
