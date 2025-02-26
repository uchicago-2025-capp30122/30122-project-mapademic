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

        # 疑问词
        "what", "where", "when", "why", "how",

        # 助动词
        "can", "could", "may", "might", "shall", "should", "will", "would",
        "do", "does", "did", "done",

        # 关系词和连接词
        "and", "or", "but", "if", "because", "since", "although", "though",
        "while", "whereas", "unless", "however", "moreover", "furthermore",
        "therefore", "thus", "such", "for", "also", "from"

        # 介词
        "in", "on", "at", "by", "with", "without", "over", "under", "between", 
        "among", "through", "before", "after", "about", "above", "below", "from",

        # 频率副词和程度副词
        "very", "too", "quite", "rather", "almost", "always", "never", "sometimes",
        "often", "rarely", "seldom",

        # Be动词及变形
        "be", "am", "is", "are", "was", "were", "been", "being",

        # Have动词及变形
        "have", "has", "had", "having",

        # Make/Do/Take 相关
        "make", "makes", "made", "making",
        "do", "does", "doing", "done",
        "take", "takes", "took", "taken", "taking",

        # 常见无意义动词
        "get", "gets", "got", "getting",
        "give", "gives", "gave", "given", "giving",
        "use", "uses", "used", "using",
        "put", "puts", "putting",
        "set", "sets", "setting",

        # 学术论文常见无意义词
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

        # 其他常见停用词
        "like", "such", "many", "much", "more", "most", "less", "least",
        "some", "any", "none", "all", "both", "each", "every", "either", "neither",
        "other", "another", "same", "different",
        "this", "these", "those", "their", "they", "them",

        # 其他可能的无意义字符
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
    new_words = [
        word for word in word_lst
        if word not in INDEX_IGNORE and not re.fullmatch(r"\d+|[a-zA-Z]{1,2}", word)
    ]
    return new_words




def process_word_list(word_list):
    word_set = set(word_list)  # 使用集合加速查找
    processed_list = []
    
    for word in word_list:
        if word.endswith("ss"):
            processed_list.append(word)  # 直接保留 "ss" 结尾的单词
        elif word.endswith("ies"):
            singular = word[:-3] + "y"  # 将 "ies" 替换为 "y"
            if singular in word_set:
                processed_list.append(singular)
            else:
                processed_list.append(word)
        elif word.endswith("es"):
            word_without_s = word[:-1]  # 去掉 's'
            word_without_es = word[:-2]  # 去掉 'es'
            
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
            processed_list.append(word)  # 不是 "es"/"ies" 结尾的词直接保留
    
    return processed_list