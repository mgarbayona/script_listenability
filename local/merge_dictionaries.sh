#!/usr/bin/env bash

DICT_ONE="$1"
DICT_TWO="$2"

rm -f merged.dict

cat "${DICT_ONE}" \
  | cut -d " " -f1 \
  | sed -E "s#\([0-9]\)##g" \
  | sort | uniq > wlist_one.tmp
cat "${DICT_TWO}" \
  | cut -d " " -f1 \
  | sed -E "s#\([0-9]\)##g" \
  | sort | uniq > wlist_two.tmp

cat wlist_one.tmp wlist_two.tmp \
  | sort | uniq > wlist_merged.tmp

cat wlist_merged.tmp | while read word; do
  echo "Gathering pronunciations for ${word}..."
  grep -E "^${word}  " "${DICT_ONE}" >> prons.tmp
  grep -E "^${word}\([0-9]\)  " "${DICT_ONE}" \
    | sed -E "s#\([0-9]\)##g" >> prons.tmp

  grep -E "^${word}  " "${DICT_TWO}" >> prons.tmp
  grep -E "^${word}\([0-9]\)  " "${DICT_TWO}" \
    | sed -E "s#\([0-9]\)##g" >> prons.tmp

  cat prons.tmp | sort | uniq > tmp; mv tmp prons.tmp
  pron_count=`cat prons.tmp | wc -l | bc`
  echo "${word} has ${pron_count} entries"

  if [ "${pron_count}" -eq 1 ]; then
    cat prons.tmp >> merged.dict
  else
    alt_count=0
    cat prons.tmp | while read entry; do
      if [ "${alt_count}" -eq 0 ] ; then
        formatted_entry=`echo "${entry}"`
      else
        formatted_entry=`echo "${entry}" | sed -E "s#  #(${alt_count})  #g"`
      fi
      echo "${formatted_entry}" >> merged.dict
      ((alt_count+=1))
    done
  fi
  rm -f prons.tmp
done

rm -f wlist_one.tmp
rm -f wlist_two.tmp
rm -f wlist_merged.tmp
rm -f prons.tmp
