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
ROOT.gStyle.SetPadRightMargin(0.20)

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

    left_vs_right_lo = ROOT.TH2F("left_vs_right_lo", ";q(left);q(right);"                  , 200,  -120,  280, 200,  -120,  280)
    left_vs_right_hi = ROOT.TH2F("left_vs_right_hi", ";q(left);q(right);"                  , 200,  -600, 3400, 200,  -600, 3400)
    minlr_vs_max_lo  = ROOT.TH2F("minlr_vs_max_lo", ";minimum of q(left), q(right);q(max);", 200,   -40,  120, 200, 0,  400)
    minlr_vs_max_hi  = ROOT.TH2F("minlr_vs_max_hi", ";minimum of q(left), q(right);q(max);", 200,  -600, 3000, 200, 0, 3600)

    xtitle_r = "r [mm]"
    xtitle_l = "inst. lumi. [e^{33} cm^{-2} s^{-1} ]"
    ytitle   = "N(strips)"
    ybins_lo = 30
    ybins_hi = 120

    r_vs_strips_lo = ROOT.TH2F("r_vs_strips_lo", ";%s;%s;" % (xtitle_r, ytitle), 100,  800, 2200, ybins_lo, 0.5, ybins_lo+0.5)
    r_vs_strips_hi = ROOT.TH2F("r_vs_strips_hi", ";%s;%s;" % (xtitle_r, ytitle), 100,  800, 2200, ybins_hi, 0.5, ybins_hi+0.5)
    l_vs_strips_lo = ROOT.TH2F("l_vs_strips_lo", ";%s;%s;" % (xtitle_l, ytitle), 100,  3.0,  5.5, ybins_lo, 0.5, ybins_lo+0.5)
    l_vs_strips_hi = ROOT.TH2F("l_vs_strips_hi", ";%s;%s;" % (xtitle_l, ytitle), 100,  3.0,  5.5, ybins_hi, 0.5, ybins_hi+0.5)
    
    h2s = [minlr_vs_max_lo, 
           minlr_vs_max_hi,
           left_vs_right_lo, 
           left_vs_right_hi,
           r_vs_strips_lo,
           r_vs_strips_hi,
           l_vs_strips_lo,
           l_vs_strips_hi,
           ]

    ch.Draw("csc_chamber_cluster_qright/1000:csc_chamber_cluster_qleft/1000 >> left_vs_right_lo", "prescale_HLT", "goff")
    ch.Draw("csc_chamber_cluster_qright/1000:csc_chamber_cluster_qleft/1000 >> left_vs_right_hi", "prescale_HLT", "goff")

    ch.Draw("csc_chamber_cluster_qmax/1000:min(csc_chamber_cluster_qleft, csc_chamber_cluster_qright)/1000 >> minlr_vs_max_lo", "prescale_HLT", "goff")
    ch.Draw("csc_chamber_cluster_qmax/1000:min(csc_chamber_cluster_qleft, csc_chamber_cluster_qright)/1000 >> minlr_vs_max_hi", "prescale_HLT", "goff")

    ch.Draw("csc_chamber_cluster_strips:csc_chamber_cluster_r      >> r_vs_strips_lo", "prescale_HLT", "goff")
    ch.Draw("csc_chamber_cluster_strips:csc_chamber_cluster_r      >> r_vs_strips_hi", "prescale_HLT", "goff")
    ch.Draw("csc_chamber_cluster_strips:lbAverageLuminosity/1000.0 >> l_vs_strips_lo", "prescale_HLT", "goff")
    ch.Draw("csc_chamber_cluster_strips:lbAverageLuminosity/1000.0 >> l_vs_strips_hi", "prescale_HLT", "goff")

    for h2 in h2s:

        ROOT.TH1.StatOverflows(ROOT.kTRUE)
        integral = h2.Integral(0, h2.GetNbinsX()+1, 0, h2.GetNbinsY()+1)
        h2.Scale(1/integral)

        style(h2)
        
        name = "csc_q_"+h2.GetName()
        canvas = ROOT.TCanvas(name, name, 800, 800)
        canvas.Draw()
        h2.Draw("colzsame")

        if "strips_lo" in h2.GetName():
            profile = h2.ProfileX(h2.GetName()+"pfx", 1, -1, "")
            profile.SetLineColor(ROOT.kGreen)
            profile.SetMarkerColor(ROOT.kGreen)
            profile.SetMarkerStyle(20)
            profile.SetMarkerSize(0.7)
            profile.Draw("pesame")

        ROOT.gPad.RedrawAxis()
        ROOT.gPad.SetLogz(1 if "_hi" in h2.GetName() else 0)
        canvas.SaveAs("output/"+canvas.GetName()+".pdf")
        
def fatal(message):
    import sys
    sys.exit("Error in %s: %s" % (__file__, message))

def style(hist, ndiv=505):
    ops = options()
    hist.SetStats(0)
    hist.SetMinimum(0 if not "_hi" in hist.GetName() else 2e-7)
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

