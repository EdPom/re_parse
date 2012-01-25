A Regular Expression Parser
===========================

This is a regular expression parser, it transforms a given regular expression 
to a non-deterministic finite automata (NFA), then transforms it into a 
deterministic finite automata (DFA).


The rule of RE
--------------

For now, this parser only accepts a regular expression that contains the basic
operators:

* Concatenation
* Alternation -- `|`
* Closure -- `*`
* One or more -- `+`
* Zero or one -- `?`

Any other operators are not yet implemented.


Procedure
---------

This part explains the procedure of the parser.

### Tokenizing

The regular expression (RE) that the parser gets is in the format of strings,
so the first thing it does is to determine what each character means in the
regular expression. For example, `[` means the beginning of an alternation 
block (alternation of all the characters inside between it and a right bracket
). But if there is a escaping character (`\`) before the bracket, then 
together, `\[` means the bracket character.

Letters and digits can be recognized easily.

Noted characters and operators are stored in a list of `(Type, Value)` pair.


### Adding missing concatenations and alternations

By default, concatenations are not directly shown in the RE. To make things
easy (or more complicated?), I want then to be included. 
Concatenations are added before a character when the character is a "normal 
character" (`a`, `1`, `\n`, etc.) or a left bracket or parenthese (`[`, `(`) 
and the character before it is a

* Closure -- `*`
* One or more -- `+`
* Normal character -- `a`, `1`, `\n`, etc.
* Right bracket or parenthese -- `]`, `)`

Unlike concatenation, alternations are specified in the RE already (if it is a
valid RE), so all the parser does for alternation is to transform the bracket
expression into a string of alternations.

For example,

    [1-4]

will be transformed to

    (1|2|3|4)



### Turn special operators into basic operators

To simplify the complexity, only basic operators (alternation, concatenation,
and closure) are supported, all other operators must be transformed to
combinations of these basic operators before they can be transformed to a NFA.

For example,

    a+

will be transformed to

    aa*


### RE to NFA transformation

REs are transformed to NFA using Thompson's Construction.


### NFA to DFA transformation

(under construction)


### DFA minimization

(under construction)

