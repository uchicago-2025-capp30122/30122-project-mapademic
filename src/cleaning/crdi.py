from pathlib import Path
import pandas as pd
from collections import Counter
from utils import remove, ignore, process_word_list
import json


def process_json(file_path, output_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for province in data:
        province["name"] = province["name"].lower().replace(" ", "")

    # 保存修改后的 JSON 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
