import codecs, json, re, os
from stat import ST_CTIME
team_dict = {'Toronto Raptors': ['@Raptors', '#WeTheNorth', '#RTZ'], 'Golden State Warriors': ['#DubNation', '#WarriorsGround'], 'OKC Thunder': ['@okcthunder', '#ThunderUp'], 'Los Angles Lakers': ['@Lakers', '#LakeShow'], 'New York Knicks': ['@nyknicks'], 'Cleveland Cavaliers': ['@cavs', '#AllForOne'], 'Houston Rockets': ['@HoustonRockets'], 'San Antonio Spurs': ['@spurs', '#GoSpursGo'], 'Denver Nuggets': ['@nuggets', '#MileHighBasketball'], 'New Orleans Pelicans': ['@PelicansNBA', '#Pelicans', '#DoItBig'], 'Dallas Mavericks': ['@dallasmavs'], 'Charlotte Hornets': ['@hornets'], 'LA Clippers': ['@LAClippers', '#ItTakesEverything'], 'Timberwolvers': ['@Timberwolves', '#PowerOfThePack'], 'Orlando Magic': ['@OrlandoMagic'], 'Indiana Pacers': ['@Pacers'], 'Brooklyn Nets': ['@BrooklynNets', '#BrooklynGrit'], 'Phoenix Suns': ['@Suns', '#WeArePHX'], 'Utah Jazz': ['@utahjazz', '#TakeNote'], 'Boston Celtics': ['@celtics'], 'Atlanta Hawks': ['@ATLHawks','#TrueToAtlanta'], 'Detroit Pistons': ['@DetroitPistons', '#DetroitBasketball', '#Pistons'], 'Chicago Bulls': ['@chicagobulls'], 'Philadelphia 76ers': ['@sixers'], 'Milwaukee Bucks': ['@Bucks', '#FearTheDeer'], 'Washington Wizards': ['@WashWizards'], 'Miami HEAT': ['@MiamiHEAT'], 'Memphis Grizzlies': ['@memgrizz', '#GrindCity'], 'Trail Blazers': ['@trailblazers'], 'Sacramento Kings': ['@SacramentoKings']}

tag_dict = {'#AllForOne': 'Cleveland Cavaliers',
 '#BrooklynGrit': 'Brooklyn Nets',
 '#DetroitBasketball': 'Detroit Pistons',
 '#DoItBig': 'New Orleans Pelicans',
 '#DubNation': 'Golden State Warriors',
 '#FearTheDeer': 'Milwaukee Bucks',
 '#GoSpursGo': 'San Antonio Spurs',
 '#GrindCity': 'Memphis Grizzlies',
 '#ItTakesEverything': 'LA Clippers',
 '#LakeShow': 'Los Angles Lakers',
 '#MileHighBasketball': 'Denver Nuggets',
 '#Pelicans': 'New Orleans Pelicans',
 '#Pistons': 'Detroit Pistons',
 '#PowerOfThePack': 'Timberwolvers',
 '#RTZ': 'Toronto Raptors',
 '#TakeNote': 'Utah Jazz',
 '#ThunderUp': 'OKC Thunder',
 '#TrueToAtlanta': 'Atlanta Hawks',
 '#WarriorsGround': 'Golden State Warriors',
 '#WeArePHX': 'Phoenix Suns',
 '#WeTheNorth': 'Toronto Raptors',
 '@ATLHawks': 'Atlanta Hawks',
 '@BrooklynNets': 'Brooklyn Nets',
 '@Bucks': 'Milwaukee Bucks',
 '@DetroitPistons': 'Detroit Pistons',
 '@HoustonRockets': 'Houston Rockets',
 '@LAClippers': 'LA Clippers',
 '@Lakers': 'Los Angles Lakers',
 '@MiamiHEAT': 'Miami HEAT',
 '@OrlandoMagic': 'Orlando Magic',
 '@Pacers': 'Indiana Pacers',
 '@PelicansNBA': 'New Orleans Pelicans',
 '@Raptors': 'Toronto Raptors',
 '@SacramentoKings': 'Sacramento Kings',
 '@Suns': 'Phoenix Suns',
 '@Timberwolves': 'Timberwolvers',
 '@WashWizards': 'Washington Wizards',
 '@cavs': 'Cleveland Cavaliers',
 '@celtics': 'Boston Celtics',
 '@dallasmavs': 'Dallas Mavericks',
 '@hornets': 'Charlotte Hornets',
 '@memgrizz': 'Memphis Grizzlies',
 '@nuggets': 'Denver Nuggets',
 '@nyknicks': 'New York Knicks',
 '@okcthunder': 'OKC Thunder',
 '@sixers': 'Philadelphia 76ers',
 '@spurs': 'San Antonio Spurs',
 '@trailblazers': 'Trail Blazers',
 '@utahjazz': 'Utah Jazz',
 'chicagobulls': 'Chicago Bulls'}
        
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
    words = []
    for w in text.split:
        if not w.startswith('@') and not w.startswith('#') and w != 'RT':
            words.append(w) 
    word_str = (" ").join(words)        
    clean_words = re.sub("[^a-zA-Z]", " ", word_str).lower().split()
    return clean_words
