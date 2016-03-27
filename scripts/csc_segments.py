import copy
import math
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

filepaths = ["/Users/alexandertuna/Downloads/ntuple.2016-03-25-11h54m08s.Run00284285_1.root",
             "/Users/alexandertuna/Downloads/ntuple.2016-03-25-11h54m19s.Run00284285_2.root",
             ]

tree = ROOT.TChain("physics")
for path in filepaths:
    tree.Add(path)

def main(overlay_sectors):
    
    if overlay_sectors:
        ROOT.gStyle.SetPadRightMargin(0.20)
    else:
        ROOT.gStyle.SetPadRightMargin(0.15)
        ROOT.gStyle.SetPadLeftMargin(0.10)
    
    hist = {}

    title_all = "; segment #it{#phi} ; segment #it{r} [cm] ; Segments"
    title_phi = "; segment #it{#phi} ; segment #it{r} [cm] ; < #phi-clusters on segment >"
    title_eta = "; segment #it{#phi} ; segment #it{r} [cm] ; < #eta-clusters on segment >"

    if overlay_sectors:
        hist["segments_CSL"] = ROOT.TH2F("segments_CSL", title_all, 60, -0.48, 0.48, 60, 70, 250)
        hist["segments_CSS"] = ROOT.TH2F("segments_CSS", title_all, 60, -0.48, 0.48, 60, 70, 250)

        hist["phiclust_CSL"] = ROOT.TH2F("phiclust_CSL", title_phi, 60, -0.48, 0.48, 60, 70, 250)
        hist["phiclust_CSS"] = ROOT.TH2F("phiclust_CSS", title_phi, 60, -0.48, 0.48, 60, 70, 250)

        hist["etaclust_CSL"] = ROOT.TH2F("etaclust_CSL", title_eta, 60, -0.48, 0.48, 60, 70, 250)
        hist["etaclust_CSS"] = ROOT.TH2F("etaclust_CSS", title_eta, 60, -0.48, 0.48, 60, 70, 250)

    else:
        hist["segments_CSL"] = ROOT.TH2F("segments_CSL", title_all, 120, -3.6, 3.6,  60, 70, 250)
        hist["segments_CSS"] = ROOT.TH2F("segments_CSS", title_all, 120, -3.6, 3.6,  60, 70, 250)

        hist["phiclust_CSL"] = ROOT.TH2F("phiclust_CSL", title_phi, 120, -3.6, 3.6,  60, 70, 250)
        hist["phiclust_CSS"] = ROOT.TH2F("phiclust_CSS", title_phi, 120, -3.6, 3.6,  60, 70, 250)

        hist["etaclust_CSL"] = ROOT.TH2F("etaclust_CSL", title_eta, 120, -3.6, 3.6,  60, 70, 250)
        hist["etaclust_CSS"] = ROOT.TH2F("etaclust_CSS", title_eta, 120, -3.6, 3.6,  60, 70, 250)

        for hi in hist.values():
            hi.GetYaxis().SetTitleOffset(0.9)
            hi.GetZaxis().SetTitleOffset(0.9)

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
            sect = tree.csc_segment_phi_sector[iseg]
            nphi = tree.csc_segment_nphiclusters[iseg]
            neta = tree.csc_segment_netaclusters[iseg]

            phi = rotate(phi, sect, type) if overlay_sectors else phi

            hist["segments_%s" % (type)].Fill(phi, r)
            hist["phiclust_%s" % (type)].Fill(phi, r, nphi)
            hist["etaclust_%s" % (type)].Fill(phi, r, neta)

    print
    print

    for cluster in ["phiclust", "etaclust"]:
        for region in ["_CSL", "_CSS"]:
            hist[cluster+region].Divide(hist[cluster+region], hist["segments"+region], 1.0, 1.0, "")

    for name in ["segments_CSL", "segments_CSS",
                 "phiclust_CSL", "phiclust_CSS",
                 "etaclust_CSL", "etaclust_CSS",
                 ]:
        canv = ROOT.TCanvas(name, name, 800 if overlay_sectors else 1600, 800)
        canv.Draw()
        hist[name].Draw("colz,same")
        hist[name].GetXaxis().SetNdivisions(505)

        if overlay_sectors:
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
    main(overlay_sectors=True)


