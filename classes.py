'''
Módulo que contiene clases usadas en main.py.
Clases de manejo de excepciones:
    RecursoNoEncontrado
    BadGateway
Clase para consumo de PokeAPI:
    RequestPokemonApi
Clase para escritura de Log de errores:
    Log

También contiene función asociada a decorador @singleton

'''
from typing import List
from os import getcwd, path, mkdir
from datetime import datetime
from requests import Response
import requests

#definicíon de decorador Singleton

def singleton(cls):
    '''
    Funcion decoradora para patrón singleton
    '''
    instances = dict()
    def wrp(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrp

@singleton
class Log:
    '''
    Clase encargada de escribir en log de errores
    LOG: Path del log de errores, el cual es relativo a la ubicación actual
    '''
    LOG: str = 'log/log_file'
    def __init__(self):
        '''
        Constructor. Verifica que la carpeta contenedora del Log (self.Log)
        esté presente. Si no es así la crea y apunta al log por medio de
        self.log_path
        '''
        folder_log_path: str = path.join(getcwd(), path.split(self.LOG)[0])
        if not path.exists(folder_log_path):
            mkdir(folder_log_path)
        
        self.log_path = path.join(getcwd(), self.LOG)

    def log_write(self, log_type: str, msj: str):
        '''
        Método encargado de escribir en el log de eventos
        type: Tipo de evento o error
        msj: Cuerpo del mensaje a escribir
        '''
        with open(file=self.log_path, mode='a', encoding='utf-8') as log_file:
            date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            log_file.write(f'ERROR\nFecha: {date_time}, Tipo: {log_type}, Msj: {msj}\n')


class RecursoNoEncontrado(Exception):
    '''
    Se levanta esta excepción cuando se presenta HTTP status: 404
    '''
    def __init__(self, recurso: str):
        message = f'El recurso {recurso} a respondido con HTTP status 404'
        super().__init__(message)

class BadGateway(Exception):
    '''
    Se levanta esta excepción cuando se presenta HTTP status: 502
    '''
    def __init__(self, recurso: str):
        message = f'El recurso {recurso} a respondido con HTTP status 502'
        super().__init__(message)

class RequestPokemonApi:
    '''
    Clase para ejecutar operaciones de consumo sobre PokeApi.
    '''

    #URL BASE Y SEGMENTOS A USAR
    DOM = 'https://pokeapi.co/api/v2/'
    PK = 'pokemon/'
    PK_ESP = 'pokemon-species/'
    EGG_GRP = 'egg-group/'
    TP = 'type/'

    def __init__(self):
        pass

    @staticmethod
    def _id_by_url(url: str) -> int:
        '''
        Método privado que retorna id de URL de PokeAPI (de endpoint /pokemon/id)
        url: URL a tratar <str>
        '''
        partes: List[str] = url.split('/')
        if partes[-1] == '':
            return int(partes[-2])
        else:
            return int(partes[-1])

    @staticmethod
    def _request_url_api(url: str) -> Response:
        '''
        Metodo privado encargada de hacer request a URLs de PokeAPI
        url: str: URL a consultar
        Salida: Response. En caso de presentarse exepciones en el llamado del endpoint, se
        retornará None
        '''
        try:
            resp:Response = requests.get(url)

            if resp.status_code == 404:
                raise RecursoNoEncontrado(url)
            elif resp.status_code == 502:
                raise BadGateway(url)

            return resp

        except RecursoNoEncontrado:
            log = Log()
            log.log_write(log_type='HTTP Error', msj=f'HTTP status 404: {url}')
            return None
        except BadGateway:
            log = Log()
            log.log_write(log_type='HTTP Error', msj=f'HTTP status 502: {url}')
            return None
        except Exception as excep:
            log = Log()
            log.log_write(log_type=excep.__class__, msj=excep.args)
            return None

    def get_pokemon_names(self) -> list:
        '''
        Método usado para traer desde PokeAPI los nombres de todos los pokemon registrados
        '''

        url = self.DOM + self.PK
        #Se inspecciona cuandos datos disponibles hay
        resp = self._request_url_api(url + '?limit=1')
        if resp:
            cantidad: int = resp.json()['count']

            #Se agrega parametro query limit al request
            resp = self._request_url_api(url + f'?limit={cantidad}')
            if resp:

                data:List[dict] = resp.json()['results']

                # se retorna lista con los nombres de los pokemons
                return [pok['name'] for pok in data]

            else:
                print('ERROR: revisar logs')
                return None
        else:
            print('ERROR: revisar logs')
            return None

    def get_pokemon_interbreed(self, pokemon: str) -> set:
        '''
        Método que permite, para un pokemon dado, conocer todos las especies de pokemon 
        con las cuales podría cruzarse
        pokemon: nombre del pokemon
        '''
    
        if isinstance(pokemon,str):
            #extracción de la especie de pokemon
            url = self.DOM + self.PK + pokemon

            resp = self._request_url_api(url)
            if resp:       
                url_species: str = resp.json()['species']['url']

                #extracción de los egg-group para la especie de pokemon
                resp = self._request_url_api(url_species)

                if resp:
                    egg_groups: List[dict] = resp.json()['egg_groups']   
                    #Se extraen URLs de los egg_groups de interés     
                    urls_egg_groups: List[str] = [data['url'] for data in egg_groups]                 
                    pk_names = set()
                    del egg_groups
                    for url_egg_group in urls_egg_groups:

                        #pokemon_species para cada egg_group
                        resp = self._request_url_api(url_egg_group)
                        if resp:
                            pk_esp: List[dict] = resp.json()['pokemon_species']
                            #Se extren los nombres de los pokemon_spieces asociados a cada
                            #egg_group de interés
                            pokemon_species = {data['name'] for data in pk_esp}
                            pk_names = pk_names.union(pokemon_species)
                        else:
                            print('ERROR: revisar logs')

                    return pk_names

                else:
                    print('ERROR: revisar logs')
                    return None   
            else:
                return None
        else:
            return None
    
    def pokemon_type_weights(self, type_pk: str, limit_lt_e: int = 151) -> list:

        '''
        Método que retorna los pesos de los pokemones de cierto tipo
        type: Tipo de pokemon <str>
        limit_lt_e: Entero que sirve como filtro para los ids de pokemon menores o iguales a 
        éste parámetro
        '''
        
        url = self.DOM + self.TP
        #se consulta URL general que retorna los tipos de pokemons
        resp = self._request_url_api(url)

        if resp:
            #Se busca URL válida para el tipo de pokemon indicado
            url_type = ''
            types: List[dict] = resp.json()['results']

            for p_type in types:
                if p_type['name'] == type_pk:
                    url_type = p_type['url']
                    break
            if url_type != '':
                #Se consulta el endpoint asociado al tipo de pokemon para extraer los
                #Pokemons pertenecientes a esa categoria

                resp = self._request_url_api(url_type)
                if resp:

                    #se verifican ids para condición id<=limit_gt_e
                    pokemons: List[str] = [pokemon['pokemon']['url'] for pokemon in resp.json()['pokemon'] if self._id_by_url(pokemon['pokemon']['url']) <= limit_lt_e]
                    weight = [0 for i in range(0,len(pokemons))]
                    
                    for i, url_pokemon in enumerate(pokemons, 0):
                        
                        # se realiza consulta por cada pokemon valido y extarcción del peso

                        resp = self._request_url_api(url_pokemon)
                        if resp:
                            try:
                                #Conversion a entero del peso del pokemon
                                weight[i] = int(resp.json()['weight'])
                                
                            except ValueError as excep:
                                log = Log()
                                log.log_write(log_type='ValueError', msj=excep.args[0])
                                print('ERROR: revisar logs')
                                weight[i] = 0  

                            except Exception as excep:
                                log = Log()
                                log.log_write(log_type=excep.__class__, msj=excep.args[0])
                                print('ERROR: revisar logs')
                                weight[i] = 0                       
                        else:
                            print('ERROR: revisar logs')

                    return weight

                else:
                    print('ERROR: revisar logs')
                    return None
            else:
                print('ERROR: revisar logs')
                return None
        else:
            print('ERROR: revisar logs')
            return None

