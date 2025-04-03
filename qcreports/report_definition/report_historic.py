import numpy as np
import pandas as pd
import qcdata
from qcreports.utils import get_plot_definitions, get_worksheet

rename_dictionary = {
    "DELU": "DE",
    "EE": "BT",
    "LT": "BT",
    "LV": "BT",
    "NO1": "NO125",
    "NO2": "NO125",
    "NO5": "NO125",
}

def get_worksheets():
    worksheets = []
    df_price = qcdata.read(f"ENTSO-E,price,*")
    df_price = df_price.rename(columns=rename_dictionary)
    df_price = df_price.groupby(level=0, axis=1).mean()
    df_price_old = pd.read_csv("/viking-vault/QCL_Dropbox/data/historic/review/price.csv", index_col=0, parse_dates=True)
    df_price_old = df_price_old[df_price_old.index.year < df_price.index.year.min()]
    df_price = pd.concat([df_price_old, df_price])
    df_price = df_price[df_price.index.year >= 2015]
    df_price = df_price[df_price.index.year < 2025]
    df_price = df_price.interpolate()
    df_price = df_price.fillna(0)
    zones_model = ["BT", "DE", "DK1", "DK2", "ES", "FI", "FR", "NL", "NO125", "NO3", "NO4", "PL", "SE1", "SE2", "SE3", "SE4", "UK"]
    df_price = df_price[zones_model]
    df_mean_price = df_price.resample("YS").mean()

    sheet_name = "price"
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="€/MWh")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df_mean_price, plot_definitions=plot_definitions))

    sheet_name = "negative_price"
    df = pd.DataFrame()
    for column in df_price.columns:
        for year in df_price.index.year.unique():
            print(column, year)
            prices = df_price[column]
            prices = prices[prices.index.year == year]
            prices = prices.values
            df.loc[year, column] = sum(prices <= 0) / len(prices)
            
    df = df * 1e2
    plot_definitions = get_plot_definitions(method="line", title=sheet_name, xlabel="year", ylabel="%")
    worksheets.append(get_worksheet(sheet_name=sheet_name, df=df, plot_definitions=plot_definitions))

    return worksheets
