import abc
import json
from typing import Any, Dict


class BaseStorage(abc.ABC):

    @abc.abstractmethod
    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""

    @abc.abstractmethod
    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""


class JsonFileStorage(BaseStorage):

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def save_state(self, state: Dict[str, Any]) -> None:
        """Сохранить состояние в хранилище."""
        with open(self.file_path, 'r+', encoding='utf-8') as file:
            data = file.read()
            buffer = json.loads(data) if data else {}
            buffer.update(state)
            file.seek(0)
            file.write(json.dumps(buffer))

    def retrieve_state(self) -> Dict[str, Any]:
        """Получить состояние из хранилища."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write("{}")
            return {}


class State:
    """Класс для работы с состояниями."""

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа."""
        self.storage.save_state(state={key: value})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу."""
        return self.storage.retrieve_state().get(key)


etl_settings = State(storage=JsonFileStorage(file_path='etl_settings'))
