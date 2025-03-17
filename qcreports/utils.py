import io
import gzip
import numpy as np
import pandas as pd

rename_dictionary = {
    "thermal": "bio",
#    "must_run": "?",
    }
remove_subdivisions = ["existing",]

def read_compressed_data(compressed_data):
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
            decompressed_data = f.read()
        array = np.load(io.BytesIO(decompressed_data), allow_pickle=True)
    except:
        array = np.array([0])
    return array

def merge_columns(df):
    for remove_subdivision in remove_subdivisions:
        remove_str = f"_{remove_subdivision}"
        df.columns = [col.replace(remove_str, '') for col in df.columns]
        df = df.T.groupby(level=0).sum().T
    return df

def get_plot_definitions(method, title, xlabel, ylabel):
    plot_definitions = {
        "method": method,
        "title": title,
        "xlabel": xlabel,
        "ylabel": ylabel,
        }
    return plot_definitions

def get_worksheet(sheet_name, df, plot_definitions):
    worksheet = {
        "sheet_name": sheet_name,
        "df": df,
        "plot_definitions": plot_definitions,    
        }
    return worksheet

def get_df_from_worksheet(xls, sheet_name):
    df_worksheet = pd.read_excel(xls, sheet_name=sheet_name)
    ip = df_worksheet.columns.get_loc("plot_definitions")
    plot_definitions = df_worksheet.iloc[:, ip-1:]
    plot_definitions = plot_definitions.dropna(how="all")
    plot_definitions = plot_definitions.set_index(plot_definitions.columns[0])
    plot_definitions.index.name = ""
    plot_definitions = plot_definitions.T
    method = plot_definitions.loc["plot_definitions", "method"]
    df = df_worksheet.iloc[:, :ip-2]
    if method.startswith("combo_"):
        ic = [i for i, column in enumerate(df.columns) if column.startswith("Unnamed")]
        ic = ic[1]
        df1 = df.iloc[:, :ic]
        df1 = df1.set_index(df1.columns[0])
        df1.index.name = ""    
        df2 = df.iloc[:, ic+1:]
        df2 = df2.set_index(df2.columns[0])
        df2.index.name = ""    
        df = [df1, df2]
    else:
        df = df.set_index(df.columns[0])
        df.index.name = ""    
    return plot_definitions, df

def get_bake_resources(xls):
    sheet_names = xls.sheet_names
    sheet_names = [sheet_name for sheet_name in sheet_names if "generation_capacity_" in sheet_name]
    resource_columns = []
    for sheet_name in sheet_names:
        _, df = get_df_from_worksheet(xls, sheet_name)
        resource_columns = resource_columns + df.columns.to_list()
    resource_columns = list(set(resource_columns))
    bake_resources = resource_columns + ["demand"]
    return bake_resources
