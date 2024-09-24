"""Tests for the 'importmodifyinfo' plugin."""

import unittest
from typing import List

import beets.plugins  # type: ignore
from beets import config  # type: ignore
from beets.plugins import BeetsPlugin
from beets.plugins import find_plugins
from beets.plugins import send
from beets.test.helper import TestHelper  # type: ignore
from beetsplug.importmodifyinfo import ImportModifyInfoPlugin


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


class ImportModifyInfoPluginTestDisabled(BeetsTestCase):
    """Test cases for the importmodifyinfo beets plugin when disabled."""
    def setUp(self) -> None:
        """Set up test cases."""
        super().setUp()

        config["importmodifyinfo"]["enabled"] = False
        ImportModifyInfoPlugin.listeners = None
        ImportModifyInfoPlugin._raw_listeners = None
        self.plugin = ImportModifyInfoPlugin(name="importmodifyinfo")

    def test_disabled(self) -> None:
        """Test if the plugin can be disabled."""
        assert not self.plugin.config["enabled"].get(bool)
        assert not self.plugin.__class__.listeners


class ImportModifyInfoPluginTest(BeetsTestCase):
    """Test cases for the importmodifyinfo beets plugin."""

    def setUp(self) -> None:
        """Set up test cases."""
        super().setUp()
        self.load_plugin()

    def load_plugin(self) -> None:
        """Load importmodifyinfo plugin."""
        plugins = self.load_plugins("importmodifyinfo")
        for plugin in plugins:
            if plugin.name == "importmodifyinfo":
                self.plugin = plugin
                break
        else:
            self.fail("Plugin not loaded")

    def _setup_config(self, **kwargs: str) -> None:
        """Set up configuration."""
        self.plugin.config.clear()
        self.plugin.config.update(kwargs)

    def test_albuminfo(self) -> None:
        """Test basic rules applied to an AlbumInfo object."""
        pass
