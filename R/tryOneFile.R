

library('emov')


#read.table(file="data/", header=FALSE, skip=1, sep=",", col.names=c("Timestamp", "Trigger", "LeftGazeX", "LeftGazeY", "RightGazeX", "RightGazeY", "LeftPupilMajorAxis", "LeftPupilMinorAxis", "RightPupilMajorAxis", "RightPupilMinorAxis", "Comment", "Comment2"))

tryMe <- function() {
  
  convertCommentsWithCommas('data/marius_exp1.csv.csv', 'data/marius_exp1.csv')
  
  df <- read.csv('data/marius_exp1.csv')
  df <- fixLiveTrack(df)
  df$X <- rowMeans(as.matrix(df[,c('LeftGazeX', 'RightGazeX')]))
  df$Y <- rowMeans(as.matrix(df[,c('LeftGazeY', 'RightGazeY')]))
  
  idx <- which(df$Comment != " ")
  trialno       <- 0
  blockno       <- 1
  condition     <- ""
  lookforstart  <- FALSE
  lookforend    <- FALSE
  fixationbroken <- FALSE
  
  layout(mat=matrix(c(1:9), nrow=3, byrow=TRUE))
  
  for (idx_no in c(1:length(idx))) {
    i <- idx[idx_no]
    if (grepl("block", df$Comment[i], fixed=TRUE)) {
      blockno <- as.numeric( strsplit( strsplit(df$Comment[i], " ")[[1]][3], '/' )[[1]][1] )
      trialno <- 0
    }
    if (grepl("trial", df$Comment[i], fixed=TRUE)) {
      trialno <- as.numeric((strsplit(df$Comment[i], " ")[[1]][3] )) + 1
      condition <- strsplit(df$Comment[idx[idx_no+1]], " ")[[1]][2]
      lookforstart <- TRUE
      fixationbroken <- FALSE
      # if (trialno > 27) {
      #   break
      # }
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
        rownames(fixations) <- 1:nrow(fixations)
        cat(sprintf("Block %d, Trial %d, Condition %s: %d fixations\n", blockno, trialno, condition, dim(fixations)[1]))
        # print(fixations)
        saccades <- getSaccades(condition=condition,
                                fixations=fixations, 
                                time_s=mus, x=X, y=Y )
        plot(X, Y, type='l', 
             main=sprintf("%s (block %d, trial %d)", condition, blockno, trialno),
             asp=1,col='#00000033')
        points(0,0,col='blue', pch=4)
        text(fixations$x, fixations$y, labels=sprintf('%d',c(1:dim(fixations)[1])), col='red', pch=1)
      }
    }
    
  }
  
}

getSaccades <- function(condition,
                        fixations, 
                        time_s=NULL, x=NULL, y=NULL) {
  
  
  
  fixations <- fixations[which(fixations$start > 0),]
  fixations$distance <- sqrt(fixations$x^2 + fixations$y^2)
  # print(fixations)
  fixations <- fixations[which(fixations$distance > 2),]
  
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
  
  direction <- list("up"='V', "down"='V', "left"='H', "right"='H')[[strsplit(condition, "-")[[1]][1]]]
  amplitude <- as.numeric(strsplit(condition, "-")[[1]][3])
  
  factors1 <- list(c(1,1),c(-1,1),c(-1,-1),c(1,-1))[[quadrants[1]]]
  factors2 <- list(c(1,1),c(-1,1),c(-1,-1),c(1,-1))[[quadrants[2]]]
  # print(factors1)
  # print(factors2)
  
  idx1 <- which( ((fixations$x * factors1[1]) > 0) & ((fixations$y * factors1[2]) > 0) )
  idx1 <- idx1[which.max(fixations$distance[idx1])]
  idx2 <- which( ((fixations$x * factors2[1]) > 0) & ((fixations$y * factors2[2]) > 0) )
  idx2 <- idx2[which.max(fixations$distance[idx2])]
  Qselect <-fixations[c(idx1,idx2),]
  
  if(dim(Qselect)[1] == 2) {
    Qstart_x <- Qselect$x[1]
    Qstart_y <- Qselect$y[1]
    Qend_x <- Qselect$x[2]
    Qend_y <- Qselect$y[2]
    Qsacc_amp <- sqrt((Qend_x - Qstart_x)^2 + (Qend_y - Qstart_y)^2)
  } else {
    Qstart_x <- NA
    Qstart_y <- NA
    Qend_x <- NA
    Qend_y <- NA
    Qsacc_amp <- NA
  }
  
  # - # - # - # - # - # - # - # - # - # - # - #
  # determine by fixation order and rules:
  print(fixations)
  
  
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