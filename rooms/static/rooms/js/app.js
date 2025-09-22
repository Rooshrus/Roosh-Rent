var roomAddress = document.querySelector("#address")

var addresses = document.querySelector("#addresses")

var address = document.querySelector("#id_address")
var coordX = document.querySelector("#id_coordX")
var coordY = document.querySelector("#id_coordY")


function showAddresses(){
    addresses.innerHTML = ""
    if (addressData.length > 0){
        addressData.forEach(address => {
            addressName = address.display_name.replace("'", "")
            addresses.innerHTML += `<div class='result' onclick='selectAddress(${address.lat}, ${address.lon}, "${addressName}")'>
                                ${address.display_name}</div>`;
        });
    }
}

function selectAddress(x, y ,adr){
    address.value = adr
    coordX.value = x
    coordY.value = y
    mymap.flyTo([x,y],16)
    marker.closePopup()
    marker.setLatLng([x,y])
    marker.closePopup()
}

function findAddresses() {
    var url = "https://nominatim.openstreetmap.org/search?format=json&limit=3&q=" + roomAddress.value
    fetch(url)
                  .then(response => response.json())
                  .then(data => addressData = data)
                  .then(show => showAddresses())
                  .catch(err => console.log(err))
}

//map
var mymap;
var marker;
window.onload = function () {
    mymap = L.map('mapid').setView([49.498077, 23.965648], 12);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mymap);

    marker = L.marker([49.498077, 23.965648]).addTo(mymap);
};