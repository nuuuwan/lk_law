import os
from functools import cached_property

from utils import TIME_FORMAT_TIME, File, Log, Time

from lk_law.Document import Document

log = Log('ReadMe')

N_LATEST_DOCS = 30


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
            f'Downloaded **{self.n_docs}** documents, as of *{self.time_str}*.',
            '',
        ]

    @cached_property
    def selected_docs_lines(self) -> list[str]:
        n_display = min(N_LATEST_DOCS, self.n_docs)
        lines = ['## Selected Documents']
        for i in range(n_display):
            if i % 5 == 0:
                lines.append('')
            j = (
                int((self.n_docs - 1) * (i) / (n_display - 1))
                if n_display > 1
                else 0
            )
            doc = self.doc_list[j]
            lines.append(
                f'* ({j}) [{doc.date} {doc.name}]({doc.pdf_path_unix})'
            )

        lines.append('')
        return lines

    @cached_property
    def body_lines(self) -> list[str]:
        return self.statistics_lines + self.selected_docs_lines

    @cached_property
    def lines(self) -> list[str]:
        return self.header_lines + self.body_lines

    def write(self):
        File(self.path).write_lines(self.lines)
        log.debug(f'Updated {self.path}')
