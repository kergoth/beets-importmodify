"""Tests for the 'importmodifyinfo' plugin."""

import unittest
from typing import List

import beets.plugins  # type: ignore
from beets.plugins import BeetsPlugin
from beets.plugins import find_plugins
from beets.plugins import send
from beets.test.helper import TestHelper  # type: ignore
from beets.test.helper import capture_log


class BeetsTestCase(unittest.TestCase, TestHelper):  # type: ignore
    """TestHelper based TestCase for beets."""

    def setUp(self) -> None:
        """Set up test case."""
        self.setup_beets()

    def tearDown(self) -> None:
        """Tear down test case."""
        self.teardown_beets()

    def load_plugins(self, *plugins: str) -> List[BeetsPlugin]:
        """Load and initialize plugins by names."""
        beets.plugins._instances.clear()
        beets.plugins._classes.clear()
        super().load_plugins(*plugins)
        send("pluginload")
        return find_plugins()  # type: ignore


class ImportModifyInfoPluginTest(BeetsTestCase):
    """Test cases for the importmodifyinfo beets plugin."""

    def setUp(self) -> None:
        """Set up test cases."""
        super().setUp()
        self.load_plugin()

    def load_plugin(self) -> None:
        """Load importmodifyinfo plugin."""
        with capture_log() as logs:
            plugins = self.load_plugins("importmodifyinfo")

        for plugin in plugins:
            if plugin.name == "importmodifyinfo":
                self.plugin = plugin
                break
        else:
            self.fail("Plugin not loaded")

        self.assertIn("importmodifyinfo: Plugin loaded!", logs)
