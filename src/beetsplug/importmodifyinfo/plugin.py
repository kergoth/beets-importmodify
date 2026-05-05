"""ImportModifyInfo Plugin for Beets."""

import shlex

from beets.autotag.hooks import AlbumInfo
from beets.autotag.hooks import TrackInfo
from beets.dbcore import Model
from beets.dbcore import Query
from beets.library import Album
from beets.library import Item
from beets.library import parse_query_parts
from beets.plugins import BeetsPlugin
from beets.ui import UserError
from beets.ui.commands.modify import modify_parse_args
from beets.util import as_string
from beets.util import functemplate


Mods = dict[str, str]
Dels = list[str]
Rules = list[tuple[str, Query, Mods, Dels]]


class ImportModifyInfoPlugin(BeetsPlugin):
    """ImportModifyInfo Plugin for Beets."""

    def __init__(self, name: str | None = "importmodifyinfo") -> None:
        super().__init__(name)
        self.config.add(
            {"enabled": True, "modify_trackinfo": [], "modify_albuminfo": []}
        )
        self.configured = False

        if self.config["enabled"].get(bool):
            self.register_listener("trackinfo_received", self.apply_trackinfo_rules)
            self.register_listener("albuminfo_received", self.apply_albuminfo_rules)

    def set_rules(self) -> None:
        """Set rules from configuration."""
        if not self.configured:
            item_modifies: list[str] = self.config["modify_trackinfo"].get(list)
            self.item_rules = self.get_modifies(item_modifies, Item, "modify_trackinfo")

            album_modifies: list[str] = self.config["modify_albuminfo"].get(list)
            self.album_rules = self.get_modifies(
                album_modifies, Album, "modify_albuminfo"
            )
            self.configured = True

    def get_modifies(
        self, items: list[str], model_cls: type[Model], context: str
    ) -> Rules:
        """Parse modify items from configuration."""
        modifies = []
        for modify in items:
            query, mods, dels = self.parse_modify(modify, model_cls is Album)
            if not query:
                raise UserError(
                    f"importmodifyinfo.{context}: no query found in entry {modify}"
                )
            elif not mods and not dels:
                raise UserError(
                    f"importmodifyinfo.{context}: no mods found in entry {modify}"
                )
            dbquery, _ = parse_query_parts(query, model_cls)  # type: ignore[no-untyped-call]
            modifies.append((modify, dbquery, mods, dels))
        return modifies

    def parse_modify(self, modify: str, is_album: bool) -> tuple[list[str], Mods, Dels]:
        """Parse modify string into query, mods, and dels."""
        modify = as_string(modify)
        args = shlex.split(modify)
        query, mods, dels = modify_parse_args(args, is_album=is_album)
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
        item.update(info.item_data)  # type: ignore[no-untyped-call]
        self.process_rules(self.item_rules, info, item, Item)

    def process_rules(
        self,
        rules: Rules,
        info: TrackInfo | AlbumInfo,
        obj: Item | Album,
        model_cls: type[Model],
    ) -> None:
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
                    # Indirect to deal with type conversions, and allow for later
                    # rules to match the modified values.
                    obj[field] = value
                    info[field] = obj[field]


def apply_album_metadata(album_info: AlbumInfo, album: Album) -> None:
    """Set the album's metadata to match the AlbumInfo object."""
    album.artist = album_info.artist
    album.artists = album_info.artists
    album.artist_sort = album_info.artist_sort
    album.artists_sort = album_info.artists_sort
    album.artist_credit = album_info.artist_credit
    album.artists_credit = album_info.artists_credit
    album.year = album_info.year

    for field, value in album_info.items():
        if value is None:
            continue
        album[field] = value
