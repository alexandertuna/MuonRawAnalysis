import ROOT
ROOT.gROOT.Macro("$ROOTCOREDIR/scripts/load_packages.C")
ROOT.gROOT.SetBatch()

inp    = "/n/atlasfs/atlasdata/tuna/MuonRawHits/batch-2016-01-31-17h22m18s/00284285/secondhalf/ntuple.2016-01-31-17h29m54s.Run00284285_2.root"
output = "count_tubes.txt"

entries = 10000

job = ROOT.CountTubes(inp, output)
job.initialize()
# job.execute(entries)
job.finalize()

counts = {}
for line in open(output).readlines():
    if not line:
        continue
    tube, count = line.split()
    counts[tube] = int(count)

tubes = sorted(counts.keys(), key=counts.get, reverse=True)
for tube in tubes[:200]:
    print tube, counts[tube]

occupancy = ROOT.TH1F("hist", ";occupancy [%];tubes;", 200, 0, 20)
occupancy.Sumw2()
for line in open(output).readlines():
    if not line:
        continue
    tube, count = line.split()
    _ = occupancy.Fill(100*float(count)/entries)

canvas = ROOT.TCanvas("occupancy", "occupancy", 800, 800)
canvas.Draw()
occupancy.Draw("psame")
canvas.SaveAs(canvas.GetName()+".pdf")

