import argparse
from datetime import date, timedelta
from uuid import uuid4

from .application import (
    IssueLoan,
    IssueLoanCommand,
    RequestLoan,
    RequestLoanCommand,
    ReturnLoan,
    ReturnLoanCommand,
)
from .domain import Borrower, BorrowerRole, Projector, ProjectorType
from .infrastructure import (
    InMemoryBorrowerRepository,
    InMemoryProjectorRepository,
)
from .presentation import ConsolePresenter


def run_demo() -> list[str]:
    borrower = Borrower(uuid4(), BorrowerRole.STAFF)
    projector = Projector(uuid4(), ProjectorType.STANDARD)
    borrower_repository = InMemoryBorrowerRepository((borrower,))
    projector_repository = InMemoryProjectorRepository((projector,))

    start_date = date.today()
    requested = RequestLoan(
        borrower_repository,
        projector_repository,
    ).execute(
        RequestLoanCommand(
            borrower.borrower_id,
            projector.projector_id,
            start_date,
            start_date + timedelta(days=3),
        )
    )
    issued = IssueLoan(borrower_repository, projector_repository).execute(
        IssueLoanCommand(borrower.borrower_id, requested.loan_id)
    )
    returned = ReturnLoan(borrower_repository, projector_repository).execute(
        ReturnLoanCommand(borrower.borrower_id, requested.loan_id)
    )
    return [
        ConsolePresenter.render_loan(requested),
        ConsolePresenter.render_loan(issued),
        ConsolePresenter.render_loan(returned),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Projector borrowing system")
    parser.add_argument(
        "command",
        choices=("demo",),
        help="workflow to run",
    )
    parser.parse_args(argv)

    for line in run_demo():
        print(line)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
