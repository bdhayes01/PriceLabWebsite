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
    cohorts = None
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

    categories = [f"{i}" for i in cohorts]
    colors = generate_random_colors(len(cohorts))
    return cohorts, colors, categories


def generate_random_colors(n):
    """Generate a dynamic list of n random colors in hexadecimal format."""
    return [f'#{random.randint(0, 0xFFFFFF):06X}' for _ in range(n)]


def make_graph_mutation(chalf, cohorts, colors, categories):
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