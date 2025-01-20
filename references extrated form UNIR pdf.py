import re
import pdfplumber
from AppKit import NSApplication, NSApp
from Cocoa import NSOpenPanel, NSSavePanel


def select_pdf_file():
    """Open a native macOS file picker to select a PDF file."""
    panel = NSOpenPanel.openPanel()
    panel.setAllowedFileTypes_(["pdf"])
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)

    if panel.runModal() == 1:  # 1 means OK button clicked
        return panel.URLs()[0].path()
    return None

from collections import Counter


def identify_head_footer_pattern(pdf):
    """Identify repeated header/footer patterns across pages and log them to a file."""
    try:
        # Counter to keep track of line occurrences across pages
        line_counter = Counter()

        # Count occurrences of each line from all pages
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                lines = page_text.splitlines()
                line_counter.update(lines)

        # Identify lines that appear on more than 80% of pages
        total_pages = len(pdf.pages)
        head_footer_patterns = {line for line, count in line_counter.items() if count / total_pages > 0.8}

        # Write identified patterns to a debug file
        with open("header_footer_debug.txt", "w", encoding="utf-8") as debug_file:
            debug_file.write("Identified Header/Footer Patterns:\n")
            for pattern in head_footer_patterns:
                debug_file.write(f"{pattern}\n")

            # Log which pages each pattern was found on
            debug_file.write("\nPatterns found on pages:\n")
            for pattern in head_footer_patterns:
                pages_found = [
                    page_number + 1
                    for page_number, page in enumerate(pdf.pages)
                    if page.extract_text() and pattern in page.extract_text()
                ]
                debug_file.write(f"{pattern} -> Found on pages: {pages_found}\n")

        return head_footer_patterns

    except Exception as e:
        print(f"An error occurred while identifying header/footer patterns: {e}")
        return set()


def filter_head_footer_patterns(text, patterns):
    """Remove head/footer patterns from the extracted text."""
    filtered_lines = [line for line in text.splitlines() if line.strip() not in patterns]
    return "\n".join(filtered_lines)


def is_page_number(line):
    """Detect if a line is a page number in English or Spanish using regex patterns."""
    patterns = [
        r"^\d+$",                     # Single number (e.g., "1")
        r"^\d+/\d+$",                 # Fraction format (e.g., "1/10")
        r"^Page \d+$",                # "Page X" in English
        r"^Página \d+$",              # "Página X" in Spanish
        r"^\d+ of \d+$",              # "X of Y" in English
        r"^\d+ de \d+$",              # "X de Y" in Spanish
    ]
    return any(re.match(pattern, line) for pattern in patterns)


def extract_references_from_pdf(pdf_path):
    """Extract text between the last occurrence of 'Referencias bibliográficas' and 'Anexo', filtering repeated headers/footers."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            extracted_text = ""

            # Step 1: Identify repeated header/footer patterns
            head_footer_patterns = identify_head_footer_pattern(pdf)
            print(f"Identified Head/Footer Patterns: {head_footer_patterns}")

            # Step 2: Extract text from each page and filter the patterns
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    filtered_text = filter_head_footer_patterns(page_text, head_footer_patterns)
                    text += filtered_text + "\n"

            # Step 3: Find the last occurrence of "Referencias bibliográficas"
            ref_positions = [i for i, line in enumerate(text.splitlines()) if "Referencias bibliográficas" in line]

            if not ref_positions:
                print("No occurrences of 'Referencias bibliográficas' found.")
                return

            # Start extraction from the last occurrence
            start_line = ref_positions[-1]
            lines = text.splitlines()

            for line in lines[start_line:]:
                #Skip lines which are identified as page numbers
                if is_page_number(line):
                    continue
                # Skip any line containing "Referencias bibliográficas"
                if "Referencias bibliográficas" in line:
                    continue

                if "Anexo" in line:
                    break

                extracted_text += line + "\n"

            # Save the extracted text
            if not extracted_text.strip():
                print("No text found between the last 'Referencias bibliográficas' and 'Anexo'.")
            else:
                save_text_file(extracted_text)

    except Exception as e:
        print(f"An error occurred: {e}")


def save_text_file(text):
    """Open a native macOS save panel to save extracted text."""
    from Cocoa import NSSavePanel
    panel = NSSavePanel.savePanel()
    panel.setAllowedFileTypes_(["txt"])
    panel.setCanCreateDirectories_(True)

    if panel.runModal() == 1:
        file_url = panel.URL()
        if file_url:
            file_path = file_url.path()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Text successfully saved to {file_path}")
        else:
            print("No file path returned.")
    else:
        print("Save operation cancelled.")


def main():
    """Main function to select PDF, extract text, and save it."""
    NSApp()
    print("Select a PDF file...")
    pdf_path = select_pdf_file()

    if pdf_path:
        print(f"Extracting text from {pdf_path}...")
        extract_references_from_pdf(pdf_path)
    else:
        print("File selection cancelled.")

if __name__ == "__main__":
    main()
