#!/usr/bin/env python
import os
import datetime
import shutil

global logfpath
global ignore_dirs

def log(str_):
    global logfpath
    print str_
    with open(logfpath, 'a') as fp:
        time = str(datetime.datetime.now())
        logstr = time + ":" + str_
        fp.write(logstr+"\n")

def copy_files(src_dir, src_file, dest_dir):
    log("Copying "+os.path.join(src_dir, src_file)+" to "+os.path.join(dest_dir, src_file)+"...")
    shutil.copy2(os.path.join(src_dir, src_file), os.path.join(dest_dir, src_file))
    log("Copied "+os.path.join(src_dir, src_file)+" to "+os.path.join(dest_dir, src_file)+"...")

def copy_dirs(src_dir, dest_dir):
    log("Copying "+src_dir+" to "+dest_dir+"...")
    shutil.copytree(src_dir, dest_dir)
    log("Copied "+src_dir+" to "+dest_dir+"...")

def copy_new_files(src_dir, new_files, dest_dir):
    if src_dir in ignore_dirs:
        return
    for file_ in new_files:
        copy_files(src_dir, file_, dest_dir)

def copy_new_dirs(src_dir, new_dirs, dest_dir):
    for dir_ in new_dirs:
        if os.path.join(src_dir, dir_) in ignore_dirs:
            continue
        copy_dirs(os.path.join(src_dir, dir_), os.path.join(dest_dir, dir_))

def get_modified_files(from_files, to_files):
    from_dict, to_dict = dict(), dict()
    for f in from_files:
        if f in to_files:
            from_dict[f] = from_files[f]
            to_dict[f] = to_files[f]
    return set(f for f in from_dict if from_dict[f]!=to_dict[f])

def copy_modified_files(src_dir, new_files, dest_dir):
    copy_new_files(src_dir, new_files, dest_dir)

def get_src_dst(fpath):
    global ignore_dirs
    ignore_dirs = []
    with open(fpath) as fp:
        a = fp.read()
    src, dest, ignore_dirs = a.splitlines()
    src, dest = [i.strip() for i in src.split(";") if i], [i.strip() for i in dest.split(";") if i]
    ignore_dirs = [i.strip() for i in ignore_dirs.split(";") if i]
    return src, dest
    

def backup(from_dirs, to_dirs):
    if not from_dirs or not to_dirs:
        return
    for from_dir, to_dir in zip(from_dirs, to_dirs):
        try:
            assert os.path.isdir(from_dir)
        except AssertionError:
            print from_dir, "Doesn't exist!!!"
            return
        try:
            assert os.path.isdir(to_dir)
        except AssertionError:
            print to_dir, "Doesn't exist!!!"
            return
            
        from_files = dict()
        from_subdirs = set()
        to_files = dict()
        to_subdirs = set()
        for f in os.listdir(from_dir):
            if f.startswith("."):
                continue
            f_path = os.path.join(from_dir, f)
            if os.path.isfile(f_path):
                from_files[f] = int(os.path.getmtime(f_path))
            elif os.path.isdir(f_path):
                from_subdirs.add(f)
        for f in os.listdir(to_dir):
            f_path = os.path.join(to_dir, f)
            if os.path.isfile(f_path):
                to_files[f] = int(os.path.getmtime(f_path))
            elif os.path.isdir(f_path):
                to_subdirs.add(f)
        new_files = set(from_files.keys()) - set(to_files.keys())
        new_subdirs = from_subdirs - to_subdirs
        modified_files = get_modified_files(from_files, to_files)
        copy_new_files(from_dir, new_files, to_dir)
        copy_modified_files(from_dir, modified_files, to_dir)
        copy_new_dirs(from_dir, new_subdirs, to_dir)
        backup([os.path.join(from_dir, from_subdir) for from_subdir in from_subdirs&to_subdirs], [os.path.join(to_dir, from_subdir) for from_subdir in from_subdirs&to_subdirs]) 


def main():
    global logfpath
    logfpath = "log.txt"
    src, dest = get_src_dst("dir_info.txt")
    log ("Backup Started...")
    backup(src, dest)
    log ("Backup completed...")

if __name__ == "__main__":
    main()