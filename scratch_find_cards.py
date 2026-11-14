import re
s = open('partials/21-services.html', encoding='utf-8').read()
# Get a full example of tech-card-footer-actions
matches = list(re.finditer('tech-card-footer-actions', s))
m = matches[0]
# Get the full content of this footer block
snippet = s[m.start()-50:m.start()+1000]
print(snippet)
