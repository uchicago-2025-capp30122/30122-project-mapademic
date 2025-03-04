import re
INDEX_IGNORE = set(
    [
        # conj
        "a", "an", "the",

        # pronouns
        "i", "you", "he", "she", "it", "we", "they",
        "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their",
        "mine", "yours", "hers", "ours", "theirs",
        "who", "whom", "whose", "which", "that", 
        "what", "where", "when", "why", "how",
        "can", "could", "may", "might", "shall", "should", "will", "would",
        "do", "does", "did", "done",

        # Conjections
        "and", "or", "but", "if", "because", "since", "although", "though",
        "while", "whereas", "unless", "however", "moreover", "furthermore",
        "therefore", "thus", "such", "for", "also", "from"

        # Preposition
        "in", "on", "at", "by", "with", "without", "over", "under", "between", 
        "among", "through", "before", "after", "about", "above", "below", "from",

        # Adverbs
        "very", "too", "quite", "rather", "almost", "always", "never", "sometimes",
        "often", "rarely", "seldom",
        
        # Normal verbs
        "be", "am", "is", "are", "was", "were", "been", "being",
        "get", "gets", "got", "getting",
        "give", "gives", "gave", "given", "giving",
        "use", "uses", "used", "using",
        "put", "puts", "putting",
        "set", "sets", "setting",
        "make", "makes", "made", "making",
        "do", "does", "doing", "done",
        "take", "takes", "took", "taken", "taking",
        "have", "has", "had", "having",

        # Meaningless words in paper abstract
        "research", "study", "paper", "article", "findings", "results", "conclusion",
        "approach", "method", "methods", "analysis", "data", "dataset", "datasets",
        "experiment", "experiments", "observations", "observation",
        "propose", "proposed", "evaluate", "evaluated",
        "including", "based", "using", "applied", "application",
        "system", "systems", "frameworks", "approach", "approaches",
        "science", "scientific", "technology", "technologies", "engineering",
        "field", "fields", "process", "processes",
        "used", "utilized", "utilize", "develop", "developed", "development", "into",
        "one", "two", "three", "four", "five", "six", "seven","eight",

        # Normal conjections and no-meaning words
        "like", "such", "many", "much", "more", "most", "less", "least",
        "some", "any", "none", "all", "both", "each", "every", "either", "neither",
        "other", "another", "same", "different",
        "this", "these", "those", "their", "they", "them",

        # Other Strange characters
        "om", "log"
    ]
)

def remove(word_lst):
    remove_char = "(!.,'\"?:-/%ω)`~^$#@′√“‘”"
    for i in range(len(word_lst)):
        word = word_lst[i]
        for char in word:
            if char in remove_char:
                word = word.replace(char, '')
        word_lst[i] = word
    return word_lst

def ignore(word_lst):
    new_words = []
    for word in word_lst:
        if word not in INDEX_IGNORE and not re.fullmatch(r"\d+|[a-zA-Z]{1,2}", word):
            new_words.append(word)
    return new_words

def process_word_list(word_list):
    word_set = set(word_list)
    processed_list = []
    for word in word_list:
        # Process the plural form of the word
        if word.endswith("ss"):
            processed_list.append(word)
        elif word.endswith("ies"):
            # Check if this word is the plural form of a word end with "y"
            singular = word[:-3] + "y"
            if singular in word_set:
                processed_list.append(singular)
            else:
                processed_list.append(word)
        elif word.endswith("es"):
            # Check if this word ends with "e"
            word_without_s = word[:-1]
            word_without_es = word[:-2]
            if word_without_s in word_set:
                processed_list.append(word_without_s)
            elif word_without_es in word_set:
                processed_list.append(word_without_es)
            else:
                processed_list.append(word)
        elif word.endswith("s"):
            word_without_s = word[:-1]
            if word_without_s in word_set:
                processed_list.append(word_without_s)
            else:
                processed_list.append(word)           
        else:
            processed_list.append(word)
    return processed_list