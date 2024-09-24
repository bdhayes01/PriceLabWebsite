function searchSequence() {
    const query = document.getElementById('search').value;
    if (query) {
        window.location.href = `?q=${query}`;
    }
}

function createHeatmap(cohorts, variants) {
    const sequenceContainer = document.createElement('p');
    for (let i = 0; i < cohorts.length; i++) {
        const span = document.createElement('span');
        const individuals = document.createElement('h3');
        individuals.textContent += "Cohort " + (i + 1) + ':\t' + cohorts[i][0];

        for (let j = 1; j < cohorts[i].length; j++){
            individuals.textContent += ',\t' + cohorts[i][j];
        }
        span.innerHTML += "Variations: ";
        let entered = false;
        for (const key in variants[cohorts[i][0]]){
            entered = true;
            span.innerHTML += key + ": "  + variants[cohorts[i][0]][key] + '\t';
        }
        if(!entered){
            span.innerHTML += "None."
        }
        span.className = 'normal';
        sequenceContainer.appendChild(individuals);
        sequenceContainer.appendChild(span);
    }
    return sequenceContainer;
}

function renderSequenceList() {
    const sequence = sequence_json;  // Access from global variable
    const seqList = document.getElementById('sequence-list');

    if (sequence.Cohorts.length > 0) {
        seqList.innerHTML = '';  // Clear previous results
        const heatmap = createHeatmap(sequence.Cohorts, sequence.Variants);
        seqList.appendChild(heatmap);
    } else {
        seqList.innerHTML = '<li>No results found.</li>';
    }
}

window.onload = function() {
    renderSequenceList();
};