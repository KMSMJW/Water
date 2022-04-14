const API_END_POINT = `${location.protocol}//${location.host}/api/`;
const request = async (url, options = {}) => {
    try {
        const fullUrl = `${API_END_POINT}${url}`;
        const response = await fetch(fullUrl, options);

        if(response.ok) {
            const data = await response.json();
            return data;
        }
        throw new Error("API Error")
    }catch (e) {
        console.log(e.message)
    }
}

const formatint = (number) => {

}

function getCellData(element) {
    if(element){
        let text = element.innerText
        return parseFloat(text.replace(/,/g,''))
    }

    return null;
}

class FirstWaterQualityComponent {
    constructor({$target}){
        this.state = {}
        this.$inputTable = $target.querySelector('#first-water-table');
        this.$cells = this.$inputTable.rows[2].cells;
        this.$resultBOD = $target.querySelector('#result-bod');
        this.$resultCNRaito = $target.querySelector('#result-cn-raito');
        this.$secondWaterCells = $target.querySelector('#second-water-predict-table').rows[1].cells

            //Add Event Listenser
        this.$inputTable.addEventListener('keypress', (event) => {
            if (event.key == 'Enter') {
                //disable enter on table
                event.preventDefault();
                //updatePredictSecondWater();
                this.postData()
            }
        })

        //get today data.
        request('data').then((data) => {
            this.state = data;
            
            this.renderRow();
            this.renderResult();
        })
    }


    //render html code.
    renderRow() {
        this.$cells[0].innerText = this.state.data['date'];
        this.$cells[1].innerText = this.state.data['temp_air'].toFixed(1);
        this.$cells[2].innerText = this.state.data['rainfall'].toFixed(1);
        this.$cells[3].innerText = this.state.data['temp_biotank'].toFixed(1);
        this.$cells[4].innerText = this.state.data['inflow_volume'].toLocaleString();
        this.$cells[5].innerText = this.state.data['inflow_ss'].toFixed(1);
        this.$cells[6].innerText = this.state.data['inflow_tn'].toFixed(3);
        this.$cells[7].innerText = this.state.data['inflow_tp'].toFixed(3);
        this.$cells[8].innerText = this.state.data['outflow_ss'].toFixed(1);
        this.$cells[9].innerText = this.state.data['outflow_tn'].toFixed(3);
        this.$cells[10].innerText = this.state.data['outflow_tp'].toFixed(3);
        this.$cells[11].innerText = this.state.data['outflow_nh4'].toFixed(3);
        this.$cells[12].innerText = this.state.data['air_flowrate'].toLocaleString();
    }

    renderResult() {
        if(this.state.result){
            this.$resultBOD.innerText = this.state.result['bod'].toFixed(1);
            this.$resultCNRaito.innerText = this.state.result['cn-raito'].toFixed(1);

            this.$secondWaterCells[0].innerText = this.state.result['predict'][0].toFixed(1)
            this.$secondWaterCells[1].innerText = this.state.result['predict'][1].toFixed(3)
            this.$secondWaterCells[2].innerText = this.state.result['predict'][2].toFixed(3)
        }
    }

    //api requests.
    postData() {
        let data = {
            data : this.getData()
        }
        
        console.log(JSON.stringify(data))

        request('data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        }).then((data) => {
            this.state = data;
            this.renderRow();
            this.renderResult();
        })

    }

    //get data from cell with type cast.
    getCellData(index) {
        let text = this.$cells[index].innerText
        return parseFloat(text)
    }

    getData(){
        let data = {
            date: this.state.data.date,
            temp_air: getCellData(this.$cells[1]),
            rainfall: getCellData(this.$cells[2]),
            temp_biotank: getCellData(this.$cells[3]),
            inflow_volume: getCellData(this.$cells[4]),
            inflow_ss: getCellData(this.$cells[5]),
            inflow_tn: getCellData(this.$cells[6]),
            inflow_tp: getCellData(this.$cells[7]),
            outflow_ss: getCellData(this.$cells[8]),
            outflow_tn: getCellData(this.$cells[9]),
            outflow_tp: getCellData(this.$cells[10]),
            outflow_nh4: getCellData(this.$cells[11]),
            air_flowrate: getCellData(this.$cells[12]),
        }

        return data;
    }
}

class AirflowPredictComponent{
    constructor({ $target }){
        this.state = {}
        this.$inputTable = $target.querySelector('#second-water-target-table');
        this.$cells = this.$inputTable.rows[1].cells;
        this.$resultRNNAirflow = $target.querySelector('#rnn-airflow')
        this.$resultRequireAirflow = $target.querySelector('#require-airflow')

        this.$inputTable.addEventListener('keypress', (event) => {
            if (event.key == 'Enter') {
                event.preventDefault();
                
                this.getAirflowPredict()
            }
        })
    }

    updateResults(){
        this.$resultRNNAirflow.innerText = this.state.result['rnn'].toLocaleString()
        this.$resultRequireAirflow.innerText = this.state.result['require'].toLocaleString()
    }

    getInput(){
        let input = {
            ss: this.$cells[0].innerText,
            tn: this.$cells[1].innerText,
            tp: this.$cells[2].innerText,
        }

        return input
    }

    getAirflowPredict() {
        let params = this.getInput()
        let query = Object.keys(params)
                        .map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`)
                        .join('&');
                    
        request('airflow?' + query).then((data) => {
            this.state = data;
            
            if(this.state.error){
                alert(this.state.message) 
            }else{
                this.updateResults()
            }
        })

        //update cells
    }
}

class FinalDecisionContainer{
    constructor({ $target }){
        this.$finalInput = $target.querySelector('#final-input')
        this.$finalOutputCells = $target.querySelector('#final-result-table').rows[1].cells


        this.$finalInput.addEventListener('keypress', (event) => {
            if (event.key == 'Enter') {
                event.preventDefault();
                
                this.getFinalResult()
            }
        })

        
    }

    updateResults() {
        this.$finalOutputCells[0].innerText = this.state.result[0].toFixed(1)
        this.$finalOutputCells[1].innerText = this.state.result[1].toFixed(3)
        this.$finalOutputCells[2].innerText = this.state.result[2].toFixed(3)
    }

    getInput() {
        let params = {
            d_air: getCellData(this.$finalInput)
        }

        return params
    }

    getFinalResult() {
        let params = this.getInput()
        let query = Object.keys(params)
                        .map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`)
                        .join('&');
                    
        request('final?' + query).then((data) => {
            this.state = data;
            
            if(this.state.error){
                alert(this.state.message) 
            }else{
                this.updateResults()
                this.$finalInput.innerText = params['d_air'].toLocaleString()
            }
            
        })

        

    }
}

new FirstWaterQualityComponent({
    $target: document.getElementById('first-water-container')
})

new AirflowPredictComponent({
    $target: document.getElementById('airflow-predict-container')
})

new FinalDecisionContainer({
    $target: document.getElementById('final-decision-container')
})