from abc import ABC, abstractmethod
from typing import Iterable
from wind_compass.domain.models import WindReading, PowerPlantModel


class WindDataReader(ABC):
    """
    風況データを読み込むリポジトリのインターフェース（ポート）
    """
    @abstractmethod
    def read(self, file_path: str) -> Iterable[WindReading]:
        """
        指定されたパスから風況データを読み込み、
        WindReadingオブジェクトのイテレータを返す。

        :param file_path: 風況データファイルのパス
        :return: WindReadingオブジェクトのイテレータ
        :raises FileNotFoundError: ファイルが見つからない場合
        :raises ValueError: ファイル形式が不正な場合
        """
        raise NotImplementedError


class PowerPlantModelReader(ABC):
    """
    設備特性コンフィグを読み込むリポジトリのインターフェース（ポート）
    """
    @abstractmethod
    def read(self, file_path: str) -> PowerPlantModel:
        """
        指定されたパスから設備特性コンフィグを読み込み、
        PowerPlantModelオブジェクトを返す。

        :param file_path: 設備特性コンフィグファイルのパス
        :return: PowerPlantModelオブジェクト
        :raises FileNotFoundError: ファイルが見つからない場合
        :raises ValueError: ファイル形式が不正な場合
        """
        raise NotImplementedError
