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
ROOT.gStyle.SetPadBottomMargin(0.12)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

livetime_csc = 140e-9
livetime_mdt = 1300e-9

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",  help="Output directory for plots.")
    parser.add_argument("--hits",    help="Type of hits to use: raw or adc")
    return parser.parse_args()

def main():

    ops = options()
    if not ops.output                : ops.output = "output"
    if not os.path.isdir(ops.output) : os.makedirs(ops.output)
    if not ops.hits in ["raw", "adc"]: fatal("Please give --hits as raw or adc")

    runs = [
        "00278880",
        "00279169",
        #"00279345",
        "00279685",
        "00280464",
        #"00280673",
        "00280862",
        #"00281074",
        "00281143",
        "00281411",
        "00282992",
        "00283429",
        #"00283780",
        "00284213",
        "00284285",
        ]

    # reorganize to deal with ROOT TLegend SetNColumns
    runs = ["00278880", "00281411",
            "00279169", "00282992",
            "00279685", "00283429",
            "00280464", "00284213",
            "00280862", "00284285",
            "00281143",
            ]
    
    # reorganize to deal with ROOT TLegend SetNColumns
#     runs = ["00279169", "00281411", 
#             "00279685", "00282992", 
#             "00280464", "00283429", 
#             "00280862", "00284213", 
#             "00281143", "00284285", 
#             ]

    runs = sorted(runs)
    
    for perbc in [False]:
#        plots_vs_lumi(runs, perbc, rate=True, extrapolate=False)
#        plots_vs_r(runs, layer="EI")
        plots_vs_r(runs, layer="EM")
#        plots_vs_region(runs, rate=True, logz=True)
#     plots_vs_bcid(runs)
#     plots_vs_lumi_vs_r(runs)

def plots_vs_lumi(runs, perbc, rate, extrapolate):

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)

    verbose = False
    colz()

    fits              = True
    draw_slope        = False
    suppress_bullshit = True
    ndiv              = 505

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    graphs = {}
    funcs  = {}
    template = "hits_%s_vs_lumi_vs_evts_%s_%s"
    if perbc:
        template = template.replace("lumi", "mu")

    if not perbc:
        if not extrapolate: rangex = (0.5, 5.4)
        else:               rangex = (0.5, 5.5)
    else:
        rangex = (8, 19)

    for region in ["mdt_full",
                   "mdt_EIL1",
                   "mdt_EIS1",
                   "mdt_EML1",
                   "mdt_EMS1",
                   "mdt_BIS8",
                   "csc_CSL1",
                   "csc_CSS1",
                   ]:

        # for 2D plots
        ROOT.gStyle.SetPadRightMargin(0.18)
        ROOT.gStyle.SetPadBottomMargin(0.12)

        for run in runs:

            name = template % (ops.hits, region, run)

            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()

            hists[name] = input.Get(os.path.join(run, name))
            if not hists[name]:
                fatal("Cannot retrieve %s" % (os.path.join(run, name)))
            yaxis = hists[name].GetYaxis()
            hists[name].GetXaxis().SetTitle(xtitle(name))
            hists[name].GetYaxis().SetTitle(ytitle(name))
            # hists[name].Rebin2D(2, 2)
            hists[name].GetXaxis().SetRangeUser(*rangex)
            hists[name].GetXaxis().SetNdivisions(ndiv)
            hists[name].Draw("same,colz")

            pfx = name+"_pfx"
            hists[pfx] = hists[name].ProfileX(pfx, 1, -1, "")
            if suppress_bullshit:
                kill_weird_bins(hists[pfx])
            if rate:
                livetime = livetime_csc if "csc" in region else livetime_mdt
                areas = chamber_area()
                area = -1
                if region == "mdt_full": area = sum([areas[cham] for cham in filter(lambda key: not "CS" in key, areas)])
                if region == "mdt_EIL1": area = sum([areas[cham] for cham in filter(lambda key:   "EIL1" in key, areas)])
                if region == "mdt_EIL2": area = sum([areas[cham] for cham in filter(lambda key:   "EIL2" in key, areas)])
                if region == "mdt_EIS1": area = sum([areas[cham] for cham in filter(lambda key:   "EIS1" in key, areas)])
                if region == "mdt_EIS2": area = sum([areas[cham] for cham in filter(lambda key:   "EIS2" in key, areas)])
                if region == "mdt_EML1": area = sum([areas[cham] for cham in filter(lambda key:   "EML1" in key, areas)])
                if region == "mdt_EML2": area = sum([areas[cham] for cham in filter(lambda key:   "EML2" in key, areas)])
                if region == "mdt_EMS1": area = sum([areas[cham] for cham in filter(lambda key:   "EMS1" in key, areas)])
                if region == "mdt_EMS2": area = sum([areas[cham] for cham in filter(lambda key:   "EMS2" in key, areas)])
                if region == "mdt_BIS7": area = sum([areas[cham] for cham in filter(lambda key:   "BIS7" in key, areas)])
                if region == "mdt_BIS8": area = sum([areas[cham] for cham in filter(lambda key:   "BIS8" in key, areas)])
                if region == "csc_CSL1": area = sum([areas[cham] for cham in filter(lambda key:   "CSL1" in key, areas)])
                if region == "csc_CSS1": area = sum([areas[cham] for cham in filter(lambda key:   "CSS1" in key, areas)])
                hists[pfx].Scale(1.0 / (livetime * area))
                
            hists[pfx].SetLineColor(ROOT.kBlack)
            hists[pfx].SetLineWidth(3)
            hists[pfx].GetXaxis().SetRangeUser(*rangex)
            hists[pfx].GetXaxis().SetNdivisions(ndiv)
            graphs[pfx] = ROOT.TGraph(hists[pfx])
            
            hists[pfx].Draw("pe,same")

            draw_logos(0.36, 0.86, run)
            ROOT.gPad.RedrawAxis()
            # canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

        # for 1D plots
        ROOT.gStyle.SetPadRightMargin(0.06)
        ROOT.gStyle.SetPadBottomMargin(0.12)

        name = template % (ops.hits, region, "overlay")
        canvas = ROOT.TCanvas(name, name, 800, 800)
        canvas.Draw()

        multi = ROOT.TMultiGraph()

        xleg, yleg = 0.180, 0.86
        ydelta = (0.035*len(runs)) if draw_slope else (0.02*len(runs))
        legend = ROOT.TLegend(xleg, yleg-ydelta, xleg+0.6, yleg)
        if not draw_slope:
            legend.SetNColumns(2)

        for run in runs:
            name = (template % (ops.hits, region, run)) + "_pfx"
            hists[name].GetXaxis().SetRangeUser(*rangex)
            hists[name].GetXaxis().SetNdivisions(ndiv)

            hists[name].GetXaxis().SetTitle(xtitle(name))
            hists[name].GetYaxis().SetTitle(ytitle(name if not rate else name.replace("hits_", "rate_")))

            hists[name].SetMinimum(ymin(region))
            hists[name].SetMaximum(ymax(region, rate, draw_slope))
            hists[name].SetLineColor(color(run))
            hists[name].SetMarkerColor(color(run))
            hists[name].SetMarkerStyle(20)
            hists[name].SetMarkerSize(0.8)

            hists[name].GetXaxis().SetTitleSize(0.05)
            hists[name].GetYaxis().SetTitleSize(0.05)
            hists[name].GetXaxis().SetLabelSize(0.05)
            hists[name].GetYaxis().SetLabelSize(0.05)

            hists[name].Draw("pe,same")

            if fits:
                x1 = hists[name].GetBinCenter(hists[name].FindFirstBinAbove()-1)
                x2 = hists[name].GetBinCenter(hists[name].FindLastBinAbove()+1)
                y1 = hists[name].GetBinContent(hists[name].FindFirstBinAbove())
                y2 = hists[name].GetBinContent(hists[name].FindLastBinAbove())
                if run == "00278880" and not perbc:
                    x1 = 0.8
                funcs[name] = ROOT.TF1("fit"+name,"[0]*(x) + [1]", 0.9*x1, 1.1*x2)

                m = (y2-y1)/(x2-x1)
                funcs[name].SetParameter(0, m)
                funcs[name].SetParameter(1, y1 - m*x1)

                funcs[name].SetLineColor(color(run))
                funcs[name].SetLineWidth(1)
                funcs[name].SetLineStyle(1)
                hists[name].Fit(funcs[name], "RWQN")
                if verbose:
                    print " [ fit ] %s: %7.2f (%5.2f), %7.2f (%5.2f) %7.2f" % (
                        run,
                        funcs[name].GetParameter(0), funcs[name].GetParError(0),
                        funcs[name].GetParameter(1), funcs[name].GetParError(1),
                        funcs[name].GetChisquare(),
                        )
                else:
                    print "%20s %10s %5s %10.5f %10.5f" % (name, run, bunches(run), funcs[name].GetParameter(0), funcs[name].GetParameter(1))
                slope  = funcs[name].GetParameter(0)
                offset = funcs[name].GetParameter(1)
                chi2   = funcs[name].GetChisquare()
                funcs[name].Draw("same")

            capt = caption(run) if (not draw_slope or not fits) else "%s (%.2f, %.2f)" % (caption(run), slope, offset)
                
            entry = legend.AddEntry(hists[name], capt, "")
            entry.SetTextColor(color(run))

        draw_logos(0.36, 0.89, fit=draw_slope)

        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetMargin(0.3)
        legend.SetTextSize(0.03)
        legend.Draw()

        if rate:
            canvas.SetName(canvas.GetName().replace("hits_", "rate_"))
        if rate and extrapolate:
            name = region+"extrap"
            funcs[name] = ROOT.TF1("fit"+name,"[0]*(x) + [1]", 3, 6)
            slope, offset = slope_offset(region)
            funcs[name].SetParameter(0, slope)
            funcs[name].SetParameter(1, offset)
            funcs[name].SetLineColor(ROOT.kBlack)
            funcs[name].SetLineWidth(1)
            funcs[name].SetLineStyle(7)
            funcs[name].Draw("same")

        ROOT.gPad.RedrawAxis()
        ROOT.gPad.Modified()
        ROOT.gPad.Update()
        canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))


def plots_vs_r(runs, layer):

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)
    if not layer in ["EI", "EM"]:
        fatal("Need layer to be EI or EM")
    
    ROOT.gStyle.SetPadRightMargin(0.06)

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    funcs  = {}
    rebin  = 4

    boundary = 2050 # mm

    # area vs r
    input_area = ROOT.TFile.Open("area.root")
    area_L = input_area.Get("area_vs_r_%sL" % layer)
    area_S = input_area.Get("area_vs_r_%sS" % layer)

    for hist in [area_L, area_S]:
        hist.Rebin(rebin)
        style_vs_r(hist, layer)
        draw_vs_r(hist, ops.output)

    sectors = [layer+"L",
               layer+"S", 
               ]

    # hits vs r
    for run in runs:

        name = "evts_%s" % (run)
        entries = input.Get(os.path.join(run, name)).GetBinContent(1)

        for sector in sectors:

            name = "hits_%s_vs_r_%s_%s" % (ops.hits, sector, run)
            hists[name] = input.Get(os.path.join(run, name))
            if not hists[name]:
                fatal("Could not retrieve %s" % (os.path.join(run, name)))
            hists[name].Rebin(rebin)
            style_vs_r(hists[name], layer)
            for bin in xrange(0, hists[name].GetNbinsX()+1):
                hists[name].SetBinError(bin, 0)
            # draw_vs_r(hists[name], ops.output)
            
            numer = copy.copy(hists[name])
            denom = copy.copy(area_L if "L" in sector else area_S)

            for bin in xrange(0, denom.GetNbinsX()+1):
                radius   = denom.GetBinCenter(bin)
                area     = denom.GetBinContent(bin)
                livetime = livetime_csc if (radius < boundary and layer=="EI") else livetime_mdt
                denom.SetBinContent(bin, entries * area * livetime)

            name = numer.GetName().replace("hits_", "rate_")
            hists[name] = copy.copy(numer)
            hists[name].Reset()
            hists[name].Divide(numer, denom)
            hists[name].SetName(name)

            style_vs_r(hists[name], layer)
            hists[name].GetYaxis().SetTitle(hists[name].GetYaxis().GetTitle().replace("hits", "hit rate [ cm^{-2} s^{-1} ]"))
            hists[name].SetMaximum(950 if layer=="EI" else 45)

            name = "rate_%s_vs_r_%s_%s" % (ops.hits, sector, run)
            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()
        
            hists[name].Draw("psame")
            
            if layer=="EI":
                exponential_csc = ROOT.TF1("fit_csc_"+name, "expo(0)",  950, 2000)
                exponential_mdt = ROOT.TF1("fit_mdt_"+name, "expo(0)", 2050, 4400)
                expos = [exponential_csc, exponential_mdt]
            if layer=="EM":
                edge = 3500 if "L" in sector else 3700
                xhi  = 5400 if "L" in sector else 5650
                exponential_em1 = ROOT.TF1("fit_em1_"+name, "expo(0)", 1750, edge-50)
                exponential_em2 = ROOT.TF1("fit_em2_"+name, "expo(0)", edge, xhi)
                expos = [exponential_em1, exponential_em2]

                #xlo = 1800
                #xhi = 5400 if "L" in sector else 5650
                #exponential_em = ROOT.TF1("fit_em_"+name, "expo(0)", xlo, xhi)
                #expos = [exponential_em]

            for expo in expos:
                expo.SetFillStyle(1001)
                expo.SetFillColor(18)
                expo.SetLineColor(ROOT.kBlack)
                expo.SetLineWidth(2)
                expo.SetLineStyle(1)
                hists[name].Fit(expo, "RWQN")
                expo.Draw("FCsame")

                line_lo = ROOT.TLine(expo.GetMaximumX(), 0, expo.GetMaximumX(), expo.GetMaximum())
                line_hi = ROOT.TLine(expo.GetMinimumX(), 0, expo.GetMinimumX(), expo.GetMinimum())
                for line in [line_lo, line_hi]:
                    ROOT.SetOwnership(line, False)
                    line.SetLineColor(ROOT.kBlack)
                    line.SetLineWidth(2)
                    line.SetLineStyle(1)
                    line.Draw()

            for expo in expos:
                # exp([0] + [1]*x)
                # parameter in meters [m]
                pass # print "%s: exp(%.3f + %.3f*x)" % (expo.GetName(), expo.GetParameter(0), expo.GetParameter(1)*1000)
            # print

            hists[name].Draw("psame")

            xleg, yleg = 0.60, 0.66
            ydelta = 0.1
            legend = ROOT.TLegend(xleg, yleg-ydelta, xleg+0.2, yleg)
            legend.AddEntry(hists[name], "%s sectors" % (sector), "p")
            legend.AddEntry(expo,        "expo. fits",            "f")
            legend.SetBorderSize(0)
            legend.SetFillColor(0)
            legend.SetMargin(0.3)
            legend.SetTextSize(0.045)
            legend.Draw()
            draw_logos(xcoord=0.55, ycoord=0.85, run=run, fit=False)

            if layer=="EI":
                boundary_line = ROOT.TLine(boundary, 300, boundary, 500)
                boundary_line.Draw()
                arrow_csc = ROOT.TArrow(boundary, 400, boundary-350, 400, 0.01, "|>")
                arrow_mdt = ROOT.TArrow(boundary, 350, boundary+350, 350, 0.01, "|>")
                for arrow in [arrow_csc, arrow_mdt]:
                    arrow.Draw()
                blurb_csc = ROOT.TLatex(boundary-280, 405, "CSC")
                blurb_mdt = ROOT.TLatex(boundary+050, 355, "MDT")
                for blurb in [blurb_csc, blurb_mdt]:
                    blurb.SetTextSize(0.025)
                    blurb.Draw()

            ROOT.gPad.RedrawAxis()
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))
            
def plots_vs_bcid(runs):

    ops = options()
    if not ops.output:
        ops.output = "output"
    if not os.path.isdir(ops.output): 
        os.makedirs(ops.output)

    per_event = True

    ROOT.gStyle.SetPadLeftMargin(0.08)
    ROOT.gStyle.SetPadRightMargin(0.04)

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    funcs  = {}
    rebin  = 1

    # hits vs bcid
    for run in runs:

        entries         = input.Get("%s/evts_%s"         % (run, run)).GetBinContent(1)
        entries_vs_bcid = input.Get("%s/evts_vs_bcid_%s" % (run, run))
        actlumi_vs_bcid = input.Get("%s/lumi_vs_bcid_%s" % (run, run))
        avglumi_vs_bcid = input.Get("%s/lumi_vs_bcid_%s" % (run, run))

        actlumi_vs_bcid.GetYaxis().SetTitle("< inst. lumi. > per BCID per event [ e^{30} ]")
        avglumi_vs_bcid.GetYaxis().SetTitle("< inst. lumi. > per event [ e^{33} ]")

        for hist in [actlumi_vs_bcid, 
                     ]:

            hist.Divide(hist, entries_vs_bcid)
            hist.GetXaxis().SetTitle("BCID")
            hist.SetTitle("")

            for bcid in xrange(3600):
                hist.SetBinError(bcid, 0)
            style_vs_bcid(hist, per_event, setmax=4)

            name = hist.GetName()
            canvas = ROOT.TCanvas(name, name, 1600, 500)
            canvas.Draw()
            hist.Draw("histsame")
            draw_logos(xcoord=0.35, ycoord=0.85, run=run, fit=False)
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

        for det in ["mdt_full", "csc_full"]:

            name = "hits_vs_bcid_%s_%s" % (det, run)
            hists[name] = input.Get(os.path.join(run, name))
            hists[name].GetYaxis().SetTitle("< hits in %s > per event" % (det.split("_")[0].upper()))
            if per_event:
                hists[name].Divide(hists[name], entries_vs_bcid)
            setmax=4300 if "mdt" in det else 60
            style_vs_bcid(hists[name], per_event, setmax=setmax)

            canvas = ROOT.TCanvas(name, name, 1600, 500)
            canvas.Draw()
            hists[name].Draw("histsame")
            draw_logos(xcoord=0.35, ycoord=0.85, run=run, fit=False)
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

def plots_vs_region(runs, rate=True, logz=False):

    colz()

    ops = options()
    if not ops.output:                ops.output = "output"
    if not os.path.isdir(ops.output): os.makedirs(ops.output)

    ROOT.gStyle.SetPadLeftMargin(0.12)
    ROOT.gStyle.SetPadRightMargin(0.20)

    input = ROOT.TFile.Open("histograms.root")
    hists = {}

    area = ROOT.TFile.Open("area.root")
    area_L = area.Get("area_vs_region_L")
    area_S = area.Get("area_vs_region_S")

    # hits vs region
    for sector in ["L", "S"]:
        
        for run in runs:

            name = "evts_%s" % (run)
            entries = input.Get(os.path.join(run, name)).GetBinContent(1)
            
            name = "hits_%s_vs_region_%s_%s" % (ops.hits, sector, run)
            hists[name] = input.Get(os.path.join(run, name))
            
            hists[name].GetXaxis().SetTitle("#eta station")
            hists[name].GetZaxis().SetTitle("hits")
            style_vs_region(hists[name], rate)

            # turn off BOL7 right now because they arent actually BOL7
            for binx in xrange(hists[name].GetNbinsX()+1):
                if abs(hists[name].GetXaxis().GetBinCenter(binx)) != 7:
                    continue
                for biny in xrange(hists[name].GetNbinsX()+1):
                    if hists[name].GetYaxis().GetBinLabel(biny) == "BOL":
                        hists[name].SetBinContent(binx, biny, 0.0)
                        hists[name].SetBinError(  binx, biny, 0.0)

            if rate:
                numer = copy.copy(hists[name])
                denom = copy.copy(area_L if "L" in sector else area_S)

                biny_csc = 8
                for biny in xrange(denom.GetNbinsX()+1):
                    livetime = livetime_csc if biny == biny_csc else livetime_mdt
                    for binx in xrange(denom.GetNbinsX()+1):
                        denom.SetBinContent(binx, biny, entries * livetime * denom.GetBinContent(binx, biny))

                name = numer.GetName().replace("hits_", "rate_")
                hists[name] = copy.copy(numer)
                hists[name].Reset()
                hists[name].Divide(numer, denom)
                hists[name].SetName(name)
                hists[name].GetZaxis().SetTitle(ytitle(name))
                hists[name].SetMinimum(0.9)
                hists[name].SetMaximum(409)

            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()
            ROOT.gStyle.SetPaintTextFormat(".1f")
            hists[name].SetMarkerSize(1.2)
            hists[name].GetYaxis().SetTickLength(0.00)
            hists[name].Draw("histsame,colz")
            hists[name].Draw("histsame,text35")

            logo = ROOT.TLatex(0.15, 0.96, "ATLAS Internal        Run %s      13 TeV" % (int(run)))
            logo.SetTextSize(0.035)
            logo.SetTextFont(42)
            # logo.SetTextAlign(22)
            logo.SetNDC()
            logo.Draw()

            if logz: ROOT.gPad.SetLogz(1)
            
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))

            if logz: ROOT.gPad.SetLogz(0)

def plots_vs_lumi_vs_r(runs):

    ops = options()
    if not ops.output:                ops.output = "output"
    if not os.path.isdir(ops.output): os.makedirs(ops.output)
    
    colz()
    ROOT.gStyle.SetPadRightMargin(0.20)

    input = ROOT.TFile.Open("histograms.root")
    hists  = {}
    funcs  = {}
    rebin  = 4

    boundary = 2050 # mm

    # area vs r
    input_area = ROOT.TFile.Open("area.root")
    area_L = input_area.Get("area_vs_r_L")
    area_S = input_area.Get("area_vs_r_S")

    for hist in [area_L, area_S]:
        hist.Rebin(rebin)

    sectors = ["L", "S"]

    # hits vs r
    for run in runs:

        name = "evts_vs_lumi_%s" % (run)
        entries = input.Get(os.path.join(run, name))
        entries.Rebin(rebin)

        for sector in sectors:

            name = "hits_%s_vs_lumi_vs_r_%s_%s" % (ops.hits, sector, run)
            hists[name] = input.Get(os.path.join(run, name))
            if not hists[name]:
                fatal("Could not retrieve %s" % (os.path.join(run, name)))
            hists[name].Rebin2D(rebin, rebin)

            numer = copy.copy(hists[name])
            denom = copy.copy(hists[name])
            denom.Reset()
            denom_area = copy.copy(area_L if "L" in sector else area_S)

            if not denom.GetNbinsX() == entries.GetNbinsX():
                fatal("Cannot make rate for %s. Conflict in x-axis and entries vs. lumi." % (name))

            for xbin in xrange(denom.GetNbinsX()):

                ents = entries.GetBinContent(xbin)

                if not denom.GetNbinsY() == denom_area.GetNbinsX():
                    fatal("Cannot make rate for %s. Conflict in y-axis and area." % (name))

                for ybin in xrange(denom.GetNbinsY()):
                    radius   = denom_area.GetBinCenter(ybin)
                    area     = denom_area.GetBinContent(ybin)
                    livetime = livetime_csc if radius < boundary else livetime_mdt
                    denom.SetBinContent(xbin, ybin, ents * area * livetime)

            name = numer.GetName().replace("hits_", "rate_")
            hists[name] = copy.copy(numer)
            hists[name].Reset()
            hists[name].Divide(numer, denom)
            hists[name].SetName(name)
            style_vs_lumi_vs_r(hists[name])
            for xbin in xrange(0, hists[name].GetNbinsX()+1):
                for ybin in xrange(0, hists[name].GetNbinsY()+1):
                    hists[name].SetBinError(xbin, ybin, 0)

            name = "rate_%s_vs_lumi_vs_r_%s_%s" % (ops.hits, sector, run)
            canvas = ROOT.TCanvas(name, name, 800, 800)
            canvas.Draw()
        
            hists[name].Draw("colz,same")

            xcoord, ycoord = 0.2, 0.96
            atlas = ROOT.TLatex(xcoord, ycoord, "ATLAS Internal, Run %s      #rho = %.3f" % (run.lstrip("0"), hists[name].GetCorrelationFactor()))
            atlas.SetTextSize(0.03)
            atlas.SetTextFont(42)
            atlas.SetNDC()
            atlas.Draw()

            ROOT.gPad.RedrawAxis()
            canvas.SaveAs(os.path.join(ops.output, canvas.GetName()+".pdf"))
            

def style_vs_r(hist, layer, ndiv=505):
    xlo  = 800  if layer=="EI" else 1400
    xhi  = 4500 if layer=="EI" else 6000
    name = hist.GetName()
    hist.SetMarkerColor(ROOT.kAzure+1 if "L" in name else ROOT.kRed)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(0.9)
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetXaxis().SetRangeUser(xlo, xhi)
    hist.GetXaxis().SetTitle(xtitle(name))
    hist.GetYaxis().SetTitle(ytitle(name))
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.6)

def style_vs_lumi_vs_r(hist, ndiv=505):
    name = hist.GetName()
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetYaxis().SetRangeUser(800, 4500)
    if "284285" in name:
        hist.GetXaxis().SetRangeUser(2.5, 5.5)
    hist.GetXaxis().SetTitle(xtitle(name))
    hist.GetYaxis().SetTitle(ytitle(name))
    hist.GetZaxis().SetTitle(ytitle("rate"))
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetZaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.1)
    hist.GetYaxis().SetTitleOffset(1.7)
    hist.GetZaxis().SetTitleOffset(1.4)

def draw_vs_r(hist, output, height=800, width=800, drawopt="psame", logos=False):
    name = hist.GetName()
    canvas = ROOT.TCanvas(name, name, width, height)
    canvas.Draw()
    hist.Draw(drawopt)
    if logos:
        draw_logos()
    canvas.SaveAs(os.path.join(output, canvas.GetName()+".pdf"))

def style_vs_bcid(hist, per_event, ndiv=505, setmax=False):
    name = hist.GetName()
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetMarkerStyle(20)
    hist.SetMarkerSize(0.9)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetLineStyle(1)
    if "lumi" in name: hist.SetFillColor(ROOT.kYellow)
    if "mdt"  in name: hist.SetFillColor(ROOT.kRed)
    if "csc"  in name: hist.SetFillColor(ROOT.kAzure+1)
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetXaxis().SetTitle(xtitle(name))
    hist.GetYaxis().SetTitle(ytitle(name))
    hist.GetYaxis().SetTitleOffset(0.65)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    if per_event and setmax:
        hist.SetMaximum(setmax)

def style_vs_region(hist, rate):
    name = hist.GetName()
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetZaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.07)
    hist.GetZaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.1)
    hist.GetYaxis().SetTitleOffset(1.6)
    hist.GetZaxis().SetTitleOffset(1.4)

def draw_logos(xcoord=0.5, ycoord=0.5, run=None, fit=True):

    atlas = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
    if run:
        runz  = ROOT.TLatex(xcoord, ycoord-0.06, "Run %s" % (int(run)))
        bunch = ROOT.TLatex(xcoord, ycoord-0.12, "%s bunches" % (bunches(run)))
    fits = ROOT.TLatex(xcoord+0.25, ycoord, "(slope, offset)")

    if run:
        logos = [atlas, runz, bunch]
    else:
        if fit: logos = [atlas, fits]
        else:   logos = [atlas]

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

    if run == "00278880": return ROOT.kGray+2
    if run == "00279169": return ROOT.kViolet
    if run == "00279685": return ROOT.kMagenta
    if run == "00280464": return ROOT.kRed+1
    if run == "00280862": return ROOT.kRed-4
    if run == "00281143": return ROOT.kOrange-3
    if run == "00281411": return ROOT.kOrange+4
    if run == "00282992": return 210
    if run == "00283429": return ROOT.kCyan+1
    if run == "00284213": return ROOT.kAzure+1
    if run == "00284285": return ROOT.kBlue

    return ROOT.kBlack

def ymax(region, rate=False, draw_slope=True):

    if rate and not draw_slope:
        if region == "mdt_full": return  15
        if region == "mdt_EIL1": return 180
        if region == "mdt_EIS1": return 180
        if region == "mdt_EML1": return  60
        if region == "mdt_EMS1": return  60
        if region == "mdt_BIS8": return  60
        if region == "csc_CSL1": return 800
        if region == "csc_CSS1": return 800

    if region == "mdt_full": return 6100 if not rate else   20
    if region == "mdt_EIL1": return  550 if not rate else  200
    if region == "mdt_EIS1": return  380 if not rate else  200
    if region == "mdt_EIL2": return  180
    if region == "mdt_EIS2": return   90
    if region == "mdt_EIL3": return  100
    if region == "mdt_EIS3": return  100
    if region == "csc_full": return  100
    if region == "csc_CSL1": return   50 if not rate else 1000
    if region == "csc_CSS1": return   40 if not rate else 1000
    fatal("no ymax for %s" % (region))
    
def ymin(region):
    if region == "mdt_full": return 0
    if region == "mdt_EIL1": return 0
    if region == "mdt_EIL2": return 0
    if region == "mdt_EIL3": return 0
    if region == "mdt_EIS1": return 0
    if region == "mdt_EIS2": return 0
    if region == "mdt_EIS3": return 0
    if region == "csc_full": return 0
    if region == "csc_CSL1": return 0
    if region == "csc_CSS1": return 0
    return 0

def xtitle(name):
    if "_vs_bcid" in name: return "BCID"
    if "_vs_lumi" in name: return "< inst. lumi. > [e^{33}_cm^{-2}_s^{-1}_]".replace("_", "#scale[0.5]{ }")
    if "_vs_r"    in name: return "radius [mm]"
    if "_vs_mu"   in name: return "< interactions per BC > (#mu)"
    
    if "endcap"   in name: return xtitle("_vs_r")

    return "fuck"

def ytitle(name):

    if any(tag in name for tag in ["hits_raw_vs_lumi",  "hits_raw_vs_mu", 
                                   "hits_adc_vs_lumi",  "hits_adc_vs_mu", 
                                   "hits_vs_bcid"]) and not "vs_r" in name:
        if "mdt_full" in name: return      "< MDT hits per event >"
        if "mdt_EIL1" in name: return "< MDT EIL1 hits per event >"
        if "mdt_EIL2" in name: return "< MDT EIL2 hits per event >"
        if "mdt_EIS1" in name: return "< MDT EIS1 hits per event >"
        if "mdt_EIS2" in name: return "< MDT EIS2 hits per event >"
        if "mdt_EML1" in name: return "< MDT EML1 hits per event >"
        if "mdt_EML2" in name: return "< MDT EML2 hits per event >"
        if "mdt_EMS1" in name: return "< MDT EMS1 hits per event >"
        if "mdt_EMS2" in name: return "< MDT EMS2 hits per event >"
        if "mdt_BIS7" in name: return "< MDT BIS7 hits per event >"
        if "mdt_BIS8" in name: return "< MDT BIS8 hits per event >"
        if "csc_full" in name: return      "< CSC hits per event >"
        if "csc_CSL1" in name: return    "< CSC L hits per event >"
        if "csc_CSS1" in name: return    "< CSC S hits per event >"

    if any(tag in name for tag in ["rate_raw_vs_lumi", "rate_raw_vs_mu",
                                   "rate_adc_vs_lumi", "rate_adc_vs_mu",
                                   ]) and not "vs_r" in name:
        unit = "[Hz / cm^{2}]"
        if "mdt_full" in name: return      "MDT hit rate %s" % (unit)
        if "mdt_EIL1" in name: return "MDT EIL1 hit rate %s" % (unit)
        if "mdt_EIL2" in name: return "MDT EIL2 hit rate %s" % (unit)
        if "mdt_EIS1" in name: return "MDT EIS1 hit rate %s" % (unit)
        if "mdt_EIS2" in name: return "MDT EIS2 hit rate %s" % (unit)
        if "mdt_EML1" in name: return "MDT EML1 hit rate %s" % (unit)
        if "mdt_EML2" in name: return "MDT EML2 hit rate %s" % (unit)
        if "mdt_EMS1" in name: return "MDT EMS1 hit rate %s" % (unit)
        if "mdt_EMS2" in name: return "MDT EMS2 hit rate %s" % (unit)
        if "mdt_BIS7" in name: return "MDT BIS7 hit rate %s" % (unit)
        if "mdt_BIS8" in name: return "MDT BIS8 hit rate %s" % (unit)
        if "csc_full" in name: return      "CSC hit rate %s" % (unit)
        if "csc_CSL1" in name: return    "CSC L hit rate %s" % (unit)
        if "csc_CSS1" in name: return    "CSC S hit rate %s" % (unit)

    if "lumi_vs_bcid"          in name: return "< inst. lumi. > [e^{30}_cm^{-2}_s^{-1}_]".replace("_", "#scale[0.5]{ }")
    if "hits_raw_vs_r"         in name: return "< hits per event >"
    if "hits_adc_vs_r"         in name: return "< hits per event >"
    if "rate_raw_vs_region"    in name: return "hit rate [Hz / cm^{2}]"
    if "rate_adc_vs_region"    in name: return "hit rate [Hz / cm^{2}]"
    if "rate_raw_vs_r"         in name: return "hit rate [Hz / cm^{2}]"
    if "rate_adc_vs_r"         in name: return "hit rate [Hz / cm^{2}]"
    if "rate_raw_vs_lumi_vs_r" in name: return "radius [mm]"
    if "rate_adc_vs_lumi_vs_r" in name: return "radius [mm]"

    if name == "endcap_L_area": return "L area [cm^{2}]"
    if name == "endcap_S_area": return "S area [cm^{2}]"

    if "rate" in name: return "hit rate [Hz / cm^{2}]"

    return "fuck"
            
def caption(run):
    return "%s, %s bunches" % (int(run), bunches(run))

def bunches(run):
    if run == "00278880": return  447
    if run == "00279169": return  733
    if run == "00279345": return  877
    if run == "00279598": return 1021
    if run == "00279685": return 1021
    if run == "00280231": return 1165
    if run == "00280464": return 1309
    if run == "00280614": return 1309
    if run == "00280673": return 1453
    if run == "00280862": return 1453
    if run == "00281074": return 1596
    if run == "00281143": return 1596
    if run == "00281381": return 1813
    if run == "00281385": return 1813
    if run == "00281411": return 1813
    if run == "00282992": return 1813
    if run == "00283429": return 2029
    if run == "00283780": return 2232
    if run == "00284213": return 2232
    if run == "00284285": return 2232

def kill_weird_bins(hist):
    for bin in xrange(1, hist.GetNbinsX()):
        if hist.GetBinContent(bin-1) == 0 and hist.GetBinContent(bin+1) == 0:
            hist.SetBinContent(bin, 0)
            hist.SetBinError(bin, 0)
        if hist.GetBinContent(bin-2) == 0 and hist.GetBinContent(bin+1) == 0:
            hist.SetBinContent(bin, 0)
            hist.SetBinError(bin, 0)
        if hist.GetBinContent(bin-1) == 0 and hist.GetBinContent(bin+2) == 0:
            hist.SetBinContent(bin, 0)
            hist.SetBinError(bin, 0)

def slope_offset(region, bunches=2808):
    if bunches == 2808:
        if region == "csc_CSS1": return (82.984, 0)
        if region == "csc_CSL1": return (80.863, 0)
        if region == "mdt_EIS1": return (18.522, 0)
        if region == "mdt_EIL1": return (19.531, 0)
        if region == "mdt_full": return (0, 0)
    if bunches == 3564:
        if region == "csc_CSS1": return (75.131, 0)
        if region == "csc_CSL1": return (72.823, 0)
        if region == "mdt_EIS1": return (17.082, 0)
        if region == "mdt_EIL1": return (17.745, 0)
        if region == "mdt_full": return (0, 0)
    fatal("No slope, offset for %s, %s bunches" % (region, bunches))

def chamber_area():

    pkg   = "/Users/alexandertuna/Downloads/MuonRawHits/"
    areas = {}
    # here  = os.path.abspath(__file__)
    geo   = os.path.join(pkg, "data/geometry")

    mm2_to_cm2 = (1/10.0)*(1/10.0)

    for detector in ["mdt_chambers.txt",
                     "csc_chambers.txt",
                     ]:
        for line in open(os.path.join(geo, detector)).readlines():
            line = line.strip()
            if not line:
                continue
            
            _, chamber, area = line.split()
            areas[chamber] = float(area) * mm2_to_cm2
            
    return areas

def fatal(message):
    sys.exit("Error in %s: %s" % (__file__, message))

def colz():
    import array
    ncontours = 200
    #stops = array.array("d", [0.0, 0.3, 0.6, 1.0])
    #red   = array.array("d", [1.0, 1.0, 1.0, 0.0])
    #green = array.array("d", [1.0, 1.0, 0.0, 0.0])
    #blue  = array.array("d", [1.0, 0.0, 0.0, 0.0])
    stops = array.array("d", [0.0, 0.5, 1.0])
    red   = array.array("d", [1.0, 1.0, 1.0])
    green = array.array("d", [1.0, 1.0, 0.0])
    blue  = array.array("d", [1.0, 0.0, 0.0])

    stops = array.array("d", [0.0, 0.5, 1.0])
    red   = array.array("d", [0.0, 1.0, 1.0])
    green = array.array("d", [1.0, 1.0, 0.0])
    blue  = array.array("d", [0.0, 0.0, 0.0])

    ROOT.TColor.CreateGradientColorTable(len(stops), stops, red, green, blue, ncontours)
    ROOT.gStyle.SetNumberContours(ncontours)


if __name__ == "__main__":
    main()


