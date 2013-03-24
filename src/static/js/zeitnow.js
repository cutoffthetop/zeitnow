app = angular.module('zeitnow', []);

app.controller('ZeitNowCtrl', function($scope) {

	$.ajax({
		type: 'POST',
		url: '/api/channel?client_id=1234',
		success: function(data) {
			token = JSON.parse(data).channel;
			channel = new goog.appengine.Channel(token);
			socket = channel.open();
			socket.onmessage = $scope.onMessage;
		}
	});

	$scope.onMessage = function(msg) {
		$scope.stories = JSON.parse(msg.data);
		$scope.$apply();
	};

});
