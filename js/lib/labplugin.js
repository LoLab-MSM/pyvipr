var pyvipr = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'pyvipr',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'pyvipr',
          version: pyvipr.version,
          exports: pyvipr
      });
  },
  autoStart: true
};

