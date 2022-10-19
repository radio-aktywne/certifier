#!/bin/bash --login

set +euo pipefail
conda activate certifier
set -euo pipefail

exec "$@"
