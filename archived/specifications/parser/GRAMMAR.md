# Grammar

This grammar is the source of truth for the parser design. It is derived from [LANGUAGE_SPEC.md](../../LANGUAGE_SPEC.md) and feeds the parser, CST, and AST specifications.

## Notation
This grammar uses EBNF-style notation.

## Program
module = { declaration } ;
program = module ;

## Declarations

declaration = variable_declaration
            | function_declaration ;

## Statements
statement = declaration
          | expression_statement
          | if_statement ;

variable_declaration = "let", identifier, "=", expression, ";" ;

function_declaration = "fn", identifier, "(", [ parameter_list ], ")", block ;
parameter_list = identifier, { ",", identifier } ;

expression_statement = expression, ";" ;

if_statement = "if", "(", expression, ")", block, [ "else", block ] ;


## Blocks
block = "{", { statement }, "}" ;

## Expressions
expression = assignment_expression ;

assignment_expression = logical_or_expression, [ "=", assignment_expression ] ;

logical_or_expression = logical_and_expression, { "||", logical_and_expression } ;
logical_and_expression = equality_expression, { "&&", equality_expression } ;
equality_expression = comparison_expression, { ( "==" | "!=" ), comparison_expression } ;
comparison_expression = additive_expression, { ( "<" | "<=" | ">" | ">=" ), additive_expression } ;
additive_expression = multiplicative_expression, { ( "+" | "-" ), multiplicative_expression } ;
multiplicative_expression = unary_expression, { ( "*" | "/" | "%" ), unary_expression } ;
unary_expression = [ ( "!" | "-" ) ], primary_expression ;

primary_expression = identifier
                   | number_literal
                   | string_literal
                   | "(", expression, ")" ;

## Parsing Strategy
The grammar is intended for recursive-descent parsing. It is unambiguous because declaration forms are distinguished by the leading keywords "let" and "fn", and operator precedence and associativity are defined explicitly from low precedence to high precedence.

## Lexical Elements
identifier = letter_or_underscore, { letter_or_digit_or_underscore } ;
number_literal = digit, { digit } ;
string_literal = '"', { string_char }, '"' ;
string_char = ? any character except '"' or '\\' ? | escape_sequence ;
escape_sequence = "\\n" | "\\t" | "\\r" | "\\\\" | '"' ;

letter_or_underscore = "A" | ... | "Z" | "a" | ... | "z" | "_" ;
letter_or_digit_or_underscore = letter_or_underscore | digit ;
digit = "0" | ... | "9" ;
