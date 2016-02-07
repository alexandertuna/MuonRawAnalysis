import argparse
import glob
import os
import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

ROOT.gStyle.SetPadTopMargin(0.06)
ROOT.gStyle.SetPadBottomMargin(0.15)
ROOT.gStyle.SetPadLeftMargin(0.18)
ROOT.gStyle.SetPadRightMargin(0.16)

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  help="glob-able input files")
    return parser.parse_args()

def main():

    ops = options()
    if not ops.input: fatal("Please give --input files")

    ch = ROOT.TChain("physics")
    for inp in glob.glob(os.path.abspath(ops.input)):
        ch.Add(inp)
        
    colz()

    left_vs_right_lo = ROOT.TH2F("left_vs_right_lo", ";q(left);q(right);"                  , 400,  -120,  280, 400,  -120,  280)
    left_vs_right_hi = ROOT.TH2F("left_vs_right_hi", ";q(left);q(right);"                  , 400,  -600, 3400, 400,  -600, 3400)
    minlr_vs_max_lo  = ROOT.TH2F("minlr_vs_max_lo", ";minimum of q(left), q(right);q(max);", 400,   -40,  120, 400, 0,  400)
    minlr_vs_max_hi  = ROOT.TH2F("minlr_vs_max_hi", ";minimum of q(left), q(right);q(max);", 400,  -600, 3000, 400, 0, 3600)

    ytitle   = "N(strips)"
    xtitle_r = "r [mm]"
    xtitle_l = "inst. lumi. [e^{33} cm^{-2} s^{-1} ]"
    xbins    = 30

    r_vs_strips = ROOT.TH2F("r_vs_strips", ";%s;%s;" % (xtitle_r, ytitle), 100,  800, 2200, 3*xbins, 0.5, xbins+0.5)
    l_vs_strips = ROOT.TH2F("l_vs_strips", ";%s;%s;" % (xtitle_l, ytitle), 100,  3.0,  5.5, 3*xbins, 0.5, xbins+0.5)
    
    h2s = [minlr_vs_max_lo, 
           minlr_vs_max_hi,
           left_vs_right_lo, 
           left_vs_right_hi,
           r_vs_strips,
           l_vs_strips,
           ]

    ch.Draw("csc_chamber_cluster_qright/1000:csc_chamber_cluster_qleft/1000 >> left_vs_right_lo", "", "goff")
    ch.Draw("csc_chamber_cluster_qright/1000:csc_chamber_cluster_qleft/1000 >> left_vs_right_hi", "", "goff")

    ch.Draw("csc_chamber_cluster_qmax/1000:min(csc_chamber_cluster_qleft, csc_chamber_cluster_qright)/1000 >> minlr_vs_max_lo", "", "goff")
    ch.Draw("csc_chamber_cluster_qmax/1000:min(csc_chamber_cluster_qleft, csc_chamber_cluster_qright)/1000 >> minlr_vs_max_hi", "", "goff")

    ch.Draw("csc_chamber_cluster_strips:csc_chamber_cluster_r      >> r_vs_strips", "", "goff")
    ch.Draw("csc_chamber_cluster_strips:lbAverageLuminosity/1000.0 >> l_vs_strips", "", "goff")

    for h2 in h2s:

        style(h2)

        name = "csc_q_"+h2.GetName()
        canvas = ROOT.TCanvas(name, name, 800, 800)
        canvas.Draw()
        h2.Draw("colzsame")

        canvas.SaveAs("output/"+canvas.GetName()+".pdf")
        
def fatal(message):
    import sys
    sys.exit("Error in %s: %s" % (__file__, message))

def style(hist, ndiv=505):
    ops = options()
    hist.SetStats(0)
    hist.SetMinimum(0)
    # hist.SetMaximum()
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetZaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.8)

def colz():
    import array
    ncontours = 200
    stops = array.array("d", [0.0, 0.5, 1.0])
    red   = array.array("d", [1.0, 1.0, 0.0][::-1])
    green = array.array("d", [1.0, 0.0, 0.0][::-1])
    blue  = array.array("d", [0.0, 0.0, 0.0][::-1])

    ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, ncontours)
    ROOT.gStyle.SetNumberContours(ncontours)


if __name__ == "__main__":
    main()

