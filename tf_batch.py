#!/usr/bin/python3

import sys
import subprocess
import argparse
import threading
import os
import shutil

def exe_testflinger(cid, folder, job_template):
    job_name = args.job_template.split("/")[-1]

    work_dir = folder + '/' + cid
    os.makedirs(work_dir, exist_ok = True)
    shutil.copy(job_name, work_dir + '/' + cid + '.yaml')

    subprocess.run(
        "sed -e 's/{0}/{1}/g' {0} > {3}/{1}.yaml".format(
            job_name, cid, job_template, work_dir),
        shell=True,
        check=True,
    )
    try:
        subprocess.run(
            "testflinger submit -p {0}/{1} 2>&1 | tee {0}/output_{1}.txt".format(
                work_dir, cid),
            shell=True,
            check=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        print("%s testflinger job expired" % cid)

if __name__ == "__main__":
    # Parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("cid_list", help="text file containing cid list")
    parser.add_argument("job_template", help="job template yaml file")
    parser.add_argument(
        "target_folder",
        help="where to save the yaml files and testflinger output files",
    )
    args = parser.parse_args()

    threads = []

    with open(args.cid_list, "r") as f:
        cids = f.readlines()
        length = len(cids)
        for line in cids:
            cid = line.rstrip()
            thread = threading.Thread(
                        target=exe_testflinger,
                        args=(cid, args.target_folder, args.job_template))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()
