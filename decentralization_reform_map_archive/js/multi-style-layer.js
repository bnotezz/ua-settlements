var _____WB$wombat$assign$function_____ = function(name) {return (self._wb_wombat && self._wb_wombat.local_init && self._wb_wombat.local_init(name)) || self[name]; };
if (!self.__WB_pmw) { self.__WB_pmw = function(obj) { this.__WB_source = obj; return this; } }
{
  let window = _____WB$wombat$assign$function_____("window");
  let self = _____WB$wombat$assign$function_____("self");
  let document = _____WB$wombat$assign$function_____("document");
  let location = _____WB$wombat$assign$function_____("location");
  let top = _____WB$wombat$assign$function_____("top");
  let parent = _____WB$wombat$assign$function_____("parent");
  let frames = _____WB$wombat$assign$function_____("frames");
  let opener = _____WB$wombat$assign$function_____("opener");

!(function () {
    var yes = function () { return true; };

    L.GeoJSON.MultiStyle = L.GeoJSON.extend({
        options: {
            styles: [
                {color: 'black', opacity: 0.15, weight: 9},
                {color: 'white', opacity: 0.8, weight: 6},
                {color: '#444', opacity: 1, weight: 2}
            ],
            pointToLayer: function(feature, latlng) {
                return L.circleMarker(latlng, {radius: 0})
            },
            filters: [yes, yes, yes]
        },

        addData: function(data) {
            if (!this._isAdding) {
                this._isAdding = true;
                if (this.options.styles) {
                    var styler = this.options.style,
                        filter = this.options.filter;
                    this.options.styles.forEach(L.bind(function(style, i) {
                        this.options.style = style;
                        if (this.options.filters && this.options.filters[i]) {
                            this.options.filter = this.options.filters[i];
                        }
                        L.GeoJSON.prototype.addData.call(this, data);
                    }, this));
                }
                if (this.options.pointToLayers) {
                    this.options.pointToLayers.forEach(L.bind(function(pointToLayer, i) {
                        this.options.pointToLayer = pointToLayer;
                        if (this.options.filters && this.options.filters[i]) {
                            this.options.filter = this.options.filters[i];
                        }
                        L.GeoJSON.prototype.addData.call(this, data);
                    }, this));
                }
                this.options.style = styler;
                this.options.filter = filter;
                this._isAdding = false;
            } else {
                L.GeoJSON.prototype.addData.call(this, data);
            }
        }
    });

    L.geoJson.multiStyle = function(data, options) {
        return new L.GeoJSON.MultiStyle(data, options);
    }
})();


}
/*
     FILE ARCHIVED ON 04:13:17 Oct 07, 2021 AND RETRIEVED FROM THE
     INTERNET ARCHIVE ON 12:11:32 Jul 18, 2025.
     JAVASCRIPT APPENDED BY WAYBACK MACHINE, COPYRIGHT INTERNET ARCHIVE.

     ALL OTHER CONTENT MAY ALSO BE PROTECTED BY COPYRIGHT (17 U.S.C.
     SECTION 108(a)(3)).
*/
/*
playback timings (ms):
  captures_list: 0.771
  exclusion.robots: 0.025
  exclusion.robots.policy: 0.012
  esindex: 0.017
  cdx.remote: 14.123
  LoadShardBlock: 169.117 (3)
  PetaboxLoader3.datanode: 115.007 (4)
  PetaboxLoader3.resolve: 126.567 (2)
  load_resource: 82.838
*/