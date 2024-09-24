"""ImportModifyInfo Plugin for Beets."""

import shlex
from typing import Optional

from beets.autotag import _apply_metadata
from beets.autotag import apply_item_metadata
from beets.autotag.hooks import AlbumInfo
from beets.autotag.hooks import TrackInfo
from beets.library import Album
from beets.library import Item
from beets.library import parse_query_parts
from beets.plugins import BeetsPlugin  # type: ignore
from beets.ui import UserError
from beets.ui import decargs
from beets.ui.commands import modify_parse_args
from beets.util import as_string
from beets.util import functemplate


class ImportModifyInfoPlugin(BeetsPlugin):  # type: ignore
    """ImportModifyInfo Plugin for Beets."""

    def __init__(self, name: Optional[str] = "importmodifyinfo") -> None:
        super().__init__(name)
        self.config.add(
            {"enabled": True, "modify_iteminfo": [], "modify_albuminfo": []}
        )
        self.item_rules = self.album_rules = None

        if self.config["enabled"].get(bool):
            self.register_listener("trackinfo_received", self.apply_trackinfo_rules)
            self.register_listener("albuminfo_received", self.apply_albuminfo_rules)

    def set_rules(self) -> None:
        """Set rules from configuration."""
        if self.item_rules is None:
            item_modifies = self.config["modify_iteminfo"].get(list)
            self.item_rules = self.get_modifies(item_modifies, Item, "modify_iteminfo")
        if self.album_rules is None:
            album_modifies = self.config["modify_albuminfo"].get(list)
            self.album_rules = self.get_modifies(
                album_modifies, Album, "modify_albuminfo"
            )

    def get_modifies(self, items, model_cls, context):
        """Parse modify items from configuration."""
        modifies = []
        for modify in items:
            query, mods, dels = self.parse_modify(modify)
            if not query:
                raise UserError(
                    f"importmodifyinfo.{context}: no query found in entry {modify}"
                )
            elif not mods and not dels:
                raise UserError(
                    f"importmodifyinfo.{context}: no modifications found in entry {modify}"
                )
            dbquery, _ = parse_query_parts(query, model_cls)
            modifies.append((modify, dbquery, mods, dels))
        return modifies

    def parse_modify(self, modify):
        """Parse modify string into query, mods, and dels."""
        modify = as_string(modify)
        args = shlex.split(modify)
        query, mods, dels = modify_parse_args(decargs(args))
        return query, mods, dels

    def apply_albuminfo_rules(self, info: AlbumInfo) -> None:
        """Apply rules for album information from the importer."""
        self.set_rules()

        album = Album()
        apply_album_metadata(info, album)
        self.process_rules(self.album_rules, info, album, Album)

    def apply_trackinfo_rules(self, info: TrackInfo) -> None:
        """Apply rules for track information from the importer."""
        self.set_rules()

        item = Item()
        apply_item_metadata(item, info)
        self.process_rules(self.item_rules, info, item, Item)

    def process_rules(self, rules, info, obj, model_cls):
        """Process rules for info on an object."""
        for _, query, mods, dels in rules:
            templates = {
                key: functemplate.template(value) for key, value in mods.items()
            }
            obj_mods = {
                key: model_cls._parse(key, obj.evaluate_template(templates[key]))
                for key in mods.keys()
            }
            if query.match(obj):
                for field in dels:
                    try:
                        del info[field]
                    except KeyError:
                        pass

                for field, value in obj_mods.items():
                    if value is not None:
                        # Indirect to deal with type conversions
                        obj[field] = value
                        info[field] = obj[field]


def format_item(info):
    """Format an Info item for display."""
    return f"{info.artist} - {info.album} ({info.album_id})"


def apply_album_metadata(album_info: AlbumInfo, album: Album):
    """Set the album's metadata to match the AlbumInfo object."""
    album.artist = album_info.artist
    album.artists = album_info.artists
    album.artist_sort = album_info.artist_sort
    album.artists_sort = album_info.artists_sort
    album.artist_credit = album_info.artist_credit
    album.artists_credit = album_info.artists_credit

    _apply_metadata(album_info, album)
