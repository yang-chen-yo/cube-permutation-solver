// web/main.js
async function main() {
    let pyodide = await loadPyodide();
    document.getElementById('status').innerText = "Python Environment Ready!";
    
    // 載入掛載腳本
    await pyodide.runPythonAsync(await (await fetch('scripts/mount_project.py')).text());
    await pyodide.runPythonAsync("from mount_project import mount_project; await mount_project()");
    
    document.getElementById('status').innerText = "Project Files Mounted Successfully!";
    window.pyodide = pyodide;
}
main();