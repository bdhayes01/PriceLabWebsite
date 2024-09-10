import pandas as pd
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Sequence
import os
import json


def upload_csv(request):
    if request.method == 'POST':
        # Check if the user has uploaded a file
        if 'file' in request.FILES:
            csv_file = request.FILES['file']

            # Parse the uploaded Excel file using pandas
            df = pd.read_csv(csv_file)

            file_name = os.path.splitext(csv_file.name)[0]
            individual = file_name.split('-')[1]

            # Assuming the Excel file has columns: 'individual', 'protein', 'aa_sequence', 'variants'
            for _, row in df.iterrows():

                variants_str = row.get('Variants', '{}')
                if isinstance(variants_str, str):
                    try:
                        variants_dict = eval(variants_str)
                    except Exception as e:
                        print(f"Error parsing string: {e}")
                        variants_dict = {}

                    # Convert dictionary keys to strings
                    variants_dict_str_keys = {str(key): value for key, value in variants_dict.items()}

                    # Convert back to JSON string with stringified keys
                    json_variants_str = json.dumps(variants_dict_str_keys)
                else:
                    json_variants_str = {}

                Sequence.objects.create(
                    Individual=individual,
                    Accession=row['Accession'],
                    Sequence=row['Sequence'],
                    Variants=json_variants_str  # Defaults to empty dict if variants column doesn't exist
                )

            return HttpResponse("File uploaded and parsed successfully.")
        else:
            return HttpResponse("No file uploaded.")

    return render(request, 'upload_csv.html')


def home(request):
    query = request.GET.get('q', '')
    if query:
        sequences = Sequence.objects.filter(Accession__exact=query)
    else:
        sequences = Sequence.objects.none()

    sequence_json = json.dumps(
        [{'Individual': seq.Individual, 'Accession': seq.Accession, 'Sequence': seq.Sequence, 'Variants': seq.Variants}
         for seq in sequences])

    return render(request, 'home.html', {'sequence_json': sequence_json, 'query': query})