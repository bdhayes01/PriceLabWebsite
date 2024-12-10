let curr_cohorts = {};
// let cohortColors = ['red', 'blue', 'green', 'purple'];
let sequence = null;
let cohorts = null;
let variants = null;
let cohort_colors = null;
let cohorts_variants = null;
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
        top_char_span.style.display = i < 2000 ? 'inline' : 'none';  // Show only the first 2000 chars initially
        top_char_span.style.backgroundColor = null;

        // Loop through cohorts to check for a variant at this position
        for (let cohort in curr_cohorts){
            let varis_amount = cohorts_variants[cohort][i + 1];
            if (varis_amount){
                if (top_char_span.style.backgroundColor !== "" || top_char_span.style.backgroundImage !== ""){
                    top_char_span.style.backgroundImage = ""
                    top_char_span.style.color = "black";
                    top_char_span.style.backgroundColor = "white";
                    top_char_span.style.border = "solid";
                    top_char_span.style.borderColor = "black";
                } else {
                    if(parseFloat(varis_amount[1]) * 100 < 99){
                        top_char_span.style.backgroundImage = `linear-gradient(to bottom right, ${curr_cohorts[cohort]}, white)`
                        // top_char_span.style.textShadow = `1px 1px ${curr_cohorts[cohort]}`
                        // top_char_span.style.textDecorationThickness = "4px";
                        // top_char_span.style.textDecorationLine = "underline overline";
                        // top_char_span.style.textDecorationColor = curr_cohorts[cohort];
                    }else{
                        top_char_span.style.backgroundColor = curr_cohorts[cohort];
                        top_char_span.style.color = "white";
                    }
                }
                top_char_span.title += `Cohort ${parseInt(cohort) + 1} has ${Math.round(parseFloat(varis_amount[1]) * 100)}% mutation penetrance at position ${i + 1};\t`;
            }
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
        let x = cohorts_variants[i];


        for (const position in cohorts_variants[i]){
            let variant_span = document.createElement('span');
            variant_span.innerHTML = `${sequence[parseInt(position) - 1]} ${position} ${cohorts_variants[i][position][2]},\t`
            for(let mut in cohorts_variants[i][position][0]){
                for(let indiv of cohorts_variants[i][position][0][mut]){
                    variant_span.title += `${indiv} has mutation ${mut}\n`
                    entered = true;
                }
            }
             span.appendChild(variant_span);
        }
        if(!entered){
            span.innerHTML += "None."
        }
        else{
            let element = span.lastElementChild;
            element.innerHTML = element.innerHTML.slice(0, -2);
        }
        span.className = 'normal';
        sequenceContainer.appendChild(cohort_container);
        sequenceContainer.appendChild(span);
    }
    return sequenceContainer;
}

function renderSequenceList() {
    const json = chalf_json;  // Access from global variable
    const seqList = document.getElementById('sequence-list');

    if (json.Sequence) {
        seqList.innerHTML = '';  // Clear previous results
        sequence = json.Sequence;
        variants = json.Variants;
        if(cohorts !== null){
            const heatmap = createHeatmap();
            seqList.appendChild(heatmap);
        }
        else if (Object.values(variants).every(dict => Object.keys(dict).length === 0)){
            let paragraphElement = document.createElement('p');
            paragraphElement.innerHTML += "No mutations found.";
            seqList.appendChild(paragraphElement);
        }
    } else {
        seqList.innerHTML = '<li>No results found. Last valid search displayed.</li>';
    }
}

window.onload = function() {
    renderSequenceList();
};
function map_cohort(cohort){
    let c = parseInt(cohort);
    if(curr_cohorts.hasOwnProperty(c)){
        cohortColors.push(curr_cohorts[c]);
        delete curr_cohorts[c];
    }
    else if(Object.keys(curr_cohorts).length < 4){
        curr_cohorts[c] = cohortColors.pop();
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
    cohorts_variants = {};
    for (let c in cohorts){
        let cohort_variants = {};
        let cohort = cohorts[c];
        for (let indiv of cohort){
            for (let position in variants[indiv]){
                if(cohort_variants[position]){

                    //Adds to the percentage of the cohort with variant in the position
                    cohort_variants[position][1] = cohort_variants[position][1] + 1/cohort.length;

                    let positional_variants = cohort_variants[position][0];
                    if(positional_variants[variants[indiv][position]]){
                        //Appends to the list of individuals with this specific mutation in the cohort.
                        positional_variants[variants[indiv][position]].push(indiv);
                    }
                    else{
                        // Adds a new variant at this position
                        positional_variants[variants[indiv][position]] = [indiv];
                    }
                }
                else{
                    let positional_variants = {};
                    positional_variants[variants[indiv][position]] = [indiv];
                    cohort_variants[position] = [positional_variants, 1/cohort.length];
                }
                let max_char = "Z";
                let max_num = -1;
                for(let mut in cohort_variants[position][0]){
                    let length_mutations = cohort_variants[position][0][mut].length;
                    if(length_mutations > max_num){
                        max_num = length_mutations;
                        max_char = mut;
                    }
                }
                cohort_variants[position].push(max_char);
            }
        }
        cohorts_variants[c] = cohort_variants;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const helpButton = document.getElementById('help-button');
    const modal = document.getElementById('help-modal');

    // Show the modal when the help button is clicked
    helpButton.onclick = function() {
        if(modal.style.display === ""){
            modal.style.display = 'block';
        }else{
            modal.style.display = "";
        }
    };

    // Close the modal when clicking outside the content
    window.onclick = function(event) {
        if (event.target !== helpButton) {
            modal.style.display = "";
        }
    };
});

document.addEventListener("DOMContentLoaded", () => {
    const dropdown = document.getElementById("independent_variable");
    const dynamicContent = document.getElementById("dynamic-content");

    dropdown.addEventListener("change", () => {
        const selectedValue = dropdown.value;

        // Clear any existing content
        dynamicContent.innerHTML = "";

        // Update HTML based on the selected value
        switch (selectedValue) {
            case "age":
                dynamicContent.innerHTML = `
                    <p>Group into cohorts by age. Choose the number of cohorts.</p>
                    <input type="number" placeholder="Number of Cohorts" id="age_cohort_number">
                    <button onclick="make_age_cohorts()">Make Cohorts</button>
                `;
                break;
            case "bmi":
                dynamicContent.innerHTML = `
                    <p>Group into cohorts by BMI. Choose the number of cohorts.</p>
                    <input type="number" placeholder="Number of Cohorts" id="bmi_cohort_number">
                    <button onclick="make_bmi_cohorts()">Make Cohorts</button>
                `;
                break;
            case "disease":
                dynamicContent.innerHTML = `
                    <br>
                    <button onclick="make_disease_cohorts()">Make Cohorts Based On Disease Status</button>
                `;
                break;
            case "drug":
                dynamicContent.innerHTML = `
                    <br>
                    <button onclick="make_drug_cohorts()">Make Cohorts Based On Drug Status</button>
                `;
                break;
            case "mutations":
                dynamicContent.innerHTML = `
                    <h3>Mutations Module</h3>
                    <p>Configure mutations or view details here.</p>
                    <textarea placeholder="Enter mutations data"></textarea>
                `;
                break;
            case "sex":
                dynamicContent.innerHTML = `
                    <br>
                    <button onclick="make_sex_cohorts()">Make Cohorts Based On Sex</button>
                `;
                break;
            default:
                dynamicContent.innerHTML = `<p>Select an option to view details.</p>`;
        }
    });
});

function bust_cache(){
    const img = document.querySelector("img[alt='CHalf']");
    img.src = img.src + '?' + new Date().getTime();
}

function make_sex_cohorts(){
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `make_sex_cohorts`, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            cohorts = response.cohorts;
            cohort_colors = response.cohort_colors;
            populate_cohort_list_sex()
        } else {
            console.error('Error making cohorts:', xhr.status);
        }
    };
    xhr.send();
}

function populate_cohort_list_sex(){
    let element = document.getElementById("dynamic-content")
    element.innerHTML = '';  // Clear previous results
    if(cohorts === null){
        element.innerHTML = '<li>No Cohorts Made.</li>';
        return;
    }
    for (let i = 0; i < 2; i++) {
        let cohort_container = document.createElement('div');
        const individuals = document.createElement('h3');
        if(i===0){
            individuals.textContent += "Male Cohort:\t";
            for(let indiv of cohorts[0]){
                individuals.textContent += `${indiv},\t`
            }
        }else{
            individuals.textContent += "Female Cohort:\t";
            for(let indiv of cohorts[1]){
                individuals.textContent += `${indiv},\t`
            }
        }
        individuals.textContent = individuals.textContent.slice(0, -2);
        individuals.style.backgroundColor = cohort_colors[i];
        cohort_container.appendChild(individuals);
        cohort_container.style.display = 'flex';
        cohort_container.style.justifyContent = 'flex-start';
        cohort_container.style.alignItems = 'center';
        element.appendChild(cohort_container);
    }
    bust_cache();
}

function make_disease_cohorts(){
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `make_disease_cohorts`, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            cohorts = response.cohorts;
            cohort_colors = response.cohort_colors;
            populate_cohort_list_disease()
        } else {
            console.error('Error making cohorts:', xhr.status);
        }
    };
    xhr.send();
}

function populate_cohort_list_disease(){
    let element = document.getElementById("dynamic-content")
    element.innerHTML = '';  // Clear previous results
    if(cohorts === null){
        element.innerHTML = '<li>No Cohorts Made.</li>';
        return;
    }
    for (let i = 0; i < 2; i++) {
        let cohort_container = document.createElement('div');
        const individuals = document.createElement('h3');
        if(i===0){
            individuals.textContent += "Diseased Cohort:\t";
            for(let indiv of cohorts[0]){
                individuals.textContent += `${indiv},\t`
            }
        }else{
            individuals.textContent += "Undiseased Cohort:\t";
            for(let indiv of cohorts[1]){
                individuals.textContent += `${indiv},\t`
            }
        }
        individuals.textContent = individuals.textContent.slice(0, -2);
        individuals.style.backgroundColor = cohort_colors[i];
        cohort_container.appendChild(individuals);
        cohort_container.style.display = 'flex';
        cohort_container.style.justifyContent = 'flex-start';
        cohort_container.style.alignItems = 'center';
        element.appendChild(cohort_container);
    }
    bust_cache();
}

function make_drug_cohorts(){
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `make_drug_cohorts`, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            cohorts = response.cohorts;
            cohort_colors = response.cohort_colors;
            populate_cohort_list_drug()
        } else {
            console.error('Error making cohorts:', xhr.status);
        }
    };
    xhr.send();
}

function populate_cohort_list_drug(){
    let element = document.getElementById("dynamic-content")
    element.innerHTML = '';  // Clear previous results
    if(cohorts === null){
        element.innerHTML = '<li>No Cohorts Made.</li>';
        return;
    }
    for (let i = 0; i < 2; i++) {
        let cohort_container = document.createElement('div');
        const individuals = document.createElement('h3');
        if(i===0){
            individuals.textContent += "Taking Drug Cohort:\t";
            for(let indiv of cohorts[0]){
                individuals.textContent += `${indiv},\t`
            }
        }else{
            individuals.textContent += "Not Taking Drug Cohort:\t";
            for(let indiv of cohorts[1]){
                individuals.textContent += `${indiv},\t`
            }
        }
        individuals.textContent = individuals.textContent.slice(0, -2);
        individuals.style.backgroundColor = cohort_colors[i];
        cohort_container.appendChild(individuals);
        cohort_container.style.display = 'flex';
        cohort_container.style.justifyContent = 'flex-start';
        cohort_container.style.alignItems = 'center';
        element.appendChild(cohort_container);
    }
    bust_cache();
}

function make_age_cohorts(){
    if (document.getElementById("age_cohort_number").value === null){
        return;
    }
    let cohortNumber = parseInt(document.getElementById("age_cohort_number").value);
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `make_age_cohorts/?cohort_number=${cohortNumber}`, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            cohorts = response.cohorts;
            cohort_colors = response.cohort_colors;
            populate_cohort_list_age()
        } else {
            console.error('Error making cohorts:', xhr.status);
        }
    };
    xhr.send();
}

function populate_cohort_list_age(){
    let cohortNumber = parseInt(document.getElementById("age_cohort_number").value);
    //The above line needs to be executed before we delete the innerHTML of dynamic-content
    let element = document.getElementById("dynamic-content");
    element.innerHTML = '';  // Clear previous results
    if(cohorts === null){
        element.innerHTML = '<li>No Cohorts Made.</li>';
        return;
    }
    for (let i = 0; i < cohortNumber; i++) {
        let cohort_container = document.createElement('div');
        const individuals = document.createElement('h3');
        individuals.textContent += `Cohort ${i + 1}:\t`;
        for(let indiv of cohorts[i]){
                individuals.textContent += `${indiv},\t`
            }

        individuals.textContent = individuals.textContent.slice(0, -2);
        individuals.style.backgroundColor = cohort_colors[i];
        cohort_container.appendChild(individuals);
        cohort_container.style.display = 'flex';
        cohort_container.style.justifyContent = 'flex-start';
        cohort_container.style.alignItems = 'center';
        element.appendChild(cohort_container);
    }
    bust_cache();
}

function make_bmi_cohorts(){
    if (document.getElementById("bmi_cohort_number").value === null){
        return;
    }
    let cohortNumber = parseInt(document.getElementById("bmi_cohort_number").value);
    const xhr = new XMLHttpRequest();
    xhr.open('GET', `make_bmi_cohorts/?cohort_number=${cohortNumber}`, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            cohorts = response.cohorts;
            cohort_colors = response.cohort_colors;
            populate_cohort_list_bmi()
        } else {
            console.error('Error making cohorts:', xhr.status);
        }
    };
    xhr.send();
}

function populate_cohort_list_bmi(){
    let cohortNumber = parseInt(document.getElementById("bmi_cohort_number").value);
    //The above line needs to be executed before we delete the innerHTML of dynamic-content
    let element = document.getElementById("dynamic-content");
    element.innerHTML = '';  // Clear previous results
    if(cohorts === null){
        element.innerHTML = '<li>No Cohorts Made.</li>';
        return;
    }
    for (let i = 0; i < cohortNumber; i++) {
        let cohort_container = document.createElement('div');
        const individuals = document.createElement('h3');
        individuals.textContent += `Cohort ${i + 1}:\t`;
        for(let indiv of cohorts[i]){
                individuals.textContent += `${indiv},\t`
            }

        individuals.textContent = individuals.textContent.slice(0, -2);
        individuals.style.backgroundColor = cohort_colors[i];
        cohort_container.appendChild(individuals);
        cohort_container.style.display = 'flex';
        cohort_container.style.justifyContent = 'flex-start';
        cohort_container.style.alignItems = 'center';
        element.appendChild(cohort_container);
    }
    bust_cache();
}
