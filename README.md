# pkl-zed-icons

An icon theme for the [Zed](https://zed.dev) editor that shows the official
[Pkl](https://pkl-lang.org) logo on Pkl files: `*.pkl`, `*.pcf`, and
`PklProject`.

All other file types keep your regular icons — Zed merges partial icon themes
over its defaults, so this theme only overrides the Pkl file types.

It pairs well with the [pkl-lang](https://github.com/danteay/pkl-zed)
language extension, which provides highlighting, snippets, live evaluation,
and pkl-lsp support. Zed requires icon themes to be published as separate
extensions from language support, which is why this lives in its own
repository.

## Usage

Install the `pkl-icons` extension, then select the icon theme with the
`icon theme selector: toggle` command or in your `settings.json`:

```json
{
  "icon_theme": "Pkl Icons"
}
```

## Attribution

The Pkl logo is sourced from
[apple/pkl-vscode](https://github.com/apple/pkl-vscode) (`img/icon.svg`),
which is licensed under the Apache License 2.0. The Pkl name and logo belong
to Apple Inc.

## License

Apache-2.0 — see [LICENSE](LICENSE).
