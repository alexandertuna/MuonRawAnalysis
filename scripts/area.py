"""
area.py -- a script to write a root file of the MDT/CSC area.
"""
import os
import ROOT
import hists

def main():

    xaxis = "radius [mm]"

    area_vs_r_L = ROOT.TH1F("area_vs_r_L", ";%s;%s;" % (xaxis, "area: L [cm^{2}]"), 500, 0, 5200)
    area_vs_r_S = ROOT.TH1F("area_vs_r_S", ";%s;%s;" % (xaxis, "area: S [cm^{2}]"), 500, 0, 5440)

    mdt_chambers, mdt_radii, mdt_areas, mdt_timings = geometry_mdt_tubes_EI()
    csc_chambers, csc_radii, csc_areas, csc_timings = geometry_csc_strips()

    # mdt geometry
    for chamber, radius, area, timing in zip(mdt_chambers, mdt_radii, mdt_areas, mdt_timings):

        if   "EIL1" in chamber or "EIL2" in chamber: area_vs_r_L.Fill(radius, area)
        elif "EIS1" in chamber or "EIS2" in chamber: area_vs_r_S.Fill(radius, area)
        else:
            continue

    # csc geometry
    for chamber, radius, area, timing in zip(csc_chambers, csc_radii, csc_areas, csc_timings):

        if   "CSL" in chamber: area_vs_r_L.Fill(radius, area)
        elif "CSS" in chamber: area_vs_r_S.Fill(radius, area)
        else:
            continue

    # turn off uncertainties
    for hist in [area_vs_r_L, area_vs_r_S]:
        for bin in xrange(0, hist.GetNbinsX()+1):
            hist.SetBinError(bin, 0.0)

    # write
    output = ROOT.TFile.Open("area.root", "recreate")
    for hist in [area_vs_r_L, area_vs_r_S]:
        output.cd()
        hist.Write()
    output.Close()

def geometry_mdt_tubes_EI():

    livetime    = 1300e-9
    mm2_to_cm2  = (1/10.0)*(1/10.0)
    muonrawhits = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geometry    = os.path.join(muonrawhits, "data/geometry/mdt_tubes_EI.txt")

    chambers = []
    radii    = []
    areas    = []
    times    = []

    for line in open(geometry).readlines():
        line = line.strip()
        if not line:
            continue
        _, chamber, ml, layer, tube, r, radius, length, area = line.split()

        chambers.append(chamber)
        radii.append(float(r))
        areas.append(float(area)*mm2_to_cm2)
        times.append(float(livetime))

    return chambers, radii, areas, times

def geometry_csc_strips():

    livetime    = 140e-9
    mm2_to_cm2   = (1/10.0)*(1/10.0)
    muonrawhits = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    geometry    = os.path.join(muonrawhits, "data/geometry/csc_strips.txt")

    chambers = []
    radii    = []
    areas    = []
    times    = []

    for line in open(geometry).readlines():
        line = line.strip()
        if not line:
            continue
        _, chamber, layer, strip, r, length, width, area = line.split()

        chambers.append(chamber)
        radii.append(float(r))
        areas.append(float(area)*mm2_to_cm2)
        times.append(float(livetime))

    return chambers, radii, areas, times

if __name__ == "__main__":
    main()
