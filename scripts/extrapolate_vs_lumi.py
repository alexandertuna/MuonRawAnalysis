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

def options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bunches",  help="Number of bunches. Must be 2808 or 3564.")
    parser.add_argument("--lines",    help="Draw guiding lines", action="store_true")
    parser.add_argument("--hits",     help="Type of hits to use: raw or adc")
    return parser.parse_args()

def main():

    ops = options()
    if not ops.bunches in ["2808", "3564"]: 
        fatal("Please give --bunches as 2808 (Run 3) or 3564 (HL-LHC)")
    if not ops.hits in ["raw", "adc"]:
        fatal("Please give --hits as raw or adc")

    xlo = 0.1
    xhi = 2.8 if ops.bunches=="2808" else 9.9

    xaxis = "projected < hit rate > [ Hz / cm^{2} ]"
    yaxis = "inst. lumi. [ e^{34} cm^{-2} s^{-1} ]"
    dummy = ROOT.TH1F("dummy", ";%s;%s" % (yaxis, xaxis), 1, xlo, xhi)
    style(dummy)

    name = "extrapolate_vs_lumi_%s_%s" % (ops.hits, ops.bunches)
    canvas = ROOT.TCanvas(name, name, 800, 800)
    canvas.Draw()
    dummy.Draw("same")
    
    fit   = {}
    for name in ["CSL1",
                 "CSS1",
                 "EIL1",
                 "EIS1",
                 "EML1",
                 "EMS1",
                 ]:
        fit[name] = ROOT.TF1("fit_"+name, "[0]*(x) + [1]", xlo, xhi)
        slope, offset = slope_offset(name, int(ops.bunches), ops.hits)
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
    xcoord, ycoord = 0.31, 0.56
    ydelta = 0.05
    legend["CSL1"] = ROOT.TLatex(xcoord,      ycoord-0*ydelta, "CSC L")
    legend["CSS1"] = ROOT.TLatex(xcoord,      ycoord-1*ydelta, "CSC S")
    legend["EIL1"] = ROOT.TLatex(xcoord+0.37, ycoord-0*ydelta, "MDT EIL1")
    legend["EIS1"] = ROOT.TLatex(xcoord+0.37, ycoord-1*ydelta, "MDT EIS1")
    legend["EML1"] = ROOT.TLatex(xcoord+0.37, ycoord-2*ydelta, "MDT EML1")
    legend["EMS1"] = ROOT.TLatex(xcoord+0.37, ycoord-3*ydelta, "MDT EMS1")
    
    for reg in legend:
        legend[reg].SetTextColor(color(reg))
        legend[reg].SetTextSize(0.038)
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
 
    canvas.SaveAs("output/"+canvas.GetName()+".pdf")
        
def fatal(message):
    import sys
    sys.exit("Error in %s: %s" % (__file__, message))

def slope_offset(region, bunches, hits):
    # NB: slope in units of e33.
    if bunches == 2808 and hits=="raw":
        if region == "CSL1": return (79.872, 0)
        if region == "CSS1": return (80.470, 0)
        if region == "EIL1": return (18.872, 0)
        if region == "EIS1": return (17.793, 0)
        if region == "EML1": return ( 4.577, 0)
        if region == "EMS1": return ( 5.977, 0)
    if bunches == 3564 and hits=="raw":
        if region == "CSL1": return (72.360, 0)
        if region == "CSS1": return (73.418, 0)
        if region == "EIL1": return (16.992, 0)
        if region == "EIS1": return (16.243, 0)
        if region == "EML1": return ( 4.104, 0)
        if region == "EMS1": return ( 5.307, 0)
    if bunches == 2808 and hits=="adc":
        if region == "CSL1": return (69.699, 0)
        if region == "CSS1": return (70.856, 0)
        if region == "EIL1": return (16.044, 0)
        if region == "EIS1": return (15.180, 0)
        if region == "EML1": return ( 3.861, 0)
        if region == "EMS1": return ( 5.006, 0)
    if bunches == 3564 and hits=="adc":
        if region == "CSL1": return (62.852, 0)
        if region == "CSS1": return (63.995, 0)
        if region == "EIL1": return (14.388, 0)
        if region == "EIS1": return (13.822, 0)
        if region == "EML1": return ( 3.445, 0)
        if region == "EMS1": return ( 4.413, 0)
    fatal("No slope, offset for %s, %s bunches, %s hits" % (region, bunches, hits))

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
    if region == "EMS1": return ROOT.kViolet
    if region == "EML1": return ROOT.kOrange-3

if __name__ == "__main__":
    main()

