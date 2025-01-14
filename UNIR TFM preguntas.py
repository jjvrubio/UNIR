import os
from pathlib import Path
import anthropic
import PyPDF2
from typing import Dict
from datetime import datetime
from Foundation import NSURL
from AppKit import (
    NSOpenPanel,
    NSApplication,
    NSModalResponseOK
)

class MacOSPDFPicker:
    @staticmethod
    def pick_pdf_file() -> str:
        NSApplication.sharedApplication()
        
        panel = NSOpenPanel.alloc().init()
        panel.setTitle_("Select Student PDF")
        panel.setMessage_("Choose a PDF file to generate questions")
        panel.setPrompt_("Choose")
        panel.setAllowedFileTypes_(["pdf"])
        panel.setAllowsMultipleSelection_(False)
        panel.setCanChooseFiles_(True)
        panel.setCanChooseDirectories_(False)
        
        if panel.runModal() == NSModalResponseOK:
            selected_url = panel.URLs()[0]
            return selected_url.path()
        
        return None

class PDFQuestionGenerator:
    def __init__(self):
        api_key = os.getenv('MI_CLAVE_API_ANTROPIC')
        if not api_key:
            raise ValueError("Anthropic API key not found in environment variables")
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")

    def generate_questions(self, pdf_text: str, num_questions: int = 10) -> str:
        prompt = f"""
        Based on the following text, generate {num_questions} thoughtful questions.
        Return the response in a clear markdown format with exactly this structure:

        # Questions for Document Review

        ## Understanding & Concepts
        1. [Generate a deep question about core concepts]
        2. [Generate a question about theoretical foundations]
        3. [Generate a question about key definitions or principles]

        ## Methodology & Approach
        4. [Generate a question about methods used]
        5. [Generate a question about approach justification]
        6. [Generate a question about implementation details]

        ## Results & Implications
        7. [Generate a question about main findings]
        8. [Generate a question about practical implications]

        ## Future Work & Applications
        9. [Generate a question about potential extensions]
        10. [Generate a question about real-world applications]

        Use the following text as context:
        {pdf_text[:4000]}

        Important: Format the response exactly as shown above, with proper markdown headers and numbering.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1024,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Handle the response content properly
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            elif isinstance(response.content, list):
                # If it's a list of TextBlocks, join their text content
                return '\n'.join(block.text for block in response.content if hasattr(block, 'text'))
            else:
                # Fallback for string content
                return str(response.content)
            
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")

    def format_markdown(self, content: str) -> str:
        markdown_template = f"""---
title: Document Review Questions
date: {datetime.now().strftime('%Y-%m-%d')}
---

{content}

---
*Generated using PDFQuestionGenerator*
"""
        return markdown_template

def save_questions(pdf_path: str, num_questions: int = 10) -> Path:
    try:
        generator = PDFQuestionGenerator()
        
        print("Extracting text from PDF...")
        pdf_text = generator.extract_text_from_pdf(pdf_path)
        
        print("Generating questions...")
        questions_content = generator.generate_questions(pdf_text, num_questions)
        
        print("Formatting markdown...")
        markdown_content = generator.format_markdown(questions_content)
        
        # Create output path in same directory as PDF
        pdf_path = Path(pdf_path)
        output_path = pdf_path.parent / f"preguntas-{pdf_path.stem}.md"
        
        print(f"Saving to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return output_path
        
    except Exception as e:
        raise Exception(f"Error saving questions: {str(e)}")

def main():
    try:
        print("Starting PDF Question Generator...")
        pdf_picker = MacOSPDFPicker()
        pdf_path = pdf_picker.pick_pdf_file()
        
        if not pdf_path:
            print("No PDF file selected.")
            return
        
        print(f"Selected PDF: {pdf_path}")
        result_path = save_questions(pdf_path)
        
        if result_path:
            print(f"Questions generated and saved to: {result_path}")
            os.system(f"open '{result_path}'")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()