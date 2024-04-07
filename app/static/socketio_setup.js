var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('disconnect', function() {
    console.log('Disconnected from server');
});
