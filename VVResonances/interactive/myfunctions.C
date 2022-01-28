#include <TROOT.h>
#include <TLorentzVector.h>
#include <TFile.h>
#include <TString.h>
#include <TH2F.h>
#include <TMath.h>
#include <stdio.h>


auto puppijjmass(const Double_t pt1, const Double_t eta1, const Double_t phi1, const Double_t mass1,const Double_t pt2, const Double_t eta2, const Double_t phi2, const Double_t mass2) {
  // Compose four-vectors of both muons
  TLorentzVector p1, p2;
  p1.SetPtEtaPhiM(pt1, eta1, phi1, mass1);
  p2.SetPtEtaPhiM(pt2, eta2, phi2, mass2);
  // Add four-vectors to build dimuon system and return the invariant mass
  return (p1 + p2).M();
};

//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p7rho_smoothed.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_scaled_0p7_map_dijet" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p9rho_smoothed.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_scaled_0p9_map_dijet" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p9rho_smoothed.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_scaled_0p9_map_dijet" ){
auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p02rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_scaled_yx_0p02" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_MD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p02rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_MD_v_rho_v_pT_scaled_yx_0p02" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_finepTaround500_Pt_2016/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2017/myDeepBoostedMap_0p02rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p02" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2018/myDeepBoostedMap_0p02rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p02" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2016/myDeepBoostedMap_0p02rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p02" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2017/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p10" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p10" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2016-2017-2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p10" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2016-2017-2018/myDeepBoostedMap_0p02rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p02" ){
//auto getZHcut(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2016/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p10" ){
  //  TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_yx";
   //std::cout << "getZHcut"<< std::endl;
  TH2D *  map_WvsQCD = (TH2D*)gROOT->FindObject(mapName);
  if (map_WvsQCD == nullptr) {
    TFile file;
    file.Open(filename);
    map_WvsQCD = (TH2D*)file.Get(mapName);
    map_WvsQCD->SetDirectory(0);
    file.Close();
  }

  Double_t rho = 2*TMath::Log(mass/pt);
  int pt_bin,x_bin;
  float cut_WvsQCD;

  //std::cout << "pt " << pt << " rho " << rho << std::endl;
  pt_bin = map_WvsQCD->GetYaxis()->FindFixBin(pt);
  //std::cout << "pt_bin " <<pt_bin <<std::endl;
  if(pt_bin > map_WvsQCD->GetYaxis()->GetNbins()){
    pt_bin = map_WvsQCD->GetYaxis()->GetNbins();
  }else if(pt_bin <=0){
    pt_bin = 1;
  }
   //std::cout << "pt_bin " <<pt_bin <<std::endl;
  x_bin = map_WvsQCD->GetXaxis()->FindFixBin(rho);
  if(x_bin > map_WvsQCD->GetXaxis()->GetNbins()){
    x_bin = map_WvsQCD->GetXaxis()->GetNbins();
  }else if(x_bin <= 0){
    x_bin = 1;
  }
  //std::cout << "x_bin " <<x_bin <<std::endl;
  cut_WvsQCD = map_WvsQCD->GetBinContent(x_bin,pt_bin);        
   //std::cout << "cut_WvsQCD " <<cut_WvsQCD <<std::endl;

  return cut_WvsQCD;

};




//auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2017/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p10" ){
//auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p5rho_smoothed.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_scaled_0p5_map_dijet" ){
//auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p8rho_smoothed.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_scaled_0p8_map_dijet" ){
auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
  //auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_ZHbbvsQCD_MD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_MD_v_rho_v_pT_scaled_yx_0p10" ){

  //auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p10" ){
//auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2016-2017-2018/myDeepBoostedMap_0p02rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p02" ){
//auto getZHcut2(const Double_t pt, const Double_t mass, TString filename = "testMapZH_fineBinning_Pt_2016-2017-2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_ZHbbvsQCD_v_rho_v_pT_sclaed_yx_0p10" ){
   //std::cout << "getZHcut2"<< std::endl;
  TH2D *  map_WvsQCD = (TH2D*)gROOT->FindObject(mapName);
  if (map_WvsQCD == nullptr) {
    TFile file;
    file.Open(filename);
    map_WvsQCD = (TH2D*)file.Get(mapName);
    map_WvsQCD->SetDirectory(0);
    file.Close();
  }

  Double_t rho = 2*TMath::Log(mass/pt);
  int pt_bin,x_bin;
  float cut_WvsQCD;

   //std::cout << "pt " << pt << " rho " << rho << std::endl;
  pt_bin = map_WvsQCD->GetYaxis()->FindFixBin(pt);
   //std::cout << "pt_bin " <<pt_bin <<std::endl;
  if(pt_bin > map_WvsQCD->GetYaxis()->GetNbins()){
    pt_bin = map_WvsQCD->GetYaxis()->GetNbins();
  }else if(pt_bin <=0){
    pt_bin = 1;
  }
  //std::cout << "pt_bin " <<pt_bin <<std::endl;
  x_bin = map_WvsQCD->GetXaxis()->FindFixBin(rho);
  if(x_bin > map_WvsQCD->GetXaxis()->GetNbins()){
    x_bin = map_WvsQCD->GetXaxis()->GetNbins();
  }else if(x_bin <= 0){
    x_bin = 1;
  }
   //std::cout << "x_bin " <<x_bin <<std::endl;
  cut_WvsQCD = map_WvsQCD->GetBinContent(x_bin,pt_bin);        
   //std::cout << "cut_WvsQCD " <<cut_WvsQCD <<std::endl;

  return cut_WvsQCD;

};





//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_deltaEta_2016/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx" ){
auto getWcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p05rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p05"){
// auto getWcut(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_MD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p05rho.root", TString mapName = "DeepBoosted_WvsQCD_MD_v_rho_v_pT_scaled_yx_0p05"){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_finepTaround500_Pt_2016/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapTau21_fineBinning_Pt_2016/myDeepBoostedMap_0p05rho.root", TString mapName = "tau21_v_rho_v_pT_yx" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2016/myDeepBoostedMap_0p05rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p05" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2017/myDeepBoostedMap_0p05rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p05" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2018/myDeepBoostedMap_0p05rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p05" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2016/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2017/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2016-2017-2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
//auto getWcut(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2016-2017-2018/myDeepBoostedMap_0p05rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p05" ){
  //  TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_yx";
  TH2D *  map_WvsQCD = (TH2D*)gROOT->FindObject(mapName);
  if (map_WvsQCD == nullptr) {
    TFile file;
    file.Open(filename);
    map_WvsQCD = (TH2D*)file.Get(mapName);
    map_WvsQCD->SetDirectory(0);
    file.Close();
  }

  Double_t rho = 2*TMath::Log(mass/pt);
  int pt_bin,x_bin;
  float cut_WvsQCD;

  // std::cout << "pt " << pt << " rho " << rho << std::endl;
  pt_bin = map_WvsQCD->GetYaxis()->FindFixBin(pt);
  // std::cout << "pt_bin " <<pt_bin <<std::endl;
  if(pt_bin > map_WvsQCD->GetYaxis()->GetNbins()){
    pt_bin = map_WvsQCD->GetYaxis()->GetNbins();
  }else if(pt_bin <=0){
    pt_bin = 1;
  }
  // std::cout << "pt_bin " <<pt_bin <<std::endl;
  x_bin = map_WvsQCD->GetXaxis()->FindFixBin(rho);
  if(x_bin > map_WvsQCD->GetXaxis()->GetNbins()){
    x_bin = map_WvsQCD->GetXaxis()->GetNbins();
  }else if(x_bin <= 0){
    x_bin = 1;
  }
  // std::cout << "x_bin " <<x_bin <<std::endl;
  cut_WvsQCD = map_WvsQCD->GetBinContent(x_bin,pt_bin);        
  // std::cout << "cut_WvsQCD " <<cut_WvsQCD <<std::endl;

  return cut_WvsQCD;

};

//auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2016-2017-2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
//auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2018/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
//auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2017/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
//auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "testMapW_fineBinning_Pt_2016/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10" ){
auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p10"){
  //auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_MD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_MD_v_rho_v_pT_scaled_yx_0p10"){
 
 TH2D *  map_WvsQCD = (TH2D*)gROOT->FindObject(mapName);
  if (map_WvsQCD == nullptr) {
    TFile file;
    file.Open(filename);
    map_WvsQCD = (TH2D*)file.Get(mapName);
    map_WvsQCD->SetDirectory(0);
    file.Close();
  }

  Double_t rho = 2*TMath::Log(mass/pt);
  int pt_bin,x_bin;
  float cut_WvsQCD;

  // std::cout << "pt " << pt << " rho " << rho << std::endl;
  pt_bin = map_WvsQCD->GetYaxis()->FindFixBin(pt);
  // std::cout << "pt_bin " <<pt_bin <<std::endl;
  if(pt_bin > map_WvsQCD->GetYaxis()->GetNbins()){
    pt_bin = map_WvsQCD->GetYaxis()->GetNbins();
  }else if(pt_bin <=0){
    pt_bin = 1;
  }
  // std::cout << "pt_bin " <<pt_bin <<std::endl;
  x_bin = map_WvsQCD->GetXaxis()->FindFixBin(rho);
  if(x_bin > map_WvsQCD->GetXaxis()->GetNbins()){
    x_bin = map_WvsQCD->GetXaxis()->GetNbins();
  }else if(x_bin <= 0){
    x_bin = 1;
  }
  // std::cout << "x_bin " <<x_bin <<std::endl;
  cut_WvsQCD = map_WvsQCD->GetBinContent(x_bin,pt_bin);        
  // std::cout << "cut_WvsQCD " <<cut_WvsQCD <<std::endl;

  return cut_WvsQCD;

};

auto getWcut3(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p15rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p15"){
  //auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_MD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_MD_v_rho_v_pT_scaled_yx_0p10"){                                                                                                                                                                                                                                    

 TH2D *  map_WvsQCD = (TH2D*)gROOT->FindObject(mapName);
  if (map_WvsQCD == nullptr) {
    TFile file;
    file.Open(filename);
    map_WvsQCD = (TH2D*)file.Get(mapName);
    map_WvsQCD->SetDirectory(0);
    file.Close();
  }

  Double_t rho = 2*TMath::Log(mass/pt);
  int pt_bin,x_bin;
  float cut_WvsQCD;

  // std::cout << "pt " << pt << " rho " << rho << std::endl;                                                                                                                                                                                 
  pt_bin = map_WvsQCD->GetYaxis()->FindFixBin(pt);
  // std::cout << "pt_bin " <<pt_bin <<std::endl;                                                                                                                                                                                             
  if(pt_bin > map_WvsQCD->GetYaxis()->GetNbins()){
    pt_bin = map_WvsQCD->GetYaxis()->GetNbins();
  }else if(pt_bin <=0){
    pt_bin = 1;
  }
  // std::cout << "pt_bin " <<pt_bin <<std::endl;                                                                                                                                                                                             
  x_bin = map_WvsQCD->GetXaxis()->FindFixBin(rho);
  if(x_bin > map_WvsQCD->GetXaxis()->GetNbins()){
    x_bin = map_WvsQCD->GetXaxis()->GetNbins();
  }else if(x_bin <= 0){
    x_bin = 1;
  }
  // std::cout << "x_bin " <<x_bin <<std::endl;                                                                                                                                                                                               
  cut_WvsQCD = map_WvsQCD->GetBinContent(x_bin,pt_bin);
  // std::cout << "cut_WvsQCD " <<cut_WvsQCD <<std::endl;                                                                                                                                                                                     

  return cut_WvsQCD;

};

auto getWcut4(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p50rho.root", TString mapName = "DeepBoosted_WvsQCD_v_rho_v_pT_scaled_yx_0p50"){
  //auto getWcut2(const Double_t pt, const Double_t mass, TString filename = "MapsDeltaEta/DDTMap_WvsQCD_MD_scaled_2018_withDeltaEta_finerbinning/myDeepBoostedMap_0p10rho.root", TString mapName = "DeepBoosted_WvsQCD_MD_v_rho_v_pT_scaled_yx_0p10"){                                                                                                                                                                                                                                    

 TH2D *  map_WvsQCD = (TH2D*)gROOT->FindObject(mapName);
  if (map_WvsQCD == nullptr) {
    TFile file;
    file.Open(filename);
    map_WvsQCD = (TH2D*)file.Get(mapName);
    map_WvsQCD->SetDirectory(0);
    file.Close();
  }

  Double_t rho = 2*TMath::Log(mass/pt);
  int pt_bin,x_bin;
  float cut_WvsQCD;

  // std::cout << "pt " << pt << " rho " << rho << std::endl;                                                                                                                                                                                 
  pt_bin = map_WvsQCD->GetYaxis()->FindFixBin(pt);
  // std::cout << "pt_bin " <<pt_bin <<std::endl;                                                                                                                                                                                             
  if(pt_bin > map_WvsQCD->GetYaxis()->GetNbins()){
  pt_bin = map_WvsQCD->GetYaxis()->GetNbins();
}else if(pt_bin <=0){
  pt_bin = 1;
}
  // std::cout << "pt_bin " <<pt_bin <<std::endl;                                                                                                                                                                                             
  x_bin = map_WvsQCD->GetXaxis()->FindFixBin(rho);
  if(x_bin > map_WvsQCD->GetXaxis()->GetNbins()){
  x_bin = map_WvsQCD->GetXaxis()->GetNbins();
}else if(x_bin <= 0){
  x_bin = 1;
}
  // std::cout << "x_bin " <<x_bin <<std::endl;                                                                                                                                                                                               
  cut_WvsQCD = map_WvsQCD->GetBinContent(x_bin,pt_bin);
  // std::cout << "cut_WvsQCD " <<cut_WvsQCD <<std::endl;                                                                                                                                                                                     

  return cut_WvsQCD;

};
