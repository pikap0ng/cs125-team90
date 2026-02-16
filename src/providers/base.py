from __future__ import annotations

from abc import ABC, abstractmethod

from study_spot_recommender.Config import AppConfig
from study_spot_recommender.Models import SourceRecord


class BaseProvider(ABC):
    name: str

    def __init__(self, config: AppConfig):
        self.config = config

    @abstractmethod
    def fetch(self) -> list[SourceRecord]:
        raise NotImplementedError
