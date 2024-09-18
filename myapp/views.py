import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Sequence
import os, re, json


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

                # Assuming the Excel file has columns: 'individual', 'protein', 'aa_sequence', 'variants'
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
                        defaults={'Variants': variants})

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
        sequences = Sequence.objects.filter(Accession__exact=query)
    else:
        sequences = Sequence.objects.none()

    sequence_json = json.dumps(
        [{'Accession': seq.Accession, 'Variants': seq.Variants}
         for seq in sequences])

    return render(request, 'home.html', {'sequence_json': sequence_json, 'query': query})
