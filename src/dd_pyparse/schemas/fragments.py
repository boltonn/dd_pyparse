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
    sha1: str = Field(None, description="sha1 hash")
    sha256: str = Field(None, description="sha256 hash")
    sha512: str = Field(None, description="sha512 hash")
    sha3_256: str = Field(None, description="sha3_256 hash")
    sha3_512: str = Field(None, description="sha3_512 hash")
    blake2b: str = Field(None, description="blake2b hash")
    blake2s: str = Field(None, description="blake2s hash")
    sha224: str = Field(None, description="sha224 hash")
    sha384: str = Field(None, description="sha384 hash")
    shake_128: str = Field(None, description="shake_128 hash")
    shake_256: str = Field(None, description="shake_256 hash")
    sha3_224: str = Field(None, description="sha3_224 hash")
    sha3_384: str = Field(None, description="sha3_384 hash")
    blake3: str = Field(None, description="blake3 hash")


class Reference(BaseModel):
    """Reference to another source"""

    name: str = Field(..., description="Name of the system")
    id: str = Field(..., description="ID of the object in another system")


class Text(BaseModel):
    """Text data"""

    source: str = Field(..., description="Source text")
    translated: str = Field(None, description="Translated text")
