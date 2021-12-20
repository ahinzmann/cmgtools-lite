import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
from array import array
import math
import CMS_lumi
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gROOT.ProcessLine(".x tdrstyle.cc");


class Postfitplotter():
    logfile = ""
    options = None
    colors = [ROOT.kGray+2,ROOT.kRed,ROOT.kBlue,ROOT.kMagenta,210,ROOT.kOrange,ROOT.kViolet,ROOT.kAzure,ROOT.kTeal,ROOT.kGreen,ROOT.kBlack,ROOT.kPink,ROOT.kMagenta]
    signalName = "BulkG"
    def __init__(self,optparser,logfile,signalName,backuplabel=""):
        print "initialize plotter"
        self.logfile = logfile
        self.options = optparser.parse_args()[0]
        self.signalName = signalName
        
        

        
        try: 
            self.options.projection
        except AttributeError:
            optparser.add_option("-p","--projection",dest="projection",help="choose which projection should be done",default="xyz")
            self.options = optparser.parse_args()[0]

        
        
        try: 
            self.options.input
        except AttributeError:
            optparser.add_option("-i","--input",dest="input",help="Input nonRes histo",default='JJ_HPHP.root')
            self.options = optparser.parse_args()[0]

        
        try: 
            self.options.label
        except AttributeError:
            optparser.add_option("-l","--label",dest="label",help="add extra label such as pythia or herwig",default=backuplabel)
            self.options = optparser.parse_args()[0]
        
        
        try: 
            self.options.output
        except AttributeError:
            optparser.add_option("-o","--output",dest="output",help="Output folder name",default='')
            self.options = optparser.parse_args()[0]
        

        try: 
            self.options.fit
        except AttributeError:
            optparser.add_option("--doFit",dest="fit",action="store_false",help="actually fit the the distributions",default=True)
            self.options = optparser.parse_args()[0]
            

        try: 
            self.options.log
        except AttributeError:
            optparser.add_option("--log",dest="log",help="write output in logfile given as argument here!",default="chi2.log")
            self.options = optparser.parse_args()[0]
            
        try:
            self.options.blind
        except AttributeError:
            optparser.add_option("--blind",dest="blind",help="Use to blind data in control region",action="store_true",default=False)
            self.options = optparser.parse_args()[0]


        try: 
            self.options.addTop
        except AttributeError:
            optparser.add_option("--addTop",dest="addTop",default=False)
            self.options = optparser.parse_args()[0]
        try:
            self.options.addDIB
        except AttributeError:
            optparser.add_option("--addDIB",dest="addDIB",default=False)
            self.options = optparser.parse_args()[0]
              
        
        
        try: 
            self.options.signalScaleF
        except AttributeError:
            optparser.add_option("--signalScaleF",dest="signalScaleF",type=float,help="scale factor to apply to signal when drawing so its still visible!",default=500.)
            optparser.add_option("-s","--signal",dest="fitSignal",action="store_true",help="do S+B fit",default=False)
            optparser.add_option("-M","--mass",dest="signalMass",type=float,help="signal mass",default=1560.)

            self.options = optparser.parse_args()[0]
            
           
            
        try: 
            self.options.prelim
        except AttributeError:
            optparser.add_option("--prelim",dest="prelim",default="Preliminary")
            self.options = optparser.parse_args()[0]

        try:
            self.options.plotbonly
        except AttributeError:
            optparser.add_option("--plotbonly",dest="plotbonly",default=False)
            self.options = optparser.parse_args()[0]


        try: 
            self.options.pdfy
        except AttributeError:
            optparser.add_option("--pdfz",dest="pdfz",help="name of pdfs lie PTZUp etc",default="")
            optparser.add_option("--pdfx",dest="pdfx",help="name of pdfs lie PTXUp etc",default="")
            optparser.add_option("--pdfy",dest="pdfy",help="name of pdfs lie PTYUp etc",default="")
            self.options = optparser.parse_args()[0]
            
        try: 
            self.options.name
        except AttributeError:
            optparser.add_option("--wsname",dest="name",default="")
            self.options = optparser.parse_args()[0]
                
        try: 
            self.options.channel
        except AttributeError:
            optparser.add_option("--channel",dest="channel",default="VH_HPHP")
            self.options = optparser.parse_args()[0]
            print " attention channel not specified default channel VH_HPHP used"
            
        try: 
            self.options.addTop
        except AttributeError:
            optparser.add_option("--addTop",dest="addTop",default=False)
            optparser.add_option("-v","--doVjets",dest="doVjets",action="store_true",help="Fit top",default=False)
            self.options = optparser.parse_args()[0]
                
            
        

    def calculateChi2ForSig(self,hsig,pred,axis,logfile,label):
        if axis.find("z")!=-1:
            #logfile.open("testChi2.log","rw")
            chi2 = self.getChi2proj(pred,hsig)
            #print hsig.GetEntries(),hsig.Integral()
            logfile.write(label+"\n")
            if chi2[1]!=0:
                logfile.write("full chi2 \n ")
                logfile.write( "Projection %s: Chi2/ndf = %.2f/%i"%(axis,chi2[0],chi2[1])+"= %.2f"%(chi2[0]/chi2[1])+" prob = "+str(ROOT.TMath.Prob(chi2[0],chi2[1]))+"\n")
                logfile.write( "\n calculate Chi2 value around 2RMS of the mean value \n")
                
                mean = hsig.GetMean()
                rms = hsig.GetRMS()
                logfile.write( "mean : "+str(mean)+"  RMS "+str(rms)+" \n")
                chi2 = self.getChi2proj(pred,hsig,mean-rms,mean+rms)
                print hsig.GetEntries(),hsig.Integral()
                if chi2[1]!=0:
                    logfile.write( "Projection %s: Chi2/ndf = %.2f/%i"%(axis,chi2[0],chi2[1])+"= %.2f"%(chi2[0]/chi2[1])+" prob = "+str(ROOT.TMath.Prob(chi2[0],chi2[1]))+"\n")
                
                logfile.write("\n chi2 basen on window 10% around the mean:  \n")
                chi2 = self.getChi2proj(pred,hsig,mean*0.9,mean*1.1)
                print hsig.GetEntries(),hsig.Integral()
                if chi2[1]!=0:
                    logfile.write( "Projection %s: Chi2/ndf = %.2f/%i"%(axis,chi2[0],chi2[1])+"= %.2f"%(chi2[0]/chi2[1])+" prob = "+str(ROOT.TMath.Prob(chi2[0],chi2[1]))+"\n")
        

    def addPullPlot(self,hdata,hpostfit,nBins,error_band):
        #print "make pull plots: (data-fit)/sigma_data & sigma_fit"
        N = hdata.GetNbinsX()
        gpost = ROOT.TGraphErrors(0)
        gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
        for i in range(1,N+1):
            m = hdata.GetXaxis().GetBinCenter(i)
            # nominal way of calculating pulls
            #The pull is defined as (Data-fit)/$\sigma$, with $\sigma=\sqrt{\sigma_\mathrm{data}^2-\sigma_\mathrm{fit}^2}$ for each bin to ensure a Gaussian pull-distribution, as defined in Ref.~\cite{CDF:AN5776}.
            if hpostfit.GetBinContent(i) <= hdata.GetBinContent(i):
                if error_band !=0: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ ROOT.TMath.Abs(hdata.GetBinErrorUp(i))
                else: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ hdata.GetBinErrorUp(i)
            else:
                if error_band!=0: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ ROOT.TMath.Sqrt(ROOT.TMath.Abs( pow(hdata.GetBinErrorUp(i),2) - pow(error_band.GetErrorYlow(i-1),2) ))
                else: ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ hdata.GetBinErrorUp(i)

            '''
            #Alternative way of calculating pulls with pvalue
            if error_band !=0:
                ypostfit = ROOT.Math.normal_quantile(ROOT.Math.poisson_cdf(int(hdata.GetBinContent(i)),hpostfit.GetBinContent(i)),1)
                if hpostfit.GetBinContent(i) < 1 and hdata.GetBinContent(i) == 0.0: ypostfit = 0.
            else:
                if hdata.GetBinErrorUp(i) == 0.0:
                    ypostfit =0
                else:
                    ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ hdata.GetBinErrorUp(i)
            '''

            '''
            print "^*^*^*^*^*^*^*^*^  Alternative way of calculating pulls with error from model / postfit ^*^*^*^*^*^*^*^*^*^*^*^*^"
            if error_band !=0:
                if ROOT.TMath.Sqrt(ROOT.TMath.Abs(hpostfit.GetBinContent(i)-pow(error_band.GetErrorYlow(i-1),2))) !=0:
                    ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ ROOT.TMath.Sqrt(ROOT.TMath.Abs(hpostfit.GetBinContent(i)-pow(error_band.GetErrorYlow(i-1),2)))
                elif hpostfit.GetBinContent(i) == 0. and hdata.GetBinContent(i) == 0.:
                    ypostfit = 0.
                else:
                    ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ROOT.TMath.Sqrt(hpostfit.GetBinContent(i))
            else:
                if hpostfit.GetBinContent(i) == 0. and hdata.GetBinContent(i) == 0.:
                    ypostfit = 0.
                else:
                    ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ROOT.TMath.Sqrt(hpostfit.GetBinContent(i)) # hdata.GetBinErrorUp(i)
            '''

            gpost.SetPoint(i-1,m,ypostfit)
            gt.SetBinContent(i,ypostfit)
            #print "bin",i,"x",m,"data",hdata.GetBinContent(i),"post fit",hpostfit.GetBinContent(i),"err data",hdata.GetBinErrorUp(i),"err fit",error_band.GetBinError(i),"pull postfit",ypostfit
            #print "bin",i,"x",m,"data",hdata.GetBinContent(i),"post fit",hpostfit.GetBinContent(i),"err data",hdata.GetBinErrorUp(i),"err fit",error_band.GetErrorYhigh(i-1),"pull postfit",ypostfit
                    
        gpost.SetLineColor(self.colors[1])
        gpost.SetMarkerColor(self.colors[1])
        gpost.SetFillColor(ROOT.kGray+3)
        gpost.SetMarkerSize(1)
        gpost.SetMarkerStyle(20)
        gt.SetFillColor(ROOT.kGray+3)
        gt.SetLineColor(ROOT.kGray+3)
        
        #gt = ROOT.TH1F("gt","gt",hdata.GetNbinsX(),hdata.GetXaxis().GetXmin(),hdata.GetXaxis().GetXmax())
        #gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
        gt.SetTitle("")
        #gt.SetMinimum(0.5);
        gt.SetMaximum(4);
        gt.SetMinimum(-4);
        #gt.SetMaximum(3.5);
        gt.SetDirectory(0);
        gt.SetStats(0);
        gt.SetLineStyle(0);
        gt.SetMarkerStyle(20);
        gt.GetXaxis().SetTitle(hpostfit.GetXaxis().GetTitle());
        gt.GetXaxis().SetLabelFont(42);
        gt.GetXaxis().SetLabelOffset(0.02);
        gt.GetXaxis().SetLabelSize(0.17);
        gt.GetXaxis().SetTitleSize(0.15);
        gt.GetXaxis().SetTitleOffset(1.2);
        gt.GetXaxis().SetTitleFont(42);
        gt.GetYaxis().SetTitle("#frac{Data-fit}{#sigma}");
        gt.GetYaxis().CenterTitle(True);
        gt.GetYaxis().SetNdivisions(205);
        gt.GetYaxis().SetLabelFont(42);
        gt.GetYaxis().SetLabelOffset(0.007);
        gt.GetYaxis().SetLabelSize(0.15);
        gt.GetYaxis().SetTitleSize(0.15);
        gt.GetYaxis().SetTitleOffset(0.4);
        gt.GetYaxis().SetTitleFont(42);
        gt.GetXaxis().SetNdivisions(505)
        #gpre.SetHistogram(gt);
        #gpost.SetHistogram(gt);       
        return [gt] 


    def addStatPullPlot(self,hdata,hpostfit,nBins):
        #print "make pull plots: (data-fit)/sigma_data"
        N = hdata.GetNbinsX()
        gpost = ROOT.TGraphErrors(0)
        gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
        for i in range(1,N+1):
            m = hdata.GetXaxis().GetBinCenter(i)
            if hdata.GetBinContent(i) == 0:
                continue
            ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/hdata.GetBinError(i)

            #"^*^*^*^*^*^*^*^*^  Alternative way of calculating pulls with error from model / postfit ^*^*^*^*^*^*^*^*^*^*^*^*^"
            #ypostfit = (hdata.GetBinContent(i) - hpostfit.GetBinContent(i))/ ROOT.TMath.Sqrt(hpostfit.GetBinContent(i))
            #if hpostfit.GetBinContent(i) < 1 and hdata.GetBinContent(i) == 0.0: ypostfit = 0.

            #"^*^*^*^*^*^*^*^*^  Alternative way of calculating pulls from p-value ^*^*^*^*^*^*^*^*^*^*^*^*^"
            #ypostfit = ROOT.Math.normal_quantile(ROOT.Math.poisson_cdf(int(hdata.GetBinContent(i)),hpostfit.GetBinContent(i)),1)

            gpost.SetPoint(i-1,m,ypostfit)
            gt.SetBinContent(i,ypostfit)
            gt.SetBinError(i,1)
            #print "bin",i,"x",m,"data",hdata.GetBinContent(i),"post fit",hpostfit.GetBinContent(i),"err data",hdata.GetBinErrorUp(i),"err fit",error_band.GetBinError(i),"pull postfit",ypostfit
            #print "bin",i,"x",m,"data",hdata.GetBinContent(i),"post fit",hpostfit.GetBinContent(i),"err data",hdata.GetBinErrorUp(i),"err fit",error_band.GetErrorYhigh(i-1),"pull postfit",ypostfit

        gpost.SetLineColor(self.colors[1])
        gpost.SetMarkerColor(self.colors[1])
        gpost.SetFillColor(ROOT.kBlack)
        gpost.SetMarkerSize(1)
        gpost.SetMarkerStyle(20)
        gt.SetFillColor(ROOT.kBlack)
        gt.SetLineColor(ROOT.kBlack)

        #gt = ROOT.TH1F("gt","gt",hdata.GetNbinsX(),hdata.GetXaxis().GetXmin(),hdata.GetXaxis().GetXmax())
        #gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
        gt.SetTitle("")
        #gt.SetMinimum(0.5);
        #gt.SetMaximum(1.5);
        gt.SetMinimum(-3.5);
        #gt.SetMaximum(3.5);
        gt.SetDirectory(0);
        gt.SetStats(0);
        gt.SetLineStyle(0);
        gt.SetMarkerStyle(20);
        gt.GetXaxis().SetTitle(hpostfit.GetXaxis().GetTitle());
        gt.GetXaxis().SetLabelFont(42);
        gt.GetXaxis().SetLabelOffset(0.02);
        gt.GetXaxis().SetLabelSize(0.17);
        gt.GetXaxis().SetTitleSize(0.15);
        gt.GetXaxis().SetTitleOffset(1.2);
        gt.GetXaxis().SetTitleFont(42);
        gt.GetYaxis().SetTitle("#frac{Data-fit}{#sigma}");
        gt.GetYaxis().CenterTitle(True);
        gt.GetYaxis().SetNdivisions(205);
        gt.GetYaxis().SetLabelFont(42);
        gt.GetYaxis().SetLabelOffset(0.007);
        gt.GetYaxis().SetLabelSize(0.15);
        gt.GetYaxis().SetTitleSize(0.15);
        gt.GetYaxis().SetTitleOffset(0.4);
        gt.GetYaxis().SetTitleFont(42);
        gt.GetXaxis().SetNdivisions(505)
        #gpre.SetHistogram(gt);
        #gpost.SetHistogram(gt);
        return [gt]

    def addRatioPlot(self,hdata,hpostfit,nBins,error_band):
        #print "make pull plots: (data-fit)/sigma_data"
        N = hdata.GetNbinsX()
        gpost = ROOT.TGraphErrors(0)
        gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
        for i in range(1,N+1):
            m = hdata.GetXaxis().GetBinCenter(i)
            ypostfit = (hdata.GetBinContent(i)/hpostfit.GetBinContent(i))
            gpost.SetPoint(i-1,m,ypostfit)
            gt.SetBinContent(i,ypostfit)
            print "bin",i,"x",m,"data",hdata.GetBinContent(i),"post fit",hpostfit.GetBinContent(i),"err data",hdata.GetBinErrorUp(i),"err fit",error_band.GetBinError(i),"pull postfit",ypostfit
                    
        gpost.SetLineColor(self.colors[1])
        gpost.SetMarkerColor(self.colors[1])
        gpost.SetFillColor(ROOT.kBlue)
        gpost.SetMarkerSize(1)
        gpost.SetMarkerStyle(20)
        gt.SetFillColor(ROOT.kBlue)
        gt.SetLineColor(ROOT.kBlue)
        
        #gt = ROOT.TH1F("gt","gt",hdata.GetNbinsX(),hdata.GetXaxis().GetXmin(),hdata.GetXaxis().GetXmax())
        #gt = ROOT.TH1F("gt","gt",len(nBins)-1,nBins)
        gt.SetTitle("")
        #gt.SetMinimum(0.5);
        #gt.SetMaximum(1.5);
        gt.SetMinimum(0.001);
        gt.SetMaximum(1.999);
        gt.SetDirectory(0);
        gt.SetStats(0);
        gt.SetLineStyle(0);
        gt.SetMarkerStyle(20);
        gt.GetXaxis().SetTitle(hpostfit.GetXaxis().GetTitle());
        gt.GetXaxis().SetLabelFont(42);
        gt.GetXaxis().SetLabelOffset(0.02);
        gt.GetXaxis().SetLabelSize(0.17);
        gt.GetXaxis().SetTitleSize(0.15);
        gt.GetXaxis().SetTitleOffset(1);
        gt.GetXaxis().SetTitleFont(42);
        gt.GetYaxis().SetTitle("#frac{data}{fit}");
        gt.GetYaxis().CenterTitle(True);
        gt.GetYaxis().SetNdivisions(205);
        gt.GetYaxis().SetLabelFont(42);
        gt.GetYaxis().SetLabelOffset(0.007);
        gt.GetYaxis().SetLabelSize(0.15);
        gt.GetYaxis().SetTitleSize(0.15);
        gt.GetYaxis().SetTitleOffset(0.4);
        gt.GetYaxis().SetTitleFont(42);
        gt.GetXaxis().SetNdivisions(505)
        #gpre.SetHistogram(gt);
        #gpost.SetHistogram(gt);       
        return [gt]




    def getChi2fullModel(self,pdf,data,norm):
        pr=[]
        dr=[]
        for xk, xv in xBins.iteritems():
            MJ1.setVal(xv)
            for yk, yv in yBins.iteritems():
                MJ2.setVal(yv)
                for zk,zv in zBins.iteritems():
                    MJJ.setVal(zv)
                    dr.append(data.weight(argset))
                    binV = zBinsWidth[zk]*xBinsWidth[xk]*yBinsWidth[yk]
                    pr.append( pdf.getVal(argset)*binV*norm)
        ndof = 0
        chi2 = 0
        for i in range(0,len(pr)):
            if dr[i] < 10e-10:
                continue
            ndof+=1
            #chi2+= pow((dr[i] - pr[i]),2)/pr[i]
            if pr[i] > 10e-10:
                chi2+= 2*( pr[i] - dr[i] + dr[i]* ROOT.TMath.Log(dr[i]/pr[i]))

        return [chi2,ndof]

    def getChi2proj(self,histo_pdf,histo_data,minx=-1,maxx=-1):
        pr=[]
        dr=[]
        for b in range(1,histo_pdf.GetNbinsX()+1):
            if minx!=-1:
                if histo_pdf.GetBinCenter(b) < minx: continue
            if maxx!=-1:
                if histo_pdf.GetBinCenter(b) > maxx: continue
            dr.append(histo_data.GetBinContent(b))
            pr.append(histo_pdf.GetBinContent(b))
        
        ndof = 0
        chi2 = 0
        for i in range(0,len(pr)):
            if dr[i] < 10e-10:
                continue
            ndof+=1
            #chi2+= pow((dr[i] - pr[i]),2)/pr[i]
            #print i,dr[i],pr[i],(dr[i] - pr[i]),pow((dr[i] - pr[i]),2)/pr[i],(dr[i] - pr[i])/histo_data.GetBinError(i+1)
            if pr[i] > 10e-10:
                chi2+= 2*( pr[i] - dr[i] + dr[i]* ROOT.TMath.Log(dr[i]/pr[i]))

        return [chi2,ndof]       

    def get_canvas(self,cname):

        #change the CMS_lumi variables (see CMS_lumi.py)
        CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
        CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
        CMS_lumi.writeExtraText = 1
        CMS_lumi.extraText = self.options.prelim
        H_ref = 600 
        W_ref = 600 
        W = W_ref
        H  = H_ref

        iPeriod = 0

        # references for T, B, L, R
        T = 0.08*H_ref
        B = 0.12*H_ref 
        L = 0.12*W_ref
        R = 0.04*W_ref

        canvas = ROOT.TCanvas(cname,cname,50,50,W,H)
        canvas.SetFillColor(0)
        canvas.SetBorderMode(0)
        canvas.SetFrameFillStyle(0)
        canvas.SetFrameBorderMode(0)
        canvas.SetLeftMargin( L/W )
        canvas.SetRightMargin( R/W )
        canvas.SetTopMargin( T/H )
        canvas.SetBottomMargin( B/H )
        canvas.SetTickx()
        canvas.SetTicky()
        
        return canvas

    def get_pad(self,name):

        #change the CMS_lumi variables (see CMS_lumi.py)
        CMS_lumi.lumi_7TeV = "4.8 fb^{-1}"
        CMS_lumi.lumi_8TeV = "18.3 fb^{-1}"
        period = "2016"
        if self.options.name.find("2017")!=-1: period = "2017"
        if self.options.name.find("2018")!=-1: period = "2018"
        if self.options.name.find("1617")!=-1: period = "1617"
        if self.options.name.find("Run2")!=-1: period = "Run2"
        if period =="2016":  CMS_lumi.lumi_13TeV = "36 fb^{-1}"
        if period =="2017":  CMS_lumi.lumi_13TeV = "42 fb^{-1}"
        if period =="2018":  CMS_lumi.lumi_13TeV = "60 fb^{-1}"
        if period =="1617":  CMS_lumi.lumi_13TeV = "78 fb^{-1}"
        if period =="Run2":  CMS_lumi.lumi_13TeV = "138 fb^{-1}"
        CMS_lumi.writeExtraText = 1
        CMS_lumi.lumi_sqrtS = "13 TeV (2016+2017)" # used with iPeriod = 0, e.g. for simulation-only plots (default is an empty string)
        CMS_lumi.extraText = self.options.prelim

        CMS_lumi.lumiText = "(13 TeV)"
        iPos = 0
        if( iPos==0 ): CMS_lumi.relPosX = 0.014
        CMS_lumi.relPosX=0.05
        H_ref = 600 
        W_ref = 600 
        W = W_ref
        H  = H_ref

        iPeriod = 0
        iPeriod = 4

        pad = ROOT.TPad(name, name, 0, 0.3, 1, 1.0)
        pad.SetFillColor(0)
        pad.SetBorderMode(0)
        pad.SetFrameFillStyle(0)
        pad.SetFrameBorderMode(0)
        pad.SetTickx()
        pad.SetTicky()
        
        pad.SetBottomMargin(0.02)
        pad.SetTopMargin(0.1) 
        
        return pad


    def fromGeVtoTeV(self,hist,scale=1000.):
        xaxis =  hist.GetXaxis()
        xbins = []
        xbins = xaxis.GetXbins()
        for i in range(xbins.GetSize()):
            xbins[i] = xbins[i]/scale
        xaxis.Set((xbins.GetSize() - 1), xbins.GetArray())
        return hist

    def fromGeVtoTeVGraph(self,graph,scale=1000.):
        N =  graph.GetN()
        syst_band_scaled = ROOT.TGraphAsymmErrors()
        syst_band_scaled.Copy(graph)
        for i in range(N):
            X = ROOT.Double()
            Y = ROOT.Double()
            graph.GetPoint(i,X,Y)
            syst_band_scaled.SetPoint(i,X/scale,Y)
            Y = graph.GetErrorYhigh(i)
            X = graph.GetErrorXhigh(i)
            syst_band_scaled.SetPointEYhigh(i,Y)
            syst_band_scaled.SetPointEXhigh(i,X/scale)
            Y = graph.GetErrorYlow(i)
            X = graph.GetErrorXlow(i)
            syst_band_scaled.SetPointEYlow(i,Y)
            syst_band_scaled.SetPointEXlow(i,X/scale)

        return syst_band_scaled

    def MakePlots(self,histos,hdata,hsig,axis,nBins,maxY=-1.,normsig = 1.,errors=None,pseudo=False,both=False,fitted_r=0,binwidth=4):
        print histos
        extra1 = ''
        extra2 = ''
        htitle = ''
        xtitle = ''
        ymin = 0
        ymax = 0
        xrange = self.options.xrange
        yrange = self.options.yrange
        zrange = self.options.zrange
        if self.options.xrange == '0,-1': xrange = '55,215'
        if self.options.yrange == '0,-1': yrange = '55,215'
        if self.options.zrange == '0,-1': zrange = '1.25,6.0' #5500'
        xlow = xrange.split(',')[0]
        xhigh = xrange.split(',')[1]
        ylow = yrange.split(',')[0]
        yhigh = yrange.split(',')[1]
        if self.options.blind == True:
            if len(xrange.split(',')) == 4:
                xlow2 = xrange.split(',')[2]
                xhigh2 = xrange.split(',')[3]
            if len(yrange.split(',')) == 4:
                ylow2 = yrange.split(',')[2]
                yhigh2 = yrange.split(',')[3]

        if axis=='z':
            print "make Z projection"
            htitle = "Z-Proj. x : "+self.options.xrange+" y : "+self.options.yrange
            hhtitle = self.options.channel
            xtitle = "Dijet invariant mass [TeV]"
            ymin = 0.2
            ymax = max(hdata.GetMaximum()*5000,maxY*5000)
            extra1 = xrange.split(',')[0]+' < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
            if self.options.blind == True and len(xrange.split(',')) == 4:
                extra1 = 'Blind '+xhigh+' < m_{jet1} < '+xlow2+' GeV'        #xlow+' < m_{jet1} < '+xhigh+' & '+xlow2+' < m_{jet1} < '+xhigh2+' GeV'
            extra2 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
            if self.options.blind == True and len(yrange.split(',')) == 4:
                extra2 = 'Blind '+yhigh+' < m_{jet2} < '+ylow2+' GeV'  #extra2 = ylow+' < m_{jet2} < '+yhigh+' & '+ylow2+' < m_{jet2} < '+yhigh2+' GeV'
            if both == True:
                extra1 = str(round(float(xrange.split(',')[0])))+' < m_{jet1/2} < '+ str(round(float(xrange.split(',')[1])))+' GeV'
                extra2 = str(round(float(yrange.split(',')[0])))+' < m_{jet2/1} < '+ str(round(float(yrange.split(',')[1])))+' GeV'
        elif axis=='x':
            print "make X projection"
            htitle = "X-Proj. y : "+self.options.yrange+" z : "+self.options.zrange
            hhtitle = self.options.channel
            xtitle = " m_{jet1} [GeV]"
            ymin = 0.02
            ymax = hdata.GetMaximum()*2#max(hdata.GetMaximum()*1.3,maxY*1.3)
            if "VBF" in self.options.channel:
                ymax = (hdata.GetMaximum()+ROOT.TMath.Sqrt(hdata.GetMaximum())) *2.5
            extra1 = yrange.split(',')[0]+' < m_{jet2} < '+ yrange.split(',')[1]+' GeV'
            if self.options.blind == True and len(yrange.split(',')) == 4:
                extra1 = 'Blind '+yhigh+' < m_{jet2} < '+ylow2+' GeV'  #extra1 = ylow+' < m_{jet2} < '+yhigh+' & '+ylow2+' < m_{jet2} < '+yhigh2+' GeV'
            extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' TeV'
        elif axis=='y':
            print "make Y projection"
            htitle = "Y-Proj. x : "+self.options.xrange+" z : "+self.options.zrange
            hhtitle = self.options.channel
            xtitle = " m_{jet2} [GeV]"
            ymin = 0.02
            ymax = hdata.GetMaximum()*2#max(hdata.GetMaximum()*1.3,maxY*1.3)
            if "VBF" in self.options.channel:
                ymax = (hdata.GetMaximum()+ROOT.TMath.Sqrt(hdata.GetMaximum())) *2.5

            extra1 = xrange.split(',')[0]+' < m_{jet1} < '+ xrange.split(',')[1]+' GeV'
            if self.options.blind == True and len(xrange.split(',')) == 4:
                extra1 = 'Blind '+xhigh+' < m_{jet1} < '+xlow2+' GeV'  #extra1 = xlow+' < m_{jet1} < '+xhigh+' & '+xlow2+' < m_{jet1} < '+xhigh2+' GeV'
            extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' TeV'
        elif axis=='b':
            print "make X+Y projection"
            htitle = "XY-Proj. x : "+self.options.xrange+" y  : "+self.options.yrange+" z : "+self.options.zrange
            hhtitle = self.options.channel
            xtitle = " m_{jet} [GeV]"
            ymin = 0.02
            ymax = hdata.GetMaximum()*2.5#max(hdata.GetMaximum()*1.3,maxY*1.3)
            if "VBF" in self.options.channel:
                ymax = (hdata.GetMaximum()+ROOT.TMath.Sqrt(hdata.GetMaximum())) *2.5

            extra1 = xrange.split(',')[0]+' < m_{jet1,2} < '+ xrange.split(',')[1]+' GeV'
            if self.options.blind == True and len(xrange.split(',')) == 4:
                extra1 = 'Blind '+xhigh+' < m_{jet} < '+xlow2+' GeV'  #extra1 = xlow+' < m_{jet1} < '+xhigh+' & '+xlow2+' < m_{jet1} < '+xhigh2+' GeV'
            extra2 = zrange.split(',')[0]+' < m_{jj} < '+ zrange.split(',')[1]+' TeV'


                    
        #leg = ROOT.TLegend(0.450436242,0.5531968,0.7231544,0.8553946)
        #leg = ROOT.TLegend(0.55809045,0.3063636,0.7622613,0.8520979)
        leg = ROOT.TLegend(0.5,0.45,0.82,0.88)
        leg.SetTextSize(0.045)
        c = self.get_canvas('c')
        pad1 = self.get_pad("pad1") #ROOT.TPad("pad1", "pad1", 0, 0.3, 1, 1.0)
        if axis == 'z': pad1.SetLogy()

        pad1.Draw()
        pad1.cd()	 
        outfile = ROOT.TFile.Open(self.options.output+"Histos"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root","RECREATE");
    
        histos[0].SetMinimum(ymin)
        histos[0].SetMaximum(ymax) 
        histos[0].SetTitle(hhtitle)
        histos[0].SetLineColor(self.colors[0])
        histos[0].SetLineWidth(2)
        histos[0].GetXaxis().SetTitle(xtitle)
        histos[0].GetXaxis().SetLabelSize(0.0)
        histos[0].GetYaxis().SetTitleOffset(1.3)
        histos[0].GetYaxis().SetTitle("Events")
        histos[0].GetYaxis().SetTitleOffset(1.3)
        histos[0].GetYaxis().SetTitle("Events / "+str(binwidth)+" GeV")
        if axis == 'z':
            histos[0].GetYaxis().SetTitle("Events / 100 GeV")
            histos[0] = self.fromGeVtoTeV(histos[0])
            histos[0].GetXaxis().SetRangeUser(1.246,6.)
        histos[0].GetYaxis().SetTitleSize(0.06)
        histos[0].GetYaxis().SetLabelSize(0.06)
        histos[0].Draw('HIST')
        print "---------------------------------------------------------------------------------------"
        print histos[0].Integral()
        print "---------------------------------------------------------------------------------------"

        if len(histos)>1:
            if axis == 'z':
                histos[1]= self.fromGeVtoTeV(histos[1])
                histos[2]= self.fromGeVtoTeV(histos[2])

            histos[1].SetLineColor(self.colors[1])
            histos[1].SetLineWidth(2)
            
            histos[2].SetLineColor(self.colors[2])
            histos[2].SetLineWidth(2)
            
        
            if self.options.addTop:
                histos[3].SetLineColor(self.colors[3])
                histos[3].SetLineWidth(2)
                if axis == 'z':
                    histos[3] =self.fromGeVtoTeV(histos[3])

            if self.options.addDIB:
                histos[4].SetLineColor(self.colors[4])
                histos[4].SetLineWidth(2)
                histos[5].SetLineColor(self.colors[5])
                histos[5].SetLineWidth(2)
                if axis == 'z':
                    histos[4] = self.fromGeVtoTeV(histos[4])
                    histos[5]= self.fromGeVtoTeV(histos[5])

        for i in range(4,len(histos)):
            histos[i].SetLineColor(self.colors[i])
            if axis == 'z':
                histos[i] = self.fromGeVtoTeV(histos[i])

            histos[i].Draw("histsame")
            name = histos[i].GetName().split("_")

            #if len(name)>2:
                #leg.AddEntry(histos[i],name[1],"l")
            #else:
                #leg.AddEntry(histos[i],name[0],"l")
        hdata.SetMarkerStyle(20)
        hdata.SetMarkerColor(ROOT.kBlack)
        hdata.SetLineColor(ROOT.kBlack)
        hdata.SetMarkerSize(0.7)
        if axis == 'z':
            hdata = self.fromGeVtoTeV(hdata)

        if errors!=None:
            if axis == 'z':
                errors[0] = self.fromGeVtoTeVGraph(errors[0])
            errors[0].SetFillColor(self.colors[0])
            errors[0].SetFillStyle(3001)
            errors[0].SetLineColor(self.colors[0])
            errors[0].SetLineWidth(0)
            errors[0].SetMarkerSize(0)

        
        #change this scaling in case you don't want to plot signal! has to match number of generated signal events
        scaling = self.options.signalScaleF
        print " ********** signal scaling : ",scaling
        eff = 0.1
        
        
        if hsig!= None: # and (self.options.name.find('sigonly')!=-1  and doFit==0):
            print "print do hsignal, that has integral ", hsig.Integral()
            if axis == 'z':
                hsig = self.fromGeVtoTeV(hsig)
            hsig.Write(self.signalName)
            if hsig.Integral()!=0. and scaling !=0 :   
                #hsig.Scale(scaling/normsig.getVal())
                print "sig integral ",hsig.Integral()
                hsig.Scale(scaling)
            print " after rescling check integral is ",hsig.Integral()
        
            hsig.SetFillColor(ROOT.kGreen-6)
            hsig.SetLineColor(ROOT.kBlack)
            hsig.SetLineStyle(1)
            #hsig.SetTitle("category  "+self.options.channel)
            hsig.Draw("HISTsame")
            #leg.AddEntry(hsig,"Signal pdf","F")
        #errors[0].Draw("E5same")
        if errors!=None:
            if axis=="z":
                errors[0].Draw("2same")
            else:
                errors[0].Draw("3same")
        histos[0].SetTitle("category  "+self.options.channel)
        histos[0].Draw("samehist")
        if len(histos)>1:
            if self.options.addTop: histos[3].Draw("histsame")
            histos[1].SetLineStyle(7)
            histos[2].SetLineStyle(6)
            if "ttbar" not in self.options.output: histos[1].Draw("histsame")
            if "ttbar" not in self.options.output: histos[2].Draw("histsame")
        drawBox = False
        if self.options.blind == True and axis!='z' and ( xrange == '55,215' or yrange == '55,215') :
            drawBox = True
            hdata.GetXaxis().SetRangeUser(55,65)
            hdata.DrawCopy("sameE0")
            hdata.GetXaxis().SetRangeUser(140,215)
            hdata.Draw("samePE0")
        else:
            hdata.Draw("samePE0")
        leg.SetLineColor(0)
        
        nevents = {}
        nevents["data"]=hdata.Integral()
        if pseudo == False:
            leg.AddEntry(hdata,"Data","ep")
            hdata.Write("Data")
        else:
            leg.AddEntry(hdata,"Simulation","ep")
            hdata.Write("Simulation")
        #leg.AddEntry(histos[0],"Signal+background fit","l")
        #if "ttbar" not in self.options.output:
            #leg.AddEntry(histos[0],"Background fit","l")
        if self.options.fitSignal==False or self.options.plotbonly==True:
            print " &&&&&&&& b only "
            leg.AddEntry(histos[0],"Background fit","l")
        elif self.options.fitSignal==True and self.options.plotbonly==False:
            leg.AddEntry(histos[0],"Signal+background fit","l")
            print " &&&&&&&& s+b only "
        else:
            print " &&&&&&&& else-> b only "
            leg.AddEntry(histos[0],"Background fit","l")
        histos[0].Write("BackgroundFit")
        if errors!=None:
            leg.AddEntry(errors[0],"#pm 1#sigma unc.","f")
            errors[0].Write("syst_unc")
            #to have the syst errors centered around zero (to be able to plot a nice pulls band) & rescaled by the stats unc.
            # these are used in the paper pull plot
            syst_band = ROOT.TGraphAsymmErrors()
            syst_band.Copy(errors[0])
            for i in range(0,errors[0].GetN()):
                X = ROOT.Double()
                Y = ROOT.Double()
                errors[0].GetPoint(i,X,Y)
                syst_band.SetPoint(i,X,0)
                if hdata.GetBinContent(i+1) ==0: continue
                Y = errors[0].GetErrorYhigh(i)
                X = hdata.GetBinWidth(i+1)/2
                syst_band.SetPointEYhigh(i,Y/hdata.GetBinError(i+1))
                syst_band.SetPointEXhigh(i,X)
                Y = errors[0].GetErrorYlow(i)
                syst_band.SetPointEYlow(i,Y/hdata.GetBinError(i+1))
                syst_band.SetPointEXlow(i,X)
            syst_band.Write("syst_band")

            syst_band_fit = ROOT.TGraphAsymmErrors()
            syst_band_fit.Copy(errors[0])
            for i in range(0,errors[0].GetN()):
                X = ROOT.Double()
                Y = ROOT.Double()
                errors[0].GetPoint(i,X,Y)
                syst_band_fit.SetPoint(i,X,0)
                if histos[0].GetBinContent(i+1) ==0: continue
                Y = errors[0].GetErrorYhigh(i)
                X = hdata.GetBinWidth(i+1)/2
                syst_band_fit.SetPointEYhigh(i,Y/ROOT.TMath.Sqrt(histos[0].GetBinContent(i+1)))
                syst_band_fit.SetPointEXhigh(i,X)
                Y = errors[0].GetErrorYlow(i)
                syst_band_fit.SetPointEYlow(i,Y/ROOT.TMath.Sqrt(histos[0].GetBinContent(i+1)))
                syst_band_fit.SetPointEXlow(i,X)
            syst_band_fit.Write("syst_band_fit")

        if len(histos)>1 and "ttbar" not in self.options.output:
            leg.AddEntry(histos[1],"W+jets","l")  ; print "Wjets ", histos[1].Integral(); nevents["Wjets"] = histos[1].Integral()
            histos[1].Write("Wjets")
            leg.AddEntry(histos[2],"Z+jets","l")  ; print "Zjets ", histos[2].Integral(); nevents["Zjets"] = histos[2].Integral()
            histos[2].Write("Zjets")
        if len(histos)>2:
            if self.options.addTop: leg.AddEntry(histos[3],"t#bar{t}","l"); print "all ttbar ", histos[3].Integral() ; nevents["TTbarall"] = histos[3].Integral()
            histos[3].Write("TTbarall")
            if len(histos)>6 and self.options.addDIB == False:
                if self.options.addTop: leg.AddEntry(histos[6],"res Top","l") ; print "res top ", histos[6].Integral(); nevents["resT"] = histos[6].Integral()
                histos[6].Write("TTbar_2resT")
                if self.options.addTop: leg.AddEntry(histos[7],"res W","l") ; print "res W  ", histos[7].Integral() ; nevents["resW"] = histos[7].Integral()
                histos[7].Write("TTbar_2resW")
                if self.options.addTop: leg.AddEntry(histos[8],"nonres Top","l") ; print "nonres top ", histos[8].Integral() ; nevents["nonresT"] = histos[8].Integral()
                histos[8].Write("TTbar_nonresonant")
                if self.options.addTop: leg.AddEntry(histos[9],"nonres Top + res Top","l") ; print "resT nonres T ", histos[9].Integral() ; nevents["resTnonresT"] = histos[9].Integral()
                histos[9].Write("TTbar_resTnonresT")
                if self.options.addTop: leg.AddEntry(histos[10],"nonres Top + res W","l"); print "res W nonresT ", histos[10].Integral(); nevents["resWnonresT"] = histos[10].Integral()
                histos[10].Write("TTbar_resWnonresT")
                if self.options.addTop: leg.AddEntry(histos[11],"res T + res W","l") ; print "resW resT ", histos[11].Integral(); nevents["resTresW"] = histos[11].Integral()
                histos[11].Write("TTbar_resTresW")
        if len(histos)>3:
            if self.options.addDIB:
                leg.AddEntry(histos[4],"WZ","l"); print "WZ ", histos[4].Integral() ; nevents["WZ"] = histos[4].Integral()
                leg.AddEntry(histos[5],"ZZ","l"); print "ZZ ", histos[5].Integral() ; nevents["ZZ"] = histos[5].Integral()
                histos[4].Write("WZ")
                histos[5].Write("ZZ")

        text = "G_{bulk} (%.1f TeV) #rightarrow WW"%(self.options.signalMass/1000.)
        if (self.options.signalMass%1000.)==0:
            text = "G_{bulk} (%i TeV) #rightarrow WW"%(self.options.signalMass/1000.)

        if self.signalName.find("BulkGZZ")!=-1:
            text = "G_{bulk} (%.1f TeV) #rightarrow ZZ"%(self.options.signalMass/1000.)
            if (self.options.signalMass%1000.)==0:
                text = "G_{bulk} (%i TeV) #rightarrow ZZ"%(self.options.signalMass/1000.)

        if self.signalName.find("RadionWW")!=-1:
            text = "Rad (%.1f TeV) #rightarrow WW"%(self.options.signalMass/1000.)
            if (self.options.signalMass%1000.)==0:
                text = "Rad (%i TeV) #rightarrow WW"%(self.options.signalMass/1000.)

        if self.signalName.find("RadionZZ")!=-1:
            text = "Rad (%.1f TeV) #rightarrow ZZ"%(self.options.signalMass/1000.)
            if (self.options.signalMass%1000.)==0:
                text = "Rad (%i TeV) #rightarrow ZZ"%(self.options.signalMass/1000.)
        
        if self.signalName.find("ZprimeWW")!=-1:
            text = "Z' (%.1f TeV) #rightarrow WW"%(self.options.signalMass/1000.)
            if (self.options.signalMass%1000.)==0:
                text = "Z' (%i TeV) #rightarrow WW"%(self.options.signalMass/1000.)
                
        if self.signalName.find("ZprimeZH")!=-1:
            text = "Z' (%.1f TeV) #rightarrow ZH"%(self.options.signalMass/1000.)
            if (self.options.signalMass%1000.)==0:
                text = "Z' (%i TeV) #rightarrow ZH"%(self.options.signalMass/1000.)
                
                
        if self.signalName.find("WprimeWZ")!=-1:
            text = "W' (%.1f TeV) #rightarrow WZ"%(self.options.signalMass/1000.)
            if (self.options.signalMass%1000.)==0:
                text = "W' (%i TeV) #rightarrow WZ"%(self.options.signalMass/1000.)
                
        if self.signalName.find("WprimeWH")!=-1:
            text = "W' (%.1f TeV) #rightarrow WH"%(self.options.signalMass/1000.)
            if (self.options.signalMass%1000.)==0:
                text = "W' (%i TeV) #rightarrow WH"%(self.options.signalMass/1000.)

        rescaletext = "(#times %i)"%scaling
        if scaling ==0: rescaletext = "(%f)"%fitted_r
        if self.signalName.find("VBF") !=-1:
            text = "VBF "+text

        if self.options.fitSignal==True: 
            leg.AddEntry(hsig,text,"F")
            leg.AddEntry(hsig,rescaletext,"")
        leg.Draw("same")
        
        #errors[0].Draw("E2same")
        print "projection "+extra1+"  "+extra2+" \n"
        
        chi2 = self.getChi2proj(histos[0],hdata)
        print hdata.GetEntries(),hdata.Integral()
        if chi2[1]!=0:
            print "Projection %s: Chi2/ndf = %.2f/%i"%(axis,chi2[0],chi2[1]),"= %.2f"%(chi2[0]/chi2[1])," prob = ",ROOT.TMath.Prob(chi2[0],chi2[1])

        pt = ROOT.TPaveText(0.18,0.06,0.54,0.17,"NDC")
        pt.SetTextFont(42)
        pt.SetTextSize(0.05)
        pt.SetTextAlign(12)
        pt.SetFillColor(0)
        pt.SetBorderSize(0)
        pt.SetFillStyle(0)
        if chi2[1]!=0:
            pt.AddText("Chi2/ndf = %.2f/%i = %.2f"%(chi2[0],chi2[1],chi2[0]/chi2[1]))
            pt.AddText("Prob = %.3f"%ROOT.TMath.Prob(chi2[0],chi2[1]))
        #pt.Draw()

        #pt2 = ROOT.TPaveText(0.125,0.79,0.99,0.4,"NDC")
        #pt2 = ROOT.TPaveText(0.55,0.35,0.99,0.32,"NDC")
        pt2 = ROOT.TPaveText(0.4,0.38,0.99,0.44,"NDC")
        pt2.SetTextFont(42)
        pt2.SetTextSize(0.04)
        pt2.SetTextAlign(12)
        pt2.SetFillColor(0)
        pt2.SetBorderSize(0)
        pt2.SetFillStyle(0)
        categorystring= self.options.channel.replace('_control_region','').replace("_"," ")
        if categorystring.find("VBF")==-1: categorystring="DY/gg "+categorystring
        print " categorystring ",categorystring
        pt2.AddText(categorystring+" category")
        #pt2.AddText("category  "+self.options.channel)
        pt2.Draw()

        #pt3 = ROOT.TPaveText(0.65,0.39,0.99,0.52,"NDC")
        pt3 = ROOT.TPaveText(0.18,0.55,0.39,0.68,"NDC")
        pt3.SetTextFont(42)
        pt3.SetTextSize(0.04)
        pt3.SetTextAlign(12)
        pt3.SetFillColor(0)
        pt3.SetBorderSize(0)
        pt3.SetFillStyle(0)
        pt3.AddText(extra1)
        pt3.AddText(extra2)
        pt3.Draw()

        CMS_lumi.CMS_lumi(pad1, 4, 10)
        
        pad1.Modified()
        pad1.Update()
        
        c.Update()
        c.cd()
        pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
        pad2.SetTopMargin(0.04)
        pad2.SetBottomMargin(0.4)
        #pad2.SetGridy()
        pad2.Draw()
        pad2.cd()
        
        #for ratio
        #graphs = addRatioPlot(hdata,histos[0],nBins,errors[0])
        #graphs[1].Draw("AP")
        #graphs[0].Draw("E3same")
        #graphs[1].Draw("Psame")
        
        #for pulls
        if errors ==None: errors=[0,0];
        if self.options.name.find('sigonly')!=-1: graphs = self.addPullPlot(hdata,hsig,nBins,errors[0])
        else:
            graphs = self.addPullPlot(hdata,histos[0],nBins,errors[0])
            statgraphs = self.addStatPullPlot(hdata,histos[0],nBins)
        # graphs = addRatioPlot(hdata,histos[0],nBins,errors[0])
        if axis == 'z':
            graphs[0] = self.fromGeVtoTeV(graphs[0])
        graphs[0].Write("pulls_syst_stat")
        statgraphs[0].Write("pulls_stat")
        if axis == 'z':
            graphs[0].GetXaxis().SetRangeUser(1.246,6.)
        graphs[0].Draw("HIST")
        if self.options.blind == True and axis != 'z' and drawBox == True:
            box = ROOT.TBox(65,graphs[0].GetMinimum(),140,graphs[0].GetMaximum())
            box.SetFillColor(0)
            box.Draw("same")

        pad2.Modified()
        pad2.Update()
        outfile.Close()
        c.cd()
        c.Update()
        c.Modified()
        c.Update()
        c.cd()
        c.SetSelected(c)
        #errors[0].Draw("E2same")
        #CMS_lumi.CMS_lumi(c, 0, 11)
        #c.cd()
        #c.Update()
        #c.RedrawAxis()
        #frame = c.GetFrame()
        #frame.Draw()
        if self.logfile!="":
            self.calculateChi2ForSig(hdata,hsig,axis,self.logfile,"\n \n projection "+extra1+"  "+extra2+" \n")
        if self.options.prelim==0:
            print "save plot as ", self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".pdf" 
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".png")
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".pdf")
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".C")
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+".root")
        else:
            print "save plot as ",   self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+"_prelim.pdf"
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+"_prelim.png")
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+"_prelim.pdf")
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+"_prelim.C")
            c.SaveAs(self.options.output+"PostFit"+self.options.label+"_"+htitle.replace(' ','_').replace('.','_').replace(':','_').replace(',','_')+"_prelim.root")


class Projection():
    xBins_redux ={}
    yBins_redux ={}
    zBins_redux ={}
    xBinsWidth ={}
    yBinsWidth ={}
    zBinsWidth ={}
    
    BinsWidth_1 ={}
    BinsWidth_2 ={}
    BinsWidth_3 ={}
    
    
    Bins_redux ={}
    Bins_redux_1 ={}
    Bins_redux_2 ={}

    xBinslowedge =[]
    yBinslowedge =[]
    zBinslowedge =[]
    Binslowedge =[]
    neventsPerBin_1 = {}
    
    h=[]
    hfinals = []
    lv=[]
    lv1_sig=[]
    h1_sig = 0
    dh = None
    data = None
    h1_sig = None
    
    M1=None
    M2=None
    M3=None
    argset_ws = None
    workspace = None
    htot_sig = None
    htot_nonres = None
    htot_Wres = None
    htot_Zres = None
    htot_WZ = None
    htot_ZZ = None
    htot_TTJets = None
    htot_TTJetsTop = None
    htot_TTJetsW = None
    htot_TTJetsNonRes =None
    htot_TTJetsTnonresT= None
    htot_TTJetsWnonresT= None
    htot_TTJetsresTresW= None
    htot_TTJetsresWresT= None
    htot = None
    doFit = False
    axis = ""
    maxYaxis = 0
    fitres = None
    
    def __init__(self,hinMC,opt_range,workspace,doFit,isBlinded=False,plotBonly=False,fitres=None):
        self.doFit = doFit
        self.fitres = fitres
        self.workspace = workspace
        #################################################
        xBins= self.getListOfBins(hinMC,"x")
        self.xBinslowedge = self.getListOfBinsLowEdge(hinMC,'x')
        self.xBinsWidth   = self.getListOfBinsWidth(hinMC,"x")     
        #################################################
        yBins= self.getListOfBins(hinMC,"y")
        self.yBinslowedge = self.getListOfBinsLowEdge(hinMC,'y')     
        self.yBinsWidth   = self.getListOfBinsWidth(hinMC,"y")
        #################################################
        zBins= self.getListOfBins(hinMC,"z")
        self.zBinslowedge = self.getListOfBinsLowEdge(hinMC,'z')
        self.zBinsWidth   = self.getListOfBinsWidth(hinMC,"z")
        ################################################# 
        
        #################################################
        x = self.getListFromRange(opt_range[0],isBlinded)
        y = self.getListFromRange(opt_range[1],isBlinded)
        z = self.getListFromRange(opt_range[2],isBlinded)
        
        self.xBins_redux = self.reduceBinsToRange(xBins,x)
        self.yBins_redux = self.reduceBinsToRange(yBins,y)
        self.zBins_redux = self.reduceBinsToRange(zBins,z)

        ################################################# 
    
    def getListFromRange(self,xyzrange,isBlinded):
        r=[]
        if isBlinded == True and len(xyzrange.split(","))==4:
            a,b,c,d = xyzrange.split(",")
            r.append(float(a))
            r.append(float(b))
            r.append(float(c))
            r.append(float(d))
        else:
            a,b = xyzrange.split(",")
            r.append(float(a))
            r.append(float(b))
        return r


    def getListOfBins(self,hist,dim):
        axis =0
        N = 0
        if dim =="x":
            axis= hist.GetXaxis()
            N = hist.GetNbinsX()
        if dim =="y":
            axis = hist.GetYaxis()
            N = hist.GetNbinsY()
        if dim =="z":
            axis = hist.GetZaxis()
            N = hist.GetNbinsZ()
        if axis==0:
            return {}
        
        mmin = axis.GetXmin()
        mmax = axis.GetXmax()
        bins ={}
        for i in range(1,N+1): bins[i] = axis.GetBinCenter(i) 
        
        return bins


    def getListOfBinsLowEdge(self,hist,dim):
        axis =0
        N = 0
        if dim =="x":
            axis= hist.GetXaxis()
            N = hist.GetNbinsX()
        if dim =="y":
            axis = hist.GetYaxis()
            N = hist.GetNbinsY()
        if dim =="z":
            axis = hist.GetZaxis()
            N = hist.GetNbinsZ()
        if axis==0:
            return {}
        
        mmin = axis.GetXmin()
        mmax = axis.GetXmax()
        r=[]
        for i in range(1,N+2): r.append(axis.GetBinLowEdge(i)) 

        return array("d",r)


    def getListOfBinsWidth(self,hist,dim):
        axis =0
        N = 0
        if dim =="x":
            axis= hist.GetXaxis()
            N = hist.GetNbinsX()
        if dim =="y":
            axis = hist.GetYaxis()
            N = hist.GetNbinsY()
        if dim =="z":
            axis = hist.GetZaxis()
            N = hist.GetNbinsZ()
        if axis==0:
            return {}
        
        mmin = axis.GetXmin()
        mmax = axis.GetXmax()
        r ={}
        for i in range(0,N+2):
            #v = mmin + i * (mmax-mmin)/float(N)
            r[i] = axis.GetBinWidth(i)
        return r 

    
    def reduceBinsToRange(self,Bins,r):
        if r[0]==0 and r[1]==-1:
            return Bins
        result ={}
        for key, value in Bins.iteritems():
            if value >= r[0] and value <=r[1]:
                result[key]=value
            if len(r)==4:
                if value >= r[2] and value <=r[3]:
                    result[key]=value

        return result


    def doProjection(self,data,pdfs,norms,axis,pdf_sig=None,norm_sig=0,show_all=False,plotBonly=False):
        self.neventsPerBin_1 = {}
        self.h=[]
        self.hfinals = []
        self.lv=[]
        self.lv1_sig=[]
        self.h1_sig = 0
        self.dh = None
        self.data = None
        self.h1_sig = None
        self.maxYaxis = 0
        self.axis = axis
        if axis=="x":
           self.dh = ROOT.TH1F("dh"+axis,"dh"+axis,len(self.xBinslowedge)-1,self.xBinslowedge)
           self.Bins_redux = self.xBins_redux
           self.Bins_redux_1 = self.yBins_redux
           self.Bins_redux_2 = self.zBins_redux
           self.Binslowedge = self.xBinslowedge
           self.BinsWidth_1 = self.xBinsWidth
           self.BinsWidth_2 = self.yBinsWidth
           self.BinsWidth_3 = self.zBinsWidth
           # get variables from workspace 
           self.M1 = self.workspace.var("MJ1");
           self.M2 = self.workspace.var("MJ2");
           self.M3 = self.workspace.var("MJJ");
           for xk,xv in self.xBins_redux.iteritems():
                self.neventsPerBin_1[xk]=0
        if axis=="y":
           self.dh = ROOT.TH1F("dh"+axis,"dh"+axis,len(self.yBinslowedge)-1,self.yBinslowedge)
           self.Bins_redux = self.yBins_redux
           self.Bins_redux_1 = self.xBins_redux
           self.Bins_redux_2 = self.zBins_redux
           self.BinsWidth_1 = self.yBinsWidth
           self.BinsWidth_2 = self.xBinsWidth
           self.BinsWidth_3 = self.zBinsWidth
           self.Binslowedge = self.yBinslowedge
           # get variables from workspace 
           self.M1 = self.workspace.var("MJ2");
           self.M2 = self.workspace.var("MJ1");
           self.M3 = self.workspace.var("MJJ");
           for yk,yv in self.yBins_redux.iteritems():
                self.neventsPerBin_1[yk]=0
        if axis=="z":
           self.dh = ROOT.TH1F("dh"+axis,"dh"+axis,len(self.zBinslowedge)-1,self.zBinslowedge)
           self.Bins_redux = self.zBins_redux
           self.Bins_redux_1 = self.xBins_redux
           self.Bins_redux_2 = self.yBins_redux
           self.BinsWidth_1 = self.zBinsWidth
           self.BinsWidth_2 = self.xBinsWidth
           self.BinsWidth_3 = self.yBinsWidth
           self.Binslowedge = self.zBinslowedge
           # get variables from workspace 
           self.M1 = self.workspace.var("MJJ");
           self.M2 = self.workspace.var("MJ1");
           self.M3 = self.workspace.var("MJ2");
           for zk,zv in self.zBins_redux.iteritems():
                self.neventsPerBin_1[zk]=0 
        argset = ROOT.RooArgSet();
        argset.add(self.M3);
        argset.add(self.M2);
        argset.add(self.M1);
        self.args_ws = argset
        print "initialize histograms with ",self.Binslowedge
        self.data = ROOT.RooDataHist("data"+axis,"data"+axis,self.args_ws,data)
        self.htot_nonres = ROOT.TH1F("htot_nonres"+axis,"htot_nonres"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_sig = ROOT.TH1F("htot_sig"+axis,"htot_sig"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot = ROOT.TH1F("htot"+axis,"htot"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_Wres = ROOT.TH1F("htot_Wres"+axis,"htot_Wres"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_Zres = ROOT.TH1F("htot_Zres"+axis,"htot_Zres"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJets = ROOT.TH1F("htot_TTJets"+axis,"htot_TTJets"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJetsTop = ROOT.TH1F("htot_TTJetsTop"+axis,"htot_TTJetsTop"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJetsW = ROOT.TH1F("htot_TTJetsW"+axis,"htot_TTJetsW"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJetsNonRes = ROOT.TH1F("htot_TTJetsNonRes"+axis,"htot_TTJetsNonRes"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJetsTnonresT = ROOT.TH1F("htot_TTJetsTnonresT"+axis,"htot_TTJetsTnonresT"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJetsWnonresT  = ROOT.TH1F("htot_TTJetsWnonresT"+axis,"htot_TTJetsWnonresT"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJetsresTresW= ROOT.TH1F("htot_TTJetsresTresW"+axis,"htot_TTJetsresTresW"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_TTJetsresWresT= ROOT.TH1F("htot_TTJetsresWresT"+axis,"htot_TTJetsresWresT"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_WZ = ROOT.TH1F("htot_WZ"+axis,"htot_WZ"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        self.htot_ZZ = ROOT.TH1F("htot_ZZ"+axis,"htot_ZZ"+axis,len(self.Binslowedge)-1,self.Binslowedge)
        
        for p in pdfs:
            self.h.append( ROOT.TH1F("h_"+p.GetName(),"h_"+p.GetName(),len(self.Binslowedge)-1,self.Binslowedge))
            self.lv.append({})
        for i in range(0,len(pdfs)):
            for ik,iv in self.Bins_redux.iteritems(): self.lv[i][iv]=0
        
        if pdf_sig!=None:
                self.h1_sig = ROOT.TH1F("h1_"+pdf_sig.GetName(),"h1_"+pdf_sig.GetName(),len(self.Binslowedge)-1,self.Binslowedge)
                self.lv1_sig.append({})
                for ik,iv in self.Bins_redux.iteritems(): self.lv1_sig[0][iv]=0
	
    	
        for ik, iv in self.Bins_redux_1.iteritems():
            self.M2.setVal(iv)
            for jk, jv in self.Bins_redux_2.iteritems():
                self.M3.setVal(jv)
                for kk,kv in self.Bins_redux.iteritems():
                    self.M1.setVal(kv)
                    self.neventsPerBin_1[kk] += self.data.weight(self.args_ws)
                    i=0
                    binV = self.BinsWidth_2[ik]*self.BinsWidth_3[jk]*self.BinsWidth_1[kk]
                    for p in pdfs:
                        if "nonRes" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["nonRes"][0].getVal()
                        if "Wjets" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["Wjets"][0].getVal()
                        if "Zjets" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["Zjets"][0].getVal()
                        if "TTJetsTop_" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["TTJetsTop"][0].getVal()
                        if "TTJetsW_" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["TTJetsW"][0].getVal()
                        if "TTJetsNonRes_" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["TTJetsNonRes"][0].getVal()
                        if "TTJetsTNonResT_" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["TTJetsTNonResT"][0].getVal()
                        if "TTJetsWNonResT_" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["TTJetsWNonResT"][0].getVal()
                        if "TTJetsResWResT_" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["TTJetsResWResT"][0].getVal()    #; print norms["TTJetsResWResT"][0].getVal()
                        if "WZ" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["WZ"][0].getVal()
                        if "ZZ" in str(p.GetName()) :
                            self.lv[i][kv] += p.getVal(self.args_ws)*binV*norms["ZZ"][0].getVal()

                        i+=1
                    if pdf_sig!=None:
                        self.lv1_sig[0][kv] += pdf_sig.getVal(self.args_ws)*binV
        return self.fillHistos(pdfs,data,norms,pdf_sig,norm_sig,show_all,plotBonly)
        
    def fillHistos(self,pdfs,data,norms,pdf_sig=None,norm_sig=None,show_all=False,plotBonly=False):
        print " make Projection ", self.axis
        for i in range(0,len(pdfs)):
            for ik,iv in self.Bins_redux.iteritems():
                tmp = self.lv[i][iv]
                if tmp >+ self.maxYaxis: self.maxYaxis = tmp
                if "nonRes" in str(pdfs[i].GetName()) : self.htot_nonres.Fill(iv,self.lv[i][iv]); 
                elif "Wjets" in str(pdfs[i].GetName()) : self.htot_Wres.Fill(iv,self.lv[i][iv]); 
                elif "Zjets" in str(pdfs[i].GetName()) : self.htot_Zres.Fill(iv,self.lv[i][iv]); 
                elif "TTJetsTop_" in str(pdfs[i].GetName()): self.htot_TTJets.Fill(iv,self.lv[i][iv]); self.htot_TTJetsTop.Fill(iv,self.lv[i][iv])
                elif "TTJetsW_" in str(pdfs[i].GetName()): self.htot_TTJets.Fill(iv,self.lv[i][iv]); self.htot_TTJetsW.Fill(iv,self.lv[i][iv])
                elif "TTJetsNonRes_" in str(pdfs[i].GetName()):
                    #print "nonresT ",pdfs[i].GetName()
                    self.htot_TTJets.Fill(iv,self.lv[i][iv]) ; self.htot_TTJetsNonRes.Fill(iv,self.lv[i][iv])
                elif "TTJetsTNonResT_" in str(pdfs[i].GetName()): 
                    self.htot_TTJets.Fill(iv,self.lv[i][iv]) ;
                    #print "TnonresT ",pdfs[i].GetName()
                    self.htot_TTJetsTnonresT.Fill(iv,self.lv[i][iv])
                elif "TTJetsWNonResT_" in str(pdfs[i].GetName()): 
                    self.htot_TTJets.Fill(iv,self.lv[i][iv]) ; self.htot_TTJetsWnonresT.Fill(iv,self.lv[i][iv])
                    #print "WnonresT ",pdfs[i].GetName()
                elif "TTJetsresWresT" in str(pdfs[i].GetName()): self.htot_TTJets.Fill(iv,self.lv[i][iv]) ; self.htot_TTJetsresWresT.Fill(iv,self.lv[i][iv])
                elif "TTJetsResWResT_" in str(pdfs[i].GetName()):
                    self.htot_TTJets.Fill(iv,self.lv[i][iv]) ; self.htot_TTJetsresTresW.Fill(iv,self.lv[i][iv]);
                elif "WZ" in str(pdfs[i].GetName()) : self.htot_WZ.Fill(iv,self.lv[i][iv]);
                elif "ZZ" in str(pdfs[i].GetName()) : self.htot_ZZ.Fill(iv,self.lv[i][iv]);
                
                else: self.h[i].Fill(iv,tmp);
        
        if pdf_sig!=None:
            print "fill signal "
            for ik,iv in self.Bins_redux.iteritems(): self.htot_sig.Fill(iv,self.lv1_sig[0][iv]*norm_sig[0].getVal()); # print self.lv1_sig[0][iv]*norm_sig[0]

        self.htot.Add(self.htot_nonres)
        if self.htot_Wres!=None: self.htot.Add(self.htot_Wres)
        if self.htot_Zres!=None: self.htot.Add(self.htot_Zres)
        if self.htot_WZ!=None: self.htot.Add(self.htot_WZ)
        if self.htot_ZZ!=None: self.htot.Add(self.htot_ZZ)
        if self.htot_TTJets!=None: self.htot.Add(self.htot_TTJets)
        if self.htot_sig!=None and plotBonly == False: self.htot.Add(self.htot_sig);
        print "htot sig ",str(self.htot_sig.Integral())
        print "htot integral" , self.htot.Integral()
        print "htot_Wres integral" , self.htot_Wres.Integral()
        print "htot_WZ integral" , self.htot_WZ.Integral()
        self.hfinals.append(self.htot)
        if self.htot_Wres!=None: self.hfinals.append(self.htot_Wres)
        if self.htot_Zres!=None: self.hfinals.append(self.htot_Zres)
        if self.htot_TTJets!=None: self.hfinals.append(self.htot_TTJets)
        if self.htot_WZ!=None: self.hfinals.append(self.htot_WZ)
        if self.htot_ZZ!=None: self.hfinals.append(self.htot_ZZ)
        if show_all:
            if self.htot_TTJetsTop!=None: self.hfinals.append(self.htot_TTJetsTop)
            if self.htot_TTJetsW!=None: self.hfinals.append(self.htot_TTJetsW)
            if self.htot_TTJetsNonRes!=None: self.hfinals.append(self.htot_TTJetsNonRes)
            if self.htot_TTJetsTnonresT!=None: self.hfinals.append(self.htot_TTJetsTnonresT)
            if self.htot_TTJetsWnonresT!=None: self.hfinals.append(self.htot_TTJetsWnonresT)
            if self.htot_TTJetsresTresW!=None: self.hfinals.append(self.htot_TTJetsresTresW)
        #for i in range(10,len(h)): hfinals.append(h[i])    
        for b,v in self.neventsPerBin_1.iteritems(): self.dh.SetBinContent(b,self.neventsPerBin_1[b]);
        self.dh.SetBinErrorOption(ROOT.TH1.kPoisson)
        if self.doFit:
            errors = self.draw_error_band(norms,pdfs[-1],pdf_sig)
        else: errors =  None
        return [self.hfinals,self.dh, self.htot_sig,self.axis,self.Binslowedge,self.maxYaxis, norm_sig[0],errors]
        
    
    def draw_error_band(self,norms,rpdf1,pdf_sig):
        histo_central = self.htot
        print norms
        try:
            norms["TTJetsTNonResT"][0].getVal()
            allbkg = True
        except:
            allbkg = False
        try:
            norms["WZ"][0].getVal()
            dibbkg = True
        except:
            dibbkg = False

        if allbkg == True and not dibbkg:
            norm1 = norms["nonRes"][0].getVal()+norms["Wjets"][0].getVal()+norms["Zjets"][0].getVal()+norms["TTJetsTNonResT"][0].getVal()+norms["TTJetsWNonResT"][0].getVal()+norms["TTJetsW"][0].getVal()+norms["TTJetsNonRes"][0].getVal()+norms["TTJetsResWResT"][0].getVal()+norms["TTJetsTop"][0].getVal()
            err_norm1 = math.sqrt(norms["nonRes"][1]*norms["nonRes"][1]+norms["Wjets"][1]*norms["Wjets"][1]+norms["Zjets"][1]*norms["Zjets"][1]+norms["TTJetsTNonResT"][1]*norms["TTJetsTNonResT"][1]+norms["TTJetsWNonResT"][1]*norms["TTJetsWNonResT"][1]+norms["TTJetsW"][1]*norms["TTJetsW"][1]+norms["TTJetsNonRes"][1]*norms["TTJetsNonRes"][1]+norms["TTJetsResWResT"][1]*norms["TTJetsResWResT"][1]+norms["TTJetsTop"][1]*norms["TTJetsTop"][1])
        elif allbkg == True and dibbkg == True:
            norm1 = norms["nonRes"][0].getVal()+norms["Wjets"][0].getVal()+norms["Zjets"][0].getVal()+norms["TTJetsTNonResT"][0].getVal()+norms["TTJetsWNonResT"][0].getVal()+norms["TTJetsW"][0].getVal()+norms["TTJetsNonRes"][0].getVal()+norms["TTJetsResWResT"][0].getVal()+norms["TTJetsTop"][0].getVal()+norms["WZ"][0].getVal()+norms["ZZ"][0].getVal()
            err_norm1 = math.sqrt(norms["nonRes"][1]*norms["nonRes"][1]+norms["Wjets"][1]*norms["Wjets"][1]+norms["Zjets"][1]*norms["Zjets"][1]+norms["TTJetsTNonResT"][1]*norms["TTJetsTNonResT"][1]+norms["TTJetsWNonResT"][1]*norms["TTJetsWNonResT"][1]+norms["TTJetsW"][1]*norms["TTJetsW"][1]+norms["TTJetsNonRes"][1]*norms["TTJetsNonRes"][1]+norms["TTJetsResWResT"][1]*norms["TTJetsResWResT"][1]+norms["TTJetsTop"][1]*norms["TTJetsTop"][1]+norms["WZ"][1]*norms["WZ"][1]+norms["ZZ"][1]*norms["ZZ"][1])

        else:
            norm1 = norms["nonRes"][0].getVal()+norms["Wjets"][0].getVal()+norms["Zjets"][0].getVal()
            err_norm1 = math.sqrt(norms["nonRes"][1]*norms["nonRes"][1]+norms["Wjets"][1]*norms["Wjets"][1]+norms["Zjets"][1]*norms["Zjets"][1])

        x_min = self.Binslowedge
        proj = self.axis
        rand = ROOT.TRandom3(1234);
        number_errorband = 100
        #print " number_errorband reduced to "+str(number_errorband)+" for speed reasons!"
        syst = [0 for i in range(number_errorband)]
      
        value = [0 for x in range(len(x_min))]  
        number_point = len(value)
        par_pdf1 = rpdf1.getParameters(self.args_ws)  
        iter = par_pdf1.createIterator()
        var = iter.Next()
        print var.GetName()
        for j in range(number_errorband):
            syst[j] = ROOT.TGraph(number_point+1);
            #paramters value are randomized using rfres and this can be done also if they are not decorrelate
            par_tmp = ROOT.RooArgList(self.fitres.randomizePars())
            iter = par_pdf1.createIterator()
            var = iter.Next()

            while var:
                index = par_tmp.index(var.GetName())
                if index != -1:
                    #print "pdf1",var.GetName(), var.getVal(), var.getError()
                    var.setVal(par_tmp.at(index).getVal())
                    #print " ---> new value: ",var.getVal()
                var = iter.Next()

            norm1_tmp = rand.Gaus(norm1,err_norm1); #new poisson random number of events
            value = [0 for i in range(number_point)]
            for ik, iv in self.Bins_redux.iteritems():
                self.M1.setVal(iv)
                for jk, jv in self.Bins_redux_1.iteritems():
                    self.M2.setVal(jv)
                    for kk,kv in self.Bins_redux_2.iteritems():
                        self.M3.setVal(kv)
                        binV = self.BinsWidth_1[ik]*self.BinsWidth_2[jk]*self.BinsWidth_3[kk]
                        value[ik-1] += (norm1_tmp*rpdf1.getVal( self.args_ws )*binV)

            for ix,x in enumerate(x_min):
                syst[j].SetPoint(ix, x, value[ix])

        #Try to build and find max and minimum for each point --> not the curve but the value to do a real envelope -> take one 2sigma interval
        errorband = ROOT.TGraphAsymmErrors()#ROOT.TH1F("errorband","errorband",len(x_min)-1,x_min)

        val = [0 for i in range(number_errorband)]
        for ix,x in enumerate(x_min):
    
            for j in range(number_errorband):
                val[j]=(syst[j]).GetY()[ix]
            val.sort()
            errorband.SetPoint(ix,x_min[ix]+histo_central.GetBinWidth(ix+1)/2.,histo_central.GetBinContent(ix+1))
            errup = (val[int(0.84*number_errorband)]-histo_central.GetBinContent(ix+1)) #ROOT.TMath.Abs
            errdn = ( histo_central.GetBinContent(ix+1)-val[int(0.16*number_errorband)])
            #print "error up "+str(errup)+" error down "+str(errdn)
            errorband.SetPointError(ix,histo_central.GetBinWidth(ix+1)/2.,histo_central.GetBinWidth(ix+1)/2.,ROOT.TMath.Abs(errdn),ROOT.TMath.Abs(errup))
        errorband.SetFillColor(ROOT.kBlack)
        errorband.SetFillStyle(3008)
        errorband.SetLineColor(ROOT.kGreen)
        errorband.SetMarkerSize(0)
       
        return [errorband]
    
    
def definefinalPDFs(options,axis,allpdfs):
    allpdfsz = allpdfs
    listofextrapdf = []
    if axis=="z":
         #let's have always pre-fit and post-fit as firt elements here, and add the optional shapes if you want with options.pdf
         listofextrapdf = options.pdfz.split(",")
    if axis=="x": listofextrapdf = options.pdfx.split(",")
    if axis=="x": listofextrapdf = options.pdfy.split(",")
    for p in listofextrapdf:
        if p == '': continue
        print "add pdf:",p
        args[p].Print()
        if p.find("2016")!=-1:
            allpdfsz["2016"].append(args[p])
        if p.find("2017")!=-1:
            allpdfsz["2017"].append(args[p])
        if p.find("2018")!=-1:
            allpdfsz["2018"].append(args[p])
    return allpdfsz
