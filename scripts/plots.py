"""
plots.py: script to make plots from MuonRawHits histograms. 

Run outside athena.

> python plots.py 
"""

import argparse
import copy
import glob
import multiprocessing as mp
import os
import sys
import time
import warnings
warnings.filterwarnings(action="ignore", category=RuntimeWarning)

import ROOT
import rootlogon
ROOT.gROOT.SetBatch(True)

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",  help="Output directory for plots.")
    return parser.parse_args()

def main():
    
    runs = [
        278880,
        279169,
        # 279345,
        # 279685,
        280464,
        # 280673,
        # 280862,
        # 281074,
        281143,
        # 281381,
        # 281385,
        # 281411,
        282992,
        # 283429,
        # 283780,
        # 284213,
        284285,
        ]
    
#    for perbc in [True, False]:
#        plots_vs_lumi(runs, perbc)

    plots_vs_r(runs)
    plots_vs_bcid(runs)

def plots_vs_lumi(runs, perbc):

    graphical = True

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)

    colz()

    fits              = True
    suppress_bullshit = True
    design_bunches    = 2808.0

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    graphs = {}
    funcs  = {}
    template = "%s_vs_lumi_orbit_%s"
    if perbc:
        template = template.replace("_lumi_orbit_", "_lumi_bunch_")

    rangex = (0.2, 4.8) if not perbc else (1.2, 2.7)
    rangex = (2.0, 4.8) if not perbc else (1.2, 2.7)
    ndiv = 505

    for region in ["mdt_all",
                   "mdt_EIL1",
                   "mdt_EIS1",
                   #"mdt_EIL2",
                   #"mdt_EIS2",
                   #"mdt_EIL3",
                   #"mdt_EIS3",
                   "csc_all",
                   "csc_L",
                   "csc_S",
                   ]:

        # for 2D plots
        ROOT.gStyle.SetPadRightMargin(0.18)

        for run in runs:

            name = template % (region, run)

            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()

            hists[name] = input.Get(name)
            if not hists[name]:
                continue
            yaxis = hists[name].GetYaxis()
            yaxis.SetTitle(ytitle(region))
            # hists[name].Rebin2D(2, 2)
            hists[name].GetXaxis().SetRangeUser(*rangex)
            hists[name].GetXaxis().SetNdivisions(ndiv)
            hists[name].Draw("same,colz")

            pfx = name+"_pfx"
            hists[pfx] = hists[name].ProfileX(pfx, 1, -1, "")
            if suppress_bullshit:
                kill_weird_bins(hists[pfx])
            hists[pfx].GetYaxis().SetTitle("< %s >" % (ytitle(region)))
            hists[pfx].SetLineColor(ROOT.kBlack)
            hists[pfx].SetLineWidth(3)
            hists[pfx].GetXaxis().SetRangeUser(*rangex)
            hists[pfx].GetXaxis().SetNdivisions(ndiv)
            graphs[pfx] = ROOT.TGraph(hists[pfx])
            
            if graphical:
                graphs[pfx].SetMarkerColor(color(run))
                graphs[pfx].SetLineColor(color(run))
                graphs[pfx].SetMarkerStyle(20)
                graphs[pfx].SetMarkerSize(0.8)
                graphs[pfx].SetLineWidth(2)
                graphs[pfx].Draw("Asame")
            else:
                hists[pfx].Draw("histe,same")

            draw_logos(0.36, 0.86, run)
            ROOT.gPad.RedrawAxis()
            # canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

        # for 1D plots
        ROOT.gStyle.SetPadRightMargin(0.06)

        name = template % (region, "overlay")
        canvas = ROOT.TCanvas(name, name, 800, 800)
        canvas.Draw()

        multi = ROOT.TMultiGraph()

        xleg, yleg = 0.175, 0.86
        legend = ROOT.TLegend(xleg, yleg-(0.035*len(runs)), xleg+0.2, yleg)

        for run in runs:
            name = (template % (region, run)) + "_pfx"
            hists[name].GetXaxis().SetRangeUser(*rangex)
            hists[name].GetXaxis().SetNdivisions(ndiv)
            hists[name].SetMinimum(ymin(region))
            hists[name].SetMaximum(ymax(region))
            hists[name].SetLineColor(color(run))
            # hists[name].SetLineColor(0)

            if graphical:
                graphs[name].SetTitle(";%s;%s" % (hists[name].GetXaxis().GetTitle(),
                                                  hists[name].GetYaxis().GetTitle(),
                                                  ))
                multi.Add(graphs[name], "PZ")
            else:
                hists[name].Draw("histe,same")

            if fits:
                x1 = hists[name].GetBinCenter(hists[name].FindFirstBinAbove()-1)
                x2 = hists[name].GetBinCenter(hists[name].FindLastBinAbove()+1)
                y1 = hists[name].GetBinContent(hists[name].FindFirstBinAbove())
                y2 = hists[name].GetBinContent(hists[name].FindLastBinAbove())
                funcs[name] = ROOT.TF1("fit"+name,"[0]*(x) + [1]", x1, x2)

                m = (y2-y1)/(x2-x1)
                funcs[name].SetParameter(0, m)
                funcs[name].SetParameter(1, y1 - m*x1)

                funcs[name].SetLineColor(color(run))
                funcs[name].SetLineWidth(2)
                funcs[name].SetLineStyle(7)
                hists[name].Fit(funcs[name], "RWQN")
                print " [ fit ] %s: %7.2f (%5.2f), %7.2f (%5.2f) %7.2f" % (
                    run,
                    funcs[name].GetParameter(0), funcs[name].GetParError(0),
                    funcs[name].GetParameter(1), funcs[name].GetParError(1),
                    funcs[name].GetChisquare(),
                    )
                slope  = funcs[name].GetParameter(0)
                offset = funcs[name].GetParameter(1)
                chi2   = funcs[name].GetChisquare()
                funcs[name].Draw("same")

            capt = caption(run) if not fits else "%s (%.1f, %.1f)" % (caption(run), slope, offset)
                
            entry = legend.AddEntry(hists[name], capt, "")
            entry.SetTextColor(color(run))

        if graphical:
            multi.SetTitle(";%s;%s" % (multi.GetListOfGraphs()[0].GetXaxis().GetTitle(),
                                       multi.GetListOfGraphs()[0].GetYaxis().GetTitle(),
                                       ))
            multi.SetMinimum(0.00)
            multi.SetMaximum(ymax(region))
            multi.Draw("Asame")
            multi.GetXaxis().SetRangeUser(*rangex)
            multi.Draw("Asame")
            for run in runs:
                name = (template % (region, run)) + "_pfx"
                funcs[name].SetLineStyle(1)
                funcs[name].Draw("same")
            
        draw_logos(0.36, 0.89)

        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetMargin(0.3)
        legend.SetTextSize(0.03)
        legend.Draw()

        ROOT.gPad.RedrawAxis()
        canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))


def plots_vs_r(runs):

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)
    
    ROOT.gStyle.SetPadRightMargin(0.06)

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    funcs  = {}
    rebin  = 1

    livetime_csc = 140e-9
    livetime_mdt = 1300e-9
    boundary     = 2050 # mm

    # area vs r
    input_area = ROOT.TFile.Open("area.root")
    area_L = input_area.Get("endcap_L_area")
    area_S = input_area.Get("endcap_S_area")

    for hist in [area_L, area_S]:
        hist.Rebin(rebin)
        style_vs_r(hist)
        draw_vs_r(hist, ops.output)

    # hits vs r
    for run in runs:

        name = "entries_%s" % (run)
        entries = input.Get(name).GetBinContent(1)

        for sector in ["L", "S"]:

            name = "endcap_%s_hits_%s" % (sector, run)
            hists[name] = input.Get(name)
            hists[name].Rebin(rebin)
            style_vs_r(hists[name])
            for bin in xrange(0, hists[name].GetNbinsX()+1):
                hists[name].SetBinError(bin, 0)
            draw_vs_r(hists[name], ops.output)

            numer = copy.copy(hists["endcap_%s_hits_%s" % (sector, run)])
            denom = copy.copy(area_L if sector=="L" else area_S)

            for bin in xrange(0, denom.GetNbinsX()+1):
                radius   = denom.GetBinCenter(bin)
                area     = denom.GetBinContent(bin)
                livetime = livetime_csc if radius < boundary else livetime_mdt
                denom.SetBinContent(bin, entries * area * livetime)

            name = numer.GetName().replace("_hits_", "_rate_")
            ratio = copy.copy(hists["endcap_%s_hits_%s" % (sector, run)])
            ratio.Reset()

            ratio.Divide(numer, denom)
            ratio.SetName(name)
            style_vs_r(ratio)
            ratio.GetYaxis().SetTitle(ratio.GetYaxis().GetTitle().replace("hits", "hit rate [ cm^{-2} s^{-1} ]"))
            ratio.SetMaximum(950)
            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()
            ratio.Draw("psame")

            exponential_csc = ROOT.TF1("fit_csc_"+name,"expo(0)",  950, 2000)
            exponential_mdt = ROOT.TF1("fit_mdt_"+name,"expo(0)", 2050, 4400)
            for expo in [exponential_csc,
                         exponential_mdt,
                         ]:
                expo.SetLineColor(ROOT.kBlack)
                expo.SetLineWidth(2)
                expo.SetLineStyle(7)
                ratio.Fit(expo, "RWQN")
                
                expo.Draw("same")

            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

def plots_vs_bcid(runs):

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)

    per_event = True

    ROOT.gStyle.SetPadLeftMargin(0.12)
    ROOT.gStyle.SetPadRightMargin(0.04)

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    funcs  = {}
    rebin  = 1

    # hits vs bcid
    for run in runs:

        entries         = input.Get("entries_%s" % (run)).GetBinContent(1)
        entries_vs_bcid = input.Get("entries_vs_bcid_%s" % (run))

        for det in ["mdt", "csc"]:

            name = "%s_all_vs_bcid_%s" % (det, run)
            hists[name] = input.Get(name)
            if per_event:
                hists[name].Divide(hists[name], entries_vs_bcid)
            style_vs_bcid(hists[name], per_event)

            canvas = ROOT.TCanvas(name, name, 1600, 500)
            canvas.Draw()
            hists[name].Draw("histsame")
            draw_logos(xcoord=0.35, ycoord=0.85, run=run, fit=False)
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

def style_vs_r(hist, ndiv=505):
    name = hist.GetName()
    hist.SetMarkerColor(ROOT.kAzure+1 if "L" in name else ROOT.kRed)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(0.9)
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetXaxis().SetRangeUser(700, 4700)

def draw_vs_r(hist, output, height=800, width=800, drawopt="psame", logos=False):
    name = hist.GetName()
    canvas = ROOT.TCanvas(name, name, width, height)
    canvas.Draw()
    hist.Draw(drawopt)
    if logos:
        draw_logos()
    canvas.SaveAs(os.path.join(output, canvas.GetName()+".pdf"))

def style_vs_bcid(hist, per_event, ndiv=505):
    name = hist.GetName()
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(0.9)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetLineStyle(1)
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetYaxis().SetTitleOffset(1.0)
    if per_event:
        hist.SetMaximum(4100)

def draw_logos(xcoord=0.5, ycoord=0.5, run=None, fit=True):

    atlas = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
    if run:
        runz  = ROOT.TLatex(xcoord, ycoord-0.06, "Run %s" % (run))
        bunch = ROOT.TLatex(xcoord, ycoord-0.12, "%s bunches" % (bunches(run)))
    fits = ROOT.TLatex(xcoord+0.25, ycoord, "(slope, offset)")

    logos = [atlas, runz, bunch] if run else [atlas, fits]

    for logo in logos:
        ROOT.SetOwnership(logo, False)
        logo.SetTextSize(0.040)
        if logo == fits:
            logo.SetTextSize(0.03)
        logo.SetTextFont(42)
        logo.SetTextAlign(22)
        logo.SetNDC()
        logo.Draw()

    return logos

def color(run):
    if run == 278880: return ROOT.kBlack
    if run == 279169: return ROOT.kGray
    if run == 279345: return ROOT.kGreen+3
    if run == 279685: return ROOT.kOrange+7
    if run == 280464: return ROOT.kBlack
    if run == 280614: return ROOT.kBlack
    if run == 280673: return ROOT.kRed
    if run == 280862: return 210
    if run == 281074: return ROOT.kBlue
    if run == 281143: return ROOT.kOrange+7
    if run == 281381: return ROOT.kViolet-5
    if run == 281385: return ROOT.kOrange-7
    if run == 281411: return ROOT.kOrange-3
    if run == 282992: return ROOT.kRed+3
    if run == 283429: return ROOT.kRed
    if run == 283780: return ROOT.kBlue
    if run == 284213: return ROOT.kBlack

def ymax(region):
    if region == "mdt_all":  return 5200
    if region == "mdt_EIL1": return  500
    if region == "mdt_EIL2": return  180
    if region == "mdt_EIL3": return  100
    if region == "mdt_EIS1": return  350
    if region == "mdt_EIS2": return   90
    if region == "mdt_EIS3": return  100
    if region == "csc_all":  return  100
    if region == "csc_L":    return   50
    if region == "csc_S":    return   50
    fatal("no ymax for %s" % (region))
    
def ymin(region):
    if region == "mdt_all":  return    0 # 1500
    if region == "mdt_EIL1": return    0 # 130
    if region == "mdt_EIL2": return   70
    if region == "mdt_EIL3": return   20
    if region == "mdt_EIS1": return    0 # 90
    if region == "mdt_EIS2": return   40
    if region == "mdt_EIS3": return   20
    if region == "csc_all":  return    0
    if region == "csc_L":    return    0
    if region == "csc_S":    return    0
    fatal("no ymin for %s" % (region))

def ytitle(region):
    # mdt_all
    detector, subset = region.split("_")
    detector = detector.upper()
    return "%s hits: %s" % (detector, subset)

def caption(run):
    return "%s, %s bunches" % (run, bunches(run))

def bunches(run):
    if run == 278880: return  447
    if run == 279169: return  733
    if run == 279345: return  877
    if run == 279598: return 1021
    if run == 279685: return 1021
    if run == 280231: return 1165
    if run == 280464: return 1309
    if run == 280614: return 1309
    if run == 280673: return 1453
    if run == 280862: return 1453
    if run == 281074: return 1596
    if run == 281143: return 1596
    if run == 281381: return 1813
    if run == 281385: return 1813
    if run == 281411: return 1813
    if run == 282992: return 1813
    if run == 283429: return 2029
    if run == 283780: return 2232
    if run == 284213: return 2232
    if run == 284285: return 2232

def kill_weird_bins(hist):
    for bin in xrange(1, hist.GetNbinsX()):
        if hist.GetBinContent(bin-1) == 0 and hist.GetBinContent(bin+1) == 0:
            hist.SetBinContent(bin, 0)
        if hist.GetBinContent(bin-2) == 0 and hist.GetBinContent(bin+1) == 0:
            hist.SetBinContent(bin, 0)
        if hist.GetBinContent(bin-1) == 0 and hist.GetBinContent(bin+2) == 0:
            hist.SetBinContent(bin, 0)

def colz():
    import array
    ncontours = 200
    stops = array.array("d", [0.0, 0.3, 0.6, 1.0])
    red   = array.array("d", [1.0, 1.0, 1.0, 0.0])
    green = array.array("d", [1.0, 1.0, 0.0, 0.0])
    blue  = array.array("d", [1.0, 0.0, 0.0, 0.0])
    
    ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, ncontours)
    ROOT.gStyle.SetNumberContours(ncontours)


if __name__ == "__main__":
    main()


