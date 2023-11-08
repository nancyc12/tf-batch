#!/usr/bin/python3

import sys
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("cid_list", help="text file containing cid list")
parser.add_argument("job_template", help="job template yaml file")
parser.add_argument(
    "target_folder",
    help="where to save the yaml files and testflinger output files",
)
args = parser.parse_args()
job_name = args.job_template.split("/")[-1]

with open(args.cid_list, "r") as f:
    cids = f.readlines()
    for line in cids:
        cid = line.rstrip()
        print(cid)
        subprocess.run(
            "sed -e 's/{0}/{1}/g' {2} > {3}/{1}".format(
                job_name, cid, args.job_template, args.target_folder
            ),
            shell=True,
            check=True,
        )
        try:
            subprocess.run(
                "testflinger submit -p {0}/{1} | tee {0}/output_{1}.txt".format(
                    args.target_folder, cid
                ),
                shell=True,
                check=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            print("%s testflinger job expired" % cid)
