#ifndef MUONRAWHITS_MUONRAWHISTOGRAMS_H
#define MUONRAWHITS_MUONRAWHISTOGRAMS_H

#include <vector>
#include <cstring>
#include <string>
#include <chrono>

#include <TFile.h>
#include <TDirectory.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH2F.h>

class MuonRawHistograms {

 public:

    MuonRawHistograms();
    MuonRawHistograms(std::string ipath, std::string opath);
    ~MuonRawHistograms();

    int initialize();
    int execute(int ents = -1);
    int finalize();

    std::string  input_path = "";
    std::string output_path = "";
    std::string run         = "";

    void announce();
    void initialize_branches();
    void initialize_histograms();

    int ybin(std::string chamber_type);

    TFile* file;
    TTree* tree;
    int entries;

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

    std::chrono::time_point<std::chrono::system_clock> time_start, time_end;
    std::chrono::duration<double> elapsed_seconds;

    int eta   = 0;
    int eta_n = 8;

    // inputs
    int mdt_chamber_n;
    std::vector<std::string>* mdt_chamber_type          = 0; //!
    std::vector<std::string>* mdt_chamber_side          = 0; //!
    std::vector<int>*         mdt_chamber_eta_station   = 0; //!
    std::vector<int>*         mdt_chamber_phi_sector    = 0; //!

    std::vector<int>*              mdt_chamber_tube_n       = 0; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_r       = 0; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_adc     = 0; //!
    std::vector<int>*              mdt_chamber_tube_n_adc50 = 0; //!

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
    std::vector<int>*              csc_chamber_cluster_n_qmax25    = 0; //!

    // outputs
    TH1F* evts = 0;

    TH1F* evts_vs_bcid          = 0;
    TH1F* lumi_vs_bcid          = 0;
    TH1F* hits_vs_bcid_mdt_full = 0;
    TH1F* hits_vs_bcid_csc_full = 0;

    TH2F* hits_vs_lumi_vs_evts_mdt_full = 0;
    TH2F* hits_vs_lumi_vs_evts_mdt_EIL1 = 0;
    TH2F* hits_vs_lumi_vs_evts_mdt_EIL2 = 0;
    TH2F* hits_vs_lumi_vs_evts_mdt_EIS1 = 0;
    TH2F* hits_vs_lumi_vs_evts_mdt_EIS2 = 0;
    TH2F* hits_vs_lumi_vs_evts_csc_full = 0;
    TH2F* hits_vs_lumi_vs_evts_csc_CSL1 = 0;
    TH2F* hits_vs_lumi_vs_evts_csc_CSS1 = 0;

    TH2F* hits_vs_mu_vs_evts_mdt_full = 0;
    TH2F* hits_vs_mu_vs_evts_mdt_EIL1 = 0;
    TH2F* hits_vs_mu_vs_evts_mdt_EIL2 = 0;
    TH2F* hits_vs_mu_vs_evts_mdt_EIS1 = 0;
    TH2F* hits_vs_mu_vs_evts_mdt_EIS2 = 0;
    TH2F* hits_vs_mu_vs_evts_csc_full = 0;
    TH2F* hits_vs_mu_vs_evts_csc_CSL1 = 0;
    TH2F* hits_vs_mu_vs_evts_csc_CSS1 = 0;

    TH1F* hits_vs_r_L     = 0;
    TH1F* hits_vs_r_S     = 0;
    TH1F* hits_vs_r_adc_L = 0;
    TH1F* hits_vs_r_adc_S = 0;

    TH1F* hits_vs_r_L_01 = 0;
    TH1F* hits_vs_r_L_03 = 0;
    TH1F* hits_vs_r_L_05 = 0;
    TH1F* hits_vs_r_L_07 = 0;
    TH1F* hits_vs_r_L_09 = 0;
    TH1F* hits_vs_r_L_11 = 0;
    TH1F* hits_vs_r_L_13 = 0;
    TH1F* hits_vs_r_L_15 = 0;

    TH1F* hits_vs_r_S_02 = 0;
    TH1F* hits_vs_r_S_04 = 0;
    TH1F* hits_vs_r_S_06 = 0;
    TH1F* hits_vs_r_S_08 = 0;
    TH1F* hits_vs_r_S_10 = 0;
    TH1F* hits_vs_r_S_12 = 0;
    TH1F* hits_vs_r_S_14 = 0;
    TH1F* hits_vs_r_S_16 = 0;

    TH2F* hits_vs_region_L = 0;
    TH2F* hits_vs_region_S = 0;

    std::vector<TH1F*> histograms1D;
    std::vector<TH2F*> histograms2D;

    TFile*      output;
    TDirectory* outdir;

};

#endif
