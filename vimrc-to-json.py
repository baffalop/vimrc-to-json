import os
import re
import sys
import json

if len(sys.argv) > 1:
    path = os.path.realpath(sys.argv[1])
    print('Getting .vimrc from: %s' % path)
else:
    # get .vimrc from the same directory as this script
    path = os.getcwd() + "/.vimrc"
    print('Getting .vimrc from current working directory: %s (specify vimrc path in 1st argument to override)' % path)

if len(sys.argv) > 2:
    settingsPath = os.path.realpath(sys.argv[2])
    print('Getting settings.json from: %s' % settingsPath)
else:
    # get .vimrc from the same directory as this script
    settingsPath = os.path.dirname(path) + "/settings.json"
    print('Getting settings.json from .vimrc directory: %s (specify settings.json path in 2nd argument to override)' % path)

if not os.path.isfile(path):
    print('ERROR: Cannot find file at path %s' % path)
    exit(1)

file = open(path)
lines = file.read().split("\n")
file.close()

specialSearch = re.compile("^(<Leader>|<CR>|<Esc>|<Space>|<C-.>)", flags=re.I)

maptypes = {
    "nmap": "vim.normalModeKeyBindings",
    "vmap": "vim.visualModeKeyBindings",
    "imap": "vim.insertModeKeyBindings",
    "nnoremap": "vim.normalModeKeyBindingsNonRecursive",
    "vnoremap": "vim.visualModeKeyBindingsNonRecursive",
    "inoremap": "vim.insertModeKeyBindingsNonRecursive"
}

multimaptypes = {
    "map": ("nmap", "vmap"),
    "noremap": ("nnoremap", "vnoremap"),
}

vsmap = {
    "vim.normalModeKeyBindings": [],
    "vim.visualModeKeyBindings": [],
    "vim.insertModeKeyBindings": [],
    "vim.normalModeKeyBindingsNonRecursive": [],
    "vim.visualModeKeyBindingsNonRecursive": [],
    "vim.insertModeKeyBindingsNonRecursive": []
}

def splitMap(keymap):
    result = []

    while len(keymap) > 0:
        specials = specialSearch.match(keymap)
        if specials:
            special = specials.group(1)
            result.append(special)
            keymap = keymap[len(special):]
        else:
            result.append(keymap[0])
            keymap = keymap[1:]
    return result

mapPattern = re.compile("^(\w*map)\s+(\S+)\s+(\S+)")

# Get all the mappings and place them in the correct category.
for item in lines:
    matches = mapPattern.match(item)
    if not matches:
        continue

    mapname = matches.group(1)
    mapping = {
        "before": splitMap(matches.group(2)),
        "after": splitMap(matches.group(3)),
    }

    if mapname in maptypes:
        maptype = maptypes[mapname]
        vsmap[maptype].append(mapping)
    elif mapname in multimaptypes:
        for maptype in multimaptypes[mapname]:
            maptype = maptypes[maptype]
            vsmap[maptype].append(mapping)

# Write the JSON to settings.json in the same directory.
file = open(settingsPath, "w")
file.write(json.dumps(vsmap, indent=4))
file.close()
