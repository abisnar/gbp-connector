# Releasing

This project follows [Semantic Versioning](https://semver.org/). Releases are
driven by git tags — there is no version string to bump by hand.

## How a release happens

1. You push a tag matching `v*.*.*` to `main`.
2. [`.github/workflows/release.yml`](../.github/workflows/release.yml) fires:
   - `build` — runs `python -m build`, producing an sdist and a wheel whose
     version is derived from the tag by [`hatch-vcs`](https://github.com/ofek/hatch-vcs).
     Verifies the built filename matches the tag (no version drift).
   - `publish-pypi` — uploads to PyPI via **OIDC Trusted Publishing**. No
     API token is stored anywhere; PyPI verifies the request came from
     GitHub Actions running this workflow on this repository.
   - `github-release` — attaches the same wheel + sdist to a new
     [GitHub Release](https://github.com/abisnar/gbp-connector/releases),
     using the matching `## [X.Y.Z]` section of [`CHANGELOG.md`](../CHANGELOG.md)
     as the release notes.

## One-time PyPI setup (required before the first release)

The very first PyPI publish needs you to register a **Pending Publisher** so
PyPI knows to trust this repo's release workflow. After that, every future
release just works.

1. Create a PyPI account at <https://pypi.org/account/register/> (if you
   don't already have one) and enable 2FA.
2. Open <https://pypi.org/manage/account/publishing/>.
3. Under **Add a new pending publisher**, fill in **exactly**:

   | Field                  | Value                              |
   |------------------------|------------------------------------|
   | PyPI Project Name      | `gbp-connector`                    |
   | Owner                  | `abisnar`                          |
   | Repository name        | `gbp-connector`                    |
   | Workflow name          | `release.yml`                      |
   | Environment name       | `pypi`                             |

4. Click **Add**. (Nothing happens on PyPI until you push a tag.)

That's it. The `environment: pypi` line in `release.yml` matches the
Environment name above; the `id-token: write` permission on the publish job
gives the runner an OIDC token that PyPI verifies against the publisher config.

> Want a manual-approval gate? In GitHub repo Settings → Environments →
> `pypi`, add yourself as a required reviewer. The publish job will then wait
> for you to click "Approve" before uploading to PyPI.

## Cutting a release

```bash
# 1. Move the [Unreleased] section in CHANGELOG.md under a new heading.
#    The header must be `## [0.1.0] - YYYY-MM-DD` for the workflow to find
#    the notes and use them as the GitHub Release body.
vim CHANGELOG.md
git commit -am "changelog: 0.1.0"

# 2. Tag and push. The tag triggers .github/workflows/release.yml.
git tag v0.1.0
git push origin main --tags
```

Within a minute or two the run shows up in
[Actions → Release](https://github.com/abisnar/gbp-connector/actions/workflows/release.yml).
When it goes green the package is live at
<https://pypi.org/project/gbp-connector/>.

## Consuming a release in another project

Pin to an exact version (recommended for production):

```toml
# pyproject.toml
[project]
dependencies = [
    "gbp-connector==0.1.0",
]
```

Allow patches but not minor or major bumps:

```toml
dependencies = ["gbp-connector~=0.1.0"]   # >=0.1.0, <0.2.0
```

Pre-release / unpublished testing — install straight from a tag:

```bash
pip install git+https://github.com/abisnar/gbp-connector@v0.1.0
```

## Version policy

Pre-1.0 (we are here):

- **0.x.0** may include breaking API changes — call them out at the top of
  the CHANGELOG entry under `### Breaking`.
- **0.x.y** is bug fixes and additive changes only.

After 1.0:

- **major** = backwards-incompatible API change
- **minor** = backwards-compatible addition
- **patch** = backwards-compatible fix

What counts as the "public API" is anything exported by
`gbp_connector/__init__.py` — see the `__all__` list there.

## Yanking a bad release

If a published version breaks consumers, do not delete it (deletion is
discouraged on PyPI and confuses caches). Instead:

```bash
# On https://pypi.org/manage/project/gbp-connector/releases/
# click "Options → Yank" on the bad version, then publish a fixed version.
```

Yanked versions stay resolvable for `==` pins (so existing builds don't
break) but new `pip install gbp-connector` resolutions will skip them.
