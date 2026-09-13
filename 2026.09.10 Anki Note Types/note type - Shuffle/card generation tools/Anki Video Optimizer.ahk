; Anki Video Optimizer.ahk - do not delete or modify this line. v4
#Requires AutoHotkey v2.0

; --- CONFIGURATION ---
; If ffmpeg is in your System PATH, leave as "ffmpeg.exe".
; Otherwise, replace with full path like "C:\ffmpeg\bin\ffmpeg.exe"
ffmpegPath := "ffmpeg.exe"

; Set to true to show the command prompt terminal with live FFmpeg logs.
; Set to false to run silently in the background.
enableDebug := false

; YouTube loudness target (-14 LUFS, -1.0 dBTP)
audioFilter := "loudnorm=I=-14:TP=-1.0:LRA=11"

; --- GUI SETUP ---
myGui := Gui("+AlwaysOnTop", "Anki Video Optimizer (WebM)")
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
    outputFile := dir . "\" . nameNoExt . "_anki.webm"

    ; Clean scale filter string to prevent AHK quotation escaping issues
    scaleFilter := "scale=-2:'min(720,ih)'"

    ; -b:v 0 combined with -crf 32 enables pure quality-based encoding without forcing a target bitrate floor
    cmd := '"' . ffmpegPath . '" -i "' . inputFile .
        '" -vf "' . scaleFilter .
        '" -c:v libvpx-vp9 -crf 32 -b:v 0 -row-mt 1 -pix_fmt yuv420p ' .
        '-af "' . audioFilter .
        '" -c:a libopus -b:a 96k -y "' .
        outputFile . '"'

    ; Toggle window visibility based on enableDebug
    hideWindow := enableDebug ? "" : "Hide"

    ToolTip("Compressing video & normalizing audio to -14 LUFS...")
    RunWait(A_ComSpec . ' /c "' . cmd . '"', , hideWindow)
    ToolTip()

    MsgBox("Done! Optimized WebM saved to:`n" . outputFile, "Anki Video Optimizer", "Iconi")
}
