import ast
from importlib.util import resolve_name
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_NAME = "projector_borrowing"
SOURCE_ROOT = PROJECT_ROOT / "src" / PACKAGE_NAME


def module_context(path: Path) -> tuple[str, str]:
    relative_path = path.relative_to(PROJECT_ROOT / "src").with_suffix("")
    module_name = ".".join(relative_path.parts)
    if path.name == "__init__.py":
        package = module_name.removesuffix(".__init__")
    else:
        package = module_name.rpartition(".")[0]
    return module_name, package


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    _, package = module_context(path)

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = resolve_name("." * node.level + module, package)
            imports.add(module)
            for alias in node.names:
                if alias.name != "*":
                    imports.add(f"{module}.{alias.name}")
    return imports


@pytest.mark.parametrize(
    ("layer", "forbidden_layers"),
    [
        ("domain", {"application", "infrastructure", "presentation"}),
        ("application", {"infrastructure", "presentation"}),
        ("infrastructure", {"presentation"}),
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
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)} "
                        f"imports forbidden module {imported}"
                    )

    assert not violations, (
        "Architecture dependency violations:\n" + "\n".join(violations)
    )
