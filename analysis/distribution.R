library(tidyverse)



df <- read_csv('../output/aclew_sample_optim.csv') 



df$mated <- recode(df$std_mat_ed, unknown='05_unknown', bhs='04_bhs', hs='03_hs', sc='02_sc', cd='01_cd', ad='00_ad')


mated <- ggplot(df, aes(x=age_mo_round)) +
            geom_histogram(aes(fill=mated), binwidth=3)
mated
ggsave("sample_mated.pdf", device='pdf')



gender <- ggplot(df, aes(x=age_mo_round)) +
            geom_histogram(aes(fill=child_sex), binwidth=3)
gender
ggsave("sample_gender.pdf", device='pdf')


gender_bylab <- ggplot(df, aes(x=age_mo_round)) +
                  geom_histogram(aes(fill=child_sex), binwidth=4) +
                  facet_grid(~corpus)
gender_bylab
ggsave("sample_bylab_gender.pdf", device='pdf')


mated_bylab <- ggplot(df, aes(x=age_mo_round)) +
                geom_histogram(aes(fill=mated), binwidth=4) +
                facet_grid(~corpus)
mated_bylab
ggsave("sample_bylab_mated.pdf", device='pdf')


corpus_dist <- ggplot(df, aes(x=age_mo_round)) +
                geom_histogram(aes(fill=corpus), binwidth=3)
corpus_dist
ggsave("sample_fill_bycorpus.pdf", device='pdf')

total_gender <- ggplot(df, aes(child_sex)) +
                  geom_histogram(stat='count', aes(fill=child_sex))
total_gender
ggsave("total_gender.pdf", device='pdf')
