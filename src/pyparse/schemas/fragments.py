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

class Reference(BaseModel):
    """Reference to another source"""

    name: str = Field(..., description="Name of the system")
    id: str = Field(..., description="ID of the object in another system")
