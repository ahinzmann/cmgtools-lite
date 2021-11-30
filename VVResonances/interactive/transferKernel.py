import ROOT
ROOT.gROOT.SetBatch(True)
import os, sys, re, optparse,pickle,shutil,json
import time
from array import array
ROOT.gErrorIgnoreLevel = ROOT.kWarning
ROOT.gROOT.ProcessLine(".x tdrstyle.cc");
import math, copy
import cuts
from tools.PostFitTools import *
from tools.DatacardTools import *
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker

parser = optparse.OptionParser()
parser.add_option("-o","--output",dest="output",help="Output folder name",default='postfit_qcd/')
parser.add_option("-i","--input",dest="input",help="Input nonRes histo with MC data",default='JJ_2016_nonRes_VV_HPLP.root')
parser.add_option("--pdfIn","--pdfIn",dest="pdfIn",help="3D nonRes pdf",default='JJ_2016_nonRes_3D_VV_HPLP.root')
parser.add_option("-x","--xrange",dest="xrange",help="set range for x bins in projection",default="0,-1")
parser.add_option("-y","--yrange",dest="yrange",help="set range for y bins in projection",default="0,-1")
parser.add_option("-z","--zrange",dest="zrange",help="set range for z bins in projection",default="0,-1")
parser.add_option("-p","--projection",dest="projection",help="choose which projection should be done",default="xyz")
parser.add_option("--merge",dest="merge",action="store_true",help="Merge all kernels",default=False)
parser.add_option("--sample",dest="sample",help="pythia, madgraph or herwig",default="pythia")
parser.add_option("--pdfz",dest="pdfz",help="name of pdfs lie PTZUp etc",default="")
parser.add_option("--pdfx",dest="pdfx",help="name of pdfs lie PTXUp etc",default="")
parser.add_option("--pdfy",dest="pdfy",help="name of pdfs lie PTYUp etc",default="")
parser.add_option("--year",dest="year",help="year",default="2017")
parser.add_option("--channel",dest="channel",default="VH_HPHP")
(options,args) = parser.parse_args()
ROOT.gStyle.SetOptStat(0)
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.FATAL)

def unequalScale(histo,name,alpha,power=1,dim=1):
    newHistoU =copy.deepcopy(histo) 
    newHistoU.SetName(name+"Up")
    newHistoD =copy.deepcopy(histo) 
    newHistoD.SetName(name+"Down")
    if dim == 2:
	    maxFactor = max(pow(histo.GetXaxis().GetXmax(),power),pow(histo.GetXaxis().GetXmin(),power))
	    for i in range(1,histo.GetNbinsX()+1):
	        x= histo.GetXaxis().GetBinCenter(i)
	        for j in range(1,histo.GetNbinsY()+1):
	            nominal=histo.GetBinContent(i,j)
	            factor = 1+alpha*pow(x,power) 
	            newHistoU.SetBinContent(i,j,nominal*factor)
	            newHistoD.SetBinContent(i,j,nominal/factor)
	    if newHistoU.Integral()>0.0:        
	        newHistoU.Scale(1.0/newHistoU.Integral())        
	    if newHistoD.Integral()>0.0:        
	        newHistoD.Scale(1.0/newHistoD.Integral())        
    else:
	    for i in range(1,histo.GetNbinsX()+1):
	        x= histo.GetXaxis().GetBinCenter(i)
	        nominal=histo.GetBinContent(i) #ROOT.TMath.Log10(histo.GetBinContent(i))
		factor = 1+alpha*pow(x,power)
	        newHistoU.SetBinContent(i,nominal*factor)
	        if factor != 0: newHistoD.SetBinContent(i,nominal/factor)	
    return newHistoU,newHistoD 
    
def mirror(histo,histoNominal,name,dim=1):
    newHisto =copy.deepcopy(histoNominal) 
    newHisto.SetName(name)
    intNominal=histoNominal.Integral()
    intUp = histo.Integral()
    if dim == 2:
		for i in range(1,histo.GetNbinsX()+1):
			for j in range(1,histo.GetNbinsY()+1):
				up=histo.GetBinContent(i,j)/intUp
				nominal=histoNominal.GetBinContent(i,j)/intNominal
				if up != 0: newHisto.SetBinContent(i,j,histoNominal.GetBinContent(i,j)*nominal/up)
    else:
		for i in range(1,histo.GetNbinsX()+1):
			up=histo.GetBinContent(i)/intUp
			nominal=histoNominal.GetBinContent(i)/intNominal
                        if up!=0: newHisto.SetBinContent(i,histoNominal.GetBinContent(i)*nominal/up)
                        else: newHisto.SetBinContent(i,histoNominal.GetBinContent(i)*nominal)
    return newHisto       

def expandHisto(histo,suffix,binsMVV,binsMJ,minMVV,maxMVV,minMJ,maxMJ):
    histogram=ROOT.TH2F(histo.GetName()+suffix,"histo",binsMJ,minMJ,maxMJ,binsMVV,minMVV,maxMVV)
    for i in range(1,histo.GetNbinsX()+1):
        proje = histo.ProjectionY("q",i,i)
        graph=ROOT.TGraph(proje)
        for j in range(1,histogram.GetNbinsY()+1):
            x=histogram.GetYaxis().GetBinCenter(j)
            bin=histogram.GetBin(i,j)
            histogram.SetBinContent(bin,graph.Eval(x,0,"S"))
    return histogram

def expandHistoBinned(histo,suffix ,binsx,binsy):
    histogram=ROOT.TH2F(histo.GetName()+suffix,"histo",len(binsx)-1,array('f',binsx),len(binsy)-1,array('f',binsy))
    for i in range(1,histo.GetNbinsX()+1):
        proje = histo.ProjectionY("q",i,i)
        graph=ROOT.TGraph(proje)
        for j in range(1,histogram.GetNbinsY()+1):
            x=histogram.GetYaxis().GetBinCenter(j)
            bin=histogram.GetBin(i,j)
            histogram.SetBinContent(bin,graph.Eval(x,0,"S"))
    return histogram
        
def conditional(hist):
    for i in range(1,hist.GetNbinsY()+1):
        proj=hist.ProjectionX("q",i,i)
        integral=proj.Integral()
        if integral==0.0:
            print 'SLICE WITH NO EVENTS!!!!!!!!',hist.GetName()
            continue
        for j in range(1,hist.GetNbinsX()+1):
            hist.SetBinContent(j,i,hist.GetBinContent(j,i)/integral)


def merge_all(dataset):
 fin_herwig_mjj = ROOT.TFile.Open('save_new_shapes_%s_herwig_%s_1D.root'%(dataset,purity),'READ')
 histo_altshapeUp_mjj = fin_herwig_mjj.histo_nominal
 histo_altshapeUp_mjj.SetName('histo_altshapeUp')
 histo_altshapeUp_mjj.SetTitle('histo_altshapeUp')

 fin_madgraph_mjj = ROOT.TFile.Open('save_new_shapes_%s_madgraph_%s_1D.root'%(dataset,purity),'READ')
 histo_altshape2Up_mjj = fin_madgraph_mjj.histo_nominal
 histo_altshape2Up_mjj.SetName('histo_altshape2Up')
 histo_altshape2Up_mjj.SetTitle('histo_altshape2Up')
 
 fin_pythia_mjj = ROOT.TFile.Open('save_new_shapes_%s_pythia_%s_1D.root'%(dataset,purity),'UPDATE')
 histo_nominal = fin_pythia_mjj.histo_nominal
 histo_altshapeUp_mjj.Write('histo_altshapeUp')
 histo_altshapeDown_mjj = mirror(histo_altshapeUp_mjj,histo_nominal,"histo_altshapeDown")
 histo_altshapeDown_mjj.SetName('histo_altshapeDown')
 histo_altshapeDown_mjj.SetTitle('histo_altshapeDown')
 histo_altshapeDown_mjj.Write('histo_altshapeDown') 
 
 histo_altshape2Up_mjj.Write('histo_altshape2Up')
 histo_altshape2Down_mjj = mirror(histo_altshape2Up_mjj,histo_nominal,"histo_altshape2Down")
 histo_altshape2Down_mjj.SetName('histo_altshape2Down')
 histo_altshape2Down_mjj.SetTitle('histo_altshape2Down')
 histo_altshape2Down_mjj.Write('histo_altshape2Down') 
 
 fin_pythia_mjj.Close()
 fin_madgraph_mjj.Close()
 fin_herwig_mjj.Close()
 
 fin_herwig_l1 = ROOT.TFile.Open('save_new_shapes_%s_herwig_%s_COND2D_l1.root'%(dataset,purity),'READ')
 histo_altshapeUp_l1 = fin_herwig_l1.histo_nominal
 histo_altshapeUp_l1.SetName('histo_altshapeUp')
 histo_altshapeUp_l1.SetTitle('histo_altshapeUp')
 
 fin_madgraph_l1 = ROOT.TFile.Open('save_new_shapes_%s_madgraph_%s_COND2D_l1.root'%(dataset,purity),'READ')
 histo_altshape2Up_l1 = fin_madgraph_l1.histo_nominal
 histo_altshape2Up_l1.SetName('histo_altshape2Up')
 histo_altshape2Up_l1.SetTitle('histo_altshape2Up')
 
 fin_pythia_l1 = ROOT.TFile.Open('save_new_shapes_%s_pythia_%s_COND2D_l1.root'%(dataset,purity),'UPDATE')
 histo_nominal = fin_pythia_l1.histo_nominal
 histo_altshapeUp_l1.Write('histo_altshapeUp')
 histo_altshapeDown_l1 = mirror(histo_altshapeUp_l1,histo_nominal,"histo_altshapeDown",2)
 conditional(histo_altshapeDown_l1)
 histo_altshapeDown_l1.SetName('histo_altshapeDown')
 histo_altshapeDown_l1.SetTitle('histo_altshapeDown')
 histo_altshapeDown_l1.Write('histo_altshapeDown') 
 
 histo_altshape2Up_l1.Write('histo_altshape2Up')
 histo_altshape2Down_l1 = mirror(histo_altshape2Up_l1,histo_nominal,"histo_altshape2Down",2)
 conditional(histo_altshape2Down_l1)
 histo_altshape2Down_l1.SetName('histo_altshape2Down')
 histo_altshape2Down_l1.SetTitle('histo_altshape2Down')
 histo_altshape2Down_l1.Write('histo_altshape2Down') 
 
 fin_pythia_l1.Close()
 fin_madgraph_l1.Close()
 fin_herwig_l1.Close()
 
 fin_herwig_l2 = ROOT.TFile.Open('save_new_shapes_%s_herwig_%s_COND2D_l2.root'%(dataset,purity),'READ')
 histo_altshapeUp_l2 = fin_herwig_l2.histo_nominal
 histo_altshapeUp_l2.SetName('histo_altshapeUp')
 histo_altshapeUp_l2.SetTitle('histo_altshapeUp')
 
 fin_madgraph_l2 = ROOT.TFile.Open('save_new_shapes_%s_madgraph_%s_COND2D_l2.root'%(dataset,purity),'READ')
 histo_altshape2Up_l2 = fin_madgraph_l2.histo_nominal
 histo_altshape2Up_l2.SetName('histo_altshape2Up')
 histo_altshape2Up_l2.SetTitle('histo_altshape2Up')
 
 fin_pythia_l2 = ROOT.TFile.Open('save_new_shapes_%s_pythia_%s_COND2D_l2.root'%(dataset,purity),'UPDATE')
 histo_nominal = fin_pythia_l2.histo_nominal
 histo_altshapeUp_l2.Write('histo_altshapeUp')
 histo_altshapeDown_l2 = mirror(histo_altshapeUp_l2,histo_nominal,"histo_altshapeDown",2)
 conditional(histo_altshapeDown_l2)
 histo_altshapeDown_l2.SetName('histo_altshapeDown')
 histo_altshapeDown_l2.SetTitle('histo_altshapeDown')
 histo_altshapeDown_l2.Write('histo_altshapeDown') 
 
 histo_altshape2Up_l2.Write('histo_altshape2Up')
 histo_altshape2Down_l2 = mirror(histo_altshape2Up_l2,histo_nominal,"histo_altshape2Down",2)
 conditional(histo_altshape2Down_l2)
 histo_altshape2Down_l2.SetName('histo_altshape2Down')
 histo_altshape2Down_l2.SetTitle('histo_altshape2Down')
 histo_altshape2Down_l2.Write('histo_altshape2Down') 
 
 fin_pythia_l2.Close()
 fin_madgraph_l2.Close()
 fin_herwig_l2.Close()
 
 inputx=fin_pythia_l1.GetName()
 inputy=fin_pythia_l2.GetName()
 inputz=fin_pythia_mjj.GetName()     
 rootFile="save_new_shapes_%s_pythia_"%dataset+purity+"_3D.root"
   
 print "Reading " ,inputx
 print "Reading " ,inputy
 print "Reading " ,inputz
 print "Saving to ",rootFile 
   
 cmd='vvMergeHistosToPDF3D.py -i "{inputx}" -I "{inputy}" -z "{inputz}" -o "{rootFile}"'.format(rootFile=rootFile,inputx=inputx,inputy=inputy,inputz=inputz)
 print "going to execute "+str(cmd)
 os.system(cmd)
             
def save_shape(final_shape,norm_nonres,pTools,sample="pythia"):

    histo = ROOT.TH3F('histo','histo',len(pTools.xBinslowedge)-1,pTools.xBinslowedge,len(pTools.yBinslowedge)-1,pTools.yBinslowedge,len(pTools.zBinslowedge)-1,pTools.zBinslowedge)
    histo_xz = ROOT.TH2F('histo_xz','histo_xz',len(pTools.xBinslowedge)-1,pTools.xBinslowedge,len(pTools.zBinslowedge)-1,pTools.zBinslowedge)
    histo_yz = ROOT.TH2F('histo_yz','histo_yz',len(pTools.yBinslowedge)-1,pTools.yBinslowedge,len(pTools.zBinslowedge)-1,pTools.zBinslowedge)
    histo_z = ROOT.TH1F('histo_z','histo_z',len(pTools.zBinslowedge)-1,pTools.zBinslowedge)
    print "Done creating out histos"

    lv = {}
    for xk, xv in pTools.xBins_redux.iteritems():
        lv[xv] = {}
        for yk, yv in pTools.yBins_redux.iteritems():
          lv[xv][yv] = {}
          for zk,zv in pTools.zBins_redux.iteritems():
            lv[xv][yv][zv] = 0
  
    lv_xz = {}
    lv_yz = {}
    for xk, xv in pTools.xBins_redux.iteritems():
        lv_xz[xv] = {}
        lv_yz[xv] = {}
        for zk,zv in pTools.zBins_redux.iteritems():
          lv_xz[xv][zv] = 0
          lv_yz[xv][zv] = 0

    lv_z = []
    for zk,zv in pTools.zBins_redux.iteritems():
      lv_z.append(0)
                               
    for xk, xv in pTools.xBins_redux.iteritems():
         MJ1.setVal(xv)
         for yk, yv in pTools.yBins_redux.iteritems():
             MJ2.setVal(yv)
             for zk,zv in pTools.zBins_redux.iteritems():
                 MJJ.setVal(zv)
                 binV = pTools.zBinsWidth[zk]*pTools.xBinsWidth[xk]*pTools.yBinsWidth[yk]
                 lv[xv][yv][zv] = final_shape.getVal(argset)*binV
                 lv_xz[xv][zv] += final_shape.getVal(argset)*binV
                 lv_yz[yv][zv] += final_shape.getVal(argset)*binV
                 lv_z[zk-1] += final_shape.getVal(argset)*binV

    for xk, xv in pTools.xBins_redux.iteritems():
     for yk, yv in pTools.yBins_redux.iteritems():
      for zk, zv in pTools.zBins_redux.iteritems():
       histo.Fill(xv,yv,zv,lv[xv][yv][zv]*norm_nonres[0])

    for xk, xv in pTools.xBins_redux.iteritems():
      for zk, zv in pTools.zBins_redux.iteritems():
       histo_xz.Fill(xv,zv,lv_xz[xv][zv]*norm_nonres[0])
       histo_yz.Fill(xv,zv,lv_yz[xv][zv]*norm_nonres[0])
    
    for zk,zv in pTools.zBins_redux.iteritems(): histo_z.Fill(zv,lv_z[zk-1]*norm_nonres[0])    
       
    fout_z = ROOT.TFile.Open('save_new_shapes_%s_%s_%s_1D.root'%(dataset,sample,purity),'RECREATE')
    fout_z.cd()
    histo_z.Scale(1./histo_z.Integral())
    histo_z.SetTitle('histo_nominal')
    histo_z.SetName('histo_nominal')
    histo_z.Write('histo_nominal')

    print "Now PT 1D",pTools.zBinslowedge[-1],pTools.zBinslowedge[0],pTools.xBinslowedge[-1],pTools.xBinslowedge[0]
    alpha=1.5/float(pTools.zBinslowedge[-1])    
    histogram_pt_up,histogram_pt_down=unequalScale(histo_z,"histo_nominal_PT",alpha,1)
    histogram_pt_down.SetName('histo_nominal_PTDown')
    histogram_pt_down.SetTitle('histo_nominal_PTDown')
    histogram_pt_down.Write('histo_nominal_PTDown')
    histogram_pt_up.SetName('histo_nominal_PTUp')
    histogram_pt_up.SetTitle('histo_nominal_PTUp')
    histogram_pt_up.Write('histo_nominal_PTUp')

    print "Now OPT 1D"
    alpha=1.5*float(pTools.zBinslowedge[0])
    histogram_opt_up,histogram_opt_down=unequalScale(histo_z,"histo_nominal_OPT",alpha,-1)
    histogram_opt_down.SetName('histo_nominal_OPTDown')
    histogram_opt_down.SetTitle('histo_nominal_OPTDown')
    histogram_opt_down.Write('histo_nominal_OPTDown')
    histogram_opt_up.SetName('histo_nominal_OPTUp')
    histogram_opt_up.SetTitle('histo_nominal_OPTUp')
    histogram_opt_up.Write('histo_nominal_OPTUp')

    print "Now pT2"
    alpha=15./(5000.*5000.)
    histogram_pt2_up,histogram_pt2_down=unequalScale(histo_z,"histo_nominal_PT2",alpha,2)
    histogram_pt2_down.SetName('histo_nominal_PT2Down')
    histogram_pt2_down.SetTitle('histo_nominal_PT2Down')
    histogram_pt2_down.Write('histo_nominal_PT2Down')
    histogram_pt2_up.SetName('histo_nominal_PT2Up')
    histogram_pt2_up.SetTitle('histo_nominal_PT2Up')
    histogram_pt2_up.Write('histo_nominal_PT2Up')
    print "Now opT2"
    alpha=15.*1000.*1000.
    histogram_opt2_up,histogram_opt2_down=unequalScale(histo_z,"histo_nominal_OPT2",alpha,-2)
    histogram_opt2_up.SetName('histo_nominal_OPT2Up')
    histogram_opt2_up.SetTitle('histo_nominal_OPT2Up')
    histogram_opt2_up.Write('histo_nominal_OPT2Up')
    histogram_opt2_down.SetName('histo_nominal_OPT2Down')
    histogram_opt2_down.SetTitle('histo_nominal_OPT2Down')
    histogram_opt2_down.Write('histo_nominal_OPT2Down')
    #alpha=5000.*5000.*5000.
    alpha=150./(7000.*7000.*7000.)
    histogram_pt3_down,histogram_pt3_up=unequalScale(histo_z,"histo_nominal_PT3",alpha,3)
    histogram_pt3_down.SetName('histo_nominal_PT3Down')
    histogram_pt3_down.SetTitle('histo_nominal_PT3Down')
    histogram_pt3_down.Write('histo_nominal_PT3Down')
    histogram_pt3_up.SetName('histo_nominal_PT3Up')
    histogram_pt3_up.SetTitle('histo_nominal_PT3Up')
    histogram_pt3_up.Write('histo_nominal_PT3Up')
    alpha=150.*1000.*1000.*1000.
    histogram_opt3_down,histogram_opt3_up=unequalScale(histo_z,"histo_nominal_OPT3",alpha,-3)
    histogram_opt3_up.SetName('histo_nominal_OPT3Up')
    histogram_opt3_up.SetTitle('histo_nominal_OPT3Up')
    histogram_opt3_up.Write('histo_nominal_OPT3Up')
    histogram_opt3_down.SetName('histo_nominal_OPT3Down')
    histogram_opt3_down.SetTitle('histo_nominal_OPT3Down')
    histogram_opt3_down.Write('histo_nominal_OPT3Down')

    #alpha=5000.*5000.*5000.
    alpha=1500./(7000.*7000.*7000.*7000.)
    histogram_pt4_down,histogram_pt4_up=unequalScale(histo_z,"histo_nominal_PT4",alpha,4)
    histogram_pt4_down.SetName('histo_nominal_PT4Down')
    histogram_pt4_down.SetTitle('histo_nominal_PT4Down')
    histogram_pt4_down.Write('histo_nominal_PT4Down')
    histogram_pt4_up.SetName('histo_nominal_PT4Up')
    histogram_pt4_up.SetTitle('histo_nominal_PT4Up')
    histogram_pt4_up.Write('histo_nominal_PT4Up')
    alpha=1500.*1000.*1000.*1000.*1000.
    histogram_opt4_down,histogram_opt4_up=unequalScale(histo_z,"histo_nominal_OPT4",alpha,-4)
    histogram_opt4_up.SetName('histo_nominal_OPT4Up')
    histogram_opt4_up.SetTitle('histo_nominal_OPT4Up')
    histogram_opt4_up.Write('histo_nominal_OPT4Up')
    histogram_opt4_down.SetName('histo_nominal_OPT4Down')
    histogram_opt4_down.SetTitle('histo_nominal_OPT4Down')
    histogram_opt4_down.Write('histo_nominal_OPT4Down')
    #alpha=5000.*5000.*5000.
    alpha=15000./(7000.*7000.*7000.*7000.*7000.)
    histogram_pt5_down,histogram_pt5_up=unequalScale(histo_z,"histo_nominal_PT5",alpha,5)
    histogram_pt5_down.SetName('histo_nominal_PT5Down')
    histogram_pt5_down.SetTitle('histo_nominal_PT5Down')
    histogram_pt5_down.Write('histo_nominal_PT5Down')
    histogram_pt5_up.SetName('histo_nominal_PT5Up')
    histogram_pt5_up.SetTitle('histo_nominal_PT5Up')
    histogram_pt5_up.Write('histo_nominal_PT5Up')
    alpha=15000.*1000.*1000.*1000.*1000.*1000.
    histogram_opt5_down,histogram_opt5_up=unequalScale(histo_z,"histo_nominal_OPT5",alpha,-5)
    histogram_opt5_up.SetName('histo_nominal_OPT5Up')
    histogram_opt5_up.SetTitle('histo_nominal_OPT5Up')
    histogram_opt5_up.Write('histo_nominal_OPT5Up')
    histogram_opt5_down.SetName('histo_nominal_OPT5Down')
    histogram_opt5_down.SetTitle('histo_nominal_OPT5Down')
    histogram_opt5_down.Write('histo_nominal_OPT5Down')
    #alpha=5000.*5000.*5000.
    alpha=150000./(7000.*7000.*7000.*7000.*7000.*7000)
    histogram_pt6_down,histogram_pt6_up=unequalScale(histo_z,"histo_nominal_PT6",alpha,6)
    histogram_pt6_down.SetName('histo_nominal_PT6Down')
    histogram_pt6_down.SetTitle('histo_nominal_PT6Down')
    histogram_pt6_down.Write('histo_nominal_PT6Down')
    histogram_pt6_up.SetName('histo_nominal_PT6Up')
    histogram_pt6_up.SetTitle('histo_nominal_PT6Up')
    histogram_pt6_up.Write('histo_nominal_PT6Up')
    alpha=150000.*1000.*1000.*1000.*1000.*1000.*1000
    histogram_opt6_down,histogram_opt6_up=unequalScale(histo_z,"histo_nominal_OPT6",alpha,-6)
    histogram_opt6_up.SetName('histo_nominal_OPT6Up')
    histogram_opt6_up.SetTitle('histo_nominal_OPT6Up')
    histogram_opt6_up.Write('histo_nominal_OPT6Up')
    histogram_opt6_down.SetName('histo_nominal_OPT6Down')
    histogram_opt6_down.SetTitle('histo_nominal_OPT6Down')
    histogram_opt6_down.Write('histo_nominal_OPT6Down')
    #alpha=5000.*5000.*5000.
    alpha=0.
    histogram_ptn_down,histogram_ptn_up=unequalScale(histo_z,"histo_nominal_PTN",alpha,0)
    histogram_ptn_down.SetName('histo_nominal_PTNDown')
    histogram_ptn_down.SetTitle('histo_nominal_PTNDown')
    histogram_ptn_down.Write('histo_nominal_PTNDown')
    histogram_ptn_up.SetName('histo_nominal_PTNUp')
    histogram_ptn_up.SetTitle('histo_nominal_PTNUp')
    histogram_ptn_up.Write('histo_nominal_PTNUp')

    fout_z.Close()
    
    fout_xz = ROOT.TFile.Open('save_new_shapes_%s_%s_%s_COND2D_l1.root'%(dataset,sample,purity),'RECREATE')
    fout_xz.cd()  
    conditional(histo_xz)
    histo_xz.SetTitle('histo_nominal')
    histo_xz.SetName('histo_nominal')
    histo_xz.Write('histo_nominal')

    print "Now PT 2D l1"
    alpha=1.5/float(pTools.xBinslowedge[-1])
    histogram_pt_up,histogram_pt_down=unequalScale(histo_xz,"histo_nominal_PT",alpha,1,2)
    conditional(histogram_pt_down)
    histogram_pt_down.SetName('histo_nominal_PTDown')
    histogram_pt_down.SetTitle('histo_nominal_PTDown')
    histogram_pt_down.Write('histo_nominal_PTDown')
    conditional(histogram_pt_up)
    histogram_pt_up.SetName('histo_nominal_PTUp')
    histogram_pt_up.SetTitle('histo_nominal_PTUp')
    histogram_pt_up.Write('histo_nominal_PTUp')

    print "Now OPT 2D l1"
    alpha=1.5*float(pTools.xBinslowedge[0])
    h1,h2=unequalScale(histo_xz,"histo_nominal_OPT",alpha,-1,2)
    conditional(h1)
    h1.SetName('histo_nominal_OPTUp')
    h1.SetTitle('histo_nominal_OPTUp')
    h1.Write('histo_nominal_OPTUp')
    conditional(h2)
    h2.SetName('histo_nominal_OPTDown')
    h2.SetTitle('histo_nominal_OPTDown')
    h2.Write('histo_nominal_OPTDown')
        
    print "Now pT2"
    alpha=15./(5000.*5000.)
    histogram_pt2_up,histogram_pt2_down=unequalScale(histo_xz,"histo_nominal_PT2",alpha,2,2)
    histogram_pt2_down.SetName('histo_nominal_PT2Down')
    histogram_pt2_down.SetTitle('histo_nominal_PT2Down')
    histogram_pt2_down.Write('histo_nominal_PT2Down')
    histogram_pt2_up.SetName('histo_nominal_PT2Up')
    histogram_pt2_up.SetTitle('histo_nominal_PT2Up')
    histogram_pt2_up.Write('histo_nominal_PT2Up')
    print "Now opT2"
    alpha=15.*1000.*1000.
    histogram_opt2_up,histogram_opt2_down=unequalScale(histo_xz,"histo_nominal_OPT2",alpha,-2,2)
    histogram_opt2_up.SetName('histo_nominal_OPT2Up')
    histogram_opt2_up.SetTitle('histo_nominal_OPT2Up')
    histogram_opt2_up.Write('histo_nominal_OPT2Up')
    histogram_opt2_down.SetName('histo_nominal_OPT2Down')
    histogram_opt2_down.SetTitle('histo_nominal_OPT2Down')
    histogram_opt2_down.Write('histo_nominal_OPT2Down')
    #alpha=5000.*5000.*5000.
    alpha=150./(7000.*7000.*7000.)
    histogram_pt3_down,histogram_pt3_up=unequalScale(histo_xz,"histo_nominal_PT3",alpha,3,2)
    histogram_pt3_down.SetName('histo_nominal_PT3Down')
    histogram_pt3_down.SetTitle('histo_nominal_PT3Down')
    histogram_pt3_down.Write('histo_nominal_PT3Down')
    histogram_pt3_up.SetName('histo_nominal_PT3Up')
    histogram_pt3_up.SetTitle('histo_nominal_PT3Up')
    histogram_pt3_up.Write('histo_nominal_PT3Up')
    alpha=150.*1000.*1000.*1000.
    histogram_opt3_down,histogram_opt3_up=unequalScale(histo_xz,"histo_nominal_OPT3",alpha,-3,2)
    histogram_opt3_up.SetName('histo_nominal_OPT3Up')
    histogram_opt3_up.SetTitle('histo_nominal_OPT3Up')
    histogram_opt3_up.Write('histo_nominal_OPT3Up')
    histogram_opt3_down.SetName('histo_nominal_OPT3Down')
    histogram_opt3_down.SetTitle('histo_nominal_OPT3Down')
    histogram_opt3_down.Write('histo_nominal_OPT3Down')

    #alpha=5000.*5000.*5000.
    alpha=1500./(7000.*7000.*7000.*7000.)
    histogram_pt4_down,histogram_pt4_up=unequalScale(histo_xz,"histo_nominal_PT4",alpha,4,2)
    histogram_pt4_down.SetName('histo_nominal_PT4Down')
    histogram_pt4_down.SetTitle('histo_nominal_PT4Down')
    histogram_pt4_down.Write('histo_nominal_PT4Down')
    histogram_pt4_up.SetName('histo_nominal_PT4Up')
    histogram_pt4_up.SetTitle('histo_nominal_PT4Up')
    histogram_pt4_up.Write('histo_nominal_PT4Up')
    alpha=1500.*1000.*1000.*1000.*1000.
    histogram_opt4_down,histogram_opt4_up=unequalScale(histo_xz,"histo_nominal_OPT4",alpha,-4,2)
    histogram_opt4_up.SetName('histo_nominal_OPT4Up')
    histogram_opt4_up.SetTitle('histo_nominal_OPT4Up')
    histogram_opt4_up.Write('histo_nominal_OPT4Up')
    histogram_opt4_down.SetName('histo_nominal_OPT4Down')
    histogram_opt4_down.SetTitle('histo_nominal_OPT4Down')
    histogram_opt4_down.Write('histo_nominal_OPT4Down')
    #alpha=5000.*5000.*5000.
    alpha=15000./(7000.*7000.*7000.*7000.*7000.)
    histogram_pt5_down,histogram_pt5_up=unequalScale(histo_xz,"histo_nominal_PT5",alpha,5,2)
    histogram_pt5_down.SetName('histo_nominal_PT5Down')
    histogram_pt5_down.SetTitle('histo_nominal_PT5Down')
    histogram_pt5_down.Write('histo_nominal_PT5Down')
    histogram_pt5_up.SetName('histo_nominal_PT5Up')
    histogram_pt5_up.SetTitle('histo_nominal_PT5Up')
    histogram_pt5_up.Write('histo_nominal_PT5Up')
    alpha=15000.*1000.*1000.*1000.*1000.*1000.
    histogram_opt5_down,histogram_opt5_up=unequalScale(histo_xz,"histo_nominal_OPT5",alpha,-5,2)
    histogram_opt5_up.SetName('histo_nominal_OPT5Up')
    histogram_opt5_up.SetTitle('histo_nominal_OPT5Up')
    histogram_opt5_up.Write('histo_nominal_OPT5Up')
    histogram_opt5_down.SetName('histo_nominal_OPT5Down')
    histogram_opt5_down.SetTitle('histo_nominal_OPT5Down')
    histogram_opt5_down.Write('histo_nominal_OPT5Down')
    #alpha=5000.*5000.*5000.
    alpha=150000./(7000.*7000.*7000.*7000.*7000.*7000)
    histogram_pt6_down,histogram_pt6_up=unequalScale(histo_xz,"histo_nominal_PT6",alpha,6,2)
    histogram_pt6_down.SetName('histo_nominal_PT6Down')
    histogram_pt6_down.SetTitle('histo_nominal_PT6Down')
    histogram_pt6_down.Write('histo_nominal_PT6Down')
    histogram_pt6_up.SetName('histo_nominal_PT6Up')
    histogram_pt6_up.SetTitle('histo_nominal_PT6Up')
    histogram_pt6_up.Write('histo_nominal_PT6Up')
    alpha=150000.*1000.*1000.*1000.*1000.*1000.*1000
    histogram_opt6_down,histogram_opt6_up=unequalScale(histo_xz,"histo_nominal_OPT6",alpha,-6,2)
    histogram_opt6_up.SetName('histo_nominal_OPT6Up')
    histogram_opt6_up.SetTitle('histo_nominal_OPT6Up')
    histogram_opt6_up.Write('histo_nominal_OPT6Up')
    histogram_opt6_down.SetName('histo_nominal_OPT6Down')
    histogram_opt6_down.SetTitle('histo_nominal_OPT6Down')
    histogram_opt6_down.Write('histo_nominal_OPT6Down')
    #alpha=5000.*5000.*5000.
    alpha=0.
    histogram_ptn_down,histogram_ptn_up=unequalScale(histo_xz,"histo_nominal_PTN",alpha,0,2)
    histogram_ptn_down.SetName('histo_nominal_PTNDown')
    histogram_ptn_down.SetTitle('histo_nominal_PTNDown')
    histogram_ptn_down.Write('histo_nominal_PTNDown')
    histogram_ptn_up.SetName('histo_nominal_PTNUp')
    histogram_ptn_up.SetTitle('histo_nominal_PTNUp')
    histogram_ptn_up.Write('histo_nominal_PTNUp')


    fout_xz.Close()
    
    fout_yz = ROOT.TFile.Open('save_new_shapes_%s_%s_%s_COND2D_l2.root'%(dataset,sample,purity),'RECREATE')
    fout_yz.cd()  
    conditional(histo_yz)
    histo_yz.SetTitle('histo_nominal')
    histo_yz.SetName('histo_nominal')
    histo_yz.Write('histo_nominal')

    print "Now PT 2D l2"
    alpha=1.5/float(pTools.xBinslowedge[-1])
    histogram_pt_up,histogram_pt_down=unequalScale(histo_yz,"histo_nominal_PT",alpha,1,2)
    conditional(histogram_pt_down)
    histogram_pt_down.SetName('histo_nominal_PTDown')
    histogram_pt_down.SetTitle('histo_nominal_PTDown')
    histogram_pt_down.Write('histo_nominal_PTDown')
    conditional(histogram_pt_up)
    histogram_pt_up.SetName('histo_nominal_PTUp')
    histogram_pt_up.SetTitle('histo_nominal_PTUp')
    histogram_pt_up.Write('histo_nominal_PTUp')

    print "Now OPT 2D l2"
    alpha=1.5*float(pTools.xBinslowedge[0])
    h1,h2=unequalScale(histo_yz,"histo_nominal_OPT",alpha,-1,2)
    conditional(h1)
    h1.SetName('histo_nominal_OPTUp')
    h1.SetTitle('histo_nominal_OPTUp')
    h1.Write('histo_nominal_OPTUp')
    conditional(h2)
    h2.SetName('histo_nominal_OPTDown')
    h2.SetTitle('histo_nominal_OPTDown')
    h2.Write('histo_nominal_OPTDown')

    print "Now pT2"
    alpha=15./(5000.*5000.)
    histogram_pt2_up,histogram_pt2_down=unequalScale(histo_yz,"histo_nominal_PT2",alpha,2,2)
    histogram_pt2_down.SetName('histo_nominal_PT2Down')
    histogram_pt2_down.SetTitle('histo_nominal_PT2Down')
    histogram_pt2_down.Write('histo_nominal_PT2Down')
    histogram_pt2_up.SetName('histo_nominal_PT2Up')
    histogram_pt2_up.SetTitle('histo_nominal_PT2Up')
    histogram_pt2_up.Write('histo_nominal_PT2Up')
    print "Now opT2"
    alpha=15.*1000.*1000.
    histogram_opt2_up,histogram_opt2_down=unequalScale(histo_yz,"histo_nominal_OPT2",alpha,-2,2)
    histogram_opt2_up.SetName('histo_nominal_OPT2Up')
    histogram_opt2_up.SetTitle('histo_nominal_OPT2Up')
    histogram_opt2_up.Write('histo_nominal_OPT2Up')
    histogram_opt2_down.SetName('histo_nominal_OPT2Down')
    histogram_opt2_down.SetTitle('histo_nominal_OPT2Down')
    histogram_opt2_down.Write('histo_nominal_OPT2Down')
    #alpha=5000.*5000.*5000.
    alpha=150./(7000.*7000.*7000.)
    histogram_pt3_down,histogram_pt3_up=unequalScale(histo_yz,"histo_nominal_PT3",alpha,3,2)
    histogram_pt3_down.SetName('histo_nominal_PT3Down')
    histogram_pt3_down.SetTitle('histo_nominal_PT3Down')
    histogram_pt3_down.Write('histo_nominal_PT3Down')
    histogram_pt3_up.SetName('histo_nominal_PT3Up')
    histogram_pt3_up.SetTitle('histo_nominal_PT3Up')
    histogram_pt3_up.Write('histo_nominal_PT3Up')
    alpha=150.*1000.*1000.*1000.
    histogram_opt3_down,histogram_opt3_up=unequalScale(histo_yz,"histo_nominal_OPT3",alpha,-3,2)
    histogram_opt3_up.SetName('histo_nominal_OPT3Up')
    histogram_opt3_up.SetTitle('histo_nominal_OPT3Up')
    histogram_opt3_up.Write('histo_nominal_OPT3Up')
    histogram_opt3_down.SetName('histo_nominal_OPT3Down')
    histogram_opt3_down.SetTitle('histo_nominal_OPT3Down')
    histogram_opt3_down.Write('histo_nominal_OPT3Down')

    #alpha=5000.*5000.*5000.
    alpha=1500./(7000.*7000.*7000.*7000.)
    histogram_pt4_down,histogram_pt4_up=unequalScale(histo_yz,"histo_nominal_PT4",alpha,4,2)
    histogram_pt4_down.SetName('histo_nominal_PT4Down')
    histogram_pt4_down.SetTitle('histo_nominal_PT4Down')
    histogram_pt4_down.Write('histo_nominal_PT4Down')
    histogram_pt4_up.SetName('histo_nominal_PT4Up')
    histogram_pt4_up.SetTitle('histo_nominal_PT4Up')
    histogram_pt4_up.Write('histo_nominal_PT4Up')
    alpha=1500.*1000.*1000.*1000.*1000.
    histogram_opt4_down,histogram_opt4_up=unequalScale(histo_yz,"histo_nominal_OPT4",alpha,-4,2)
    histogram_opt4_up.SetName('histo_nominal_OPT4Up')
    histogram_opt4_up.SetTitle('histo_nominal_OPT4Up')
    histogram_opt4_up.Write('histo_nominal_OPT4Up')
    histogram_opt4_down.SetName('histo_nominal_OPT4Down')
    histogram_opt4_down.SetTitle('histo_nominal_OPT4Down')
    histogram_opt4_down.Write('histo_nominal_OPT4Down')
    #alpha=5000.*5000.*5000.
    alpha=15000./(7000.*7000.*7000.*7000.*7000.)
    histogram_pt5_down,histogram_pt5_up=unequalScale(histo_yz,"histo_nominal_PT5",alpha,5,2)
    histogram_pt5_down.SetName('histo_nominal_PT5Down')
    histogram_pt5_down.SetTitle('histo_nominal_PT5Down')
    histogram_pt5_down.Write('histo_nominal_PT5Down')
    histogram_pt5_up.SetName('histo_nominal_PT5Up')
    histogram_pt5_up.SetTitle('histo_nominal_PT5Up')
    histogram_pt5_up.Write('histo_nominal_PT5Up')
    alpha=15000.*1000.*1000.*1000.*1000.*1000.
    histogram_opt5_down,histogram_opt5_up=unequalScale(histo_yz,"histo_nominal_OPT5",alpha,-5,2)
    histogram_opt5_up.SetName('histo_nominal_OPT5Up')
    histogram_opt5_up.SetTitle('histo_nominal_OPT5Up')
    histogram_opt5_up.Write('histo_nominal_OPT5Up')
    histogram_opt5_down.SetName('histo_nominal_OPT5Down')
    histogram_opt5_down.SetTitle('histo_nominal_OPT5Down')
    histogram_opt5_down.Write('histo_nominal_OPT5Down')
    #alpha=5000.*5000.*5000.
    alpha=150000./(7000.*7000.*7000.*7000.*7000.*7000)
    histogram_pt6_down,histogram_pt6_up=unequalScale(histo_yz,"histo_nominal_PT6",alpha,6,2)
    histogram_pt6_down.SetName('histo_nominal_PT6Down')
    histogram_pt6_down.SetTitle('histo_nominal_PT6Down')
    histogram_pt6_down.Write('histo_nominal_PT6Down')
    histogram_pt6_up.SetName('histo_nominal_PT6Up')
    histogram_pt6_up.SetTitle('histo_nominal_PT6Up')
    histogram_pt6_up.Write('histo_nominal_PT6Up')
    alpha=150000.*1000.*1000.*1000.*1000.*1000.*1000
    histogram_opt6_down,histogram_opt6_up=unequalScale(histo_yz,"histo_nominal_OPT6",alpha,-6,2)
    histogram_opt6_up.SetName('histo_nominal_OPT6Up')
    histogram_opt6_up.SetTitle('histo_nominal_OPT6Up')
    histogram_opt6_up.Write('histo_nominal_OPT6Up')
    histogram_opt6_down.SetName('histo_nominal_OPT6Down')
    histogram_opt6_down.SetTitle('histo_nominal_OPT6Down')
    histogram_opt6_down.Write('histo_nominal_OPT6Down')
    #alpha=5000.*5000.*5000.
    alpha=0.
    histogram_ptn_down,histogram_ptn_up=unequalScale(histo_yz,"histo_nominal_PTN",alpha,0,2)
    histogram_ptn_down.SetName('histo_nominal_PTNDown')
    histogram_ptn_down.SetTitle('histo_nominal_PTNDown')
    histogram_ptn_down.Write('histo_nominal_PTNDown')
    histogram_ptn_up.SetName('histo_nominal_PTNUp')
    histogram_ptn_up.SetTitle('histo_nominal_PTNUp')
    histogram_ptn_up.Write('histo_nominal_PTNUp')

    
    fout_yz.Close()    

    if sample != 'pythia':
     inputx=fout_xz.GetName()
     inputy=fout_yz.GetName()
     inputz=fout_z.GetName()     
     rootFile="save_new_shapes_%s_%s_"%(dataset,sample)+purity+"_3D.root"
   
     print "Reading " ,inputx
     print "Reading " ,inputy
     print "Reading " ,inputz
     print "Saving to ",rootFile 
   
     cmd='vvMergeHistosToPDF3D.py -i "{inputx}" -I "{inputy}" -z "{inputz}" -o "{rootFile}"'.format(rootFile=rootFile,inputx=inputx,inputy=inputy,inputz=inputz)
     print "going to execute "+str(cmd)
     os.system(cmd)

def makeNonResCard():
 print " ############ options.pdfIn", options.pdfIn
 if options.pdfIn.find("VV_HPHP")!=-1: category_pdf = "VV_HPHP"
 elif options.pdfIn.find("VV_HPLP")!=-1: category_pdf = "VV_HPLP"
 elif options.pdfIn.find("VH_HPHP")!=-1: category_pdf = "VH_HPHP" 
 elif options.pdfIn.find("VH_HPLP")!=-1: category_pdf = "VH_HPLP"
 elif options.pdfIn.find("VH_LPHP")!=-1: category_pdf = "VH_LPHP"
 elif options.pdfIn.find("VH_LPLP")!=-1: category_pdf = "VH_LPLP"
 elif options.pdfIn.find("NP")!=-1: category_pdf = "NP"
 else: category_pdf = "VV_LPLP"  

 dataset = options.year
 sig = 'BulkGWW' 
 doCorrelation = False

 dataset = str(options.year)
 ctx = cuts.cuts("init_VV_VH.json",dataset,"dijetbins_random")
 if options.year.find(",")!=-1:
     dataset ="Run2"
     if options.year.find("2018")==-1:
         dataset ="1617"
 print dataset

 lumi = ctx.lumi
 print "lumi ",lumi
 lumi_unc = ctx.lumi_unc
 print "lumi unc",lumi_unc 
 vtag_pt_dependence = ctx.tagger_pt_dependence
 print " vtag_pt_dependence ",vtag_pt_dependence
 PU_unc = ctx.PU_uncertainties
 PDF_unc = ctx.PDF_uncertainties
 JES_unc = ctx.JES_uncertainties
 JER_unc = ctx.JER_uncertainties
 scales = [ctx.W_HPmassscale,ctx.W_LPmassscale]
 scalesHiggs = [ctx.H_HPmassscale,ctx.H_LPmassscale]


 DTools = DatacardTools(scales,scalesHiggs,vtag_pt_dependence,PU_unc,JES_unc,JER_unc,lumi_unc,PDF_unc,1.0,"","",doCorrelation)
 print '##########      PURITY      :', purity 

 cat='_'.join(['JJ',sig,purity,'13TeV_'+dataset])
 card=DataCardMaker('',purity,'13TeV_'+dataset,lumi[dataset],'JJ',cat)
 cardName='datacard_'+cat+'.txt'
 workspaceName='workspace_'+cat+'.root'
      
# DTools.AddSignal(card,dataset,purity,sig,'results_2016',0)
 print "Adding Signal"
 DTools.AddOneSignal(card,dataset,purity,sig,'results_%s'%dataset,0)
 print "Signal Added !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
 hname = 'histo'
 if options.sample!='pythia': hname+=('_'+options.sample)
 print " hname 1 ",hname 
 fin = ROOT.TFile.Open(options.pdfIn)
 if not fin.Get(hname):
  print "WARNING: histogram",hname,"NOT FOUND in file",options.pdfIn,". This is probably expected. Use instead histogram histo"
  hname = 'histo'
 fin.Close() 
 print " hname 2",hname
 print "adding shapes bkg"
 #card.addHistoShapeFromFile("nonRes",["MJ1","MJ2","MJJ"],options.pdfIn,hname,['OPTXY:CMS_VV_JJ_nonRes_OPTXY_'+category_pdf,'OPTZ:CMS_VV_JJ_nonRes_OPTZ_'+category_pdf,'TurnOn:CMS_VV_JJ_nonRes_TurnOn_'+category_pdf],False,0)
 #card.addHistoShapeFromFile("nonRes",["MJ1","MJ2","MJJ"],options.pdfIn,hname,['OPTXY:CMS_VV_JJ_nonRes_OPTXY_'+category_pdf,'OPTZ:CMS_VV_JJ_nonRes_OPTZ_'+category_pdf],False,0)
 card.addHistoShapeFromFile("nonRes",["MJ1","MJ2","MJJ"],options.pdfIn,hname,['PTZ:CMS_VV_JJ_nonRes_PTZ_'+category_pdf,'OPTXY:CMS_VV_JJ_nonRes_OPTXY_'+category_pdf,'OPTZ:CMS_VV_JJ_nonRes_OPTZ_'+category_pdf,'TurnOn:CMS_VV_JJ_nonRes_TurnOn_'+category_pdf],False,0)
 print "adding yield"
 card.addFixedYieldFromFile("nonRes",1,options.input,"nonRes",1)
 print "adding data"
 DTools.AddData(card,options.input,"nonRes",lumi[dataset] )
 print "adding sig sys for purity", purity
 DTools.AddOneSigSystematics(card,sig,dataset,purity,0,"0","results_"+dataset)

 print "Adding systematics to card"
 print "norm"
 card.addSystematic("CMS_VV_JJ_nonRes_norm","lnN",{'nonRes':1.5}) 
 print "OPTZ"
 card.addSystematic("CMS_VV_JJ_nonRes_OPTZ_"+category_pdf,"param",[0.,2.]) #[0.,2.])
 print "OPTXY"
 card.addSystematic("CMS_VV_JJ_nonRes_OPTXY_"+category_pdf,"param",[0.,2.]) #0,2
 print "TurnOn"
 card.addSystematic("CMS_VV_JJ_nonRes_TurnOn_"+category_pdf,"param",[1.,2.]) #test for VH_HPHP
 print "PTZ"
 card.addSystematic("CMS_VV_JJ_nonRes_PTZ_"+category_pdf,"param",[0.0,2.]) #orig
  
 

 print " and now make card"     
 card.makeCard()

 t2wcmd = "text2workspace.py %s -o %s"%(cardName,workspaceName)
 print t2wcmd
 os.system(t2wcmd)
 print " workspaceName ", workspaceName
 return workspaceName
        
if __name__=="__main__":
     
     #if os.path.exists(options.output):
      #answer = raw_input('The output folder '+options.output+'already exsists. Do you want to remove it first? (YES or NO) ')
     # answer = 'YES'
     # if answer=='YES': 
     #  os.system('rm -rf %s'%options.output) 
     #  os.mkdir(options.output)     

     #################################################
     if options.year.find(",")!=-1:
         dataset ="Run2"
         if options.year.find("2018")==-1:
             dataset ="1617"
     else: dataset =options.year
     print dataset

     finMC = ROOT.TFile(options.input,"READ");
     hinMC = finMC.Get("nonRes");
     purity = ''
     if options.input.find("VV_HPHP")!=-1: purity = "VV_HPHP"
     elif options.input.find("VH_HPHP")!=-1: purity = "VH_HPHP"
     elif options.input.find("VV_HPLP")!=-1: purity = "VV_HPLP"
     elif options.input.find("VH_HPLP")!=-1: purity = "VH_HPLP"
     elif options.input.find("VH_LPHP")!=-1: purity = "VH_LPHP"
     elif options.input.find("LPLP")!=-1: purity = "LPLP"
     if options.input.find('VBF')!=-1: purity = 'VBF_'+purity  
     if purity == '' and 'control_region' in options.input:
         if 'VH_NPHP' in options.input:
             purity = 'VH_NPHP_control_region'
         if 'VV_NPHP' in options.input:
             purity = 'VV_NPHP_control_region'
         else:
             purity = 'VH_HPNP_control_region'
     if purity == '':
      print "SPECIFIED PURITY IS NOT ALLOWED!",options.input,purity
      sys.exit()  
     print "Using purity: " ,purity    
     if options.merge:
      merge_all(dataset)
      sys.exit()       

     print " ########################       makeNonResCard      ###"
     w_name = makeNonResCard()
     print " ########################   DONE    makeNonResCard      ###"
     print 
     print "open file " +w_name
     f = ROOT.TFile(w_name,"READ")
     workspace = f.Get("w")
     f.Close()
     workspace.Print()

     MJ1= workspace.var("MJ1");
     MJ2= workspace.var("MJ2");
     MJJ= workspace.var("MJJ");
     data = workspace.data("data_obs")
    
     argset = ROOT.RooArgSet();
     argset.add(MJJ);
     argset.add(MJ2);
     argset.add(MJ1);

     data = workspace.data("data_obs")
     data.Print()  
     print
     print "Observed number of events:",data.sumEntries()
          
     #################################################
     print " ########################       PostFitTools      ###"   
     Tools = Projection(hinMC,[options.xrange,options.yrange,options.zrange],workspace,False) #Postfitplotter(optparser,logfile,signalName)#(hinMC,argset,options.xrange,options.yrange,options.zrange,purity+'_'+options.sample,options.output,data)
     
     print "x bins:"
     print Tools.xBins_redux
     print "x bins low edge:"
     print Tools.xBinslowedge
     print "x bins width:"
     print Tools.xBinsWidth
     
     print
     print "y bins:"
     print Tools.yBins_redux
     print "y bins low edge:"
     print Tools.yBinslowedge
     print "y bins width:"
     print Tools.yBinsWidth
     
     print 
     print "z bins:"
     print Tools.zBins_redux
     print "z bins low edge:"
     print Tools.zBinslowedge
     print "z bins width:"
     print Tools.zBinsWidth
                  
     #################################################                
     model = workspace.pdf("model_b") 
                  
     args  = model.getComponents()
     print "model ",model.Print()
     print "args = model components ",args.Print()
     pdfName = "pdf_binJJ_"+purity+"_13TeV_%s_bonly"%dataset
     print "pdfName ",pdfName 
     print "Expected number of QCD events:",(args[pdfName].getComponents())["n_exp_binJJ_"+purity+"_13TeV_%s_proc_nonRes"%dataset].getVal()
    
     #################################################
     print "###########        Fitting:            ################"
     fitresult = model.fitTo(data,ROOT.RooFit.SumW2Error(1),ROOT.RooFit.Minos(0),ROOT.RooFit.Verbose(0),ROOT.RooFit.Save(1),ROOT.RooFit.NumCPU(8))#,ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
     print "#####   Fitting results ###########" 
     fitresult.Print()
     print "###########        Fitting DONE            ################"
     print "model ",model.Print()

     #################################################
     print            
            
     print 
     print "Prefit nonRes pdf:"
     pdf_nonres_shape_prefit = args["nonResNominal_JJ_"+purity+"_13TeV_%s"%dataset]
     pdf_nonres_shape_prefit.Print()
     print
     print "Postfit nonRes pdf:"
     pdf_nonres_shape_postfit  = args["shapeBkg_nonRes_JJ_"+purity+"_13TeV_%s"%dataset]
     pdf_nonres_shape_postfit.Print()
     pdf_nonres_shape_postfit.funcList().Print()
     pdf_nonres_shape_postfit.coefList().Print()
     print
     
     allpdfsz = [] #let's have always pre-fit and post-fit as firt elements here, and add the optional shapes if you want with options.pdf
     allpdfsz.append(pdf_nonres_shape_prefit)
     allpdfsz.append(pdf_nonres_shape_postfit)
     for p in options.pdfz.split(","):
         if p == '': continue
         print "add pdf:",p
         args[p].Print()
         allpdfsz.append(args[p])

     allpdfsx = [] #let's have always pre-fit and post-fit as firt elements here, and add the optional shapes if you want with options.pdf
     allpdfsx.append(pdf_nonres_shape_prefit)
     allpdfsx.append(pdf_nonres_shape_postfit)
     for p in options.pdfx.split(","):
         if p == '': continue
         print "add pdf:",p
         args[p].Print()
         allpdfsx.append(args[p])

     allpdfsy = [] #let's have always pre-fit and post-fit as firt elements here, and add the optional shapes if you want with options.pdf
     allpdfsy.append(pdf_nonres_shape_prefit)
     allpdfsy.append(pdf_nonres_shape_postfit)
     for p in options.pdfy.split(","):
         if p == '': continue
         print "add pdf:",p
         args[p].Print()
         allpdfsy.append(args[p])
      
     print
    
     norm = (args["pdf_binJJ_"+purity+"_13TeV_%s_bonly"%dataset].getComponents())["n_exp_binJJ_"+purity+"_13TeV_%s_proc_nonRes"%dataset].getVal()
     print "norm after fit "+str(norm)
          
     #################################################
     (args[pdfName].getComponents())["n_exp_binJJ_"+purity+"_13TeV_%s_proc_nonRes"%dataset].dump()
     norm_nonres = [0,0]
     norm_nonres[0] = (args["pdf_binJJ_"+purity+"_13TeV_%s_bonly"%dataset].getComponents())["n_exp_binJJ_"+purity+"_13TeV_%s_proc_nonRes"%dataset].getVal()
     norm_nonres[1] = (args["pdf_binJJ_"+purity+"_13TeV_%s_bonly"%dataset].getComponents())["n_exp_binJJ_"+purity+"_13TeV_%s_proc_nonRes"%dataset].getPropagatedError(fitresult)
     print "QCD normalization after fit",norm_nonres[0],"+/-",norm_nonres[1]
     #################################################     
     save_shape(pdf_nonres_shape_postfit,norm_nonres,Tools,options.sample)
     nevents = {"nonRes": [(args["pdf_binJJ_"+purity+"_13TeV_%s_bonly"%dataset].getComponents())["n_exp_binJJ_"+purity+"_13TeV_%s_proc_nonRes"%dataset], (args["pdf_binJJ_"+purity+"_13TeV_%s_bonly"%dataset].getComponents())["n_exp_binJJ_"+purity+"_13TeV_%s_proc_nonRes"%dataset].getPropagatedError(fitresult)]}

     forplotting = Postfitplotter(parser,"","BulkGWW",options.sample+"_"+purity)
     #make projections onto MJJ axis 
     
         
     #make projections onto MJJ axis
     if options.projection =="z": 
         results = Tools.doProjection(data,[pdf_nonres_shape_postfit],nevents,"z",None,[0,0])
         forplotting.MakePlots(results[0],results[1],results[2],results[3],results[4],results[5], results[6],results[7])
         
     #make projections onto MJ1 axis
     if options.projection =="x":  
         results = Tools.doProjection(data,[pdf_nonres_shape_postfit],nevents,"x",None,[0,0])
         forplotting.MakePlots(results[0],results[1],results[2],results[3],results[4],results[5], results[6],results[7])
                  
     #make projections onto MJ2 axis
     if options.projection =="y":  
         results = Tools.doProjection(data,[pdf_nonres_shape_postfit],nevents,"y",None,[0,0])
         forplotting.MakePlots(results[0],results[1],results[2],results[3],results[4],results[5], results[6],results[7])
         
     if options.projection =="xyz":
         results = Tools.doProjection(data,[pdf_nonres_shape_postfit],nevents,"x",None,[0,0])
         forplotting.MakePlots(results[0],results[1],results[2],results[3],results[4],results[5], results[6],results[7])
         results = Tools.doProjection(data,[pdf_nonres_shape_postfit],nevents,"y",None,[0,0])
         forplotting.MakePlots(results[0],results[1],results[2],results[3],results[4],results[5], results[6],results[7])
         results = Tools.doProjection(data,[pdf_nonres_shape_postfit],nevents,"z",None,[0,0])
         forplotting.MakePlots(results[0],results[1],results[2],results[3],results[4],results[5], results[6],results[7])
     
