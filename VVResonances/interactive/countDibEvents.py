import ROOT



lumi=137600.0
year="Run2"
directory="dibBKG_Run2/" # bkcpVjetsMVV/" #"results_start1181/"                                                                                                                        
contrib =["WWJets","WZJets","ZZJets","WHJets","ZHJets"]

categories = ["VBF_VH_HPHP","VBF_VV_HPHP","VBF_VH_LPHP","VBF_VH_HPLP","VBF_VV_HPLP","VH_HPHP","VV_HPHP","VH_LPHP","VH_HPLP","VV_HPLP","NP"]

events = {}

for cat in categories:
    print cat
    events[cat] = {}
    for i,con in enumerate(contrib):
        print con
        tf = ROOT.TFile.Open(directory+"JJ_"+year+"_"+con+"_"+cat+".root",'READ')
        print tf

        hist = tf.Get(con)
        hist.SetDirectory(0)
        #integral = round(hist.Integral()*lumi,2)
        integral = hist.GetEntries()
        print integral

        events[cat][con] = integral


print events


contributions="                  "
for con in contrib:  contributions+=con+"    "
print contributions
for cat in categories:
    space="    "
    if cat.find("VBF") == -1: space = "        "
    if cat == "NP": space ="            "
    string = "   "+cat+space
    for con in contrib: 
        space="       "
        if cat.find("VBF") == -1: space = "      "
        if cat == "NP": space ="     "
        string+=str(events[cat][con])+space
    print string
