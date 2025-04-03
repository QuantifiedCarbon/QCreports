import numpy as np
import pandas as pd
import QCplots
import qcmaps.plot as qcmp
from qcreports.utils import get_df_from_worksheet, get_bake_resources
QCplots.qc_settings.QC_PLOT_BORDER = None

def make_report_data(worksheets, output_file_name="report_data.xlsx"):
    with pd.ExcelWriter(output_file_name, engine="openpyxl") as writer:
        for worksheet in worksheets:
            sheet_name = worksheet["sheet_name"]
            df = worksheet["df"]
            plot_definitions = worksheet["plot_definitions"]
            method = plot_definitions["method"]
            plot_definitions = pd.DataFrame({
                "": plot_definitions.keys(),
                "plot_definitions": plot_definitions.values(),
            })
            plot_definitions = plot_definitions.set_index(plot_definitions.columns[0])
            if method.startswith("combo_"):
                df1 = df[0]
                df2 = df[1]
                df1.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
                df2.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=df1.shape[1] + 2)
                plot_definitions.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=df1.shape[1] + df2.shape[1] + 4)
            else:
                df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
                plot_definitions.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=df.shape[1] + 2)

def focus_report_data(zones, input_file_name="report_data.xlsx", output_file_name=None):
    zones = np.sort(zones)
    xls = pd.ExcelFile(input_file_name)
    sheet_names = xls.sheet_names
    keep_sheet_names_zones = [sheet_name for sheet_name in sheet_names if sheet_name.endswith(tuple(zones))]
    remove_start_with = [sheet_name.rsplit("_", 1)[0] for sheet_name in keep_sheet_names_zones]
    remove_start_with = list(set(remove_start_with))  
    keep_sheet_names_combined = [sheet_name for sheet_name in sheet_names if not sheet_name.startswith(tuple(remove_start_with))]
    keep_sheet_names = keep_sheet_names_zones + keep_sheet_names_combined
    if output_file_name is None:
        output_file_name = input_file_name.split(".")[0] + "_focus.xlsx"
    with pd.ExcelWriter(output_file_name, engine="openpyxl") as writer:
        for sheet_name in sheet_names:
            if sheet_name in keep_sheet_names:
                plot_definitions, df = get_df_from_worksheet(xls, sheet_name)
                method = plot_definitions.loc["plot_definitions", "method"]
                plot_definitions = plot_definitions.T
                if method.startswith("combo_"):
                    df1 = df[0]
                    df2 = df[1]
                    if sheet_name in keep_sheet_names_combined:
                        if any(zone in df2.columns for zone in zones):
                            columns = [zone for zone in zones if zone in df2.columns]
                            df2 = df2[columns]
                        elif any(transmission.startswith(zone) for transmission in df2.columns for zone in zones) * any(transmission.endswith(zone) for transmission in df2.columns for zone in zones):
                            columns = [
                                column for column in df2.columns 
                                if all(zone in zones for zone in column.split("_"))]
                            df2 = df2[columns]
                        else:
                            continue
                    df1 = df1.sort_index(axis=1)
                    df2 = df2.sort_index(axis=1)
                    df1.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
                    df2.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=df1.shape[1] + 2)
                    plot_definitions.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=df1.shape[1] + df2.shape[1] + 4)
                else:
                    if sheet_name in keep_sheet_names_combined:
                        if any(zone in df.columns for zone in zones):
                            columns = [zone for zone in zones if zone in df.columns]
                            df = df[columns]
                        elif any(transmission.startswith(zone) for transmission in df.columns for zone in zones) * any(transmission.endswith(zone) for transmission in df.columns for zone in zones):
                            columns = [
                                column for column in df.columns 
                                if all(zone in zones for zone in column.split("_"))]
                            df = df[columns]
                        else:                        
                            continue
                    df = df.sort_index(axis=1)
                    df.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=0)
                    plot_definitions.to_excel(writer, sheet_name=sheet_name, startrow=0, startcol=df.shape[1] + 2)

def add_QCplots(plotter, xls, sheet_name):
    plot_definitions, df = get_df_from_worksheet(xls, sheet_name)
    method = plot_definitions.loc["plot_definitions", "method"]
    title = plot_definitions.loc["plot_definitions", "title"]
    xlabel = plot_definitions.loc["plot_definitions", "xlabel"]
    ylabel = plot_definitions.loc["plot_definitions", "ylabel"]
    plot_text=QCplots.PlotText(
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,)
    if not method.startswith("combo_"):
        if method == "add_data":
            plotter.add_data(df, worksheet=sheet_name, plot_text=plot_text)
        elif method == "scatter":
            plotter.scatter(df, worksheet=sheet_name, plot_text=plot_text)
        elif method == "bar":
            plotter.bar(df, worksheet=sheet_name, plot_text=plot_text)
        elif method == "stacked":
            plotter.stacked(df, worksheet=sheet_name, plot_text=plot_text)
        elif method == "line":
            plotter.line(df, worksheet=sheet_name, plot_text=plot_text)
        elif method == "dashed":
            plotter.dashed(df, worksheet=sheet_name, plot_text=plot_text)
        elif method == "area":
            plotter.area(df, worksheet=sheet_name, plot_text=plot_text)
    else:
        df1 = df[0]
        df2 = df[1]
        if method == "combo_dashed_line":
            plotter.combo_dashed_line(data1=df1, data2=df2, worksheet=sheet_name, plot_text=plot_text)
        elif method == "combo_line_dashed":
            plotter.combo_line_dashed(data1=df1, data2=df2, worksheet=sheet_name, plot_text=plot_text)
        elif method == "combo_plot_forced_line_forced_dashed":
            plotter.combo_plot_forced_line_forced_dashed(data1=df1, data2=df2, worksheet=sheet_name, plot_text=plot_text)
        elif method == "combo_line_stacked":
            plotter.combo_line_stacked(data1=df1, data2=df2, worksheet=sheet_name, plot_text=plot_text)
        elif method == "combo_dashed_stacked":
            plotter.combo_dashed_stacked(data1=df1, data2=df2, worksheet=sheet_name, plot_text=plot_text)
        elif method == "combo_line_area":
            plotter.combo_line_area(data1=df1, data2=df2, worksheet=sheet_name, plot_text=plot_text)

def generate_QCplots(input_file_name="report_data.xlsx", output_file_name=None):
    xls = pd.ExcelFile(input_file_name)
    bake_resources = get_bake_resources(xls)
    if output_file_name is None:
        output_file_name = input_file_name.split(".")[0] + "_QCplots.xlsx"
    with QCplots.QCPlot(output_file_name) as plotter:
        plotter.bake_resources(bake_resources)  
        for sheet_name in xls.sheet_names:            
            add_QCplots(plotter, xls, sheet_name)

def generate_QCmaps(zones="all", years="all", input_file_name="report_data.xlsx", output_file_name=None):
    xls = pd.ExcelFile(input_file_name)
    sheet_names = xls.sheet_names
    sheet_names = [sheet_name for sheet_name in sheet_names if "balance_" in sheet_name]
    list_df = []
    for sheet_name in sheet_names:
        zone = sheet_name.split("_")[1]
        _, df = get_df_from_worksheet(xls, sheet_name)
        index = df[0].index
        demand = df[0].T.values[0]
        generation = df[1].sum(axis=1).values
        balance = generation - demand
        df = pd.DataFrame(balance, index=index, columns=[zone])
        if years is "all":
            years = df.index
        df = df.loc[years]
        list_df.append(df)
    df = pd.concat(list_df, axis=1)
    qcmp.COLORMAP = "QC_diverging_r"
    qcmp.HIGHLIGHT_ZONES = zones
    fig = qcmp.plot(df, "Balance (TWh/year)")
    if output_file_name is None:
        output_file_name = input_file_name.split(".")[0] + ".svg"
    fig.savefig(output_file_name, format="svg", dpi=300, bbox_inches="tight")
