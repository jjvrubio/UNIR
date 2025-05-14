#!/usr/bin/env python3
# PDF Search Tool for macOS
# This script searches for a specific word in all PDF files within a specified folder and its subfolders.
# It handles common macOS quirks such as hidden files and directories, and provides a summary of the search results.    

import os
import sys
import PyPDF2
from datetime import datetime

def search_pdfs_for_word(root_folder, search_word, case_sensitive=False):
    """
    Search for a word in all PDF files within a folder and its subfolders on macOS.
    
    Args:
        root_folder (str): Path to the root folder to search
        search_word (str): Word to search for in the PDFs
        case_sensitive (bool): Whether the search should be case-sensitive
    """
    search_term = search_word if case_sensitive else search_word.lower()
    total_matches = 0
    total_files_searched = 0
    
    print(f"\n🔍 Searching for '{search_word}' in PDFs under: {root_folder}")
    if not case_sensitive:
        print("ℹ️ Performing case-insensitive search")
    
    start_time = datetime.now()
    
    for foldername, _, filenames in os.walk(root_folder):
        # Skip hidden directories (common on macOS)
        if '/.' in foldername:
            continue
            
        for filename in filenames:
            if filename.lower().endswith('.pdf'):
                filepath = os.path.join(foldername, filename)
                total_files_searched += 1
                
                # Skip hidden files (common on macOS)
                if filename.startswith('.'):
                    continue
                    
                try:
                    with open(filepath, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        found_in_file = False
                        
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            text = page.extract_text()
                            
                            if text:
                                content = text if case_sensitive else text.lower()
                                if search_term in content:
                                    if not found_in_file:
                                        print(f"\n📄 Found in: {filepath}")
                                        found_in_file = True
                                    print(f"   📑 Page {page_num + 1}")
                                    total_matches += 1
                                    
                except Exception as e:
                    print(f"⚠️ Error processing {filename}: {str(e)}", file=sys.stderr)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n📊 Search Summary:")
    print(f"• Total PDF files searched: {total_files_searched}")
    print(f"• Total matches found: {total_matches}")
    print(f"• Search duration: {duration.total_seconds():.2f} seconds")

def get_folder_path():
    """Helper function to handle folder path input with macOS quirks"""
    while True:
        path = input("Enter the folder path to search (or drag folder here): ").strip()
        
        # Handle paths with spaces that might be dragged in
        path = path.replace('\\ ', ' ')
        
        # Remove surrounding quotes if present
        if path.startswith("'") and path.endswith("'"):
            path = path[1:-1]
        elif path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
            
        if os.path.isdir(path):
            return os.path.abspath(path)
        print("Error: Folder not found. Please try again.", file=sys.stderr)

if __name__ == "__main__":
    print("\nPDF Search Tool for macOS")
    print("------------------------")
    
    folder_path = get_folder_path()
    search_term = input("Enter the word to search for: ").strip()
    case_sensitive = input("Case-sensitive search? (y/N): ").strip().lower() == 'y'
    
    search_pdfs_for_word(folder_path, search_term, case_sensitive)