# MuonRawAnalysis

A rootcore package for turning MuonRawHits ntuples into plots.

    batch_dir="/n/atlasfs/atlasdata/tuna/MuonRawHits/batch-2016-02-01-11h04m18s"
    time python scripts/hists.py --input=${batch_dir}/00*/*/ntuple*.root --cpu=14

