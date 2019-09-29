import os
import re
import sys
import json

# get .vimrc path
if len(sys.argv) > 1:
    path = os.path.realpath(sys.argv[1])
    print('Getting .vimrc from: %s' % path)
else:
    # get .vimrc from the same directory as this script
    path = os.getcwd() + "/.vimrc"
    print('Getting .vimrc from current working directory: %s (specify vimrc path in 1st argument to override)' % path)

if not os.path.isfile(path):
    print('ERROR: Cannot find file at path %s' % path)
    exit(1)

# get settings.json path
if len(sys.argv) > 2:
    settingsPath = os.path.realpath(sys.argv[2])
    print('Getting settings.json from: %s' % settingsPath)
else:
    # get .vimrc from the same directory as this script
    settingsPath = os.path.dirname(path) + "/settings.json"
    print('Getting settings.json from .vimrc directory: %s (specify settings.json path in 2nd argument to override)' % path)

file = open(path)
lines = file.read().split("\n")
file.close()

settings = {}
if os.path.isfile(settingsPath):
    file = open(settingsPath)
    settings = json.loads(file.read())

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

lets = {
    "mapleader": "vim.leader",
}

sets = {
    "hlsearch": "vim.hlsearch",
}

vsmap = {
    "vim.normalModeKeyBindings": {},
    "vim.visualModeKeyBindings": {},
    "vim.insertModeKeyBindings": {},
    "vim.normalModeKeyBindingsNonRecursive": {},
    "vim.visualModeKeyBindingsNonRecursive": {},
    "vim.insertModeKeyBindingsNonRecursive": {}
}

reMappings = re.compile("^(\w*map)\s+(\S+)\s+(\S+)")
reLet = re.compile("^let (\S+)\s*=\s*(.*)")
reSet = re.compile("^set (\w+)(?:\s*=\s*(.*))?")
reSpecials = re.compile("^(<Leader>|<CR>|<Esc>|<Space>|<C-.>)", flags=re.I)

def splitMap(keymap):
    result = []

    while len(keymap) > 0:
        specials = reSpecials.match(keymap)
        if specials:
            special = specials.group(1)
            result.append(special)
            keymap = keymap[len(special):]
        else:
            result.append(keymap[0])
            keymap = keymap[1:]
    return result

def mappingsListToDict(mappings):
    return {''.join(mapping['before']): mapping for mapping in mappings}


# compile dictionary of existing mappings from settings.json
for maptype in vsmap.keys():
    if maptype in settings:
        vsmap[maptype] = mappingsListToDict(settings[maptype])

# Parse vimrc into mappings and add to vsmap dict
for item in lines:
    matches = reMappings.match(item)
    if not matches:
        continue

    mapname = matches.group(1)
    before = matches.group(2)
    mapping = {
        "before": splitMap(before),
        "after": splitMap(matches.group(3)),
    }

    if mapname in maptypes:
        maptype = maptypes[mapname]
        vsmap[maptype][before] = mapping
    elif mapname in multimaptypes:
        for maptype in multimaptypes[mapname]:
            maptype = maptypes[maptype]
            vsmap[maptype][before] = mapping

# Add or update mappings to settings.json based on vsmap
for (maptype, mappings) in vsmap.items():
    if mappings:
        settings[maptype] = list(mappings.values())

# Write the JSON to settings.json
file = open(settingsPath, "w")
json.dump(settings, file, indent=4)
file.close()
