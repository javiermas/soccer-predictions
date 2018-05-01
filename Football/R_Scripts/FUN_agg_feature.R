
agg_feature <- function(HA, var) {

datalist1 <- list()
datalist2 <- list()

for (i in 1:length(years_for_search_and_extract)){
  
  sub <- subset(data, Season == years_for_search_and_extract[i])
  
  l <- unique(sub[,HA])
  
  for (j in 1:length(l)){
    
    temp <- subset(sub, sub[,HA] == l[j], select = c('Date','Div', 'HomeTeam', 'AwayTeam', HA, var))
    
    if (HA == 'HomeTeam'){
    name.var <- paste('H.agg_', var, sep = '')
    }else 
    {
      name.var <- paste('A.agg_', var, sep = '')  
    }
    
    temp[,name.var] <- cumsum(temp[,var])
    
    datalist1[[j]] <- temp
    
  }
  
  temp2 <- do.call(rbind, datalist1[])
  # sub <- merge(x = sub, y = temp2[,c('Date','HomeTeam','agg_goals.f')], by = c("Date","HomeTeam"), all.x = TRUE)
  datalist2[[i]] <-temp2    
  
}

return(datalist2)

}