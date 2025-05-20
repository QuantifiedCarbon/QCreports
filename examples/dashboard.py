import numpy as np
import pandas as pd
import QCcolours
import plotly.express as px
import plotly.graph_objs as go
import ipywidgets as widgets
from IPython.display import display, clear_output
from plotly.graph_objs import FigureWidget

def generate(file):
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