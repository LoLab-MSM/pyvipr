"use strict";(self.webpackChunkpyvipr=self.webpackChunkpyvipr||[]).push([[73],{3645:e=>{e.exports=function(e){var t=[];return t.toString=function(){return this.map((function(t){var n=e(t);return t[2]?"@media ".concat(t[2]," {").concat(n,"}"):n})).join("")},t.i=function(e,n,r){"string"==typeof e&&(e=[[null,e,""]]);var i={};if(r)for(var o=0;o<this.length;o++){var a=this[o][0];null!=a&&(i[a]=!0)}for(var s=0;s<e.length;s++){var u=[].concat(e[s]);r&&i[u[0]]||(n&&(u[2]?u[2]="".concat(n," and ").concat(u[2]):u[2]=n),t.push(u))}},t}},1667:e=>{e.exports=function(e,t){return t||(t={}),e?(e=String(e.__esModule?e.default:e),/^['"].*['"]$/.test(e)&&(e=e.slice(1,-1)),t.hash&&(e+=t.hash),/["'() \t\n]|(%20)/.test(e)||t.needQuotes?'"'.concat(e.replace(/"/g,'\\"').replace(/\n/g,"\\n"),'"'):e):e}},3379:e=>{var t=[];function n(e){for(var n=-1,r=0;r<t.length;r++)if(t[r].identifier===e){n=r;break}return n}function r(e,r){for(var o={},a=[],s=0;s<e.length;s++){var u=e[s],c=r.base?u[0]+r.base:u[0],p=o[c]||0,f="".concat(c," ").concat(p);o[c]=p+1;var d=n(f),l={css:u[1],media:u[2],sourceMap:u[3]};-1!==d?(t[d].references++,t[d].updater(l)):t.push({identifier:f,updater:i(l,r),references:1}),a.push(f)}return a}function i(e,t){var n=t.domAPI(t);return n.update(e),function(t){if(t){if(t.css===e.css&&t.media===e.media&&t.sourceMap===e.sourceMap)return;n.update(e=t)}else n.remove()}}e.exports=function(e,i){var o=r(e=e||[],i=i||{});return function(e){e=e||[];for(var a=0;a<o.length;a++){var s=n(o[a]);t[s].references--}for(var u=r(e,i),c=0;c<o.length;c++){var p=n(o[c]);0===t[p].references&&(t[p].updater(),t.splice(p,1))}o=u}}},569:e=>{var t={};e.exports=function(e,n){var r=function(e){if(void 0===t[e]){var n=document.querySelector(e);if(window.HTMLIFrameElement&&n instanceof window.HTMLIFrameElement)try{n=n.contentDocument.head}catch(e){n=null}t[e]=n}return t[e]}(e);if(!r)throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");r.appendChild(n)}},9216:e=>{e.exports=function(e){var t=document.createElement("style");return e.setAttributes(t,e.attributes),e.insert(t),t}},3565:(e,t,n)=>{e.exports=function(e){var t=n.nc;t&&e.setAttribute("nonce",t)}},7795:e=>{e.exports=function(e){var t=e.insertStyleElement(e);return{update:function(n){!function(e,t,n){var r=n.css,i=n.media,o=n.sourceMap;i?e.setAttribute("media",i):e.removeAttribute("media"),o&&"undefined"!=typeof btoa&&(r+="\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(o))))," */")),t.styleTagTransform(r,e)}(t,e,n)},remove:function(){!function(e){if(null===e.parentNode)return!1;e.parentNode.removeChild(e)}(t)}}}},4589:e=>{e.exports=function(e,t){if(t.styleSheet)t.styleSheet.cssText=e;else{for(;t.firstChild;)t.removeChild(t.firstChild);t.appendChild(document.createTextNode(e))}}},3786:(e,t,n)=>{var r=n(8187),i="tippy-content",o="tippy-backdrop",a="tippy-arrow",s="tippy-svg-arrow",u={passive:!0,capture:!0};function c(e,t,n){if(Array.isArray(e)){var r=e[t];return null==r?Array.isArray(n)?n[t]:n:r}return e}function p(e,t){var n={}.toString.call(e);return 0===n.indexOf("[object")&&n.indexOf(t+"]")>-1}function f(e,t){return"function"==typeof e?e.apply(void 0,t):e}function d(e,t){return 0===t?e:function(r){clearTimeout(n),n=setTimeout((function(){e(r)}),t)};var n}function l(e){return[].concat(e)}function v(e,t){-1===e.indexOf(t)&&e.push(t)}function m(e){return e.split("-")[0]}function h(e){return[].slice.call(e)}function b(){return document.createElement("div")}function g(e){return["Element","Fragment"].some((function(t){return p(e,t)}))}function y(e){return p(e,"MouseEvent")}function T(e,t){e.forEach((function(e){e&&(e.style.transitionDuration=t+"ms")}))}function w(e,t){e.forEach((function(e){e&&e.setAttribute("data-state",t)}))}function x(e){var t,n=l(e)[0];return(null==n||null==(t=n.ownerDocument)?void 0:t.body)?n.ownerDocument:document}function E(e,t,n){var r=t+"EventListener";["transitionend","webkitTransitionEnd"].forEach((function(t){e[r](t,n)}))}var A={isTouch:!1},O=0;function C(){A.isTouch||(A.isTouch=!0,window.performance&&document.addEventListener("mousemove",L))}function L(){var e=performance.now();e-O<20&&(A.isTouch=!1,document.removeEventListener("mousemove",L)),O=e}function k(){var e,t=document.activeElement;if((e=t)&&e._tippy&&e._tippy.reference===e){var n=t._tippy;t.blur&&!n.state.isVisible&&t.blur()}}var D="undefined"!=typeof window&&"undefined"!=typeof document?navigator.userAgent:"",M=/MSIE |Trident\//.test(D),S=Object.assign({appendTo:function(){return document.body},aria:{content:"auto",expanded:"auto"},delay:0,duration:[300,250],getReferenceClientRect:null,hideOnClick:!0,ignoreAttributes:!1,interactive:!1,interactiveBorder:2,interactiveDebounce:0,moveTransition:"",offset:[0,10],onAfterUpdate:function(){},onBeforeUpdate:function(){},onCreate:function(){},onDestroy:function(){},onHidden:function(){},onHide:function(){},onMount:function(){},onShow:function(){},onShown:function(){},onTrigger:function(){},onUntrigger:function(){},onClickOutside:function(){},placement:"top",plugins:[],popperOptions:{},render:null,showOnCreate:!1,touch:!0,trigger:"mouseenter focus",triggerTarget:null},{animateFill:!1,followCursor:!1,inlinePositioning:!1,sticky:!1},{},{allowHTML:!1,animation:"fade",arrow:!0,content:"",inertia:!1,maxWidth:350,role:"tooltip",theme:"",zIndex:9999}),I=Object.keys(S);function V(e){var t=(e.plugins||[]).reduce((function(t,n){var r=n.name,i=n.defaultValue;return r&&(t[r]=void 0!==e[r]?e[r]:i),t}),{});return Object.assign({},e,{},t)}function j(e,t){var n=Object.assign({},t,{content:f(t.content,[e])},t.ignoreAttributes?{}:function(e,t){return(t?Object.keys(V(Object.assign({},S,{plugins:t}))):I).reduce((function(t,n){var r=(e.getAttribute("data-tippy-"+n)||"").trim();if(!r)return t;if("content"===n)t[n]=r;else try{t[n]=JSON.parse(r)}catch(e){t[n]=r}return t}),{})}(e,t.plugins));return n.aria=Object.assign({},S.aria,{},n.aria),n.aria={expanded:"auto"===n.aria.expanded?t.interactive:n.aria.expanded,content:"auto"===n.aria.content?t.interactive?null:"describedby":n.aria.content},n}function N(e,t){e.innerHTML=t}function H(e){var t=b();return!0===e?t.className=a:(t.className=s,g(e)?t.appendChild(e):N(t,e)),t}function U(e,t){g(t.content)?(N(e,""),e.appendChild(t.content)):"function"!=typeof t.content&&(t.allowHTML?N(e,t.content):e.textContent=t.content)}function R(e){var t=e.firstElementChild,n=h(t.children);return{box:t,content:n.find((function(e){return e.classList.contains(i)})),arrow:n.find((function(e){return e.classList.contains(a)||e.classList.contains(s)})),backdrop:n.find((function(e){return e.classList.contains(o)}))}}function _(e){var t=b(),n=b();n.className="tippy-box",n.setAttribute("data-state","hidden"),n.setAttribute("tabindex","-1");var r=b();function o(n,r){var i=R(t),o=i.box,a=i.content,s=i.arrow;r.theme?o.setAttribute("data-theme",r.theme):o.removeAttribute("data-theme"),"string"==typeof r.animation?o.setAttribute("data-animation",r.animation):o.removeAttribute("data-animation"),r.inertia?o.setAttribute("data-inertia",""):o.removeAttribute("data-inertia"),o.style.maxWidth="number"==typeof r.maxWidth?r.maxWidth+"px":r.maxWidth,r.role?o.setAttribute("role",r.role):o.removeAttribute("role"),n.content===r.content&&n.allowHTML===r.allowHTML||U(a,e.props),r.arrow?s?n.arrow!==r.arrow&&(o.removeChild(s),o.appendChild(H(r.arrow))):o.appendChild(H(r.arrow)):s&&o.removeChild(s)}return r.className=i,r.setAttribute("data-state","hidden"),U(r,e.props),t.appendChild(n),n.appendChild(r),o(e.props,e.props),{popper:t,onUpdate:o}}_.$$tippy=!0;var B=1,F=[],P=[];function W(e,t){var n,i,o,a,s,p,g,O,C,L=j(e,Object.assign({},S,{},V((n=t,Object.keys(n).reduce((function(e,t){return void 0!==n[t]&&(e[t]=n[t]),e}),{}))))),k=!1,D=!1,I=!1,N=!1,H=[],U=d(ge,L.interactiveDebounce),_=B++,W=(C=L.plugins).filter((function(e,t){return C.indexOf(e)===t})),q={id:_,reference:e,popper:b(),popperInstance:null,props:L,state:{isEnabled:!0,isVisible:!1,isDestroyed:!1,isMounted:!1,isShown:!1},plugins:W,clearDelayTimeouts:function(){clearTimeout(i),clearTimeout(o),cancelAnimationFrame(a)},setProps:function(t){if(!q.state.isDestroyed){ie("onBeforeUpdate",[q,t]),he();var n=q.props,r=j(e,Object.assign({},q.props,{},t,{ignoreAttributes:!0}));q.props=r,me(),n.interactiveDebounce!==r.interactiveDebounce&&(se(),U=d(ge,r.interactiveDebounce)),n.triggerTarget&&!r.triggerTarget?l(n.triggerTarget).forEach((function(e){e.removeAttribute("aria-expanded")})):r.triggerTarget&&e.removeAttribute("aria-expanded"),ae(),re(),J&&J(n,r),q.popperInstance&&(xe(),Ae().forEach((function(e){requestAnimationFrame(e._tippy.popperInstance.forceUpdate)}))),ie("onAfterUpdate",[q,t])}},setContent:function(e){q.setProps({content:e})},show:function(){var e=q.state.isVisible,t=q.state.isDestroyed,n=!q.state.isEnabled,r=A.isTouch&&!q.props.touch,i=c(q.props.duration,0,S.duration);if(!(e||t||n||r||K().hasAttribute("disabled")||(ie("onShow",[q],!1),!1===q.props.onShow(q)))){if(q.state.isVisible=!0,G()&&(z.style.visibility="visible"),re(),fe(),q.state.isMounted||(z.style.transition="none"),G()){var o=te();T([o.box,o.content],0)}var a,s,u;g=function(){var e;if(q.state.isVisible&&!N){if(N=!0,z.offsetHeight,z.style.transition=q.props.moveTransition,G()&&q.props.animation){var t=te(),n=t.box,r=t.content;T([n,r],i),w([n,r],"visible")}oe(),ae(),v(P,q),null==(e=q.popperInstance)||e.forceUpdate(),q.state.isMounted=!0,ie("onMount",[q]),q.props.animation&&G()&&function(e,t){le(e,(function(){q.state.isShown=!0,ie("onShown",[q])}))}(i)}},s=q.props.appendTo,u=K(),(a=q.props.interactive&&s===S.appendTo||"parent"===s?u.parentNode:f(s,[u])).contains(z)||a.appendChild(z),xe()}},hide:function(){var e=!q.state.isVisible,t=q.state.isDestroyed,n=!q.state.isEnabled,r=c(q.props.duration,1,S.duration);if(!(e||t||n)&&(ie("onHide",[q],!1),!1!==q.props.onHide(q))){if(q.state.isVisible=!1,q.state.isShown=!1,N=!1,k=!1,G()&&(z.style.visibility="hidden"),se(),de(),re(),G()){var i=te(),o=i.box,a=i.content;q.props.animation&&(T([o,a],r),w([o,a],"hidden"))}oe(),ae(),q.props.animation?G()&&function(e,t){le(e,(function(){!q.state.isVisible&&z.parentNode&&z.parentNode.contains(z)&&t()}))}(r,q.unmount):q.unmount()}},hideWithInteractivity:function(e){ee().addEventListener("mousemove",U),v(F,U),U(e)},enable:function(){q.state.isEnabled=!0},disable:function(){q.hide(),q.state.isEnabled=!1},unmount:function(){q.state.isVisible&&q.hide(),q.state.isMounted&&(Ee(),Ae().forEach((function(e){e._tippy.unmount()})),z.parentNode&&z.parentNode.removeChild(z),P=P.filter((function(e){return e!==q})),q.state.isMounted=!1,ie("onHidden",[q]))},destroy:function(){q.state.isDestroyed||(q.clearDelayTimeouts(),q.unmount(),he(),delete e._tippy,q.state.isDestroyed=!0,ie("onDestroy",[q]))}};if(!L.render)return q;var $=L.render(q),z=$.popper,J=$.onUpdate;z.setAttribute("data-tippy-root",""),z.id="tippy-"+q.id,q.popper=z,e._tippy=q,z._tippy=q;var Q=W.map((function(e){return e.fn(q)})),X=e.hasAttribute("aria-expanded");return me(),ae(),re(),ie("onCreate",[q]),L.showOnCreate&&Oe(),z.addEventListener("mouseenter",(function(){q.props.interactive&&q.state.isVisible&&q.clearDelayTimeouts()})),z.addEventListener("mouseleave",(function(e){q.props.interactive&&q.props.trigger.indexOf("mouseenter")>=0&&(ee().addEventListener("mousemove",U),U(e))})),q;function Y(){var e=q.props.touch;return Array.isArray(e)?e:[e,0]}function Z(){return"hold"===Y()[0]}function G(){var e;return!!(null==(e=q.props.render)?void 0:e.$$tippy)}function K(){return O||e}function ee(){var e=K().parentNode;return e?x(e):document}function te(){return R(z)}function ne(e){return q.state.isMounted&&!q.state.isVisible||A.isTouch||s&&"focus"===s.type?0:c(q.props.delay,e?0:1,S.delay)}function re(){z.style.pointerEvents=q.props.interactive&&q.state.isVisible?"":"none",z.style.zIndex=""+q.props.zIndex}function ie(e,t,n){var r;void 0===n&&(n=!0),Q.forEach((function(n){n[e]&&n[e].apply(void 0,t)})),n&&(r=q.props)[e].apply(r,t)}function oe(){var t=q.props.aria;if(t.content){var n="aria-"+t.content,r=z.id;l(q.props.triggerTarget||e).forEach((function(e){var t=e.getAttribute(n);if(q.state.isVisible)e.setAttribute(n,t?t+" "+r:r);else{var i=t&&t.replace(r,"").trim();i?e.setAttribute(n,i):e.removeAttribute(n)}}))}}function ae(){!X&&q.props.aria.expanded&&l(q.props.triggerTarget||e).forEach((function(e){q.props.interactive?e.setAttribute("aria-expanded",q.state.isVisible&&e===K()?"true":"false"):e.removeAttribute("aria-expanded")}))}function se(){ee().removeEventListener("mousemove",U),F=F.filter((function(e){return e!==U}))}function ue(e){if(!(A.isTouch&&(I||"mousedown"===e.type)||q.props.interactive&&z.contains(e.target))){if(K().contains(e.target)){if(A.isTouch)return;if(q.state.isVisible&&q.props.trigger.indexOf("click")>=0)return}else ie("onClickOutside",[q,e]);!0===q.props.hideOnClick&&(q.clearDelayTimeouts(),q.hide(),D=!0,setTimeout((function(){D=!1})),q.state.isMounted||de())}}function ce(){I=!0}function pe(){I=!1}function fe(){var e=ee();e.addEventListener("mousedown",ue,!0),e.addEventListener("touchend",ue,u),e.addEventListener("touchstart",pe,u),e.addEventListener("touchmove",ce,u)}function de(){var e=ee();e.removeEventListener("mousedown",ue,!0),e.removeEventListener("touchend",ue,u),e.removeEventListener("touchstart",pe,u),e.removeEventListener("touchmove",ce,u)}function le(e,t){var n=te().box;function r(e){e.target===n&&(E(n,"remove",r),t())}if(0===e)return t();E(n,"remove",p),E(n,"add",r),p=r}function ve(t,n,r){void 0===r&&(r=!1),l(q.props.triggerTarget||e).forEach((function(e){e.addEventListener(t,n,r),H.push({node:e,eventType:t,handler:n,options:r})}))}function me(){var e;Z()&&(ve("touchstart",be,{passive:!0}),ve("touchend",ye,{passive:!0})),(e=q.props.trigger,e.split(/\s+/).filter(Boolean)).forEach((function(e){if("manual"!==e)switch(ve(e,be),e){case"mouseenter":ve("mouseleave",ye);break;case"focus":ve(M?"focusout":"blur",Te);break;case"focusin":ve("focusout",Te)}}))}function he(){H.forEach((function(e){var t=e.node,n=e.eventType,r=e.handler,i=e.options;t.removeEventListener(n,r,i)})),H=[]}function be(e){var t,n=!1;if(q.state.isEnabled&&!we(e)&&!D){var r="focus"===(null==(t=s)?void 0:t.type);s=e,O=e.currentTarget,ae(),!q.state.isVisible&&y(e)&&F.forEach((function(t){return t(e)})),"click"===e.type&&(q.props.trigger.indexOf("mouseenter")<0||k)&&!1!==q.props.hideOnClick&&q.state.isVisible?n=!0:Oe(e),"click"===e.type&&(k=!n),n&&!r&&Ce(e)}}function ge(e){var t=e.target,n=K().contains(t)||z.contains(t);if("mousemove"!==e.type||!n){var r=Ae().concat(z).map((function(e){var t,n=null==(t=e._tippy.popperInstance)?void 0:t.state;return n?{popperRect:e.getBoundingClientRect(),popperState:n,props:L}:null})).filter(Boolean);(function(e,t){var n=t.clientX,r=t.clientY;return e.every((function(e){var t=e.popperRect,i=e.popperState,o=e.props.interactiveBorder,a=m(i.placement),s=i.modifiersData.offset;if(!s)return!0;var u="bottom"===a?s.top.y:0,c="top"===a?s.bottom.y:0,p="right"===a?s.left.x:0,f="left"===a?s.right.x:0,d=t.top-r+u>o,l=r-t.bottom-c>o,v=t.left-n+p>o,h=n-t.right-f>o;return d||l||v||h}))})(r,e)&&(se(),Ce(e))}}function ye(e){we(e)||q.props.trigger.indexOf("click")>=0&&k||(q.props.interactive?q.hideWithInteractivity(e):Ce(e))}function Te(e){q.props.trigger.indexOf("focusin")<0&&e.target!==K()||q.props.interactive&&e.relatedTarget&&z.contains(e.relatedTarget)||Ce(e)}function we(e){return!!A.isTouch&&Z()!==e.type.indexOf("touch")>=0}function xe(){Ee();var t=q.props,n=t.popperOptions,i=t.placement,o=t.offset,a=t.getReferenceClientRect,s=t.moveTransition,u=G()?R(z).arrow:null,c=a?{getBoundingClientRect:a,contextElement:a.contextElement||K()}:e,p=[{name:"offset",options:{offset:o}},{name:"preventOverflow",options:{padding:{top:2,bottom:2,left:5,right:5}}},{name:"flip",options:{padding:5}},{name:"computeStyles",options:{adaptive:!s}},{name:"$$tippy",enabled:!0,phase:"beforeWrite",requires:["computeStyles"],fn:function(e){var t=e.state;if(G()){var n=te().box;["placement","reference-hidden","escaped"].forEach((function(e){"placement"===e?n.setAttribute("data-placement",t.placement):t.attributes.popper["data-popper-"+e]?n.setAttribute("data-"+e,""):n.removeAttribute("data-"+e)})),t.attributes.popper={}}}}];G()&&u&&p.push({name:"arrow",options:{element:u,padding:3}}),p.push.apply(p,(null==n?void 0:n.modifiers)||[]),q.popperInstance=r.createPopper(c,z,Object.assign({},n,{placement:i,onFirstUpdate:g,modifiers:p}))}function Ee(){q.popperInstance&&(q.popperInstance.destroy(),q.popperInstance=null)}function Ae(){return h(z.querySelectorAll("[data-tippy-root]"))}function Oe(e){q.clearDelayTimeouts(),e&&ie("onTrigger",[q,e]),fe();var t=ne(!0),n=Y(),r=n[0],o=n[1];A.isTouch&&"hold"===r&&o&&(t=o),t?i=setTimeout((function(){q.show()}),t):q.show()}function Ce(e){if(q.clearDelayTimeouts(),ie("onUntrigger",[q,e]),q.state.isVisible){if(!(q.props.trigger.indexOf("mouseenter")>=0&&q.props.trigger.indexOf("click")>=0&&["mouseleave","mousemove"].indexOf(e.type)>=0&&k)){var t=ne(!1);t?o=setTimeout((function(){q.state.isVisible&&q.hide()}),t):a=requestAnimationFrame((function(){q.hide()}))}}else de()}}function q(e,t){void 0===t&&(t={});var n=S.plugins.concat(t.plugins||[]);document.addEventListener("touchstart",C,u),window.addEventListener("blur",k);var r,i=Object.assign({},t,{plugins:n}),o=(r=e,g(r)?[r]:function(e){return p(e,"NodeList")}(r)?h(r):Array.isArray(r)?r:h(document.querySelectorAll(r))).reduce((function(e,t){var n=t&&W(t,i);return n&&e.push(n),e}),[]);return g(e)?o[0]:o}q.defaultProps=S,q.setDefaultProps=function(e){Object.keys(e).forEach((function(t){S[t]=e[t]}))},q.currentInput=A;Object.assign({},r.applyStyles,{effect:function(e){var t=e.state,n={popper:{position:t.options.strategy,left:"0",top:"0",margin:"0"},arrow:{position:"absolute"},reference:{}};Object.assign(t.elements.popper.style,n.popper),t.styles=n,t.elements.arrow&&Object.assign(t.elements.arrow.style,n.arrow)}});var $={name:"sticky",defaultValue:!1,fn:function(e){var t=e.reference,n=e.popper;function r(t){return!0===e.props.sticky||e.props.sticky===t}var i=null,o=null;function a(){var s=r("reference")?(e.popperInstance?e.popperInstance.state.elements.reference:t).getBoundingClientRect():null,u=r("popper")?n.getBoundingClientRect():null;(s&&z(i,s)||u&&z(o,u))&&e.popperInstance&&e.popperInstance.update(),i=s,o=u,e.state.isMounted&&requestAnimationFrame(a)}return{onMount:function(){e.props.sticky&&a()}}}};function z(e,t){return!e||!t||e.top!==t.top||e.right!==t.right||e.bottom!==t.bottom||e.left!==t.left}q.setDefaultProps({render:_}),t.ZP=q,t.CA=$}}]);