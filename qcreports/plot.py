import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import cgriddb
import QCcolours

def generate_inputs_ixyz_nordics(tags, output_file_name="input_data.xlsx"):
    ids = cgriddb.get_jobid(comment=tags)    
    comments = cgriddb.get_comments(ids)
    wys = [int(w.split("=")[1]) for c in comments for w in c if w.startswith("wy=")]
    idx = np.argsort(wys)
    ids = ids[idx]
    zones = ["DK1", "DK2", "FI", "NO125", "NO3", "NO4", "SE1", "SE2", "SE3", "SE4"]
    index_names = ["wind_total_generation", "hydro_total_inflow", "mean_price"]
    with pd.ExcelWriter(output_file_name, engine="openpyxl") as writer:
        for idi in ids:
            root = cgriddb.get_result_dict(idi)
            wy = root.t0
            list_df = []
            for zone in zones:
                print(wy, zone)
                wind_names = root.resources.keys()
                wind_names = [n for n in wind_names if n.startswith("wind_") and n.endswith(f"_{zone}")]
                wind_total_generation = 0
                for wind_name in wind_names:
                    wind_total_generation += root.resources[wind_name].total_generation
                if f"hydro_{zone}" in root.hydro_resources.keys():
                    hydro_total_inflow = root.hydro_resources[f"hydro_{zone}"].inflow.sum()
                else:
                    hydro_total_inflow = 0
                mean_price = root.zones[zone].mean_price
                data = [wind_total_generation, hydro_total_inflow, mean_price]

                df = pd.DataFrame(data, columns=[zone], index=index_names)
                list_df.append(df)

            df = pd.concat(list_df, axis=1)
            df.to_excel(writer, sheet_name=wy)

def plot_scatter_ixyz(index, value_x, value_y, value_z, fc={}):
    if "cmap" in fc:
        if fc["cmap"] == "sequential":
            vmin, vmax = value_z.min(), value_z.max()      
            colors = QCcolours.QC_CMAP_COLOURS
        elif fc["cmap"] == "diverging":
            vam = abs(value_z).max()
            vmin, vmax = -vam, vam      
            colors = ["QC_green", "QC_blue", "QC_brown"]
    else:
        vmin, vmax = value_z.min(), value_z.max()      
        colors = QCcolours.QC_CMAP_COLOURS
    cmap = QCcolours.matplotlib_utils.make_cmap_range(colors)

    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_axisbelow(True)  
    ax.grid(True, zorder=0)
    sc = ax.scatter(value_x, value_y, c=value_z, s=75, cmap=cmap, vmin=vmin, vmax=vmax, zorder=1)
    cbar = plt.colorbar(sc)
    texts = []  
    for i in range(len(index)):
        txt = ax.text(value_x[i], value_y[i], str(int(index[i])), fontsize=8, ha='center', va='center', zorder=2)
        texts.append(txt)
    adjust_text(texts, ax=ax)
    #ax.set_box_aspect(1)    
    if "xlabel" in fc:
        ax.set_xlabel(fc["xlabel"])
    if "ylabel" in fc:
        ax.set_ylabel(fc["ylabel"])
    if "zlabel" in fc:
        cbar.set_label(fc["zlabel"])
    if "xlim" in fc:
        ax.set_xlim(fc["xlim"])
    if "ylim" in fc:
        ax.set_ylim(fc["ylim"])
    if "options" in fc:
        if "invert_cbar" in fc["options"]:
            cbar.ax.invert_yaxis()

    #plt.savefig("Figure_Years_v3.png", dpi=300)
#    plt.show()

    return fig, ax