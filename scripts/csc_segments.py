import copy
import math
import multiprocessing
import os
import sys
import time

import ROOT
import rootlogon
ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

outdir = "csc_segments"
if not os.path.isdir(outdir):
    os.makedirs(outdir)

files = filter(lambda line: line and not line.startswith("#"), 
               [line.strip() for line in open("csc_segments.txt")])

def main():

    # farm histogramming
    configs = []
    for ijob, fi in enumerate(files):
        config = {}
        config["input"] = fi
        config["ijob"]  = "%02i" % (ijob)
        configs.append(config)

    if len(configs) > 1:
        npool = min(len(configs), multiprocessing.cpu_count())
        pool = multiprocessing.Pool(npool)
        results = pool.map(ntuple_to_hist, configs)
    else:
        results = [ntuple_to_hist(config)]

    hist = add_histograms(results)

    # divide
    for name in hist:
        if "segments_" in name:
            continue
        segments = name.replace("phiclust_", "segments_").replace("etaclust_", "segments_")
        hist[name].Divide(hist[name], hist[segments], 1.0, 1.0, "")

    # pretty plots
    for name in sorted(hist):

        overlay = "overlaid" in name

        if overlay:
            ROOT.gStyle.SetPadRightMargin(0.20)
            ROOT.gStyle.SetPadLeftMargin(0.16)
        else:
            ROOT.gStyle.SetPadRightMargin(0.15)
            ROOT.gStyle.SetPadLeftMargin(0.10)
            hist[name].GetYaxis().SetTitleOffset(0.9)
            hist[name].GetZaxis().SetTitleOffset(0.9)

        canv = ROOT.TCanvas(name, name, 800 if overlay else 1600, 800)
        canv.Draw()
        hist[name].Draw("colz,same")
        hist[name].GetXaxis().SetNdivisions(505)

        if overlay:
            text = "L" if "CSL" in name else "S"
            this = ROOT.TLatex(0, 220, text)
            this.SetTextAlign(22)
            this.SetTextSize(0.04)
            this.Draw()
        else:
            latex = []
            sectors = [1, 3, 5, 7, 9, 11, 13, 15] if "CSL" in name else [2, 4, 6, 8, 10, 12, 14, 16]
            for sector in sectors:
                text = "%s%02i" % ("L" if "CSL" in name else "S", sector)
                this = ROOT.TLatex(center(sector), 220, text)
                this.SetTextAlign(22)
                this.SetTextSize(0.04)
                this.Draw()
                latex.append(this)

        canv.SaveAs(os.path.join(outdir, canv.GetName()+".pdf"))

def ntuple_to_hist(config):

    ijob = config["ijob"]

    tree = ROOT.TChain("physics")
    tree.Add(config["input"])

    hist = {}

    title_all = "; segment #it{#phi} ; segment #it{r} [cm] ; Segments"
    title_phi = "; segment #it{#phi} ; segment #it{r} [cm] ; < #phi-clusters on segment >"
    title_eta = "; segment #it{#phi} ; segment #it{r} [cm] ; < #eta-clusters on segment >"

    hist["segments_CSL_overlaid"] = ROOT.TH2F("segments_CSL_overlaid_%s" % (ijob), title_all, 60, -0.48, 0.48, 60, 70, 250)
    hist["segments_CSS_overlaid"] = ROOT.TH2F("segments_CSS_overlaid_%s" % (ijob), title_all, 60, -0.48, 0.48, 60, 70, 250)
    
    hist["phiclust_CSL_overlaid"] = ROOT.TH2F("phiclust_CSL_overlaid_%s" % (ijob), title_phi, 60, -0.48, 0.48, 60, 70, 250)
    hist["phiclust_CSS_overlaid"] = ROOT.TH2F("phiclust_CSS_overlaid_%s" % (ijob), title_phi, 60, -0.48, 0.48, 60, 70, 250)
    
    hist["etaclust_CSL_overlaid"] = ROOT.TH2F("etaclust_CSL_overlaid_%s" % (ijob), title_eta, 60, -0.48, 0.48, 60, 70, 250)
    hist["etaclust_CSS_overlaid"] = ROOT.TH2F("etaclust_CSS_overlaid_%s" % (ijob), title_eta, 60, -0.48, 0.48, 60, 70, 250)
        
    for side in ["A", "C"]:
        hist["segments_CSL_separate_%s" % side] = ROOT.TH2F("segments_CSL_separate_%s_%s" % (side, ijob), title_all, 120, -3.6, 3.6,  60, 70, 250)
        hist["segments_CSS_separate_%s" % side] = ROOT.TH2F("segments_CSS_separate_%s_%s" % (side, ijob), title_all, 120, -3.6, 3.6,  60, 70, 250)

        hist["phiclust_CSL_separate_%s" % side] = ROOT.TH2F("phiclust_CSL_separate_%s_%s" % (side, ijob), title_phi, 120, -3.6, 3.6,  60, 70, 250)
        hist["phiclust_CSS_separate_%s" % side] = ROOT.TH2F("phiclust_CSS_separate_%s_%s" % (side, ijob), title_phi, 120, -3.6, 3.6,  60, 70, 250)

        hist["etaclust_CSL_separate_%s" % side] = ROOT.TH2F("etaclust_CSL_separate_%s_%s" % (side, ijob), title_eta, 120, -3.6, 3.6,  60, 70, 250)
        hist["etaclust_CSS_separate_%s" % side] = ROOT.TH2F("etaclust_CSS_separate_%s_%s" % (side, ijob), title_eta, 120, -3.6, 3.6,  60, 70, 250)

    for hi in hist.values():
        hi.Sumw2()
        ROOT.SetOwnership(hi, False)

    events     = tree.GetEntries()
    start_time = time.time()

    for event in xrange(events):

        _ = tree.GetEntry(event)
        if event > 0 and event % 500 == 0:
            progress(start_time, event, events)
        
        for iseg in xrange(tree.csc_segment_n):

            r    = tree.csc_segment_r[iseg] / 10.0
            phi  = tree.csc_segment_phi[iseg]
            type = tree.csc_segment_type[iseg]
            side = tree.csc_segment_side[iseg]
            sect = tree.csc_segment_phi_sector[iseg]
            nphi = tree.csc_segment_nphiclusters[iseg]
            neta = tree.csc_segment_netaclusters[iseg]

            phi_rotated = rotate(phi, sect, type)

            hist["segments_%s_overlaid" % (type)].Fill(phi_rotated, r)
            hist["phiclust_%s_overlaid" % (type)].Fill(phi_rotated, r, nphi)
            hist["etaclust_%s_overlaid" % (type)].Fill(phi_rotated, r, neta)

            hist["segments_%s_separate_%s" % (type, side)].Fill(phi, r)
            hist["phiclust_%s_separate_%s" % (type, side)].Fill(phi, r, nphi)
            hist["etaclust_%s_separate_%s" % (type, side)].Fill(phi, r, neta)

    print
    return hist

def add_histograms(results):

    output = {}
    for result in results:
        for key in result:
            if key in output:
                output[key].Add(result[key])
            else:
                output[key] = copy.copy(result[key])
                output[key].SetName(key)
    return output
                
def rotate(phi, sector, type):
    
    deg_to_rad = math.pi / 180
    rad_to_deg = 180 / math.pi

    if type == "CSL":
        if phi > ( 3.5 * 45 * deg_to_rad): return phi - (4.0 * 45 * deg_to_rad)
        if phi > ( 2.5 * 45 * deg_to_rad): return phi - (3.0 * 45 * deg_to_rad)
        if phi > ( 1.5 * 45 * deg_to_rad): return phi - (2.0 * 45 * deg_to_rad)
        if phi > ( 0.5 * 45 * deg_to_rad): return phi - (1.0 * 45 * deg_to_rad)
        if phi > (-0.5 * 45 * deg_to_rad): return phi - (0.0 * 45 * deg_to_rad)
        if phi > (-1.5 * 45 * deg_to_rad): return phi + (1.0 * 45 * deg_to_rad)
        if phi > (-2.5 * 45 * deg_to_rad): return phi + (2.0 * 45 * deg_to_rad)
        if phi > (-3.5 * 45 * deg_to_rad): return phi + (3.0 * 45 * deg_to_rad)
        if phi > (-4.5 * 45 * deg_to_rad): return phi + (4.0 * 45 * deg_to_rad)

    if type == "CSS":
        if phi > ( 3.0 * 45 * deg_to_rad): return phi - (3.5 * 45 * deg_to_rad)
        if phi > ( 2.0 * 45 * deg_to_rad): return phi - (2.5 * 45 * deg_to_rad)
        if phi > ( 1.0 * 45 * deg_to_rad): return phi - (1.5 * 45 * deg_to_rad)
        if phi > ( 0.0 * 45 * deg_to_rad): return phi - (0.5 * 45 * deg_to_rad)
        if phi > (-1.0 * 45 * deg_to_rad): return phi + (0.5 * 45 * deg_to_rad)
        if phi > (-2.0 * 45 * deg_to_rad): return phi + (1.5 * 45 * deg_to_rad)
        if phi > (-3.0 * 45 * deg_to_rad): return phi + (2.5 * 45 * deg_to_rad)
        if phi > (-4.0 * 45 * deg_to_rad): return phi + (3.5 * 45 * deg_to_rad)
        
    fatal("What the fuck is this? %s %s %s" % (phi, sector, type))

def center(sector):
    deg_to_rad = math.pi / 180
    if sector ==  1: return  0 * 45 * deg_to_rad
    if sector ==  3: return  1 * 45 * deg_to_rad
    if sector ==  5: return  2 * 45 * deg_to_rad
    if sector ==  7: return  3 * 45 * deg_to_rad
    if sector ==  9: return  4 * 45 * deg_to_rad
    if sector == 11: return -3 * 45 * deg_to_rad
    if sector == 13: return -2 * 45 * deg_to_rad
    if sector == 15: return -1 * 45 * deg_to_rad

    if sector ==  2: return  0 * 45 * deg_to_rad + 22.5 * deg_to_rad
    if sector ==  4: return  1 * 45 * deg_to_rad + 22.5 * deg_to_rad
    if sector ==  6: return  2 * 45 * deg_to_rad + 22.5 * deg_to_rad
    if sector ==  8: return  3 * 45 * deg_to_rad + 22.5 * deg_to_rad
    if sector == 10: return -4 * 45 * deg_to_rad + 22.5 * deg_to_rad
    if sector == 12: return -3 * 45 * deg_to_rad + 22.5 * deg_to_rad
    if sector == 14: return -2 * 45 * deg_to_rad + 22.5 * deg_to_rad
    if sector == 16: return -1 * 45 * deg_to_rad + 22.5 * deg_to_rad

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


if __name__ == "__main__":
    main()


