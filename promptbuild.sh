#!/bin/bash

# Get the file tree excluding specific patterns

# Define the patterns to exclude
exclude_patterns="context_prompt.txt|*.db|public|*modules*|rollup.config.js|*.pyc*|*__pyc*|*.csv|_temp*|*promptbuild*|*.ipynb|*.lock|LICENCE|setupTypeScript.js|*.png|*.jpg|package-lock.json|.gitignore|*.vscode"

# Add all in .gitignore that are not commented out, not empty, and not already in exclude_patterns to exclude_patterns if .gitignore exists
if [ -f ".gitignore" ]; then
  while IFS= read -r line; do
    if [[ ! "$line" =~ ^#.*$ ]] && [[ -n "$line" ]] && [[ ! "$exclude_patterns" =~ $line ]]; then
      exclude_patterns+="|$line"
    fi
  done < ".gitignore"
fi

file_tree=$(tree -fi -I "$exclude_patterns")

# Initialize an empty string to hold the concatenated file contents
concatenated_files=""

# Iterate over each line in the file tree output
while IFS= read -r line; do
  # Skip directories and non-files
  if [ -f "$line" ]; then
    concatenated_files+="\n\n--- File: $line ---\n\n"
    concatenated_files+="$(cat "$line")"
  fi
done <<< "$file_tree"

# Build the prompt with the file tree and concatenated file contents
prompt="File Tree:\n$file_tree\n\nConcatenated Files:\n$concatenated_files"

prompt_pretext="I want you to help me fix some issues with my Svelte project with a Python backend. I have attached the code and file structure."

# Add the pretext to the prompt
prompt="$prompt_pretext\n\n$prompt"

# Copy the prompt to clipboard using pbcopy
echo -e "$prompt" | pbcopy

# Print a message to indicate completion
echo "Prompt with file tree and concatenated file contents has been copied to clipboard."