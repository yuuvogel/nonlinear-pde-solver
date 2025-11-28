import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import matplotlib.ticker as ticker
import os

# --- Configuration: 2つのターゲットを定義 ---
TARGETS = [
    {
        "title": "Baseline Method (Final)",
        "input_dir": "./results_baseline/",
        "file_name": "solution_final.csv",
        "output_img": "final_plot_2d.png"
    },
    {
        "title": "Improved Method (Hybrid Final)",
        "input_dir": "./results_improved/",
        "file_name": "solution_final.csv",
        "output_img": "final_plot_2d.png"
    }
]

def plot_and_save(target):
    input_dir = target["input_dir"]
    file_name = target["file_name"]
    output_img_name = target["output_img"]
    title_text = target["title"]

    target_file_path = os.path.join(input_dir, file_name)
    output_img_path = os.path.join(input_dir, output_img_name)

    print(f"--- Processing: {title_text} ---")

    if not os.path.exists(target_file_path):
        print(f"Skipping: File {target_file_path} not found. Please run the corresponding .edp solver first.")
        return

    # データの読み込み
    try:
        data = pd.read_csv(target_file_path, header=None).values
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]
    except Exception as e:
        print(f"Error reading {target_file_path}: {e}")
        return

    # 三角形分割
    tri = mtri.Triangulation(x, y)

    # プロット設定
    fig, ax = plt.subplots(figsize=(8, 7))

    # Z値の範囲取得と等高線レベル設定
    z_min = z.min()
    z_max = z.max()
    # 値の範囲が極端に小さい場合の対策
    if z_max - z_min < 1e-9:
        levels = np.linspace(z_min - 1e-9, z_max + 1e-9, 12)
    else:
        levels = np.linspace(z_min, z_max, 12)

    # 1. 等高線プロット（塗りつぶし）: Jetカラー
    contour = ax.tricontourf(tri, z, levels=levels, cmap=plt.cm.jet)
    
    # 2. 等高線の境界線: 黒色で細く
    ax.tricontour(tri, z, levels=levels, colors='black', linewidths=0.5)

    # カラーバーの設定
    cbar = plt.colorbar(contour, ax=ax, shrink=0.9)
    cbar.set_label('u value', fontsize=14)
    cbar.ax.tick_params(labelsize=12)
    
    # 指数表記の設定
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0, 0))
    cbar.ax.yaxis.set_major_formatter(formatter)
    cbar.update_ticks()

    try:
        # 最大値の絶対値で指数を決定（0付近対策）
        max_abs_z = max(abs(z_max), abs(z_min))
        if max_abs_z < 1e-9: exp = 0
        else: exp = int(np.floor(np.log10(max_abs_z)))
        
        cbar.ax.yaxis.offsetText.set_text(f"$10^{{{exp}}}$")
        cbar.ax.yaxis.offsetText.set_size(14)
    except Exception:
        pass

    # ラベルとタイトルの設定
    ax.set_xlabel('x', fontsize=14)
    ax.set_ylabel('y', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_aspect('equal')
    ax.set_title(title_text, fontsize=16)

    plt.tight_layout()
    
    # 画像として保存
    plt.savefig(output_img_path, dpi=300)
    print(f"Saved plot to: {output_img_path}")
    plt.close(fig) # メモリ解放

def main():
    for target in TARGETS:
        plot_and_save(target)
    print("\nAll 2D plots generated.")

if __name__ == "__main__":
    main()
