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
                    if isinstance(variants_str, str):
                        variants = re.findall(r'\d+', variants_str)
                        variants = [int(num) for num in variants]
                        nucleotide_variants = re.findall(r'[a-zA-Z]+', variants_str)
                        #TODO: Ask Chad what to do if there is more than one nucleotide here.
                        nucleotide_variants = [str(ch) for ch in nucleotide_variants]
                    else:
                        variants = []
                        nucleotide_variants = []

                    Sequence.objects.create(
                        Individual=individual,
                        Accession=row['Accession'],
                        Sequence=row['Sequence'],
                        Variants=variants,
                        Nucleotide_Variants=nucleotide_variants
                    )

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
        [{'Individual': seq.Individual, 'Accession': seq.Accession,
          'Sequence': seq.Sequence, 'Variants': seq.Variants,
          'Nucleotide_Variants': seq.Nucleotide_Variants}
         for seq in sequences])

    return render(request, 'home.html', {'sequence_json': sequence_json, 'query': query})