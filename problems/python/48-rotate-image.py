def ninety_degrees(mat):
  for row in range(len(mat)):
     for col in range(row + 1, len(mat)):
      mat[row][col], mat[col][row] = mat[col][row], mat[row][col]
  for row in mat:
    row[:] = row[::-1]
  return mat

mat = [[1, 2, 3],
       [4, 5, 6],
       [7, 8, 9]]
print(ninety_degrees(mat))