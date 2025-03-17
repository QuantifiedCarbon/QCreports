import numpy as np
import pandas as pd
import cgriddb
from qcreports.utils import merge_columns, read_compressed_data, rename_dictionary, get_plot_definitions, get_worksheet

def get_worksheets(tags):

    ids = cgriddb.get_jobid(comment=tags)
    worksheets = []

    sheet_name = "price"
    df = cgriddb.get_value_with_index(ids, 'zone,mean_price', 'my').sort_index(axis=1)
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="€/MWh")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "negative_price"
    df = cgriddb.get_value_with_index(ids, 'zone,price', 'my').sort_index(axis=1)
    for column in df.columns:
        for index in df.index:
            prices = read_compressed_data(df.loc[index, column])
            df.loc[index, column] = sum(prices <= 0) / len(prices)
    df = df * 1e2
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="%")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "capture_rate_wind_onshore"
    df = cgriddb.get_value_with_index(ids, 'resource,capture_rate,^wind_onshore.*', 'my').sort_index(axis=1)
    df = df.ffill().bfill()
    columns = [column for column in df.columns if "existing" not in column]
    df = df[columns]
    df.columns = [column.rsplit("_", 1)[1] for column in df.columns]
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "capture_rate_wind_offshore"
    df = cgriddb.get_value_with_index(ids, 'resource,capture_rate,^wind_offshore.*', 'my').sort_index(axis=1)
    df = df.ffill().bfill()
    columns = [column for column in df.columns if "existing" not in column]
    df = df[columns]
    df.columns = [column.rsplit("_", 1)[1] for column in df.columns]
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "capture_rate_solar"
    df = cgriddb.get_value_with_index(ids, 'resource,capture_rate,^solar_.*', 'my').sort_index(axis=1)
    columns = [column for column in df.columns if "existing" not in column]
    df = df[columns]
    df.columns = [column.rsplit("_", 1)[1] for column in df.columns]
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name_start = "generation_capacity"
    dfx = cgriddb.get_value_with_index(ids, 'resource,capacity', 'my').sort_index(axis=1)
    dfx = dfx.fillna(0)
    dfx = dfx * 1e-3
    resources = dfx.columns
    zones = [resource.rsplit("_", 1)[1] for resource in resources]
    zones = np.sort(zones)
    for zone in zones:
        sheet_name = f"{sheet_name_start}_{zone}"
        df = dfx.copy()
        df = df.filter(regex=f"_{zone}$")
        df.columns = [column.rsplit("_", 1)[0] for column in df.columns]
        df = df.rename(columns=rename_dictionary)
        df = merge_columns(df).sort_index(axis=1)
        plot_definitions = get_plot_definitions(method="stacked", title=sheet_name, xlabel="year", ylabel="GW")
        worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name_start = "balance"
    df1x = cgriddb.get_value_with_index(ids, 'zone,total_demand', 'my').sort_index(axis=1)
    df1x = df1x * 1e-6
    df2x = cgriddb.get_value_with_index(ids, 'resource,total_generation', 'my').sort_index(axis=1)
    df2x = df2x.fillna(0)
    df2x = df2x * 1e-6
    zones = df1x.columns
    for zone in zones:
        sheet_name = f"{sheet_name_start}_{zone}"
        df1 = df1x.copy()
        df1 = df1[[zone]]
        df1.columns = ["demand"]
        df2 = df2x.copy()
        df2 = df2.filter(regex=f"_{zone}$")
        df2.columns = [column.rsplit("_", 1)[0] for column in df2.columns]
        df2 = df2.rename(columns=rename_dictionary)
        df2 = merge_columns(df2).sort_index(axis=1)
        plot_definitions = get_plot_definitions(method="combo_line_stacked", title=sheet_name, xlabel="year", ylabel="TWh/year")
        worksheets.append(get_worksheet(sheet_name=sheet_name, df=[df1, df2], plot_definitions=plot_definitions))

    sheet_name = "transmission_capacity"
    df1 = cgriddb.get_value_with_index(ids, 'transmission,capacity1', 'my').sort_index(axis=1)
    for column in df1.columns:
        for index in df1.index:
            df1.loc[index, column] = read_compressed_data(df1.loc[index, column]).mean()
    df2 = cgriddb.get_value_with_index(ids, 'transmission,capacity2', 'my').sort_index(axis=1)
    for column in df2.columns:
        for index in df2.index:
            df2.loc[index, column] = read_compressed_data(df2.loc[index, column]).mean()
    columns = [column.split("_") for column in df2.columns]
    df2.columns = [f"{c[1]}_{c[0]}" for c in columns]
    df = pd.concat([df1, df2], axis=1).sort_index(axis=1)
    df = df * 1e-3
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="GW")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "transmission_flow"
    df = cgriddb.get_value_with_index(ids, 'transmission,flow', 'my').sort_index(axis=1)
    for column in df.columns:
        for index in df.index:
            df.loc[index, column] = read_compressed_data(df.loc[index, column]).sum()
    df = df * 1e-6
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="TWh/year")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    return worksheets
