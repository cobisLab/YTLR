# Related paper:

T.-H. Yang*, C.-Y. Wang+, H.-C. Tsai+, Y.-C. Yang+, and C.-T. Liu, YTLR: extracting yeast transcription factor-gene associations from the literature using automated literature readers, (Under Review)


# Prepare the Environment

Suggested running environments: Linux Ubuntu 16.04.6, Python 3.8.5

We recommend using the conda package to create a new environment for YTLR to automatically include the required python packages. 

Here is an example: 

1. Install the Conda package for your system. The installation of the package can be found <a href="https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html">here</a>. 

2. Create the YTLR Conda environment. This may take a while, depending on the network status.

```
conda create -n "YTLR" python=3.8.5
```

3. Activate your YTLR Conda environment. 

```
conda activate YTLR
```

4. If you are using APPLE MAC systems, please install wget first:

```
brew install wget
``` 

If you are using Microsoft Windows systems, please install wget first:

```
conda install -c menpo wget
``` 

5. If you want to leave the YTLR Conda envrionment, please type:

```
conda deactivate YTLR
```

6. **Notice!** Because the PMC FTP service will be updated daily, we recommend executing the following command before using YTLR functions.
 
``` python update_PMC_xml.py```


# Steps to Use YTLR

1. Download the codes. Please skip this if you have already downloaded the codes.

```
wget https://cobishss0.im.nuk.edu.tw/YTLR/YTLR.tar.gz
```

2. Unzip the file.

```
tar -zxvf YTLR.tar.gz
```

3. Change the working directory.

```
cd YTLR/
```

4. Download the model from the following link and unzip the file. Please skip it if you have done this step.

```
wget https://cobisHSS0.im.nuk.edu.tw/YTLR/Model.tar.gz

tar zxvf Model.tar.gz
```

5. If this is the first time you use YTLR, run the following command to install the necessary packages. 

```
pip install -r requirements.txt

python -m spacy download en_core_web_trf 3.2.0
```

If the second command fails, try below:

```
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_trf-3.2.0/en_core_web_trf-3.2.0.tar.gz
```

6. Prepare the inputs for YTLR. In YTLR, users can input a list of abstracts downloaded using the PubMed download function. 
    >***HOW TO GET ABSTRACTS FROM PubMed***
    >>1. Search the PubMed website for specific keywords to obtain the lists of articles. 
    >>2. Select the abstracts of interest or select all abstracts in the page. 
    >>3. Click the ***save*** button.
    >>4. Choose the ***Abstract(text)***.
    >>5. The .txt file containing all the abstracts will be downloaded.
    >>![](https://i.imgur.com/36LDa3P.png)


7. (Optional) Users can specify the full-texts of the selected abstracts by themselves. However, this is an optional step. YTLR can also help retrieve the available PMC full-texts using the PMC FTP service (Detail can be found <a href ="https://www.ncbi.nlm.nih.gov/pmc/tools/ftp/">here</a>). 

    >***HOW TO GET FULL TEXT FROM PMC***
    >>1. Browse the PubMed website(https://www.ncbi.nlm.nih.gov/pmc/) and choose the paper you want.
    >>2. You can get the full content of the website by using the right mouse button and clicking "save as new file" to save it as an HTML file. 

8. Put the abstract .txt file and the full-text .html files in the same input folder.  

   We have provided an example input folder named "small_input."
      
   **SAMPLE INPUT**
   
    ```
    sample_input/ - abstracts.txt
                  - PMC165726.html
                  - PMC5469029.html

    .txt --> abstracts downloaded from PubMed (only abstract)
    .html --> full-texts downloaded from PMC (optional)
    ```

9. Run YTLR and predict the results. The results will be saved in the output folder specified with the -o parameter. The program will download some essential data on the first use.
```
python main.py -i <path to input directory> -d <tfb/tfr/both> -check <0/1> -download <0/1> -o <path to the output directory>
```

>**Required arguments:**

>* -i: The input data directory path.

>* -d: Specify the type of TF-gene association to consider ('tfb', 'tfr', or 'both', default = 'both').

>* -check: Check if the article relates to the yeast species (1 --> check, 0 -> do not check, default = 1).

>* -download: Check if the user wants to use the auto full text retrieval script based on the PMC FTP service (1 -> yes, 0 -> no, default = 1).


>* -o: The output directory for the results. 


**Notice!**

***It may take a while (generally, half an hour to several hours, depending on the network bandwidth and the number of articles given) to download the full texts using the PMC ftp services due to its file package structures. We do not suggest using wifi connections for this automated script since the download process may break in wifi transmissions.***

***And due to the restriction of the term usage of the PMC ftp services, only part of the full texts in PMC can be downloaded via this service. Those articles that cannot be downloaded through the PMC ftp services may require an additional PMC website "Save as..." action for each of them. ***

# Example and Output Results

If we use the example inputs with the example command:

```
python main.py -i ./sample_input -d tfb -check 1 -o tfb_output
```

The results will be generated in the tfb_output folder. 

**SAMPLE OUTPUTS**

```
tfb_output/ - TFB_article_identification.tsv
            - non-TFB_articles.txt
            - TF-gene_transcriptional_relation_summary.tsv
            - pmids_cannot_find_fullText.txt
            - download_xml/ - {PMC4063667}.xml
            - TF-gene_Pair_Details/ - TFB/ - YPR065W_YOR011W/ - 23435728.txt
                                           - {TF_ORF}_{GENE_ORF}/ - {PMID}.txt

```
 

>**File descriptions:**

>* **{TFB/TFR}\_article\_identification.tsv:** Articles that contain TFB or TFR evidence.
>* **non-{TFB/TFR}\_articles.txt:** Articles that does not contain TFB or TFR evidence.
>* **TF-gene\_transcriptional\_relation\_summary.tsv:** Summary of TF-gene transcriptional relation conclusion results.
>* **pmids\_cannot\_find\_fullText.txt:** PMIDs with no available full text. If full texts are available for all articles, the content of the file will be empty.
>* **download_xml/{PMCID}.xml:** the xml files downloaded from the PMC FTP service.
>* **TF-gene\_Pair\_Details/{TFB/TFR}/{TF\_ORF}\_{GENE\_ORF}/{PMID}.txt:** Sentence descriptions for the TF-gene pairs found in the articles.

### **Stage I Outputs**

Stage I outputs contain the following: 

```
tfb_output/TFB_article_identification.tsv
tfb_output/non-TFB_articles.txt
```

eg. TFB_article_identification.tsv

```
PMID    PMCID   Evidence        Abstract        Experiment Description
24236068        PMC3827324      TFB article     The choice between alternative developmental pathways is primarily controlled at the level of transcription. Induction of meiosis in budding yeasts in response to nutrient levels provides a system to investigate the molecular basis of cellular decision-making. In Saccharomyces cerevisiae, entry into meiosis depends on multiple signals converging upon IME1, the master transcriptional activator of meiosis. Here we studied the regulation of the cis-acting regulatory element Upstream Activation Signal (UAS)ru, which resides within the IME1 promoter. Guided by our previous data acquired using a powerful high-throughput screening system, here we provide evidence that UASru is regulated by multiple stimuli that trigger distinct signal transduction pathways as follows: (i) The glucose signal inhibited UASru activity through the cyclic AMP (cAMP/protein kinase A (PKA) pathway, targeting the transcription factors (TFs), Com2 and Sko1; (ii) high osmolarity activated UASru through the Hog1/mitogen-activated protein kinase (MAPK) pathway and its corresponding TF Sko1; (iii) elevated temperature increased the activity of UASru through the cell wall integrity pathway and the TFs Swi4/Mpk1 and Swi4/Mlp1; (iv) the nitrogen source repressed UASru activity through Sum1; and (v) the absence of a nitrogen source was detected and transmitted to UASru by the Kss1 and Fus3 MAPK pathways through their respective downstream TFs, Ste12/Tec1 and Ste12/Ste12 as well as by their regulators Dig1/2. These signaling events were specific to UASru; they did not affect the mating and filamentation response elements that are regulated by MAPK pathways. The complex regulation of UASru through all the known vegetative MAPK pathways is unique to S. cerevisiae and is specific for IME1, likely because it is the master regulator of gametogenesis.     Chromatin Immunoprecipitation (ChIP) ChIP assays were performed essentially as described [10].
```

>**Column descriptions:**

>* PMID: PubMed ID of the article.
>* Evidence: TFB/TFR article, if it contains TFB/TFR evidence; non-TFB//non-TFR article, if it does not describe TFB or TFR evidence.
>* Abstract: abstract of the paper.
>* Experiment Description: The sentence that may contain information of the experiment carried out in this research.

eg. non-TFB_articles.txt

```
PMID    Evidence    Abstract
10940042    non-TFB article    The phenotype of an organism is the manifestation of its expressed genome. The gcr1 mutant of yeast grows at near wild-type rates on nonfermentable carbon sources but exhibits a severe growth defect when grown in the presence of glucose, even when nonfermentable carbon sources are available. Using DNA microarrays, the genomic expression patterns of wild-type and gcr1 mutant yeast growing on various media, with and without glucose, were compared. A total of 53 open reading frames (ORFs) were identified as GCR1 dependent based on the criterion that their expression was reduced twofold or greater in mutant versus wild-type cultures grown in permissive medium consisting of YP supplemented with glycerol and lactate. The GCR1-dependent genes, so defined, fell into three classes: (i) glycolytic enzyme genes, (ii) ORFs carried by Ty elements, and (iii) genes not previously known to be GCR1 dependent. In wild-type cultures, GCR1-dependent genes accounted for 27% of the total hybridization signal, whereas in mutant cultures, they accounted for 6% of the total. Glucose addition to the growth medium resulted in a reprogramming of gene expression in both wild-type and mutant yeasts. In both strains, glycolytic enzyme gene expression was induced by the addition of glucose, although the expression of these genes was still impaired in the mutant compared to the wild type. By contrast, glucose resulted in a strong induction of Ty-borne genes in the mutant background but did not greatly affect their already high expression in the wild-type background. Both strains responded to glucose by repressing the expression of genes involved in respiration and the metabolism of alternative carbon sources. Thus, the severe growth inhibition observed in gcr1 mutants in the presence of glucose is the result of normal signal transduction pathways and glucose repression mechanisms operating without sufficient glycolytic enzyme gene expression to support growth via glycolysis alone.
```

>**Column descriptions:**

>* PMID: PubMed ID of the article.
>* Evidence: non-TFB/non-TFR article, if it does not describe TFB or TFR evidence.
>* Abstract: Abstract of the paper.

### **Stage II Outputs**

Stage II outputs contain the following: 

```
tfb_output/TF-gene_transcriptional_relation_summary.tsv
tfb_output/TF-gene_Pair_Details/ 
tfb_ouptut/download_xml/
```


eg.  TF-gene\_transcriptional\_relation\_summary.tsv

```
TF_ORF  TF_Alias        Gene_ORF        Gene_Alias      Relation        PMIDs
YBL103C YBL103CP|RTG3|RTG3P     YCR005C CIT2    TFB     10490611
YBL103C YBL103CP|RTG3|RTG3P     YCR005C CIT2    TFR     10490611
YBL103C YBL103CP|RTG3|RTG3P     YLR304C ACO1|GLU1       TFB     10490611
YBL103C YBL103CP|RTG3|RTG3P     YLR304C ACO1|GLU1       TFR     10490611
YBL103C YBL103CP|RTG3|RTG3P     YNL037C IDH1    TFB     10490611
YBL103C YBL103CP|RTG3|RTG3P     YNL037C IDH1    TFR     10490611
YBL103C YBL103CP|RTG3|RTG3P     YNR001C CIT1|CS1|LYS6   TFB     10490611
YBL103C YBL103CP|RTG3|RTG3P     YNR001C CIT1|CS1|LYS6   TFR     10490611
YBL103C YBL103CP|RTG3|RTG3P     YOR136W IDH2    TFB     10490611
YBL103C YBL103CP|RTG3|RTG3P     YOR136W IDH2    TFR     10490611
YGL252C YGL252CP|RTG2|RTG2P     YBL103C RTG3    TFB     10490611
YGL252C YGL252CP|RTG2|RTG2P     YLR304C ACO1|GLU1       TFB     10490611
YGL252C YGL252CP|RTG2|RTG2P     YLR304C ACO1|GLU1       TFR     10490611
YGL252C YGL252CP|RTG2|RTG2P     YNL037C IDH1    TFB     10490611
YGL252C YGL252CP|RTG2|RTG2P     YNL037C IDH1    TFR     10490611
YGL252C YGL252CP|RTG2|RTG2P     YNR001C CIT1|CS1|LYS6   TFB     10490611
YGL252C YGL252CP|RTG2|RTG2P     YNR001C CIT1|CS1|LYS6   TFR     10490611

```

>**Column descriptions:**

>* TF\_ORF: TF ORF names.
>* TF_Alias: The aliases of the TF.
>* Gene_ORF: gene ORF names.
>* Gene_Alias: The aliases of the gene.
>* Relation: TF binding (TFB) relations or TF regulatory (TFR) relations.
>* PMIDs: PubMed IDs that support the TF-gene transcriptional relation pairs.

You can find the folder named "TF-gene\_Pair\_Details" in the output folder. In this folder, subdirectories named TFB and TFR and the corresponding {TF}\_{GENE} folders specify the detailed sentence descriptions in the file named {PMID}.txt.

eg. TFB/YPR065W_YOR011W/23435728.txt

```
TF_ORF  TF_Alias        Gene_ORF        Gene_Alias      PMID    Evidence        Sentence_Description
YGL252C YGL252CP|RTG2|RTG2P     YNR001C CIT1|CS1|LYS6   10490611        TF-gene binding pair We show that as the cells' respiratory function is reduced or eliminated, the expression of four TCA cycle genes, CIT1, ACO1, IDH1, and IDH2, switches from HAP control to control by three genes, RTG1, RTG2, and RTG3.
```

>**Column descriptions:**

>* TF_ORF: TF ORF names.
>* TF_Alias: The aliases of the TF.
>* Gene_ORF: gene ORF names.
>* Gene_Alias: The aliases of the gene.
>* PMID: PubMed ID of the article.
>* Evidence: binding/regulatory relation identified for the TF-gene pairs.
>* Sentence_Description: Sentence descriptions for the TF-gene pair found in the article that supports the evidence.