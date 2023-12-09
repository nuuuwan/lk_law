from dataclasses import dataclass


@dataclass
class PubType:
    id: str
    name: str

    @property
    def isHTML(self):
        return self.id in ['a', 'b']

    @property
    def isJSON(self):
        return self.id in ['egz']

    def __hash__(self):
        return hash(self.id)

    @staticmethod
    def list_all() -> list['PubType']:
        return [
            PubType('a', 'Act'),
            PubType('b', 'Bill'),
            PubType('egz', 'Extraordinary Gazette'),
        ]

    @staticmethod
    def idx() -> dict[str, 'PubType']:
        return {pub_type.id: pub_type for pub_type in PubType.list_all()}
