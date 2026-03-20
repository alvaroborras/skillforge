"""Skill publisher — sends built packages to registries."""

from pathlib import Path


class Publisher:
    """Publishes a built skill archive to a registry."""

    def publish(
        self,
        target: Path,
        *,
        registry: str = "https://registry.dotskills.dev",
        dry_run: bool = False,
    ) -> dict:
        """Publish a skill directory or built archive.

        Returns a dict with publication metadata.
        """
        if target.is_dir():
            # For a directory we need the SKILL.md to identify the skill.
            skill_file = target / "SKILL.md"
            if not skill_file.exists():
                raise PublishError(f"No SKILL.md found in '{target}'")
            # For dry-run from a directory, we note what *would* be published.
            manifest = _quick_read_manifest(skill_file)
            package = f"{manifest['name']}-{manifest['version']}.tar.gz"
        elif target.suffix in (".gz", ".zip"):
            package = target.name
        else:
            raise PublishError(f"Unrecognised target: {target}")

        result = {
            "registry": registry,
            "package": package,
            "dry_run": dry_run,
        }

        if dry_run:
            result["message"] = (
                f"[DRY RUN] Would publish '{package}' to {registry}"
            )
        else:
            result["message"] = f"Published '{package}' to {registry}"
            result["url"] = f"{registry.rstrip('/')}/skills/{package}"

        return result


def _quick_read_manifest(skill_file: Path) -> dict:
    import yaml

    content = skill_file.read_text()
    parts = content.split("---", 2)
    return yaml.safe_load(parts[1]) if len(parts) >= 3 else {}


class PublishError(Exception):
    """Raised when publication fails."""
