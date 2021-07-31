#bin/bash!

period=Run2
inputdir=results_Run2/
wsdir=results_Run2/

extralabel=afterpreapproval_1000
#extralabel=afterpreapproval_newShapesFits

c=$1
ws=VBF_VVVH

name=_${extralabel}
signal=WprimeWHinc
mass=2000

#signal=ZprimeZHinc
#mass=3000

outputdir=prefit_data_SR_VorH_${signal}${mass}_${extralabel}_${period}/

mkdir ${outputdir}
echo "############## make postfit for ##############"
label=prefit_data_SR_VorH_${signal}${mass}_${extralabel}_${period}_${c}
echo $label

python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${wsdir}/workspace_JJ_${signal}_${ws}_13TeV_${period}_data${name}.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M ${mass}  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --signalScaleF 0 -s -x 65,105 -y 110,140 --proj z --both | tee ${label}.log

  

