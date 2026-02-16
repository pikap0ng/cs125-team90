from studySpotRecommender.appConfig import AppConfig
from studySpotRecommender.ingestionPipeline import IngestionPipeline


class _FailingProvider:
    name = "failing"

    def fetch(self):
        raise RuntimeError("boom")


class _StaticProvider:
    name = "static"

    def __init__(self, records):
        self._records = records

    def fetch(self):
        return self._records


def testProviderFilteringByName(tmp_path) -> None:
    config = AppConfig(sqlitePath=str(tmp_path / "spots.db"), enabledProviders=("osm", "uci"))
    pipeline = IngestionPipeline(config)

    assert [provider.name for provider in pipeline.providers] == ["uci", "osm"]


def testCollectSkipsProviderExceptions(tmp_path) -> None:
    config = AppConfig(sqlitePath=str(tmp_path / "spots.db"), verbose=True)
    pipeline = IngestionPipeline(config)
    pipeline.providers = [_FailingProvider(), _StaticProvider([])]

    assert pipeline.collect() == []
