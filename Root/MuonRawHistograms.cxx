#include "MuonRawAnalysis/MuonRawHistograms.h"

#include <iostream>
#include <vector>
#include <string>

#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>

MuonRawHistograms::MuonRawHistograms(){
    
    int x = 1;
    std::cout << " FUUUUCK " << x << std::endl;

}

MuonRawHistograms::~MuonRawHistograms(){}

int MuonRawHistograms::initialize(){

    file = TFile::Open("/n/atlasfs/atlasdata/tuna/MuonRawHits/ntuples-2015-11-08-09h00m45s/00281143/ntuple_0000.root");
    if (!file){
        std::cout << "FATAL MuonRawHistograms::initialize: no file" << std::endl;
        return 1;
    }
    else{
        std::cout << "file " << std::endl;
    }

    tree = (TTree*)(file->Get("physics"));
    if (!tree){
        std::cout << "FATAL MuonRawHistograms::initialize: no tree" << std::endl;
        return 1;
    }
    else{
        std::cout << "tree " << tree->GetEntries() << std::endl;
    }
    
    tree->SetBranchAddress("RunNumber",           &RunNumber);
    tree->SetBranchAddress("EventNumber",         &EventNumber);
    tree->SetBranchAddress("lbn",                 &lbn);
    tree->SetBranchAddress("bcid",                &bcid);
    tree->SetBranchAddress("colliding_bunches",   &colliding_bunches);
    tree->SetBranchAddress("avgIntPerXing",       &avgIntPerXing);
    tree->SetBranchAddress("actIntPerXing",       &actIntPerXing);
    tree->SetBranchAddress("lbAverageLuminosity", &lbAverageLuminosity);
    tree->SetBranchAddress("lbLuminosityPerBCID", &lbLuminosityPerBCID);
    tree->SetBranchAddress("prescale_L1",         &prescale_L1);
    tree->SetBranchAddress("prescale_HLT",        &prescale_HLT);

    tree->SetBranchAddress("mdt_chamber_n",           &mdt_chamber_n);
    tree->SetBranchAddress("mdt_chamber_type",        &mdt_chamber_type);
    tree->SetBranchAddress("mdt_chamber_side",        &mdt_chamber_side);
    tree->SetBranchAddress("mdt_chamber_eta_station", &mdt_chamber_eta_station);
    tree->SetBranchAddress("mdt_chamber_phi_sector",  &mdt_chamber_phi_sector);

    tree->SetBranchAddress("mdt_chamber_tube_n",      &mdt_chamber_tube_n);
    tree->SetBranchAddress("mdt_chamber_tube_r",      &mdt_chamber_tube_r);
    tree->SetBranchAddress("mdt_chamber_tube_adc",    &mdt_chamber_tube_adc);

    tree->SetBranchAddress("csc_chamber_n",              &csc_chamber_n);
    tree->SetBranchAddress("csc_chamber_r",              &csc_chamber_r);
    tree->SetBranchAddress("csc_chamber_type",           &csc_chamber_type);
    tree->SetBranchAddress("csc_chamber_side",           &csc_chamber_side);
    tree->SetBranchAddress("csc_chamber_phi_sector",     &csc_chamber_phi_sector);

    tree->SetBranchAddress("csc_chamber_cluster_n",      &csc_chamber_cluster_n);
    tree->SetBranchAddress("csc_chamber_cluster_r",      &csc_chamber_cluster_r);
    tree->SetBranchAddress("csc_chamber_cluster_rmax",   &csc_chamber_cluster_rmax);
    tree->SetBranchAddress("csc_chamber_cluster_qsum",   &csc_chamber_cluster_qsum);
    tree->SetBranchAddress("csc_chamber_cluster_qmax",   &csc_chamber_cluster_qmax);
    tree->SetBranchAddress("csc_chamber_cluster_strips", &csc_chamber_cluster_strips);

    std::string name  = "hits_vs_lumi_mdt_full_00281143";
    std::string title = "fuckboy";
    int nbins = 200;
    float xlo = 0;
    float xhi = 6;
    hits_vs_lumi_mdt_full = new TH1F(name.c_str(), title.c_str(), nbins, xlo, xhi);

    return 0;
}

int MuonRawHistograms::execute(){

    int ent           = 0;
    int ch            = 0;
    int hits_mdt_full = 0;

    int entries = 100; // (int)(tree->GetEntries());

    for (int ent = 1; ent < entries; ++ent){

        tree->GetEntry(ent);

        hits_mdt_full = 0;

        for (ch = 0; ch < mdt_chamber_n; ++ch){

            hits_mdt_full += mdt_chamber_tube_n->at(ch);

        }
        
        hits_vs_lumi_mdt_full->Fill(lbAverageLuminosity/1000.0, hits_mdt_full*prescale_HLT);

        std::cout << mdt_chamber_n << " fuckos " << mdt_chamber_tube_n->size() << std::endl;

    }

    return 0;
}

int MuonRawHistograms::finalize(){

    return 0;
}

