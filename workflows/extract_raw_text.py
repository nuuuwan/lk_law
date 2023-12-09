from lk_law import Document


def main():
    doc_list = Document.list_all()
    for doc in doc_list:
        doc.extract_raw_text()


if __name__ == '__main__':
    main()
