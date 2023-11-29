from abc import abstractmethod, ABC


class ContentGenerator(ABC):
    @abstractmethod
    def generate_content(self, article_id: int, args: dict):
        pass
