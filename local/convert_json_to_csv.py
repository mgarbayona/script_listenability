import csv
import datetime
import json
import os
import re

from os.path import join, splitext

voa_level_map = dict({1: 'beginner', 2: 'intermediate', 3: 'advanced'})

def convert_to_elllo_record(json_record):
    elllo_record = dict()

    elllo_record['level - elllo'] = json_record['level_desc']
    elllo_record['level - numerical'] = json_record['level_nmbr']
    elllo_record['title'] = json_record['title']

    elllo_record['site link'] = json_record['url']
    elllo_record['filename'] = "elllo-" + json_record['id']
    elllo_record['speaker locations'] = json_record['speaker_locs']
    elllo_record['speaker names'] = json_record['speaker_names']

    return elllo_record

def convert_to_voa_record(json_record, material_level, material_category):
    """
    Converts the VoA record from the JSON file to a record compatible to the
    online spreadsheet

    Parameters
    ----------
    json_record : dict
        VoA material information from a JSON-format database
    material_level : int
        Assigned level to the VoA material
    material_category : string
        Category of the VoA material

    Returns
    -------
    voa_record : dict
        VoA material information compatible to the online spreadsheet
    """
    voa_record = dict()

    voa_record['level - voa'] = voa_level_map[material_level]
    voa_record['level - numerical'] = material_level
    voa_record['category'] = material_category
    voa_record['title'] = json_record['title']

    orig_voa_filename = json_record['files'][0]['path']
    voa_record['filename'] = transform_voa_filename(orig_voa_filename,
                                                    material_level)

    voa_record['site link'] = json_record['url']
    voa_record['speaker count'] = ""
    voa_record['speaker names'] = ""
    voa_record['writer or adapter'] = ""
    voa_record['editor'] = ""

    date_raw = datetime.datetime.strptime(json_record['date'], '%B %d, %Y')
    voa_record['date'] = date_raw.strftime('%d-%b-%Y')

    return voa_record

def run_voa_example():
    # Request permission from VoA to access the these files
    voa_scraped_json = "data/voa/materials/json/voa_beg-news-words.json"
    material_level = 1
    material_category = "News Words"
    material_infos_csv = "data/voa/materials/infos/voa_beg-news-words.csv"

    # Output directory for the transcripts in *.txt format
    transcript_dir = "data/voa/materials/txt"

    with open(voa_scraped_json, mode='r') as in_f:
        json_records = json.load(in_f)

    with open(material_infos_csv, mode='w') as out_f:
        count = 0
        record_writer = csv.writer(out_f, delimiter=';')

        for json_record in json_records:
            voa_record = convert_to_voa_record(
                json_record, material_level, material_category
            )

            if count == 0:
                record_writer.writerow(voa_record.keys())
                count += 1

            record_writer.writerow(voa_record.values())

            if json_record['text']:
                transcript_path = f"{transcript_dir}/{voa_record['filename']}.txt"
                with open(transcript_path, mode='w') as text_f:
                    text_f.write(json_record['text'])

def transform_voa_filename(orig_voa_filename, material_level):
    """
    Change filename as used in the VoA website to a name used in the
    experiiment

    Parameters
    ----------
    orig_voa_filename : string
        Original filename of the VoA material as used in the website
    material_level : int
        Assigned level to the VoA material

    Returns
    -------
    new_voa_filename : string
        New filename compliant to format used in the experiment
    """
    new_voa_filename = re.sub(r'^full/', "voa-", orig_voa_filename)

    new_voa_filename = re.sub(
        r'_[A-Za-z0-9]+', str(material_level), new_voa_filename
    )

    new_voa_filename = splitext(new_voa_filename)[0]

    return new_voa_filename

def main():
    run_voa_example()

if __name__ == "__main__":
    main()
