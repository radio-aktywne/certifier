import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Set, Optional

from trustme import CA

from certifier.cert.issuers.base import Issuer
from certifier.config.models import (
    SelfSignedCertConfig,
    SelfSignedSingleCertConfig,
)
from certifier.utils import classproperty

logger = logging.getLogger(__name__)


@dataclass
class SelfSignedIssuerContext:
    ca: CA
    organization: str
    unit: str
    name: str
    path: Path
    default_identities: Set[str]
    default_ca_file: str
    default_cert_file: str
    default_key_file: str
    default_client_cert_file: str
    default_client_key_file: str


class SelfSignedIssuer(Issuer[SelfSignedIssuerContext, SelfSignedCertConfig]):
    @classproperty
    def category(cls) -> str:
        return "self-signed"

    @classmethod
    def issue(
        cls, context: SelfSignedIssuerContext, config: SelfSignedCertConfig
    ) -> None:
        for cfg in config.server:
            cls._issue_server(context, cfg)
        for cfg in config.client:
            cls._issue_client(context, cfg)

        logger.info("Issuing CA certificate")
        ca_file = config.ca_file or context.default_ca_file
        context.ca.cert_pem.write_to_path(str(context.path / ca_file))
        os.chmod(context.path / ca_file, 0o644)
        logger.info(f"CA certificate written to {context.path / ca_file}")

    @staticmethod
    def _issue_single(
        ca: CA,
        identities: Set[str],
        organization: Optional[str],
        unit: Optional[str],
        cert_path: Path,
        key_path: Path,
    ):
        cert = ca.issue_cert(
            *list(identities),
            organization_name=organization,
            organization_unit_name=unit,
        )

        for i, entry in enumerate(cert.cert_chain_pems):
            entry.write_to_path(str(cert_path), append=i > 0)

        cert.private_key_pem.write_to_path(key_path)

        os.chmod(cert_path, 0o644)
        os.chmod(key_path, 0o600)

    @staticmethod
    def _safe_filename(directory: Path, filename: str) -> str:
        filtered = [
            file
            for file in directory.iterdir()
            if file.is_file() and file.name.endswith(f"{filename}")
        ]

        if not filtered:
            return filename

        prefixes = [file.name.partition(".")[0] for file in filtered]

        numbers = []
        for prefix in prefixes:
            try:
                numbers.append(int(prefix))
            except ValueError:
                pass

        highest = max(numbers) if numbers else -1
        return f"{highest + 1}.{filename}"

    @classmethod
    def _issue_server(
        cls,
        context: SelfSignedIssuerContext,
        config: SelfSignedSingleCertConfig,
    ) -> None:
        identities = config.identities or {context.name}
        identities.update(context.default_identities)

        cert_file = config.cert_file or context.default_cert_file
        key_file = config.key_file or context.default_key_file

        cert_file = cls._safe_filename(context.path, cert_file)
        key_file = cls._safe_filename(context.path, key_file)

        logger.info(
            f"Issuing server certificate for {', '.join(identities)}..."
        )

        cls._issue_single(
            context.ca,
            identities,
            context.organization,
            context.unit,
            context.path / cert_file,
            context.path / key_file,
        )

        logger.info(
            f"Server certificate written to {context.path / cert_file} "
            f"and key to {context.path / key_file}",
        )

    @classmethod
    def _issue_client(
        cls,
        context: SelfSignedIssuerContext,
        config: SelfSignedSingleCertConfig,
    ) -> None:
        identities = config.identities or {context.name}
        identities.update(context.default_identities)

        cert_file = config.cert_file or context.default_client_cert_file
        key_file = config.key_file or context.default_client_key_file

        cert_file = cls._safe_filename(context.path, cert_file)
        key_file = cls._safe_filename(context.path, key_file)

        logger.info(
            f"Issuing client certificate for {', '.join(identities)}..."
        )

        cls._issue_single(
            context.ca,
            identities,
            context.organization,
            context.unit,
            context.path / cert_file,
            context.path / key_file,
        )

        logger.info(
            f"Client certificate written to {context.path / cert_file} "
            f"and key to {context.path / key_file}",
        )
