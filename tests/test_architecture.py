import ast
from importlib.util import resolve_name
from pathlib import Path

import pytest


SOURCE_ROOT = Path("src/projector_borrowing")


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    relative_path = path.relative_to("src").with_suffix("")
    parts = relative_path.parts
    package = ".".join(parts[:-1])
    if path.name == "__init__.py":
        package = ".".join(parts[:-1])

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = resolve_name("." * node.level + module, package)
            imports.add(module)
    return imports


@pytest.mark.parametrize(
    ("layer", "forbidden_layers"),
    [
        ("domain", {"application", "infrastructure", "presentation"}),
        ("application", {"infrastructure", "presentation"}),
        ("infrastructure", {"application", "presentation"}),
        ("presentation", {"domain", "infrastructure"}),
    ],
)
def test_dependencies_point_inward(
    layer: str,
    forbidden_layers: set[str],
) -> None:
    violations: list[str] = []
    for path in (SOURCE_ROOT / layer).rglob("*.py"):
        for imported in imported_modules(path):
            for forbidden in forbidden_layers:
                prefix = f"projector_borrowing.{forbidden}"
                if imported == prefix or imported.startswith(f"{prefix}."):
                    violations.append(f"{path}: imports {imported}")

    assert violations == []
