/**
 * Created by laotang on 17-5-2.
 */
/**
 * Created by Bella on 2017/4/24.
 */
    L.LocShare = {};
    var LS = L.LocShare;
    LS.Send = {};
    LS.Send.Marker = {};
    // LS.Send.Popup = L.popup().setContent(
    //     '<div style="width: 160px">' +
    //     '<div>' +
    //     '<p style="font-size:15px;font-weight:bold;">请把该标注移动到目的地点，再确定该地址！</p>' +
    //     '</div>' +
    //     '<div style="height:35px;">' +
    //     '<input type="button" value=确定 style="border-style:solid;border-radius:5px;border-color:#3d94f6;float:right;color:white;background-color:#3d94f6;height:20px;font-size:12px;line-height:3px;margin:5px;" onclick="copyPrompt()" />' +
    //     '</div>' +
    //     '</div>');

    var sendIcon = L.icon({
      iconUrl: "https://raw.githubusercontent.com/CliffCloud/Leaflet.LocationShare/master/dist/images/IconMapSend.png",
      iconSize:     [50, 50], // size of the icon
      iconAnchor:   [25, 50], // point of the icon which will correspond to marker's location
      popupAnchor:  [0, -30] // point from which the popup should open relative to the iconAnchor
    });


    L.Map.addInitHook(function () {
      this.sharelocationControl = new L.Control.ShareLocation();
      this.addControl(this.sharelocationControl);
    });

    L.Control.ShareLocation = L.Control.extend({
        options: {
            position: 'topleft',
            title: 'mark location'
        },

        onAdd: function () {
            var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control');

            this.link = L.DomUtil.create('a', 'leaflet-bar-part', container);
            this.link.title = this.options.title;
            var userIcon = L.DomUtil.create('img' , 'img-responsive' , this.link);
            userIcon.src = 'https://raw.githubusercontent.com/CliffCloud/Leaflet.LocationShare/master/dist/images/IconLocShare.png'
            this.link.href = '#';

            L.DomEvent.on(this.link, 'click', this._click, this);

            return container;
        },

        _click: function (e) {
          L.DomEvent.stopPropagation(e);
          L.DomEvent.preventDefault(e);
          placeMarker( this._map )
        }
    });


    // function copyPrompt() {
    //     document.getElementById("lnglat1").value=LS.Send.latlng;
    //     document.getElementById("lnglat").value=LS.Send.latlng;
    // }

    function placeMarker( selectedMap ){
    //  var test = LS.Send.Marker._latlng
    //  if ( isFinite(test.lat) && isFinite(test.lng) ){
        if (!LS.Send.Marker._latlng ) {
          console.log('if (!LS.Send.Marker._latlng ) { passed!  line 95');
          LS.Send.Marker = L.marker( selectedMap.getCenter() , {draggable: true,icon: sendIcon} );

          // setSendValues( selectedMap.getCenter() );

            // document.getElementById("lnglat1").value=selectedMap.getCenter();
            // document.getElementById("lnglat").value=selectedMap.getCenter();

          LS.Send.Marker.on('dragend', function(event) {
            // setSendValues( event.target.getLatLng());
              document.getElementById("lnglat1").value=event.target.getLatLng().lng +','+event.target.getLatLng().lat;
            document.getElementById("lnglat").value=event.target.getLatLng().lng +','+event.target.getLatLng().lat;
            // LS.Send.Marker.openPopup();
          });

          LS.Send.Marker.bindPopup(LS.Send.Popup);
          LS.Send.Marker.addTo(selectedMap);
        } else {
          LS.Send.Marker.setLatLng( selectedMap.getCenter() );
            // setSendValues( e.latlng );
            document.getElementById("lnglat1").value=e.latlng.lng+','+e.latlng.lat;
            document.getElementById("lnglat").value=e.latlng.lng+','+e.latlng.lat;
        }
        //selectedMap.setView( location , 16 )
        // LS.Send.Marker.openPopup();
    //  }
    }

        function placeMarker_z( e,selectedMap){
    //  var test = LS.Send.Marker._latlng
    //  if ( isFinite(test.lat) && isFinite(test.lng) ){
        if (!LS.Send.Marker._latlng) {
          LS.Send.Marker = L.marker( e.latlng , {draggable: true,icon: sendIcon} );

          // setSendValues( e.latlng );
            document.getElementById("lnglat1").value=e.latlng.lng+','+e.latlng.lat;
            document.getElementById("lnglat").value=e.latlng.lng+','+e.latlng.lat;

          LS.Send.Marker.on('dragend', function(event) {
            // setSendValues( event.target.getLatLng());
              document.getElementById("lnglat1").value=event.target.getLatLng().lng +','+event.target.getLatLng().lat;
            document.getElementById("lnglat").value=event.target.getLatLng().lng +','+event.target.getLatLng().lat;
            // LS.Send.Marker.openPopup();
          });

          // LS.Send.Marker.bindPopup(LS.Send.Popup);
          LS.Send.Marker.addTo(selectedMap);


        } else {
            // alert(LS.Send.Marker._latlng+"aaa");
          LS.Send.Marker.setLatLng( e.latlng );

          // setSendValues( e.latlng );

            document.getElementById("lnglat1").value=e.latlng.lng+','+e.latlng.lat;
            document.getElementById("lnglat").value=e.latlng.lng+','+e.latlng.lat;

        }

        // LS.Send.Marker.openPopup();
    //  }
    }


    // function setSendValues( result )
    // {
    //     if(result.lat){
    //         LS.Send.latlng = result.lat+","+result.lng;}
    //     else {
    //         LS.Send.latlng = result;
    //         }
    // }





