#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Copyright (c) 2021, ICGC ARGO

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.

  Authors:
    Linda Xiang
"""

import os
import sys
import argparse
import subprocess
from multiprocessing import cpu_count
from zipfile import ZipFile
import json
from glob import glob
import tarfile
import io

def run_cmd(cmd):
    proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
    stdout, stderr = proc.communicate()

    return (
        stdout.decode("utf-8").strip(),
        stderr.decode("utf-8").strip(),
        proc.returncode
    )

def get_tool_version(toolname):
    get_tool_version_cmd = f"{toolname} --version | grep -i '^{toolname}'"
    stdout, stderr, returncode = run_cmd(get_tool_version_cmd)
    if returncode:
        sys.exit(f"Error: unable to get version info for {toolname}.\nStdout: {stdout}\nStderr: {stderr}\n")

    return stdout.strip().split(' ')[-1].strip('v')

def prep_qc_metrics(output_dir, tool_ver):
    qc_metrics = {
        'tool': {
            'name': 'FastQC',
            'version': tool_ver
        },
        'metrics': {},
        'description': 'High level sequencing reads QC metrics generated by FastQC.'
    }

    fastqc_zip = glob(os.path.join(output_dir, "*_fastqc.zip"))[0]
    fastqc_data = os.path.join(os.path.basename(fastqc_zip).rstrip('.zip'), "summary.txt")
    with ZipFile(fastqc_zip) as myzip:
      with myzip.open(fastqc_data) as myfile:
        with io.TextIOWrapper(myfile, encoding="utf-8") as mytext:
          for line in mytext:
            cols = line.rstrip().split('\t')
            qc_metrics['metrics'].update({
              cols[1]: cols[0]
            })

    qc_metrics_file = 'qc_metrics.json'
    with open(qc_metrics_file, "w") as j:
        j.write(json.dumps(qc_metrics, indent=2))

    return qc_metrics_file

def prepare_tarball(seq, qc_metrics, output_dir):

    files_to_tar = [qc_metrics]
    for f in sorted(glob(output_dir+'/*')):
      files_to_tar.append(f)

    tarfile_name = f"{os.path.basename(seq)}.fastqc.tgz"
    with tarfile.open(tarfile_name, "w:gz") as tar:
      for f in files_to_tar:
        tar.add(f, arcname=os.path.basename(f))


def main():
    """
    Python implementation of tool: fastqc
    """

    parser = argparse.ArgumentParser(description='Tool: fastqc')
    parser.add_argument('-s', '--seq', type=str,
                        help='Input seq', required=True)
    parser.add_argument('-t', '--threads', type=int, default=cpu_count(),
                        help='Number of threads')
    args = parser.parse_args()

    if not os.path.isfile(args.seq):
        sys.exit('Error: specified seq file %s does not exist or is not accessible!' % args.seq)


    # get tool version info
    tool_ver = get_tool_version('fastqc')

    output_dir = 'output'
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)

    # run fastqc
    fastqc_args = [
        '-t', str(args.threads),
        '-o', output_dir
    ]

    cmd = ['fastqc'] + fastqc_args + [args.seq]
    stdout, stderr, returncode = run_cmd(" ".join(cmd))
    if returncode:
        sys.exit(f"Error: 'fastqc' failed.\nStdout: {stdout}\nStderr: {stderr}\n")

    
    # parse fastqc output and put it in qc_metrics.json
    qc_metrics_file = prep_qc_metrics(output_dir, tool_ver)

    # prepare tarball to include output files and qc_metrics.json
    prepare_tarball(args.seq, qc_metrics_file, output_dir)

if __name__ == "__main__":
    main()
