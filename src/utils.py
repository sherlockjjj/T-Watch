import codecs, json

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

def demo():
    path = 'tmp/test.jsonl'

    ary_of_objects = [
        {'name': 'a', 'title': 'CEO'},
        {'name': 'b', 'title': 'VP'},
        {'name': 'c', 'title': 'CMO'}
    ]

    single_object = {'name': 'a', 'title': 'CEO'}
    write_json_file(ary_of_objects, path)
    obj = read_json_file(path)
    print (obj)
    pass
