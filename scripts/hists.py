"""
hists.py: script to make histograms from MuonRawHits ntuples. 

Run outside athena.

> python hists.py --input=input_*.root --cpu=2
"""

import argparse
import glob
import multiprocessing as mp
import subprocess
import sys
import warnings
warnings.filterwarnings(action="ignore", category=RuntimeWarning)

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro("$ROOTCOREDIR/scripts/load_packages.C")

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  help="comma-separated, glob-able input root files")
    parser.add_argument("--cpu",    help="number of cpu")
    parser.add_argument("--events", help="max number of events")
    return parser.parse_args()

def main():

    ops = options()
    if not ops.input:
        fatal("Please give a comma-separated list of --input files (glob-capable)")

    inputs = []
    for inp in ops.input.split(","):
        if "*" in inp:
            inputs.extend(glob.glob(inp))
        else:
            inputs.append(inp)

    status = parallelize_histograms(inputs)

def parallelize_histograms(files):

    ops = options()

    maxevents   = int(ops.events) if ops.events else -1
    cpu         = int(ops.cpu)    if ops.cpu    else 1
    configs     = []

    while files:
        iconfig = len(configs)
        configs.append(dict())
        configs[iconfig]["input"]  = files.pop(0)
        configs[iconfig]["output"] = "histograms_%04i.root" % (iconfig)
        configs[iconfig]["events"] = maxevents

    for iconfig, config in enumerate(configs):
        print " job", iconfig
        print " -", config["input"]

    # map
    npool = min(len(configs), cpu, mp.cpu_count()-1)
    pool = mp.Pool(npool)
    results = pool.map(ntuple_to_histogram, configs)

    # reduce
    hadd("histograms.root", sorted(glob.glob("histograms_*.root")))

def ntuple_to_histogram(config):

    job = ROOT.MuonRawHistograms(config["input"], config["output"])
    job.initialize()
    job.execute(config["events"])
    job.finalize()

def hadd(output, inputs, delete=False):

    command = ["hadd", output] + inputs
    print
    print " ".join(command)
    print
    subprocess.call(command)
    print
    print "rm -f %s" % (" ".join(inputs))
    print

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
