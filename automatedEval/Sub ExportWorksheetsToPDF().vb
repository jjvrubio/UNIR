Sub ExportWorksheetsToPDF()
    Dim folderPath As String
    Dim fileName As String
    Dim wb As Workbook
    Dim ws As Worksheet
    Dim pdfPath As String

    ' Prompt user to select folder (macOS-compatible)
    folderPath = MacScript("return POSIX path of (choose folder with prompt ""Select the folder containing Excel files"")")

    If folderPath = "" Then Exit Sub

    ' Ensure folder path ends with slash
    If Right(folderPath, 1) <> "/" Then folderPath = folderPath & "/"

    fileName = Dir(folderPath & "*.xlsx")

    Do While fileName <> ""
        Set wb = Workbooks.Open(folderPath & fileName)
        
        On Error Resume Next
        Set ws = wb.Sheets("Rubrica") ' Change to your desired sheet name
        On Error GoTo 0
        
        If Not ws Is Nothing Then
            ws.Select
            
            With ws.PageSetup
                .Zoom = False
                .FitToPagesWide = 1
                .FitToPagesTall = 1
                .Orientation = xlPortrait
                .PaperSize = xlPaperA4
            End With
            
            pdfPath = folderPath & Replace(fileName, ".xlsx", ".pdf")
            ws.ExportAsFixedFormat Type:=xlTypePDF, fileName:=pdfPath, Quality:=xlQualityStandard
        End If
        
        wb.Close SaveChanges:=False
        fileName = Dir
    Loop

    MsgBox "PDF export complete!"
End Sub

