app = angular.module('zeitnow', []);

app.controller('ZeitNowCtrl', function($scope) {

	$scope.openChannel = function() {
		$.ajax({
			type: 'POST',
			url: '/api/channel?client_id=' + $scope.getClientId(),
			success: function(data) {
				token = JSON.parse(data).channel;
				channel = new goog.appengine.Channel(token);
				socket = channel.open();
				socket.onmessage = $scope.onMessage;
				socket.onclose = $scope.onClose;
			}
		});
	}

	$scope.getClientId = function(){
		if (window.localStorage.getItem('client_id')===null) {
			var random = (Math.random() + '').slice(2)
			window.localStorage.setItem('client_id',random);
			return random;
		} else {
			return window.localStorage.getItem('client_id');
		}
	}

	$scope.onMessage = function(msg) {
		$scope.stories = JSON.parse(msg.data);
		$scope.$apply();
		$scope.timestampUpdater();
		$('.progress').hide();
	};

	$scope.onClose = function(msg) {
		window.localStorage.clear('client_id');
		$scope.openChannel();
	};

	$scope.timestampUpdater = function() {
		$('i[data-time]').each(function(){
			var timestamp = $(this).attr('data-time');
			var timeago = moment(timestamp).fromNow();
			$(this).text(timeago);
		})
	};

	$scope.progressUpdater = function(times, interval) {
		var ID = setInterval(function(times) {
			return function() {
				if (--times <= 0) {
					clearInterval(ID);	
				}
				$scope.progress = 100-times;
				$scope.$apply();
			}
		}(times), interval);
	};

	var init = (function() {
		moment.lang('de');
		$scope.progressUpdater(100, 30);
		$scope.openChannel();
		setInterval($scope.timestampUpdater, 60000);
	})();

});