import math
import ROOT, rootlogon
ROOT.gROOT.SetBatch()
# ROOT.gROOT.Macro("$ROOTCOREDIR/scripts/load_packages.C")

ROOT.gStyle.SetPadRightMargin(0.06)

inp    = "/n/atlasfs/atlasdata/tuna/MuonRawHits/batch-2016-01-31-17h22m18s/00284285/secondhalf/ntuple.2016-01-31-17h29m54s.Run00284285_2.root"
output = "count_tubes.txt"

entries = 10000

# job = ROOT.CountTubes(inp, output)
# job.initialize()
# job.execute(entries)
# job.finalize()

counts = {}
for line in open(output).readlines():
    if not line:
        continue
    tube, count = line.split()
    counts[tube] = int(count)

def show_overflow(hist):
    """ Show overflow and underflow on a TH1. h/t Josh """

    nbins          = hist.GetNbinsX()
    underflow      = hist.GetBinContent(   0   )
    underflowerror = hist.GetBinError  (   0   )
    overflow       = hist.GetBinContent(nbins+1)
    overflowerror  = hist.GetBinError  (nbins+1)
    firstbin       = hist.GetBinContent(   1   )
    firstbinerror  = hist.GetBinError  (   1   )
    lastbin        = hist.GetBinContent( nbins )
    lastbinerror   = hist.GetBinError  ( nbins )

    if underflow != 0 :
        newcontent = underflow + firstbin
        if firstbin == 0 :
            newerror = underflowerror
        else:
            newerror = math.sqrt( underflowerror * underflowerror + firstbinerror * firstbinerror )
        hist.SetBinContent(1, newcontent)
        hist.SetBinError  (1, newerror)

    if overflow != 0 :
        newcontent = overflow + lastbin
        if lastbin == 0 :
            newerror = overflowerror
        else:
            newerror = math.sqrt( overflowerror * overflowerror + lastbinerror * lastbinerror )
        hist.SetBinContent(nbins, newcontent)
        hist.SetBinError  (nbins, newerror)

ignore_template = 'if (chamber == "%s" && ml == %s && layer == %s && tube == %s) return 1;'

tubes = sorted(counts.keys(), key=counts.get, reverse=True)
tubes = tubes[:300]
tubes = sorted(tubes)
for tube in tubes:
    print tube, float(counts[tube])/100
    if "total" in tube:
        continue
    if float(counts[tube])/100 < 10:
        continue
    chamber, id = tube.split("_")
    ml, layer, tube = id[0], id[1], id[2:]
    print ignore_template % (chamber, ml, layer, tube)

print
print
occupancy = ROOT.TH1F("hist", ";occupancy [%];MDT tubes;", 100, 0, 20)
occupancy.Sumw2()
occupancy.SetLineColor(ROOT.kBlack)
occupancy.SetLineWidth(2)
occupancy.SetFillColor(19)

for line in open(output).readlines():
    if not line:
        continue
    tube, count = line.split()
    occup = 100*float(count)/entries
    _ = occupancy.Fill(occup)

show_overflow(occupancy)

canvas = ROOT.TCanvas("occupancy", "occupancy", 800, 800)
canvas.Draw()
occupancy.Draw("histsame")
ROOT.gPad.SetLogy()

cut_verti = ROOT.TLine( 10,   0, 10, 500)
cut_horiz = ROOT.TArrow(10, 200, 11, 200, 0.01, "|>")
for line in [cut_verti, cut_horiz]:
    line.SetLineColor(ROOT.kRed)
    if isinstance(line, ROOT.TArrow):
        line.SetFillColor(ROOT.kRed)
    line.SetLineWidth(2)
    line.SetLineStyle(1)
    line.Draw()

xcoord, ycoord = 0.65, 0.80
atlas = ROOT.TLatex(xcoord, ycoord,      "ATLAS Internal")
data  = ROOT.TLatex(xcoord, ycoord-0.06, "13 TeV, Run 284285")
logos = [atlas, data]
for logo in logos:
    logo.SetTextSize(0.040)
    logo.SetTextFont(42)
    logo.SetTextAlign(22)
    logo.SetNDC()
    logo.Draw()


canvas.SaveAs(canvas.GetName()+".pdf")

