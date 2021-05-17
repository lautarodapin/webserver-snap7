const instance = axios.create({
    baseURL: `${window.location.protocol}//${window.location.host}/api/`,
    timeout: 10000,
}); 

const PlotlyComponent =  {
    name: "plotly-component",
    template: `
    <div>
        <h1>{{name || 'Test'}}</h1>
        {{fila}}
        <div ref="plot"></div>
    </div>
    `,
    props: ["dato",],
    computed:{
        name() {return this.dato?.data.name;},
        fila() {return this.dato?.fila;},
        data() {return this.dato?.data;},
    },
    mounted() {
        var selectorOptions = {
            buttons: [{
                step: 'month',
                stepmode: 'backward',
                count: 1,
                label: '1m'
            }, {
                step: 'month',
                stepmode: 'backward',
                count: 6,
                label: '6m'
            }, {
                step: 'year',
                stepmode: 'todate',
                count: 1,
                label: 'YTD'
            }, {
                step: 'year',
                stepmode: 'backward',
                count: 1,
                label: '1y'
            }, {
                step: 'all',
            }],
        };
        var layout = {
            title: this.name,
            xaxis: {
                rangeselector: selectorOptions,
                rangeslider: {}
            },
            yaxis: {
                fixedrange: true
            }
        };
        console.log(this.data)
        const data = [this.data]
        Plotly.newPlot(this.$refs.plot, [this.data], layout);
    }
}

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    components: {PlotlyComponent, },
    data(){
        return{
            loading: false,
            progress: 0,
            searchFila: "",
            checkedFilas: [],
            plcs: [],
            areas: [],
            filas: [],
            datosProcesados: [],
            layout:{
                title: "My graph",
            },
            datos: [],
        }
    },
    computed:{
        filteredFilas(){
            if (this.searchFila === "") return this.filas;
            if (this.filas.length == 0) return [];
            return this.filas.filter(fila => {
                return this.searchFila.toLowerCase().split(' ').every(v => `${fila.area} ${fila.string}`.toLowerCase().includes(v))
            })
        },
    },
    methods:{
        async fetchData(e, url){
            var limit = 10000
            this.loading = true
            
            if (this.datosProcesados.length > 0) this.datosProcesados = [];
            if (!url) url = `datos-procesados/datos_procesados/?filas=${this.checkedFilas.join(",")}&limit=${limit}&offset=0`;
            var response = await this.getDatosProcesados(url)
            
            urlParams = new URLSearchParams(url)
            var offset = parseInt(urlParams.get("offset"))
            var progress = (offset + limit) / response.data.count * 100;
            
            console.log(response)
            this.datosProcesados.push(...response.data.results)
            // var count = response.count;
            // var hits_to_endpoint = count / limit
            // var progress = 1 / hits_to_endpoint
            while (response.data.next != null) {
                url = response.data.next;
                try {
                    response = await this.getDatosProcesados(url);
                    urlParams = new URLSearchParams(url)
                    offset = parseInt(urlParams.get("offset"))
                    progress = (offset + limit) / response.data.count * 100;
                    console.log(response)
                    this.datosProcesados.push(...response.data.results)
                    this.progress = progress;
                    // progress += 1 / hits_to_endpoint
                    // this.progress = progress * 100
                } catch (error) {
                    console.log("Error", error.response)
                    break;
                }
            }
            this.progress = 0;
            this.checkedFilas= [];
            this.loading = false
            this.renderDatosProcesados();
        },
        getDatosProcesados(url){
            return new Promise((resolve, reject) => {
                instance.get(url)
                .then(response => {
                    resolve(response)
                })
                .catch(error =>     {
                    reject(error)
                })
            })
        },
        renderDatosProcesados(){
            // mountApp.datosProcesados.map(dato => dato.fila).filter((value, index, self) => self.indexOf(value) === index)
            // console.log(this.datosProcesados)
            const filas = this.datosProcesados
                .map(dato => dato.fila)
                .filter((value, index, self) => self.indexOf(value) === index)
            // console.log(filas)
            var datos = []
            for(var i = 0; i < filas.length; i++){
                var datosFiltrados = this.datosProcesados.filter(dato => dato.fila === filas[i])
                // console.log(datosFiltrados)
                var dato = {
                    data: {
                        x: Array.from(datosFiltrados, dato => dato.date),//.split("T").join(" ").substring(0, dato.date.length - 1)), // "2020-01-01T00:02:00Z".split("T").join(" ").substring(0, "2020-01-01T00:02:00Z".length-1)
                        y: Array.from(datosFiltrados, dato => dato.dato),
                        type: "scatter",
                        name: `${datosFiltrados[0].name}`,
                    },
                    fila: filas[i],
                }
                datos.push(dato)
            }
            // console.log(data)
            this.datos = datos;
        },
        getPlcs(){
            return new Promise((resolve, reject) => {
                instance.get("plcs/")
                .then(response => {
                    this.plcs = response.data.results
                    resolve(response)
                })
                .catch(error => {
                    reject(error.response)
                })
            })
        },
        getAreas(){
            return new Promise((resolve, reject) => {
                instance.get("areas/")
                .then(response => {
                    this.areas = response.data.results
                    resolve(response)
                })
                .catch(error => {
                    reject(error.response)
                })
            })
        },
        getFilas(){
            return new Promise((resolve, reject) => {
                instance.get("filas/?limit=100")
                .then(response => {
                    this.filas = response.data.results
                    resolve(response)
                })
                .catch(error => {
                    reject(error.response)
                })
            })
        },
        addPoint(){
            this.data[0].x.push(Math.random()); 
            this.data[0].y.push(Math.random()); 
            Plotly.redraw(this.$refs.plotlyEl)
        }
    },
    created(){
        Promise.all([
            this.getFilas(),
        ])
    },
    mounted(){
    }
});
const mountApp = app.mount("#app")