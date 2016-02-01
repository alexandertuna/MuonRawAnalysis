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
import time
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

    for inp in inputs:

        counts = count_tubes(inp)

        tubes = sorted(counts.keys(), key=counts.get, reverse=True)
        for tube in tubes[:500]:
            print tube, counts[tube], counts["total"]
            
def count_tubes(inp):

    rfile = ROOT.TFile.Open(inp)
    tree  = rfile.Get("physics")

    tree.SetBranchStatus("*", 0)
    tree.SetBranchStatus("mdt_chamber_n",           1)
    tree.SetBranchStatus("mdt_chamber_type",        1)
    tree.SetBranchStatus("mdt_chamber_eta_station", 1)
    tree.SetBranchStatus("mdt_chamber_side",        1)
    tree.SetBranchStatus("mdt_chamber_phi_sector",  1)
    tree.SetBranchStatus("mdt_chamber_tube_n",      1)
    tree.SetBranchStatus("mdt_chamber_tube_id",     1)

    counts = {}
    counts["total"] = 0

    start_time = time.time()

    entries = 25000

    for ient in xrange(entries):

        _ = tree.GetEntry(ient)
        counts["total"] += 1

        if ient and not ient % 500:
            progress(start_time, ient, entries)

        for ich in xrange(tree.mdt_chamber_n):

            chamber = "%s%i%s%02i" % (tree.mdt_chamber_type[ich],
                                      tree.mdt_chamber_eta_station[ich],
                                      tree.mdt_chamber_side[ich],
                                      tree.mdt_chamber_phi_sector[ich])

            for itu in xrange(tree.mdt_chamber_tube_n[ich]):
                tube = "%s_%i" % (chamber, tree.mdt_chamber_tube_id[ich][itu])
                counts[tube] = counts[tube]+1 if tube in counts else 1

    return counts

def progress(start_time, ievent, nevents):
    time_diff = time.time() - start_time
    rate = float(ievent+1)/time_diff
    sys.stdout.write("\r > %6i / %6i events | %2i%% | %6.2f Hz | %6.1fm elapsed | %6.1fm remaining" % (ievent, 
                                                                                                       nevents, 
                                                                                                       100*float(ievent)/float(nevents), 
                                                                                                       rate, 
                                                                                                       time_diff/60, 
                                                                                                       (nevents-ievent)/(rate*60)))
    sys.stdout.flush()
            
def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

if __name__ == "__main__":
    main()
