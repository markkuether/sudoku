import sudokuobjects as so
import os
import sys

'''
Techniques mirroring those from RFC963 on YouTube
https://www.youtube.com/watch?v=b123EURtu3I
https://www.youtube.com/channel/UCrowx1RqiPhsg0LLUAWKObg
'''


def getPath():
    '''
    Get path of running application
    Copied shamelessly from Stack Overflow
    https://stackoverflow.com/questions/404744/
    determining-application-path-in-a-python-exe-generated-by-pyinstaller
    '''

    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return application_path


def getPuzzle(file: str) -> list:
    '''
    Reads puzzle from a file into 
    a list of text lines

    Returns the list of text lines
    '''
    puzzle = []
    with open(file, "r") as f:
        # Easiest way to read w/o newline:
        # Reads all lines with newline at end into a string
        # Splits string on newline into a list
        puzzle = f.read().splitlines()

    return puzzle


def populateCells(puzzle: list, allCells: list):
    '''
    Parses the list of text lines
    Assigns any number > 0 to the
    corresponding cell object.

    Returns allCells
    '''
    cellIndex = 0
    for row in puzzle:
        for number in row:
            numVal = int(number)
            allCells[cellIndex].number = numVal
            if numVal:
                allCells[cellIndex].locked = True
            cellIndex += 1

    return allCells


def singleVals(allCells: list, haveGoal: int):
    '''
    Search all cells for single possible values.
    Decrement haveGoal as needed 

    Return updated calls, haveGoal, and success
    '''

    bFound = False
    lastRow = 0
    for cell in allCells:
        if cell.row.id != lastRow:
            print()
            lastRow = cell.row.id
        print(
            f"Row {cell.row.id} Cell {cell.id}: {cell.number} - {cell.possible}")
        if (len(cell.possible) == 1) and (cell.number == 0):
            cell.number = cell.possible.pop()
            haveGoal -= 1
            bFound = True
            print(f"  Setting value to {cell.number}")

    return (allCells, haveGoal, bFound)


def hiddenSingles(allRows: list, allCols: list, allBlocks: list, haveGoal: int):
    '''
    Count the frequencies of each possible value
    within each structure. If any possible value within
    the structure only appears once, that cell must
    have that value.

    Return allRows, allCols, allBlocks, goal, and success
    '''
    desc = ["Rows", "Columns", "Blocks"]
    structures = [allRows, allCols, allBlocks]
    bFound = False

    # Loop through all rows, cols, and blocks
    for item, structure in enumerate(structures):
        print()
        print(f"Analyzing {desc[item]}...")
        for element in structure:
            print(f"  #{element.id}")
            valCells = {val: [] for val in element.possible}
            elmCells = element.cells

            # Populate dictionary with value frequencies
            for cell in elmCells:
                if len(cell.possible):
                    for eachVal in cell.possible:
                        valCells[eachVal].append(cell)

            # Find any values with only a single cell
            for eachVal in valCells:
                #print(f"{eachVal}:", end="")
                # for eachCell in valCells[eachVal]:
                #    print(f"{eachCell.id},", end="")
                # print()
                if len(valCells[eachVal]) == 1:
                    singleCell = valCells[eachVal][0]
                    print(f"    Cell {singleCell.id} = {eachVal}")
                    singleCell.number = eachVal
                    haveGoal -= 1
                    bFound = True
    print()
    return(allRows, allCols, allBlocks, haveGoal, bFound)


def pairVals(allRows, allCols, allBlocks):
    '''
    Only reduces possible values. Does not fill in
    unknown values.

    If any row,col, or block has two cells that have
    the same two values EXCLUSIVELY in both cells,
    those two individual values can be eliminated 
    from other cells within the row or col.

    If both cells are in the same block and row or col,
    those values may be removed from the block as well.

    Returns allRows, allCols, allBlocks, success.
    '''
    bFound = False
    desc = ["Rows", "Columns", "Blocks"]
    structures = [allRows, allCols, allBlocks]

    # Loop through all rows, columns, blocks
    for item, structure in enumerate(structures):
        print()
        print(f"Analyzing {desc[item]}...")
        for element in structure:
            elmCells = element.cells

            # Gather all cells with only 2 values
            pairs = []
            for cell in elmCells:
                if (cell.number == 0) and (len(cell.possible) == 2):
                    #print(f"adding cell {cell.id}")
                    pairs.append(cell)

            # Determine if any pairs are the same:
            # For exclusive pairs, any matches must be the only matches
            if len(pairs) > 1:
                for limit in range(len(pairs), 0, -1):
                    for compare in range(1, limit):
                        itemPair = pairs[0].possible
                        compPair = pairs[compare].possible
                        print(
                            f"cell {pairs[0].id}: {itemPair}", end="")
                        print(f" cell {pairs[compare].id}: {compPair}")
                        # Test if sets the same numbers
                        if len(itemPair.intersection(compPair)) == 2:
                            print(
                                f"  intersection = {itemPair.intersection(compPair)}")
                            # Eliminate all values for other cells within element
                            pairCells = [pairs[0].id, pairs[compare].id]
                            #print(f"  pair id's = {pairCells}")
                            for cell in elmCells:
                                # print(
                                #    f"  Checking cell: {cell.id} possible: {cell.possible}")
                                if cell.id not in pairCells:
                                    for val in itemPair:
                                        if val in cell.possible:
                                            print(
                                                f"    Clearing {val} from cell {cell.id} with value {cell.number}")
                                            cell.isNot(val)
                                            bFound = True
                            break  # out of compare loop
                    pairs.append(pairs.pop(0))  # Cycle order of elements
    print()
    return (allRows, allCols, allBlocks, bFound)


def pointingPair(allRows, allCols, allBlocks):
    '''
    Only reduces possible values. Does not fill in
    unknown values.

    If two of three cells in a block EXCLUSIVELY contain
    the same possible value, AND they are in the same
    row or column, then that value may be removed
    from all other possible values in that row or col.

    Returns allRows, allCols, allBlocks, success.
    '''
    bFound = False

    # Loop across all block structures
    for block in allBlocks:
        print()
        print(f"Checking Block {block.id}...")
        valCells = {val: [] for val in block.possible}
        blockCells = block.cells

        # Populate dictionary with value frequencies
        for cell in blockCells:
            if (not cell.number) and (len(cell.possible)):
                for eachVal in cell.possible:
                    valCells[eachVal].append(cell)

        # Check any values contained by 2 or 3 cells
        for val in valCells:
            if len(valCells[val]) in [2, 3]:
                print(f"  Possible value: {val}")
                cellRows = set()
                cellCols = set()
                for cell in valCells[val]:
                    cellRows.add(cell.row)
                    cellCols.add(cell.column)

                # Check if all values in same row
                if len(cellRows) == 1:
                    print(f"    {val} in same Row")
                    thisRow = cellRows.pop()
                    rowCells = thisRow.cells
                    for cell in rowCells:
                        if cell not in valCells[val]:
                            if val in cell.possible:
                                print(
                                    f"      Clear cell {cell.id}: {val} with number {cell.number}")
                                cell.isNot(val)
                                bFound = True

                # Check if all values in same col
                if len(cellCols) == 1:
                    print(f"    {val} in same Col")
                    thisCol = cellCols.pop()
                    colCells = thisCol.cells
                    for cell in colCells:
                        if cell not in valCells[val]:
                            if val in cell.possible:
                                print(f"      Clear cell {cell.id}: {val}")
                                cell.isNot(val)
                                bFound = True
    print()
    return (allRows, allCols, allBlocks, bFound)


def claimingPair(allRows, allCols, allBlocks):
    '''
    Only reduces possible values. Does not fill in
    unknown values.

    If two of three cells in a row or column EXCLUSIVELY 
    contain the same possible value, AND they are in 
    the same block, then that value may be removed
    from all other possible values in that block.

    Returns allRows, allCols, allBlocks, success.
    '''
    bFound = False
    desc = ["Rows", "Columns"]
    structures = [allRows, allCols]

    # Loop over all rows and columns
    for item, structure in enumerate(structures):
        print()
        print(f"Analyzing {desc[item]}...")

        # Create dictionary to hold value frequencies
        for element in structure:
            print(f"#{element.id}")
            valCells = {val: [] for val in element.possible}

            # Populate dictionary with cells holding possible value
            elmCells = element.cells
            for cell in elmCells:
                if not cell.number:
                    for val in cell.possible:
                        valCells[val].append(cell)

            # Check row or col for 2 or 3 of the same values
            for val in valCells:
                blocks = set()
                if len(valCells[val]) in (2, 3):
                    print(f"  Checking value {val}")
                    for cell in valCells[val]:
                        blocks.add(cell.block)

                    # Check if values are in the same block
                    if len(blocks) == 1:
                        print(f"    {val} is a candidate")
                        thisBlock = blocks.pop()
                        blockCells = thisBlock.cells

                        # Remove possible value for other cells in block
                        for cell in blockCells:
                            if (cell not in valCells[val]) and (val in cell.possible):
                                cell.isNot(val)
                                print(
                                    f"      Removing {val} from block {thisBlock.id} cell {cell.id}")
                                bFound = True
    print()
    return (allRows, allCols, allBlocks, bFound)


def tripleVals(allRows, allCols, allBlocks):
    '''
    Only reduces possible values. Does not fill in
    unknown values.

    If three cells in a structure contain either 2 or 3
    values AND they all belong to the same set of
    3 numbers, those numbers may be removed from other
    cells within that structure.

    Returns allRows, allCols, allBlocks, success.
    '''

    desc = ["Rows", "Columns", "Blocks"]
    structures = [allRows, allCols, allBlocks]
    bFound = False

    # Loop through all rows, cols, and blocks
    for item, structure in enumerate(structures):
        print()
        print(f"Analyzing {desc[item]}...")
        for element in structure:
            print(f"  #{element.id}")
            valCells = {val: [] for val in element.possible}
            elmCells = element.cells

            # Gather candidate cells with 2 or 3 possible values
            candidates = []
            for cell in elmCells:
                if (not cell.number) and (len(cell.possible) in (2, 3)):
                    candidates.append(cell)

            # If we have at least three candidates, check for triples
            if len(candidates) > 2:
                print(f"    Found {len(candidates)} candidates")

                # Get potential values from cells
                cellVals = set()
                for cell in candidates:
                    cellVals = cellVals.union(cell.possible)

                # Generate possible triples
                triples = []
                valList = list(cellVals)
                while len(valList) > 3:
                    valListLen = len(valList)
                    for digitTwo in range(1, len(valList)-1):
                        for digitThree in range(digitTwo+1, len(valList)):
                            thisTriple = set()
                            thisTriple.add(valList[0])
                            thisTriple.add(valList[digitTwo])
                            thisTriple.add(valList[digitThree])
                            #print(f"({thisTriple})", end="")
                            triples.append(thisTriple)
                    # print()
                    valList.pop(0)
                if len(valList) == 3:
                    thisTriple = set((valList[0], valList[1], valList[2]))
                    triples.append(thisTriple)

                # Check if three candidate cells hold members of a triple
                if len(triples):
                    print(f"    {len(triples)} triples found")
                    for triple in triples:
                        tripleCells = []
                        for cell in candidates:
                            if len(cell.possible.intersection(triple)) == len(cell.possible):
                                tripleCells.append(cell)
                                print(
                                    f"    Cell {cell.id} member of triple {triple}")

                        # Remove values from other cells
                        # Converting to sets and using intersection may be more direct
                        if len(tripleCells) == 3:
                            for cell in candidates:
                                if cell not in tripleCells:
                                    checkVals = cell.possible
                                    for val in checkVals:
                                        if val in triple:
                                            cell.isNot(val)
                                            bFound = True
                                            print(
                                                f"      Removing {val} from cell {cell.id}")

                            # Stop looking for triples.
                            break
    print()
    return (allRows, allCols, allBlocks, bFound)


def findRect(cells: list):
    '''
    Used for XWing.
    Provided a list of cells, this uses the row and column
    properties to determine if the cells form a
    rectangle on the board. 

    Returns a list of tuples [(row nums),(col nums)] that make up the
    rectangle.  If no rectangle is found, the tuples will be
    empty.
    '''

    print()
    print("  Looking for rectangle...")
    rectangle = []
    lines = {}
    # Check all cell combinations for lines
    for thisCell in range(len(cells)-1):
        for nextCell in range(thisCell+1, len(cells)):
            row1 = cells[thisCell].row.id
            row2 = cells[nextCell].row.id
            col1 = cells[thisCell].column.id
            col2 = cells[nextCell].column.id
            print()
            print(f" {cells[thisCell].id} row {row1} col {col1}")
            print(f" {cells[nextCell].id} row {row2} col {col2}")

            line = ()
            if row1 == row2:
                print(f"    Horizontal Line")
                line = ("h", min([col1, col2]), max([col1, col2]))
            elif col1 == col2:
                print(f"    Veritcal Line")
                line = ("v", min([row1, row2]), max([row1, row2]))

            if line in lines:
                lines[line] += 1
            elif len(line):
                lines[line] = 1

    rows = ()
    cols = ()
    for line in lines:
        if lines[line] == 2:
            if line[0] == "v":
                rows = (line[1], line[2])
                print(f"    Rec - Rows:{rows},", end="")
            else:
                cols = (line[1], line[2])
                print(f" Cols:{cols}", end="")
    print()

    rectangle.append(rows)
    rectangle.append(cols)
    return rectangle


def clearDupes(value: int, rectangle: list, allRows: list, allCols: list, element: int):
    '''
    Used for XWing
    Eliminates values from the opposite structure when an
    XWing structure is found.

    element=0 -> looking through rows - eliminate values from columns
    element=1 -> looking through cols - eliminate values from rows

    Returns allRows, allCols, and bFound
    '''
    bFound = False
    row1, row2 = rectangle[0]
    col1, col2 = rectangle[1]

    # Switch positions so we work on the opposite structure
    swRect = [rectangle[1], rectangle[0]]
    structures = [allCols, allRows]
    structure = structures[element]
    for item in structure:
        if item.id in swRect[element]:
            itemCells = item.cells
            for cell in itemCells:
                if value in cell.possible:
                    # Do not remove values from XWing structure cells
                    if (not element) and (cell.row.id not in [row1, row2]):
                        bFound = True
                        cell.isNot(value)
                    elif (element) and (cell.column.id not in [col1, col2]):
                        bFound = True
                        cell.isNot(value)

    return (allRows, allCols, bFound)


def xWing(allRows, allCols):
    '''
    Only reduces possible values. Does not fill in
    unknown values.

    If a row has a value in only two cells, and another 
    row has that same value only in the same
    column, that value may be removed from other cells
    in either of those columns.

    This also applies to columns and rows.  

    Returns allRows, allCols, allBlocks, success.
    '''
    desc = ["Rows", "Columns"]
    structures = [allRows, allCols]
    bFound = False

    # Loop over structures 1-8
    for item, structure in enumerate(structures):
        print(f"Analyzing {desc[item]}")
        pairCells = {val: [] for val in range(1, 10)}
        # If collecting all pairs across all structures,
        # Can loop over all rows or cols.
        for element in structure:
            #element = structure[index]
            print(f"  #{element.id}")
            valCells = {val: [] for val in element.possible}
            elmCells = element.cells

            # Add cells to dictionary of values
            for cell in elmCells:
                if not cell.number:
                    for val in cell.possible:
                        #print(f"    {val} - cell {cell.id}")
                        valCells[val].append(cell)

            # Gather cells where structure holds two copies of value.
            for val in valCells:
                if len(valCells[val]) == 2:
                    print(f"    {val} is in 2 cells")
                    pairCells[val] += valCells[val]
                    print(f"      {val} has {len(pairCells[val])} cells")

        # After gathering cells for all rows or cols
        # Check pairs to at least 4 cells containing each value.
        for val in pairCells:
            if len(pairCells[val]) >= 4:
                # Check if we have an XWing structure
                print()
                print(f"  VAL {val}")
                rectangle = findRect(pairCells[val])
                if len(rectangle[0]):
                    # Clear all dupe values from opposite structures
                    # item=0 -> rows. item=1 -> cols
                    allRows, allCols, bFound = clearDupes(
                        val, rectangle, allRows, allCols, item)
                    if bFound:
                        break

    return (allRows, allCols, bFound)


def clearOtherVals(keepVals, cells):
    '''
    Look for any values in cells that are not
    included in vals. Remove those values

    return Cells and bFound
    '''
    bFound = False
    for cell in cells:
        for val in cell.possible:
            if val not in keepVals:
                cell.isNot(val)
                bFound = True

    return (cells, bFound)


def hiddenPair(allRows, allCols, allBlocks):
    '''
    Only reduces possible values. Does not fill in
    unknown values.

    If a structure has two values that both exist 
    EXCLUSIVELY two cells of that structure, any
    other values within those two cells may be
    eliminated.

    Returns allRows, allCols, allBlocks, success.
    '''
    # Loop over all structures
    desc = ["Rows", "Columns", "Blocks"]
    structures = [allRows, allCols, allBlocks]
    bFound = False

    for item, structure in enumerate(structures):
        print(f"Analyzing {desc[item]}")
        for element in structure:
            print(f"  #{element.id}")
            #valCells = {val: [] for val in element.possible}
            elmCells = element.cells

            testSet = {}
            for thisCell in range(8):
                for nextCell in range(thisCell+1, 9):
                    if (not elmCells[thisCell].number) and (not elmCells[nextCell].number):
                        testSet = set(elmCells[thisCell].possible).intersection(
                            set(elmCells[nextCell].possible))
                        if len(testSet) == 2:
                            print(f"    Found pair {testSet}")
                            theseCells = [
                                elmCells[thisCell], elmCells[nextCell]]
                            theseCells, bFound = clearOtherVals(
                                testSet, theseCells)

    return (allRows, allCols, allBlocks, bFound)


def printCells(allRows):
    '''
    Prints the values of all cells
    in a 3X3 block framework

    No Return
    '''
    print("-------------")
    for row in allRows:
        rowCells = row.cells
        print("|", end="")
        for cell in rowCells:
            if cell.number:
                print(f"{cell.number}", end="")
            else:
                print(" ", end="")
            if not (cell.id % 3):
                print("|", end="")
        print()
        if not (row.id % 3):
            print("-------------")


def cellAssignments(allRows, allCols, allBlocks):
    print("CELL ASSIGNMENTS")
    desc = ["Row", "Column", "Block"]
    structures = [allRows, allCols, allBlocks]
    for item, structure in enumerate(structures):
        for element in structure:
            print()
            print(f"{desc[item]}{element.id}")
            print(f"cells: ", end="")
            for cell in element.cells:
                print(f"{cell.id}", end=", ")
            print()
    print()


# Generate empyt Sudoku objects
oneBoard = so.Board()
allObjects = oneBoard.buildBoard()
allCells, allRows, allCols, allBlocks = allObjects

# Populate cells with known values
filePath = getPath()
fileName = "s_board2.txt"
fullFile = filePath + "/" + fileName
puzzle = getPuzzle(fullFile)
allCells = populateCells(puzzle, allCells)

print("STARTING BOARD")
print("==============")
printCells(allRows)
print()

# Determine number of cells to solve
haveGoal = 0
for cell in allCells:
    if not cell.number:
        haveGoal += 1

# Repeat algorithm until all cells solved
count = 0
while haveGoal:
    #cellAssignments(allRows, allCols, allBlocks)
    count += 1
    bFound = False

    # First approach - populate all cells with
    # only a single value possible.

    print("SINGLES VALUES")
    print("===============")
    allCells, haveGoal, bFound = singleVals(allCells, haveGoal)

    #cellAssignments(allRows, allCols, allBlocks)

    if not bFound:
        print("No Single Values Found")
    else:
        printCells(allRows)
    print()

    # single values no longer available
    if haveGoal and not bFound:
        print("HIDDEN SINGLES")
        print("=============")
        allRows, allCols, allBlocks, haveGoal, bFound = hiddenSingles(
            allRows, allCols, allBlocks, haveGoal)
        #cellAssignments(allRows, allCols, allBlocks)

        if not bFound:
            print("No Hidden Values Found")
        else:
            printCells(allRows)
        print()

    if haveGoal and not bFound:
        print("EXCLUSIVE PAIRS")
        print("===============")
        allRows, allCols, allBlocks, bFound = pairVals(
            allRows, allCols, allBlocks)
        if not bFound:
            print("Unable to reduce possible values")
        else:
            print("Reduced Possible Values")
        print()

    if haveGoal and not bFound:
        print("POINTING PAIR")
        print("=============")
        allRows, allCols, allBlocks, bFound = pointingPair(
            allRows, allCols, allBlocks)
        if not bFound:
            print("Unable to reduce possible values")
        else:
            print("Reduced Possible Values")
        print()

    if haveGoal and not bFound:
        print("CLAIMING PAIR")
        print("=============")
        allRows, allCols, allBlocks, bFound = claimingPair(
            allRows, allCols, allBlocks)
        if not bFound:
            print("Unable to reduce possible values")
        else:
            print("Reduced Possible Values")
        print()

    if haveGoal and not bFound:
        print("TRIPLES VALUES")
        print("==============")
        allRows, allCols, allBlocks, bFound = tripleVals(
            allRows, allCols, allBlocks)
        if not bFound:
            print("Unable to reduce possible values")
        else:
            print("Reduced Possible Values")
        print()

    if haveGoal and not bFound:
        print("XWING VALUES")
        print("============")
        allRows, allCols, bFound = xWing(allRows, allCols)
        if not bFound:
            print("Unable to reduce possible values")
        else:
            print("Reduced Possible Values")

    if haveGoal and not bFound:
        print("HIDDEN PAIR")
        print("===========")
        allRows, allCols, allBlocks, bFound = hiddenPair(
            allRows, allCols, allBlocks)
        if not bFound:
            print("Unable to reduce possible values")
        else:
            print("Reduced Possible Values")

    if count > 10:
        haveGoal = 0

# Puzzle complete - Print Results.
print("ENDING BOARD")
print("============")
printCells(allRows)
