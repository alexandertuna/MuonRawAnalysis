# MuonRawAnalysis

A rootcore package for turning MuonRawHits ntuples into plots.

    batch_dir="/n/atlasfs/atlasdata/tuna/MuonRawHits/batch-2015-12-15-14h55m43s"
    time python scripts/hists.py --input=${batch_dir}/00*/*/ntuple*.root --cpu=14

