"""

Notice we don't follow the same test structure as in unit tests.
That's because functional tests should test the code from "outside".
So we don't need to follow any hierarchy.

"""

import pytest
from certifier.__main__ import cli
from typer.testing import CliRunner


class TestCertifier:

    # pytest fixture, passed to all methods by argument
    @pytest.fixture(autouse=True, scope="class")
    def runner(self):
        return CliRunner()

    def test_certifier_prints_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert "Usage" in result.output
