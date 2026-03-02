def delete_minimum_elements(hunny_jar_sizes):
	res = []
	while len(hunny_jar_sizes) > 0:
		least = min(hunny_jar_sizes)
		hunny_jar_sizes.remove(least)
		res.append(least)
	return print(res)

hunny_jar_sizes = [5, 3, 2, 4, 1]
delete_minimum_elements(hunny_jar_sizes)

hunny_jar_sizes = [5, 2, 1, 8, 2]
delete_minimum_elements(hunny_jar_sizes)