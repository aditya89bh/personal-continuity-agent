from continuity_core.cli import build_parser


def test_cli_add_event_parser() -> None:
    parser = build_parser()

    args = parser.parse_args(
        [
            "add-event",
            "--content",
            "Started continuity architecture work",
            "--event-type",
            "goal",
            "--tag",
            "continuity",
            "--importance",
            "0.9",
        ]
    )

    assert args.command == "add-event"
    assert args.content == "Started continuity architecture work"
    assert args.event_type == "goal"
    assert args.tag == ["continuity"]
    assert args.importance == 0.9


def test_cli_list_events_parser() -> None:
    parser = build_parser()

    args = parser.parse_args(["list-events"])

    assert args.command == "list-events"


def test_cli_reflect_parser() -> None:
    parser = build_parser()

    args = parser.parse_args(["reflect"])

    assert args.command == "reflect"
