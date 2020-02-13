import json as j
import pandas as pd
import requests
import time


def get_data(symbol):
    """
    Función se encarga de hacerle un pedido a la API y devolver la información relevante en formato de dataframe
    :param symbol: símbolo para pedir
    :return: DataFrame conteniendo la información que devuelve la API
    """
    # url es la url de la api, donde le paso los parametros que necesito para mi búsqueda
    url = "https://min-api.cryptocompare.com/data/v2/histominute?fsym=" + symbol + "&tsym=USD&limit=100&e=bitstamp"
    # le hago un "request" a la api, donde le paso el url para que me devuelva del url que yo necesito
    request_resp = requests.get(url=url).text
    # cargo la respuesto en un objeto json de forma tal que lo pueda utilizar para generar un data frame
    json = j.loads(request_resp)
    # creo un dataframe con la información del json, en este caso agarro los datos con la clave "Data" y dentro de
    # eso la próxima clave con clave "Data
    df = pd.DataFrame(json['Data']['Data']).dropna()
    # Devuelvo el dataframe para utilizarlo por fuera de esta función
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


if __name__ == '__main__':
    pos = "Wait"
    while True:
        tabla = get_tabla("BTC", 10, 20)
        cruce = tabla['rapida'].iloc[-1] / tabla['lenta'].iloc[-1]
        precio = tabla['close'].iloc[-1]
        pos = accion(cruce, pos, precio)
        print(pos+" $" +str(precio) )
        time.sleep(60)
