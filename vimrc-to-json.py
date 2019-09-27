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
    print('Getting .vimrc from current working directory: %s (specify vimrc path in argument to override)' % path)

if not os.path.isfile(path):
    print('ERROR: Cannot find file at path %s' % path)
    exit(1)

file = open(path)
lines = file.read().split("\n")
file.close()

maptypes = {
    "nmap": "vim.normalModeKeyBindings",
    "vmap": "vim.visualModeKeyBindings",
    "imap": "vim.insertModeKeyBindings",
    "nnoremap": "vim.normalModeKeyBindingsNonRecursive",
    "vnoremap": "vim.visualModeKeyBindingsNonRecursive",
    "inoremap": "vim.insertModeKeyBindingsNonRecursive"
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
    specialSearch = re.compile("^(<Leader>|<CR>|<Esc>|<Space>|<C-.>)", flags=re.I)
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

# Get all the mappings and place them in the correct category.
for item in lines:
    matches = re.match("(^.*map)\s([\S]+)\s+([\S]+)$", item)
    if matches:
        maptype = matches.group(1)
        before = matches.group(2)
        after = matches.group(3)

        if maptype in maptypes:
            maptype = maptypes[maptype]
            vsmap[maptype].append({"before" : splitMap(before), "after" : splitMap(after)})

# Write the JSON to settings.json in the same directory.
file = open(os.path.dirname(path) + "/settings.json", "w")
file.write(json.dumps(vsmap, indent=4))
file.close()
