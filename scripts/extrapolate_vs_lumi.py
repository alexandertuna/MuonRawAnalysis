import argparse
import ROOT
ROOT.gROOT.SetBatch(True)

ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

ROOT.gStyle.SetPadTopMargin(0.06)
ROOT.gStyle.SetPadBottomMargin(0.15)
ROOT.gStyle.SetPadLeftMargin(0.18)
ROOT.gStyle.SetPadRightMargin(0.06)

bunches_run3  = 2808
bunches_hllhc = 3564

lumi_run3  = 10
lumi_hllhc = 50

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bunches",  help="Number of bunches. Must be 2808 or 3564.")
    parser.add_argument("--lines",    help="Draw guiding lines", action="store_true")
    return parser.parse_args()

def main():

    ops = options()
    if not ops.bunches in ["2808", "3564"]: 
        fatal("Please give --bunches as 2808 (Run 3) or 3564 (HL-LHC)")

    xlo = 0.1
    xhi = 2.8 if ops.bunches=="2808" else 9.9

    xaxis = "projected < hit rate > [ Hz / cm^{2} ]"
    yaxis = "inst. lumi. [ e^{34} cm^{-2} s^{-1} ]"
    dummy = ROOT.TH1F("dummy", ";%s;%s" % (yaxis, xaxis), 1, xlo, xhi)
    style(dummy)

    name = "extrapolate_vs_lumi_%s" % (ops.bunches)
    canvas = ROOT.TCanvas(name, name, 800, 800)
    canvas.Draw()
    dummy.Draw("same")
    
    fit   = {}
    for name in ["CSL1",
                 "CSS1",
                 "EIL1",
                 "EIS1",
                 ]:
        fit[name] = ROOT.TF1("fit_"+name, "[0]*(x) + [1]", xlo, xhi)
        slope, offset = slope_offset(name, int(ops.bunches))
        fit[name].SetParameter(0, slope*10)
        fit[name].SetParameter(1, offset)
        fit[name].SetLineColor(color(name))
        fit[name].SetLineWidth(3)
        fit[name].SetLineStyle(7)
        fit[name].DrawCopy("same")

        if "L" in name and ops.lines:
            lumi_1 = 1.0 if ops.bunches=="2808" else 5.0
            y_at_lumi_1  = fit[name].Eval(lumi_1)
            horiz_line_1 = ROOT.TLine(xlo,    y_at_lumi_1, lumi_1, y_at_lumi_1)
            verti_line_1 = ROOT.TLine(lumi_1, 0,           lumi_1, y_at_lumi_1)

            lumi_2 = 2.0 if ops.bunches=="2808" else 7.0
            y_at_lumi_2  = fit[name].Eval(lumi_2)
            horiz_line_2 = ROOT.TLine(xlo,    y_at_lumi_2, lumi_2, y_at_lumi_2)
            verti_line_2 = ROOT.TLine(lumi_2, 0,           lumi_2, y_at_lumi_2)

            for line in [horiz_line_1, verti_line_1,
                         horiz_line_2, verti_line_2,
                         ]:
                ROOT.SetOwnership(line, False)
                line.SetLineColor(ROOT.kBlack)
                line.SetLineWidth(1)
                line.SetLineStyle(1)
                line.Draw()

        fit[name].DrawCopy("same")

    legend = {}
    xcoord, ycoord = 0.7, 0.56
    ydelta = 0.05
    legend["CSL1"] = ROOT.TLatex(xcoord, ycoord-0*ydelta, "CSC, L")
    legend["CSS1"] = ROOT.TLatex(xcoord, ycoord-1*ydelta, "CSC, S")
    legend["EIL1"] = ROOT.TLatex(xcoord, ycoord-2*ydelta, "MDT, EIL1")
    legend["EIS1"] = ROOT.TLatex(xcoord, ycoord-3*ydelta, "MDT, EIS1")
    
    for reg in legend:
        legend[reg].SetTextColor(color(reg))
        legend[reg].SetTextSize(0.035)
        legend[reg].SetTextFont(42)
        legend[reg].SetNDC()
        legend[reg].Draw()

    xcoord, ycoord = 0.42, 0.8
    atlas = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
    data  = ROOT.TLatex(xcoord, ycoord-0.06, "assuming %s bunches" % (ops.bunches))
    logos = [atlas, data]
    for logo in logos:
        logo.SetTextSize(0.040 if logo==atlas else 0.03)
        logo.SetTextFont(42)
        logo.SetTextAlign(22)
        logo.SetNDC()
        logo.Draw()
 
    canvas.SaveAs(canvas.GetName()+".pdf")
        
def fatal(message):
    import sys
    sys.exit("Error in %s: %s" % (__file__, message))

def slope_offset(region, bunches=2808):
    # NB: slope in units of e33.
    if bunches == 2808:
        if region == "CSS1": return (82.984, 0)
        if region == "CSL1": return (80.863, 0)
        if region == "EIS1": return (18.522, 0)
        if region == "EIL1": return (19.531, 0)
    if bunches == 3564:
        if region == "CSS1": return (75.131, 0)
        if region == "CSL1": return (72.823, 0)
        if region == "EIS1": return (17.082, 0)
        if region == "EIL1": return (17.745, 0)
    fatal("No slope, offset for %s, %s bunches" % (region, bunches))

def style(hist, ndiv=505):
    ops = options()
    hist.SetStats(0)
    hist.SetMinimum(0)
    hist.SetMaximum(2190 if ops.bunches=="2808" else 6900)
    hist.GetXaxis().SetNdivisions(ndiv)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.8)

def color(region):
    if region == "CSS1": return ROOT.kBlue
    if region == "CSL1": return ROOT.kBlack
    if region == "EIS1": return ROOT.kRed
    if region == "EIL1": return 210

if __name__ == "__main__":
    main()

# xcoord,ycoord = 0.7, 0.85
# atlas = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
# data  = ROOT.TLatex(xcoord, ycoord-0.06, "Data, 13 TeV")
# logos = [atlas, data]
# for logo in logos:
#     logo.SetTextSize(0.040)
#     logo.SetTextFont(42)
#     logo.SetTextAlign(22)
#     logo.SetNDC()
#     logo.Draw()

# legend = {}
# ycoord = ycoord - 0.15
# ydelta = 0.05
# legend["CSL1"] = ROOT.TLatex(xcoord-0.2, ycoord-0*ydelta, "CSC, L")
# legend["CSS1"] = ROOT.TLatex(xcoord-0.2, ycoord-1*ydelta, "CSC, S")
# legend["EIL1"] = ROOT.TLatex(xcoord-0.2, ycoord-2*ydelta, "MDT, EIL1")
# legend["EIS1"] = ROOT.TLatex(xcoord-0.2, ycoord-3*ydelta, "MDT, EIS1")

# for reg in legend:
#     legend[reg].SetTextColor(color(reg))
#     legend[reg].SetTextSize(0.035)
#     legend[reg].SetTextFont(42)
#     legend[reg].SetNDC()
#     legend[reg].Draw()



