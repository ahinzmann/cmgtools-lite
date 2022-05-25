#!/usr/bin/env python
import sys, os
import json
import ROOT
import math
  
class DatacardTools():

 def __init__(self,scales,scalesHiggs,tagger_pt_dependence,PU_unc,JES_unc,JER_unc,lumi_unc,PDF_unc,sfQCD,pseudodata,outlabel,doCorrelation=True,fitvjetsmjj=False,doKfactors=False,sfWjets=1,sfZjets=1,dib=False):
  
  self.scales=scales
  self.tagger_pt_dependence=tagger_pt_dependence
  self.PU_unc = PU_unc
  self.JES_unc = JES_unc
  self.JER_unc = JER_unc
  self.lumi_unc = lumi_unc
  self.PDF_unc = PDF_unc
  self.sfQCD = sfQCD
  self.sfWjets = sfWjets
  self.sfZjets = sfZjets
  self.pseudodata = pseudodata
  self.outlabel = outlabel
  self.scalesHiggs=scalesHiggs
  self.doCorrelation= doCorrelation
  self.fitvjetsmjj = fitvjetsmjj
  self.kfactors = doKfactors
  self.dib = dib

 def AddOneSignal(self,card,dataset,category,sig,resultsDir,ncontrib):

       print "sig ",sig

       if 'ZprimeWW' in sig:

        card.addMVVSignalParametricShape("%s_MVV"%sig,"MJJ",resultsDir+"/JJ_%s_%s_MVV.json"%(sig,dataset),{'CMS_jes_scale_j':1},{'CMS_jer_res_j':1.0})
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq1"%sig,"MJ1" ,resultsDir+"/JJ_%s_%s_MJrandom_"%(sig,dataset)+"NP.json",{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq2"%sig,"MJ2" ,resultsDir+"/JJ_%s_%s_MJrandom_"%(sig,dataset)+"NP.json",{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        card.product3D("%s"%sig,"%s_Wqq1"%sig,"%s_Wqq2"%sig,"%s_MVV"%sig)
        if 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTC.json","Zprime_cH1","BRWW",10000.,'CMS_pdf',self.PDF_unc["VBF_ZprimeToWW_narrow"]["VV_HPHP"],1.)
        else: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTB.json","CX0(pb)","BRWW",1000.,'CMS_pdf',self.PDF_unc["ZprimeToWW_narrow"]["VV_HPHP"],1.)
	
       elif 'WprimeWZ' in sig:

        card.addMVVSignalParametricShape("%s_MVV"%sig,"MJJ",resultsDir+"/JJ_%s_%s_MVV.json"%(sig,dataset),{'CMS_jes_scale_j':1},{'CMS_jer_res_j':1.0},self.doCorrelation)
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq1_c1"%sig,"MJ1" ,resultsDir+"/JJ_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq2_c1"%sig,"MJ2" ,resultsDir+"/JJ_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        if self.doCorrelation:
            print "doing correlation"
            card.product("%s_Wqq_c1"%sig,"%s_Wqq1_c1"%sig,"%s_Wqq2_c1"%sig)
            card.conditionalProduct("%s_c1"%sig,"%s_MVV"%sig,"MJ1,MJ2","%s_Wqq_c1"%sig)
        else:
            print "no MVV correlation"
            card.product3D("%s_c1"%sig,"%s_Wqq1_c1"%sig,"%s_Wqq2_c1"%sig,"%s_MVV"%sig)

        card.addMJJSignalParametricShapeNOEXP("%s_Wqq1_c2"%sig,"MJ1" ,resultsDir+"/JJ_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq2_c2"%sig,"MJ2" ,resultsDir+"/JJ_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        if self.doCorrelation:
            print "doing correlation"
            card.product("%s_Wqq_c2"%sig,"%s_Wqq1_c2"%sig,"%s_Wqq2_c2"%sig)
            card.conditionalProduct("%s_c2"%sig,"%s_MVV"%sig,"MJ1,MJ2","%s_Wqq_c2"%sig)
        else:
            card.product3D("%s_c2"%sig,"%s_Wqq1_c2"%sig,"%s_Wqq2_c2"%sig,"%s_MVV"%sig)

        card.sumSimple("%s"%sig,"%s_c1"%sig,"%s_c2"%sig,"0.5")
       
        if not "sigOnly" in self.outlabel:
         if 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTC.json","Wprime_cH1","BRWZ",10000.,'CMS_pdf',self.PDF_unc["VBF_WprimeToWZ_narrow"]["VV_HPHP"],1.)
         else: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTB.json","CX+(pb),CX-(pb)","BRWZ",1000.,'CMS_pdf',self.PDF_unc["WprimeToWZToWhadZhad_narrow"]["VV_HPHP"],1.)
        else:
         if 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTC.json","Wprime_cH1","BRWZ",10000.,'CMS_pdf',self.PDF_unc["VBF_WprimeToWZ_narrow"]["VV_HPHP"],1.)
         else: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTB.json","CX+(pb),CX-(pb)","BRWZ",1000.,'CMS_pdf',self.PDF_unc["WprimeToWZToWhadZhad_narrow"]["VV_HPHP"],1.)
                
       elif 'BulkG' in sig or 'Radion' in sig:
       
        card.addMVVSignalParametricShape("%s_MVV"%sig,"MJJ",resultsDir+"/JJ_%s_%s_MVV.json"%(sig,dataset),{'CMS_jes_scale_j':1},{'CMS_jer_res_j':1.0})
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq1"%sig,"MJ1" ,resultsDir+"/JJ_%s_%s_MJrandom_"%(sig,dataset)+"NP.json",{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq2"%sig,"MJ2" ,resultsDir+"/JJ_%s_%s_MJrandom_"%(sig,dataset)+"NP.json",{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        card.product3D("%s"%sig,"%s_Wqq1"%sig,"%s_Wqq2"%sig,"%s_MVV"%sig)

        if sig=='BulkGWW':
         card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/BulkG.json","sigma","BRWW",10000.,'CMS_pdf',self.PDF_unc["BulkGravToWW_narrow"]["VV_HPHP"],1.)
        elif sig=='BulkGZZ': card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/BulkG.json","sigma","BRZZ",10000.,'CMS_pdf',self.PDF_unc["BulkGravToZZToZhadZhad_narrow"]["VH_HPHP"],1.)
        elif sig=='RadionWW': card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/Radion.json","sigma","BRWW",10000.,'CMS_pdf',self.PDF_unc["RadionToWW_narrow"]["VV_HPHP"],1.)
        elif sig=='RadionZZ': card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/Radion.json","sigma","BRZZ",10000.,'CMS_pdf',self.PDF_unc["RadionToZZ_narrow"]["VH_HPHP"],1.)
        elif sig=='VBF_BulkGWW': card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/VBF_BulkG.json","sigma","BRWW",10000.,'CMS_pdf',self.PDF_unc["VBF_BulkGravToWW_narrow"]["VV_HPHP"],1.)
        elif sig=='VBF_BulkGZZ': card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/VBF_BulkG.json","sigma","BRZZ",10000.,'CMS_pdf',self.PDF_unc["VBF_BulkGravToZZ_narrow"]["VH_HPHP"],1.)
        elif sig=='VBF_RadionWW': card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/VBF_Radion.json","sigma","BRWW",10000.,'CMS_pdf',self.PDF_unc["VBF_RadionToWW_narrow"]["VV_HPHP"],1.)
        elif sig=='VBF_RadionZZ': card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/VBF_Radion.json","sigma","BRZZ",10000.,'CMS_pdf',self.PDF_unc["VBF_RadionToZZ_narrow"]["VH_HPHP"],1.)
       
       elif 'H' in sig:
     
        card.addMVVSignalParametricShape("%s_MVV"%sig,"MJJ",resultsDir+"/JJ_%s_%s_MVV.json"%(sig,dataset),{'CMS_jes_scale_j':1},{'CMS_jer_res_j':1.0},self.doCorrelation)

        card.addMJJSignalParametricShapeHiggs("%s_Wqq1_c1"%sig,"MJ1" ,resultsDir+"/JJ_Hjet_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_jes_scale_j':1},{'CMS_jer_res_j':1.0},self.scalesHiggs)
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq2_c1"%sig,"MJ2" ,resultsDir+"/JJ_Vjet_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        if self.doCorrelation:
         print "doing correlation"
         card.product("%s_Wqq_c1"%sig,"%s_Wqq1_c1"%sig,"%s_Wqq2_c1"%sig)
         card.conditionalProduct("%s_c1"%sig,"%s_MVV"%sig,"MJ1,MJ2","%s_Wqq_c1"%sig)
        else:
         print "no MVV correlation"
         card.product3D("%s_c1"%sig,"%s_Wqq1_c1"%sig,"%s_Wqq2_c1"%sig,"%s_MVV"%sig)

        card.addMJJSignalParametricShapeHiggs("%s_Wqq2_c2"%sig,"MJ2" ,resultsDir+"/JJ_Hjet_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_jes_scale_j':1},{'CMS_jer_res_j':1.0},self.scalesHiggs)
        card.addMJJSignalParametricShapeNOEXP("%s_Wqq1_c2"%sig,"MJ1" ,resultsDir+"/JJ_Vjet_%s_%s_MJrandom_%s.json"%(sig,dataset,"NP"),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
        if self.doCorrelation:
         print "doing correlation"
         card.product("%s_Wqq_c2"%sig,"%s_Wqq1_c2"%sig,"%s_Wqq2_c2"%sig)
         card.conditionalProduct("%s_c2"%sig,"%s_MVV"%sig,"MJ1,MJ2","%s_Wqq_c2"%sig)
        else:
         card.product3D("%s_c2"%sig,"%s_Wqq1_c2"%sig,"%s_Wqq2_c2"%sig,"%s_MVV"%sig)
       
        card.sumSimple("%s"%sig,"%s_c1"%sig,"%s_c2"%sig,"0.5")

        if not "sigOnly" in self.outlabel:
           if 'Zprime' in sig and 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTC.json","Zprime_cH1","BRZh",10000.,'CMS_pdf',self.PDF_unc["VBF_ZprimeToZhToZhadhinc_narrow"]["VH_HPHP"],1.)
           elif 'Wprime' in sig and 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTC.json","Wprime_cH1","BRWh",10000.,'CMS_pdf',self.PDF_unc["VBF_WprimeToWhToWhadhinc_narrow"]["VH_HPHP"],1.)
           elif 'Zprime' in sig and not 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTB.json","CX0(pb)","BRZh",1000.,"CMS_pdf",self.PDF_unc["ZprimeToZhToZhadhinc_narrow"]["VH_HPHP"],1.)
           elif 'Wprime' in sig and not 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTB.json","CX+(pb),CX-(pb)","BRWh",1000.,'CMS_pdf',self.PDF_unc["WprimeToWhToWhadhinc_narrow"]["VH_HPHP"],1.)
        else:
           if 'Zprime' in sig and 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTC.json","Zprime_cH1","BRZh",1000.,'CMS_pdf',self.PDF_unc["VBF_ZprimeToZhToZhadhinc_narrow"]["VH_HPHP"],1.)
           elif 'Wprime' in sig and 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTC.json","Wprime_cH1","BRWh",1000.,'CMS_pdf',self.PDF_unc["VBF_WprimeToWhToWhadhinc_narrow"]["VH_HPHP"],1.)
           elif 'Zprime' in sig and not 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTB.json","CX0(pb)","BRZh",1000.,'CMS_pdf',self.PDF_unc["ZprimeToZhToZhadhinc_narrow"]["VH_HPHP"],1.)
           elif 'Wprime' in sig and not 'VBF' in sig: card.addParametricYieldHVTBR("%s"%sig,ncontrib,resultsDir+"/JJ_%s_%s_"%(sig,dataset)+category+"_yield.json","../scripts/theoryXsec/HVTB.json","CX+(pb),CX-(pb)","BRWh",1000.,'CMS_pdf',self.PDF_unc["WprimeToWhToWhadhinc_narrow"]["VH_HPHP"],1.)


 def AddMultipleSignals(self,card,dataset,category,sig,resultsDir,ncontrib):
 
  isvbf = ''
  if 'VBF' in sig: isvbf='VBF_'
  
  if 'VprimeWV' in sig:
   self.AddOneSignal(card,dataset,category,'%sWprimeWZ'%isvbf,resultsDir,ncontrib)
   self.AddOneSignal(card,dataset,category,'%sZprimeWW'%isvbf,resultsDir,ncontrib-1)
  elif 'VprimeVHinc' in sig:
   self.AddOneSignal(card,dataset,category,'%sWprimeWHinc'%isvbf,resultsDir,ncontrib)
   self.AddOneSignal(card,dataset,category,'%sZprimeZHinc'%isvbf,resultsDir,ncontrib-1)
  elif sig == 'Wprime' or sig == 'VBF_Wprime':
   self.AddOneSignal(card,dataset,category,'%sWprimeWZ'%isvbf,resultsDir,ncontrib)
   self.AddOneSignal(card,dataset,category,'%sWprimeWHinc'%isvbf,resultsDir,ncontrib-1)
  elif sig == 'Zprime' or sig == 'VBF_Zprime':
   self.AddOneSignal(card,dataset,category,'%sZprimeWW'%isvbf,resultsDir,ncontrib)
   self.AddOneSignal(card,dataset,category,'%sZprimeZHinc'%isvbf,resultsDir,ncontrib-1)
  elif sig == 'Vprime' or sig == 'VBF_Vprime':
   self.AddOneSignal(card,dataset,category,'%sWprimeWZ'%isvbf,resultsDir,ncontrib)
   self.AddOneSignal(card,dataset,category,'%sZprimeWW'%isvbf,resultsDir,ncontrib-1)
   self.AddOneSignal(card,dataset,category,'%sWprimeWHinc'%isvbf,resultsDir,ncontrib-2)
   self.AddOneSignal(card,dataset,category,'%sZprimeZHinc'%isvbf,resultsDir,ncontrib-3)
  elif 'BulkGVV' in sig:
   self.AddOneSignal(card,dataset,category,'%sBulkGWW'%isvbf,resultsDir,ncontrib)
   self.AddOneSignal(card,dataset,category,'%sBulkGZZ'%isvbf,resultsDir,ncontrib-1)
  elif 'RadionVV' in sig:
   self.AddOneSignal(card,dataset,category,'%sRadionWW'%isvbf,resultsDir,ncontrib)
   self.AddOneSignal(card,dataset,category,'%sRadionZZ'%isvbf,resultsDir,ncontrib-1)
          
 #default implementation not working
 def AddTTBackground(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib):
       print "add TT+jets background"  

       card.addMJJTTJetsParametricShape("TTJets_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.addMJJTTJetsParametricShape("TTJets_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.addHistoShapeFromFile("TTJets_mjj",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_TTJets_PTZ_'+category,'OPT:CMS_VV_JJ_TTJets_OPTZ_'+category],False,0)       
       card.conditionalProduct3('TTJets','TTJets_mjj','TTJets_mjetRes_l1','TTJets_mjetRes_l2','MJJ',tag1="",tag2="",tag3="")
       
       print "outlabel "+self.outlabel
       if self.pseudodata=="" or self.pseudodata=="Vjets":
           card.addFixedYieldFromFile('TTJets',ncontrib,rootFileNorm,"TTJets")
       elif self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1:
           print "add small yield"
           card.addFixedYieldFromFile('TTJets',ncontrib,rootFileNorm,"TTJets",0.000001)
       else:
           card.addFixedYieldFromFile('TTJets',ncontrib,rootFileNorm,"TTJets")
           
 #new implementation: split in 3 contributions W+W, T+T, nonRes+nonRes
 def AddTTBackground2(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib):
       print "add TT+jets background"  
 
       #load mJJ - assume same for the three contributions (preliminary)
       card.addHistoShapeFromFile("TTJets_mjj",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_TTJets_PTZ_'+category,'OPT:CMS_VV_JJ_TTJets_OPTZ_'+category],False,0)       

       # W+W PDF
       card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.conditionalProduct3('TTJetsW','TTJets_mjj','TTJetsW_mjetRes_l1','TTJetsW_mjetRes_l2','MJJ',tag1="",tag2="",tag3="")

       #T+T PDF
       card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.conditionalProduct3('TTJetsTop','TTJets_mjj','TTJetsTop_mjetRes_l1','TTJetsTop_mjetRes_l2','MJJ',tag1="",tag2="",tag3="")

       #nonRes+nonRes PDF
       card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
       card.conditionalProduct3('TTJetsNonRes','TTJets_mjj','TTJetsNonRes_mjetRes_l1','TTJetsNonRes_mjetRes_l2','MJJ',tag1="",tag2="",tag3="")
       
       print "outlabel "+self.outlabel
       if self.pseudodata=="" or self.pseudodata=="Vjets":
           card.addFixedYieldFromFile('TTJets',ncontrib,rootFileNorm,"TTJets")
       elif self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1:
           print "add small yield"
           card.addFixedYieldFromFile('TTJets',ncontrib,rootFileNorm,"TTJets",0.000001)
       else:
           card.addFixedYieldFromFile('TTJetsW',ncontrib,rootFileNorm,"TTJets")
           card.addFixedYieldFromFile('TTJetsTop',ncontrib+1,rootFileNorm,"TTJets")
           card.addFixedYieldFromFile('TTJetsNonRes',ncontrib+2,rootFileNorm,"TTJets")
           
           
           
 
 #new implementation: split in 6 contributions W+W, T+T, nonRes+nonRes, nonRes+T, nonres+W, resT+resW with mjj fit
 def AddTTBackground3(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib,uncertainty,normjson):
    print "add TT+jets background"  
    contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
    mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}
    #uncjsonfile=open(resultsDir+"/JJ_"+dataset+"_TTJets_MjjUnc_"+category+".json")
    uncjsonfile=open(resultsDir+"/JJ_"+dataset+"_TTJets_MjjUnc_NP.json")
    unc = json.load(uncjsonfile)
    allunc = []
    for i in range(0,len(contrib)):
     allunc.append(unc[contrib[i]])
    print " allunc ",allunc
    maxunc = max(allunc)
    print " max unc is ",maxunc

    for i in range(0,len(contrib)):
     if self.pseudodata.find("ttbar")!=-1:

       #load mJJ - assume same for the three contributions (preliminary)
       #jsonfile = resultsDir+"/JJ_"+contrib[i]+dataset+"_TTJets_MVV_"+category+".json"
       jsonfile = resultsDir+"/JJ_"+dataset+"_TTJets"+contrib[i]+"_MVV_NP.json"
       print "load parametrisation for MVV ttbar contributions ",jsonfile,contrib[i]
       #card.addMVVMinorBkgParametricShape("TTJets"+contrib[i]+"_mjj",["MJJ"],jsonfile,[uncertainty[0].replace("TTJets",mappdf[contrib[i]])+"_"+category,unc[contrib[i]]])
       card.addMVVMinorBkgParametricShape("TTJets"+contrib[i]+"_mjj",["MJJ"],jsonfile,[uncertainty[0].replace("TTJets",mappdf[contrib[i]]),unc[contrib[i]]])

       #print "load ", rootFileMVV[contrib[i]], " for ttbar contribution"
       #f = ROOT.TFile(rootFileMVV[contrib[i]],"READ")
       #card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",["PT:CMS_VV_JJ_TTJets_PTZ_"+category],False,0)       
     else:
      jsonfile = resultsDir+"/JJ_"+dataset+"_TTJets"+contrib[i]+"_MVV_NP.json"
      slopejson= normjson.replace("Norm","NormSlopes")
      print "load parametrisation for MVV ttbar contributions ",jsonfile,contrib[i],slopejson
      #card.addMVVMinorBkgParametricShape("TTJets"+contrib[i]+"_mjj",["MJJ"],jsonfile,[uncertainty[0].replace("TTJets",mappdf[contrib[i]])+"_"+category,unc[contrib[i]]])
      #card.addMVVMinorBkgParametricShape("TTJets"+contrib[i]+"_mjj",["MJJ"],jsonfile,[uncertainty[0].replace("TTJets",mappdf[contrib[i]]),unc[contrib[i]]],slopejson)
      # have only one slope variation for all 6 contributions, the largest
      card.addMVVMinorBkgParametricShape("TTJets"+contrib[i]+"_mjj",["MJJ"],jsonfile,[uncertainty[0],maxunc],slopejson)


    card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    
    card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    
    card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    '''
    print " testing uncorrelated mjet unc"
    card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj_W_'+category:1.},{'CMS_res_prunedj_W_'+category:1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj_W_'+category:1.},{'CMS_res_prunedj_W_'+category:1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})

    card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj_T_'+category:1.},{'CMS_res_prunedj_T_'+category:1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj_T_'+category:1.},{'CMS_res_prunedj_T_'+category:1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})

    card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj_'+category:1.},{'CMS_res_prunedj_'+category:1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj_'+category:1.},{'CMS_res_prunedj_'+category:1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    '''
    # built final PDFs:
    # W+W PDF
    card.conditionalProduct3('TTJetsW','TTJetsresW_mjj','TTJetsW_mjetRes_l1','TTJetsW_mjetRes_l2','MJJ')

    #T+T PDF
    card.conditionalProduct3('TTJetsTop','TTJetsresT_mjj','TTJetsTop_mjetRes_l1','TTJetsTop_mjetRes_l2','MJJ')


    #nonRes+nonRes PDF
    card.conditionalProduct3('TTJetsNonRes','TTJetsnonresT_mjj','TTJetsNonRes_mjetRes_l1','TTJetsNonRes_mjetRes_l2','MJJ')
    
    #resT + nonresT
    card.conditionalProduct3('TTJetsTnonresT','TTJetsresTnonresT_mjj','TTJetsTop_mjetRes_l1','TTJetsNonRes_mjetRes_l2','MJJ')
    #nonresT + resT
    card.conditionalProduct3('TTJetsnonresTresT','TTJetsresTnonresT_mjj','TTJetsNonRes_mjetRes_l1','TTJetsTop_mjetRes_l2','MJJ')
    card.sumPdf('TTJetsTNonResT','TTJetsTnonresT','TTJetsnonresTresT',"CMS_ratio_const")
        
    #resW + nonresT
    card.conditionalProduct3('TTJetsWnonresT','TTJetsresWnonresT_mjj','TTJetsW_mjetRes_l1','TTJetsNonRes_mjetRes_l2','MJJ')
    #nonresT + resW
    card.conditionalProduct3('TTJetsnonresTresW','TTJetsresWnonresT_mjj','TTJetsNonRes_mjetRes_l1','TTJetsW_mjetRes_l2','MJJ')
    card.sumPdf('TTJetsWNonResT','TTJetsWnonresT','TTJetsnonresTresW',"CMS_ratio_const")
    
    #resW + resT
    card.conditionalProduct3('TTJetsresWresT','TTJetsresTresW_mjj','TTJetsW_mjetRes_l1','TTJetsTop_mjetRes_l2','MJJ')
    #resT + resW 
    card.conditionalProduct3('TTJetsresTresW','TTJetsresTresW_mjj','TTJetsTop_mjetRes_l1','TTJetsW_mjetRes_l2','MJJ')
    card.sumPdf('TTJetsResWResT','TTJetsresWresT','TTJetsresTresW',"CMS_ratio_const")
    
       
    print "outlabel "+self.outlabel
    if self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1:
        print "add small yield"
        for i in range(0,len(contrib)):
         card.addFixedYieldFromFile(mappdf[contrib[i]],ncontrib+i,rootFileNorm[contrib[i]],"TTJets"+mappdf[contrib[i]],0.000001)
    elif self.pseudodata.find("ttbar")!=-1:
     for i in range(0,len(contrib)):
      card.addFixedYieldFromFile(mappdf[contrib[i]],ncontrib+i,rootFileNorm[contrib[i]],"TTJets"+contrib[i])
    else:
        norm = open(normjson,"r")
        norms = json.load(norm)
        for i in range(0,len(contrib)):
            card.addYield(mappdf[contrib[i]],ncontrib+i,norms[contrib[i]])

 #default implementation: split in 6 contributions W+W, T+T, nonRes+nonRes, nonRes+T, nonres+W, resT+resW with mjj templates
 def AddTTBackground4(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib,normjson):
    print "add TT+jets background"
    contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
    mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}

    #card.addMJJTTJetsParametricCBShapeResW("TTJetsW_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    #card.addMJJTTJetsParametricCBShapeResW("TTJetsW_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResW("TTJetsW_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)#,{'CMS_f_g1':1.},{'CMS_f_res':1.})

    #card.addMJJTTJetsParametricCBShapeResT("TTJetsTop_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    #card.addMJJTTJetsParametricCBShapeResT("TTJetsTop_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeResT("TTJetsTop_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})

    #card.addMJJTTJetsParametricShapeNonResGaus("TTJetsNonRes_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    #card.addMJJTTJetsParametricShapeNonResGaus("TTJetsNonRes_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})

    card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l1","MJ1",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})
    card.addMJJTTJetsParametricShapeNonRes("TTJetsNonRes_mjetRes_l2","MJ2",resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.})#,{'CMS_f_g1':1.},{'CMS_f_res':1.})

    if self.pseudodata.find("ttbar")!=-1: # when making workspace to derive ttbar normalizations
     for i in range(0,len(contrib)):
      card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",['TOPPT:CMS_VV_JJ_'+mappdf[contrib[i]]+'_TOPPTZ_'+category],False,0)
    else: # when making ttbar with all backgrounds, using the normalizations derived in the step above
     for i in range(0,len(contrib)):
      card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",['TOPPT:CMS_VV_JJ_TTJets_TOPPTZ'],False,0) #default
      #print " ,./,./,./,.,./,./,./,./,./,./,/.,./,./,.,./,./,./,./,./,./,./,      no top-pt !!!!!! ,.,./,.,./,./,./,./,./,./,./,./,./,./,./,./,./,.,./,/"
      #card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal") #,['TOPPT:CMS_VV_JJ_TTJets_TOPPTZ'],False,0)
      #print "-------------           TT mjj per component ---------------------"
      #card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",['TOPPT:CMS_VV_JJ_'+mappdf[contrib[i]]+'_TOPPTZ'],False,0)

      #print " ,./,./,./,.,./,./,./,./,./,./,/.,./,./,.,./,./,./,./,./,./,./,  !!!!!!   top shapes per category !!!!!! ,.,./,.,./,./,./,./,./,./,./,./,./,./,./,./,./,.,./,/"
      #card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",['TOPPT:CMS_VV_JJ_TTJets_TOPPTZ_'+category],False,0)
      #if contrib[i] == "nonresT": card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",['TOPPT:CMS_VV_JJ_'+mappdf[contrib[i]]+'_TOPPTZ'],False,0)
      #else : card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",['TOPPT:CMS_VV_JJ_TTJetsPR_TOPPTZ'],False,0)

    '''
    for i in range(0,len(contrib)):
     card.addHistoShapeFromFile("TTJets"+contrib[i]+"_mjj",["MJJ"],rootFileMVV[contrib[i]],"histo_nominal",['TOPPT:CMS_VV_JJ_'+mappdf[contrib[i]]+'_TOPPTZ_'+category],False,0)
    '''
    # built final PDFs:
    # W+W PDF
    print " *** W+W PDF "
    card.conditionalProduct3('TTJetsW','TTJetsresW_mjj','TTJetsW_mjetRes_l1','TTJetsW_mjetRes_l2','MJJ')

    #T+T PDF
    print " *** T+T PDF "
    card.conditionalProduct3('TTJetsTop','TTJetsresT_mjj','TTJetsTop_mjetRes_l1','TTJetsTop_mjetRes_l2','MJJ')

    #nonRes+nonRes PDF
    print " nonRes + nonRes PDF "
    card.conditionalProduct3('TTJetsNonRes','TTJetsnonresT_mjj','TTJetsNonRes_mjetRes_l1','TTJetsNonRes_mjetRes_l2','MJJ')

    #resT + nonresT
    card.conditionalProduct3('TTJetsTnonresT','TTJetsresTnonresT_mjj','TTJetsTop_mjetRes_l1','TTJetsNonRes_mjetRes_l2','MJJ')
    #nonresT + resT
    card.conditionalProduct3('TTJetsnonresTresT','TTJetsresTnonresT_mjj','TTJetsNonRes_mjetRes_l1','TTJetsTop_mjetRes_l2','MJJ')
    card.sumPdf('TTJetsTNonResT','TTJetsTnonresT','TTJetsnonresTresT',"CMS_ratio_const")

    #resW + nonresT
    card.conditionalProduct3('TTJetsWnonresT','TTJetsresWnonresT_mjj','TTJetsW_mjetRes_l1','TTJetsNonRes_mjetRes_l2','MJJ')
    #nonresT + resW
    card.conditionalProduct3('TTJetsnonresTresW','TTJetsresWnonresT_mjj','TTJetsNonRes_mjetRes_l1','TTJetsW_mjetRes_l2','MJJ')
    card.sumPdf('TTJetsWNonResT','TTJetsWnonresT','TTJetsnonresTresW',"CMS_ratio_const")

    #resW + resT
    card.conditionalProduct3('TTJetsresWresT','TTJetsresTresW_mjj','TTJetsW_mjetRes_l1','TTJetsTop_mjetRes_l2','MJJ')
    #resT + resW
    card.conditionalProduct3('TTJetsresTresW','TTJetsresTresW_mjj','TTJetsTop_mjetRes_l1','TTJetsW_mjetRes_l2','MJJ')
    card.sumPdf('TTJetsResWResT','TTJetsresWresT','TTJetsresTresW',"CMS_ratio_const")


    print "outlabel "+self.outlabel
    if self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1 or self.pseudodata.find("dib")!=-1:
        print "add small yield"
        for i in range(0,len(contrib)):
         card.addFixedYieldFromFile(mappdf[contrib[i]],ncontrib+i,rootFileNorm[contrib[i]],"TTJets"+contrib[i],0.000001)
    elif self.pseudodata.find("ttbar")!=-1: 
     for i in range(0,len(contrib)):
      card.addFixedYieldFromFile(mappdf[contrib[i]],ncontrib+i,rootFileNorm[contrib[i]],"TTJets"+contrib[i])
    else:
        norm = open(normjson,"r")
        norms = json.load(norm)
        for i in range(0,len(contrib)):
         print "*****  no tagger pt reweight for tt"
         card.addYield(mappdf[contrib[i]],ncontrib+i,norms[contrib[i]])
         '''
         print " contrib "+contrib[i]+" tagger_pt_dependence "+self.tagger_pt_dependence[contrib[i]]
         if self.tagger_pt_dependence[contrib[i]] == "1" :
          print " no pt dep"
          card.addYield(mappdf[contrib[i]],ncontrib+i,norms[contrib[i]])
         else:
          print " pt dep"
          card.addYieldWithUncertainty(mappdf[contrib[i]],ncontrib+i,norms[contrib[i]],"CMS_tagger_PtDependence",self.tagger_pt_dependence[contrib[i]],1.0)
         '''
 def AddWResBackground(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib,uncertainty=[]):
       print "add Wres background"  
       sys.path.append(resultsDir)
       module_name = 'JJ_%s_WJets_%s'%(dataset,category)
       module = __import__(module_name)  
       print module_name
       # W+jets 
       if self.fitvjetsmjj == True:
        card.addMVVMinorBkgParametricShape("Wjets_mjj",["MJJ"],rootFileMVV,uncertainty)
       elif self.kfactors == True:
        print "<<<<<<<<         <<<<<<<     using kfactors!!!    >>>>>>>   >>>>>>>>>>>>"
        card.addHistoShapeFromFile("Wjets_mjj_c1",["MJJ"],rootFileMVV,"histo_nominal",['Kfactors:CMS_VV_JJ_Wjets_Kfactors'],False,0)
       else:
        print " >>>>>>>>>>>> usual V+jets MVV "
        card.addHistoShapeFromFile("Wjets_mjj_c1",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_Wjets_PTZ_'+category,'OPT:CMS_VV_JJ_Wjets_OPTZ_'+category],False,0)

       card.addMJJSignalShapeNOEXP("Wjets_mjetRes_l1","MJ1","",getattr(module,'Wjets_TTbar_%s_Res'%category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       print " addGaussianShape"
       card.addGaussianShape("Wjets_mjetNonRes_l2","MJ2",getattr(module,'Wjets_TTbar_%s_nonRes'%category))
       if self.fitvjetsmjj == True:
        card.product3D("Wjets_c2","Wjets_mjetRes_l2","Wjets_mjetNonRes_l1","Wjets_mjj")
       else:
        card.product3D("Wjets_c1","Wjets_mjetRes_l1","Wjets_mjetNonRes_l2","Wjets_mjj_c1")

       # jets + W
       if self.fitvjetsmjj == False and self.kfactors == False:
        print " >>>>>>>>>>>> usual V+jets MVV "
        card.addHistoShapeFromFile("Wjets_mjj_c2",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_Wjets_PTZ_'+category,'OPT:CMS_VV_JJ_Wjets_OPTZ_'+category],False,0)
       elif self.kfactors == True:
        card.addHistoShapeFromFile("Wjets_mjj_c2",["MJJ"],rootFileMVV,"histo_nominal",['Kfactors:CMS_VV_JJ_Wjets_Kfactors'],False,0)

       card.addMJJSignalShapeNOEXP("Wjets_mjetRes_l2","MJ2","",getattr(module,'Wjets_TTbar_%s_Res'%category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       card.addGaussianShape("Wjets_mjetNonRes_l1","MJ1",getattr(module,'Wjets_TTbar_%s_nonRes'%category))
       if self.fitvjetsmjj == True:
        card.product3D("Wjets_c2","Wjets_mjetRes_l2","Wjets_mjetNonRes_l1","Wjets_mjj")
       else:
        card.product3D("Wjets_c2","Wjets_mjetRes_l2","Wjets_mjetNonRes_l1","Wjets_mjj_c2")
       card.sumPdf('Wjets',"Wjets_c1","Wjets_c2","CMS_ratio_Wjets_"+category)

       print "outlabel "+self.outlabel
       if self.pseudodata=="" or self.pseudodata=="Vjets":
           card.addFixedYieldFromFile('Wjets',ncontrib,rootFileNorm,"WJets")
       elif self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1 or self.pseudodata.find("ttbar")!=-1 or self.pseudodata.find("dib")!=-1:
           print "add small yield"
           card.addFixedYieldFromFile('Wjets',ncontrib,rootFileNorm,"WJets",0.0000000000001)
       else:
           #card.addFixedYieldFromFileWithUncertainty('Wjets',ncontrib,rootFileNorm,"WJets",1.0,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Wjets"],1.0)
           print "*****  no tagger pt reweight for W jets "
           card.addFixedYieldFromFile('Wjets',ncontrib,rootFileNorm,"WJets",self.sfWjets) #,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Wjets"],1.0)

 def AddZResBackground(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib,uncertainty=[]):
       print "add Zres background"
       sys.path.append(resultsDir)
       module_name = 'JJ_%s_WJets_%s'%(dataset,category)
       module = __import__(module_name)   
            
       # Z+jets 
       if self.fitvjetsmjj == True:
        #card.addMVVMinorBkgParametricShape("Zjets_mjj_c1",["MJJ"],rootFileMVV,uncertainty)
        card.addMVVMinorBkgParametricShape("Zjets_mjj",["MJJ"],rootFileMVV,uncertainty)
       elif self.kfactors == True:
        print "<<<<<<<<         <<<<<<<     using kfactors!!!    >>>>>>>   >>>>>>>>>>>>"
        card.addHistoShapeFromFile("Zjets_mjj_c1",["MJJ"],rootFileMVV,"histo_nominal",['Kfactors:CMS_VV_JJ_Zjets_Kfactors'],False,0)
       else:
        print " >>>>>>>>>>>> usual V+jets MVV "
        card.addHistoShapeFromFile("Zjets_mjj_c1",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_Zjets_PTZ_'+category,'OPT:CMS_VV_JJ_Zjets_OPTZ_'+category],False,0)

       card.addMJJSignalShapeNOEXP("Zjets_mjetRes_l1","MJ1","",getattr(module,'Zjets_%s_Res'%category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       card.addGaussianShape("Zjets_mjetNonRes_l2","MJ2",getattr(module,'Zjets_%s_nonRes'%category))
       if self.fitvjetsmjj == True:
        card.product3D("Zjets_c1","Zjets_mjetRes_l1","Zjets_mjetNonRes_l2","Zjets_mjj")
       else:
        card.product3D("Zjets_c1","Zjets_mjetRes_l1","Zjets_mjetNonRes_l2","Zjets_mjj_c1")
           
       # jets + Z
       if self.fitvjetsmjj == False and self.kfactors == False:
        print " >>>>>>>>>>>> usual V+jets MVV "
        card.addHistoShapeFromFile("Zjets_mjj_c2",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_Zjets_PTZ_'+category,'OPT:CMS_VV_JJ_Zjets_OPTZ_'+category],False,0)
       elif self.kfactors == True:
        card.addHistoShapeFromFile("Zjets_mjj_c2",["MJJ"],rootFileMVV,"histo_nominal",['Kfactors:CMS_VV_JJ_Zjets_Kfactors'],False,0)
       card.addMJJSignalShapeNOEXP("Zjets_mjetRes_l2","MJ2","",getattr(module,'Zjets_%s_Res'%category),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       card.addGaussianShape("Zjets_mjetNonRes_l1","MJ1",getattr(module,'Zjets_%s_nonRes'%category))
       if self.fitvjetsmjj == True:
        card.product3D("Zjets_c2","Zjets_mjetRes_l2","Zjets_mjetNonRes_l1","Zjets_mjj")
       else:
        card.product3D("Zjets_c2","Zjets_mjetRes_l2","Zjets_mjetNonRes_l1","Zjets_mjj_c2")
       card.sumPdf('Zjets',"Zjets_c1","Zjets_c2","CMS_ratio_Zjets_"+category)

       if self.pseudodata=="" or self.pseudodata=="Vjets":
             card.addFixedYieldFromFile('Zjets',ncontrib,rootFileNorm,"ZJets") 
       elif self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1 or self.pseudodata.find("ttbar")!=-1 or self.pseudodata.find("dib")!=-1:
           card.addFixedYieldFromFile('Zjets',ncontrib,rootFileNorm,"ZJets",0.0000000000001)
       else:
           #card.addFixedYieldFromFileWithUncertainty('Zjets',ncontrib,rootFileNorm,"ZJets",1.0,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Zjets"],1.0)
           print "*****  no tagger pt reweight for Z jets "
           card.addFixedYieldFromFile('Zjets',ncontrib,rootFileNorm,"ZJets",self.sfZjets) #,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Wjets"],1.0)

       print "stop Zres background"
   


 def AddWZResBackground(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib,uncertainty=[]):
       print "add WZ background"
       sys.path.append(resultsDir)
       module_name = 'JJ_%s_WZ_NP'%(dataset)
       module = __import__(module_name)
       print module_name
       card.addHistoShapeFromFile("WZ_mjj",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_WZ_PTZ_'+category,'OPT:CMS_VV_JJ_WZ_OPTZ_'+category],False,0)

       card.addMJJSignalShapeNOEXP("WZ_mjetRes_l1","MJ1","",getattr(module,'Res_random'),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       card.addMJJSignalShapeNOEXP("WZ_mjetRes_l2","MJ2","",getattr(module,'Res_random'),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       card.product3D("WZ","WZ_mjetRes_l1","WZ_mjetRes_l2","WZ_mjj")

       print "outlabel "+self.outlabel
       if self.pseudodata=="" or self.pseudodata=="VZ":
           card.addFixedYieldFromFile('WZ',ncontrib,rootFileNorm,"WZ")
       elif self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1 or self.pseudodata.find("ttbar")!=-1 :
           print "add small yield"
           card.addFixedYieldFromFile('WZ',ncontrib,rootFileNorm,"WZ",0.0000000000001)
       else:
           #card.addFixedYieldFromFileWithUncertainty('Wjets',ncontrib,rootFileNorm,"WJets",1.0,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Wjets"],1.0)
           print "*****  no tagger pt reweight for WZ "
           card.addFixedYieldFromFile('WZ',ncontrib,rootFileNorm,"WZJets") #,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Wjets"],1.0)

 def AddZZResBackground(self,card,dataset,category,rootFileMVV,rootFileNorm,resultsDir,ncontrib,uncertainty=[]):
       print "add ZZ background"
       sys.path.append(resultsDir)
       module_name = 'JJ_%s_ZZ_NP'%(dataset)
       module = __import__(module_name)
       print module_name
       card.addHistoShapeFromFile("ZZ_mjj",["MJJ"],rootFileMVV,"histo_nominal",['PT:CMS_VV_JJ_ZZ_PTZ_'+category,'OPT:CMS_VV_JJ_ZZ_OPTZ_'+category],False,0)

       card.addMJJSignalShapeNOEXP("ZZ_mjetRes_l1","MJ1","",getattr(module,'Res_random'),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       card.addMJJSignalShapeNOEXP("ZZ_mjetRes_l2","MJ2","",getattr(module,'Res_random'),{'CMS_scale_prunedj':1.},{'CMS_res_prunedj':1.},self.scales)
       card.product3D("ZZ","ZZ_mjetRes_l1","ZZ_mjetRes_l2","ZZ_mjj")

       print "outlabel "+self.outlabel
       if self.pseudodata=="" or self.pseudodata=="VZ":
           card.addFixedYieldFromFile('ZZ',ncontrib,rootFileNorm,"ZZ")
       elif self.outlabel.find("sigOnly")!=-1 or self.outlabel.find("sigonly")!=-1 or self.pseudodata.find("ttbar")!=-1:
           print "add small yield"
           card.addFixedYieldFromFile('ZZ',ncontrib,rootFileNorm,"ZZJets",0.0000000000001)
       else:
           #card.addFixedYieldFromFileWithUncertainty('Wjets',ncontrib,rootFileNorm,"WJets",1.0,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Wjets"],1.0)
           print "*****  no tagger pt reweight for ZZ "
           card.addFixedYieldFromFile('ZZ',ncontrib,rootFileNorm,"ZZJets") #,"CMS_tagger_PtDependence",self.tagger_pt_dependence["Wjets"],1.0)



 def AddNonResBackground(self,card,dataset,category,rootFile3DPDF,rootFileNorm,ncontrib,RESCALE,indir):
      #default!!!
      card.addHistoShapeFromFile("nonRes",["MJ1","MJ2","MJJ"],rootFile3DPDF,"histo",['PT:CMS_VV_JJ_nonRes_PT_'+category,'OPT:CMS_VV_JJ_nonRes_OPT_'+category,'TurnOn:CMS_VV_JJ_nonRes_TurnOn_'+category,'altshape:CMS_VV_JJ_nonRes_altshape_'+category,'altshape2:CMS_VV_JJ_nonRes_altshape2_'+category],False,0)
      #card.addHistoShapeFromFile("nonRes",["MJ1","MJ2","MJJ"],rootFile3DPDF,"histo",['PT:CMS_VV_JJ_nonRes_PT_'+category,'OPT:CMS_VV_JJ_nonRes_OPT_'+category,'altshape:CMS_VV_JJ_nonRes_altshape_'+category,'altshape2:CMS_VV_JJ_nonRes_altshape2_'+category,'PT6:CMS_VV_JJ_nonRes_PT6_'+category,'OPT6:CMS_VV_JJ_nonRes_OPT6_'+category,'OPT3:CMS_VV_JJ_nonRes_OPT3_'+category,'TurnOn:CMS_VV_JJ_nonRes_TurnOn_'+category,'PT3:CMS_VV_JJ_nonRes_PT3_'+category],False,0) #,'PT4:CMS_VV_JJ_nonRes_PT4_'+category,'OPT4:CMS_VV_JJ_nonRes_OPT4_'+category,'PT5:CMS_VV_JJ_nonRes_PT5_'+category,'OPT5:CMS_VV_JJ_nonRes_OPT5_'+category,'PT6:CMS_VV_JJ_nonRes_PT6_'+category,'OPT6:CMS_VV_JJ_nonRes_OPT6_'+category],False,0)
          
      if self.outlabel.find("sigonly")!=-1 or self.outlabel.find("sigOnly")!=-1 or self.pseudodata.find("ttbar")!=-1 or self.pseudodata.find("dib")!=-1:
          card.addFixedYieldFromFile("nonRes",ncontrib,rootFileNorm,"nonRes",0.0000000000001)
      elif RESCALE==True:
          normExp = open(indir+"/Expected_"+dataset+"_"+category+".json","r")
          normsExp = json.load(normExp)
          normObs = open(indir+"/Observed_"+dataset+"_"+category+".json","r")
          normsObs = json.load(normObs)
          rescale=normsObs["nonRes"]/normsExp["nonRes"]
          print " obs/exp ",rescale
          rescale=rescale*self.sfQCD
          print" final rescale ",rescale
          card.addFixedYieldFromFile("nonRes",ncontrib,rootFileNorm,"nonRes",rescale)
      else:
          card.addFixedYieldFromFile("nonRes",ncontrib,rootFileNorm,"nonRes",self.sfQCD)

 def AddData(self,card,fileData,histoName,scaleData):

      card.importBinnedData(fileData,histoName,["MJ1","MJ2","MJJ"],'data_obs',scaleData)
 
 #with old implementation 
 def AddTTSystematics(self,card,sig,dataset,category):
    card.addSystematic("CMS_f_g1","param",[0.0,0.02])
    card.addSystematic("CMS_f_res","param",[0.0,0.08])
    card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{'TTJets':1.2})  
    card.addSystematic("CMS_VV_JJ_TTJets_PTZ_"+category,"param",[0,0.1]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJets_OPTZ_"+category,"param",[0,0.1]) #0.333
   
 #with new implementation
 def AddTTSystematics2(self,card,sig,dataset,category,resultsDir):
    card.addSystematic("CMS_f_g1","param",[0.0,0.02])
    card.addSystematic("CMS_f_res","param",[0.0,0.08])
    card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{'TTJetsW':1.2,'TTJetsTop':1.2,'TTJetsNonRes':1.2})  
    card.addSystematic("CMS_VV_JJ_TTJets_PTZ_"+category,"param",[0,0.1]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJets_OPTZ_"+category,"param",[0,0.1]) #0.333

    f=open(resultsDir+"/JJ_%s_TTJets_%s.json"%(dataset,category))
    info=json.load(f)
    card.addSystematic("TTresW_frac","rateParam", "{formula}".format(formula=info['f_g1'].replace('MJJ','@0')),"JJ_{category}_13TeV_{year}".format(category=category,year=dataset), "TTJetsW",'MJJ')
    card.addSystematic("TTres_frac","rateParam", "{formula}".format(formula=info['f_res'].replace('MJJ','@0')),"JJ_{category}_13TeV_{year}".format(category=category,year=dataset), "TTJetsW",'MJJ')
    card.addSystematic("TTresT_frac","rateParam", "(@0*(1-@1))","JJ_{category}_13TeV_{year}".format(category=category,year=dataset), "TTJetsTop",'TTres_frac,TTresW_frac')
    card.addSystematic("TTnonres_frac","rateParam", "(1-@0)","JJ_{category}_13TeV_{year}".format(category=category,year=dataset), "TTJetsNonRes",'TTres_frac')

 #with old implementation 
 def AddTTSystematics3(self,card,sig,dataset,category):
    card.addSystematic("CMS_f_g1","param",[0.0,0.02])
    card.addSystematic("CMS_f_res","param",[0.0,0.08])
    #   card.addSystematic("CMS_scale_prunedj_top","param",[0.0,0.02])
    #    card.addSystematic("CMS_res_prunedj_top","param",[0.0,0.08])
    card.addSystematic("CMS_scale_prunedj","param",[0.0,0.02])
    card.addSystematic("CMS_res_prunedj","param",[0.0,0.08])
    card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{'TTJetsW':1.2,'TTJetsTop':1.2,'TTJetsNonRes':1.2,'TTJetsWNonResT':1.2,'TTJetsResWResT':1.2,'TTJetsTNonResT':1.2})  
    #card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{'TTJets':1.2})  
    card.addSystematic("CMS_VV_JJ_TTJetsTop_PTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsTop_OPTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsW_PTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsW_OPTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsNonRes_PTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsNonRes_OPTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsTnonresT_PTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsTnonresT_OPTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsWnonresT_PTZ_"+category,"param",[0,0.333]) #0.333
    card.addSystematic("CMS_VV_JJ_TTJetsWnonresT_OPTZ_"+category,"param",[0,0.333]) #0.333
    
 def AddTTSystematics4(self,card,extra_uncertainty,dataset,category):
    card.addSystematic("CMS_f_g1","param",[0.0,0.02])
    card.addSystematic("CMS_f_res","param",[0.0,0.08])
    #card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{'TTJets':1.2})
    card.addSystematic("CMS_scale_prunedj","param",[0.0,0.02])
    card.addSystematic("CMS_res_prunedj","param",[0.0,0.08])
    '''
    print "decorrelateeeeeeeee "
    card.addSystematic("CMS_scale_prunedj_"+category,"param",[0.0,0.3])
    card.addSystematic("CMS_res_prunedj_"+category,"param",[0.0,0.3])
    card.addSystematic("CMS_scale_prunedj_W_"+category,"param",[0.0,0.3])
    card.addSystematic("CMS_res_prunedj_W_"+category,"param",[0.0,0.3])
    card.addSystematic("CMS_scale_prunedj_T_"+category,"param",[0.0,0.3])
    card.addSystematic("CMS_res_prunedj_T_"+category,"param",[0.0,0.3])
    '''
    contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
    mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}
    #uncjsonfile=open('results_'+dataset+"/JJ_"+dataset+"_TTJets_MjjUnc_"+category+".json")
    uncjsonfile=open('results_'+dataset+"/JJ_"+dataset+"_TTJets_MjjUnc_NP.json")
    unc = json.load(uncjsonfile)
    allunc = []
    for i in range(0,len(contrib)):
       allunc.append(unc[contrib[i]])

    #card.addSystematic("CMS_scale_prunedj_top","param",[0.0,0.02])
    #card.addSystematic("CMS_res_prunedj_top","param",[0.0,0.08])
    if self.pseudodata.find("ttbar")==-1:
        #card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{'TTJetsW':1.2,'TTJetsTop':1.2,'TTJetsNonRes':1.2,'TTJetsWNonResT':1.2,'TTJetsResWResT':1.2,'TTJetsTNonResT':1.2}) 
        card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{'TTJetsW':1.05,'TTJetsTop':1.05,'TTJetsNonRes':1.05,'TTJetsWNonResT':1.05,'TTJetsResWResT':1.05,'TTJetsTNonResT':1.05})
        #card.addSystematic(extra_uncertainty[0],"param",[0.0,extra_uncertainty[1]])
        #card.addSystematic(extra_uncertainty[0].replace("TTJets",mappdf[contrib[i]])+"_"+category,"param",[0.0,float("{:.3f}".format(unc[contrib[i]]))])
        card.addSystematic(extra_uncertainty[0],"param",[0.0,float("{:.3f}".format(max(allunc)))])
    else:
        for i in range(0,len(contrib)):
         #card.addSystematic(extra_uncertainty[0].replace("TTJets",mappdf[contrib[i]])+"_"+category,"param",[0.0,float("{:.3f}".format(unc[contrib[i]]))])
         card.addSystematic("CMS_VV_JJ_"+mappdf[contrib[i]]+"_norm","lnN",{mappdf[contrib[i]]:3.2})
         card.addSystematic(extra_uncertainty[0].replace("TTJets",mappdf[contrib[i]]),"param",[0.0,float("{:.3f}".format(unc[contrib[i]]))])
    
 def AddTTSystematics5(self,card,category,vbf):
    contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
    #contribPR =["resT","resW","resTnonresT","resWnonresT","resTresW"]
    mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}

    if category.find("VBF") != -1 and not vbf: category = category.replace("VBF_","")

    if self.pseudodata.find("ttbar")==-1: #workspace with all backgrounds
        card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{mappdf[ttcon]:1.06 for ttcon in contrib}) #default!!!!!
        card.addSystematic("CMS_VV_JJ_TTJets_TOPPTZ","param",[0,1.]) #default!!!!

        #card.addSystematic("CMS_VV_JJ_TTJets_norm","lnN",{mappdf[ttcon]:1.30 for ttcon in contrib})

        '''
        for i in range(0,len(contrib)):
         card.addSystematic("CMS_VV_JJ_"+mappdf[contrib[i]]+"_norm","lnN",{mappdf[contrib[i]]:1.30})
        '''
        '''
        card.addSystematic("CMS_VV_JJ_TTJets_W_norm","lnN",{"TTJetsW":1.30,"TTJetsWNonResT":1.30,"TTJetsResWResT":1.30})
        card.addSystematic("CMS_VV_JJ_TTJets_T_norm","lnN",{"TTJetsT":1.30,"TTJetsTNonResT":1.30,"TTJetsResWResT":1.30})
        card.addSystematic("CMS_VV_JJ_TTJets_NonRes_norm","lnN",{"TTJetsNonRes":1.30,"TTJetsTNonResT":1.30,"TTJetsWNonResT":1.30})
        '''

        #print "///////////////////////        TT norm per categoryyyyyyy **************** "
        #card.addSystematic("CMS_VV_JJ_TTJets_norm_"+category,"lnN",{mappdf[ttcon]:1.06 for ttcon in contrib})
        #print " ,./,./,./,.,./,./,./,./,./,./,/.,./,./,.,./,./,./,./,./,./,./,      no top-pt !!!!!! ,.,./,.,./,./,./,./,./,./,./,./,./,./,./,./,./,.,./,/"
        #card.addSystematic("CMS_VV_JJ_TTJets_TOPPTZ","param",[0,2.])
        #print " *(*(*(*(*( top shape unc increased to 2 )*)*)*)*)*"

        #print "-------------           TT mjj per component ---------------------"
        #for i in range(0,len(contrib)):
        # card.addSystematic("CMS_VV_JJ_"+mappdf[contrib[i]]+"_TOPPTZ","param",[0,1.])

        #print "*&*&*&*&*&*&* top shapes per category &*&*&*&*&*&*&*&*&*&*"
        #card.addSystematic("CMS_VV_JJ_TTJets_TOPPTZ_"+category,"param",[0,1.])
        # try to separate non res from partially res
        #card.addSystematic("CMS_VV_JJ_TTJetsNonRes_TOPPTZ","param",[0,1.])
        #card.addSystematic("CMS_VV_JJ_TTJetsPR_TOPPTZ","param",[0,1.])
        #card.addSystematic("CMS_VV_JJ_TTJetsNonRes_norm_"+category,"lnN",{"TTJetsNonRes":1.06})
        #card.addSystematic("CMS_VV_JJ_TTJetsPR_norm","lnN",{mappdf[ttcon]:1.06 for ttcon in contribPR}) 

    else: # workspace with ttbar only!!!!
        for i in range(0,len(contrib)):
         card.addSystematic("CMS_VV_JJ_"+mappdf[contrib[i]]+"_norm","lnN",{mappdf[contrib[i]]:3.2})
         card.addSystematic("CMS_VV_JJ_"+mappdf[contrib[i]]+"_TOPPTZ_"+category,"param",[0,1.])

       
 def AddOneSigSystematics(self,card,sig,dataset,category,correlate,case,resultsDir="results_Run2/",pt_dependence_rescaling=1):
      print " signal ",sig
      production = "nonVBFcat"
      productionBKG = "ggDY"
      signaltype = "nonVBFsig"
      if category.find("VBF") !=-1:
       production = "VBFcat"
       productionBKG = "VBF"
      if sig.find("VBF") !=-1:
       signaltype = "VBFsig"
      print " case ",case
      if case != "0":
       # JES & JER uncertainties: migration uncertainties betwenn VBF and non VBF categories do to the mjj cut on the VBF jets + shape uncertainties
       #migration
       jesfilename=resultsDir+"/JES_case"+case+"_"+signaltype+"_"+production+".json"
       jerfilename=resultsDir+"/JER_case"+case+"_"+signaltype+"_"+production+".json"
       try:
        jesjsonfile=open(jesfilename)
        jes = json.load(jesjsonfile)
       except:
        print "no jes file ",jesfilename
        sys.exit()
       try:
        jerjsonfile=open(jerfilename)
        jer = json.load(jerjsonfile)
       except:
        print "no jer file ",jerfilename
        sys.exit()

       if case=="1":
        print "case 1: fully correlated JER and JES"
        jesunc=str(round(jes[sig.replace("VBF_","")],3))
        print "jesunc ",jesunc
        if self.dib == True:
         print " attention for DIB JES USING same as VJETS"
         card.addSystematic("CMS_jes_norm","lnN",{'%s'%sig:jesunc,'Wjets':self.JES_unc[productionBKG]['Wjets'],'Zjets':self.JES_unc[productionBKG]['Zjets'],"TTJetsW":self.JES_unc[productionBKG]['TTjets'],"TTJetsWNonResT":self.JES_unc[productionBKG]['TTjets'],"TTJetsResWResT":self.JES_unc[productionBKG]['TTjets'],"TTJetsTop":self.JES_unc[productionBKG]['TTjets'],"TTJetsNonRes":self.JES_unc[productionBKG]['TTjets'],"TTJetsTNonResT":self.JES_unc[productionBKG]['TTjets'],'WZ':self.JES_unc[productionBKG]['Wjets'],'ZZ':self.JES_unc[productionBKG]['Zjets']})
        else:
         card.addSystematic("CMS_jes_norm","lnN",{'%s'%sig:jesunc,'Wjets':self.JES_unc[productionBKG]['Wjets'],'Zjets':self.JES_unc[productionBKG]['Zjets'],"TTJetsW":self.JES_unc[productionBKG]['TTjets'],"TTJetsWNonResT":self.JES_unc[productionBKG]['TTjets'],"TTJetsResWResT":self.JES_unc[productionBKG]['TTjets'],"TTJetsTop":self.JES_unc[productionBKG]['TTjets'],"TTJetsNonRes":self.JES_unc[productionBKG]['TTjets'],"TTJetsTNonResT":self.JES_unc[productionBKG]['TTjets'],})
        jerunc=str(round(jer[sig.replace("VBF_","")],3))
        print "jerunc ",jerunc
        if self.dib == True:
         print " attention for DIB JER USING same as VJETS"
         card.addSystematic("CMS_jer_norm","lnN",{'%s'%sig:jerunc,'Wjets':self.JER_unc[productionBKG]['Wjets'],'Zjets':self.JER_unc[productionBKG]['Zjets'],"TTJetsW":self.JER_unc[productionBKG]['TTjets'],"TTJetsWNonResT":self.JER_unc[productionBKG]['TTjets'],"TTJetsResWResT":self.JER_unc[productionBKG]['TTjets'],"TTJetsTop":self.JER_unc[productionBKG]['TTjets'],"TTJetsNonRes":self.JER_unc[productionBKG]['TTjets'],"TTJetsTNonResT":self.JER_unc[productionBKG]['TTjets'],'WZ':self.JER_unc[productionBKG]['Wjets'],'ZZ':self.JER_unc[productionBKG]['Zjets']})
        else:
         card.addSystematic("CMS_jer_norm","lnN",{'%s'%sig:jerunc,'Wjets':self.JER_unc[productionBKG]['Wjets'],'Zjets':self.JER_unc[productionBKG]['Zjets'],"TTJetsW":self.JER_unc[productionBKG]['TTjets'],"TTJetsWNonResT":self.JER_unc[productionBKG]['TTjets'],"TTJetsResWResT":self.JER_unc[productionBKG]['TTjets'],"TTJetsTop":self.JER_unc[productionBKG]['TTjets'],"TTJetsNonRes":self.JER_unc[productionBKG]['TTjets'],"TTJetsTNonResT":self.JER_unc[productionBKG]['TTjets']})
       else:
        print "case ",case,"not found!"

       #shape
      print " adding CMS_jes_scale_j "
      card.addSystematic("CMS_jes_scale_j","param",[0.0,0.012])
      #card.addSystematic("CMS_jes_res_j","param",[0.0,0.04])
      #card.addSystematic("CMS_jer_scale_j","param",[0.0,0.002])
      card.addSystematic("CMS_jer_res_j","param",[0.0,0.06])
      #card.addSystematic("CMS_jer_res_j","param",[0.0,0.08])

      card.addSystematic("CMS_scale_prunedj","param",[0.0,0.02])
      if self.pseudodata == "True" or self.pseudodata == "PrepPseudo":
       card.addSystematic("CMS_res_prunedj","param",[0.0,0.08])
       print " *!*!*!!*!*!*!*!*!*!*!*!*!**!*!*! removed 1 sigma smearing in the jet mass!!!! !*!*!*!*!*!*!**!*!"
      else:
       card.addSystematic("CMS_res_prunedj","param",[0.08,0.16])

      taggingfile = resultsDir+'/migrationunc_'+sig+'_'+dataset+'.json'
      with open(taggingfile) as json_file:
       data_sig = json.load(json_file)
       signal = sig
      if sig.find('Zprime')!=-1 and sig.find("ZH")!=-1: signal = "ZprimeToZh"
      if sig.find('Zprime')!=-1 and sig.find("WW")!=-1: signal = "ZprimeToWW"
      if sig.find('Wprime')!=-1 and sig.find("WH")!=-1: signal = "WprimeToWh"
      if sig.find('Wprime')!=-1 and sig.find("WZ")!=-1: signal = "WprimeToWZ"
      if sig.find('BulkGWW')!=-1 : signal = "BulkGravToWW"
      if sig.find('BulkGZZ')!=-1 : signal = "BulkGravToZZ"
      if sig.find('VBF')!=-1 : signal = "VBF_"+sig
      contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
      mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}
      uncup_t = {}
      uncdown_t = {}
      with open(taggingfile.replace(sig,"WJets")) as json_file_w:
       data_w = json.load(json_file_w)
      with open(taggingfile.replace(sig,"ZJets")) as json_file_z:
       data_z = json.load(json_file_z)
      with open(taggingfile.replace(sig,"TTJets")) as json_file_t:
       data_t = json.load(json_file_t)
      uncup_s   = round(1.-(1.-data_sig[sig+"_CMS_VV_JJ_DeepJet_Htag_eff"][category+"_up"])*pt_dependence_rescaling,2)
      uncdown_s = round(1.-(1.-data_sig[sig+"_CMS_VV_JJ_DeepJet_Htag_eff"][category+"_down"])*pt_dependence_rescaling,2)
      uncup_w   = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WJets."+category+"_up"])*pt_dependence_rescaling,2)
      uncdown_w = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WJets."+category+"_down"])*pt_dependence_rescaling,2)
      uncup_z   = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZJets."+category+"_up"])*pt_dependence_rescaling,2)
      uncdown_z = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZJets."+category+"_down"])*pt_dependence_rescaling,2)
      for c in contrib:
       uncup_t.update( {mappdf[c] :round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Htag_eff"][mappdf[c]+"."+category+"_up"])*pt_dependence_rescaling,2) })
       uncdown_t.update({mappdf[c] : round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Htag_eff"][mappdf[c]+"."+category+"_down"])*pt_dependence_rescaling,2)})
      if self.dib == True:
       print " ((((((( diiiiiiiiiiibbbbbbbb ))))))))"
       with open(taggingfile.replace(sig,"WZJets")) as json_file_wz:
        data_wz = json.load(json_file_wz)
       uncup_wz   = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WZJets."+category+"_up"])*pt_dependence_rescaling,2)
       uncdown_wz = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WZJets."+category+"_down"])*pt_dependence_rescaling,2)
       with open(taggingfile.replace(sig,"ZZJets")) as json_file_zz:
        data_zz = json.load(json_file_zz)
       uncup_zz   = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZZJets."+category+"_up"])*pt_dependence_rescaling,2)
       uncdown_zz = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZZJets."+category+"_down"])*pt_dependence_rescaling,2)


       unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"]),'WZ': str(uncdown_wz)+"/"+ str(uncup_wz),'ZZ': str(uncdown_zz)+"/"+ str(uncup_zz)}

      else:
       unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"])}

      #unc = {'%s'%sig: str(uncdown_s)+"/"+ str(uncup_s)}
      if (category.find('VV_HPHP') !=-1 or category.find('VH_HPLP') !=-1 or category.find('VV_HPLP') !=-1):
       print " #################   taking into account the H/V tagging anti-correlation ############## "
       #unc = {'%s'%sig: str(uncup_s)+"/"+ str(uncdown_s) }
       if self.dib == True:
        unc = {'%s'%sig: str(uncup_s)+"/"+ str(uncdown_s),'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"]),'WZ': str(uncup_wz)+"/"+ str(uncdown_wz),'ZZ': str(uncup_zz)+"/"+ str(uncdown_zz)}
       else:
        unc = {'%s'%sig: str(uncup_s)+"/"+ str(uncdown_s),'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"])}

      card.addSystematic("CMS_Htagger_PtDependence","lnN",unc)
    
      uncup_s   = round(1.-(1.-data_sig[sig+"_CMS_VV_JJ_DeepJet_Vtag_eff"][category+"_up"])*pt_dependence_rescaling,2)
      uncdown_s = round(1.-(1.-data_sig[sig+"_CMS_VV_JJ_DeepJet_Vtag_eff"][category+"_down"])*pt_dependence_rescaling,2)
      uncup_w   = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WJets."+category+"_up"])*pt_dependence_rescaling,2)
      uncdown_w = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WJets."+category+"_down"])*pt_dependence_rescaling,2)
      uncup_z   = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZJets."+category+"_up"])*pt_dependence_rescaling,2)
      uncdown_z = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZJets."+category+"_down"])*pt_dependence_rescaling,2)
      for c in contrib:
       uncup_t.update( {mappdf[c] :round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Vtag_eff"][mappdf[c]+"."+category+"_up"])*pt_dependence_rescaling,2)} )
       uncdown_t.update({mappdf[c] : round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Vtag_eff"][mappdf[c]+"."+category+"_down"])*pt_dependence_rescaling,2)})
      if self.dib == True:
       print " ((((((( diiiiiiiiiiibbbbbbbb ))))))))"
       uncup_wz   = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WZJets."+category+"_up"])*pt_dependence_rescaling,2)
       uncdown_wz = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WZJets."+category+"_down"])*pt_dependence_rescaling,2)
       uncup_zz   = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZZJets."+category+"_up"])*pt_dependence_rescaling,2)
       uncdown_zz = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZZJets."+category+"_down"])*pt_dependence_rescaling,2)


       unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"]),'WZ': str(uncdown_wz)+"/"+ str(uncup_wz),'ZZ': str(uncdown_zz)+"/"+ str(uncup_zz)}

      else:
       unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"])}




      #unc = {'%s'%sig: str(uncdown_s)+"/"+ str(uncup_s)}
      if (category.find('VH_LPHP')  !=-1 or category.find('VV_HPLP') !=-1 ):
       print " #################   taking into account the H/V tagging anti-correlation ############## "
       #unc = {'%s'%sig: str(uncup_s)+"/"+ str(uncdown_s) }
       if self.dib == True: unc = {'%s'%sig: str(uncup_s)+"/"+ str(uncdown_s),'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"]),'WZ': str(uncup_wz)+"/"+ str(uncdown_wz),'ZZ': str(uncup_zz)+"/"+ str(uncdown_zz)}
       else: unc = {'%s'%sig: str(uncup_s)+"/"+ str(uncdown_s),'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"])}
      card.addSystematic("CMS_Vtagger_PtDependence","lnN",unc)
      
      production = "ggDY"
      signaltype = "signal"
      if category.find("VBF") !=-1:
       production = "VBF"
      if sig.find("VBF") !=-1:
       signaltype = "signalVBF"
      print " production mode ",production
      print "adding PU systematics"
      card.addSystematic("CMS_PU","lnN",{"Wjets":self.PU_unc[production]["PRbackground"],"Zjets":self.PU_unc[production]["PRbackground"],'TTJetsW':self.PU_unc[production]["PRbackground"],'TTJetsTop':self.PU_unc[production]["PRbackground"],'TTJetsNonRes':self.PU_unc[production]["PRbackground"],'TTJetsWNonResT':self.PU_unc[production]["PRbackground"],'TTJetsResWResT':self.PU_unc[production]["PRbackground"],'TTJetsTNonResT':self.PU_unc[production]["PRbackground"]})
      card.addSystematic("CMS_PU","lnN",{'%s'%sig:self.PU_unc[production][signaltype]})
      if self.dib == True: card.addSystematic("CMS_PU","lnN",{"WW":self.PU_unc[production]["PRbackground"],"ZZ":self.PU_unc[production]["PRbackground"]})
      prefiringperiods = ["2016","2017"]
      for year in prefiringperiods:
       if self.dib == True:
        card.addSystematic("CMS_L1prefiring"+year+"_"+production,"lnN",{'%s'%sig:1.01,"Wjets":1.01,"Zjets":1.01,'TTJetsW':1.01,'TTJetsTop':1.01,'TTJetsNonRes':1.01,'TTJetsWNonResT':1.01,'TTJetsResWResT':1.01,'TTJetsTNonResT':1.01,"WZ":1.01,"ZZ":1.01})
       else:
        card.addSystematic("CMS_L1prefiring"+year+"_"+production,"lnN",{'%s'%sig:1.01,"Wjets":1.01,"Zjets":1.01,'TTJetsW':1.01,'TTJetsTop':1.01,'TTJetsNonRes':1.01,'TTJetsWNonResT':1.01,'TTJetsResWResT':1.01,'TTJetsTNonResT':1.01})

      if correlate:
       if self.dib == True: card.addSystematic("CMS_lumi","lnN",{'%s'%sig:self.lumi_unc[dataset],"Wjets":self.lumi_unc[dataset],"Zjets":self.lumi_unc[dataset],'TTJetsW':self.lumi_unc[dataset],'TTJetsTop':self.lumi_unc[dataset],'TTJetsNonRes':self.lumi_unc[dataset],'TTJetsWNonResT':self.lumi_unc[dataset],'TTJetsResWResT':self.lumi_unc[dataset],'TTJetsTNonResT':self.lumi_unc[dataset],"WW":self.lumi_unc[dataset],"ZZ":self.lumi_unc[dataset]})
       else: card.addSystematic("CMS_lumi","lnN",{'%s'%sig:self.lumi_unc[dataset],"Wjets":self.lumi_unc[dataset],"Zjets":self.lumi_unc[dataset],'TTJetsW':self.lumi_unc[dataset],'TTJetsTop':self.lumi_unc[dataset],'TTJetsNonRes':self.lumi_unc[dataset],'TTJetsWNonResT':self.lumi_unc[dataset],'TTJetsResWResT':self.lumi_unc[dataset],'TTJetsTNonResT':self.lumi_unc[dataset]})
      else: 
       card.addSystematic("CMS_lumi","lnN",{'%s'%sig:self.lumi_unc[dataset]})

 def AddMultiSigSystematics(self,card,sig,dataset,category,correlate,case,resultsDir="results_Run2/",pt_dependence_rescaling=1):
  isvbf = ''
  if 'VBF' in sig: isvbf='VBF_'

  if 'VprimeWV' in sig:
   self.AddOneSigSystematics(card,'%sWprimeWZ'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sZprimeWW'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
  elif 'VprimeVHinc' in sig:
   self.AddOneSigSystematics(card,'%sWprimeWHinc'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sZprimeZHinc'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
  elif sig == 'Wprime' or sig == 'VBF_Wprime':
   self.AddOneSigSystematics(card,'%sWprimeWZ'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sWprimeWHinc'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
  elif sig == 'Zprime' or sig == 'VBF_Zprime':
   self.AddOneSigSystematics(card,'%sZprimeWW'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sZprimeZHinc'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
  elif sig == 'Vprime' or sig == 'VBF_Vprime':
   self.AddOneSigSystematics(card,'%sWprimeWZ'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sZprimeWW'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sWprimeWHinc'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sZprimeZHinc'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
  elif 'BulkGVV' in sig:
   self.AddOneSigSystematics(card,'%sBulkGWW'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sBulkGZZ'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
  elif 'RadionVV' in sig:
   self.AddOneSigSystematics(card,'%sRadionWW'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)
   self.AddOneSigSystematics(card,'%sRadionZZ'%isvbf,dataset,category,correlate,case,resultsDir,pt_dependence_rescaling)



 def AddTauTaggingSystematics(self,card,sig,p,dataset):
  print "^^^^^^^^^^^^^^^^^^^^^^^     hardcoded tau21 unc!!!!! ^^^^^^^^^^^^^^^^^^^^^^^^^"
  vtag_unc = {'VV_HPHP':{},'VV_HPLP':{},'VV_LPLP':{}}
  vtag_unc['VV_HPHP'] = {'2016':'1.232/0.792','2017':'1.269/0.763','1617':'1.269/0.763'}
  vtag_unc['VV_HPLP'] = {'2016':'0.882/1.12','2017':'0.866/1.136','1617':'0.866/1.136'}
  vtag_unc['VV_LPLP'] = {'2016':'1.063','2017':'1.043'}
  card.addSystematic("CMS_VV_JJ_tau21_eff","lnN",{'%s'%sig:vtag_unc[p][dataset],"Wjets":vtag_unc[p][dataset],"Zjets":vtag_unc[p][dataset]})


 def AddOneTaggingSystematics(self,card,signal,p,jsonfile,isVVonly=False,doFour=False,dataset="Run2",lumiweight=1.):
    contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
    mappdf = {"resT":"TTJetsTop","resW":"TTJetsW","nonresT":"TTJetsNonRes","resTnonresT":"TTJetsTNonResT","resWnonresT":"TTJetsWNonResT","resTresW":"TTJetsResWResT"}
    uncup_t = {}
    uncdown_t = {}
    with open(jsonfile[0]) as json_file_sig:
     data_sig = json.load(json_file_sig)
    with open(jsonfile[1]) as json_file_w:
     data_w = json.load(json_file_w)
    with open(jsonfile[2]) as json_file_z:
     data_z = json.load(json_file_z)
    with open(jsonfile[3]) as json_file_t:
     data_t = json.load(json_file_t)
    sig = signal
    if signal.find('Zprime')!=-1 and signal.find("ZH")!=-1: sig = "ZprimeToZh"
    if signal.find('Zprime')!=-1 and signal.find("WW")!=-1: sig = "ZprimeToWW"
    if signal.find('Wprime')!=-1 and signal.find("WH")!=-1: sig = "WprimeToWh"
    if signal.find('Wprime')!=-1 and signal.find("WZ")!=-1: sig = "WprimeToWZ"
    if signal.find('BulkGWW')!=-1 : sig = "BulkGravToWW"
    if signal.find('BulkGZZ')!=-1 : sig = "BulkGravToZZ"
    if signal.find('VBF')!=-1 : sig = "VBF_"+sig

    uncup_s   = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Htag_eff"][p+"_up"])*lumiweight,2)
    uncdown_s = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Htag_eff"][p+"_down"])*lumiweight,2)
    uncup_w   = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WJets."+p+"_up"])*lumiweight,2)
    uncdown_w = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WJets."+p+"_down"])*lumiweight,2)
    uncup_z   = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZJets."+p+"_up"])*lumiweight,2)
    uncdown_z = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZJets."+p+"_down"])*lumiweight,2)
    for c in contrib:
     uncup_t.update( {mappdf[c] :round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Htag_eff"][mappdf[c]+"."+p+"_up"])*lumiweight,2) })
     uncdown_t.update({mappdf[c] : round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Htag_eff"][mappdf[c]+"."+p+"_down"])*lumiweight,2)})
    if self.dib == True:
     print " ((((((( diiiiiiiiiiibbbbbbbb ))))))))"
     with open(jsonfile[4]) as json_file_wz:
      data_wz = json.load(json_file_wz)
     uncup_wz   = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WZJets."+p+"_up"])*lumiweight,2)
     uncdown_wz = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WZJets."+p+"_down"])*lumiweight,2)
     with open(jsonfile[5]) as json_file_zz:
      data_zz = json.load(json_file_zz)
     uncup_zz   = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZZJets."+p+"_up"])*lumiweight,2)
     uncdown_zz = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZZJets."+p+"_down"])*lumiweight,2)


     unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"]),'WZ': str(uncdown_wz)+"/"+ str(uncup_wz),'ZZ': str(uncdown_zz)+"/"+ str(uncup_zz)}

    else:
     unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"])}


    if (p.find('VV_HPHP') !=-1 or p.find('VH_HPLP') !=-1 or p.find('VV_HPLP') !=-1) and not isVVonly:
     print " #################   taking into account the H/V tagging anti-correlation ############## "
     if p.find('VV_HPHP') !=-1: ap = 'VH_HPHP'
     if p.find('VH_HPLP') !=-1: ap = 'VH_LPHP'
     if p.find('VV_HPLP') !=-1: ap = 'VH_HPLP'
     if doFour == True:
      if p.find('VV_HPLP') !=-1: ap = 'VH_LPHP'
     if p.find('VBF') !=-1 : ap = 'VBF_'+ap
     uncup_s   = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Htag_eff"][ap+"_up"])*lumiweight,2)
     uncdown_s = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Htag_eff"][ap+"_down"])*lumiweight,2)
     uncup_w   = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WJets."+ap+"_up"])*lumiweight,2)
     uncdown_w = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Htag_eff"]["WJets."+ap+"_down"])*lumiweight,2)
     uncup_z   = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZJets."+ap+"_up"])*lumiweight,2)
     uncdown_z = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Htag_eff"]["ZJets."+ap+"_down"])*lumiweight,2)
     for c in contrib:
      uncup_t.update( {mappdf[c] :round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Htag_eff"][mappdf[c]+"."+ap+"_up"])*lumiweight,2) })
      uncdown_t.update({mappdf[c] : round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Htag_eff"][mappdf[c]+"."+ap+"_down"])*lumiweight,2)})


     if self.dib == True: 
      unc = {'%s'%signal: str(uncup_s)+"/"+ str(uncdown_s) ,'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"]),'WZ': str(uncup_wz)+"/"+ str(uncdown_wz),'ZZ': str(uncup_zz)+"/"+ str(uncdown_zz)}
     else:
      unc = {'%s'%signal: str(uncup_s)+"/"+ str(uncdown_s) ,'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"])}
    if self.pseudodata=="qcdvjets": unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z)}
    print unc
    if not isVVonly: 
     card.addSystematic("CMS_VV_JJ_DeepJet_Htag_eff_"+dataset,"lnN",unc)
    
    uncup_s   = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Vtag_eff"][p+"_up"])*lumiweight,2)
    uncdown_s = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Vtag_eff"][p+"_down"])*lumiweight,2)
    uncup_w   = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WJets."+p+"_up"])*lumiweight,2)
    uncdown_w = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WJets."+p+"_down"])*lumiweight,2)
    uncup_z   = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZJets."+p+"_up"])*lumiweight,2)
    uncdown_z = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZJets."+p+"_down"])*lumiweight,2)
    for c in contrib:     
     uncup_t.update( {mappdf[c] :round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Vtag_eff"][mappdf[c]+"."+p+"_up"])*lumiweight,2)} )
     uncdown_t.update({mappdf[c] : round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Vtag_eff"][mappdf[c]+"."+p+"_down"])*lumiweight,2)})
    if self.dib == True:
     print " ((((((( diiiiiiiiiiibbbbbbbb ))))))))"
     uncup_wz   = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WZJets."+p+"_up"])*lumiweight,2)
     uncdown_wz = round(1.-(1.-data_wz["WZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["WZJets."+p+"_down"])*lumiweight,2)
     uncup_zz   = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZZJets."+p+"_up"])*lumiweight,2)
     uncdown_zz = round(1.-(1.-data_zz["ZZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]["ZZJets."+p+"_down"])*lumiweight,2)


     unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"]),'WZ': str(uncdown_wz)+"/"+ str(uncup_wz),'ZZ': str(uncdown_zz)+"/"+ str(uncup_zz)}

    else:
     unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z),"TTJetsW":str(uncdown_t["TTJetsW"])+"/"+ str(uncup_t["TTJetsW"]),"TTJetsWNonResT":str(uncdown_t["TTJetsWNonResT"])+"/"+ str(uncup_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"])}


    if (p.find('VH_LPHP')  !=-1 or p.find('VV_HPLP') !=-1 ) and not isVVonly:
     print " #################   taking into account the H/V tagging anti-correlation ############## "
     if p.find('VH_LPHP') !=-1: ap = 'VV_HPHP'
     if p.find('VV_HPLP') !=-1: ap = 'VH_HPLP'
     if doFour == True:
      if p.find('VV_HPLP') !=-1: ap = 'VH_LPHP'
     if p.find('VBF') !=-1 : ap = 'VBF_'+ap
     uncup_s   = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Vtag_eff"][ap+"_up"])*lumiweight,2)
     uncdown_s = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_Vtag_eff"][ap+"_down"])*lumiweight,2)
     uncup_w   = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Vtag_eff"]['WJets.'+ap+"_up"])*lumiweight,2)
     uncdown_w = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_Vtag_eff"]['WJets.'+ap+"_down"])*lumiweight,2)
     uncup_z   = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]['ZJets.'+ap+"_up"])*lumiweight,2)
     uncdown_z = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_Vtag_eff"]['ZJets.'+ap+"_down"])*lumiweight,2)
     for c in contrib:     
      uncup_t.update( {mappdf[c] :round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Vtag_eff"][mappdf[c]+"."+ap+"_up"])*lumiweight,2)} )
      uncdown_t.update({mappdf[c] : round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_Vtag_eff"][mappdf[c]+"."+ap+"_down"])*lumiweight,2)})
     if self.dib == True: 
      unc = {'%s'%signal: str(uncup_s)+"/"+ str(uncdown_s) ,'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"]),'WZ': str(uncup_wz)+"/"+ str(uncdown_wz),'ZZ': str(uncup_zz)+"/"+ str(uncdown_zz)}
     else:
      unc = {'%s'%signal: str(uncup_s)+"/"+ str(uncdown_s) ,'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"])}


    if self.pseudodata=="qcdvjets": unc = {'%s'%signal: str(uncdown_s)+"/"+ str(uncup_s) ,'Wjets': str(uncdown_w)+"/"+ str(uncup_w),'Zjets': str(uncdown_z)+"/"+ str(uncup_z)}
    if p.find('VV_HPLP')!=-1 and isVVonly==True:
     print " !!!!!!!! anticorrelate in VV only !!!!!!!!!!!!"
     unc = {'%s'%signal: str(uncup_s)+"/"+ str(uncdown_s) ,'Wjets': str(uncup_w)+"/"+ str(uncdown_w),'Zjets': str(uncup_z)+"/"+ str(uncdown_z),"TTJetsW":str(uncup_t["TTJetsW"])+"/"+ str(uncdown_t["TTJetsW"]),"TTJetsWNonResT":str(uncup_t["TTJetsWNonResT"])+"/"+ str(uncdown_t["TTJetsWNonResT"]),"TTJetsResWResT": str(uncup_t["TTJetsResWResT"])+"/"+ str(uncdown_t["TTJetsResWResT"])}
    print " VTAG UNC ",unc
    card.addSystematic("CMS_VV_JJ_DeepJet_Vtag_eff_"+dataset,"lnN",unc)
    
    uncup_s   = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_TOPtag_mistag"][p+"_up"])*lumiweight,2)
    uncdown_s = round(1.-(1.-data_sig[signal+"_CMS_VV_JJ_DeepJet_TOPtag_mistag"][p+"_down"])*lumiweight,2)
    uncup_w   = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_TOPtag_mistag"]["WJets."+p+"_up"])*lumiweight,2)
    uncdown_w = round(1.-(1.-data_w["WJets_CMS_VV_JJ_DeepJet_TOPtag_mistag"]["WJets."+p+"_down"])*lumiweight,2)
    uncup_z   = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_TOPtag_mistag"]["ZJets."+p+"_up"])*lumiweight,2)
    uncdown_z = round(1.-(1.-data_z["ZJets_CMS_VV_JJ_DeepJet_TOPtag_mistag"]["ZJets."+p+"_down"])*lumiweight,2)
    for c in contrib:
     uncup_t.update( {mappdf[c] :round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_TOPtag_mistag"][mappdf[c]+"."+p+"_up"])*lumiweight,2)} )
     uncdown_t.update({mappdf[c] : round(1.-(1.-data_t["TTJets_CMS_VV_JJ_DeepJet_TOPtag_mistag"][mappdf[c]+"."+p+"_down"])*lumiweight,2)})
    unc = {"TTJetsTop" : str(uncdown_t["TTJetsTop"])+"/"+ str(uncup_t["TTJetsTop"]), "TTJetsTNonResT":str(uncdown_t["TTJetsTNonResT"])+"/"+ str(uncup_t["TTJetsTNonResT"]),"TTJetsResWResT":str(uncdown_t["TTJetsResWResT"])+"/"+ str(uncup_t["TTJetsResWResT"]) }
    if not isVVonly: card.addSystematic("CMS_VV_JJ_DeepJet_TOPtag_mistag_"+dataset,"lnN",unc)

 def AddMultiTaggingSystematics(self,card,sig,p,jsonfile,isVVonly=False,doFour=False,dataset="Run2",lumiweight=1.):
  isvbf = ''
  if 'VBF' in sig: isvbf='VBF_'

  if 'VprimeWV' in sig:
   newjson = jsonfile[0].replace('VprimeWV','WprimeWZ')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sWprimeWZ'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('WprimeWZ','ZprimeWW')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sZprimeWW'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
  elif 'VprimeVHinc' in sig:
   newjson = jsonfile[0].replace('VprimeVHinc','WprimeWHinc')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sWprimeWHinc'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('WprimeWH','ZprimeZH')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sZprimeZHinc'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
  elif sig == 'Wprime' or sig == 'VBF_Wprime':
   newjson = jsonfile[0].replace('Wprime','WprimeWZ')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sWprimeWZ'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('WprimeWZ','WprimeWHinc')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sWprimeWHinc'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
  elif sig == 'Zprime' or sig == 'VBF_Zprime':
   newjson = jsonfile[0].replace('Zprime','ZprimeWW')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sZprimeWW'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('ZprimeWW','ZprimeZHinc')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sZprimeZHinc'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
  elif sig == 'Vprime' or sig == 'VBF_Vprime':
   newjson = jsonfile[0].replace('Vprime','WprimeWZ')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sWprimeWZ'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('WprimeWZ','ZprimeWW')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sZprimeWW'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('ZprimeWW','WprimeWHinc')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sWprimeWHinc'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('WprimeWHinc','ZprimeZHinc')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sZprimeZHinc'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
  elif 'BulkGVV' in sig:
   newjson = jsonfile[0].replace('BulkGVV','BulkGWW')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sBulkGWW'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('BulkGWW','BulkGZZ')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sBulkGZZ'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
  elif 'RadionVV' in sig:
   newjson = jsonfile[0].replace('RadionVV','RadionWW')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sRadionWW'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)
   newjson = jsonfile[0].replace('RadionWW','RadionZZ')
   jsonfile[0] = newjson
   self.AddOneTaggingSystematics(card,'%sRadionZZ'%isvbf,p,jsonfile,isVVonly,doFour,dataset,lumiweight)

 def AddResBackgroundSystematics(self,card,category,vbf,corrvbf,extra_uncertainty=[]):
       incat = category
       if not corrvbf:
        print " V+jets has 1 norm syst per category! "
        card.addSystematic("CMS_VV_JJ_Wjets_norm_"+category,"lnN",{'Wjets':1.50})
        card.addSystematic("CMS_VV_JJ_Zjets_norm_"+category,"lnN",{'Zjets':1.50})
        #print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
        #print "&&&  ATTENTION V+Jets norm uncertainty raised to 2. (100%)    &&&"
        #print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
        #card.addSystematic("CMS_VV_JJ_Wjets_norm_"+category,"lnN",{'Wjets':2.0})
        #card.addSystematic("CMS_VV_JJ_Zjets_norm_"+category,"lnN",{'Zjets':2.0})
       else:
        print " corr VBF for V+jets!!! "
        if category.find("VBF") != -1:
         card.addSystematic("CMS_VV_JJ_Wjets_norm_VBF","lnN",{'Wjets':1.50})
         card.addSystematic("CMS_VV_JJ_Zjets_norm_VBF","lnN",{'Zjets':1.50})
        if category.find("VBF") != -1 and not vbf: category = category.replace("VBF_","")
        card.addSystematic("CMS_VV_JJ_Wjets_norm_"+category,"lnN",{'Wjets':1.50})
        card.addSystematic("CMS_VV_JJ_Zjets_norm_"+category,"lnN",{'Zjets':1.50})

       if category.find("VBF") != -1 and not vbf: category = category.replace("VBF_","")
       if self.fitvjetsmjj == True:
        card.addSystematic(extra_uncertainty[0],"param",[0.0,extra_uncertainty[1]])
        card.addSystematic(extra_uncertainty[2],"param",[0.0,extra_uncertainty[3]])
       elif self.kfactors == True :
        print "<<<<<<<<         <<<<<<<     using kfactors!!!    >>>>>>>   >>>>>>>>>>>>"
        card.addSystematic("CMS_VV_JJ_Wjets_Kfactors","param",[0,1.]) #0.333
        card.addSystematic("CMS_VV_JJ_Zjets_Kfactors","param",[0,1.]) #0.333
       else:
        
        card.addSystematic("CMS_VV_JJ_Wjets_PTZ_"+category,"param",[0,1.]) #0.333
        card.addSystematic("CMS_VV_JJ_Wjets_OPTZ_"+category,"param",[0,1.]) #0.333
        card.addSystematic("CMS_VV_JJ_Zjets_PTZ_"+category,"param",[0,1.]) #0.333
        card.addSystematic("CMS_VV_JJ_Zjets_OPTZ_"+category,"param",[0,1.]) #0.333
        '''
        print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
        print "&&&  ATTENTION V+Jets shape uncertainty raised to 2 .          &&&"
        print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
        card.addSystematic("CMS_VV_JJ_Wjets_PTZ_"+category,"param",[0,2.]) #0.333
        card.addSystematic("CMS_VV_JJ_Wjets_OPTZ_"+category,"param",[0,2.]) #0.333
        card.addSystematic("CMS_VV_JJ_Zjets_PTZ_"+category,"param",[0,2.]) #0.333
        card.addSystematic("CMS_VV_JJ_Zjets_OPTZ_"+category,"param",[0,2.]) #0.333
        '''
       
       if self.dib == True:
        category = incat
        print " ******** adding DIBOSN syst ************ "
        if not corrvbf:
         card.addSystematic("CMS_VV_JJ_WZ_norm_"+category,"lnN",{'WZ':1.50})
         card.addSystematic("CMS_VV_JJ_ZZ_norm_"+category,"lnN",{'ZZ':1.50})
        else:
         print " corr VBF for V+jets!!! "
         if category.find("VBF") != -1:
          card.addSystematic("CMS_VV_JJ_WZ_norm_VBF","lnN",{'WZ':1.50})
          card.addSystematic("CMS_VV_JJ_ZZ_norm_VBF","lnN",{'ZZ':1.50})
         if category.find("VBF") != -1 and not vbf: category = category.replace("VBF_","")
         card.addSystematic("CMS_VV_JJ_WZ_norm_"+category,"lnN",{'WZ':1.50})
         card.addSystematic("CMS_VV_JJ_ZZ_norm_"+category,"lnN",{'ZZ':1.50})

        if category.find("VBF") != -1 and not vbf: category = category.replace("VBF_","")
        card.addSystematic("CMS_VV_JJ_WZ_PTZ_"+category,"param",[0,1.]) #0.333
        card.addSystematic("CMS_VV_JJ_WZ_OPTZ_"+category,"param",[0,1.]) #0.333
        card.addSystematic("CMS_VV_JJ_ZZ_PTZ_"+category,"param",[0,1.]) #0.333
        card.addSystematic("CMS_VV_JJ_ZZ_OPTZ_"+category,"param",[0,1.]) #0.333
       

 def AddNonResBackgroundSystematics(self,card,category,vbf,corrvbf):
      print " nonres syst for ",category
      normunc=1.5
      if not corrvbf:
       print " QCD has 1 norm syst per category! "
       card.addSystematic("CMS_VV_JJ_nonRes_norm_"+category,"lnN",{'nonRes':normunc})
      else:
       print " corr VBF for V+jets!!! "
       if category.find("VBF") != -1:
        card.addSystematic("CMS_VV_JJ_nonRes_norm_VBF","lnN",{'nonRes':normunc})
       if category.find("VBF") != -1 and not vbf: category = category.replace("VBF_","")
       card.addSystematic("CMS_VV_JJ_nonRes_norm_"+category,"lnN",{'nonRes':normunc})

      if category.find("VBF") != -1 and not vbf: category = category.replace("VBF_","")
      print " now ",category
      shapeunc=2.
      card.addSystematic("CMS_VV_JJ_nonRes_PT_"+category,"param",[0.0,shapeunc])
      card.addSystematic("CMS_VV_JJ_nonRes_OPT_"+category,"param",[0.0,shapeunc])
      card.addSystematic("CMS_VV_JJ_nonRes_TurnOn_"+category,"param",[1.,shapeunc])
      card.addSystematic('CMS_VV_JJ_nonRes_altshape2_'+category,"param",[0.0,shapeunc])
      card.addSystematic('CMS_VV_JJ_nonRes_altshape_'+category,"param",[0.0,shapeunc])

      #card.addSystematic("CMS_VV_JJ_nonRes_OPT3_"+category,"param",[1.,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_PT3_"+category,"param",[1.,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_OPT6_"+category,"param",[0.0,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_PT6_"+category,"param",[0.0,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_OPT5_"+category,"param",[0.0,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_PT5_"+category,"param",[0.0,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_OPT4_"+category,"param",[0.0,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_PT4_"+category,"param",[0.0,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_OPT2_"+category,"param",[0.0,shapeunc])
      #card.addSystematic("CMS_VV_JJ_nonRes_PT2_"+category,"param",[0.0,shapeunc])
