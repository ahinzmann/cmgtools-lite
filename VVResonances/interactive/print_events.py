import os,sys,json,ROOT
from functions import *
from optparse import OptionParser
import cuts
import argparse

c = "VV_HPHP"
widerMVV=True
jsonfile="init_VV_VH.json"
ctx  = cuts.cuts(jsonfile,"2016,2017,2018","randomdijetbins",widerMVV)

dataTemplate="JetHT"

dirs=["2016/","2017/","2018/"]
outputvariables= {}
yeartag = {"2016/":"16","2017/":"17","2018/":"18"}
jsonfile="excess_kinematic_new.json"

mjjCut='(jj_LV_mass>2500.&&jj_LV_mass< 3000.)'
mjet1Cut='(jj_l1_softDrop_mass>65.&&jj_l1_softDrop_mass<105.)'
mjet2Cut='(jj_l2_softDrop_mass>65.&&jj_l2_softDrop_mass<105.)'

if 'VBF' in c: cut='*'.join([ctx.cuts['common_VBF'],ctx.cuts[c.replace('VBF_','')],ctx.cuts['acceptance'],mjjCut,mjet1Cut,mjet2Cut])
else:cut='*'.join([ctx.cuts['common_VV'],ctx.cuts[c],ctx.cuts['acceptance'],mjjCut,mjet1Cut,mjet2Cut])
print cut
#cut ="1"
for directory in dirs:
    print directory
    year = yeartag[directory]
    print year
    for filename in os.listdir(directory):
        if filename.find(".")==-1:
            #print "in "+str(filename)+"the separator . was not found. -> continue!"
            continue
        if filename.find(dataTemplate)!=-1 and filename.find("root") !=-1:
            outputvariables[filename]={}
            root_file = directory+'/'+filename
            print root_file
            rf = ROOT.TFile.Open(root_file,"READ")
            tree = rf.Get('AnalysisTree')
            reader = ROOT.TTreeReader(tree)
            event = ROOT.TTreeReaderValue('Int_t')(reader,'evt')
            tree.Draw(">>+elist1",cut,"goff")     
            evlist = ROOT.gDirectory.Get("elist1")
            print evlist
            print "size ",evlist.GetSize()
            evlist.Print()
            print " entries ",evlist.GetN()
            if evlist.GetN()>0:
                i = 0
                for i in range(evlist.GetN()):
                    outputvariables[filename][i]={}
                    print i
                    entry =  evlist.GetEntry(i)
                    reader.SetEntry(entry)
                    print entry, reader
                    #print "reader.evt ",reader.evt
                    print event.Get()[0]
                    chosenevent=event.Get()[0]
                    outputvariables[filename][i]['evt']= chosenevent
                    print " chosen event ",chosenevent, outputvariables[filename][i]['evt']
                    tree.Draw("jj_LV_mass:lumi:run","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    print " jj_LV_mass ",tree.GetV1()[0]
                    outputvariables[filename][i]['jj_LV_mass']=tree.GetV1()[0]
                    print " jj_LV_mass in dict ",outputvariables[filename][i]['jj_LV_mass']
                    print " lumi ",tree.GetV2()[0]
                    outputvariables[filename][i]['lumi']=tree.GetV2()[0]
                    print " run ",tree.GetV3()[0]
                    outputvariables[filename][i]['run']=tree.GetV3()[0]
                    tree.Draw("jj_l1_pt:jj_l2_pt:jj_l1_eta:jj_l2_eta","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['jj_l1_pt']=tree.GetV1()[0]
                    outputvariables[filename][i]['jj_l2_pt']=tree.GetV2()[0]
                    outputvariables[filename][i]['jj_l1_eta']=tree.GetV3()[0]
                    outputvariables[filename][i]['jj_l2_eta']=tree.GetV4()[0]
                    tree.Draw("jj_l1_softDrop_nSubJets:jj_l2_softDrop_nSubJets","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['jj_l1_softDrop_nSubJets']=tree.GetV1()[0]
                    outputvariables[filename][i]['jj_l2_softDrop_nSubJets']=tree.GetV2()[0]
                    tree.Draw("jj_l1_softDrop_mass:jj_l2_softDrop_mass:2*TMath::Log(jj_l1_softDrop_mass/jj_l1_pt):2*TMath::Log(jj_l2_softDrop_mass/jj_l2_pt)","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['jj_l1_softDrop_mass']=tree.GetV1()[0]
                    outputvariables[filename][i]['jj_l2_softDrop_mass']=tree.GetV2()[0]
                    outputvariables[filename][i]['rho l1']=tree.GetV3()[0]
                    outputvariables[filename][i]['rho l2']=tree.GetV4()[0]
                    tree.Draw("jj_l1_softDrop_pt:jj_l2_softDrop_pt:2*TMath::Log(jj_l1_softDrop_mass/jj_l1_softDrop_pt):2*TMath::Log(jj_l2_softDrop_mass/jj_l2_softDrop_pt)","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['jj_l1_softDrop_pt']=tree.GetV1()[0]
                    outputvariables[filename][i]['jj_l2_softDrop_pt']=tree.GetV2()[0]
                    outputvariables[filename][i]['rhoSD l1']=tree.GetV3()[0]
                    outputvariables[filename][i]['rhoSD l2']=tree.GetV4()[0]
                    tree.Draw("jj_l1_tau2/jj_l1_tau1:jj_l2_tau2/jj_l2_tau1:(jj_l1_tau2/jj_l1_tau1+(0.080*TMath::Log((jj_l1_softDrop_mass*jj_l1_softDrop_mass)/jj_l1_pt))):(jj_l2_tau2/jj_l2_tau1+(0.080*TMath::Log((jj_l2_softDrop_mass*jj_l2_softDrop_mass)/jj_l2_pt)))","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['tau21 l1']=tree.GetV1()[0]
                    outputvariables[filename][i]['tau21 l2']=tree.GetV2()[0]
                    outputvariables[filename][i]['tau21DDT l1']=tree.GetV3()[0]
                    outputvariables[filename][i]['tau21DDT l2']=tree.GetV4()[0]
                    tree.Draw("jj_l1_MassDecorrelatedDeepBoosted_WvsQCD:jj_l2_MassDecorrelatedDeepBoosted_WvsQCD:jj_l1_DeepBoosted_WvsQCD__0p05_MD_default_161718:jj_l2_DeepBoosted_WvsQCD__0p05_MD_default_161718","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['jj_l1_MassDecorrelatedDeepBoosted_WvsQCD']=tree.GetV1()[0]
                    outputvariables[filename][i]['jj_l2_MassDecorrelatedDeepBoosted_WvsQCD']=tree.GetV2()[0]
                    outputvariables[filename][i]['jj_l1_DeepBoosted_WvsQCD__0p05_MD_default_161718']=tree.GetV3()[0]
                    outputvariables[filename][i]['jj_l2_DeepBoosted_WvsQCD__0p05_MD_default_161718']=tree.GetV4()[0]
                    tree.Draw("jj_l1_DeepBoosted_WvsQCD:jj_l2_DeepBoosted_WvsQCD:jj_l1_DeepBoosted_WvsQCD__0p05_default_161718:jj_l2_DeepBoosted_WvsQCD__0p05_default_161718","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['jj_l1_DeepBoosted_WvsQCD']=tree.GetV1()[0]
                    outputvariables[filename][i]['jj_l2_DeepBoosted_WvsQCD']=tree.GetV2()[0]
                    outputvariables[filename][i]['jj_l1_DeepBoosted_WvsQCD__0p05_default_161718']=tree.GetV3()[0]
                    outputvariables[filename][i]['jj_l2_DeepBoosted_WvsQCD__0p05_default_161718']=tree.GetV4()[0]
                    tree.Draw("jj_l1_DeepBoosted_WvsQCD__0p05_MD_default_%s:jj_l2_DeepBoosted_WvsQCD__0p05_MD_default_%s:jj_l1_DeepBoosted_WvsQCD__0p05_default_%s:jj_l2_DeepBoosted_WvsQCD__0p05_default_%s"%(year,year,year,year),"evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['jj_l1_DeepBoosted_WvsQCD__0p05_MD_default_%s'%year]=tree.GetV1()[0]
                    outputvariables[filename][i]['jj_l2_DeepBoosted_WvsQCD__0p05_MD_default_%s'%year]=tree.GetV2()[0]
                    outputvariables[filename][i]['jj_l1_DeepBoosted_WvsQCD__0p05_default_%s'%year]=tree.GetV3()[0]
                    outputvariables[filename][i]['jj_l2_DeepBoosted_WvsQCD__0p05_default_%s'%year]=tree.GetV4()[0]
                    '''
                    tree.Draw("vbf_jj_l1_nhf:vbf_jj_l2_nhf:vbf_jj_l1_nef:vbf_jj_l2_nef","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['vbf_jj_l1_nhf']=tree.GetV1()[0]
                    outputvariables[filename][i]['vbf_jj_l2_nhf']=tree.GetV2()[0]
                    outputvariables[filename][i]['vbf_jj_l1_nef']=tree.GetV3()[0]
                    outputvariables[filename][i]['vbf_jj_l2_nef']=tree.GetV4()[0]
                    tree.Draw("vbf_jj_l1_Nconst:vbf_jj_l2_Nconst:vbf_jj_l1_eta:vbf_jj_l2_eta","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['vbf_jj_l1_Nconst']=tree.GetV1()[0]
                    outputvariables[filename][i]['vbf_jj_l2_Nconst']=tree.GetV2()[0]
                    outputvariables[filename][i]['vbf_jj_l1_eta']=tree.GetV3()[0]
                    outputvariables[filename][i]['vbf_jj_l2_eta']=tree.GetV4()[0]
                    tree.Draw("vbf_jj_l1_chf:vbf_jj_l2_chf:vbf_jj_l1_cmult:vbf_jj_l2_cmult","evt==%d&&jj_LV_mass>2500."%chosenevent,"goff")
                    outputvariables[filename][i]['vbf_jj_l1_chf']=tree.GetV1()[0]
                    outputvariables[filename][i]['vbf_jj_l2_chf']=tree.GetV2()[0]
                    outputvariables[filename][i]['vbf_jj_l1_cmult']=tree.GetV3()[0]
                    outputvariables[filename][i]['vbf_jj_l2_cmult']=tree.GetV4()[0]
                    '''
                    print outputvariables[filename]


print outputvariables

with open(jsonfile, 'w') as f:
    json.dump(outputvariables, f)
