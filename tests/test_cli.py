import json

from projector_borrowing.__main__ import main, run_demo


def test_demo_returns_complete_workflow() -> None:
    output = [json.loads(line) for line in run_demo()]
    assert [item["status"] for item in output] == [
        "PENDING",
        "ACTIVE",
        "RETURNED",
    ]


def test_main_prints_demo(capsys) -> None:
    assert main(["demo"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 3
