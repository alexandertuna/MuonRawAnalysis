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
    int sign(std::string chamber_side);
    std::string phi_string(int phi_sector);

    std::string chamber = "";
    TH2F* hist = 0;

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

    std::vector<std::string> chamber_types = {"BIL", "BML", "BOL", "EIL", "EML", "EOL",
                                              "BIS", "BMS", "BOS", "EIS", "EMS", "EOS",
                                              "BEE", "BIM", "BIR", "BME", "BMF", "BOF", "BOG", 
                                              "EEL", "EES", "CSL", "CSS"};
    std::vector<std::string> chamber_sides = {"A", "B", "C"};
    std::vector<std::string> phi_sectors_L = {"01", "03", "05", "07", "09", "11", "13", "15"};
    std::vector<std::string> phi_sectors_S = {"02", "04", "06", "08", "10", "12", "14", "16"};
    std::vector<std::string> phi_sectors   = {};

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
    std::vector<std::vector<int>>* csc_chamber_cluster_qleft       = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_qright      = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_strips      = 0; //!
    std::vector<std::vector<int>>* csc_chamber_cluster_measuresphi = 0; //!
    std::vector<int>*              csc_chamber_cluster_n_qmax100   = 0; //!
    std::vector<int>*              csc_chamber_cluster_n_notecho   = 0; //!

    // outputs
    TH1F* evts = 0;

    TH1F* evts_vs_lumi          = 0;
    TH1F* evts_vs_bcid          = 0;
    TH1F* lumi_vs_bcid          = 0;
    TH1F* hits_vs_bcid_mdt_full = 0;
    TH1F* hits_vs_bcid_csc_full = 0;

    TH2F* hits_raw_vs_lumi_vs_evts_mdt_full = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EIL1 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EIL2 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EIS1 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EIS2 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EML1 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EML2 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EMS1 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_EMS2 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_BIS7 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_mdt_BIS8 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_csc_full = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_csc_CSL1 = 0;
    TH2F* hits_raw_vs_lumi_vs_evts_csc_CSS1 = 0;

    TH2F* hits_adc_vs_lumi_vs_evts_mdt_full = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EIL1 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EIL2 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EIS1 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EIS2 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EML1 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EML2 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EMS1 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_EMS2 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_BIS7 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_mdt_BIS8 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_csc_full = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_csc_CSL1 = 0;
    TH2F* hits_adc_vs_lumi_vs_evts_csc_CSS1 = 0;

    TH2F* hits_raw_vs_mu_vs_evts_mdt_full = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EIL1 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EIL2 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EIS1 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EIS2 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EML1 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EML2 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EMS1 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_EMS2 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_BIS7 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_mdt_BIS8 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_csc_full = 0;
    TH2F* hits_raw_vs_mu_vs_evts_csc_CSL1 = 0;
    TH2F* hits_raw_vs_mu_vs_evts_csc_CSS1 = 0;

    TH2F* hits_adc_vs_mu_vs_evts_mdt_full = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EIL1 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EIL2 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EIS1 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EIS2 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EML1 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EML2 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EMS1 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_EMS2 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_BIS7 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_mdt_BIS8 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_csc_full = 0;
    TH2F* hits_adc_vs_mu_vs_evts_csc_CSL1 = 0;
    TH2F* hits_adc_vs_mu_vs_evts_csc_CSS1 = 0;

    TH1F* hits_raw_vs_r_EIL = 0;
    TH1F* hits_raw_vs_r_EIS = 0;
    TH1F* hits_raw_vs_r_EML = 0;
    TH1F* hits_raw_vs_r_EMS = 0;
    TH1F* hits_adc_vs_r_EIL = 0;
    TH1F* hits_adc_vs_r_EIS = 0;
    TH1F* hits_adc_vs_r_EML = 0;
    TH1F* hits_adc_vs_r_EMS = 0;

    std::map<std::string, TH1F*> hits_raw_vs_r;
    std::map<std::string, TH1F*> hits_adc_vs_r;

    TH2F* hits_raw_vs_region_L = 0;
    TH2F* hits_raw_vs_region_S = 0;
    TH2F* hits_adc_vs_region_L = 0;
    TH2F* hits_adc_vs_region_S = 0;

    std::vector<TH1F*> histograms1D;
    std::vector<TH2F*> histograms2D;

    TFile*      output;
    TDirectory* outdir;

};

#endif
