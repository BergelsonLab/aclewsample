library(tidyverse)



df <- read_csv('../output/aclew_sample_new.csv') 

ggplot(df, aes(x=age_mo_round)) +
  geom_histogram(aes(fill=std_mat_ed), binwidth=3)

ggplot(df, aes(x=age_mo_round)) +
  geom_histogram(aes(fill=child_sex), binwidth=3)

ggplot(df, aes(x=age_mo_round)) +
  geom_histogram(aes(fill=child_sex), binwidth=4) +
  facet_grid(~corpus)

ggplot(df, aes(x=age_mo_round)) +
  geom_histogram(aes(fill=std_mat_ed), binwidth=4) +
  facet_grid(~corpus)

