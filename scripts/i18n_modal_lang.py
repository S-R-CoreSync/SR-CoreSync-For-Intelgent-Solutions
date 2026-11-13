P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\js\sr-studio-i18n.js'
s = open(P, encoding='utf-8', newline='').read()
before = s

# 1 · each language card declares the language of its own name
old_card = '<div class="sr-i18n-launchpad-card${activeClass}" data-code="${l.code}"'
new_card = '<div class="sr-i18n-launchpad-card${activeClass}" lang="${l.code}" data-code="${l.code}"'
if old_card in s:
    s = s.replace(old_card, new_card, 1)
    print('cards: lang added')

# 2 · the selector itself is a language menu, not page content
old_attr = "modal.setAttribute('aria-label', 'Sovereign Language Selector');"
new_attr = ("modal.setAttribute('aria-label', 'Sovereign Language Selector');\r\n"
            "        modal.setAttribute('translate', 'no');")
if old_attr in s and "setAttribute('translate'" not in s:
    s = s.replace(old_attr, new_attr, 1)
    print('modal: translate=no added')

# 3 · the active card is the current language
old_pick = "var activeClass = l.code === curLang ? ' active' : '';"
new_pick = ("var activeClass = l.code === curLang ? ' active' : '';\r\n"
            "            var current = l.code === curLang ? ' aria-current=\"true\"' : '';")
if old_pick in s and 'aria-current' not in s:
    s = s.replace(old_pick, new_pick, 1)
    s = s.replace('<div class="sr-i18n-launchpad-card${activeClass}" lang="${l.code}"',
                  '<div class="sr-i18n-launchpad-card${activeClass}" lang="${l.code}"${current}', 1)
    print('active card: aria-current added')

if s != before:
    open(P, 'w', encoding='utf-8', newline='').write(s)
    print('written')
else:
    print('nothing changed')
