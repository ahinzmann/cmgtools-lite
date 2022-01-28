//#include "TString.h"
//#include "TFile.h"
//#include "TH1F.h"
//#include "TGraph.h"
//#include "RooDataSet.h"
//#include "RooWorkspace.h"
//#include "RooRealVar.h"
//#include "RooChebychev.h"
//#include "RooVoigtian.h"
//#include "RooArgSet.h"
//#include "RooAddPdf.h"
//#include "RooPlot.h"
//#include "utilities.cc"
using namespace RooFit;
double max_significance_in_data = 3.6;
void count_toys_with_signif_lt_localmax(int hello=-1){
	gSystem->Load("libHiggsAnalysisCombinedLimit.so");
	//TFile ftoydatasets("higgsCombineTest.GenerateOnly.mH16.5.123456.root");
	TFile fws("results_Run2/workspace_JJ_WprimeWZ_VBF_VVVH_13TeV_Run2_data_afterpreapproval_newShapesFits.root");
	RooWorkspace *ws=(RooWorkspace*)fws.Get("w");
	for(int itoy=1; itoy<=300; itoy++){
		if(hello>=0 && itoy!=hello) continue; 
		TCanvas c("c","c",1000,500); 
		TString stoy = "toy_"; stoy+=itoy;
		TString btoy = ""; btoy+=itoy;
		if(hello==-1) stoy="data";

		Float_t MH, deltaNLL, r;
		Double_t nll, nll0;
		//TFile fbfit("higgsCombine_bfit_"+stoy+".MultiDimFit.mH120.root");
		//TFile fscan("higgsCombine_"+stoy+".MultiDimFit.mH120.root");
		TString fbfit_file;
		TString fscan_file;
		if(hello == -1){
		  fbfit_file = "higgsCombine_bfit_"+stoy+".MultiDimFit.mH120.root";
		  fscan_file = "higgsCombinemhscan_"+stoy+"_test_split_r_forsignificance.root";
		}
		else{
		  fbfit_file = "higgsCombine_bfit_toy_jobs_"+btoy+".MultiDimFit.mH120.root";
		  fscan_file = "higgsCombine_mhscan_data_scan_"+stoy+".MultiDimFit.mH120.root";
		}

		std::cout << "b file "<<  fbfit_file << std::endl;
		std::cout << " scan file " << fscan_file << std::endl;
		TFile fbfit(fbfit_file);
		TFile fscan(fscan_file);

		TTree *t=(TTree*)fbfit.Get("limit");
		t->SetBranchAddress("MH",&MH);
		t->SetBranchAddress("deltaNLL",&deltaNLL);
		t->SetBranchAddress("nll",&nll);
		t->SetBranchAddress("nll0",&nll0);

		double nll_bfit = 0;
		Long_t nentries = t->GetEntries();
		for (Int_t i = 0; i<1; i++) {
			t->GetEntry(i);
			nll_bfit = nll+nll0;
		}
		cout<<"nll_bfit="<<nll_bfit<<endl;

		t=(TTree*)fscan.Get("limit");
		t->SetBranchAddress("MH",&MH);
		t->SetBranchAddress("deltaNLL",&deltaNLL);
		t->SetBranchAddress("nll",&nll);
		t->SetBranchAddress("nll0",&nll0);

		TGraph hsignif(0);	
		hsignif.GetXaxis()->SetRangeUser(1300,6000);
		nentries = t->GetEntries();
		double sig_max = -1, MH_max;

		for (Int_t i = 0; i<nentries; i++) {
			t->GetEntry(i);
			double rel_nll = nll+nll0+deltaNLL - nll_bfit; if(rel_nll>0) rel_nll=0;
			double sig = sqrt(2*fabs(rel_nll));
			cout << " MH "<< MH << " sig "<< sig << endl;
			if(sig>5) continue;
			hsignif.Set(i+1);
			hsignif.SetPoint(i, MH, sig);
		}
		hsignif.Sort();
		//spikeKiller1D(&hsignif);
		for(int i=1; i< hsignif.GetN(); i++){
			double x, y; hsignif.GetPoint(i, x, y);
			if(y>=sig_max){ sig_max=y; MH_max=x;
			}
		}

		c.cd();
		TH1F htmp("htmp","htmp",48,1300,6000);
		htmp.SetMaximum(5);
		htmp.SetMinimum(0);
		htmp.SetTitle("; m_{X} (GeV); Q = #sqrt{-2#Delta ln L}");
		htmp.SetStats(0);
		htmp.Draw();
		hsignif.Draw("LP");
		TString ssig = TString::Format("Q_{max} = %.2f",sig_max);
		TLatex tsig;
		tsig.SetNDC();
		tsig.SetTextSize(0.06);
		if(sig_max>=max_significance_in_data) tsig.SetTextColor(kRed);
		tsig.DrawLatex(0.17,0.85, ssig.Data());

		TLine *lh = new TLine(1300,max_significance_in_data, 6000, max_significance_in_data);
		lh->SetLineStyle(kDashed);
		lh->Draw();

		c.SaveAs("scan_signif_"+stoy+(sig_max<max_significance_in_data?".png":"_red.png"));
		if(hello<=0)break;
	}
}

