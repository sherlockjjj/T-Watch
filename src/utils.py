import codecs, json, re, os
from stat import ST_CTIME
#IO helpers
def write_json_file(obj, path):
    """
    Dump an object and write it out as JSON to a file
    """
    f = codecs.open(path, 'w', 'utf-8')
    f.write(json.dumps(obj, ensure_ascii=False))
    f.close()

def write_json_lines_file(ary_of_objects, path):
    """
    Dump a list of objects out as a JSON lines file
    """
    f = codecs.open(path, 'w', 'utf-8')
    for obj in ary_of_objects:
        json_record = json.dumps(obj, ensure_ascii=False)
        f.write(json_record + "\n")
    f.close()

def read_json_file(path):
    """
    Turn a normal JSON line (no CRs per record) into an object.
    """
    text = codecs.open(path, 'r', 'utf-8').read()
    return json.loads(text)

def read_json_lines_file(path):
    """
    Turn a JSON lines files (CRs per record) into an array of objects
    """
    ary = []
    f = codecs.open(path, 'r', 'utf-8')
    for line in f:
        record = json.loads(line.rstrip("\n|\r"))
        ary.append(record)
    return ary

def find_input_files():
    """
    Find all files in a folder and sort by time
    """
    paths = []
    for file in os.listdir("../kafka_files"):
        if file.endswith(".jsonl"):
            paths.append(os.path.join("../kafka_files/", file))
    entries = [(os.stat(path)[ST_CTIME], path) for path in paths]
    sorted_entries = sorted(entries)
    return sorted_entries

#nlp helpers
def filter_ads(text):
    """
    Filter tweets with hyper links
    """
    return 'https' not in text

def preprocess(text):
    words = re.sub("[^a-zA-Z]", " ", text).lower().split()
    return words
