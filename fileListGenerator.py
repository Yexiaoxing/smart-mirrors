#!/usr/bin/env python3

import json, hashlib, datetime
from os.path import join as path_join, isdir, getsize, getmtime, getctime, exists
from os import listdir, mkdir
from time import process_time

json_path = "json/"
search_root = "/mirror"
log_path = "filelistgenerator.log"

root_dirs = []

log_list = []

ignore_dir = [".DS_Store", ".git", "_h5ai"]
#response = open(local_filename)
#with open(fileNameToSave, 'w') as fileHandler:
#    fileHandler.write(json.dumps(wordList))

def log(log_msg):
    print(log_msg)
    log_list.append([process_time(), log_msg])

def log_finish():
    with open(log_path, "w") as handler:
        handler.write("\n".join(" ".join([str(a) for a in i]) for i in log_list))

def createDict(path, root={}):
    pathList = listdir(path)
    for i, item in enumerate(pathList):
        file_path = path_join(path, item)
        if item not in ignore_dir and exists(file_path):
            if isdir(file_path):
                if not root.get(item, False):
                    root[item] = {"type": "dir", "files": {}}
                createDict(file_path, root[item]["files"])
            else:
                if not root.get(item, False):
                    log("new file " + file_path)
                    root[item] = {"type": "file",
                                  "file_size": getsize(file_path),
                                  "mtime": getmtime(file_path), 
                                  "ctime": getctime(file_path),
                                  "md5": md5(file_path),
                                  "sha256": sha256(file_path)}
                else:
                    if root[item]["mtime"] != getmtime(file_path):
                        log("rehashing " + file_path)
                        root[item] = {"type": "file",
                                      "file_size": getsize(file_path),
                                      "mtime": getmtime(file_path), 
                                      "ctime": getctime(file_path),
                                      "md5": md5(file_path),
                                      "sha256": sha256(file_path)}
                        
                                    
    return root

def walkRoot(root):
    if not exists(json_path):
        mkdir(json_path)

    path_list = listdir(search_root)
    for i, item in enumerate(path_list):
        path = path_join(root, item)
        if isdir(path):
            root_dirs.append(item)
            if not exists(path_join(json_path, item + ".json")):
                inFile = open(path_join(json_path, item + ".json"), 'x')
                inFile.write("{}")
                inFile.close()
            with open(path_join(json_path, item + ".json"), 'r') as inFile:
                log(item + " generating at " + str(datetime.datetime.now()))
                generateJSON(json_path, item, createDict(path, json.load(inFile)))
                log(item + " generated at " + str(datetime.datetime.now()))
    
    with open(path_join(json_path, "rootdirs.json"), "w") as handler:
        handler.write(json.dumps(root_dirs))

def generateJSON(json_path, dir_name, file_dict):
    with open(path_join(json_path, dir_name + ".json"), 'w') as handler:
        handler.write(json.dumps(file_dict))
    print(dir_name + " json generated at " + str(datetime.datetime.now()))

def md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sha256(file_path):
    hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

startTime = process_time()
print("Process starts at " + str(datetime.datetime.now()))
walkRoot(search_root)
endTime = process_time()

log("All done within" + search_root)
log("Execution Time:" + str(endTime - startTime))
log_finish()