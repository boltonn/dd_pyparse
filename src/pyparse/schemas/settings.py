from typing import Optional

from pydantic import Field

from pyparse.schemas.fragments import ElasticsearchConfig
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    host: str = Field("0.0.0.0", validation_alias="HOST", description="Host to bind to")
    port: int = Field(8080, validation_alias="PORT", description="Port to bind to")
    reload: Optional[bool] = Field(True, description="Reload mode")
    log_file: Optional[str] = Field(None, description="File to write logs to if desired")
    log_level: Optional[str] = Field("INFO", validation_alias="LOG_LEVEL", description="Log level")
    es_config: Optional[ElasticsearchConfig] = Field(None, description="Elasticsearch configuration object")
    model_config = SettingsConfigDict(env_file='.env', env_nested_delimiter='__', use_enum_values=True)
