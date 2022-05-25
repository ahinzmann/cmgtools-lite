#!bin/bash

signals=("ZprimeZHinc" "WprimeWHinc" "ZprimeWW" "BulkGZZ" "BulkGWW"  "WprimeWZ" "RadionWW" "RadionZZ" "RadionVV" "BulkGVV" "Vprime" "VBF_ZprimeZHinc" "VBF_WprimeWHinc" "VBF_ZprimeWW" "VBF_BulkGZZ" "VBF_BulkGWW"  "VBF_WprimeWZ" "VBF_RadionWW" "VBF_RadionZZ" "VBF_Vprime" "VBF_BulkGVV" "VBF_RadionVV" "VprimeWV" "VBF_VprimeWV" "VprimeVHinc" "VBF_VprimeVHinc") 

mergefiles=false

year=Run2
year2=1617
output=ObsLimits
name=afterpreapproval
hvt=0
period="ALL"


for signal in ${signals[*]}; do
    echo $signal
    if $mergefiles; then
	combinename=*.AsymptoticLimits #_data_VBFggDY_VVVVH_${year}_afterpreapproval_sched14.AsymptoticLimits
	#if [[ $signal == ?"prime"* ]]; then 
	#    combinename=.AsymptoticLimits
	#fi
	#if [[ $signal == "ZprimeWW" ]]; then 
	#    combinename=*.AsymptoticLimits
	#fi
	find limits_$signal/higgsCombine${signal}${combinename}.mH* -size +1500c | xargs hadd -f Limits_${signal}_13TeV_${year}_data_ggDYVBF_VVVH_afterpreapprovalMix.root
	if [[ $signal == *"BulkGWW" || $signal == *"BulkGZZ" ]]; then
	    combinename=_data_VBFggDY_VVVVH_${year2}_afterpreapproval_sched14.AsymptoticLimits
	    find higgsCombine${signal}${combinename}.mH* -size +1500c | xargs hadd -f Limits_${signal}_13TeV_${year2}_data_ggDYVBF_VVVH_partial_afterpreapproval.root
	fi
    fi

    limitfile=Limits_${signal}_13TeV_Run2_data_ggDYVBF_VVVH_afterpreapprovalMix.root
    workspace=results_Run2/AllCat_workspace/workspace_JJ_${signal}_VBF_VVVH_13TeV_Run2_data_newbaseline.root 
    echo $limitfile
    echo $workspace

    vvMakeLimitPlot.py ${limitfile} -o ${output} -s ${signal} -n ${name} -p ${period} --hvt ${hvt}  --HVTworkspace ${workspace} --blind 0 --theoryUnc 

    python compareLimitsALLsignals.py -s ${signal}  --limitname afterpreapprovalMix -n comparisons_afterpreapproval
    if [[ $signal == "Bulk"* ]]; then
	cp Limits_${signal}_13TeV_Run2_data_ggDYVBF_VVVH_afterpreapprovalMix.root Limits_${signal}_13TeV_Run2_data_ggDYVBF_VVVH_afterpreapproval.root
	python compareLimitsALLsignals.py -s ${signal} -n compareB2G18002_afterpreapproval --limitname afterpreapproval
    fi

done
