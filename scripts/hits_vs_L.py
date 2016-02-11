import os
import ROOT
import rootlogon
ROOT.gROOT.SetBatch(True)

f = ROOT.TFile.Open("histograms.root")

outdir = "hits_vs_r"

events = f.Get("evts_00284285").GetBinContent(1)

hits_vs_r_L_01_00284285  = f.Get("hits_vs_r_L_01_00284285")
hits_vs_r_L_03_00284285  = f.Get("hits_vs_r_L_03_00284285")
hits_vs_r_L_05_00284285  = f.Get("hits_vs_r_L_05_00284285")
hits_vs_r_L_07_00284285  = f.Get("hits_vs_r_L_07_00284285")
hits_vs_r_L_09_00284285  = f.Get("hits_vs_r_L_09_00284285")
hits_vs_r_L_11_00284285  = f.Get("hits_vs_r_L_11_00284285")
hits_vs_r_L_13_00284285  = f.Get("hits_vs_r_L_13_00284285")
hits_vs_r_L_15_00284285  = f.Get("hits_vs_r_L_15_00284285")
hits_vs_r_L_A15_00284285 = f.Get("hits_vs_r_L_A15_00284285")
hits_vs_r_L_C15_00284285 = f.Get("hits_vs_r_L_C15_00284285")

def sector(hist):
    return hist.GetName().split("_")[4]

def style(hist):
    hist.GetXaxis().SetTitle("radius [mm]")
    hist.GetYaxis().SetTitle("< MDT hits per event > EIL1, EIL2")
    hist.GetXaxis().SetTitleSize(0.05)
    hist.GetYaxis().SetTitleSize(0.05)
    hist.GetXaxis().SetLabelSize(0.05)
    hist.GetYaxis().SetLabelSize(0.05)
    hist.GetXaxis().SetTitleOffset(1.2)
    hist.GetYaxis().SetTitleOffset(1.6)
    hist.SetLineColor(ROOT.kBlack)
    hist.SetMarkerColor(ROOT.kBlack)
    hist.SetMinimum(0.0)
    hist.SetMaximum(1.0)

for hist in [hits_vs_r_L_01_00284285,
             hits_vs_r_L_03_00284285,
             hits_vs_r_L_05_00284285,
             hits_vs_r_L_07_00284285,
             hits_vs_r_L_09_00284285,
             hits_vs_r_L_11_00284285,
             hits_vs_r_L_13_00284285,
             hits_vs_r_L_15_00284285,
             hits_vs_r_L_A15_00284285,
             hits_vs_r_L_C15_00284285,
             ]:
    hist.Scale(1 / events)
    style(hist)
    name = hist.GetName()
    canv = ROOT.TCanvas(name, name, 800, 800)
    canv.Draw()
    hist.Draw("pesame")
    canv.SaveAs(os.path.join(outdir, canv.GetName()+".pdf"))

