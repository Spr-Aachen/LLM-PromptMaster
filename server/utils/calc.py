import pandas
import numpy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import engine
from pathlib import Path
from typing import Optional, Union

##############################################################################################################################

average_similarity = None

def computeSimilarity(
    answers: list,
    codeInput: list,
    totalTestTimes: Optional[int] = None,
    sqlConnection: Optional[Union[engine.Engine, engine.Connection]] = None
):
    global average_similarity

    # Compute the similarity matrix
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(answers) # Transfer data into TF-IDF vector
    similarity_matrix = cosine_similarity(tfidf_matrix) # Compute cosine similarity of the matrix
    # Compute the average similarity
    num_of_elements = similarity_matrix.shape[0] * similarity_matrix.shape[1] - similarity_matrix.shape[0]
    sum_of_similarity = numpy.sum(similarity_matrix) - numpy.sum(numpy.diagonal(similarity_matrix))
    average_similarity = sum_of_similarity / num_of_elements

    # Save the test result
    TestResult = {
        'CodeInput': [codeInput],
        'Answer': [answers[0]],
        'TestTimes': totalTestTimes,
        'Similarity': [average_similarity]
    }
    TestResultDF = pandas.DataFrame(TestResult)
    jsonPath = './TestResult.json'
    if Path(jsonPath).exists():
        TestResultsDF = pandas.read_json(jsonPath, encoding = 'utf-8')
        TestResultsDF = TestResultsDF[TestResultsDF['CodeInput'] != codeInput]
        TestResultsDF = pandas.concat([TestResultsDF, TestResultDF])
        TestResultsDF.reset_index(inplace = True, drop = True)
    else:
        TestResultsDF = TestResultDF
    TestResultsDF.to_json(jsonPath)

    # Upload the test result to the database
    if sqlConnection is not None:
        TestResultsDF.to_sql(
            name = "Prompt Test Result",
            con = sqlConnection,
            if_exists = 'replace'
        )
        sqlConnection.close()

##############################################################################################################################