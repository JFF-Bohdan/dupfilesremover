# dupfilesremover

Tool for duplicate files removing.

Removes duplicate files existing with same or different name in on one
or more folder(s).

For example, I do backups of my photos over multiple devices, and sometimes I can have same photo 
copied multiple times. It can happen when I move photo from one folder to another.

This tool, helps me find duplicates of a same file, when it's stored in multiple folders or there are 
multiple copies in a same folder but with a different names.

## Use case

For example, let's assume that same image available (with different names) in:

- Folders `data1`, `data2` and `data3`
- Sub-folders of any of these folders (for example `data1/new images/best`)

We want to remove all duplicates and follow these rules:

- Recursively remove all duplicates and save only one file
- In case if duplicates will be in same folder - save file with the shortest name
- Save images from `data1` folder (or sub-folders of `data1` in case if identical files 
  also available in `data2` and `data3`)
- In case if file will be found in any of `data1` sub-folders save with the shortest path

To do this we may just run:

```
python -m dupfilesremover --recurse .\data1 .\data2 .\data3
```

Basically the folders order in the command line will define priorities of the copies if more than 
one will be found. As a result, `data1` will have the highest priority and inside `data1` files with shorter 
file name and shortest path will have precedence.

## How to install

You can install from PyPi just by using:

```
pip install dupfilesremover
```

Or you can install from GitHub by using pip:

```
pip install git+https://github.com/JFF-Bohdan/dupfilesremover
```

Or just clone and install from source code:

```
git clone https://github.com/JFF-Bohdan/dupfilesremover.git
cd dupfilesremover
python setup.py install
```

## Usage

You can use tool like:

```shell
dupfilesremover --recurse tmp/folder1 tmp/folder2 tmp/folder3
```

In this example we are going to analyse folders `tmp/folder1`, `tmp/folder2` and `tmp/folder3` 
for duplicate files and remove them.

If you would like to perform dry-run (no action files removal, just analysis), you can use:

```shell
dupfilesremover --dry-run --recurse tmp/folder1 tmp/folder2 tmp/folder3
```
