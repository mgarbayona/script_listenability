import inflect
import re

from num2words import num2words
from os.path import join

p = inflect.engine()

def spell_out_numbers(text):
    normalised_text = []
    era_check = re.compile(r'^\d{4}S$')
    ordinal_check = re.compile(r'^\d+(ST|ND|RD|TH)$')
    year_check = re.compile(r'^\d{4}$')

    text = text.upper()

    for token in text.split():
        token = token.strip()

        if any(char.isdigit() for char in token):
            if bool(re.search(ordinal_check, token)):
                # Ordinal
                print("%s is ordinal." % token)
                number = re.search(r'\d*', token).group(0)
                normalised_token = num2words(number, to='ordinal')
            elif bool(re.search(era_check, token)):
                # Era
                print("%s is era." % token)
                number = re.search(r'\d*', token).group(0)
                year = num2words(number, to='year').split()
                year[-1] = p.plural(year[-1])
                normalised_token = " ".join(year)
            elif bool(re.search(year_check, token)):
                # Year
                print("%s is year." % token)
                normalised_token = num2words(token, to='year')
            else:
                normalised_tokens = []
                subtokens = re.split(r'(\d+)', token)

                for subtoken in subtokens:
                    if subtoken:
                        if subtoken.isnumeric():
                            print("%s is a number." % subtoken)
                            normalised_tokens.append(num2words(subtoken))
                        else:
                            if "%" in subtoken:
                                print("%s is percent." % subtoken)
                                subtoken = subtoken.replace("%", "PERCENT")

                            print("%s is text." % subtoken)

                            normalised_tokens.append(subtoken)

                normalised_token = " ".join(normalised_tokens)

            normalised_text.append(normalised_token.strip())

        else:
            normalised_text.append(token.strip())

    normalised_text = " ".join(normalised_text)
    normalised_text = normalised_text.replace('-', ' ').strip()

    return normalised_text

def main():
    data_name = "voa"
    asr_name = "google"

    main_dir = join("data", data_name)
    results_dir = join(main_dir, "results/pipeline/google-web-speech")
    results_file = "voa_google-web_Tr-chunks_Tr-period_norm.txt"
    results_path = join(results_dir, results_file)

    transcript_dir = join(main_dir, "results/pipeline/google-web-speech")
    transcript_file = "voa_google-web_Tr-chunks_Tr-period.txt"
    transcript_path = join(transcript_dir, transcript_file)

    with open(results_path, 'a') as tr_out_f:
        with open(transcript_path, 'r') as tr_in_f:
            for entry in tr_in_f:
                utt_id,text = entry.strip().split(" ", maxsplit=1)
                print("Analyzing %s" % utt_id)

                formatted_text = text.replace('-', ' ')
                normalised_text = spell_out_numbers(formatted_text).upper()
                normalised_text = utt_id + " " + normalised_text + "\n"

                tr_out_f.writelines(normalised_text)

    # normalised_text = spell_out_numbers("T'S SETUP CENTRES ABLE TO PROVIDE UP TO 10000 SHOTS IN ONE DAY. TODAY 76% OF MALAYSIA'S POPULATION IS FULLY VACCINATED. MANY OTHER COUNTRIES IN THE ASIA-PACIFIC AREA ALSO HAVE VACCINATION RATES CLOSE TO OR ABOVE 70%.").upper()
    # print(normalised_text)

if __name__ == "__main__":
    main()
