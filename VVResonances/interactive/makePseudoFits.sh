#bin/bash!

category=("VH_HPLP" "VH_LPHP" "VH_HPHP" "VV_HPLP" "VV_HPHP")
period=Run2
inputdir=$1
extralabel=$2
for c in ${category[@]}
do 
    outputdir=postfit_pseudodata_${extralabel}_${period}/
    mkdir ${outputdir}
    echo "############## make postfit for ##############"
    label=postfit_pseudodata_${extralabel}_${period}_${c}
    echo $label
    python runFitPlots_vjets_signal_bigcombo_splitRes.py -n ${inputdir}/workspace_JJ_BulkGWW_VVVH_13TeV_${period}_pseudodata.root  -i  ${inputdir}/JJ_${period}_nonRes_${c}.root -M 2000  -o ${outputdir} --channel ${c} -l ${c} --doVjets --addTop --doFit --pseudo | tee ${label}.log
  
done
  
