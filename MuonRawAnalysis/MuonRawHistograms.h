#ifndef MUONRAWHITS_MUONRAWHISTOGRAMS_H
#define MUONRAWHITS_MUONRAWHISTOGRAMS_H

#include <vector>
#include <string>

#include <TFile.h>
#include <TTree.h>
#include <TH1F.h>

class MuonRawHistograms {

 public:

    MuonRawHistograms();
    ~MuonRawHistograms();

    int initialize();
    int execute();
    int finalize();

    TFile *file;
    TTree *tree;

    int RunNumber; 
    int EventNumber;
    int lbn;
    int bcid;
    int colliding_bunches;
    double avgIntPerXing;
    double actIntPerXing;
    double lbAverageLuminosity;
    double lbLuminosityPerBCID;
    double prescale_L1;
    double prescale_HLT;

    // inputs
    int mdt_chamber_n;
    std::vector<std::string>* mdt_chamber_type          = 0; //!
    std::vector<std::string>* mdt_chamber_side          = 0; //!
    std::vector<int>*         mdt_chamber_eta_station   = 0; //!
    std::vector<int>*         mdt_chamber_phi_sector    = 0; //!

    std::vector<int>*              mdt_chamber_tube_n   = 0; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_r   = 0; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_adc = 0; //!

    int csc_chamber_n;
    std::vector<int>*         csc_chamber_r          = 0; //!
    std::vector<std::string>* csc_chamber_type       = 0; //!
    std::vector<std::string>* csc_chamber_side       = 0; //!
    std::vector<int>*         csc_chamber_phi_sector = 0; //!

    std::vector<int>*              csc_chamber_cluster_n           = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_r           = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_rmax        = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_qsum        = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_qmax        = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_strips      = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_measuresphi = 0; //!

    // outputs
    TH1F* hits_vs_lumi_mdt_full = 0;
    TH1F* hits_vs_lumi_mdt_EIL1 = 0;
    TH1F* hits_vs_lumi_mdt_EIL2 = 0;
    TH1F* hits_vs_lumi_mdt_EIS1 = 0;
    TH1F* hits_vs_lumi_mdt_EIS2 = 0;
    TH1F* hits_vs_lumi_csc_L    = 0;
    TH1F* hits_vs_lumi_csc_S    = 0;

};

#endif
