import pdfplumber

def extract_text(file_path, start_page=1, end_page=None):
    text = ""

    with pdfplumber.open(file_path) as pdf:
        total = len(pdf.pages)

        if end_page is None:
            end_page = total

        # Proper error handling
        if start_page < 1 or end_page > total:
            raise ValueError(f"Invalid range! PDF has {total} pages only!")

        for i in range(start_page - 1, end_page):
            page = pdf.pages[i]
            page_text = page.extract_text()

            if page_text:
                text += page_text + " "

    return text
