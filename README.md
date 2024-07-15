# ChartFact: Explainable Fact-Checking over Chart Images
- Authors: Paraskevi Stergiopoulou, Angeline Wang, Mubashara Akhtar
- Paper Link: [ChartFact]()

## ChartFact Dataset
ChartFact is a chart fact-checking dataset with 100K fact-checking data entries and ___ charts created using ChartQA [(Masry et al., 2022)](https://arxiv.org/pdf/2203.10244), FigureQA [Kahou et al., 2017](https://arxiv.org/pdf/1710.07300), and PlotQA [Methani et al., 2020](https://arxiv.org/pdf/1909.00997) as seed datasets. 

The dataset includes chart images, tables (translated through Deplot for FigureQA and PlotQA), 'supports', 'refutes' and 'not enough information' claims, along with explanations. 

ChartFact is thus a mixture of synthetic and real-world chart images, and contains a diverse range of chart types including: Bar charts, line graphs, dot-line plots, pie charts, and scatter plots. The real-world data within the dataset is extracted from sources such as Pew, the World Bank and Statista [(Masry et al., 2022)](https://arxiv.org/pdf/2203.10244).

To download the dataset, click [here](https://github.com/eviestergio/ChartFC).

Code for baselines available here: []()

The dataset has the following structure:

├── ChartFact Dataset                   
│   ├── train   
│   │   ├── fc_entries.json # ChartFact machine generated claims and explanations. 
│   │   ├── png                   # Chart Images Folder
│   │   │   ├── chartQA_id-train.png
│   │   │   ├── figureQA_id-train.png
│   │   │   ├── plotQA_id-train.png
│   │   │   ├── ...
│   │   ├── tables                # Underlying Data Tables Folder
│   │   │   ├── chartQA_id-train.csv
│   │   │   ├── figureQA_id-train.csv
│   │   │   ├── plotQA_id-train.csv
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
If you have any questions about this work, please contact *Paraskevi Stergiopoulou* at [paraskevi.stergiopoulou@kcl.ac.uk](mailto:paraskevi.stergiopoulou@kcl.ac.uk) or *Angeline Wang* at [angeline.wang@kcl.ac.uk](mailto:angeline.wang@kcl.ac.uk).

## Reference 
If you use our dataset or code, please cite our paper: [ChartFact: An Evidence-Based Fact-Checking Dataset over Chart Images](). 

@article{,
  author       = {Paraskevi Stergiopoulou and
                  Angeline Wang and
                  Mubashara Akhtar},
  title        = {ChartFact: An Evidence-Based Fact-Checking Dataset over Chart Images},
  journal      = {},
  volume       = {},
  year         = {},
  url          = {},
  doi          = {},
  eprinttype    = {},
  eprint       = {},
  timestamp    = {},
  biburl       = {},
  bibsource    = {}
}