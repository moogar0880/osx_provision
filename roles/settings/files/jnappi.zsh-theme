###############################################################################
# Echo information about the currently active python virtualenv, if one is
# currently active
# Globals:
#   None
# Arguments:
#   None
# Returns:
#   None
###############################################################################
venv_name() {
	local venv=$VIRTUAL_ENV
	if [[ -n "${venv##*/}" ]] ; then
		echo "%{$fg[yellow]%}venv:%{$reset_color%}%{$fg[red]%}${venv##*/}%{$reset_color%} $EPS1"
	fi
}

ZSH_THEME_GIT_PROMPT_PREFIX="%{$reset_color%}%{$fg[green]%}["
ZSH_THEME_GIT_PROMPT_SUFFIX="]%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_DIRTY="%{$fg[red]%}*%{$reset_color%}"
ZSH_THEME_GIT_PROMPT_CLEAN=""

###############################################################################
# Echo git information about the current directory, if the current directory is
# a git repository.
# Globals:
#   ZSH_THEME_GIT_PROMPT_PREFIX
#   ZSH_THEME_GIT_PROMPT_SUFFIX
#   ZSH_THEME_GIT_PROMPT_DIRTY
#   ZSH_THEME_GIT_PROMPT_CLEAN
# Arguments:
#   None
# Returns:
#   None
###############################################################################
# Customized git status, oh-my-zsh currently does not allow render dirty status before branch
git_custom_status() {
  local cb=$(current_branch)
  if [ -n "$cb" ]; then
    echo "$(parse_git_dirty)$ZSH_THEME_GIT_PROMPT_PREFIX$(current_branch)$ZSH_THEME_GIT_PROMPT_SUFFIX"
  fi
}

RPS1='$(venv_name)'
PROMPT='$(git_custom_status)%{$fg[cyan]%}[%~% ]%{$reset_color%}%B$%b '
