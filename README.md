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

By default, concatenations are not directly shown in the RE. To make 
conversion simpler, they are added before converting the RE to NFA. 
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

After above steps, the RE should now only composed of basic operators and
operands (in cluding parentheses).

### RE to NFA transformation

REs are transformed to NFA using Thompson's Construction.

Before RE is transformed to NFA, it is transformed to stack form first.

To give you an example, assume we have a regular expression `ab|c`, it will be
transformed to:

    a b CONCATENATION c ALTERNATION

(The top of the stack is at the right)

After transformed to Stack form, transform REs to NFA is fairly easy. But now,
how do we transform RE to stack form?

We need 2 data structure: a stack for all elements (stack S) and a stack for 
operators (stack O). Stack S is the final output. Stack O is used as temperary
storage.

Now look at elements in the RE, assuming they are all identified in advance:

    a CONCATENATION b ALTERNATION c EOF

The first is `a`, it is put directly into stack S.

The second is `CONCATENATION`, it is put into stack O first, since we don't 
know whether it is safe to push it into stack S (or, we know it's not). The 
reason is, the second operator haven't show up yet. Also, the operators after
it might have higher precedence, or they have to be performed first. In this 
case, the operator can only be pushed into the stack after these operators 
with higher precedence are pushed into stack.

Then `b` is read. It is pushed into stack S directly.

When `ALTERNATION` is read, its precedence is compared against that of the top
operator os stack O, in this case, `CONCATENATION`. Since `ALTERNATION` has 
lower precedence, the `CONCATENATION` is taken out from stack O, and pushed 
into stack O. It is pushed into stack O because an operator after it with 
lower precedence is encountered, and that means it `CONCATENATION` can be 
safely performed.

Now the current operator needs to be pushed into stack S for the same reason
with above: the right operand has not show up.

Or you can look it this way: the current operator, `ALTERNATION`, has to be 
compared against the top operator of stack O again. Now stack O is empty, so
`ALTERNATION` is compared against nothing. We can assume `ALTERNATION` has
higher precedence than `nothing`. Therefore, `ALTERNATION` is pushed into the
stack O.

Then `c` is read. It is pushed into stack S directly.

When re finally read `EOF`, we reach the end of string. so all operands have
been pushed into stack S. Therefore, we can pop all operators from stack O and
push them into stack S respectivly.

In short, the core rule for precedence comparison is:

if the current operator has

* higher precedence -- push it into stack S
* same precedence -- top operator of stack S to stack O, push current operator to stack O
* lower precedence -- top operator of stack S to stack O, then compare again


### NFA to DFA transformation





### DFA minimization

Below is the algorithm used:

    T <- {Da, {D - Da}}
    P <- {}
    while P != T do
        P <- T
        T <- {}
        for each set p in P do
            T <- T | Split(p)
    
    Split(S):
        for each char do
            if c splits S into s1 and s2
                then return {s1, s2}

We first divide all states into accepting state and num-accepting state. Then
for each set of states, we check if their behavior on encountering certain
character are the same. In other words we check if the destination states of
transitions are the same. If not, then states with different destination 
states are splitted into two sets. This process keeps on until no more new
set of states can be generated. That is, we are done when all states in the
same set have same behavior.

