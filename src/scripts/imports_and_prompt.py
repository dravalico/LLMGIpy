from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from word2number import w2n
import re
from scripts.function_util import orderering_preserving_duplicates_elimination


def import_manipulation(imports, available_vars):
    """
    qui semplicemnte metto gli 'as' agli import oppure sostituisco il valore dell'as' con le variabili disponibili
    """
    final = []
    num_imports = len(imports)
    for i, imp in enumerate(imports):
        if imp.find(" as ") == -1:
            final.append(imp + " as " + available_vars[i])
        else:
            imp_splitted = imp.split()
            imp_splitted[-1] = available_vars[i]

            final.append(' '.join(imp_splitted))

    remain_vars = available_vars[num_imports:]
    return final, remain_vars


def real_imports(original_imports, imports_predefined, vars_used_original):
    """
    questa funzione è un po una merda e forse si poteva fare meglio almeno funziona
    1. guardo quali delle variabili predefinite sono utilizzate negli import
    2. elimino dalle variabili disponibili le variabili utilizzate ma che non sono utilizzate negli import
    3. riordino gli import in modo che gli import che avevano già una variabile gli venga riassegnata la variabile che aveano prima (per coerenza con il resto del codice)
    """

    possible_names = ["v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9",
                      "v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19"]
    reorder = []
    vars_used = vars_used_original.copy()
    original_import_reordered = []
    for n, im_pre in enumerate(imports_predefined):
        im_pre = im_pre.split()
        for v in im_pre:
            if v in vars_used:
                reorder.append(n)
                vars_used.remove(v)
    for i in range(len(original_imports)):
        if i not in reorder:
            reorder.append(i)

    for i in range(len(original_imports)):
        original_import_reordered.append(original_imports[reorder[i]])

    #print(f"reord {original_import_reordered}")
    #print(f"ori {original_imports}")
    #print(f"fail {imports_predefined}")
    res = [i for i in possible_names if i not in vars_used]
    imports, free_var = import_manipulation(original_import_reordered, res)
    return imports, [i for i in possible_names if i not in free_var]


def extract_prompt_info(corpus):
    """
    cerco di estrarre info dal prompt con tf-idf non funziona bene
    ATTENZIONE: installare sklearn
    """
    vectorizer = TfidfVectorizer()
    vectorizer.fit_transform(corpus)
    return vectorizer.get_feature_names_out()


def extract_prompt_info_with_keybert(prompt):
    """
    utilizzo keybert per estrarre parole chiave. Inizialmente estrae tutto lower case quindi ho fatto dei maneggi per ricondurmi alla parola originale del prompt.
    cosi possiamo mettere la parola originale tra le stringhe
    """
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(prompt, stop_words="english")
    prompt_list = prompt.split()
    original_key = []

    for i, elem in enumerate(prompt_list):
        for k in keywords:
            if elem.lower() == k[0]:
                original_key.append(elem)
    return orderering_preserving_duplicates_elimination(original_key)


def extract_numbers_from_string(prompt):
    """
    funzione per estrarre i numeri dal prompt, e inseririli nei numeri. Estrare si numeri scritti come digit che numeri scritti come lettere (es. four, five ...)
    """
    words = prompt.split()
    numbers = []
    
    for string in re.findall(r'\d+\.\d+', prompt):
        try:
            _ = float(string.strip().lower())  # Try converting to a float
            numbers.append(string.strip().lower())
        except ValueError:
            pass  # Couldn't convert to either int or float
    
    for string in re.findall(r'-?\d*\.?\d+(?:[eE][-+]?\d+)?', prompt):
        try:
            _ = int(string.strip().lower())
            numbers.append(string.strip().lower())
        except ValueError:
            pass  # Couldn't convert to either int or float

    for word in words:
        try:
            number = w2n.word_to_num(word)
            numbers.append(str(number))
        except ValueError:
            pass  # Ignore words that are not recognized as numbers
    return orderering_preserving_duplicates_elimination(numbers)


if __name__ == "__main__":
    print(extract_prompt_info_with_keybert(
        "Given an integer 1 <= x <= 50,000, return ""Fizz"" if x is divisible by 3, ""Buzz"" if x is divisible by 5, ""FizzBuzz"" if x is divisible by 3 and 5, and x if none of the above hold."))
    print()
    # corpus = [
    #            "Basement;Given a list of integers, what is the position of the first integer such that the sum of all integers from the start to it inclusive is negative?",
    #            "Take a string and convert all of the words to camelCase. Each group of words is delimitered by ""-"", and each group of words is separated by a space",
    #            "Peter has an n sided die and Colin has an m sided die. If they both roll their dice, what is the probabilitiy that Peter rolls strictly higher than Colin",
    #            "Given an integer 1 <= x <= 50,000, return ""Fizz"" if x is divisible by 3, ""Buzz"" if x is divisible by 5, ""FizzBuzz"" if x is divisible by 3 and 5, and x if none of the above hold.",
    #            "Given a string, if it is odd length return the middle character; if it is even length, return the two middle characters.",
    #            "Given 1 int (hours) and 3 floats (current snow, falling snow, percent melting), determine how much snow will be on the ground in the amount of hours given"
    #        ]
    # print(extract_prompt_info(corpus))

    print(extract_numbers_from_string("Given four an integer 1 <= x <= 50,000, 50000 return ""Fizz"" if x is divisible by 3, ""Buzz"" if x is divisible by five 5, ""FizzBuzz"" if x is divisible by 3 and 5, and x if none of the above hold."))
    print(real_imports(["import math", "import re", "from numpy import ciao", "from numpy import ciao as c", "import prova as pr"], [
          "import math", "import v1", "from numpy import ciao", "from numpy import ciao as c", "import prova as v4"],  ["v0", "v1", "v2", "v3", "v4", "v5"]))
