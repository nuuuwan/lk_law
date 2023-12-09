import os
from functools import cached_property

import requests
from utils import JSONFile, Log

log = Log('Document')


class Document:
    DIR = os.path.join('data', 'doc')
    PUB_TYPE_LIST = ['b']  # ['a', 'egz', 'b']

    def __init__(self, pub_type: str, date: str, name: str, href: str):
        self.pub_type = pub_type
        self.date = date
        self.name = name
        self.href = href

    def to_dict(self) -> dict:
        return dict(
            pub_type=self.pub_type,
            date=self.date,
            name=self.name,
            href=self.href,
        )

    @cached_property
    def short_name(self):
        s = self.name.strip().lower().replace(' ', '-')
        s = ''.join(c for c in s if c.isalnum() or c == '-')
        if len(s) > 64:
            s = s[:64]
        return s

    @cached_property
    def file_name(self):
        return f'{self.date}-{self.short_name}'

    def __lt__(self, other):
        return self.file_name < other.file_name

    @cached_property
    def dir_doc(self) -> str:
        return os.path.join(Document.DIR, self.pub_type, self.file_name)

    @cached_property
    def pdf_path(self) -> str:
        return os.path.join(self.dir_doc, 'doc.pdf')

    @cached_property
    def data_path(self) -> str:
        return os.path.join(self.dir_doc, 'data.json')

    def write_data(self):
        if not os.path.exists(self.dir_doc):
            os.makedirs(self.dir_doc)

        JSONFile(self.data_path).write(self.to_dict())
        log.debug(f'Wrote {self.data_path}')

    def download_pdf(self):
        if os.path.exists(self.pdf_path):
            log.warning(f'{self.pdf_path} already exists')
            return

        pdf = requests.get(self.href).content
        with open(self.pdf_path, 'wb') as f:
            f.write(pdf)
        log.debug(f'Downloaded {self.pdf_path}')

    def write(self):
        self.write_data()
        self.download_pdf()

    @staticmethod
    def list_all() -> list['Document']:
        doc_list = []
        for pub_type in os.listdir(Document.DIR):
            for dir_doc in os.listdir(os.path.join(Document.DIR, pub_type)):
                data_path = os.path.join(
                    Document.DIR, pub_type, dir_doc, 'data.json'
                )
                d = JSONFile(data_path).read()
                if 'pub_type' not in d:
                    d['pub_type'] = 'a'
                doc_list.append(Document(**d))

        doc_list.sort()
        return doc_list
