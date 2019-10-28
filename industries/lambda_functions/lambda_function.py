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
import csv

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

#from pandas.compat import StringIO

def lambda_handler(event, context):
    # TODO implement
    s3 = boto3.client('s3')
    # dynamodb = boto3.client('dynamodb', region_name = "us-east-1")
    recList = []
    obj = s3.get_object(Bucket = "mylambdajosh", Key = "short_data.csv")
    
    recList = obj["Body"].read().decode("utf-8").split("\n")
    firstrecord = True
    csv_reader = csv.reader(recList, delimiter = ",", quotechar = '"')
    counter = 0
    
    index_lst = []
    type_lst = []
    amount_lst = []
    oldbalanceOrig_lst = []
    newbalanceOrig_lst = []
    oldbalanceDest_lst = []
    newbalanceDest_lst = []
    isFraud_lst = []
    for row in csv_reader:
        if counter == 501:
            break
        counter += 1
        if (firstrecord):
            firstrecord = False
            continue
        if len(row) != 0:
            index_lst.append(row[0])
            type_lst.append(row[1])
            amount_lst.append(row[2])
            oldbalanceOrig_lst.append(row[3])
            newbalanceOrig_lst.append(row[4])
            oldbalanceDest_lst.append(row[5])
            newbalanceDest_lst.append(row[6])
            isFraud_lst.append(row[7])
    
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
        
    s3 = boto3.client("s3")
    file_obj = s3.get_object(Bucket = "mylambdajosh", Key = "project-stock.html")
    indexPage = file_obj["Body"].read().decode('utf-8')
    
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
