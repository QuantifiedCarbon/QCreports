import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
import cgriddb
import QCcolours

import plotly.express as px
import plotly.graph_objs as go
import ipywidgets as widgets
from IPython.display import display, clear_output
import plotly.colors as pc
from plotly.graph_objs import FigureWidget

def generate_inputs_ixyz_nordics(tags, output_file_name="input_data.xlsx"):
    ids = cgriddb.get_jobid(comment=tags)    
    comments = cgriddb.get_comments(ids)
    wys = [int(w.split("=")[1]) for c in comments for w in c if w.startswith("wy=")]
    idx = np.argsort(wys)
    ids = ids[idx]
    zones = ["DK1", "DK2", "FI", "NO125", "NO3", "NO4", "SE1", "SE2", "SE3", "SE4"]
    index_names = ["total_wind_generation", "total_hydro_inflow", "mean_price"]
    with pd.ExcelWriter(output_file_name, engine="openpyxl") as writer:
        for idi in ids:
            root = cgriddb.get_result_dict(idi)
            wy = root.t0
            list_df = []
            for zone in zones:
                print(wy, zone)
                wind_names = root.resources.keys()
                wind_names = [n for n in wind_names if n.startswith("wind_") and n.endswith(f"_{zone}")]
                total_wind_generation = 0
                for wind_name in wind_names:
                    total_wind_generation += root.resources[wind_name].total_generation
                if f"hydro_{zone}" in root.hydro_resources.keys():
                    total_hydro_inflow = root.hydro_resources[f"hydro_{zone}"].inflow.sum()
                else:
                    total_hydro_inflow = 0
                mean_price = root.zones[zone].mean_price
                data = [total_wind_generation, total_hydro_inflow, mean_price]

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

def dashboard(file):
    # Extract file paths and labels
    file1 = file.iloc[0, 0]
    file2 = file.iloc[0, 1]
    label1 = file.columns[0]
    label2 = file.columns[1]

    # Widgets
    sheet_dropdown = widgets.Dropdown(description='Parameter:', layout=widgets.Layout(width='300px'))
    checkboxes_container = widgets.HBox()
    output = widgets.Output()
    all_checkbox = widgets.Checkbox(value=True, description="All")

    # Read Excel data
    data1 = pd.read_excel(file1, sheet_name=None, engine='openpyxl')
    data2 = pd.read_excel(file2, sheet_name=None, engine='openpyxl')

    skip_sheets = {"Report", "Plot Summary", "Runtime Warnings"}
    common_sheets = sorted(set(data1.keys()) & set(data2.keys()))
    filtered_sheets = [s for s in common_sheets if s not in skip_sheets]

    sheet_dropdown.options = filtered_sheets
    if filtered_sheets:
        sheet_dropdown.value = filtered_sheets[0]

    colors = px.colors.qualitative.Plotly

    # Track checkbox updates to avoid recursion
    updating_checkboxes = False
    current_fig = FigureWidget()

    def create_checkboxes(columns):
        return [widgets.Checkbox(value=True, description=col) for col in columns]

    def update_plot(sheet):
        nonlocal current_fig
        current_fig = FigureWidget()

        df1 = data1[sheet].copy()
        df2 = data2[sheet].copy()

        x1 = df1.iloc[:, 0]
        x2 = df2.iloc[:, 0]

        # Get base column (year, etc.)
        index_col = df1.columns[0]

        # Get all subparameters (columns except the first)
        params1 = set(df1.columns[1:])
        params2 = set(df2.columns[1:])
        all_params = sorted(params1.union(params2))

        # Add missing columns filled with NaN
        for param in all_params:
            if param not in df1.columns:
                df1[param] = np.nan
            if param not in df2.columns:
                df2[param] = np.nan

        # Ensure the column order is consistent
        df1 = df1[[index_col] + all_params]
        df2 = df2[[index_col] + all_params]

#        df1 = data1[sheet]
#        df2 = data2[sheet]
#        x1 = df1.iloc[:, 0]
#        x2 = df2.iloc[:, 0]
        selected = [cb.description for cb in checkboxes_container.children[1:] if cb.value]

        sheet_lower = sheet.lower()
        is_gen_cap = sheet_lower.startswith("generation_capacity")
        is_balance = sheet_lower.startswith("balance")

        if is_gen_cap:
            colour_dict = QCcolours.bake_resources(selected)
            for i, sub in enumerate(selected):
                fill_color = colour_dict[sub].colour
                current_fig.add_trace(go.Bar(x=x1, y=df1[sub], name=f"{label1}: {sub}",
                                             marker=dict(color=fill_color), offsetgroup=0, legendgroup=sub))
                current_fig.add_trace(go.Bar(x=x2, y=df2[sub], name=f"{label2}: {sub}",
                                             marker=dict(color=fill_color), offsetgroup=1,
                                             marker_pattern_shape="/", legendgroup=sub))
#                border_color = colour_dict[sub].border
#                current_fig.add_trace(go.Bar(x=x1, y=df1[sub], name=f"{label1}: {sub}",
#                                             marker=dict(color=fill_color, line=dict(color=border_color, width=1)), offsetgroup=0, legendgroup=sub))
#                current_fig.add_trace(go.Bar(x=x2, y=df2[sub], name=f"{label2}: {sub}",
#                                             marker=dict(color=fill_color, line=dict(color=border_color, width=1)), offsetgroup=1,
#                                             marker_pattern_shape="/", legendgroup=sub))
            current_fig.update_layout(barmode='stack')

        elif is_balance:
            bar_subs = [s for s in selected if s.lower() != "demand"]
            line_subs = [s for s in selected if s.lower() == "demand"]
            colour_dict = QCcolours.bake_resources(bar_subs)

            for i, sub in enumerate(bar_subs):
                fill_color = colour_dict[sub].colour
                current_fig.add_trace(go.Bar(x=x1, y=df1[sub], name=f"{label1}: {sub}",
                                             marker=dict(color=fill_color), offsetgroup=0, legendgroup=sub))
                current_fig.add_trace(go.Bar(x=x2, y=df2[sub], name=f"{label2}: {sub}",
                                             marker=dict(color=fill_color), offsetgroup=1,
                                             marker_pattern_shape="/", legendgroup=sub))
#                border_color = colour_dict[sub].border
#                current_fig.add_trace(go.Bar(x=x1, y=df1[sub], name=f"{label1}: {sub}",
#                                             marker=dict(color=fill_color, line=dict(color=border_color, width=1)), offsetgroup=0, legendgroup=sub))
#                current_fig.add_trace(go.Bar(x=x2, y=df2[sub], name=f"{label2}: {sub}",
#                                             marker=dict(color=fill_color, line=dict(color=border_color, width=1)), offsetgroup=1,
#                                             marker_pattern_shape="/", legendgroup=sub))
            for sub in line_subs:
                current_fig.add_trace(go.Scatter(x=x1, y=df1[sub], name=f"{label1}: {sub}",
                                                 mode='lines+markers', line=dict(color='black', dash='solid'),
                                                 marker=dict(symbol='triangle-up', size=10)))
                current_fig.add_trace(go.Scatter(x=x2, y=df2[sub], name=f"{label2}: {sub}",
                                                 mode='lines+markers', line=dict(color='black', dash='dash'),
                                                 marker=dict(symbol='triangle-down', size=10)))
            current_fig.update_layout(barmode='stack')

        else:
            for i, sub in enumerate(selected):
                color = colors[i % len(colors)]
                current_fig.add_trace(go.Scatter(x=x1, y=df1[sub], name=f"{label1}: {sub}",
                                                 mode='lines+markers', line=dict(color=color, dash='solid'),
                                                 marker=dict(symbol='triangle-up', size=10)))
                current_fig.add_trace(go.Scatter(x=x2, y=df2[sub], name=f"{label2}: {sub}",
                                                 mode='lines+markers', line=dict(color=color, dash='dash'),
                                                 marker=dict(symbol='triangle-down', size=10)))

        current_fig.update_layout(title=sheet, template='plotly_white', legend_title="Legend")

        with output:
            clear_output(wait=True)
            display(current_fig)

    def update_checkboxes(sheet):
        df = data1[sheet]
        columns = [c for c in df.columns[1:] if not str(c).startswith("Unnamed")]
        boxes = create_checkboxes(columns)

        for box in boxes:
            box.observe(on_individual_checkbox_change, names='value')

        all_checkbox.observe(on_all_checkbox_change, names='value')

        checkboxes_container.children = [all_checkbox] + boxes
        all_checkbox.value = True  # Reset all to true

    def on_sheet_change(change):
        sheet = change['new']
        update_checkboxes(sheet)
        update_plot(sheet)

    def update_trace_visibility():
        selected = [cb.description for cb in checkboxes_container.children[1:] if cb.value]
        visibility = []
        for cb in checkboxes_container.children[1:]:
            show = cb.description in selected
            visibility.append(show)  # for label1 trace
            visibility.append(show)  # for label2 trace

        for i, vis in enumerate(visibility):
            current_fig.data[i].visible = vis

    def on_all_checkbox_change(change):
        nonlocal updating_checkboxes
        if change['name'] == 'value':
            updating_checkboxes = True
            for cb in checkboxes_container.children[1:]:
                cb.value = change['new']
            updating_checkboxes = False
            update_trace_visibility()  # <-- Only update visibility

    def on_individual_checkbox_change(change):
        nonlocal updating_checkboxes
        if updating_checkboxes:
            return
        all_checked = all(cb.value for cb in checkboxes_container.children[1:])
        updating_checkboxes = True
        if all_checkbox.value != all_checked:
            all_checkbox.unobserve(on_all_checkbox_change, names='value')
            all_checkbox.value = all_checked
            all_checkbox.observe(on_all_checkbox_change, names='value')
        updating_checkboxes = False
        update_trace_visibility()  # <-- Only update visibility


    # Initial setup
    sheet_dropdown.observe(on_sheet_change, names='value')
    update_checkboxes(sheet_dropdown.value)
    update_plot(sheet_dropdown.value)

    return widgets.VBox([
        widgets.HBox([sheet_dropdown, checkboxes_container]),
        output
    ])