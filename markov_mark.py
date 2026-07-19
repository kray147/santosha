import bisect

from syllabreak import Syllabreak
s_var = Syllabreak("-")

alphabet = "abcdefghijklmnopqrstuvwxyz,. "
vowels = "aeiouy"
consumns = "bcdfghjklmnpqrstvwxz"


#D'abord, lisons ce texte, il s'appelera constamment le cicero.txt
with open("cicero.txt","r") as file:
    content = file.read()
    # print(content[0:400])

unwanted = set("[]0123456789")

def rm_numbers(text):
    filtered_text = []
    for i in text:
        if i not in unwanted:
            filtered_text.append(i)
    #mots = "".join(filtered_text)
    return ("".join(filtered_text)).lower()


text_filtered = rm_numbers(content)
with open("filtered.txt","w") as file:
    file.write(text_filtered)


def proba_count(text):
    matrix = {char_0: {char_1: 0 for char_1 in alphabet} for char_0 in alphabet}
    total_caracs = 0
    #On va lire chaque char du text_filtered, pour chacun on regarde quelle lettre on a maintenant et quelle lettre suit. En fonction, on ajoute un +1 au compteur de la suite de lettre dans le dictionnaire
    for i in range(len(text) - 1):
        if text[i] in alphabet and text[i+1] in alphabet:
            total_caracs += 1
            matrix[text[i]][text[i+1]] += 1
    return matrix

matrix = proba_count(text_filtered)        
# print("il y a un pourcentage de ab de ",matrix['a']['b']*100/total,"%")

def proba_of_suite(matrix, suite): #suite of two caracters that are in alphabet
    if len(suite) == 2 and suite[0] in alphabet and suite[1] in alphabet:
        proba = matrix[suite[0]][suite[1]]*100/sum(matrix[suite[0]].values())
        print("The probability of", suite[1],"is :", proba, "% if it starts with", suite[0])
    else:
        print("Not a valid suite")
    return 0

""" proba_of_suite(matrix,"qu")
print(matrix['q']) """

#On va quand même implémenter cette histoire de syllabes, car bosser avec des paquets de 2 lettres, ça peut donner des trucs pas ouf


def syllabic_count(text):
    all_syllabs = []
    words_array = text.split()
    words_array = [mot + " " for mot in words_array]
    words_array = words_array[7:len(words_array) - 15] # On enlève le tout début et la toute fin du texte car c'est de l'anglais ou du latin pourri (genre avec les v à la place des u)
    for i in range(len(words_array)):
        temp_s = (s_var.syllabify(words_array[i].replace(" ","!"))).split("-")
        for syllab in temp_s:
            syllab = syllab.replace("!"," ")
            if syllab not in all_syllabs:
                all_syllabs.append(syllab)
    return all_syllabs



def finisher_syllabs(array_s):
    count = 0
    for syllab in array_s:
        if syllab[-1] == " ":
            count += 1
    return count




""" # cut_syllabs = syllabic_count(text_filtered)  
print("On a en tout",len(cut_syllabs),"syllabes")
print("Parmi ces syllabes, on a",finisher_syllabs(cut_syllabs),"de fin de mots")
print("Donc on a", len(cut_syllabs)-finisher_syllabs(cut_syllabs),"de syllabes début ou milieu de mots") """


def syllabic_count_NDORDER(text):
    all_syllabs = []
    words_array = text.split()
    words_array = [mot + " " for mot in words_array]
    words_array = words_array[7:len(words_array) - 15] # On enlève le tout début et la toute fin du texte car c'est de l'anglais ou du latin pourri (genre avec les v à la place des u)
    for i in range(len(words_array)):
        temp_s = (s_var.syllabify(words_array[i].replace(" ","!"))).split("-")
        for syllab in temp_s:
            syllab = syllab.replace("!"," ")
            all_syllabs.append(syllab)
    return all_syllabs


cut_syllabs = syllabic_count_NDORDER(text_filtered)
# print(cut_syllabs[0:100])


def build_syllabic_markov(syllables_cut_text):
    matrix = {}
    for i in range(len(syllables_cut_text)-1):
        if syllables_cut_text[i] not in matrix:
            matrix[syllables_cut_text[i]] = {}
        if syllables_cut_text[i+1] not in matrix[syllables_cut_text[i]]:
            matrix[syllables_cut_text[i]][syllables_cut_text[i+1]] =0
        
        matrix[syllables_cut_text[i]][syllables_cut_text[i+1]] += 1
    return matrix

matrix_syllabs = build_syllabic_markov(cut_syllabs)
# print(matrix_syllabs)


def sorting_dict(dic):
    return dict(sorted(dic.items()))

"""Cette fonction renvoie la matrice de first syllabes ainsi que le nombre total d'occurences dans cette clé"""
def first_syllabs_isolator(matrix):
    buffer_matrix = {}
    total_count = 0
    for syllab in matrix:
        if syllab[-1] != " ":
            count = 0
            # buffer_matrix[syllab] = matrix[syllab]
            for subsyllab in matrix[syllab]:
                count += matrix[syllab][subsyllab]
                total_count += total_count
            buffer_matrix[syllab] = count
    return buffer_matrix
            


def syllabs_intervals(matrix):
    lowlim = 0
    work_matrix = sorting_dict(matrix) #d'abord on trie le dictionnaire interne
    array_tuple = []
    for syllab in work_matrix:
        array_tuple.append((syllab, lowlim, work_matrix[syllab]+lowlim))
        lowlim = work_matrix[syllab] + lowlim
    return array_tuple


""" with open("syllabcount.txt","w") as file:
    file.write(str(matrix_syllabs)) """


first_syllabs_dic = first_syllabs_isolator(matrix_syllabs)
# print(syllabs_intervals(first_syllabs_dic))

with open("first_to_eat.txt", "w") as file:
    file.write(str(syllabs_intervals(first_syllabs_dic)))

def recherche_syll(array_tuple, in_interval):
    #On effectue une recherche par dichotomie parce que je veux une complexité vraiment cool (en log(N))
    index = 0
    upper_interval = [tup[2] for tup in array_tuple]
    index = bisect.bisect_right(upper_interval, in_interval)
    return array_tuple[index] #Après la recherche, on trouve notre syllabe et les bornes qui l'entourent


def encoder(bits): #Les bits sont traités ici comme un string
    V = int(bits, 2) #On transforme ces bits en un seul grand nombre avec lequel on va travailler
    first_turn = True
    MODULATOR = 0
    choice_index = 0
    current_syllab = ""
    full_word = ""
    print("Les bits encodés sont:", bits)
    while V != 0:
        
        print("V est actuellement:", V)
        if first_turn:
            MODULATOR = syllabs_intervals(first_syllabs_dic)
            MODULATOR_MAX = MODULATOR[-1][2]
            choice_index = V % MODULATOR_MAX
            print(MODULATOR)
            # print("Choice index est ",choice_index,"pour la first syllab")
            
            current_syllab = recherche_syll(MODULATOR, choice_index)[0]
            # current_syllab = current_syllab[0].upper()+"".join(current_syllab[1:])
            # print(current_syllab)
            # print("MODULATOR_MAX vaut ici dans ce tour :",MODULATOR_MAX)
            V = V // MODULATOR_MAX
            full_word = full_word + "".join(current_syllab)
            first_turn = False
        
        else:
            MODULATOR = syllabs_intervals(matrix_syllabs[current_syllab])
            MODULATOR_MAX = MODULATOR[-1][2]
            # print("MODULATOR_MAX vaut ici dans ce tour :",MODULATOR_MAX)
            choice_index = V % MODULATOR_MAX
            print(MODULATOR)
            current_syllab = recherche_syll(MODULATOR, choice_index)[0]

            V = V // MODULATOR_MAX
            full_word = full_word + "".join(current_syllab)
    print(full_word)
    return 0
             
encoder("0b111111111111110")
encoder("0b111111111111111")
    

#Maintenant, on a la possibilité de générer des mots en latin qui ne sont pas stupides.