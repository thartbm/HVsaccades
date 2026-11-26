
# imports and utility functions -----

library('emov')

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

# before doing anything in saccade / fixation detection, we should filter the recording
# Gunnar recommends an autoregressive filter with a cutoff of 50 - 60 Hz
# we can get these using the arma filters from the signal package
# however, those do not allow specifying a cutoff frequency
# I did find a stack exchange post that said that cut-off frequency is:
#  "roughly the sampling rate divided by the window length"
#  (https://dsp.stackexchange.com/questions/69685/how-does-window-length-influence-cut-off-frequency-of-filter-and-group-delay)
# so here the sampling rate is 500 Hz, and for a 60 Hz low-pass filter,
# we'd need a window length of 500 / 60 = 8.33, so we can use a window length of 9 or lower
# but how do the "coefficients" of the AR part of the filter determine window length?
# is it just a kernel, where the coefficients are the weights of the kernel? 
# If so, then the window length is just the number of coefficients, and we can just use a vector of 9 coefficients that sum to 1.

# Coefficients:
# AR: a = c(1, -1.31, 0.81)
# MA: `b = c(0.01, 0, 0)

# af <- signal::Arma(b=c(0.01, 0, 0), a=c(1, -1.31, 0.81))
# zplane(af)


# stats::filter( timeseries, 
#                filter = rep(1/3,3),
#                method = "recursive",
#                sides  = 2,
#                init   = timeseries[1])


extractSaccadesFromFile <- function(datafile) {
  
  if (grepl('alice', datafile)) {
    switch_points <- TRUE
  } else {
    switch_points <- FALSE
  }
  
  #convertCommentsWithCommas('data/marius_exp1.csv.csv', 'data/marius_exp1.csv')
  fixation_sets <- 0
  # df <- read.csv('data/marius_exp1.csv')
  # df <- read.csv('data/marius2_exp1.csv')
  # df <- read.csv('data/p02_exp1.csv')
  df <- read.csv(datafile)
  df <- fixLiveTrack(df)
  # df$X <- rowMeans(as.matrix(df[,c('LeftGazeX', 'RightGazeX')]))
  # df$Y <- rowMeans(as.matrix(df[,c('LeftGazeY', 'RightGazeY')]))
  
  # dirs <- c('down-left', 'down-right', 'up-left', 'up-right', 'right-lo', 'right-hi', 'left-lo', 'left-hi')
  
  # conditions <- c(sprintf('%s%s', dirs, '-10'), sprintf('%s%s', dirs, '-15'), sprintf('%s%s', dirs, '-20'))
  
  
  idx <- which(df$Comment != " ")
  trialno       <- 0
  blockno       <- 1
  condition     <- ""
  lookforstart  <- FALSE
  lookforend    <- FALSE
  fixationbroken <- FALSE
  
  all_saccades <- NA
  
  
  interfixationdata <-  list('block'=c(), 
                             'trial'=c(), 
                             'target'=c(), 
                             'BS_tilt'=c(),
                             'AW_tilt'=c(),
                             'AWratio'=c(),
                             'eye'=c(),
                             'point1_x'=c(), 
                             'point1_y'=c(), 
                             'point2_x'=c(), 
                             'point2_y'=c(), 
                             'point_dist'=c(),
                             'intfixdist_init'=c(), 
                             'intfixdist_corr'=c())
  
  layout(mat=matrix(c(1:9), nrow=3, byrow=TRUE))
  
  for (idx_no in c(1:length(idx))) {
    i <- idx[idx_no]
    # print(i)
    # print(df$Comment[i])

    if (grepl("block", df$Comment[i], fixed=TRUE)) {
      commentparts <- strsplit(df$Comment[i], " ")[[1]]
      # print(commentparts)
      blockno      <- as.numeric(commentparts[3])
      trialno      <- as.numeric(commentparts[5])
      
      cat(sprintf('Block %d, Trial %d\n', blockno, trialno))
      
      # lookforstart <- TRUE # only IFF all condition vars have been set
      fixationbroken <- FALSE
      
      var_set <- c('BStilt'=FALSE,
                   'AWtilt'=FALSE,
                   'targetpair'=FALSE,
                   'eye'=FALSE,
                   'AWratio'=FALSE,
                   'point1'=FALSE,
                   'point2'=FALSE,
                   'point3'=FALSE,
                   'point4'=FALSE)
      
      # blockno <- as.numeric( strsplit( strsplit(df$Comment[i], " ")[[1]][3], '/' )[[1]][1] )
      # trialno <- 0
    }
    
    # we also need:
    # condition, which has four bits of info:
    # 1: orientation of BS pair
    # 2: orientation of AW pair
    # 3: which pair is supposed to be fixated
    # 4: which eye the stimuli were presented to

    # then, to check the gaze data, we need to know where people
    # where supposed to fixate, which is the coordinates of
    # point 1 and point 2 (in that order)
    
    # then we get the X/Y coordinates from 'stimulus off' to 'gaze returned'
    # first we filter the 4 signals, then average the X's and average the Y's
    # then use the emov fix/sacc detection thing
    if (grepl("BS tilt", df$Comment[i], fixed=TRUE)) {
      BStilt <- as.numeric(strsplit(df$Comment[i], " ")[[1]][4])
      # print('BS tilt')
      var_set['BStilt'] <- TRUE
    }
    # [1] " BS tilt 0"
    # [1] " AW tilt 90"
    if (grepl("AW tilt", df$Comment[i], fixed=TRUE)) {
      AWtilt <- as.numeric(strsplit(df$Comment[i], " ")[[1]][4])
      # print('AW tilt')
      var_set['AWtilt'] <- TRUE
    }
    # [1] " target pair AW"
    if (grepl("target pair", df$Comment[i], fixed=TRUE)) {
      targetpair <- strsplit(df$Comment[i], " ")[[1]][4]
      # print('target pair')
      var_set['targetpair'] <- TRUE
    }
    
    # [1] " eye contra"
    if (grepl("eye", df$Comment[i], fixed=TRUE)) {
      eye <- strsplit(df$Comment[i], " ")[[1]][3]
      # print(strsplit(df$Comment[i], " ")[[1]])
      # print(eye)
      var_set['eye'] <- TRUE
    }
    
    if (grepl("AWratio", df$Comment[i], fixed=TRUE)) {
      # print(df$Comment[i])
      AWratio <- as.numeric(strsplit(df$Comment[i], " ")[[1]][3])
      # print(strsplit(df$Comment[i], " ")[[1]])
      # print(AWratio)
      var_set['AWratio'] <- TRUE
    }
    
    
    # [1] " point4 -23.5100 -1.4900"
    if (grepl("point1", df$Comment[i], fixed=TRUE)) {
      point1 <- as.numeric(strsplit(df$Comment[i], " ")[[1]][c(3,4)])
      # print('point 1')
      var_set['point1'] <- TRUE
    }
    if (grepl("point2", df$Comment[i], fixed=TRUE)) {
      point2 <- as.numeric(strsplit(df$Comment[i], " ")[[1]][c(3,4)])
      # print('point 2')
      var_set['point2'] <- TRUE
    }
    if (grepl("point3", df$Comment[i], fixed=TRUE)) {
      point3 <- as.numeric(strsplit(df$Comment[i], " ")[[1]][c(3,4)])
      # print('point 3')
      var_set['point3'] <- TRUE
    }
    if (grepl("point4", df$Comment[i], fixed=TRUE)) {
      point4 <- as.numeric(strsplit(df$Comment[i], " ")[[1]][c(3,4)])
      # print('point 4')
      var_set['point4'] <- TRUE
    }
    
    
    if (exists('var_set')) {
      # print('var_set exists...')
      if (all(var_set)) {
        # print(var_set)
        lookforstart <- TRUE
        
        if (switch_points) {
          tmp <- point1
          point1 <- point3
          point3 <- tmp
          tmp <- point2
          point2 <- point4
          point4 <- tmp
        }
        
        # print(c(eye, AWratio, BStilt, AWtilt, targetpair))
        
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
        trial_idx <- c(trial_idx, i) # saccade interval starts AFTER stimulus
      }
      if (df$Comment[i] == " gaze returned") {
        lookforend <- FALSE
        trial_idx <- c(trial_idx, i)
        mus <- (df$Timestamp[trial_idx[1]:trial_idx[3]] / 1000000) - (df$Timestamp[trial_idx[2]] / 1000000)
        # X <- df$X[trial_idx[1]:trial_idx[3]]
        # Y <- df$Y[trial_idx[1]:trial_idx[3]]
        
        lX <- df$LeftGazeX[trial_idx[1]:trial_idx[3]]
        # flX <- stats::filter( lX, 
        #                       filter = rep(1/3,3),
        #                       method = "recursive",
        #                       sides  = 2,
        #                       init   = rep(lX[1],3))
        flX <- stats::filter( lX, 
                              filter = rep(1/3,3))
        lY <- df$LeftGazeY[trial_idx[1]:trial_idx[3]] 
        flY <- stats::filter( lY,
                              filter = rep(1/3,3))
                              # method = "recursive",
                              # sides  = 2,
                              # init   = rep(lY[1],3))
        rX <- df$RightGazeX[trial_idx[1]:trial_idx[3]]
        frX <- stats::filter( rX,
                              filter = rep(1/3,3))
                              # method = "recursive",
                              # sides  = 2,
                              # init   = rep(rX[1],3))
        rY <- df$RightGazeY[trial_idx[1]:trial_idx[3]]
        frY <- stats::filter( rY,
                              filter = rep(1/3,3))
                              # method = "recursive",
                              # sides  = 2,
                              # init   = rep(rY[1],3))
        
        # print(rY)
        # print(frY)
        
        fX <- rowMeans(cbind(flX, frX), na.rm=TRUE)
        fY <- rowMeans(cbind(flY, frY), na.rm=TRUE)
        
        # df$X <- rowMeans(as.matrix(df[,c('LeftGazeX', 'RightGazeX')]))
        # df$Y <- rowMeans(as.matrix(df[,c('LeftGazeY', 'RightGazeY')]))
        
        fixations <- emov::emov.idt(t=mus, x=fX, y=fY, dispersion=1.5, duration=50)
        fixations <- fixations[which(fixations$end > 0),]
        

        
        if (TRUE) {
          x_stim <- c(point1[1], point2[1], point3[1], point4[1])
          y_stim <- c(point1[2], point2[2], point3[2], point4[2])
          xrange <- range(c(-5, 5, fX, x_stim), na.rm=TRUE)
          yrange <- range(c(-5, 5, fY, y_stim), na.rm=TRUE)
          
          plot(NULL, NULL,
               x = fX, y = fY,
               xlim=xrange, 
               ylim=yrange,
               type='l', col='gray',
               asp=1,
               log=""
          )
          
          points( x = x_stim,
                  y = y_stim,
                  col=c('red','red','blue','blue'))
          
          text(0,0,'X')
          
          xfix <- fixations$x
          yfix <- fixations$y
          
          text(x = xfix, y = yfix,
               labels = sprintf('%d', c(1:length(xfix))),
               col='purple')
          
          fixation_sets <- fixation_sets + 1
          title(main=sprintf('fixation set %d', fixation_sets))
        }
        
        
        point12_sep <- sqrt((point1[1]-point2[1])^2 + (point1[2]-point2[2])^2)
        
        # print(point12_sep)
        # print(sqrt((fixations$x-point1[1])^2 + (fixations$y-point1[2])^2))
        
        fixations$p1c <- sqrt((fixations$x-point1[1])^2 + (fixations$y-point1[2])^2) < (point12_sep / 2)
        fixations$p2c <- sqrt((fixations$x-point2[1])^2 + (fixations$y-point2[2])^2) < (point12_sep / 2)
        
        fixations$idx <- c(1:nrow(fixations))
        # print(which(fixations$p1c | fixations$p2c))
        fixations <- fixations[which(fixations$p1c | fixations$p2c),]

        cat(sprintf('fixation set %d\n', fixation_sets))
        print(fixations)
        
        # cat('need fixations on both points\n')
        if (any(fixations$p1c) & any(fixations$p2c)) {
          # cat('both fixation points found\n')
          
          # cat('skipping fixations on point 1 after fixations on point 2\n')
          fixations <- fixations[which(fixations$idx <= max(fixations$idx[which(fixations$p2c)])),]    
          

        } else {
          # cat('both points need to be fixated\n')
          next
        }
        
        if (fixations$p1c[1]) {
          # first <- point1
          # second <- point2
          
          
        } else if (fixations$p2c[1]) {
          # first <- point2
          # second <- point1
          cat('fixation points switched\n')
          next
        } # else {
        #   first <- c(NA, NA)
        #   second <- c(NA, NA)
        # }
        
        f1_idx  <- max(which(fixations$p1c))
        
        f2i_idx <- min(which(fixations$p2c))
        f2c_idx <- max(which(fixations$p2c))
        
        intfixdist_init <- sqrt((fixations$x[f2i_idx]-fixations$x[f1_idx])^2 + (fixations$y[f2i_idx]-fixations$y[f1_idx])^2)
        if (f2c_idx > f2i_idx) {
          intfixdist_corr <- sqrt((fixations$x[f2c_idx]-fixations$x[f1_idx])^2 + (fixations$y[f2c_idx]-fixations$y[f1_idx])^2)
        } else {
          intfixdist_corr <- NA
        }
        
        
        print(intfixdist_init)
        print(intfixdist_corr)
        
        
        
        # store things
        
        # interfixationdata <-  list('block'=c(), 
        #                            'trial'=c(), 
        #                            'target'=c(), 
        #                            'BS_tilt'=c(),
        #                            'AW_tilt'=c(),
        #                            'point1_x'=c(), 
        #                            'point1_y'=c(), 
        #                            'point2_x'=c(), 
        #                            'point2_y'=c(), 
        #                            'intfixdist_init'=c(), 
        #                            'intfixdist_corr'=c())
        
        interfixationdata[['block']] <- c(interfixationdata[['block']], blockno)
        interfixationdata[['trial']] <- c(interfixationdata[['trial']], trialno)
        interfixationdata[['target']] <- c(interfixationdata[['target']], targetpair)
        interfixationdata[['BS_tilt']] <- c(interfixationdata[['BS_tilt']], BStilt)
        interfixationdata[['AW_tilt']] <- c(interfixationdata[['AW_tilt']], AWtilt)
        interfixationdata[['eye']] <- c(interfixationdata[['eye']], eye)
        interfixationdata[['AWratio']] <- c(interfixationdata[['AWratio']], AWratio)
        interfixationdata[['point1_x']] <- c(interfixationdata[['point1_x']], point1[1])
        interfixationdata[['point1_y']] <- c(interfixationdata[['point1_y']], point1[2])
        interfixationdata[['point2_x']] <- c(interfixationdata[['point2_x']], point2[1])
        interfixationdata[['point2_y']] <- c(interfixationdata[['point2_y']], point2[2])
        interfixationdata[['point_dist']] <- c(interfixationdata[['point_dist']], point12_sep)
        interfixationdata[['intfixdist_init']] <- c(interfixationdata[['intfixdist_init']], intfixdist_init)
        interfixationdata[['intfixdist_corr']] <- c(interfixationdata[['intfixdist_corr']], intfixdist_corr)
        
        
        

      #   if (nrow(fixations) == 0) {
      #     cat(sprintf("Block %d, Trial %d, Condition %s: no fixations\n", blockno, trialno, condition))
      #     next
      #   }
      # 
      #   rownames(fixations) <- 1:nrow(fixations)
      # 
      #   # print(fixations)
      #   if (condition == "") {
      #     condition <- conditionFromTargets(first=first, second=second)
      #   }
        
      #   cat(sprintf("Block %d, Trial %d, Condition %s: %d fixations\n", blockno, trialno, condition, dim(fixations)[1]))
      #   if (condition != "") {
      #     print('getting saccades')
      #     saccades <- getSaccades(condition=condition,
      #                             fixations=fixations,
      #                             time_s=mus, x=X, y=Y )
      #     saccades$block <- blockno
      #     saccades$trial <- trialno
      #     # print(saccades)
      #     if (is.data.frame(all_saccades)) {
      #       all_saccades <- rbind(all_saccades, saccades)
      #     } else {
      #       all_saccades <- saccades
      #     }
      #     plot(X, Y, type='l',
      #          main=sprintf("%s (block %d, trial %d)", condition, blockno, trialno),
      #          asp=1,col='#00000033')
      #     points(0,0,col='blue', pch=4)
      #     text(fixations$x, fixations$y, labels=sprintf('%d',c(1:dim(fixations)[1])), col='red', pch=1)
      #     Q <- c(saccades$Qstart_x, saccades$Qstart_y, saccades$Qend_x, saccades$Qend_y)
      #     if (!any(is.na(Q))) {
      #       lines(x = Q[c(1,3)],
      #             y = Q[c(2,4)], col='purple', lwd=2)
      #     }
      #     R <- c(saccades$Rstart_x, saccades$Rstart_y, saccades$Rend_x, saccades$Rend_y)
      #     if (!any(is.na(R))) {
      #       lines(x = R[c(1,3)],
      #             y = R[c(2,4)], col='orange', lwd=2)
      #     }
      # 
      #   }
      
      }
      
    }

  }
  
  # print(all_saccades)
  # write.csv(all_saccades, 'data/p03_saccades.csv', row.names=FALSE)
  # return(all_saccades)
  return(as.data.frame(interfixationdata))
  
}


getParticipantSaccades <- function(ppid) {

  allIFD <- NA
  for (hemifield in c('LH', 'RH')) {

    datafile <- sprintf('data/saccades/eyetracking/%s/HVsc%s1.csv', ppid, hemifield)

    IFD <- extractSaccadesFromFile(datafile)

    IFD$ppid <- ppid
    IFD$hemifield <- hemifield

    if (is.data.frame(allIFD)) {
      allIFD <- rbind(allIFD, IFD)
    } else {
      allIFD <- IFD
    }
  }

  return(allIFD)

}


getAllIFD <- function() {
  allIFD <- NA
  for (ppid in c('mtest')) {
    IFD <- getParticipantSaccades(ppid)
    if (is.data.frame(allIFD)) {
      allIFD <- rbind(allIFD, IFD)
    } else {
      allIFD <- IFD
    }
  }
  
  write.csv(allIFD, 'data/interfixationdata.csv', row.names=FALSE)
  return(allIFD)
  
}


plotIFDcontrols <- function() {
  
  # IFD <- getParticipantSaccades('mtest')
  IFD <- read.csv('data/mtest.csv', stringsAsFactors = FALSE)
  
  IFD <- IFD[which(IFD$AW_tilt == 0 & IFD$BS_tilt == 0 & IFD$eye == 'contra'),]
  
  
  plot(NULL,
       xlim=c(0.6, 1.4), ylim=c(0, max(c(IFD$intfixdist_init, max(IFD$intfixdist_corr)), na.rm=TRUE)),
       xlab='AW ratio', ylab='inter-fixation distance [dva]',
       bty='n')
  
  points(IFD$AWratio, IFD$intfixdist_init, col='blue', pch=1)
  
  IFD_m <- aggregate(intfixdist_init ~ AWratio, data=IFD, FUN=mean)
  
  points(IFD_m$AWratio, IFD_m$intfixdist_init, col='red', pch=19)
  
  AWratRange <- range(IFD$AWratio)
  
  # dist.odr <- Reach::odregress(x = IFD$AWratio, y = IFD$intfixdist_init)
  
  dist.lm <- lm(intfixdist_init ~ AWratio, data=IFD)
  print(summary(dist.lm))
  lines(x = AWratRange,
        y = dist.lm$coefficients[1] + dist.lm$coefficients[2] * AWratRange, col='red', lty=2, xpd=TRUE)
  
  default_length_LH <- IFD$point_dist[which(IFD$AWratio == 1 & IFD$hemifield == 'LH')[1]]
  default_length_RH <- IFD$point_dist[which(IFD$AWratio == 1 & IFD$hemifield == 'RH')[1]]
  
  lines(x = AWratRange,
        y = default_length_LH * AWratRange, col='black', lty=2, xpd=TRUE)
  lines(x = AWratRange,
        y = default_length_RH * AWratRange, col='black', lty=2, xpd=TRUE)
  
}