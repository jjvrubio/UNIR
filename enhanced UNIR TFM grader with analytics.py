import os
import json
import PyPDF2
from typing import Dict, List, Optional
import anthropic
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

class UNIRDocumentGrader:
    def __init__(self, api_key: str, historical_data_path: Optional[str] = None):
        """
        Initialize the UNIR TFM grader with enhanced analytics capabilities
        
        Args:
            api_key (str): The Anthropic API key for authentication
            historical_data_path (str, optional): Path to historical evaluations JSON file
        """
        self.client = anthropic.Client(api_key)
        self.historical_data = self.load_historical_data(historical_data_path) if historical_data_path else None
        
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
        
        # Generate category comparisons
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
            
        # Create visualizations directory
        vis_dir = Path(output_dir) / 'visualizaciones'
        vis_dir.mkdir(exist_ok=True)
        
        # Generate score distribution plot
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

    def generate_questions(self, results: Dict) -> str:
        """Generate follow-up questions based on the evaluation results"""
        # This will be implemented in a separate artifact
        pass

    def save_results(self, results: Dict, output_base_path: str):
        """
        Save enhanced grading results in multiple formats
        
        Args:
            results (Dict): Grading results to save
            output_base_path (str): Base path for output files
        """
        output_dir = Path(output_base_path).parent
        
        # Add timestamp and trend analysis
        results['fecha'] = datetime.now().strftime("%d/%m/%Y")
        results['analisis_tendencias'] = self.perform_trend_analysis(results)
        
        # Generate visualizations
        self.generate_comparative_visuals(results, output_dir)
        
        # Save JSON results
        json_path = output_dir / f"{Path(output_base_path).name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        # Generate and save enhanced markdown report
        markdown_path = output_dir / f"{Path(output_base_path).name}.md"
        markdown_content = self.generate_markdown_report(results)
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        # Update historical data if available
        if self.historical_data is not None:
            self.historical_data.append(results)
            with open(output_dir / 'historical_evaluations.json', 'w', encoding='utf-8') as f:
                json.dump(self.historical_data, f, indent=4, ensure_ascii=False)

        return json_path, markdown_path