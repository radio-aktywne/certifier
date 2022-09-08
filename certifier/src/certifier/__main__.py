"""Main script.

This module provides basic CLI entrypoint.

"""
import logging
from pathlib import Path
from typing import Optional

import typer
from typer import FileText

from certifier import log
from certifier.cert.certify import certify
from certifier.config.parse import parse_config
from certifier.config.source import get_config
from certifier.log import Verbosity

cli = typer.Typer()  # this is actually callable and thus can be an entry point

logger = logging.getLogger(__name__)


@cli.command()
def main(
    config: Optional[FileText] = typer.Option(
        None, "--config", "-c", dir_okay=False, help="Configuration file"
    ),
    ca_cert: Optional[Path] = typer.Option(
        None, "--ca-cert", "-C", dir_okay=False, help="CA certificate"
    ),
    ca_key: Optional[Path] = typer.Option(
        None, "--ca-key", "-K", dir_okay=False, help="CA private key"
    ),
    verbosity: Verbosity = typer.Option(
        "INFO", "--verbosity", "-v", help="Verbosity level."
    ),
) -> None:
    """Command line interface for certifier."""

    log.configure(verbosity)

    logger.info("Loading config...")

    extra = {}
    if ca_cert is not None and ca_cert.exists():
        extra["ca_cert"] = ca_cert
    if ca_key is not None and ca_cert.exists():
        extra["ca_key"] = ca_key

    try:
        config = parse_config(get_config(config, **extra))
    except ValueError as e:
        logger.error("Failed to parse config", exc_info=e)
        raise typer.Exit(1)

    logger.info("Config loaded!")
    logger.info("Generating certificates...")

    certify(config)

    logger.info("Certificates generated!")


if __name__ == "__main__":
    # entry point for "python -m"
    cli()
