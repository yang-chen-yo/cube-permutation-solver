# web/scripts/mount_project.py
import pyodide_js
import js

async def mount_project():
    # 這裡我們會把你的核心資料夾內容讀取並掛載到 Pyodide 的虛擬空間
    # 為了方便開發，我們先做一個簡單的清單映射
    files_to_mount = [
        'algorithms/base.py',
        'algorithms/batcher.py',
        'algorithms/bitonic.py',
        'utils/__init__.py',
        'utils/cube.py' # 確保你有這些檔案
    ]
    
    for path in files_to_mount:
        # 從網頁端讀取檔案內容並寫入虛擬檔案系統
        response = await js.fetch(f'../{path}')
        content = await response.text()
        
        # 在 Pyodide 裡面建立對應的目錄與檔案
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)