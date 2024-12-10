from myapp.models import Metadata
from collections import defaultdict
import matplotlib.pyplot as plt
from django.http import HttpResponse
import io


def make_disease_cohort():
    metadata = Metadata.objects.all()
    diseased_cohort = [meta.Individual for meta in metadata if meta.Disease]
    undiseased_cohort = [meta.Individual for meta in metadata if not meta.Disease]
    return [diseased_cohort, undiseased_cohort], ["orange", "blue"]


def make_graph_disease(chalf, cohorts, colors):
    x_values = defaultdict(list)
    y_values = defaultdict(list)
    errors = defaultdict(list)

    for indiv, value in chalf.items():
        for k, v in value.items():
            color = colors[0] if indiv in cohorts[0] else colors[1]
            x_values[color].append(round(float(k)))
            y_values[color].append(v[0])
            errors[color].append(v[1])
    plt.figure(figsize=(10, 6))
    for color in colors:
        if color not in x_values:
            continue
        sorted_data = sorted(zip(x_values[color], y_values[color], errors[color]),
                             key=lambda x: x[0])  # Sort by x_values
        sorted_x, sorted_y, sorted_errors = zip(*sorted_data)  # Use separate variables to unpack sorted data
        plt.errorbar(sorted_x, sorted_y, yerr=sorted_errors, fmt='o', capsize=5, label=f'Data ({color})',
                     color=color)
    plt.title("C-Half values for selected protein")
    plt.xlabel("Residues")
    plt.ylabel("C-Half")
    plt.grid(True)
    plt.legend(["With disease", "Without disease"])
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')
