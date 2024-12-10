from myapp.models import Metadata
from collections import defaultdict
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io
from sklearn.cluster import KMeans
import pandas as pd
import random


def make_age_cohort(cohort_number):
    metadata = Metadata.objects.all()
    ages = {record.Individual: record.Age for record in metadata}
    ages = pd.DataFrame({'Age': list(ages.values())}, index=ages.keys())

    kmeans = KMeans(n_clusters=cohort_number, random_state=42)
    cohorts = kmeans.fit_predict(ages)
    ages['Cluster'] = cohorts
    temp_cohorts = {}
    for indiv, coh in zip(ages.index, cohorts):
        if coh in temp_cohorts:
            temp_cohorts[coh].append(indiv)
        else:
            temp_cohorts[coh] = [indiv]
    cohorts = [temp_cohorts[num] for num in sorted(temp_cohorts.keys())]
    return cohorts


def make_graph_age(chalf, cohorts):
    x_values = defaultdict(list)
    y_values = defaultdict(list)
    errors = defaultdict(list)
    colors = generate_random_colors(len(cohorts))

    for indiv, value in chalf.items():
        for k, v in value.items():
            color = colors[0] if indiv in cohorts[0] else colors[1]
            x_values[color].append(round(float(k)))
            y_values[color].append(v[0])
            errors[color].append(v[1])
    plt.figure(figsize=(10, 6))
    for color in colors:
        if color not in x_values:
            continue
        sorted_data = sorted(zip(x_values[color], y_values[color], errors[color]),
                             key=lambda x: x[0])  # Sort by x_values
        sorted_x, sorted_y, sorted_errors = zip(*sorted_data)  # Use separate variables to unpack sorted data
        plt.errorbar(sorted_x, sorted_y, yerr=sorted_errors, fmt='o', capsize=5, label=f'Data ({color})',
                     color=color)
    plt.title("C-Half values for selected protein")
    plt.xlabel("Residues")
    plt.ylabel("C-Half")
    plt.grid(True)
    plt.legend([f"Cohort {i + 1}" for i in range(len(cohorts))])
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')


def generate_random_colors(n):
    """Generate a dynamic list of n random colors in hexadecimal format."""
    return [f'#{random.randint(0, 0xFFFFFF):06X}' for _ in range(n)]
