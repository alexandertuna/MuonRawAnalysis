#include "MuonRawAnalysis/CountTubes.h"

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>

#include <TFile.h>
#include <TDirectory.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH2F.h>

CountTubes::CountTubes(std::string ipath, std::string opath){
    input_path  = ipath;
    output_path = opath;
}

CountTubes::~CountTubes(){}

int CountTubes::initialize(){

    file = TFile::Open(input_path.c_str());
    if (!file)
        std::cout << "\n FATAL FUCK CountTubes::initialize: no file \n" << std::endl;

    tree = (TTree*)(file->Get("physics"));
    if (!tree)
        std::cout << "\n FATAL FUCK CountTubes::initialize: no tree \n" << std::endl;

    announce();
    initialize_branches();
    
    return 0;
}

int CountTubes::execute(int ents){

    int ent = 0;
    int ch  = 0;
    int hit = 0;

    std::string chamber_name     = "";
    std::string chamber_side     = "";
    std::string chamber_type     = "";
    int         chamber_eta      = 0;
    int         chamber_phi      = 0;
    int         chamber_hits_raw = 0;

    std::string tube_name = "";
    int         tube_id   = 0;

    int tree_entries = (int)(tree->GetEntries());
    if (ents < 0 || ents > tree_entries) entries = tree_entries;
    else                                 entries = ents;

    counts.clear();
    time_start = std::chrono::system_clock::now();

    counts["total"] = 0;

    for (ent = 1; ent < entries; ++ent){

        tree->GetEntry(ent);

        if (ent % 2000 == 0) {
            printf("%8i / %8i \n", ent, entries);
            printf("\033[F\033[J");
        } 

        counts["total"]++;

        for (ch = 0; ch < mdt_chamber_n; ++ch){

            chamber_hits_raw = mdt_chamber_tube_n->at(ch);
            chamber_eta      = mdt_chamber_eta_station->at(ch);
            chamber_phi      = mdt_chamber_phi_sector->at(ch);
            chamber_type     = mdt_chamber_type->at(ch);
            chamber_side     = mdt_chamber_side->at(ch);

            chamber_name = chamber_type + std::to_string(chamber_eta) + chamber_side + phi_string(chamber_phi);

            for (hit = 0; hit < chamber_hits_raw; ++hit){

                tube_id   = (mdt_chamber_tube_id->at(ch)).at(hit);
                tube_name = chamber_name + "_" + std::to_string(tube_id);

                if (counts.count(tube_name)) counts[tube_name]++;
                else                         counts[tube_name] = 1;
            }
        }
    }

    time_end = std::chrono::system_clock::now();
    elapsed_seconds = time_end - time_start;

    printf("%8i / %8i in %.2f s = %.2f Hz\n", ent, entries, elapsed_seconds.count(), (float)(entries) / elapsed_seconds.count());

    return 0;
}

int CountTubes::finalize(){
    
    std::ofstream output_file;
    output_file.open(output_path);
    
    for (std::map<std::string, int>::iterator iter = counts.begin(); iter != counts.end(); ++iter)
        output_file << iter->first << " " << iter->second << std::endl;

    output_file.close();
    return 0;
}

void CountTubes::announce(){
    
    std::cout << std::endl;
    std::cout << "   input | " <<  input_path        << std::endl;
    std::cout << "  output | " << output_path        << std::endl;
    std::cout << " entries | " << tree->GetEntries() << std::endl;
    std::cout << std::endl;
}

void CountTubes::initialize_branches(){

    tree->SetBranchAddress("mdt_chamber_n",           &mdt_chamber_n);
    tree->SetBranchAddress("mdt_chamber_type",        &mdt_chamber_type);
    tree->SetBranchAddress("mdt_chamber_side",        &mdt_chamber_side);
    tree->SetBranchAddress("mdt_chamber_eta_station", &mdt_chamber_eta_station);
    tree->SetBranchAddress("mdt_chamber_phi_sector",  &mdt_chamber_phi_sector);

    tree->SetBranchAddress("mdt_chamber_tube_n",       &mdt_chamber_tube_n);
    tree->SetBranchAddress("mdt_chamber_tube_id",      &mdt_chamber_tube_id);
}

std::string CountTubes::phi_string(int phi){
    if (phi < 10) return "0"+std::to_string(phi);
    else          return     std::to_string(phi);
}

int CountTubes::sign(std::string chamber_side){
    if (chamber_side == "A") return  1;
    if (chamber_side == "C") return -1;
    return 0;
}
