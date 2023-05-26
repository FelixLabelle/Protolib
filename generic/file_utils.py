import json

def load_jsonl(filename):
    examples = []
    with open(filename,'r',encoding="utf-8") as fh:
        examples = [json.loads(line) for line in fh.readlines()]
    return examples