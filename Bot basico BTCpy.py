import json as j
import pandas as pd
import requests
import time
import yfinance as yf
import performanceanalytics.table.table as pat
import datetime
import performanceanalytics.statistics as pas


def get_data(symbol):
    """
    Función se encarga de hacerle un pedido a la API y devolver la información relevante en formato de dataframe
    :param symbol: símbolo para pedir
    :return: DataFrame conteniendo la información que devuelve la API
    """
    # Se define la variable con la url de la api, donde le paso los parametros que necesito para mi búsqueda
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=" + symbol + "&tsym=USD&limit=100&e=bitstamp"
    # Se hace un "request" a la api, donde le paso el url para que me devuelva la data que yo necesito
    request_resp = requests.get(url=url).text
    # Se carga la respuesto en un objeto json de forma tal que lo pueda utilizar para generar un data frame
    json = j.loads(request_resp)
    # Se crea un dataframe con la información del json, en este caso agarro los datos con la clave "Data" y dentro de
    # eso la próxima clave con clave "Data
    df = pd.DataFrame(json['Data']['Data']).dropna()
    # Se devuelve el dataframe para utilizarlo por fuera de esta función
    return df


def sma(serie, ruedas, nombreColumna):
    """
    Función que calcula y devuelve la media móvil simple
    :param serie:
    :param ruedas:
    :param nombreColumna:
    :return:
    """
    rta = pd.DataFrame({nombreColumna: []})
    i = 0
    for _ in serie:

        if i >= ruedas:
            promedio = sum(serie[i - ruedas: i]) / ruedas
            rta.loc[i] = promedio
        # Le sumo a i para que siga iterando hasta que haya iterando más
        i = i + 1
    return rta


def get_tabla(simbolo, nRapida, nLenta):
    """
    Función que devuelve una tabla
    :param simbolo:
    :param nRapida:
    :param nLenta:
    :return:
    """
    data = get_data(simbolo)
    rapidas = sma(data['close'], nRapida, "rapida")
    lentas = sma(data['close'], nLenta, "lenta")
    tabla = rapidas.join(lentas).join(data['close']).dropna().reset_index()
    return tabla


def accion(cruce, pos, precio):
    """

    :param cruce:
    :param pos:
    :param precio:
    :return:
    """
    if cruce > 1:
        if pos == "Wait":
            print("--Buy Order $" + str(precio) + "--")
        pos = "Hold"
    else:
        if pos == "Hold":
            print("--Sell Order $" + str(precio) + "--")
        pos = "Wait"
    return pos


def long_even_short_odd(day):
    return 1 if day % 2 == 0 else -1


def position(boolean_value):
    return 1 if boolean_value is True else -1


if __name__ == '__main__':
    # pos = "Wait"
    # while True:
    #     tabla = get_tabla("BTC", 10, 20)
    #     cruce = tabla['rapida'].iloc[-1] / tabla['lenta'].iloc[-1]
    #     precio = tabla['close'].iloc[-1]
    #     pos = accion(cruce, pos, precio)
    #     print(pos+" $" +str(precio) )
    #     time.sleep(60)
    snp500 = yf.Ticker('^GSPC')
    data = snp500.history(period="max")

    data.head()
    data.tail()
    data.describe()

    snp500_return = data['Close'].pct_change().dropna()
    snp500_return.describe()

    data['even'] = data.index.day % 2 == 0
    # strategy 1: long on even days, short on odd days
    strategy1_return = (data['Close'].pct_change() * data.even.apply(position)).dropna()
    # strategy 2: short on even days, long on odd days
    strategy2_return = (data['Close'].pct_change() * - data.even.apply(position)).dropna()

    strategy1_return.describe()
    strategy2_return.describe()

    pas.vol(snp500_return)
    pas.beta(strategy1_return, snp500_return)
    pas.beta(strategy2_return, snp500_return)
    pas.correlation(strategy1_return, snp500_return)
    pas.sharpe_ratio(snp500_return, 0.03)
    pas.sharpe_ratio(strategy1_return, 0.03)
    pas.sharpe_ratio(strategy2_return, 0.03)
    pas.capm(strategy1_return, snp500_return)
    pas.capm(strategy2_return, snp500_return)

    pas.annualized_return(snp500_return, datetime.date(1928, 1, 3), datetime.date(2020, 2, 12))
    pas.annualized_return(strategy1_return, datetime.date(1928, 1, 3), datetime.date(2020, 2, 12))
    pas.annualized_return(strategy2_return, datetime.date(1928, 1, 3), datetime.date(2020, 2, 12))

    data['snp500_return'] = data['Close'].pct_change()
    pat.stats_table(data, manager_col=8)

    data['strategy1_return'] = (data['Close'].pct_change() * data.even.apply(position))
    pat.stats_table(data, manager_col=9)

    data['strategy2_return'] = (data['Close'].pct_change() * - data.even.apply(position))
    pat.stats_table(data, manager_col=10)

    pat.stats_table(data, manager_col=8, other_cols=[9, 10])

    pat.drawdown_table(snp500_return, -.03).head()
    pat.drawdown_table(strategy1_return, -.03).head()
    pat.drawdown_table(strategy2_return, -.03).head()

    # https://gist.github.com/justthetips/ff777cb95cc5d26c22f01e6e723c6d6e
