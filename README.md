# ImportModifyInfo Plugin for Beets

[![PyPI](https://img.shields.io/pypi/v/beets-importmodifyinfo.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/beets-importmodifyinfo.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/beets-importmodifyinfo)][pypi status]
[![License](https://img.shields.io/pypi/l/beets-importmodifyinfo)][license]

[![Read the documentation at https://beets-importmodifyinfo.readthedocs.io/](https://img.shields.io/readthedocs/beets-importmodifyinfo/latest.svg?label=Read%20the%20Docs)][read the docs]
[![The Ethical Source Principles](https://img.shields.io/badge/ethical-source-%23bb8c3c?labelColor=393162)][ethical source]
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)][contributor covenant]
[![Tests](https://github.com/kergoth/beets-importmodifyinfo/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/kergoth/beets-importmodifyinfo/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Ruff codestyle][ruff badge]][ruff project]

[pypi status]: https://pypi.org/project/beets-importmodifyinfo/
[ethical source]: https://ethicalsource.dev/principles/
[read the docs]: https://beets-importmodifyinfo.readthedocs.io/
[tests]: https://github.com/kergoth/beets-importmodifyinfo/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/kergoth/beets-importmodifyinfo
[pre-commit]: https://github.com/pre-commit/pre-commit
[ruff badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
[ruff project]: https://github.com/charliermarsh/ruff

The [ImportModifyInfo](https://github.com/kergoth/beets-importmodifyinfo) Plugin for [Beets][] applies modifications to received metadata before import. This is largely intended to correct issues with imported metadata which would otherwise be lost on running `mbsync`. This plugin is inspired by the [ImportReplace][] Plugin and my old [modifyonimport][] plugin, but I found that those modifications would often be lost when running `mbsync` or equivalent.

## Installation

As the beets documentation describes in [Other plugins][], to use an external plugin like this one, there are two options for installation:

- Make sure it’s in the Python path (known as `sys.path` to developers). This just means the plugin has to be installed on your system (e.g., with a setup.py script or a command like pip or easy_install). For example, `pip install beets-importmodifyinfo`.
- Set the pluginpath config variable to point to the directory containing the plugin. (See Configuring) This would require cloning or otherwise downloading this [repository](https://github.com/kergoth/beets-stylize) before adding to the pluginpath.

## Configuring

First, enable the `importmodifyinfo` plugin (see [Using Plugins][]).

To configure the plugin, make a `importmodifyinfo:` section in your configuration file. Sections may be added for `modify_albuminfo` and `modify_trackinfo`, each of which is a list of strings as you would supply to the `modify` command. For example:

```yaml
importmodifyinfo:
  modify_albuminfo:
    - album:'some album' albumtype=ep albumtypes='ep; remix'
  modify_trackinfo:
    - album:'some album' title:'some title' title='some other title'
```

## Using

There is no direct usage other than the configuration, as these modifications are automatically applied during the import or sync process.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_ImportModifyInfo Plugin for Beets_ is free and open source software. This software prioritizes meeting the criteria of the [Ethical Source Principles][ethical source], though it does not currently utilize an [ethical source license][].

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project is a plugin for the [beets][] project, and would not exist without that fantastic project.
This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/kergoth/beets-importmodifyinfo/issues
[beets]: https://beets.readthedocs.io/en/stable/index.html
[other plugins]: https://beets.readthedocs.io/en/stable/plugins/index.html#other-plugins
[using plugins]: https://beets.readthedocs.io/en/stable/plugins/index.html#using-plugins
[ethical source license]: https://ethicalsource.dev/faq/#what-is-an-ethical-license-for-open-source
[importreplace]: https://github.com/edgars-supe/beets-importreplace
[modifyonimport]: https://github.com/kergoth/beets-kergoth/blob/master/docs/modifyonimport.rst

<!-- github-only -->

[license]: ./LICENSE
[contributor guide]: ./CONTRIBUTING.md
[contributor covenant]: ./CODE_OF_CONDUCT.md
