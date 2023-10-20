# Git Hooks

This folder contains git hooks to be installed on PythonAnywhere in order to ease syncing changes from a local machine to the server.

Have a look at each file for more informations, and installation steps.

## Requirements

Set up the local git repository to push changes to PythonAnywhere:

```console
# Usage:
# git remote add pythonanywhere <USER>@ssh.pythonanywhere.com:<SHAARLIMAGES_FOLDER>

# Example
$ git remote add pythonanywhere tiger222@ssh.pythonanywhere.com:/home/tiger222/shaarlimages
```

## Sync

To sync your local repository with PythonAnywhere:

```console
$ git push pythonanywhere main
```
