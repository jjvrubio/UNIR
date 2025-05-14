# Este documento tendrá que ir creciendo.
He creado un par de programas. Para auomatizar la generacion de las actas de los tribunales que particippo.
Las rúbricas son archivos excel (workbook) que contienen dos pestañas (worksheet). Una de ellas es la que contiene la rúbrica y se denomina Rubrica.
La forma sencilla es  copiar todas las rúbricas en el mismo directorio y ahí convertirlas a PDF que es lo que se requiere aportar.  Así he creado dos  automatizaciones:
1.	Appplescript para copiar los xlsx en un único directorio.
2.	VBA para generar los PDF desde Excel ya que puede controlar las condiciones de impresión.

Consideraciones no están en VS Code sino como scripts independientes. El de VBA tiene el incoveniente de que va incrustado en el workbook.
