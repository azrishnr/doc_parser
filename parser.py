import docx
import json
import os

def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text.replace('"', "").replace('delimTITL', '').replace('delimJUNK', '').replace('delimINGR', '').replace('delimSTEP', '').strip())
    return '\n'.join(fullText)


def getSingleTag(recipe):
    _next = _prev = ""
    nxt = prev = False
    for x in recipe.strip().split("\n"):
        if 'next:' in x.strip().lower():
            nxt = True
        elif nxt == True:
            _next = x
            nxt = False
        elif 'previous:' in x.strip().lower():
            prev = True
        elif prev == True:
            _prev = x
            prev = False
    return _next, _prev


def getIngredients(recipe):
    _ing = []
    ing = _obj = False
    obj = {}
    curr = ""
    for x in recipe.strip().split("\n"):
        if ing == True and x.strip() == "":
            break
        elif 'ingredients' in x.strip().lower():
            ing = True
        elif ing == True and ':' in x:
            if _obj == True:
                _ing.append(obj)
                obj = {}
            obj[x.replace(":", "")] = []
            curr = x.replace(":", "")
            _obj = True
        elif ing == True:
            if _obj == True:
                obj[curr].append(breakIngredient(x))
            else:
                _ing.append(breakIngredient(x))
    if len(obj) >= 1:
        _ing.append(obj)
    return _ing

def breakIngredient(ing):
    units =  ['cup', 'can', 'bottle', 'tablespoon', 'tablespoons', 'tbsp', 'ounce', 'pound', 
'box', 'fliud ounce', 'fl oz', 'pint', 'gill','teaspoon', 'quart',
'gallon', ' ml ', ' c. ', ' l ', ' ml ', ' dl ', ' mg ', ' g ', ' kg ', ' mm ', ' cm ',
' m ', 'inch', 'in.', '(15- to 18-pound)', 'ball', 'qts', ' t ']
    ings = ing.split()
    result = {}
    desc = ""
    for i in ings:   
        _unit = False
        for u in units:
            if u in  " " + i.lower() + " ":
                result["quantity"] = desc
                desc = ""
                result["unit"] = i
                _unit = True
                break
        if _unit != True:
            desc = desc + " " + i
    result["description"] = desc
    return result
                
            
    
    
def getInstructions(recipe):
    _inst = []
    ing = _obj = False
    obj = {}
    curr = ""
    for x in recipe.strip().split("\n"):
        if 'instructions' in x.strip().lower() or 'preparation' in x.strip().lower() or 'method' in x.strip().lower():
            ing = True
        elif ing == True and ':"' in x:
            if _obj == True:
                _inst.append(obj)
                obj = {}
            obj[x.replace(":", "")] = []
            curr = x.replace(":", "")
            _obj = True
        elif ing == True:
            if _obj == True:
                obj[curr].append(x)
            else:
                _inst.append(x) 
    if len(obj) >= 1:
        _inst.append(obj)
    return _inst


def parseText(text):
    recipes = text.split("#START RECIPE#")
    listings = []
    for recipe in recipes:
        if recipe != "" and recipe is not None:
            _next, _prev = getSingleTag(recipe)
            append = True
            title =False
            _recipe = []
            instructions = ""
            for x in recipe.strip().split("\n"):
                if x == "" and append == False:
                    append = True
                elif 'next:' in x.strip().lower():
                    _recipe.append({x.replace(":", ""): _next})
                    append =False
                elif 'previous:' in x.strip().lower():
                    _recipe.append({x.replace(":", ""): _prev})
                    append =False
                elif 'ingredients' in x.strip().lower():
                    ingredients = getIngredients(recipe)
                    _recipe.append({x.replace(":", ""): ingredients})
                    append =False
                elif 'instructions' in x.strip().lower() or 'preparation' in x.strip().lower() or 'method' in x.strip().lower():
                    instructions = getInstructions(recipe)
                    _recipe.append({x.replace(":", ""): instructions})
                    break
                elif x != "" and append == True:
                    if title == False:
                        _recipe.append({'title': x})
                        title = True
                    else:
                        _recipe.append(x)
            listings.append(_recipe)
    return listings


filename = input("Enter File path: ")
#check file exists
if(os.path.exists(filename)):
    name, ext = os.path.splitext(filename)
    if ext in [".docx", ".txt"]:
        if ext == ".docx":
            data = getText(filename)
        else:
            with open(filename, 'rb', encoding="utf8") as myfile:
                data=myfile.read().replace('"', "").replace('delimTITL', '').replace('delimJUNK', '').replace('delimINGR', '').replace('delimSTEP', '').strip()
        listings = parseText(data)
        output = name + '.json'
        with open(output, 'w') as outfile:
            json.dump({'recipes' : listings}, outfile, indent=4, separators=(',', ': '), ensure_ascii=False)
        print("{} is created successfully".format(output))
    else:
        print("Invalid file extension...")
else:
    print("File does not exists")

