#!/usr/bin/env nextflow

/*
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
    Peter Ruzanov
*/

/********************************************************************/
/* this block is auto-generated based on info from pkg.json where   */
/* changes can be made if needed, do NOT modify this block manually */
nextflow.enable.dsl = 2
version = '2.30.0'  // package version

container = [
    'ghcr.io': 'ghcr.io/icgc-argo-qc-wg/argo-qc-tools.bedtools-mean'
]
default_container_registry = 'ghcr.io'
/********************************************************************/


// universal params go here
params.container_registry = ""
params.container_version = ""
params.container = ""

params.cpus = 1
params.mem = 4  // GB
params.publish_dir = ""  // set to empty string will disable publishDir

// tool specific params go here, add / change as needed
params.input_data = "tests/input/SWID_SQ_REPSYM_REPSYM_NoIndex_L001_001.chr22.sub.bam"
params.interval_file = "tests/input/LTR_intervals.chr22.bed"


process coverageMeanTarget {
    container "${params.container ?: container[params.container_registry ?: default_container_registry]}:${params.container_version ?: version}"
    publishDir "${params.publish_dir}/${task.process.replaceAll(':', '_')}", mode: "copy", enabled: params.publish_dir

    cpus params.cpus
    memory "${params.mem} GB"

    input:
      path input_data
      path interval_file

    output:
      path "${input_data}.coverage_mean.tgz", emit: qc_tar

    script:
      """
      main.py -d ${input_data} \
              -i ${interval_file} 
      """
   }


// this provides an entry point for this main script, so it can be run directly without clone the repo
// using this command: nextflow run <git_acc>/<repo>/<pkg_name>/<main_script>.nf -r <pkg_name>.v<pkg_version> --params-file xxx
workflow {
  coverageMeanTarget(
    file(params.input_data),
    file(params.interval_file)
  ).collect()
}
