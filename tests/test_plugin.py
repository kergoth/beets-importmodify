"""Tests for the 'importmodifyinfo' plugin."""

from typing import Any
from typing import List
from typing import Union
from typing import get_type_hints

import beets.plugins  # type: ignore
import pytest
from beets.autotag.hooks import AlbumInfo  # type: ignore
from beets.autotag.hooks import TrackInfo
from beets.plugins import BeetsPlugin
from beets.plugins import find_plugins
from beets.plugins import send
from beets.test.helper import TestHelper  # type: ignore
from beets.ui import UserError  # type: ignore


def new_trackinfo() -> TrackInfo:
    """Create a TrackInfo object for testing."""
    info = TrackInfo(track_flex="flex", track_flex_none=None)
    set_default_values(info)
    return info


def new_albuminfo() -> AlbumInfo:
    """Create an AlbumInfo object for testing."""
    track_info = new_trackinfo()
    info = AlbumInfo(
        year=2000,
        tracks=[track_info],
        albumtype="album",
        albumtypes=["album", "remix"],
        flex="flex",
        flex_none=None,
    )
    set_default_values(info)
    return info


def set_default_values(info: Union[TrackInfo, AlbumInfo]) -> None:
    """Set default values for testing TrackInfo or AlbumInfo."""
    infotypes = get_type_hints(info.__init__)
    for field, field_type in sorted(infotypes.items()):
        if field_type is bool or field_type.__origin__ is bool:
            continue
        elif field_type.__origin__ is Union:
            args = field_type.__args__
            if args[1] == type(None):
                # Optional type
                field_type = args[0]
            else:
                continue

        if field_type is str:
            info[field] = field
        elif field_type is int:
            info[field] = 0
        elif field_type is float:
            info[field] = 0.0
        elif getattr(field_type, "__origin__", None) is list:
            if field_type.__args__[0] is str:
                info[field] = [field]


class BeetsTestCase(TestHelper):  # type: ignore
    """TestHelper based TestCase for beets."""

    def setup_method(self) -> None:
        """Set up test case."""
        self.setup_beets()

    def teardown_method(self) -> None:
        """Tear down test case."""
        self.teardown_beets()

    def load_plugins(self, *plugins: str) -> List[BeetsPlugin]:
        """Load and initialize plugins by names."""
        beets.plugins._instances.clear()
        beets.plugins._classes.clear()
        super().load_plugins(*plugins)
        send("pluginload")
        return find_plugins()  # type: ignore


class ImportModifyInfoTestCase(BeetsTestCase):
    """Base class for the importmodifyinfo beets plugin."""

    def setup_method(self) -> None:
        """Set up test cases."""
        super().setup_method()
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

    def _setup_config(self, **kwargs: Any) -> None:
        """Set up configuration."""
        self.plugin.config.set(kwargs)


class TestImportModifyInfoPluginDisabled(ImportModifyInfoTestCase):
    """Test cases for the importmodifyinfo beets plugin when disabled."""

    def setup_method(self) -> None:
        """Set up test cases."""
        self.setup_beets()
        self.config["importmodifyinfo"]["enabled"] = False
        BeetsPlugin.listeners = None
        BeetsPlugin._raw_listeners = None
        self.load_plugin()

    def test_disabled(self) -> None:
        """Test if the plugin can be disabled."""
        assert not self.plugin.config["enabled"].get(True)
        assert not BeetsPlugin.listeners


class TestImportModifyInfoPlugin(ImportModifyInfoTestCase):
    """Test cases for the importmodifyinfo beets plugin."""

    @pytest.mark.parametrize(
        "field,new_value",
        [
            ("album", "new album"),
            ("artist", "new artist"),
            ("year", 1900),
            ("flex", "new flex"),
        ],
    )
    def test_album_matching(self, field: str, new_value: str) -> None:
        """Test rules applied to an AlbumInfo object."""
        albuminfo = new_albuminfo()
        value = albuminfo[field]

        if isinstance(value, str):
            query = f"{field}:'{value}'"
        else:
            query = f"{field}:{value}"
        rule = f"{query} {field}='{new_value}'"
        self._setup_config(modify_albuminfo=[rule])

        self.plugin.apply_albuminfo_rules(albuminfo)
        assert (
            albuminfo[field] == new_value
        ), f"field {field} was not set to {new_value} with rule {rule}"

    def test_unquoted_singleword(self) -> None:
        """Test rules applied to an AlbumInfo object without quotes."""
        albuminfo = new_albuminfo()
        self._setup_config(modify_albuminfo=["album:album album=new_album"])
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo["album"] == "new_album"

    def test_album_matching_multiple(self) -> None:
        """Test multiple rules applied to an AlbumInfo object."""
        albuminfo = new_albuminfo()
        self._setup_config(
            modify_albuminfo=[
                f"album:'{albuminfo['album']}' album='new album'",
                f"artist:'{albuminfo['artist']}' artist='new artist'",
            ]
        )
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo["album"] == "new album"
        assert albuminfo["artist"] == "new artist"

    def test_album_unmatched(self) -> None:
        """Test rules not applied to an AlbumInfo object."""
        albuminfo = new_albuminfo()
        self._setup_config(modify_albuminfo=["album:'not an album' album='new album'"])
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo["album"] == "album"

    def test_album_noquery(self) -> None:
        """Test that a rule with no query raises an error."""
        self._setup_config(modify_albuminfo=["a=b"])
        albuminfo = new_albuminfo()
        with pytest.raises(UserError, match="no query found"):
            self.plugin.apply_albuminfo_rules(albuminfo)

    def test_album_nomods(self) -> None:
        """Test that a rule with no mods raises an error."""
        self._setup_config(modify_albuminfo=["album:album"])
        albuminfo = new_albuminfo()
        with pytest.raises(UserError, match="no mods found"):
            self.plugin.apply_albuminfo_rules(albuminfo)

    def test_album_noquery_nomods(self) -> None:
        """Test that a rule with no query and no mods raises an error."""
        self._setup_config(modify_albuminfo=[""])
        albuminfo = new_albuminfo()
        with pytest.raises(UserError, match="no query found"):
            self.plugin.apply_albuminfo_rules(albuminfo)

    @pytest.mark.skip("Not implemented: Not sure how to set artists with modify")
    def test_album_multivalue(self) -> None:
        """Test setting a multi-value field on an album."""
        self._setup_config(
            modify_albuminfo=["artists:artist artists='new artist\0another artist'"]
        )
        albuminfo = new_albuminfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo["artists"] == ["new artist", "another artist"]

    def test_album_semicolon_dsv(self) -> None:
        """Test setting a semicolon separated field on an album."""
        self._setup_config(
            modify_albuminfo=["albumtypes::album albumtypes='album; remix; newtype'"]
        )
        albuminfo = new_albuminfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo["albumtypes"] == ["album", "remix", "newtype"]

    def test_album_order_subsequent(self) -> None:
        """Test that rules run in order and can match previous modifications."""
        self._setup_config(
            modify_albuminfo=[
                "album:album album='new album'",
                "album:'new album' album='new album 2'",
            ]
        )
        albuminfo = new_albuminfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo["album"] == "new album 2"

    @pytest.mark.skip("Currently not implemented")
    def test_album_tracks(self) -> None:
        """Test matching against track fields on an AlbumInfo object."""
        self._setup_config(modify_albuminfo=["title:title album='new album'"])
        albuminfo = new_albuminfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo["album"] == "new album"

    def test_track(self) -> None:
        """Test rules applied to a TrackInfo object."""
        self._setup_config(modify_trackinfo=["title:title title='new title'"])
        trackinfo = new_trackinfo()
        assert trackinfo.title == "title"
        self.plugin.apply_trackinfo_rules(trackinfo)
        assert trackinfo.title == "new title"

    def test_multiple(self) -> None:
        """Test rules applied to multiple info objects."""
        self._setup_config(
            modify_albuminfo=["album:album album='new album'"],
            modify_trackinfo=["title:title title='new title'"],
        )
        albuminfo = new_albuminfo()
        trackinfo = new_trackinfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        self.plugin.apply_trackinfo_rules(trackinfo)
        assert albuminfo.album == "new album"
        assert trackinfo.title == "new title"

    def test_dels(self) -> None:
        """Test deleting fields from an AlbumInfo object."""
        self._setup_config(modify_albuminfo=["flex:flex flex!"])
        albuminfo = new_albuminfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert "flex" not in albuminfo

    def test_dels_not_present(self) -> None:
        """Test deletion of a field that isn't present."""
        self._setup_config(modify_albuminfo=["^flex2:flex2 flex2!"])
        albuminfo = new_albuminfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert "flex2" not in albuminfo

    def test_query_none_field(self) -> None:
        """Test matching against a field that is None."""
        self._setup_config(modify_albuminfo=[r"^flex_none::. flex_none='new flex'"])
        albuminfo = new_albuminfo()
        self.plugin.apply_albuminfo_rules(albuminfo)
        assert albuminfo.flex_none == "new flex"

    @pytest.mark.parametrize(
        "field,new_value",
        [
            ("title", "new title"),
            ("album", "new album"),
            ("track_flex", "new flex"),
        ],
    )
    def test_track_matching(self, field: str, new_value: str) -> None:
        """Test rules applied to an TrackInfo object."""
        trackinfo = new_trackinfo()
        value = trackinfo[field]

        if isinstance(value, str):
            query = f"{field}:'{value}'"
        else:
            query = f"{field}:{value}"
        rule = f"{query} {field}='{new_value}'"
        self._setup_config(modify_trackinfo=[rule])

        self.plugin.apply_trackinfo_rules(trackinfo)
        assert (
            trackinfo[field] == new_value
        ), f"field {field} was not set to {new_value} with rule {rule}"
