'''
Modulo de funciones principales que dan solución a la prueba.
en if __name__ se dá ejemplo de uso de las funciones.
'''
from pandas import Series
from classes import RequestPokemonApi

def regex_pokemons() -> int:
    """
    Función que da solución al punto 1 de la prueba.
    Retorna <int> que indica los pokemons que cumplen el criterio especificado
    """
    req = RequestPokemonApi()
    data = req.get_pokemon_names()

    if data:
        data_serie: Series = Series(data=data, name='names')

        #filtrado de data de acuerdo a lo especificado
        filter_at = data_serie.str.contains(pat='at', case=False, regex=True)
        filter_a_a = data_serie.str.count('a') == 2

        rta = data_serie.loc[filter_at & filter_a_a]

        return rta.shape[0]
    else:
        #Se ha presentado un problema llamando a los endpoints necesarios de PokeAPI
        return None

def pokemon_interbreed_raichu() -> int:
    '''
    Función que da solución al punto 2 de la Prueba
    Retorna int que especifica número de especies con las que raichu podría cruzarse
    '''
    pokemon_name = 'raichu'
    req = RequestPokemonApi()
    data = req.get_pokemon_interbreed(pokemon_name)

    if data:
        return len(data)
    else:
        return None

def max_min_fighting() -> list:
    '''
    Función que da solución al punto 3 de la Prueba
    Retorna lista con pesos minimo y máximo de los pokemons de tipo Fighting [Max, Min]
    '''
    req = RequestPokemonApi()
    weights: list = req.pokemon_type_weights('fighting')

    if weights:
        return [max(weights), min(weights)]
    else:
        return None

if __name__ == '__main__':  
    #Ejecucion función punto1
    print('\nPrueba Punto 1')  
    result = regex_pokemons()
    print(result)
    #Ejecucion función punto2
    print('\nPrueba Punto 2')
    result = pokemon_interbreed_raichu()
    print(result)
    #Ejecucion función punto3
    print('\nPrueba Punto 3')
    result = max_min_fighting()
    print(result)
    