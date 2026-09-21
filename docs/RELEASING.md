# Release checklist

Publish from a clean public checkout. Never build public artifacts from a
private account workspace or replace an existing published tag or artifact.

1. Update the version in `pyproject.toml`, `src/legends_dataforseo/__init__.py`,
   and `src/legends_dataforseo/routes.json`; update the changelog and install URLs.
2. Use an empty `dist/` directory for the new build. Keep older release artifacts
   separately if needed.
3. Run the offline verification below. Inspect source and archive contents for
   private paths, credentials, account data, and unrelated files. The automated
   scan is a bounded pattern check, not a complete secrets certification.
4. Commit the reviewed source and wait for every cross-platform CI job to pass.
5. Tag that exact commit. Create a GitHub release using a notes file and attach
   the wheel, sdist, and `SHA256SUMS.txt`. Include the full source commit, a
   working install command, meaningful changes, and compatibility details.
6. Download the published assets, verify their hashes, and install the published
   wheel and source ZIP into clean environments. Verify the tag's commit and
   release state from GitHub.

```sh
python -m pip install -e ".[dev]"
python -m pytest
python examples/offline.py
python -m build
python -m twine check dist/*
python scripts/audit_public.py
python scripts/smoke_wheel.py
python scripts/release_checksums.py
```

The CI workflow uploads its Linux/Python 3.13 distribution for inspection.
Release publication remains an explicit maintainer action. Paid requests and
provider credentials are never required by CI or the release build.

## Presentation assets

The README uses `assets/banner.webp`; `assets/banner.png` preserves the full
render. `assets/social-preview.png` is a separate 1280 × 640 social card.
The source distribution includes these assets so the README's image paths resolve.
The wheel contains the Python package, license, and package metadata; full guides
and examples are in the source distribution and repository.

To configure a social card, upload the PNG through the repository's Settings →
General → Social preview. Committing it does not set that GitHub property.
Verify the saved image after upload. Preserve the supplied font's license;
font binaries are not included in this repository.
