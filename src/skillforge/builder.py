"""Package builder — produces deterministic tar.gz or zip archives."""

import hashlib
import io
import tarfile
import zipfile
from pathlib import Path

from skillforge.models import BuildArtifact, SkillManifest
from skillforge.validator import Validator


class Builder:
    """Builds distributable skill archive from a skill directory."""

    def __init__(self, validator: Validator | None = None) -> None:
        self._validator = validator or Validator()

    def build(
        self, skill_dir: Path, output_dir: Path, fmt: str = "tar.gz"
    ) -> BuildArtifact:
        result = self._validator.validate(skill_dir)
        if not result.valid:
            error_msgs = "; ".join(e.message for e in result.errors)
            raise BuildError(f"Validation failed: {error_msgs}")

        manifest = self._load_manifest(skill_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{manifest.name}-{manifest.version}.{fmt}"
        archive_path = output_dir / filename

        if fmt == "tar.gz":
            archive_path, checksum, size = self._build_tar(skill_dir, manifest, archive_path)
        elif fmt == "zip":
            archive_path, checksum, size = self._build_zip(skill_dir, manifest, archive_path)
        else:
            raise BuildError(f"Unsupported format: {fmt}")

        return BuildArtifact(
            manifest=manifest,
            archive_path=archive_path,
            checksum=checksum,
            size_bytes=size,
        )

    # ----------------------------------------------------------------- helpers

    @staticmethod
    def _load_manifest(skill_dir: Path) -> SkillManifest:
        import yaml

        content = (skill_dir / "SKILL.md").read_text()
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise BuildError("No valid YAML front matter in SKILL.md")
        data = yaml.safe_load(parts[1])
        if not isinstance(data, dict):
            raise BuildError("Front matter is not a YAML mapping")
        try:
            return SkillManifest(**data)
        except Exception as exc:
            raise BuildError(f"Failed to parse manifest: {exc}")

    @staticmethod
    def _files_to_pack(skill_dir: Path, manifest: SkillManifest) -> list[Path]:
        """Return sorted list of relative paths to include in the archive."""
        paths = {Path(manifest.skill_file)}
        for asset in manifest.asset_paths:
            full = skill_dir / asset
            if full.is_dir():
                paths.update(
                    p.relative_to(skill_dir)
                    for p in full.rglob("*")
                    if p.is_file()
                )
            else:
                paths.add(asset)
        return sorted(paths)

    def _build_tar(
        self, skill_dir: Path, manifest: SkillManifest, archive_path: Path
    ) -> tuple[Path, str, int]:
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            for rel in self._files_to_pack(skill_dir, manifest):
                tar.add(
                    skill_dir / rel,
                    arcname=f"{manifest.name}/{rel}",
                )
        payload = buf.getvalue()
        archive_path.write_bytes(payload)
        return archive_path, _sha256(payload), len(payload)

    def _build_zip(
        self, skill_dir: Path, manifest: SkillManifest, archive_path: Path
    ) -> tuple[Path, str, int]:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for rel in self._files_to_pack(skill_dir, manifest):
                zf.write(
                    skill_dir / rel,
                    arcname=f"{manifest.name}/{rel}",
                )
        payload = buf.getvalue()
        archive_path.write_bytes(payload)
        return archive_path, _sha256(payload), len(payload)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class BuildError(Exception):
    """Raised when a build cannot proceed."""
