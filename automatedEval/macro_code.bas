
Sub ExportWorksheetsToPDF()
    Dim folderPath As String
    Dim fileName As String
    Dim wb As Workbook
    Dim ws As Worksheet
    Dim pdfPath As String

    ' Solicita al usuario seleccionar una carpeta (compatible con macOS)
    On Error Resume Next
    folderPath = MacScript("return POSIX path of (choose folder with prompt ""Selecciona la carpeta que contiene los archivos Excel"")")
    On Error GoTo 0

    If folderPath = "" Then
        MsgBox "No se seleccionó ninguna carpeta.", vbExclamation
        Exit Sub
    End If

    ' Asegura que la ruta termine con "/"
    If Right(folderPath, 1) <> "/" Then folderPath = folderPath & "/"

    ' Busca archivos .xlsx en la carpeta
    fileName = Dir(folderPath & "*.xlsx")

    If fileName = "" Then
        MsgBox "No se encontraron archivos .xlsx en la carpeta seleccionada.", vbInformation
        Exit Sub
    End If

    ' Procesa cada archivo
    Do While fileName <> ""
        Set wb = Workbooks.Open(folderPath & fileName)
        Set ws = Nothing ' Limpia la variable antes de buscar la hoja

        On Error Resume Next
        Set ws = wb.Sheets("Rubrica") ' Cambia el nombre si es necesario
        On Error GoTo 0

        If Not ws Is Nothing Then
            ' Configura la hoja para impresión
            With ws.PageSetup
                .Zoom = False
                .FitToPagesWide = 1
                .FitToPagesTall = 1
                .Orientation = xlPortrait
                .PaperSize = xlPaperA4
            End With

            ' Exporta como PDF
            pdfPath = folderPath & Replace(fileName, ".xlsx", ".pdf")
            ws.ExportAsFixedFormat Type:=xlTypePDF, fileName:=pdfPath, Quality:=xlQualityStandard
        Else
            MsgBox "La hoja 'Rubrica' no se encontró en: " & fileName, vbExclamation
        End If

        wb.Close SaveChanges:=False
        fileName = Dir ' Siguiente archivo
    Loop

    MsgBox "¡Exportación a PDF completada!", vbInformation
End Sub
