<script setup>
//import { RouterLink, RouterView } from 'vue-router'
import Button from 'primevue/button';
import { PrimeIcons } from "primevue/api";
import 'primeicons/primeicons.css';
import { ref, onMounted } from 'vue';
import {api} from 'C:/Users/mehme/OneDrive/Masaüstü/vue/vue-roll/src/axios.js';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup';   // optional
import Row from 'primevue/row';                   // optional
import Listbox from 'primevue/listbox';


onMounted(() => {
    rolls()
});


const cur_table = ref()
const rolls_list = ref()
const selectedRoll = ref()
const Roll = ref()
const paus = ref()

async function cont(){
  let res= await api.get("continue")
  console.log(res)
  paus.value =0
  curr()
}



async function curr(){
  while (true){
    if (paus.value == 0){
      await new Promise(r => setTimeout(r, 1000))
      cur_table.value = await api.get("curr")
      console.log(cur_table.value.data)
      for (let e in cur_table.value.data){
        cur_table.value.data[e].Image ="data:image/gif;base64," +(cur_table.value.data[e].Image)    
      }
      cur_table.value = cur_table.value.data
    }
    else{
      break
    }
  }
}


async function pau(){
  paus.value =1
  let res= await api.get("pause")
  console.log(res)
}

async function roll(){
  console.log(selectedRoll.value)
  Roll.value = await api.get("roll?Id="+selectedRoll.value)
  console.log(Roll.value.data)
  for (let e in Roll.value.data){
    //Roll.value.data[e].Image = atob(Roll.value.data[e].Image)
    // base64 to DATA URL
    Roll.value.data[e].Image ="data:image/gif;base64," +(Roll.value.data[e].Image)    
  }
  Roll.value = Roll.value.data
}

async function rolls(){
  rolls_list.value = await api.get("rolls")
  //console.log(rolls_list.value.data)
  for (let e in rolls_list.value.data){
    rolls_list.value.data[e].list = (rolls_list.value.data[e].Id + "-" + rolls_list.value.data[e].DateTime)
  }
  console.log(rolls_list.value.data)
  rolls_list.value = rolls_list.value.data
}


</script>

<template>
  <header>
    <h1 class="bas">Kusur Tespiti</h1>
    <div >
      <div class="current">
        <div class="img">
          <img src="http://127.0.0.1:5000/video"   alt="Başlatın">
        </div>
        <div class="buttons">
          <Button size="large" icon="pi pi-play" @click="cont">  </Button>
          <Button size="large" icon="pi pi-pause" @click="pau">  </Button>
        </div>
        <div class="cur_table">
          <h1>Şuan Bulunan Kusurlar</h1>
          <DataTable :value="cur_table"  paginator :rows="6" :rowsPerPageOptions="[6, 12, 18]" sortMode="multiple" showGridlines  tableStyle="min-width: 50rem">
            <Column field="Img" header="İmge">
              <template #body="slotProps">
                  <img :src="slotProps.data.Image" class="shadow-2 border-round" style="width: 128px; height: 128px;"  />
              </template>
            </Column>
            <Column field="Defect" header="Kusur"></Column>
            <Column field="DetSec" header="Saniye"></Column>
          </DataTable>
        </div>
      </div>
      <div class="log">
        <h1>Kayıtlara Gözat</h1>
        <div class="rolls"> 
          <h1>Kayıt Seç</h1>
          <Listbox v-model="selectedRoll" @click="roll" :options="rolls_list" listStyle="max-height:250px" filter optionLabel="list" optionValue="Id" class="w-full md:w-14rem" />
        </div>
        <div class="log_table">
          <h1>Seçilen Kayıt</h1>
          <DataTable :value="Roll"  paginator :rows="3" sortMode="multiple" showGridlines  tableStyle="min-width: 50rem">
            <Column header="İmge">
              <template #body="slotProps">
                  <img :src="slotProps.data.Image" class="shadow-2 border-round" style="width: 128px; height: 128px;"  />
              </template>
            </Column>
            <Column field="Defect" header="Kusur"></Column>
            <Column field="DetSec" header="Saniye"></Column>
          </DataTable>

        </div>


      </div>


      

    </div>
  </header>


</template>

<style scoped>

  div.rolls{
    margin-top: 5rem;
    position: fixed;
    left: 0;
    margin-left: 5rem;
  }

  div.log_table{
    margin-left: 10rem;
  }

  div.log{
    display: flex;
    position: fixed;
    left: 0;
    margin: 5px;

  }



  div.img{
    background-color: black;
    width: 1024px;
    height: 256px;
    object-fit: contain;
    margin: 10px;
  }

  div.current{
    display: flex;
    position: fixed;
    left: 0;
    top: 100px;
  }
  Button{
    width: 64px;
    height: 64px;
    object-fit: contain;
    margin: 10px;
  }

  div.cur_table{
    margin-left: 100px;
  }

  div.buttons{
    margin-top: 5rem;
    width: 50px;
    height: 256 px;
    object-fit: contain;
  }

  h1.bas{
    position: fixed;
    top: 0;
  }

  img {
    width: 1024px;
    height: 256px;
    border-radius: 35px;
    object-fit: contain;
  }

</style>
