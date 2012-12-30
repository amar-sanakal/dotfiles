# include .bashrc if it exists
[[ -f "$HOME/.bashrc" ]] && source "$HOME/.bashrc"

# set PATH to include user's private bin, if it exists
[[ -d "$HOME/bin" ]] && PATH="$HOME/bin:$PATH"

# setup rvm, if locally installed
[[ -s "$HOME/.rvm/scripts/rvm" ]] && source "$HOME/.rvm/scripts/rvm" # Load RVM into a shell session *as a function*
