# Sudoku solver/analyzer
# Backtracking iterative approach

start_board = [
			[ 5, 3, 0, 0, 7, 0, 0, 0, 0],
			[ 6, 0, 0, 1, 9, 5, 0, 0, 0],
			[ 0, 9, 8, 0, 0, 0, 0, 6, 0],
			[ 8, 0, 0, 0, 6, 0, 0, 0, 3],
			[ 4, 0, 0, 8, 0, 3, 0, 0, 1],
			[ 7, 0, 0, 0, 2, 0, 0, 0, 6],
			[ 0, 6, 0, 0, 0, 0, 2, 8, 0],
			[ 0, 0, 0, 4, 1, 9, 0, 0, 5],
			[ 0, 0, 0, 0, 8, 0, 0, 7, 9],
		]

class MV:
	FORWARD = 1													# when the solver is moving forward
	BACKWARD = -1												# when the solver is backtracking

class Sudoku:
	def __init__(self, initial_state):
		self.board = initial_state
		self.solution_list = {}									# keep track of previous solution for backtracking
		self.move_direction = MV.FORWARD 						

	def possible_solutions (self, row, col):
		solution_set = set(list(range(1,10)))												

																# start with all solutions, then remove the invalid ones

		remove_solution = lambda i : solution_set.remove(i) if i in solution_set else None

		[remove_solution(num) for num in self.board[row]]		# remove numbers that already exist in the row
		[remove_solution(each_row[col]) for each_row in self.board]
																# remove numbers that already exist in the col

		quanta = lambda i : i // 3 * 3
		qrow   = quanta(row)
		qcol   = quanta(col)
		
		for sub_row in self.board[qrow : qrow + 3]:				# find the numbers that exist in the 3 x 3 sub-block
			for subblock in sub_row[qcol : qcol + 3]:
				remove_solution(subblock)
			
		return solution_set	

	def move(self, row, col):			
		if self.move_direction == MV.FORWARD:
			col += 1
			if col == 9: col = 0; row += 1			
		else:													# MV.BACKWARD
			col -= 1
			if col == -1: col = 8; row -= 1
		return row, col

	def solve(self):
		row = col = 0

		while row < 9:											# depends on the move method

			if self.board[row][col] != 0 and (row, col) not in self.solution_list:	
																# not in self.solution_list to exclude the original population of numbers
				row, col = self.move(row, col)
			else:
				if self.move_direction == MV.BACKWARD:			# moving backwards always lookup solutions, if there are any, else keep moving backwards
					solns = self.solution_list[(row, col)]		# pick another possible solution

					if len(solns) == 0:							# all solutions tested
						self.board[row][col] = 0				# set this to 0 for correct possible solution calculation when traveling forward
																 
						row, col = self.move (row, col)			# move, direction is set to backwards
					else:	
						self.board[row][col] = solns.pop()		# else try another solution
						self.move_direction = MV.FORWARD		# move forward
						row, col = self.move(row, col)
				else:
					solns = self.possible_solutions(row, col)	# always generate solutions when moving forward to replace the stale solutions
					self.solution_list[(row,col)] = solns		# keep this to try unused solutions when backtracking	

					if solns:
						self.board[row][col] = solns.pop()		# pick up a solution and move forward
						row, col = self.move(row, col)
					else:
						self.board[row][col] = 0				# set this to 0 for correct possible solution calculation when traveling forward
						self.move_direction = MV.BACKWARD		# change direction for backtracking
						row, col = self.move(row, col)			# move, direction is set to backwards

		for row in self.board:									
			if 0 in row: raise ValueError("No solution found!")	# any zeros would indicate that the sudoku board was not solved

	def __repr__ (self):
		l = ["  " + "-"*35]
		for r in self.board:
			rs = " | " + " | ".join([ str(num) if num else " " for num in r]) + " | "
			l += [rs]
			l += ["  " + "-"*35]
		return "\n".join(l)

if __name__ == "__main__":
	s = Sudoku(start_board)	
	s.solve()
	print(s)
