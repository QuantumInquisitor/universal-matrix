from abc import ABC, abstractmethod

class BaseHardwareDriver(ABC):
    @abstractmethod
    def initialize() -> bool:
        pass

    @abstractmethod
    def get_status(self) -> dict:
        pass

