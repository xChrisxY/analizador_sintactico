import re
from enum import Enum

# Definición de tokens
class TokenType(Enum):
    IDENTIFIER = 1
    NUMBER = 2
    STRING = 3  # Nuevo tipo para cadenas entre comillas dobles
    PLUS = 4
    MINUS = 5
    MULTIPLY = 6
    DIVIDE = 7
    ASSIGN = 8
    SEMICOLON = 9
    LPAREN = 10
    RPAREN = 11
    LBRACE = 12
    RBRACE = 13
    IF = 14
    ELSE = 15
    WHILE = 16
    FOR = 17
    PRINT = 18
    INPUT = 19
    VAR = 20
    EQUALS = 21
    LESS = 22
    GREATER = 23
    EOF = 24

class Token:
    def __init__(self, type, value, line, position):
        self.type = type
        self.value = value
        self.line = line
        self.position = position
    
    def __str__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, pos={self.position})"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if len(self.text) > 0 else None
        self.line = 1
        self.line_pos = 1
        
        # Palabras reservadas
        self.keywords = {
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'for': TokenType.FOR,
            'print': TokenType.PRINT,
            'input': TokenType.INPUT,
            'var': TokenType.VAR
        }
    
    def error(self):
        raise Exception(f'Carácter ilegal: {self.current_char} en línea {self.line}, posición {self.line_pos}')
    
    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.line_pos = 0
        
        self.pos += 1
        self.line_pos += 1
        
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def identifier(self):
        """Maneja identificadores y palabras clave."""
        start_pos = self.line_pos
        id_str = ''
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        
        # Comprueba si es una palabra clave
        token_type = self.keywords.get(id_str, TokenType.IDENTIFIER)
        return Token(token_type, id_str, self.line, start_pos)
    
    def number(self):
        """Maneja números enteros y decimales."""
        start_pos = self.line_pos
        num_str = ''
        
        while self.current_char is not None and self.current_char.isdigit():
            num_str += self.current_char
            self.advance()
        
        # Si hay un punto decimal y luego más dígitos
        if self.current_char == '.' and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit():
            num_str += self.current_char  # añade el punto
            self.advance()
            
            while self.current_char is not None and self.current_char.isdigit():
                num_str += self.current_char
                self.advance()
        
        return Token(TokenType.NUMBER, num_str, self.line, start_pos)
    
    def string(self):
        """Maneja cadenas entre comillas dobles."""
        start_pos = self.line_pos
        self.advance()  # Salta la comilla doble inicial
        string_value = ''
        
        while self.current_char is not None and self.current_char != '"':
            # Podría mejorarse para manejar secuencias de escape
            string_value += self.current_char
            self.advance()
        
        if self.current_char is None:
            raise Exception(f'Cadena sin cerrar en línea {self.line}')
        
        self.advance()  # Salta la comilla doble final
        return Token(TokenType.STRING, string_value, self.line, start_pos)
    
    def get_next_token(self):
        """Analizador léxico: descompone el texto de entrada en tokens."""
        while self.current_char is not None:
            start_pos = self.line_pos
            
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            if self.current_char.isdigit():
                return self.number()
            
            if self.current_char == '"':
                return self.string()
            
            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', self.line, start_pos)
            
            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', self.line, start_pos)
            
            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', self.line, start_pos)
            
            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', self.line, start_pos)
            
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.EQUALS, '==', self.line, start_pos)
                return Token(TokenType.ASSIGN, '=', self.line, start_pos)
            
            if self.current_char == '<':
                self.advance()
                return Token(TokenType.LESS, '<', self.line, start_pos)
            
            if self.current_char == '>':
                self.advance()
                return Token(TokenType.GREATER, '>', self.line, start_pos)
            
            if self.current_char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, ';', self.line, start_pos)
            
            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', self.line, start_pos)
            
            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', self.line, start_pos)
            
            if self.current_char == '{':
                self.advance()
                return Token(TokenType.LBRACE, '{', self.line, start_pos)
            
            if self.current_char == '}':
                self.advance()
                return Token(TokenType.RBRACE, '}', self.line, start_pos)
            
            self.error()
        
        return Token(TokenType.EOF, None, self.line, self.line_pos)

# Tabla de análisis LL(1)
class ParseTable:
    def __init__(self):
        # Esta es una tabla mejorada para nuestro lenguaje
        # Formato: {no_terminal: {terminal: producción}}
        self.table = {
            'Program': {
                TokenType.VAR: ['StatementList'],
                TokenType.IDENTIFIER: ['StatementList'],
                TokenType.IF: ['StatementList'],
                TokenType.WHILE: ['StatementList'],
                TokenType.FOR: ['StatementList'],
                TokenType.PRINT: ['StatementList'],
                TokenType.INPUT: ['StatementList'],
                TokenType.EOF: ['ε']  # Producción vacía
            },
            'StatementList': {
                TokenType.VAR: ['Statement', 'StatementList'],
                TokenType.IDENTIFIER: ['Statement', 'StatementList'],
                TokenType.IF: ['Statement', 'StatementList'],
                TokenType.WHILE: ['Statement', 'StatementList'],
                TokenType.FOR: ['Statement', 'StatementList'],
                TokenType.PRINT: ['Statement', 'StatementList'],
                TokenType.INPUT: ['Statement', 'StatementList'],
                TokenType.RBRACE: ['ε'],  # Para manejar el fin de un bloque
                TokenType.EOF: ['ε']
            },
            'Statement': {
                TokenType.VAR: ['VarDeclaration'],
                TokenType.IDENTIFIER: ['AssignmentStatement'],
                TokenType.IF: ['IfStatement'],
                TokenType.WHILE: ['WhileStatement'],
                TokenType.FOR: ['ForStatement'],
                TokenType.PRINT: ['PrintStatement'],
                TokenType.INPUT: ['InputStatement']
            },
            'VarDeclaration': {
                TokenType.VAR: ['VAR', 'IDENTIFIER', 'OptionalAssignment', 'SEMICOLON']
            },
            'OptionalAssignment': {
                TokenType.ASSIGN: ['ASSIGN', 'Expression'],
                TokenType.SEMICOLON: ['ε']
            },
            'AssignmentStatement': {
                TokenType.IDENTIFIER: ['IDENTIFIER', 'ASSIGN', 'Expression', 'SEMICOLON']
            },
            'IfStatement': {
                TokenType.IF: ['IF', 'LPAREN', 'Condition', 'RPAREN', 'Block', 'OptionalElse']
            },
            'OptionalElse': {
                TokenType.ELSE: ['ELSE', 'Block'],
                TokenType.VAR: ['ε'],
                TokenType.IDENTIFIER: ['ε'],
                TokenType.IF: ['ε'],
                TokenType.WHILE: ['ε'],
                TokenType.FOR: ['ε'],
                TokenType.PRINT: ['ε'],
                TokenType.INPUT: ['ε'],
                TokenType.RBRACE: ['ε'],
                TokenType.EOF: ['ε']
            },
            'WhileStatement': {
                TokenType.WHILE: ['WHILE', 'LPAREN', 'Condition', 'RPAREN', 'Block']
            },
            'ForStatement': {
                TokenType.FOR: ['FOR', 'LPAREN', 'ForInitializer', 'Condition', 'SEMICOLON', 'ForUpdate', 'RPAREN', 'Block']
            },
            # Nuevo no terminal para manejar tanto VarDeclaration como AssignmentStatement en el for
            'ForInitializer': {
                TokenType.VAR: ['VarDeclaration'],
                TokenType.IDENTIFIER: ['AssignmentStatement']
            },
            # Nuevo no terminal para manejar la actualización en el for
            'ForUpdate': {
                TokenType.IDENTIFIER: ['IDENTIFIER', 'ASSIGN', 'Expression']
            },
            'PrintStatement': {
                TokenType.PRINT: ['PRINT', 'LPAREN', 'PrintableExpression', 'RPAREN', 'SEMICOLON']
            },
            'PrintableExpression': {
                TokenType.IDENTIFIER: ['Expression'],
                TokenType.NUMBER: ['Expression'],
                TokenType.LPAREN: ['Expression'],
                TokenType.STRING: ['STRING']
            },
            'InputStatement': {
                TokenType.INPUT: ['INPUT', 'LPAREN', 'IDENTIFIER', 'RPAREN', 'SEMICOLON']
            },
            'Block': {
                TokenType.LBRACE: ['LBRACE', 'StatementList', 'RBRACE']
            },
            'Condition': {
                TokenType.IDENTIFIER: ['Expression', 'RelOp', 'Expression'],
                TokenType.NUMBER: ['Expression', 'RelOp', 'Expression'],
                TokenType.LPAREN: ['Expression', 'RelOp', 'Expression'],
                TokenType.STRING: ['Expression', 'RelOp', 'Expression']
            },
            'RelOp': {
                TokenType.EQUALS: ['EQUALS'],
                TokenType.LESS: ['LESS'],
                TokenType.GREATER: ['GREATER']
            },
            'Expression': {
                TokenType.IDENTIFIER: ['Term', 'ExpressionPrime'],
                TokenType.NUMBER: ['Term', 'ExpressionPrime'],
                TokenType.LPAREN: ['Term', 'ExpressionPrime'],
                TokenType.STRING: ['STRING']
            },
            'ExpressionPrime': {
                TokenType.PLUS: ['PLUS', 'Term', 'ExpressionPrime'],
                TokenType.MINUS: ['MINUS', 'Term', 'ExpressionPrime'],
                TokenType.RPAREN: ['ε'],
                TokenType.SEMICOLON: ['ε'],
                TokenType.EQUALS: ['ε'],
                TokenType.LESS: ['ε'],
                TokenType.GREATER: ['ε']
            },
            'Term': {
                TokenType.IDENTIFIER: ['Factor', 'TermPrime'],
                TokenType.NUMBER: ['Factor', 'TermPrime'],
                TokenType.LPAREN: ['Factor', 'TermPrime']
            },
            'TermPrime': {
                TokenType.MULTIPLY: ['MULTIPLY', 'Factor', 'TermPrime'],
                TokenType.DIVIDE: ['DIVIDE', 'Factor', 'TermPrime'],
                TokenType.PLUS: ['ε'],
                TokenType.MINUS: ['ε'],
                TokenType.RPAREN: ['ε'],
                TokenType.SEMICOLON: ['ε'],
                TokenType.EQUALS: ['ε'],
                TokenType.LESS: ['ε'],
                TokenType.GREATER: ['ε']
            },
            'Factor': {
                TokenType.IDENTIFIER: ['IDENTIFIER'],
                TokenType.NUMBER: ['NUMBER'],
                TokenType.LPAREN: ['LPAREN', 'Expression', 'RPAREN']
            }
        }
    
    def get_production(self, non_terminal, token_type):
        if non_terminal in self.table and token_type in self.table[non_terminal]:
            return self.table[non_terminal][token_type]
        return None  # Indica error sintáctico

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.parse_table = ParseTable()
        self.stack = ['$', 'Program']  # Pila de análisis, comienza con símbolo de fondo y símbolo inicial
    
    def error(self, expected=None):
        if expected:
            raise Exception(f"Error de sintaxis: se esperaba {expected} pero se encontró {self.current_token.type} en línea {self.current_token.line}, posición {self.current_token.position}")
        else:
            raise Exception(f"Error de sintaxis en línea {self.current_token.line}, posición {self.current_token.position}: token inesperado {self.current_token.type}")
    
    def consume(self, token_type):
        if self.current_token.type == token_type:
            print(f"Consumiendo token: {self.current_token}")
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(token_type)
    
    def match_terminal(self, terminal):
        # Si el terminal es un tipo de token específico, lo consumimos
        if terminal == self.current_token.type.name:
            print(f"Match: {terminal}")
            self.consume(getattr(TokenType, terminal))
            return True
        return False
    
    def parse(self):
        print("Iniciando análisis sintáctico...")
        
        while len(self.stack) > 0:
            # Obtener el elemento superior de la pila
            top = self.stack[-1]
            
            print(f"Pila: {self.stack}")
            print(f"Token actual: {self.current_token}")
            
            # Si hemos llegado al fondo de la pila
            if top == '$':
                if self.current_token.type == TokenType.EOF:
                    print("Análisis completado con éxito!")
                    return True
                else:
                    self.error("fin de archivo")
            
            # Si es un terminal (en forma de cadena que representa un tipo de token)
            if top in [t.name for t in TokenType]:
                if self.match_terminal(top):
                    self.stack.pop()  # Eliminar el terminal de la pila después de consumirlo
                else:
                    self.error(top)
            
            # Si es un no terminal
            elif isinstance(top, str) and top != 'ε':
                # Buscar producción en la tabla
                production = self.parse_table.get_production(top, self.current_token.type)
                
                if production is None:
                    self.error()
                
                # Reemplazar el no terminal por su producción
                self.stack.pop()
                
                # Agregar los símbolos de la producción a la pila en orden inverso
                for symbol in reversed(production):
                    if symbol != 'ε':  # No agregar símbolo vacío
                        self.stack.append(symbol)
                
                print(f"Aplicando producción: {top} -> {production}")
            
            # Si es epsilon, simplemente eliminarlo
            elif top == 'ε':
                self.stack.pop()
            
            else:
                self.error()
        
        return False  # No debería llegar aquí

def read_file():
    code = ""
    with open("codigo_5.txt", "r") as f:
        code = f.read()

    return code

# Función principal
def main():

    code = read_file()
    
    lexer = Lexer(code)
    parser = Parser(lexer)
    
    try:
        result = parser.parse()
        if result:
            print("El código es sintácticamente correcto.")
        else:
            print("Hay errores sintácticos en el código.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
