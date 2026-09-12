; Anki Video Optimizer.ahk - do not delete or modify this line. v1
#Requires AutoHotkey v2.0

; --- CONFIGURATION ---
; If ffmpeg is in your System PATH, leave as "ffmpeg.exe".
; Otherwise, replace with full path like "C:\ffmpeg\bin\ffmpeg.exe"
ffmpegPath := "ffmpeg.exe"

; --- GUI SETUP ---
myGui := Gui("+AlwaysOnTop", "Anki Video Optimizer")
myGui.SetFont("s10", "Segoe UI")
myGui.Add("Text", "w320 Center", "Drag & drop a video file here`nor click the button below:")
btnSelect := myGui.Add("Button", "w320 h35", "Select Video File")
btnSelect.OnEvent("Click", SelectFile)
myGui.OnEvent("DropFiles", OnDropFiles)
myGui.Show()

SelectFile(*) {
    selectedFile := FileSelect(1, , "Select Video to Compress", "Video Files (*.mp4; *.mov; *.mkv; *.webm; *.avi)")
    if (selectedFile != "") {
        ProcessVideo(selectedFile)
    }
}

OnDropFiles(guiObj, dropTarget, files, x, y) {
    for filePath in files {
        ProcessVideo(filePath)
        break ; Processes the first dropped file
    }
}

ProcessVideo(inputFile) {
    SplitPath(inputFile, &fileName, &dir, &ext, &nameNoExt)
    outputFile := dir . "\" . nameNoExt . "_anki.mp4"

    ; Recommended Anki Target Command (720p, CRF 26, AAC 96k)
    cmd := '"' . ffmpegPath . '" -i "' . inputFile .
        '" -vf "scale=-2:720" -c:v libx264 -crf 26 -preset faster -c:a aac -b:a 96k -y "' . outputFile . '"'

    ToolTip("Compressing video for Anki...")
    RunWait(A_ComSpec . ' /c "' . cmd . '"', , "Hide")
    ToolTip()

    MsgBox("Done! Optimized file saved to:`n" . outputFile, "Anki Video Optimizer", "Iconi")
}
