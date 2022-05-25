#bin/bash!

#category=("VV_HPLP" "VV_HPHP" "VH_HPLP" "VH_LPHP" "VH_HPHP")
period=Run2
inputdir=results_Run2/
wsdir=results_Run2/
extralabel=afterpreapproval_newShapesFits_10000000
c=$1
ws=VBF_VVVH
#ws=VVVH
name=_${extralabel}    #_JMRplus1sigmaForReal_Vjets50_VjetsCat_ptdeponlysig_NEWkfactorsMVV1sigma
#name=_10000_${extralabel}
#for c in ${category[@]}
#do 
signal=VBF_BulkGWW
'''
outputdir=prefit_data_SR_${signal}_${extralabel}_${period}/
mkdir ${outputdir}
echo "############## make prefit for ##############"
label=prefit_data_SR_${signal}_${extralabel}_${period}_${c}
echo $label
python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop  --signalScaleF 0 -s | tee ${label}.log

'''
sf=500
if [[ $c == "VBF_"* ]]; then
    sf=3
fi
echo " sf "
echo $sf

outputdir=postfit_noprelim_data_SR_${signal}_${extralabel}_${period}/
mkdir ${outputdir}
echo "############## make postfit for ##############"
label=postfit_noprelim_data_SR_${signal}_${extralabel}_${period}_${c}
echo $label
#python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit --addDIB | tee ${label}.log
python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 3000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit -s --signalScaleF ${sf} --plotbonly -p b --both --prelim "" | tee ${label}.log

python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 3000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit -s --signalScaleF ${sf} --plotbonly -p xyz --prelim "" | tee ${label}.log

  
#done
  

