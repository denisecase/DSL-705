===============================================================================
      README.TXT
===============================================================================

   705 Domain Specific Language Project

   Unless required by applicable law or agreed to in writing, software
   is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
   CONDITIONS OF ANY KIND, either express or implied.

   Developer:     Denise Case
		  dmcase@ksu.edu
	          denisecase@gmail.com

===============================================================================
      QUICK START GUIDE  
===============================================================================

1) Make sure you have python installed correctly on your machine.
   To learn how to check and how to install if needed, please 
   read "Installing Python" at 
	http://people.cis.ksu.edu/~schmidt/705s12/installPython.html.

2) After your python installation is verified, unzip the contents 
   of the LittleLanguageProject.zip into a new folder.

3) Verify the contents match those listed under "About This Project" below.

4) Test drive the first reliability example: 
	From Windows Explorer, double-click "R1.py".
	Or open a command window here and type "run R1.txt".

5) Test drive the first goal specification example: 
	From Windows Explorer, double-click "MAS1.py".
	Or open a command window here and type "run MAS1.txt".

6) Use the LANGUAGE GUIDE to create your own program and save it in a myProg.txt file.

7) Run your program by typing "run myProg.txt" at the command line.

===============================================================================
       ABOUT THIS PROJECT
===============================================================================
 
Main DSL files:

	lex.py  - lexer for the language - breaks input text into tokens.
	parse.py - parser for the language - reads list of tokens 
		   and creates output trees as nested lists.
	interpreter.py - interpreter for the language. 
	run.py - used with a filename.ext argument to run a program written in this DSL
	README.txt - this readme file.
	LANGUAGEGUIDE.txt - a guide to the language

Sample programs:

	R1.txt  -  a program that demonstrates using the language to 
		      calculate reliability.
	MAS1.txt - a program that demonstrates using the language to 
                      test a goal specification for a multiagent system. 
	R1.py   - quick launch of UC-R1.txt
	MAS1.py - quick launch of UC-MAS1.txt

PLY (Python Lex-Yacc) - python implementation of compiler tools lex and yacc.

	ply/__init__.py  - PLY package
	ply/__init__.pyc - compiled PLY package
	ply/cpp.py      - lexical preprocessor for PLY
	ply/ctokens.py  - library of token specifications
	ply/lex.py   - python tokenizer  
	ply/lex.pyc  - compiled python tokenizer
	ply/yacc.py  - python syntax recognizer
	ply/yacc.pyc - compiled python syntax recognizer

Data files used for online simulation example

	data/data01.csv
	data/data02.csv
	data/data03.csv
	data/data04.csv
	data/data05.csv
	data/data06.csv
	data/data07.csv

===============================================================================
      2012
===============================================================================





