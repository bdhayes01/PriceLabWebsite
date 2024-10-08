import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Sequence
import os, re, json
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
import matplotlib.pyplot as plt
import io

global variants

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
        sequence = Sequence.objects.first()
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
    seqs = Sequence.objects.all()
    for seq in seqs:
        variants = dict(seq.Variants)
        indivs = list(variants.keys())
        indivs2 = list(variants.keys())
        cohorts = []
        for indiv in indivs:
            for i in cohorts:
                for j in i:
                    if j == indiv:
                        continue
            temp = []
            for ind in indivs2:
                if variants[ind] == variants[indiv]:
                    temp.append(ind)
            for ind in temp:
                indivs2.pop(indivs2.index(ind))
            if len(temp) > 0:
                cohorts.append(temp)

        seq.Cohorts = cohorts
        seq.save()
    result_message = "Cohorts made successfully!"
    return JsonResponse({'message': result_message})


def make_dendrogram(request):
    global variants
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

    # Save the image to a BytesIO object (in-memory file)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')
