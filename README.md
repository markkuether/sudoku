# sudoku
This is an OOP exercise written in Python to solve a 9X9 sudoku puzzle. The objects use a compositional relationship of row-cells, column-cells, and block-cells. The goal is to build an OOP model that can be used to test multiple types of solutions. This model locks initial values in place, and allows adding or removing values as needed at the cell level. The model also tracks legal values for each cell, which is modified if other cell values in the row, column, or block are added or removed.  The rows, columns, and block objects also hold legal values to simplify logic for determining legal values.

## Solution 1: 
__fastsolver.py__ is an initial attempt to use strategies from a specific youtube channel to solve the puzzles. This has grown unweildy as each new approach has failed to resolve one of the test puzzles. This will be refactored into a module and main code file. The module will have more discreet functions to reduce repeated code used to test certain states on the sudoku board. It will also handle the overall functions used to reduce unknowns within the puzzle.  The main code file will simply apply the various functions in the module file and test to see if the board is completed.

## Solution 2:
__Unwritten__ will use recursion to provide a brute force attack. This will search for cells that have the fewest possible values, guess a value, then repeat until it can either go no further or has solved the problem. If the solution can not proceed further, it will backtrack and work through branches until the correct solution is found.
