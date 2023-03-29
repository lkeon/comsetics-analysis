"""Test extracting individual ingredients from the ingredients
JSON entry."""

import json
import re

def find_string(str, key):
    """Find all occurences of key in provided string."""
    keyLen = len(key)
    strLen = len(str)
    locs = []
    for ii in range(strLen - keyLen):
        if str[ii: ii + keyLen] == key:
            locs.append(ii)
    return locs

def trim_chars(str, lead=[' ', '-'], lag=[' ']):
    """Remove leading and trailing characters from the string provided."""
    if lead:  # Trim leading
        ii = 0
        while True:
            if str[ii] in lead:
                ii += 1
            else:
                break
        str = str[ii:]

    if lag:  # Trim lagging
        ii = len(str)
        while True:
            if str[ii - 1] in lag:
                ii -= 1
            else:
                break
        str = str[:ii]

    return str

def trim_string(str, lead=[' ', '<br>'], lag=[' ', '<br>']):
    """Trims leading and lagging strings."""
    while True:
        stopWhile = True
        for lds in lead:
            if str.find(lds) == 0:
                str = str[len(lds):]
                stopWhile = False
                break  # repeat for loop from beginning if trimmed
            else:
                stopWhile = stopWhile and True
        if stopWhile:
            break  # stop while if nothing to trim
    
    while True:
        stopWhile = True
        for lgs in lag:
            lastPos = len(str) - len(lgs)
            if lastPos >= 0 and str.rfind(lgs) == lastPos:
                str = str[:lastPos]
                stopWhile = False
                break
            else:
                stopWhile = stopWhile and True
        if stopWhile:
            break

    return str

def starts_with(str, char, ignore=[' ']):
    """Checks whether string starts with specified char."""
    if len(str) == 0:
        return False
    
    ii = 0
    while True:
        if len(str) > ii + 1 and str[ii] in ignore:
            ii += 1
        elif str[ii] == char:
            return True
        else:
            return False

def extract_ingredients(strIn):
    """Extract ingredients as obtained from the website."""
    # Find line breaks in string that determine text sections
    locs1 = find_string(strIn, '<br>')
    locs2 = find_string(strIn, '<p>')
    if len(locs1) >= len(locs2):
        locs = locs1
        skip = 4
    else:
        locs = locs2
        skip = 3

    # Remove any subsequent line breaks
    if len(locs) > 1:
        locs = [(loc + skip, locNext) for loc, locNext in zip(
            [-skip] + locs, locs + [len(strIn)]) if locNext - loc > skip]
    
    if len(locs) == 0:
        locs = [(0, len(strIn))]

    # Divide string into sections based on '<br>'
    ingr = []
    for start, stop in locs:
        strSplit = strIn[start: stop]
        lead = [' ', '<br>', '</br>', '\n', '\r', '<p>', '</p>']
        lag = [' ', '<br>', '</br>', '\r', '\n', '.', '<p>', '</p>', '\t']
        strSplit = trim_string(strSplit, lead=lead, lag=lag)
        
        # Section where ingredients start with '-'
        if starts_with(strSplit, '-'):
            # Separate ingredient from explanation using ':'
            semi = strSplit.find(':')
            if semi != -1:
                strSplit = strSplit[:semi]
            strSplit = trim_chars(strSplit)
            # If multiple ingredients in one line 'and' is present
            andWord = strSplit.find('and')
            if andWord != -1:
                # If 'and' present, split ingredients
                strSplitBefore = trim_chars( strSplit[:andWord] )
                strSplitBefore = trim_ingrediens(strSplitBefore)
                ingr.append(strSplitBefore)
                strSplitAfter = trim_chars( strSplit[andWord + 3:] )
                strSplitAfter = trim_ingrediens(strSplitAfter)
                ingr.append(strSplitAfter)
            else:
                strSplit = trim_ingrediens(strSplit)
                ingr.append(strSplit)
        
        # Subsequent section (only first) contains other ingredients, comma separated
        else:
            if len(strSplit) > 10:
                ingredientList = strSplit.split(', ')
                ingredientList = trim_ingrediens(ingredientList)
                ingr.extend(ingredientList)
                break # other subsections contain generic info
            else:
                continue  # ingredients likely not present in this section
    
    return ingr

def is_water(str):
    """Check whether ingredient is water."""
    str = str.lower()

    if 'water' in str:
        if len(str) <= len('water') + 2:
            return True
        elif 'eau' in str:
            return True
        elif 'aqua' in str:
            return True
        else:
            return False
    else:
        return False


def is_parfum(str):
    """Check if ingredient is parfum."""
    str = str.lower()

    if 'fragrance' in str:
        if len(str) <= len('fragrance') + 4:
            return True
        elif 'parfum' in str:
            return True
    elif 'parfum' in str:
        if len(str) <= len('parfum') + 4:
            return True  
    else:
        return False


def trim_ingrediens(ingList):
    """Rename known ingredients to the same name."""
    # Convert to list if not
    if not isinstance(ingList, list):
        returnList = False
        ingList = [ingList]
    else:
        returnList = True

    for ii, ing in enumerate(ingList):
        if is_water(ing):
            ingList[ii] = 'Water/Aqua/Eau'
            continue
        if is_parfum(ing):
            ingList[ii] = 'Parfum/Fragrance'
            continue
        ingList[ii] = trim_chars(ingList[ii], lead=['*', '+', ' '], lag=['*', ' ', '.'])
        ingList[ii] = re.sub('\(.*\)', ' ', ingList[ii])  # remove any parenthesis with content
        ingList[ii] = re.sub('\[.*\]', ' ', ingList[ii])  # remove square brackets
        ingList[ii] = re.sub('[\d\.]*\%', ' ', ingList[ii])  # remove percentages
        ingList[ii] = re.sub('\s{2,}', ' ', ingList[ii])  # remove double space
    
    if returnList:
        return ingList
    else:
        return ingList[0]


def main():
    """Run main function if this file is run."""

    # Import JSON file
    pth = '/path/'
    fileIn = pth + 'in.json'
    with open(fileIn, 'r') as txtIn:
        dataIn = json.load(txtIn)
    
    # Loop through dictionary and get ingredients
    dataOut = {}
    for ii, product in enumerate(dataIn):
        try:
            if ii == 15:
                print('stop')
            dataOut[product] = {}
            ingredients = dataIn[product]['ingredients']
            ingredients = extract_ingredients(ingredients)
            dataOut[product]['ingredients'] = ingredients
            dataOut[product]['price'] = float( re.findall('\d*\.\d*', dataIn[product]['price'])[0] )
            dataOut[product]['loves-count'] = dataIn[product]['loves-count']
            dataOut[product]['rating'] = dataIn[product]['rating']
            dataOut[product]['reviews'] = dataIn[product]['reviews']
            dataOut[product]['bestselling'] = 1 - eval( dataIn[product]['bestselling'] )
            print('Parsed ' + str(ii) + '/' + str(len(dataIn)) + ': ' + product)
        except Exception as e:
            print('WARNING Skipping ' + str(ii) + ': ' + product)
            print(e)
            continue
    
    print('Finished parsing.')
    
    # Save as JSON
    fileOut = pth + 'out.json'
    with open(fileOut, 'w') as fileOut:
        jsonTxt = json.dumps(dataOut)
        fileOut.write(jsonTxt)
    
    print('JSON file saved.')

if __name__ == '__main__':
    main()
