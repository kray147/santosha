from markov_mark import * 
import secrets
HEADER_EOF = ","

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

def encoder(bits,verbose = False, initial_syll = ""): 
    """Fonction permettant d'encoder une suite de bits en pseudo-latin markovien"""
    gbits = guard_bit(bits, "in")
    nbits = len(gbits[2:])  
    V = equitore(gbits)
    
    low, high = 0, 2 ** nbits
    full_word = ""
    current_syll = initial_syll
    if verbose: print("Your number is:", V)
    
    first_word = True
    while high - low > 1:
        if verbose : print("low =", low,"| high =", high)
        if first_word and initial_syll == "":
            work_matrix = syllabs_intervals(first_syllabs_dic)
        else:
            work_matrix = syllabs_intervals(matrix_syllabs[current_syll])
        MAX_MATRIX = work_matrix[-1][-1]
        first_word = False

        
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
    
    
    
    return full_word, nbits, current_syll
    
def wrong_syllab_recognizer(input):
    """Décomposition en syllabes avec backtracking complet (pile d'alternatives)."""
    length_input = len(input)
    stack = []  # chaque frame : {'syllab': choisie, 'candidates': alternatives restantes, 'start': position avant}
    progressive_length = 0

    while progressive_length < length_input:
        work_matrix = matrix_syllabs[stack[-1]['syllab']] if stack else first_syllabs_dic

        candidates = sorted(
            (s for s in work_matrix
             if input[progressive_length:progressive_length + len(s)] == s),
            key=len, reverse=True
        )

        if candidates:
            chosen = candidates[0]
            stack.append({
                'syllab': chosen,
                'candidates': candidates[1:],  # alternatives gardées pour un futur backtrack
                'start': progressive_length
            })
            progressive_length += len(chosen)
            continue

        # Aucun candidat : backtracker, potentiellement sur plusieurs niveaux
        backtracked = False
        while stack:
            frame = stack.pop()
            progressive_length = frame['start']
            if frame['candidates']:
                chosen = frame['candidates'][0]
                stack.append({
                    'syllab': chosen,
                    'candidates': frame['candidates'][1:],
                    'start': progressive_length
                })
                progressive_length += len(chosen)
                backtracked = True
                break
            # sinon : ce niveau n'a plus d'alternative, on continue à remonter

        if not backtracked:
            raise ValueError("Aucune décomposition syllabique possible pour cette entrée.")

    return [frame['syllab'] for frame in stack]
    
def syllab_recognizer(input, header = False):
    """Fonction permettant de détecter les syllabes dans le texte en suivant les syllabes de markov déjà extraites"""
    length_input = len(input)
    syllab_decomposer = []
    progressive_length = 0
    work_matrix = first_syllabs_dic
    temp_syllabs = []
    while progressive_length < length_input:
        # breakpoint()
        anciens_candidats = temp_syllabs
        temp_syllabs = []
        chosen_syllab = ""
        # print("to treat:", input[progressive_length: length_input])
        if len(syllab_decomposer) > 0:
            work_matrix = matrix_syllabs[syllab_decomposer[-1]]
        for syllab in work_matrix:
            if syllab == input[progressive_length : progressive_length + len(syllab)]:
                temp_syllabs.append(syllab)
        # print(temp_syllabs, chosen_syllab)

        # print("THIS IS TEMP_SYLLABS:", temp_syllabs)
        if temp_syllabs:
            chosen_syllab = max(temp_syllabs, key=len)

        if chosen_syllab:
            progressive_length += len(chosen_syllab)
            syllab_decomposer.append(chosen_syllab)

        if not (chosen_syllab):
            mauvaise_syllab = syllab_decomposer.pop()
            progressive_length -= len(mauvaise_syllab)

            anciens_candidats.remove(mauvaise_syllab)
            nouvelle_syllab = max(anciens_candidats, key=len)

            syllab_decomposer.append(nouvelle_syllab)
            progressive_length += len(nouvelle_syllab)
            temp_syllabs = [nouvelle_syllab]
        # print("progressive syllabs:", syllab_decomposer)
    return syllab_decomposer

def veryold_syllab_recognizer(input):
    """Fonction permettant de détecter les syllabes dans le texte en suivant les syllabes de markov déjà extraites"""
    length_input = len(input)
    syllab_decomposer = []
    progressive_length = 0
    work_matrix = first_syllabs_dic
    while progressive_length < length_input:
        print(syllab_decomposer)
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

def decoder(input, nbits, verbose = False, header = False):
    """Fonction permettant de décoder le pseudo-latin markovien"""
    input = input.lower()
    #Bon, on doit retrouver V en partant de l'input et sachant qu'on doit récuperer nbits.
    syllabs = syllab_recognizer(input, header)
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
        
        if high - low <= 1:
            break
        
    V = high
    
    if verbose: print(guard_bit(bin(V), "out"))
    
    return guard_bit(bin(V), "out") #on remove le guardbit après avoir trouvé la bonne séquence

def encode_chain(input, verbose = False):
    word, nbits, _ = encoder(input, False)
    header = encoder("0b" + f"{nbits:015b}", False)
    full_word = header[0] + HEADER_EOF + word
    chars = list(full_word)
    chars[0] = chars[0].upper() 
    for i in range(len(chars)):
        if chars[i-2] in ["."] and i >= 2:
            chars[i] = chars[i].upper()
    full_word = "".join(chars)
    return full_word

def decoder_header(input):
    # pos_chariot = input.find(HEADER_EOF)
    pos_chariot = 0
    for c in range(len(input)):
        # print("prog input:",input[c:c+1])
        if input[c] == HEADER_EOF and input[c+1] != " ":
            pos_chariot = c
            break
        
    
    # print("This is input in decoder_header:", input)
    # print("THIS IS THE FUCKASS DECODER_HEADER:", input[:pos_chariot])
    # print(input[pos_chariot+1:])
    aaaaah = decoder(input[:pos_chariot], 16, False, True)
    # print(int(aaaaah,2))
    return aaaaah, pos_chariot

def decode_chain(input, c):
    pos_chariot = c
    return input[pos_chariot + 1:]

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

def no1char(user_input):
    if not(user_input):
        print("Has to be a non NULL string")
        return "  "
    elif len(user_input):
        return user_input + " "
    else:
        return user_input

# print(type_sorter("110011101"))

####################################################################################
# TESTS DIVERS
####################################################################################

""" # ditch = "C'est la vie qui m'entraine mais j'la vois en grise"
ditch = no1char(input("Give an input:\n"))
print("This is the word we're going to encode:", ditch)
# print(text2bin(ditch))
beta = encode_chain(text2bin(ditch),False)
# ceta = encode_chain_continuous(text2bin(ditch),False)
print("This is the encoded continuous chain:", beta)
print("")
# print("decoder_header: ", decoder_header(beta),"which means:", int(decoder_header(beta),2))
omega = decoder(decode_chain(beta), int(decoder_header(beta),2), False)
omega = bin2text(omega)
with open("encoded.txt", "w") as file:
    file.write(beta) """
    
# print("this is the decoded data:", omega) 

def benchmark_encoding(binary_str, latin_text):
    """Calcule la capacité d'information par syllabe."""
    # Nettoyage
    bits_only = (
        binary_str[2:] if binary_str.startswith("0b") else binary_str
    )
    nbits = len(bits_only)

    # Découpage du texte généré en syllabes
    syllables = syllab_recognizer(latin_text)
    nsyllabs = len(syllables)

    bits_per_syllable = nbits / nsyllabs

    print(f"--- RÉSULTATS DU BENCHMARK ---")
    print(f"Bits totaux cachés   : {nbits} bits")
    print(f"Syllabes générées   : {nsyllabs} syllabes")
    print(f"Densité d'encodage  : {bits_per_syllable:.3f} bits / syllabe")
    print(f"Rendement approximif : {bits_per_syllable / 8:.2f} octets / syllabe")


""" # --- TEST 1 : Aléatoire pur (2048 bits = 256 octets) ---
raw_bytes = secrets.token_bytes(256)
bits_test = "0b" + "".join(f"{b:08b}" for b in raw_bytes)

latin_out = encoder(bits_test,False)
print(latin_out[0])
benchmark_encoding(bits_test, latin_out[0]) """

# print(syllab_recognizer("Monis, que ,flammaximam misque sunt omni minem conferre. Catur, quem agros ferta obscemus, concidunt amissi id esset, gravideconiugi, in eiusmodi possit, ut id sophorum veniat et fortis intellerit, ut et mutanta tecum habere persobrinobitranquilliqui losocietate ferri si nos studiosum sit silio cernatu propoteneque eoque et ".lower()))