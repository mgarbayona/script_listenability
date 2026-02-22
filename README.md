# Script Listenability

**Text-based measures for evaluating the comprehensibility of spoken materials**

This repository accompanies the paper:

> **M. G. A. R. Bayona, A. Hines, E. Gilmartin, and E. Uí Dhonnchadha**,  
> *"An Evaluation of the Use of Text-Based Comprehensibility Measures on Online Spoken Language Learning Materials,"*  
> 2023 34th Irish Signals and Systems Conference (ISSC), Dublin, Ireland, 2023, pp. 1–6.  
> DOI: [10.1109/ISSC59246.2023.10162065](https://doi.org/10.1109/ISSC59246.2023.10162065)

---

## 📘 Overview

This repository contains code and data used to evaluate how well **readability-based text measures** can capture the **listenability** (or comprehensibility) of online spoken language learning materials.  
The study explored the relationship between **expert-assigned difficulty levels** and automatically computed **readability scores** from spoken transcripts, including those generated via automatic speech recognition (ASR).

Key aspects:
- Comparison of four text-based measures: *Flesch Reading Ease*, *Dale–Chall Readability*, *Lensear Write*, and *McAlpine EFLAW™ Readability*.
- Evaluation using **Voice of America (VOA) Learning English** news materials.
- Analysis of robustness when using **automatically generated transcripts** (Kaldi ASpIRE and Google Web Speech API).
- Classification experiments predicting VOA difficulty levels from readability scores.

---

## 🧩 Repository Structure

- `assets/issc/` — Figures and plots used in the ISSC paper  
- `data/` — Processed data and example transcripts  
- `local/` — Scripts for running experiments and ASR pipelines  
  - `kaldi/` — Files to run Kaldi’s ASpIRE Chain Model on VOA data  
  - `resources/` — Resources needed to compute different text statistics  
- `LICENSE` — Apache 2.0 License  
- `README.md` — Project overview  


---

## 🧰 Environment
This project was developed and tested with Python 3.9. To create a matching conda environment:

```bash
git clone https://github.com/mgarbayona/script_listenability.git
cd script_listenability
conda create -n listenability python=3.9 -c conda-forge
conda activate listenability
pip install -r requirements.txt
```

### 🧩 Additional Dependencies

This project also makes use of the following external tools and libraries:

- **[Punctuator](https://github.com/ottokart/punctuator2)** - for adding punctuations to ASR output
- **[Syllabify](https://github.com/cainesap/syllabify)** — for syllable segmentation  
- **[Textstat](https://github.com/textstat/textstat)** — for calculating text statistics and for cross-checking the implementation of standard readability metrics


---

## 🧠 Acknowledgements

This research was supported by the Science Foundation Ireland Centre for Research Training in Digitally-Enhanced Reality (d-real) under Grant No. 18/CRT/6224.
We also acknowledge the Voice of America (VOA) Learning English program for providing access to educational materials used in this study.
