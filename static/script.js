
function animateMarker(el){
 el.style.opacity=0;
 el.style.transform='scale(0.6)';
 setTimeout(()=>{el.style.transition='0.4s'; el.style.opacity=1; el.style.transform='scale(1)';},10);
}

// marker management
let __markers = [];
function clearMarkers(){
  __markers.forEach(m=>{ map.removeLayer(m); });
  __markers = [];
}

function addMarkerFromPin(pin){
  const icon=L.divIcon({className:'heart-marker',html:`<div class="heart"></div>`});
  const marker=L.marker([pin.lat,pin.lng],{icon}).addTo(map);
  marker.on("add",()=>animateMarker(marker._icon));
  marker.bindPopup(`
    <div class="popup-container fade-in">
      <h3>${pin.name}</h3>
      <p><em>${pin.date||''}</em></p>
      ${pin.photo_filename?`<img class="popup-photo" src="/static/photos/${pin.photo_filename}">`:''}
      <p>${pin.description||''}</p>
    </div>
  `);
  __markers.push(marker);
}

async function loadPins(){
  try{
    const r = await fetch('/api/pins');
    const pins = await r.json();
    clearMarkers();
    pins.forEach(addMarkerFromPin);
  }catch(e){
    console.error('Failed to load pins', e);
  }
}

loadPins();

map.on("click",e=>{
  // fallback: fill admin inputs on admin page if present
  let lat=document.getElementById("lat");
  let lng=document.getElementById("lng");
  if(lat && lng){
    lat.value=e.latlng.lat.toFixed(6);
    lng.value=e.latlng.lng.toFixed(6);
    // gentle non-blocking hint
    const hint = document.createElement('div');
    hint.textContent = 'Coordinates filled in admin form';
    hint.style.position='fixed'; hint.style.right='18px'; hint.style.bottom='18px';
    hint.style.background='rgba(255,255,255,0.95)'; hint.style.padding='8px 12px'; hint.style.borderRadius='10px';
    document.body.appendChild(hint);
    setTimeout(()=>hint.remove(),1800);
  }
});
// Note: admin page contains its own picker modal and JS for submitting pins from there.
