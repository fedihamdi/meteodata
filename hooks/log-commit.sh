#!/usr/bin/env bash
set -e

function get_version() {
  ver=$(git show origin/"$2":src/"$1"/__init__.py |grep __version__| sed 's/__version__ = //'| sed 's/\"//g')
  echo "$ver"
}

function add_line() {
  if [ $# -ne 2 ]; then
    text="$1 = \"$2\""
  else
    text="$1 = \"$2\"\r\n"
  fi
  echo "$text"
}

#=== 'prev-commit' solution by o_O Tync
#commit_hash=$(git rev-parse --verify HEAD)
commit=$(git log -1 --pretty="%H%n%ci") # hash \n date
commit_hash=$(echo "$commit" | head -1)
commit_date=$(echo "$commit" | head -2 | tail -1) # 2322-12-28 05:16:23 +0300

branch_name=$(git symbolic-ref -q HEAD)
branch_name=${branch_name##refs/heads/}
branch_name=${branch_name:-HEAD} # 'HEAD' indicates detached HEAD situation

#module=$(ls -1 src | grep -v egg-info | grep -v py |sed 1q)
#${module}
file="src/GITCOMMIT"
touch "$file"
git add "$file" # Force the add of the file

#dev_version=$(get_version "$module" "develop")
#main_version=$(get_version "$module" "master")


txt=$(add_line "git_commit" "$commit_hash")
txt+=$(add_line "date" "$commit_date")
txt+=$(add_line "branch" "$branch_name")
#txt+=$(add_line "develop_version" "$dev_version")
#txt+=$(add_line "master_version" "$main_version" "end")

intext=$(cat "$file")
if [ "$intext" != "$txt" ] ; then
  echo -e "$txt" > "$file"
fi
