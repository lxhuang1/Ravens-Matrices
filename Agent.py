# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image
from PIL import ImageChops
import numpy as np

probNames = []
ansNames = []
equalityErrorRate = 0.02
problemType = ""
eliminatedAnswers = []
transposeMethods = []
otherTransformMethods = []

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints 
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self,problem):
        global problemType
        global probNames 
        global ansNames
        global eliminatedAnswers
        global transposeMethods
        global otherTransformMethods
        
      #  eliminatedAnswers = []
        transposeMethods = [Image.FLIP_LEFT_RIGHT, Image.FLIP_TOP_BOTTOM, Image.ROTATE_90, Image.ROTATE_180, Image.ROTATE_270]
        otherTransformMethods = [self.RollRight, self.RollTop]
        
        problemType = problem.problemType
        figureNames = []
        if problemType == "2x2":
             probNames = ["A","B","C"]
             ansNames = ["1","2","3","4","5","6"]
        else:
            probNames = ["A","B","C","D","E","F","G","H"]
            ansNames = ["1","2","3","4","5","6","7","8"]
        
        #creates matrix with number of total black pixels for each image provided
        probDataMatrix = self.FindDataMatrix(problem, probNames)
        ansDataMatrix = self.FindDataMatrix(problem, ansNames)
        print("ProbDataMatrix: ")
        print(probDataMatrix)
        print("AnsDataMatrix: ")
        print(ansDataMatrix)
        
        #try a set of short-cut heuristics to find an exact match
        ans = self.Heuristics(probDataMatrix, ansDataMatrix)
        if ans != -1:
            return ans
        
        #try a set of transformations to find an exact match
        ans = self.Transformations(problem.figures)
        if ans != -1:
            return ans
        
        #try Average Error Algorithm to find most likely answer
        ans = self.AvgErrorAlg(probDataMatrix, ansDataMatrix) 
        print("Best guess answer: ", ans)
        return ans
       
        return -1

    def Transformations(self, problemFigures):
    #tries a set of transformations to see if they apply to given problem, if so returns corresponding answer choice if it exists
        
        answer = -1
        foundAnswer = -1
        startFigure = problemFigures["A"]
        endFigureHorizontal = None
        endFigureVertical = None
        
        if problemType == "2x2":
            endFigureHorizontal = problemFigures["B"]
            endFigureVertical = problemFigures["C"]
        else:
            endFigureHorizontal = problemFigures["C"]
            endFigureVertical = problemFigures["G"]
        
        #tries all methods in transposeMethods. Returns projected image if find match, or None if not
        answer = self.Transpose(problemFigures, startFigure, endFigureHorizontal, endFigureVertical)
        
        if answer != -1:
            return answer
        
        return -1
        
    def Transpose(self, problemFigures, startFigure, endFigureHorizontal, endFigureVertical):
    #tries a series of transformations on images. Returns projected image if rotation found to match problem, or None if not
    
        answer = -1
        startImage = Image.open(startFigure.visualFilename)
        endImageHorizontal = Image.open(endFigureHorizontal.visualFilename)
        endImageVertical = Image.open(endFigureVertical.visualFilename)
        possibleAnswers = set()

        #try all transpose methods in transposeMethods
        for method in transposeMethods:
            transposedImage = startImage.transpose(method)
            if self.ImagesEqual(transposedImage, endImageHorizontal):
                print("Found transpose match for horizontal")
                #check that the solution with the transposed image works in the context of the entire problem. check for analogous vertical relationships
                proposedAnswerImage = endImageVertical.transpose(method)
                #if self.SolutionWorks(startImage, endImageVertical, endImageHorizontal, proposedAnswerImage):
                self.findMatchingAnswer(proposedAnswerImage, problemFigures, possibleAnswers)
            if self.ImagesEqual(transposedImage, endImageVertical):
                print("Found transpose match for vertical")
                #check that the solution with the transposed image works in the context of the entire problem. check for analogous horizontal relationships
                proposedAnswerImage = endImageHorizontal.transpose(method)
                #if self.SolutionWorks(startImage, endImageHorizontal, endImageVertical, proposedAnswerImage):
                self.findMatchingAnswer(proposedAnswerImage, problemFigures, possibleAnswers)
            else:
                print("No vertical transpose match found")
            
        #try other image transformations
        for transform in otherTransformMethods:
            transposedImage = transform(startImage)
            if self.ImagesEqual(transposedImage, endImageHorizontal):
                print("Found other transformation match")
                #check that the solution with the transposed image works in the context of the entire problem. check for analogous vertical relationships
                proposedAnswerImage = transform(endImageVertical)
                #if self.SolutionWorks(startImage, endImageVertical, endImageHorizontal, proposedAnswerImage):
                self.findMatchingAnswer(proposedAnswerImage, problemFigures, possibleAnswers)
            if self.ImagesEqual(transposedImage, endImageVertical):
                print("Found transpose match for vertical")
                #check that the solution with the transposed image works in the context of the entire problem. check for analogous horizontal relationships
                proposedAnswerImage = endImageHorizontal.transpose(method)
                #if self.SolutionWorks(startImage, endImageHorizontal, endImageVertical, proposedAnswerImage):
                self.findMatchingAnswer(proposedAnswerImage, problemFigures, possibleAnswers)
        
        if len(possibleAnswers) == 1:
            print("possible answers: ", possibleAnswers)
            return possibleAnswers.pop()
        else:
            print("possible answers: ", possibleAnswers)
            return -1        
           
      
           
    
    def RollRight(self, image):
        xsize, ysize = image.size

        delta = int(xsize / 2)

        newImage = Image.new("RGBA", (xsize, ysize))

        part1 = image.crop((0, 0, delta, ysize))
        part2 = image.crop((delta, 0, xsize, ysize))
        part1.load()
        part2.load()
        newImage.paste(part2, (0, 0, xsize-delta, ysize))
        newImage.paste(part1, (xsize-delta, 0, xsize, ysize))
        
        return newImage
    
    def RollTop(self, image):
        xsize, ysize = image.size

        delta = int(ysize / 2)

        newImage = Image.new("RGBA", (xsize, ysize))
        
        part1 = image.crop((0, 0, xsize, delta))
        part2 = image.crop((0, delta, xsize, ysize))
        part1.load()
        part2.load()
        newImage.paste(part2, (0, 0, xsize, ysize-delta))
        newImage.paste(part1, (0, ysize-delta, xsize, ysize))
        
        return newImage



    def findMatchingAnswer(self, targetImage, problemFigures, possibleAnswers):
    #loops through answers and tries to find one that matches the target image provided. Returns matching image if found, None if not
    
        for answer in ansNames:
            answerImage = Image.open(problemFigures[answer].visualFilename)
            if self.ImagesEqual(targetImage, answerImage):
                possibleAnswers.add(int(answer))
                print("Found Match: ", answer)
    

    def ImagesEqual(self, image1, image2):
    #compares 2 images and returns True if images are "equal" and False if not; current acceptable error rate is 3%
    
        diffImage = ImageChops.difference(image1, image2)
        
        diffValue = 0
        for value in list(diffImage.getdata(0)):
            if value > 128:
                diffValue = diffValue+value
        print("Difference before correction: ", sum(diffImage.getdata(0)))
        print("Difference: ", diffValue)
        if diffValue < (8700000 *0.03): #error rate 3%
            return True
            
        return False
            

    def Heuristics(self, probDataMatrix, ansDataMatrix):
    # runs a set of short-cut heuristics to try to find an exact match answer choice. Returns -1 if none found
        
        #check if same number of incremental pixels added/subtracted as figure moves horizontally and vertically (can be increments unique per row/column). 
        #If so, return corresponding answer choice
        ans = self.IncrementChange(probDataMatrix, ansDataMatrix)
        if ans != -1:
            return ans
  
        #return -1 of none of the above heuristics yields an answer
        return -1
  
 
        
  
    def IncrementChange(self, probDataMatrix, ansDataMatrix):
    #looks to see if any object added/subtracted, returns corresponding answer if so
        
        print("Running Increment Change")
        
        projection1,projection2 = 0,0 
        if problemType == "2x2":
        
            #subtract total # of black pixels horizontally, apply to lower-left corner = guess D1
            print(probDataMatrix, ansDataMatrix)
            pixelDiff = probDataMatrix[1,1] - probDataMatrix[0,1]
            projection1 = probDataMatrix[2,1]+pixelDiff
            print("PixelDiff: ", pixelDiff, "Projected Pixels 1: ", projection1)
        
            #subtract total # of black pixels vertically, apply average subtraction to upper-right corner = guess D2
            pixelDiff = probDataMatrix[2,1] - probDataMatrix[0,1]
            projection2 = probDataMatrix[1,1]+pixelDiff
            print("PixelDiff: ", pixelDiff, "Projected Pixels 2: ", projection2)
        
        else:
            #check pixel change increment horizontally
            #check if pixel increment change is same for A->B->C and D->E->F. 
            #If so, applies pixel change from G->H to H to estimate pixels in projection1
            pixelDiff1A = probDataMatrix[1,1] - probDataMatrix[0,1]
            pixelDiff1B = probDataMatrix[2,1] - probDataMatrix[1,1]
            pixelDiff2A = probDataMatrix[4,1] - probDataMatrix[3,1]
            pixelDiff2B = probDataMatrix[5,1] - probDataMatrix[4,1]
            pixelDiff3A = probDataMatrix[7,1] - probDataMatrix[6,1]
            print("Horizontal Increments1: ", pixelDiff1A, pixelDiff1B)
            print("Horizontal Increments2: ", pixelDiff2A, pixelDiff2B)
            print("last row increment: ", pixelDiff3A)
            
            #acceptable error rate of 15%
            if abs(pixelDiff1A / pixelDiff1B-1) < 0.15 and abs(pixelDiff2A / pixelDiff2B-1) < 0.15: 
                projection1 = probDataMatrix[7,1]+pixelDiff3A
                print("Found Projection1: ", projection1)
            
            #check pixel change increment vertically
            #check if pixel increment change is same for A->D->G and B->E->H. 
            #If so, applies pixel change from C->F to F to estimate pixels in projection2
            pixelDiff1A = probDataMatrix[3,1] - probDataMatrix[0,1]
            pixelDiff1B = probDataMatrix[6,1] - probDataMatrix[3,1]
            pixelDiff2A = probDataMatrix[4,1] - probDataMatrix[1,1]
            pixelDiff2B = probDataMatrix[7,1] - probDataMatrix[4,1]
            pixelDiff3A = probDataMatrix[5,1] - probDataMatrix[2,1]
            print("Vetical Increments1: ", pixelDiff1A, pixelDiff1B)
            print("Vertical Increments2: ", pixelDiff2A, pixelDiff2B)
            print("last column increment: ", pixelDiff3A)
            
            #acceptable error rate of 15%
            if abs(pixelDiff1A / pixelDiff1B-1) < 0.15 and abs(pixelDiff2A / pixelDiff2B-1) < 0.15: 
                projection2 = probDataMatrix[5,1]+pixelDiff3A
                print("Found Projection2: ", projection2)
        
        #if there are projections for 1 & 2, find corresponding answer choice for projection based on # of pixels and return answer
        #accepts 15% error rate
        if projection2 != 0:
            #if self.FuzzyEquals(projection1,projection2):
            if abs(projection1 / projection2-1) < 0.15:
                print("Project1 and Projection2 match")
                possibleAnswers = []
                ansChoice = 1
                projection = (projection1+projection2)/2
                for answer in ansDataMatrix:
                    if self.FuzzyEquals(answer[1],projection):
                        print("possible answer: ", ansChoice, "number of pixels: ", answer[1])
                        possibleAnswers.append(ansChoice)
                    ansChoice = ansChoice +1
               
                
                if len(possibleAnswers) == 1:
                    print("Found Answer with incremental change heuristic: Answer Choice ", possibleAnswers[0])
                    return possibleAnswers[0]
                
        return -1
  
    
    def FuzzyEquals(self,a,b):
    # bitmapSN considered equal if within error rate given by equalityErrorRate
        if b == 0:
            return a==0
        elif abs(a/b-1) < equalityErrorRate:
            return True
        return False


    def AvgErrorAlg(self, probDataMatrix, ansDataMatrix):
    # runs average error algorithm based on specified set of attributes and returns corresponding answer choice
        print("Running AvgErrorAlg")
        print("ProbDataMatrix: ")
        print(probDataMatrix)
        print("AnsDataMatrix: ")
        print(ansDataMatrix)
        
        errorVector=[]
        D1=[]
        D2=[]
        
        #find expected D1 based on horizontal transformations from A and D2 based on vertical transformations from A
        D1,D2 = [],[]
        
        if problemType == "2x2":
            #average horizontal transformations
            D1Trans = probDataMatrix[1] / probDataMatrix[0]
            D1 = probDataMatrix[2] * D1Trans
        
            #expected value from average vertical transformations
            D2Trans = probDataMatrix[2] / probDataMatrix[0]
            D2 = probDataMatrix[1] * D2Trans
        else: 
            #average horizontal transformations
            D1ATrans = probDataMatrix[2] / probDataMatrix[0]
            D1BTrans = probDataMatrix[5] / probDataMatrix[3]
            D1Trans = (D1ATrans + D1BTrans)/2
            D1 = probDataMatrix[6] * D1Trans
            
            #expected value from average vertical transformations
            D2ATrans = probDataMatrix[6] / probDataMatrix[0]
            D2BTrans = probDataMatrix[7] / probDataMatrix[1]
            D2Trans = (D2ATrans + D2BTrans)/2
            D2 = probDataMatrix[2] * D2Trans
        
        print("D1Trans: ", D1Trans, "D2Trans: ",D2Trans)
        print("Expected D1: ", D1, "Expected D2: ", D2)
        
        #calculate total error rate for each answer based on expected D1 and D2, and add into errorVector
        answerIndex = 1
        for answer in ansDataMatrix:
            print("Answer Choice: ", answerIndex)
            errorVec1 = (answer / D1 - 1)**2
            totError1 = np.sum(errorVec1[2:]) + 4*errorVec1[1]
            errorVec2 = (answer / D2 - 1)**2
            totError2 = np.sum(errorVec2[2:]) + 4*errorVec1[1]
            print("ErrorVec1: ", errorVec1)
            print("D1 error: ", totError1)
            print("ErrorVec2: ", errorVec2)
            print("D2 error: ", totError2)
            totError = totError1 + totError2
            print("Total Error: ", totError)
            errorVector.append(totError)
            answerIndex = 1+answerIndex
        print("ErrorVector for all Answers: ",errorVector)
        
        
        minError = min(i for i in errorVector if i >= 0)
        likelyAns = errorVector.index(minError)+1
        print("Proposed Answer: ", likelyAns)
        return likelyAns
        
    
    def FindDataMatrix(self, problem, names):
    # returns matrix encapsulating basic information about the images given
    # attribute #0: bitmapSN -- unique number for each image, which is sum of each pixel's absolute location from origin (0,0)
    # attribute #1: totBlack - number of total black pixels for each image provided
    # attribute #2: topWeight - number or black pixels in top-half of figure
    # attribute #3: bottomWeight - number of black pixels in bottom-half of figure
    # attribute #4: leftWeight - number of black pixels in left-half of figure
    # attribute #5: rightWeight - number of black pixels in right-half of figure
    
        dataMatrix = np.zeros((len(names),6))
 
        imageCounter = 0
        for name in names:
            im = Image.open(problem.figures[name].visualFilename)
            xsize, ysize = im.size
            pixCounter = 0
            
            pixels = list(im.getdata(0))
            bitmapSN, totBlack = 0,0
            topWeight, bottomWeight, leftWeight, rightWeight = 1,1,1,1

            for pixelVal in pixels:
                # only execute for black pixels, defined as any value that is 0
                if pixelVal < 128:
                    currXVal = pixCounter % xsize
                    currYVal = pixCounter // xsize
                    
                    #attribute #0
                    bitmapSN = bitmapSN+pixCounter*pixCounter
                    
                    #attribute #1
                    totBlack=totBlack+1
                    
                    #attribute #2,3
                    if currYVal < ysize/2:
                        topWeight=topWeight+1
                    else:
                        bottomWeight=bottomWeight+1
                    
                    #attribute #4,5
                    if currXVal < xsize/2:
                        leftWeight=leftWeight+1
                    else:
                        rightWeight=rightWeight+1
                    
                    
                pixCounter = pixCounter + 1   
            dataMatrix[imageCounter,0] = bitmapSN
            dataMatrix[imageCounter,1] = totBlack
            dataMatrix[imageCounter,2] = topWeight
            dataMatrix[imageCounter,3] = bottomWeight
            dataMatrix[imageCounter,4] = leftWeight
            dataMatrix[imageCounter,5] = rightWeight
           
            imageCounter = imageCounter+1
        return dataMatrix   
        


                    
        
       
