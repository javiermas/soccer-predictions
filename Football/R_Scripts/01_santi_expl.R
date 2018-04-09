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
              'HTR',
              'Season')


## Extract, order, clean
data <- all_data[,as.vector(rbind(match_vars, feature_list))]
data <- data[is.na(data$FTR)==FALSE,]
data<- data[order(as.Date(data$Date, format="%d/%m/%y")),]


## --------------- Features ------------- ##

## Create target  
target <- ifelse(data$FTR=='H', 1, 0)


## Agg goals feature

datalist1 <- list()
datalist2 <- list()
for (i in 1:length(years_for_search_and_extract)){
  
  sub <- subset(data, Season == years_for_search_and_extract[i])
  
  l <- unique(sub$HomeTeam)
  
  for (j in 1:length(l)){
    
    temp <- subset(sub, HomeTeam == l[j], select = c('Date','HomeTeam','FTHG'))
    temp$agg_goals.f <- cumsum(temp$FTHG)
    
    datalist2[[j]] <- temp
    
  }

temp2 <- do.call(rbind, datalist2[])
sub <- merge(x = sub, y = temp2[,c('Date','HomeTeam','agg_goals.f')], by = c("Date","HomeTeam"), all.x = TRUE)
datalist1[[i]] <- sub    
  
}


 








