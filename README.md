Suggested running environments: Linux Ubuntu 16.04.6, Python 3.8.5

To install the necessary packages, you can find them in requirements.txt
We recommend that you can use the conda package to create a new environment.
```
pip install -r requirements.txt
```

## **NOTICE**
You need to install the spacy model "en_core_web_trf" for StageII data preprocessing:
```
python -m spacy download en_core_web_trf
```

**STEPS TO USE**
1. Download the codes from the repo. Please skip it if you have done this step.

2. Change the working directory into the model codes.
   ```
   cd TFBTFRnlp
   ```
   
3. Download the model from the following link and unzip the file. Please skip it if you have done this step.
    ```
    wget https://cobisHSS0.im.nuk.edu.tw/YTLR/Model.tar.gz

    tar zxvf Model.tar.gz
    ```

4. For StageI, please prepare the txt file that contains an abstract that downloads from PubMed(https://pubmed.ncbi.nlm.nih.gov/).
    >***HOW TO GET ABSTRACT FROM PubMed***
    >>1. Browse the PubMed website(https://pubmed.ncbi.nlm.nih.gov/) and choose the paper you want.
    >>2. Click the ***save*** button.
    >>3. choose the ***Abstract(text)*** then create.
    >>4. The txt file containing the abstract of this paper will download immediately.
    >>![](https://i.imgur.com/Dq3pFeS.png)

    For SatgeII, please prepare the HTML file that contains full text which is downloaded from PMC(https://www.ncbi.nlm.nih.gov/pmc/).

    >***HOW TO GET FULL TEXT FROM PMC***
    >>1. Browse the PubMed website(https://www.ncbi.nlm.nih.gov/pmc/) and choose the paper you want.
    >>2. You can get the full content of the website using wget or request and save it as an HTML file.

   The same paper will be in the same directory, and the input directory can contain multiple paper directories.
   We provide an example input folder named small_input.
      
   **SAMPLE INPUT**
    ```
    small_input/ - 01/ - abstract-25957495.txt
                 - 02/ - abstract-25957495.txt
                       - PMC5469029.html

    .txt --> download from PubMed abstract (only abstract)
    .html --> download from PMC (full content)
    ```
   
5. Predict the results, and the results will save to the file that is specified with the -o parameter.
   We also provide an example output file for small_input named result_tfb.txt.

### ***StageI***
---
In folder StageI, you can execute main.py by this command:
```
python main.py -p ../small_input/ -d tfb -check 1 -o result.txt
```
The results will be written to result_tfb.txt in folder StageI, and the format of output will be like this:

```
PMID    Evidence        Abstract
25957495    TFB    Chromatin modification enzymes are important regulators of gene expression and some are evolutionarily conserved from yeast to human. Saccharomyces cerevisiae is a major model organism for genome-wide studies that aim at the identification of target genes under the control of conserved epigenetic regulators. Ume6 interacts with the upstream repressor site 1 (URS1) and represses transcription by recruiting both the conserved histone deacetylase Rpd3 (through the co-repressor Sin3) and the chromatin-remodeling factor Isw2. Cells lacking Ume6 are defective in growth, stress response, and meiotic development. RNA profiling studies and in vivo protein-DNA binding assays identified mRNAs or transcript isoforms that are directly repressed by Ume6 in mitosis. However, a comprehensive understanding of the transcriptional alterations, which underlie the complex ume6Δ mutant phenotype during fermentation, respiration, or sporulation, is lacking. We report the protein-coding transcriptome of a diploid MAT a/α wild-type and ume6/ume6 mutant strains cultured in rich media with glucose or acetate as a carbon source, or sporulation-inducing medium. We distinguished direct from indirect effects on mRNA levels by combining GeneChip data with URS1 motif predictions and published high-throughput in vivo Ume6-DNA binding data. To gain insight into the molecular interactions between successive waves of Ume6-dependent meiotic genes, we integrated expression data with information on protein networks. Our work identifies novel Ume6 repressed genes during growth and development and reveals a strong effect of the carbon source on the derepression pattern of transcripts in growing and developmentally arrested ume6/ume6 mutant cells. Since yeast is a useful model organism for chromatin-mediated effects on gene expression, our results provide a rich source for further genetic and molecular biological work on the regulation of cell growth and cell differentiation in eukaryotes.
```
Or
```
python main.py -p ../small_input/ -d tfr -check 1 -o result.txt
```
The results will be written to result_tfr.txt in folder StageI, and the format of output will be like this:
```
PMID    Evidence        Abstract
25957495    TFR    Chromatin modification enzymes are important regulators of gene expression and some are evolutionarily conserved from yeast to human. Saccharomyces cerevisiae is a major model organism for genome-wide studies that aim at the identification of target genes under the control of conserved epigenetic regulators. Ume6 interacts with the upstream repressor site 1 (URS1) and represses transcription by recruiting both the conserved histone deacetylase Rpd3 (through the co-repressor Sin3) and the chromatin-remodeling factor Isw2. Cells lacking Ume6 are defective in growth, stress response, and meiotic development. RNA profiling studies and in vivo protein-DNA binding assays identified mRNAs or transcript isoforms that are directly repressed by Ume6 in mitosis. However, a comprehensive understanding of the transcriptional alterations, which underlie the complex ume6Δ mutant phenotype during fermentation, respiration, or sporulation, is lacking. We report the protein-coding transcriptome of a diploid MAT a/α wild-type and ume6/ume6 mutant strains cultured in rich media with glucose or acetate as a carbon source, or sporulation-inducing medium. We distinguished direct from indirect effects on mRNA levels by combining GeneChip data with URS1 motif predictions and published high-throughput in vivo Ume6-DNA binding data. To gain insight into the molecular interactions between successive waves of Ume6-dependent meiotic genes, we integrated expression data with information on protein networks. Our work identifies novel Ume6 repressed genes during growth and development and reveals a strong effect of the carbon source on the derepression pattern of transcripts in growing and developmentally arrested ume6/ume6 mutant cells. Since yeast is a useful model organism for chromatin-mediated effects on gene expression, our results provide a rich source for further genetic and molecular biological work on the regulation of cell growth and cell differentiation in eukaryotes.
```
>**column description**
>* PMID: Paper id in PubMed.
>* Evidence: TFB/non-TFB, TFR/non-TFR. If it has direct(TFB) or indirect(TFR) relation of yeast or Saccharomyces cerevisiae.
>* Abstract: Abstract of the paper.



### ***StageII***
---
In folder StageII, you can execute main.py by this command:
```
python main.py -p ../small_input/ -d tfb -check 1 -o result.txt
```
The results will be written to result_tfb.txt in folder StageII, and the format of output will be like this:
```
TF_ORF    TF_Alias    Gene_ORF    Gene_Alias    PMID    Evidence    Sentence_Description
YDR207C    UME6/UME6P/CAR80/CAR80P/NIM2/NIM2P/RIM16/RIM16P    YMR101C    SRT1    25957495    binding    Our approach was designed to cover changes in RNA levels during growth and development related to the deletion of UME6 as broadly as possible. As a consequence, we identified all core Ume6 target genes determined in an earlier RNA profiling study (Williams et al. 2002), apart from the dubious gene YBR116C not represented on the Yeast Genome 2.0 GeneChip, and YIR016W and YMR101C that are not differentially expressed in the current study.<sep>As a consequence, we identified all core Ume6 target genes determined in an earlier RNA profiling study (Williams et al. 2002), apart from the dubious gene YBR116C not represented on the Yeast Genome 2.0 GeneChip, and YIR016W and YMR101C that are not differentially expressed in the current study.
```
Or
```
python main.py -p ../small_input/ -d tfr -check 1 -o result.txt
```
The results will be written to result_tfr.txt in folder StageII, and the format of output will be like this:
```
TF_ORF    TF_Alias    Gene_ORF    Gene_Alias    PMID    Evidence    Sentence_Description
YDR207C    UME6/UME6P/CAR80/CAR80P/NIM2/NIM2P/RIM16/RIM16P    YFL039C    ACT1/ABY1/END7/ACTIN    25957495    regulatory    In all cases, we find that RT-PCR assays of wild-type and ume6 mutant samples cultured in growth media (YPD, YPA) and sporulation medium (SPII) reiterate the pattern obtained with GeneChips; ACT1 was used as a loading control (Fig. 5b).<sep>In all cases, we find that RT-PCR assays of wild-type and ume6 mutant samples cultured in growth media (YPD, YPA) and sporulation medium (SPII) reiterate the pattern obtained with GeneChips; ACT1 was used as a loading control (Fig. 5b). We next used protein network data to explore the interactions among Ume6-dependent proteins shown in Fig. 5.
```
>**column description**
>* TF_ORF: The protein of gene.
>* TF_Alias: The alias of gene.
>* Gene_ORF: The protein of gene.
>* Gene_Alias: The alias of gene.
>* PMID: Paper id in PubMed.
>* Evidence: binding/regulatory. If it has evidence in pair to prove the TF and Gene relation.
>* Sentence_Description: Sentences of the paper which contain pair TF and Gene.


### ***USAGE***
---
```
python main.py -p <input_data_directory_path> -d <tfb/tfr/both> -check <0/1> -o <output_file.txt>
```
>**Required arguments:**
>* -p: The input data directory path, which contains several subdirectories, and each subdirectory contains one paper( at least contain the HTML file downloaded from PMC, you also can put a txt file downloaded from PUBMED in the same directory).
>* -d: Specify direct or indirect or both, tfb --> direct, tfr --> indirect, both --> direct and indirect
>* -check: Specify check input title contains keyword, default 1, 1 --> check, 0 -> not check.
>* -o: The output filename of the result. For example, the output filename is "result.txt", and if choose tfb, the output file will be named "result_tfb.txt", if choose both, output files will contain "result_tfb.txt" and "result_tfr.txt".
