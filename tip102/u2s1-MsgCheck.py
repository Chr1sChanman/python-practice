'''
Understand:
    I: string only lower and whitespace
    O: boolean
    C: N/A
    E: Empty string
Plan: 
    Create a template set set('a...z')
    Create set 2
    iterate through the string and exclude spaces:
        Add i to set 2
    if template == set2
        return True
    return False
Implement:
'''

def can_trust_message(message):
    set2 = set(message)
    if " " in set2:
        set2.remove(" ")
    
    if len(set2) == 26:
        return True
    else:
        return False


message1 = "sphinx of black quartz judge my vow"
message2 = "trust me"

print(can_trust_message(message1))
print(can_trust_message(message2))

True
False