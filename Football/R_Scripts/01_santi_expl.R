rm(list=ls())

setwd("~/Desktop/soccer-predictions/Football/all_data")
# all_data <- read.csv('Football/all_data/combined_data.csv')

library(plyr)


## ----------- Combine Data ------------ ## 

years_for_search_and_extract = c('1718','1617','1516','1415','1314','1213','1112',
                                '1011','0910','0809','0708','0607','0506','0405',
                                '0304','0203','0102','0001','9900','9899','9798')

combined.df <- list()

for (i in 1:length(years_for_search_and_extract)){
  
    
  setwd(paste("~/Desktop/soccer-predictions/Football/all_data",years_for_search_and_extract[i],sep='/'))
  
    files  <- list.files(pattern = '\\.csv')
    
    # read files into a list - are there headers?
    
    tables <- lapply(files, read.csv, header = TRUE)
    
    # rbind files
    
    combined.df[[i]] <- do.call(rbind.fill , tables)
    combined.df[[i]]$Season <- rep(years_for_search_and_extract[i], nrow(combined.df[[i]]))
    
}

all_data <- do.call(rbind.fill, combined.df[])

## ----------- Var list/ Clean ------------- ## 

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
                'ABP' ,
                'HFKC',
                'AFKC')

match_vars <- c('Div',
              'Date',
              'AwayTeam',
              'HomeTeam',
              'FTHG',
              'FTAG',
              'FTR',
              'HTHG',
              'HTAG',
              'HTR',
              'Season')


## Extract, order, clean
data <- all_data[,as.vector(rbind(match_vars, feature_list))]
data <- data[is.na(data$FTR)==FALSE,]
data<- data[order(as.Date(data$Date, format="%d/%m/%y")),]


## --------------- Features ------------- ##

## Create target  
target <- ifelse(data$FTR=='H', 1, 0)

## ----------------------------------------- FT AGG goals -------------------------------------------- ##
## Agg Home goals feature

# datalist1 <- list()
# agg_goals.df <- list()
# 
# for (i in 1:length(years_for_search_and_extract)){
#   
#   sub <- subset(data, Season == years_for_search_and_extract[i])
#   
#   l <- unique(sub$HomeTeam)
#   
#   for (j in 1:length(l)){
#     
#     temp <- subset(sub, HomeTeam == l[j], select = c('Date','Div', 'HomeTeam','FTHG'))
#     temp$agg_goals.f <- cumsum(temp$FTHG)
#     
#     datalist1[[j]] <- temp
#     
#   }
# 
# temp2 <- do.call(rbind, datalist1[])
# # sub <- merge(x = sub, y = temp2[,c('Date','HomeTeam','agg_goals.f')], by = c("Date","HomeTeam"), all.x = TRUE)
# agg_goals.df[[i]] <-temp2    
#   
# }

## --------------------------------------------------------------------------------------------- ##
## Worked, Create function agg_feature and source

source('~/Desktop/soccer-predictions/Football/R_Scripts/FUN_agg_feature.R')

agg_goals.df <- agg_feature('HomeTeam', 'FTHG')

## Agg Away goals by away team feature (Cum away goals scored by away team)

agg_goalsA.df <- agg_feature('AwayTeam', 'FTAG')

## Agg Away goals feature (Cum away goals scored on home team)

agg_A_goals.df <- agg_feature('HomeTeam','FTAG')

## Agg Home goals on Away team 

agg_H_goals.df <- agg_feature('AwayTeam', 'FTHG')


## ---------------------------------------------HT AGG Goals ------------------------------------------------ ##
H.agg_goals.df <- agg_feature('HomeTeam', 'HTHG')

H.agg_goalsA.df <- agg_feature('AwayTeam', 'HTAG')

H.agg_A_goals.df <- agg_feature('HomeTeam','HTAG')

H.agg_H_goals.df <- agg_feature('AwayTeam', 'HTHG')


## ---------------------------------------------Shots -------------------------------------------- ##

agg_shots.df <- agg_feature('HomeTeam', 'HS')

agg_shotsA.df <- agg_feature('AwayTeam', 'AS')

agg_A_shots.df <- agg_feature('HomeTeam','AS')

agg_H_shots.df <- agg_feature('AwayTeam', 'HS')

## ------------------------------------- Shots on Target ------------------------------------------- ##

agg_shots_T.df <- agg_feature('HomeTeam', 'HST')

agg_shotsA_T.df <- agg_feature('AwayTeam', 'AST')

agg_A_shots_T.df <- agg_feature('HomeTeam','AST')

agg_H_shots_T.df <- agg_feature('AwayTeam', 'HST')

## ------------------------------------ Woodwork --------------------------------------------------- ##

agg_wood.df <- agg_feature('HomeTeam', 'HHW')

agg_woodA.df <- agg_feature('AwayTeam', 'AHW')

agg_A_wood.df <- agg_feature('HomeTeam','AHW')

agg_H_wood.df <- agg_feature('AwayTeam', 'HHW')

## ---------------------------------------- Corners ------------------------------------------------ ##

agg_corn.df <- agg_feature('HomeTeam', 'HC')

agg_cornA.df <- agg_feature('AwayTeam', 'AC')

agg_A_corn.df <- agg_feature('HomeTeam','AC')

agg_H_corn.df <- agg_feature('AwayTeam', 'HC')

## ---------------------------------------- Fouls ------------------------------------------------- ##

agg_fouls.df <- agg_feature('HomeTeam', 'HF')

agg_foulsA.df <- agg_feature('AwayTeam', 'AF')

agg_A_fouls.df <- agg_feature('HomeTeam','AF')

agg_H_fouls.df <- agg_feature('AwayTeam', 'HF')

## ---------------------------------------- Free Kicks ------------------------------------------------- ##

agg_FK.df <- agg_feature('HomeTeam', 'HFKC')

agg_FKA.df <- agg_feature('AwayTeam', 'AFKC')

agg_A_FK.df <- agg_feature('HomeTeam','AFKC')

agg_H_FK.df <- agg_feature('AwayTeam', 'HFKC')

## ---------------------------------------- Offsides ------------------------------------------------- ##

agg_off.df <- agg_feature('HomeTeam', 'HO')

agg_offA.df <- agg_feature('AwayTeam', 'AO')

agg_A_off.df <- agg_feature('HomeTeam','AO')

agg_H_off.df <- agg_feature('AwayTeam', 'HO')

## ---------------------------------------- Yellow cards ------------------------------------------------- ##

agg_YC.df <- agg_feature('HomeTeam', 'HY')

agg_YCA.df <- agg_feature('AwayTeam', 'AY')

agg_A_YC.df <- agg_feature('HomeTeam','AY')

agg_H_YC.df <- agg_feature('AwayTeam', 'HY')

## ---------------------------------------- Red cards ------------------------------------------------- ##

agg_RC.df <- agg_feature('HomeTeam', 'HR')

agg_RCA.df <- agg_feature('AwayTeam', 'AR')

agg_A_RC.df <- agg_feature('HomeTeam','AR')

agg_H_RC.df <- agg_feature('AwayTeam', 'HR')

## --------------------------------------- Booking pts ------------------------------------------------ ##

agg_BP.df <- agg_feature('HomeTeam', 'HBP')

agg_BPA.df <- agg_feature('AwayTeam', 'ABP')

agg_A_BP.df <- agg_feature('HomeTeam','ABP')

agg_H_BP.df <- agg_feature('AwayTeam', 'HBP')


