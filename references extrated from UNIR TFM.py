import re
import pdfplumber
import json
import os
from AppKit import NSApplication, NSApp
from Cocoa import NSOpenPanel
from collections import Counter


def select_pdf_file():
    """Open a native macOS file picker to select a PDF file."""
    panel = NSOpenPanel.openPanel()
    panel.setAllowedFileTypes_(["pdf"])
    panel.setCanChooseFiles_(True)
    panel.setCanChooseDirectories_(False)

    if panel.runModal() == 1:  # 1 means OK button clicked
        return panel.URLs()[0].path()
    return None


def identify_head_footer_pattern(pdf):
    """Identify repeated header/footer patterns across pages."""
    try:
        line_counter = Counter()

        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                lines = page_text.splitlines()
                line_counter.update(lines)

        total_pages = len(pdf.pages)
        head_footer_patterns = {line for line, count in line_counter.items() if count / total_pages > 0.8}

        return head_footer_patterns
    except Exception as e:
        print(f"Error identifying header/footer patterns: {e}")
        return set()


def filter_head_footer_patterns(text, patterns):
    """Remove head/footer patterns from the extracted text."""
    filtered_lines = [line for line in text.splitlines() if line.strip() not in patterns]
    return "\n".join(filtered_lines)


def is_page_number(line):
    """Detect if a line is a page number."""
    patterns = [
        r"^\d+$", r"^\d+/\d+$", r"^Page \d+$", r"^Página \d+$", r"^\d+ of \d+$", r"^\d+ de \d+$"
    ]
    return any(re.match(pattern, line) for pattern in patterns)


def extract_references_from_pdf(pdf_path):
    """Extract references and export to JSON."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            extracted_references = []

            head_footer_patterns = identify_head_footer_pattern(pdf)

            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    filtered_text = filter_head_footer_patterns(page_text, head_footer_patterns)
                    text += filtered_text + "\n"

            ref_positions = [i for i, line in enumerate(text.splitlines()) if "REFERENCIAS" in line]

            if not ref_positions:
                print("No occurrences of 'REFERENCIAS' found.")
                return

            start_line = ref_positions[-1]
            lines = text.splitlines()

            for line in lines[start_line:]:
                if is_page_number(line) or "REFERENCIAS" in line:
                    continue

                if "Anexo" in line:
                    break

                if line.strip():  # Add non-empty lines to the references list
                    extracted_references.append(line.strip())

            if not extracted_references:
                print("No references found between 'REFERENCIAS' and 'Anexo'.")
            else:
                save_json_file(extracted_references, pdf_path)

    except Exception as e:
        print(f"Error during extraction: {e}")


def save_json_file(references, input_file_path):
    """Save references as JSON in the same directory as the input file with a custom name."""
    try:
        input_dir = os.path.dirname(input_file_path)
        input_filename = os.path.splitext(os.path.basename(input_file_path))[0]
        output_file_path = os.path.join(input_dir, f"{input_filename}_REFERENCIAS.json")

        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(references, f, ensure_ascii=False, indent=4)
        
        print(f"References successfully saved to {output_file_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")


def main():
    """Main function to select PDF, extract references, and save them as JSON."""
    NSApp()
    print("Select a PDF file...")
    pdf_path = select_pdf_file()

    if pdf_path:
        print(f"Extracting references from {pdf_path}...")
        extract_references_from_pdf(pdf_path)
    else:
        print("File selection cancelled.")


if __name__ == "__main__":
    main()
