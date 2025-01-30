from myapp.models import Sequence
from collections import defaultdict
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io
from sklearn.cluster import KMeans
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import random
import myapp.views as views
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
import seaborn as sns


def make_mutation_cohort(accession, cohort_number, individuals):

    seq = Sequence.objects.get(Accession__contains=accession)
    variants = seq.Variants
    temp_variants = {}
    for indiv in individuals:
        if indiv in variants.keys():
            temp_variants[indiv] = variants[indiv]
    variants = temp_variants
    seq = seq.Sequence

    # variants_copy = {}
    # for vari in variants.keys():
    #     if vari[0] in individuals:
    #         variants_copy[vari] = variants[vari]
    # variants = variants_copy

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
        combined_variants = combine_variants(variants, cohorts)
    except:
        return None

    categories = [f"{i}" for i in cohorts]
    colors = generate_random_colors(len(cohorts))
    return cohorts, colors, categories, seq, combined_variants


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


def make_dendrogram(individuals, curr_accession):
    seq = Sequence.objects.get(Accession__exact=curr_accession)
    variants = seq.Variants
    temp_variants = {}
    for indiv in individuals:
        if indiv in variants.keys():
            temp_variants[indiv] = variants[indiv]
    variants = temp_variants

    plt.clf()
    minfigsize = (8.0, 6.0)

    figuresize = (len(variants) / 2, len(variants) / 4)
    selected_figuresize = (
        max(minfigsize[0], figuresize[0]),  # Select the larger width
        max(minfigsize[1], figuresize[1])  # Select the larger height
    )
    all_items = set(item for sublist in variants.values() for item in sublist)
    binary_matrix = pd.DataFrame(
        [[1 if item in variants[key] else 0 for item in all_items] for key in variants.keys()],
        index=list(variants.keys()),
        columns=list(all_items)
    )
    dist_matrix = pdist(binary_matrix.values, metric='jaccard')

    linked = linkage(dist_matrix, method='ward')
    plt.figure(figsize=selected_figuresize)
    dendrogram(linked)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')

def combine_variants(variants, cohorts):
    combined_variants = {}
    for idx, cohort in enumerate(cohorts):
        combined_variants[idx] = {}
        for indiv in cohort:
            for variant in variants[indiv].keys():  # This is the index of the mutation
                if variant in combined_variants[idx]:
                    combined_variants[idx][variant] = combined_variants[idx][variant] + 1/len(cohort)
                else:
                    combined_variants[idx][variant] = 1/len(cohort)
        for key in combined_variants[idx].keys():
            combined_variants[idx][key] = round(combined_variants[idx][key], 2) * 100

    return combined_variants
