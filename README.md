# Finding-name-patterns
This project determines first and last names for a given American Name

Syntax for running the code in CLI:
>python verify_name_pattern.py -n "ADAM KAISER"

To run this code: Paste the zipped folder 'Dictionaries' in the path where the code is pasted and unzip the folder

Output of the code would appear as mentioned below: - \
-----------------OUTPUT------------------------------ \
Processed Name Output will always be in  {Last Name, First Name Suffix} format\
Original Name:  ADAM KAISER \
Processed Name:  KAISER,ADAM \
Action:  Suggested Format printed \

The code will only work for the following name formats: -
1) One string in text {Name}
2) Two strings in text separated by comma or space {Name1, Name2} or {Name1 Name2}
3) Three strings in text separated by (space, comma) or (comma, space) or (space space)

For all other cases the program will not work
