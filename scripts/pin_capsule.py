P = r'D:\I-Ai\App\S&R CoreSync For Intelligent Solutions\Project\js\sr-dock-merge.js'
s = open(P, encoding='utf-8', newline='').read()

old_start = "  /* the capsule rides on top of the dock, measured - never a fixed guess */"
old_end = "    cap.style.setProperty('left', Math.max(14, Math.round(r.left - cw - 20)) + 'px', 'important');\r\n  }"
i = s.find(old_start)
j = s.find(old_end)
assert i > 0 and j > i, 'capsule function not found'
j += len(old_end)

new = """  /* desktop: the capsule sits at the far left edge, the mirror of the counters
     at the far right, with the dock holding the centre. When the space left of
     the dock is too tight, it steps one level up instead of crowding it. */
  function stickTools() {
    var cap = document.querySelector('.sr-tools-capsule');
    var dock = document.getElementById('appleMacosDockWrapper');
    if (!cap || !dock) { return; }
    var r = dock.getBoundingClientRect();
    if (r.height < 10) { return; }
    var box = cap.getBoundingClientRect();
    var cw = box.width || 260;
    var ch = box.height || 46;
    var edge = 22;
    var bottom = window.innerHeight - r.bottom;
    if (edge + cw + 12 > r.left) { bottom += ch + 12; }
    cap.style.setProperty('bottom', bottom + 'px', 'important');
    cap.style.setProperty('left', edge + 'px', 'important');
  }"""

s = s[:i] + new + s[j:]
open(P, 'w', encoding='utf-8', newline='').write(s)
print('capsule pinned to the left edge')
