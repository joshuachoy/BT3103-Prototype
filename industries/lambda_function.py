# -*- coding: utf-8 -*-
import json
import traceback
import logging

import re

import signal
import time

import pandas as pd
import boto3
import doctest

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

#from pandas.compat import StringIO


def lambda_handler(event, context):
     # TODO implement
    dynamodb = boto3.resource("dynamodb", region_name = "us-east-1")
    table = dynamodb.Table("Fraud_data")
    
    response = table.scan()

    index_lst = []
    type_lst = []
    amount_lst = []
    oldbalanceOrig_lst = []
    newbalanceOrig_lst = []
    oldbalanceDest_lst = []
    newbalanceDest_lst = []
    isFraud_lst = []
    for i in response['Items']:
        index_lst.append(i['index'])
        type_lst.append(i['type'])
        amount_lst.append(i['amount'])
        oldbalanceOrig_lst.append(i['oldbalanceOrig'])
        newbalanceOrig_lst.append(i['newbalanceOrig'])
        oldbalanceDest_lst.append(i['oldbalanceDest'])
        newbalanceDest_lst.append(i['newbalanceDest'])
        isFraud_lst.append(i['isFraud'])
    
    d = {'index': index_lst, 'type': type_lst, 'amount': amount_lst, 'oldbalanceOrig': oldbalanceOrig_lst,
        'newbalanceOrig': newbalanceOrig_lst, 'oldbalanceDest': oldbalanceDest_lst, 'newbalanceDest': newbalanceDest_lst, 'isFraud': isFraud_lst}
    df = pd.DataFrame(data=d)
    
    

    ####################################################### Codes to Run Website Comes Below ###################################################################


    def run_local(requestDict):
        #namespace = UsedNamespace()
    
        #Add a try here to catch errors and return a better response
        solution = requestDict['solution']
        tests = requestDict['tests']
        questionType = requestDict["type"]
        
        import io
        import sys
        # Store App Engine's modified stdout so we can restore it later
        gae_stdout = sys.stdout
        # Redirect stdout to a StringIO object
        new_stdout = io.StringIO()
        sys.stdout = new_stdout

        try:
            namespace = {}
            compiled = compile('import json', 'submitted code', 'exec')
            exec(compiled, namespace, {"df": df})
            compiled = compile(solution, 'submitted code', 'exec')
            exec(compiled, namespace, {"df": df})
            namespace['YOUR_SOLUTION'] = solution.strip()
            namespace['LINES_IN_YOUR_SOLUTION'] = len(solution.strip().splitlines())

            test_cases = doctest.DocTestParser().get_examples(tests)
            results, solved = execute_test_cases(test_cases, namespace, questionType)
        
            # Get whatever was printed to stdout using the `print` statement (if necessary)
            printed = new_stdout.getvalue()
            # Restore App Engine's original stdout
            sys.stdout = gae_stdout
        
            responseDict = {"solved": solved , "results": results, "printed":printed}
        
            #Add a try here can catch errors. 
            responseJSON = json.dumps(responseDict)
            logging.info("Python verifier returning %s",responseJSON)
            return responseJSON
        except:
            sys.stdout = gae_stdout
            errors = traceback.format_exc()
            logging.info("Python verifier returning errors =%s", errors)
            if len(errors) > 500:
                lines = errors.splitlines()
                i = len(lines) - 1
                errors = lines[i]
                i -= 1
                while i >= 0:
                    line = lines[i]
                    s = '%s\n%s' % (line, errors)
                    if len(s) > 490:
                        break
                    errors = s
                    i -= 1
                errors = '...\n%s' % errors

            responseDict = {'errors': '%s' % errors}
            responseJSON = json.dumps(responseDict)
            #logging.info("######## Returning json encoded errors %s", responseJSON)
            return responseJSON

    #Refactor for better readability.
    def execute_test_cases(testCases, namespace, questionType):
        resultList = []
        solved = True
        for test in testCases:
            # the next if statement may not be needed, just only if there is no answer provided for the test case but there's no assignment of results
            if not test.want:
                exec(test.source, namespace)
                continue
            call = test.source.strip()
            logging.warning('call: %s', (call,))
            got = eval(namespace["YOUR_SOLUTION"], {"df": df})                  #! Edited Here and the next few rows below
            
            
            if questionType == "non-dataframe":
                expected = eval(test.want)
                correct = True
                if got == expected:
                    correct = True
                else:
                    correct = False
                    solved = False
                    
            elif questionType == "dataframe":
                
                expected = test.want[:-1].replace("--", "\n")
                
                
                # Purposely converting "got" that is a dataframe into a string format and back to dataframe again because
                # in the process of doing so, there are changes from int values to float values
                # we need to do this to match the results of expected
                
                got = got.to_string().replace("\n", "--")
                got = got.replace("--", "\n")
                
                got = pd.read_csv(StringIO(got), sep = "\s+")
                expected = pd.read_csv(StringIO(expected), sep = "\s+")
                
                
                if got.equals(expected):                   
                    correct = True
                else:
                    correct = False
                    solved = False
                
                expected = expected.to_html()
                
                got = got.to_html()
                
                # got = got.to_string().replace("\n", "--")
                # expected = test.want[:-1]
                # if got == test.want[:-1]:                                       # use of test.want[:-1] as for some reason, test.want adds an extra space behind the solution
                #     correct = True
                # else:
                #     correct = False
                #     solved = False
            resultDict = {'call': call, 'expected': expected, 'received': "%(got)s" % {'got': got}, 'correct': correct, "questionType": questionType}    #! Edited Here
            resultList.append(resultDict)
        return resultList, solved
    
    method = event.get('httpMethod',{}) 
        
    indexPage="""
    <!DOCTYPE html>
<html lang="en">
  <head>
    <title>Industries Website Template by Colorlib</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700|Oxygen:400,700" rel="stylesheet">

    <link rel="stylesheet" href="https://mylambdajosh.s3.amazonaws.com/css/animate.css">
    <link rel="stylesheet" href="https://mylambdajosh.s3.amazonaws.com/css/owl.carousel.min.css">
    <link rel="stylesheet" href="https://mylambdajosh.s3.amazonaws.com/css/jquery.fancybox.min.css">

    <link rel="stylesheet" href="https://mylambdajosh.s3.amazonaws.com/fonts/ionicons/css/ionicons.min.css">
    <link rel="stylesheet" href="https://mylambdajosh.s3.amazonaws.com/fonts/fontawesome/css/font-awesome.min.css">

    <!-- Theme Style -->
    <link rel="stylesheet" href="https://mylambdajosh.s3.amazonaws.com/css/style.css">

    <!-- Google Prettify Script-->
    <script src="https://cdn.jsdelivr.net/gh/google/code-prettify@master/loader/run_prettify.js"></script>
    
    <!-- VueJS Scripts-->
    <script src="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
    <script src="https://unpkg.com/vuex"></script>

  </head>
  <body>
    
    <header role="banner">
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
          <a class="navbar-brand " href="index.html"><img src="images/invert.png"width = "280" height = "180"></a>
          <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarsExample05" aria-controls="navbarsExample05" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>

          <div class="collapse navbar-collapse" id="navbarsExample05">
            <ul class="navbar-nav pl-md-5 ml-auto">
              <li class="nav-item">
                <a class="nav-link active" href="index.html">Home</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="about.html">About</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="projects.html">Projects</a>
              </li>
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="services.html" id="dropdown04" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Industries</a>
                <div class="dropdown-menu" aria-labelledby="dropdown04">
                  <a class="dropdown-item" href="services.html">Finance</a>
                  <a class="dropdown-item" href="services.html">Consumer Goods</a>
                  <a class="dropdown-item" href="services.html">Others</a>
                </div>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="blog.html">Blog</a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="contact.html">Contact</a>
              </li>
            </ul>

          
          </div>
        </div>
      </nav>
    </header>
    <!-- END header -->

    <div class="top-shadow"></div>

    <div class="inner-page">
    <div class="slider-item" style="background-image: url('images/money1.jpg');">
        
        <div class="container">
          <div class="row slider-text align-items-center justify-content-center">
            <div class="col-md-8 text-center col-sm-12 element-animate pt-5">
              <h1 class="pt-5"><span>Fraud Detection</span></h1>
              <p class="mb-5 w-75 pl-0">To identify and analyse characteristics of fraudulent transactions</p>
            </div>
          </div>
        </div>

      </div>
    </div>
    <!-- END slider -->
    </div>
    
      <div class="container" id="vueOnly">
        <div class="row">
          <div class="col-12" style="margin-top: -150px;">
            <p><img src="images/stock3.jpg" alt="Image" class="img-fluid"></p>
          </div>
        </div>
        <div class="row justify-content-center">
          <div class="col-md-8 mb-5">
            <h1>Overview</h1>
            
            <!--<iframe class="col-md-12" id="code-box" src="test.html"></iframe>-->
            

            <p> ipsum dolor sit amet, consecteturLorem adipisicing elit. Vero nulla delectus sit vel magnam, ad voluptatem hic. Maxime ipsam quibusdam eius exercitationem iusto, totam possimus dolore magnam voluptatum illum consequuntur.</p>
            <p> Fraud Detection is a commonly employed activity in banking industries to identify customers who obtain money illegally. </p>
            <h1>Aim</h1>
            <p> To analyse characteristics of fraudulent transactions </p>
          </div>
        </div>
        <div class="row justify-content-center">
          <div class="col-md-8 mb-5">
            <h1> Dataset </h1>
            <iframe width="830" height="400" src="https://docs.google.com/spreadsheets/d/e/2PACX-1vTxLAhPejZjOPpuM7jgq6vhy6Y5FVqAV_oK0JKlrc1PsR9IPEAp1eccHHS74YJvWAdsyam2JP-w3btJ/pubhtml?gid=1157778684&amp;single=true&amp;widget=true&amp;headers=false"></iframe>
          </div>
        </div>

        <div class="row justify-content-center">
          <div class="col-md-8">
            <p>Fraud Dataset contains 500 rows and 7 columns. </p>
            <p> Columns are: </p>
            <p> 1) index: specifies the row ID in dataset </p>
            <p> 2) type: specifies the kind of transaction made (e.g. PAYMENT, DEBIT, TRANSFER) </p>
            <p> 3) amount: specifies the amount of money involved in the transaction </p>
            <p> 4) oldbalanceOrg: displays the original balance of the account </p>
            <p> 5) newbalanceOrg: displays the new balance of account after transaction </p>
            <p> 6) oldbalanceDest: displays the old balance of the destination account, which is the account in which money will be transferred to </p>
            <p> 7) newbalanceDest: displays the new balance of destination account , which is the account in which money has been transferred to </p>
            <p> 8) isFraud: indicates the possibility that a transaction is fraud where 1 = yes and 0 = no </p>
          </div>
        </div>

        <div class="row justify-content-center">
          <div class="col-md-8">     
            <h1> 0. Let's get started and install Pandas package in your desktop! </h1>
            <iframe width="560" height="315" src="https://www.youtube.com/embed/8Sipkd9vNKk" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
            <h1> 1. Load in File</h1>
            <h2> 1.1. Loading in Data </h2>
            <p> Loading data from different types of file (.txt or .csv or .xlsx) </p>
            <p> </p>
            <p> Step 1: Save file in same folder as current Python script. </p>
            <p> Step 2: Open file </p>
            <ul> 
              <li> For CSV file </li>
              <iframe src="loadcsv.html" width="100%"></iframe>
              <li> For Text file </li>
              <iframe src="loadtxt.html" width="100%"></iframe>
              <li> For Excel file </li>
              <iframe src="loadexcel.html" width="100%"></iframe>
            </ul>
            <p>How do we open a text file named “StockData” that has tabs between data?</p>

                <form name="myForm">
                    <input type="radio" name="myRadios"  value="1" >df = pd.read_excel(“StockData.txt”)<br>
                    <input type="radio" name="myRadios"  value="2" >df = pd.read_csv((“StockData.txt”, delimiter = “/t”)<br>
                    <input type="radio" name="myRadios"  value="3" >df = pd.read_csv(“StockData.txt”, delimiter = “,”)<br>
                </form>
                <span id="1.2 answer"></span>
                
                <script>
                var amountField = document.getElementById('1.2 answer');
                var rad = document.myForm.myRadios;
                for(var i = 0; i < rad.length; i++) {
                    rad[i].onclick = function() {
                        console.log(this.value);
                        if(this.value == 2) {
                            amountField.textContent = "Correct!";
                        } else{
                            amountField.textContent = "Wrong. Please try again.";
                        }
                    };
                }
                </script>
            <p style="color:red;"> Checkpoint: Question insert here for user to practice loading in data. </p>

            <h2> 1.2. Checking Loaded Data </h2>
            <p> Always make it a practice to check that our data has been loaded correctly (meaning all columns and rows are loaded). </p>
            <p> Step 1: Check the number of rows and columns. </p>
            <ul>
              <li> Showing the number of rows then number of columns. </li>
              <iframe src="dfShape.html" width="100%"></iframe>
              <li> Print out results to interpret numbers easily. </li>
              <iframe src="printRowCol.html" width="100%"></iframe>
            </ul>
          </div>
        </div>

        <head>
        <meta charset="utf-8">
        <meta content="width=device-width,initial-scale=1,minimal-ui" name="viewport">
        <link rel="stylesheet" href="https://unpkg.com/vue-material@beta/dist/vue-material.min.css">
        <link rel="stylesheet" href="https://unpkg.com/vue-material@beta/dist/theme/default.css">
        </head>
        <body>
          <h1>Q1. Checking Loaded Data Activity</h1>
          <div>
              <doctest-activity v-bind:layout-things=questions[0].layoutItems v-bind:question-name=questions[0].name>
          </div>
        </body>
        <body>
          <h1>Q2. Get First Few Rows Activity</h1>
            <div>
              <doctest-activity v-bind:layout-things=questions[1].layoutItems v-bind:question-name=questions[1].name>
            </div>
        </body>
        
        <div class="row justify-content-center">
          <div class="col-md-8">
              <p> Step 2: Check the first few rows. </p>
              <ul>
                <li> Display first 5 rows of data. </li>
                <iframe src="showFirst5.html" width="100%"></iframe>
                <li> Display first 10 rows of data. </li>
                <iframe src="showFirst10.html" width="100%"></iframe>
              </ul>
              <p> Step 3: Check the last few rows. </p>
              <ul>
                <li> Display last 5 rows of data. </li>
                <iframe src="showlast5.html" width="100%"></iframe>
                <li> Display last 20 rows of data. </li>
                <iframe src="showlast20.html" width="100%"></iframe>
              </ul>
              <p style="color:red;"> Checkpoint: Question insert here for user to practice checking first/last few rows of data. </p>

              <h1> 2. Data Exploration </h1>
              <h2> Exploratory Data Analysis </h2>
              <p> Exploratory Data Analysis (EDA) is performed in which mean, standard deviation and correlation etc. are found between variables. This gives us a better understanding of the data we are dealing with. </p>
              <p> Step 1: Finding Mean of Variables. </p>
              <ul>
                <li> The function .mean() can be called to the dataframe. It will return the mean values of each variable of type numeric and float. </li>
                <li> Note that the resulting table of mean does not include variables of string data type (e.g. column “type”). </li>
                <iframe src="dfMean.html" width="100%"></iframe>
                <li style="color:red;"> Show output table here. </li>
              </ul>
              <p> Step 2: Finding Median of Variables. </p>
              <ul>
                <li> The function .median() can be called to the dataframe. It will return the median value of each variable of type numeric and float. </li>
                <iframe src="dfMedian.html" width="100%"></iframe>
                <li style="color:red;"> Show output table here. </li>
              </ul>

              <p> Step 3: Finding Standard Deviation of Variables. </p>
              <ul>
                <li> The function .std() can be called to the dataframe. It will return the standard deviation value of each variable of type numeric and float. </li>
                <iframe src="dfStandardDe.html" width="100%"></iframe>
                <li style="color:red;"> Show output table here. </li>
              </ul>

              <p> Step 4: Finding Correlations between Variables. </p>
              <ul>
                <li> The function .corr() can be called to the dataframe. It will return the correlation value between every variable of type numeric and float. </li>
                <iframe src="dfCorr.html" width="100%"></iframe>
              </ul>
              <div class="row justify-content-center">
                <div class="col-md-8 mb-5">
                  <h3> df.corr() </h3>
                  <iframe width="830" height="400" src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRwMhm8TtteDrr4b9evXy3va8U2ztEn6MdMkszi4Tz4nfU3s2cTmLPgPoQF6gAz64mw7CK0iUWaIhkB/pubhtml?gid=0&single=true"></iframe>
                </div>
              </div>
              <p style="color:red;"> Checkpoint: Question insert here for user to perform EDA on data. </p>

              <h1> 3. Data Cleaning </h1>
              <h2> 3.1. Checking for NA rows and columns </h2>
              <p> In reality, datasets are full of inconsistencies such as missing values due to poor data collection and management practices. To avoid running into errors when furthering our analysis, we need to clean our data. </p>
              <p> Step 1: Examine if data entries are null values. </p>
              <ul>
                <li> This method is only suitable for small datasets as it is hard to examine numerous rows and columns. </li>
                <iframe src="dfNull.html" width="100%"></iframe>
              </ul>
              <div class="row justify-content-center">
                <div class="col-md-8 mb-5">
                  <h3> df.isNull() </h3>
                  <iframe width="830" height="400" src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRwMhm8TtteDrr4b9evXy3va8U2ztEn6MdMkszi4Tz4nfU3s2cTmLPgPoQF6gAz64mw7CK0iUWaIhkB/pubhtml?gid=1148384071&single=true"></iframe>
                </div>
              </div>
              <p> Step 2: More concise method to checking for null values. </p>
              <ul>
                <li> Show the sum of null values in each column. </li>
                <iframe src="dfNullSum.html" width="100%"></iframe>
                <li style="color:red;"> Show output table here. </li>
              </ul>

              <h2> 3.2. Dealing with NA values </h2>
              <p> Method 1: Dropping all rows that have at least 1 null value. </p>
              <iframe src="dfDropNA.html" width="100%"></iframe>
              <p> Method 2: Replacing null values with the computed mean of column/variable. </p>
              <iframe src="dfReplaceNA.html" width="100%"></iframe>
              <p style="color:red;"> Checkpoint: Question insert here for user to practice cleaning data. </p>

              <h1> 4. Subsetting Data </h1>
              <h2> 4.1. Subsetting based on a single condition </h2>
              <p> Understanding data better by subsetting smaller sections that are of our interest. </p>
              <iframe src="dfSubsetSingle.html" width="100%"></iframe>
              <p style="color:red;"> Show output table here. </p>

              <h2> 4.2. Subsetting based on multiple condition </h2>
              <p> & refers to “and” where both conditions has to be satisfied. </p>
              <p> | refers to “or” where either condition has to be satisfied. </p>
              <iframe src="dfSubsetMultiple.html" width="100%"></iframe>
              <p style="color:red;"> Show output table here. </p>
              <p style="color:red;"> Checkpoint: Question insert here for user to practice subsetting data. </p>

              <h1> 5. Sorting Data </h1>
              <h2> 5.1. Sorting in Ascending Order </h2>
              <p> Sorting can help to easily identify the largest or smallest rows of data. </p>
              <iframe src="dfSortingAscending.html" width="100%"></iframe>
              <div class="row justify-content-center">
                <div class="col-md-8 mb-5">
                  <h3> Sorting - Ascending Order </h3>
                  <iframe width="830" height="400" src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRwMhm8TtteDrr4b9evXy3va8U2ztEn6MdMkszi4Tz4nfU3s2cTmLPgPoQF6gAz64mw7CK0iUWaIhkB/pubhtml?gid=411973687&single=true"></iframe>
                </div>
              </div>

              <h2> 5.2. Sorting in Descending Order </h2>
              <iframe src="dfSortingDescending.html" width="100%"></iframe>
              <div class="row justify-content-center">
                <div class="col-md-8 mb-5">
                  <h3> Sorting - Descending Order </h3>
                  <iframe width="830" height="400" src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRwMhm8TtteDrr4b9evXy3va8U2ztEn6MdMkszi4Tz4nfU3s2cTmLPgPoQF6gAz64mw7CK0iUWaIhkB/pubhtml?gid=1748770864&single=true"></iframe>
                </div>
              </div>
              <p style="color:red;"> Checkpoint: Question insert here for user to practice sorting data. </p>

              <p><a href="#" class="btn btn-primary py-3 px-3">Try Project!</a></p>
            </div>
        </div>
      </div>
    </div>
    
    <footer class="site-footer bg-light" role="contentinfo">
      <div class="container">
        <div class="row mb-5">
          <div class="col-md-4 mb-5">
            <h3>About Us</h3>
            <p class="mb-5">Far far away, behind the word mountains, far from the countries Vokalia and Consonantia, there live the blind texts. .</p>
            <ul class="list-unstyled footer-link d-flex footer-social">
              <li><a href="#" class="p-2"><span class="fa fa-twitter"></span></a></li>
              <li><a href="#" class="p-2"><span class="fa fa-facebook"></span></a></li>
              <li><a href="#" class="p-2"><span class="fa fa-linkedin"></span></a></li>
              <li><a href="#" class="p-2"><span class="fa fa-instagram"></span></a></li>
            </ul>

          </div>
          <div class="col-md-5 mb-5 pl-md-5">
            <h3>Contact Info</h3>
            <ul class="list-unstyled footer-link">
              <li class="d-block">
                <span class="d-block">Address:</span>
                <span >34 Street Name, City Name Here, United States</span></li>
              <li class="d-block"><span class="d-block">Telephone:</span><span >+1 242 4942 290</span></li>
              <li class="d-block"><span class="d-block">Email:</span><span >info@yourdomain.com</span></li>
            </ul>
          </div>
          <div class="col-md-3 mb-5">
            <h3>Quick Links</h3>
            <ul class="list-unstyled footer-link">
              <li><a href="#">About</a></li>
              <li><a href="#">Terms of Use</a></li>
              <li><a href="#">Disclaimers</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
          <div class="col-md-3">
          
          </div>
        </div>
        <div class="row">
          <div class="col-12 text-md-center text-left">
             <p>
              <!-- Link back to Colorlib can't be removed. Template is licensed under CC BY 3.0. -->
              Copyright &copy;
              <script>document.write(new Date().getFullYear());</script> All rights reserved | This template is made
              with <i class="fa fa-heart" aria-hidden="true"></i> by <a href="https://colorlib.com" target="_blank"
                class="text-primary">Colorlib</a>
              <!-- Link back to Colorlib can't be removed. Template is licensed under CC BY 3.0. -->
            </p>
          </div>
        </div>
      </div>
    </footer>
    <!-- END footer -->

    <!-- loader -->
    <div id="loader" class="show fullscreen"><svg class="circular" width="48px" height="48px"><circle class="path-bg" cx="24" cy="24" r="22" fill="none" stroke-width="4" stroke="#eeeeee"/><circle class="path" cx="24" cy="24" r="22" fill="none" stroke-width="4" stroke-miterlimit="10" stroke="#f4b214"/></svg></div>

    <script src="js/jquery-3.2.1.min.js"></script>
    <script src="js/popper.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/owl.carousel.min.js"></script>
    <script src="js/jquery.waypoints.min.js"></script>
    <script src="js/jquery.fancybox.min.js"></script>
    <script src="js/main.js"></script>

    <script src="js/main.js"></script>
    <script src="https://unpkg.com/vue"></script>
    <script src="https://unpkg.com/vue-material@beta"></script>
    <script>
    Vue.use(VueMaterial.default)
    
    Vue.component('doctest-activity', {
        props: ['layoutThings', 'questionName'],
        data: function () {
            return {
            answer:"",
            layoutItems: this.layoutThings
        }
        },
        methods: {
            postContents: function () {
            // comment: leaving the gatewayUrl empty - API will post back to itself
            const gatewayUrl = '';
            fetch(gatewayUrl, {
        method: "POST",
        headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({name: {0:this.questionName}, editable:{0:this.layoutItems[0].vModel}})          <!-- Edited Here -->
        }).then(response => {
            return response.json()
        }).then(data => {
            this.answer = JSON.parse(JSON.stringify(data))
            return this.$emit('questionhandler',{data, questionName:this.questionName})
            })
         }
        },
        template: '<div class="md-layout  md-gutter"><div id="cardGroupCreator" class="md-layout-item md-size-80">\
            <md-card v-for="layoutItem in layoutItems" :key=layoutItem.header>\
                <md-card-header>\
                    <md-card-header-text>\
                        <div class="md-title">{{layoutItem.header}}</div>\
                        <div class="md-subhead">{{layoutItem.subHeader}}</div>\
                    </md-card-header-text>\
                </md-card-header>\
                <md-card-content>\
                    <md-field>\
                        <md-textarea v-model="layoutItem.vModel"></md-textarea>\
                     </md-field>\
                </md-card-content>\
            </md-card>\
                    <button v-on:click="postContents">Submit</button>\
            </div>\
            <div id="cardGroupPreview" class="md-layout-item md-size-80">\
                <md-card>\
                    <md-card-header>\
                    <md-card-header-text>\
                        <div class="md-title">Output</div>\
                        <div class="md-subhead">Test results</div>\
                    </md-card-header-text>\
                </md-card-header>\
                <md-card-content>\
                    <md-field>\
                        <md-tabs><md-tab id="tab-htmlResults" md-label="HTML results"><div v-html="answer.htmlFeedback"></div></md-tab><md-tab id="tab-jsonResults" md-label="JSON results"><md-textarea v-model="answer.jsonFeedback" readonly></md-textarea></md-tab>\
                            <md-tab id="tab-textResults" md-label="Text results">\
                                <md-textarea v-model="answer.textFeedback" readonly></md-textarea>\
                            </md-tab></md-tabs>\
                     </md-field>\
                </md-card-content>\
            </md-card>\
            </div></div>\
            '
    })
    
    new Vue({
        el: '#vueOnly',
        data: function () {
            return {
            questions:[
                {name:"question 1", layoutItems: [
                {header:"Check Loaded Data", subHeader:'Your code goes below', vModel:""}
                ], status:" ??"},
                {name:"question 2", layoutItems: [
                {header:"Check First Five Rows of Data", subHeader:'Your code goes below', vModel:""}
                ], status:" ??"},
                {name:"question 3", layoutItems: [
                {header:"Editable Code Block", subHeader:'Your code goes below', vModel:"def floorDivide(a,b):\\n return b"}
                ], status:" ??"},
                {name:"question 4", layoutItems: [
                {header:"Editable Code Block", subHeader:'Your code goes below', vModel:"def logicAndOperation(a,b):\\n return b"}
                ], status:" ??"},
                {name:"question 5", layoutItems: [
                {header:"Editable Code Block", subHeader:'Your code goes below', vModel:"def doubleEqualOperation(a,b):\\n return b"}
                ], status:" ??"}
            ]
        }
        },
         methods: {
            toggleQuestionStatus (response) {
                const {data, questionName} = response
                if (data.htmlFeedback) {
                    const searchText = data.htmlFeedback
                    searchText.search(/b2d8b2/) !== -1 ?
                        searchText.search(/#ff9999/) == -1 ?
                        this.questions.find(item => item.name === questionName).status = " ??"
                        :
                        this.questions.find(item => item.name === questionName).status = " ??"
                    :
                    this.questions.find(item => item.name === questionName).status = " ??"
                }
            }
        }
      })
    </script>
    
  </body>
</html>
    """
    
    if method == 'GET':
        return {
            "statusCode": 200,
            "headers": {
            'Content-Type': 'text/html',
            },
            "body": indexPage
        }
        
    if method == 'POST':
        bodyContent = event.get('body',{}) 
        parsedBodyContent = json.loads(bodyContent)
        print(bodyContent)
        #testCases = parsedBodyContent["shown"]["0"]                             #! Edited Here

        question = parsedBodyContent["name"]["0"]                                #! Edited Here
        
        # allTestCases = {"question 1": ">>> df.shape\n(500,8)",                                              #! Edited Here
        #                 "question 2": ">>> df.head()\n" + dataFrames_test_ans[question]
        #                 }
        
        
        allTestCases = {"question 1": ">>> df.shape\n(500,8)",                                              #! Edited Here NOTE THAT FOR TUPLES, CANNOT LEAVE SPACE AFTER COMMA!
                        "question 2": ">>> df.head()\n" + df.head().to_string().replace("\n", "--")
                        }
        
        
        
        questionType = {"question 1": "non-dataframe",
                        "question 2": "dataframe"}
                        
        testCases = allTestCases[question] 
        #testCases = ">>> df.shape\n(500,8)"                                     #! Edited Here
        
        qtype = questionType[question]                                           #! Edited Here 
        
        solution = parsedBodyContent["editable"]["0"] 
        #hidden = "\n" + parsedBodyContent["hidden"]["0"]                        #! Edited Here
        
        timeout = False
        # handler function that tell the signal module to execute
        # our own function when SIGALRM signal received.
        def timeout_handler(num, stack):
            print("Received SIGALRM")
            raise Exception("processTooLong")

        # register this with the SIGALRM signal    
        signal.signal(signal.SIGALRM, timeout_handler)
        
        # signal.alarm(10) tells the OS to send a SIGALRM after 10 seconds from this point onwards.
        signal.alarm(10)

        # After setting the alarm clock we invoke the long running function.
        try:
            jsonResponse = run_local({"solution": solution, "tests": testCases, "type": qtype})        #! Edited Here
            #jsonResponse = run_local({"solution": solution, "tests": testCases+hidden})        #! Edited Here
        except Exception as ex:
            if "processTooLong" in ex:
                timeout = True
                print("processTooLong triggered")
        # set the alarm to 0 seconds after all is done
        finally:
            signal.alarm(0)

        jsonResponseData = json.loads(jsonResponse)
        
        solvedStatusText = expectedText = receivedText = callText = textResults = tableContentsPublic = tableContentsPrivate = ""
        overallResults = """<span class="md-subheading">All tests passed: {0}</span><br/>""".format(str(jsonResponseData.get("solved")))
        numTestCases = len(re.findall('>>>', testCases))
        resultContent = jsonResponseData.get('results') 
        textBackgroundColor = "#ffffff"
        
        if resultContent:
            for i in range(len(resultContent)):
                expectedText = resultContent[i]["expected"]
                receivedText = resultContent[i]["received"]
                correctText = resultContent[i]["correct"]
                callText = resultContent[i]["call"]
                questionType = resultContent[i]["questionType"]                  #! Edited Here
                
                if questionType == "non-dataframe":
                    if type(expectedText) == list:
                        expectedText = tuple(expectedText)
                        
                        
                if numTestCases > i:
                    if str(expectedText) == str(receivedText):
                        textResults = textResults + "\nHurray! You have passed the test case. You called {0} and received {1} against the expected value of {2}.\n".format(callText, receivedText, expectedText)
                        textBackgroundColor = "#b2d8b2"
                    else:
                        textResults = textResults + "\nThe test case eludes your code so far but try again! You called {0} and received {1} against the expected value of {2}.\n".format(callText, receivedText, expectedText)
                        textBackgroundColor = "#ff9999"
                    tableContentsPublic = tableContentsPublic + """
                    <tr bgcolor={4}>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                    </tr>
                    """.format(callText,expectedText,receivedText,correctText,textBackgroundColor)
                else:
                    if str(expectedText) == str(receivedText):
                        textResults = textResults + "\nHurray! You have passed the hidden test case. You called {0} and received {1} against the expected value of {2}.\n".format(callText, receivedText, expectedText)
                        textBackgroundColor = "#b2d8b2"
                    else:
                        textResults = textResults + "\nThe hidden test case eludes your code so far but try again! The hidden test case called {0} and received {1} against the expected value of {2}.\n".format(callText, receivedText, expectedText)
                        textBackgroundColor = "#ff9999"
                    tableContentsPrivate = tableContentsPrivate + """
                    <tr bgcolor={4}>
                        <td>{0}</td>
                        <td>{1}</td>
                        <td>{2}</td>
                        <td>{3}</td>
                    </tr>
                    """.format(callText,expectedText,receivedText,correctText,textBackgroundColor)                        
        solvedStatusText = str(jsonResponseData.get("solved")) or "error"
        textResults = """All tests passed: {0}\n""".format(solvedStatusText) + textResults
        if not resultContent:
            textResults = "Your test is passing but something is incorrect..."
            
        if timeout or jsonResponseData.get("errors"):
            textResults = "An error - probably related to code syntax - has occured. Do look through the JSON results to understand the cause."
            tableContentsPublic = """
                <tr>
                    <td></td>
                    <td></td>
                    <td>error</td>
                    <td></td>
                </tr>
                """
            tableContentsPrivate = """
                <tr>
                    <td></td>
                    <td></td>
                    <td>error</td>
                    <td></td>
                </tr>
                """                
        htmlResults="""
            <html>
                <head>
                    <meta charset="utf-8">
                    <meta content="width=device-width,initial-scale=1,minimal-ui" name="viewport">
                </head>
                <body>
                    <div>
                        {0}
                        <span class="md-subheading tableTitle">Public tests</span>
                        <table>
                             <thead>
                                <tr>
                                    <th>Called</th>
                                    <th>Expected</th>
                                    <th>Received</th>
                                    <th>Correct</th>
                                </tr>
                            </thead>
                            <tbody>
                                {1}
                            </tbody>
                        </table>
                        <br/>
                        <span class="md-subheading tableTitle">Private tests</span>
                        <table>
                             <thead>
                                <tr>
                                    <th>Called</th>
                                    <th>Expected</th>
                                    <th>Received</th>
                                    <th>Correct</th>
                                </tr>
                            </thead>
                            <tbody>
                                {2}
                            </tbody>
                        </table>
                    </div>
                </body>
                <style>
                br {{
                    display:block;
                    content:"";
                    margin:1rem
                }}
                table{{
                    text-align:center
                }}
                .tableTitle{{
                    text-decoration:underline
                }}
                </style>
            </html>
            """.format(overallResults,tableContentsPublic,tableContentsPrivate)
        return {
            "statusCode": 200,
            "headers": {
            "Content-Type": "application/json",
                },
            "body":  json.dumps({
                "isComplete":jsonResponseData.get("solved"),
                "jsonFeedback": jsonResponse,
                "htmlFeedback": htmlResults,
                "textFeedback": textResults
            })
            }
