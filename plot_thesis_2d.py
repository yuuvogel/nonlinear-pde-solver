import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import matplotlib.ticker as ticker
import os

# --- Configuration ---
TARGETS = [
    {
        "title": "Baseline Method (Final)",
        "input_dir": "./results_baseline/",
        "sol_file": "solution_final.csv",
        "tri_file": "mesh_tri.csv", # メッシュ情報ファイル
        "output_img": "final_plot_2d.png"
    },
    {
        "title": "Improved Method (Hybrid Final)",
        "input_dir": "./results_improved/",
        "sol_file": "solution_final.csv",
        "tri_file": "mesh_tri.csv", # メッシュ情報ファイル
        "output_img": "final_plot_2d.png"
    }
]

def plot_and_save(target):
    input_dir = target["input_dir"]
    sol_path = os.path.join(input_dir, target["sol_file"])
    tri_path = os.path.join(input_dir, target["tri_file"])
    output_img_path = os.path.join(input_dir, target["output_img"])
    title_text = target["title"]

    print(f"--- Processing: {title_text} ---")

    if not os.path.exists(sol_path):
        print(f"Skipping: {sol_path} not found.")
        return
    if not os.path.exists(tri_path):
        print(f"Skipping: {tri_path} not found. (Mesh data missing)")
        return

    # 1. 解データ（頂点座標と値）の読み込み
    try:
        # header=None想定: 0:x, 1:y, 2:u
        data = pd.read_csv(sol_path, header=None).values
        x = data[:, 0]
        y = data[:, 1]
        z = data[:, 2]
    except Exception as e:
        print(f"Error reading solution: {e}")
        return

    # 2. メッシュ情報（三角形のつながり）の読み込み
    try:
        # header=None想定: 0:v1, 1:v2, 2:v3 (頂点インデックス)
        triangles = pd.read_csv(tri_path, header=None).values.astype(int)
    except Exception as e:
        print(f"Error reading mesh: {e}")
        return

    # 3. 三角形分割 (元のコードと同じく triangles= を指定)
    # これによりFreeFEMと同じ正しい穴あき形状になります
    tri = mtri.Triangulation(x, y, triangles=triangles)

    # --- プロット設定 ---
    fig, ax = plt.subplots(figsize=(8, 7))

    z_min = z.min()
    z_max = z.max()
    if z_max - z_min < 1e-9:
        levels = np.linspace(z_min - 1e-9, z_max + 1e-9, 12)
    else:
        levels = np.linspace(z_min, z_max, 12)

    # 等高線プロット
    contour = ax.tricontourf(tri, z, levels=levels, cmap=plt.cm.jet)
    ax.tricontour(tri, z, levels=levels, colors='black', linewidths=0.5)

    # カラーバー
    cbar = plt.colorbar(contour, ax=ax, shrink=0.9)
    cbar.set_label('u value', fontsize=14)
    cbar.ax.tick_params(labelsize=12)
    
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((0, 0))
    cbar.ax.yaxis.set_major_formatter(formatter)
    cbar.update_ticks()

    try:
        max_abs_z = max(abs(z_max), abs(z_min))
        if max_abs_z < 1e-9: exp = 0
        else: exp = int(np.floor(np.log10(max_abs_z)))
        cbar.ax.yaxis.offsetText.set_text(f"$10^{{{exp}}}$")
        cbar.ax.yaxis.offsetText.set_size(14)
    except Exception:
        pass

    ax.set_xlabel('x', fontsize=14)
    ax.set_ylabel('y', fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_aspect('equal')
    ax.set_title(title_text, fontsize=16)

    plt.tight_layout()
    plt.savefig(output_img_path, dpi=300)
    print(f"Saved plot to: {output_img_path}")
    plt.close(fig)

def main():
    for target in TARGETS:
        plot_and_save(target)
    print("\nAll 2D plots generated.")

if __name__ == "__main__":
    main()