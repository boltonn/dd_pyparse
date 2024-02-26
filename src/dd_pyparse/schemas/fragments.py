from pydantic import BaseModel, Field


class ElasticsearchConfig(BaseModel):
    host: str = Field(
        "0.0.0.0",
        validation_alias="ELASTICSEARCH__HOST",
        description="Elasticsearch host for attaching to the logical cluster",
    )
    port: int = Field(9200, validation_alias="ELASTICSEARCH__PORT", description="Elasticsearch port")
    crt: str = Field(
        "/home/boltonn/rogue-analytics/http_ca.crt",
        validation_alias="ELASTICSEARCH__CA_CERT",
        description="Elasticsearch CA certificate",
    )
    user: str = Field("elastic", validation_alias="ELASTICSEARCH_USERNAME", description="Elasticsearch username")
    pwd: str = Field(
        "A*1eatWYWy_bZ7vLrbaA",
        validation_alias="ELASTICSEARCH__PASSWORD",
        description="Elasticsearch password",
    )


class Hash(BaseModel):
    """Hash data"""

    md5: str = Field(None, description="md5 hash")
    meaningful: str = Field(None, description="Meaningful hash")
    sha256: str = Field(None, description="sha256 hash")
    sha512: str = Field(None, description="sha512 hash")

class Reference(BaseModel):
    """Reference to another source"""

    name: str = Field(..., description="Name of the system")
    url: str = Field(..., description="URL of the object in another system")


class Text(BaseModel):
    """Text data"""

    source: str = Field(..., description="Source text")
    translated: str = Field(None, description="Translated text")
