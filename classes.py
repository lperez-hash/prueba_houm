import requests
from requests import Response


class RecursoNoEncontrado(Exception):
    pass

class BadGateway(Exception):
    pass

class RequestPokemonApi:
    '''
    Clase para ejecutar operaciones de consumo sobre PokeApi.
    Expone 3 funciones.
    '''

    #URL BASE Y SEGMENTOS A USAR
    DOM = 'https://pokeapi.co/api/v2/'
    PK = 'pokemon/'
    PK_ESP = 'pokemon-species/'
    EGG_GRP = 'egg-group'
    TP = 'type/'

    def __init__(self):
        pass

    def _id_by_url(self, url: str) -> int:
        '''
        Función privada que retorna id de URL de PokeAPI (de endpoint /pokemon)
        url: URL a tratar <str>
        '''
        partes: list[str] = url.split('/')
        if partes[-1] == '':
            return int(partes[-2])
        else:
            return int(partes[-1])


    def _request_url_api(self, url: str) -> Response:
        '''
        Funcion privada encargada de hacer request a URLs de PokeAPI
        url: str: URL a consultar
        Salida: Response. En caso de presentarse exepciones en el llamado del endpoint, se
        retornará None
        '''
        try:
            r:Response = requests.get(url)

            if r.status_code == 404:
                raise RecursoNoEncontrado
            elif r.status_code == 502:
                raise BadGateway

            return r

        except RecursoNoEncontrado:
            print('El recurso no está disponible')
            return None
        except BadGateway:
            print('HTTP 502 al tratar de acceder al recurso')
            return None
        except Exception as e:
            print(f'ERR: {e.__class__}')
            return None
            
    
    def get_pokemon_names(self) -> list:
        '''
        Método usado para traer desde PokeAPI los nombres de todos los pokemon registrados
        '''

        url = self.DOM + self.PK
        #Se inspecciona cuandos datos disponibles hay
        rp = self._request_url_api(url + '?limit=1')
        if rp:
            cantidad: int = rp.json()['count']

            #Se agrega parametro query limit al request
            rp = self._request_url_api(url + f'?limit={cantidad}')
            if rp:

                data:list[dict] = rp.json()['results']

                # se retorna lista con los nombres de los pokemons
                return [pok['name'] for pok in data]

            else:
                return None
        else:
            return None
    
    def get_pokemon_interbreed(self, pokemon: str) -> set:
        '''
        Método que permite, para un pokemon dado, conocer todos los pokemons con los cuales 
        podría cruzarse
        pokemon: nombre del pokemon
        '''
        
        if isinstance(pokemon,str):
            
            #extracción de la especie de pokemon
            url = self.DOM + self.PK + pokemon

            rp = self._request_url_api(url)
            if rp:
                
                url_species: str = rp.json()['species']['url']

                #extracción de los egg-group para la especie de pokemon
                rp = self._request_url_api(url_species)

                if rp:
                    egg_groups: list[dict] = rp.json()['egg_groups']   

                    #Se extraen URLs de los egg_groups de interés     
                    urls_egg_groups: list[str] = [data['url'] for data in egg_groups]
                    
                    pk_names = set()

                    del egg_groups
                    for url_egg_group in urls_egg_groups:

                        #pokemon_species para cada egg_group

                        print(f'## Egg_group: {url_egg_group}\n')
                        rp = self._request_url_api(url_egg_group)
                        if rp:
                            pk_esp: list[dict] = rp.json()['pokemon_species']
                            #Se extren las URL de los pokemon_spieces asociados a cada
                            #egg_group de interés
                            urls_pokemon_species: list[str] = [data['url'] for data in pk_esp]

                            for url_pokemon_species in urls_pokemon_species:

                                #extracción de pokemons para cada pokemon_species

                                print(f'## pokemon_species: {url_pokemon_species}\n')

                                rp = self._request_url_api(url_pokemon_species)
                                if rp:

                                    #extraccion de pokemons por cada pokemon_spieces
                                    #y se genera arreglo para contenerlos
                                    pokemons:list[dict] = rp.json()['varieties']
                                    pk_names_pr = {data['pokemon']['name'] for data in pokemons}
                                    pk_names = pk_names.union(pk_names_pr)

                                else:
                                    print(f'ERROR ACCESO url_pokemon_species: {url_pokemon_species}')
                        else:
                            print(f'ERROR ACCESO url_egg_group: {url_egg_group}') 

                    return pk_names

                else:
                    print(f'ERROR ACCESO url_species: {url_species}')
                    return None
        
            else:
                return None
        else:
            return None
    
    def pokemon_type_weights(self, type: str, limit_lt_e: int = 151) -> list:

        '''
        Método que retorna los pesos de los pokemones de cierto tipo
        type: Tipo de pokemon <str>
        limit_lt_e: Entero que sirve como filtro para los ids de pokemon menores o iguales a 
        éste parámetro
        '''
        
        url = self.DOM + self.TP
        #se consulta URL general que retorna los tipos de pokemons
        rp = self._request_url_api(url)

        if rp:
            #Se busca URL válida para el tipo de pokemon indicado
            url_type = ''
            types: list[dict] = rp.json()['results']

            for p_type in types:
                if p_type['name'] == type:
                    url_type = p_type['url']
                    break
            if url_type != '':
                #Se consulta el endpoint asociado al tipo de pokemon para extraer los
                #Pokemons pertenecientes a esa categoria

                rp = self._request_url_api(url_type)
                if rp:

                    #se verifican ids para condición id<=limit_gt_e
                    pokemons: list[str] = [pokemon['pokemon']['url'] for pokemon in rp.json()['pokemon'] if self._id_by_url(pokemon['pokemon']['url']) <= limit_lt_e]
                    weight = [0 for i in range(0,len(pokemons))]
                    
                    for i, url_pokemon in enumerate(pokemons, 0):
                        
                        # se realiza consulta por cada pokemon valido y extarcción del peso

                        rp = self._request_url_api(url_pokemon)
                        if rp:
                            weight[i] = int(rp.json()['weight'])                         
                        else:
                            print(f'Error al consultar link de pokemon {url_pokemon}')

                    return weight

                else:
                    print('Error al consultar URL de tipo de pokemon')
                    return None
            else:
                print('No se encontro URL para el tipo de pokemon solicitado')
                return None
        else:
            print('Error al consultar URL de tipos de pokemon')
            return None
        
