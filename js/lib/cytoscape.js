var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var cytoscape = require('cytoscape');
var tippy = require('tippy.js');
var popper = require('cytoscape-popper');
var coseBilkent = require('cytoscape-cose-bilkent');
var dagre = require('cytoscape-dagre');
var klay = require('cytoscape-klay');
var expandCollapse = require('cytoscape-expand-collapse');
var typeahead = require('typeahead.js');
var $ = require('jquery');
var semver_range = "^" + require("../package.json").version;
cytoscape.use(popper);
cytoscape.use(coseBilkent);
cytoscape.use(dagre);
cytoscape.use(klay);
expandCollapse( cytoscape, $ ); // register extension

// Load CSS
require('./cytoscape.css');
require('./elements_style.css');

const FORMAT = {
    CX: 'cx',
    CYJS: 'cyjs',
    EDGELIST: 'el',
};

const DEF_BG = '#FFFFFF';
const DEF_LAYOUT = 'cose';
const DEF_HEIGHT = '500px';

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
        selector: 'edge',
        style: {
            'width': 1,
            'line-color': '#37474F',
            'target-arrow-color': '#37474F',
            'target-arrow-shape': 'triangle'
        }
    }
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
var CytoscapeModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name: 'CytoscapeModel',
        _view_name: 'CytoscapeView',
        _model_module: 'viz-pysb-widget',
        _view_module: 'viz-pysb-widget',
        _model_module_version: semver_range,
        _view_module_version: semver_range
    })
});


// Custom View. Renders the widget model.
var CytoscapeView = widgets.DOMWidgetView.extend({

    render: function() {
        this.value_changed();
        this.model.on('change:value', this.value_changed, this);
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

    renderCy: function() {
        // Remove tippy elements that might be present from previous run
        const tippies = document.getElementsByClassName("tippy-popper");
        while (tippies.length > 0) tippies[0].remove();
        var that = this;

        // Extract parameters
        // const data = that.model.get('data');
        const format = that.model.get('format');
        let layoutName = that.model.get('layout_name');

        let network = that.model.get('data');
        let visualStyle = null;

        const vsParam = that.model.get('visual_style');
        if (vsParam) {
            // Override VS
            visualStyle = vsParam
        }

        if (!visualStyle) {
            visualStyle = DEF_STYLE;
        }

        if (!layoutName || typeof layoutName !== 'string') {
            if (this.checkPositions(network.elements)) {
                // This network has layout information
                layoutName = 'preset'
            } else {
                layoutName = DEF_LAYOUT
            }
        }

        // Doing a deep copy of the node positions to obtain the dot layout
        let dot_positions = JSON.parse(JSON.stringify(network["elements"]["nodes"].map(x => x.position)));

        let cy = cytoscape({
            container: that.el, // container to render in
            elements: network.elements,
            style: cytoscape.stylesheet()
                .selector('node[shape]')
                .style({
                    'label': 'data(label)',
                    'shape': 'data(shape)',
                    // 'font-size': 24,
                    'pie-size': '80%',
                    'pie-1-background-color': 'data(background_color)',
                    'pie-1-background-size': '100',
                    'pie-2-background-color': '#dddcd4',
                    'pie-2-background-size': '100'
                })

                .selector('edge')
                .style({
                    'curve-style': 'bezier',
                    // 'width': 'data(width)',
                    'target-arrow-shape': 'data(target_arrow_shape)',
                    'source-arrow-shape': 'data(source_arrow_shape)',
                    'source-arrow-fill': 'data(source_arrow_fill)'
                })
                .selector(':parent')
                .style({
                    'background-opacity': '0.5',
                    'shape': 'rectangle',
                    'label': 'data(id)'
                })
                .selector('node.cy-expand-collapse-collapsed-node')
                .style({
                    'background-color': 'darkblue',
                    'shape': 'rectangle'})
                .selector('.faded')
                .style({
                    'opacity': 0.25,
                    'text-opacity': 0
                }),
            layout: {
                name: layoutName,
                nodeDimensionsIncludeLabels: true
            }
        });
        // console.log(cy.elements().components()); this could be potentially used to find
        // disjoint subnetworks within a model network

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

        // Finds nodes with no edges
        let sp_nodes = cy.nodes().unmerge(cy.nodes().parent()); // cytoscape.js recommends not using unmerge function
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

            that.$close = $("<span id='close'>x</span>")
                .css('float', 'right');
            that.$message = $("<p class=\"text\">" +
                "        "+message+" " +
                "    </p>" );

            that.$popup = $("<div class='fragment'>" +
                "</div>")
                .css('border', '1px solid #ccc')
                .css('background', '#FF7F7F')
                .append(that.$close)
                .append(that.$message)
                .appendTo(that.el.parentElement);

            that.$close.on('click', function () {
            this.parentNode.parentNode
                .removeChild(this.parentNode);
            return false;
        });

        }

        // Expand collapse compound nodes
        var api = cy.expandCollapse({
            layoutBy: {
                name: "cose-bilkent",
                animate: "end",
                randomize: false,
                fit: true
            },
            fisheye: true,
            animate: true,
            undoable: false
        });

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
                cy.elements().addClass('faded');
                children.removeClass('faded')
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

        // Make tip function
        let makeTippy = function(target, text){
            return tippy( target.popperRef(), {
                html: (function(){
                    let div = document.createElement('div');
                    div.innerHTML = text;
                    return div;
                })(),
                // appendTo: that.el,
//                        offset: '0, 450',
                trigger: 'manual',
                arrow: true,
                placement: 'bottom',
                hideOnClick: false,
                interactive: true,
                multiple: true,
                sticky: true
            } ).tooltips[0];
        };
        // I set the that.el.parentElement position to relative so the buttons can be render
        // relative to it in readthedocs. I don't know if this can have consequences on the notebook rendering.
        // Ideally we would create a new div where we would embed everything.
        that.el.parentElement.style.position = 'relative';

        // Fit button to fit network to cell space
        let fitButton = document.createElement("BUTTON");
        fitButton.id = 'fitbuttonid';
        fitButton.innerHTML = '<i class=\"fa fa-arrows-h\"></i>';

        let allNodes = cy.nodes();
        let layoutPadding = 30;
        let aniDur = 500;
        let easing = 'linear';
        fitButton.addEventListener('click', function(){
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
        that.el.parentElement.appendChild(fitButton);

        // Download button
        let downloadButton = document.createElement("BUTTON");
        downloadButton.id = 'dbutton';
        downloadButton.innerHTML = '<i class="fa fa-download" aria-hidden="true"></i>';
        downloadButton.addEventListener('click', function(){
            let element = document.createElement('a');
            element.setAttribute('href', cy.png({scale: 3}));
            element.setAttribute('download', 'graph.png');
            element.style.display = 'none';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
        });
        that.el.parentElement.append(downloadButton);

        let layouts = ["cose-bilkent", "dagre", "klay", "random", "preset", "grid", "circle", "concentric", "breadthfirst", "cose"];
        let unusedlayouts = layouts.filter(function(e) {return e !== layoutName});

        // pysb adds the file path to the model name. Here we removed the path info to only use the model name
        let name_spl = network.data.name.split(".");
        //TODO: put h1 tag within a div and restrict it size to the size of that div
        that.$model_title = $("  <h1>"+ name_spl[name_spl.length - 1] +"</h1>\n")
            .css('font-size', '16px')
            .css('margin-top', '10px');
        // .css('height', '0.7em');

        that.$title = $("<div id='title'></div>")
            .append(that.$model_title)
            .appendTo(that.el.parentElement);

        that.$layoutDd = $(
            "<select id=\"myList\" >\n" +
            "  <option value='"+layoutName+"'>"+layoutName+"</option>\n" +
            "  <option value='"+unusedlayouts[0]+"'>"+unusedlayouts[0]+"</option>\n" +
            "  <option value='"+unusedlayouts[1]+"'>"+unusedlayouts[1]+"</option>  \n" +
            "  <option value='"+unusedlayouts[2]+"'>"+unusedlayouts[2]+"</option>\n" +
            "  <option value='"+unusedlayouts[3]+"'>"+unusedlayouts[3]+"</option>\n" +
            "  <option value='"+unusedlayouts[4]+"'>"+unusedlayouts[4]+"</option>\n" +
            "  <option value='"+unusedlayouts[5]+"'>"+unusedlayouts[5]+"</option>\n" +
            "  <option value='"+unusedlayouts[6]+"'>"+unusedlayouts[6]+"</option>\n" +
            "</select>\n")
            .appendTo(that.el.parentElement);

        that.$layoutDd.on('change', function() {
            let layout = cy.layout({
                name: this.value,
                nodeDimensionsIncludeLabels: true,
                positions: function(node){
                    let idx = parseInt(node.id().match(/\d+/),10);
                    return dot_positions[idx];
                },
            });
            layout.run();

        });


        that.$search = $("<input type=\"text\" class=\"form-control\" id=\"search\" placeholder=\"Search..\">")

        that.$search_wrapper = $("<div id='bla'></div>")
            .append(that.$search)
            .appendTo(that.el.parentElement);

        that.$info = $("<div id='info'></div>")
            .appendTo(that.el.parentElement);
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
            let aaa = ['<div class="tt-suggest-page"><p><strong>' + name + '</strong></p>',
                '<p><strong>' + '<i class="fa fa-list-ol"></i>' + ' ' + index + '</strong></p><div>',
                '<p><strong>' + '<i class="fa fa-info-circle"></i>' + ' ' + data.NodeType + '</strong></p><div>'].join('');
            return aaa;
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

                    var fields = ['label', 'id', 'NodeType'];

                    function anyFieldMatches( n ){
                        for( var i = 0; i < fields.length; i++ ){
                            var f = fields[i];

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

                    var res = allNodes.stdFilter( anyFieldMatches ).sort( sortByName ).map( getData );

                    cb( res );
                },
                templates: {
                    suggestion: infoTemplate
                }
            }).on('typeahead:selected', function(e, entry, dataset){
            var n = cy.getElementById(entry.id);

            cy.batch(function(){
                allNodes.unselect();

                n.select();
            });

            showNodeInfo( n );
        }).on('keydown keypress keyup change', _.debounce(function(e){
            var thisSearch = that.$search.val();

            if( thisSearch !== lastSearch ){
                $('.tt-dropdown-menu').scrollTop(0);

                lastSearch = thisSearch;
            }
        }, 50));

        let dynamics_vis = function(){
            // Adding empty tips to nodes and edges in advanced so they
            // can be updated later on
            let allEles = cy.elements();
            // remove parent elements
            allEles.unmerge(cy.nodes().parent());
            allEles.forEach(function(ele){
                ele.data()['tip'] = makeTippy(ele, '');
            });

            // Show tip on tap
            cy.on('taphold', 'node, edge',  function(evt){
                let ele = evt.target;
                if (ele.data()['tip']['state']['visible']){
                    ele.data()['tip'].hide();
                } else {
                    ele.data()['tip'].show();
                }
            });

            // Defining player buttons
            let playButton = document.createElement("BUTTON");
            playButton.innerHTML = '<i class="fa fa-play"></i>';
            playButton.style.position='absolute';
            playButton.style.width='30px';
            playButton.style.height='25px';
            playButton.style.bottom='0%';
            // playButton.style.left='100px';
            playButton.style.border='none';
            playButton.style.background='#fffffff7';
            // that.el.parentElement.appendChild(playButton);

            let slider = document.createElement('input');
            slider.id = 'sliderid';
            slider.type = 'range';
            slider.min = 0;
            slider.max = 50;
            slider.value = 0;
            slider.step = 1;
            slider.style.width = '100%';
            slider.style.height = '25px';
            slider.style.top = '0%';
            // slider.style.left = '150px';
            slider.style.position = 'absolute';
            slider.style.border = 'none';
            // that.el.parentElement.appendChild(slider);

            let slider_text = document.createElement('input');
            slider_text.id = 'textid';
            slider_text.type = 'text';
            slider_text.size = 400;
            slider_text.value = 0;
            slider_text.style.width = '50px';
            slider_text.style.height = '25px';
            slider_text.style.bottom = '0%';
            slider_text.style.left = '100px';
            slider_text.style.position = 'absolute';
            slider_text.style.border = 'none';
            // that.el.parentElement.appendChild(slider_text);

            let resetButton = document.createElement("BUTTON");
            resetButton.innerHTML = '<i class="fa fa-refresh"></i>';
            resetButton.style.width = '30px';
            resetButton.style.height = '25px';
            resetButton.style.position = 'absolute';
            resetButton.style.bottom = '0%';
            resetButton.style.left = '50px';
            resetButton.style.border = 'none';
            // that.el.parentElement.appendChild(resetButton);

            let playerSection = document.createElement('div');
            playerSection.style.width = '100%';
            playerSection.style.height = '50px';
            playerSection.style.bottom = '0%';
            playerSection.style.position = 'relative';
            // playerSection.style.boxSizing = 'border-box';
            playerSection.appendChild(playButton);
            playerSection.appendChild(slider);
            playerSection.appendChild(slider_text);
            playerSection.appendChild(resetButton);
            that.el.parentElement.appendChild(playerSection);

            let tspan = network.data.tspan;
            slider.max = tspan.length - 1;

            function animateAll(ele){
                let animationDuration = 1000;
                let animationQueue = [];
                if (ele.isEdge()){
                    let edgeColor = ele.data('edge_color');
                    let edgeSize = ele.data('edge_size');
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
                    }
                }
                else {
                    let nodeRelValue = ele.data('rel_value');
                    for (let idx = 0; idx < nodeRelValue.length; idx++){
                        let value = nodeRelValue[idx];
                        animationQueue.push(ele.animation({
                            style:{
                                'pie-1-background-size': value
                            },
                            duration: animationDuration
                        }));
                    }
                }

                return animationQueue;
            }
            let currentTime = 0;

            function animateAllEles(time, onetime){
                let playQueue = function(ele, queue, position){
                    if (position < queue.length){
                        if (ele.isEdge()){
                            let qtip = ele.data('edge_qtip')[position];
                            ele.data()['tip']['popper'].querySelector('.tippy-content').textContent = qtip.toExponential(2).toString();

                        }
                        else {
                            let qtip = ele.data('abs_value')[position];
                            ele.data()['tip']['popper'].querySelector('.tippy-content').textContent = qtip.toExponential(2).toString();

                        }
                        currentTime = position;
                        slider.value = currentTime;
                        slider_text.value = tspan[currentTime].toFixed(2);
                        if (onetime === true){
                            queue[position].play().promise('complete').then(() => {
                                cy.elements().stop(false, false)
                            })
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
                for (let i=0; i < allEles.length; i++){
                    let ele = allEles[i];
                    let animationQueue = animateAll(ele);
                    playQueue(ele, animationQueue, time)
                }
            }

            let playing = false;
            //
            function pauseSlideshow(){
                playButton.innerHTML = '<i class="fa fa-play"></i>';
                playing = false;
                cy.elements().stop(false, false);
            }
            //
            function playSlideshow(){
                playButton.innerHTML = '<i class="fa fa-pause"></i>';
                playing = true;
                animateAllEles(currentTime, false);
            }
            //
            //
            resetButton.onclick = function(){
                currentTime = 0;
                pauseSlideshow();
                animateAllEles(currentTime, true);

            };

            playButton.onclick = function(){
                if(playing){ pauseSlideshow(); }
                else{ playSlideshow(); }
            };
            slider.addEventListener('mouseup', function(){
                currentTime = this.value;
                currentTime = parseInt(currentTime);
                pauseSlideshow();
                animateAllEles(currentTime, true);

            });

        };
        if(network.data.view === 'dynamic'){
            dynamics_vis()
        }

    }

});


module.exports = {
    CytoscapeModel: CytoscapeModel,
    CytoscapeView: CytoscapeView
};