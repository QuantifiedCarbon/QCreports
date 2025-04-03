import numpy as np
import pandas as pd
import cgriddb
from qcreports.utils import merge_columns, read_compressed_data, rename_dictionary, get_plot_definitions, get_worksheet

def get_worksheets(tags, run_ids, weather_year):

    tags1 = tags + [run_ids[0]] + [weather_year]
    tags2 = tags + [run_ids[1]] + [weather_year]
    ids1 = cgriddb.get_jobid(comment=tags1)
    ids2 = cgriddb.get_jobid(comment=tags2)
    ids = np.concatenate([ids1, ids2])

    tags1 = tags + [run_ids[0]]
    tags2 = tags + [run_ids[1]]
    ids1 = cgriddb.get_jobid(comment=tags1)
    ids2 = cgriddb.get_jobid(comment=tags2)
    ids_all = np.concatenate([ids1, ids2])

    worksheets = []

    columns = ["p10", "p50", "p90"]
    quartiles = [0.1, 0.5, 0.9]

    zones = cgriddb.get_value_with_index(ids_all, 'zone,mean_price', 'my').sort_index(axis=1).columns

    sheet_name = "price"
    print(sheet_name)
    df = cgriddb.get_value_with_index(ids, 'zone,mean_price', 'my').sort_index(axis=1)
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="€/MWh")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name_start = "price_statistics"
    for zone in zones:
        sheet_name = f"{sheet_name_start}_{zone}"
        print(sheet_name)
        df = cgriddb.get_value_with_index_and_column(ids_all, f'zone,mean_price,{zone}', 'my', 'wy')
        df[columns] = df.quantile(quartiles, axis=1).T
        df["mean"] = df.mean(axis=1).T
        df = df[columns + ["mean"]]
        plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="€/MWh")
        worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "negative_price"
    print(sheet_name)
    df = cgriddb.get_value_with_index(ids, 'zone,price', 'my').sort_index(axis=1)
    for column in df.columns:
        for index in df.index:
            prices = read_compressed_data(df.loc[index, column])
            df.loc[index, column] = sum(prices <= 0) / len(prices)
    df = df * 1e2
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="%")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    folder = "~/working_folder/final_plots/capture_rates/"

    sheet_name = "cap_rate_solar"
    print(sheet_name)
    df1 = pd.read_csv(folder + "annual_solar_FI.csv", index_col=0, parse_dates=True)[["1991"]]
    df2 = pd.read_csv(folder + "annual_solar_SE1.csv", index_col=0, parse_dates=True)[["1991"]]
    df3 = pd.read_csv(folder + "annual_solar_SE2.csv", index_col=0, parse_dates=True)[["1991"]]
    df4 = pd.read_csv(folder + "annual_solar_SE3.csv", index_col=0, parse_dates=True)[["1991"]]
    df5 = pd.read_csv(folder + "annual_solar_SE4.csv", index_col=0, parse_dates=True)[["1991"]]
    df1.columns = ["FI"] 
    df2.columns = ["SE1"] 
    df3.columns = ["SE2"] 
    df4.columns = ["SE3"] 
    df5.columns = ["SE4"] 
    df = pd.concat([df1, df2, df3, df4, df5], axis=1)
    df.index.name = None
    df.index = df.index.year
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "cap_rate_wind_onshore_existing"
    print(sheet_name)
    df1 = pd.read_csv(folder + "annual_wind_onshore_existing_FI.csv", index_col=0, parse_dates=True)[["1991"]]
    df2 = pd.read_csv(folder + "annual_wind_onshore_existing_SE1.csv", index_col=0, parse_dates=True)[["1991"]]
    df3 = pd.read_csv(folder + "annual_wind_onshore_existing_SE2.csv", index_col=0, parse_dates=True)[["1991"]]
    df4 = pd.read_csv(folder + "annual_wind_onshore_existing_SE3.csv", index_col=0, parse_dates=True)[["1991"]]
    df5 = pd.read_csv(folder + "annual_wind_onshore_existing_SE4.csv", index_col=0, parse_dates=True)[["1991"]]
    df1.columns = ["FI"] 
    df2.columns = ["SE1"] 
    df3.columns = ["SE2"] 
    df4.columns = ["SE3"] 
    df5.columns = ["SE4"] 
    df = pd.concat([df1, df2, df3, df4, df5], axis=1)
    df.index.name = None
    df.index = df.index.year
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="-")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    sheet_name = "cap_rate_wind_onshore_new"
    print(sheet_name)
    df1 = pd.read_csv(folder + "annual_wind_onshore_FI.csv", index_col=0, parse_dates=True)[["1991"]]
    df2 = pd.read_csv(folder + "annual_wind_onshore_SE1.csv", index_col=0, parse_dates=True)[["1991"]]
    df3 = pd.read_csv(folder + "annual_wind_onshore_SE2.csv", index_col=0, parse_dates=True)[["1991"]]
    df4 = pd.read_csv(folder + "annual_wind_onshore_SE3.csv", index_col=0, parse_dates=True)[["1991"]]
    df5 = pd.read_csv(folder + "annual_wind_onshore_SE4.csv", index_col=0, parse_dates=True)[["1991"]]
    df1.columns = ["FI"] 
    df2.columns = ["SE1"] 
    df3.columns = ["SE2"] 
    df4.columns = ["SE3"] 
    df5.columns = ["SE4"] 
    df = pd.concat([df1, df2, df3, df4, df5], axis=1)
    df = df[df.index.year >= 2025]
    df.index.name = None
    df.index = df.index.year
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
        print(sheet_name)
        df = dfx.copy()
        df = df.filter(regex=f"_{zone}$")
        df.columns = [column.rsplit("_", 1)[0] for column in df.columns]
        df = df.rename(columns=rename_dictionary)
        df = merge_columns(df)
        df = df.sort_index(axis=1)
        df.index = df.index.astype(int)
        new_index = pd.RangeIndex(start=int(df.index.min()), stop=int(df.index.max()) + 1, step=1)
        df = df.reindex(new_index).fillna(0)
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
        print(sheet_name)
        df1 = df1x.copy()
        df1 = df1[[zone]]
        df1.columns = ["demand"]
        df2 = df2x.copy()
        df2 = df2.filter(regex=f"_{zone}$")
        df2.columns = [column.rsplit("_", 1)[0] for column in df2.columns]
        df2 = df2.rename(columns=rename_dictionary)
        df2 = merge_columns(df2)
        df2 = df2.sort_index(axis=1)
        df1.index = df1.index.astype(int)
        df2.index = df2.index.astype(int)
        new_index = pd.RangeIndex(start=int(df1.index.min()), stop=int(df1.index.max()) + 1, step=1)
        df1 = df1.reindex(new_index).interpolate()
        df2 = df2.reindex(new_index).fillna(0)
        plot_definitions = get_plot_definitions(method="combo_line_stacked", title=sheet_name, xlabel="year", ylabel="TWh/year")
        worksheets.append(get_worksheet(sheet_name=sheet_name, df=[df1, df2], plot_definitions=plot_definitions))

    return worksheets
