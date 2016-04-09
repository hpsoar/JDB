#!/bin/bash

tt=("jpn" "cmn" "eng")
for lang in ${tt[@]}; do 
  ofile="tatoeba/${lang}_sentences.csv"
  echo $lang
  echo $ofile
  awk -v var="$lang" '$2~var{print $0;}' tatoeba/sentences_detailed.csv > $ofile
done
