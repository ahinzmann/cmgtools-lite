import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
from array import array
import math
import CMS_lumi
import numpy as np
from tools import PostFitTools
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gROOT.ProcessLine(".x tdrstyle.cc");

# NB running on ttbar only or plotting all ttbar components and DIB do not work together

addTT = False 
parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output folder name",default='')
parser.add_option("-n","--name",dest="name",help="Input workspace",default='workspace.root')
parser.add_option("-j","--jsonname",dest="jsonname",help="write the name of the output json file, the category will be automatically inserted",default='ttbarNorm')
parser.add_option("-i","--input",dest="input",help="Input nonRes histo",default='JJ_HPHP.root')
parser.add_option("-x","--xrange",dest="xrange",help="set range for x bins in projection",default="0,-1")
parser.add_option("-y","--yrange",dest="yrange",help="set range for y bins in projection",default="0,-1")
parser.add_option("-z","--zrange",dest="zrange",help="set range for z bins in projection",default="0,-1")
parser.add_option("-p","--projection",dest="projection",help="choose which projection should be done",default="xyz")
parser.add_option("-d","--data",dest="data",action="store_true",help="make also postfit plots",default=True)
parser.add_option("-l","--label",dest="label",help="add extra label such as pythia or herwig",default="")
parser.add_option("--log",dest="log",help="write fit result to log file",default="fit_results.log")
parser.add_option("--blind",dest="blind",action="store_true",help="Use to blind data in control region",default=False) 
parser.add_option("--pdfz",dest="pdfz",help="name of pdfs lie PTZUp etc",default="")
parser.add_option("--pdfx",dest="pdfx",help="name of pdfs lie PTXUp etc",default="")
parser.add_option("--pdfy",dest="pdfy",help="name of pdfs lie PTYUp etc",default="")
parser.add_option("-s","--signal",dest="fitSignal",action="store_true",help="do S+B fit",default=False)
parser.add_option("-t","--addTop",dest="addTop",action="store_true",help="Fit top",default=False)
parser.add_option("--addDIB",dest="addDIB",action="store_true",help="Fit DIB",default=False)
parser.add_option("-M","--mass",dest="signalMass",type=float,help="signal mass",default=1560.)
parser.add_option("--signalScaleF",dest="signalScaleF",type=float,help="scale factor to apply to signal when drawing so its still visible!",default=500.)
parser.add_option("--prelim",dest="prelim",help="add preliminary label",default="Preliminary")
parser.add_option("--channel",dest="channel",help="which category to use? ",default="VV_HPHP")
parser.add_option("--doFit",dest="fit",action="store_true",help="actually fit the the distributions",default=False)
parser.add_option("-v","--doVjets",dest="doVjets",action="store_true",help="Fit top",default=False)
parser.add_option("--slopes",dest="slopes",action="store_true",help="save ttbar slopes",default=False)
parser.add_option("--pseudo",dest="pseudo",action="store_true",help="write pseudodata in legend",default=False)
parser.add_option("--both",dest="both",action="store_true",help="add projections with exchanged X and Y projections",default=False)
parser.add_option("--plotbonly",dest="plotbonly",action="store_true",help="plot b only",default=False)

(options,args) = parser.parse_args()
ROOT.gStyle.SetOptStat(0)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)

period = "2016"
if options.name.find("2017")!=-1: period = "2017"
if options.name.find("2018")!=-1: period = "2018"
if options.name.find("Run2")!=-1: period = "Run2"
if options.name.find("1617")!=-1: period = "1617"

showallTT=False
signalName = "ZprimeZH"
if options.name.find("ZHinc")!=-1:
    signalName="ZprimeZHinc"
if options.name.find("WZ")!=-1:
    signalName="WprimeWZ"
if options.name.find("WH")!=-1:
    signalName="WprimeWH"
if options.name.find("WHinc")!=-1:
    signalName="WprimeWHinc"
if options.name.find("ZprimeWW")!=-1:
    signalName="ZprimeWW"
if options.name.find("BulkGWW")!=-1:
    signalName="BulkGWW"
if options.name.find("BulkGZZ")!=-1:
    signalName="BulkGZZ"
if options.name.find("RadionZZ")!=-1:
    signalName="RadionZZ"
if options.name.find("RadionWW")!=-1:
    signalName="RadionWW"
if options.name.find("VBF_"+signalName)!=-1:
    signalName="VBF_"+signalName

def addGraph(graphs):
    if graphs[0]==None: return None
    gnew = ROOT.TGraphAsymmErrors()
    h = graphs[0].GetHistogram()
    for p in range(0,h.GetNbinsX()):
        x = 0.
        y = 0.
        ex = 0.
        ey = 0.
        for g in graphs:
            x = h.GetBinCenter(p)
            y += g.Eval(x)
            ex = g.GetErrorX(p)
            ey += pow(g.GetErrorY(p),2)
        gnew.SetPoint(p,x,y)
        gnew.SetPointError(p,ex,np.sqrt(ey))

def addResults(results): #self.hfinals,self.dh, self.htot_sig,self.axis,self.Binslowedge,self.maxYaxis, norm_sig[0],errors
    histos = results[0][0]
    dh = results[0][1]
    hsig = results[0][2]
    maxY = results[0][5]
    normsig = results[0][6]
    errs = []
    for i in range(0,len(results)):
        errs.append(results[i][7])
    errors = addGraph(errs)
    for j in range(1,len(results)):
        dh.Add(results[j][1])
        hsig.Add(results[j][2])
        maxY += results[j][5]
        maxY += normsig[j][6]
        for i in range(0,len(histos)):
            histos[i].Add(results[j][i])
    return [histos,dh,hsig,results[0][3],results[0][4],maxY,normsig,errors]


def writeLogfile(options,fitresult):
    if options.log!="":
     	 params = fitresult.floatParsFinal()
     	 paramsinit = fitresult.floatParsInit()
     	 paramsfinal = ROOT.RooArgSet(params)
     	 paramsfinal.writeToFile(options.output+options.log)
     	 logfile = open(options.output+options.log,"a::ios::ate")
     	 logfile.write("#################################################\n")
     	 for k in range(0,len(params)):
     	     pf = params.at(k)
             if pf.getError() !=0:
                 print pf.GetName(), pf.getVal(), pf.getError(), "%.2f"%(pf.getVal()/pf.getError())
             else: 
                 print pf.GetName(), pf.getVal(), pf.getError()
     	     if not("nonRes" in pf.GetName()):
     		 continue
     	     pi = paramsinit.at(k)
     	     r  = pi.getMax()-1
             if r !=0 :
                 logfile.write(pf.GetName()+" & "+str((pf.getVal()-pi.getVal())/r)+"\\\\ \n")
             else:
                 logfile.write(pf.GetName()+" & "+str((pf.getVal()-pi.getVal()))+"\\\\ \n")
         logfile.close()

if __name__=="__main__":
     finMC = ROOT.TFile(options.input,"READ");
     hinMC = finMC.Get("nonRes");
     binwidth = hinMC.GetXaxis().GetBinWidth(3)
     print "binwidth ",binwidth

     print options.name
     purity = options.channel  
     
     print "open file " +options.name
     f = ROOT.TFile(options.name,"READ")
     workspace = f.Get("w")
     workspace.var("MH").setVal(options.signalMass)
     workspace.var("MH").setConstant(1)
     f.Close()
     #workspace.Print()
     model = workspace.pdf("model_b")
     model_b = workspace.pdf("model_b")
     if options.fitSignal: model = workspace.pdf("model_s")
     data_all = workspace.data("data_obs")
     args  = model_b.getComponents()
     if options.fitSignal and options.plotbonly==False:
         print "using s+b model"
         args  = model.getComponents()
     sig_args =  workspace.pdf("model_s").getComponents()
     data_all.Print()
     data = {}
     pdf1Name = {}
     all_expected = {}
     signal_expected= {}
     workspace.var("MJJ").setVal(2000)
     bkgs = ["nonRes","Wjets","Zjets","TTJetsTop","TTJetsW","TTJetsNonRes","TTJetsWNonResT","TTJetsResWResT" ,"TTJetsTNonResT","WZ","ZZ"]
     #print number of events before the fit
     data[period] = (workspace.data("data_obs").reduce("CMS_channel==CMS_channel::JJ_"+purity+"_13TeV_"+period))
     pdf1Name [period] =  "pdf_binJJ_"+purity+"_13TeV_"+period+"_bonly"
     if options.fitSignal and options.plotbonly==False: pdf1Name [period] =  "pdf_binJJ_"+purity+"_13TeV_"+period
     print "pdf1Name ",pdf1Name
     print
     print "Observed number of events in",purity,"category:"
     print data[period].sumEntries() ,"   ("+period+")"
     norms = {}
     norms["data"] = data[period].sumEntries()
     expected = {}
     for bkg in bkgs:
         if options.doVjets==False and (bkg=="Wjets" or bkg=="Zjets"): expected[bkg] = [None,None]; continue
         if options.addTop==False and (bkg.find("TTJets")!=-1): expected[bkg] = [None,None]; continue
         if options.addDIB==False and (bkg.find("WZ")!=-1): expected[bkg] = [None,None]; continue
         if options.addDIB==False and (bkg.find("ZZ")!=-1): expected[bkg] = [None,None]; continue
         expected[bkg] = [ (args[pdf1Name[period]].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+period+"_proc_"+bkg],0.]
         norms[bkg] = expected[bkg][0].getVal()
         print "Expected number of "+bkg+" events:",(expected[bkg][0].getVal()),"   ("+period+")"
     jsonfile = open(options.output+"/Expected_"+period+"_"+options.channel+".json","w")
     json.dump(norms,jsonfile)
     jsonfile.close()
     all_expected[period] = expected
     if options.fitSignal:
        print " pdf1Name[period] ",pdf1Name[period], " replacing ",pdf1Name[period].replace("_bonly","")
        print "Expected signal yields:",(sig_args[pdf1Name[period].replace("_bonly","")].getComponents())["n_exp_final_binJJ_"+purity+"_13TeV_"+period+"_proc_"+signalName].getVal(),"(",period,")"
        signal_expected[period] = [ (sig_args[pdf1Name[period].replace("_bonly","")].getComponents())["n_exp_final_binJJ_"+purity+"_13TeV_"+period+"_proc_"+signalName], 0.]
        fitted_r = workspace.var("r").getVal()
     else: signal_expected[period] = [0.,0.]
     print 
     
   
        
     ################################################# do the fit ###################################
     print
     
     if options.fit:
        if options.fitSignal == True and options.plotbonly == True:
            #if options.label.find("sigonly")==-1:
            print " ****************** doing b only fit **************"
            fitresult = model_b.fitTo(data_all,ROOT.RooFit.SumW2Error(not(options.data)),ROOT.RooFit.Minos(0),ROOT.RooFit.Verbose(0),ROOT.RooFit.Save(1),ROOT.RooFit.NumCPU(8))
        else:
            print " *********** doing s+b fit ***************"
            fitresult = model.fitTo(data_all,ROOT.RooFit.SumW2Error(not(options.data)),ROOT.RooFit.Minos(0),ROOT.RooFit.Verbose(0),ROOT.RooFit.Save(1),ROOT.RooFit.NumCPU(8))


        #else: fitresult_bkg_only = fitresult
        print " FIT RESULT ",fitresult.Print() 
        print 
        #writeLogfile(options,fitresult)
     ############################################################################################
     

     #################################################
     
     ########### lets add all the pdfs we need ################
     allpdfs = {}
     allsignalpdfs={}
     allpdfs[period] = []
     allsignalpdfs[period] = None
     for bkg in bkgs:
         if options.doVjets==False and (bkg=="Wjets" or bkg=="Zjets"): continue
         if options.addTop==False and (bkg.find("TTJets")!=-1): continue
         if options.addDIB==False and (bkg=="WZ" or bkg=="ZZ"): continue
         allpdfs[period].append(args["shapeBkg_"+bkg+"_JJ_"+purity+"_13TeV_"+period])
         print period, " shape ", bkg, " :"
         allpdfs[period][-1].Print()
         #allpdfs[period][-1].funcList().Print()
         #allpdfs[period][-1].coefList().Print()
     if options.fitSignal and options.plotbonly == False:
            allsignalpdfs[period] = args["shapeSig_"+signalName+"_JJ_"+purity+"_13TeV_"+period]
     elif options.fitSignal and options.plotbonly == True:
            allsignalpdfs[period] = sig_args["shapeSig_"+signalName+"_JJ_"+purity+"_13TeV_"+period]
     else: allsignalpdfs[period] =None
        
        
     print
     print period+" Prefit nonRes pdf:"
     pdf1_nonres_shape_prefit = args["nonResNominal_JJ_"+purity+"_13TeV_"+period]
     pdf1_nonres_shape_prefit.Print()
     print "Full "+period+" post-fit pdf:"     
     allpdfs[period].append( args[pdf1Name[period]+"_nuis"])
     allpdfs[period][-1].Print()
     
     allpdfsz = PostFitTools.definefinalPDFs(options,"z",allpdfs)
     allpdfsx = PostFitTools.definefinalPDFs(options,"x",allpdfs)
     allpdfsy = PostFitTools.definefinalPDFs(options,"y",allpdfs)

     if options.fit:
        bkgLabel = ["nonRes","Wjets","Zjets","resT","resW","nonresT","resWnonresT","resTresW","resTnonresT","WZ","ZZ"]
        mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}
        expected = {}
        norms = {}
        unc = {}
        slopes = {}
        norms["data"] = data[period].sumEntries()
        unc["data"]= ROOT.TMath.Sqrt(data[period].sumEntries())
        for bkg,bn in zip(bkgs,bkgLabel):
                if options.doVjets==False and (bkg=="Wjets" or bkg=="Zjets"): expected[bkg] = [0.,0.]; continue
                if options.addTop==False and (bkg.find("TTJets")!=-1): expected[bkg] = [0.,0.]; continue
                if options.addDIB==False and (bkg=="WZ" or bkg=="ZZ"): expected[bkg] = [0.,0.]; continue
                #(args[pdf1Name[period]].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+period+"_proc_"+bkg].dump()
                expected[bkg] = [ (args[pdf1Name[period]].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+period+"_proc_"+bkg],(args[pdf1Name[period]].getComponents())["n_exp_binJJ_"+purity+"_13TeV_"+period+"_proc_"+bkg].getPropagatedError(fitresult)]
                norms[bn] = expected[bkg][0].getVal()
                unc[bn]=expected[bkg][1]
                if bn in mappdf:
                    #print "+mappdf[bn] ",mappdf[bn]
                    params = fitresult.floatParsFinal()
                    paramsfinal = ROOT.RooArgSet(params)
                    for k in range(0,len(params)):
                        pf = params.at(k)
                        if not("CMS_VV_JJ_"+mappdf[bn]+"_slope" in pf.GetName()):
                            continue
                        else:
                            print pf.GetName(), pf.getVal(), pf.getError()
                            slopes[bn] =pf.getVal()
                            print "slopes[bn] ",slopes[bn]
                print "normalization of "+bkg+" after fit:",(expected[bkg][0].getVal()), " +/- ",expected[bkg][1] ,"   ("+period+")"
        all_expected[period] = expected
        #save post fit ttbar only normalization to be used as prefit value when fitting all bkg
        if options.name.find("ttbar")!=-1:
                jsonfile = open(options.jsonname+"_"+period+"_"+options.channel+".json","w")
                json.dump(norms,jsonfile)
                jsonfile.close()
                if options.slopes == True:
                    jsonfileslopes = open(options.jsonname+"Slopes_"+options.channel+".json","w")
                    json.dump(slopes,jsonfileslopes)
                    jsonfileslopes.close()
        jsonfile = open(options.output+"/Observed_"+period+"_"+options.channel+".json","w")
        json.dump(norms,jsonfile)
        jsonfile.close()
        jsonfile = open(options.output+"/Uncertainty_"+period+"_"+options.channel+".json","w")
        json.dump(unc,jsonfile)
        jsonfile.close()
        if options.fitSignal and options.plotbonly == False:
                signal_expected[period] = [ (args[pdf1Name[period]].getComponents())["n_exp_final_binJJ_"+purity+"_13TeV_"+period+"_proc_"+signalName], (args[pdf1Name[period]].getComponents())["n_exp_final_binJJ_"+purity+"_13TeV_"+period+"_proc_"+signalName].getPropagatedError(fitresult)]
                fitted_r = workspace.var("r").getVal()
                print "Fitted signal yields:",signal_expected[period][0].getVal()," +/- ", signal_expected[period][1] ,"(",period,")"
        print 
          	 	 	
         
     logfile = open(options.output+options.log,"a::ios::ate")
     forplotting = PostFitTools.Postfitplotter(parser,logfile,signalName)
     if options.fit:
          forproj = PostFitTools.Projection(hinMC,[options.xrange,options.yrange,options.zrange], workspace,options.fit,options.blind,options.plotbonly,fitresult)
          if options.both == True:
              forprojInv = PostFitTools.Projection(hinMC,[options.yrange,options.xrange,options.zrange], workspace,options.fit,options.blind,options.plotbonly,fitresult)
     else:
         forproj = PostFitTools.Projection(hinMC,[options.xrange,options.yrange,options.zrange], workspace,options.fit,options.blind)
         if options.both == True:
             forprojInv = PostFitTools.Projection(hinMC,[options.yrange,options.xrange,options.zrange], workspace,options.fit,options.blind)

     #make projections onto MJJ axis 
     if options.projection =="z" or options.projection =="xyz":
         results = []
         res = forproj.doProjection(data[period],allpdfsz[period],all_expected[period],"z",allsignalpdfs[period],signal_expected[period],showallTT,options.plotbonly)
         if options.both == True:
             resInv = forprojInv.doProjection(data[period],allpdfsz[period],all_expected[period],"z",allsignalpdfs[period],signal_expected[period],showallTT,options.plotbonly)
             for i in range(len(res[0])):
                 res[0][i].Sumw2()
                 resInv[0][i].Sumw2()
                 res[0][i].Add(resInv[0][i])
             res[1].Sumw2()
             resInv[1].Sumw2()
             res[1].Add(resInv[1])
             res[2].Sumw2()
             resInv[2].Sumw2()
             res[2].Add(resInv[2])
             if options.fit:
                 #adding error band. The middle point in added while the uncertainty is averaged
                 N =  res[7][0].GetN()
                 for i in range(N):
                     X = ROOT.Double()
                     Y = ROOT.Double()
                     res[7][0].GetPoint(i,X,Y)
                     XI = ROOT.Double()
                     YI = ROOT.Double()
                     resInv[7][0].GetPoint(i,XI,YI)
                     res[7][0].SetPoint(i,X,Y+YI)
                     Y = res[7][0].GetErrorYhigh(i)
                     X = res[7][0].GetErrorXhigh(i)
                     YI = resInv[7][0].GetErrorYhigh(i)
                     XI = resInv[7][0].GetErrorXhigh(i)
                     res[7][0].SetPointEYhigh(i,(Y+YI)/2.) #average
                     res[7][0].SetPointEXhigh(i,X)
                     Y = res[7][0].GetErrorYlow(i)
                     X = res[7][0].GetErrorXlow(i)
                     YI = resInv[7][0].GetErrorYlow(i)
                     XI = resInv[7][0].GetErrorXlow(i)
                     res[7][0].SetPointEYlow(i,(Y+YI)/2.) #average
                     res[7][0].SetPointEXlow(i,X)

         if options.fitSignal and options.plotbonly == False: workspace.var("r").setVal(fitted_r)
         forplotting.MakePlots(res[0],res[1],res[2],res[3],res[4],res[5], res[6],res[7],options.pseudo,options.both)
     #make projections onto MJ1 axis
     if options.projection =="x" or options.projection =="xyz":
         results = []
         res = forproj.doProjection(data[period],allpdfsx[period],all_expected[period],"x",allsignalpdfs[period],signal_expected[period],showallTT,options.plotbonly)
         if options.fitSignal and options.plotbonly == False: workspace.var("r").setVal(fitted_r)
         forplotting.MakePlots(res[0],res[1],res[2],res[3],res[4],res[5], res[6],res[7],options.pseudo,binwidth)
     #make projections onto MJ2 axis
     if options.projection =="y" or options.projection =="xyz":
         results = []
         res = forproj.doProjection(data[period],allpdfsy[period],all_expected[period],"y",allsignalpdfs[period],signal_expected[period],showallTT,options.plotbonly)
         if options.fitSignal and options.plotbonly == False: workspace.var("r").setVal(fitted_r)
         forplotting.MakePlots(res[0],res[1],res[2],res[3],res[4],res[5], res[6],res[7],options.pseudo,binwidth)


        
     logfile.close()
     #################################################   
     #calculate chi2  
     #norm=norm_nonres+norm_res
     #chi2 = getChi2fullModel(pdf_nonres_shape_postfit,data,norm)
     #print "Chi2/ndof: %.2f/%.2f"%(chi2[0],chi2[1])," = %.2f"%(chi2[0]/chi2[1])," prob = ",ROOT.TMath.Prob(chi2[0], int(chi2[1]))
   
