"""
hot_tubes.py: script to dump the hottest tubes from MuonRawHits ntuples. 

Run outside athena.

> python hot_tubes.py --input=input_*.root
"""

import argparse
import glob
import multiprocessing as mp
import subprocess
import sys
import ROOT

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  help="comma-separated, glob-able input root files")
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

    for input in inputes:
        counts = count_tubes(inputs)
        for tube in counts:
            print tube, counts[tube]
        
def count_tubes(input):

    file = ROOT.TFile.Open(input)
    tree = file.Get("physics")

    tree.SetBranchStatus("*", 0)
    tree.SetBranchStatus("mdt_chamber_n",           1)
    tree.SetBranchStatus("mdt_chamber_type",        1)
    tree.SetBranchStatus("mdt_chamber_eta_station", 1)
    tree.SetBranchStatus("mdt_chamber_side",        1)
    tree.SetBranchStatus("mdt_chamber_phi_sector",  1)
    tree.SetBranchStatus("mdt_chamber_tube_n",      1)
    tree.SetBranchStatus("mdt_chamber_tube_id",     1)

    counts = {}
    for entry in xrange(10):
        _ = tree.GetEntry(entry)

        for ich in xrange(tree.mdt_chamber_n):
            chamber = "%s%i%s%2i" % (tree.mdt_chamber_type[ich],
                                     tree.mdt_chamber_eta_station[ich],
                                     tree.mdt_chamber_side[ich],
                                     tree.mdt_chamber_phi_sector[ich])
            print chamber
            for itu in xrange(tree.mdt_chamber_tube_n[ich]):
                tube = "%s_%i" % (chamber, tree.mdt_chamber_tube_id[ich][itu])
                print tube
                counts[tube] = counts[tube]+1 if tube in counts else 1
            print

    return counts
            
def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
