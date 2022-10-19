import logging

from trustme import CA

from certifier.cert.issuers.selfsigned import (
    SelfSignedIssuerContext,
    SelfSignedIssuer,
)
from certifier.cert.issuers.traefik import (
    TraefikMeIssuerContext,
    TraefikMeIssuer,
)
from certifier.config.models import Config

logger = logging.getLogger(__name__)


def certify(config: Config) -> None:
    path = config.path

    if config.ca_cert is not None and config.ca_key is not None:
        if config.ca_cert.exists() and config.ca_key.exists():
            ca = CA.from_pem(
                config.ca_cert.read_bytes(), config.ca_key.read_bytes()
            )
        else:
            logger.warning("CA cert or key not found, generating new CA.")
            ca = CA(
                organization_name=config.organization,
                organization_unit_name=config.unit,
            )
    else:
        ca = CA(
            organization_name=config.organization,
            organization_unit_name=config.unit,
        )

    for name, cfg in config.certs.items():
        subpath = path / name
        if subpath.exists() and any(subpath.iterdir()):
            logger.warning(
                f"Certificates for {name} already exist, skipping..."
            )
            continue

        subpath.mkdir(parents=True, exist_ok=True)

        if cfg.type == "self-signed":
            logger.info(f"Generating self-signed certificates for {name}...")

            context = SelfSignedIssuerContext(
                ca=ca,
                organization=config.organization,
                unit=config.unit,
                name=name,
                path=subpath,
                default_identities=config.default_identities,
                default_ca_file=config.default_ca_file,
                default_cert_file=config.default_cert_file,
                default_key_file=config.default_key_file,
                default_client_cert_file=config.default_client_cert_file,
                default_client_key_file=config.default_client_key_file,
            )
            SelfSignedIssuer.issue(context, cfg)

            logger.info(f"Certificates for {name} generated!")
        elif cfg.type == "traefik.me":
            logger.info(f"Generating traefik.me certificates for {name}...")

            context = TraefikMeIssuerContext(
                path=subpath,
                default_cert_file=config.default_cert_file,
                default_key_file=config.default_key_file,
            )
            TraefikMeIssuer.issue(context, cfg)

            logger.info(f"Certificates for {name} generated!")

        else:
            logger.error(
                f"Unknown certificate type {cfg.type} for {name}! Skipping..."
            )
