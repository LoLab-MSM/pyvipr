var viz-pysb-widget = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'viz-pysb-widget',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'viz-pysb-widget',
          version: viz-pysb-widget.version,
          exports: viz-pysb-widget
      });
  },
  autoStart: true
};

