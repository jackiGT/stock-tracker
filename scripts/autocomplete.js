let ExampleKeywords = [
    'AAPL',
    'NVDA',
    'INTC',
    'NOK',
    'RBLX',
    'RDDT',
    'AMZN',
    'MCD',
    'UBER',
    'PANW',
    'O',
    'NKE',
    'PEP',
    'NNE'
];

const resultsBox = document.querySelector('.result-box')
const inputBox = document.getElementById("input-box")

inputBox.addEventListener('keyup', (e) => {
    let result = [];
    let input = inputBox.value;
    if(input.length > 0){
        result = ExampleKeywords.filter((keyword) => {
            return keyword.toLowerCase().includes(input.toLowerCase());
        });
    }
    display(result);

    if(!result.length){
        resultsBox.firstChild.remove();
    }
});


function display(result){
    const ul = document.createElement('ul');

    const content = result.map((stock)=>{
        const li = document.createElement('li');

        li.addEventListener('click', (e) => {
            inputBox.value = stock;
            ul.remove();
        });
        li.textContent = stock;

        ul.appendChild(li);
        
    });

    console.log(resultsBox);
    resultsBox.appendChild(ul);


    if(resultsBox.children.length === 0){
        resultsBox.appendChild(ul);
    }else {
        resultsBox.firstChild.remove();
        resultsBox.appendChild(ul);
    }
}

