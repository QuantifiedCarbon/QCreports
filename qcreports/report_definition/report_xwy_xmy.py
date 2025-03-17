import numpy as np
import pandas as pd
import cgriddb
from qcreports.utils import merge_columns, read_compressed_data, rename_dictionary, get_plot_definitions, get_worksheet

def get_worksheets(tags):

    ids = cgriddb.get_jobid(comment=tags)
    columns = ["p10", "p50", "p90"]
    quartiles = [0.1, 0.5, 0.9]
    worksheets = []

    zones = cgriddb.get_value_with_index(ids, 'zone,mean_price', 'my').sort_index(axis=1).columns

    sheet_name_start = "price"
    for zone in zones:
        sheet_name = f"{sheet_name_start}_{zone}"
        print(sheet_name)
        df = cgriddb.get_value_with_index_and_column(ids, f'zone,mean_price,{zone}', 'my', 'wy')
        df[columns] = df.quantile(quartiles, axis=1).T
        df["mean"] = df.mean(axis=1).T
        df = df[columns + ["mean"]]
        plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="€/MWh")
        worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name_start = "cap_rate_wind_onshore"
    for zone in zones:
        try:
            sheet_name = f"{sheet_name_start}_{zone}"
            print(sheet_name)
            df = cgriddb.get_value_with_index_and_column(ids, f'resource,capture_rate,wind_onshore_{zone}', 'my', 'wy')
            df[columns] = df.quantile(quartiles, axis=1).T
            df["mean"] = df.mean(axis=1).T
            df = df[columns + ["mean"]]
            plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
            worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))
        except:
            pass

    sheet_name_start = "cap_rate_wind_offshore"
    for zone in zones:
        try:
            sheet_name = f"{sheet_name_start}_{zone}"
            print(sheet_name)
            df = cgriddb.get_value_with_index_and_column(ids, f'resource,capture_rate,wind_offshore_{zone}', 'my', 'wy')
            df[columns] = df.quantile(quartiles, axis=1).T
            df["mean"] = df.mean(axis=1).T
            df = df[columns + ["mean"]]
            plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
            worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))
        except:
            pass

    sheet_name_start = "cap_rate_solar"
    for zone in zones:
        try:
            sheet_name = f"{sheet_name_start}_{zone}"
            print(sheet_name)
            df = cgriddb.get_value_with_index_and_column(ids, f'resource,capture_rate,solar_{zone}', 'my', 'wy')
            df[columns] = df.quantile(quartiles, axis=1).T
            df["mean"] = df.mean(axis=1).T
            df = df[columns + ["mean"]]
            plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
            worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))
        except:
            pass

    return worksheets
