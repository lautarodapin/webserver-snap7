const instance = axios.create({
    baseURL: `${window.location.protocol}//${window.location.host}/api/`,
    timeout: 10000,
}); 
const DB_NAME = "testDb"
const DB_VERSION = 2
let DB;

const app = Vue.createApp({
    delimiters: ["[[", "]]"],
    data(){
        return{
            db: null,
            ws: null,
            loading: false,
            progress: 0,
            searchFila: "",
            checkedFilas: [],
            plcs: [],
            areas: [],
            filas: [],
            // datosProcesados: [],
            data:[{
                x: [],
                y: [],
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
        async datosProcesados(){
            return await this.getDatos();
        },
    },
    methods:{
        async fetchData(){
            // await this.clearDatos();
            this.data[0].x = []
            this.data[0].y = []
            this.loading = true;
            this.ws.send(JSON.stringify({
                action: "list",
                request_id: new Date().getTime(),
                limit: 10000,
                filters:{
                    "fila_id__in": this.checkedFilas,
                },
            }))
        },
        async renderDatosProcesados(){
            // mountApp.datosProcesados.map(dato => dato.fila).filter((value, index, self) => self.indexOf(value) === index)
            // console.log(this.datosProcesados)
            // this.datosProcesados = JSON.parse(localStorage.getItem("datosProcesados"))
            // datosProcesados = await this.datosProcesados
            // const filas = datosProcesados
            //     .map(dato => dato.fila)
            //     .filter((value, index, self) => self.indexOf(value) === index)
            // // console.log(filas)
            // var data = []
            // for(var i = 0; i < filas.length; i++){
            //     var datosFiltrados = datosProcesados.filter(dato => dato.fila === filas[i])
            //     // console.log(datosFiltrados)
            //     var trace = {
            //         x: Array.from(datosFiltrados, dato => dato.date),//.split("T").join(" ").substring(0, dato.date.length - 1)), // "2020-01-01T00:02:00Z".split("T").join(" ").substring(0, "2020-01-01T00:02:00Z".length-1)
            //         y: Array.from(datosFiltrados, dato => dato.dato),
            //         type: "scatter",
            //         name: `${datosFiltrados[0].name}`,
            //     }
            //     if (i > 0){
            //         trace.xaxis = `x${i + 1}`; 
            //         trace.yaxis = `y${i + 1}`; 
            //     }
            //     data.push(trace)
            // }
            // var layout = {
            //     grid: {
            //         rows: filas.length,
            //         columns: 1,
            //         pattern: 'independent',
            //     }
            // }
            // // console.log(data)
            const el = this.$refs.plotlyEl
            Plotly.newPlot(el, this.data, this.layout)
            // this.data = data;
            // this.layout = layout;
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
        createWs(){
            var self = this;
            this.ws = new WebSocket("ws://localhost:8000/ws/dato-procesado/")
            this.ws.onopen = function(){

            }
            this.ws.onmessage = async function(e){
                const response = JSON.parse(e.data)
                // console.log(response)
                // for (i=0; i<response.data.results.length; i++){
                //     const datos = response.data.results[i]
                //     let data = await self.saveDato(datos)
                // }
                // await self.saveDatos(response.data.results)
                // let datos = await self.getDatos();
                self.data[0].x.push(...response.data.results.x)
                self.data[0].y.push(...response.data.results.y)
                var progress = response.data.offset + response.data.results.x.length;
                if (progress == response.data.count) {
                    self.loading = false;
                    return self.renderDatosProcesados();
                }
                self.progress = progress / response.data.count * 100
                // console.log(datos)
                // self.datosProcesados.push(...response.data.results)
            }
        },
        async getDb() {
            return new Promise((resolve, reject) => {
                if (DB) return resolve(DB);
                // console.log("OPENING DB", DB);
                let request = window.indexedDB.open(DB_NAME, DB_VERSION);
                request.onerror = e => {
                    // console.log('Error opening db', e);
                    reject('Error');
                };
                request.onsuccess = e => {
                    DB = e.target.result;
                    resolve(DB);
                };
                request.onupgradeneeded = e => {
                    // console.log('onupgradeneeded');
                    let db = e.target.result;
                    let objectStore = db.createObjectStore("datosProcesados", { autoIncrement: true, keyPath:'id' });
                };
            });
        },
        async getDatos(){
            let db = await this.getDb();
            return new Promise((resolve, reject) => {
                let transaction = db.transaction(["datosProcesados"], "readonly")
                transaction.oncomplete = () => resolve(datos)
                let store = transaction.objectStore("datosProcesados")
                let datos = []
                store.openCursor().onsuccess = e => {
                    let cursor = e.target.result;
                    if (cursor){
                        datos.push(cursor.value)
                        cursor.continue();
                    }
                }
            })
        },
        async saveDatos(datos){
            datos.forEach(dato =>  this.saveDato(dato))//.then(response => console.log("Saved dato", dato)))
        },
        async saveDato(dato){
            let db = await this.getDb();
            return new Promise((resolve, reject) => {
                let transaction = db.transaction(["datosProcesados"], "readwrite");
                transaction.oncomplete = () => {
                    resolve(dato)
                };
                let store = transaction.objectStore("datosProcesados")
                store.put(dato);
            })
        },
        async clearDatos(){
            let db = await this.getDb();
            return new Promise((resolve, reject) => {
                let transaction = db.transaction(["datosProcesados"], "readwrite")
                transaction.oncomplete = () => resolve();
                let objectStore = transaction.objectStore("datosProcesados")
                let request = objectStore.clear();
                request.onsuccess = (e) => resolve(e)
            })
        },
    },
    async created(){
        Promise.all([
            this.getFilas(),
        ])
        this.createWs();
        await this.getDb();

        
    },
    mounted(){
    }
});
const mountApp = app.mount("#app")