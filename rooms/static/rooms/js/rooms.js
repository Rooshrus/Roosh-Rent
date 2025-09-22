// rooms.js - ініціалізація карти та hover синхронізація
document.addEventListener('DOMContentLoaded', function(){
    var mymap = L.map('mapid').setView([49.498077, 23.965648], 7);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19
    }).addTo(mymap);

    fetch('/roomsapi')
        .then(response => response.json())
        .then(rooms => {
            const markers = {};
            rooms.forEach(room => {
                const coords = [room.coordX, room.coordY];
                const content = `<a href="/rooms/${room.id}/" style="display:block"><img src="${room.image_url || room.picture}" style="width:150px;border-radius:8px;"><div style="margin-top:4px"><b>$${room.price}</b></div></a>`;
                const pop = L.popup({ closeOnClick: true }).setContent(content);
                const m = L.marker(coords).addTo(mymap).bindPopup(pop);
                m.bindTooltip('$' + room.price, { permanent: true });
                markers[room.id] = m;
            });

            const roos = document.querySelectorAll('.room.card');
            roos.forEach(el => {
                const id = el.dataset.id;
                if(!id) return;
                el.addEventListener('mouseover', () => {
                    const m = markers[id];
                    if(m){
                        mymap.flyTo(m.getLatLng(), 14);
                        m.openPopup();
                    }
                });
            });
        })
        .catch(err => console.error(err));
});
