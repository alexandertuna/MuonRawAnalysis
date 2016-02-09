import argparse
import array
import sys

import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

ROOT.gStyle.SetPadTopMargin(0.06)
ROOT.gStyle.SetPadBottomMargin(0.12)
ROOT.gStyle.SetPadLeftMargin(0.18)
ROOT.gStyle.SetPadRightMargin(0.06)

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hits", help="Type of hits to use: raw or adc", default=None)
    return parser.parse_args()
ops = options()

if ops.hits not in ["raw", "adc"]:
    sys.exit("Error: please give --hits to be raw or adc")

logy = False

bunches_run3  = 2808
bunches_hllhc = 3564

lumi_run3  = 10
lumi_hllhc = 70

bunches = {}
slope   = {}
graph   = {}
fit     = {}

regions = ["CSS1", "CSL1",
           "EIS1", "EIL1",
           "EMS1", "EML1",
           ]

for region in regions:
    bunches[region] = []
    slope[  region] = []

for line in open("slope_vs_bunches_%s.txt" % ops.hits).readlines():

    line = line.strip()
    if not line:             continue
    if line.startswith("#"): continue
    
    _name, _run, _bunches, _slope, _offset = line.split()

    for region in slope:
        if region in _name:
            slope[  region].append(float(_slope))
            bunches[region].append(float(_bunches))
            break
    else:
        sys.exit("Cant find relevant region for line:\n %s" % line)

expression = "[0] + [1]/x"
for region in regions:
    fit[region]   = ROOT.TF1("fit_"+region, expression, 0, 3800)
    graph[region] = ROOT.TGraph(len(bunches[region]), array.array("d", bunches[region]), array.array("d", slope[region]))
    graph[region].Fit(fit[region], "RWQN")

def color(region):
    if region == "CSS1": return ROOT.kBlue
    if region == "CSL1": return ROOT.kBlack
    if region == "EIS1": return ROOT.kRed
    if region == "EIL1": return 210
    if region == "EMS1": return ROOT.kViolet
    if region == "EML1": return ROOT.kOrange-3

def style(gr, region):
    gr.SetMarkerColor(color(region))
    gr.SetMarkerStyle(20)
    gr.SetMarkerSize(1.0)

multi = ROOT.TMultiGraph()
multi.SetTitle(";%s;%s" % ("colliding bunches", "fitted slope [ Hz / cm^{2} / e^{33} cm^{-2} s^{-1} ]"))

for region in graph:
    style(graph[region], region)
    multi.Add(graph[region], "PZ")

name = "slope_vs_bunches_%s" % (ops.hits)
canvas = ROOT.TCanvas(name, name, 800, 800)
canvas.Draw()

multi.SetMinimum(0.00 if not logy else 3.5)
multi.SetMaximum(300  if not logy else 500)
multi.Draw("Asame")
multi.GetXaxis().SetLimits(0, 3800)
multi.GetXaxis().SetNdivisions(505)
multi.GetXaxis().SetTitleSize(0.05)
multi.GetYaxis().SetTitleSize(0.05)
multi.GetXaxis().SetLabelSize(0.05)
multi.GetYaxis().SetLabelSize(0.05)
multi.GetXaxis().SetTitleOffset(1.2)
multi.GetYaxis().SetTitleOffset(1.6)
multi.Draw("Asame")

line_run3  = ROOT.TLine(bunches_run3,  0, bunches_run3,  150)
line_hllhc = ROOT.TLine(bunches_hllhc, 0, bunches_hllhc, 150)
for line in [line_run3, line_hllhc]:
    line.SetLineColor(ROOT.kBlack)
    line.SetLineWidth(1)
    line.SetLineStyle(1)
    line.Draw()

print
print " %7s %7s +/- %7s | %10s +/- %10s | %10s %10s | %10s %10s" % ("region", "[0]", " ", "[1]", " ", 
                                                                    "slope@2808", "slope@3564", "Hz@2808", "Hz@3564")

for region in sorted(regions):
    fit[region].SetLineColor(color(region))
    fit[region].SetLineWidth(2)
    fit[region].SetLineStyle(7)
    fit[region].Draw("same")

    slope_run3  = fit[region].GetParameter(0) + fit[region].GetParameter(1)/bunches_run3
    slope_hllhc = fit[region].GetParameter(0) + fit[region].GetParameter(1)/bunches_hllhc

    slope_run3_up  = fit[region].GetParameter(0) + fit[region].GetParError(0) + (fit[region].GetParameter(1) + fit[region].GetParError(1))/bunches_run3
    slope_hllhc_up = fit[region].GetParameter(0) + fit[region].GetParError(0) + (fit[region].GetParameter(1) + fit[region].GetParError(1))/bunches_hllhc

    print " %7s %7.3f +/- %7.3f | %10.2f +/- %10.2f | %10.3f %10.3f | %10.2f %10.2f" % (region,
                                                                                        fit[region].GetParameter(0),
                                                                                        fit[region].GetParError(0),
                                                                                        fit[region].GetParameter(1),
                                                                                        fit[region].GetParError(1),
                                                                                        slope_run3,
                                                                                        slope_hllhc,
                                                                                        lumi_run3  * slope_run3, #  / 1000,
                                                                                        lumi_hllhc * slope_hllhc, # / 1000,
                                                                                        )
print

xcoord, ycoord = 0.77, 0.81 if not logy else 0.85
atlas = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
data  = ROOT.TLatex(xcoord, ycoord-0.06, "Data, 13 TeV")
logos = [atlas, data]
for logo in logos:
    logo.SetTextSize(0.040)
    logo.SetTextFont(42)
    logo.SetTextAlign(22)
    logo.SetNDC()
    logo.Draw()

legend = {}
xcoord = 0.45 if not logy else 0.49
ycoord = 0.80
xdelta, ydelta = 0.05, 0.05
legend["CSL1"] = ROOT.TLatex(xcoord, ycoord-0*ydelta, "CSC L")
legend["CSS1"] = ROOT.TLatex(xcoord, ycoord-1*ydelta, "CSC S")
legend["EIL1"] = ROOT.TLatex(xcoord, ycoord-(2 if not logy else  4.8)*ydelta, "MDT EIL1")
legend["EIS1"] = ROOT.TLatex(xcoord, ycoord-(3 if not logy else  5.8)*ydelta, "MDT EIS1")
legend["EML1"] = ROOT.TLatex(xcoord, ycoord-(4 if not logy else 10.1)*ydelta, "MDT EML1")
legend["EMS1"] = ROOT.TLatex(xcoord, ycoord-(5 if not logy else  9.1)*ydelta, "MDT EMS1")

for reg in regions:
    legend[reg].SetTextColor(color(reg))
    legend[reg].SetTextSize(0.038)
    legend[reg].SetTextFont(42)
    legend[reg].SetNDC()
    legend[reg].Draw()

if logy:
    ROOT.gPad.SetLogy()

canvas.SaveAs("output/%s_%s.%s" % (canvas.GetName(), "log" if logy else "lin", "pdf"))


