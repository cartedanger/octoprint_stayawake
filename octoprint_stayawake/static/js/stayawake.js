$(function () {
  function StayAwakeSettingsViewModel(parameters) {
    var self = this;
    self.settingsViewModel = parameters[0];

    self.sendNowCommand = function () {
      OctoPrint.simpleApiCommand("stayawake", "send_now", {})
        .done(function () {
          if (window.PNotify) {
            new PNotify({
              title: "Stay Awake",
              text: "Command sent",
              type: "success"
            });
          }
        })
        .fail(function (xhr) {
          var message = "Unable to send command";
          if (xhr && xhr.responseJSON && xhr.responseJSON.error) {
            message = xhr.responseJSON.error;
          } else if (xhr && xhr.responseText) {
            message = xhr.responseText;
          } else if (xhr && xhr.status) {
            message = "Unable to send command (HTTP " + xhr.status + ")";
          }

          if (window.PNotify) {
            new PNotify({
              title: "Stay Awake",
              text: message,
              type: "error"
            });
          }
        });
    };
  }

  OCTOPRINT_VIEWMODELS.push({
    construct: StayAwakeSettingsViewModel,
    dependencies: ["settingsViewModel"],
    elements: ["#settings_plugin_stayawake"]
  });
});
