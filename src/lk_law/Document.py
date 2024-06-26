import os
import random
import shutil
import sys
from functools import cached_property

import openai
import requests
from pdf2docx import Converter
from pdfminer.high_level import extract_text
from utils import File, Hash, JSONFile, Log

from lk_law.PubType import PubType

log = Log('Document')


class Document:
    DIR = os.path.join('data', 'doc')

    def __init__(self, pub_type: PubType, date: str, name: str, href: str):
        self.pub_type = pub_type
        self.date = date
        self.name = name
        self.href = href

    @staticmethod
    def from_dict(d: dict) -> 'Document':
        pub_type_id = d.get('pub_type', 'a')
        return Document(
            PubType.from_id(pub_type_id),
            d['date'],
            d['name'],
            d['href'],
        )

    def to_dict(self) -> dict:
        return dict(
            pub_type=self.pub_type.id,
            date=self.date,
            name=self.name,
            href=self.href,
        )

    def __str__(self):
        return f'Document({str(self.to_dict())})'

    @cached_property
    def md5(self):
        return Hash.md5(str(self))

    def __hash__(self):
        return hash(self.md5)

    @cached_property
    def short_name(self):
        s = self.name.strip().lower().replace(' ', '-')
        s = ''.join(c for c in s if c.isalnum() or c == '-')
        if len(s) > 32:
            s = s[:32]
        s += f'-{self.md5[:8]}'
        return s

    @cached_property
    def file_name(self):
        return f'{self.date}-{self.short_name}'

    def __lt__(self, other):
        return self.file_name < other.file_name

    @cached_property
    def dir_doc(self) -> str:
        return os.path.join(self.pub_type.dir_pub_type, self.file_name)

    # Data

    @cached_property
    def data_path(self) -> str:
        return os.path.join(self.dir_doc, 'data.json')

    def write_data(self):
        if not os.path.exists(self.dir_doc):
            os.makedirs(self.dir_doc)

        JSONFile(self.data_path).write(self.to_dict())
        log.debug(f'Wrote {self.data_path}')

    # PDF

    @cached_property
    def pdf_path(self) -> str:
        return os.path.join(self.dir_doc, 'doc.pdf')

    def download_pdf(self):
        if os.path.exists(self.pdf_path):
            log.warning(f'{self.pdf_path} already exists')
            return

        pdf = requests.get(self.href).content
        with open(self.pdf_path, 'wb') as f:
            f.write(pdf)
        log.debug(f'Downloaded {self.pdf_path}')

    # Raw Text
    @cached_property
    def raw_text_path(self) -> str:
        return os.path.join(self.dir_doc, 'raw_text.txt')

    def extract_raw_text(self):
        if os.path.exists(self.raw_text_path):
            log.warning(f'{self.raw_text_path} already exists')
            return

        try:
            text = extract_text(self.pdf_path)
        except Exception as e:
            log.error(f'Failed to extract text from {self.pdf_path}: {e}')
            return

        File(self.raw_text_path).write(text)
        n_k = os.path.getsize(self.raw_text_path) / 1_000.0
        log.debug(f'Extracted text to {self.raw_text_path}  ({n_k:.1f}KB)')

    # DocX (MS Word)
    @cached_property
    def docx_path(self) -> str:
        return os.path.join(self.dir_doc, 'doc.docx')

    def build_docx(self):
        if os.path.exists(self.docx_path):
            log.warning(f'{self.docx_path} already exists')
            return

        try:
            cv = Converter(self.pdf_path)
            cv.convert(
                self.docx_path, start=0, end=None, multi_processing=True
            )
            cv.close()
            log.debug(f'Converted {self.pdf_path} to {self.docx_path}')
        except Exception as e:
            log.error(
                f'Failed to convert {self.pdf_path} to {self.docx_path}: {e}'
            )

    # README

    @staticmethod
    def summarize(text: str) -> list[str]:
        if len(text) > 30_000:
            text = text[:30_000]
        if len(sys.argv) < 2:
            raise ValueError('OpenAI API key is required. Missing argument.')
        api_key = sys.argv[1]
        client = openai.Client(api_key=api_key)
        messages = [
            dict(
                role='system',
                content='Summarize the most important points'
                + ' in the following document text'
                + ' into bullets:',
            ),
            dict(role='user', content=text),
        ]
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=messages,
        )
        return response.choices[0].message.content

    @cached_property
    def doc_readme_path(self) -> str:
        return os.path.join(self.dir_doc, 'README.md')
    
    @cached_property
    def readme_latest_path(self) -> str:
        return os.path.join('README.latest.md')

    @cached_property
    def doc_readme_summary_path(self) -> str:
        return os.path.join(self.dir_doc, 'README.summary.md')

    def write_doc_readme(self):
        if os.path.exists(self.doc_readme_path):
            return

        if os.path.exists(self.doc_readme_summary_path):
           return

        raw_text = File(self.raw_text_path).read()
        summary = ''
        try:
            summary = Document.summarize(raw_text)
            File(self.doc_readme_summary_path).write(summary)
            log.debug(f'Wrote {self.doc_readme_summary_path}')
        except Exception as e:
            log.error(f'Failed to summarize {self.raw_text_path}: {e}')

        lines = [
            f'# {self.pub_type.emoji}  {self.name}',
            '',
            f'{self.pub_type.name} published on **{self.date}**.',
            '',
        ] + [summary, '']
        File(self.doc_readme_path).write('\n'.join(lines))
        log.debug(f'Wrote {self.doc_readme_path}')

    def copy_to_latest(self):
        shutil.copyfile(self.doc_readme_path, self.readme_latest_path)
        log.debug(f'Copied to {self.readme_latest_path}')

    # -- List Methods  --

    @staticmethod
    def list_all() -> list['Document']:
        doc_list = []
        for pub_type_id in os.listdir(Document.DIR):
            dir_pub_type = os.path.join(Document.DIR, pub_type_id)
            for dir_doc in os.listdir(dir_pub_type):
                data_path = os.path.join(dir_pub_type, dir_doc, 'data.json')
                d = JSONFile(data_path).read()
                doc_list.append(Document.from_dict(d))
        doc_list.sort(key=lambda doc: doc.date, reverse=True)
        return doc_list
