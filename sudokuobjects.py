class Cell:
    def __init__(self, id):
        self.__possible = set(range(1, 10))  # Unique Set
        self.__number = 0
        self.__locked = False
        self.__row = 0
        self.__column = 0
        self.__block = 0
        self.id = id

    def __setnum(self, num):
        if not self.__locked:
            rowPossible = self.row.possible
            colPossible = self.column.possible
            blockPossible = self.block.possible
            allPossible = rowPossible.intersection(
                colPossible.intersection(blockPossible))
            if num in allPossible:
                self.__number = num
                self.row.isNot(num)
                self.column.isNot(num)
                self.block.isNot(num)
                # self.__possible.discard(num)
                self.__possible.clear()
                self.__number = num
                return True
            else:
                return False

    def __clearnum(self):
        if not self.__locked:
            if self.__number:
                self.row.mayBe(self.__number)
                self.column.mayBe(self.__number)
                self.block.mayBe(self.__number)
                self.__number = 0
            else:
                self.__number = 0

    def isNot(self, num):
        # Remove a value from possible values
        self.__possible.discard(num)

    def mayBe(self, num):
        # Add a value to possible values
        self.__possible.add(num)

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, num):
        if num:
            self.__setnum(num)
        else:
            self.__clearnum()

    @property
    def row(self):
        return self.__row

    @row.setter
    def row(self, row):
        self.__row = row

    @property
    def column(self):
        return self.__column

    @column.setter
    def column(self, column):
        self.__column = column

    @property
    def block(self):
        return self.__block

    @block.setter
    def block(self, block):
        self.__block = block

    @property
    def possible(self):
        return self.__possible

    @property
    def locked(self):
        return self.__locked

    @locked.setter
    def locked(self, state=False):
        if self.__number:
            self.__possible.clear()
            # self.__possible.add(self.__number)
            self.__locked = state


class Row:
    def __init__(self, id: int, cellList: list):
        self.id = id
        self.__possible = set(range(1, 10))
        self.__cells = cellList
        for cell in self.__cells:
            cell.row = self

    def isNot(self, num):
        # Remove a value from possible values
        self.__possible.discard(num)
        for cell in self.__cells:
            cell.isNot(num)

    def mayBe(self, num):
        # Add a value to possible values
        self.__possible.add(num)
        for cell in self.__cells:
            cell.mayBe(num)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def possible(self):
        return self.__possible

    @property
    def cells(self):
        return self.__cells


class Column:
    def __init__(self, id: int, cellList: list):
        self.id = id
        self.__possible = set(range(1, 10))
        self.__cells = cellList
        for cell in self.__cells:
            cell.column = self

    def isNot(self, num):
        # Remove a value from possible values
        self.__possible.discard(num)
        for cell in self.__cells:
            cell.isNot(num)

    def mayBe(self, num):
        # Add a value to possible values
        self.__possible.add(num)
        for cell in self.__cells:
            cell.mayBe(num)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def possible(self):
        return self.__possible

    @property
    def cells(self):
        return self.__cells


class Block:
    def __init__(self, id: int, cellList: list):
        self.id = id
        self.__possible = set(range(1, 10))
        self.__cells = cellList
        for cell in self.__cells:
            cell.block = self

    def isNot(self, num):
        # Remove a value from possible values
        self.__possible.discard(num)
        for cell in self.__cells:
            cell.isNot(num)

    def mayBe(self, num):
        # Add a value to possible values
        self.__possible.add(num)
        for cell in self.__cells:
            cell.mayBe(num)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def possible(self):
        return self.__possible

    @property
    def cells(self):
        return self.__cells


class Board:
    '''
    Builds an empty board
    Returns list of objects to program
    '''

    def __init__(self):
        pass

    def buildBoard(self):
        # Create 81 Cell objects
        cells = []
        for cellId in range(1, 82):
            cells.append(Cell(cellId))

        # create 9 Row objects
        # populate with appropriate cells
        rows = []
        for rowIndex in range(9):
            rowOfCells = []
            for colIndex in range(9):
                cellIndex = (9*rowIndex) + colIndex
                rowOfCells.append(cells[cellIndex])
            rows.append(Row(rowIndex+1, rowOfCells))

        # Create 9 Column objects
        # populate with appropriate cells
        cols = []
        for colIndex in range(9):
            colOfCells = []
            for rowIndex in range(9):
                cellIndex = (9*rowIndex) + colIndex
                colOfCells.append(cells[cellIndex])
            cols.append(Column(colIndex+1, colOfCells))

        # Build 9 cube objects
        # populate with appropriate cells
        blocks = []
        cellBlocks = []
        for eachBlock in range(9):
            thisBlock = []
            cellBlocks.append(thisBlock)

        # Calculate which block each cell belongs to.
        # Add the appropriate cells to the appropriate sub-list.
        for rowIndex in range(9):
            for colIndex in range(9):
                cellIndex = (9*rowIndex) + colIndex
                blockNum = (colIndex+3)//3 + (rowIndex//3)*3
                cellBlocks[blockNum-1].append(cells[cellIndex])

        # Create block objects with appropriate cell lists.
        for blockNum in range(1, 10):
            blocks.append(Block(blockNum, cellBlocks[blockNum-1]))

        allObjects = [cells, rows, cols, blocks]
        return allObjects
