from markov_mark import * 


####################################################################################
# PARTIE ENCODER DECODER
####################################################################################
 
def equitore(bits):
    #This just turns the bits into an int
    # print(int(bits,2))
    return int(bits,2)

def guard_bit(sequence, state):
    if state == "in":
        return "".join([sequence[0:2], "1", sequence[2:]])
    elif state == "out":
        return "".join([sequence[0:2], sequence[3:]])
    else:
        print("Non existing STATE, choose between 'in' and 'out'")
        return "blank"

def encoder(bits,verbose): 
    """Fonction permettant d'encoder une suite de bits en pseudo-latin markovien"""
    gbits = guard_bit(bits, "in")
    V = equitore(gbits)
    nbits = len(gbits[2:])
    low, high = 0, 2 ** nbits
    full_word = ""
    current_syll = ""
    if verbose: print("Your number is:", V)
    
    first_word = True
    while high - low > 1:
        if verbose : print("low =", low,"| high =", high)
        if first_word:
            work_matrix = syllabs_intervals(first_syllabs_dic)
            first_word =not(first_word)
        else:
            work_matrix = syllabs_intervals(matrix_syllabs[current_syll])
        MAX_MATRIX = work_matrix[-1][-1]
        if verbose : print("max of chosen matrix =",MAX_MATRIX)
        
        span = high - low
        vamped_V = ((V - low) * work_matrix[-1][2])//(high-low)
        if vamped_V >= MAX_MATRIX:
            vamped_V = MAX_MATRIX - 1
        
        if verbose: print("vamped_V =",vamped_V)
        current_result = recherche_syll(work_matrix, vamped_V)
        current_syll = current_result[0]
        high = low + (span * current_result[2]) // MAX_MATRIX
        low = low + (span * current_result[1]) // MAX_MATRIX
        if verbose: print(current_result)
        full_word += "".join(current_syll)
        if verbose: print("---------------------")
    
    return full_word, nbits
    
def syllab_recognizer(input):
    """Fonction permettant de détecter les syllabes dans le texte en suivant les syllabes de markov déjà extraites"""
    length_input = len(input)
    syllab_decomposer = []
    progressive_length = 0
    work_matrix = first_syllabs_dic
    while progressive_length < length_input:
        # temp_syllabs = []
        temp_syllab = ""
        chosen_syllab = ""
        if len(syllab_decomposer) > 0: work_matrix = matrix_syllabs[syllab_decomposer[-1]]
        for syllab in work_matrix:
            if syllab == input[progressive_length: progressive_length + len(syllab)]:
                temp_syllab = syllab
                if len(temp_syllab) > len(chosen_syllab): chosen_syllab = temp_syllab
        progressive_length += len(chosen_syllab)
        syllab_decomposer.append(chosen_syllab)
        
        if not(chosen_syllab):
            print("Pas de syllabe trouvée, c'est inquiétant")
    # print(syllab_decomposer)
    return syllab_decomposer

def decoder(input, nbits, verbose):
    """Fonction permettant de décoder le pseudo-latin markovien"""
    #Bon, on doit retrouver V en partant de l'input et sachant qu'on doit récuperer nbits.
    syllabs = syllab_recognizer(input)
    low, high = 0, 2 ** nbits
    work_matrix_inter = syllabs_intervals(first_syllabs_dic)
    # print(enumerate(syllabs))
    for i, syll in enumerate(syllabs):
        if i > 0: work_matrix_inter = syllabs_intervals(matrix_syllabs[syllabs[i-1]])
        MAX_MATRIX = work_matrix_inter[-1][-1]
        span = high - low
        
        low_i, high_i = 0, 0
        for it_syll, it_low, it_high in work_matrix_inter:
            if it_syll == syll:
                low_i, high_i = it_low, it_high
        if verbose: print(syll,"|", low_i,"|", high_i)
        
        high = low + (span * high_i) // MAX_MATRIX
        low = low + (span * low_i) // MAX_MATRIX
        
    V = high
    
    if verbose: print(guard_bit(bin(V), "out"))
    
    return guard_bit(bin(V), "out") #on remove le guardbit après avoir trouvé la bonne séquence

def text2bin(text):
    """Texte ASCII/UTF-8 to binary"""
    binary_output = "0b"
    binary_output += ''.join(f'{ord(char):08b}' for char in text)
    return binary_output

def bin2text(bin):
    """Binary to ASCII/UTF-8 text"""
    text = bin[2:] 
    bytes_list = [text[i:i+8] for i in range(0,len(text),8)]
    char_list = [int(i,2) for i in bytes_list]
    
    return "".join(chr(nchar) for nchar in char_list)

def type_sorter(string):
    """Fonction permettant la détection automatique de la nature du texte à encoder"""
    for i in string:
        if i != "0" and i != "1":
            return "TEXT"
        else: 
            return "RAW"    

print(type_sorter("110011101"))

####################################################################################
# TESTS DIVERS
####################################################################################
"""
ditch = "putaria"
print("This is the word we're going to encode:", ditch)
# print(text2bin(ditch))

alpha = encoder(text2bin(ditch),False)
print("this is the encoded data before guardedbit:", alpha[0])
ask = print("")
omega = decoder(alpha[0], alpha[1], False)
omega = bin2text(omega)
print("this is the decoded data:", omega)
print(ditch == omega)
"""