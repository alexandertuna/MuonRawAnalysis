#ifndef MUONRAWHITS_MUONRAWHISTOGRAMS_H
#define MUONRAWHITS_MUONRAWHISTOGRAMS_H

#include <vector>
#include <string>

#include <TFile.h>
#include <TTree.h>
#include <TTreeReader.h>
#include <TTreeReaderValue.h>
#include <TTreeReaderArray.h>

#include <TH1.h>

class MuonRawHistograms {

 public:

    MuonRawHistograms();
    ~MuonRawHistograms();

    int initialize();
    int execute();
    int finalize();

    TFile *file;
    TTreeReader treereader;
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

    int mdt_chamber_n;
    std::vector<std::string>* mdt_chamber_type; //!
    std::vector<std::string>* mdt_chamber_side; //!
    std::vector<int>*         mdt_chamber_eta_station; //!
    std::vector<int>*         mdt_chamber_phi_sector; //!

    std::vector<int>*              mdt_chamber_tube_n; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_r; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_adc; //!

    int csc_chamber_n;
    std::vector<int>*         csc_chamber_r; //!
    std::vector<std::string>* csc_chamber_type; //!
    std::vector<std::string>* csc_chamber_side; //!
    std::vector<int>*         csc_chamber_phi_sector; //!

    std::vector<int>*              csc_chamber_cluster_n; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_r; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_rmax; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_qsum; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_qmax; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_strips; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_measuresphi; //!

};

#endif
