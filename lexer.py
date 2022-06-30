import json
import graphviz
from ply.lex import lex 
from ply.yacc import yacc




#...........................................................................#
#                                                                           #
#                           ANALISIS LEXICO                                 #
#                                                                           #
#...........................................................................#

#Funcion que obtiene la columna
def ObtenerColumna(t):
  line_start = INPUT.rfind('\n', 0, t.lexpos) + 1
  return (t.lexpos-line_start)+1


reserved = {
    "reservada_inicio":r'INICIO',
    "reservada_fin" : r'FIN'
}
#Esta tupla es obligatoria ya que siempre deben ir
tokens =   (
    "operador_suma",
    "operador_resta",
    "operador_multiplicacion",
    'operador_division',
    'operador_igualacion',
    'operador_resto',
    'numero',
    'id'
) +tuple(reserved.keys()) 

#Ahora se ponen los tokens con t_*Inserte nombre del token*
t_reservada_inicio = r'INICIO'
t_reservada_fin = r'FIN'
t_operador_suma = r'\+'
t_operador_resta = r'-'
t_operador_multiplicacion = r'\*'
t_operador_division = r'/'
t_operador_resto = r'%'
t_numero = r'\d'

#Lexemas ignorados
t_ignore = r' \t\r'

"""
Propiedades de t
  t:
    - lineno: numero de linea
    - value: valor del lexema
    - type: nombre del token
"""

def t_id(t): # t_id
  r'[a-zA-Z_][a-zA-Z_0-9]*'
  for clave,valor in reserved.items(): #Recorre un diccionario con 2 iteradore
    if t.value == valor:
      t.type = clave
  return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value) #Le suma las lineas al analizador lexico

def t_error(t):
    print(t.lineno, ObtenerColumna(t), f"No se pudo reconocer el lexema '{t.value}'")
    t.lexer.skip(1)


#...........................................................................#
#                                                                           #
#                           ANALISIS SINTACTICO                             #
#                                                                           #
#...........................................................................#
      

#Grafo del arbol sintactico
Grafo =graphviz.Graph("G",filename="Grafo.png",format='png',node_attr= { 'height': '1'},directory='Grafos')
nodo = []
#La precedencia de las operaciones, se define de menos a mas
#Mientras mas arriba, menos importan
preendence = ( #Left o right se resfieren a la asociatividad o agrupacion
  ('left','operador_suma','operador_resta' ),
  ('left','operador_multiplicacion','operador_division', 'operador_resto' )
)
#Producciones
#LLevan la sintaxis de la gramatica entre comillas triples
#Van de abajo hacia arriba
def p_INITIAL (p):
  '''
  INITIAL : reservada_inicio EXPRESSIONS reservada_fin
  '''
 # / \          / \             / \           / \
  # |            |               |             |
  # p0           p1              p2            p3
  #EXPRESSIONS SERA UNA LISTA DE EXPRESIONES
  #Se le asigna a P0 la lista de expresiones
  p[0] = p[2]

def p_EXPRESSIONS(p):
  '''
  EXPRESSIONS : EXPRESSIONS E
              | E
  '''
  
  if len(p) == 3:
    p[0] = p[1]
    #Se le añade la expresion al arreglo agregado anteriormente
    p[0].append(p[2])
  else:
    #Se hace una lista de las expresiones retornadas, sera una lista porque van a ser mas de una,
    #Aunque ahorita solo tengan un elemento
    p[0] = [p[1]]
    
  
    

def p_E(p):
  #Los tokens y su posible orden
  ''' 
  E : E operador_suma E
    | E operador_resta E
    | E operador_multiplicacion E
    | E operador_division E
    | E operador_resto E
    | id
    | numero 
  '''
   #P puede tener dos longitudes, o 4, o 2
   #Si P tiene longitud de 2. entonces seroa de un solo elemento
  
  if len(p) == 2:
    #Le asignamos al lado izquierdo de la produccion los valores del lado derecho    
    p[0] = {
      'NoTerminal': False,
      'Linea': p.lexer.lineno,
      'Columna' : ObtenerColumna(p.lexer),
      'Tipo': (p[1]), #Retrorna el tipo de lexema
      'Valor': p[1]
    }
    

  else:
    #Si no mide 2 entonces mide 4 y es una operacion
    p[0] = {
      'NoTerminal': True,
      'Linea': p.lexer.lineno,
      'Columna' : ObtenerColumna(p.lexer),
      #Por alguna razon no reconoce lo tokens de suma
      'Tipo': 'Operacion',
      'Hijos':[p[1]
      ,{
      'NoTerminal': False,
      'Linea': p.lexer.lineno,
      'Columna' : ObtenerColumna(p.lexer),
      'Tipo': (p[2]), 
      'Valor': p[2]
      },p[3]]
    }

    
#Error sintactico
def p_error(p):
  print(p)
  if p:
    print(f"Sintaxis no válida cerca de '{p.value}' ({p.type})")
  else:
    print("Ninguna instrucción válida")



#Variable para leer
INPUT = r'''
INICIO
5*9+1-2
FIN
'''

#ANALIZADOR LEXICO
Lexer = lex()

INPUT = r'''
INICIO
56*9-5/2552
FIN
'''

Lexer.input(INPUT)
#Se necesita guardar los tokens en otra variable, para trabajar con ellos
Lexer2 = []
for tok in Lexer:
  Lexer2.append(tok)

def ObtenerTipo(t):
  tipo = None
  for tok in Lexer2:
    print (t, tok)
    if t == tok.value:
      tipo = (tok.type)
  return (tipo) 

#ANALIZADOR SINTACTICO
parser = yacc(start='INITIAL') #Le diremos de donde debe comenzar, aunque si no empieza por la primera produccion que estedefinida

ast = parser.parse(INPUT, Lexer) #Retorna una lista de instrucciones
Json = json.loads(json.dumps(ast, indent= 4, sort_keys= False))

#-----------------------------------------------------------------------------#
#                      Verificar el tipo de lexemaa obtenido                  #
#.............................................................................#



#print(Json)
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
#                                                                             #
#                         GENERACION DE GRAFO                                 #
#                                                                             #
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::#
#Recorre el Json creado
def Graficar(i):
  #Nombra las hojas de los iteracdores
    if i['NoTerminal'] == True:
      #Itera en los hijos
      #Crea un nodo para conectarlo con los hijos
      #El ID es muy importante porque grantiza que aunque hayan mas nodos con ese mismo valor, no
      #Se unan incorrectamente
      Grafo.node(name = str(id(i)), label=str(i['Tipo']))
      for j in i['Hijos']:
        #Obtiene el lexema del cual provienen los no terminales, eso solo si hace match con algun token
        if ObtenerTipo(j['Tipo']) != None:
          j['Tipo'] = ObtenerTipo(j['Tipo'])
        #Por cada hijo que tenga lo une con sus padres
        #Si es un simbolo terminal, entonces tendra un valor
        if j['NoTerminal'] == False:
          Grafo.node(name = str(id(j)), label=str(j['Tipo'])+" : "+ str(j['Valor']))
        else:
          Grafo.node(name = str(id(j)), label=str(j['Tipo']))
        Grafo.edge(str(id(i)), str(id(j)))
        #Luego de unirlos, pregunta si son No terminales, si  son No terminales entonces se agraga recursividad
        if j['NoTerminal'] == True:
          Graficar(j)


for i in Json:
  Graficar(i)

Grafo.view()




