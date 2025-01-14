from Foundation import NSURL
from Quartz import PDFDocument, PDFAnnotation
from AppKit import NSOpenPanel
import openpyxl

def select_file(title, file_types):
    """
    Open a native macOS file picker dialog.
    
    Args:
        title (str): Window title
        file_types (list): List of allowed file extensions
        
    Returns:
        str: Path to selected file, or None if cancelled
    """
    panel = NSOpenPanel.alloc().init()
    panel.setTitle_(title)
    panel.setAllowedFileTypes_(file_types)
    panel.setCanChooseDirectories_(False)
    panel.setCanChooseFiles_(True)
    panel.setAllowsMultipleSelection_(False)
    
    if panel.runModal() == 1:  # NSModalResponseOK
        return panel.URLs()[0].path()
    return None

def read_excel_cells(excel_path):
    """
    Read specific cells from Excel file.
    
    Args:
        excel_path (str): Path to Excel file
        
    Returns:
        dict: Dictionary with cell values
    """
    workbook = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = workbook.active
    
    values = {
        'txtNotaEstructura': sheet['J5'].value,
        'txtNotaContenido': sheet['J7'].value,
        'txtNotaPresentación': sheet['J12'].value,
        'txtNotaCalificaciónFinal': sheet['H14'].value
    }
    
    workbook.close()
    return values

def fill_pdf_form(pdf_path, values):
    """
    Fill PDF form fields with given values.
    
    Args:
        pdf_path (str): Path to PDF file
        values (dict): Dictionary of field names and values
    """
    # Create URL from path
    url = NSURL.fileURLWithPath_(pdf_path)
    
    # Load PDF document
    pdf_document = PDFDocument.alloc().initWithURL_(url)
    if pdf_document is None:
        raise ValueError("Could not open PDF file")
    
    # Iterate through all pages to find and fill form fields
    for page_idx in range(pdf_document.pageCount()):
        page = pdf_document.pageAtIndex_(page_idx)
        annotations = page.annotations()
        
        if annotations:
            for annotation in annotations:
                if annotation.isKindOfClass_(PDFAnnotation):
                    field_name = annotation.fieldName()
                    if field_name in values:
                        # Convert value to string and set it
                        value = str(values[field_name])
                        annotation.setStringValue_(value)
    
    # Save the modified PDF
    save_path = pdf_path.replace('.pdf', '_filled.pdf')
    pdf_document.writeToFile_(save_path)
    return save_path

def main():
    # Select Excel file
    print("Please select the Excel file...")
    excel_path = select_file("Choose Excel File", ["xlsx", "xls"])
    if not excel_path:
        print("No Excel file selected.")
        return

    # Select PDF file
    print("Please select the PDF form...")
    pdf_path = select_file("Choose PDF Form", ["pdf"])
    if not pdf_path:
        print("No PDF file selected.")
        return

    try:
        # Read values from Excel
        print("\nReading Excel cells...")
        values = read_excel_cells(excel_path)
        print("Values read from Excel:")
        for field, value in values.items():
            print(f"- {field}: {value}")

        # Fill PDF form
        print("\nFilling PDF form...")
        saved_path = fill_pdf_form(pdf_path, values)
        print(f"\nPDF form has been filled and saved as: {saved_path}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()