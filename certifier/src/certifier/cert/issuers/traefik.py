import os
from dataclasses import dataclass
from pathlib import Path

import httpx

from certifier.cert.issuers.base import Issuer
from certifier.config.models import TraefikMeCertConfig
from certifier.utils import classproperty


@dataclass
class TraefikMeIssuerContext:
    path: Path
    default_cert_file: str
    default_key_file: str


class TraefikMeIssuer(Issuer[TraefikMeIssuerContext, TraefikMeCertConfig]):
    @classproperty
    def category(cls) -> str:
        return "traefik.me"

    @classmethod
    def issue(
        cls, context: TraefikMeIssuerContext, config: TraefikMeCertConfig
    ) -> None:
        cert_file = config.cert_file or context.default_cert_file
        key_file = config.key_file or context.default_key_file

        with open(context.path / cert_file, "w") as f:
            response = httpx.get("https://traefik.me/fullchain.pem")
            f.write(response.text)

        with open(context.path / key_file, "w") as f:
            response = httpx.get("https://traefik.me/privkey.pem")
            f.write(response.text)

        os.chmod(context.path / cert_file, 0o644)
        os.chmod(context.path / key_file, 0o600)
