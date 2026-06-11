# main.py
import subprocess

def main():
    print("=== 開始執行超立方體路由完整實驗作業 ===")

    print("\n[步驟 1 & 2] 跑所有維度實驗 (3D 全排列 + 選定測資)...")
    subprocess.run(["python", "experiments/run_experiments.py"])

    print("\n[步驟 3] 整合分析並輸出數據報表...")
    subprocess.run(["python", "experiments/compare.py"])

    print("\n[步驟 4] 繪製分佈圖形...")
    subprocess.run(["python", "analysis/plot.py"])

    print("\n🎉 所有實驗已全部完成！請查閱控制台輸出、data/ 目錄與 analysis/ 圖檔。")

if __name__ == "__main__":
    main()