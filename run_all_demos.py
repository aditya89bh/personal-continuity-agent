"""Run all available Personal Continuity Agent demos.

Run from repository root:

    python run_all_demos.py
"""

from __future__ import annotations

from examples.goal_drift_demo.run_demo import main as run_goal_drift_demo


def main() -> None:
    print("Running Personal Continuity Agent demos")
    print("=" * 52)
    print()
    run_goal_drift_demo()


if __name__ == "__main__":
    main()
