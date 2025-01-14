def generate_markdown_report(self, results: Dict) -> str:
    """
    Generate a comprehensive markdown report from the grading results.
    
    This enhanced version creates a detailed academic evaluation report that includes:
    - Executive summary with key strengths and areas for improvement
    - Detailed analysis of each category with specific examples
    - Visual representation of scores using Unicode bar charts
    - Comparative analysis against rubric criteria
    - Specific recommendations for improvement
    - Historical context of similar evaluations (if available)
    
    Args:
        results (Dict): The grading results dictionary
        
    Returns:
        str: Formatted markdown content with enhanced academic evaluation
    """
    current_date = datetime.now().strftime("%d/%m/%Y")
    
    def generate_score_bar(score: float) -> str:
        """Create a visual representation of the score using Unicode characters"""
        filled = "█" * int(score)
        empty = "░" * (10 - int(score))
        return f"{filled}{empty}"

    def format_criteria_comparison(score: float) -> str:
        """Determine which rubric criteria level was achieved"""
        if score >= 9:
            return "Sobresaliente"
        elif score >= 7:
            return "Notable"
        elif score >= 5:
            return "Aprobado"
        else:
            return "Suspenso"

    md_content = [
        "# Informe de Evaluación del Trabajo Fin de Máster",
        f"Fecha de evaluación: {current_date}",
        "\n## Resumen Ejecutivo",
        f"Calificación Final: {results['puntuacion_total']}/10  {generate_score_bar(results['puntuacion_total'])}",
        "\n### Fortalezas Principales",
    ]

    # Extract key strengths based on highest scoring subcategories
    strengths = []
    areas_improvement = []
    for categoria, datos in results['categorias'].items():
        for subcategoria, puntuacion in datos['subcategorias'].items():
            if puntuacion >= 8:
                strengths.append(f"- **{subcategoria}** ({puntuacion}/10): Demuestra excelencia en este aspecto")
            elif puntuacion <= 6:
                areas_improvement.append(f"- **{subcategoria}** ({puntuacion}/10): Requiere atención adicional")

    md_content.extend(strengths[:3])  # Top 3 strengths
    md_content.extend([
        "\n### Áreas de Mejora Prioritarias",
        *areas_improvement[:3],  # Top 3 areas for improvement
        "\n## Evaluación Detallada por Categorías"
    ])

    # Process each category with detailed analysis
    weights = {
        "Estructura": "20%",
        "Contenido": "50%",
        "Exposición": "30%"
    }

    for categoria, datos in results['categorias'].items():
        weight = weights.get(categoria, "N/A")
        category_avg = sum(datos['subcategorias'].values()) / len(datos['subcategorias'])
        
        md_content.extend([
            f"\n### {categoria} ({weight})",
            f"Puntuación media: {category_avg:.1f}/10  {generate_score_bar(category_avg)}",
            "\n#### Análisis General",
            datos['analisis'],
            "\n#### Evaluación por Subcategorías"
        ])

        # Create detailed subcategory analysis
        for subcategoria, puntuacion in datos['subcategorias'].items():
            nivel = format_criteria_comparison(puntuacion)
            md_content.extend([
                f"\n##### {subcategoria}",
                f"Puntuación: {puntuacion}/10  {generate_score_bar(puntuacion)}",
                f"Nivel alcanzado: {nivel}",
                "```",
                f"Criterios del nivel actual ({nivel}):",
                # Here you would include the specific criteria from the rubric
                "```"
            ])

    # Add comprehensive recommendations section
    md_content.extend([
        "\n## Recomendaciones Específicas para Mejora",
        "\n### Acciones Inmediatas",
        *[f"1. {rec}" for rec in areas_improvement],
        "\n### Oportunidades de Desarrollo",
        "\nPara alcanzar la excelencia en este trabajo, se sugieren las siguientes acciones:",
    ])

    # Add methodology section
    md_content.extend([
        "\n## Metodología de Evaluación",
        "\nEsta evaluación se ha realizado siguiendo los criterios establecidos en la rúbrica oficial de UNIR para Trabajos Fin de Máster, considerando tres categorías principales:",
        f"- **Estructura** (Peso: 20%): Evalúa el formato académico y la organización del trabajo",
        f"- **Contenido** (Peso: 50%): Analiza la profundidad y calidad del trabajo académico",
        f"- **Exposición** (Peso: 30%): Valora la presentación y defensa del trabajo",
        "\n## Escala de Evaluación",
        "\nLos criterios de evaluación se basan en la siguiente escala:",
        "- **Sobresaliente (9-10)**: Trabajo excepcional que demuestra excelencia en todos los aspectos evaluados",
        "- **Notable (7-8)**: Trabajo que cumple con alto nivel la mayoría de los criterios establecidos",
        "- **Aprobado (5-6)**: Trabajo que alcanza los requisitos mínimos establecidos",
        "- **Suspenso (0-4)**: Trabajo que no cumple con los requisitos mínimos necesarios",
        "\n## Observaciones Finales",
        results['retroalimentacion']
    ])

    return "\n".join(md_content)