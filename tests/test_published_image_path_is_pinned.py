"""A published image path is a promise, not a mirror of the repo name.

When the repository was renamed to `VoiceStudio`, `docker.yml` derived its
GHCR path from ``${{ github.repository }}`` — so the next build would have
started publishing to ``ghcr.io/debpalash/voicestudio`` while Docker Hub, a
hardcoded literal, stayed exactly where it was. Every user pulling the
documented GHCR path would have kept receiving the last pre-rename image
indefinitely: no error, no warning, a channel that quietly stopped updating.

Renaming a published image is a deliberate migration (publish to both, document
the move, retire the old one). It must never be a side effect of renaming the
repository, which is why the path is pinned and why that is pinned here.
"""

import os

import pytest

yaml = pytest.importorskip("yaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKFLOW = os.path.join(ROOT, ".github", "workflows", "docker.yml")


def _env():
    with open(WORKFLOW, encoding="utf-8") as fh:
        return yaml.safe_load(fh)["env"]


def test_the_ghcr_path_does_not_follow_the_repository_name():
    image = _env()["IMAGE_NAME"]
    assert "github.repository" not in str(image), (
        "IMAGE_NAME derives from the repo name again — renaming the repository "
        "would silently move published images and strand everyone pulling the "
        "documented path"
    )
    assert image == "hidayattubeofficial-ai/voicestudio"


def test_the_two_registries_use_explicit_published_paths():
    # The registries may intentionally use different namespaces/names. What
    # matters is that each path is explicit rather than derived implicitly from
    # the renamed repository.
    env = _env()
    assert str(env["IMAGE_NAME"]) == "hidayattubeofficial-ai/voicestudio"
    assert str(env["DOCKERHUB_IMAGE"]) == "palashdeb/omnivoice-studio"


def test_the_docs_name_the_path_that_is_actually_published():
    """Docs drift here is invisible: a wrong pull command fails only for users."""
    env = _env()
    published = f"ghcr.io/{env['IMAGE_NAME']}"
    for rel in ("docs/install/docker.md", "deploy/dockerhub-overview.md"):
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        if "ghcr.io/" not in text:
            continue
        assert published in text, f"{rel} does not document {published}"
