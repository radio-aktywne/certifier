from pathlib import Path
from typing import Optional, Set, Literal, List, Annotated, Union, Dict

from pydantic import BaseModel, Field

from certifier.config.base import BaseConfig


class SelfSignedSingleCertConfig(BaseModel):
    identities: Optional[Set[str]] = None
    cert_file: Optional[str] = None
    key_file: Optional[str] = None


class SelfSignedCertConfig(BaseModel):
    type: Literal["self-signed"] = "self-signed"
    ca_file: Optional[str] = None
    server: List[SelfSignedSingleCertConfig] = []
    client: List[SelfSignedSingleCertConfig] = []


class TraefikMeCertConfig(BaseModel):
    type: Literal["traefik.me"] = "traefik.me"
    cert_file: Optional[str] = None
    key_file: Optional[str] = None


CertConfig = Annotated[
    Union[
        SelfSignedCertConfig,
        TraefikMeCertConfig,
    ],
    Field(discriminator="type"),
]


class Config(BaseConfig):
    path: Path
    organization: str = "certifier"
    unit: str = "certifier"
    ca_cert: Optional[Path] = None
    ca_key: Optional[Path] = None
    certs: Dict[str, CertConfig] = {}
    default_identities: Set[str] = ["127.0.0.1", "localhost", "*.localhost"]
    default_ca_file: str = "ca.pem"
    default_cert_file: str = "cert.pem"
    default_key_file: str = "key.pem"
    default_client_cert_file: str = "client.cert.pem"
    default_client_key_file: str = "client.key.pem"
