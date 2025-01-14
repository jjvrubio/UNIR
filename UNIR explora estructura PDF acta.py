from Foundation import NSURL
from Quartz import PDFDocument, PDFAnnotation
from AppKit import NSOpenPanel

def select_pdf_file():
    """
    Open a native macOS file picker dialog to select a PDF file.
    
    Returns:
        str: Path to selected PDF file, or None if cancelled
    """
    panel = NSOpenPanel.alloc().init()
    panel.setTitle_("Choose a PDF Form")
    panel.setAllowedFileTypes_(["pdf"])
    panel.setCanChooseDirectories_(False)
    panel.setCanChooseFiles_(True)
    panel.setAllowsMultipleSelection_(False)
    
    if panel.runModal() == 1:  # NSModalResponseOK
        return panel.URLs()[0].path()
    return None

def get_form_fields(pdf_path):
    """
    Extract all form field names from a PDF file using macOS native PDFKit.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary containing lists of different types of form fields
    """
    # Create URL from path
    url = NSURL.fileURLWithPath_(pdf_path)
    
    # Load PDF document
    pdf_document = PDFDocument.alloc().initWithURL_(url)
    if pdf_document is None:
        raise ValueError("Could not open PDF file")
    
    fields = {
        'text_fields': [],
        'buttons': [],
        'choice_fields': [],
        'other_fields': []
    }
    
    # Iterate through all pages
    for page_idx in range(pdf_document.pageCount()):
        page = pdf_document.pageAtIndex_(page_idx)
        annotations = page.annotations()
        
        if annotations:
            for annotation in annotations:
                # Check if it's a form element annotation
                if annotation.isKindOfClass_(PDFAnnotation):
                    field_type = annotation.widgetFieldType()
                    field_name = annotation.fieldName()
                    
                    if field_name:
                        if field_type == 'Text':
                            fields['text_fields'].append(field_name)
                        elif field_type in ['Button', 'Radio', 'CheckBox']:
                            fields['buttons'].append(field_name)
                        elif field_type in ['Choice', 'ListBox', 'ComboBox']:
                            fields['choice_fields'].append(field_name)
                        else:
                            fields['other_fields'].append(field_name)
    
    return fields

def print_fields(fields):
    """
    Print the extracted form fields in a organized way.
    """
    print("\nForm Fields Found:")
    print("\nText Fields:")
    for field in fields['text_fields']:
        print(f"- {field}")
        
    print("\nButtons (including Radio and Checkboxes):")
    for field in fields['buttons']:
        print(f"- {field}")
        
    print("\nChoice Fields (ComboBox/ListBox):")
    for field in fields['choice_fields']:
        print(f"- {field}")
        
    print("\nOther Fields:")
    for field in fields['other_fields']:
        print(f"- {field}")

def main():
    pdf_path = select_pdf_file()
    if pdf_path:
        try:
            fields = get_form_fields(pdf_path)
            print(f"\nAnalyzing PDF: {pdf_path}")
            print_fields(fields)
        except Exception as e:
            print(f"Error: {str(e)}")
    else:
        print("No file selected.")

if __name__ == "__main__":
    main()