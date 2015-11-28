import array
import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

ROOT.gStyle.SetPadTopMargin(0.06)
ROOT.gStyle.SetPadBottomMargin(0.12)
ROOT.gStyle.SetPadLeftMargin(0.18)
ROOT.gStyle.SetPadRightMargin(0.06)

bunches_run3  = 2808
bunches_hllhc = 3564

lumi_run3  = 10
lumi_hllhc = 50

runs = [
    "00278880",
    "00279169",
    "00279685",
    "00280464",
    "00280862",
    "00281143",
    "00281411",
    "00282992",
    "00283429",
    "00283780",
    "00284213",
    "00284285",
    ]

slope = {}
graph = {}
fit   = {}

bunches       = [447,    733,    1021,   1309,   1541,   1596,    1813,   1813,  2029,  2232,  2232,  2232]
slope["CSS1"] = [270.48, 197.77, 159.79, 122.35, 120.00, 110.09,  98.58, 97.12, 94.01, 90.45, 93.93, 90.89]
slope["CSL1"] = [277.55, 189.88, 159.49, 116.66, 121.88, 106.12, 107.80, 88.58, 93.50, 90.02, 92.75, 88.77]

slope["EIL1"] = [ 62.02,  44.56,  37.19,  32.93,  28.02,  24.96,  21.36, 23.19, 21.74, 20.89, 21.03, 21.47]
slope["EIS1"] = [ 52.78,  39.25,  33.54,  25.97,  25.36,  23.14,  21.11, 21.67, 20.37, 19.61, 19.98, 20.30]

graph["CSS1"] = ROOT.TGraph(len(bunches), array.array("d", bunches), array.array("d", slope["CSS1"]))
graph["CSL1"] = ROOT.TGraph(len(bunches), array.array("d", bunches), array.array("d", slope["CSL1"]))
graph["EIL1"] = ROOT.TGraph(len(bunches), array.array("d", bunches), array.array("d", slope["EIL1"]))
graph["EIS1"] = ROOT.TGraph(len(bunches), array.array("d", bunches), array.array("d", slope["EIS1"]))

expression = "[0] + [1]/x"
for region in graph:
    fit[region] = ROOT.TF1("fit_"+region, expression, 0, 3800)
    graph[region].Fit(fit[region], "RWQN")

def color(region):
    if region == "CSS1": return ROOT.kBlue
    if region == "CSL1": return ROOT.kBlack
    if region == "EIS1": return ROOT.kRed
    if region == "EIL1": return 210

def style(gr, region):
    gr.SetMarkerColor(color(region))
    gr.SetMarkerStyle(20)
    gr.SetMarkerSize(1.0)

multi = ROOT.TMultiGraph()
multi.SetTitle(";%s;%s" % ("colliding bunches", "fitted slope [ Hz / cm^{2} / e^{33} cm^{-2} s^{-1} ]"))

for region in graph:
    style(graph[region], region)
    multi.Add(graph[region], "PZ")

name = "slope_vs_bunches"
canvas = ROOT.TCanvas(name, name, 800, 800)
canvas.Draw()

multi.SetMinimum(0.00)
multi.SetMaximum(300)
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
print " %7s %7s %10s | %10s %10s | %10s %10s" % ("region", "[0]", "[1]", "slope@2808", "slope@3564", "kHz@2808", "kHz@3564")

for region in graph:
    fit[region].SetLineColor(color(region))
    fit[region].SetLineWidth(2)
    fit[region].SetLineStyle(7)
    fit[region].Draw("same")

    slope_run3  = fit[region].GetParameter(0) + fit[region].GetParameter(1)/bunches_run3
    slope_hllhc = fit[region].GetParameter(0) + fit[region].GetParameter(1)/bunches_hllhc

    print " %7s %7.3f %10.1f | %10.3f %10.3f | %10.1f %10.1f" % (region,
                                                                 fit[region].GetParameter(0),
                                                                 fit[region].GetParameter(1),
                                                                 slope_run3,
                                                                 slope_hllhc,
                                                                 lumi_run3  * slope_run3  / 1000,
                                                                 lumi_hllhc * slope_hllhc / 1000,
                                                                 )
print

xcoord,ycoord = 0.7, 0.85
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
ycoord = ycoord - 0.15
ydelta = 0.05
legend["CSL1"] = ROOT.TLatex(xcoord-0.2, ycoord-0*ydelta, "CSC, L")
legend["CSS1"] = ROOT.TLatex(xcoord-0.2, ycoord-1*ydelta, "CSC, S")
legend["EIL1"] = ROOT.TLatex(xcoord-0.2, ycoord-2*ydelta, "MDT, EIL1")
legend["EIS1"] = ROOT.TLatex(xcoord-0.2, ycoord-3*ydelta, "MDT, EIS1")

for reg in legend:
    legend[reg].SetTextColor(color(reg))
    legend[reg].SetTextSize(0.035)
    legend[reg].SetTextFont(42)
    legend[reg].SetNDC()
    legend[reg].Draw()

canvas.SaveAs(canvas.GetName()+".pdf")


