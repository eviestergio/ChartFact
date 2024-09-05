# ChartFact: An Explainable Three-Way Labelled Fact-Checking Dataset for Chart Images
- Authors: Evie Stergiopoulou, Angeline Wang, Mubashara Akhtar
- Paper Link: [ChartFact]()

## ChartFact Dataset
ChartFact is a chart fact-checking dataset with 100K fact-checking data entries and ___ charts created using ChartQA ([Masry et al., 2022](https://arxiv.org/pdf/2203.10244)), FigureQA ([Kahou et al., 2017](https://arxiv.org/pdf/1710.07300)), and PlotQA ([Methani et al., 2020](https://arxiv.org/pdf/1909.00997)) as seed datasets. 

The dataset includes chart images, their underlying tables and titles (translated through DePlot for FigureQA and PlotQA charts), and JSON files containing claims, labels ('supports', 'refutes', and 'not enough information'), and explanations.

ChartFact is thus a mixture of synthetic and real-world chart images, and contains a diverse range of chart types including: vertical and horizontal bar charts, line graphs, dot-line plots, pie charts, and scatter plots. The real-world data within the dataset is extracted from sources such as Pew, the World Bank, and Statista ([Masry et al., 2022](https://arxiv.org/pdf/2203.10244); [Methani et al., 2020](https://arxiv.org/pdf/1909.00997)).

To download the dataset, click [here](https://github.com/eviestergio/ChartFC).

### Pipeline for Creating the ChartFact Dataset

The pipeline for creating the ChartFact dataset includes the following steps: 
1. **Data Extraction:** Extract a subset of data entries from a source folder of QA datasets. 
2. **Data Preprocessing:** Standardise the extracted data into a consistent format. 
3. **Data Translation:** Generate underlying tables and titles (if available) for charts that don’t have any. 
4. **Data Formatting:** Convert the translated data tables into properly formatted CSV files and move titles (if available) to separate TXT files. 
5. **Data Prompting:** Generate claims and explanations for each class of labels.
6. **Final Dataset Creation:** Combine all processed data into a final dataset, shuffling and organizing it into relevant JSON files and folders for images and tables. 

#### Code Map 

All pipeline-related source code lives in the root directory `ChartFact`: 
- `data_extraction/random_extraction.py`: Script for extracting a subset of data entries. 
- `data_preprocessing/file-data_standardisation.py`: Script for standardising the extracted data. 
- `data_translation/deplot.py`: Script for generating underlying tables and titles (if available) using the DePlot model. 
- `data_translation/deplot_CSV_format.py`: Script for formatting the translated data tables into CSV files and titles (if available) into TXT files. 
- `data_prompting/main.py`: Script for generating claims and explanations using OpenAI's GPT-3.5-turbo.
- `final_dataset_creation/combine_datasets.py`: Script for combining all processed data into the final dataset. 

####  Prerequisites 
1. Install the necessary packages: ``` pip install -r requirements.txt ```
2. Ensure you have enough space. The full 100K dataset needs {#} GB when uncompressed and additional space is needed for intermediate data during processing.
3. Download all the required datasets ([ChartQA](https://huggingface.co/datasets/ahmed-masry/ChartQA/blob/main/ChartQA%20Dataset.zip); [FigureQA](https://www.microsoft.com/en-hk/download/details.aspx?id=100635); [PlotQA](https://github.com/NiteshMethani/PlotQA/blob/master/PlotQA_Dataset.md)) and place them under one folder (e.g., named 'QA_datasets') with each dataset named strictly as ChartQA, FigureQA, and PlotQA.

```
QA_datasets
├── ChartQA
│   ├── train
│   ├── val
│   └── test
├── FigureQA
│   ├── train
│   ├── val
│   └── test
└── PlotQA
    ├── train
    ├── val
    └── test
```
Make sure to manually adjust the path to the folder of the downloaded QA datasets in the first step of the pipeline (data extraction).

#### Generating the ChartFact Dataset

##### Using the pipeline script
1. Run the main_pipeline.py script: ``` python main_pipeline.py ```
2. The script will prompt you to enter the base folder name (e.g., seed_datasets) and the number of entries (e.g., 100K) for the dataset. Note that this number is used for naming the folders but does not automatically set the number of entries in the extraction file. The number of entries to be extracted from data_extraction/random_extraction.py need to be manually specified in the script.
3. You can choose to use a default source folder path (e.g., ChartFact/QA_datasets) or specify a custom one to extract the data from. 
4. Follow the prompts to complete each step of the pipeline.

##### Using individual scripts
1. ```cd ChartFact```
2. ```python data_extraction/random_extraction.py /path/to/QA_datasets seed_datasets_{#}/1_extracted_data_{#}```
3. ```python data_preprocessing/file-data_standardisation.py seed_datasets_{#}/1_extracted_data_{#} seed_datasets_{#}/2_preprocessed_data_{#}```
4. ```python data_translation/deplot.py seed_datasets_{#}/2_preprocessed_data_{#} seed_datasets_{#}/3_translated_data_{#}```
5. ```python data_translation/deplot_CSV_format.py seed_datasets_{#}/3_translated_data_{#} seed_datasets_{#}/3_translated_data_{#}```
6. ```python data_prompting/main.py seed_datasets_{#}/3_translated_data_{#} seed_datasets_{#}/4_prompted_data_{#} ```
7. ```python final_dataset_creation/combine_datasets.py seed_datasets_{#}/4_prompted_data_{#}  seed_datasets_{#}/5_final_dataset_{#}```


## Dataset Structure
The ChartFact dataset has the following structure:
```
├── ChartFact                   
│   ├── train   
│   │   ├── fc_entries.json       # Contains generated claims with corresponding labels and explanations
│   │   ├── png                   # Folder containing chart images 
│   │   │   ├── chartQA_{ID}-train.png
│   │   │   ├── figureQA_{ID}-train.png
│   │   │   ├── plotQA_{ID}-train.png
│   │   │   ├── ...
│   │   ├── tables                # Folder containing underlying data tables and titles (if available)
│   │   │   ├── chartQA_{ID}-train.csv
│   │   │   ├── figureQA_{ID}-train.csv
│   │   │   ├── plotQA_{ID}-train.csv    # Table file
│   │   │   ├── plotQA_{ID}-train.txt    # Title file 
│   │   │   ├── ...
│   └── val  
│   │   │   ...
│   │   │   ...
│   └── test  
│   │   │   ...
│   │   │   ...
│   │   |   ...
```

## Models

#### Proprietary
- **GPT-4o:** Please refer to [GPT-4o]().
- **Gemini 1.5 Flash:** Please refer to [Gemini 1.5 Flash]().
- **Claude 3.5 Sonnet:** Please refer to [Claude 3.5 Sonnet]().

#### Open-source
- **Llama 3:** Please refer to [Llama 3]().
- **ChartT5:** Please refer to [ChartT5]().
- **MatCha:** Please refer to [MatCha]().

## Contact 
If you have any questions about this work, please contact *Evie Stergiopoulou* at [paraskevi.stergiopoulou@kcl.ac.uk](mailto:paraskevi.stergiopoulou@kcl.ac.uk) or *Angeline Wang* at [02angelinewang@gmail.com](mailto:02angelinewang@gmail.com).

## Reference 
If you use our dataset or code, please cite our paper: [ChartFact: An Explainable Three-Way Labelled Fact-Checking Dataset for Chart Images](). 
```
@article{,
  author       = {Evie Stergiopoulou and
                  Angeline Wang and
                  Mubashara Akhtar},
  title        = {ChartFact: An Explainable Three-Way Labelled Fact-Checking Dataset for Chart Images},
  journal      = {},
  volume       = {},
  year         = {},
  url          = {},
  doi          = {},
  eprinttype   = {},
  eprint       = {},
  timestamp    = {},
  biburl       = {},
  bibsource    = {}
}
```