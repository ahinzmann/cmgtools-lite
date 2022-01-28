#!bin/bash

period=Run2
inputdir=results_Run2/
wsdir=results_Run2/
#extralabel=afterpreapproval_newShapesFits
extralabel=afterpreapproval_1000
c=$1
ws=VBF_VVVH
name=_${extralabel} 

signal=BulkGZZ
mass=3000

#signal=BulkGWW
#mass=2000

outputdir=prefit_data_SR_${signal}${mass}_${extralabel}_${period}_VV65-105/
mkdir ${outputdir}
echo "############## make prefit for ##############"
label=prefit_data_SR_${signal}${mass}_${extralabel}_${period}_${c}_VV65-105
echo $label
python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M ${mass}  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop  --signalScaleF 0 -s -x 65,105 -y 65,105 --proj z | tee ${label}.log


