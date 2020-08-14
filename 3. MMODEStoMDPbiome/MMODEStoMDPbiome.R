source("~/Escritorio/MMODEStoMDPbiome/initMMODEStoMDPbiome.R")
labelExp='~/Escritorio/OutputMMODES/Root_sin_P/results'
setwd(labelExp)

###USER-INTERACTION###
# Some useful commands are commented, that could be uncommented 
# if they are required.
# A.-To rename output files:
#folderList=list.files(pattern="atr2\\..*")
#lapply(folderList, rename.biomass.file, 'atr2.')
# B.- To replace comma by TAB
# Es necesario que este script esté dentro de la carpeta de los resultados de MMODES
# que vamos a transformar.
system("sh scriptCommaToTab.sh")

# Read biomass tables from MMODES
#file = list.files(pattern="biomass\\_[[:alnum:]]+\\.tsv")
file = list.files(pattern="^biomass\\_.*\\.tsv$")
# Add subject and sample ID per table
tables.list=lapply(file, process.one.biomass.file)
# Concatenate all biomass data.frames (one per subject) in a unique one
table.all=rbind.with.rownames(tables.list)
# Save
biomasses=table.all
save(biomasses,file='allTimeSeries_biomass.RData')
write.table(biomasses,file='allTimeSeries_biomass.tsv',sep='\t',quote=FALSE)


# Generate taxonomy table in file 'taxtable.tsv': OTU id + 7 rank
taxmat=read.table('~/Escritorio/OutputMMODES/taxtable.tsv',sep="\t",header=TRUE)
colnames(taxmat) <- c("Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species")
#complete.tax.table(taxmat,"Species")
num.strains=nrow(taxmat)
# Generate OTU table: id + biomass columns (depending on number of strains)
pos.pert.column=grep('Perturbations',colnames(biomasses))
num.metabolites=pos.pert.column-num.strains-1
otu.table.df=subset(biomasses, select=c(1:num.strains))
# Generate mapping table: all, except to biomasses
mapping.table.df=subset(biomasses, select=c((num.strains+1):ncol(biomasses)))
mapping.table.df$time=as.numeric(mapping.table.df$time)


# Build phyloseq object
otumat <- t(otu.table.df)
OTU = otu_table(otumat, taxa_are_rows = TRUE)
mapmat <- mapping.table.df
MAP = sample_data(mapmat)
TAX = tax_table(as.matrix(taxmat))
## If not complete tax_table levesls:
# taxmat = matrix(nrow=ntaxa(OTU),ncol=7)
# rownames(taxmat) <- taxa_names(OTU)
# taxmat = complete.tax.table(taxmat,"Species")
data = phyloseq(OTU, TAX, MAP)
save(data,file='phyloseqObject.RData')


# Get relative abundances
data.norm <- transform_sample_counts(data, function(x) x / sum(x) )
save(data.norm,file='data.norm_phyloseqObject.RData')


load('data.norm_phyloseqObject.RData')
data.norm.sub=subset_samples(data.norm,Perturbations!=FALSE)
###USER-INTERACTION###
# Next line: to be commented in 'Atrazine' case study, not to remove the initial samples with 'START': Because the initial points is also required, to compute the amount of atrazine degradation in the initial state
#data.norm.sub=subset_samples(data.norm.sub,Perturbations!='START')
#
data.norm=data.norm.sub # Robust clustering need the object is called data.norm!!!
save(data.norm,file='data.norm.sub_phyloseqObject.RData')
pdf('barplot_sampleWithPert_Phylum.pdf',width=30)
plot_bar(data.norm,fill='Phylum')
dev.off()
pdf('barplot_sampleWithPert_Species.pdf',width=30)
plot_bar(data.norm,fill='Species')
dev.off()

###USER-INTERACTION###
# Space for ad-hoc adjustment to the samples in the current case study, 
# before applying clustering to identify microbiome states
# It could be not required in many case studies

## Example of adjustment for soil microbiome case:
## Add a new variable, to differentiate sample of the same subject by its position in the time series, i.e. the sequence ID
# load('data.norm.sub_phyloseqObject.RData')
# for(sample in sample_names(data.norm)){
#   seq=unlist(strsplit(sample,'_'))[3]
#   sample_data(data.norm)[sample,'seqId'] <- seq
}
## To filter samples from state before and after the perturbation (seq T2 to T5).
# data.norm=subset_samples(data.norm, seqId %in% c('00002','00003','00004','00005'))
# save(data.norm,file='data.norm.sub_phyloseqObject.RData')
# 
# pdf('barplot_sampleWithPert_Phylum.pdf',width=30)
# plot_bar(data.norm,fill='Phylum')
# dev.off()
# pdf('barplot_sampleWithPert_Species.pdf',width=30)
# plot_bar(data.norm,fill='Species')
# dev.off()