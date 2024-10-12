let curr_cohorts = {};
let cohortColors = ['red', 'blue', 'yellow', 'purple'];
let sequence = null;
let cohorts = null;
let variants = null;
let cohort_variants = null;
let expanded = false;


function searchSequence() {
    const query = document.getElementById('search').value;
    if (query) {
        window.location.href = `?q=${query}`;
    }
}

function color_code(container){
    const toggleButton = document.createElement('button');
    toggleButton.textContent = "Show More";
    const spans = [];

    for (let i = 0; i < sequence.length; i++) {
        const top_char_span = document.createElement('span');
        top_char_span.textContent = sequence[i];
        top_char_span.style.display = i < 2000 ? 'inline' : 'none';  // Show only the first 50 chars initially

        // Loop through cohorts to check for a variant at this position
        for (let key in curr_cohorts){
            if (cohort_variants[key][i]){
                top_char_span.style.backgroundColor = curr_cohorts[key];
                top_char_span.title += `Cohort ${parseInt(key) + 1} has variant at position ${i + 1};\t`;
            }
            // let cohort = cohorts[key][0];
            // const variantPositions = Object.keys(variants[cohort] || {});
            // if (variantPositions.includes((i + 1).toString())) {
            //     // Apply background color based on cohort index
            //     charSpan.style.backgroundColor = curr_cohorts[key];
            //     charSpan.title += `Cohort ${parseInt(key) + 1} Variant: ${variants[cohort][parseInt(i) + 1]} at position ${i + 1};\t`;  // Optional tooltip
            // }
        }
        container.appendChild(top_char_span);
        spans.push(top_char_span);
    }
        // Add toggle button functionality
    toggleButton.onclick = () => {
        expanded = !expanded; // Toggle the expanded state
        // Loop through spans to toggle visibility based on the expanded state
        spans.forEach((span, index) => {
            span.style.display = expanded || index < 2000 ? 'inline' : 'none'; // Show the span if expanded or index < 2000
        });

        toggleButton.textContent = expanded ? 'Show Less' : 'Show More';
    };

    container.appendChild(toggleButton);  // Add button to the container
}

function createHeatmap() {
    const sequenceContainer = document.createElement('p');
    color_code(sequenceContainer);
    for (let i = 0; i < cohorts.length; i++) {
        const span = document.createElement('span');
        let cohort_container = document.createElement('div');
        const individuals = document.createElement('h3');
        individuals.textContent += "Cohort " + (i + 1) + ':\t' + cohorts[i][0];

        for (let j = 1; j < cohorts[i].length; j++){
            individuals.textContent += ',\t' + cohorts[i][j];
        }
        individuals.style.marginRight = '10px';
        const cohort_button = document.createElement('button');
        cohort_button.textContent = "Map Variants";
        cohort_button.onclick = () => map_cohort(i);

        if (i in curr_cohorts){
            individuals.style.backgroundColor = curr_cohorts[i];
        }

        cohort_container.appendChild(individuals);
        cohort_container.appendChild(cohort_button);
        cohort_container.style.display = 'flex';
        cohort_container.style.justifyContent = 'flex-start';

        cohort_container.style.alignItems = 'center';

        span.innerHTML += "Variations: ";
        let entered = false;

        let cohort_variants_set = new Set();
        for (const member of cohorts[i]) {
            for (const key in variants[member]) {
                cohort_variants_set.add(sequence[parseInt(key) - 1] + " " + key + " " + variants[member][key] + ',\t');
            }
        }
        for(let item of cohort_variants_set){
            entered = true;
            span.innerHTML += item
        }
        if(!entered){
            span.innerHTML += "None."
        }
        else{
            span.innerHTML = span.innerHTML.slice(0, -2);
        }
        span.className = 'normal';
        sequenceContainer.appendChild(cohort_container);
        sequenceContainer.appendChild(span);
    }
    return sequenceContainer;
}

function renderSequenceList() {
    const json = sequence_json;  // Access from global variable
    const seqList = document.getElementById('sequence-list');

    if (json.Sequence.length > 0) { //TODO: Check if this works with no valid json
        seqList.innerHTML = '';  // Clear previous results
        sequence = json.Sequence;
        variants = json.Variants;
        if(cohorts !== null){
            const heatmap = createHeatmap();
            seqList.appendChild(heatmap);
        }
    } else {
        seqList.innerHTML = '<li>No results found.</li>';
    }
}

window.onload = function() {
    renderSequenceList();
};
function map_cohort(cohort){
    if(parseInt(cohort) in Object.keys(curr_cohorts)){
        let c = parseInt(cohort)
        delete curr_cohorts[c];
    }
    else{
        curr_cohorts[parseInt(cohort)] = cohortColors[parseInt(cohort)];
    }
    renderSequenceList();
}

function make_cohorts(){
    const cohortNumber = document.getElementById('cohort_number').value;
    localStorage.setItem('cohort_number', cohortNumber);
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `make_cohorts/?cohort_number=${cohortNumber}`, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            cohorts = response.cohorts;
            const dendrogramImage = document.querySelector("img[alt='Dendrogram']");
            dendrogramImage.src = dendrogramImage.src + '?' + new Date().getTime();  // Cache-busting
            make_cohort_variants();
            renderSequenceList();
        } else {
            console.error('Error making cohorts:', xhr.status);
        }
    };
    xhr.send();
}

function make_cohort_variants(){
    cohort_variants = {}
    for (let c in cohorts){
        let varis = {};
        let cohort = cohorts[c];
        for (let indiv of cohort){
            for (let variation in variants[indiv]){
                if (varis[variation]){
                    varis[variation] = varis[variation] + 1;
                }
                else{
                    varis[variation] = 1;
                }
            }
        }
        cohort_variants[c] = varis;
    }
}

document.addEventListener('DOMContentLoaded', function () {
        const savedCohortNumber = localStorage.getItem('cohort_number');
        if (savedCohortNumber) {
            document.getElementById('cohort_number').value = savedCohortNumber;
        }
    });