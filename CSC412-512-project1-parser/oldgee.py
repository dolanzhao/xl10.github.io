#! /usr/bin/python


import re, sys, string

debug = False
dict = { }


#  Expression class and its subclasses
class Expression( object ):
	def __str__(self):
		return "" 
	
class BinaryExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)

class Number( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)

class String( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)
	
class VariableRef( Expression ):
	def __init__(self, ident):
		global dict
		self.name = ident
		
	def __str__(self):
		return self.name
	

def error( msg ):
	#print msg
	sys.exit(msg)

# The "parse" function. This builds a list of tokens from the input string,
# and then hands it to a recursive descent parser for the PAL grammar.

def match(matchtok, tokens):
	tok = tokens.peek( )
	if (tok != matchtok): error("Expecting "+matchtok)
	return tokens.next( )
	
def parseFactor(tokens):
	"""factor     = number | 'True' | 'False' |  string | ident | '(' expression ')' """

	tok = tokens.peek( )
	if debug: print ("Factor: ", tok)
	if re.match(Lexer.number, tok):
		tokens.next( )
		return Number(tok)
	if re.match(Lexer.string, tok):
		tokens.next( )
		return String(tok)
	if re.match(Lexer.identifier, tok):
		tokens.next( )
		return VariableRef(tok)
	if tok == "(":
		tokens.next( )
		expr = parseExpr(tokens)
		tok = tokens.peek( )
		# if tok != ")":
		#	error("Missing )");
		tok = match(")", tokens)
		#tokens.next( )
		return expr
	error("Invalid operand")
	return None

def parseTerm(tokens):
	""" term    = factor { ('*' | '/') factor } """
	tok = tokens.peek( )
	if debug: print ("Term: ", tok)
	left = parseFactor(tokens)
	tok = tokens.peek( )
	while tok == "*" or tok == "/":
		savetok = tok
		tokens.next()
		right = parseFactor(tokens)
		left = BinaryExpr(savetok, left, right)
		tok = tokens.peek( )
	return left

def parseExpr(tokens):
	""" addExpr    = term { ('+' | '-') term } """
	tok = tokens.peek( )
	if debug: print ("Expr: ", tok)
	left = parseTerm(tokens)
	tok = tokens.peek( )
	while tok == "+" or tok == "-":
		savetok = tok
		tokens.next()
		right = parseTerm(tokens)
		left = BinaryExpr(savetok, left, right)
		tok = tokens.peek( )
	return left

def parseStmtList( tokens ):
        """ gee = { Statement } """
        tok = tokens.peek( )
        while tok is not None:
                parseStmt(tokens)
        return

def parse( text ) :
	tokens = Lexer( text )
	expr = parseExpr(tokens)
	print (str(expr))
	#     Or:
	# stmtlist = parseStmtList( tokens )
	# print str(stmtlist)
	return


# Lexer, a private class that represents lists of tokens from a Gee
# statement. This class provides the following to its clients:
#
#   o A constructor that takes a string representing a statement
#       as its only parameter, and that initializes a sequence with
#       the tokens from that string.
#
#   o peek, a parameterless message that returns the next token
#       from a token sequence. This returns the token as a string.
#       If there are no more tokens in the sequence, this message
#       returns None.
#
#   o removeToken, a parameterless message that removes the next
#       token from a token sequence.
#
#   o __str__, a parameterless message that returns a string representation
#       of a token sequence, so that token sequences can print nicely

class Lexer :
	
	
	# The constructor with some regular expressions that define Gee's lexical rules.
	# The constructor uses these expressions to split the input expression into
	# a list of substrings that match Gee tokens, and saves that list to be
	# doled out in response to future "peek" messages. The position in the
	# list at which to dole next is also saved for "nextToken" to use.
	
	special = r"\(|\)|\[|\]|,|:|;|@|~|;|\$"
	relational = "<=?|>=?|==?|!="
	arithmetic = "\+|\-|\*|/"
	#char = r"'."
	string = r"'[^']*'" + "|" + r'"[^"]*"'
	number = r"\-?\d+(?:\.\d+)?"
	literal = string + "|" + number
	#idStart = r"a-zA-Z"
	#idChar = idStart + r"0-9"
	#identifier = "[" + idStart + "][" + idChar + "]*"
	identifier = "[a-zA-Z]\w*"
	lexRules = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier
	
	def __init__( self, text ) :
		self.tokens = re.findall( Lexer.lexRules, text )
		self.position = 0
		self.indent = [ 0 ]
	
	
	# The peek method. This just returns the token at the current position in the
	# list, or None if the current position is past the end of the list.
	
	def peek( self ) :
		if self.position < len(self.tokens) :
			return self.tokens[ self.position ]
		else :
			return None
	
	
	# The removeToken method. All this has to do is increment the token sequence's
	# position counter.
	
	def next( self ) :
		self.position = self.position + 1
		return self.peek( )
	
	
	# An "__str__" method, so that token sequences print in a useful form.
	
	def __str__( self ) :
		return "<Lexer at " + str(self.position) + " in " + str(self.tokens) + ">"



def chkIndent(line):
        ct = 0
        for ch in line:
                if ch != " ": return ct
                ct += 1
        return ct
                

def delComment(line):
        pos = line.find("#")
        if pos > -1:
                line = line[0:pos]
                line = line.rstrip()
        return line

def mklines(filename):
        inn = open(filename, "r")
        lines = [ ]
        pos = [0]
        ct = 0
        for line in inn:
                ct += 1
                line = line.rstrip( )+";"
                line = delComment(line)
                if len(line) == 0 or line == ";": continue
                indent = chkIndent(line)
                line = line.lstrip( )
                if indent > pos[-1]:
                        pos.append(indent)
                        line = '@' + line
                elif indent < pos[-1]:
                        while indent < pos[-1]:
                                del(pos[-1])
                                line = '~' + line
                print ct, "\t", line
                lines.append(line)
	# print len(pos)
	undent = ""
	for i in pos[1:]:
		undent += "~"
	lines.append(undent)
	# print undent
        return lines



def main():
        """main program for testing"""
	global debug
	ct = 0
	for opt in sys.argv[1:]:
		if opt[0] != "-": break
		ct = ct + 1
		if opt == "-d": debug = True
        if len(sys.argv) < 2+ct:
                print "Usage:  %s filename" % sys.argv[0]
                return
        parse(string.join(mklines(sys.argv[1+ct]), ""))
        return


main()
