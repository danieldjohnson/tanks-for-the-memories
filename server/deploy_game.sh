#!/bin/sh
set -e
cd ../game
mv config.py ../game_config.py
echo 'OUTPUT_LED = False\nOUTPUT_STDOUT = False\nUSE_SIMULATOR = True' >config.py
cd ../server/public/pypyjs-release-nojit/
git reset HEAD --hard
python tools/module_bundler.py add ./lib/modules ../../../game
cd ../../../
mv game_config.py game/config.py