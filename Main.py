import json
import graphviz
from ply.lex import lex 
from ply.yacc import yacc

class Gestor:
    def __init__(self):
        self.lexer = lex()
        self.INPUT = r'''
        INICIO
        56*9-5/2552
        FIN
        '''
        self.lexer.input(self.INPUT)

        self.reserved = (
        'reservada_inicio',
        'reservada_fin'
        )

        self.tokens = self.reserved + (
        'operador_suma',
        'operador_resata',
        'operador_multiplicacion',
        'operador_division',
        'operador_igualacion',
        'operador_resto',
        'numero',
        'id',
        )

        self.t_reservada_inicio = r'INICIO'
        self.t_reservada_fin = r'FIN'
        self.t_operador_suma = r'\+'
        self.t_operador_resata = r'-'
        self.t_operador_multiplicacion = r'\*'
        self.t_operador_division = r'/'
        self.t_operador_resto = r'%'
        self.t_numero = r'\d+'

        # Lexemas ignorados
        self.t_ignore = ' \t\r\n'
        for tok in self.lexer:
            print(tok)



    def getColumn(self,t):
        line_start = self.INPUT.rfind('\n', 0, t.lexpos) + 1
        return (t.lexpos-line_start)+1


    """
    t:
        - lineno: numero de linea
        - value: valor del lexema
        - type: nombre del token
    """

    def t_id(self, t): # t_id
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        if t.value in self.reserved: t.type = t.value
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno+=len(t.value)

    def t_error(self, t):
        print(t.lineno, self.getColumn(t), f"No se pudo reconocer el lexema '{t.value}'")
        t.lexer.skip(1)

    

Gestor()  