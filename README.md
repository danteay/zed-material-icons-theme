# zed-material-icons-theme

An icon theme for the [Zed](https://zed.dev) editor that combines the
[Material Icon Theme](https://github.com/material-extensions/vscode-material-icon-theme)
file and folder icons with the official [Pkl](https://pkl-lang.org) logo on
Pkl files (`*.pkl`, `*.pcf`, `PklProject`, `PklProject.deps.json`).

It ships two themes:

- **Material Icons** — for dark UI themes
- **Material Icons Light** — for light UI themes, with the Material light icon
  variants

Coverage includes ~1,400 file extensions, ~4,600 well-known file names, and
per-name folder icons (`src`, `tests`, `docs`, `node_modules`, ...). File
types without a Material mapping fall back to the generic Material file icon.

It pairs well with the [pkl-lang](https://github.com/danteay/pkl-zed)
language extension, which provides highlighting, snippets, live evaluation,
and pkl-lsp support. Zed requires icon themes to be published as separate
extensions from language support, which is why this lives in its own
repository.

## Usage

Install the `material-icons` extension, then select the icon theme with the
`icon theme selector: toggle` command or in your `settings.json`:

```json
{
  "icon_theme": "Material Icons"
}
```

## Regenerating from upstream

The theme JSON and the SVGs in `icons/material/` are generated from the
[`material-icon-theme`](https://www.npmjs.com/package/material-icon-theme)
npm package by [`scripts/generate_icon_theme.py`](scripts/generate_icon_theme.py).
To pull in a newer upstream release, bump `UPSTREAM_VERSION` in the script
and run:

```sh
python3 scripts/generate_icon_theme.py
```

The script documents the VS Code → Zed conversion differences (case
sensitivity, path-pattern keys, language-id mappings).

## Attribution

- Material icons and mappings are from
  [material-extensions/vscode-material-icon-theme](https://github.com/material-extensions/vscode-material-icon-theme)
  (v5.36.1), licensed under the MIT License — see
  [licenses/material-icon-theme.LICENSE](licenses/material-icon-theme.LICENSE).
- The Pkl logo is sourced from
  [apple/pkl-vscode](https://github.com/apple/pkl-vscode) (`img/icon.svg`),
  which is licensed under the Apache License 2.0. The Pkl name and logo belong
  to Apple Inc.

## License

Apache-2.0 — see [LICENSE](LICENSE).
