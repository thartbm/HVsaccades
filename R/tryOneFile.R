

library('emov')


#read.table(file="data/", header=FALSE, skip=1, sep=",", col.names=c("Timestamp", "Trigger", "LeftGazeX", "LeftGazeY", "RightGazeX", "RightGazeY", "LeftPupilMajorAxis", "LeftPupilMinorAxis", "RightPupilMajorAxis", "RightPupilMinorAxis", "Comment", "Comment2"))

tryMe <- function() {
  
  convertCommentsWithCommas('data/marius_exp1.csv.csv', 'data/marius_exp1.csv')
  
  # df <- read.csv('data/marius_exp1.csv')
  # df <- read.csv('data/marius2_exp1.csv')
  df <- read.csv('data/p02_exp1.csv')
  df <- fixLiveTrack(df)
  df$X <- rowMeans(as.matrix(df[,c('LeftGazeX', 'RightGazeX')]))
  df$Y <- rowMeans(as.matrix(df[,c('LeftGazeY', 'RightGazeY')]))
  
  dirs <- c('down-left', 'down-right', 'up-left', 'up-right', 'right-lo', 'right-hi', 'left-lo', 'left-hi')
  
  conditions <- c(sprintf('%s%s', dirs, '-10'), sprintf('%s%s', dirs, '-15'), sprintf('%s%s', dirs, '-20'))
  
  
  idx <- which(df$Comment != " ")
  trialno       <- 0
  blockno       <- 1
  condition     <- ""
  lookforstart  <- FALSE
  lookforend    <- FALSE
  fixationbroken <- FALSE
  
  all_saccades <- NA
  
  layout(mat=matrix(c(1:9), nrow=3, byrow=TRUE))
  
  for (idx_no in c(1:length(idx))) {
    i <- idx[idx_no]
    print(i)
    print(df$Comment[i])
    if (grepl("block", df$Comment[i], fixed=TRUE)) {
      blockno <- as.numeric( strsplit( strsplit(df$Comment[i], " ")[[1]][3], '/' )[[1]][1] )
      trialno <- 0
    }
    if (grepl("trial", df$Comment[i], fixed=TRUE)) {
      trialno   <- 0
      condition <- ""
      first     <- c()
      second    <- c()
      
      trialno <- as.numeric((strsplit(df$Comment[i], " ")[[1]][3] )) + 1
      lookforstart <- TRUE
      fixationbroken <- FALSE
      # if (trialno > 27) {
      #   break
      # }
    }
    if (grepl("first", df$Comment[i], fixed=TRUE)) {
       first <- strsplit(df$Comment[i], " ")[[1]][3]

    }
    if (grepl("second", df$Comment[i], fixed=TRUE)) {
      second <- strsplit(df$Comment[i], " ")[[1]][3]
    }
    
    # check conditions: should be a key-value pair as well!
    for (cond in conditions) {
      if (grepl(cond, df$Comment[i], fixed=TRUE)) {
        condition <- cond
        break
      }
    }
    if (df$Comment[i] == " fixation broken") {
      # cat("fixation broken\n")
      fixationbroken <- TRUE
      lookforstart <- FALSE
      lookforend <- FALSE
    }
    if (lookforstart) {
      if (df$Comment[i] == " stimulus on") {
        trial_idx <- c(i)
        lookforstart <- FALSE
        lookforend <- TRUE
      }
    }
    if (lookforend) {
      if (df$Comment[i] == " stimulus off") {
        trial_idx <- c(trial_idx, i) # saccade interval starts
      }
      if (df$Comment[i] == " stop recording") {
        lookforend <- FALSE
        trial_idx <- c(trial_idx, i)
        mus <- (df$Timestamp[trial_idx[1]:trial_idx[3]] / 1000000) - (df$Timestamp[trial_idx[2]] / 1000000)
        X <- df$X[trial_idx[1]:trial_idx[3]]
        Y <- df$Y[trial_idx[1]:trial_idx[3]]
        fixations <- emov::emov.idt(t=mus, x=X, y=Y, dispersion=1.5, duration=50)
        fixations <- fixations[which(fixations$end > 0),]
        
        if (nrow(fixations) == 0) {
          cat(sprintf("Block %d, Trial %d, Condition %s: no fixations\n", blockno, trialno, condition))
          next
        }
        
        rownames(fixations) <- 1:nrow(fixations)
        
        # print(fixations)
        if (condition == "") {
          condition <- conditionFromTargets(first=first, second=second)
        }
        cat(sprintf("Block %d, Trial %d, Condition %s: %d fixations\n", blockno, trialno, condition, dim(fixations)[1]))
        if (condition != "") {
          print('getting saccades')
          saccades <- getSaccades(condition=condition,
                                  fixations=fixations, 
                                  time_s=mus, x=X, y=Y )
          saccades$block <- blockno
          saccades$trial <- trialno
          # print(saccades)
          if (is.data.frame(all_saccades)) {
            all_saccades <- rbind(all_saccades, saccades)
          } else {
             all_saccades <- saccades
          }
          plot(X, Y, type='l', 
               main=sprintf("%s (block %d, trial %d)", condition, blockno, trialno),
               asp=1,col='#00000033')
          points(0,0,col='blue', pch=4)
          text(fixations$x, fixations$y, labels=sprintf('%d',c(1:dim(fixations)[1])), col='red', pch=1)
          Q <- c(saccades$Qstart_x, saccades$Qstart_y, saccades$Qend_x, saccades$Qend_y)
          if (!any(is.na(Q))) {
            lines(x = Q[c(1,3)],
                  y = Q[c(2,4)], col='purple', lwd=2)
          }
          R <- c(saccades$Rstart_x, saccades$Rstart_y, saccades$Rend_x, saccades$Rend_y)
          if (!any(is.na(R))) {
            lines(x = R[c(1,3)],
                  y = R[c(2,4)], col='orange', lwd=2)
          }
          
        }
      }
    }
    
  }
  
  # print(all_saccades)
  write.csv(all_saccades, 'data/saccades.csv', row.names=FALSE)
}

getSaccades <- function(condition,
                        fixations, 
                        time_s=NULL, x=NULL, y=NULL) {
  
  
  
  fixations <- fixations[which(fixations$start > 0),]
  fixations$distance <- sqrt(fixations$x^2 + fixations$y^2)
  print(fixations)
  
  # - # - # - # - # - # - # - # - # - # - # - #
  # determine quadrant-wise:
  
  condstarts <- list('down-left'=c(2,3),
                     'down-right'=c(1,4),
                     'up-left'=c(3,2),
                     'up-right'=c(4,1),
                     'right-lo'=c(3,4),
                     'right-hi'=c(2,1),
                     'left-lo'=c(4,3),
                     'left-hi'=c(1,2))
  main_cond <- paste(strsplit(condition, "-")[[1]][c(1:2)], collapse="-")
  quadrants <- condstarts[[main_cond]]
  
  orientation <- list("up"='V', "down"='V', "left"='H', "right"='H')[[strsplit(condition, "-")[[1]][1]]]
  amplitude <- as.numeric(strsplit(condition, "-")[[1]][3])
  
  # print(fixations)
  
  cutoff <- sqrt(2*(amplitude^2))/4
  # cat(sprintf('cutoff: %0.3f\n', cutoff))
  fixations <- fixations[which(fixations$distance > cutoff),]
  
  # cat(sprintf('first quadrant: %d, second quadrant: %d\n',quadrants[1], quadrants[2]))
  factors1 <- list(c(1,1),c(-1,1),c(-1,-1),c(1,-1))[[quadrants[1]]]
  factors2 <- list(c(1,1),c(-1,1),c(-1,-1),c(1,-1))[[quadrants[2]]]
  # print(factors1)
  # print(factors2)
  
  idx1 <- which( ((fixations$x * factors1[1]) > 0) & ((fixations$y * factors1[2]) > 0) )
  idx1 <- idx1[which.max(fixations$distance[idx1])]
  idx2 <- which( ((fixations$x * factors2[1]) > 0) & ((fixations$y * factors2[2]) > 0) )
  idx2 <- idx2[which.max(fixations$distance[idx2])]
  Qselect <-fixations[c(idx1,idx2),]
  # print(Qselect)
  # print(diff(Qselect$start))
  
  Qstart_x <- NA
  Qstart_y <- NA
  Qend_x <- NA
  Qend_y <- NA
  Qsacc_amp <- NA
  
  if (dim(Qselect)[1] == 2) { 
    if (diff(Qselect$start) > 0) {
      Qstart_x <- Qselect$x[1]
      Qstart_y <- Qselect$y[1]
      Qend_x <- Qselect$x[2]
      Qend_y <- Qselect$y[2]
      Qsacc_amp <- sqrt((Qend_x - Qstart_x)^2 + (Qend_y - Qstart_y)^2)
    }
  } 

  # - # - # - # - # - # - # - # - # - # - # - #
  # determine by fixation order and rules:
  
  # - more then 2 dva from starts 
  # - AND in the right quadrants
  
  # print(fixations)
  fixd <- c()
  for (qi in c(1,2)) {
    factors <- list(factors1, factors2)[[qi]]
    
    idx <- which( ((fixations$x * factors[1]) > 0) & ((fixations$y * factors[2]) > 0) )
    # cat(sprintf('Q %d: initially %d fixations in quadrant\n', qi, length(idx)))
    if (length(idx) > 1) {
      if (any(diff(idx) != 1)) {
        idx <- idx[c(1:(min(which(diff(idx) != 1))+1))]
        # cat('-- removed non-contiguity\n')
      }
      dists <- sqrt(diff(fixations$x[idx])^2 + diff(fixations$y[idx])^2)
      if (any(dists < .5)) {
        idx <- idx[c(TRUE, which(dists > .5))]
        # cat('-- removed close fixations\n')
      }
      if (length(idx) %in% c(1,2)) {
        # idx <- max(idx)
        
        # or maybe the one closest to the target?
        targetloc <- .5 * amplitude * factors
        # print(targetloc)
        dist2target <- sqrt((fixations$x[idx]-targetloc[1])^2 + (fixations$y[idx]-targetloc[2])^2)
        idx <- idx[which.min(dist2target)]
      } else {
        # cat('-- too many fixations, removed all\n')
        idx <- c()
      }
    }
    
    # cat(sprintf('Q %d: %d fixations\n', qi, length(idx)))
    
    fixd <- c(fixd, idx)
    
  }
  # print(length(fixd))
  
  Rstart_x <- NA
  Rstart_y <- NA
  Rend_x <- NA
  Rend_y <- NA
  Rsacc_amp <- NA
  
  # if (dim(Rselect)[1] == 2) { 
  if (length(fixd) == 2) {
    Rselect <- fixations[fixd,]
    if (diff(Rselect$start) > 0) {
      Rstart_x <- Rselect$x[1]
      Rstart_y <- Rselect$y[1]
      Rend_x <- Rselect$x[2]
      Rend_y <- Rselect$y[2]
      Rsacc_amp <- sqrt((Rend_x - Rstart_x)^2 + (Rend_y - Rstart_y)^2)
    }
  } 
  
  
  # # first target quadrant:
  # idx1 <- which( ((fixations$x * factors1[1]) > 0) & ((fixations$y * factors1[2]) > 0) )
  # # print(length(idx1))
  # if (length(idx1) > 1) {
  #   # actually, let's be more strict about this:
  #   if (any(diff(idx1) != 1)) {
  #     # idx1 <- c() # just remove everything?
  #     # it does happen that the first fixation back on start is more than 2 dva away from start,
  #     # and accidentally falls within the 'wrong' quadrant - which should be fine,
  #     # so lets just remove anything after the first disruption of gaze in a quadrant
  #     idx1 <- idx1[c(1:(min(which(diff(idx1) != 1))+1))]
  #     # cat('= - = - = - = - = - = - = - =\n RETURN TO QUADRANT\n= - = - = - = - = - = - = - =\n')
  #   }
  #   dists1 <- sqrt(diff(fixations$x[idx1])^2 + diff(fixations$y[idx1])^2)
  #   # print(dists1)
  #   if (any(dists1 < .5)) {
  #     # cat('remove close fixations\n')
  #     # print(which(dists1 < .5))
  #     # c(TRUE, which(dists1 > .5))
  #     idx1 <- idx1[c(TRUE, which(dists1 > .5))]
  #     # print(idx1)
  #   }
  #   if (length(idx1) %in% c(1,2)) {
  #     # if there are 1 or 2 fixations, we take the last one as the true one
  #     idx1 <- max(idx1)
  #     targetloc <- .5 * amplitude * factors1
  #     print(targetloc)
  #     # dist2target <- sqrt(fixations$x[idx1]^2 + fixations$y[idx1]^2)
  #   } else {
  #     # if there are 3 or more, we don't know what to do, so we remove all of them
  #     idx1 <- c()
  #   }
  # }
  # # second target quadrant:
  # idx2 <- which( ((fixations$x * factors2[1]) > 0) & ((fixations$y * factors2[2]) > 0) )
  # # print(length(idx2))
  # if (length(idx2) > 1) {
  #   idx2f <- c(min(idx2): max(idx2))
  #   dists2 <- sqrt(diff(fixations$x[idx2f])^2 + diff(fixations$y[idx2f])^2)
  #   # print(dists2)
  # }
  
  
  answers <- list(
    'condition'  = condition,
    'orientation'= orientation,
    'amplitude'  = amplitude,
    
    'Qstart_x'   = Qstart_x,
    'Qstart_y'   = Qstart_y,
    'Qend_x'     = Qend_x,
    'Qend_y'     = Qend_y,
    'Qsacc_amp'  = Qsacc_amp,
    
    'Rstart_x'   = Rstart_x,
    'Rstart_y'   = Rstart_y,
    'Rend_x'     = Rend_x,
    'Rend_y'     = Rend_y,
    'Rsacc_amp'  = Rsacc_amp
  )
  # print(answers)
  return(as.data.frame(answers))
  
}


fixLiveTrack <- function(df) {
  
  df <- df[which(df$Timestamp != 'Timestamp'),]
  
  df <- df[,which(names(df) != 'Trigger')]
  
  for (colname in names(df)) {
    
    if (colname != 'Comment') {
      df[,colname] <- as.numeric(df[,colname])
    }
    
  }
  
  # find spots where time goes back down (calibration):
  idxs <- which(diff(df$Timestamp) < 0)
  
  # how many samples are there:
  nsamples <- length(df$Timestamp)
  
  # loop through reset points:
  for (idx_no in c(1:length(idxs))) {
    idx <- idxs[idx_no]
    lval <- df$Timestamp[idx]
    if (idx_no == length(idxs)) {
      tidx <- c((idx+1):nsamples)
    } else {
      tidx <- c((idx+1):idxs[idx_no+1])
    }
    df$Timestamp[tidx] <- df$Timestamp[tidx] + lval
  }
  
  # fix instances where timestamps go up too much:
  # find spots where time goes back down (calibration):
  idxs <- which(diff(df$Timestamp) > 2500)
  
  # loop through reset points:
  for (idx_no in c(1:length(idxs))) {
    idx <- idxs[idx_no]
    lval <- df$Timestamp[idx] - df$Timestamp[idx+1] + 2000
    if (idx_no == length(idxs)) {
      tidx <- c((idx+1):nsamples)
    } else {
      tidx <- c((idx+1):idxs[idx_no+1])
    }
    df$Timestamp[tidx] <- df$Timestamp[tidx] + lval
  }
  
  
  return(df)
  
}


# this function only necessary for some initial pilot runs
# where coordinates of targets contained a comma: this breaks reading the CSV file
# later on, the coordinates were split with a colon, so this function is not needed anymore

convertCommentsWithCommas <- function(filename, outfile) {
  
  df <- read.csv(filename)
  nlines <- dim(df)[1]
  
  con1 <- file(filename, "r")
  con2 <- file(outfile, "w")

  for (line in c(1:nlines)) {
    thisline <- readLines(con=con1, n=1)
    if (length(thisline) == 0) {
      break
    }
    # get the last character in the string:
    if (substr(thisline, nchar(thisline), nchar(thisline)) == "]") {
      # print(thisline)
      # replace the last comma with a colon:
      ellist <- strsplit(thisline, ", ")[[1]]
      # print(length(ellist))
      ellist[11] <- sprintf("%s:%s", ellist[11], ellist[12])
      thisline <- paste(ellist[1:11], collapse=",")
      
      # thisline <- sprintf("%s:%s", substr(thisline, 1, lastidx-1) , substr(thisline, lastidx+2, nchar(thisline))) # get the part before the last comma
      
      # thisline <- sub(", ", ":", thisline, fixed=TRUE)
      # print(thisline)
    }
    writeLines(thisline, con=con2)
  }
  
  close(con1)
  close(con2)
  # return(df)
  
}


conditionFromTargets <- function(first, second) {
  
  first <- gsub("[","",first,fixed=TRUE)
  first <- gsub("]","",first,fixed=TRUE)
  first <- strsplit(first, ":")[[1]]
  first <- c(as.numeric(first[1]), as.numeric(first[2]))
  
  second <- gsub("[","",second,fixed=TRUE)
  second <- gsub("]","",second,fixed=TRUE)
  second <- strsplit(second, ":")[[1]]
  second <- c(as.numeric(second[1]), as.numeric(second[2]))
  
  
  distance <- round(sqrt((second[1]-first[1])^2 + (second[2]-first[2])^2))
  
  if (first[1] == second[1]) {
    # vertical condition: up or down
    if (first[2] > second[2]) {
      direction <- 'down'
    } else {
      direction <- 'up'
    }
    # to the left or right of the center:
    if (first[1] > 0) {
      side <- 'right'
    } else {
      side <- 'left'
    }
  } else {
    # horizontal condition: left or right
    if (first[1] > second[1]) {
      direction <- 'left'
    } else {
      direction <- 'right'
    }
    # lo or hi relative to center?
    if (first[2] > 0) {
      side <- 'hi'
    } else {
      side <- 'lo'
    }
  }

  condition <- sprintf('%s-%s-%d', direction, side, distance)
  return(condition)
  
}


plotHVsaccades <- function() {
  
  df <- read.csv('data/p02_saccades.csv', stringsAsFactors = FALSE)
  
  layout(mat=matrix(c(1:2), nrow=2, byrow=TRUE))
  
  conditions <- data.frame('amplitude' = c(10,10,15,15,20,20), 'orientation' = c('H', 'V', 'H', 'V', 'H', 'V'))
  
  for (depvar in c('Qsacc_amp', 'Rsacc_amp')) {
    
    df$depvar <- df[,depvar]
    
    plot(NULL,NULL,
         main=depvar, xlab='target distance [dva]', ylab='saccade amplitude [dva]',
         xlim=c(0.4,6.6), ylim=c(0,30), 
         ax=F, bty='n')
    
    lines(c(0.5,2.5), c(10,10), col='grey', lty=1)
    lines(c(2.5,4.5), c(15,15), col='grey', lty=1)
    lines(c(4.5,6.5), c(20,20), col='grey', lty=1)
    
    
    for (cond_no in c(1:(dim(conditions)[1]))) {
      
      amplitude <- conditions$amplitude[cond_no]
      orientation <- conditions$orientation[cond_no]
      
      color <- ifelse(orientation == 'H', 'blue', 'red')
      
      subdf <- df[which((df$amplitude == amplitude) & (df$orientation == orientation)),]
      
      points(cond_no+runif(n=dim(subdf)[1], min=-0.1, max=.1), 
             subdf$depvar, 
             col=Reach::colorAlpha(col=color, alpha=34), pch=16)
      
      avg <- mean(subdf$depvar, na.rm=TRUE)
      CI <-  Reach::getConfidenceInterval(subdf$depvar,method='b')
      # print(avg)
      # print(CI)
      
      polygon(x=cond_no + c(-0.2, -0.4, -0.4, -0.2), 
              y=c(CI[1], CI[1], CI[2], CI[2]), 
              col=Reach::colorAlpha(col=color, alpha=34), border=NA)
      lines(x=cond_no + c(-0.2, -0.4), y=c(avg, avg), col=color, lwd=2)
      
      kd <- density(subdf$depvar, na.rm=TRUE,
                    from=0, to=30, n=512)
      X <- kd$x
      Y <- kd$y
      idx <- which(Y > 0.00001)
      X <- X[idx]
      Y <- Y[idx]
      Y <- Y / max(Y) * 0.2
      
      X <- c(min(X), X, max(X))
      Y <- c(0, Y, 0)
      
      polygon(x=cond_no + Y + .2, y=X, col=Reach::colorAlpha(col=color, alpha=34), border=NA)
      lines(x=cond_no + Y + .2, y=X, col=color, lwd=1)
      
    }
    
    axis(side=1, at=c(1,2,3,4,5,6), labels=c('10-H', '10-V', '15-H', '15-V', '20-H', '20-V'))
    axis(side=2, at=c(0,10,20,30))
    
  }
  
  
}