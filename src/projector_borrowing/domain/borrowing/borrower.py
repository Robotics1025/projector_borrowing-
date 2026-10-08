from uuid  import UUID, uuid4
from  .enums  import  BorrowerRole

class Borrower:
  def __init__(self, borrower_id: UUID, role: BorrowerRole):
      if not isinstance(borrower_id, UUID):
          raise TypeError("borrower_id must be UUID")
      if not isinstance(role, BorrowerRole):
          raise TypeError("role must be BorrowerRole")
      self._borrower_id = borrower_id
      self.role = role
      self._loans=[]
      self._event=[]


  def  get_borrower_id(self) -> UUID:
      return self._borrower_id
  def get_role(self) -> BorrowerRole:
      return self.role



