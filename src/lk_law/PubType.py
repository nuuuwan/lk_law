import os
from dataclasses import dataclass

from lk_law.constants import DIR_DATA_DOC


@dataclass
class PubType:
    id: str
    name: str
    data_mode: str

    @property
    def isHTML(self):
        return self.data_mode == 'html'

    @property
    def isJSON(self):
        return self.data_mode == 'json'

    @property
    def dir_pub_type(self):
        return os.path.join(DIR_DATA_DOC, self.name.lower() + 's')

    def __hash__(self):
        return hash(self.id)

    @staticmethod
    def list_all() -> list['PubType']:
        return [
            PubType.ACT,
            PubType.BILL,
        ]

    @staticmethod
    def idx() -> dict[str, 'PubType']:
        return {pub_type.id: pub_type for pub_type in PubType.list_all()}

    @staticmethod
    def from_id(id: str) -> 'PubType':
        return PubType.idx()[id]


PubType.ACT = PubType('a', 'Act', 'html')
PubType.BILL = PubType('b', 'Bill', 'html')
# PubType.EXTRAORDINARY_GAZETTE = PubType(
#     'egz', 'Extraordinary Gazette', 'json'
# )
