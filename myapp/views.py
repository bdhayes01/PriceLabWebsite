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
    cohort_number = int(request.GET.get('cohort_number', 1)) # Default to 1 if not provided
    mlb = MultiLabelBinarizer()
    global variants
    global encoded_data
    encoded_data = pd.DataFrame(mlb.fit_transform(variants.values()), index=variants.keys(), columns=mlb.classes_)
    kmeans = KMeans(n_clusters=cohort_number, random_state=42) # Can add in random_state=1 to ensure that you will always get the same result.
    global cohorts
    cohorts = kmeans.fit_predict(encoded_data)
    encoded_data['Cluster'] = cohorts
    temp_cohorts = {}
    for indiv, coh in zip(variants.keys(), cohorts):
        if coh in temp_cohorts:
            temp_cohorts[coh].append(indiv)
        else:
            temp_cohorts[coh] = [indiv]
    cohorts = [temp_cohorts[num] for num in sorted(temp_cohorts.keys())]

    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts})


def make_dendrogram(request):  # Must always have 'request' else a 500 error.
    global cohorts
    global variants
    global encoded_data
    plt.clf()

    if cohorts is None:
        figuresize = (len(variants)/2, len(variants)/4)
        all_items = set(item for sublist in variants.values() for item in sublist)
        binary_matrix = pd.DataFrame(
            [[1 if item in variants[key] else 0 for item in all_items] for key in variants.keys()],
            index=list(variants.keys()),
            columns=list(all_items)
        )
        dist_matrix = pdist(binary_matrix.values, metric='jaccard')

        linked = linkage(dist_matrix, method='ward')
        plt.figure(figsize=figuresize)
        dendrogram(linked)
    else:
        figuresize = (len(encoded_data.columns)/4, len(encoded_data))
        linked = linkage(encoded_data.drop('Cluster', axis=1), method='ward')

        numeric_columns = sorted([int(col) for col in encoded_data.columns if col != 'Cluster' and col.isdigit()])
        numeric_columns = [str(col) for col in numeric_columns]
        encoded_data3 = encoded_data.reindex(numeric_columns, axis=1)
        g = sns.clustermap(encoded_data3, row_linkage=linked, col_cluster=False,
                       cmap='Blues', figsize=figuresize, cbar_pos=None)
        plt.title("Heatmap with Hierarchical clustering dendrogram. Blue represents a variant.")
        cluster_colors = sns.color_palette("husl", len(cohorts))
        ax = g.ax_heatmap
        new_labels = []
        for label in ax.get_yticklabels():
            file_name = label.get_text()
            cluster = encoded_data.loc[file_name, 'Cluster']
            label.set_color(cluster_colors[cluster])
            new_labels.append(f"{file_name} ({cluster + 1})")
        ax.set_yticklabels(new_labels, rotation=0)
        g.fig.subplots_adjust(left=0, right=0.91, top=1.1, bottom=0.1)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')
