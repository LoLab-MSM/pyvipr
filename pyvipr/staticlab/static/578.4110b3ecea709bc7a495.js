(self.webpackChunkpyvipr=self.webpackChunkpyvipr||[]).push([[578,901],{578:function(e,t,n){var r;r=function(e){return function(e){var t={};function n(r){if(t[r])return t[r].exports;var o=t[r]={i:r,l:!1,exports:{}};return e[r].call(o.exports,o,o.exports,n),o.l=!0,o.exports}return n.m=e,n.c=t,n.i=function(e){return e},n.d=function(e,t,r){n.o(e,t)||Object.defineProperty(e,t,{configurable:!1,enumerable:!0,get:r})},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="",n(n.s=7)}([function(e,t,n){"use strict";e.exports=null!=Object.assign?Object.assign.bind(Object):function(e){for(var t=arguments.length,n=Array(t>1?t-1:0),r=1;r<t;r++)n[r-1]=arguments[r];return n.forEach((function(t){null!=t&&Object.keys(t).forEach((function(n){return e[n]=t[n]}))})),e}},function(e,t,n){"use strict";var r=n(5).getBoundingBox;e.exports={getRef:function(e,t){return{getBoundingClientRect:function(){return r(e,t)}}}}},function(e,t,n){"use strict";var r=n(0),o=n(1).getRef,i=n(6).getContent,p={},u=n(8).createPopper;e.exports={getPopper:function(e,t){var n=o(e,t),c=i(e,t.content),s=r({},p,t.popper);return u(n,c,s)}}},function(e,t,n){"use strict";var r=n(0),o=n(2).getPopper,i=n(1).getRef;function p(e,t){var n=function(e){return e.isNode()?{w:e.renderedWidth(),h:e.renderedHeight()}:{w:3,h:3}},o=e.cy(),i={renderedDimensions:n,renderedPosition:function(e){return e.isNode()?function(e,t){var n=e.renderedPosition(),r=t(e),o=r.w/2,i=r.h/2;return{x:n.x-o,y:n.y-i}}(e,n):function(e){var t=e.midpoint(),n=e.cy().pan(),r=e.cy().zoom();return{x:t.x*r+n.x,y:t.y*r+n.y}}(e)},popper:{},cy:o};return r({},i,t)}function u(e){e.length>1&&(console.warn("Popper.js Extension should only be used on one element."),console.warn("Ignoring all subsequent elements"))}e.exports={popper:function(e){return u(this),o(this[0],p(this[0],e))},popperRef:function(e){return u(this),i(this[0],p(this[0],e))}}},function(e,t,n){"use strict";var r=n(0),o=n(2).getPopper,i=n(1).getRef;function p(e,t){return r({},{boundingBox:{top:0,left:0,right:0,bottom:0,w:3,h:3},renderedDimensions:function(){return{w:3,h:3}},renderedPosition:function(){return{x:0,y:0}},popper:{},cy:e},t)}e.exports={popper:function(e){return o(this,p(this,e))},popperRef:function(e){return i(this,p(this,e))}}},function(e,t,n){"use strict";e.exports={getBoundingBox:function(e,t){var n=t.renderedPosition,r=t.cy,o=t.renderedDimensions,i=r.container().getBoundingClientRect(),p=o(e),u=n(e);return{top:u.y+i.top,left:u.x+i.left,right:u.x+p.w+i.left,bottom:u.y+p.h+i.top,width:p.w,height:p.h}}}},function(e,t,n){"use strict";e.exports={getContent:function(e,t){var n;if("function"!=typeof t){if(t instanceof HTMLElement)return t;throw new Error("Can not create popper from 'target' with unknown type")}if(null===(n=t(e)))throw new Error("No 'target' specified to create popper");return n}}},function(e,t,n){"use strict";var r=n(4),o=n(3),i=function(e){e&&(e("core","popper",r.popper),e("collection","popper",o.popper),e("core","popperRef",r.popperRef),e("collection","popperRef",o.popperRef))};"undefined"!=typeof cytoscape&&i(cytoscape),e.exports=i},function(t,n){t.exports=e}])},e.exports=r(n(8187))}}]);