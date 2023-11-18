import cherrypy
import re

def cpf_check(cpf):
        return re.fullmatch(r'[0-9]{3}.[0-9]{3}.[0-9]{3}-[0-9]{2}', cpf)

def placa_check(placa):
    return re.fullmatch(r'[A-Z]{3}-\d{4}', placa) or re.fullmatch(r'[A-Z]{3}[0-9][A-Z]\d{2}', placa) 

def birth_check(birth):
    return re.fullmatch(r'\d{2}/\d{2}/\d{4}', birth)

class Resource(object):

    def __init__(self):
        self.cars = {}
        self.people = {}

    @cherrypy.expose
    def index(self):
        return """<h1>CRUD de carros</h1>
                <hr>
                <div>Para ver todos os carros cadastrados: <a href="/cars">http://127.0.0.1:1234/cars</a>
                <div>Para ver todas as pessoas cadastradas: <a href="/person">http://127.0.0.1:1234/person</a>
                <hr>
                <h2>CREATE</h2>
                <div>Antes de cadastrar um carro, é necessário cadastrar seu proprietário
                <br>
                <div><b>Para cadastrar uma pessoa:</b> curl -d cpf=000.000.000-00 -d nome=Ronaldo -d "cidade=Rio de Janeiro" -d nascimento=18/09/1976 -X POST "http://127.0.0.1:1234/person/create"
                <div><b>Para cadastrar um carro:</b> curl -d placa=ABC-1234 -d marca=hyundai -d modelo= -d km=23000 -d ano=2006 -d combustivel=gasolina -d proprietario=000.000.000-00 -X POST "http://127.0.0.1:1234/cars/create"
                <br>
                <h2>READ</h2>
                <div><b>Para cadastrar buscar uma pessoa:</b> curl -G -d cpf=000.000.000-00 -X GET "http://127.0.0.1:1234/person/read"
                <div><b>Para cadastrar buscar um carro:</b> curl -G -d placa=ABC-1234 -X GET "http://127.0.0.1:1234/cars/read"
                <br>
                <h2>UPDATE</h2>
                Para atualizar um cadastro é necessário passar somente a chave primária e os campos que serão editados
                <br>
                <div><b>Para cadastrar atualizar uma pessoa:</b> curl -d cpf=000.000.000-00 -d "cidade=São Paulo" -X PATCH "http://127.0.0.1:1234/person/update"
                <div><b>Para cadastrar buscar um carro:</b> curl -d placa=ABC-1234 -d km=20000000000 -d ano=1999 -X PATCH "http://127.0.0.1:1234/cars/update"
                <br>
                <h2>DELETE</h2>
                <div><b>Para deletar uma pessoa:</b> curl -G -d cpf=111.111.111-11 -X DELETE "http://127.0.0.1:1234/person/delete"
                <div><b>Para deletar um carro:</b> curl -G -d placa=ABC-1234 -X DELETE "http://127.0.0.1:1234/cars/delete"

                <br>

                """

    @cherrypy.expose
    def car_index(self):
        return '<h1>Carros cadastrados</h1>' + '<hr>'.join(f"<div> Placa: {car['placa']} <br> Marca: {car['marca']} <br> Modelo: {car['modelo']} \
                            <br> Ano: {car['ano']} <br> Km: {car['km']} <br> Combustível: {car['combustivel']} <br> Proprietário: {car['proprietario']}</div>" for car in self.cars.values())

    @cherrypy.expose
    def car_create(self, **args):
        if not all(key in args.keys() for key in ['placa', 'marca', 'modelo', 'ano', 'km', 'combustivel','proprietario']):
            raise cherrypy.HTTPError(400, 'Dados incompletos')
        
        if not placa_check(args['placa']):
            raise cherrypy.HTTPError(422, 'Formato de placa inválido!')
        elif int(args['km']) < 0:
            raise cherrypy.HTTPError(422, 'Quilometragem inválida!')
        elif int(args['ano']) < 0:
            raise cherrypy.HTTPError(422, 'Ano inválido!')    
        elif args['proprietario'] != '':
            if not cpf_check(args['proprietario']):
                raise cherrypy.HTTPError(422, 'Formato de CPF inválido!')   
            if not args['proprietario'] in self.people.keys():
                raise cherrypy.HTTPError(404, 'Proprietário não cadastrado')

        if args['placa'] in self.cars.keys():
            raise cherrypy.HTTPError(400, 'Paca já cadastrada')

        self.cars[args['placa']] = {'placa': args['placa'], 
                                    'marca': args['marca'], 
                                    'modelo': args['modelo'],
                                    'ano': int(args['ano']),
                                    'km': int(args['km']),
                                    'combustivel': args['combustivel'],
                                    'proprietario': args['proprietario']}
        
        cherrypy.response.status = "201"
        return f"<h1>Registro criado com sucesso!</h1>" + f"<div> Placa: {args['placa']} <br> Marca: {args['marca']} <br> Modelo: {args['modelo']} \
                            <br> Ano: {args['ano']} <br> Km: {args['km']} <br> Combustível: {args['combustivel']} <br> Proprietário: {args['proprietario']}</div>"

    @cherrypy.expose
    def car_read(self, placa):
        if not placa in self.cars.keys():
            raise cherrypy.HTTPError(404,'Carro não encontrado')            
        car = self.cars[placa]
        return f"<h1>Resultado da Busca</h1><div> Placa: {placa} <br> Marca: {car['marca']} <br> Modelo: {car['modelo']} \
                    <br> Ano: {car['ano']} <br> Km: {car['km']}, <br> Combustível: {car['combustivel']} <br> Proprietário: {car['proprietario']}</div>"


    @cherrypy.expose
    def car_update(self, **args):
        if 'placa' not in args.keys(): 
            raise cherrypy.HTTPError(400,'Dados incompletos')           
        if not args['placa'] in self.cars.keys():
            raise cherrypy.HTTPError(404,'Carro não Encontrado')
        for key in args.keys():
            if key == 'km' and int(args['km']) < 0:
                raise cherrypy.HTTPError(422, 'Quilometragem inválida!')
            elif key == 'ano' and int(args['ano']) < 0:
                raise cherrypy.HTTPError(422, 'Ano inválido!')    
            elif key == 'proprietario' and args['proprietario'] != '':
                if not args['proprietario'] in self.people.keys():
                    raise cherrypy.HTTPError(404, 'Proprietário não cadastrado')

            if(key == 'ano' or key == 'km'):
                self.cars[args['placa']][key] = int(args[key])
            else:
                self.cars[args['placa']][key] = args[key]

        cherrypy.response.status = "200"
        return f"<h1>Registro atualizado com sucesso!</h1><div> Placa: {args['placa']} <br> Marca: {self.cars[args['placa']]['marca']} <br> Modelo: {self.cars[args['placa']]['modelo']} \
                <br> Ano: {self.cars[args['placa']]['ano']} <br> Km: {self.cars[args['placa']]['km']}, <br> Combustível: {self.cars[args['placa']]['combustivel']} \
                <br> Proprietário: {self.cars[args['placa']]['proprietario']}</div>"

    @cherrypy.expose
    def car_delete(self, placa):
        if not placa in self.cars.keys():
            raise cherrypy.HTTPError(404,'Carro não Encontrado')

        self.cars.pop(placa)

        cherrypy.response.status = "200"
        return f"<h1>Registro deletado com sucesso!</h1>"

    @cherrypy.expose
    def person_index(self):
        return '<h1>Pessoas cadastradas</h1>' + '<hr>'.join(f"<div> CPF: {person['cpf']} <br> Nome: {person['nome']} <br> Cidade: {person['cidade']} \
                            <br> Data de Nascimento: {person['nascimento']} </div>" for person in self.people.values())
    
    @cherrypy.expose
    def person_create(self, **args):
        if not all(key in args.keys() for key in ['cpf', 'nome', 'cidade', 'nascimento']):
            raise cherrypy.HTTPError(400,'Dados incompletos!')            
        if not cpf_check(args['cpf']):
            raise cherrypy.HTTPError(422, 'CPF inválido!')
        if args['cpf'] in self.people   .keys():
            raise cherrypy.HTTPError(422, 'CPF já cadastrado')
        if not birth_check(args['nascimento']):
            raise cherrypy.HTTPError(422, 'Data de nascimento precisa ter o formato DD/MM/AAAA!')

        
        self.people[args['cpf']] = {'cpf': args['cpf'], 
                                    'nome': args['nome'], 
                                    'cidade': args['cidade'],
                                    'nascimento': args['nascimento']}
        
        cherrypy.response.status = "201"
        return f"<h1>Registro criado com sucesso!</h1>" + f"<div> CPF: {args['cpf']} <br> Nome: {args['nome']} <br> Cidade: {args['cidade']} \
                            <br> Data de nascimento: {args['nascimento']} </div>"

        

    @cherrypy.expose
    def person_read(self, cpf):
        if not cpf in self.people.keys():
            raise cherrypy.HTTPError(404,'Pessoa não Encontrada')

        person = self.people[cpf]
        return f"<h1>Resultado da Busca</h1><div> CPF: {cpf} <br> Nome: {person['nome']} <br> Cidade: {person['cidade']} \
                    <br> Data de Nascimento: {person['nascimento']} </div>"

    @cherrypy.expose
    def person_update(self, **args):
        if 'cpf' not in args.keys():
            raise cherrypy.HTTPError(400, 'Dados incompletos!')
        if not args['cpf'] in self.people.keys():
            raise cherrypy.HTTPError(404,'Pessoa não Encontrada')
        
        for key in args.keys():
            if key == 'nascimento' and not birth_check(args['nascimento']):
                raise cherrypy.HTTPError(422, 'Data de nascimento precisa ter o formato DD/MM/AAAA!')
        
            self.people[args['cpf']][key] = args[key] 

        cherrypy.response.status = "200"
        return f"<h1>Registro atualizado com sucesso!</h1>" + f"<div> CPF: {args['cpf']} <br> Nome: {self.people[args['cpf']]['nome']} <br> Cidade: {self.people[args['cpf']]['cidade']} \
                            <br> Data de nascimento: {self.people[args['cpf']]['nascimento']} </div>"

    @cherrypy.expose
    def person_delete(self, cpf):
        if not cpf in self.people.keys():
            raise cherrypy.HTTPError(404,'Pessoa não Encontrada')

        self.people.pop(cpf)

        for car in self.cars.values():
            if car['proprietario'] == cpf:
                car['proprietario'] = ""

        cherrypy.response.status = "200"
        return f"<h1>Registro deletado com sucesso!</h1>"
    

if __name__ == '__main__':
    
    dispatcher = cherrypy.dispatch.RoutesDispatcher()
    
    obj = Resource()

    dispatcher.connect('index', route='/', controller= obj, action = 'index', conditions=dict(method=['GET']))

    dispatcher.connect('index_carro', route='/cars', controller = obj, action = 'car_index', conditions=dict(method=['GET']))
    dispatcher.connect('criar_carro', route='/cars/create', controller = obj, action = 'car_create', conditions=dict(method=['POST']))
    dispatcher.connect('ler_carro', route='/cars/read', controller = obj, action = 'car_read', conditions=dict(method=['GET']))
    dispatcher.connect('atualizar_carro', route='/cars/update', controller = obj, action = 'car_update', conditions=dict(method=['PATCH']))
    dispatcher.connect('deletar_carro', route='/cars/delete', controller = obj, action = 'car_delete', conditions=dict(method=['DELETE']))

    dispatcher.connect('index_pessoa', route='/person', controller = obj, action = 'person_index', conditions=dict(method=['GET']))
    dispatcher.connect('criar_pessoa', route='/person/create', controller = obj, action = 'person_create', conditions=dict(method=['POST']))
    dispatcher.connect('ler_pessoa', route='/person/read', controller = obj, action = 'person_read', conditions=dict(method=['GET']))
    dispatcher.connect('atualizar_pessoa', route='/person/update', controller = obj, action = 'person_update', conditions=dict(method=['PATCH']))
    dispatcher.connect('deletar_pessoa', route='/person/delete', controller = obj, action = 'person_delete', conditions=dict(method=['DELETE']))

    conf = {'/':{'request.dispatch':dispatcher}}
    cherrypy.tree.mount(root = None, config = conf)

    cherrypy.config.update({'server.socket_port': 1234})
    cherrypy.engine.start()
    cherrypy.engine.block()
