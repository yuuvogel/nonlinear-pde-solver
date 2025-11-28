import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
import os
import glob
import re

# --- Configuration: 2つのターゲットを定義 ---
TARGETS = [
    {
        "name": "baseline",
        "input_dir": "./results_baseline/",
        "output_gif": "baseline_demo.gif"
    },
    {
        "name": "improved",
        "input_dir": "./results_improved/",
        "output_gif": "improved_demo.gif"
    }
]

FILE_PATTERN = 'solution_*.csv'

def get_iteration_from_filename(fname):
    match = re.search(r'solution_(\d+).csv', fname)
    return int(match.group(1)) if match else -1

def create_animation(target):
    name = target["name"]
    input_dir = target["input_dir"]
    output_gif = target["output_gif"]

    print(f"--- Processing: {name} ---")
    
    if not os.path.exists(input_dir):
        print(f"Skipping {name}: Directory {input_dir} not found.")
        return

    search_path = os.path.join(input_dir, FILE_PATTERN)
    file_list = glob.glob(search_path)
    
    # 数値順にソート
    file_list = [f for f in file_list if get_iteration_from_filename(f) != -1]
    file_list.sort(key=get_iteration_from_filename)
    
    if not file_list:
        print(f"Skipping {name}: No csv files found in {input_dir}")
        return

    print(f"Found {len(file_list)} files. Generating GIF...")

    # データ読み込み
    z_values_list = []
    
    # 最初のファイルでメッシュ作成
    first_data = pd.read_csv(file_list[0], header=None).values
    x = first_data[:, 0]
    y = first_data[:, 1]
    tri = mtri.Triangulation(x, y)

    for fname in file_list:
        df = pd.read_csv(fname, header=None).values
        z_values_list.append(df[:, 2])

    # カラーバー固定用
    z_min = min(z.min() for z in z_values_list)
    z_max = max(z.max() for z in z_values_list)

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    def update_plot(frame_idx):
        ax.clear()
        z_data = z_values_list[frame_idx]
        current_iter = get_iteration_from_filename(file_list[frame_idx])
        
        surf = ax.plot_trisurf(tri, z_data, cmap=plt.cm.jet, 
                             linewidth=0.2, antialiased=True, 
                             vmin=z_min, vmax=z_max)
        
        ax.set_title(f"[{name.upper()}] Iteration: {current_iter}", fontsize=16)
        ax.set_zlabel('u')
        ax.view_init(elev=30, azim=-60 + frame_idx * 2)
        return surf,

    ani = animation.FuncAnimation(fig, update_plot, frames=len(file_list), interval=300)
    ani.save(output_gif, writer='pillow', fps=4)
    print(f"Saved: {output_gif}")
    plt.close(fig) # メモリ解放

def main():
    for target in TARGETS:
        create_animation(target)
    print("\nAll done!")

if __name__ == "__main__":
    main()
