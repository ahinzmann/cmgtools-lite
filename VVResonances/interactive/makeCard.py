from tools.DatacardTools import *
import sys,os
import ROOT
import json
ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit")
from CMGTools.VVResonances.statistics.DataCardMaker import DataCardMaker
from optparse import OptionParser
import cuts

# produce workspace with ttbar only
# python makeCard.py -p "2016" --signal "BulkGWW" -c "VH_NPHP_control_region,VH_HPNP_control_region" --outlabel "_ttbar" --pseudodata "ttbar"
# produce the preparatory workspace to make the pseudodata with all workspace
# python makeCard.py -p "2016" --signal "BulkGWW" -c "VH_HPNP_control_region" --outlabel "_PrepPseudo" --pseudodata "PrepPseudo"
# produce the workspace with all backgrounds and pseudodata
# python makeCard.py -p "2016" --signal "BulkGWW" -c "VH_HPNP_control_region,VH_NPHP_control_region" --outlabel "_pseudodata" --pseudodata "True"
# produce the workspace with all backgrounds and data
# python makeCard.py -p "2016" --signal "BulkGWW" -c "VH_NPHP_control_region,VH_HPNP_control_region" --outlabel "_data" --pseudodata "False"

parser = OptionParser()
parser.add_option("-p","--period",dest="period",default="2016,2017,2018",help="run period")
parser.add_option("--pseudodata",dest="pseudodata",help="make cards with real data(False option) or differen pseudodata sets: Vjets, ZprimeZH etc",default='')
parser.add_option("--signal",dest="signal",default="BulkGWW,BulkGZZ,ZprimeWW,ZprimeZH,WprimeWH,WprimeWZ",help="which signal do you want to run? options are BulkGWW, BulkGZZ, WprimeWZ, ZprimeWW, ZprimeZH")
parser.add_option("--outlabel",dest="outlabel",help="lebel for output workspaces for example sigonly_M4500",default='')
parser.add_option("-c","--category",dest="category",default="VV_HPLP,VV_HPHP,VH_HPLP,VH_HPHP,VH_LPHP",help="choose category, use a specific category, ggDY, VBF or all")
parser.add_option("-j","--jsonname",dest="jsonname",help="write the name of the output json file, the category will be automatically inserted",default='ttbarNorm')
parser.add_option("--fitvjetsmjj",dest="fitvjetsmjj",default=False,action="store_true",help="True makes fits for mjj of vjets, False uses hists")
parser.add_option("--fitTTmjj",dest="fitTTmjj",default=False,action="store_true",help="True makes fits for mjj of ttbar, False uses hists")
parser.add_option("--combo",dest="combo",default=True,help="If True inputs from the 3 years combined will be used")
parser.add_option("--vbf",dest="vbf",help="do you want to keep VBF uncertainties separated?",action='store_true')
parser.add_option("-m","--merge",dest="merge",help="set to False if you do not want to combine datacards",default=True)
parser.add_option("-i","--inputdir",dest="inputdir",help="input direcory of all the files",default='results_Run2')
parser.add_option("--vv",dest="vv",help="make VV only (no VHveto) ?",action='store_true')
parser.add_option("--tau",dest="tau",help="tau21 ?",action='store_true',default=False)
parser.add_option("--four",dest="four",help="is VH HPLP merged in VV HPLP?",action='store_true')
parser.add_option("--kfactors",dest="kfactors",help="use combination of kfactors as V+Jets MVV alternative shapes?",action='store_true',default=False)
parser.add_option("--rescale",dest="rescale",help="use the rescale option if you want to rescale the QCD after having performed a preliminary postfit.",action='store_true')
parser.add_option("--corrvbf",dest="corrvbf",help="correlate VBF cat with non VBF cat + 1 nuisance for all VBF for QCD and V+jets",action='store_true',default=False)
parser.add_option("--peryear",dest="peryear",help="divide tagger eff per year",action='store_false',default=True) #this may look counter intuitive, but it is modified to have the chosen option as default for safety
parser.add_option("--dib",dest="dib",help="add diboson bkg?",action='store_true',default=False)
(options,args) = parser.parse_args()



cmd='combineCards.py '

#specify how to correlate jes & jer norm uncertainties
# 1 = fully correlated among years, 2 = fully uncerrelated among years, 3 = partial correlation among years (do as in CASE 1 but take half effect as fully correlated and half effect as fully uncorrelated) (but NB json case2 = 2016 unc, case3 = 2017, case4 = 2018)
# NB: only case 1 is fully implemented, case 0 removes this unc.
case=1
#print " **************************** jer/jes disabled "

#### to create the preparatory WS for pseudodata with Vjets: pseudodata = "" & doVjets=True 
pseudodata = options.pseudodata
if pseudodata == "ttbar": case=0
outlabel = options.outlabel


purities= options.category.split(",")
if options.category == "all": purities = ["VV_HPLP","VV_HPHP","VH_HPLP","VH_HPHP","VH_LPHP","VBF_VV_HPLP","VBF_VV_HPHP","VBF_VH_HPLP","VBF_VH_HPHP","VBF_VH_LPHP"]
if options.category == "VBF": purities = ["VBF_VV_HPLP","VBF_VV_HPHP","VBF_VH_HPLP","VBF_VH_HPHP","VBF_VH_LPHP"]
if options.category == "ggDY": purities = ["VV_HPLP","VV_HPHP","VH_HPLP","VH_HPHP","VH_LPHP"]

signals = options.signal.split(",")
print "signals ",signals
doVjets= True
rescale = False
sf_qcd=1.8
sf_Wjets=1.
sf_Zjets=1.

print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
print "% sf_qcd= "+str(sf_qcd)+" - sf_Wjets= "+str(sf_Wjets)+" - sf_Zjets= "+str(sf_Zjets)
print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"

if outlabel.find("sigonly")!=-1 or outlabel.find("qcdonly")!=-1: doVjets = False
if outlabel.find("sigonly")!=-1 or outlabel.find("Vjetsonly")!=-1: sf_qcd = 0.00001


# vtag uncertainty is added through the migrationunc.json file 
# all other uncertainties and SF from one place: defined in init_VV_VH.json imported via the class defined in cuts.py
ctx = cuts.cuts("init_VV_VH.json",options.period,"dijetbins_random")

lumi = ctx.lumi
lumi_unc = ctx.lumi_unc
if rescale == True: sf_qcd=lumi["Run2"]/lumi[options.period]

scales = [1.,1.]
scalesHiggs = [1.,1.]
if pseudodata == "False":
  scales = [ctx.W_HPmassscale,ctx.W_LPmassscale]
  scalesHiggs = [ctx.H_HPmassscale,ctx.H_LPmassscale]

vtag_pt_dependence = ctx.tagger_pt_dependence
PU_unc = ctx.PU_uncertainties
JES_unc = ctx.JES_uncertainties
JER_unc = ctx.JER_uncertainties
PDF_unc = ctx.PDF_uncertainties


datasets= options.period.split(",")
resultsDir = {year:'results_'+year for year in datasets}

if len(datasets) == 1 : lumitot=lumi[options.period]
if len(datasets) == 3 and options.combo == True:
  datasets = []
  datasets.append("Run2")
  resultsDir.update({"Run2" : options.inputdir})
  lumitot=lumi["Run2"]
if len(datasets) == 2 and options.combo == True:
  datasets = []
  datasets.append("1617")
  resultsDir.update({"1617" : options.inputdir})
  lumitot=lumi["1617"]
print "datasets ",datasets
print "result dir ",resultsDir

doCorrelation = True 
Tools = DatacardTools(scales,scalesHiggs,vtag_pt_dependence,PU_unc,JES_unc,JER_unc,lumi_unc,PDF_unc,sf_qcd,pseudodata,outlabel,doCorrelation,options.fitvjetsmjj,options.kfactors,sf_Wjets,sf_Zjets,options.dib)


for sig in signals:

  cmd ="combineCards.py"
  for dataset in datasets:
    print dataset
    cmd_combo="combineCards.py"
    for p in purities:
      shape_purity = p
      if p.find("VBF") !=-1 : shape_purity= p.replace("VBF_","")
      print " purity "+p+" shape to use "+shape_purity
      ncontrib = 0
      print dataset," has lumi ",lumi[dataset]
      print type(lumi[dataset])
      
      cat='_'.join(['JJ',sig,p,'13TeV_'+dataset])
      card=DataCardMaker('',p,'13TeV_'+dataset,lumi[dataset],'JJ',cat)
      cmd=cmd+" "+cat.replace('_%s'%sig,'')+'=datacard_'+cat+'.txt '
      cmd_combo=cmd_combo+" "+cat.replace('_%s'%sig,'')+'=datacard_'+cat+'.txt '
      cardName='datacard_'+cat+'.txt '
      workspaceName='workspace_'+cat+outlabel+'.root'
      oneSignal = True
      if 'WW' in sig or 'ZZ' in sig or 'WH' in sig or 'ZH' in sig or 'WZ' in sig:
        Tools.AddOneSignal(card,dataset,p,sig,resultsDir[dataset],ncontrib)
      else:
        oneSignal = False
        Tools.AddMultipleSignals(card,dataset,p,sig,resultsDir[dataset],ncontrib)
      print " oneSignal ",oneSignal
      ncontrib+=1      
      print "##########################       including W/Z jets in datacard      ######################"
      rootFileNorm = resultsDir[dataset]+'/JJ_%s_WJets_%s.root'%(dataset,p)
      if options.fitvjetsmjj == True:
        rootFileMVV =  resultsDir[dataset]+'/JJ_%s_WJets_MVV_NP_Wjets'%dataset+'.json'
        Tools.AddWResBackground(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib,["CMS_VV_JJ_WJets_slope",0.5])
      else:
        rootFileMVV = resultsDir[dataset]+'/JJ_%s_WJets_MVV_'%dataset+shape_purity+'.root'
        Tools.AddWResBackground(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib)
      ncontrib+=1
      
      rootFileNorm = resultsDir[dataset]+"/JJ_%s_ZJets_%s.root"%(dataset,p)
      if options.fitvjetsmjj == True:
        rootFileMVV =  resultsDir[dataset]+'/JJ_%s_ZJets_MVV_NP_Zjets'%dataset+'.json'
        Tools.AddZResBackground(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib,["CMS_VV_JJ_ZJets_slope",0.5])
      else:
        rootFileMVV = resultsDir[dataset]+'/JJ_%s_ZJets_MVV_'%dataset+shape_purity+'.root'
        Tools.AddZResBackground(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib)
      ncontrib+=1

      if pseudodata !="qcdvjets":
        print "##########################       including tt+jets in datacard      ######################"
        contrib =["resT","resW","nonresT","resTnonresT","resWnonresT","resTresW"]
        rootFileMVV = {ttcon:resultsDir[dataset]+'/JJ_'+dataset+'_TTJets'+ttcon+'_MVV_'+shape_purity+'.root' for ttcon in contrib}
        rootFileNorm = {ttcon:resultsDir[dataset]+'/JJ_'+dataset+'_TTJets'+ttcon+'_'+p+'.root' for ttcon in contrib}
        jsonfileNorm = resultsDir[dataset]+'/'+options.jsonname+'_'+dataset+'_'+p+'.json'
        if options.fitTTmjj == True:
          print "load fits"
          Tools.AddTTBackground3(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib,["CMS_VV_JJ_TTJets_slope",0.5],jsonfileNorm)
        else:
          print "load templates"
          Tools.AddTTBackground4(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib,jsonfileNorm)
          ncontrib+=6
      else:
        print "########^^^^^^^^^^^^^^ NOT ADDING TTBAR!!!!! ^^^^^^^^^^^^^########################"

      if options.dib == True:
        print "##########################       including WZ and ZZ in datacard      ######################"
        rootFileNorm = resultsDir[dataset]+'/JJ_%s_WZJets_%s.root'%(dataset,p)
        rootFileMVV = resultsDir[dataset]+'/JJ_%s_WZ_MVV_'%dataset+'NP.root'
        Tools.AddWZResBackground(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib)
        ncontrib+=1

        rootFileNorm = resultsDir[dataset]+"/JJ_%s_ZZJets_%s.root"%(dataset,p)
        rootFileMVV = resultsDir[dataset]+'/JJ_%s_ZZ_MVV_'%dataset+'NP.root'
        Tools.AddZZResBackground(card,dataset,shape_purity,rootFileMVV,rootFileNorm,resultsDir[dataset],ncontrib)
        ncontrib+=1


      print "##########################       including QCD in datacard      ######################"
      rootFile3DPDF = resultsDir[dataset]+"/save_new_shapes_{year}_pythia_{purity}_3D.root".format(year=dataset,purity=shape_purity)
      print "rootFile3DPDF ",rootFile3DPDF
      rootFileNorm = resultsDir[dataset]+"/JJ_%s_nonRes_"%dataset+p+".root"
      print "rootFileNorm ",rootFileNorm

      Tools.AddNonResBackground(card,dataset,shape_purity,rootFile3DPDF,rootFileNorm,ncontrib,options.rescale,options.inputdir)
      print "##########################       QCD added in datacard      ######################"



      print " including data or pseudodata in datacard"
      if pseudodata=="PrepPseudo":
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_nonRes_3D_NP.root" #use this only to prepare workspace for making pseudo data with vjets
        histName="histo"
        scaleData=lumi[dataset]
      elif pseudodata=="True":
        print "Using pseudodata with all backgrounds (QCD, V+jets and tt+jets)"
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_PDALL_"+p+".root"
        histName="data"
        scaleData=1.0
      elif pseudodata=="ttjets":
        print "Using pseudodata with only tt+jets backgrounds"
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_TTJets_"+p+".root"
        histName="data_obs"
        scaleData=1.0
      elif pseudodata=="noqcd":
        print "Using pseudodata with only tt+jets backgrounds and no qcd"
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_PDnoQCD_"+p+".root"
        histName="data"
        scaleData=1.0
      elif pseudodata=="qcdvjets":
        print "Using pseudodata with only qcd and V+jets backgrounds"
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_PDVjets_"+p+".root"
        histName="data"
        scaleData=1.0
      elif pseudodata=="ttbar":
        print "Using pseudodata with only tt backgrounds"
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_PDTT_"+p+".root"
        histName="data"
        scaleData=1.0
      elif pseudodata==sig:
       rootFileData = resultsDir[dataset]+"/pseudodata_sigOnly_"+dataset+"_"+sig+"_"+p+"_"+"M"+outlabel.split("_M")[1]+".root"
       histName="data_obs" 
       scaleData=1.0
      elif pseudodata=="dib":
        print "Using pseudodata with only tt backgrounds"
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_PDDIB_"+p+".root"
        histName="data"
        scaleData=1.0
      elif pseudodata=="False":
        rootFileData = resultsDir[dataset]+"/JJ_"+dataset+"_data_"+p+".root"
        if dataset == "Run2" or dataset == "1617" : rootFileData = resultsDir[dataset]+"/JJ_"+p+".root"
        histName="data"
        scaleData=1.0


      Tools.AddData(card,rootFileData,histName,scaleData)

      print "##########################       data/pseudodata added in datacard      ######################"  
      correlateyields=1
      pt_dependence_rescaling = 1.5
      if oneSignal == True:
        Tools.AddOneSigSystematics(card,sig,dataset,p,correlateyields,str(case),resultsDir[dataset],pt_dependence_rescaling)
      else:
        Tools.AddMultiSigSystematics(card,sig,dataset,p,correlateyields,str(case),resultsDir[dataset],pt_dependence_rescaling)
      if options.fitvjetsmjj == True:
        Tools.AddResBackgroundSystematics(card,p,options.vbf,options.corrvbf,["CMS_VV_JJ_WJets_slope",0.2,"CMS_VV_JJ_ZJets_slope",0.2])
      else:
        Tools.AddResBackgroundSystematics(card,p,options.vbf,options.corrvbf)
      Tools.AddNonResBackgroundSystematics(card,p,options.vbf,options.corrvbf)
      if options.tau==False and options.peryear==False:
        print " 1 tagger eff per full Run2 "
        if options.dib == True: Tools.AddTaggingSystematics(card,sig,p,[resultsDir[dataset]+'/migrationunc_'+sig+'_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_WJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_ZJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_TTJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_WZJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_ZZJets_'+dataset+'.json'],options.vv,options.four,dataset)
        else: Tools.AddTaggingSystematics(card,sig,p,[resultsDir[dataset]+'/migrationunc_'+sig+'_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_WJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_ZJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_TTJets_'+dataset+'.json'],options.vv,options.four,dataset)
      elif options.peryear == True:
        years= options.period.split(",")
        for year in years:
          print " tagging eff per year!! "
          if oneSignal == True:
            if options.dib == True: Tools.AddOneTaggingSystematics(card,sig,p,[resultsDir[dataset]+'/migrationunc_'+sig+'_'+year+'.json',resultsDir[dataset]+'/migrationunc_WJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_ZJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_TTJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_WZJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_ZZJets_'+dataset+'.json'],options.vv,options.four,year,lumi[year]/lumitot)
            else: Tools.AddOneTaggingSystematics(card,sig,p,[resultsDir[dataset]+'/migrationunc_'+sig+'_'+year+'.json',resultsDir[dataset]+'/migrationunc_WJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_ZJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_TTJets_'+year+'.json'],options.vv,options.four,year,lumi[year]/lumitot)
          else:
            if options.dib == True: Tools.AddMultiTaggingSystematics(card,sig,p,[resultsDir[dataset]+'/migrationunc_'+sig+'_'+year+'.json',resultsDir[dataset]+'/migrationunc_WJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_ZJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_TTJets_'+year+'.json'],options.vv,options.four,year,lumi[year]/lumitot)
            else: Tools.AddMultiTaggingSystematics(card,sig,p,[resultsDir[dataset]+'/migrationunc_'+sig+'_'+year+'.json',resultsDir[dataset]+'/migrationunc_WJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_ZJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_TTJets_'+year+'.json',resultsDir[dataset]+'/migrationunc_WZJets_'+dataset+'.json',resultsDir[dataset]+'/migrationunc_ZZJets_'+dataset+'.json'],options.vv,options.four,year,lumi[year]/lumitot)
      else:
        print "!!!!!!!!@@@@@@@@                    using tau21!!!    @@@@@@@@@@@@@@@@@@@@@@"
        Tools.AddTauTaggingSystematics(card,sig,p,dataset)
      if pseudodata!="qcdvjets":
        if options.fitTTmjj == True:
          print "load fits syst"
          Tools.AddTTSystematics4(card,["CMS_VV_JJ_TTJets_slope",0.05],dataset,p)
        else:
          print "load templates syst"
          Tools.AddTTSystematics5(card,p,options.vbf)
      else:
        print "tt syst not added"
      print "##########################       systematics added in datacard      ######################"  



        
      card.makeCard()
      t2wcmd = "text2workspace.py %s -o %s"%(cardName,workspaceName)
      print t2wcmd
      os.system(t2wcmd)
    del card

    print "#####################################"

    #make combined 
    if len(purities)>1 and options.merge == True:
      print "#######     going to combine purity categories: ",purities    
      combo_card = cardName.replace("VV_HPHP","").replace("VV_HPLP","").replace("VV_LPLP","").replace("VH_HPHP","").replace("VH_HPLP","").replace("VH_LPHP","").replace("VH_HPNP_control_region","").replace("VH_NPHP_control_region","").replace("__","_VVVH_")
      combo_workspace = workspaceName.replace("VV_HPHP","").replace("VV_HPLP","").replace("VV_LPLP","").replace("VH_HPHP","").replace("VH_HPLP","").replace("VH_LPHP","").replace("VH_HPNP_control_region","").replace("VH_NPHP_control_region","").replace("__","_VVVH_")
      os.system('rm %s'%combo_card)
      cmd_combo+=' >> %s'%combo_card
      print cmd_combo
      os.system(cmd_combo)
      t2wcmd = "text2workspace.py %s -o %s"%(combo_card,combo_workspace)
      print t2wcmd
      os.system(t2wcmd)
      print "#####################################"

  if len(datasets)>1:   
    #make combine 2016+2017 card
    print "more than one year, making combined cards"
    combo_card = 'datacard_'+cat.replace("_HPHP","").replace("_HPLP","").replace("_LPLP","").replace('_2016','').replace('_2017','')+'.txt'
    combo_workspace = 'workspace_'+cat.replace("_HPHP","").replace("_HPLP","").replace("_LPLP","").replace('_2016','').replace('_2017','')+'.root'
    os.system('rm %s'%combo_card)
    cmd+=' >> %s'%combo_card
    print cmd
    os.system(cmd)
    t2wcmd = "text2workspace.py %s -o %s"%(combo_card,combo_workspace)
    print t2wcmd
    os.system(t2wcmd)

    


