# ChartFact: Explainable Fact-Checking over Chart Images
- Authors: Paraskevi Stergiopoulou, Angeline Wang, Mubashara Akhtar
- Paper Link: [ChartFact]()

## ChartFact Dataset
ChartFact is a chart fact-checking dataset with 100K data entries created using ChartQA [(Masry et al., 2022)](https://arxiv.org/pdf/2203.10244), FigureQA [Kahou et al., 2017](https://arxiv.org/pdf/1710.07300), and PlotQA [Methani et al., 2020](https://arxiv.org/pdf/1909.00997) as seed datasets. 

The dataset includes chart images, tables (translated through Deplot and Chart-to-table for FigureQA and PlotQA), 'supports', 'refutes' and 'not enough information' claims, along with explanations. 

ChartFact is thus a mixture of synthetic and real-world chart images, and contains a diverse range of chart types including: Bar charts, line graphs, dot-line plots, pie charts, and scatter plots. The real-world data within the dataset is extracted from sources such as Pew, the World Bank and Statista [(Masry et al., 2022)](https://arxiv.org/pdf/2203.10244).

Dataset available here: (https://github.com/eviestergio/ChartFC)

Code for baselines available here: []()

### First Version (does not have the annotations folder)
The ChartFact dataset is available in the ChartFact Dataset folder in this repository.

### Full Version (with the annotations folder)
The full ChartFact dataset (including the annotations) can be downloaded from the following huggingface dataset: [Full ChartFact Dataset](). The dataset has the following structure:

├── ChartFact Dataset                   
│   ├── train   
│   │   ├── train.json # ChartFact machine generated claims and explanations. 
│   │   ├── annotations           # Chart Images Annotations Folder
│   │   │   ├── chart1_name.json
│   │   │   ├── chart2_name.json
│   │   │   ├── ...
│   │   ├── png                   # Chart Images Folder
│   │   │   ├── chart1_name.png
│   │   │   ├── chart2_name.png
│   │   │   ├── ...
│   │   ├── tables                # Underlying Data Tables Folder
│   │   │   ├── chart1_name.csv
│   │   │   ├── chart2_name.csv
│   │   │   ├── ...
│   └── val  
│   │   │   ...
│   │   │   ...
│   └── test  
│   │   │   ...
│   │   │   ...
│   │   |   ...

### Models
_Proprietary_
#### GPT-4o
Please refer to [GPT-4o]()

#### Gemini 1.5 Flash 
Please refer to [Gemini 1.5 Flash]()

#### Claude 3.5 Sonnet
Please refer to [Claude 3.5 Sonnet]()

_Open-source_
#### Llama 3
Please refer to [Llama 3]()

#### ChartT5
Please refer to [ChartT5]()

#### MatCha 
Please refer to [MatCha]()

## Contact 
If you have any questions about this work, please contact *Paraskevi Stergiopoulou* at [paraskevi.stergiopoulou@kcl.ac.uk]() or *Angeline Wang* at [angeline.wang@kcl.ac.uk]().

## Reference 
If you use our dataset or code, please cite our paper: [ChartFact: An Evidence-Based Fact-Checking Dataset over Chart Images](). 

@article{akhtar-etal-2023-chartcheck,
  author       = {Paraskevi Stergiopoulou and
                  Angeline Wang and
                  Mubashara Akhtar},
  title        = {ChartFact: An Evidence-Based Fact-Checking Dataset over Chart Images},
  journal      = {CoRR},
  volume       = {abs/2311.07453},
  year         = {2023},
  url          = {https://doi.org/10.48550/arXiv.2311.07453},
  doi          = {10.48550/ARXIV.2311.07453},
  eprinttype    = {arXiv},
  eprint       = {2311.07453},
  timestamp    = {Wed, 15 Nov 2023 16:23:10 +0100},
  biburl       = {https://dblp.org/rec/journals/corr/abs-2311-07453.bib},
  bibsource    = {dblp computer science bibliography, https://dblp.org}
}