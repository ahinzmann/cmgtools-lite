void PlotPulls()
{

  int nfiles = 1;
  TString label="data_Run2_VBFggDY_afterpreapproval_TTkernels_WprimeWZ_3000";
  const int nlabels = 101; // number of nuissance parameters
  std::string labels[nlabels] = {""};
  // To get the fitDiagnostics.root file run ~ this command  'combine -M FitDiagnostics -m 2000 results_2016/workspace_JJ_BulkGWW_VH_NPHP_control_region_13TeV_2016_newdata.root -v 2 --noErrors --minos none' on the workspace
  TFile* tf = new TFile("fitDiagnosticsdata_Run2_VBFggDY_afterpreapproval_TTkernels_WprimeWZ_3000.root","READ");
  tf->ls();

  int np = 0;
  Double_t x_np_s[nlabels] = {0};
  Double_t x_np_b[nlabels] = {0};
  Double_t y_np[nlabels] = {0};
  Double_t x_errs_s[nlabels] = {0};
  Double_t x_errs_b[nlabels] = {0};
  Double_t y_errs[nlabels] = {0};

  TGraphErrors* np_gr_s = new TGraphErrors(nlabels);
  np_gr_s->SetName("s_plus_b");
  TGraphErrors* np_gr_b = new TGraphErrors(nlabels);
  np_gr_b->SetName("b_only");
  
  RooArgSet* prefit = (RooArgSet*)tf->Get("nuisances_prefit") ;
  RooFitResult* postfit_s = (RooFitResult*)tf->Get("fit_s");
  RooFitResult* postfit_b = (RooFitResult*)tf->Get("fit_b");
 
  RooArgList fpf_s = postfit_s->floatParsFinal();
  RooArgList fpf_b = postfit_b->floatParsFinal();

  for(int k=0; k<fpf_s.getSize(); ++k){
    RooRealVar* param_s = (RooRealVar*)fpf_s.at(k);
    std::string name = param_s->GetName();
    RooRealVar* nuis_p = (RooRealVar*)prefit->find(name.c_str());
    std:: cout << k << std::endl;
    if( std::string(param_s->GetName()) == "r" ){
      continue;
      std::cout << name << " " << param_s->getVal() << " " << param_s->getError() << " " << (param_s->getVal()-10.0)/param_s->getError() << std::endl;
      double pull_s = 0;//(param_s->getVal()-0.0)/param_s->getError();
      double pull_b = 0;
      double err_s = param_s->getError()/param_s->getError();
      double err_b = 0;
      labels[np] = "r";
      np_gr_s->SetPoint(np,pull_s,np+0.5);
      np_gr_s->SetPointError(np,err_s,0.);
      np_gr_b->SetPoint(np,pull_b,np+0.5);
      np_gr_b->SetPointError(np,err_b,0.);
      np+=1;  
   
    }
    else{
    
      //RooRealVar* param_s = (RooRealVar*)fpf_s.at(k);
      RooRealVar*param_b = (RooRealVar*)fpf_b.at(k);   

      std::cout << name << std::endl;
      std::cout << "   * post-fit val: " << param_s->getVal()<< " (S+B) " << param_b->getVal() << " (B) " << std::endl;
      std::cout << "   * post-fit err: " << param_s->getError() << " (S+B) " << param_b->getError() << "(B)" << std::endl;
      std::cout << "   * pre-fit val: " << nuis_p->getVal() << " pre-fit err:" << nuis_p->getError() << std::endl;
      std::cout << "   * pull vs prefit: " << (param_s->getVal()-nuis_p->getVal())/nuis_p->getError() << " (S+B) " << (param_b->getVal()-nuis_p->getVal())/nuis_p->getError() << " (B) " << std::endl;
      std::cout << "   * pull vs postfit: "<< (param_s->getVal()-nuis_p->getVal())/param_s->getError() << " (S+B) " << (param_b->getVal()-nuis_p->getVal())/param_b->getError() << " (B) "  << std::endl;


      double pull_s = (param_s->getVal()-nuis_p->getVal())/nuis_p->getError();
      double pull_b = (param_b->getVal()-nuis_p->getVal())/nuis_p->getError();
      double err_s = param_s->getError()/nuis_p->getError();
      double err_b = param_b->getError()/nuis_p->getError();

      np_gr_s->SetPoint(np,pull_s,np+0.5);
      np_gr_s->SetPointError(np,err_s,0.);
      np_gr_b->SetPoint(np,pull_b,np+0.5);
      np_gr_b->SetPointError(np,err_b,0.);
      labels[np] = name;
      np+=1;
      
    }
 
  }

  std::cout << "DONE" << std::endl;
  TText t;
  t.SetTextAngle(60);
  t.SetTextSize(0.015);
  t.SetTextFont(42);
  t.SetTextAlign(33);
  const Int_t nx = 12;
  const Int_t ny=nlabels;
  TCanvas *c1 = new TCanvas("c1","demo bin labels",10,10,800,800);
  c1->SetLeftMargin(0.5);
  c1->SetTopMargin(0.01);
  c1->SetRightMargin(0.02);
  TH2F *h = new TH2F("h","test",8,-4,4,ny,0,ny);

  h->SetStats(0);
  h->SetTitle(0);
  //h->GetXaxis()->SetLabelOffset(99);
  h->GetYaxis()->SetLabelOffset(99);
  h->GetXaxis()->SetTitleOffset(1.);
  h->GetXaxis()->SetTitleSize(0.04);
  h->GetXaxis()->SetTitle("(#theta-#theta_{in})/#sigma_{#theta}");
  h->GetXaxis()->CenterTitle();
  h->Draw("text");

  Float_t x, y;
  x = -4.3;
  t.SetTextAlign(32);
  t.SetTextAngle(0);
  for (int i=0;i<ny;i++) {
    y = h->GetYaxis()->GetBinCenter(i+1);
    t.DrawText(x,y,labels[i].c_str());
  }

  TLine* l_zero = new TLine(0, 0, 0, nlabels);
  TLine* l_m1 = new TLine(-1, 0, -1, nlabels);
  TLine* l_p1 = new TLine(1,0,1,nlabels);
  TLine* l_m2 = new TLine(-2, 0, -2, nlabels);
  TLine* l_p2 = new TLine(2, 0, 2, nlabels);
  l_zero->SetLineStyle(3);
  l_zero->SetLineWidth(2);
  l_m1->SetLineStyle(3);
  l_m1->SetLineWidth(2);
  l_p1->SetLineStyle(3);
  l_p1->SetLineWidth(2);
  l_m2->SetLineStyle(3);
  l_m2->SetLineWidth(2);
  l_p2->SetLineStyle(3);
  l_p2->SetLineWidth(2);

  l_zero->Draw();
  l_m1->Draw();
  l_p1->Draw();
  l_m2->Draw();
  l_p2->Draw();

  TLegend* legend = new TLegend(0.1,0.92,0.3,0.99);
  legend->SetTextSize(0.032);
  legend->SetNColumns(2);
  legend->SetLineColor(0);
  legend->SetShadowColor(0);
  legend->SetLineStyle(1);
  legend->SetLineWidth(1);
  legend->SetFillColor(0);
  legend->SetFillStyle(0);
  //legend->SetMargin(0.35);
  legend->AddEntry(np_gr_b,"B-only","LP");
  legend->AddEntry(np_gr_s,"S+B","LP");
  legend->Draw();
   
  np_gr_b->SetMarkerStyle(20);
  np_gr_b->SetMarkerColor(kPink-1);
  np_gr_b->SetLineColor(kPink-1);
  np_gr_s->SetMarkerStyle(20);
  np_gr_s->Draw("Psame");
  np_gr_b->Draw("Psame");
  TString name = "pulls_"+label;
  c1->SaveAs(name+".C");
  c1->SaveAs(name+".png");
  c1->SaveAs(name+".pdf");
  
  tf->Close();

}

