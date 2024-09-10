#### R script for generating a heatmap from NER similarity data

## Install complex heatmap if not installed
if (!requireNamespace("ComplexHeatmap", quietly=TRUE)) {
    if (!requireNamespace("BiocManager", quietly=TRUE)) {
        install.packages("BiocManager", repos = "http://cran.us.r-project.org")
    }
    BiocManager::install("S4Vectors")
    BiocManager::install("IRanges")
    BiocManager::install("ComplexHeatmap")
}

## load libraries
library(ComplexHeatmap)
library(tidyverse)
library(optparse)

option_list <- list(
    make_option(c("-i", "--input_file"), type = "character", default = NULL, help = "literature evaluation file", metavar="character"),
    make_option(c("-o", "--output_directory"), type = "character", default = NULL, help = "output directory for heatmaps", metavar="character"),
    make_option(c("-s", "--search_type"), type = "character", default = NULL, help = "type of literature search", metavar="character")
)

opt_parse <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parse)


### Data
evaluation_df <- read.csv(opt$input_file)

## filter duplicate rows and duplicate terms

evaluation_df <- evaluation_df %>%
    distinct( Pathway_Term, NER_Term,  Cosine_Similarity,Algorithm,Pathway_ID, NER_ID, .keep_all = T)

## averagePathwayTerm computes the average similarities between each pathway term and all NER terms in a pathway
averagePathwayTerm <- function(df) {

    ## find all unique algorithms
    algorithms <- unique(df$Algorithm)
    
    ### average over compared pathway
    avg <- df %>%
        group_by(Algorithm,Pathway_Term,Pathway_ID, NER_ID)%>%
        summarise(Average = mean(Cosine_Similarity), .groups = "keep")

    return(avg)
}

## averagePathwayTerm computes the average similarities between each pathway term and all NER terms in a pathway
averageNER <- function(df) {

    ## find all unique algorithms
    algorithms <- unique(df$Algorithm)
    
    ### average over compared pathway
    avg <- df %>%
        group_by(Algorithm,Pathway_ID, NER_ID)%>%
        summarise(Average = mean(Average), .groups = "keep")

    return(avg)
}




averageData <- function(average_data, algorithm) {

    ### average over compared pathway
    avg_ner <- average_data %>%
        group_by(Algorithm,Pathway_ID, Compared_Pathway)%>%
        summarise(Average = mean(Average_Cosine_Similarity), .groups = "keep")

    res <- avg_ner %>%
        filter(Algorithm == algorithm) %>%
        pivot_wider(names_from = Compared_Pathway,
                    values_from = Average
                    ) %>%
        column_to_rownames("Pathway_ID") %>%
        select(-Algorithm)

    return(res)
}


stouffers <- function(z1,z2) {
    combined_z <-  sum(z1,z2)/sqrt(2)
    return(combined_z)
}

zScoreData <- function(df) {
    z1 <- t(apply(df, 1,scale))
    z2 <- apply(df, 2,scale)

    combined_z <- sapply(1:ncol(z1), function(i) {
        sapply(1:nrow(z1), function(j) {
            stouffers(z1[j,i],z2[j,i])
        })
    })

    colnames(combined_z) <- colnames(df)
    rownames(combined_z) <- rownames(df)

    return(combined_z)
}
    
    
    

averageHeatmap <- function(df, algorithm) {

    p1 <- Heatmap(t(df),
                 name = "Average similarity \ndifference from original",
                 row_dend_reorder = FALSE, 
                 column_dend_reorder = FALSE, 
                 show_row_dend = FALSE, 
                 show_column_dend = FALSE,
                 row_order = colnames(df),
                 column_order = rownames(df),
                 show_row_names = TRUE, 
                 show_column_names =TRUE,
                 heatmap_legend_param = list(direction = "horizontal"),
                 column_title = algorithm,
                 row_title = "Abstract terms",
                 row_title_side = "left",
                 column_title_side = "top"
                 )
    return(p1)
}

HeatmapWrapper <- function(df) {
    pathway_term_avg <- averagePathwayTerm(df)
    ner_pathway_avg <- averageNER(pathway_term_avg)

    algorithms <- unique(ner_pathway_avg$Algorithm)

    plots <- lapply(algorithms, function(x) {
        toplot <- ner_pathway_avg %>%
            filter(Algorithm == x) %>%
            pivot_wider(names_from = NER_ID, values_from = Average) %>%
            column_to_rownames("Pathway_ID") %>%
            select(-Algorithm)
        averageHeatmap(toplot,x)
    })


    return(plots)
}

pdfOutWrapper <- function(df, condition) {
        heatmaps <-  HeatmapWrapper(df)
        suppressWarnings(c_heatmaps <-  heatmaps[[1]] + heatmaps[[2]] + heatmaps[[3]])
        pdf(paste0(opt$output_directory,"/average_",condition,"_",opt$search_type,".pdf"), width = 18, height = 8)
        print(paste("outputting ", condition, "heatmap at ", paste0(opt$output_directory,"/average_",condition,"_",opt$search_type,".pdf")))
        draw(c_heatmaps, heatmap_legend_side = "bottom", column_title = paste0("Average similarity  ---  ",opt$search_type,"_",condition))
        dev.off()
}

## create output directory
if(!dir.exists(opt$output_directory)) {
    dir.create(opt$output_directory)
}


## baseline
pdfOutWrapper(evaluation_df, "All_terms")

## ### drop terms not mapped to IDF
## w_idf <- evaluation_df %>%
##     filter(!is.na(IDF))
## pdfOutWrapper(w_idf, "no_IDF_terms")


## ### Impute missing terms with min value and weight similarities by term
## min_impute_idf <- evaluation_df %>%
##     mutate(new_IDF = replace_na(IDF, min(IDF, na.rm = T))) %>%
##     mutate(Average_Cosine_Similarity = Average_Cosine_Similarity * new_IDF)
## pdfOutWrapper(min_impute_idf, "IDF_weighted_impute_with_min(IDF)")


## ### Impute missing terms with the median value and weight similarities by term
## median_impute_idf <- evaluation_df %>%
##     mutate(new_IDF = replace_na(IDF, median(IDF, na.rm = T))) %>%
##     mutate(Average_Cosine_Similarity = Average_Cosine_Similarity * new_IDF)
## pdfOutWrapper(median_impute_idf, "IDF_weighted_impute_with_median(IDF)")

## ### filter those without IDF and weight similarities by term
## w_idf_weighted <- evaluation_df %>%
##     filter(!is.na(IDF)) %>%
##     mutate(Average_Cosine_Similarity = Average_Cosine_Similarity * IDF)

## pdfOutWrapper(w_idf_weighted, "IDF_filtered_IDF_weighted")



