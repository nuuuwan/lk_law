from lk_law import Document


def main():
    doc_list = Document.list_all()
    for doc in doc_list:
        doc.write_doc_readme()

    latest_doc = doc_list[0]
    latest_doc.copy_to_latest()


if __name__ == '__main__':
    main()
