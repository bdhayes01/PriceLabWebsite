import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Sequence
import os, re, json
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import io
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import KMeans
import seaborn as sns

global variants, cohorts, encoded_data
variants = {}
cohorts = None
encoded_data = None


def upload_csv(request):
    message = None  # Initialize message
    if request.method == 'POST':
        # Check if the user has uploaded a file
        if 'file' in request.FILES:
            files = request.FILES.getlist('file')
            for file in files:
                # Parse the uploaded Excel file using pandas
                df = pd.read_csv(file)

                file_name = os.path.splitext(file.name)[0]
                individual = file_name.split('-')[1]

                for _, row in df.iterrows():

                    variants_str = row.get('Variants', '{}')
                    variants = {individual: {}}
                    if isinstance(variants_str, str):
                        varis = variants_str.split('],')
                        for i in range(len(varis)):
                            integer_variants = re.findall(r'\d+', varis[i])[0]
                            peptide_variants = re.findall(r'[a-zA-Z]+', varis[i])
                            peptide_variants = [str(ch) for ch in peptide_variants]
                            variants[individual][integer_variants] = peptide_variants
                    sequence, created = Sequence.objects.get_or_create(
                        Accession=row['Accession'],
                        defaults={'Variants': variants},
                        Sequence=row['Sequence'])

                    if not created:
                        sequence.Variants.update(variants)
                        sequence.save()

            message = "File(s) uploaded and parsed successfully."  # Set success message
        else:
            message = "No file uploaded."

    return render(request, 'upload_csv.html', {'message': message})


def home(request):
    query = request.GET.get('q', '')
    if query:
        sequence = Sequence.objects.filter(Accession__exact=query).first()
    else:
        # sequence = Sequence.objects.first()
        sequence = Sequence.objects.filter(Accession__exact="Q8WZ42|TITIN_HUMAN").first()
    if sequence:
        global variants
        variants = sequence.Variants
        sequence_json = json.dumps({
            'Accession': sequence.Accession,
            'Variants': sequence.Variants,
            'Cohorts': sequence.Cohorts,
            'Sequence': sequence.Sequence
        })
    else:
        sequence_json = json.dumps({})
    return render(request, 'home.html', {'sequence_json': sequence_json, 'query': query})


def make_cohorts(request):
    cohort_number = int(request.GET.get('cohort_number', 1))  # Default to 1 if not provided
    mlb = MultiLabelBinarizer()
    global variants
    global encoded_data
    encoded_data = pd.DataFrame(mlb.fit_transform(variants.values()), index=variants.keys(), columns=mlb.classes_)
    kmeans = KMeans(
        n_clusters=cohort_number)  # Can add in random_state=1 to ensure that you will always get the same result.
    global cohorts
    cohorts = kmeans.fit_predict(encoded_data)
    temp_cohorts = {}
    for indiv, coh in zip(variants.keys(), cohorts):
        if coh in temp_cohorts:
            temp_cohorts[coh].append(indiv)
        else:
            temp_cohorts[coh] = [indiv]
    cohorts = [temp_cohorts[num] for num in sorted(temp_cohorts.keys())]

    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts})


def clear_cohorts(request):
    global cohorts
    cohorts = None
    return JsonResponse({'message': 'Cohorts cleared successfully'})


def make_dendrogram(request):  # Must always have 'request' else a 500 error.
    global cohorts
    global variants
    global encoded_data
    plt.clf()

    if cohorts is None:
        all_items = set(item for sublist in variants.values() for item in sublist)
        binary_matrix = pd.DataFrame(
            [[1 if item in variants[key] else 0 for item in all_items] for key in variants.keys()],
            index=list(variants.keys()),
            columns=list(all_items)
        )
        dist_matrix = pdist(binary_matrix.values, metric='jaccard')

        linked = linkage(dist_matrix, method='ward')
        plt.figure(figsize=(10, 7))
        dendrogram(linked)
    else:
        linked = linkage(encoded_data, method='ward')
        sns.clustermap(encoded_data, row_linkage=linked, col_cluster=False, cmap='coolwarm', figsize=(10, 7))
        plt.title("Heatmap with Hierarchical clustering dendrogram")

    # Save the image to a BytesIO object (in-memory file)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')
