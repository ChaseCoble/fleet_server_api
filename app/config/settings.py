from pydantic import BaseSettings
import json
class AppSettings(BaseSettings):
    app_name: str
    debug: bool
    database_url: PostgresDsn
    secret_key: str

    class Config:
        env_file = ".env"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            def json_config_settings_source(settings: BaseSettings):
                with open("config.json") as f:
                    return json.load(f)

            return (
                init_settings,
                json_config_settings_source,
                env_settings,
                file_secret_settings,
            )
