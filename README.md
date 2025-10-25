# script_listenability

**Text-based measures for evaluating the comprehensibility of spoken materials**

This repository accompanies the paper:

> **M. Gringo Angelo Bayona, A. Hines, E. Gilmartin, and E. Uí Dhonnchadha**,  
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
assets/issc/ # Figures and plots used in the ISSC paper
data/ # Processed data and example transcripts
local/ # Local scripts for running experiments
LICENSE # Apache 2.0 License
README.md # Project overview

---

## 🚀 Quickstart

Clone the repository and install dependencies:
```bash
git clone https://github.com/mgarbayona/script_listenability.git
cd script_listenability
pip install -r requirements.txt
```

---

## 🧰 Environment
This project was developed and tested with Python 3.12. To create a matching conda environment:
```bash
conda create -n listenability python=3.12 -c conda-forge
conda activate listenability
pip install -r requirements.txt
```

