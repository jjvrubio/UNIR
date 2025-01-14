import json
import os
from AppKit import NSApplication, NSOpenPanel
import PyPDF2
import openai

# Function to open file dialog for choosing files
def open_file_dialog(file_types):
    app = NSApplication.sharedApplication()
    #app.setActivationPolicy_(2)  # NSApplicationActivationPolicyRegular
    #app.activateIgnoringOtherApps_(True) # Bring app to front
    
    panel = NSOpenPanel.openPanel()
    panel.setCanChooseDirectories_(False)
    panel.setCanChooseFiles_(True)
    panel.setAllowsMultipleSelection_(False)
    panel.setAllowedFileTypes_(file_types)
    panel.setMessage_("Please select a file")
    app.activateIgnoringOtherApps_(True)
    if panel.runModal() == 1:
        return panel.URL().path()
    return None

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        with open(pdf_file, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

# Function to evaluate the thesis based on the rubric
def evaluate_thesis_with_rubric(thesis_text, rubric):
    # Ensure OpenAI API Key is set
    openai.api_key = os.getenv("MI_CLAVE_API_OPENAI")
    if not openai.api_key:
        print("OpenAI API key not found. Set it in your environment variables.")
        return None

    results = {}
    try:
        for category, items in rubric.items():
            results[category] = []
            for item in items:
                subcategory = item["subcategoría"]
                criteria = item["criterios"]
                prompt = f"""
                You are a thesis grader. Evaluate the following thesis text according to the rubric:
                Subcategory: {subcategory}
                Criteria: {json.dumps(criteria, indent=2)}
                Thesis Text: {thesis_text}
                Provide a grade and brief feedback for this subcategory.
                """
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # Use "gpt-3.5-turbo" if needed
                    messages=[
                        {"role": "system", "content": "You are an academic evaluator skilled in assessing theses."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=300,
                    temperature=0.7,
                )

                results[category].append({
                    "subcategory": subcategory,
                    "grade_and_feedback": response['choices'][0]['message']['content'].strip()
                })

                return results

    except Exception as e:
        print(f"Error evaluating thesis: {e}")
        return None

# Main program
if __name__ == "__main__":
    # Step 1: Choose JSON rubric file
    print("Select the JSON rubric file.")
    rubric_file = open_file_dialog(["json"])
    if not rubric_file:
        print("No rubric file selected.")
        exit()

    # Load the rubric
    try:
        with open(rubric_file, 'r', encoding='utf-8') as file:
            rubric = json.load(file)
    except Exception as e:
        print(f"Error loading rubric file: {e}")
        exit()

    # Step 2: Choose PDF thesis file
    print("Select the thesis PDF file.")
    pdf_file = open_file_dialog(["pdf"])
    if not pdf_file:
        print("No thesis file selected.")
        exit()

    # Extract text from PDF
    thesis_text = extract_text_from_pdf(pdf_file)
    if not thesis_text:
        print("Error extracting text from PDF.")
        exit()

    # Step 3: Evaluate thesis
    print("Evaluating thesis...")
    results = evaluate_thesis_with_rubric(thesis_text, rubric)
    if not results:
        print("Error during thesis evaluation.")
        exit()

    # Step 4: Save results
    output_file = os.path.splitext(pdf_file)[0] + "_grades.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=4, ensure_ascii=False)
        print(f"Evaluation results saved to {output_file}")
    except Exception as e:
        print(f"Error saving results: {e}")
