from abc import ABC
import pytest


def test_repository_interfaces_are_importable():
    """アーキテクチャの骨格が正しく、インターフェースがインポートできることを確認"""
    from wind_compass.use_cases.ports import WindDataReader, PowerPlantModelReader


def test_repository_interfaces_are_abstract():
    """リポジトリインターフェースが抽象クラスであり、直接インスタンス化できないことを確認"""
    from wind_compass.use_cases.ports import WindDataReader, PowerPlantModelReader

    # ABCであることを確認
    assert issubclass(WindDataReader, ABC)
    assert issubclass(PowerPlantModelReader, ABC)

    # インスタンス化しようとするとTypeErrorが発生することを確認
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        WindDataReader()

    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        PowerPlantModelReader()
