#!bin/bash

year=Run2
indirW=MapsDeltaEta/DDTMap_WvsQCD_MD_scaled_${year}_withDeltaEta_finerbinning/
outdirW=MapsDeltaEta/DDTMap_WvsQCD_MD_scaled_${year}_withDeltaEta_finerbinning/
indirZH=MapsDeltaEta/DDTMap_ZHbbvsQCD_MD_scaled_${year}_withDeltaEta_finerbinning/
outdirZH=MapsDeltaEta/DDTMap_ZHbbvsQCD_MD_scaled_${year}_withDeltaEta_finerbinning/
cuts=("0p02" "0p03" "0p05" "0p10" "0p15" "0p20" "0p30" "0p50")


for cat in ${cuts[*]}; do
    echo $cat
    python changeMapName.py -c $cat -i ${indirZH} -o ${outdirZH} -t "ZH" --dec "MD"
    python changeMapName.py -c $cat -i ${indirW} -o ${outdirW} -t "W" --dec "MD"
done


