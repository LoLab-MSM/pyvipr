(self.webpackChunkpyvipr=self.webpackChunkpyvipr||[]).push([[755],{755:t=>{t.exports=function t(a,e,r){function n(o,s){if(!e[o]){if(!a[o]){if(i)return i(o,!0);var d=new Error("Cannot find module '"+o+"'");throw d.code="MODULE_NOT_FOUND",d}var c=e[o]={exports:{}};a[o][0].call(c.exports,(function(t){return n(a[o][1][t]||t)}),c,c.exports,t,a,e,r)}return e[o].exports}for(var i=void 0,o=0;o<r.length;o++)n(r[o]);return n}({1:[function(t,a,e){a.exports=function(t,a,e){function r(t){for(var r=t.isNode()?"node":"edge",n=["css","data","position"],i={},o=0;o<n.length;o++){var s=n[o],d=e[r][s];if(d)if(a.isArray(d)){i[s]={};for(var c=0;c<d.length;c++){var p=d[o];t[s](p)&&(i[s][p]=t[s](p))}}else{var u=t[s]();for(var f in i[s]={},u)a.inArray(f,e[r].discludeds)<0&&"parent"!=f&&(i[s][f]={value:u[f],attrType:s})}else i[s]={}}return a.extend(i.css,i.data,i.position)}function n(t,e){var i=a("<node />",e).attr({id:t.id()}).appendTo(e),o=r(t);for(var s in o)a("<data />",i).attr({type:o[s].attrType,key:s}).text(o[s].value).appendTo(i);if(t.isParent()){var d=a("<graph />",i).attr({id:t.id()+":"}).appendTo(i);t.children().each((function(t){n(t,d)}))}return i}e.node.discludeds.push("id"),e.edge.discludeds.push("id","source","target");var i,o=a.parseXML('<?xml version="1.0" encoding="UTF-8"?>\n<graphml xmlns="http://graphml.graphdrawing.org/xmlns"\nxmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\nxsi:schemaLocation="http://graphml.graphdrawing.org/xmlns\nhttp://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">\n  <graph>\n </graph>\n </graphml>\n'),s=a(o).find("graph");return t.nodes().orphans().forEach((function(t){n(t,s)})),t.edges().forEach((function(t){var e=a("<edge />",s).attr({id:t.id(),source:t.source().id(),target:t.target().id()}).appendTo(s),n=r(t);for(var i in n)a("<data />",e).attr({key:i}).text(n[i].value).appendTo(e)})),i=o,window.ActiveXObject?i.xml:(new XMLSerializer).serializeToString(i)}},{}],2:[function(t,a,e){a.exports=function(t,a,e,r){function n(e,r){e.children("node").each((function(){var e=a(this),i={data:{id:e.attr("id")},css:{},position:{}};null!=r&&(i.data.parent=r.attr("id")),e.children("data").each((function(){var t=a(this);i.data[t.attr("key")]=t.text()})),t.add({group:"nodes",data:i.data,css:i.css,position:i.position}),e.children("graph").each((function(){n(a(this),e)}))}))}t.batch((function(){xml=a.parseXML(r),$xml=a(xml),$graphs=$xml.find("graph").first(),$graphs.each((function(){var e=a(this);n(e,null),e.find("edge").each((function(){var e=a(this),r={data:{id:e.attr("id"),source:e.attr("source"),target:e.attr("target")},css:{},position:{}};e.find("data").each((function(){var t=a(this);r.data[t.attr("key")]=t.text()})),t.add({group:"edges",data:r.data,css:r.css})}))}));var i=typeof e.layoutBy;"string"==i?t.layout({name:e.layoutBy}).run():"function"==i&&e.layoutBy()}))}},{}],3:[function(t,a,e){!function(){"use strict";var e=function(a,e){if(a&&e){var r=t("./exporter"),n=t("./importer"),i={node:{css:!1,data:!0,position:!0,discludeds:[]},edge:{css:!1,data:!0,discludeds:[]},layoutBy:"cose"};a("core","graphml",(function(t){var a,o=this;switch(typeof t){case"string":a=n(o,e,i,t);break;case"object":e.extend(!0,i,t),a=o;break;case"undefined":a=r(o,e,i);break;default:console.log("Functionality(argument) of .graphml() is not recognized.")}return a}))}};void 0!==a&&a.exports&&(a.exports=e),"undefined"!=typeof cytoscape&&"undefined"!=typeof $&&e(cytoscape,$)}()},{"./exporter":1,"./importer":2}]},{},[3])(3)}}]);