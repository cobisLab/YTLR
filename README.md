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
python main.py -i <path to input directory> -d <tfb/tfr/both> -check <0/1> -o <path to the output directory>
```

>**Required arguments:**

>* -i: The input data directory path.

>* -d: Specify the type of TF-gene association to consider ('tfb', 'tfr', or 'both', default = 'both').

>* -check: Check if the article relates to the yeast species (1 --> check, 0 -> do not check, default = 1).

>* -o: The output directory for the results. 


# Example and Output Results

If we use the example inputs with the example command:

```
python main.py -i ./sample_input -d tfb -check 1 -o tfb_output
```

The results will be generated in the tfb_output folder. 

**SAMPLE OUTPUTS**

```
tfb_output/ - TFB_article_identification.tsv
            - TF-gene_transcriptional_relation_summary.tsv
            - Experimental_condition_summary.tsv
            - pmids_cannot_find_fullText.txt
            - TF-gene_Pair_Details/ - TFB/ - YPR065W_YOR011W/ - 23435728.txt
                                           - {TF_ORF}_{GENE_ORF}/ - {PMID}.txt

                                    - TFR/
```

>**File descriptions:**

>* **{TFB/TFR}\_article\_identification.tsv:** Articles contain TFB or TFR evidence.
>* **TF-gene\_transcriptional\_relation\_summary.tsv:** Summary of Stage II outputs.
>* **Experimental\_condition\_summary.tsv:** paragraph contains a potential experiment and potential experimental condition.
>* **pmids\_cannot\_find\_fullText.txt:** contains several PMIDs that can not be found in full text and this file lists per pmid a line. if there is not exist full content of pmids not found, the content of the file will be empty.
>* **TF-gene\_Pair\_Details/{TFB/TFR}/{TF\_ORF}\_{GENE\_ORF}/{PMID}.txt:** Evidence for supportting the TF-gene pair found in the article.

### **Stage I Outputs**

Stage I outputs contain the following: 

```
tfb_output/TFB_article_identification.tsv
```

Example: 

```
PMID    Evidence        Abstract
25957495    TFB article    Chromatin modification enzymes are important regulators of gene expression and some are evolutionarily conserved from yeast to human. Saccharomyces cerevisiae is a major model organism for genome-wide studies that aim at the identification of target genes under the control of conserved epigenetic regulators. Ume6 interacts with the upstream repressor site 1 (URS1) and represses transcription by recruiting both the conserved histone deacetylase Rpd3 (through the co-repressor Sin3) and the chromatin-remodeling factor Isw2. Cells lacking Ume6 are defective in growth, stress response, and meiotic development. RNA profiling studies and in vivo protein-DNA binding assays identified mRNAs or transcript isoforms that are directly repressed by Ume6 in mitosis. However, a comprehensive understanding of the transcriptional alterations, which underlie the complex ume6Î mutant phenotype during fermentation, respiration, or sporulation, is lacking. We report the protein-coding transcriptome of a diploid MAT a/Î± wild-type and ume6/ume6 mutant strains cultured in rich media with glucose or acetate as a carbon source, or sporulation-inducing medium. We distinguished direct from indirect effects on mRNA levels by combining GeneChip data with URS1 motif predictions and published high-throughput in vivo Ume6-DNA binding data. To gain insight into the molecular interactions between successive waves of Ume6-dependent meiotic genes, we integrated expression data with information on protein networks. Our work identifies novel Ume6 repressed genes during growth and development and reveals a strong effect of the carbon source on the derepression pattern of transcripts in growing and developmentally arrested ume6/ume6 mutant cells. Since yeast is a useful model organism for chromatin-mediated effects on gene expression, our results provide a rich source for further genetic and molecular biological work on the regulation of cell growth and cell differentiation in eukaryotes.
```

>**Column descriptions:**

>* PMID: PubMed ID of the article.
>* Evidence: TFB/TFR article, if it contains TFB/TFR evidence; non-TFB//non-TFR article, if it does not describe TFB or TFR evidence.
>* Abstract: abstract of the paper.

### **Stage II Outputs**

Stage II outputs contain the following: 

```
tfb_output/TF-gene_Pair_Details/ 
tfb_output/TF-gene_transcriptional_relation_summary.tsv
tfb_ouptut/Experimental_condition_summary.tsv
```

You can find the folder named "TF-gene\_Pair\_Details" in the output folder. In this folder, subdirectories named TFB and TFR and the corresponding {TF}\_{GENE} folders specify the detailed sentence descriptions in the file named {PMID}.txt.

eg. TFB/YPR065W_YOR011W/23435728.txt

```
TF_ORF  TF_Alias        Gene_ORF        Gene_Alias      PMID    Evidence        Sentence_Description
YPR065W YPR065WP|ROX1|ROX1P|REO1|REO1P  YOR011W AUS1    23435728        binding Several genes which encode diverse transport functions of the cell were identified here to be overexpressed in the mot3 rox1 mutant strain. These genes are FET4, ZRT1, HXT9, ATO3, PHO89, YHK8, YCT1, and AUS1, involved in iron, zinc, sugar, ammonia, phosphate, multidrug, cysteine, and sterol transport, respectively.<sep>These genes are FET4, ZRT1, HXT9, ATO3, PHO89, YHK8, YCT1, and AUS1, involved in iron, zinc, sugar, ammonia, phosphate, multidrug, cysteine, and sterol transport, respectively. In the case of the Fet4 alone, low-affinity iron permease, an oxygen-dependent regulation involving the Rox1 repressor function has been described previously (31, 32).<sep>Here, we identify more target genes repressed by Mot3 and Rox1 under acute salt stress which are related to sterol uptake and biosynthesis, such as ECM22, RTA1, SUT1, and AUS1 (Fig. 7).
```

>**Column descriptions:**

>* TF_ORF: TF ORF names.
>* TF_Alias: The aliases of the TF.
>* Gene_ORF: gene ORF names.
>* Gene_Alias: The aliases of the gene.
>* PMID: PubMed ID of the article.
>* Evidence: binding/regulatory relation identified for the TF-gene pairs.
>* Sentence_Description: Sentence descriptions for the TF-gene pair found in the article that supports the evidence.


eg.  TF-gene\_transcriptional\_relation\_summary.tsv

```
TF_ORF  TF_Alias        Gene_ORF        Gene_Alias      Relation        PMIDs
YDR207C YDR207CP|UME6|UME6P|CAR80|CAR80P|NIM2|NIM2P|RIM16|RIM16P        YBL078C ATG8|APG8|AUT7|CVT5     TFB     25957495
YDR207C YDR207CP|UME6|UME6P|CAR80|CAR80P|NIM2|NIM2P|RIM16|RIM16P        YBR116C         TFB     25957495
YDR207C YDR207CP|UME6|UME6P|CAR80|CAR80P|NIM2|NIM2P|RIM16|RIM16P        YIR016W         TFB     25957495
YDR207C YDR207CP|UME6|UME6P|CAR80|CAR80P|NIM2|NIM2P|RIM16|RIM16P        YMR101C SRT1    TFB     25957495
YDR207C YDR207CP|UME6|UME6P|CAR80|CAR80P|NIM2|NIM2P|RIM16|RIM16P        YJL089W SIP4    TFB     25957495
```

>**Column descriptions:**

>* TF\_ORF: TF ORF names.
>* TF_Alias: The aliases of the TF.
>* Gene_ORF: gene ORF names.
>* Gene_Alias: The aliases of the gene.
>* Relation: TF binding (TFB) relations or TF regulatory (TFR) relations.
>* PMIDs: PubMed IDs that support the TF-gene transcriptional relation pairs.


eg. Experimental\_condition\_summary.tsv

```
PMID    Experiment Description
10510295        Northern-blot analysis shows that the GLK1 gene is expressed at a basal level in the presence of glucose, de-repressed more than 6-fold under conditions of sugar limitation and more than 25-fold under conditions of ethanol induction.       Northern-blot analysis shows that the GLK1 gene is expressed at a basal level in the presence of glucose, de-repressed more than 6-fold under conditions of sugar limitation and more than 25-fold under conditions of ethanol induction.
23435728        Chromatin immunoprecipitation (ChIP) was performed as described previously (30).Quantitative PCR analyses at the indicated chromosomal loci were performed in real time using an Applied Biosystems 7500 sequence detector with the POL1 coding sequence (+1796/+1996) as an internal control.  Chromatin immunoprecipitation (ChIP) was performed as described previously (30).Quantitative PCR analyses at the indicated chromosomal loci were performed in real time using an Applied Biosystems 7500 sequence detector with the POL1 coding sequence (+1796/+1996) as an internal control.
```

>**Column descriptions:**

>* PMID: PubMed ID of the article.
>* Experiment Description: paragraph contains a potential experiment.

