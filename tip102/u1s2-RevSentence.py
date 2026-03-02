''''
Understand: 
	Takes an x amount of words in a string an reverse
	In python, string are immutable, so we'll need convert them into a mutable type, aka a list
	.split() to that

    Input: Is a string
    Output: Returns a string
    Constraints: Only contains alphabetical chars and spaces
    Edge Cases: If it is only one word, return original string
    	If there is an empty string, return "" or print "no string to reverse"
Plan:
	If not sentence, return "" or print statment
    Convert sentence into list to figure out many words are in the string
    If just one word, return original string
    while left < right:
		swap left value and right value
        increment left
        decrement right
    print(result)
'''

def reverse_sentence(sentence):
    if not sentence:
        print("No string")
        return

    words = sentence.split()

    if len(words) == 1:
        print(sentence)
        return

    # Reverse using slicing instead of manual swap
    reversed_words = words[::-1]
    res = ' '.join(reversed_words)
    print(res)


sentence = "Hi my name is Chris"
reverse_sentence(sentence)
