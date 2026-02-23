autoload -Uz compinit

zstyle ':completion:*' cache-path "$XDG_CACHE_HOME/zsh/compcache"
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'

_comp_files=("$XDG_CACHE_HOME/zsh/compdump"(Nm-20))
if (( $#_comp_files )); then
    compinit -C -d "$XDG_CACHE_HOME/zsh/compdump"
else
    compinit -d "$XDG_CACHE_HOME/zsh/compdump"
fi
unset _comp_files
