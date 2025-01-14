import os
from pathlib import Path
import anthropic
import PyPDF2
from typing import Dict, List
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
    
    def _process_toc(self, outline, level=0) -> List[Dict]:
        """
        Recursively process PDF outline/bookmarks into structured TOC
        """
        toc = []
        if not outline:
            return toc
            
        for item in outline:
            if isinstance(item, list):
                # Recursive call for nested items
                toc.extend(self._process_toc(item, level + 1))
            else:
                # Process individual item
                if hasattr(item, '/Title'):
                    toc.append({
                        'title': item['/Title'],
                        'level': level,
                        'page': item.get('/Page', '').strip()
                    })
        return toc

    def _format_toc(self, toc: List[Dict]) -> str:
        """
        Format TOC into readable string for prompt
        """
        formatted = []
        for item in toc:
            indent = "  " * item['level']
            formatted.append(f"{indent}- {item['title']}")
        return "\n".join(formatted)

    def extract_toc(self, pdf_path: str) -> List[Dict]:
        """Extract table of contents from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                outline = pdf_reader.outline
                return self._process_toc(outline)
        except Exception as e:
            print(f"Warning: Could not extract TOC: {str(e)}")
            return []

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

    def generate_questions(self, pdf_text: str, toc: List[Dict]) -> str:
        # If no TOC available, use default sections
        if not toc:
            return self._generate_default_questions(pdf_text)
            
        prompt = f"""
        Generate questions based on this document's structure:

        {self._format_toc(toc)}

        Rules for question generation:
        1. Create 2-3 questions for each main section (level 0)
        2. Questions should follow the document's organization
        3. Focus on key concepts, methodology, results, and applications
        4. Number questions sequentially across all sections
        5. Use markdown formatting

        Format the output as:
        # Document Review Questions

        ## [Section Name]
        1. [Question]
        2. [Question]
        (continue for each section)

        Use this document content:
        {pdf_text[:4000]}
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
            
            # Extract the text content from the TextBlock
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            elif isinstance(response.content, list):
                return '\n'.join(block.text for block in response.content if hasattr(block, 'text'))
            else:
                return str(response.content)
            
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")

    def _generate_default_questions(self, pdf_text: str) -> str:
        """Fallback method when no TOC is available"""
        prompt = f"""
        Generate 10 thoughtful questions about this document.
        Structure them in these sections:

        # Document Review Questions

        ## Understanding & Concepts
        1. [Core concepts question]
        2. [Theoretical foundations question]
        3. [Key definitions question]

        ## Methodology & Approach
        4. [Methods question]
        5. [Approach question]
        6. [Implementation question]

        ## Results & Implications
        7. [Findings question]
        8. [Implications question]

        ## Future Work & Applications
        9. [Extensions question]
        10. [Applications question]

        Document content:
        {pdf_text[:4000]}
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
            
            if hasattr(response.content[0], 'text'):
                return response.content[0].text
            elif isinstance(response.content, list):
                return '\n'.join(block.text for block in response.content if hasattr(block, 'text'))
            else:
                return str(response.content)
            
        except Exception as e:
            raise Exception(f"Error generating default questions: {str(e)}")

    def format_markdown(self, content: str) -> str:
        markdown_template = f"""---
title: Document Review Questions
date: {datetime.now().strftime('%Y-%m-%d')}
---

{content}

---
*Generated using PDFQuestionGenerator with document structure analysis*
"""
        return markdown_template

def save_questions(pdf_path: str) -> Path:
    try:
        generator = PDFQuestionGenerator()
        
        print("Extracting text from PDF...")
        pdf_text = generator.extract_text_from_pdf(pdf_path)
        
        print("Extracting table of contents...")
        toc = generator.extract_toc(pdf_path)
        
        print("Generating questions...")
        questions_content = generator.generate_questions(pdf_text, toc)
        
        print("Formatting markdown...")
        markdown_content = generator.format_markdown(questions_content)
        
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