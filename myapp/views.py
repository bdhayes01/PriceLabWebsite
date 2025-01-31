import math
from collections import defaultdict
import statistics
import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Sequence, Metadata, CHalf
import os, re, json

import matplotlib.pyplot as plt
import io

from .Datatypes import Sex, Disease, Drug, Age, BMI, Mutation

# global variants, cohorts, encoded_data, chalf, dt, cohort_colors, categories, individuals
global cohorts, chalf, dt, cohort_colors, categories, individuals, curr_accession
cohorts = None


def upload_file(request):
    message = None  # Initialize message
    if 'file' in request.FILES:
        files = request.FILES.getlist('file')
        for file in files:
            message = "File(s) uploaded and parsed successfully."  # Set success message

            file_name = os.path.splitext(file.name)[0]
            # Separates the files based on which ones they are. Each function then parses.
            # May need to adjust based on future file name changes/ format changes.

            if "visual" in file_name:
                upload_visual_outputs(file)
            elif "Sites" in file_name:
                upload_c_half(file)
            elif "Masterlist" in file_name:
                upload_metadata(file)
            else:
                message = "No valid file uploaded."
    else:
        message = "No file uploaded."
    return message


def upload_visual_outputs(file):
    # Parse the uploaded Excel file using pandas
    df = pd.read_csv(file)
    individual = os.path.splitext(file.name)[0].split('-')[1]
    for _, row in df.iterrows():

        variants_str = row.get('Variants', '{}')
        variants = {individual: {}}
        if isinstance(variants_str, str):
            varis = variants_str.split('],')
            for i in range(len(varis)):
                split = varis[i].split(',')
                integer_variants = int(re.findall(r'\d+', split[0])[0])
                # peptide_variants = re.findall(r'[a-zA-Z]+', split[0])[0]  # This line is for if you need the actual
                # mutation peptide
                effect = float(split[4])
                variants[individual][integer_variants] = effect
        sequence, created = Sequence.objects.get_or_create(
            Accession=row['Accession'],
            defaults={'Variants': variants, 'Sequence': row['Sequence']}
        )

        if not created:
            sequence.Variants.update(variants)
            sequence.Sequence = row.get('Sequence', '')
            sequence.save()
    return


def upload_c_half(file):
    df = pd.read_csv(file)
    individual = os.path.splitext(file.name)[0].split()[0]
    curr_accession = df.get('Accession')[0]
    c_half_vals = {individual: {}}
    for _, row in df.iterrows():
        accession = row.get('Accession')
        if accession != curr_accession:
            chalf, created = CHalf.objects.get_or_create(
                Accession=curr_accession,
                defaults={'CHalf': c_half_vals}
            )
            if not created:
                chalf.CHalf.update(c_half_vals)
                chalf.save()
            curr_accession = accession
            c_half_vals = {individual: {}}
        chalf = row.get('trim_CHalf')
        error = row.get('trim_CHalf_ConfidenceInterval')
        position = row.get('Residue Number')
        c_half_vals[individual][position] = (chalf, error)

    return


def upload_metadata(file):
    df = pd.read_csv(file)
    for _, row in df.iterrows():
        individual = row['Condition']
        disease = (True if row['Disease'] == 1 else False)
        age = int(row['Age'])
        sex = (True if row['Sex'] == 1 else False)  # 1 represents male
        bmi = float(row['BMI'])
        drug = (True if row['Drug'] == 1 else False)
        meta, create = Metadata.objects.get_or_create(Individual=individual, Disease=disease,
                                                      Age=age, Sex=sex, BMI=bmi, Drug=drug)
    return


def home(request):
    message = None
    if request.method == 'POST':
        message = upload_file(request)
    query = request.GET.get('q', '')
    if query:
        global curr_accession
        c = CHalf.objects.filter(Accession__contains=query).first()
        curr_accession = query
    else:
        c = CHalf.objects.filter(Accession__contains="P02768|ALBU_HUMAN").first()
        curr_accession = "P02768|ALBU_HUMAN"
    if c:
        global chalf, individuals
        individuals = Metadata.objects.values_list('Individual', flat=True)
        chalf = c.CHalf
        chalf_json = json.dumps({
            'Accession': c.Accession,
            'CHalf': c.CHalf
        })
    else:
        chalf_json = json.dumps({})
    if message:
        return render(request, 'home.html', {'chalf_json': chalf_json, 'query': query, 'message': message})
    return render(request, 'home.html', {'chalf_json': chalf_json, 'query': query})


def make_mutation_cohorts(request):
    global curr_accession, cohorts, dt, cohort_colors, categories, individuals
    dt = "Mutation"
    cohort_number = int(request.GET.get('cohort_number', 1))  # Default to 1 if not provided
    cohorts, cohort_colors, categories, seq, variants = Mutation.make_mutation_cohort(curr_accession, cohort_number, individuals)

    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts,
                         'cohort_colors': cohort_colors, 'categories': categories,
                         'sequence': seq, 'variants': variants})


def make_mutation_dendrogram(request):  # Must always have 'request' else a 500 error.

    global individuals, curr_accession
    return Mutation.make_dendrogram(individuals, curr_accession)


def make_c_half_graph(request):
    plt.clf()
    global dt, chalf, cohorts
    if cohorts is None:
        return make_basic_graph()
    else:
        if dt == "sex":
            return Sex.make_graph_sex(chalf, cohorts, cohort_colors, categories)
        elif dt == "disease":
            return Disease.make_graph_disease(chalf, cohorts, cohort_colors, categories)
        elif dt == "drug":
            return Drug.make_graph_drug(chalf, cohorts, cohort_colors, categories)
        elif dt == "age":
            return Age.make_graph_age(chalf, cohorts, cohort_colors, categories)
        elif dt == "bmi":
            return BMI.make_graph_bmi(chalf, cohorts, cohort_colors, categories)
        elif dt == "Mutation":
            return Mutation.make_graph_mutation(chalf, cohorts, cohort_colors, categories)


def make_basic_graph():
    x_values = []
    y_values = []
    errors = []
    global chalf, individuals
    for key, value in chalf.items():
        if key not in individuals:
            continue
        for k, v in value.items():
            x_values.append(round(float(k)))
            y_values.append(v[0])
            errors.append(v[1])

    sorted_data = sorted(zip(x_values, y_values, errors), key=lambda x: x[0])  # Sort by x_values
    x_values, y_values, errors = zip(*aggregate_data(sorted_data))

    plt.figure(figsize=(10, 6))
    plt.errorbar(x_values, y_values, yerr=errors, fmt='o', capsize=5, label='Data with error bars')
    plt.title("C-Half values for selected protein")
    plt.xlabel("Residues")
    plt.ylabel("C-Half")
    plt.grid(True)
    # plt.legend()
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')


def aggregate_data(data):
    grouped_data = defaultdict(list)
    for identifier, value, error in data:
        grouped_data[identifier].append((value, error))

    aggregated_data = []
    for identifier, entries in grouped_data.items():
        values = [x[0] for x in entries]
        errors = [x[1] for x in entries]
        y = statistics.median(values)
        err = (0.0 if len(errors) < 2 else statistics.stdev(errors))

        aggregated_data.append((identifier, y, err))
    aggregated_data.sort(key=lambda x: x[0])
    return aggregated_data


def make_sex_cohorts(request):
    global cohorts, dt, cohort_colors, categories, individuals
    dt = "sex"
    categories = ["Male", "Female"]
    cohorts, cohort_colors = Sex.make_sex_cohort(individuals)
    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts,
                         'cohort_colors': cohort_colors, 'categories': categories})


def make_disease_cohorts(request):
    global cohorts, dt, cohort_colors, categories, individuals
    dt = "disease"
    categories = ["With disease", "Without disease"]
    cohorts, cohort_colors = Disease.make_disease_cohort(individuals)
    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts,
                         'cohort_colors': cohort_colors, 'categories': categories})


def make_drug_cohorts(request):
    global cohorts, dt, cohort_colors, categories, individuals
    dt = "drug"
    categories = ["Taking drug", "Not taking drug"]
    cohorts, cohort_colors = Drug.make_drug_cohort(individuals)
    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts,
                         'cohort_colors': cohort_colors, 'categories': categories})


def make_age_cohorts(request):
    global cohorts, dt, cohort_colors, categories, individuals
    cohort_number = int(request.GET.get('cohort_number', 1))
    dt = "age"
    cohorts, cohort_colors, categories = Age.make_age_cohort(cohort_number, individuals)
    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts,
                         'cohort_colors': cohort_colors, 'categories': categories})


def make_bmi_cohorts(request):
    global cohorts, dt, cohort_colors, categories, individuals
    cohort_number = int(request.GET.get('cohort_number', 1))
    dt = "bmi"
    cohorts, cohort_colors, categories = BMI.make_bmi_cohort(cohort_number, individuals)
    return JsonResponse({'message': 'Cohorts created successfully', 'cohorts': cohorts,
                         'cohort_colors': cohort_colors, 'categories': categories})


def reset_filters(request):
    global individuals
    individuals = Metadata.objects.values_list('Individual', flat=True)
    return JsonResponse({'message': 'Successfully reset filters'})


def filter_age(request):
    min_age = request.GET.get('min_age')
    max_age = request.GET.get('max_age')

    # Convert to integers if necessary
    min_age = int(min_age) if min_age else None
    max_age = int(max_age) if max_age else None

    valid_meta = Metadata.objects.filter(Age__lte=max_age, Age__gte=min_age)
    indivs = list(valid_meta.values_list('Individual', flat=True))
    filter_individuals(indivs)
    return JsonResponse({'message': 'Successfully filtered by age'})

def filter_bmi(request):
    min_bmi = request.GET.get('min_bmi')
    max_bmi = request.GET.get('max_bmi')

    # Convert to integers if necessary
    min_bmi = int(min_bmi) if min_bmi else None
    max_bmi = int(max_bmi) if max_bmi else None

    valid_meta = Metadata.objects.filter(BMI__lte=max_bmi, BMI__gte=min_bmi)
    indivs = list(valid_meta.values_list('Individual', flat=True))
    filter_individuals(indivs)
    return JsonResponse({'message': 'Successfully filtered by age'})

def filter_disease(request):
    disease_status = request.GET.get('disease_status')  # '1' for With Disease, '0' for Without Disease
    if disease_status not in ['0', '1']:
        return JsonResponse({"error": "Invalid disease status"}, status=400)

    # Filter the Metadata model based on disease status
    valid_meta = Metadata.objects.filter(Disease=disease_status)
    indivs = list(valid_meta.values_list('Individual', flat=True))
    filter_individuals(indivs)
    return JsonResponse({'message': 'Successfully filtered by disease'})

def filter_drugs(request):
    drug_status = request.GET.get('drug_status')  # '1' for With Disease, '0' for Without Disease
    if drug_status not in ['0', '1']:
        return JsonResponse({"error": "Invalid drug status"}, status=400)

    # Filter the Metadata model based on disease status
    valid_meta = Metadata.objects.filter(Drug=drug_status)
    indivs = list(valid_meta.values_list('Individual', flat=True))
    filter_individuals(indivs)
    return JsonResponse({'message': 'Successfully filtered by drug'})

def filter_sex(request):
    sex_status = request.GET.get('sex')  # '1' for With Disease, '0' for Without Disease
    if sex_status not in ['0', '1']:
        return JsonResponse({"error": "Invalid sex status"}, status=400)

    # Filter the Metadata model based on disease status
    valid_meta = Metadata.objects.filter(Sex=sex_status)
    indivs = list(valid_meta.values_list('Individual', flat=True))
    filter_individuals(indivs)
    return JsonResponse({'message': 'Successfully filtered by sex'})

def filter_individuals(indivs):
    global individuals

    individuals_2 = list()

    for indiv in indivs:
        if indiv in individuals:
            individuals_2.append(indiv)

    individuals = individuals_2
    return

