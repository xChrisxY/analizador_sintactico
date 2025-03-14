import re
from enum import Enum
import tkinter as tk 
from tkinter import filedialog, scrolledtext, ttk
import sys
import io
from tkinter import font
import os

# Mantenemos todas las clases existentes (TokenType, Token, Lexer, ParseTable, Parser)
# Definición de tokens
class TokenType(Enum):
    IDENTIFIER = 1
    NUMBER = 2
    STRING = 3
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

# Nueva versión mejorada de la interfaz gráfica
class ModernParserGUI:
    def __init__(self, master):
        self.master = master
        master.title("Analizador Sintáctico")
        
        # Configurar estilos y temas
        self.setup_styles()
        
        # Configurar la ventana principal
        master.geometry("900x700")
        master.minsize(700, 500)
        
        # Crear la interfaz
        self.create_widgets()
        
        # Variable para la última ruta de archivo utilizada
        self.last_directory = os.path.expanduser("~")
        
        # Configurar colores para resaltado de sintaxis
        self.setup_syntax_highlighting()

    def setup_styles(self):
        # Crear un estilo personalizado
        self.style = ttk.Style()
        
        # Configurar tema
        if "azure" in self.style.theme_names():
            self.style.theme_use("azure")
        elif "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        
        # Colores
        self.bg_color = "#f5f5f5"
        self.accent_color = "#3498db"
        self.success_color = "#2ecc71"
        self.error_color = "#e74c3c"
        self.text_color = "#2c3e50"
        self.editor_bg = "#ffffff"
        self.output_bg = "#f9f9f9"
        
        # Configurar fuentes
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        
        self.code_font = font.Font(family="Consolas", size=11)
        self.heading_font = font.Font(family="Segoe UI", size=12, weight="bold")
        
        # Configurar estilos de los botones
        self.style.configure("TButton", font=self.default_font, padding=6)
        self.style.configure("Accent.TButton", background=self.accent_color, foreground="white")
        self.style.configure("Success.TButton", background=self.success_color, foreground="white")
        
        # Configurar estilos de las etiquetas
        self.style.configure("TLabel", font=self.default_font, background=self.bg_color)
        self.style.configure("Heading.TLabel", font=self.heading_font)
        
        # Configurar estilos de los frames
        self.style.configure("TFrame", background=self.bg_color)
        
        # Configurar el notebook (pestañas)
        self.style.configure("TNotebook", background=self.bg_color, tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab", font=self.default_font, padding=[10, 4])

    def setup_syntax_highlighting(self):
        # Configurar etiquetas para resaltado de sintaxis
        self.keyword_tags = ["if", "else", "while", "for", "print", "input", "var"]
        self.operator_tags = ["+", "-", "*", "/", "=", "==", "<", ">", ";"]
        
        # Colores para los diferentes tipos de tokens
        self.keyword_color = "#8e44ad"  # Morado para palabras clave
        self.string_color = "#27ae60"   # Verde para cadenas
        self.number_color = "#e67e22"   # Naranja para números
        self.operator_color = "#c0392b" # Rojo para operadores
        self.comment_color = "#7f8c8d"  # Gris para comentarios

    def highlight_syntax(self, event=None):
        # Limpiar resaltado previo
        for tag in self.keyword_tags + ["string", "number", "operator", "comment"]:
            self.input_text.tag_remove(tag, "1.0", "end")
        
        # Configurar colores para los diferentes tipos de tokens
        self.input_text.tag_configure("keyword", foreground=self.keyword_color, font=(self.code_font.cget("family"), self.code_font.cget("size"), "bold"))
        self.input_text.tag_configure("string", foreground=self.string_color)
        self.input_text.tag_configure("number", foreground=self.number_color)
        self.input_text.tag_configure("operator", foreground=self.operator_color)
        self.input_text.tag_configure("comment", foreground=self.comment_color, font=(self.code_font.cget("family"), self.code_font.cget("size"), "italic"))
        
        # Obtener todo el texto
        text = self.input_text.get("1.0", "end-1c")
        lines = text.split("\n")
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Resaltar palabras clave
            for keyword in self.keyword_tags:
                pattern = r"\b" + keyword + r"\b"
                for match in re.finditer(pattern, line):
                    start_idx = match.start()
                    end_idx = match.end()
                    self.input_text.tag_add("keyword", f"{line_num}.{start_idx}", f"{line_num}.{end_idx}")
            
            # Resaltar cadenas
            for match in re.finditer(r'"[^"]*"', line):
                start_idx = match.start()
                end_idx = match.end()
                self.input_text.tag_add("string", f"{line_num}.{start_idx}", f"{line_num}.{end_idx}")
            
            # Resaltar números
            for match in re.finditer(r'\b\d+(\.\d+)?\b', line):
                start_idx = match.start()
                end_idx = match.end()
                self.input_text.tag_add("number", f"{line_num}.{start_idx}", f"{line_num}.{end_idx}")
            
            # Resaltar operadores
            for op in self.operator_tags:
                for match in re.finditer(re.escape(op), line):
                    start_idx = match.start()
                    end_idx = match.end()
                    self.input_text.tag_add("operator", f"{line_num}.{start_idx}", f"{line_num}.{end_idx}")
            
            # Resaltar comentarios (si se añaden en el futuro)
            for match in re.finditer(r'//.*$', line):
                start_idx = match.start()
                end_idx = match.end()
                self.input_text.tag_add("comment", f"{line_num}.{start_idx}", f"{line_num}.{end_idx}")

    def create_widgets(self):
        # Crear contenedor principal
        main_container = ttk.Frame(self.master, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título de la aplicación
        header_frame = ttk.Frame(main_container, style="TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="Analizador Sintáctico", style="Heading.TLabel")
        title_label.pack(side=tk.LEFT, pady=5)
        
        # Notebook (pestañas) para organizar la interfaz
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de Editor
        editor_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(editor_frame, text="Editor")
        
        # Pestaña de Resultados
        output_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(output_frame, text="Resultados")
        
        # Configurar el área de texto para entrada de código con resaltado de línea actual
        editor_label = ttk.Label(editor_frame, text="Código Fuente:", style="TLabel")
        editor_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Frame para el editor con barra de números de línea
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Área de números de línea
        self.line_numbers = tk.Text(editor_container, width=4, padx=3, pady=5, takefocus=0,
                               bg="#f0f0f0", fg="#606060", border=0, font=self.code_font,
                               state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor principal
        self.input_text = tk.Text(editor_container, wrap=tk.NONE, padx=5, pady=5,
                             bg=self.editor_bg, fg=self.text_color, insertbackground=self.text_color,
                             selectbackground=self.accent_color, selectforeground="white",
                             font=self.code_font, undo=True, maxundo=100)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Agregar scrollbars horizontales y verticales al editor
        y_scroll = ttk.Scrollbar(editor_container, orient=tk.VERTICAL, command=self.input_text.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.input_text.configure(yscrollcommand=y_scroll.set)
        
        x_scroll = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.input_text.xview)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_text.configure(xscrollcommand=x_scroll.set)
        
        # Vincular eventos para resaltado de sintaxis y actualización de números de línea
        self.input_text.bind("<KeyRelease>", self.highlight_syntax)
        self.input_text.bind("<KeyRelease>", self.update_line_numbers, add="+")
        self.input_text.bind("<MouseWheel>", self.update_line_numbers)
        
        # Frame para botones de acción
        button_frame = ttk.Frame(editor_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botones de acción
        self.load_btn = ttk.Button(button_frame, text="Cargar Archivo", command=self.load_file)
        self.load_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_btn = ttk.Button(button_frame, text="Guardar Archivo", command=self.save_file)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.analyze_btn = ttk.Button(button_frame, text="Analizar Código", style="Accent.TButton", command=self.analyze_code)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Limpiar Editor", command=self.clear_editor)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Configurar el área de salida de resultados
        output_label = ttk.Label(output_frame, text="Resultados del Análisis:", style="TLabel")
        output_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Área de resultados con scroll
        self.output_area = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, padx=10, pady=10,
                                                bg=self.output_bg, fg=self.text_color, font=self.code_font)
        self.output_area.pack(fill=tk.BOTH, expand=True)
        
        # Botón para limpiar resultados
        self.clear_output_btn = ttk.Button(output_frame, text="Limpiar Resultados", command=self.clear_output)
        self.clear_output_btn.pack(anchor=tk.E, pady=10)
        
        # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para analizar código")
        self.status_bar = ttk.Label(main_container, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
                # Barra de estado
        self.status_var = tk.StringVar()
        self.status_var.set("Listo para analizar código")
        self.status_bar = ttk.Label(main_container, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def update_line_numbers(self, event=None):
        """Actualiza los números de línea en el editor."""
        lines = self.input_text.get("1.0", "end-1c").split("\n")
        line_numbers_text = "\n".join(str(i) for i in range(1, len(lines) + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers_text)
        self.line_numbers.config(state=tk.DISABLED)

    def load_file(self):
        """Carga un archivo de código en el editor."""
        file_path = filedialog.askopenfilename(
            initialdir=self.last_directory,
            title="Seleccionar archivo",
            filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
        )
        
        if file_path:
            self.last_directory = os.path.dirname(file_path)
            with open(file_path, "r") as file:
                code = file.read()
                self.input_text.delete("1.0", "end")
                self.input_text.insert("1.0", code)
                self.update_line_numbers()
                self.status_var.set(f"Archivo cargado: {os.path.basename(file_path)}")

    def save_file(self):
        """Guarda el contenido del editor en un archivo."""
        file_path = filedialog.asksaveasfilename(
            initialdir=self.last_directory,
            title="Guardar archivo",
            filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
        )
        
        if file_path:
            self.last_directory = os.path.dirname(file_path)
            with open(file_path, "w") as file:
                file.write(self.input_text.get("1.0", "end-1c"))
                self.status_var.set(f"Archivo guardado: {os.path.basename(file_path)}")

    def analyze_code(self):
        """Analiza el código ingresado en el editor."""
        code = self.input_text.get("1.0", "end-1c")
        if not code.strip():
            self.status_var.set("Error: No hay código para analizar.")
            return
        
        try:
            lexer = Lexer(code)
            parser = Parser(lexer)
            result = parser.parse()
            
            if result:
                self.output_area.insert("end", "Análisis completado con éxito!\n")
                self.status_var.set("Análisis completado con éxito.")
            else:
                self.output_area.insert("end", "Error durante el análisis.\n")
                self.status_var.set("Error durante el análisis.")
        
        except Exception as e:
            self.output_area.insert("end", f"Error: {str(e)}\n")
            self.status_var.set(f"Error: {str(e)}")

    def clear_editor(self):
        """Limpia el contenido del editor."""
        self.input_text.delete("1.0", "end")
        self.update_line_numbers()
        self.status_var.set("Editor limpiado.")

    def clear_output(self):
        """Limpia el área de resultados."""
        self.output_area.delete("1.0", "end")
        self.status_var.set("Resultados limpiados.")

# Función principal para ejecutar la aplicación
def main():
    root = tk.Tk()
    app = ModernParserGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()