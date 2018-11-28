var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var cytoscape = require('cytoscape');
var tippy = require('tippy.js');
var popper = require('cytoscape-popper');
var coseBilkent = require('cytoscape-cose-bilkent');
cytoscape.use(popper);
cytoscape.use(coseBilkent);

const FORMAT = {
    CX: 'cx',
    CYJS: 'cyjs',
    EDGELIST: 'el',
}

const DEF_BG = '#FFFFFF'
const DEF_LAYOUT = 'cose'
const DEF_HEIGHT = '500px'

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
        _model_module_version: '0.3.0',
        _view_module_version: '0.3.0'
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
        const elements = document.getElementsByClassName("tippy-popper");
        while (elements.length > 0) elements[0].remove();
        var that = this;

        // Extract parameters
        const data = that.model.get('data');
        const format = that.model.get('format');
        let layoutName = that.model.get('layout_name');

        let network = data;
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
                    'background-opacity': '0.33',
                    'shape': 'rectangle',
                    'label': 'data(id)'
                })
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
        // Adds feature, that when a node is tapped, it fades off all the
        // nodes that are not in its neighborhood
        cy.on('click', 'node', function(e){
            let node = e.target;
            if (node.isParent()){
                cy.stop();
                // let layout = node.children().layout({
                //     name: 'grid',
                //     fit: 'false',
                //     boundingBox: node.parent().boundingBox(),
                //     nodeDimensionsIncludeLabels: true
                // });
                // layout.run();
                cy.animation({
                    fit: {
                        eles: node,
                        padding: layoutPadding
                    },
                    duration: aniDur,
                    easing: easing
                }).play();
                let children = node.children().add(node).add(node.ancestors());
                cy.elements().addClass('faded');
                children.removeClass('faded')
            }
            else {
                let neighborhood = node.neighborhood().add(node);
                cy.elements().addClass('faded');
                neighborhood.removeClass('faded')
            }
        });
        cy.on('click', function(e){
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


        // Fit button to fit network to cell space
        let fitButton = document.createElement("BUTTON");
        fitButton.innerHTML = '<i class=\"fa fa-arrows-h\"></i>';
        // fitButton.setAttribute("type", "button");
        fitButton.style.position='absolute';
        fitButton.style.width='3em';
        fitButton.style.margin='0.5em';
        fitButton.style.top='0';
        fitButton.style.right='15px';

        let allNodes;
        let layoutPadding = 30;
        let aniDur = 500;
        let easing = 'linear';
        allNodes = cy.nodes();
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

        let dynamics_vis = function(){
            // Adding empty tips to nodes and edges in advanced so they
            // can be updated later on
            cy.nodes().forEach(function(n){
                n.data()['tip'] = makeTippy(n, n.position().x);
            });

            cy.edges().forEach(function(e){
                e.data()['tip'] = makeTippy(e, 'test2');
            });

            // Show tip on tap
            cy.on('click', 'node, edge',  function(evt){
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
            // let text = $('#{{textid}}')[0];
            // let rangeInput = $('#{{rangeid}}')[0];
            slider.max = tspan.length - 1;

            // Adding empty tips to nodes and edges in advanced so they
            // can be updated later on
            cy.nodes().forEach(function(n){
                n.data()['tip'] = makeTippy(n, '');
            });

            cy.edges().forEach(function(e){
                e.data()['tip'] = makeTippy(e, 'bla');
            });

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
                let allEles = cy.elements();
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

            slider.oninput = function(){
                text.value = tspan[this.value].toFixed(2);

            };
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