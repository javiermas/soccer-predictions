
setwd("~/Desktop/soccer-predictions")
all_data <- read.csv('Football/all_data/combined_data.csv')

## Test some stuff
temp <- subset(all_data, Div == 'D1', select = c('PSA', 'Date'))

## Subset only features from list (TBD)

feature_list <- c(
                'Attendance',
                'Referee' ,
                'HS' ,
                'AS' ,
                'HST' ,
                'AST' ,
                'HHW' ,
                'AHW' ,
                'HC' ,
                'AC' ,
                'HF' ,
                'AF' ,
                'HO' ,
                'AO' ,
                'HY',
                'AY' ,
                'HR' ,
                'AR' ,
                'HBP' ,
                'ABP' )

match_vars <- c('Div',
              'Date',
              'AwayTeam',
              'HomeTeam',
              'FTHG',
              'FTAG',
              'FTR',
              'HTHG',
              'HTAG',
              'HTR')

## Subset feature list (match stats) with no Nas)
complete_df <- all_data[!is.na(all_data[feature_list]),]

## Extract and remove duplcated columns
data <- complete_df[,as.vector(rbind(match_vars, feature_list))]
data <- data[, !duplicated(t(data))]





