import os
from functools import cached_property

from utils import TIME_FORMAT_TIME, File, Log, Time

from lk_law.Document import Document

log = Log('ReadMe')


class ReadMe:
    def __init__(self):
        self.doc_list = Document.list_all()

    @cached_property
    def path(self) -> str:
        return os.path.join('README.data.md')

    @cached_property
    def n_docs(self) -> int:
        return len(self.doc_list)

    @cached_property
    def time_str(self) -> str:
        return TIME_FORMAT_TIME.stringify(Time.now())

    @cached_property
    def header_lines(self) -> list[str]:
        return [
            '# Legal Documents of Sri Lanka (Data)',
            '',
            'Legal documents from http://documents.gov.lk.',
            '',
        ]

    @cached_property
    def statistics_lines(self) -> list[str]:
        return [
            f'Downloaded **{self.n_docs:,}** documents,'
            + f' as of *{self.time_str}*.',
        ]

    @cached_property
    def docs_lines(self) -> list[str]:
        lines = []
        prev_year = None
        prev_year_and_month = None
        for doc in self.doc_list:
            year = doc.date[:4]
            year_and_month = doc.date[:7]

            if year != prev_year:
                lines.extend(['', f'## {year}'])
                prev_year = year

            if year_and_month != prev_year_and_month:
                lines.extend(['', f'### {year_and_month}', ''])
                prev_year_and_month = year_and_month

            lines.append(
                f'* [[{doc.date}] {doc.name}]({doc.dir_doc})'
                + f' ({doc.pub_type.name})'
            )
        return lines

    @cached_property
    def body_lines(self) -> list[str]:
        return self.statistics_lines + self.docs_lines

    @cached_property
    def lines(self) -> list[str]:
        return self.header_lines + self.body_lines

    def write(self):
        File(self.path).write_lines(self.lines)
        log.debug(f'Updated {self.path}')
