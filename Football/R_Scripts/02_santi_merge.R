## Merge all features by Home Team, Date for all 21 Seasons

datalist_ft <- list()
l <- ls(pattern= 'agg_*')
l <- l[!l %in% 'agg_feature']
list <- mget(l)


for (i in 1:21){
  
  temp <- list[[1]][[i]]
  temp <- temp[,c('Date', 'HomeTeam')]
  
  for (j in 1:48){
    
    df.ft <- list[[j]][[i]]
    
    temp <- merge(temp, df.ft[,c(1,3,7)], all.x =TRUE, by = c('Date', 'HomeTeam'))
    
  }
  
  datalist_ft[[i]] <- temp
}
