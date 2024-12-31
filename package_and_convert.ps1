# 既存のファイルを削除
Remove-Item -Path "pyxel_test.pyxapp" -ErrorAction SilentlyContinue
Remove-Item -Path "index.html" -ErrorAction SilentlyContinue

# main.pyをpyxappにパッケージ化
pyxel package . main.py

# pyxappファイルの存在を確認
if (Test-Path -Path "pyxel_test.pyxapp") {
    # pyxappをHTMLに変換
    pyxel app2html pyxel_test.pyxapp

    # HTMLファイルの存在を確認
    if (Test-Path -Path "pyxel_test.html") {
        # HTMLファイルをindex.htmlにリネーム
        Rename-Item -Path "pyxel_test.html" -NewName "index.html"

        # index.html内のgamepad設定を変更
        (Get-Content -Path "index.html") -replace 'gamepad: "enabled"', 'gamepad: "disabled"' | Set-Content -Path "index.html"
    }
    else {
        Write-Host "Error: pyxel_test.html not found"
    }
}
else {
    Write-Host "Error: pyxel_test.pyxapp not found"
}