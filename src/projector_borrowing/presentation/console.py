import json

from ..application import LoanResult


class ConsolePresenter:
    @staticmethod
    def render_loan(result: LoanResult) -> str:
        return json.dumps(
            {
                "loan_id": str(result.loan_id),
                "projector_id": str(result.projector_id),
                "status": result.status.value,
                "start_date": result.start_date.isoformat(),
                "due_date": result.due_date.isoformat(),
            },
            sort_keys=True,
        )
