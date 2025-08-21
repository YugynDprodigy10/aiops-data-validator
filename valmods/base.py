
from abc import ABC, abstractmethod
from typing import List
from core.models import ValidationIssue   

class BaseValidator(ABC):
    @abstractmethod
    def validate(self, file_path: str) -> List[ValidationIssue]:
        raise NotImplementedError
