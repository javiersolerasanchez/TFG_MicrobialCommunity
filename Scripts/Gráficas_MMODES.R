library(tidyverse)
library("ggpubr")
library(readr)

plot <- read_delim("C:/Users/Javier/Desktop/Datos/Normal_con_P/atr2.9/plot.tsv", 
                   "\t", escape_double = FALSE, trim_ws = TRUE)
colnames(plot)[2]<- "H_stevensii"

#La primera gráfica tiene fondo blanco y grid. La de abajo es transparente, para que al superponer 
#en Inkscape no dé problemas.
#Ese es el factor de conversión calculado para que se mantengan las unidades.
organism <- ggplot(data = plot, mapping = aes(x = time)) + 
  geom_line(aes(y = Halobacillus_sp*5.23790729, colour="Halobacillus_sp"), size=1, alpha=0.8) +
  geom_line(aes(y = kb_g_684_fbamdl3_Arthrobacter*5.23790729, colour="Arthrobacter"), size=1, alpha=0.8) +
  geom_line(aes(y = H_stevensii*5.23790729, colour="H_stevensii"), size=1, alpha=0.8) +
  #ggtitle("Biomasa") +
  scale_colour_manual("", 
                      values = c("Halobacillus_sp"="blue", "Arthrobacter"="green", 
                                 "H_stevensii"="red")) +
  scale_x_continuous(name="Time", labels=waiver()) +
  scale_y_continuous(name="Organism (g/L)") +
  theme_light() +
  #theme(panel.grid.major = element_blank(),
   #     panel.grid.minor = element_blank()) +
  #theme(panel.background = element_rect(fill = "transparent")) +
  theme(legend.position="top") +
  theme(plot.title = element_text(hjust = 0.5))

organism

metabolites <- ggplot(data = plot, mapping = aes(x = time)) + 
  geom_line(aes(y = cpd03959_e0*5.239825046, colour="Atrazina"), size=1, alpha=0.8, linetype="longdash") +
  geom_line(aes(y = cpd00027_e0*5.239825046, colour="Glucosa"), size=1, alpha=0.8, linetype="longdash") +
  #geom_line(aes(y = cpd00009_e0*5.239825046, colour="Fosfato"), size=1, alpha=0.6, linetype="longdash") +
  #ggtitle("Metabolitos") +
  scale_colour_manual("", 
                      values = c("Atrazina"="purple", "Glucosa"="orange", 
                                 "Fosfato"="grey")) +
  scale_x_continuous(name="Time", labels=waiver()) +
  scale_y_continuous(name="Metabolites (mmol/L)", position="right") +
  #Este tema de por sí tiene el fondo transparente. Las líneas de abajo eliminan el grid y el fondo(si lo tuviera)
  theme_minimal() +
  theme(panel.grid.major = element_blank(),
        panel.grid.minor = element_blank()) +
  theme(panel.background = element_rect(fill = "transparent")) +
  theme(legend.position="top") +
  theme(plot.title = element_text(hjust = 0.5))

metabolites



yourplot <- ggarrange(organism, metabolites, 
          ncol = 1, nrow = 2,
          align="hv")

ggsave(filename="yourfile.pdf", 
       plot = yourplot, 
       device = cairo_pdf, 
       width = 210, 
       height = 270, 
       units = "mm")

