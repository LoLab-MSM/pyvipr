/*
 * Copyright (C) 2015 José Villaveces
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Modifications copyright (C) 2019 Oscar Ortega
 */

//private members
var _getNode = function(id, nodes){
    if(!nodes[id]) nodes[id] = {id:id};
    return nodes[id];
}
    
var _parse = function(line, i, links, nodes){
    line = (line.split('\t').length > 1) ? line.split('\t') : line.split(' ');
    
    if(line.length < 3){
        console.warn('SIFJS cannot parse line ' + i + ' "' + line + '"');
        return;
    }
    
    var source = _getNode(line[0], nodes), intType = line[1], j, length;
    for (j = 2, length = line.length; j < length; j++) {
        var target = _getNode(line[j], nodes);
            
        if(source < target){
            links[source.id + target.id + intType] = {target: target.id, source: source.id, intType: intType};
        }else{
            links[target.id + source.id + intType] = {target: target.id, source: source.id, intType: intType};
        }
    }        
}

var _toArr = function(obj){
    var arr = [];
    for (var key in obj) arr.push(obj[key]);
    return arr;
}    
    
//public
function SIFJS() {};
    
SIFJS.parse = function(text){
    var nodes = {}, links = {};
    
    var lines = text.split('\n'), i, length;
    for (i = 0, length = lines.length; i < length; i++) _parse(lines[i], i, links, nodes);
    
    return {nodes:_toArr(nodes), links:_toArr(links)};
};

SIFJS.parseCyjson = function(text){
    var nodes = {}, links = {};
    
    var lines = text.split('\n'), i, length;
    for (i = 0, length = lines.length; i < length; i++) _parse(lines[i], i, links, nodes);
    let cy_nodes = [];
    let cy_edges = [];
    for (let key in nodes) cy_nodes.push({'data': {'name':nodes[key]['id'], 'id':nodes[key]['id']}});
    for (let key in links) cy_edges.push({'data': links[key]});
    
    return {'nodes': cy_nodes, 'edges':cy_edges};
};

module.exports = SIFJS;
