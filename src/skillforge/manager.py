"""SkillManager — orchestrates scanner, validator, builder, publisher, and init."""

from pathlib import Path

from jinja2 import Environment, PackageLoader

from skillforge.builder import Builder
from skillforge.publisher import Publisher
from skillforge.scanner import Scanner
from skillforge.validator import Validator


class SkillManager:
    """Top-level orchestrator that wires together all skillforge subsystems."""

    def __init__(self) -> None:
        self.validator = Validator()
        self.scanner = Scanner(self.validator)
        self.builder = Builder(self.validator)
        self.publisher = Publisher()
        self._jinja = Environment(
            loader=PackageLoader("skillforge", "templates"),
            autoescape=False,
        )

    def scan(self, path: Path) -> list:
        return self.scanner.scan(path)

    def validate(self, path: Path) -> list:
        if (path / "SKILL.md").exists():
            result = self.validator.validate(path)
            manifest = self._try_parse(path)
            return [(path, manifest, result)]
        return self.scanner.scan(path)

    def build(self, skill_dir: Path, output_dir: Path, fmt: str = "tar.gz"):
        return self.builder.build(skill_dir, output_dir, fmt)

    def publish(self, target: Path, registry: str, dry_run: bool = False) -> dict:
        return self.publisher.publish(target, registry=registry, dry_run=dry_run)

    def init_skill(self, name: str, base_dir: Path, template: str = "default") -> Path:
        skill_dir = base_dir / name
        if skill_dir.exists():
            raise FileExistsError(f"'{skill_dir}' already exists")

        skill_dir.mkdir(parents=True)

        tpl = self._jinja.get_template("init/SKILL.md.j2")
        rendered = tpl.render(name=name, description=f"{name} skill")

        (skill_dir / "SKILL.md").write_text(rendered)
        return skill_dir

    @staticmethod
    def _try_parse(skill_dir: Path):
        try:
            import yaml

            from skillforge.models import SkillManifest

            content = (skill_dir / "SKILL.md").read_text()
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None
            return SkillManifest(**yaml.safe_load(parts[1]))
        except Exception:
            return None
