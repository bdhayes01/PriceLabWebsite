from myapp.models import Metadata
from collections import defaultdict
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io
from sklearn.cluster import KMeans
import pandas as pd
import random
import myapp.views as views

def make_bmi_cohort(cohort_number):
    metadata = Metadata.objects.all()
    bmi = {record.Individual: record.BMI for record in metadata}
    bmi = pd.DataFrame({'BMI': list(bmi.values())}, index=bmi.keys())

    kmeans = KMeans(n_clusters=cohort_number, random_state=42)
    cohorts = kmeans.fit_predict(bmi)
    bmi['Cluster'] = cohorts
    temp_cohorts = {}
    for indiv, coh in zip(bmi.index, cohorts):
        if coh in temp_cohorts:
            temp_cohorts[coh].append(indiv)
        else:
            temp_cohorts[coh] = [indiv]
    cohorts = [temp_cohorts[num] for num in sorted(temp_cohorts.keys())]
    colors = generate_random_colors(len(cohorts))
    categories = generate_categories(cohorts, bmi['BMI'])
    categories = [f"{val[0]} - {val[1]}" for val in categories]
    return cohorts, colors, categories

def generate_categories(cohorts, ages):
    categories = []
    i = 0
    for cohort in cohorts:
        minmax = [200.0, -1.0]
        for indiv in cohort:
            age = ages.get(indiv)
            if age < minmax[0]:
                minmax[0] = age
            if age > minmax[1]:
                minmax[1] = age
            i += 1
        categories.append(minmax)
    return categories


def make_graph_bmi(chalf, cohorts, colors, categories):
    x_values = defaultdict(list)
    y_values = defaultdict(list)
    errors = defaultdict(list)

    for indiv, value in chalf.items():
        for k, v in value.items():
            cohort_index = next((i for i, cohort in enumerate(cohorts) if indiv in cohort), None)
            color = colors[cohort_index] if cohort_index is not None else "#FFFFFF"
            x_values[color].append(round(float(k)))
            y_values[color].append(v[0])
            errors[color].append(v[1])
    plt.figure(figsize=(10, 6))
    for color in colors:
        if color not in x_values:
            continue
        sorted_data = sorted(zip(x_values[color], y_values[color], errors[color]),
                             key=lambda x: x[0])  # Sort by x_values
        sorted_x, sorted_y, sorted_errors = zip(*views.aggregate_data(sorted_data))  # Use separate variables to unpack sorted data
        plt.errorbar(sorted_x, sorted_y, yerr=sorted_errors, fmt='o', capsize=5, label=f'Data ({color})',
                     color=color)
    plt.title("C-Half values for selected protein")
    plt.xlabel("Residues")
    plt.ylabel("C-Half")
    plt.grid(True)
    plt.legend(categories)
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
