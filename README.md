# BMSTU Modelling HW2 Solver
This script allow you to get all data for BMSTU Modelling HW2
## Installing
Clone this repository and run:
`pip3 install -r requirements.txt`

## How to use
Open modelling.py in your IDE and fix schema according to your variant
Line 197: 
`schema = Schema(['a','b','c','d','e'])`
Use input names as arguments here

Line 198-209:
`schema.add_element('l',['a'],lyes)`
Add elements to your schema. 
First argument is name of new element. 
Second argument is array with inputs of new elements.
Third argument is logical functions. Functions land (logical and), lor (logical or), lnot (logical not), lyes (logical yes), lnand (sheffer stroke), lnor (logical nor) have already written and you can use it.
land, lor, lnand, lnor are working for an arbitrary number of inputs, lnot and lyes just for one input.

After writing your schema, you can run script
`./modelling.py [<CSV_FILENAME>]`

If you pass <CSV_FILENAME> argument script will generate this csv file which you can import to table editor and use it for report.

