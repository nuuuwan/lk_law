from lk_law import Document


def main():
    doc_list = Document.list_all()
    for doc in doc_list:
        doc.build_docx()


if __name__ == '__main__':
    main()
