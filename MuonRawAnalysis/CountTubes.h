#ifndef MUONRAWHITS_COUNTTUBES_H
#define MUONRAWHITS_COUNTTUBES_H

#include <vector>
#include <cstring>
#include <string>
#include <chrono>

#include <TFile.h>
#include <TDirectory.h>
#include <TTree.h>
#include <TH1F.h>
#include <TH2F.h>

class CountTubes {

 public:

    CountTubes();
    CountTubes(std::string ipath, std::string opath);
    ~CountTubes();

    int initialize();
    int execute(int ents = -1);
    int finalize();

    std::string  input_path = "";
    std::string output_path = "";
    std::string run         = "";

    std::map<std::string, int> counts;

    void announce();
    void initialize_branches();

    std::string phi_string(int phi);
    int sign(std::string chamber_side);

    std::string chamber = "";
    TH2F* hist = 0;

    TFile* file;
    TTree* tree;
    int entries;

    std::chrono::time_point<std::chrono::system_clock> time_start, time_end;
    std::chrono::duration<double> elapsed_seconds;

    // inputs
    int mdt_chamber_n;
    std::vector<std::string>* mdt_chamber_type          = 0; //!
    std::vector<std::string>* mdt_chamber_side          = 0; //!
    std::vector<int>*         mdt_chamber_eta_station   = 0; //!
    std::vector<int>*         mdt_chamber_phi_sector    = 0; //!

    std::vector<int>*              mdt_chamber_tube_n       = 0; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_adc     = 0; //!
    std::vector<std::vector<int>>* mdt_chamber_tube_id      = 0; //!

};

#endif
