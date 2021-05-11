const instance = axios.create({
    baseURL: `${window.location.protocol}//${window.location.host}/api/`,
    timeout: 1000,
}); 
const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data(){
        return{
            searchFila: "",
            checkedFilas: [],
            plcs: [],
            areas: [],
            filas: [],
            datosProcesados: [],
            data:[{
                x: [1,2,3,4],
                y: [10,15,13,17],
                type:"scattergl"
            }],
            layout:{
                title: "My graph",
            }
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
            if (this.datosProcesados.length > 0) this.datosProcesados = [];
            if (!url) url = `datos-procesados/filter_filas/?filas=${this.checkedFilas.join(",")}`;
            var response = await this.getDatosProcesados(url)
            console.log(response)
            this.datosProcesados.push(...response.data.results)
            while (response.data.next != null) {
                url = response.data.next;
                response = await this.getDatosProcesados(url);
                console.log(response)
                this.datosProcesados.push(...response.data.results)
            }
            this.renderDatosProcesados();
            this.checkedFilas= [];
        },
        renderDatosProcesados(){
            console.log(this.datosProcesados)
            const data = [{
                x: Array.from(this.datosProcesados, dato => dato.date),//.split("T").join(" ").substring(0, dato.date.length - 1)), // "2020-01-01T00:02:00Z".split("T").join(" ").substring(0, "2020-01-01T00:02:00Z".length-1)
                y: Array.from(this.datosProcesados, dato => dato.dato),
                type:"scatter",
            }]
            console.log(data)
            const el = this.$refs.plotlyEl
            Plotly.newPlot(el, data, this.layout)
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
                instance.get("filas/")
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