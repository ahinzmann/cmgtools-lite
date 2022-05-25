#!bin/bash

period=Run2
inputdir=results_Run2/
wsdir=results_Run2/
extralabel=afterpreapproval_newShapesFits
c=$1
ws=VBF_VVVH

name=_${extralabel}
signal=WprimeWZ
#outputdir=prefit_data_blindSR_${extralabel}_${period}/
#mkdir ${outputdir}
#echo "############## make prefit for ##############"
#label=prefit_data_blindSR_${extralabel}_${period}_${c}
#echo $label
#python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${inputdir}/workspace_JJ_BulkGWW_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --blind -x 55,65,140,215 -y 55,65,140,215 | tee ${label}.log


outputdir=postfit_data_SR_bonly_${period}_VV65-105/
mkdir ${outputdir}
echo "############## make postfit for ##############"
label=postfit_data_SR_bonly_${period}_VV65-105_${c}
echo $label
python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit -x 65,105 -y 65,105  | tee ${label}.log
#python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit -x 65,105 -y 65,105 --addDIB | tee ${label}.log
  

