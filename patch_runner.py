
import re

with open('js/sr-lang-map.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's inspect index of var MARKETS
idx1 = code.find('var MARKETS = [')
idx2 = code.find('];', idx1)
print('Found MARKETS from', idx1, 'to', idx2)
