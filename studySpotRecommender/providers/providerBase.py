from __future__ import annotations

from abc import ABC, abstractmethod

from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.dataModels import SourceRecord


class BaseProvider(ABC):
    name: str

    def __init__(self, config: AppConfig):
        self.config = config

    @abstractmethod
    def fetch(self) -> list[SourceRecord]:
        raise NotImplementedError
