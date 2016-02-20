import copy
import os
import ROOT
import rootlogon
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetPadRightMargin(0.06)

run      = "00284285"
template = "%s/hits_raw_vs_r_%sxx%s_%s"
boundary = 2050
rebin    = 4
hits     = "raw"
outdir   = "phi_symmetry"

if not os.path.isdir(outdir):
    os.makedirs(outdir)

livetime_csc = 140e-9
livetime_mdt = 1300e-9

efficiency_csc_adc = 0.789
efficiency_mdt_adc = 1.0

regions = ["EIL", "EIS"]
sectors = [["01", "03", "05", "07", "09", "11", "13", "15"],
           ["02", "04", "06", "08", "10", "12", "14", "16"],
           ]

fi         = ROOT.TFile.Open("histograms.root")
input_area = ROOT.TFile.Open("area.root")

def main():

    entries = fi.Get("%s/evts_%s" % (run, run))
    entries = entries.GetBinContent(1)

    rates = {}
    hists = {}

    for region, sects in zip(regions, sectors):

        name   = "rate_raw_vs_r_%s_%s" % (region, run)
        canvas = ROOT.TCanvas(name, name, 800, 800)
        canvas.Draw()

        for sect in reversed(sects):

            name        = "hits_%s_%s" % (region, sect)
            hists[name] = fi.Get(template % (run, region, sect, run))
            area        = input_area.Get("area_vs_r_%s_%s" % (region, sect))

            for hist in [hists[name], area]:
                hist.Rebin(rebin)

            numer = copy.copy(hists[name])
            denom = copy.copy(area)

            for bin in xrange(0, denom.GetNbinsX()+1):
                radius     = denom.GetBinCenter(bin)
                thisarea   = denom.GetBinContent(bin)
                livetime   = livetime_csc       if (radius < boundary and "EI" in region) else livetime_mdt
                efficiency = efficiency_csc_adc if (radius < boundary and "EI" in region) else efficiency_mdt_adc
                if hits=="raw":
                    efficiency = 1.0
                denom.SetBinContent(bin, entries * thisarea * livetime * efficiency)

            name = numer.GetName().replace("hits_", "rate_")
            hists[name] = copy.copy(numer)
            hists[name].Reset()
            hists[name].Divide(numer, denom)
            hists[name].SetName(name)

            style(hists[name], sect)
            hists[name].Draw("psame")

        xcoord, ycoord = 0.6, 0.85
        atlas  = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
        runz   = ROOT.TLatex(xcoord, ycoord-0.05, "Run %s" % (int(run)))
        bunch  = ROOT.TLatex(xcoord, ycoord-0.10, "%s bunches" % (2232))
        logos  = [atlas, runz, bunch]
        labels = create_labels(sects, region)
        for logo in logos+labels:
            ROOT.SetOwnership(logo, False)
            logo.SetTextSize(0.045)
            logo.SetTextFont(42)
            logo.SetTextAlign(22)
            logo.SetNDC()
            logo.Draw()
        
        ROOT.gPad.RedrawAxis()
        canvas.SaveAs(os.path.join(outdir, canvas.GetName()+".pdf"))

def create_labels(phis, region):
    xcoord, ycoord = 0.6, 0.6
    xdelta, ydelta = 0.05, 0.05
    labels = [ROOT.TLatex(xcoord, ycoord+0.05, "phi sector, %s" % (region))]
    for iphi, phi in enumerate(phis):
        labels.append(ROOT.TLatex(xcoord + (-xdelta if iphi < 4 else xdelta), 
                                  ycoord - ((iphi % 4)*ydelta), 
                                  phi))
        labels[-1].SetTextColor(color(phi))
    return labels

def style(hist, phi):
    xlo  = 800  # if layer=="EI" else 1400
    xhi  = 4500 # if layer=="EI" else 6000
    hist.GetXaxis().SetNdivisions(505)
    hist.GetXaxis().SetRangeUser(xlo, xhi)
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.SetMarkerColor(color(phi))
    hist.SetMarkerSize(0.9)
    hist.GetXaxis().SetTitle("radius [mm]")
    hist.GetYaxis().SetTitle("hit rate [ cm^{-2} s^{-1} ]")
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.6)
    hist.SetMinimum(0)
    hist.SetMaximum(950)

def color(phi):
    if phi in ["01", "02"]: return ROOT.kBlue
    if phi in ["03", "04"]: return ROOT.kRed
    if phi in ["05", "06"]: return 210
    if phi in ["07", "08"]: return ROOT.kViolet
    if phi in ["09", "10"]: return ROOT.kCyan
    if phi in ["11", "12"]: return ROOT.kMagenta
    if phi in ["13", "14"]: return ROOT.kOrange+1
    if phi in ["15", "16"]: return ROOT.kGray+1


if __name__ == "__main__":
    main()


