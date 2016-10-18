#include "MuonRawAnalysis/MuonRawHistograms.h"

#include <iostream>
#include <vector>
#include <string>
#include <chrono>

#include <TFile.h>
#include <TDirectory.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH2F.h>

MuonRawHistograms::MuonRawHistograms(std::string ipath, std::string opath){
    input_path  = ipath;
    output_path = opath;
}

MuonRawHistograms::~MuonRawHistograms(){}

int MuonRawHistograms::initialize(){

    file = TFile::Open(input_path.c_str());
    if (!file)
        std::cout << "\n FATAL FUCK MuonRawHistograms::initialize: no file \n" << std::endl;

    tree = (TTree*)(file->Get("physics"));
    if (!tree)
        std::cout << "\n FATAL FUCK MuonRawHistograms::initialize: no tree \n" << std::endl;

    announce();
    initialize_branches();
    initialize_histograms();
    
    return 0;
}

int MuonRawHistograms::execute(int ents){

    int ent = 0;
    int ch  = 0;
    int hit = 0;
    int hit_rad  = 0;
    int hit_adc  = 0;
    int pass_adc = 0;

    int hits_raw_mdt_full = 0;
    int hits_adc_mdt_full = 0;
    std::map<std::string, int> hits_raw;
    std::map<std::string, int> hits_adc;

    int hits_raw_csc_full = 0;
    int hits_adc_csc_full = 0;

    std::string chamber_side     = "";
    std::string chamber_type     = "";
    std::string chamber_type_mdt = "";
    std::string chamber_phi_str  = "";
    int         chamber_phi      = 0;
    int         chamber_eta      = 0;
    int         chamber_hits_raw = 0;
    int         chamber_hits_adc = 0;

    float lumi = 0.0;
    
    int tree_entries = (int)(tree->GetEntries());
    if (ents < 0 || ents > tree_entries)
        entries = tree_entries;
    else
        entries = ents;

    time_start = std::chrono::system_clock::now();

    phi_sectors.insert(phi_sectors.end(), phi_sectors_L.begin(), phi_sectors_L.end());
    phi_sectors.insert(phi_sectors.end(), phi_sectors_S.begin(), phi_sectors_S.end());

    for (ent = 1; ent < entries; ++ent){

        tree->GetEntry(ent);

        if (ent % 2000 == 0) {
            printf("%8i / %8i \n", ent, entries);
            printf("\033[F\033[J");
        } 

        lumi = lbAverageLuminosity/1000.0;

        hits_raw_mdt_full = 0; hits_adc_mdt_full = 0;
        hits_adc_csc_full = 0; hits_raw_csc_full = 0;
        
        for (auto type: chamber_types)
            for (auto side: chamber_sides)
                for (eta = 1; eta <= eta_n; ++eta){

                    hits_raw[type + std::to_string(eta) + side] = 0;
                    hits_adc[type + std::to_string(eta) + side] = 0;
                    
                    if (type=="EIL" || type=="EIS" || 
                        type=="CSL" || type=="CSS"
                        )
                        for (auto phi: phi_sectors){
                            hits_raw[type + std::to_string(eta) + side + phi] = 0;
                            hits_adc[type + std::to_string(eta) + side + phi] = 0;
                        }
                }

        for (ch = 0; ch < mdt_chamber_n; ++ch){

            chamber_hits_raw = mdt_chamber_tube_n->at(ch);
            chamber_hits_adc = mdt_chamber_tube_n_adc50->at(ch);
            chamber_eta      = mdt_chamber_eta_station->at(ch);
            chamber_phi      = mdt_chamber_phi_sector->at(ch);
            chamber_type     = mdt_chamber_type->at(ch);
            chamber_side     = mdt_chamber_side->at(ch);
            chamber_phi_str  = phi_string(chamber_phi);

            hits_raw_mdt_full += chamber_hits_raw;
            hits_adc_mdt_full += chamber_hits_adc;

            hits_raw[chamber_type + std::to_string(chamber_eta) + chamber_side] += chamber_hits_raw;
            hits_adc[chamber_type + std::to_string(chamber_eta) + chamber_side] += chamber_hits_adc;

            if ((chamber_type=="EIL" || chamber_type=="EIS" || chamber_type=="EML" || chamber_type=="EMS") && (chamber_eta==1 || chamber_eta==2)){
                for (hit = 0; hit < chamber_hits_raw; ++hit){

                    hit_rad  = (mdt_chamber_tube_r->at(ch)).at(hit);
                    hit_adc  = (mdt_chamber_tube_adc->at(ch)).at(hit);
                    pass_adc = (hit_adc > 50);

                    if (chamber_type=="EIL" && abs(chamber_eta) <= 2){ 
                        hits_raw_vs_lumi_vs_r_L->Fill(lumi,          hit_rad, prescale_HLT);
                        hits_raw_vs_acmu_vs_r_L->Fill(actIntPerXing, hit_rad, prescale_HLT);
                        hits_raw_vs_avmu_vs_r_L->Fill(avgIntPerXing, hit_rad, prescale_HLT);
                    }
                    if (chamber_type=="EIS" && abs(chamber_eta) <= 2){
                        hits_raw_vs_lumi_vs_r_S->Fill(lumi,          hit_rad, prescale_HLT);
                        hits_raw_vs_acmu_vs_r_S->Fill(actIntPerXing, hit_rad, prescale_HLT);
                        hits_raw_vs_avmu_vs_r_S->Fill(avgIntPerXing, hit_rad, prescale_HLT);
                    }

                    if (chamber_type=="EIL" || chamber_type=="EIS")
                        hits_raw_vs_r[chamber_type+"_"+chamber_phi_str]->Fill(hit_rad, prescale_HLT);

                    if (chamber_type=="EIL"){
                        hits_raw_vs_r_EIL->Fill(hit_rad, prescale_HLT);
                        if (pass_adc)
                            hits_adc_vs_r_EIL->Fill(hit_rad, prescale_HLT);
                    }
                    if (chamber_type=="EIS"){
                        hits_raw_vs_r_EIS->Fill(hit_rad, prescale_HLT);
                        if (pass_adc)
                            hits_adc_vs_r_EIS->Fill(hit_rad, prescale_HLT);
                    }
                    if (chamber_type=="EML"){
                        hits_raw_vs_r_EML->Fill(hit_rad, prescale_HLT);
                        if (pass_adc)
                            hits_adc_vs_r_EML->Fill(hit_rad, prescale_HLT);
                    }
                    if (chamber_type=="EMS"){
                        hits_raw_vs_r_EMS->Fill(hit_rad, prescale_HLT);
                        if (pass_adc)
                            hits_adc_vs_r_EMS->Fill(hit_rad, prescale_HLT);
                    }
                }
            }
        }
        
        for (ch = 0; ch < csc_chamber_n; ++ch){

            chamber_type     = csc_chamber_type->at(ch);
            chamber_type_mdt = chamber_type=="CSL" ? "EIL" : "EIS";
            chamber_side     = csc_chamber_side->at(ch);
            chamber_phi      = csc_chamber_phi_sector->at(ch);
            chamber_eta      = 1;
            chamber_hits_raw = csc_chamber_cluster_n->at(ch);
            chamber_hits_adc = csc_chamber_cluster_n_qmax100->at(ch);
            chamber_phi_str  = phi_string(chamber_phi);

            hits_raw_csc_full += chamber_hits_raw;
            hits_adc_csc_full += chamber_hits_adc;

            hits_raw[chamber_type + std::to_string(chamber_eta) + chamber_side] += chamber_hits_raw;
            hits_adc[chamber_type + std::to_string(chamber_eta) + chamber_side] += chamber_hits_adc;

            for (hit = 0; hit < chamber_hits_raw; ++hit){

                hit_rad  = (csc_chamber_cluster_r->at(ch)).at(hit);
                hit_adc  = (csc_chamber_cluster_qmax->at(ch)).at(hit);
                pass_adc = (hit_adc > 100*1000);

                hits_raw_vs_r[chamber_type_mdt+"_"+chamber_phi_str]->Fill(hit_rad, prescale_HLT);

                if (chamber_type=="CSL"){
                    hits_raw_vs_lumi_vs_r_L->Fill(lumi,          hit_rad, prescale_HLT);
                    hits_raw_vs_acmu_vs_r_L->Fill(actIntPerXing, hit_rad, prescale_HLT);
                    hits_raw_vs_avmu_vs_r_L->Fill(avgIntPerXing, hit_rad, prescale_HLT);
                }
                if (chamber_type=="CSS"){
                    hits_raw_vs_lumi_vs_r_S->Fill(lumi,          hit_rad, prescale_HLT);
                    hits_raw_vs_acmu_vs_r_S->Fill(actIntPerXing, hit_rad, prescale_HLT);
                    hits_raw_vs_avmu_vs_r_S->Fill(avgIntPerXing, hit_rad, prescale_HLT);
                }

                if (chamber_type=="CSL"){
                    hits_raw_vs_r_EIL->Fill(hit_rad, prescale_HLT);
                    if (pass_adc)
                        hits_adc_vs_r_EIL->Fill(hit_rad, prescale_HLT);
                }
                if (chamber_type=="CSS"){
                    hits_raw_vs_r_EIS->Fill(hit_rad, prescale_HLT);
                    if (pass_adc)
                        hits_adc_vs_r_EIS->Fill(hit_rad, prescale_HLT);
                }
            }
        }

        evts->Fill(1, prescale_HLT);

        lumi = lbAverageLuminosity/1000.0;
        hits_raw_vs_lumi_vs_evts_mdt_full->Fill(lumi, hits_raw_mdt_full,                   prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EIL1->Fill(lumi, hits_raw["EIL1A"]+hits_raw["EIL1C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EIL2->Fill(lumi, hits_raw["EIL2A"]+hits_raw["EIL2C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EIS1->Fill(lumi, hits_raw["EIS1A"]+hits_raw["EIS1C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EIS2->Fill(lumi, hits_raw["EIS2A"]+hits_raw["EIS2C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EML1->Fill(lumi, hits_raw["EML1A"]+hits_raw["EML1C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EML2->Fill(lumi, hits_raw["EML2A"]+hits_raw["EML2C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EMS1->Fill(lumi, hits_raw["EMS1A"]+hits_raw["EMS1C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_EMS2->Fill(lumi, hits_raw["EMS2A"]+hits_raw["EMS2C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_BIS7->Fill(lumi, hits_raw["BIS7A"]+hits_raw["BIS7C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_mdt_BIS8->Fill(lumi, hits_raw["BIS8A"]+hits_raw["BIS8C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_csc_full->Fill(lumi, hits_raw_csc_full,                   prescale_HLT);
        hits_raw_vs_lumi_vs_evts_csc_CSL1->Fill(lumi, hits_raw["CSL1A"]+hits_raw["CSL1C"], prescale_HLT);
        hits_raw_vs_lumi_vs_evts_csc_CSS1->Fill(lumi, hits_raw["CSS1A"]+hits_raw["CSS1C"], prescale_HLT);

        hits_adc_vs_lumi_vs_evts_mdt_full->Fill(lumi, hits_adc_mdt_full,                   prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EIL1->Fill(lumi, hits_adc["EIL1A"]+hits_adc["EIL1C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EIL2->Fill(lumi, hits_adc["EIL2A"]+hits_adc["EIL2C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EIS1->Fill(lumi, hits_adc["EIS1A"]+hits_adc["EIS1C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EIS2->Fill(lumi, hits_adc["EIS2A"]+hits_adc["EIS2C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EML1->Fill(lumi, hits_adc["EML1A"]+hits_adc["EML1C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EML2->Fill(lumi, hits_adc["EML2A"]+hits_adc["EML2C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EMS1->Fill(lumi, hits_adc["EMS1A"]+hits_adc["EMS1C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_EMS2->Fill(lumi, hits_adc["EMS2A"]+hits_adc["EMS2C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_BIS7->Fill(lumi, hits_adc["BIS7A"]+hits_adc["BIS7C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_mdt_BIS8->Fill(lumi, hits_adc["BIS8A"]+hits_adc["BIS8C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_csc_full->Fill(lumi, hits_adc_csc_full,                   prescale_HLT);
        hits_adc_vs_lumi_vs_evts_csc_CSL1->Fill(lumi, hits_adc["CSL1A"]+hits_adc["CSL1C"], prescale_HLT);
        hits_adc_vs_lumi_vs_evts_csc_CSS1->Fill(lumi, hits_adc["CSS1A"]+hits_adc["CSS1C"], prescale_HLT);

        for (auto type: chamber_types)
            for (eta = 1; eta <= eta_n; ++eta){
                
                chamber = type + std::to_string(eta);
                hits_raw_vs_lumi[chamber]->Fill(lumi, (hits_raw[chamber+"A"]+hits_raw[chamber+"C"]) * prescale_HLT);
                hits_adc_vs_lumi[chamber]->Fill(lumi, (hits_adc[chamber+"A"]+hits_adc[chamber+"C"]) * prescale_HLT);

            }

        for (auto type: chamber_types)
            for (auto side: chamber_sides)
                for (eta = 1; eta <= eta_n; ++eta){

                    // e.g., EIL1A
                    chamber = type + std::to_string(eta) + side;

                    hist = (type.find("L") != std::string::npos) ? hits_raw_vs_region_L : hits_raw_vs_region_S;
                    hist->Fill(eta*sign(side), ybin(type), prescale_HLT*(float)(hits_raw[chamber]));

                    hist = (type.find("L") != std::string::npos) ? hits_adc_vs_region_L : hits_adc_vs_region_S;
                    hist->Fill(eta*sign(side), ybin(type), prescale_HLT*(float)(hits_adc[chamber]));
                }

        evts_vs_lumi->Fill(         lumi, prescale_HLT);
        evts_vs_acmu->Fill(actIntPerXing, prescale_HLT);
        evts_vs_avmu->Fill(avgIntPerXing, prescale_HLT);
        evts_vs_bcid->Fill(         bcid, prescale_HLT);
        lumi_vs_bcid->Fill(         bcid, prescale_HLT*lbLuminosityPerBCID);
        hits_vs_bcid_mdt_full->Fill(bcid, prescale_HLT*hits_raw_mdt_full);
        hits_vs_bcid_csc_full->Fill(bcid, prescale_HLT*hits_raw_csc_full);
    }

    time_end = std::chrono::system_clock::now();
    elapsed_seconds = time_end - time_start;

    printf("%8i / %8i in %.2f s = %.2f Hz\n", ent, entries, elapsed_seconds.count(), (float)(entries) / elapsed_seconds.count());

    return 0;
}

int MuonRawHistograms::finalize(){

    output = TFile::Open(output_path.c_str(), "recreate");
    outdir = output->mkdir(run.c_str());
    outdir->cd();

    for (auto hist: histograms1D) hist->Write();
    for (auto hist: histograms2D) hist->Write();
    
    output->Close();
    
    return 0;
}

void MuonRawHistograms::announce(){
    
    std::cout << std::endl;
    std::cout << "   input | " <<  input_path        << std::endl;
    std::cout << "  output | " << output_path        << std::endl;
    std::cout << " entries | " << tree->GetEntries() << std::endl;
    std::cout << std::endl;
}

void MuonRawHistograms::initialize_branches(){

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

    tree->SetBranchAddress("mdt_chamber_tube_n",       &mdt_chamber_tube_n);
    tree->SetBranchAddress("mdt_chamber_tube_r",       &mdt_chamber_tube_r);
    tree->SetBranchAddress("mdt_chamber_tube_adc",     &mdt_chamber_tube_adc);
    tree->SetBranchAddress("mdt_chamber_tube_n_adc50", &mdt_chamber_tube_n_adc50);

    tree->SetBranchAddress("csc_chamber_n",              &csc_chamber_n);
    tree->SetBranchAddress("csc_chamber_r",              &csc_chamber_r);
    tree->SetBranchAddress("csc_chamber_type",           &csc_chamber_type);
    tree->SetBranchAddress("csc_chamber_side",           &csc_chamber_side);
    tree->SetBranchAddress("csc_chamber_phi_sector",     &csc_chamber_phi_sector);

    tree->SetBranchAddress("csc_chamber_cluster_n",         &csc_chamber_cluster_n);
    tree->SetBranchAddress("csc_chamber_cluster_r",         &csc_chamber_cluster_r);
    tree->SetBranchAddress("csc_chamber_cluster_rmax",      &csc_chamber_cluster_rmax);
    tree->SetBranchAddress("csc_chamber_cluster_qsum",      &csc_chamber_cluster_qsum);
    tree->SetBranchAddress("csc_chamber_cluster_qmax",      &csc_chamber_cluster_qmax);
    tree->SetBranchAddress("csc_chamber_cluster_qleft",     &csc_chamber_cluster_qleft);
    tree->SetBranchAddress("csc_chamber_cluster_qright",    &csc_chamber_cluster_qright);
    tree->SetBranchAddress("csc_chamber_cluster_strips",    &csc_chamber_cluster_strips);
    tree->SetBranchAddress("csc_chamber_cluster_n_qmax100", &csc_chamber_cluster_n_qmax100);
    tree->SetBranchAddress("csc_chamber_cluster_n_notecho", &csc_chamber_cluster_n_notecho);
}

void MuonRawHistograms::initialize_histograms(){

    tree->GetEntry(1);
    run = std::to_string(RunNumber);
    run = "00"+run;

    int xbins = 0; float xlo = 0; float xhi = 0;
    int ybins = 0; float ylo = 0; float yhi = 0;

    evts = new TH1F(("evts_"+run).c_str(), "", 1, 0, 2);
    
    xbins = 200; xlo = 0; xhi = 16;
    ybins = 200; ylo = 0;
    evts_vs_lumi                      = new TH1F(("evts_vs_lumi_"+run).c_str(),                      "", xbins, xlo, xhi);
    hits_raw_vs_lumi_vs_evts_mdt_full = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_full_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, 5000);
    hits_raw_vs_lumi_vs_evts_mdt_EIL1 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EIL1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  500);
    hits_raw_vs_lumi_vs_evts_mdt_EIL2 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EIL2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_raw_vs_lumi_vs_evts_mdt_EIS1 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EIS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  400);
    hits_raw_vs_lumi_vs_evts_mdt_EIS2 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EIS2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_raw_vs_lumi_vs_evts_mdt_EML1 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EML1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_raw_vs_lumi_vs_evts_mdt_EML2 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EML2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_raw_vs_lumi_vs_evts_mdt_EMS1 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EMS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_raw_vs_lumi_vs_evts_mdt_EMS2 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_EMS2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_raw_vs_lumi_vs_evts_mdt_BIS7 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_BIS7_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_raw_vs_lumi_vs_evts_mdt_BIS8 = new TH2F(("hits_raw_vs_lumi_vs_evts_mdt_BIS8_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  100);
    hits_raw_vs_lumi_vs_evts_csc_full = new TH2F(("hits_raw_vs_lumi_vs_evts_csc_full_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_raw_vs_lumi_vs_evts_csc_CSL1 = new TH2F(("hits_raw_vs_lumi_vs_evts_csc_CSL1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_raw_vs_lumi_vs_evts_csc_CSS1 = new TH2F(("hits_raw_vs_lumi_vs_evts_csc_CSS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);

    hits_adc_vs_lumi_vs_evts_mdt_full = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_full_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, 5000);
    hits_adc_vs_lumi_vs_evts_mdt_EIL1 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EIL1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  500);
    hits_adc_vs_lumi_vs_evts_mdt_EIL2 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EIL2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_adc_vs_lumi_vs_evts_mdt_EIS1 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EIS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  400);
    hits_adc_vs_lumi_vs_evts_mdt_EIS2 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EIS2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_adc_vs_lumi_vs_evts_mdt_EML1 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EML1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_adc_vs_lumi_vs_evts_mdt_EML2 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EML2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_adc_vs_lumi_vs_evts_mdt_EMS1 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EMS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_adc_vs_lumi_vs_evts_mdt_EMS2 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_EMS2_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  300);
    hits_adc_vs_lumi_vs_evts_mdt_BIS7 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_BIS7_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_adc_vs_lumi_vs_evts_mdt_BIS8 = new TH2F(("hits_adc_vs_lumi_vs_evts_mdt_BIS8_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  100);
    hits_adc_vs_lumi_vs_evts_csc_full = new TH2F(("hits_adc_vs_lumi_vs_evts_csc_full_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_adc_vs_lumi_vs_evts_csc_CSL1 = new TH2F(("hits_adc_vs_lumi_vs_evts_csc_CSL1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);
    hits_adc_vs_lumi_vs_evts_csc_CSS1 = new TH2F(("hits_adc_vs_lumi_vs_evts_csc_CSS1_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo,  200);

    ybins = 500; ylo = 0; yhi = 5200; hits_raw_vs_lumi_vs_r_L = new TH2F(("hits_raw_vs_lumi_vs_r_L_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);
    ybins = 500; ylo = 0; yhi = 5440; hits_raw_vs_lumi_vs_r_S = new TH2F(("hits_raw_vs_lumi_vs_r_S_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);

    for (auto type: chamber_types) 
        for (eta = 1; eta <= eta_n; ++eta){
            chamber = type + std::to_string(eta);
            hits_raw_vs_lumi[chamber] = new TH1F(("hits_raw_vs_lumi_"+chamber+"_"+run).c_str(), "", xbins, xlo, xhi);
            hits_adc_vs_lumi[chamber] = new TH1F(("hits_adc_vs_lumi_"+chamber+"_"+run).c_str(), "", xbins, xlo, xhi);
        }

    // histograms vs. actual mu
    xbins = 200; xlo = 0; xhi = 100;
    evts_vs_acmu                                              = new TH1F(("evts_vs_acmu_"+run).c_str(),            "", xbins, xlo, xhi);
    ybins = 500; ylo = 0; yhi = 5200; hits_raw_vs_acmu_vs_r_L = new TH2F(("hits_raw_vs_acmu_vs_r_L_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);
    ybins = 500; ylo = 0; yhi = 5440; hits_raw_vs_acmu_vs_r_S = new TH2F(("hits_raw_vs_acmu_vs_r_S_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);

    // histograms vs. average mu
    evts_vs_avmu                                              = new TH1F(("evts_vs_avmu_"+run).c_str(),            "", xbins, xlo, xhi);
    ybins = 500; ylo = 0; yhi = 5200; hits_raw_vs_avmu_vs_r_L = new TH2F(("hits_raw_vs_avmu_vs_r_L_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);
    ybins = 500; ylo = 0; yhi = 5440; hits_raw_vs_avmu_vs_r_S = new TH2F(("hits_raw_vs_avmu_vs_r_S_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);

    xbins = 17; xlo = -8.5; xhi = 8.5;
    ybins =  8; ylo =  0.5; yhi = 8.5;
    hits_raw_vs_region_L = new TH2F(("hits_raw_vs_region_L_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);
    hits_raw_vs_region_S = new TH2F(("hits_raw_vs_region_S_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);
    hits_adc_vs_region_L = new TH2F(("hits_adc_vs_region_L_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);
    hits_adc_vs_region_S = new TH2F(("hits_adc_vs_region_S_"+run).c_str(), "", xbins, xlo, xhi, ybins, ylo, yhi);

    for (auto type: chamber_types){
        if (type.find("L") != std::string::npos){
            hits_raw_vs_region_L->GetYaxis()->SetBinLabel(ybin(type), type.c_str());
            hits_adc_vs_region_L->GetYaxis()->SetBinLabel(ybin(type), type.c_str());
        }
        if (type.find("S") != std::string::npos){
            hits_raw_vs_region_S->GetYaxis()->SetBinLabel(ybin(type), type.c_str());
            hits_adc_vs_region_S->GetYaxis()->SetBinLabel(ybin(type), type.c_str());
        }            
    }

    xbins = 500; xlo = 0; xhi = 5200;
    hits_raw_vs_r_EIL = new TH1F(("hits_raw_vs_r_EIL_"+run).c_str(), "", xbins, xlo, xhi);
    hits_adc_vs_r_EIL = new TH1F(("hits_adc_vs_r_EIL_"+run).c_str(), "", xbins, xlo, xhi);
    for (auto phi: phi_sectors_L) hits_raw_vs_r["EIL_"+phi] = new TH1F(("hits_raw_vs_r_EIL_"+phi+"_"+run).c_str(), "", xbins, xlo, xhi);
    for (auto phi: phi_sectors_L) hits_adc_vs_r["EIL_"+phi] = new TH1F(("hits_adc_vs_r_EIL_"+phi+"_"+run).c_str(), "", xbins, xlo, xhi);
    
    xbins = 500; xlo = 0; xhi = 5440;
    hits_raw_vs_r_EIS = new TH1F(("hits_raw_vs_r_EIS_"+run).c_str(), "", xbins, xlo, xhi);
    hits_adc_vs_r_EIS = new TH1F(("hits_adc_vs_r_EIS_"+run).c_str(), "", xbins, xlo, xhi);
    for (auto phi: phi_sectors_S) hits_raw_vs_r["EIS_"+phi] = new TH1F(("hits_raw_vs_r_EIS_"+phi+"_"+run).c_str(), "", xbins, xlo, xhi);
    for (auto phi: phi_sectors_S) hits_adc_vs_r["EIS_"+phi] = new TH1F(("hits_adc_vs_r_EIS_"+phi+"_"+run).c_str(), "", xbins, xlo, xhi);

    xbins = 450; xlo = 1500; xhi = 6000;
    hits_raw_vs_r_EML = new TH1F(("hits_raw_vs_r_EML_"+run).c_str(), "", xbins, xlo, xhi);
    hits_adc_vs_r_EML = new TH1F(("hits_adc_vs_r_EML_"+run).c_str(), "", xbins, xlo, xhi);

    xbins = 450; xlo = 1500; xhi = 6000;
    hits_raw_vs_r_EMS = new TH1F(("hits_raw_vs_r_EMS_"+run).c_str(), "", xbins, xlo, xhi);
    hits_adc_vs_r_EMS = new TH1F(("hits_adc_vs_r_EMS_"+run).c_str(), "", xbins, xlo, xhi);

    xbins = 3600; xlo = 0; xhi = 3600;
    evts_vs_bcid          = new TH1F(("evts_vs_bcid_"+run).c_str(),          "", xbins, xlo, xhi);
    lumi_vs_bcid          = new TH1F(("lumi_vs_bcid_"+run).c_str(),          "", xbins, xlo, xhi);
    hits_vs_bcid_mdt_full = new TH1F(("hits_vs_bcid_mdt_full_"+run).c_str(), "", xbins, xlo, xhi);
    hits_vs_bcid_csc_full = new TH1F(("hits_vs_bcid_csc_full_"+run).c_str(), "", xbins, xlo, xhi);

    histograms1D.push_back(evts);
    histograms1D.push_back(evts_vs_lumi);
    histograms1D.push_back(evts_vs_acmu);
    histograms1D.push_back(evts_vs_avmu);
    histograms1D.push_back(evts_vs_bcid);
    histograms1D.push_back(lumi_vs_bcid);

    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_full);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EIL1);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EIL2);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EIS1);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EIS2);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EML1);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EML2);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EMS1);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_EMS2);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_BIS7);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_mdt_BIS8);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_csc_full);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_csc_CSL1);
    histograms2D.push_back(hits_raw_vs_lumi_vs_evts_csc_CSS1);

    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_full);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EIL1);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EIL2);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EIS1);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EIS2);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EML1);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EML2);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EMS1);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_EMS2);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_BIS7);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_mdt_BIS8);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_csc_full);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_csc_CSL1);
    histograms2D.push_back(hits_adc_vs_lumi_vs_evts_csc_CSS1);

    histograms2D.push_back(hits_raw_vs_region_L);
    histograms2D.push_back(hits_raw_vs_region_S);
    histograms2D.push_back(hits_adc_vs_region_L);
    histograms2D.push_back(hits_adc_vs_region_S);

    histograms2D.push_back(hits_raw_vs_lumi_vs_r_L);
    histograms2D.push_back(hits_raw_vs_lumi_vs_r_S);
    histograms2D.push_back(hits_raw_vs_acmu_vs_r_L);
    histograms2D.push_back(hits_raw_vs_acmu_vs_r_S);
    histograms2D.push_back(hits_raw_vs_avmu_vs_r_L);
    histograms2D.push_back(hits_raw_vs_avmu_vs_r_S);

    histograms1D.push_back(hits_raw_vs_r_EIL);
    histograms1D.push_back(hits_raw_vs_r_EIS);
    histograms1D.push_back(hits_raw_vs_r_EML);
    histograms1D.push_back(hits_raw_vs_r_EMS);
    histograms1D.push_back(hits_adc_vs_r_EIL);
    histograms1D.push_back(hits_adc_vs_r_EIS);
    histograms1D.push_back(hits_adc_vs_r_EML);
    histograms1D.push_back(hits_adc_vs_r_EMS);

    for (auto iter: hits_raw_vs_r) histograms1D.push_back(iter.second);
    for (auto iter: hits_adc_vs_r) histograms1D.push_back(iter.second);

    for (auto iter: hits_raw_vs_lumi) histograms1D.push_back(iter.second);
    for (auto iter: hits_adc_vs_lumi) histograms1D.push_back(iter.second);

    histograms1D.push_back(hits_vs_bcid_mdt_full);
    histograms1D.push_back(hits_vs_bcid_csc_full);

    for (auto hist: histograms1D) hist->Sumw2();
    for (auto hist: histograms2D) hist->Sumw2();

    for (auto hist: histograms1D){
        hist->SetMarkerStyle(20);
        hist->SetMarkerSize(1);
    }

}

int MuonRawHistograms::ybin(std::string chamber_type){
    if (chamber_type == "BIL" || chamber_type == "BIS") return 1;
    if (chamber_type == "BML" || chamber_type == "BMS") return 2;
    if (chamber_type == "BOL" || chamber_type == "BOS") return 3;
    if (chamber_type == "EIL" || chamber_type == "EIS") return 4;
    if (chamber_type == "EEL" || chamber_type == "EES") return 5;
    if (chamber_type == "EML" || chamber_type == "EMS") return 6;
    if (chamber_type == "EOL" || chamber_type == "EOS") return 7;
    if (chamber_type == "CSL" || chamber_type == "CSS") return 8;
    return 0;
}

int MuonRawHistograms::sign(std::string chamber_side){
    if (chamber_side == "A") return  1;
    if (chamber_side == "C") return -1;
    return 0;
}

std::string MuonRawHistograms::phi_string(int phi_sector){
    if (phi_sector > 9) return     std::to_string(phi_sector);
    else                return "0"+std::to_string(phi_sector);
}
