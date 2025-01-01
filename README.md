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

TODO: add examples of command line

### Masks for files

You may configure masks that will be used for file name matching. For example,
if you want to remove files only matching `*.jpg` and `*.jpeg` you may this command:

```
python -m dupfilesremover -m *.jpg,*.jpeg --recurse .\data1 .\data2 .\data3
```

### Predefined masks for filenames

You may use configuration file with sets of predefined masks for files, for example:

```
python -m dupfilesremover -s images --recurse .\data1 .\data2 .\data3
```

This command will remove files that matches set `images` in default
configuration files, provided with package.

Set `images` contains extensions assumed to match images:

```
['*.jpeg', '*.jfif', '*.jpg', '*.jp2', '*.j2k', '*.jpf', '*.jpx',
'*.jpm', '*.mj2', '*.tiff', '*.tif', '*.gif', '*.bmp', '*.png',
'*.ppm', '*.pgm', '*.pbm', '*.pnm', '*.webp', '*.heif', '*.heic',
'*.bpg', '*.drw', '*.ecw', '*.fits', '*.fit', '*.fts', '*.flif',
'*.ico', '*.iff', '*.lbm', '*.img', '*.jxr', '*.hdp', '*.wdp',
'*.liff', '*.nrrd', '*.pam', '*.pcx', '*.pgf', '*.plbm', '*.sgi',
'*.sid', '*.ras', '*.sun', '*.tga', '*.icb', '*.vda', '*.vst',
'*.xisf', '*.cd5', '*.cpt', '*.psd', '*.psp', '*.xcf', '*.pdn']
```

You may create your own configuration file and define your own sets. In
this case you will be required to provide configuration file name
in command line:

```
python -m dupfilesremover -c ./config/config.ini -s images --recurse .\data1 .\data2 .\data3
```

In your configuration file you may specify named set for matching masks.
To do this you need create `.ini` file with section `predefined_masks`.
In this section you may create key which will be name for named set and
then add masks as value for this key, separating masks by comma.
Multiline values also supported in case if they will be intended.

```
[predefined_masks]
data_files = *.data,*.dat
images =
    *.jpeg,
    *.jfif,
    *.jpg,
    *.jp2,
    *.j2k,
    *.jpf
```
