import ROOT

hits       = "adc"
efficiency = 1.0 if hits=="raw" else 0.789

area  = ROOT.TFile.Open("area.root")
hists = ROOT.TFile.Open("histograms.root")

evts     = hists.Get("00284285/evts_00284285").GetBinContent(1)
counts_L = hists.Get("00284285/hits_%s_vs_region_L_00284285" % (hits))
counts_S = hists.Get("00284285/hits_%s_vs_region_S_00284285" % (hits))

area_L = area.Get("area_vs_region_L")
area_S = area.Get("area_vs_region_S")

xbin_A   = 10
xbin_C   = 8
ybin_CSC = 8

livetime = 140e-9

area_L_A   =   area_L.GetBinContent(xbin_A, ybin_CSC)
area_L_C   =   area_L.GetBinContent(xbin_C, ybin_CSC)
area_S_A   =   area_S.GetBinContent(xbin_A, ybin_CSC)
area_S_C   =   area_S.GetBinContent(xbin_C, ybin_CSC)

counts_L_A = counts_L.GetBinContent(xbin_A, ybin_CSC)
counts_L_C = counts_L.GetBinContent(xbin_C, ybin_CSC)
counts_S_A = counts_S.GetBinContent(xbin_A, ybin_CSC)
counts_S_C = counts_S.GetBinContent(xbin_C, ybin_CSC)

rate_L_A = counts_L_A / (evts * livetime * area_L_A)
rate_L_C = counts_L_C / (evts * livetime * area_L_C)
rate_S_A = counts_S_A / (evts * livetime * area_S_A)
rate_S_C = counts_S_C / (evts * livetime * area_S_C)

rate_L = (counts_L_A+counts_L_C) / (evts * livetime * (area_L_A+area_L_C) * efficiency)
rate_S = (counts_S_A+counts_S_C) / (evts * livetime * (area_S_A+area_S_C) * efficiency)

print "L  A: %.1f | C: %.1f | avg: %.1f" % (rate_L_A, rate_L_C, rate_L)
print "S  A: %.1f | C: %.1f | avg: %.1f" % (rate_S_A, rate_S_C, rate_S)

