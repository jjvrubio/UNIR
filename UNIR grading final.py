# Standard library imports
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from os import environ  # Only for environment variable access

# Third-party imports
import anthropic
import json
import PyPDF2
import pandas as pd
import matplotlib.pyplot as plt

# macOS specific imports
from Foundation import NSURL
from AppKit import (
    NSOpenPanel,
    NSSavePanel,
    NSDocumentDirectory,
    NSUserDomainMask,
    NSFileHandlingPanelOKButton
)

class UNIRDocumentGrader:
    def __init__(self, api_key: str, historical_data_path: Optional[str] = None):
        """
        Initialize the UNIR TFM grader with enhanced analytics capabilities
        
        Args:
            api_key (str): The Anthropic API key for authentication
            historical_data_path (str, optional): Path to historical evaluations JSON file
        """
        if not api_key:
            raise ValueError("API key cannot be empty")
            
        self.client = anthropic.Anthropic(api_key=api_key)
        self.historical_data = self.load_historical_data(historical_data_path) if historical_data_path else None

    

    def grade_solution(self, prompt: Optional[str], rubric_path: str, solution_path: str) -> Dict:
        """
        Grade the solution based on the rubric and return results.
        
        Args:
            prompt (Optional[str]): Custom prompt for evaluation
            rubric_path (str): Path to the rubric JSON file
            solution_path (str): Path to the solution PDF file
            
        Returns:
            Dict: Grading results
        """
        # 1. Load and process the PDF content
        try:
            with open(solution_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                content = ""
                for page in pdf_reader.pages:
                    content += page.extract_text()
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

        # 2. Load the rubric
        try:
            with open(rubric_path, 'r', encoding='utf-8') as f:
                try:
                    rubric = json.load(f)
                except json.JSONDecodeError as je:
                    print(f"JSON formatting error: {str(je)}")
                    print(f"Error occurred near position {je.pos}")
                    with open(rubric_path, 'r', encoding='utf-8') as f2:
                        lines = f2.readlines()
                        line_no = len(''.join(lines[:je.lineno-1]))
                        print(f"Context: {lines[je.lineno-1][max(0,je.colno-20):je.colno+20]}")
                    raise Exception(f"Invalid JSON format in rubric file: {str(je)}")
        except Exception as e:
            raise Exception(f"Error loading rubric: {str(e)}")

        # 3. Initialize results structure
        results = {
            "puntuacion_total": 0,
            "categorias": {},
            "retroalimentacion": ""
        }

        # 4. Evaluate each category using Anthropic API
        total_score = 0
        total_weight = 0

        for categoria, criterios in rubric.items():
            category_name = categoria.split(" (")[0]
            weight = float(categoria.split("(")[1].replace("%)", "")) / 100
            total_weight += weight
            
            category_results = {
                "analisis": "",
                "subcategorias": {}
            }

            for subcategoria in criterios:
                # Prepare the evaluation prompt for Claude
                evaluation_prompt = f"""
                Evalúa el siguiente trabajo académico para la subcategoría '{subcategoria['subcategoría']}' 
                según estos criterios:

                Suspenso (0-4): {subcategoria['criterios']['Suspenso (0-4)']}
                Aprobado (5-6): {subcategoria['criterios']['Aprobado (5-6)']}
                Notable (7-8): {subcategoria['criterios']['Notable (7-8)']}
                Sobresaliente (9-10): {subcategoria['criterios']['Sobresaliente (9-10)']}

                Contenido a evaluar:
                {content[:4000]}  # Limiting content length for API

                Por favor, proporciona:
                1. Una puntuación numérica (0-10)
                2. Una justificación detallada
                3. Recomendaciones específicas de mejora
                """

                # Get evaluation from Claude
                response = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=1000,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": evaluation_prompt}
                    ]
                )

                # Process Claude's response
                evaluation = response.content[0].text
                
                # Extract score using simple heuristic (first number found)
                import re
                score_match = re.search(r'\b([0-9]|10)(\.[0-9])?\b', evaluation)
                score = float(score_match.group()) if score_match else 5.0

                # Store subcategory results
                category_results["subcategorias"][subcategoria['subcategoría']] = score

            # Calculate category average
            category_score = sum(category_results["subcategorias"].values()) / len(category_results["subcategorias"])
            total_score += category_score * weight

            # Generate category analysis
            category_analysis_prompt = f"""
            Basándote en las siguientes puntuaciones de subcategorías para {category_name}:
            {category_results['subcategorias']}
            
            Proporciona un análisis general de 2-3 párrafos sobre el desempeño en esta categoría,
            destacando fortalezas y áreas de mejora.
            """

            analysis_response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                temperature=0.3,
                messages=[
                    {"role": "user", "content": category_analysis_prompt}
                ]
            )

            category_results["analisis"] = analysis_response.content[0].text
            results["categorias"][category_name] = category_results

        # Calculate final score
        results["puntuacion_total"] = round(total_score, 2)

        # Generate overall feedback
        feedback_prompt = f"""
        Basándote en la evaluación completa con puntuación final de {results['puntuacion_total']}/10,
        proporciona una retroalimentación general constructiva que:
        1. Resuma las principales fortalezas
        2. Identifique las áreas críticas de mejora
        3. Proporcione recomendaciones específicas y accionables
        """

        feedback_response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=800,
            temperature=0.3,
            messages=[
                {"role": "user", "content": feedback_prompt}
            ]
        )

        results["retroalimentacion"] = feedback_response.content[0].text

        return results
        
    def load_historical_data(self, file_path: str) -> List[Dict]:
        """Load historical evaluation data for comparative analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Warning: Could not load historical data: {e}")
            return []

    def perform_trend_analysis(self, current_results: Dict) -> Dict:
        """Analyze trends and patterns in evaluations over time"""
        if not self.historical_data:
            return {}
            
        all_evaluations = self.historical_data + [current_results]
        df = pd.DataFrame([
            {
                'fecha': eval.get('fecha', 'Unknown'),
                'puntuacion_total': eval['puntuacion_total'],
                **{f"{cat}_{subcat}": score 
                   for cat, data in eval['categorias'].items()
                   for subcat, score in data['subcategorias'].items()}
            }
            for eval in all_evaluations
        ])
        
        analysis = {
            'tendencias': {
                'promedio_historico': df['puntuacion_total'].mean(),
                'desviacion_estandar': df['puntuacion_total'].std(),
                'percentil': (df['puntuacion_total'] <= current_results['puntuacion_total']).mean() * 100
            },
            'comparativa_categorias': {}
        }
        
        for categoria in current_results['categorias'].keys():
            cat_cols = [col for col in df.columns if col.startswith(f"{categoria}_")]
            analysis['comparativa_categorias'][categoria] = {
                'promedio_historico': df[cat_cols].mean().mean(),
                'posicion_relativa': 'Por encima del promedio' if df[cat_cols].mean().mean() < current_results['categorias'][categoria]['subcategorias']['puntuacion_total'] else 'Por debajo del promedio'
            }
            
        return analysis

    def generate_comparative_visuals(self, results: Dict, output_dir: str):
        """Generate visual comparisons with historical data"""
        if not self.historical_data:
            return
            
        vis_dir = Path(output_dir) / 'visualizaciones'
        vis_dir.mkdir(exist_ok=True)
        
        plt.figure(figsize=(10, 6))
        historical_scores = [eval['puntuacion_total'] for eval in self.historical_data]
        plt.hist(historical_scores, bins=10, alpha=0.5, label='Histórico')
        plt.axvline(results['puntuacion_total'], color='r', linestyle='dashed', label='Evaluación actual')
        plt.title('Distribución de Calificaciones TFM')
        plt.xlabel('Puntuación')
        plt.ylabel('Frecuencia')
        plt.legend()
        plt.savefig(vis_dir / 'distribucion_calificaciones.png')
        plt.close()

    def select_files(self) -> Tuple[str, str, str]:
        """
        Opens native macOS file dialogs to select the PDF exercise and rubric JSON files.
        
        Returns:
            Tuple[str, str, str]: Paths to the selected PDF file, JSON file, and output directory
        """
        def create_file_dialog(title: str, file_types: List[str]) -> NSOpenPanel:
            panel = NSOpenPanel.alloc().init()
            panel.setTitle_(title)
            panel.setCanChooseFiles_(True)
            panel.setCanChooseDirectories_(False)
            panel.setAllowsMultipleSelection_(False)
            panel.setAllowedFileTypes_(file_types)
            return panel

        # Select PDF file
        pdf_panel = create_file_dialog("Select Student's PDF Exercise", ["pdf"])
        pdf_result = pdf_panel.runModal()
        
        if pdf_result != NSFileHandlingPanelOKButton:
            raise ValueError("No PDF file selected")
        
        pdf_path = pdf_panel.URLs()[0].path()

        # Select JSON rubric file
        json_panel = create_file_dialog("Select Rubric JSON File", ["json"])
        json_result = json_panel.runModal()
        
        if json_result != NSFileHandlingPanelOKButton:
            raise ValueError("No JSON file selected")
        
        json_path = json_panel.URLs()[0].path()

        # Select output directory
        dir_panel = NSOpenPanel.alloc().init()
        dir_panel.setTitle_("Select Output Directory")
        dir_panel.setCanChooseFiles_(False)
        dir_panel.setCanChooseDirectories_(True)
        dir_panel.setAllowsMultipleSelection_(False)
        
        if dir_panel.runModal() != NSFileHandlingPanelOKButton:
            raise ValueError("No output directory selected")
        
        output_dir = dir_panel.URLs()[0].path()

        # Verify files exist and are readable
        pdf_path_obj = Path(pdf_path)
        json_path_obj = Path(json_path)
        output_dir_obj = Path(output_dir)

        if not pdf_path_obj.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        if not json_path_obj.is_file():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
        if not output_dir_obj.is_dir():
            raise NotADirectoryError(f"Output directory not found: {output_dir}")

        return pdf_path, json_path, output_dir
    
    def generate_markdown_report(self, results: Dict) -> str:
        """
        Generate a detailed markdown report from the grading results.
        
        Args:
            results (Dict): The evaluation results from grade_solution
        
        Returns:
            str: Formatted markdown report
        """
        def generate_score_bar(score: float) -> str:
            """Create a visual representation of the score using Unicode characters"""
            filled = "█" * int(score)
            empty = "░" * (10 - int(score))
            return f"{filled}{empty}"

        def format_criteria_comparison(score: float) -> str:
            """Map score to rubric level"""
            if score >= 9:
                return "Sobresaliente"
            elif score >= 7:
                return "Notable"
            elif score >= 5:
                return "Aprobado"
            else:
                return "Suspenso"

        current_date = datetime.now().strftime("%d/%m/%Y")
        
        # Start with header and executive summary
        md_content = [
            "# Informe de Evaluación del Trabajo Fin de Máster",
            f"Fecha de evaluación: {current_date}",
            "\n## Resumen Ejecutivo",
            f"Calificación Final: {results['puntuacion_total']}/10  {generate_score_bar(results['puntuacion_total'])}"
        ]

        # Analyze strengths and areas for improvement
        strengths = []
        areas_improvement = []
        
        for categoria, datos in results['categorias'].items():
            for subcategoria, puntuacion in datos['subcategorias'].items():
                if isinstance(puntuacion, (int, float)):  # Ensure we're dealing with a number
                    if puntuacion >= 8:
                        strengths.append(f"- **{subcategoria}** ({puntuacion}/10): Demuestra excelencia en este aspecto")
                    elif puntuacion <= 6:
                        areas_improvement.append(f"- **{subcategoria}** ({puntuacion}/10): Requiere atención adicional")

        # Add strengths and improvements sections
        md_content.extend([
            "\n### Fortalezas Principales",
            *strengths[:3],  # Top 3 strengths
            "\n### Áreas de Mejora Prioritarias",
            *areas_improvement[:3],  # Top 3 areas for improvement
            "\n## Evaluación Detallada por Categorías"
        ])

        # Category weights from rubric
        weights = {
            "Estructura": "20%",
            "Contenido": "50%",
            "Exposición": "30%"
        }

        # Process each category
        for categoria, datos in results['categorias'].items():
            weight = weights.get(categoria, "N/A")
            
            # Calculate category average
            valid_scores = [score for score in datos['subcategorias'].values() 
                        if isinstance(score, (int, float))]
            category_avg = sum(valid_scores) / len(valid_scores) if valid_scores else 0
            
            md_content.extend([
                f"\n### {categoria} ({weight})",
                f"Puntuación media: {category_avg:.1f}/10  {generate_score_bar(category_avg)}",
                "\n#### Análisis General",
                datos['analisis'],
                "\n#### Evaluación por Subcategorías"
            ])

            # Add subcategory details
            for subcategoria, puntuacion in datos['subcategorias'].items():
                if isinstance(puntuacion, (int, float)):
                    nivel = format_criteria_comparison(puntuacion)
                    md_content.extend([
                        f"\n##### {subcategoria}",
                        f"Puntuación: {puntuacion}/10  {generate_score_bar(puntuacion)}",
                        f"Nivel alcanzado: {nivel}"
                    ])

        # Add methodology section
        md_content.extend([
            "\n## Metodología de Evaluación",
            "\nEsta evaluación se ha realizado siguiendo los criterios establecidos en la rúbrica oficial de UNIR para Trabajos Fin de Máster, considerando tres categorías principales:",
            "- **Estructura** (20%): Evalúa el formato académico y la organización del trabajo",
            "- **Contenido** (50%): Analiza la profundidad y calidad del trabajo académico",
            "- **Exposición** (30%): Valora la presentación y defensa del trabajo",
            "\n## Escala de Evaluación",
            "\nLos criterios de evaluación se basan en la siguiente escala:",
            "- **Sobresaliente (9-10)**: Trabajo excepcional que demuestra excelencia en todos los aspectos evaluados",
            "- **Notable (7-8)**: Trabajo que cumple con alto nivel la mayoría de los criterios establecidos",
            "- **Aprobado (5-6)**: Trabajo que alcanza los requisitos mínimos establecidos",
            "- **Suspenso (0-4)**: Trabajo que no cumple con los requisitos mínimos necesarios"
        ])

        # Add final feedback
        if "retroalimentacion" in results:
            md_content.extend([
                "\n## Observaciones Finales",
                results['retroalimentacion']
            ])

        return "\n".join(md_content)

    def save_results(self, results: Dict, output_dir: str) -> Tuple[Path, Path]:
        """
        Save grading results in both JSON and Markdown formats
        
        Args:
            results (Dict): Grading results to save
            output_dir (str): Directory path for output files
            
        Returns:
            Tuple[Path, Path]: Paths to the saved JSON and Markdown files
        """
        try:
            output_path = Path(output_dir)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_filename = f"evaluacion_tfm_{timestamp}"
            
            # Save JSON results
            json_path = output_path / f"{base_filename}.json"
            with json_path.open('w', encoding='utf-8') as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

            # Generate and save Markdown report
            markdown_path = output_path / f"{base_filename}.md"
            markdown_content = self.generate_markdown_report(results)
            with markdown_path.open('w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Create visualizations if historical data exists
            if self.historical_data:
                vis_dir = output_path / 'visualizaciones'
                vis_dir.mkdir(exist_ok=True)
                self.generate_comparative_visuals(results, str(output_path))

            return json_path, markdown_path

        except Exception as e:
            raise Exception(f"Error saving results: {str(e)}")


def main():
    # Get API key from environment variable
    api_key = environ.get("MI_CLAVE_API_ANTROPIC")
    
    if not api_key:
        raise ValueError("Anthropic API key not found in environment variables")
    
    try:
        # Initialize grader
        grader = UNIRDocumentGrader(api_key)
        
        # Let user select files and output directory using native macOS dialogs
        solution_path, rubric_path, output_dir = grader.select_files()
        
        # Grade solution
        results = grader.grade_solution(None, rubric_path, solution_path)
        
        # Save results in both formats
        json_path, markdown_path = grader.save_results(results, output_dir)
        
        print(f"""¡Evaluación completada con éxito!
            Resultados guardados en:
            - JSON: {json_path}
            - Markdown: {markdown_path}
            - Visualizaciones: {Path(output_dir) / 'visualizaciones'}""")
        
    except Exception as e:
        print(f"Error durante el proceso de evaluación: {str(e)}")

if __name__ == "__main__":
    main()