import PyPDF2

def count_pdf_pages(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return len(reader.pages)

if __name__ == "__main__":
    pdf_file_path = input("Ingrese la ruta del archivo PDF: ")
    num_pages = count_pdf_pages(pdf_file_path)
    print(f"El número de páginas en el PDF es: {num_pages}")
