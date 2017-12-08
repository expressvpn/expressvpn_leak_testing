// Credits to https://github.com/diafygi/webrtc-ips for some of the below

// TODO: Use iceGatheringState to detect when this is done
// TODO: This isn't working on Safari11 unless "Enable Legacy WebRTC API" is enabled. Why not?

function get_browser() {
    var ua=navigator.userAgent,tem,M=ua.match(/(opera|chrome|safari|firefox|msie|trident(?=\/))\/?\s*(\d+)/i) || [];
    if(/trident/i.test(M[1])){
        tem=/\brv[ :]+(\d+)/g.exec(ua) || [];
        return {name:'IE',version:(tem[1]||'')};
        }
    if(M[1]==='Chrome'){
        tem=ua.match(/\bOPR|Edge\/(\d+)/)
        if(tem!=null)   {return {name:'Opera', version:tem[1]};}
        }
    M=M[2]? [M[1], M[2]]: [navigator.appName, navigator.appVersion, '-?'];
    if((tem=ua.match(/version\/(\d+)/i))!=null) {M.splice(1,1,tem[1]);}
    return {
      name: M[0],
      version: M[1]
    };
 }

function XvICE(divName) {
    this.divName = divName
    this.askPerms = false
    return this;
}

XvICE.prototype.setAskPerms = function(ask) {
    this.askPerms = ask
}

XvICE.prototype.browser = function() {
    var is_chrome = navigator.userAgent.indexOf('Chrome') > -1;
    var is_ie = navigator.userAgent.indexOf('MSIE') > -1;
    var is_firefox = navigator.userAgent.indexOf('Firefox') > -1;
    var is_safari = navigator.userAgent.indexOf("Safari") > -1;
    var is_opera = navigator.userAgent.toLowerCase().indexOf("op") > -1;
    if ((is_chrome) && (is_safari)) { is_safari=false; }
    if ((is_chrome) && (is_opera)) { is_chrome=false; }
    if (is_chrome) {
        return 'chrome'
    } else if (is_safari) {
        return 'safari'
    } else if (is_ie) {
        return 'ie'
    } else if (is_firefox) {
        return 'firefox'
    } else if (is_opera) {
        return 'opera'
    } else {
        return 'unknown'
    }
}

XvICE.prototype.run = function() {
    // Tempted to also check: this.browser() == 'safari') {
    if (this.askPerms) {
        xvice = this
        navigator.mediaDevices.getUserMedia({ audio: true, video: false }).then(function(_) {
            console.log("WebRTC permissions granted");
            xvice.doWebRTCCheck();
        }).catch(function(err) {
            console.log("WebRTC permissions denied");
            xvice.setWebRTCSupported(false);
        })
    } else {
        this.doWebRTCCheck();
    }
}

XvICE.prototype.setWebRTCSupported = function(supported) {
    div = $(this.divName)
    div.html(JSON.stringify({'webrtc_supported': supported}));
}

XvICE.prototype.doWebRTCCheck = function() {
    var rtcPeerConnectionClass = this.getRTCPeerConnection();
    if (typeof rtcPeerConnectionClass === 'undefined') {
        this.setWebRTCSupported(false)
        return;
    } else {
        this.setWebRTCSupported(true)
    }

    var mediaConstraints = {
        optional: [{ RtpDataChannels: true }]
    };

    // No domains means just do local IP search, which is what we want
    var servers = { iceServers: [
        // { urls: "stun:DOMAIN_HERE" }
        { urls: "stun:stun.l.google.com:19302?transport=udp"},
    ]};

    var rtcPeerConnection = new rtcPeerConnectionClass(servers, mediaConstraints);
    var ips = {};
    var div = $(this.divName)
    rtcPeerConnection.onicecandidate = function (ice) {
        if (ice.candidate) {
            var ip = ice.candidate.candidate.split(" ")[4];

            // Avoid duplicates
            if (ips[ip] === undefined) {

                var json = null;
                if (div.html() == "") {
                    json = {};
                } else {
                    json = JSON.parse(div.html());
                }
                if (!('ips' in json)) {
                    json['ips'] = []
                }

                json['ips'].push(ip);

                div.html(JSON.stringify(json));
            } else {
                // Curious to see if this happens
                console.log("Duplicate IP returned (and ignored): " + ip);
            }
            ips[ip] = true;
        }
    };

    if (typeof rtcPeerConnection.createDataChannel === 'function') {
        // Not defined on Edge. ICE doesn't seem to work on Edge anyway, but this at least
        // stops the js code from dying.
        rtcPeerConnection.createDataChannel("");
    }

    browser = get_browser();
    if (browser.name == 'Safari' && browser.version == 11)
    {
        rtcPeerConnection.createOffer({}).then(
            function(result) { rtcPeerConnection.setLocalDescription(result, function () { }, function () { }) },
            null)
    } else {
        rtcPeerConnection.createOffer(function (result) {
            rtcPeerConnection.setLocalDescription(result, function () { }, function () { });
        }, function () { });
    }
}

XvICE.prototype.getRTCPeerConnection = function() {
    var RTCPeerConnection = window.RTCPeerConnection
                  || window.mozRTCPeerConnection
                  || window.webkitRTCPeerConnection
                  || window.msRTCPeerConnection;

    if (!RTCPeerConnection) {
        var iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        document.body.appendChild(iframe);
        var win = iframe.contentWindow;
        window.RTCPeerConnection = win.RTCPeerConnection;
        window.mozRTCPeerConnection = win.mozRTCPeerConnection;
        window.webkitRTCPeerConnection = win.webkitRTCPeerConnection;
        window.msRTCPeerConnection = win.msRTCPeerConnection;

        RTCPeerConnection = window.RTCPeerConnection
            || window.mozRTCPeerConnection
            || window.webkitRTCPeerConnection
            || window.msRTCPeerConnection;
    }

    return RTCPeerConnection;
}
