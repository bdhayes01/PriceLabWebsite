from myapp.models import Metadata
from collections import defaultdict
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import random
import myapp.views as views

def make_mutation_cohort(variants, cohort_number, individuals):

    variants_copy = {}
    for vari in variants.keys:
        if vari[0] in individuals:
            variants_copy[vari] = variants[vari]
    variants = variants_copy

    mlb = MultiLabelBinarizer()
    encoded_data = pd.DataFrame(mlb.fit_transform(variants.values()), index=variants.keys(), columns=mlb.classes_)
    kmeans = KMeans(n_clusters=cohort_number,
                    random_state=42)  # Can add in random_state=42 to ensure that you will always get the same result.
    global cohorts
    try:
        cohorts = kmeans.fit_predict(encoded_data)
        encoded_data['Cluster'] = cohorts
        temp_cohorts = {}
        for indiv, coh in zip(variants.keys(), cohorts):
            if coh in temp_cohorts:
                temp_cohorts[coh].append(indiv)
            else:
                temp_cohorts[coh] = [indiv]
        cohorts = [temp_cohorts[num] for num in sorted(temp_cohorts.keys())]
    except:
        cohorts = None
    return
