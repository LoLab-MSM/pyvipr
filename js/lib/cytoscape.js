const widgets = require('@jupyter-widgets/base');
const _ = require('lodash');
const cytoscape = require('cytoscape');
const tippy = require('tippy.js/dist/tippy.cjs').default;
const sticky = require('tippy.js/dist/tippy.cjs').sticky;
const popper = require('cytoscape-popper');
const coseBilkent = require('cytoscape-cose-bilkent');
const dagre = require('cytoscape-dagre');
const klay = require('cytoscape-klay');
const cola = require('cytoscape-cola');
const fcose = require('cytoscape-fcose');
const expandCollapse = require('cytoscape-expand-collapse');
const graphml = require('cytoscape-graphml');
const convert = require('sbgnml-to-cytoscape');
const SIFJS = require('./sif.js');
const sbgnStylesheet = require('cytoscape-sbgn-stylesheet');
const cxtmenu = require('cytoscape-cxtmenu');
const typeahead = require('typeahead.js');
const $ = require('jquery');
const semver_range = "^" + require("../package.json").version;
cytoscape.use(fcose);
cytoscape.use(cola);
cytoscape.use(popper);
cytoscape.use(coseBilkent);
cytoscape.use(dagre);
cytoscape.use(klay);
cytoscape.use( cxtmenu );
expandCollapse( cytoscape, $ ); // register extension
graphml( cytoscape, $ );

// Load CSS
require('./cytoscape.css');
require('./elements_style.css');

const DEF_BG = '#FFFFFF';
const DEF_LAYOUT = 'cose';
const DEF_HEIGHT = '700px';

const DEF_STYLE = [{
    selector: 'node',
    style: {
        'background-color': '#37474F',
        'label': 'data(id)',
        'width': 12,
        'height': 12,
        'color': '#333333',
        'font-weight': 400,
        'text-halign': 'right',
        'text-valign': 'bottom',
        'font-size': 16
    }
},
    {
        selector: 'node[background_color][shape]',
        style: {
            'background-color': 'data(background_color)',
            'shape': 'data(shape)',
            'label': 'data(label)',
            'border-color': 'data(border_color)',
            'border-width': 1
        }
    },
    {
        selector: ':parent',
        style: {
            'background-opacity': '0.5',
            'shape': 'data(shape)',
            'label': 'data(label)',
            'border-color': 'data(border_color)'
        }
    },
    {
        selector: 'edge',
        style: {
            'width': 1,
            'line-color': '#37474F',
            'target-arrow-color': '#37474F',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier'
        }
    },
    {
        selector: 'edge[line_style][line_color]',
        style: {
            'line-color': 'data(line_color)',
            'line-style': 'data(line_style)',
            'target-arrow-shape': 'data(target_arrow_shape)',
            'source-arrow-shape': 'data(source_arrow_shape)',
            'curve-style': 'bezier'
        }
    },
    {
        selector: '.faded',
        style: {
            'opacity': 0.25,
            'text-opacity': 0
        }
    },
];

const DEF_MODELS_STYLE = [
    {
        selector: 'node[shape]',
        style: {
            'label': 'data(label)',
            'shape': 'data(shape)',
            'pie-size': '80%',
            'pie-1-background-color': 'data(background_color)',
            'pie-1-background-size': '100',
            'pie-2-background-color': '#dddcd4',
            'pie-2-background-size': '100'
        }
    },
    {
        selector: 'node[highlight_nodes]',
        style: {
            'border-width': 'data(border_width)',
            'border-color': 'data(border_color)'
        }
    },
    {

        selector: 'edge',
        style: {
            'curve-style': 'bezier',
            'target-arrow-shape': 'data(target_arrow_shape)',
            'source-arrow-shape': 'data(source_arrow_shape)',
            'source-arrow-fill': 'data(source_arrow_fill)'
        }
    },
    {

        selector: 'edge[target_arrow_fill]',
        style: {
            'curve-style': 'bezier',
            'target-arrow-shape': 'data(target_arrow_shape)',
            'source-arrow-shape': 'data(source_arrow_shape)',
            'source-arrow-fill': 'data(source_arrow_fill)',
            'target-arrow-fill': 'data(target_arrow_fill)',
        }
    },
    {

        selector: 'edge[highlight_edges]',
        style: {
            'line-color': 'data(line_color)',
        }
    },
    {
        selector: ':parent',
        style: {
            'background-opacity': '0.5',
            'shape': 'rectangle',
            'label': 'data(id)',
            'border-color': '#000000'
        }
    },
    {
        selector:'node.cy-expand-collapse-collapsed-node',
        style: {
            'label': 'data(label)',
            'text-wrap': 'wrap',
            'background-color': 'darkblue',
            'shape': 'rectangle'
        }
    },
    {
        selector: '.faded',
        style: {
            'opacity': 0.25,
            'text-opacity': 0
        }
    },
    {
        selector:'edge.edges_expanded_collapsed',
        style: {
            'curve-style': 'unbundled-bezier',
            'control-point-distances': '0 0 0'
        }
    },
];

// Cytoscape Model. Custom widgets models must at least provide default values
// for model attributes, including
//
//  - `_view_name`
//  - `_view_module`
//  - `_view_module_version`
//
//  - `_model_name`
//  - `_model_module`
//  - `_model_module_version`
//
//  when different from the base class.

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
let CytoscapeModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name: 'CytoscapeModel',
        _view_name: 'CytoscapeView',
        _model_module: 'pyvipr',
        _view_module: 'pyvipr',
        _model_module_version: semver_range,
        _view_module_version: semver_range
    })
});

// Custom View. Renders the widget model.
let CytoscapeView = widgets.DOMWidgetView.extend({
    callback_process:function(formElement){
        this.model.set({'process':formElement});  // update the JS model with the current view value
        this.touch();   // sync the JS model with the Python backend
        this.$loader.removeClass('hide-loader');
    },

    callback_sim:function(formElement){
        this.model.set({'sim_idx':formElement});  // update the JS model with the current view value
        this.touch();  // sync the JS model with the Python backend
        this.$loader.removeClass('hide-loader');
    },

    render: function() {
        let vizType = this.model.get('type_of_viz');
        if (vizType.startsWith("dynamic") === true) {
            this.displayed.then(_.bind(this.loadData, this)).then(_.bind(this.renderButtons, this))
                .then(_.bind(this.value_changed, this)).then(_.bind(this.setupDynamics, this))
                .then(_.bind(this.cyDynamics, this));

            this.model.on('change:data', this.process_sim_changed, this);
        }
        else{
            this.displayed.then(_.bind(this.loadData, this)).then(_.bind(this.renderButtons, this))
                .then(_.bind(this.value_changed, this));
        }
    },

    value_changed: function() {
        let background = this.model.get('background');
        const layoutModel = this.model.get('layout');
        let cellHeight = layoutModel.attributes.height;

        if (!background) {
            background = DEF_BG
        }
        if (!cellHeight) {
            cellHeight = DEF_HEIGHT
        }

        this.el.classList.add('cytoscape-widget');
        this.el.id = 'cyjs';
        this.$el.css({
            background: background,
            height: cellHeight
        });
        this.displayed.then(_.bind(this.renderCy, this));
    },

    checkPositions: function(elements) {

        const nodes = elements.nodes;
        if (!nodes) {
            return false
        }

        const firstNode = nodes[0];

        if (!firstNode) {
            return false
        }

        if (firstNode.position) {
            return true
        }
    },

    renderButtons: function(){
        let that = this;
        // Layout options
        that.$layoutDd = $(
            "<select class=\"select-css\" id=\"layoutList\" ><optgroup label=\"Layouts available\"></select>");

        let layouts = ["cose-bilkent", "dagre", "klay", "cola", "random", "grid", "circle",
            "concentric", "breadthfirst", "cose", "fcose"];
        $.each(layouts, function(index, value){
            that.$layoutDd.append($("<option></option>")
                .attr("value", value)
                .text(value));
        });
        // Download options
        that.$downloadButton = $(
            "<select class=\"select-css\" id=\"dbutton\" >" +
            "<option value=\"\" disabled selected value>Download</option>" +
            "<option value=\"png\">png</option>" +
            "<option value=\"sif\">sif</option>" +
            "<option value=\"graphml\">graphml</option>" +
            "<option value=\"json\">json</option>" +
            "</select>");

        // Model title
        that.$model_title = $("<h1></h1>")
            .css({'font-size': '16px', 'margin-top': '10px'});

        that.$pyvipr = $("<h1>PyViPR</h1>")
            .css({'font-size': '1.3em', 'color': 'gray', 'margin': '0',
                'font-family': "\'Lucida console\', Lucida, monospace", 'font-weight': 'bold'});

        that.$title = $("<div id='title'></div>")
            .append(that.$model_title);

        that.$pyviprdiv = $("<div id='pyviprid'></div>")
            .append(that.$pyvipr);

        // Searchbox elements
        that.$search = $("<input type=\"text\" class=\"form-control\" id=\"search\" placeholder=\"Search..\">");

        that.$search_wrapper = $("<div id='searchDiv'></div>")
            .append(that.$search);

        that.$info = $("<div id='info'></div>")
            .css({'color': 'black'})

        // Fit button to fit network to cell space
        that.$fitButton = $("<button id='fitbuttonid'><i class=\"fa fa-arrows-h\"></i></button>");

        // Controls section
        that.$ControlSection = $("<div id='controlid'></div>")
            .css({
                "width": "100%",
                "height": "5em",
                "border": "medium solid grey",
                "border-radius": "10px",
                "background-color": "#FFFFFF",
                "position": "relative",
                "bottom": "700px"
            })
            .append(that.$downloadButton)
            .append(that.$fitButton)
            .append(that.$info)
            .append(that.$search_wrapper)
            .append(that.$title)
            .append(that.$layoutDd)
            .append(that.$pyviprdiv)
            .appendTo(that.el.parentElement);

        // Add elements for control of dynamic visualization
        let vizType = that.model.get('type_of_viz');
        if (vizType.startsWith("dynamic") === true) {
            that.$loader = $("<div class='loader hide-loader' id='loader'> </div>")
                .appendTo(that.$ControlSection);

            that.$nsimb = $(
                "<select class =\"select-css\" id=\"simLis\" ><optgroup label=\"Simulation #\"></select>")
                .appendTo(that.$ControlSection);

            let nsims = that.networkData.data.nsims;
            let sim_idx = that.model.get('sim_idx');
            for (let idx = 0; idx < nsims; idx++) {
                that.$nsimb.append($("<option></option>")
                    .attr("value", idx)
                    .text(idx));
            }
            that.$nsimb.val(sim_idx);

            let process = that.model.get('process');
            if (process === 'json_process'){
                let json_process = that.networkData.data.process;
                that.$processid = $(
                    "<select class =\"select-css\" id=\"myprocesses\" >\n" +
                    "<optgroup label=\"Process\">\n" +
                    "  <option value='" + json_process + "'>" + json_process + "</option>\n" +
                    "</select>\n")
                    .appendTo(that.$ControlSection);
            }
            else{
                let processes = ['consumption', 'production'];
                let unusedprocess = processes.filter(function (e) {
                    return e !== process
                });
                that.$processid = $(
                    "<select class =\"select-css\" id=\"myprocesses\" >\n" +
                    "<optgroup label=\"Process\">\n" +
                    "  <option value='" + process + "'>" + process + "</option>\n" +
                    "  <option value='" + unusedprocess[0] + "'>" + unusedprocess[0] + "</option>\n" +
                    "</select>\n")
                    .appendTo(that.$ControlSection);
            }

            // Defining player buttons
            that.$playButton = $("<button id='dbutton'><i class=\"fa fa-play\"></i></button>")
                .css({
                    "position": "absolute",
                    "width": "30px",
                    "height": "25px",
                    "top": "25%",
                    "border": "none",
                    "background": "#fffffff7",
                    "left": "0"
                });

            that.$slider = $('<input type="range" value="0" min="0" max="50" step="1" id="sliderid">')
                .css({
                    "width": "100%",
                    "height": "25px",
                    "top": "0%",
                    "position": "absolute",
                    "border": "none"
                });

            that.$slider_text = $($('<input type="text" size="400" value="0" id="textid">'))
                .css({
                    "width": "50px",
                    "height": "25px",
                    "top": "36%",
                    "left": "110px",
                    "position": "absolute",
                    "border": "none"
                });

            that.$resetButton = $("<button id='dbutton'><i class=\"fa fa-refresh\"></i>'</button>")
                .css({
                    "width": "30px",
                    "height": "25px",
                    "top": "25%",
                    "left": "50px",
                    "position": "absolute",
                    "border": "none"
                });

            that.$playerSection = $("<div id='playerid'></div>")
                .css({
                    "width": "100%",
                    "height": "50px",
                    "bottom": "0px",
                    "position": "relative",
                    "background-color": "white"
                })
                .append(that.$playButton)
                .append(that.$slider)
                .append(that.$slider_text)
                .append(that.$resetButton)
                .appendTo(that.el.parentElement);
        }

    },

    cyObj: null,

    networkData: null,

    loadData: function(){
        this.networkData = this.model.get('data');
    },

    process_sim_changed: function(){
        let that = this;
        let cy = this.cyObj;
        this.displayed.then(_.bind(this.loadData, this)).then(function(){cy.elements().stop(true, false)})
            .then(_.bind(this.cyDynamics, this))
            .then(function(){that.$loader.addClass('hide-loader');});
    },

    setupDynamics: function(){
        let that = this;
        let cy = this.cyObj;

        that.$processid.on('change', function(){
            that.callback_process(this.value)
        });

        that.$nsimb.on("change", function(){
            that.callback_sim(parseInt(this.value))
        });

        // Make tip function
//         let makeTippy = function(target, text){
//             return tippy( target.popperRef(), {
//                 content: (function(){
//                     let div = document.createElement('div');
//                     div.innerHTML = text;
//                     return div;
//                 })(),
//                 // appendTo: that.el,
// //                        offset: '0, 450',
//                 trigger: 'manual',
//                 arrow: true,
//                 placement: 'bottom',
//                 hideOnClick: false,
//                 interactive: true,
//                 multiple: true,
//                 sticky: true
//             } );
//         };

    },

    cyDynamics: function(){
        let that = this;
        let cy = this.cyObj;
        let network = this.networkData;

        let compound_nodes_names = ["community", "compartment"];

        that.$resetButton.off('click');
        that.$playButton.off('click');
        that.$slider.off('mouseup');

        let tspan = network.data.tspan;
        that.$slider.attr({"max": tspan.length - 1});
        // start slider, time text and animation always at 0 and expand nodes nodes
        let api = cy.expandCollapse('get');
        api.expandAll();
        let playing = false;
        let currentTime = 0;
        that.$playButton.html('<i class="fa fa-play"></i>');
        animateAllEles(currentTime, true);

        function animateAll(ele, data){
            let animationDuration = 1000;
            let animationQueue = [];
            if (ele.isEdge()){
                let edgeColor = data.edge_color;
                let edgeSize = data.edge_size;
                for (let idx = 0; idx < edgeColor.length; idx++){
                    let color = edgeColor[idx];
                    let size = edgeSize[idx];
                    animationQueue.push(ele.animation({
                        style:{
                            'line-color': color,
                            'target-arrow-color': color,
                            'source-arrow-color': color,
                            'width': size
                        },
                        duration: animationDuration
                    }));
                    ele.style(
                        {
                            'line-color': color,
                            'target-arrow-color': color,
                            'source-arrow-color': color,
                            'width': size
                        }
                    )
                }
            }
            else {
                let nodeRelValue = data.rel_value;
                for (let idx = 0; idx < nodeRelValue.length; idx++){
                    let value = nodeRelValue[idx];
                    animationQueue.push(ele.animation({
                        style:{
                            'pie-1-background-size': value
                        },
                        duration: animationDuration
                    }));
                    ele.style(
                        {
                            'pie-1-background-size': value
                        }
                    )
                }
            }

            return animationQueue;
        }

        function animateAllEles(time, onetime){
            let playQueue = function(ele, queue, position){
                if (position < queue.length){
                    if (ele.hasOwnProperty('tippy')){
                        let qtip = ele.data('qtip')[position];
                        ele.tippy.setContent(qtip.toExponential(2).toString());
                    }
                    currentTime = position;
                    that.$slider.val(currentTime);
                    that.$slider_text.val(tspan[currentTime].toFixed(2));
                    if (onetime === true){
                        queue[position].play();
                    }
                    else {
                        queue[position].play().promise('complete').then(() => {
                            playQueue(ele, queue, position + 1);
                        });
                    }

                } else {
                    //    stop animation
                    cy.elements().stop(false, false);
                }
            };

            cy.edges().forEach(function(edge){
                let source;
                let target;
                let gSource;
                let gTarget;
                if (edge.hasClass('cy-expand-collapse-meta-edge')){
                    source = edge.data('originalEnds').source.data('name');
                    target = edge.data('originalEnds').target.data('name');
                }
                else {
                    source = edge.data('source');
                    target = edge.data('target');
                }

                let ele = network.elements.edges.filter(function (e) {
                    if (e.data.hasOwnProperty('originalEnds')){
                        gSource = e.data.originalEnds.source.attr('name');
                        gTarget = e.data.originalEnds.target.attr('name');
                    }
                    else {
                        gSource = e.data.source;
                        gTarget = e.data.target;
                    }

                    return gSource === source && gTarget === target
                });
                let animationQueueEdges = animateAll(edge, ele[0].data);
                playQueue(edge, animationQueueEdges, time);


            });
            network.elements.nodes.forEach(function(node){
                let dNode = cy.filter("node[name=" + "\""+node.data.name+"\"" +"]");
                let is_compound = compound_nodes_names.includes(node.data.NodeType);
                if (!is_compound && dNode.length > 0){
                    let ele = cy.nodes().getElementById(node.data.id);
                    let animationQueueNodes = animateAll(ele, node.data);
                    playQueue(ele, animationQueueNodes, time)}
            })
        }
        // Show tip on tap
        let makeTippy = function(node, text){
            let ref = node.popperRef();
            // unfortunately, a dummy element must be passed
            // as tippy only accepts a dom element as the target
            // https://github.com/atomiks/tippyjs/issues/661
            let dummyDomEle = document.createElement('div');
            node.tippy = tippy( dummyDomEle, {
                getReferenceClientRect: ref.getBoundingClientRect,
                lazy: false, // mandatory
                trigger: 'manual', // mandatory
                // dom element inside the tippy:
                content: function(){ // function can be better for performance
                    let content = document.createElement('div');
                    content.innerHTML = text;
                    return content;
                },
                // your own preferences:
                arrow: true,
                placement: 'bottom',
                hideOnClick: false,
                multiple: true,
                sticky: true,
                plugins: [sticky]
            } );
        };

        cy.on('taphold', 'node[NodeType = "species"], edge',  function(evt){
            let ele = evt.target;
            let qtip = ele.data('qtip')[currentTime].toExponential(2).toString();

            if (ele.hasOwnProperty('tippy')){
                ele.tippy.destroy();
                delete ele.tippy;
            }
            else {
                makeTippy(ele, qtip);
                ele.tippy.show();
            }
        });

        cy.nodes().on("expandcollapse.beforecollapse", function(event) {
            pauseSlideshow();
        });

        cy.nodes().on("expandcollapse.beforeexpand", function(event) {
            pauseSlideshow();
        });

        //
        function pauseSlideshow(){
            that.$playButton.html('<i class="fa fa-play"></i>');
            playing = false;
            cy.elements().stop(false, false);
        }
        //
        function playSlideshow(){
            that.$playButton.html('<i class="fa fa-pause"></i>');
            playing = true;
            animateAllEles(currentTime, false);
        }
        //
        //
        that.$resetButton.on('click',function(){
            currentTime = 0;
            pauseSlideshow();
            animateAllEles(currentTime, true);

        });

        that.$playButton.on('click',function(){
            if(playing){ pauseSlideshow(); }
            else{ playSlideshow(); }
        });
        that.$slider.on('mouseup', function(){
            currentTime = this.value;
            currentTime = parseInt(currentTime);
            pauseSlideshow();
            animateAllEles(currentTime, true);

        });
    },

    renderCy: function() {
        // Remove tippy elements that might be present from previous run
        const tippies = document.getElementsByClassName("tippy-popper");
        while (tippies.length > 0) tippies[0].remove();
        let that = this;

        // Extract parameters
        // const data = that.model.get('data');
        let layoutArgs;
        let type_viz = that.model.get('type_of_viz');

        layoutArgs = {name: that.model.get('layout_name'), nodeDimensionsIncludeLabels: true};

        let network = that.networkData;
        let visualStyle = null;

        const vsParam = that.model.get('visual_style');
        if (vsParam) {
            // Override VS
            visualStyle = vsParam
        }

        if (!visualStyle) {
            visualStyle = DEF_STYLE;
        }

        if (!layoutArgs.name || typeof layoutArgs.name !== 'string') {
            if (this.checkPositions(network.elements)) {
                // This network has layout information
                layoutArgs = {name: 'preset'}
            } else {
                layoutArgs = {name: DEF_LAYOUT}
            }
        }

        let cy;
        let cy_json;
        let styleToUse;
        if (type_viz === 'graphml'){
            cy = cytoscape({
                container: that.el,
                style: DEF_STYLE,
                ready: function () {
                    this.graphml({layoutBy: 'cose'});
                    this.graphml(network);
                }

            })
        }
        else if (type_viz === 'sif'){
            styleToUse = DEF_STYLE;
            cy_json = SIFJS.parseCyjson(network);

        }
        else if (type_viz === 'sbgn_xml'){
            styleToUse = sbgnStylesheet(cytoscape);
            cy_json = convert(network);
        }
        else if (type_viz === 'network_static_view'){
            styleToUse = DEF_STYLE;
            cy_json = network.elements;
        }
        else if (type_viz === 'json' || type_viz === 'dynamic_json'){
            styleToUse = network.style;
            cy_json = network.elements
        }
        else{
            // pysb adds the file path to the model name. Here we removed the path info to only use the model name
            let name_spl = network.data.name.split(".");
            that.$model_title.text(name_spl[name_spl.length - 1]);
            cy_json = network.elements;

            styleToUse = network.data.style;
            if(styleToUse === 'sbgn') {
                styleToUse = sbgnStylesheet(cytoscape)
            }
            else if (styleToUse === 'atom'){
                styleToUse = DEF_STYLE
            }
            else {
                styleToUse = DEF_MODELS_STYLE
            }
        }
        if (type_viz !== 'graphml') {
            cy = cytoscape({
                container: that.el, // container to render in
                elements: cy_json,
                style: styleToUse,
                layout: layoutArgs
            });
        }
        this.cyObj = cy;
        // console.log(cy.elements().components()); this could be potentially used to find
        // disjoint subnetworks within a model network

        // Initialize Expand collapse compound nodes extension
        let api = cy.expandCollapse({undoable:false, animate:true, fisheye:false});
        // Initialize cytoscape-context-menu
        cy.cxtmenu({
            selector: 'node',

            commands: [
                {
                    content: 'Rename',
                    select: function(ele){
                        let new_name= prompt("New name", "my name");
                        ele.css({content: new_name});
                    }
                }
            ]
        });

        // Name community nodes with the highest degree node
        let communities = cy.nodes('[NodeType = "community"]');
        if (communities.nonempty()){
            that.expandButton = $("<button id='expandid'>Collapse nodes</button>")
                .css({
                    'position': 'absolute',
                    'right': '9.4em',
                    'top': '0',
                    'width': '9em',
                    'height': '1.8em',
                    'zIndex': '999',
                    'margin': '0.5em'
                })
                .on('click', function(){
                    let api_options = {
                        layoutBy: {
                            name: layoutArgs.name,
                            animate: "end",
                            randomize: false,
                            fit: true
                        },
                        fisheye: false,  // Fisheye doesn't work for expanding nodes when there is an animation playing
                        animate: true,
                        undoable: false
                    };
                    if (this.innerHTML === 'Collapse nodes') {
                        api.collapseAll(api_options);
                        this.innerHTML = 'Expand nodes'
                    }
                    else {
                        api.expandAll(api_options);
                        this.innerHTML = 'Collapse nodes'
                    }
                })
                .appendTo(that.$ControlSection);

            that.expandEdges = $("<button id='expandedgesid'>Collapse edges</button>")
                .css({
                    'position': 'absolute',
                    'right': '18.4em',
                    'top': '0',
                    'width': '9em',
                    'height': '1.8em',
                    'zIndex': '999',
                    'margin': '0.5em'
                })
                .on('click', function(){
                    let metaEdges = cy.elements(".cy-expand-collapse-meta-edge");
                    if (this.innerHTML === 'Collapse edges' && metaEdges.nonempty()) {
                        metaEdges.addClass("edges_expanded_collapsed");
                        this.innerHTML = 'Expand edges'
                    }
                    else {
                        cy.elements(".cy-expand-collapse-meta-edge").removeClass("edges_expanded_collapsed");
                        this.innerHTML = 'Collapse edges'
                    }
                })
                .appendTo(that.$ControlSection);
            communities.forEach(function(community){
                let node_degree = [];
                community.descendants().forEach(function(node){
                    node_degree.push([node, node.degree()])
                });
                node_degree.sort(function(a, b){return b[1]-a[1]});
                if (node_degree.length > 1) {
                    if (node_degree[0][1] === node_degree[1][1]) {
                        community.data('label', `${community.data('id')}: ${node_degree[0][0].data('label')} \n${node_degree[1][0].data('label')} regulation`)
                    }
                    else {community.data('label', community.data('id') +': ' +node_degree[0][0].data('label') + ' regulation')}
                }
                else {community.data('label', community.data('id') +': ' +node_degree[0][0].data('label') + ' regulation')}
            })
        }

        // Manually group selected species, rules, or reaction nodes
        let compartments_check = cy.nodes('[NodeType = "compartment"]').empty(),
            functions_check = cy.nodes('[NodeType = "function"]').empty(),
            modules_check = cy.nodes('[NodeType = "module"]').empty();

        if (compartments_check === true && functions_check === true
            && modules_check === true && communities.empty() === true){
            that.groupSelected = $("<button id='groupSel'>Group</button>")
                .css({
                    'position': 'absolute',
                    'right': '11em',
                    'top': '0',
                    'zIndex': '999',
                    'height': '1.8em',
                    'margin': '0.5em'
                })
                .on('click', function() {
                    let group_name = prompt("Group name", "Group 0");
                    let list = cy.$(':selected');
                    if (!list.filter(':parent').empty()) {
                        alert("It is not possible to group regular nodes with compound nodes")
                    }
                    if (group_name != null && list.filter(':parent').empty()){
                        let nodes = [];
                        nodes.push({group: "nodes", data: {id: group_name}, position: {x: 0, y: 0}});

                        // Create copies of old nodes
                        for (let i = list.size() - 1; i >= 0; i--) {
                            let node_info = list[i].json();
                            node_info["data"]["parent"] = group_name;
                            nodes.push(node_info);
                            let node_edges = list[i].connectedEdges();
                            for (let j = node_edges.size() - 1; j >= 0; j--) {
                                nodes.push(node_edges[j].json())
                            }
                        }
                        // Remove old nodes
                        list.remove();
                        // Add new nodes
                        cy.add(nodes);
                    }

                })
                .appendTo(that.$ControlSection)

        }

        function component_idx(data){
            let index;
            if (data.index){
                index = data.index;
            }
            else{
                index = data.id;
            }
            return index;
        }

        // Finds nodes with no edges in the following visualization views
        let vizCheckNoEdges = ['sp_view', 'sp_comp_view', 'sp_comm_louvain_view', 'sp_comm_louvain_hierarchy_view',
            'sp_comm_greedy_view', 'sp_comm_asyn_lpa_view', 'sp_comm_label_propagation_view',
            'sp_comm_girvan_newman_view', 'sp_comm_asyn_fluidc_view', 'sp_rxns_bidirectional_view', 'sp_rxns_view',
            'sp_rules_view', 'sp_rules_fxns_view', 'sp_rules_mod_view'];
        if (vizCheckNoEdges.includes(type_viz)){
            let sp_nodes = cy.nodes().filter(function(ele){
                return !(ele.isParent())
            });
            const nodesWithoutEdges = sp_nodes.filter(node => node.connectedEdges(":visible").size() === 0);
            if (nodesWithoutEdges.length > 0){
                let message = "The following components are not connected and will be highlighted in the graph:<br />";
                highlight(nodesWithoutEdges);
                let n_name;
                let n_id;
                nodesWithoutEdges.forEach(function(n){
                    n_name = n.data('label');
                    n_id = component_idx(n.data());
                    message += n_id + ": " + n_name + "<br />"
                });
                // Popup when nodes are not connected
                that.$close = $("<span id='close'>x</span>")
                    .css('float', 'right');
                that.$message = $("<p class=\"text\">" +
                    "        "+message+" " +
                    "    </p>" );

                that.$popup = $("<div class='fragment'>" +
                    "</div>")
                    .css({'border': '1px solid #ccc','background': '#FF7F7F',
                          'position': 'relative', 'bottom':'0', 'z-index': '999'})
                    .append(that.$close)
                    .append(that.$message)
                    .appendTo(that.el.parentElement);

                that.$close.on('click', function () {
                    this.parentNode.parentNode
                        .removeChild(this.parentNode);
                    return false;
                });
            }
        }


        // Adds feature, that when a node is tapped, it fades off all the
        // nodes that are not in its neighborhood
        function highlight(node){
            if (node.isParent()){
                // let layout = node.children().layout({
                //     name: 'grid',
                //     fit: 'false',
                //     boundingBox: node.parent().boundingBox(),
                //     nodeDimensionsIncludeLabels: true
                // });
                // layout.run();
                let children = node.children().add(node).add(node.ancestors());
                let children_edges = children.add(children.connectedEdges());
                cy.elements().addClass('faded');
                children_edges.removeClass('faded')
            }
            else {
                let neighborhood = node.closedNeighborhood().ancestors().add(node.closedNeighborhood());
                cy.elements().addClass('faded');
                neighborhood.removeClass('faded')
            }
        }

        function zoom(node){
            let node_to_fit;
            if (node.isParent()) {
                node_to_fit = node;
            } else {
                node_to_fit = node.neighborhood();
            }
            cy.stop();
            cy.animation({
                fit: {
                    eles: node_to_fit,
                    padding: layoutPadding
                },
                duration: aniDur,
                easing: easing
            }).play();
        }

        cy.on('boxselect', 'node', function(e){
            let node = e.target;
            zoom(node)

        });
        cy.on('tap', function(e){
            if (e.target === cy){
                cy.elements().removeClass('faded')
            }
        });

        let allNodes = cy.nodes();
        let layoutPadding = 30;
        let aniDur = 500;
        let easing = 'linear';
        that.$fitButton.on('click', function(){
            allNodes.unselect();
            cy.stop();
            cy.elements().removeClass('faded');
            cy.animation({
                fit: {
                    eles: cy.elements(),
                    padding: layoutPadding
                },
                duration: aniDur,
                easing: easing
            }).play();
        });
        let saveAs = function(data, name){
            let element = document.createElement('a');
            element.setAttribute('href', data);
            element.setAttribute('download', name);
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        };
        that.$downloadButton.on('change', function(){
            if (this.value === 'png') {
                let pngTxt = cy.png({'scale': 2, 'output': 'blob'});
                let blob = new Blob([pngTxt], {
                    type: "image/png"
                });
                let blobUrl = URL.createObjectURL(blob);
                saveAs(blobUrl, 'graph.png');
            }
            if (this.value === 'sif') {
                let sif = [];
                cy.edges().forEach(function( ele ){
                    sif.push(ele.source().id() + '\t' + ele.data('type') + '\t' + ele.target().id());
                });
                let sifTxt = sif.join('\n');
                // console.log(sifTxt);
                let blob = new Blob([sifTxt], {
                    type: "text/plain;charset=utf-8;"
                });
                let blobUrl = URL.createObjectURL(blob);
                saveAs(blobUrl, 'graph.sif');
                URL.revokeObjectURL(blobUrl);

            }
            if (this.value === 'graphml') {
                let blob = new Blob([cy.graphml()], {type: "text/plain;charset=utf-8;"});
                let blobUrl = URL.createObjectURL(blob);
                saveAs(blobUrl, 'graph.graphml');
                URL.revokeObjectURL(blobUrl);
            }
            if (this.value === 'json') {
                if (type_viz.startsWith("dynamic") === true){
                    let nsim_process = {nsims: network.data.nsims, process: that.model.get('process'),
                        tspan: network.data.tspan};
                    cy.data(nsim_process);
                }
                let blob = new Blob([JSON.stringify(cy.json(), function(key, val){
                    if (key !== 'tip')
                        return val;
                })], {type: "text/plain;charset=utf-8;"});
                let blobUrl = URL.createObjectURL(blob);
                saveAs(blobUrl, 'graph.json');
                URL.revokeObjectURL(blobUrl);
            }
        });

        that.$layoutDd.val(layoutArgs.name);
        that.$layoutDd.on('change', function() {
            layoutArgs.name = this.value;
            let layout = cy.layout({
                name: layoutArgs.name,
                nodeDimensionsIncludeLabels: true,
            });
            layout.run();

        });
        // info.id = 'infoid';
        // that.el.parentElement.appendChild(info);

        let infoTemplate = function(data){
            let name;
            let index;
            // Double check if this if statement of the name is necessary
            if (data.label){
                name = data.label;
            }
            else{
                name = data.name;
            }
            index = component_idx(data);
            let template = ['<div class="tt-suggest-page"><p><strong>' + name + '</strong></p>',
                '<p><strong>' + '<i class="fa fa-list-ol"></i>' + ' ' + index + '</strong></p><div>',
                '<p><strong>' + '<i class="fa fa-id-card-o"></i>' + ' ' + data.NodeType + '</strong></p><div>'].join('');
            if (data.NodeType === 'species'){
                template = template.concat('<p><strong>' + '<i class="fa fa-bar-chart"></i>' + ' ' + data.spInitial + '</strong></p><div>')
            }
            else if (data.NodeType === 'reaction' || data.NodeType === 'rule'){
                template = template.concat(
                    '<p><strong>' + 'kf:' + ' ' + data.kf + '</strong></p><div>',
                    '<p><strong>' + 'kr:' + ' ' + data.kr + '</strong></p><div>'
                )
            }
            return template;
        };

        function showNodeInfo( node ){
            that.$info.html( infoTemplate( node.data() ) ).show();
        }

        function hideNodeInfo(){
            that.$info.hide();
        }

        cy.on('tap', function(){
            that.$search.blur();
        });

        cy.on('select unselect', 'node', _.debounce( function(){
            let node = cy.$('node:selected');

            if( node.nonempty() ){
                showNodeInfo( node );

                Promise.resolve().then(function(){
                    return highlight( node );
                });
            } else {
                hideNodeInfo();
                // clear();
            }

        }, 100 ) );

        let lastSearch = '';

        that.$search.typeahead({
                minLength: 1,
                highlight: true,
            },
            {
                display: 'label',
                name: 'search-dataset',
                limit: 10,
                source: function( query, cb ){
                    function matches( str, q ){
                        str = (str || '').toLowerCase();
                        q = (q || '').toLowerCase();

                        return str.match( q );
                    }

                    let fields = ['label', 'id', 'NodeType'];

                    function anyFieldMatches( n ){
                        for( let i = 0; i < fields.length; i++ ){
                            let f = fields[i];

                            if( matches( n.data(f), query ) ){
                                return true;
                            }
                        }

                        return false;
                    }

                    function getData(n){
                        let data = n.data();

                        return data;
                    }

                    function sortByName(n1, n2){
                        if( n1.data('name') < n2.data('name') ){
                            return -1;
                        } else if( n1.data('name') > n2.data('name') ){
                            return 1;
                        }

                        return 0;
                    }

                    let res = allNodes.stdFilter( anyFieldMatches ).sort( sortByName ).map( getData );

                    cb( res );
                },
                templates: {
                    suggestion: infoTemplate
                }
            }).on('typeahead:selected', function(e, entry, dataset){
            let n = cy.getElementById(entry.id);

            cy.batch(function(){
                allNodes.unselect();

                n.select();
            });

            showNodeInfo( n );
        }).on('keydown keypress keyup change', _.debounce(function(e){
            let thisSearch = that.$search.val();

            if( thisSearch !== lastSearch ){
                $('.tt-dropdown-menu').scrollTop(0);

                lastSearch = thisSearch;
            }
        }, 50));
    }

});


module.exports = {
    CytoscapeModel: CytoscapeModel,
    CytoscapeView: CytoscapeView
};