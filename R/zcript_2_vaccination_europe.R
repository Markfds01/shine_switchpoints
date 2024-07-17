library(dplyr)
library(cowplot)
library(ISOweek)
source("theme.R")

# Switchpoints
data = read.csv("../results/results_summary.csv") %>%
	mutate(date_1 = as.Date(orig_date) + switchpoint_0,
		date_1_low = as.Date(orig_date) + switchpoint_0_2.5,
		date_1_high = as.Date(orig_date) + switchpoint_0_97.5,
		date_2 = as.Date(orig_date) + switchpoint_1,
		date_2_low = as.Date(orig_date) + switchpoint_1_2.5,
		date_2_high = as.Date(orig_date) + switchpoint_1_97.5) %>%
	arrange(date_1)

data = data.frame(region = rep(data$region, 2),
			rate = c(data$date_1, data$date_2),
			low = c(data$date_1_low, data$date_2_low),
			high = c(data$date_1_high, data$date_2_high),
			label = c(rep('change 1', nrow(data)), rep('change 2', nrow(data)))
		)

data = data %>% filter(nchar(region) != 2)

regions = data.frame(label = unique(data$region), id = 1:length(unique(data$region)))
data$y = regions$id[match(data$region, regions$label)]

# Vaccination
vac = read.csv("../data/ECDC/vaccination/data.csv") %>%
	group_by(YearWeekISO, ReportingCountry, Denominator, Region, TargetGroup) %>%
	summarize(FirstDose = sum(FirstDose), SecondDose = sum(SecondDose)) %>%
	mutate(date = ISOweek2date(paste0(YearWeekISO, "-1")))


plot_vac = function(vac, data, abv, r) {

	vac = vac %>% 
		filter(ReportingCountry == abv) %>% 
		filter(TargetGroup == age_group) %>%
		filter(Region == abv)

	vac = vac %>% ungroup() %>%
		mutate(FirstDose = cumsum(FirstDose), SecondDose = cumsum(SecondDose))

	data = data %>% filter(region == r)

	p = ggplot() +
		theme_custom() +
		geom_line(data = vac, aes(x = date, y = FirstDose * 100 / Denominator)) +
		geom_vline(data = data, aes(xintercept = rate, group = label), linetype = "dashed") +
		#scale_x_continuous(expand = c(0, 0), limits = c(0, 12), breaks = seq(0, 12, by = 2)) +
		scale_y_continuous(expand = c(0, 0), limits = c(0, 100), breaks = seq(0, 100, by = 25)) +
		xlab("") +
		ylab("vaccination (%)") +
		theme(legend.title = element_blank(),
			legend.position = "top") +
		scale_x_date(date_breaks = "6 month", date_labels = "%b %Y", 
			limits = as.Date(c("2021-01-01", "2022-12-31"))) +
		ggtitle(r)

	return(p)
}

age_group = "Age50_59"

pA = plot_vac(vac, data, "ES", "Spain")
pB = plot_vac(vac, data, "DE", "Germany")
pC = plot_vac(vac, data, "IT", "Italy")
pD = plot_vac(vac, data, "FR", "France")
pE = plot_vac(vac, data, "BE", "Belgium")
pF = plot_vac(vac, data, "CZ", "Czechia")

Sys.setlocale( category = "LC_TIME", locale = "en_GB.UTF-8" )

pdf(paste0("../plots/vac_", age_group, ".pdf"), width = 30, height = 12)
plot_grid(pA, pB, pC, pD, pE, pF, nrow = 2, align = "v", labels = age_group, label_size = 40)
dev.off()

