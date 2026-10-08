from enum import Enum


class LoanStatus(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    CANCELLED = "CANCELLED"
