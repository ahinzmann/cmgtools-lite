import ROOT
import time

legend=["TTbar only","Single Top","SM WW"]
year="Run2" #1617"
directory="results_Run2/" #"results_1617_VV/" # bkcpVjetsMVV/" #"results_start1181/"
contrib =["TTJets","STJets","WWJets"]
categories=["VV_HPLP","VV_HPHP","VH_HPLP","VH_HPHP","VH_LPHP","VBF_VV_HPLP","VBF_VV_HPHP","VBF_VH_HPLP","VBF_VH_HPHP","VBF_VH_LPHP"]
lumi = 137600.0
colors = [ROOT.kBlack,ROOT.kBlue,ROOT.kRed,ROOT.kMagenta,ROOT.kTeal+3,ROOT.kViolet,ROOT.kGreen+2]
markers=[8,21,22,23,33,29,34]
bkg = ["nonRes","TTJets","WJets","ZJets"]

def getNorm(background,category,lumi):
 print " background ",background
 f = ROOT.TFile.Open(directory+"JJ_"+year+"_"+background+"_"+category+".root",'READ')
 print f
 hmvv = f.Get(background)
 norm = hmvv.Integral()*lumi
 if background == "nonRes": norm = norm*1.8

 print " norm ",norm
 return norm

sumtt = 0
sum_only = {}
sum_only["TTJets"] = 0
sum_only["STJets"] = 0
sum_only["WWJets"] = 0
sum_b = {}
for b in bkg:
 sum_b[b] = 0

sumtot = 0
for cat in categories:
 print " **** cat ",cat
 sumtt = sumtt+getNorm("TTJets",cat,lumi)

 for b in bkg:
  sum_b[b] = sum_b[b]+getNorm(b,cat,lumi)
  sumtot = sumtot+getNorm(b,cat,lumi)


 for con in contrib:

  tf = ROOT.TFile.Open("JJ_"+year+"_"+con+"_"+cat+".root",'READ')
  print tf 
  hmvv = tf.Get(con)
  sum_only[con] = sum_only[con]+hmvv.Integral()*lumi
  tf.Close()


print " TT only / TT tot ",sum_only["TTJets"]/sumtt 
print " ST only / TT tot ",sum_only["STJets"]/sumtt 
print " WW only / TT tot ",sum_only["WWJets"]/sumtt 

print " TT only / tot ",sum_only["TTJets"]/sumtot 
print " ST only / tot ",sum_only["STJets"]/sumtot 
print " WW only / tot ",sum_only["WWJets"]/sumtot 


for b in bkg:
 print b+" / tot ",sum_b[b]/sumtot
