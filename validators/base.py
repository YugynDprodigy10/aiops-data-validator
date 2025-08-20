
from abc import ABC, abstractmethod
from typing import List
from core.models import ValidationIssue   # <-- change this line

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, file_path: str) -> List[ValidationIssue]:
        raise NotImplementedError
