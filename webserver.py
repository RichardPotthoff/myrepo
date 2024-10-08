from http.server import BaseHTTPRequestHandler, HTTPServer
import time

hostName = "localhost"
serverPort = 8080

class MyServer_(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))
        
sketch_min_js="""/* Copyright (C) 2013 Justin Windle, http://soulwire.co.uk */
!function(e,t){"object"==typeof exports?module.exports=t(e,e.document):"function"==typeof define&&define.amd?define(function(){return t(e,e.document)}):e.Sketch=t(e,e.document)}("undefined"!=typeof window?window:this,function(e,t){"use strict";function n(e){return"[object Array]"==Object.prototype.toString.call(e)}function o(e){return"function"==typeof e}function r(e){return"number"==typeof e}function i(e){return"string"==typeof e}function u(e){return C[e]||String.fromCharCode(e)}function a(e,t,n){for(var o in t)!n&&o in e||(e[o]=t[o]);return e}function c(e,t){return function(){e.apply(t,arguments)}}function l(e){var t={};for(var n in e)"webkitMovementX"!==n&&"webkitMovementY"!==n&&(o(e[n])?t[n]=c(e[n],e):t[n]=e[n]);return t}function s(e){function t(t){o(t)&&t.apply(e,[].splice.call(arguments,1))}function n(e){for(_=0;_<ee.length;_++)B=ee[_],i(B)?S[(e?"add":"remove")+"EventListener"].call(S,B,N,!1):o(B)?N=B:S=B}function r(){I(A),A=R(r),K||(t(e.setup),K=o(e.setup)),U||(t(e.resize),U=o(e.resize)),e.running&&!q&&(e.dt=(z=+new Date)-e.now,e.millis+=e.dt,e.now=z,t(e.update),Z&&(e.retina&&(e.save(),e.autoclear&&e.scale(V,V)),e.autoclear&&e.clear()),t(e.draw),Z&&e.retina&&e.restore()),q=++q%e.interval}function c(){S=J?e.style:e.canvas,D=J?"px":"",Y=e.width,j=e.height,e.fullscreen&&(j=e.height=v.innerHeight,Y=e.width=v.innerWidth),e.retina&&Z&&V&&(S.style.height=j+"px",S.style.width=Y+"px",Y*=V,j*=V),S.height!==j&&(S.height=j+D),S.width!==Y&&(S.width=Y+D),Z&&!e.autoclear&&e.retina&&e.scale(V,V),K&&t(e.resize)}function s(e,t){return L=t.getBoundingClientRect(),e.x=e.pageX-L.left-(v.scrollX||v.pageXOffset),e.y=e.pageY-L.top-(v.scrollY||v.pageYOffset),e}function f(t,n){return s(t,e.element),n=n||{},n.ox=n.x||t.x,n.oy=n.y||t.y,n.x=t.x,n.y=t.y,n.dx=n.x-n.ox,n.dy=n.y-n.oy,n}function d(e){if(e.preventDefault(),G=l(e),G.originalEvent=e,G.touches)for(Q.length=G.touches.length,_=0;_<G.touches.length;_++)Q[_]=f(G.touches[_],Q[_]);else Q.length=0,Q[0]=f(G,$);return a($,Q[0],!0),G}function p(n){for(n=d(n),M=(X=ee.indexOf(W=n.type))-1,e.dragging=!!/down|start/.test(W)||!/up|end/.test(W)&&e.dragging;M;)i(ee[M])?t(e[ee[M--]],n):i(ee[X])?t(e[ee[X++]],n):M=0}function g(n){F=n.keyCode,H="keyup"==n.type,te[F]=te[u(F)]=!H,t(e[n.type],n)}function m(n){e.autopause&&("blur"==n.type?E:y)(),t(e[n.type],n)}function y(){e.now=+new Date,e.running=!0}function E(){e.running=!1}function k(){(e.running?E:y)()}function P(){Z&&e.clearRect(0,0,e.width*V,e.height*V)}function T(){O=e.element.parentNode,_=b.indexOf(e),O&&O.removeChild(e.element),~_&&b.splice(_,1),n(!1),E()}var A,N,S,O,L,_,D,z,B,G,W,F,H,M,X,Y,j,q=0,Q=[],U=!1,K=!1,V=v.devicePixelRatio||1,J=e.type==w,Z=e.type==h,$={x:0,y:0,ox:0,oy:0,dx:0,dy:0},ee=[e.eventTarget||e.element,p,"mousedown","touchstart",p,"mousemove","touchmove",p,"mouseup","touchend",p,"click",p,"mouseout",p,"mouseover",x,g,"keydown","keyup",v,m,"focus","blur",c,"resize"],te={};for(F in C)te[C[F]]=!1;return a(e,{touches:Q,mouse:$,keys:te,dragging:!1,running:!1,millis:0,now:NaN,dt:NaN,destroy:T,toggle:k,clear:P,start:y,stop:E}),b.push(e),e.autostart&&y(),n(!0),c(),r(),e}for(var f,d,p="E LN10 LN2 LOG2E LOG10E PI SQRT1_2 SQRT2 abs acos asin atan ceil cos exp floor log round sin sqrt tan atan2 pow max min".split(" "),g="__hasSketch",m=Math,h="canvas",y="webgl",w="dom",x=t,v=e,b=[],E={fullscreen:!0,autostart:!0,autoclear:!0,autopause:!0,container:x.body,interval:1,globals:!0,retina:!1,type:h},C={8:"BACKSPACE",9:"TAB",13:"ENTER",16:"SHIFT",27:"ESCAPE",32:"SPACE",37:"LEFT",38:"UP",39:"RIGHT",40:"DOWN"},k={CANVAS:h,WEB_GL:y,WEBGL:y,DOM:w,instances:b,install:function(e){if(!e[g]){for(var t=0;t<p.length;t++)e[p[t]]=m[p[t]];a(e,{TWO_PI:2*m.PI,HALF_PI:m.PI/2,QUARTER_PI:m.PI/4,random:function(e,t){return n(e)?e[~~(m.random()*e.length)]:(r(t)||(t=e||1,e=0),e+m.random()*(t-e))},lerp:function(e,t,n){return e+n*(t-e)},map:function(e,t,n,o,r){return(e-t)/(n-t)*(r-o)+o}}),e[g]=!0}},create:function(e){return e=a(e||{},E),e.globals&&k.install(self),f=e.element=e.element||x.createElement(e.type===w?"div":"canvas"),d=e.context=e.context||function(){switch(e.type){case h:return f.getContext("2d",e);case y:return f.getContext("webgl",e)||f.getContext("experimental-webgl",e);case w:return f.canvas=f}}(),(e.container||x.body).appendChild(f),k.augment(d,e)},augment:function(e,t){return t=a(t||{},E),t.element=e.canvas||e,t.element.className+=" sketch",a(e,t,!0),s(e)}},P=["ms","moz","webkit","o"],T=self,A=0,N="AnimationFrame",S="request"+N,O="cancel"+N,R=T[S],I=T[O],L=0;L<P.length&&!R;L++)R=T[P[L]+"Request"+N],I=T[P[L]+"Cancel"+N];return T[S]=R=R||function(e){var t=+new Date,n=m.max(0,16-(t-A)),o=setTimeout(function(){e(t+n)},n);return A=t+n,o},T[O]=I=I||function(e){clearTimeout(e)},k});"""
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        content1=r"""<html>
    <head>
        <title>sketch.js &raquo; Basic Example</title>
        <link rel="stylesheet" href="css/example.css">
        <style type="text/css">
            html, body {
                background: #FFFFFF;// background: #F51E50;
            }
        </style>
    </head>
    <body>
        <div id="container"></div>
        <header class="info">
            <hgroup class="about">
                <h1>sketch.js &rsaquo; basic</h1>
                <h2>A minimal example of how to use sketch.js</h2>
                <h3>Start drawing!</h3>
            </hgroup>
            <nav class="more">
                <a href="https://github.com/soulwire/sketch.js/archive/master.zip" target="_blank">Download</a>
                <a href="https://github.com/soulwire/sketch.js" target="_blank">View on Github</a>
            </nav>
        </header>
        <script>"""
        content2="""</script>
        <script>

        //var COLOURS = [ '#E3EB64', '#A7EBCA', '#FFFFFF', '#D8EBA7', '#868E80' ];
        var COLOURS = [ '#ff0000', '#00ff00', '#0000FF', '#ffff00', '#00ffff', '#ff00ff','#000000'];
        var radius = 0;

        var mySketch=Sketch.create({

            container: document.getElementById( 'container' ),
            autoclear: false,
            retina: 'auto',

            setup: function() {
                console.log( 'setup' );
                this.count = 0;
            },
            draw: function(){
              this.lineCap = 'round';
                  this.lineJoin = 'round';
                  this.fillStyle = '#00ff00';
                  this.strokeStyle = '#000000';
                  this.lineWidth = 5;

                 this.beginPath();
                this.moveTo(0,0);
                this.lineTo(100,100);
                this.stroke();
                this.font = "48px serif";
                this.strokeText(this.count, 10, 50);
                this.fillText(this.count, 10, 50);  
                this.count+=1;
            },
            update: function() {
                radius = 2 ;//+ abs( sin( this.millis * 0.003 ) * 50 );
            },

            // Event handlers

            keydown: function() {
                if ( this.keys.C ) this.clear();
            },

            // Mouse & touch events are merged, so handling touch events by default
            // and powering sketches using the touches array is recommended for easy
            // scalability. If you only need to handle the mouse / desktop browsers,
            // use the 0th touch element and you get wider device support for free.
            touchmove: function() {

                for ( var i = this.touches.length - 1, touch; i >= 0; i-- ) {

                    touch = this.touches[i];

                    this.lineCap = 'round';
                    this.lineJoin = 'round';
                    this.fillStyle = this.strokeStyle = COLOURS[ i % COLOURS.length ];
                    this.lineWidth = radius;

                    this.beginPath();
                    this.moveTo( touch.ox, touch.oy );
                    this.lineTo( touch.x, touch.y );
                    this.stroke();
                }
            }
        });
                  
        </script>
    </body></html>"""
        content=content1+sketch_min_js+content2
        self.wfile.write(bytes(content, "utf-8"))
        
  
if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
