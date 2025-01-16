let curr_cohorts = {};
// let cohortColors = ['red', 'blue', 'green', 'purple'];
let sequence = null;
let cohorts = null;
let variants = null;
let cohort_colors = null;
let cohorts_variants = null;
let expanded = false;
let last_cohort_call;
// let last_


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

// window.onload = function() {
//      renderSequenceList();
// };
function map_cohort(cohort){
    let c = parseInt(cohort);
    if(curr_cohorts.hasOwnProperty(c)){
        cohortColors.push(curr_cohorts[c]);
        delete curr_cohorts[c];
    }
    else if(Object.keys(curr_cohorts).length < 4){
        curr_cohorts[c] = cohortColors.pop();
    }
    // renderSequenceList();
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
            // renderSequenceList();
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

document.addEventListener('DOMContentLoaded', function () {
    const helpButton = document.getElementById('help-button');
    const helpModal = document.getElementById('help-modal');

    const filterButton = document.getElementById('filter-button');
    const filterModal = document.getElementById('filter-modal');

    // Toggle the display of the help modal
    helpButton.onclick = function () {
        helpModal.style.display = helpModal.style.display === "block" ? "none" : "block";
    };

    // Toggle the display of the filter modal
    filterButton.onclick = function () {
        filterModal.style.display = filterModal.style.display === "block" ? "none" : "block";
    };

    // Close the help modal if clicking outside
    window.addEventListener('click', function (event) {
        if (event.target === helpModal) {
            helpModal.style.display = "none";
        }
    });

    // Close the filter modal if clicking outside
    window.addEventListener('click', function (event) {
        if (event.target === filterModal) {
            filterModal.style.display = "none";
            last_cohort_call();
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const dropdown = document.getElementById("filter_to_add");
    const dynamic_content = document.getElementById("filter-dropdown-content");

    dropdown.addEventListener("change", () => {
        const selected_filter = dropdown.value;
        dynamic_content.innerHTML = "";

        switch (selected_filter){
            case "age":
                dynamic_content.innerHTML = `
                <p>Filter the cohort based on age:</p>
                <label for="min_float">Minimum Age:</label>
                <input type="range" id="min_float" name="min_float" min="0" max="100" value="1" oninput="updateRange()">
                <span id="min_float_value">1</span>
                <br>
                
                <label for="max_float">Maximum Age:</label>
                <input type="range" id="max_float" name="max_float" min="0" max="100" value="99" oninput="updateRange()">
                <span id="max_float_value">99</span>
                <br>
                
                <button onclick="filter_age()">Filter</button>
                `;
                break
            case "bmi":
                dynamic_content.innerHTML = `
                <p>Filter the cohort based on BMI:</p>
                <label for="min_float">Minimum BMI:</label>
                <input type="range" id="min_float" name="min_float" min="0" max="100" value="1" oninput="updateRange()">
                <span id="min_float_value">1</span>
                <br>
                
                <label for="max_float">Maximum BMI:</label>
                <input type="range" id="max_float" name="max_float" min="0" max="100" value="99" oninput="updateRange()">
                <span id="max_float_value">99</span>
                <br>
                
                <button onclick="filter_age()">Filter</button>
                `;
                break
        }
    });

});

function updateRange() {
    const min_float = document.getElementById('min_float').value;
    const max_float = document.getElementById('max_float').value;

    document.getElementById('min_float_value').textContent = min_float;
    document.getElementById('max_float_value').textContent = max_float;
}

function filter_age(){
    const minAge = document.getElementById('min_float').value;
    const maxAge = document.getElementById('max_float').value;

    const xhr = new XMLHttpRequest();
    xhr.open('GET', `filter_age/?min_age=${minAge}&max_age=${maxAge}`, true);
    xhr.send();

    let element = document.getElementById('curr-filters');
    let paragraphElement = document.createElement('p');
    paragraphElement.innerHTML += `Age filtered from ${minAge} to ${maxAge}`;
    element.appendChild(paragraphElement);
}
// TODO: Start here
function filter_bmi(){
    const minAge = document.getElementById('min_float').value;
    const maxAge = document.getElementById('max_float').value;

    const xhr = new XMLHttpRequest();
    xhr.open('GET', `filter_age/?min_age=${minAge}&max_age=${maxAge}`, true);
    xhr.send();

    let element = document.getElementById('curr-filters');
    let paragraphElement = document.createElement('p');
    paragraphElement.innerHTML += `Age filtered from ${minAge} to ${maxAge}`;
    element.appendChild(paragraphElement);
}

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
                    <button onclick="call_make_cohorts(\`make_disease_cohorts\`)">Make Cohorts Based On Disease Status</button>
                `;
                break;
            case "drug":
                dynamicContent.innerHTML = `
                    <br>
                    <button onclick="call_make_cohorts(\`make_drug_cohorts\`)">Make Cohorts Based On Drug Status</button>
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
                    <button onclick="call_make_cohorts(\`make_sex_cohorts\`)">Make Cohorts Based On Sex</button>
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

function call_make_cohorts(url){
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onload = function() {
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            cohorts = response.cohorts;
            cohort_colors = response.cohort_colors;
            let categories = response.categories;
            display_cohorts(categories);
        } else {
            console.error('Error making cohorts:', xhr.status);
        }
    };
    xhr.send();
}

function make_age_cohorts(){
    if (document.getElementById("age_cohort_number").value === null){
        return;
    }
    let cohortNumber = parseInt(document.getElementById("age_cohort_number").value);
    call_make_cohorts(`make_age_cohorts/?cohort_number=${cohortNumber}`);
    last_cohort_call = () => call_make_cohorts(`make_age_cohorts/?cohort_number=${cohortNumber}`);
}

function make_bmi_cohorts(){
    if (document.getElementById("bmi_cohort_number").value === null){
        return;
    }
    let cohortNumber = parseInt(document.getElementById("bmi_cohort_number").value);
    call_make_cohorts(`make_bmi_cohorts/?cohort_number=${cohortNumber}`);
    last_cohort_call = () => call_make_cohorts(`make_bmi_cohorts/?cohort_number=${cohortNumber}`);
}

function display_cohorts(categories){
    let cohortNumber = cohorts.length;
    let element = document.getElementById("dynamic-content");
    element.innerHTML = '';  // Clear previous results
    if(cohorts === null){
        element.innerHTML = '<li>No Cohorts Made.</li>';
        return;
    }
    for (let i = 0; i < cohortNumber; i++) {
        let cohort_container = document.createElement('div');
        const individuals = document.createElement('h3');

        individuals.innerHTML += `<span style="background-color: ${cohort_colors[i]};">${categories[i]} cohort:\t`;

        for(let indiv of cohorts[i]){
                individuals.innerHTML += `<span style="background-color: white;">${indiv},\t`;
        }

        individuals.innerHTML = individuals.innerHTML.slice(0, -9) + '</span>';
        cohort_container.appendChild(individuals);
        cohort_container.style.display = 'flex';
        cohort_container.style.justifyContent = 'flex-start';
        cohort_container.style.alignItems = 'center';
        element.appendChild(cohort_container);
    }
    bust_cache();
}

function reset_filters(){
    const xhr = new XMLHttpRequest();
    xhr.open('GET', 'reset_filters/', true);
    xhr.send();
    let element = document.getElementById('curr-filters');
    element.innerHTML = '';
}

//TODO: Use the filtered data by recalling the used functions (like make_??_cohorts, bust_cache, etc...).