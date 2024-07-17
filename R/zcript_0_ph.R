library(dplyr)
library(cowplot)
source("theme.R")

data = read.csv("../results/results_summary.csv") %>% arrange(rate_0)

data = data.frame(region = rep(data$region, 3),
			rate = c(data$rate_0, data$rate_1, data$rate_2),
			low = c(data$rate_0_2.5, data$rate_1_2.5, data$rate_2_2.5),
			high = c(data$rate_0_97.5, data$rate_1_97.5, data$rate_2_97.5),
			label = c(rep('rate 0', nrow(data)), rep('rate 1', nrow(data)), rep('rate 2', nrow(data)))
		)

# Spain
data_spain = data %>% filter(nchar(region) == 2) 

regions = data.frame(label = unique(data_spain$region), id = 1:length(unique(data_spain$region)))
data_spain$y = regions$id[match(data_spain$region, regions$label)]

ccaa = read.csv("../data/provinces_iso.csv") %>% select(ccaa_iso, ccaa_name)
ccaa = unique(ccaa)

regions$label = ccaa$ccaa_name[match(regions$label, ccaa$ccaa_iso)]

plot_ph = function(data) {

	p = ggplot(data) +
		theme_custom() +
		geom_point(aes(x = rate, y = y, shape = label, color = label), size = 6) +
		geom_errorbarh(aes(xmax = high, xmin = low, y = y, color = label)) +
		scale_x_continuous(expand = c(0, 0), limits = c(0, 12), breaks = seq(0, 12, by = 2)) +
		scale_y_continuous(expand = c(0, 0), breaks = regions$id, labels = regions$label) +
		xlab("admission probability") +
		ylab("") +
		theme(legend.title = element_blank(),
			legend.position = "top")

	return(p)
}

pA = plot_ph(data_spain) + theme(axis.text.x = element_blank(), axis.title.x = element_blank())

# Europe
data_europe = data %>% filter(nchar(region) != 2)

regions = data.frame(label = unique(data_europe$region), id = 1:length(unique(data_europe$region)))
data_europe$y = regions$id[match(data_europe$region, regions$label)]

pB = plot_ph(data_europe) + theme(legend.position = "none")

pdf("../plots/ph.pdf", width = 10, height = 12)
plot_grid(pA, pB, nrow = 2, align = "v")
dev.off()

