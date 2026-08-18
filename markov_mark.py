import bisect
import math
import ast
from main_matrix import DATA

from syllabreak import Syllabreak
s_var = Syllabreak("-")

alphabet = "abcdefghijklmnopqrstuvwxyz,. "
vowels = "aeiouy"
consumns = "bcdfghjklmnpqrstvwxz"

####################################################################################
#D'abord, lisons ce texte, il s'appellera constamment le cicero.txt
""" with open("cicero.txt","r") as file:
    content = file.read() """
    # print(content[0:400])

unwanted = set("[]0123456789")

def rm_numbers(text):
    filtered_text = []
    for i in text:
        if i not in unwanted:
            filtered_text.append(i)
    #mots = "".join(filtered_text)
    return ("".join(filtered_text)).lower()

# text_filtered = rm_numbers(content)
####################################################################################

# with open("filtered.txt","w") as file:
#     file.write(text_filtered)

#!!Non utilisé
def proba_count(text):
    matrix = {char_0: {char_1: 0 for char_1 in alphabet} for char_0 in alphabet}
    total_caracs = 0
    #On va lire chaque char du text_filtered, pour chacun on regarde quelle lettre on a maintenant et quelle lettre suit. En fonction, on ajoute un +1 au compteur de la suite de lettre dans le dictionnaire
    for i in range(len(text) - 1):
        if text[i] in alphabet and text[i+1] in alphabet:
            total_caracs += 1
            matrix[text[i]][text[i+1]] += 1
    return matrix

# matrix = proba_count(text_filtered)
   

def proba_of_suite(matrix, suite): #suite of two caracters that are in alphabet
    if len(suite) == 2 and suite[0] in alphabet and suite[1] in alphabet:
        proba = matrix[suite[0]][suite[1]]*100/sum(matrix[suite[0]].values())
        print("The probability of", suite[1],"is :", proba, "% if it starts with", suite[0])
    else:
        print("Not a valid suite")
    return 0

#On va quand même implémenter cette histoire de syllabes, car bosser avec des paquets de 2 lettres, ça peut donner des trucs pas ouf
#!!

####################################################################################

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

def syllabic_count_NDORDER(text):
    """Fonction utilisée pour compter les occurences dans l'ordre des syllabes du texte fourni"""
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

def build_syllabic_markov(syllables_cut_text):
    """Fonction qui construit les probabilités de Markov"""
    matrix = {}
    for i in range(len(syllables_cut_text)-1):
        if syllables_cut_text[i] not in matrix:
            matrix[syllables_cut_text[i]] = {}
        if syllables_cut_text[i+1] not in matrix[syllables_cut_text[i]]:
            matrix[syllables_cut_text[i]][syllables_cut_text[i+1]] =0
        
        matrix[syllables_cut_text[i]][syllables_cut_text[i+1]] += 1
    return matrix
  
def sorting_dict(dic):
    return dict(sorted(dic.items()))

def first_syllabs_isolator(matrix):
    """Cette fonction renvoie la matrice de first syllabes ainsi que le nombre total d'occurences dans cette clé"""
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
    """Cette fonction utilise la chaine de Markov fournie pour calculer un espace d'intervalles où vivent les probabilités des syllabes"""
    lowlim = 0
    work_matrix = sorting_dict(matrix) #d'abord on trie le dictionnaire interne
    array_tuple = []
    for syllab in work_matrix:
        array_tuple.append((syllab, lowlim, work_matrix[syllab]+lowlim))
        lowlim = work_matrix[syllab] + lowlim
    return array_tuple

#Maintenant, on a la possibilité de générer des mots en latin qui ne sont pas stupides.


def recherche_syll(array_tuple, in_interval):
    #On effectue une recherche par dichotomie parce que je veux une complexité vraiment cool (en log(N))
    index = 0
    upper_interval = [tup[2] for tup in array_tuple]
    index = bisect.bisect_right(upper_interval, in_interval)
    return array_tuple[index] #Après la recherche, on trouve notre syllabe et les bornes qui l'entourent


# cut_syllabs = syllabic_count_NDORDER(text_filtered)
# matrix_syllabs = build_syllabic_markov(cut_syllabs)

#######################################################################
# On lit juste le contenu de matrix_main sans reconstruire toute la matrice à la main. (on peut le faire si besoin mais c'est un processus un peu lent)
#######################################################################

""" with open("matrix_main.txt", "r") as file:
    matrix_syllabs = file.read() """
matrix_syllabs = ast.literal_eval(DATA)

first_syllabs_dic = first_syllabs_isolator(matrix_syllabs)

""" with open("matrix_main.txt", "w") as file:
    file.write(str(matrix_syllabs))  """  