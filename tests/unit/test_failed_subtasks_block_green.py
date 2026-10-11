from unittest.mock import MagicMock

from agent.agents.reviewer import EvaluatorValidator
from agent.evaluation.evaluator import EvalResult


def _validator_with_failed_subtasks(failed_subtasks):
    orch = MagicMock()
    orch.frame.metadata = {"failed_subtasks": failed_subtasks}
    orch._missing_requested_files.return_value = []
    orch._no_progress_abort = False
    orch._mutations = 1
    return EvaluatorValidator(orch)


def test_failed_planner_editor_subtask_blocks_green_result():
    validator = _validator_with_failed_subtasks(["styles.css"])
    result = EvalResult(
        passed=True,
        summary="No tests found; sources compile cleanly",
        ran_tests=False,
    )

    checked = validator.validate(result)

    assert checked.passed is False
    assert "styles.css" in checked.summary
    assert "not verified" in checked.summary


def test_no_failed_planner_editor_subtasks_does_not_block_green_result():
    validator = _validator_with_failed_subtasks([])
    result = EvalResult(
        passed=True,
        summary="Tests passed",
        ran_tests=True,
    )

    checked = validator.validate(result)

    assert checked.passed is True
    assert checked.summary == "Tests passed"
