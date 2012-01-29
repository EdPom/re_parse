A Regular Expression Parser
===========================

This is a regular expression parser, it transforms a given regular expression 
to a non-deterministic finite automata (NFA), then transforms it into a 
deterministic finite automata (DFA).


Current Status
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


### Transforming RE to stack-form

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

Using this rule, we should be able to transform the regular expression to
stack form.



### RE to NFA transformation

After transforming the RE to stack form, doing the RE to NFA transformation is
easy.

Assuming all elements of RE are in stack S, and we pop out one element from
the stack at a time. Then for each element that popped out, if it's an operand
(character), we just create a finite automata (FA) for it (assume it's an `a`
character):

             'a'
    Start ---------> End

And push this finite automata into the stack.

If it's concatenation, we pop out the last two FAs in the stack, and connect
the front of last FA to the FA before it. Assume what we have are `a`, `b`,
and then `CONCATENATION`, the new FA will look like:

              'a'         'EPSILON'            'b'
    Start1 --------> End1 ---------> Start2 --------> End2 (accept)

Here the character `EPSILON` means empty string. In other words, we can move
from End1 to Start2 no matter what the input character is. So to match this
finite automata, the string should be `ab`.


Similarly, if the operator is `ALTERNATION`, we pop out the last two FAs and
connect them like this (Assume we have `a`, `b`,and then `ALTERNATION`):

        'EPSILON'            'a'          'EPSILON'
            +----> Start1 --------> End1 -----+
            |                                 |
            |                                 v
    NewStart                                NewEnd (Accept)
            |                                 ^
            |                                 |
            +----> Start2 --------> End2 -----+
        'EPSILON'            'b'          'EPSILON'

Again, `EPSILON` means we can make transition no matter what is in the input
string, so string `a` or `b` can be matched by this FA.


Now if the operator is `CLOSURE`, there would be a little different compared
to the previous operators, because `CLOSURE` only needs one operand (assume
we have `a` and `CLOSURE`):

                             'EPSILON'
                          +--------------+
                          |              |
            'EPSILON'     v     'a'      |   'EPSILON'
    NewStart ------->  Start1 --------> End1 --------> NewEnd (Accept)
          |                                              ^
          |                                              |
          +----------------------------------------------+
                             'EPSILON'

So according to this FA, strings that can be matched are `` (empty), `a`, `aa`
, `aaa`, etc.

But you might ask: "how do I know I have to make epsilon transition to Start1
or NewEnd in the first step?" Oh, I really don't know, because you can only
know it after you traverse the FA. You cannot know the 'right path' in advance
. And that's why FAs like this are called non-deterministic finite automata
(NFA).

After all elements are transformed to NFAs like this, the result shoud be just
one final NFA, which contains all small NFAs computed using the above method.



### NFA to DFA transformation

The NFA is transformed to DFA using the following algorithm:

    q0 <- epsilon-closure({n0})
    Q <- q0
    WorkList <- {q0}

    while (WorkList is not empty) do
        remove q from WorkList
        for each character c in the character set do
            t <- epsilon-closure( Delta(q, c) )
            T[q, c] <- t
            if t doesn't belongs to Q
                add t to Q and WorkList
        end
    end

The `epsilon-closure()` computes all states that can be reached by epsilon
transitions from the given set of states.

To transform the NFA to a DFA, we cannot use the original states in the NFA,
we have to make a new FA using the information in the NFA. To do this, we 
start with only one new state, which is a collection of `epsilon-closure()` of
the start state. then for each different input character, we check if the path
leads to a new set of states, we rename this set and make it a new state. But
we have to be cautious here, because `{n0, n1, n2}` may look like `{n0, n1}`,
but no, they are not the same set of states. We can only say the set A has
already been named if there is a set that is already named and which has the 
same members with this set A.

Also, the set containing the start state (`n0`) is the new start state (named
`q0` in the above algorithm), and the set containing accepting states is the 
new accepting state.



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



Other Stuff
-----------

If you are interested in the implementation details of this project, you can 
read comments in the code, or you can read my [blog] [1] .

[1]: http://edpom.tumblr.com/post/16651216995/writing-a-regular-expression-parser-1-regular
    "Writing A Regular Expression Parser (1) - Regular Expression?"