#!/bin/bash

# Remove screen clearing after closing less, vim etc
# Tested Ubuntu 22.04 with root user
# Step 1: Dump the xterm terminfo source
infocmp -I xterm > ~/xterm-noclear.src

# Step 2: Modify the terminfo source
# - Replace terminal name
# - Remove smcup and rmcup entries using
sed -i \
    -e 's/^xterm|xterm-debian/xterm-noclear|xterm-debian-noclear/' \
    -e 's/smcup=[^,]*,//g' \
    -e 's/rmcup=[^,]*,//g' \
    ~/xterm-noclear.src

# Step 3: Compile the modified terminfo
tic ~/xterm-noclear.src

# Step 4: Add export line to .profile if not already present
PROFILE=~/.profile
TERM_SETTING='export TERM=xterm-noclear'

if ! grep -Fxq "$TERM_SETTING" "$PROFILE"; then
    echo "$TERM_SETTING" >> "$PROFILE"
    echo "Added '$TERM_SETTING' to $PROFILE"
else
    echo "'$TERM_SETTING' already present in $PROFILE"
fi
