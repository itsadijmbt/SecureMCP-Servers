/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 20
(__unused_webpack_module, exports, __webpack_require__) {

/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var f=__webpack_require__(159),k=Symbol.for("react.element"),l=Symbol.for("react.fragment"),m=Object.prototype.hasOwnProperty,n=f.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner,p={key:!0,ref:!0,__self:!0,__source:!0};
function q(c,a,g){var b,d={},e=null,h=null;void 0!==g&&(e=""+g);void 0!==a.key&&(e=""+a.key);void 0!==a.ref&&(h=a.ref);for(b in a)m.call(a,b)&&!p.hasOwnProperty(b)&&(d[b]=a[b]);if(c&&c.defaultProps)for(b in a=c.defaultProps,a)void 0===d[b]&&(d[b]=a[b]);return{$$typeof:k,type:c,key:e,ref:h,props:d,_owner:n.current}}exports.Fragment=l;exports.jsx=q;exports.jsxs=q;


/***/ },

/***/ 56
(module, __unused_webpack_exports, __webpack_require__) {



/* istanbul ignore next  */
function setAttributesWithoutAttributes(styleElement) {
  var nonce =  true ? __webpack_require__.nc : 0;
  if (nonce) {
    styleElement.setAttribute("nonce", nonce);
  }
}
module.exports = setAttributesWithoutAttributes;

/***/ },

/***/ 72
(module) {



var stylesInDOM = [];
function getIndexByIdentifier(identifier) {
  var result = -1;
  for (var i = 0; i < stylesInDOM.length; i++) {
    if (stylesInDOM[i].identifier === identifier) {
      result = i;
      break;
    }
  }
  return result;
}
function modulesToDom(list, options) {
  var idCountMap = {};
  var identifiers = [];
  for (var i = 0; i < list.length; i++) {
    var item = list[i];
    var id = options.base ? item[0] + options.base : item[0];
    var count = idCountMap[id] || 0;
    var identifier = "".concat(id, " ").concat(count);
    idCountMap[id] = count + 1;
    var indexByIdentifier = getIndexByIdentifier(identifier);
    var obj = {
      css: item[1],
      media: item[2],
      sourceMap: item[3],
      supports: item[4],
      layer: item[5]
    };
    if (indexByIdentifier !== -1) {
      stylesInDOM[indexByIdentifier].references++;
      stylesInDOM[indexByIdentifier].updater(obj);
    } else {
      var updater = addElementStyle(obj, options);
      options.byIndex = i;
      stylesInDOM.splice(i, 0, {
        identifier: identifier,
        updater: updater,
        references: 1
      });
    }
    identifiers.push(identifier);
  }
  return identifiers;
}
function addElementStyle(obj, options) {
  var api = options.domAPI(options);
  api.update(obj);
  var updater = function updater(newObj) {
    if (newObj) {
      if (newObj.css === obj.css && newObj.media === obj.media && newObj.sourceMap === obj.sourceMap && newObj.supports === obj.supports && newObj.layer === obj.layer) {
        return;
      }
      api.update(obj = newObj);
    } else {
      api.remove();
    }
  };
  return updater;
}
module.exports = function (list, options) {
  options = options || {};
  list = list || [];
  var lastIdentifiers = modulesToDom(list, options);
  return function update(newList) {
    newList = newList || [];
    for (var i = 0; i < lastIdentifiers.length; i++) {
      var identifier = lastIdentifiers[i];
      var index = getIndexByIdentifier(identifier);
      stylesInDOM[index].references--;
    }
    var newLastIdentifiers = modulesToDom(newList, options);
    for (var _i = 0; _i < lastIdentifiers.length; _i++) {
      var _identifier = lastIdentifiers[_i];
      var _index = getIndexByIdentifier(_identifier);
      if (stylesInDOM[_index].references === 0) {
        stylesInDOM[_index].updater();
        stylesInDOM.splice(_index, 1);
      }
    }
    lastIdentifiers = newLastIdentifiers;
  };
};

/***/ },

/***/ 113
(module) {



/* istanbul ignore next  */
function styleTagTransform(css, styleElement) {
  if (styleElement.styleSheet) {
    styleElement.styleSheet.cssText = css;
  } else {
    while (styleElement.firstChild) {
      styleElement.removeChild(styleElement.firstChild);
    }
    styleElement.appendChild(document.createTextNode(css));
  }
}
module.exports = styleTagTransform;

/***/ },

/***/ 159
(module, __unused_webpack_exports, __webpack_require__) {



if (true) {
  module.exports = __webpack_require__(287);
} else // removed by dead control flow
{}


/***/ },

/***/ 287
(__unused_webpack_module, exports) {

/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var l=Symbol.for("react.element"),n=Symbol.for("react.portal"),p=Symbol.for("react.fragment"),q=Symbol.for("react.strict_mode"),r=Symbol.for("react.profiler"),t=Symbol.for("react.provider"),u=Symbol.for("react.context"),v=Symbol.for("react.forward_ref"),w=Symbol.for("react.suspense"),x=Symbol.for("react.memo"),y=Symbol.for("react.lazy"),z=Symbol.iterator;function A(a){if(null===a||"object"!==typeof a)return null;a=z&&a[z]||a["@@iterator"];return"function"===typeof a?a:null}
var B={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},C=Object.assign,D={};function E(a,b,e){this.props=a;this.context=b;this.refs=D;this.updater=e||B}E.prototype.isReactComponent={};
E.prototype.setState=function(a,b){if("object"!==typeof a&&"function"!==typeof a&&null!=a)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,a,b,"setState")};E.prototype.forceUpdate=function(a){this.updater.enqueueForceUpdate(this,a,"forceUpdate")};function F(){}F.prototype=E.prototype;function G(a,b,e){this.props=a;this.context=b;this.refs=D;this.updater=e||B}var H=G.prototype=new F;
H.constructor=G;C(H,E.prototype);H.isPureReactComponent=!0;var I=Array.isArray,J=Object.prototype.hasOwnProperty,K={current:null},L={key:!0,ref:!0,__self:!0,__source:!0};
function M(a,b,e){var d,c={},k=null,h=null;if(null!=b)for(d in void 0!==b.ref&&(h=b.ref),void 0!==b.key&&(k=""+b.key),b)J.call(b,d)&&!L.hasOwnProperty(d)&&(c[d]=b[d]);var g=arguments.length-2;if(1===g)c.children=e;else if(1<g){for(var f=Array(g),m=0;m<g;m++)f[m]=arguments[m+2];c.children=f}if(a&&a.defaultProps)for(d in g=a.defaultProps,g)void 0===c[d]&&(c[d]=g[d]);return{$$typeof:l,type:a,key:k,ref:h,props:c,_owner:K.current}}
function N(a,b){return{$$typeof:l,type:a.type,key:b,ref:a.ref,props:a.props,_owner:a._owner}}function O(a){return"object"===typeof a&&null!==a&&a.$$typeof===l}function escape(a){var b={"=":"=0",":":"=2"};return"$"+a.replace(/[=:]/g,function(a){return b[a]})}var P=/\/+/g;function Q(a,b){return"object"===typeof a&&null!==a&&null!=a.key?escape(""+a.key):b.toString(36)}
function R(a,b,e,d,c){var k=typeof a;if("undefined"===k||"boolean"===k)a=null;var h=!1;if(null===a)h=!0;else switch(k){case "string":case "number":h=!0;break;case "object":switch(a.$$typeof){case l:case n:h=!0}}if(h)return h=a,c=c(h),a=""===d?"."+Q(h,0):d,I(c)?(e="",null!=a&&(e=a.replace(P,"$&/")+"/"),R(c,b,e,"",function(a){return a})):null!=c&&(O(c)&&(c=N(c,e+(!c.key||h&&h.key===c.key?"":(""+c.key).replace(P,"$&/")+"/")+a)),b.push(c)),1;h=0;d=""===d?".":d+":";if(I(a))for(var g=0;g<a.length;g++){k=
a[g];var f=d+Q(k,g);h+=R(k,b,e,f,c)}else if(f=A(a),"function"===typeof f)for(a=f.call(a),g=0;!(k=a.next()).done;)k=k.value,f=d+Q(k,g++),h+=R(k,b,e,f,c);else if("object"===k)throw b=String(a),Error("Objects are not valid as a React child (found: "+("[object Object]"===b?"object with keys {"+Object.keys(a).join(", ")+"}":b)+"). If you meant to render a collection of children, use an array instead.");return h}
function S(a,b,e){if(null==a)return a;var d=[],c=0;R(a,d,"","",function(a){return b.call(e,a,c++)});return d}function T(a){if(-1===a._status){var b=a._result;b=b();b.then(function(b){if(0===a._status||-1===a._status)a._status=1,a._result=b},function(b){if(0===a._status||-1===a._status)a._status=2,a._result=b});-1===a._status&&(a._status=0,a._result=b)}if(1===a._status)return a._result.default;throw a._result;}
var U={current:null},V={transition:null},W={ReactCurrentDispatcher:U,ReactCurrentBatchConfig:V,ReactCurrentOwner:K};function X(){throw Error("act(...) is not supported in production builds of React.");}
exports.Children={map:S,forEach:function(a,b,e){S(a,function(){b.apply(this,arguments)},e)},count:function(a){var b=0;S(a,function(){b++});return b},toArray:function(a){return S(a,function(a){return a})||[]},only:function(a){if(!O(a))throw Error("React.Children.only expected to receive a single React element child.");return a}};exports.Component=E;exports.Fragment=p;exports.Profiler=r;exports.PureComponent=G;exports.StrictMode=q;exports.Suspense=w;
exports.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=W;exports.act=X;
exports.cloneElement=function(a,b,e){if(null===a||void 0===a)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+a+".");var d=C({},a.props),c=a.key,k=a.ref,h=a._owner;if(null!=b){void 0!==b.ref&&(k=b.ref,h=K.current);void 0!==b.key&&(c=""+b.key);if(a.type&&a.type.defaultProps)var g=a.type.defaultProps;for(f in b)J.call(b,f)&&!L.hasOwnProperty(f)&&(d[f]=void 0===b[f]&&void 0!==g?g[f]:b[f])}var f=arguments.length-2;if(1===f)d.children=e;else if(1<f){g=Array(f);
for(var m=0;m<f;m++)g[m]=arguments[m+2];d.children=g}return{$$typeof:l,type:a.type,key:c,ref:k,props:d,_owner:h}};exports.createContext=function(a){a={$$typeof:u,_currentValue:a,_currentValue2:a,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null};a.Provider={$$typeof:t,_context:a};return a.Consumer=a};exports.createElement=M;exports.createFactory=function(a){var b=M.bind(null,a);b.type=a;return b};exports.createRef=function(){return{current:null}};
exports.forwardRef=function(a){return{$$typeof:v,render:a}};exports.isValidElement=O;exports.lazy=function(a){return{$$typeof:y,_payload:{_status:-1,_result:a},_init:T}};exports.memo=function(a,b){return{$$typeof:x,type:a,compare:void 0===b?null:b}};exports.startTransition=function(a){var b=V.transition;V.transition={};try{a()}finally{V.transition=b}};exports.unstable_act=X;exports.useCallback=function(a,b){return U.current.useCallback(a,b)};exports.useContext=function(a){return U.current.useContext(a)};
exports.useDebugValue=function(){};exports.useDeferredValue=function(a){return U.current.useDeferredValue(a)};exports.useEffect=function(a,b){return U.current.useEffect(a,b)};exports.useId=function(){return U.current.useId()};exports.useImperativeHandle=function(a,b,e){return U.current.useImperativeHandle(a,b,e)};exports.useInsertionEffect=function(a,b){return U.current.useInsertionEffect(a,b)};exports.useLayoutEffect=function(a,b){return U.current.useLayoutEffect(a,b)};
exports.useMemo=function(a,b){return U.current.useMemo(a,b)};exports.useReducer=function(a,b,e){return U.current.useReducer(a,b,e)};exports.useRef=function(a){return U.current.useRef(a)};exports.useState=function(a){return U.current.useState(a)};exports.useSyncExternalStore=function(a,b,e){return U.current.useSyncExternalStore(a,b,e)};exports.useTransition=function(){return U.current.useTransition()};exports.version="18.3.1";


/***/ },

/***/ 314
(module) {



/*
  MIT License http://www.opensource.org/licenses/mit-license.php
  Author Tobias Koppers @sokra
*/
module.exports = function (cssWithMappingToString) {
  var list = [];

  // return the list of modules as css string
  list.toString = function toString() {
    return this.map(function (item) {
      var content = "";
      var needLayer = typeof item[5] !== "undefined";
      if (item[4]) {
        content += "@supports (".concat(item[4], ") {");
      }
      if (item[2]) {
        content += "@media ".concat(item[2], " {");
      }
      if (needLayer) {
        content += "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {");
      }
      content += cssWithMappingToString(item);
      if (needLayer) {
        content += "}";
      }
      if (item[2]) {
        content += "}";
      }
      if (item[4]) {
        content += "}";
      }
      return content;
    }).join("");
  };

  // import a list of modules into the list
  list.i = function i(modules, media, dedupe, supports, layer) {
    if (typeof modules === "string") {
      modules = [[null, modules, undefined]];
    }
    var alreadyImportedModules = {};
    if (dedupe) {
      for (var k = 0; k < this.length; k++) {
        var id = this[k][0];
        if (id != null) {
          alreadyImportedModules[id] = true;
        }
      }
    }
    for (var _k = 0; _k < modules.length; _k++) {
      var item = [].concat(modules[_k]);
      if (dedupe && alreadyImportedModules[item[0]]) {
        continue;
      }
      if (typeof layer !== "undefined") {
        if (typeof item[5] === "undefined") {
          item[5] = layer;
        } else {
          item[1] = "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {").concat(item[1], "}");
          item[5] = layer;
        }
      }
      if (media) {
        if (!item[2]) {
          item[2] = media;
        } else {
          item[1] = "@media ".concat(item[2], " {").concat(item[1], "}");
          item[2] = media;
        }
      }
      if (supports) {
        if (!item[4]) {
          item[4] = "".concat(supports);
        } else {
          item[1] = "@supports (".concat(item[4], ") {").concat(item[1], "}");
          item[4] = supports;
        }
      }
      list.push(item);
    }
  };
  return list;
};

/***/ },

/***/ 338
(__unused_webpack_module, exports, __webpack_require__) {

var __webpack_unused_export__;


var m = __webpack_require__(961);
if (true) {
  exports.H = m.createRoot;
  __webpack_unused_export__ = m.hydrateRoot;
} else // removed by dead control flow
{ var i; }


/***/ },

/***/ 354
(module) {



module.exports = function (item) {
  var content = item[1];
  var cssMapping = item[3];
  if (!cssMapping) {
    return content;
  }
  if (typeof btoa === "function") {
    var base64 = btoa(unescape(encodeURIComponent(JSON.stringify(cssMapping))));
    var data = "sourceMappingURL=data:application/json;charset=utf-8;base64,".concat(base64);
    var sourceMapping = "/*# ".concat(data, " */");
    return [content].concat([sourceMapping]).join("\n");
  }
  return [content].join("\n");
};

/***/ },

/***/ 463
(__unused_webpack_module, exports) {

/**
 * @license React
 * scheduler.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
function f(a,b){var c=a.length;a.push(b);a:for(;0<c;){var d=c-1>>>1,e=a[d];if(0<g(e,b))a[d]=b,a[c]=e,c=d;else break a}}function h(a){return 0===a.length?null:a[0]}function k(a){if(0===a.length)return null;var b=a[0],c=a.pop();if(c!==b){a[0]=c;a:for(var d=0,e=a.length,w=e>>>1;d<w;){var m=2*(d+1)-1,C=a[m],n=m+1,x=a[n];if(0>g(C,c))n<e&&0>g(x,C)?(a[d]=x,a[n]=c,d=n):(a[d]=C,a[m]=c,d=m);else if(n<e&&0>g(x,c))a[d]=x,a[n]=c,d=n;else break a}}return b}
function g(a,b){var c=a.sortIndex-b.sortIndex;return 0!==c?c:a.id-b.id}if("object"===typeof performance&&"function"===typeof performance.now){var l=performance;exports.unstable_now=function(){return l.now()}}else{var p=Date,q=p.now();exports.unstable_now=function(){return p.now()-q}}var r=[],t=[],u=1,v=null,y=3,z=!1,A=!1,B=!1,D="function"===typeof setTimeout?setTimeout:null,E="function"===typeof clearTimeout?clearTimeout:null,F="undefined"!==typeof setImmediate?setImmediate:null;
"undefined"!==typeof navigator&&void 0!==navigator.scheduling&&void 0!==navigator.scheduling.isInputPending&&navigator.scheduling.isInputPending.bind(navigator.scheduling);function G(a){for(var b=h(t);null!==b;){if(null===b.callback)k(t);else if(b.startTime<=a)k(t),b.sortIndex=b.expirationTime,f(r,b);else break;b=h(t)}}function H(a){B=!1;G(a);if(!A)if(null!==h(r))A=!0,I(J);else{var b=h(t);null!==b&&K(H,b.startTime-a)}}
function J(a,b){A=!1;B&&(B=!1,E(L),L=-1);z=!0;var c=y;try{G(b);for(v=h(r);null!==v&&(!(v.expirationTime>b)||a&&!M());){var d=v.callback;if("function"===typeof d){v.callback=null;y=v.priorityLevel;var e=d(v.expirationTime<=b);b=exports.unstable_now();"function"===typeof e?v.callback=e:v===h(r)&&k(r);G(b)}else k(r);v=h(r)}if(null!==v)var w=!0;else{var m=h(t);null!==m&&K(H,m.startTime-b);w=!1}return w}finally{v=null,y=c,z=!1}}var N=!1,O=null,L=-1,P=5,Q=-1;
function M(){return exports.unstable_now()-Q<P?!1:!0}function R(){if(null!==O){var a=exports.unstable_now();Q=a;var b=!0;try{b=O(!0,a)}finally{b?S():(N=!1,O=null)}}else N=!1}var S;if("function"===typeof F)S=function(){F(R)};else if("undefined"!==typeof MessageChannel){var T=new MessageChannel,U=T.port2;T.port1.onmessage=R;S=function(){U.postMessage(null)}}else S=function(){D(R,0)};function I(a){O=a;N||(N=!0,S())}function K(a,b){L=D(function(){a(exports.unstable_now())},b)}
exports.unstable_IdlePriority=5;exports.unstable_ImmediatePriority=1;exports.unstable_LowPriority=4;exports.unstable_NormalPriority=3;exports.unstable_Profiling=null;exports.unstable_UserBlockingPriority=2;exports.unstable_cancelCallback=function(a){a.callback=null};exports.unstable_continueExecution=function(){A||z||(A=!0,I(J))};
exports.unstable_forceFrameRate=function(a){0>a||125<a?console.error("forceFrameRate takes a positive int between 0 and 125, forcing frame rates higher than 125 fps is not supported"):P=0<a?Math.floor(1E3/a):5};exports.unstable_getCurrentPriorityLevel=function(){return y};exports.unstable_getFirstCallbackNode=function(){return h(r)};exports.unstable_next=function(a){switch(y){case 1:case 2:case 3:var b=3;break;default:b=y}var c=y;y=b;try{return a()}finally{y=c}};exports.unstable_pauseExecution=function(){};
exports.unstable_requestPaint=function(){};exports.unstable_runWithPriority=function(a,b){switch(a){case 1:case 2:case 3:case 4:case 5:break;default:a=3}var c=y;y=a;try{return b()}finally{y=c}};
exports.unstable_scheduleCallback=function(a,b,c){var d=exports.unstable_now();"object"===typeof c&&null!==c?(c=c.delay,c="number"===typeof c&&0<c?d+c:d):c=d;switch(a){case 1:var e=-1;break;case 2:e=250;break;case 5:e=1073741823;break;case 4:e=1E4;break;default:e=5E3}e=c+e;a={id:u++,callback:b,priorityLevel:a,startTime:c,expirationTime:e,sortIndex:-1};c>d?(a.sortIndex=c,f(t,a),null===h(r)&&a===h(t)&&(B?(E(L),L=-1):B=!0,K(H,c-d))):(a.sortIndex=e,f(r,a),A||z||(A=!0,I(J)));return a};
exports.unstable_shouldYield=M;exports.unstable_wrapCallback=function(a){var b=y;return function(){var c=y;y=b;try{return a.apply(this,arguments)}finally{y=c}}};


/***/ },

/***/ 540
(module) {



/* istanbul ignore next  */
function insertStyleElement(options) {
  var element = document.createElement("style");
  options.setAttributes(element, options.attributes);
  options.insert(element, options.options);
  return element;
}
module.exports = insertStyleElement;

/***/ },

/***/ 551
(__unused_webpack_module, exports, __webpack_require__) {

/**
 * @license React
 * react-dom.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
/*
 Modernizr 3.0.0pre (Custom Build) | MIT
*/
var aa=__webpack_require__(159),ca=__webpack_require__(982);function p(a){for(var b="https://reactjs.org/docs/error-decoder.html?invariant="+a,c=1;c<arguments.length;c++)b+="&args[]="+encodeURIComponent(arguments[c]);return"Minified React error #"+a+"; visit "+b+" for the full message or use the non-minified dev environment for full errors and additional helpful warnings."}var da=new Set,ea={};function fa(a,b){ha(a,b);ha(a+"Capture",b)}
function ha(a,b){ea[a]=b;for(a=0;a<b.length;a++)da.add(b[a])}
var ia=!("undefined"===typeof window||"undefined"===typeof window.document||"undefined"===typeof window.document.createElement),ja=Object.prototype.hasOwnProperty,ka=/^[:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD][:A-Z_a-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02FF\u0370-\u037D\u037F-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFD\-.0-9\u00B7\u0300-\u036F\u203F-\u2040]*$/,la=
{},ma={};function oa(a){if(ja.call(ma,a))return!0;if(ja.call(la,a))return!1;if(ka.test(a))return ma[a]=!0;la[a]=!0;return!1}function pa(a,b,c,d){if(null!==c&&0===c.type)return!1;switch(typeof b){case "function":case "symbol":return!0;case "boolean":if(d)return!1;if(null!==c)return!c.acceptsBooleans;a=a.toLowerCase().slice(0,5);return"data-"!==a&&"aria-"!==a;default:return!1}}
function qa(a,b,c,d){if(null===b||"undefined"===typeof b||pa(a,b,c,d))return!0;if(d)return!1;if(null!==c)switch(c.type){case 3:return!b;case 4:return!1===b;case 5:return isNaN(b);case 6:return isNaN(b)||1>b}return!1}function v(a,b,c,d,e,f,g){this.acceptsBooleans=2===b||3===b||4===b;this.attributeName=d;this.attributeNamespace=e;this.mustUseProperty=c;this.propertyName=a;this.type=b;this.sanitizeURL=f;this.removeEmptyString=g}var z={};
"children dangerouslySetInnerHTML defaultValue defaultChecked innerHTML suppressContentEditableWarning suppressHydrationWarning style".split(" ").forEach(function(a){z[a]=new v(a,0,!1,a,null,!1,!1)});[["acceptCharset","accept-charset"],["className","class"],["htmlFor","for"],["httpEquiv","http-equiv"]].forEach(function(a){var b=a[0];z[b]=new v(b,1,!1,a[1],null,!1,!1)});["contentEditable","draggable","spellCheck","value"].forEach(function(a){z[a]=new v(a,2,!1,a.toLowerCase(),null,!1,!1)});
["autoReverse","externalResourcesRequired","focusable","preserveAlpha"].forEach(function(a){z[a]=new v(a,2,!1,a,null,!1,!1)});"allowFullScreen async autoFocus autoPlay controls default defer disabled disablePictureInPicture disableRemotePlayback formNoValidate hidden loop noModule noValidate open playsInline readOnly required reversed scoped seamless itemScope".split(" ").forEach(function(a){z[a]=new v(a,3,!1,a.toLowerCase(),null,!1,!1)});
["checked","multiple","muted","selected"].forEach(function(a){z[a]=new v(a,3,!0,a,null,!1,!1)});["capture","download"].forEach(function(a){z[a]=new v(a,4,!1,a,null,!1,!1)});["cols","rows","size","span"].forEach(function(a){z[a]=new v(a,6,!1,a,null,!1,!1)});["rowSpan","start"].forEach(function(a){z[a]=new v(a,5,!1,a.toLowerCase(),null,!1,!1)});var ra=/[\-:]([a-z])/g;function sa(a){return a[1].toUpperCase()}
"accent-height alignment-baseline arabic-form baseline-shift cap-height clip-path clip-rule color-interpolation color-interpolation-filters color-profile color-rendering dominant-baseline enable-background fill-opacity fill-rule flood-color flood-opacity font-family font-size font-size-adjust font-stretch font-style font-variant font-weight glyph-name glyph-orientation-horizontal glyph-orientation-vertical horiz-adv-x horiz-origin-x image-rendering letter-spacing lighting-color marker-end marker-mid marker-start overline-position overline-thickness paint-order panose-1 pointer-events rendering-intent shape-rendering stop-color stop-opacity strikethrough-position strikethrough-thickness stroke-dasharray stroke-dashoffset stroke-linecap stroke-linejoin stroke-miterlimit stroke-opacity stroke-width text-anchor text-decoration text-rendering underline-position underline-thickness unicode-bidi unicode-range units-per-em v-alphabetic v-hanging v-ideographic v-mathematical vector-effect vert-adv-y vert-origin-x vert-origin-y word-spacing writing-mode xmlns:xlink x-height".split(" ").forEach(function(a){var b=a.replace(ra,
sa);z[b]=new v(b,1,!1,a,null,!1,!1)});"xlink:actuate xlink:arcrole xlink:role xlink:show xlink:title xlink:type".split(" ").forEach(function(a){var b=a.replace(ra,sa);z[b]=new v(b,1,!1,a,"http://www.w3.org/1999/xlink",!1,!1)});["xml:base","xml:lang","xml:space"].forEach(function(a){var b=a.replace(ra,sa);z[b]=new v(b,1,!1,a,"http://www.w3.org/XML/1998/namespace",!1,!1)});["tabIndex","crossOrigin"].forEach(function(a){z[a]=new v(a,1,!1,a.toLowerCase(),null,!1,!1)});
z.xlinkHref=new v("xlinkHref",1,!1,"xlink:href","http://www.w3.org/1999/xlink",!0,!1);["src","href","action","formAction"].forEach(function(a){z[a]=new v(a,1,!1,a.toLowerCase(),null,!0,!0)});
function ta(a,b,c,d){var e=z.hasOwnProperty(b)?z[b]:null;if(null!==e?0!==e.type:d||!(2<b.length)||"o"!==b[0]&&"O"!==b[0]||"n"!==b[1]&&"N"!==b[1])qa(b,c,e,d)&&(c=null),d||null===e?oa(b)&&(null===c?a.removeAttribute(b):a.setAttribute(b,""+c)):e.mustUseProperty?a[e.propertyName]=null===c?3===e.type?!1:"":c:(b=e.attributeName,d=e.attributeNamespace,null===c?a.removeAttribute(b):(e=e.type,c=3===e||4===e&&!0===c?"":""+c,d?a.setAttributeNS(d,b,c):a.setAttribute(b,c)))}
var ua=aa.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED,va=Symbol.for("react.element"),wa=Symbol.for("react.portal"),ya=Symbol.for("react.fragment"),za=Symbol.for("react.strict_mode"),Aa=Symbol.for("react.profiler"),Ba=Symbol.for("react.provider"),Ca=Symbol.for("react.context"),Da=Symbol.for("react.forward_ref"),Ea=Symbol.for("react.suspense"),Fa=Symbol.for("react.suspense_list"),Ga=Symbol.for("react.memo"),Ha=Symbol.for("react.lazy");Symbol.for("react.scope");Symbol.for("react.debug_trace_mode");
var Ia=Symbol.for("react.offscreen");Symbol.for("react.legacy_hidden");Symbol.for("react.cache");Symbol.for("react.tracing_marker");var Ja=Symbol.iterator;function Ka(a){if(null===a||"object"!==typeof a)return null;a=Ja&&a[Ja]||a["@@iterator"];return"function"===typeof a?a:null}var A=Object.assign,La;function Ma(a){if(void 0===La)try{throw Error();}catch(c){var b=c.stack.trim().match(/\n( *(at )?)/);La=b&&b[1]||""}return"\n"+La+a}var Na=!1;
function Oa(a,b){if(!a||Na)return"";Na=!0;var c=Error.prepareStackTrace;Error.prepareStackTrace=void 0;try{if(b)if(b=function(){throw Error();},Object.defineProperty(b.prototype,"props",{set:function(){throw Error();}}),"object"===typeof Reflect&&Reflect.construct){try{Reflect.construct(b,[])}catch(l){var d=l}Reflect.construct(a,[],b)}else{try{b.call()}catch(l){d=l}a.call(b.prototype)}else{try{throw Error();}catch(l){d=l}a()}}catch(l){if(l&&d&&"string"===typeof l.stack){for(var e=l.stack.split("\n"),
f=d.stack.split("\n"),g=e.length-1,h=f.length-1;1<=g&&0<=h&&e[g]!==f[h];)h--;for(;1<=g&&0<=h;g--,h--)if(e[g]!==f[h]){if(1!==g||1!==h){do if(g--,h--,0>h||e[g]!==f[h]){var k="\n"+e[g].replace(" at new "," at ");a.displayName&&k.includes("<anonymous>")&&(k=k.replace("<anonymous>",a.displayName));return k}while(1<=g&&0<=h)}break}}}finally{Na=!1,Error.prepareStackTrace=c}return(a=a?a.displayName||a.name:"")?Ma(a):""}
function Pa(a){switch(a.tag){case 5:return Ma(a.type);case 16:return Ma("Lazy");case 13:return Ma("Suspense");case 19:return Ma("SuspenseList");case 0:case 2:case 15:return a=Oa(a.type,!1),a;case 11:return a=Oa(a.type.render,!1),a;case 1:return a=Oa(a.type,!0),a;default:return""}}
function Qa(a){if(null==a)return null;if("function"===typeof a)return a.displayName||a.name||null;if("string"===typeof a)return a;switch(a){case ya:return"Fragment";case wa:return"Portal";case Aa:return"Profiler";case za:return"StrictMode";case Ea:return"Suspense";case Fa:return"SuspenseList"}if("object"===typeof a)switch(a.$$typeof){case Ca:return(a.displayName||"Context")+".Consumer";case Ba:return(a._context.displayName||"Context")+".Provider";case Da:var b=a.render;a=a.displayName;a||(a=b.displayName||
b.name||"",a=""!==a?"ForwardRef("+a+")":"ForwardRef");return a;case Ga:return b=a.displayName||null,null!==b?b:Qa(a.type)||"Memo";case Ha:b=a._payload;a=a._init;try{return Qa(a(b))}catch(c){}}return null}
function Ra(a){var b=a.type;switch(a.tag){case 24:return"Cache";case 9:return(b.displayName||"Context")+".Consumer";case 10:return(b._context.displayName||"Context")+".Provider";case 18:return"DehydratedFragment";case 11:return a=b.render,a=a.displayName||a.name||"",b.displayName||(""!==a?"ForwardRef("+a+")":"ForwardRef");case 7:return"Fragment";case 5:return b;case 4:return"Portal";case 3:return"Root";case 6:return"Text";case 16:return Qa(b);case 8:return b===za?"StrictMode":"Mode";case 22:return"Offscreen";
case 12:return"Profiler";case 21:return"Scope";case 13:return"Suspense";case 19:return"SuspenseList";case 25:return"TracingMarker";case 1:case 0:case 17:case 2:case 14:case 15:if("function"===typeof b)return b.displayName||b.name||null;if("string"===typeof b)return b}return null}function Sa(a){switch(typeof a){case "boolean":case "number":case "string":case "undefined":return a;case "object":return a;default:return""}}
function Ta(a){var b=a.type;return(a=a.nodeName)&&"input"===a.toLowerCase()&&("checkbox"===b||"radio"===b)}
function Ua(a){var b=Ta(a)?"checked":"value",c=Object.getOwnPropertyDescriptor(a.constructor.prototype,b),d=""+a[b];if(!a.hasOwnProperty(b)&&"undefined"!==typeof c&&"function"===typeof c.get&&"function"===typeof c.set){var e=c.get,f=c.set;Object.defineProperty(a,b,{configurable:!0,get:function(){return e.call(this)},set:function(a){d=""+a;f.call(this,a)}});Object.defineProperty(a,b,{enumerable:c.enumerable});return{getValue:function(){return d},setValue:function(a){d=""+a},stopTracking:function(){a._valueTracker=
null;delete a[b]}}}}function Va(a){a._valueTracker||(a._valueTracker=Ua(a))}function Wa(a){if(!a)return!1;var b=a._valueTracker;if(!b)return!0;var c=b.getValue();var d="";a&&(d=Ta(a)?a.checked?"true":"false":a.value);a=d;return a!==c?(b.setValue(a),!0):!1}function Xa(a){a=a||("undefined"!==typeof document?document:void 0);if("undefined"===typeof a)return null;try{return a.activeElement||a.body}catch(b){return a.body}}
function Ya(a,b){var c=b.checked;return A({},b,{defaultChecked:void 0,defaultValue:void 0,value:void 0,checked:null!=c?c:a._wrapperState.initialChecked})}function Za(a,b){var c=null==b.defaultValue?"":b.defaultValue,d=null!=b.checked?b.checked:b.defaultChecked;c=Sa(null!=b.value?b.value:c);a._wrapperState={initialChecked:d,initialValue:c,controlled:"checkbox"===b.type||"radio"===b.type?null!=b.checked:null!=b.value}}function ab(a,b){b=b.checked;null!=b&&ta(a,"checked",b,!1)}
function bb(a,b){ab(a,b);var c=Sa(b.value),d=b.type;if(null!=c)if("number"===d){if(0===c&&""===a.value||a.value!=c)a.value=""+c}else a.value!==""+c&&(a.value=""+c);else if("submit"===d||"reset"===d){a.removeAttribute("value");return}b.hasOwnProperty("value")?cb(a,b.type,c):b.hasOwnProperty("defaultValue")&&cb(a,b.type,Sa(b.defaultValue));null==b.checked&&null!=b.defaultChecked&&(a.defaultChecked=!!b.defaultChecked)}
function db(a,b,c){if(b.hasOwnProperty("value")||b.hasOwnProperty("defaultValue")){var d=b.type;if(!("submit"!==d&&"reset"!==d||void 0!==b.value&&null!==b.value))return;b=""+a._wrapperState.initialValue;c||b===a.value||(a.value=b);a.defaultValue=b}c=a.name;""!==c&&(a.name="");a.defaultChecked=!!a._wrapperState.initialChecked;""!==c&&(a.name=c)}
function cb(a,b,c){if("number"!==b||Xa(a.ownerDocument)!==a)null==c?a.defaultValue=""+a._wrapperState.initialValue:a.defaultValue!==""+c&&(a.defaultValue=""+c)}var eb=Array.isArray;
function fb(a,b,c,d){a=a.options;if(b){b={};for(var e=0;e<c.length;e++)b["$"+c[e]]=!0;for(c=0;c<a.length;c++)e=b.hasOwnProperty("$"+a[c].value),a[c].selected!==e&&(a[c].selected=e),e&&d&&(a[c].defaultSelected=!0)}else{c=""+Sa(c);b=null;for(e=0;e<a.length;e++){if(a[e].value===c){a[e].selected=!0;d&&(a[e].defaultSelected=!0);return}null!==b||a[e].disabled||(b=a[e])}null!==b&&(b.selected=!0)}}
function gb(a,b){if(null!=b.dangerouslySetInnerHTML)throw Error(p(91));return A({},b,{value:void 0,defaultValue:void 0,children:""+a._wrapperState.initialValue})}function hb(a,b){var c=b.value;if(null==c){c=b.children;b=b.defaultValue;if(null!=c){if(null!=b)throw Error(p(92));if(eb(c)){if(1<c.length)throw Error(p(93));c=c[0]}b=c}null==b&&(b="");c=b}a._wrapperState={initialValue:Sa(c)}}
function ib(a,b){var c=Sa(b.value),d=Sa(b.defaultValue);null!=c&&(c=""+c,c!==a.value&&(a.value=c),null==b.defaultValue&&a.defaultValue!==c&&(a.defaultValue=c));null!=d&&(a.defaultValue=""+d)}function jb(a){var b=a.textContent;b===a._wrapperState.initialValue&&""!==b&&null!==b&&(a.value=b)}function kb(a){switch(a){case "svg":return"http://www.w3.org/2000/svg";case "math":return"http://www.w3.org/1998/Math/MathML";default:return"http://www.w3.org/1999/xhtml"}}
function lb(a,b){return null==a||"http://www.w3.org/1999/xhtml"===a?kb(b):"http://www.w3.org/2000/svg"===a&&"foreignObject"===b?"http://www.w3.org/1999/xhtml":a}
var mb,nb=function(a){return"undefined"!==typeof MSApp&&MSApp.execUnsafeLocalFunction?function(b,c,d,e){MSApp.execUnsafeLocalFunction(function(){return a(b,c,d,e)})}:a}(function(a,b){if("http://www.w3.org/2000/svg"!==a.namespaceURI||"innerHTML"in a)a.innerHTML=b;else{mb=mb||document.createElement("div");mb.innerHTML="<svg>"+b.valueOf().toString()+"</svg>";for(b=mb.firstChild;a.firstChild;)a.removeChild(a.firstChild);for(;b.firstChild;)a.appendChild(b.firstChild)}});
function ob(a,b){if(b){var c=a.firstChild;if(c&&c===a.lastChild&&3===c.nodeType){c.nodeValue=b;return}}a.textContent=b}
var pb={animationIterationCount:!0,aspectRatio:!0,borderImageOutset:!0,borderImageSlice:!0,borderImageWidth:!0,boxFlex:!0,boxFlexGroup:!0,boxOrdinalGroup:!0,columnCount:!0,columns:!0,flex:!0,flexGrow:!0,flexPositive:!0,flexShrink:!0,flexNegative:!0,flexOrder:!0,gridArea:!0,gridRow:!0,gridRowEnd:!0,gridRowSpan:!0,gridRowStart:!0,gridColumn:!0,gridColumnEnd:!0,gridColumnSpan:!0,gridColumnStart:!0,fontWeight:!0,lineClamp:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,tabSize:!0,widows:!0,zIndex:!0,
zoom:!0,fillOpacity:!0,floodOpacity:!0,stopOpacity:!0,strokeDasharray:!0,strokeDashoffset:!0,strokeMiterlimit:!0,strokeOpacity:!0,strokeWidth:!0},qb=["Webkit","ms","Moz","O"];Object.keys(pb).forEach(function(a){qb.forEach(function(b){b=b+a.charAt(0).toUpperCase()+a.substring(1);pb[b]=pb[a]})});function rb(a,b,c){return null==b||"boolean"===typeof b||""===b?"":c||"number"!==typeof b||0===b||pb.hasOwnProperty(a)&&pb[a]?(""+b).trim():b+"px"}
function sb(a,b){a=a.style;for(var c in b)if(b.hasOwnProperty(c)){var d=0===c.indexOf("--"),e=rb(c,b[c],d);"float"===c&&(c="cssFloat");d?a.setProperty(c,e):a[c]=e}}var tb=A({menuitem:!0},{area:!0,base:!0,br:!0,col:!0,embed:!0,hr:!0,img:!0,input:!0,keygen:!0,link:!0,meta:!0,param:!0,source:!0,track:!0,wbr:!0});
function ub(a,b){if(b){if(tb[a]&&(null!=b.children||null!=b.dangerouslySetInnerHTML))throw Error(p(137,a));if(null!=b.dangerouslySetInnerHTML){if(null!=b.children)throw Error(p(60));if("object"!==typeof b.dangerouslySetInnerHTML||!("__html"in b.dangerouslySetInnerHTML))throw Error(p(61));}if(null!=b.style&&"object"!==typeof b.style)throw Error(p(62));}}
function vb(a,b){if(-1===a.indexOf("-"))return"string"===typeof b.is;switch(a){case "annotation-xml":case "color-profile":case "font-face":case "font-face-src":case "font-face-uri":case "font-face-format":case "font-face-name":case "missing-glyph":return!1;default:return!0}}var wb=null;function xb(a){a=a.target||a.srcElement||window;a.correspondingUseElement&&(a=a.correspondingUseElement);return 3===a.nodeType?a.parentNode:a}var yb=null,zb=null,Ab=null;
function Bb(a){if(a=Cb(a)){if("function"!==typeof yb)throw Error(p(280));var b=a.stateNode;b&&(b=Db(b),yb(a.stateNode,a.type,b))}}function Eb(a){zb?Ab?Ab.push(a):Ab=[a]:zb=a}function Fb(){if(zb){var a=zb,b=Ab;Ab=zb=null;Bb(a);if(b)for(a=0;a<b.length;a++)Bb(b[a])}}function Gb(a,b){return a(b)}function Hb(){}var Ib=!1;function Jb(a,b,c){if(Ib)return a(b,c);Ib=!0;try{return Gb(a,b,c)}finally{if(Ib=!1,null!==zb||null!==Ab)Hb(),Fb()}}
function Kb(a,b){var c=a.stateNode;if(null===c)return null;var d=Db(c);if(null===d)return null;c=d[b];a:switch(b){case "onClick":case "onClickCapture":case "onDoubleClick":case "onDoubleClickCapture":case "onMouseDown":case "onMouseDownCapture":case "onMouseMove":case "onMouseMoveCapture":case "onMouseUp":case "onMouseUpCapture":case "onMouseEnter":(d=!d.disabled)||(a=a.type,d=!("button"===a||"input"===a||"select"===a||"textarea"===a));a=!d;break a;default:a=!1}if(a)return null;if(c&&"function"!==
typeof c)throw Error(p(231,b,typeof c));return c}var Lb=!1;if(ia)try{var Mb={};Object.defineProperty(Mb,"passive",{get:function(){Lb=!0}});window.addEventListener("test",Mb,Mb);window.removeEventListener("test",Mb,Mb)}catch(a){Lb=!1}function Nb(a,b,c,d,e,f,g,h,k){var l=Array.prototype.slice.call(arguments,3);try{b.apply(c,l)}catch(m){this.onError(m)}}var Ob=!1,Pb=null,Qb=!1,Rb=null,Sb={onError:function(a){Ob=!0;Pb=a}};function Tb(a,b,c,d,e,f,g,h,k){Ob=!1;Pb=null;Nb.apply(Sb,arguments)}
function Ub(a,b,c,d,e,f,g,h,k){Tb.apply(this,arguments);if(Ob){if(Ob){var l=Pb;Ob=!1;Pb=null}else throw Error(p(198));Qb||(Qb=!0,Rb=l)}}function Vb(a){var b=a,c=a;if(a.alternate)for(;b.return;)b=b.return;else{a=b;do b=a,0!==(b.flags&4098)&&(c=b.return),a=b.return;while(a)}return 3===b.tag?c:null}function Wb(a){if(13===a.tag){var b=a.memoizedState;null===b&&(a=a.alternate,null!==a&&(b=a.memoizedState));if(null!==b)return b.dehydrated}return null}function Xb(a){if(Vb(a)!==a)throw Error(p(188));}
function Yb(a){var b=a.alternate;if(!b){b=Vb(a);if(null===b)throw Error(p(188));return b!==a?null:a}for(var c=a,d=b;;){var e=c.return;if(null===e)break;var f=e.alternate;if(null===f){d=e.return;if(null!==d){c=d;continue}break}if(e.child===f.child){for(f=e.child;f;){if(f===c)return Xb(e),a;if(f===d)return Xb(e),b;f=f.sibling}throw Error(p(188));}if(c.return!==d.return)c=e,d=f;else{for(var g=!1,h=e.child;h;){if(h===c){g=!0;c=e;d=f;break}if(h===d){g=!0;d=e;c=f;break}h=h.sibling}if(!g){for(h=f.child;h;){if(h===
c){g=!0;c=f;d=e;break}if(h===d){g=!0;d=f;c=e;break}h=h.sibling}if(!g)throw Error(p(189));}}if(c.alternate!==d)throw Error(p(190));}if(3!==c.tag)throw Error(p(188));return c.stateNode.current===c?a:b}function Zb(a){a=Yb(a);return null!==a?$b(a):null}function $b(a){if(5===a.tag||6===a.tag)return a;for(a=a.child;null!==a;){var b=$b(a);if(null!==b)return b;a=a.sibling}return null}
var ac=ca.unstable_scheduleCallback,bc=ca.unstable_cancelCallback,cc=ca.unstable_shouldYield,dc=ca.unstable_requestPaint,B=ca.unstable_now,ec=ca.unstable_getCurrentPriorityLevel,fc=ca.unstable_ImmediatePriority,gc=ca.unstable_UserBlockingPriority,hc=ca.unstable_NormalPriority,ic=ca.unstable_LowPriority,jc=ca.unstable_IdlePriority,kc=null,lc=null;function mc(a){if(lc&&"function"===typeof lc.onCommitFiberRoot)try{lc.onCommitFiberRoot(kc,a,void 0,128===(a.current.flags&128))}catch(b){}}
var oc=Math.clz32?Math.clz32:nc,pc=Math.log,qc=Math.LN2;function nc(a){a>>>=0;return 0===a?32:31-(pc(a)/qc|0)|0}var rc=64,sc=4194304;
function tc(a){switch(a&-a){case 1:return 1;case 2:return 2;case 4:return 4;case 8:return 8;case 16:return 16;case 32:return 32;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return a&4194240;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return a&130023424;case 134217728:return 134217728;case 268435456:return 268435456;case 536870912:return 536870912;case 1073741824:return 1073741824;
default:return a}}function uc(a,b){var c=a.pendingLanes;if(0===c)return 0;var d=0,e=a.suspendedLanes,f=a.pingedLanes,g=c&268435455;if(0!==g){var h=g&~e;0!==h?d=tc(h):(f&=g,0!==f&&(d=tc(f)))}else g=c&~e,0!==g?d=tc(g):0!==f&&(d=tc(f));if(0===d)return 0;if(0!==b&&b!==d&&0===(b&e)&&(e=d&-d,f=b&-b,e>=f||16===e&&0!==(f&4194240)))return b;0!==(d&4)&&(d|=c&16);b=a.entangledLanes;if(0!==b)for(a=a.entanglements,b&=d;0<b;)c=31-oc(b),e=1<<c,d|=a[c],b&=~e;return d}
function vc(a,b){switch(a){case 1:case 2:case 4:return b+250;case 8:case 16:case 32:case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:return b+5E3;case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:return-1;case 134217728:case 268435456:case 536870912:case 1073741824:return-1;default:return-1}}
function wc(a,b){for(var c=a.suspendedLanes,d=a.pingedLanes,e=a.expirationTimes,f=a.pendingLanes;0<f;){var g=31-oc(f),h=1<<g,k=e[g];if(-1===k){if(0===(h&c)||0!==(h&d))e[g]=vc(h,b)}else k<=b&&(a.expiredLanes|=h);f&=~h}}function xc(a){a=a.pendingLanes&-1073741825;return 0!==a?a:a&1073741824?1073741824:0}function yc(){var a=rc;rc<<=1;0===(rc&4194240)&&(rc=64);return a}function zc(a){for(var b=[],c=0;31>c;c++)b.push(a);return b}
function Ac(a,b,c){a.pendingLanes|=b;536870912!==b&&(a.suspendedLanes=0,a.pingedLanes=0);a=a.eventTimes;b=31-oc(b);a[b]=c}function Bc(a,b){var c=a.pendingLanes&~b;a.pendingLanes=b;a.suspendedLanes=0;a.pingedLanes=0;a.expiredLanes&=b;a.mutableReadLanes&=b;a.entangledLanes&=b;b=a.entanglements;var d=a.eventTimes;for(a=a.expirationTimes;0<c;){var e=31-oc(c),f=1<<e;b[e]=0;d[e]=-1;a[e]=-1;c&=~f}}
function Cc(a,b){var c=a.entangledLanes|=b;for(a=a.entanglements;c;){var d=31-oc(c),e=1<<d;e&b|a[d]&b&&(a[d]|=b);c&=~e}}var C=0;function Dc(a){a&=-a;return 1<a?4<a?0!==(a&268435455)?16:536870912:4:1}var Ec,Fc,Gc,Hc,Ic,Jc=!1,Kc=[],Lc=null,Mc=null,Nc=null,Oc=new Map,Pc=new Map,Qc=[],Rc="mousedown mouseup touchcancel touchend touchstart auxclick dblclick pointercancel pointerdown pointerup dragend dragstart drop compositionend compositionstart keydown keypress keyup input textInput copy cut paste click change contextmenu reset submit".split(" ");
function Sc(a,b){switch(a){case "focusin":case "focusout":Lc=null;break;case "dragenter":case "dragleave":Mc=null;break;case "mouseover":case "mouseout":Nc=null;break;case "pointerover":case "pointerout":Oc.delete(b.pointerId);break;case "gotpointercapture":case "lostpointercapture":Pc.delete(b.pointerId)}}
function Tc(a,b,c,d,e,f){if(null===a||a.nativeEvent!==f)return a={blockedOn:b,domEventName:c,eventSystemFlags:d,nativeEvent:f,targetContainers:[e]},null!==b&&(b=Cb(b),null!==b&&Fc(b)),a;a.eventSystemFlags|=d;b=a.targetContainers;null!==e&&-1===b.indexOf(e)&&b.push(e);return a}
function Uc(a,b,c,d,e){switch(b){case "focusin":return Lc=Tc(Lc,a,b,c,d,e),!0;case "dragenter":return Mc=Tc(Mc,a,b,c,d,e),!0;case "mouseover":return Nc=Tc(Nc,a,b,c,d,e),!0;case "pointerover":var f=e.pointerId;Oc.set(f,Tc(Oc.get(f)||null,a,b,c,d,e));return!0;case "gotpointercapture":return f=e.pointerId,Pc.set(f,Tc(Pc.get(f)||null,a,b,c,d,e)),!0}return!1}
function Vc(a){var b=Wc(a.target);if(null!==b){var c=Vb(b);if(null!==c)if(b=c.tag,13===b){if(b=Wb(c),null!==b){a.blockedOn=b;Ic(a.priority,function(){Gc(c)});return}}else if(3===b&&c.stateNode.current.memoizedState.isDehydrated){a.blockedOn=3===c.tag?c.stateNode.containerInfo:null;return}}a.blockedOn=null}
function Xc(a){if(null!==a.blockedOn)return!1;for(var b=a.targetContainers;0<b.length;){var c=Yc(a.domEventName,a.eventSystemFlags,b[0],a.nativeEvent);if(null===c){c=a.nativeEvent;var d=new c.constructor(c.type,c);wb=d;c.target.dispatchEvent(d);wb=null}else return b=Cb(c),null!==b&&Fc(b),a.blockedOn=c,!1;b.shift()}return!0}function Zc(a,b,c){Xc(a)&&c.delete(b)}function $c(){Jc=!1;null!==Lc&&Xc(Lc)&&(Lc=null);null!==Mc&&Xc(Mc)&&(Mc=null);null!==Nc&&Xc(Nc)&&(Nc=null);Oc.forEach(Zc);Pc.forEach(Zc)}
function ad(a,b){a.blockedOn===b&&(a.blockedOn=null,Jc||(Jc=!0,ca.unstable_scheduleCallback(ca.unstable_NormalPriority,$c)))}
function bd(a){function b(b){return ad(b,a)}if(0<Kc.length){ad(Kc[0],a);for(var c=1;c<Kc.length;c++){var d=Kc[c];d.blockedOn===a&&(d.blockedOn=null)}}null!==Lc&&ad(Lc,a);null!==Mc&&ad(Mc,a);null!==Nc&&ad(Nc,a);Oc.forEach(b);Pc.forEach(b);for(c=0;c<Qc.length;c++)d=Qc[c],d.blockedOn===a&&(d.blockedOn=null);for(;0<Qc.length&&(c=Qc[0],null===c.blockedOn);)Vc(c),null===c.blockedOn&&Qc.shift()}var cd=ua.ReactCurrentBatchConfig,dd=!0;
function ed(a,b,c,d){var e=C,f=cd.transition;cd.transition=null;try{C=1,fd(a,b,c,d)}finally{C=e,cd.transition=f}}function gd(a,b,c,d){var e=C,f=cd.transition;cd.transition=null;try{C=4,fd(a,b,c,d)}finally{C=e,cd.transition=f}}
function fd(a,b,c,d){if(dd){var e=Yc(a,b,c,d);if(null===e)hd(a,b,d,id,c),Sc(a,d);else if(Uc(e,a,b,c,d))d.stopPropagation();else if(Sc(a,d),b&4&&-1<Rc.indexOf(a)){for(;null!==e;){var f=Cb(e);null!==f&&Ec(f);f=Yc(a,b,c,d);null===f&&hd(a,b,d,id,c);if(f===e)break;e=f}null!==e&&d.stopPropagation()}else hd(a,b,d,null,c)}}var id=null;
function Yc(a,b,c,d){id=null;a=xb(d);a=Wc(a);if(null!==a)if(b=Vb(a),null===b)a=null;else if(c=b.tag,13===c){a=Wb(b);if(null!==a)return a;a=null}else if(3===c){if(b.stateNode.current.memoizedState.isDehydrated)return 3===b.tag?b.stateNode.containerInfo:null;a=null}else b!==a&&(a=null);id=a;return null}
function jd(a){switch(a){case "cancel":case "click":case "close":case "contextmenu":case "copy":case "cut":case "auxclick":case "dblclick":case "dragend":case "dragstart":case "drop":case "focusin":case "focusout":case "input":case "invalid":case "keydown":case "keypress":case "keyup":case "mousedown":case "mouseup":case "paste":case "pause":case "play":case "pointercancel":case "pointerdown":case "pointerup":case "ratechange":case "reset":case "resize":case "seeked":case "submit":case "touchcancel":case "touchend":case "touchstart":case "volumechange":case "change":case "selectionchange":case "textInput":case "compositionstart":case "compositionend":case "compositionupdate":case "beforeblur":case "afterblur":case "beforeinput":case "blur":case "fullscreenchange":case "focus":case "hashchange":case "popstate":case "select":case "selectstart":return 1;case "drag":case "dragenter":case "dragexit":case "dragleave":case "dragover":case "mousemove":case "mouseout":case "mouseover":case "pointermove":case "pointerout":case "pointerover":case "scroll":case "toggle":case "touchmove":case "wheel":case "mouseenter":case "mouseleave":case "pointerenter":case "pointerleave":return 4;
case "message":switch(ec()){case fc:return 1;case gc:return 4;case hc:case ic:return 16;case jc:return 536870912;default:return 16}default:return 16}}var kd=null,ld=null,md=null;function nd(){if(md)return md;var a,b=ld,c=b.length,d,e="value"in kd?kd.value:kd.textContent,f=e.length;for(a=0;a<c&&b[a]===e[a];a++);var g=c-a;for(d=1;d<=g&&b[c-d]===e[f-d];d++);return md=e.slice(a,1<d?1-d:void 0)}
function od(a){var b=a.keyCode;"charCode"in a?(a=a.charCode,0===a&&13===b&&(a=13)):a=b;10===a&&(a=13);return 32<=a||13===a?a:0}function pd(){return!0}function qd(){return!1}
function rd(a){function b(b,d,e,f,g){this._reactName=b;this._targetInst=e;this.type=d;this.nativeEvent=f;this.target=g;this.currentTarget=null;for(var c in a)a.hasOwnProperty(c)&&(b=a[c],this[c]=b?b(f):f[c]);this.isDefaultPrevented=(null!=f.defaultPrevented?f.defaultPrevented:!1===f.returnValue)?pd:qd;this.isPropagationStopped=qd;return this}A(b.prototype,{preventDefault:function(){this.defaultPrevented=!0;var a=this.nativeEvent;a&&(a.preventDefault?a.preventDefault():"unknown"!==typeof a.returnValue&&
(a.returnValue=!1),this.isDefaultPrevented=pd)},stopPropagation:function(){var a=this.nativeEvent;a&&(a.stopPropagation?a.stopPropagation():"unknown"!==typeof a.cancelBubble&&(a.cancelBubble=!0),this.isPropagationStopped=pd)},persist:function(){},isPersistent:pd});return b}
var sd={eventPhase:0,bubbles:0,cancelable:0,timeStamp:function(a){return a.timeStamp||Date.now()},defaultPrevented:0,isTrusted:0},td=rd(sd),ud=A({},sd,{view:0,detail:0}),vd=rd(ud),wd,xd,yd,Ad=A({},ud,{screenX:0,screenY:0,clientX:0,clientY:0,pageX:0,pageY:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,getModifierState:zd,button:0,buttons:0,relatedTarget:function(a){return void 0===a.relatedTarget?a.fromElement===a.srcElement?a.toElement:a.fromElement:a.relatedTarget},movementX:function(a){if("movementX"in
a)return a.movementX;a!==yd&&(yd&&"mousemove"===a.type?(wd=a.screenX-yd.screenX,xd=a.screenY-yd.screenY):xd=wd=0,yd=a);return wd},movementY:function(a){return"movementY"in a?a.movementY:xd}}),Bd=rd(Ad),Cd=A({},Ad,{dataTransfer:0}),Dd=rd(Cd),Ed=A({},ud,{relatedTarget:0}),Fd=rd(Ed),Gd=A({},sd,{animationName:0,elapsedTime:0,pseudoElement:0}),Hd=rd(Gd),Id=A({},sd,{clipboardData:function(a){return"clipboardData"in a?a.clipboardData:window.clipboardData}}),Jd=rd(Id),Kd=A({},sd,{data:0}),Ld=rd(Kd),Md={Esc:"Escape",
Spacebar:" ",Left:"ArrowLeft",Up:"ArrowUp",Right:"ArrowRight",Down:"ArrowDown",Del:"Delete",Win:"OS",Menu:"ContextMenu",Apps:"ContextMenu",Scroll:"ScrollLock",MozPrintableKey:"Unidentified"},Nd={8:"Backspace",9:"Tab",12:"Clear",13:"Enter",16:"Shift",17:"Control",18:"Alt",19:"Pause",20:"CapsLock",27:"Escape",32:" ",33:"PageUp",34:"PageDown",35:"End",36:"Home",37:"ArrowLeft",38:"ArrowUp",39:"ArrowRight",40:"ArrowDown",45:"Insert",46:"Delete",112:"F1",113:"F2",114:"F3",115:"F4",116:"F5",117:"F6",118:"F7",
119:"F8",120:"F9",121:"F10",122:"F11",123:"F12",144:"NumLock",145:"ScrollLock",224:"Meta"},Od={Alt:"altKey",Control:"ctrlKey",Meta:"metaKey",Shift:"shiftKey"};function Pd(a){var b=this.nativeEvent;return b.getModifierState?b.getModifierState(a):(a=Od[a])?!!b[a]:!1}function zd(){return Pd}
var Qd=A({},ud,{key:function(a){if(a.key){var b=Md[a.key]||a.key;if("Unidentified"!==b)return b}return"keypress"===a.type?(a=od(a),13===a?"Enter":String.fromCharCode(a)):"keydown"===a.type||"keyup"===a.type?Nd[a.keyCode]||"Unidentified":""},code:0,location:0,ctrlKey:0,shiftKey:0,altKey:0,metaKey:0,repeat:0,locale:0,getModifierState:zd,charCode:function(a){return"keypress"===a.type?od(a):0},keyCode:function(a){return"keydown"===a.type||"keyup"===a.type?a.keyCode:0},which:function(a){return"keypress"===
a.type?od(a):"keydown"===a.type||"keyup"===a.type?a.keyCode:0}}),Rd=rd(Qd),Sd=A({},Ad,{pointerId:0,width:0,height:0,pressure:0,tangentialPressure:0,tiltX:0,tiltY:0,twist:0,pointerType:0,isPrimary:0}),Td=rd(Sd),Ud=A({},ud,{touches:0,targetTouches:0,changedTouches:0,altKey:0,metaKey:0,ctrlKey:0,shiftKey:0,getModifierState:zd}),Vd=rd(Ud),Wd=A({},sd,{propertyName:0,elapsedTime:0,pseudoElement:0}),Xd=rd(Wd),Yd=A({},Ad,{deltaX:function(a){return"deltaX"in a?a.deltaX:"wheelDeltaX"in a?-a.wheelDeltaX:0},
deltaY:function(a){return"deltaY"in a?a.deltaY:"wheelDeltaY"in a?-a.wheelDeltaY:"wheelDelta"in a?-a.wheelDelta:0},deltaZ:0,deltaMode:0}),Zd=rd(Yd),$d=[9,13,27,32],ae=ia&&"CompositionEvent"in window,be=null;ia&&"documentMode"in document&&(be=document.documentMode);var ce=ia&&"TextEvent"in window&&!be,de=ia&&(!ae||be&&8<be&&11>=be),ee=String.fromCharCode(32),fe=!1;
function ge(a,b){switch(a){case "keyup":return-1!==$d.indexOf(b.keyCode);case "keydown":return 229!==b.keyCode;case "keypress":case "mousedown":case "focusout":return!0;default:return!1}}function he(a){a=a.detail;return"object"===typeof a&&"data"in a?a.data:null}var ie=!1;function je(a,b){switch(a){case "compositionend":return he(b);case "keypress":if(32!==b.which)return null;fe=!0;return ee;case "textInput":return a=b.data,a===ee&&fe?null:a;default:return null}}
function ke(a,b){if(ie)return"compositionend"===a||!ae&&ge(a,b)?(a=nd(),md=ld=kd=null,ie=!1,a):null;switch(a){case "paste":return null;case "keypress":if(!(b.ctrlKey||b.altKey||b.metaKey)||b.ctrlKey&&b.altKey){if(b.char&&1<b.char.length)return b.char;if(b.which)return String.fromCharCode(b.which)}return null;case "compositionend":return de&&"ko"!==b.locale?null:b.data;default:return null}}
var le={color:!0,date:!0,datetime:!0,"datetime-local":!0,email:!0,month:!0,number:!0,password:!0,range:!0,search:!0,tel:!0,text:!0,time:!0,url:!0,week:!0};function me(a){var b=a&&a.nodeName&&a.nodeName.toLowerCase();return"input"===b?!!le[a.type]:"textarea"===b?!0:!1}function ne(a,b,c,d){Eb(d);b=oe(b,"onChange");0<b.length&&(c=new td("onChange","change",null,c,d),a.push({event:c,listeners:b}))}var pe=null,qe=null;function re(a){se(a,0)}function te(a){var b=ue(a);if(Wa(b))return a}
function ve(a,b){if("change"===a)return b}var we=!1;if(ia){var xe;if(ia){var ye="oninput"in document;if(!ye){var ze=document.createElement("div");ze.setAttribute("oninput","return;");ye="function"===typeof ze.oninput}xe=ye}else xe=!1;we=xe&&(!document.documentMode||9<document.documentMode)}function Ae(){pe&&(pe.detachEvent("onpropertychange",Be),qe=pe=null)}function Be(a){if("value"===a.propertyName&&te(qe)){var b=[];ne(b,qe,a,xb(a));Jb(re,b)}}
function Ce(a,b,c){"focusin"===a?(Ae(),pe=b,qe=c,pe.attachEvent("onpropertychange",Be)):"focusout"===a&&Ae()}function De(a){if("selectionchange"===a||"keyup"===a||"keydown"===a)return te(qe)}function Ee(a,b){if("click"===a)return te(b)}function Fe(a,b){if("input"===a||"change"===a)return te(b)}function Ge(a,b){return a===b&&(0!==a||1/a===1/b)||a!==a&&b!==b}var He="function"===typeof Object.is?Object.is:Ge;
function Ie(a,b){if(He(a,b))return!0;if("object"!==typeof a||null===a||"object"!==typeof b||null===b)return!1;var c=Object.keys(a),d=Object.keys(b);if(c.length!==d.length)return!1;for(d=0;d<c.length;d++){var e=c[d];if(!ja.call(b,e)||!He(a[e],b[e]))return!1}return!0}function Je(a){for(;a&&a.firstChild;)a=a.firstChild;return a}
function Ke(a,b){var c=Je(a);a=0;for(var d;c;){if(3===c.nodeType){d=a+c.textContent.length;if(a<=b&&d>=b)return{node:c,offset:b-a};a=d}a:{for(;c;){if(c.nextSibling){c=c.nextSibling;break a}c=c.parentNode}c=void 0}c=Je(c)}}function Le(a,b){return a&&b?a===b?!0:a&&3===a.nodeType?!1:b&&3===b.nodeType?Le(a,b.parentNode):"contains"in a?a.contains(b):a.compareDocumentPosition?!!(a.compareDocumentPosition(b)&16):!1:!1}
function Me(){for(var a=window,b=Xa();b instanceof a.HTMLIFrameElement;){try{var c="string"===typeof b.contentWindow.location.href}catch(d){c=!1}if(c)a=b.contentWindow;else break;b=Xa(a.document)}return b}function Ne(a){var b=a&&a.nodeName&&a.nodeName.toLowerCase();return b&&("input"===b&&("text"===a.type||"search"===a.type||"tel"===a.type||"url"===a.type||"password"===a.type)||"textarea"===b||"true"===a.contentEditable)}
function Oe(a){var b=Me(),c=a.focusedElem,d=a.selectionRange;if(b!==c&&c&&c.ownerDocument&&Le(c.ownerDocument.documentElement,c)){if(null!==d&&Ne(c))if(b=d.start,a=d.end,void 0===a&&(a=b),"selectionStart"in c)c.selectionStart=b,c.selectionEnd=Math.min(a,c.value.length);else if(a=(b=c.ownerDocument||document)&&b.defaultView||window,a.getSelection){a=a.getSelection();var e=c.textContent.length,f=Math.min(d.start,e);d=void 0===d.end?f:Math.min(d.end,e);!a.extend&&f>d&&(e=d,d=f,f=e);e=Ke(c,f);var g=Ke(c,
d);e&&g&&(1!==a.rangeCount||a.anchorNode!==e.node||a.anchorOffset!==e.offset||a.focusNode!==g.node||a.focusOffset!==g.offset)&&(b=b.createRange(),b.setStart(e.node,e.offset),a.removeAllRanges(),f>d?(a.addRange(b),a.extend(g.node,g.offset)):(b.setEnd(g.node,g.offset),a.addRange(b)))}b=[];for(a=c;a=a.parentNode;)1===a.nodeType&&b.push({element:a,left:a.scrollLeft,top:a.scrollTop});"function"===typeof c.focus&&c.focus();for(c=0;c<b.length;c++)a=b[c],a.element.scrollLeft=a.left,a.element.scrollTop=a.top}}
var Pe=ia&&"documentMode"in document&&11>=document.documentMode,Qe=null,Re=null,Se=null,Te=!1;
function Ue(a,b,c){var d=c.window===c?c.document:9===c.nodeType?c:c.ownerDocument;Te||null==Qe||Qe!==Xa(d)||(d=Qe,"selectionStart"in d&&Ne(d)?d={start:d.selectionStart,end:d.selectionEnd}:(d=(d.ownerDocument&&d.ownerDocument.defaultView||window).getSelection(),d={anchorNode:d.anchorNode,anchorOffset:d.anchorOffset,focusNode:d.focusNode,focusOffset:d.focusOffset}),Se&&Ie(Se,d)||(Se=d,d=oe(Re,"onSelect"),0<d.length&&(b=new td("onSelect","select",null,b,c),a.push({event:b,listeners:d}),b.target=Qe)))}
function Ve(a,b){var c={};c[a.toLowerCase()]=b.toLowerCase();c["Webkit"+a]="webkit"+b;c["Moz"+a]="moz"+b;return c}var We={animationend:Ve("Animation","AnimationEnd"),animationiteration:Ve("Animation","AnimationIteration"),animationstart:Ve("Animation","AnimationStart"),transitionend:Ve("Transition","TransitionEnd")},Xe={},Ye={};
ia&&(Ye=document.createElement("div").style,"AnimationEvent"in window||(delete We.animationend.animation,delete We.animationiteration.animation,delete We.animationstart.animation),"TransitionEvent"in window||delete We.transitionend.transition);function Ze(a){if(Xe[a])return Xe[a];if(!We[a])return a;var b=We[a],c;for(c in b)if(b.hasOwnProperty(c)&&c in Ye)return Xe[a]=b[c];return a}var $e=Ze("animationend"),af=Ze("animationiteration"),bf=Ze("animationstart"),cf=Ze("transitionend"),df=new Map,ef="abort auxClick cancel canPlay canPlayThrough click close contextMenu copy cut drag dragEnd dragEnter dragExit dragLeave dragOver dragStart drop durationChange emptied encrypted ended error gotPointerCapture input invalid keyDown keyPress keyUp load loadedData loadedMetadata loadStart lostPointerCapture mouseDown mouseMove mouseOut mouseOver mouseUp paste pause play playing pointerCancel pointerDown pointerMove pointerOut pointerOver pointerUp progress rateChange reset resize seeked seeking stalled submit suspend timeUpdate touchCancel touchEnd touchStart volumeChange scroll toggle touchMove waiting wheel".split(" ");
function ff(a,b){df.set(a,b);fa(b,[a])}for(var gf=0;gf<ef.length;gf++){var hf=ef[gf],jf=hf.toLowerCase(),kf=hf[0].toUpperCase()+hf.slice(1);ff(jf,"on"+kf)}ff($e,"onAnimationEnd");ff(af,"onAnimationIteration");ff(bf,"onAnimationStart");ff("dblclick","onDoubleClick");ff("focusin","onFocus");ff("focusout","onBlur");ff(cf,"onTransitionEnd");ha("onMouseEnter",["mouseout","mouseover"]);ha("onMouseLeave",["mouseout","mouseover"]);ha("onPointerEnter",["pointerout","pointerover"]);
ha("onPointerLeave",["pointerout","pointerover"]);fa("onChange","change click focusin focusout input keydown keyup selectionchange".split(" "));fa("onSelect","focusout contextmenu dragend focusin keydown keyup mousedown mouseup selectionchange".split(" "));fa("onBeforeInput",["compositionend","keypress","textInput","paste"]);fa("onCompositionEnd","compositionend focusout keydown keypress keyup mousedown".split(" "));fa("onCompositionStart","compositionstart focusout keydown keypress keyup mousedown".split(" "));
fa("onCompositionUpdate","compositionupdate focusout keydown keypress keyup mousedown".split(" "));var lf="abort canplay canplaythrough durationchange emptied encrypted ended error loadeddata loadedmetadata loadstart pause play playing progress ratechange resize seeked seeking stalled suspend timeupdate volumechange waiting".split(" "),mf=new Set("cancel close invalid load scroll toggle".split(" ").concat(lf));
function nf(a,b,c){var d=a.type||"unknown-event";a.currentTarget=c;Ub(d,b,void 0,a);a.currentTarget=null}
function se(a,b){b=0!==(b&4);for(var c=0;c<a.length;c++){var d=a[c],e=d.event;d=d.listeners;a:{var f=void 0;if(b)for(var g=d.length-1;0<=g;g--){var h=d[g],k=h.instance,l=h.currentTarget;h=h.listener;if(k!==f&&e.isPropagationStopped())break a;nf(e,h,l);f=k}else for(g=0;g<d.length;g++){h=d[g];k=h.instance;l=h.currentTarget;h=h.listener;if(k!==f&&e.isPropagationStopped())break a;nf(e,h,l);f=k}}}if(Qb)throw a=Rb,Qb=!1,Rb=null,a;}
function D(a,b){var c=b[of];void 0===c&&(c=b[of]=new Set);var d=a+"__bubble";c.has(d)||(pf(b,a,2,!1),c.add(d))}function qf(a,b,c){var d=0;b&&(d|=4);pf(c,a,d,b)}var rf="_reactListening"+Math.random().toString(36).slice(2);function sf(a){if(!a[rf]){a[rf]=!0;da.forEach(function(b){"selectionchange"!==b&&(mf.has(b)||qf(b,!1,a),qf(b,!0,a))});var b=9===a.nodeType?a:a.ownerDocument;null===b||b[rf]||(b[rf]=!0,qf("selectionchange",!1,b))}}
function pf(a,b,c,d){switch(jd(b)){case 1:var e=ed;break;case 4:e=gd;break;default:e=fd}c=e.bind(null,b,c,a);e=void 0;!Lb||"touchstart"!==b&&"touchmove"!==b&&"wheel"!==b||(e=!0);d?void 0!==e?a.addEventListener(b,c,{capture:!0,passive:e}):a.addEventListener(b,c,!0):void 0!==e?a.addEventListener(b,c,{passive:e}):a.addEventListener(b,c,!1)}
function hd(a,b,c,d,e){var f=d;if(0===(b&1)&&0===(b&2)&&null!==d)a:for(;;){if(null===d)return;var g=d.tag;if(3===g||4===g){var h=d.stateNode.containerInfo;if(h===e||8===h.nodeType&&h.parentNode===e)break;if(4===g)for(g=d.return;null!==g;){var k=g.tag;if(3===k||4===k)if(k=g.stateNode.containerInfo,k===e||8===k.nodeType&&k.parentNode===e)return;g=g.return}for(;null!==h;){g=Wc(h);if(null===g)return;k=g.tag;if(5===k||6===k){d=f=g;continue a}h=h.parentNode}}d=d.return}Jb(function(){var d=f,e=xb(c),g=[];
a:{var h=df.get(a);if(void 0!==h){var k=td,n=a;switch(a){case "keypress":if(0===od(c))break a;case "keydown":case "keyup":k=Rd;break;case "focusin":n="focus";k=Fd;break;case "focusout":n="blur";k=Fd;break;case "beforeblur":case "afterblur":k=Fd;break;case "click":if(2===c.button)break a;case "auxclick":case "dblclick":case "mousedown":case "mousemove":case "mouseup":case "mouseout":case "mouseover":case "contextmenu":k=Bd;break;case "drag":case "dragend":case "dragenter":case "dragexit":case "dragleave":case "dragover":case "dragstart":case "drop":k=
Dd;break;case "touchcancel":case "touchend":case "touchmove":case "touchstart":k=Vd;break;case $e:case af:case bf:k=Hd;break;case cf:k=Xd;break;case "scroll":k=vd;break;case "wheel":k=Zd;break;case "copy":case "cut":case "paste":k=Jd;break;case "gotpointercapture":case "lostpointercapture":case "pointercancel":case "pointerdown":case "pointermove":case "pointerout":case "pointerover":case "pointerup":k=Td}var t=0!==(b&4),J=!t&&"scroll"===a,x=t?null!==h?h+"Capture":null:h;t=[];for(var w=d,u;null!==
w;){u=w;var F=u.stateNode;5===u.tag&&null!==F&&(u=F,null!==x&&(F=Kb(w,x),null!=F&&t.push(tf(w,F,u))));if(J)break;w=w.return}0<t.length&&(h=new k(h,n,null,c,e),g.push({event:h,listeners:t}))}}if(0===(b&7)){a:{h="mouseover"===a||"pointerover"===a;k="mouseout"===a||"pointerout"===a;if(h&&c!==wb&&(n=c.relatedTarget||c.fromElement)&&(Wc(n)||n[uf]))break a;if(k||h){h=e.window===e?e:(h=e.ownerDocument)?h.defaultView||h.parentWindow:window;if(k){if(n=c.relatedTarget||c.toElement,k=d,n=n?Wc(n):null,null!==
n&&(J=Vb(n),n!==J||5!==n.tag&&6!==n.tag))n=null}else k=null,n=d;if(k!==n){t=Bd;F="onMouseLeave";x="onMouseEnter";w="mouse";if("pointerout"===a||"pointerover"===a)t=Td,F="onPointerLeave",x="onPointerEnter",w="pointer";J=null==k?h:ue(k);u=null==n?h:ue(n);h=new t(F,w+"leave",k,c,e);h.target=J;h.relatedTarget=u;F=null;Wc(e)===d&&(t=new t(x,w+"enter",n,c,e),t.target=u,t.relatedTarget=J,F=t);J=F;if(k&&n)b:{t=k;x=n;w=0;for(u=t;u;u=vf(u))w++;u=0;for(F=x;F;F=vf(F))u++;for(;0<w-u;)t=vf(t),w--;for(;0<u-w;)x=
vf(x),u--;for(;w--;){if(t===x||null!==x&&t===x.alternate)break b;t=vf(t);x=vf(x)}t=null}else t=null;null!==k&&wf(g,h,k,t,!1);null!==n&&null!==J&&wf(g,J,n,t,!0)}}}a:{h=d?ue(d):window;k=h.nodeName&&h.nodeName.toLowerCase();if("select"===k||"input"===k&&"file"===h.type)var na=ve;else if(me(h))if(we)na=Fe;else{na=De;var xa=Ce}else(k=h.nodeName)&&"input"===k.toLowerCase()&&("checkbox"===h.type||"radio"===h.type)&&(na=Ee);if(na&&(na=na(a,d))){ne(g,na,c,e);break a}xa&&xa(a,h,d);"focusout"===a&&(xa=h._wrapperState)&&
xa.controlled&&"number"===h.type&&cb(h,"number",h.value)}xa=d?ue(d):window;switch(a){case "focusin":if(me(xa)||"true"===xa.contentEditable)Qe=xa,Re=d,Se=null;break;case "focusout":Se=Re=Qe=null;break;case "mousedown":Te=!0;break;case "contextmenu":case "mouseup":case "dragend":Te=!1;Ue(g,c,e);break;case "selectionchange":if(Pe)break;case "keydown":case "keyup":Ue(g,c,e)}var $a;if(ae)b:{switch(a){case "compositionstart":var ba="onCompositionStart";break b;case "compositionend":ba="onCompositionEnd";
break b;case "compositionupdate":ba="onCompositionUpdate";break b}ba=void 0}else ie?ge(a,c)&&(ba="onCompositionEnd"):"keydown"===a&&229===c.keyCode&&(ba="onCompositionStart");ba&&(de&&"ko"!==c.locale&&(ie||"onCompositionStart"!==ba?"onCompositionEnd"===ba&&ie&&($a=nd()):(kd=e,ld="value"in kd?kd.value:kd.textContent,ie=!0)),xa=oe(d,ba),0<xa.length&&(ba=new Ld(ba,a,null,c,e),g.push({event:ba,listeners:xa}),$a?ba.data=$a:($a=he(c),null!==$a&&(ba.data=$a))));if($a=ce?je(a,c):ke(a,c))d=oe(d,"onBeforeInput"),
0<d.length&&(e=new Ld("onBeforeInput","beforeinput",null,c,e),g.push({event:e,listeners:d}),e.data=$a)}se(g,b)})}function tf(a,b,c){return{instance:a,listener:b,currentTarget:c}}function oe(a,b){for(var c=b+"Capture",d=[];null!==a;){var e=a,f=e.stateNode;5===e.tag&&null!==f&&(e=f,f=Kb(a,c),null!=f&&d.unshift(tf(a,f,e)),f=Kb(a,b),null!=f&&d.push(tf(a,f,e)));a=a.return}return d}function vf(a){if(null===a)return null;do a=a.return;while(a&&5!==a.tag);return a?a:null}
function wf(a,b,c,d,e){for(var f=b._reactName,g=[];null!==c&&c!==d;){var h=c,k=h.alternate,l=h.stateNode;if(null!==k&&k===d)break;5===h.tag&&null!==l&&(h=l,e?(k=Kb(c,f),null!=k&&g.unshift(tf(c,k,h))):e||(k=Kb(c,f),null!=k&&g.push(tf(c,k,h))));c=c.return}0!==g.length&&a.push({event:b,listeners:g})}var xf=/\r\n?/g,yf=/\u0000|\uFFFD/g;function zf(a){return("string"===typeof a?a:""+a).replace(xf,"\n").replace(yf,"")}function Af(a,b,c){b=zf(b);if(zf(a)!==b&&c)throw Error(p(425));}function Bf(){}
var Cf=null,Df=null;function Ef(a,b){return"textarea"===a||"noscript"===a||"string"===typeof b.children||"number"===typeof b.children||"object"===typeof b.dangerouslySetInnerHTML&&null!==b.dangerouslySetInnerHTML&&null!=b.dangerouslySetInnerHTML.__html}
var Ff="function"===typeof setTimeout?setTimeout:void 0,Gf="function"===typeof clearTimeout?clearTimeout:void 0,Hf="function"===typeof Promise?Promise:void 0,Jf="function"===typeof queueMicrotask?queueMicrotask:"undefined"!==typeof Hf?function(a){return Hf.resolve(null).then(a).catch(If)}:Ff;function If(a){setTimeout(function(){throw a;})}
function Kf(a,b){var c=b,d=0;do{var e=c.nextSibling;a.removeChild(c);if(e&&8===e.nodeType)if(c=e.data,"/$"===c){if(0===d){a.removeChild(e);bd(b);return}d--}else"$"!==c&&"$?"!==c&&"$!"!==c||d++;c=e}while(c);bd(b)}function Lf(a){for(;null!=a;a=a.nextSibling){var b=a.nodeType;if(1===b||3===b)break;if(8===b){b=a.data;if("$"===b||"$!"===b||"$?"===b)break;if("/$"===b)return null}}return a}
function Mf(a){a=a.previousSibling;for(var b=0;a;){if(8===a.nodeType){var c=a.data;if("$"===c||"$!"===c||"$?"===c){if(0===b)return a;b--}else"/$"===c&&b++}a=a.previousSibling}return null}var Nf=Math.random().toString(36).slice(2),Of="__reactFiber$"+Nf,Pf="__reactProps$"+Nf,uf="__reactContainer$"+Nf,of="__reactEvents$"+Nf,Qf="__reactListeners$"+Nf,Rf="__reactHandles$"+Nf;
function Wc(a){var b=a[Of];if(b)return b;for(var c=a.parentNode;c;){if(b=c[uf]||c[Of]){c=b.alternate;if(null!==b.child||null!==c&&null!==c.child)for(a=Mf(a);null!==a;){if(c=a[Of])return c;a=Mf(a)}return b}a=c;c=a.parentNode}return null}function Cb(a){a=a[Of]||a[uf];return!a||5!==a.tag&&6!==a.tag&&13!==a.tag&&3!==a.tag?null:a}function ue(a){if(5===a.tag||6===a.tag)return a.stateNode;throw Error(p(33));}function Db(a){return a[Pf]||null}var Sf=[],Tf=-1;function Uf(a){return{current:a}}
function E(a){0>Tf||(a.current=Sf[Tf],Sf[Tf]=null,Tf--)}function G(a,b){Tf++;Sf[Tf]=a.current;a.current=b}var Vf={},H=Uf(Vf),Wf=Uf(!1),Xf=Vf;function Yf(a,b){var c=a.type.contextTypes;if(!c)return Vf;var d=a.stateNode;if(d&&d.__reactInternalMemoizedUnmaskedChildContext===b)return d.__reactInternalMemoizedMaskedChildContext;var e={},f;for(f in c)e[f]=b[f];d&&(a=a.stateNode,a.__reactInternalMemoizedUnmaskedChildContext=b,a.__reactInternalMemoizedMaskedChildContext=e);return e}
function Zf(a){a=a.childContextTypes;return null!==a&&void 0!==a}function $f(){E(Wf);E(H)}function ag(a,b,c){if(H.current!==Vf)throw Error(p(168));G(H,b);G(Wf,c)}function bg(a,b,c){var d=a.stateNode;b=b.childContextTypes;if("function"!==typeof d.getChildContext)return c;d=d.getChildContext();for(var e in d)if(!(e in b))throw Error(p(108,Ra(a)||"Unknown",e));return A({},c,d)}
function cg(a){a=(a=a.stateNode)&&a.__reactInternalMemoizedMergedChildContext||Vf;Xf=H.current;G(H,a);G(Wf,Wf.current);return!0}function dg(a,b,c){var d=a.stateNode;if(!d)throw Error(p(169));c?(a=bg(a,b,Xf),d.__reactInternalMemoizedMergedChildContext=a,E(Wf),E(H),G(H,a)):E(Wf);G(Wf,c)}var eg=null,fg=!1,gg=!1;function hg(a){null===eg?eg=[a]:eg.push(a)}function ig(a){fg=!0;hg(a)}
function jg(){if(!gg&&null!==eg){gg=!0;var a=0,b=C;try{var c=eg;for(C=1;a<c.length;a++){var d=c[a];do d=d(!0);while(null!==d)}eg=null;fg=!1}catch(e){throw null!==eg&&(eg=eg.slice(a+1)),ac(fc,jg),e;}finally{C=b,gg=!1}}return null}var kg=[],lg=0,mg=null,ng=0,og=[],pg=0,qg=null,rg=1,sg="";function tg(a,b){kg[lg++]=ng;kg[lg++]=mg;mg=a;ng=b}
function ug(a,b,c){og[pg++]=rg;og[pg++]=sg;og[pg++]=qg;qg=a;var d=rg;a=sg;var e=32-oc(d)-1;d&=~(1<<e);c+=1;var f=32-oc(b)+e;if(30<f){var g=e-e%5;f=(d&(1<<g)-1).toString(32);d>>=g;e-=g;rg=1<<32-oc(b)+e|c<<e|d;sg=f+a}else rg=1<<f|c<<e|d,sg=a}function vg(a){null!==a.return&&(tg(a,1),ug(a,1,0))}function wg(a){for(;a===mg;)mg=kg[--lg],kg[lg]=null,ng=kg[--lg],kg[lg]=null;for(;a===qg;)qg=og[--pg],og[pg]=null,sg=og[--pg],og[pg]=null,rg=og[--pg],og[pg]=null}var xg=null,yg=null,I=!1,zg=null;
function Ag(a,b){var c=Bg(5,null,null,0);c.elementType="DELETED";c.stateNode=b;c.return=a;b=a.deletions;null===b?(a.deletions=[c],a.flags|=16):b.push(c)}
function Cg(a,b){switch(a.tag){case 5:var c=a.type;b=1!==b.nodeType||c.toLowerCase()!==b.nodeName.toLowerCase()?null:b;return null!==b?(a.stateNode=b,xg=a,yg=Lf(b.firstChild),!0):!1;case 6:return b=""===a.pendingProps||3!==b.nodeType?null:b,null!==b?(a.stateNode=b,xg=a,yg=null,!0):!1;case 13:return b=8!==b.nodeType?null:b,null!==b?(c=null!==qg?{id:rg,overflow:sg}:null,a.memoizedState={dehydrated:b,treeContext:c,retryLane:1073741824},c=Bg(18,null,null,0),c.stateNode=b,c.return=a,a.child=c,xg=a,yg=
null,!0):!1;default:return!1}}function Dg(a){return 0!==(a.mode&1)&&0===(a.flags&128)}function Eg(a){if(I){var b=yg;if(b){var c=b;if(!Cg(a,b)){if(Dg(a))throw Error(p(418));b=Lf(c.nextSibling);var d=xg;b&&Cg(a,b)?Ag(d,c):(a.flags=a.flags&-4097|2,I=!1,xg=a)}}else{if(Dg(a))throw Error(p(418));a.flags=a.flags&-4097|2;I=!1;xg=a}}}function Fg(a){for(a=a.return;null!==a&&5!==a.tag&&3!==a.tag&&13!==a.tag;)a=a.return;xg=a}
function Gg(a){if(a!==xg)return!1;if(!I)return Fg(a),I=!0,!1;var b;(b=3!==a.tag)&&!(b=5!==a.tag)&&(b=a.type,b="head"!==b&&"body"!==b&&!Ef(a.type,a.memoizedProps));if(b&&(b=yg)){if(Dg(a))throw Hg(),Error(p(418));for(;b;)Ag(a,b),b=Lf(b.nextSibling)}Fg(a);if(13===a.tag){a=a.memoizedState;a=null!==a?a.dehydrated:null;if(!a)throw Error(p(317));a:{a=a.nextSibling;for(b=0;a;){if(8===a.nodeType){var c=a.data;if("/$"===c){if(0===b){yg=Lf(a.nextSibling);break a}b--}else"$"!==c&&"$!"!==c&&"$?"!==c||b++}a=a.nextSibling}yg=
null}}else yg=xg?Lf(a.stateNode.nextSibling):null;return!0}function Hg(){for(var a=yg;a;)a=Lf(a.nextSibling)}function Ig(){yg=xg=null;I=!1}function Jg(a){null===zg?zg=[a]:zg.push(a)}var Kg=ua.ReactCurrentBatchConfig;
function Lg(a,b,c){a=c.ref;if(null!==a&&"function"!==typeof a&&"object"!==typeof a){if(c._owner){c=c._owner;if(c){if(1!==c.tag)throw Error(p(309));var d=c.stateNode}if(!d)throw Error(p(147,a));var e=d,f=""+a;if(null!==b&&null!==b.ref&&"function"===typeof b.ref&&b.ref._stringRef===f)return b.ref;b=function(a){var b=e.refs;null===a?delete b[f]:b[f]=a};b._stringRef=f;return b}if("string"!==typeof a)throw Error(p(284));if(!c._owner)throw Error(p(290,a));}return a}
function Mg(a,b){a=Object.prototype.toString.call(b);throw Error(p(31,"[object Object]"===a?"object with keys {"+Object.keys(b).join(", ")+"}":a));}function Ng(a){var b=a._init;return b(a._payload)}
function Og(a){function b(b,c){if(a){var d=b.deletions;null===d?(b.deletions=[c],b.flags|=16):d.push(c)}}function c(c,d){if(!a)return null;for(;null!==d;)b(c,d),d=d.sibling;return null}function d(a,b){for(a=new Map;null!==b;)null!==b.key?a.set(b.key,b):a.set(b.index,b),b=b.sibling;return a}function e(a,b){a=Pg(a,b);a.index=0;a.sibling=null;return a}function f(b,c,d){b.index=d;if(!a)return b.flags|=1048576,c;d=b.alternate;if(null!==d)return d=d.index,d<c?(b.flags|=2,c):d;b.flags|=2;return c}function g(b){a&&
null===b.alternate&&(b.flags|=2);return b}function h(a,b,c,d){if(null===b||6!==b.tag)return b=Qg(c,a.mode,d),b.return=a,b;b=e(b,c);b.return=a;return b}function k(a,b,c,d){var f=c.type;if(f===ya)return m(a,b,c.props.children,d,c.key);if(null!==b&&(b.elementType===f||"object"===typeof f&&null!==f&&f.$$typeof===Ha&&Ng(f)===b.type))return d=e(b,c.props),d.ref=Lg(a,b,c),d.return=a,d;d=Rg(c.type,c.key,c.props,null,a.mode,d);d.ref=Lg(a,b,c);d.return=a;return d}function l(a,b,c,d){if(null===b||4!==b.tag||
b.stateNode.containerInfo!==c.containerInfo||b.stateNode.implementation!==c.implementation)return b=Sg(c,a.mode,d),b.return=a,b;b=e(b,c.children||[]);b.return=a;return b}function m(a,b,c,d,f){if(null===b||7!==b.tag)return b=Tg(c,a.mode,d,f),b.return=a,b;b=e(b,c);b.return=a;return b}function q(a,b,c){if("string"===typeof b&&""!==b||"number"===typeof b)return b=Qg(""+b,a.mode,c),b.return=a,b;if("object"===typeof b&&null!==b){switch(b.$$typeof){case va:return c=Rg(b.type,b.key,b.props,null,a.mode,c),
c.ref=Lg(a,null,b),c.return=a,c;case wa:return b=Sg(b,a.mode,c),b.return=a,b;case Ha:var d=b._init;return q(a,d(b._payload),c)}if(eb(b)||Ka(b))return b=Tg(b,a.mode,c,null),b.return=a,b;Mg(a,b)}return null}function r(a,b,c,d){var e=null!==b?b.key:null;if("string"===typeof c&&""!==c||"number"===typeof c)return null!==e?null:h(a,b,""+c,d);if("object"===typeof c&&null!==c){switch(c.$$typeof){case va:return c.key===e?k(a,b,c,d):null;case wa:return c.key===e?l(a,b,c,d):null;case Ha:return e=c._init,r(a,
b,e(c._payload),d)}if(eb(c)||Ka(c))return null!==e?null:m(a,b,c,d,null);Mg(a,c)}return null}function y(a,b,c,d,e){if("string"===typeof d&&""!==d||"number"===typeof d)return a=a.get(c)||null,h(b,a,""+d,e);if("object"===typeof d&&null!==d){switch(d.$$typeof){case va:return a=a.get(null===d.key?c:d.key)||null,k(b,a,d,e);case wa:return a=a.get(null===d.key?c:d.key)||null,l(b,a,d,e);case Ha:var f=d._init;return y(a,b,c,f(d._payload),e)}if(eb(d)||Ka(d))return a=a.get(c)||null,m(b,a,d,e,null);Mg(b,d)}return null}
function n(e,g,h,k){for(var l=null,m=null,u=g,w=g=0,x=null;null!==u&&w<h.length;w++){u.index>w?(x=u,u=null):x=u.sibling;var n=r(e,u,h[w],k);if(null===n){null===u&&(u=x);break}a&&u&&null===n.alternate&&b(e,u);g=f(n,g,w);null===m?l=n:m.sibling=n;m=n;u=x}if(w===h.length)return c(e,u),I&&tg(e,w),l;if(null===u){for(;w<h.length;w++)u=q(e,h[w],k),null!==u&&(g=f(u,g,w),null===m?l=u:m.sibling=u,m=u);I&&tg(e,w);return l}for(u=d(e,u);w<h.length;w++)x=y(u,e,w,h[w],k),null!==x&&(a&&null!==x.alternate&&u.delete(null===
x.key?w:x.key),g=f(x,g,w),null===m?l=x:m.sibling=x,m=x);a&&u.forEach(function(a){return b(e,a)});I&&tg(e,w);return l}function t(e,g,h,k){var l=Ka(h);if("function"!==typeof l)throw Error(p(150));h=l.call(h);if(null==h)throw Error(p(151));for(var u=l=null,m=g,w=g=0,x=null,n=h.next();null!==m&&!n.done;w++,n=h.next()){m.index>w?(x=m,m=null):x=m.sibling;var t=r(e,m,n.value,k);if(null===t){null===m&&(m=x);break}a&&m&&null===t.alternate&&b(e,m);g=f(t,g,w);null===u?l=t:u.sibling=t;u=t;m=x}if(n.done)return c(e,
m),I&&tg(e,w),l;if(null===m){for(;!n.done;w++,n=h.next())n=q(e,n.value,k),null!==n&&(g=f(n,g,w),null===u?l=n:u.sibling=n,u=n);I&&tg(e,w);return l}for(m=d(e,m);!n.done;w++,n=h.next())n=y(m,e,w,n.value,k),null!==n&&(a&&null!==n.alternate&&m.delete(null===n.key?w:n.key),g=f(n,g,w),null===u?l=n:u.sibling=n,u=n);a&&m.forEach(function(a){return b(e,a)});I&&tg(e,w);return l}function J(a,d,f,h){"object"===typeof f&&null!==f&&f.type===ya&&null===f.key&&(f=f.props.children);if("object"===typeof f&&null!==f){switch(f.$$typeof){case va:a:{for(var k=
f.key,l=d;null!==l;){if(l.key===k){k=f.type;if(k===ya){if(7===l.tag){c(a,l.sibling);d=e(l,f.props.children);d.return=a;a=d;break a}}else if(l.elementType===k||"object"===typeof k&&null!==k&&k.$$typeof===Ha&&Ng(k)===l.type){c(a,l.sibling);d=e(l,f.props);d.ref=Lg(a,l,f);d.return=a;a=d;break a}c(a,l);break}else b(a,l);l=l.sibling}f.type===ya?(d=Tg(f.props.children,a.mode,h,f.key),d.return=a,a=d):(h=Rg(f.type,f.key,f.props,null,a.mode,h),h.ref=Lg(a,d,f),h.return=a,a=h)}return g(a);case wa:a:{for(l=f.key;null!==
d;){if(d.key===l)if(4===d.tag&&d.stateNode.containerInfo===f.containerInfo&&d.stateNode.implementation===f.implementation){c(a,d.sibling);d=e(d,f.children||[]);d.return=a;a=d;break a}else{c(a,d);break}else b(a,d);d=d.sibling}d=Sg(f,a.mode,h);d.return=a;a=d}return g(a);case Ha:return l=f._init,J(a,d,l(f._payload),h)}if(eb(f))return n(a,d,f,h);if(Ka(f))return t(a,d,f,h);Mg(a,f)}return"string"===typeof f&&""!==f||"number"===typeof f?(f=""+f,null!==d&&6===d.tag?(c(a,d.sibling),d=e(d,f),d.return=a,a=d):
(c(a,d),d=Qg(f,a.mode,h),d.return=a,a=d),g(a)):c(a,d)}return J}var Ug=Og(!0),Vg=Og(!1),Wg=Uf(null),Xg=null,Yg=null,Zg=null;function $g(){Zg=Yg=Xg=null}function ah(a){var b=Wg.current;E(Wg);a._currentValue=b}function bh(a,b,c){for(;null!==a;){var d=a.alternate;(a.childLanes&b)!==b?(a.childLanes|=b,null!==d&&(d.childLanes|=b)):null!==d&&(d.childLanes&b)!==b&&(d.childLanes|=b);if(a===c)break;a=a.return}}
function ch(a,b){Xg=a;Zg=Yg=null;a=a.dependencies;null!==a&&null!==a.firstContext&&(0!==(a.lanes&b)&&(dh=!0),a.firstContext=null)}function eh(a){var b=a._currentValue;if(Zg!==a)if(a={context:a,memoizedValue:b,next:null},null===Yg){if(null===Xg)throw Error(p(308));Yg=a;Xg.dependencies={lanes:0,firstContext:a}}else Yg=Yg.next=a;return b}var fh=null;function gh(a){null===fh?fh=[a]:fh.push(a)}
function hh(a,b,c,d){var e=b.interleaved;null===e?(c.next=c,gh(b)):(c.next=e.next,e.next=c);b.interleaved=c;return ih(a,d)}function ih(a,b){a.lanes|=b;var c=a.alternate;null!==c&&(c.lanes|=b);c=a;for(a=a.return;null!==a;)a.childLanes|=b,c=a.alternate,null!==c&&(c.childLanes|=b),c=a,a=a.return;return 3===c.tag?c.stateNode:null}var jh=!1;function kh(a){a.updateQueue={baseState:a.memoizedState,firstBaseUpdate:null,lastBaseUpdate:null,shared:{pending:null,interleaved:null,lanes:0},effects:null}}
function lh(a,b){a=a.updateQueue;b.updateQueue===a&&(b.updateQueue={baseState:a.baseState,firstBaseUpdate:a.firstBaseUpdate,lastBaseUpdate:a.lastBaseUpdate,shared:a.shared,effects:a.effects})}function mh(a,b){return{eventTime:a,lane:b,tag:0,payload:null,callback:null,next:null}}
function nh(a,b,c){var d=a.updateQueue;if(null===d)return null;d=d.shared;if(0!==(K&2)){var e=d.pending;null===e?b.next=b:(b.next=e.next,e.next=b);d.pending=b;return ih(a,c)}e=d.interleaved;null===e?(b.next=b,gh(d)):(b.next=e.next,e.next=b);d.interleaved=b;return ih(a,c)}function oh(a,b,c){b=b.updateQueue;if(null!==b&&(b=b.shared,0!==(c&4194240))){var d=b.lanes;d&=a.pendingLanes;c|=d;b.lanes=c;Cc(a,c)}}
function ph(a,b){var c=a.updateQueue,d=a.alternate;if(null!==d&&(d=d.updateQueue,c===d)){var e=null,f=null;c=c.firstBaseUpdate;if(null!==c){do{var g={eventTime:c.eventTime,lane:c.lane,tag:c.tag,payload:c.payload,callback:c.callback,next:null};null===f?e=f=g:f=f.next=g;c=c.next}while(null!==c);null===f?e=f=b:f=f.next=b}else e=f=b;c={baseState:d.baseState,firstBaseUpdate:e,lastBaseUpdate:f,shared:d.shared,effects:d.effects};a.updateQueue=c;return}a=c.lastBaseUpdate;null===a?c.firstBaseUpdate=b:a.next=
b;c.lastBaseUpdate=b}
function qh(a,b,c,d){var e=a.updateQueue;jh=!1;var f=e.firstBaseUpdate,g=e.lastBaseUpdate,h=e.shared.pending;if(null!==h){e.shared.pending=null;var k=h,l=k.next;k.next=null;null===g?f=l:g.next=l;g=k;var m=a.alternate;null!==m&&(m=m.updateQueue,h=m.lastBaseUpdate,h!==g&&(null===h?m.firstBaseUpdate=l:h.next=l,m.lastBaseUpdate=k))}if(null!==f){var q=e.baseState;g=0;m=l=k=null;h=f;do{var r=h.lane,y=h.eventTime;if((d&r)===r){null!==m&&(m=m.next={eventTime:y,lane:0,tag:h.tag,payload:h.payload,callback:h.callback,
next:null});a:{var n=a,t=h;r=b;y=c;switch(t.tag){case 1:n=t.payload;if("function"===typeof n){q=n.call(y,q,r);break a}q=n;break a;case 3:n.flags=n.flags&-65537|128;case 0:n=t.payload;r="function"===typeof n?n.call(y,q,r):n;if(null===r||void 0===r)break a;q=A({},q,r);break a;case 2:jh=!0}}null!==h.callback&&0!==h.lane&&(a.flags|=64,r=e.effects,null===r?e.effects=[h]:r.push(h))}else y={eventTime:y,lane:r,tag:h.tag,payload:h.payload,callback:h.callback,next:null},null===m?(l=m=y,k=q):m=m.next=y,g|=r;
h=h.next;if(null===h)if(h=e.shared.pending,null===h)break;else r=h,h=r.next,r.next=null,e.lastBaseUpdate=r,e.shared.pending=null}while(1);null===m&&(k=q);e.baseState=k;e.firstBaseUpdate=l;e.lastBaseUpdate=m;b=e.shared.interleaved;if(null!==b){e=b;do g|=e.lane,e=e.next;while(e!==b)}else null===f&&(e.shared.lanes=0);rh|=g;a.lanes=g;a.memoizedState=q}}
function sh(a,b,c){a=b.effects;b.effects=null;if(null!==a)for(b=0;b<a.length;b++){var d=a[b],e=d.callback;if(null!==e){d.callback=null;d=c;if("function"!==typeof e)throw Error(p(191,e));e.call(d)}}}var th={},uh=Uf(th),vh=Uf(th),wh=Uf(th);function xh(a){if(a===th)throw Error(p(174));return a}
function yh(a,b){G(wh,b);G(vh,a);G(uh,th);a=b.nodeType;switch(a){case 9:case 11:b=(b=b.documentElement)?b.namespaceURI:lb(null,"");break;default:a=8===a?b.parentNode:b,b=a.namespaceURI||null,a=a.tagName,b=lb(b,a)}E(uh);G(uh,b)}function zh(){E(uh);E(vh);E(wh)}function Ah(a){xh(wh.current);var b=xh(uh.current);var c=lb(b,a.type);b!==c&&(G(vh,a),G(uh,c))}function Bh(a){vh.current===a&&(E(uh),E(vh))}var L=Uf(0);
function Ch(a){for(var b=a;null!==b;){if(13===b.tag){var c=b.memoizedState;if(null!==c&&(c=c.dehydrated,null===c||"$?"===c.data||"$!"===c.data))return b}else if(19===b.tag&&void 0!==b.memoizedProps.revealOrder){if(0!==(b.flags&128))return b}else if(null!==b.child){b.child.return=b;b=b.child;continue}if(b===a)break;for(;null===b.sibling;){if(null===b.return||b.return===a)return null;b=b.return}b.sibling.return=b.return;b=b.sibling}return null}var Dh=[];
function Eh(){for(var a=0;a<Dh.length;a++)Dh[a]._workInProgressVersionPrimary=null;Dh.length=0}var Fh=ua.ReactCurrentDispatcher,Gh=ua.ReactCurrentBatchConfig,Hh=0,M=null,N=null,O=null,Ih=!1,Jh=!1,Kh=0,Lh=0;function P(){throw Error(p(321));}function Mh(a,b){if(null===b)return!1;for(var c=0;c<b.length&&c<a.length;c++)if(!He(a[c],b[c]))return!1;return!0}
function Nh(a,b,c,d,e,f){Hh=f;M=b;b.memoizedState=null;b.updateQueue=null;b.lanes=0;Fh.current=null===a||null===a.memoizedState?Oh:Ph;a=c(d,e);if(Jh){f=0;do{Jh=!1;Kh=0;if(25<=f)throw Error(p(301));f+=1;O=N=null;b.updateQueue=null;Fh.current=Qh;a=c(d,e)}while(Jh)}Fh.current=Rh;b=null!==N&&null!==N.next;Hh=0;O=N=M=null;Ih=!1;if(b)throw Error(p(300));return a}function Sh(){var a=0!==Kh;Kh=0;return a}
function Th(){var a={memoizedState:null,baseState:null,baseQueue:null,queue:null,next:null};null===O?M.memoizedState=O=a:O=O.next=a;return O}function Uh(){if(null===N){var a=M.alternate;a=null!==a?a.memoizedState:null}else a=N.next;var b=null===O?M.memoizedState:O.next;if(null!==b)O=b,N=a;else{if(null===a)throw Error(p(310));N=a;a={memoizedState:N.memoizedState,baseState:N.baseState,baseQueue:N.baseQueue,queue:N.queue,next:null};null===O?M.memoizedState=O=a:O=O.next=a}return O}
function Vh(a,b){return"function"===typeof b?b(a):b}
function Wh(a){var b=Uh(),c=b.queue;if(null===c)throw Error(p(311));c.lastRenderedReducer=a;var d=N,e=d.baseQueue,f=c.pending;if(null!==f){if(null!==e){var g=e.next;e.next=f.next;f.next=g}d.baseQueue=e=f;c.pending=null}if(null!==e){f=e.next;d=d.baseState;var h=g=null,k=null,l=f;do{var m=l.lane;if((Hh&m)===m)null!==k&&(k=k.next={lane:0,action:l.action,hasEagerState:l.hasEagerState,eagerState:l.eagerState,next:null}),d=l.hasEagerState?l.eagerState:a(d,l.action);else{var q={lane:m,action:l.action,hasEagerState:l.hasEagerState,
eagerState:l.eagerState,next:null};null===k?(h=k=q,g=d):k=k.next=q;M.lanes|=m;rh|=m}l=l.next}while(null!==l&&l!==f);null===k?g=d:k.next=h;He(d,b.memoizedState)||(dh=!0);b.memoizedState=d;b.baseState=g;b.baseQueue=k;c.lastRenderedState=d}a=c.interleaved;if(null!==a){e=a;do f=e.lane,M.lanes|=f,rh|=f,e=e.next;while(e!==a)}else null===e&&(c.lanes=0);return[b.memoizedState,c.dispatch]}
function Xh(a){var b=Uh(),c=b.queue;if(null===c)throw Error(p(311));c.lastRenderedReducer=a;var d=c.dispatch,e=c.pending,f=b.memoizedState;if(null!==e){c.pending=null;var g=e=e.next;do f=a(f,g.action),g=g.next;while(g!==e);He(f,b.memoizedState)||(dh=!0);b.memoizedState=f;null===b.baseQueue&&(b.baseState=f);c.lastRenderedState=f}return[f,d]}function Yh(){}
function Zh(a,b){var c=M,d=Uh(),e=b(),f=!He(d.memoizedState,e);f&&(d.memoizedState=e,dh=!0);d=d.queue;$h(ai.bind(null,c,d,a),[a]);if(d.getSnapshot!==b||f||null!==O&&O.memoizedState.tag&1){c.flags|=2048;bi(9,ci.bind(null,c,d,e,b),void 0,null);if(null===Q)throw Error(p(349));0!==(Hh&30)||di(c,b,e)}return e}function di(a,b,c){a.flags|=16384;a={getSnapshot:b,value:c};b=M.updateQueue;null===b?(b={lastEffect:null,stores:null},M.updateQueue=b,b.stores=[a]):(c=b.stores,null===c?b.stores=[a]:c.push(a))}
function ci(a,b,c,d){b.value=c;b.getSnapshot=d;ei(b)&&fi(a)}function ai(a,b,c){return c(function(){ei(b)&&fi(a)})}function ei(a){var b=a.getSnapshot;a=a.value;try{var c=b();return!He(a,c)}catch(d){return!0}}function fi(a){var b=ih(a,1);null!==b&&gi(b,a,1,-1)}
function hi(a){var b=Th();"function"===typeof a&&(a=a());b.memoizedState=b.baseState=a;a={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:Vh,lastRenderedState:a};b.queue=a;a=a.dispatch=ii.bind(null,M,a);return[b.memoizedState,a]}
function bi(a,b,c,d){a={tag:a,create:b,destroy:c,deps:d,next:null};b=M.updateQueue;null===b?(b={lastEffect:null,stores:null},M.updateQueue=b,b.lastEffect=a.next=a):(c=b.lastEffect,null===c?b.lastEffect=a.next=a:(d=c.next,c.next=a,a.next=d,b.lastEffect=a));return a}function ji(){return Uh().memoizedState}function ki(a,b,c,d){var e=Th();M.flags|=a;e.memoizedState=bi(1|b,c,void 0,void 0===d?null:d)}
function li(a,b,c,d){var e=Uh();d=void 0===d?null:d;var f=void 0;if(null!==N){var g=N.memoizedState;f=g.destroy;if(null!==d&&Mh(d,g.deps)){e.memoizedState=bi(b,c,f,d);return}}M.flags|=a;e.memoizedState=bi(1|b,c,f,d)}function mi(a,b){return ki(8390656,8,a,b)}function $h(a,b){return li(2048,8,a,b)}function ni(a,b){return li(4,2,a,b)}function oi(a,b){return li(4,4,a,b)}
function pi(a,b){if("function"===typeof b)return a=a(),b(a),function(){b(null)};if(null!==b&&void 0!==b)return a=a(),b.current=a,function(){b.current=null}}function qi(a,b,c){c=null!==c&&void 0!==c?c.concat([a]):null;return li(4,4,pi.bind(null,b,a),c)}function ri(){}function si(a,b){var c=Uh();b=void 0===b?null:b;var d=c.memoizedState;if(null!==d&&null!==b&&Mh(b,d[1]))return d[0];c.memoizedState=[a,b];return a}
function ti(a,b){var c=Uh();b=void 0===b?null:b;var d=c.memoizedState;if(null!==d&&null!==b&&Mh(b,d[1]))return d[0];a=a();c.memoizedState=[a,b];return a}function ui(a,b,c){if(0===(Hh&21))return a.baseState&&(a.baseState=!1,dh=!0),a.memoizedState=c;He(c,b)||(c=yc(),M.lanes|=c,rh|=c,a.baseState=!0);return b}function vi(a,b){var c=C;C=0!==c&&4>c?c:4;a(!0);var d=Gh.transition;Gh.transition={};try{a(!1),b()}finally{C=c,Gh.transition=d}}function wi(){return Uh().memoizedState}
function xi(a,b,c){var d=yi(a);c={lane:d,action:c,hasEagerState:!1,eagerState:null,next:null};if(zi(a))Ai(b,c);else if(c=hh(a,b,c,d),null!==c){var e=R();gi(c,a,d,e);Bi(c,b,d)}}
function ii(a,b,c){var d=yi(a),e={lane:d,action:c,hasEagerState:!1,eagerState:null,next:null};if(zi(a))Ai(b,e);else{var f=a.alternate;if(0===a.lanes&&(null===f||0===f.lanes)&&(f=b.lastRenderedReducer,null!==f))try{var g=b.lastRenderedState,h=f(g,c);e.hasEagerState=!0;e.eagerState=h;if(He(h,g)){var k=b.interleaved;null===k?(e.next=e,gh(b)):(e.next=k.next,k.next=e);b.interleaved=e;return}}catch(l){}finally{}c=hh(a,b,e,d);null!==c&&(e=R(),gi(c,a,d,e),Bi(c,b,d))}}
function zi(a){var b=a.alternate;return a===M||null!==b&&b===M}function Ai(a,b){Jh=Ih=!0;var c=a.pending;null===c?b.next=b:(b.next=c.next,c.next=b);a.pending=b}function Bi(a,b,c){if(0!==(c&4194240)){var d=b.lanes;d&=a.pendingLanes;c|=d;b.lanes=c;Cc(a,c)}}
var Rh={readContext:eh,useCallback:P,useContext:P,useEffect:P,useImperativeHandle:P,useInsertionEffect:P,useLayoutEffect:P,useMemo:P,useReducer:P,useRef:P,useState:P,useDebugValue:P,useDeferredValue:P,useTransition:P,useMutableSource:P,useSyncExternalStore:P,useId:P,unstable_isNewReconciler:!1},Oh={readContext:eh,useCallback:function(a,b){Th().memoizedState=[a,void 0===b?null:b];return a},useContext:eh,useEffect:mi,useImperativeHandle:function(a,b,c){c=null!==c&&void 0!==c?c.concat([a]):null;return ki(4194308,
4,pi.bind(null,b,a),c)},useLayoutEffect:function(a,b){return ki(4194308,4,a,b)},useInsertionEffect:function(a,b){return ki(4,2,a,b)},useMemo:function(a,b){var c=Th();b=void 0===b?null:b;a=a();c.memoizedState=[a,b];return a},useReducer:function(a,b,c){var d=Th();b=void 0!==c?c(b):b;d.memoizedState=d.baseState=b;a={pending:null,interleaved:null,lanes:0,dispatch:null,lastRenderedReducer:a,lastRenderedState:b};d.queue=a;a=a.dispatch=xi.bind(null,M,a);return[d.memoizedState,a]},useRef:function(a){var b=
Th();a={current:a};return b.memoizedState=a},useState:hi,useDebugValue:ri,useDeferredValue:function(a){return Th().memoizedState=a},useTransition:function(){var a=hi(!1),b=a[0];a=vi.bind(null,a[1]);Th().memoizedState=a;return[b,a]},useMutableSource:function(){},useSyncExternalStore:function(a,b,c){var d=M,e=Th();if(I){if(void 0===c)throw Error(p(407));c=c()}else{c=b();if(null===Q)throw Error(p(349));0!==(Hh&30)||di(d,b,c)}e.memoizedState=c;var f={value:c,getSnapshot:b};e.queue=f;mi(ai.bind(null,d,
f,a),[a]);d.flags|=2048;bi(9,ci.bind(null,d,f,c,b),void 0,null);return c},useId:function(){var a=Th(),b=Q.identifierPrefix;if(I){var c=sg;var d=rg;c=(d&~(1<<32-oc(d)-1)).toString(32)+c;b=":"+b+"R"+c;c=Kh++;0<c&&(b+="H"+c.toString(32));b+=":"}else c=Lh++,b=":"+b+"r"+c.toString(32)+":";return a.memoizedState=b},unstable_isNewReconciler:!1},Ph={readContext:eh,useCallback:si,useContext:eh,useEffect:$h,useImperativeHandle:qi,useInsertionEffect:ni,useLayoutEffect:oi,useMemo:ti,useReducer:Wh,useRef:ji,useState:function(){return Wh(Vh)},
useDebugValue:ri,useDeferredValue:function(a){var b=Uh();return ui(b,N.memoizedState,a)},useTransition:function(){var a=Wh(Vh)[0],b=Uh().memoizedState;return[a,b]},useMutableSource:Yh,useSyncExternalStore:Zh,useId:wi,unstable_isNewReconciler:!1},Qh={readContext:eh,useCallback:si,useContext:eh,useEffect:$h,useImperativeHandle:qi,useInsertionEffect:ni,useLayoutEffect:oi,useMemo:ti,useReducer:Xh,useRef:ji,useState:function(){return Xh(Vh)},useDebugValue:ri,useDeferredValue:function(a){var b=Uh();return null===
N?b.memoizedState=a:ui(b,N.memoizedState,a)},useTransition:function(){var a=Xh(Vh)[0],b=Uh().memoizedState;return[a,b]},useMutableSource:Yh,useSyncExternalStore:Zh,useId:wi,unstable_isNewReconciler:!1};function Ci(a,b){if(a&&a.defaultProps){b=A({},b);a=a.defaultProps;for(var c in a)void 0===b[c]&&(b[c]=a[c]);return b}return b}function Di(a,b,c,d){b=a.memoizedState;c=c(d,b);c=null===c||void 0===c?b:A({},b,c);a.memoizedState=c;0===a.lanes&&(a.updateQueue.baseState=c)}
var Ei={isMounted:function(a){return(a=a._reactInternals)?Vb(a)===a:!1},enqueueSetState:function(a,b,c){a=a._reactInternals;var d=R(),e=yi(a),f=mh(d,e);f.payload=b;void 0!==c&&null!==c&&(f.callback=c);b=nh(a,f,e);null!==b&&(gi(b,a,e,d),oh(b,a,e))},enqueueReplaceState:function(a,b,c){a=a._reactInternals;var d=R(),e=yi(a),f=mh(d,e);f.tag=1;f.payload=b;void 0!==c&&null!==c&&(f.callback=c);b=nh(a,f,e);null!==b&&(gi(b,a,e,d),oh(b,a,e))},enqueueForceUpdate:function(a,b){a=a._reactInternals;var c=R(),d=
yi(a),e=mh(c,d);e.tag=2;void 0!==b&&null!==b&&(e.callback=b);b=nh(a,e,d);null!==b&&(gi(b,a,d,c),oh(b,a,d))}};function Fi(a,b,c,d,e,f,g){a=a.stateNode;return"function"===typeof a.shouldComponentUpdate?a.shouldComponentUpdate(d,f,g):b.prototype&&b.prototype.isPureReactComponent?!Ie(c,d)||!Ie(e,f):!0}
function Gi(a,b,c){var d=!1,e=Vf;var f=b.contextType;"object"===typeof f&&null!==f?f=eh(f):(e=Zf(b)?Xf:H.current,d=b.contextTypes,f=(d=null!==d&&void 0!==d)?Yf(a,e):Vf);b=new b(c,f);a.memoizedState=null!==b.state&&void 0!==b.state?b.state:null;b.updater=Ei;a.stateNode=b;b._reactInternals=a;d&&(a=a.stateNode,a.__reactInternalMemoizedUnmaskedChildContext=e,a.__reactInternalMemoizedMaskedChildContext=f);return b}
function Hi(a,b,c,d){a=b.state;"function"===typeof b.componentWillReceiveProps&&b.componentWillReceiveProps(c,d);"function"===typeof b.UNSAFE_componentWillReceiveProps&&b.UNSAFE_componentWillReceiveProps(c,d);b.state!==a&&Ei.enqueueReplaceState(b,b.state,null)}
function Ii(a,b,c,d){var e=a.stateNode;e.props=c;e.state=a.memoizedState;e.refs={};kh(a);var f=b.contextType;"object"===typeof f&&null!==f?e.context=eh(f):(f=Zf(b)?Xf:H.current,e.context=Yf(a,f));e.state=a.memoizedState;f=b.getDerivedStateFromProps;"function"===typeof f&&(Di(a,b,f,c),e.state=a.memoizedState);"function"===typeof b.getDerivedStateFromProps||"function"===typeof e.getSnapshotBeforeUpdate||"function"!==typeof e.UNSAFE_componentWillMount&&"function"!==typeof e.componentWillMount||(b=e.state,
"function"===typeof e.componentWillMount&&e.componentWillMount(),"function"===typeof e.UNSAFE_componentWillMount&&e.UNSAFE_componentWillMount(),b!==e.state&&Ei.enqueueReplaceState(e,e.state,null),qh(a,c,e,d),e.state=a.memoizedState);"function"===typeof e.componentDidMount&&(a.flags|=4194308)}function Ji(a,b){try{var c="",d=b;do c+=Pa(d),d=d.return;while(d);var e=c}catch(f){e="\nError generating stack: "+f.message+"\n"+f.stack}return{value:a,source:b,stack:e,digest:null}}
function Ki(a,b,c){return{value:a,source:null,stack:null!=c?c:null,digest:null!=b?b:null}}function Li(a,b){try{console.error(b.value)}catch(c){setTimeout(function(){throw c;})}}var Mi="function"===typeof WeakMap?WeakMap:Map;function Ni(a,b,c){c=mh(-1,c);c.tag=3;c.payload={element:null};var d=b.value;c.callback=function(){Oi||(Oi=!0,Pi=d);Li(a,b)};return c}
function Qi(a,b,c){c=mh(-1,c);c.tag=3;var d=a.type.getDerivedStateFromError;if("function"===typeof d){var e=b.value;c.payload=function(){return d(e)};c.callback=function(){Li(a,b)}}var f=a.stateNode;null!==f&&"function"===typeof f.componentDidCatch&&(c.callback=function(){Li(a,b);"function"!==typeof d&&(null===Ri?Ri=new Set([this]):Ri.add(this));var c=b.stack;this.componentDidCatch(b.value,{componentStack:null!==c?c:""})});return c}
function Si(a,b,c){var d=a.pingCache;if(null===d){d=a.pingCache=new Mi;var e=new Set;d.set(b,e)}else e=d.get(b),void 0===e&&(e=new Set,d.set(b,e));e.has(c)||(e.add(c),a=Ti.bind(null,a,b,c),b.then(a,a))}function Ui(a){do{var b;if(b=13===a.tag)b=a.memoizedState,b=null!==b?null!==b.dehydrated?!0:!1:!0;if(b)return a;a=a.return}while(null!==a);return null}
function Vi(a,b,c,d,e){if(0===(a.mode&1))return a===b?a.flags|=65536:(a.flags|=128,c.flags|=131072,c.flags&=-52805,1===c.tag&&(null===c.alternate?c.tag=17:(b=mh(-1,1),b.tag=2,nh(c,b,1))),c.lanes|=1),a;a.flags|=65536;a.lanes=e;return a}var Wi=ua.ReactCurrentOwner,dh=!1;function Xi(a,b,c,d){b.child=null===a?Vg(b,null,c,d):Ug(b,a.child,c,d)}
function Yi(a,b,c,d,e){c=c.render;var f=b.ref;ch(b,e);d=Nh(a,b,c,d,f,e);c=Sh();if(null!==a&&!dh)return b.updateQueue=a.updateQueue,b.flags&=-2053,a.lanes&=~e,Zi(a,b,e);I&&c&&vg(b);b.flags|=1;Xi(a,b,d,e);return b.child}
function $i(a,b,c,d,e){if(null===a){var f=c.type;if("function"===typeof f&&!aj(f)&&void 0===f.defaultProps&&null===c.compare&&void 0===c.defaultProps)return b.tag=15,b.type=f,bj(a,b,f,d,e);a=Rg(c.type,null,d,b,b.mode,e);a.ref=b.ref;a.return=b;return b.child=a}f=a.child;if(0===(a.lanes&e)){var g=f.memoizedProps;c=c.compare;c=null!==c?c:Ie;if(c(g,d)&&a.ref===b.ref)return Zi(a,b,e)}b.flags|=1;a=Pg(f,d);a.ref=b.ref;a.return=b;return b.child=a}
function bj(a,b,c,d,e){if(null!==a){var f=a.memoizedProps;if(Ie(f,d)&&a.ref===b.ref)if(dh=!1,b.pendingProps=d=f,0!==(a.lanes&e))0!==(a.flags&131072)&&(dh=!0);else return b.lanes=a.lanes,Zi(a,b,e)}return cj(a,b,c,d,e)}
function dj(a,b,c){var d=b.pendingProps,e=d.children,f=null!==a?a.memoizedState:null;if("hidden"===d.mode)if(0===(b.mode&1))b.memoizedState={baseLanes:0,cachePool:null,transitions:null},G(ej,fj),fj|=c;else{if(0===(c&1073741824))return a=null!==f?f.baseLanes|c:c,b.lanes=b.childLanes=1073741824,b.memoizedState={baseLanes:a,cachePool:null,transitions:null},b.updateQueue=null,G(ej,fj),fj|=a,null;b.memoizedState={baseLanes:0,cachePool:null,transitions:null};d=null!==f?f.baseLanes:c;G(ej,fj);fj|=d}else null!==
f?(d=f.baseLanes|c,b.memoizedState=null):d=c,G(ej,fj),fj|=d;Xi(a,b,e,c);return b.child}function gj(a,b){var c=b.ref;if(null===a&&null!==c||null!==a&&a.ref!==c)b.flags|=512,b.flags|=2097152}function cj(a,b,c,d,e){var f=Zf(c)?Xf:H.current;f=Yf(b,f);ch(b,e);c=Nh(a,b,c,d,f,e);d=Sh();if(null!==a&&!dh)return b.updateQueue=a.updateQueue,b.flags&=-2053,a.lanes&=~e,Zi(a,b,e);I&&d&&vg(b);b.flags|=1;Xi(a,b,c,e);return b.child}
function hj(a,b,c,d,e){if(Zf(c)){var f=!0;cg(b)}else f=!1;ch(b,e);if(null===b.stateNode)ij(a,b),Gi(b,c,d),Ii(b,c,d,e),d=!0;else if(null===a){var g=b.stateNode,h=b.memoizedProps;g.props=h;var k=g.context,l=c.contextType;"object"===typeof l&&null!==l?l=eh(l):(l=Zf(c)?Xf:H.current,l=Yf(b,l));var m=c.getDerivedStateFromProps,q="function"===typeof m||"function"===typeof g.getSnapshotBeforeUpdate;q||"function"!==typeof g.UNSAFE_componentWillReceiveProps&&"function"!==typeof g.componentWillReceiveProps||
(h!==d||k!==l)&&Hi(b,g,d,l);jh=!1;var r=b.memoizedState;g.state=r;qh(b,d,g,e);k=b.memoizedState;h!==d||r!==k||Wf.current||jh?("function"===typeof m&&(Di(b,c,m,d),k=b.memoizedState),(h=jh||Fi(b,c,h,d,r,k,l))?(q||"function"!==typeof g.UNSAFE_componentWillMount&&"function"!==typeof g.componentWillMount||("function"===typeof g.componentWillMount&&g.componentWillMount(),"function"===typeof g.UNSAFE_componentWillMount&&g.UNSAFE_componentWillMount()),"function"===typeof g.componentDidMount&&(b.flags|=4194308)):
("function"===typeof g.componentDidMount&&(b.flags|=4194308),b.memoizedProps=d,b.memoizedState=k),g.props=d,g.state=k,g.context=l,d=h):("function"===typeof g.componentDidMount&&(b.flags|=4194308),d=!1)}else{g=b.stateNode;lh(a,b);h=b.memoizedProps;l=b.type===b.elementType?h:Ci(b.type,h);g.props=l;q=b.pendingProps;r=g.context;k=c.contextType;"object"===typeof k&&null!==k?k=eh(k):(k=Zf(c)?Xf:H.current,k=Yf(b,k));var y=c.getDerivedStateFromProps;(m="function"===typeof y||"function"===typeof g.getSnapshotBeforeUpdate)||
"function"!==typeof g.UNSAFE_componentWillReceiveProps&&"function"!==typeof g.componentWillReceiveProps||(h!==q||r!==k)&&Hi(b,g,d,k);jh=!1;r=b.memoizedState;g.state=r;qh(b,d,g,e);var n=b.memoizedState;h!==q||r!==n||Wf.current||jh?("function"===typeof y&&(Di(b,c,y,d),n=b.memoizedState),(l=jh||Fi(b,c,l,d,r,n,k)||!1)?(m||"function"!==typeof g.UNSAFE_componentWillUpdate&&"function"!==typeof g.componentWillUpdate||("function"===typeof g.componentWillUpdate&&g.componentWillUpdate(d,n,k),"function"===typeof g.UNSAFE_componentWillUpdate&&
g.UNSAFE_componentWillUpdate(d,n,k)),"function"===typeof g.componentDidUpdate&&(b.flags|=4),"function"===typeof g.getSnapshotBeforeUpdate&&(b.flags|=1024)):("function"!==typeof g.componentDidUpdate||h===a.memoizedProps&&r===a.memoizedState||(b.flags|=4),"function"!==typeof g.getSnapshotBeforeUpdate||h===a.memoizedProps&&r===a.memoizedState||(b.flags|=1024),b.memoizedProps=d,b.memoizedState=n),g.props=d,g.state=n,g.context=k,d=l):("function"!==typeof g.componentDidUpdate||h===a.memoizedProps&&r===
a.memoizedState||(b.flags|=4),"function"!==typeof g.getSnapshotBeforeUpdate||h===a.memoizedProps&&r===a.memoizedState||(b.flags|=1024),d=!1)}return jj(a,b,c,d,f,e)}
function jj(a,b,c,d,e,f){gj(a,b);var g=0!==(b.flags&128);if(!d&&!g)return e&&dg(b,c,!1),Zi(a,b,f);d=b.stateNode;Wi.current=b;var h=g&&"function"!==typeof c.getDerivedStateFromError?null:d.render();b.flags|=1;null!==a&&g?(b.child=Ug(b,a.child,null,f),b.child=Ug(b,null,h,f)):Xi(a,b,h,f);b.memoizedState=d.state;e&&dg(b,c,!0);return b.child}function kj(a){var b=a.stateNode;b.pendingContext?ag(a,b.pendingContext,b.pendingContext!==b.context):b.context&&ag(a,b.context,!1);yh(a,b.containerInfo)}
function lj(a,b,c,d,e){Ig();Jg(e);b.flags|=256;Xi(a,b,c,d);return b.child}var mj={dehydrated:null,treeContext:null,retryLane:0};function nj(a){return{baseLanes:a,cachePool:null,transitions:null}}
function oj(a,b,c){var d=b.pendingProps,e=L.current,f=!1,g=0!==(b.flags&128),h;(h=g)||(h=null!==a&&null===a.memoizedState?!1:0!==(e&2));if(h)f=!0,b.flags&=-129;else if(null===a||null!==a.memoizedState)e|=1;G(L,e&1);if(null===a){Eg(b);a=b.memoizedState;if(null!==a&&(a=a.dehydrated,null!==a))return 0===(b.mode&1)?b.lanes=1:"$!"===a.data?b.lanes=8:b.lanes=1073741824,null;g=d.children;a=d.fallback;return f?(d=b.mode,f=b.child,g={mode:"hidden",children:g},0===(d&1)&&null!==f?(f.childLanes=0,f.pendingProps=
g):f=pj(g,d,0,null),a=Tg(a,d,c,null),f.return=b,a.return=b,f.sibling=a,b.child=f,b.child.memoizedState=nj(c),b.memoizedState=mj,a):qj(b,g)}e=a.memoizedState;if(null!==e&&(h=e.dehydrated,null!==h))return rj(a,b,g,d,h,e,c);if(f){f=d.fallback;g=b.mode;e=a.child;h=e.sibling;var k={mode:"hidden",children:d.children};0===(g&1)&&b.child!==e?(d=b.child,d.childLanes=0,d.pendingProps=k,b.deletions=null):(d=Pg(e,k),d.subtreeFlags=e.subtreeFlags&14680064);null!==h?f=Pg(h,f):(f=Tg(f,g,c,null),f.flags|=2);f.return=
b;d.return=b;d.sibling=f;b.child=d;d=f;f=b.child;g=a.child.memoizedState;g=null===g?nj(c):{baseLanes:g.baseLanes|c,cachePool:null,transitions:g.transitions};f.memoizedState=g;f.childLanes=a.childLanes&~c;b.memoizedState=mj;return d}f=a.child;a=f.sibling;d=Pg(f,{mode:"visible",children:d.children});0===(b.mode&1)&&(d.lanes=c);d.return=b;d.sibling=null;null!==a&&(c=b.deletions,null===c?(b.deletions=[a],b.flags|=16):c.push(a));b.child=d;b.memoizedState=null;return d}
function qj(a,b){b=pj({mode:"visible",children:b},a.mode,0,null);b.return=a;return a.child=b}function sj(a,b,c,d){null!==d&&Jg(d);Ug(b,a.child,null,c);a=qj(b,b.pendingProps.children);a.flags|=2;b.memoizedState=null;return a}
function rj(a,b,c,d,e,f,g){if(c){if(b.flags&256)return b.flags&=-257,d=Ki(Error(p(422))),sj(a,b,g,d);if(null!==b.memoizedState)return b.child=a.child,b.flags|=128,null;f=d.fallback;e=b.mode;d=pj({mode:"visible",children:d.children},e,0,null);f=Tg(f,e,g,null);f.flags|=2;d.return=b;f.return=b;d.sibling=f;b.child=d;0!==(b.mode&1)&&Ug(b,a.child,null,g);b.child.memoizedState=nj(g);b.memoizedState=mj;return f}if(0===(b.mode&1))return sj(a,b,g,null);if("$!"===e.data){d=e.nextSibling&&e.nextSibling.dataset;
if(d)var h=d.dgst;d=h;f=Error(p(419));d=Ki(f,d,void 0);return sj(a,b,g,d)}h=0!==(g&a.childLanes);if(dh||h){d=Q;if(null!==d){switch(g&-g){case 4:e=2;break;case 16:e=8;break;case 64:case 128:case 256:case 512:case 1024:case 2048:case 4096:case 8192:case 16384:case 32768:case 65536:case 131072:case 262144:case 524288:case 1048576:case 2097152:case 4194304:case 8388608:case 16777216:case 33554432:case 67108864:e=32;break;case 536870912:e=268435456;break;default:e=0}e=0!==(e&(d.suspendedLanes|g))?0:e;
0!==e&&e!==f.retryLane&&(f.retryLane=e,ih(a,e),gi(d,a,e,-1))}tj();d=Ki(Error(p(421)));return sj(a,b,g,d)}if("$?"===e.data)return b.flags|=128,b.child=a.child,b=uj.bind(null,a),e._reactRetry=b,null;a=f.treeContext;yg=Lf(e.nextSibling);xg=b;I=!0;zg=null;null!==a&&(og[pg++]=rg,og[pg++]=sg,og[pg++]=qg,rg=a.id,sg=a.overflow,qg=b);b=qj(b,d.children);b.flags|=4096;return b}function vj(a,b,c){a.lanes|=b;var d=a.alternate;null!==d&&(d.lanes|=b);bh(a.return,b,c)}
function wj(a,b,c,d,e){var f=a.memoizedState;null===f?a.memoizedState={isBackwards:b,rendering:null,renderingStartTime:0,last:d,tail:c,tailMode:e}:(f.isBackwards=b,f.rendering=null,f.renderingStartTime=0,f.last=d,f.tail=c,f.tailMode=e)}
function xj(a,b,c){var d=b.pendingProps,e=d.revealOrder,f=d.tail;Xi(a,b,d.children,c);d=L.current;if(0!==(d&2))d=d&1|2,b.flags|=128;else{if(null!==a&&0!==(a.flags&128))a:for(a=b.child;null!==a;){if(13===a.tag)null!==a.memoizedState&&vj(a,c,b);else if(19===a.tag)vj(a,c,b);else if(null!==a.child){a.child.return=a;a=a.child;continue}if(a===b)break a;for(;null===a.sibling;){if(null===a.return||a.return===b)break a;a=a.return}a.sibling.return=a.return;a=a.sibling}d&=1}G(L,d);if(0===(b.mode&1))b.memoizedState=
null;else switch(e){case "forwards":c=b.child;for(e=null;null!==c;)a=c.alternate,null!==a&&null===Ch(a)&&(e=c),c=c.sibling;c=e;null===c?(e=b.child,b.child=null):(e=c.sibling,c.sibling=null);wj(b,!1,e,c,f);break;case "backwards":c=null;e=b.child;for(b.child=null;null!==e;){a=e.alternate;if(null!==a&&null===Ch(a)){b.child=e;break}a=e.sibling;e.sibling=c;c=e;e=a}wj(b,!0,c,null,f);break;case "together":wj(b,!1,null,null,void 0);break;default:b.memoizedState=null}return b.child}
function ij(a,b){0===(b.mode&1)&&null!==a&&(a.alternate=null,b.alternate=null,b.flags|=2)}function Zi(a,b,c){null!==a&&(b.dependencies=a.dependencies);rh|=b.lanes;if(0===(c&b.childLanes))return null;if(null!==a&&b.child!==a.child)throw Error(p(153));if(null!==b.child){a=b.child;c=Pg(a,a.pendingProps);b.child=c;for(c.return=b;null!==a.sibling;)a=a.sibling,c=c.sibling=Pg(a,a.pendingProps),c.return=b;c.sibling=null}return b.child}
function yj(a,b,c){switch(b.tag){case 3:kj(b);Ig();break;case 5:Ah(b);break;case 1:Zf(b.type)&&cg(b);break;case 4:yh(b,b.stateNode.containerInfo);break;case 10:var d=b.type._context,e=b.memoizedProps.value;G(Wg,d._currentValue);d._currentValue=e;break;case 13:d=b.memoizedState;if(null!==d){if(null!==d.dehydrated)return G(L,L.current&1),b.flags|=128,null;if(0!==(c&b.child.childLanes))return oj(a,b,c);G(L,L.current&1);a=Zi(a,b,c);return null!==a?a.sibling:null}G(L,L.current&1);break;case 19:d=0!==(c&
b.childLanes);if(0!==(a.flags&128)){if(d)return xj(a,b,c);b.flags|=128}e=b.memoizedState;null!==e&&(e.rendering=null,e.tail=null,e.lastEffect=null);G(L,L.current);if(d)break;else return null;case 22:case 23:return b.lanes=0,dj(a,b,c)}return Zi(a,b,c)}var zj,Aj,Bj,Cj;
zj=function(a,b){for(var c=b.child;null!==c;){if(5===c.tag||6===c.tag)a.appendChild(c.stateNode);else if(4!==c.tag&&null!==c.child){c.child.return=c;c=c.child;continue}if(c===b)break;for(;null===c.sibling;){if(null===c.return||c.return===b)return;c=c.return}c.sibling.return=c.return;c=c.sibling}};Aj=function(){};
Bj=function(a,b,c,d){var e=a.memoizedProps;if(e!==d){a=b.stateNode;xh(uh.current);var f=null;switch(c){case "input":e=Ya(a,e);d=Ya(a,d);f=[];break;case "select":e=A({},e,{value:void 0});d=A({},d,{value:void 0});f=[];break;case "textarea":e=gb(a,e);d=gb(a,d);f=[];break;default:"function"!==typeof e.onClick&&"function"===typeof d.onClick&&(a.onclick=Bf)}ub(c,d);var g;c=null;for(l in e)if(!d.hasOwnProperty(l)&&e.hasOwnProperty(l)&&null!=e[l])if("style"===l){var h=e[l];for(g in h)h.hasOwnProperty(g)&&
(c||(c={}),c[g]="")}else"dangerouslySetInnerHTML"!==l&&"children"!==l&&"suppressContentEditableWarning"!==l&&"suppressHydrationWarning"!==l&&"autoFocus"!==l&&(ea.hasOwnProperty(l)?f||(f=[]):(f=f||[]).push(l,null));for(l in d){var k=d[l];h=null!=e?e[l]:void 0;if(d.hasOwnProperty(l)&&k!==h&&(null!=k||null!=h))if("style"===l)if(h){for(g in h)!h.hasOwnProperty(g)||k&&k.hasOwnProperty(g)||(c||(c={}),c[g]="");for(g in k)k.hasOwnProperty(g)&&h[g]!==k[g]&&(c||(c={}),c[g]=k[g])}else c||(f||(f=[]),f.push(l,
c)),c=k;else"dangerouslySetInnerHTML"===l?(k=k?k.__html:void 0,h=h?h.__html:void 0,null!=k&&h!==k&&(f=f||[]).push(l,k)):"children"===l?"string"!==typeof k&&"number"!==typeof k||(f=f||[]).push(l,""+k):"suppressContentEditableWarning"!==l&&"suppressHydrationWarning"!==l&&(ea.hasOwnProperty(l)?(null!=k&&"onScroll"===l&&D("scroll",a),f||h===k||(f=[])):(f=f||[]).push(l,k))}c&&(f=f||[]).push("style",c);var l=f;if(b.updateQueue=l)b.flags|=4}};Cj=function(a,b,c,d){c!==d&&(b.flags|=4)};
function Dj(a,b){if(!I)switch(a.tailMode){case "hidden":b=a.tail;for(var c=null;null!==b;)null!==b.alternate&&(c=b),b=b.sibling;null===c?a.tail=null:c.sibling=null;break;case "collapsed":c=a.tail;for(var d=null;null!==c;)null!==c.alternate&&(d=c),c=c.sibling;null===d?b||null===a.tail?a.tail=null:a.tail.sibling=null:d.sibling=null}}
function S(a){var b=null!==a.alternate&&a.alternate.child===a.child,c=0,d=0;if(b)for(var e=a.child;null!==e;)c|=e.lanes|e.childLanes,d|=e.subtreeFlags&14680064,d|=e.flags&14680064,e.return=a,e=e.sibling;else for(e=a.child;null!==e;)c|=e.lanes|e.childLanes,d|=e.subtreeFlags,d|=e.flags,e.return=a,e=e.sibling;a.subtreeFlags|=d;a.childLanes=c;return b}
function Ej(a,b,c){var d=b.pendingProps;wg(b);switch(b.tag){case 2:case 16:case 15:case 0:case 11:case 7:case 8:case 12:case 9:case 14:return S(b),null;case 1:return Zf(b.type)&&$f(),S(b),null;case 3:d=b.stateNode;zh();E(Wf);E(H);Eh();d.pendingContext&&(d.context=d.pendingContext,d.pendingContext=null);if(null===a||null===a.child)Gg(b)?b.flags|=4:null===a||a.memoizedState.isDehydrated&&0===(b.flags&256)||(b.flags|=1024,null!==zg&&(Fj(zg),zg=null));Aj(a,b);S(b);return null;case 5:Bh(b);var e=xh(wh.current);
c=b.type;if(null!==a&&null!=b.stateNode)Bj(a,b,c,d,e),a.ref!==b.ref&&(b.flags|=512,b.flags|=2097152);else{if(!d){if(null===b.stateNode)throw Error(p(166));S(b);return null}a=xh(uh.current);if(Gg(b)){d=b.stateNode;c=b.type;var f=b.memoizedProps;d[Of]=b;d[Pf]=f;a=0!==(b.mode&1);switch(c){case "dialog":D("cancel",d);D("close",d);break;case "iframe":case "object":case "embed":D("load",d);break;case "video":case "audio":for(e=0;e<lf.length;e++)D(lf[e],d);break;case "source":D("error",d);break;case "img":case "image":case "link":D("error",
d);D("load",d);break;case "details":D("toggle",d);break;case "input":Za(d,f);D("invalid",d);break;case "select":d._wrapperState={wasMultiple:!!f.multiple};D("invalid",d);break;case "textarea":hb(d,f),D("invalid",d)}ub(c,f);e=null;for(var g in f)if(f.hasOwnProperty(g)){var h=f[g];"children"===g?"string"===typeof h?d.textContent!==h&&(!0!==f.suppressHydrationWarning&&Af(d.textContent,h,a),e=["children",h]):"number"===typeof h&&d.textContent!==""+h&&(!0!==f.suppressHydrationWarning&&Af(d.textContent,
h,a),e=["children",""+h]):ea.hasOwnProperty(g)&&null!=h&&"onScroll"===g&&D("scroll",d)}switch(c){case "input":Va(d);db(d,f,!0);break;case "textarea":Va(d);jb(d);break;case "select":case "option":break;default:"function"===typeof f.onClick&&(d.onclick=Bf)}d=e;b.updateQueue=d;null!==d&&(b.flags|=4)}else{g=9===e.nodeType?e:e.ownerDocument;"http://www.w3.org/1999/xhtml"===a&&(a=kb(c));"http://www.w3.org/1999/xhtml"===a?"script"===c?(a=g.createElement("div"),a.innerHTML="<script>\x3c/script>",a=a.removeChild(a.firstChild)):
"string"===typeof d.is?a=g.createElement(c,{is:d.is}):(a=g.createElement(c),"select"===c&&(g=a,d.multiple?g.multiple=!0:d.size&&(g.size=d.size))):a=g.createElementNS(a,c);a[Of]=b;a[Pf]=d;zj(a,b,!1,!1);b.stateNode=a;a:{g=vb(c,d);switch(c){case "dialog":D("cancel",a);D("close",a);e=d;break;case "iframe":case "object":case "embed":D("load",a);e=d;break;case "video":case "audio":for(e=0;e<lf.length;e++)D(lf[e],a);e=d;break;case "source":D("error",a);e=d;break;case "img":case "image":case "link":D("error",
a);D("load",a);e=d;break;case "details":D("toggle",a);e=d;break;case "input":Za(a,d);e=Ya(a,d);D("invalid",a);break;case "option":e=d;break;case "select":a._wrapperState={wasMultiple:!!d.multiple};e=A({},d,{value:void 0});D("invalid",a);break;case "textarea":hb(a,d);e=gb(a,d);D("invalid",a);break;default:e=d}ub(c,e);h=e;for(f in h)if(h.hasOwnProperty(f)){var k=h[f];"style"===f?sb(a,k):"dangerouslySetInnerHTML"===f?(k=k?k.__html:void 0,null!=k&&nb(a,k)):"children"===f?"string"===typeof k?("textarea"!==
c||""!==k)&&ob(a,k):"number"===typeof k&&ob(a,""+k):"suppressContentEditableWarning"!==f&&"suppressHydrationWarning"!==f&&"autoFocus"!==f&&(ea.hasOwnProperty(f)?null!=k&&"onScroll"===f&&D("scroll",a):null!=k&&ta(a,f,k,g))}switch(c){case "input":Va(a);db(a,d,!1);break;case "textarea":Va(a);jb(a);break;case "option":null!=d.value&&a.setAttribute("value",""+Sa(d.value));break;case "select":a.multiple=!!d.multiple;f=d.value;null!=f?fb(a,!!d.multiple,f,!1):null!=d.defaultValue&&fb(a,!!d.multiple,d.defaultValue,
!0);break;default:"function"===typeof e.onClick&&(a.onclick=Bf)}switch(c){case "button":case "input":case "select":case "textarea":d=!!d.autoFocus;break a;case "img":d=!0;break a;default:d=!1}}d&&(b.flags|=4)}null!==b.ref&&(b.flags|=512,b.flags|=2097152)}S(b);return null;case 6:if(a&&null!=b.stateNode)Cj(a,b,a.memoizedProps,d);else{if("string"!==typeof d&&null===b.stateNode)throw Error(p(166));c=xh(wh.current);xh(uh.current);if(Gg(b)){d=b.stateNode;c=b.memoizedProps;d[Of]=b;if(f=d.nodeValue!==c)if(a=
xg,null!==a)switch(a.tag){case 3:Af(d.nodeValue,c,0!==(a.mode&1));break;case 5:!0!==a.memoizedProps.suppressHydrationWarning&&Af(d.nodeValue,c,0!==(a.mode&1))}f&&(b.flags|=4)}else d=(9===c.nodeType?c:c.ownerDocument).createTextNode(d),d[Of]=b,b.stateNode=d}S(b);return null;case 13:E(L);d=b.memoizedState;if(null===a||null!==a.memoizedState&&null!==a.memoizedState.dehydrated){if(I&&null!==yg&&0!==(b.mode&1)&&0===(b.flags&128))Hg(),Ig(),b.flags|=98560,f=!1;else if(f=Gg(b),null!==d&&null!==d.dehydrated){if(null===
a){if(!f)throw Error(p(318));f=b.memoizedState;f=null!==f?f.dehydrated:null;if(!f)throw Error(p(317));f[Of]=b}else Ig(),0===(b.flags&128)&&(b.memoizedState=null),b.flags|=4;S(b);f=!1}else null!==zg&&(Fj(zg),zg=null),f=!0;if(!f)return b.flags&65536?b:null}if(0!==(b.flags&128))return b.lanes=c,b;d=null!==d;d!==(null!==a&&null!==a.memoizedState)&&d&&(b.child.flags|=8192,0!==(b.mode&1)&&(null===a||0!==(L.current&1)?0===T&&(T=3):tj()));null!==b.updateQueue&&(b.flags|=4);S(b);return null;case 4:return zh(),
Aj(a,b),null===a&&sf(b.stateNode.containerInfo),S(b),null;case 10:return ah(b.type._context),S(b),null;case 17:return Zf(b.type)&&$f(),S(b),null;case 19:E(L);f=b.memoizedState;if(null===f)return S(b),null;d=0!==(b.flags&128);g=f.rendering;if(null===g)if(d)Dj(f,!1);else{if(0!==T||null!==a&&0!==(a.flags&128))for(a=b.child;null!==a;){g=Ch(a);if(null!==g){b.flags|=128;Dj(f,!1);d=g.updateQueue;null!==d&&(b.updateQueue=d,b.flags|=4);b.subtreeFlags=0;d=c;for(c=b.child;null!==c;)f=c,a=d,f.flags&=14680066,
g=f.alternate,null===g?(f.childLanes=0,f.lanes=a,f.child=null,f.subtreeFlags=0,f.memoizedProps=null,f.memoizedState=null,f.updateQueue=null,f.dependencies=null,f.stateNode=null):(f.childLanes=g.childLanes,f.lanes=g.lanes,f.child=g.child,f.subtreeFlags=0,f.deletions=null,f.memoizedProps=g.memoizedProps,f.memoizedState=g.memoizedState,f.updateQueue=g.updateQueue,f.type=g.type,a=g.dependencies,f.dependencies=null===a?null:{lanes:a.lanes,firstContext:a.firstContext}),c=c.sibling;G(L,L.current&1|2);return b.child}a=
a.sibling}null!==f.tail&&B()>Gj&&(b.flags|=128,d=!0,Dj(f,!1),b.lanes=4194304)}else{if(!d)if(a=Ch(g),null!==a){if(b.flags|=128,d=!0,c=a.updateQueue,null!==c&&(b.updateQueue=c,b.flags|=4),Dj(f,!0),null===f.tail&&"hidden"===f.tailMode&&!g.alternate&&!I)return S(b),null}else 2*B()-f.renderingStartTime>Gj&&1073741824!==c&&(b.flags|=128,d=!0,Dj(f,!1),b.lanes=4194304);f.isBackwards?(g.sibling=b.child,b.child=g):(c=f.last,null!==c?c.sibling=g:b.child=g,f.last=g)}if(null!==f.tail)return b=f.tail,f.rendering=
b,f.tail=b.sibling,f.renderingStartTime=B(),b.sibling=null,c=L.current,G(L,d?c&1|2:c&1),b;S(b);return null;case 22:case 23:return Hj(),d=null!==b.memoizedState,null!==a&&null!==a.memoizedState!==d&&(b.flags|=8192),d&&0!==(b.mode&1)?0!==(fj&1073741824)&&(S(b),b.subtreeFlags&6&&(b.flags|=8192)):S(b),null;case 24:return null;case 25:return null}throw Error(p(156,b.tag));}
function Ij(a,b){wg(b);switch(b.tag){case 1:return Zf(b.type)&&$f(),a=b.flags,a&65536?(b.flags=a&-65537|128,b):null;case 3:return zh(),E(Wf),E(H),Eh(),a=b.flags,0!==(a&65536)&&0===(a&128)?(b.flags=a&-65537|128,b):null;case 5:return Bh(b),null;case 13:E(L);a=b.memoizedState;if(null!==a&&null!==a.dehydrated){if(null===b.alternate)throw Error(p(340));Ig()}a=b.flags;return a&65536?(b.flags=a&-65537|128,b):null;case 19:return E(L),null;case 4:return zh(),null;case 10:return ah(b.type._context),null;case 22:case 23:return Hj(),
null;case 24:return null;default:return null}}var Jj=!1,U=!1,Kj="function"===typeof WeakSet?WeakSet:Set,V=null;function Lj(a,b){var c=a.ref;if(null!==c)if("function"===typeof c)try{c(null)}catch(d){W(a,b,d)}else c.current=null}function Mj(a,b,c){try{c()}catch(d){W(a,b,d)}}var Nj=!1;
function Oj(a,b){Cf=dd;a=Me();if(Ne(a)){if("selectionStart"in a)var c={start:a.selectionStart,end:a.selectionEnd};else a:{c=(c=a.ownerDocument)&&c.defaultView||window;var d=c.getSelection&&c.getSelection();if(d&&0!==d.rangeCount){c=d.anchorNode;var e=d.anchorOffset,f=d.focusNode;d=d.focusOffset;try{c.nodeType,f.nodeType}catch(F){c=null;break a}var g=0,h=-1,k=-1,l=0,m=0,q=a,r=null;b:for(;;){for(var y;;){q!==c||0!==e&&3!==q.nodeType||(h=g+e);q!==f||0!==d&&3!==q.nodeType||(k=g+d);3===q.nodeType&&(g+=
q.nodeValue.length);if(null===(y=q.firstChild))break;r=q;q=y}for(;;){if(q===a)break b;r===c&&++l===e&&(h=g);r===f&&++m===d&&(k=g);if(null!==(y=q.nextSibling))break;q=r;r=q.parentNode}q=y}c=-1===h||-1===k?null:{start:h,end:k}}else c=null}c=c||{start:0,end:0}}else c=null;Df={focusedElem:a,selectionRange:c};dd=!1;for(V=b;null!==V;)if(b=V,a=b.child,0!==(b.subtreeFlags&1028)&&null!==a)a.return=b,V=a;else for(;null!==V;){b=V;try{var n=b.alternate;if(0!==(b.flags&1024))switch(b.tag){case 0:case 11:case 15:break;
case 1:if(null!==n){var t=n.memoizedProps,J=n.memoizedState,x=b.stateNode,w=x.getSnapshotBeforeUpdate(b.elementType===b.type?t:Ci(b.type,t),J);x.__reactInternalSnapshotBeforeUpdate=w}break;case 3:var u=b.stateNode.containerInfo;1===u.nodeType?u.textContent="":9===u.nodeType&&u.documentElement&&u.removeChild(u.documentElement);break;case 5:case 6:case 4:case 17:break;default:throw Error(p(163));}}catch(F){W(b,b.return,F)}a=b.sibling;if(null!==a){a.return=b.return;V=a;break}V=b.return}n=Nj;Nj=!1;return n}
function Pj(a,b,c){var d=b.updateQueue;d=null!==d?d.lastEffect:null;if(null!==d){var e=d=d.next;do{if((e.tag&a)===a){var f=e.destroy;e.destroy=void 0;void 0!==f&&Mj(b,c,f)}e=e.next}while(e!==d)}}function Qj(a,b){b=b.updateQueue;b=null!==b?b.lastEffect:null;if(null!==b){var c=b=b.next;do{if((c.tag&a)===a){var d=c.create;c.destroy=d()}c=c.next}while(c!==b)}}function Rj(a){var b=a.ref;if(null!==b){var c=a.stateNode;switch(a.tag){case 5:a=c;break;default:a=c}"function"===typeof b?b(a):b.current=a}}
function Sj(a){var b=a.alternate;null!==b&&(a.alternate=null,Sj(b));a.child=null;a.deletions=null;a.sibling=null;5===a.tag&&(b=a.stateNode,null!==b&&(delete b[Of],delete b[Pf],delete b[of],delete b[Qf],delete b[Rf]));a.stateNode=null;a.return=null;a.dependencies=null;a.memoizedProps=null;a.memoizedState=null;a.pendingProps=null;a.stateNode=null;a.updateQueue=null}function Tj(a){return 5===a.tag||3===a.tag||4===a.tag}
function Uj(a){a:for(;;){for(;null===a.sibling;){if(null===a.return||Tj(a.return))return null;a=a.return}a.sibling.return=a.return;for(a=a.sibling;5!==a.tag&&6!==a.tag&&18!==a.tag;){if(a.flags&2)continue a;if(null===a.child||4===a.tag)continue a;else a.child.return=a,a=a.child}if(!(a.flags&2))return a.stateNode}}
function Vj(a,b,c){var d=a.tag;if(5===d||6===d)a=a.stateNode,b?8===c.nodeType?c.parentNode.insertBefore(a,b):c.insertBefore(a,b):(8===c.nodeType?(b=c.parentNode,b.insertBefore(a,c)):(b=c,b.appendChild(a)),c=c._reactRootContainer,null!==c&&void 0!==c||null!==b.onclick||(b.onclick=Bf));else if(4!==d&&(a=a.child,null!==a))for(Vj(a,b,c),a=a.sibling;null!==a;)Vj(a,b,c),a=a.sibling}
function Wj(a,b,c){var d=a.tag;if(5===d||6===d)a=a.stateNode,b?c.insertBefore(a,b):c.appendChild(a);else if(4!==d&&(a=a.child,null!==a))for(Wj(a,b,c),a=a.sibling;null!==a;)Wj(a,b,c),a=a.sibling}var X=null,Xj=!1;function Yj(a,b,c){for(c=c.child;null!==c;)Zj(a,b,c),c=c.sibling}
function Zj(a,b,c){if(lc&&"function"===typeof lc.onCommitFiberUnmount)try{lc.onCommitFiberUnmount(kc,c)}catch(h){}switch(c.tag){case 5:U||Lj(c,b);case 6:var d=X,e=Xj;X=null;Yj(a,b,c);X=d;Xj=e;null!==X&&(Xj?(a=X,c=c.stateNode,8===a.nodeType?a.parentNode.removeChild(c):a.removeChild(c)):X.removeChild(c.stateNode));break;case 18:null!==X&&(Xj?(a=X,c=c.stateNode,8===a.nodeType?Kf(a.parentNode,c):1===a.nodeType&&Kf(a,c),bd(a)):Kf(X,c.stateNode));break;case 4:d=X;e=Xj;X=c.stateNode.containerInfo;Xj=!0;
Yj(a,b,c);X=d;Xj=e;break;case 0:case 11:case 14:case 15:if(!U&&(d=c.updateQueue,null!==d&&(d=d.lastEffect,null!==d))){e=d=d.next;do{var f=e,g=f.destroy;f=f.tag;void 0!==g&&(0!==(f&2)?Mj(c,b,g):0!==(f&4)&&Mj(c,b,g));e=e.next}while(e!==d)}Yj(a,b,c);break;case 1:if(!U&&(Lj(c,b),d=c.stateNode,"function"===typeof d.componentWillUnmount))try{d.props=c.memoizedProps,d.state=c.memoizedState,d.componentWillUnmount()}catch(h){W(c,b,h)}Yj(a,b,c);break;case 21:Yj(a,b,c);break;case 22:c.mode&1?(U=(d=U)||null!==
c.memoizedState,Yj(a,b,c),U=d):Yj(a,b,c);break;default:Yj(a,b,c)}}function ak(a){var b=a.updateQueue;if(null!==b){a.updateQueue=null;var c=a.stateNode;null===c&&(c=a.stateNode=new Kj);b.forEach(function(b){var d=bk.bind(null,a,b);c.has(b)||(c.add(b),b.then(d,d))})}}
function ck(a,b){var c=b.deletions;if(null!==c)for(var d=0;d<c.length;d++){var e=c[d];try{var f=a,g=b,h=g;a:for(;null!==h;){switch(h.tag){case 5:X=h.stateNode;Xj=!1;break a;case 3:X=h.stateNode.containerInfo;Xj=!0;break a;case 4:X=h.stateNode.containerInfo;Xj=!0;break a}h=h.return}if(null===X)throw Error(p(160));Zj(f,g,e);X=null;Xj=!1;var k=e.alternate;null!==k&&(k.return=null);e.return=null}catch(l){W(e,b,l)}}if(b.subtreeFlags&12854)for(b=b.child;null!==b;)dk(b,a),b=b.sibling}
function dk(a,b){var c=a.alternate,d=a.flags;switch(a.tag){case 0:case 11:case 14:case 15:ck(b,a);ek(a);if(d&4){try{Pj(3,a,a.return),Qj(3,a)}catch(t){W(a,a.return,t)}try{Pj(5,a,a.return)}catch(t){W(a,a.return,t)}}break;case 1:ck(b,a);ek(a);d&512&&null!==c&&Lj(c,c.return);break;case 5:ck(b,a);ek(a);d&512&&null!==c&&Lj(c,c.return);if(a.flags&32){var e=a.stateNode;try{ob(e,"")}catch(t){W(a,a.return,t)}}if(d&4&&(e=a.stateNode,null!=e)){var f=a.memoizedProps,g=null!==c?c.memoizedProps:f,h=a.type,k=a.updateQueue;
a.updateQueue=null;if(null!==k)try{"input"===h&&"radio"===f.type&&null!=f.name&&ab(e,f);vb(h,g);var l=vb(h,f);for(g=0;g<k.length;g+=2){var m=k[g],q=k[g+1];"style"===m?sb(e,q):"dangerouslySetInnerHTML"===m?nb(e,q):"children"===m?ob(e,q):ta(e,m,q,l)}switch(h){case "input":bb(e,f);break;case "textarea":ib(e,f);break;case "select":var r=e._wrapperState.wasMultiple;e._wrapperState.wasMultiple=!!f.multiple;var y=f.value;null!=y?fb(e,!!f.multiple,y,!1):r!==!!f.multiple&&(null!=f.defaultValue?fb(e,!!f.multiple,
f.defaultValue,!0):fb(e,!!f.multiple,f.multiple?[]:"",!1))}e[Pf]=f}catch(t){W(a,a.return,t)}}break;case 6:ck(b,a);ek(a);if(d&4){if(null===a.stateNode)throw Error(p(162));e=a.stateNode;f=a.memoizedProps;try{e.nodeValue=f}catch(t){W(a,a.return,t)}}break;case 3:ck(b,a);ek(a);if(d&4&&null!==c&&c.memoizedState.isDehydrated)try{bd(b.containerInfo)}catch(t){W(a,a.return,t)}break;case 4:ck(b,a);ek(a);break;case 13:ck(b,a);ek(a);e=a.child;e.flags&8192&&(f=null!==e.memoizedState,e.stateNode.isHidden=f,!f||
null!==e.alternate&&null!==e.alternate.memoizedState||(fk=B()));d&4&&ak(a);break;case 22:m=null!==c&&null!==c.memoizedState;a.mode&1?(U=(l=U)||m,ck(b,a),U=l):ck(b,a);ek(a);if(d&8192){l=null!==a.memoizedState;if((a.stateNode.isHidden=l)&&!m&&0!==(a.mode&1))for(V=a,m=a.child;null!==m;){for(q=V=m;null!==V;){r=V;y=r.child;switch(r.tag){case 0:case 11:case 14:case 15:Pj(4,r,r.return);break;case 1:Lj(r,r.return);var n=r.stateNode;if("function"===typeof n.componentWillUnmount){d=r;c=r.return;try{b=d,n.props=
b.memoizedProps,n.state=b.memoizedState,n.componentWillUnmount()}catch(t){W(d,c,t)}}break;case 5:Lj(r,r.return);break;case 22:if(null!==r.memoizedState){gk(q);continue}}null!==y?(y.return=r,V=y):gk(q)}m=m.sibling}a:for(m=null,q=a;;){if(5===q.tag){if(null===m){m=q;try{e=q.stateNode,l?(f=e.style,"function"===typeof f.setProperty?f.setProperty("display","none","important"):f.display="none"):(h=q.stateNode,k=q.memoizedProps.style,g=void 0!==k&&null!==k&&k.hasOwnProperty("display")?k.display:null,h.style.display=
rb("display",g))}catch(t){W(a,a.return,t)}}}else if(6===q.tag){if(null===m)try{q.stateNode.nodeValue=l?"":q.memoizedProps}catch(t){W(a,a.return,t)}}else if((22!==q.tag&&23!==q.tag||null===q.memoizedState||q===a)&&null!==q.child){q.child.return=q;q=q.child;continue}if(q===a)break a;for(;null===q.sibling;){if(null===q.return||q.return===a)break a;m===q&&(m=null);q=q.return}m===q&&(m=null);q.sibling.return=q.return;q=q.sibling}}break;case 19:ck(b,a);ek(a);d&4&&ak(a);break;case 21:break;default:ck(b,
a),ek(a)}}function ek(a){var b=a.flags;if(b&2){try{a:{for(var c=a.return;null!==c;){if(Tj(c)){var d=c;break a}c=c.return}throw Error(p(160));}switch(d.tag){case 5:var e=d.stateNode;d.flags&32&&(ob(e,""),d.flags&=-33);var f=Uj(a);Wj(a,f,e);break;case 3:case 4:var g=d.stateNode.containerInfo,h=Uj(a);Vj(a,h,g);break;default:throw Error(p(161));}}catch(k){W(a,a.return,k)}a.flags&=-3}b&4096&&(a.flags&=-4097)}function hk(a,b,c){V=a;ik(a,b,c)}
function ik(a,b,c){for(var d=0!==(a.mode&1);null!==V;){var e=V,f=e.child;if(22===e.tag&&d){var g=null!==e.memoizedState||Jj;if(!g){var h=e.alternate,k=null!==h&&null!==h.memoizedState||U;h=Jj;var l=U;Jj=g;if((U=k)&&!l)for(V=e;null!==V;)g=V,k=g.child,22===g.tag&&null!==g.memoizedState?jk(e):null!==k?(k.return=g,V=k):jk(e);for(;null!==f;)V=f,ik(f,b,c),f=f.sibling;V=e;Jj=h;U=l}kk(a,b,c)}else 0!==(e.subtreeFlags&8772)&&null!==f?(f.return=e,V=f):kk(a,b,c)}}
function kk(a){for(;null!==V;){var b=V;if(0!==(b.flags&8772)){var c=b.alternate;try{if(0!==(b.flags&8772))switch(b.tag){case 0:case 11:case 15:U||Qj(5,b);break;case 1:var d=b.stateNode;if(b.flags&4&&!U)if(null===c)d.componentDidMount();else{var e=b.elementType===b.type?c.memoizedProps:Ci(b.type,c.memoizedProps);d.componentDidUpdate(e,c.memoizedState,d.__reactInternalSnapshotBeforeUpdate)}var f=b.updateQueue;null!==f&&sh(b,f,d);break;case 3:var g=b.updateQueue;if(null!==g){c=null;if(null!==b.child)switch(b.child.tag){case 5:c=
b.child.stateNode;break;case 1:c=b.child.stateNode}sh(b,g,c)}break;case 5:var h=b.stateNode;if(null===c&&b.flags&4){c=h;var k=b.memoizedProps;switch(b.type){case "button":case "input":case "select":case "textarea":k.autoFocus&&c.focus();break;case "img":k.src&&(c.src=k.src)}}break;case 6:break;case 4:break;case 12:break;case 13:if(null===b.memoizedState){var l=b.alternate;if(null!==l){var m=l.memoizedState;if(null!==m){var q=m.dehydrated;null!==q&&bd(q)}}}break;case 19:case 17:case 21:case 22:case 23:case 25:break;
default:throw Error(p(163));}U||b.flags&512&&Rj(b)}catch(r){W(b,b.return,r)}}if(b===a){V=null;break}c=b.sibling;if(null!==c){c.return=b.return;V=c;break}V=b.return}}function gk(a){for(;null!==V;){var b=V;if(b===a){V=null;break}var c=b.sibling;if(null!==c){c.return=b.return;V=c;break}V=b.return}}
function jk(a){for(;null!==V;){var b=V;try{switch(b.tag){case 0:case 11:case 15:var c=b.return;try{Qj(4,b)}catch(k){W(b,c,k)}break;case 1:var d=b.stateNode;if("function"===typeof d.componentDidMount){var e=b.return;try{d.componentDidMount()}catch(k){W(b,e,k)}}var f=b.return;try{Rj(b)}catch(k){W(b,f,k)}break;case 5:var g=b.return;try{Rj(b)}catch(k){W(b,g,k)}}}catch(k){W(b,b.return,k)}if(b===a){V=null;break}var h=b.sibling;if(null!==h){h.return=b.return;V=h;break}V=b.return}}
var lk=Math.ceil,mk=ua.ReactCurrentDispatcher,nk=ua.ReactCurrentOwner,ok=ua.ReactCurrentBatchConfig,K=0,Q=null,Y=null,Z=0,fj=0,ej=Uf(0),T=0,pk=null,rh=0,qk=0,rk=0,sk=null,tk=null,fk=0,Gj=Infinity,uk=null,Oi=!1,Pi=null,Ri=null,vk=!1,wk=null,xk=0,yk=0,zk=null,Ak=-1,Bk=0;function R(){return 0!==(K&6)?B():-1!==Ak?Ak:Ak=B()}
function yi(a){if(0===(a.mode&1))return 1;if(0!==(K&2)&&0!==Z)return Z&-Z;if(null!==Kg.transition)return 0===Bk&&(Bk=yc()),Bk;a=C;if(0!==a)return a;a=window.event;a=void 0===a?16:jd(a.type);return a}function gi(a,b,c,d){if(50<yk)throw yk=0,zk=null,Error(p(185));Ac(a,c,d);if(0===(K&2)||a!==Q)a===Q&&(0===(K&2)&&(qk|=c),4===T&&Ck(a,Z)),Dk(a,d),1===c&&0===K&&0===(b.mode&1)&&(Gj=B()+500,fg&&jg())}
function Dk(a,b){var c=a.callbackNode;wc(a,b);var d=uc(a,a===Q?Z:0);if(0===d)null!==c&&bc(c),a.callbackNode=null,a.callbackPriority=0;else if(b=d&-d,a.callbackPriority!==b){null!=c&&bc(c);if(1===b)0===a.tag?ig(Ek.bind(null,a)):hg(Ek.bind(null,a)),Jf(function(){0===(K&6)&&jg()}),c=null;else{switch(Dc(d)){case 1:c=fc;break;case 4:c=gc;break;case 16:c=hc;break;case 536870912:c=jc;break;default:c=hc}c=Fk(c,Gk.bind(null,a))}a.callbackPriority=b;a.callbackNode=c}}
function Gk(a,b){Ak=-1;Bk=0;if(0!==(K&6))throw Error(p(327));var c=a.callbackNode;if(Hk()&&a.callbackNode!==c)return null;var d=uc(a,a===Q?Z:0);if(0===d)return null;if(0!==(d&30)||0!==(d&a.expiredLanes)||b)b=Ik(a,d);else{b=d;var e=K;K|=2;var f=Jk();if(Q!==a||Z!==b)uk=null,Gj=B()+500,Kk(a,b);do try{Lk();break}catch(h){Mk(a,h)}while(1);$g();mk.current=f;K=e;null!==Y?b=0:(Q=null,Z=0,b=T)}if(0!==b){2===b&&(e=xc(a),0!==e&&(d=e,b=Nk(a,e)));if(1===b)throw c=pk,Kk(a,0),Ck(a,d),Dk(a,B()),c;if(6===b)Ck(a,d);
else{e=a.current.alternate;if(0===(d&30)&&!Ok(e)&&(b=Ik(a,d),2===b&&(f=xc(a),0!==f&&(d=f,b=Nk(a,f))),1===b))throw c=pk,Kk(a,0),Ck(a,d),Dk(a,B()),c;a.finishedWork=e;a.finishedLanes=d;switch(b){case 0:case 1:throw Error(p(345));case 2:Pk(a,tk,uk);break;case 3:Ck(a,d);if((d&130023424)===d&&(b=fk+500-B(),10<b)){if(0!==uc(a,0))break;e=a.suspendedLanes;if((e&d)!==d){R();a.pingedLanes|=a.suspendedLanes&e;break}a.timeoutHandle=Ff(Pk.bind(null,a,tk,uk),b);break}Pk(a,tk,uk);break;case 4:Ck(a,d);if((d&4194240)===
d)break;b=a.eventTimes;for(e=-1;0<d;){var g=31-oc(d);f=1<<g;g=b[g];g>e&&(e=g);d&=~f}d=e;d=B()-d;d=(120>d?120:480>d?480:1080>d?1080:1920>d?1920:3E3>d?3E3:4320>d?4320:1960*lk(d/1960))-d;if(10<d){a.timeoutHandle=Ff(Pk.bind(null,a,tk,uk),d);break}Pk(a,tk,uk);break;case 5:Pk(a,tk,uk);break;default:throw Error(p(329));}}}Dk(a,B());return a.callbackNode===c?Gk.bind(null,a):null}
function Nk(a,b){var c=sk;a.current.memoizedState.isDehydrated&&(Kk(a,b).flags|=256);a=Ik(a,b);2!==a&&(b=tk,tk=c,null!==b&&Fj(b));return a}function Fj(a){null===tk?tk=a:tk.push.apply(tk,a)}
function Ok(a){for(var b=a;;){if(b.flags&16384){var c=b.updateQueue;if(null!==c&&(c=c.stores,null!==c))for(var d=0;d<c.length;d++){var e=c[d],f=e.getSnapshot;e=e.value;try{if(!He(f(),e))return!1}catch(g){return!1}}}c=b.child;if(b.subtreeFlags&16384&&null!==c)c.return=b,b=c;else{if(b===a)break;for(;null===b.sibling;){if(null===b.return||b.return===a)return!0;b=b.return}b.sibling.return=b.return;b=b.sibling}}return!0}
function Ck(a,b){b&=~rk;b&=~qk;a.suspendedLanes|=b;a.pingedLanes&=~b;for(a=a.expirationTimes;0<b;){var c=31-oc(b),d=1<<c;a[c]=-1;b&=~d}}function Ek(a){if(0!==(K&6))throw Error(p(327));Hk();var b=uc(a,0);if(0===(b&1))return Dk(a,B()),null;var c=Ik(a,b);if(0!==a.tag&&2===c){var d=xc(a);0!==d&&(b=d,c=Nk(a,d))}if(1===c)throw c=pk,Kk(a,0),Ck(a,b),Dk(a,B()),c;if(6===c)throw Error(p(345));a.finishedWork=a.current.alternate;a.finishedLanes=b;Pk(a,tk,uk);Dk(a,B());return null}
function Qk(a,b){var c=K;K|=1;try{return a(b)}finally{K=c,0===K&&(Gj=B()+500,fg&&jg())}}function Rk(a){null!==wk&&0===wk.tag&&0===(K&6)&&Hk();var b=K;K|=1;var c=ok.transition,d=C;try{if(ok.transition=null,C=1,a)return a()}finally{C=d,ok.transition=c,K=b,0===(K&6)&&jg()}}function Hj(){fj=ej.current;E(ej)}
function Kk(a,b){a.finishedWork=null;a.finishedLanes=0;var c=a.timeoutHandle;-1!==c&&(a.timeoutHandle=-1,Gf(c));if(null!==Y)for(c=Y.return;null!==c;){var d=c;wg(d);switch(d.tag){case 1:d=d.type.childContextTypes;null!==d&&void 0!==d&&$f();break;case 3:zh();E(Wf);E(H);Eh();break;case 5:Bh(d);break;case 4:zh();break;case 13:E(L);break;case 19:E(L);break;case 10:ah(d.type._context);break;case 22:case 23:Hj()}c=c.return}Q=a;Y=a=Pg(a.current,null);Z=fj=b;T=0;pk=null;rk=qk=rh=0;tk=sk=null;if(null!==fh){for(b=
0;b<fh.length;b++)if(c=fh[b],d=c.interleaved,null!==d){c.interleaved=null;var e=d.next,f=c.pending;if(null!==f){var g=f.next;f.next=e;d.next=g}c.pending=d}fh=null}return a}
function Mk(a,b){do{var c=Y;try{$g();Fh.current=Rh;if(Ih){for(var d=M.memoizedState;null!==d;){var e=d.queue;null!==e&&(e.pending=null);d=d.next}Ih=!1}Hh=0;O=N=M=null;Jh=!1;Kh=0;nk.current=null;if(null===c||null===c.return){T=1;pk=b;Y=null;break}a:{var f=a,g=c.return,h=c,k=b;b=Z;h.flags|=32768;if(null!==k&&"object"===typeof k&&"function"===typeof k.then){var l=k,m=h,q=m.tag;if(0===(m.mode&1)&&(0===q||11===q||15===q)){var r=m.alternate;r?(m.updateQueue=r.updateQueue,m.memoizedState=r.memoizedState,
m.lanes=r.lanes):(m.updateQueue=null,m.memoizedState=null)}var y=Ui(g);if(null!==y){y.flags&=-257;Vi(y,g,h,f,b);y.mode&1&&Si(f,l,b);b=y;k=l;var n=b.updateQueue;if(null===n){var t=new Set;t.add(k);b.updateQueue=t}else n.add(k);break a}else{if(0===(b&1)){Si(f,l,b);tj();break a}k=Error(p(426))}}else if(I&&h.mode&1){var J=Ui(g);if(null!==J){0===(J.flags&65536)&&(J.flags|=256);Vi(J,g,h,f,b);Jg(Ji(k,h));break a}}f=k=Ji(k,h);4!==T&&(T=2);null===sk?sk=[f]:sk.push(f);f=g;do{switch(f.tag){case 3:f.flags|=65536;
b&=-b;f.lanes|=b;var x=Ni(f,k,b);ph(f,x);break a;case 1:h=k;var w=f.type,u=f.stateNode;if(0===(f.flags&128)&&("function"===typeof w.getDerivedStateFromError||null!==u&&"function"===typeof u.componentDidCatch&&(null===Ri||!Ri.has(u)))){f.flags|=65536;b&=-b;f.lanes|=b;var F=Qi(f,h,b);ph(f,F);break a}}f=f.return}while(null!==f)}Sk(c)}catch(na){b=na;Y===c&&null!==c&&(Y=c=c.return);continue}break}while(1)}function Jk(){var a=mk.current;mk.current=Rh;return null===a?Rh:a}
function tj(){if(0===T||3===T||2===T)T=4;null===Q||0===(rh&268435455)&&0===(qk&268435455)||Ck(Q,Z)}function Ik(a,b){var c=K;K|=2;var d=Jk();if(Q!==a||Z!==b)uk=null,Kk(a,b);do try{Tk();break}catch(e){Mk(a,e)}while(1);$g();K=c;mk.current=d;if(null!==Y)throw Error(p(261));Q=null;Z=0;return T}function Tk(){for(;null!==Y;)Uk(Y)}function Lk(){for(;null!==Y&&!cc();)Uk(Y)}function Uk(a){var b=Vk(a.alternate,a,fj);a.memoizedProps=a.pendingProps;null===b?Sk(a):Y=b;nk.current=null}
function Sk(a){var b=a;do{var c=b.alternate;a=b.return;if(0===(b.flags&32768)){if(c=Ej(c,b,fj),null!==c){Y=c;return}}else{c=Ij(c,b);if(null!==c){c.flags&=32767;Y=c;return}if(null!==a)a.flags|=32768,a.subtreeFlags=0,a.deletions=null;else{T=6;Y=null;return}}b=b.sibling;if(null!==b){Y=b;return}Y=b=a}while(null!==b);0===T&&(T=5)}function Pk(a,b,c){var d=C,e=ok.transition;try{ok.transition=null,C=1,Wk(a,b,c,d)}finally{ok.transition=e,C=d}return null}
function Wk(a,b,c,d){do Hk();while(null!==wk);if(0!==(K&6))throw Error(p(327));c=a.finishedWork;var e=a.finishedLanes;if(null===c)return null;a.finishedWork=null;a.finishedLanes=0;if(c===a.current)throw Error(p(177));a.callbackNode=null;a.callbackPriority=0;var f=c.lanes|c.childLanes;Bc(a,f);a===Q&&(Y=Q=null,Z=0);0===(c.subtreeFlags&2064)&&0===(c.flags&2064)||vk||(vk=!0,Fk(hc,function(){Hk();return null}));f=0!==(c.flags&15990);if(0!==(c.subtreeFlags&15990)||f){f=ok.transition;ok.transition=null;
var g=C;C=1;var h=K;K|=4;nk.current=null;Oj(a,c);dk(c,a);Oe(Df);dd=!!Cf;Df=Cf=null;a.current=c;hk(c,a,e);dc();K=h;C=g;ok.transition=f}else a.current=c;vk&&(vk=!1,wk=a,xk=e);f=a.pendingLanes;0===f&&(Ri=null);mc(c.stateNode,d);Dk(a,B());if(null!==b)for(d=a.onRecoverableError,c=0;c<b.length;c++)e=b[c],d(e.value,{componentStack:e.stack,digest:e.digest});if(Oi)throw Oi=!1,a=Pi,Pi=null,a;0!==(xk&1)&&0!==a.tag&&Hk();f=a.pendingLanes;0!==(f&1)?a===zk?yk++:(yk=0,zk=a):yk=0;jg();return null}
function Hk(){if(null!==wk){var a=Dc(xk),b=ok.transition,c=C;try{ok.transition=null;C=16>a?16:a;if(null===wk)var d=!1;else{a=wk;wk=null;xk=0;if(0!==(K&6))throw Error(p(331));var e=K;K|=4;for(V=a.current;null!==V;){var f=V,g=f.child;if(0!==(V.flags&16)){var h=f.deletions;if(null!==h){for(var k=0;k<h.length;k++){var l=h[k];for(V=l;null!==V;){var m=V;switch(m.tag){case 0:case 11:case 15:Pj(8,m,f)}var q=m.child;if(null!==q)q.return=m,V=q;else for(;null!==V;){m=V;var r=m.sibling,y=m.return;Sj(m);if(m===
l){V=null;break}if(null!==r){r.return=y;V=r;break}V=y}}}var n=f.alternate;if(null!==n){var t=n.child;if(null!==t){n.child=null;do{var J=t.sibling;t.sibling=null;t=J}while(null!==t)}}V=f}}if(0!==(f.subtreeFlags&2064)&&null!==g)g.return=f,V=g;else b:for(;null!==V;){f=V;if(0!==(f.flags&2048))switch(f.tag){case 0:case 11:case 15:Pj(9,f,f.return)}var x=f.sibling;if(null!==x){x.return=f.return;V=x;break b}V=f.return}}var w=a.current;for(V=w;null!==V;){g=V;var u=g.child;if(0!==(g.subtreeFlags&2064)&&null!==
u)u.return=g,V=u;else b:for(g=w;null!==V;){h=V;if(0!==(h.flags&2048))try{switch(h.tag){case 0:case 11:case 15:Qj(9,h)}}catch(na){W(h,h.return,na)}if(h===g){V=null;break b}var F=h.sibling;if(null!==F){F.return=h.return;V=F;break b}V=h.return}}K=e;jg();if(lc&&"function"===typeof lc.onPostCommitFiberRoot)try{lc.onPostCommitFiberRoot(kc,a)}catch(na){}d=!0}return d}finally{C=c,ok.transition=b}}return!1}function Xk(a,b,c){b=Ji(c,b);b=Ni(a,b,1);a=nh(a,b,1);b=R();null!==a&&(Ac(a,1,b),Dk(a,b))}
function W(a,b,c){if(3===a.tag)Xk(a,a,c);else for(;null!==b;){if(3===b.tag){Xk(b,a,c);break}else if(1===b.tag){var d=b.stateNode;if("function"===typeof b.type.getDerivedStateFromError||"function"===typeof d.componentDidCatch&&(null===Ri||!Ri.has(d))){a=Ji(c,a);a=Qi(b,a,1);b=nh(b,a,1);a=R();null!==b&&(Ac(b,1,a),Dk(b,a));break}}b=b.return}}
function Ti(a,b,c){var d=a.pingCache;null!==d&&d.delete(b);b=R();a.pingedLanes|=a.suspendedLanes&c;Q===a&&(Z&c)===c&&(4===T||3===T&&(Z&130023424)===Z&&500>B()-fk?Kk(a,0):rk|=c);Dk(a,b)}function Yk(a,b){0===b&&(0===(a.mode&1)?b=1:(b=sc,sc<<=1,0===(sc&130023424)&&(sc=4194304)));var c=R();a=ih(a,b);null!==a&&(Ac(a,b,c),Dk(a,c))}function uj(a){var b=a.memoizedState,c=0;null!==b&&(c=b.retryLane);Yk(a,c)}
function bk(a,b){var c=0;switch(a.tag){case 13:var d=a.stateNode;var e=a.memoizedState;null!==e&&(c=e.retryLane);break;case 19:d=a.stateNode;break;default:throw Error(p(314));}null!==d&&d.delete(b);Yk(a,c)}var Vk;
Vk=function(a,b,c){if(null!==a)if(a.memoizedProps!==b.pendingProps||Wf.current)dh=!0;else{if(0===(a.lanes&c)&&0===(b.flags&128))return dh=!1,yj(a,b,c);dh=0!==(a.flags&131072)?!0:!1}else dh=!1,I&&0!==(b.flags&1048576)&&ug(b,ng,b.index);b.lanes=0;switch(b.tag){case 2:var d=b.type;ij(a,b);a=b.pendingProps;var e=Yf(b,H.current);ch(b,c);e=Nh(null,b,d,a,e,c);var f=Sh();b.flags|=1;"object"===typeof e&&null!==e&&"function"===typeof e.render&&void 0===e.$$typeof?(b.tag=1,b.memoizedState=null,b.updateQueue=
null,Zf(d)?(f=!0,cg(b)):f=!1,b.memoizedState=null!==e.state&&void 0!==e.state?e.state:null,kh(b),e.updater=Ei,b.stateNode=e,e._reactInternals=b,Ii(b,d,a,c),b=jj(null,b,d,!0,f,c)):(b.tag=0,I&&f&&vg(b),Xi(null,b,e,c),b=b.child);return b;case 16:d=b.elementType;a:{ij(a,b);a=b.pendingProps;e=d._init;d=e(d._payload);b.type=d;e=b.tag=Zk(d);a=Ci(d,a);switch(e){case 0:b=cj(null,b,d,a,c);break a;case 1:b=hj(null,b,d,a,c);break a;case 11:b=Yi(null,b,d,a,c);break a;case 14:b=$i(null,b,d,Ci(d.type,a),c);break a}throw Error(p(306,
d,""));}return b;case 0:return d=b.type,e=b.pendingProps,e=b.elementType===d?e:Ci(d,e),cj(a,b,d,e,c);case 1:return d=b.type,e=b.pendingProps,e=b.elementType===d?e:Ci(d,e),hj(a,b,d,e,c);case 3:a:{kj(b);if(null===a)throw Error(p(387));d=b.pendingProps;f=b.memoizedState;e=f.element;lh(a,b);qh(b,d,null,c);var g=b.memoizedState;d=g.element;if(f.isDehydrated)if(f={element:d,isDehydrated:!1,cache:g.cache,pendingSuspenseBoundaries:g.pendingSuspenseBoundaries,transitions:g.transitions},b.updateQueue.baseState=
f,b.memoizedState=f,b.flags&256){e=Ji(Error(p(423)),b);b=lj(a,b,d,c,e);break a}else if(d!==e){e=Ji(Error(p(424)),b);b=lj(a,b,d,c,e);break a}else for(yg=Lf(b.stateNode.containerInfo.firstChild),xg=b,I=!0,zg=null,c=Vg(b,null,d,c),b.child=c;c;)c.flags=c.flags&-3|4096,c=c.sibling;else{Ig();if(d===e){b=Zi(a,b,c);break a}Xi(a,b,d,c)}b=b.child}return b;case 5:return Ah(b),null===a&&Eg(b),d=b.type,e=b.pendingProps,f=null!==a?a.memoizedProps:null,g=e.children,Ef(d,e)?g=null:null!==f&&Ef(d,f)&&(b.flags|=32),
gj(a,b),Xi(a,b,g,c),b.child;case 6:return null===a&&Eg(b),null;case 13:return oj(a,b,c);case 4:return yh(b,b.stateNode.containerInfo),d=b.pendingProps,null===a?b.child=Ug(b,null,d,c):Xi(a,b,d,c),b.child;case 11:return d=b.type,e=b.pendingProps,e=b.elementType===d?e:Ci(d,e),Yi(a,b,d,e,c);case 7:return Xi(a,b,b.pendingProps,c),b.child;case 8:return Xi(a,b,b.pendingProps.children,c),b.child;case 12:return Xi(a,b,b.pendingProps.children,c),b.child;case 10:a:{d=b.type._context;e=b.pendingProps;f=b.memoizedProps;
g=e.value;G(Wg,d._currentValue);d._currentValue=g;if(null!==f)if(He(f.value,g)){if(f.children===e.children&&!Wf.current){b=Zi(a,b,c);break a}}else for(f=b.child,null!==f&&(f.return=b);null!==f;){var h=f.dependencies;if(null!==h){g=f.child;for(var k=h.firstContext;null!==k;){if(k.context===d){if(1===f.tag){k=mh(-1,c&-c);k.tag=2;var l=f.updateQueue;if(null!==l){l=l.shared;var m=l.pending;null===m?k.next=k:(k.next=m.next,m.next=k);l.pending=k}}f.lanes|=c;k=f.alternate;null!==k&&(k.lanes|=c);bh(f.return,
c,b);h.lanes|=c;break}k=k.next}}else if(10===f.tag)g=f.type===b.type?null:f.child;else if(18===f.tag){g=f.return;if(null===g)throw Error(p(341));g.lanes|=c;h=g.alternate;null!==h&&(h.lanes|=c);bh(g,c,b);g=f.sibling}else g=f.child;if(null!==g)g.return=f;else for(g=f;null!==g;){if(g===b){g=null;break}f=g.sibling;if(null!==f){f.return=g.return;g=f;break}g=g.return}f=g}Xi(a,b,e.children,c);b=b.child}return b;case 9:return e=b.type,d=b.pendingProps.children,ch(b,c),e=eh(e),d=d(e),b.flags|=1,Xi(a,b,d,c),
b.child;case 14:return d=b.type,e=Ci(d,b.pendingProps),e=Ci(d.type,e),$i(a,b,d,e,c);case 15:return bj(a,b,b.type,b.pendingProps,c);case 17:return d=b.type,e=b.pendingProps,e=b.elementType===d?e:Ci(d,e),ij(a,b),b.tag=1,Zf(d)?(a=!0,cg(b)):a=!1,ch(b,c),Gi(b,d,e),Ii(b,d,e,c),jj(null,b,d,!0,a,c);case 19:return xj(a,b,c);case 22:return dj(a,b,c)}throw Error(p(156,b.tag));};function Fk(a,b){return ac(a,b)}
function $k(a,b,c,d){this.tag=a;this.key=c;this.sibling=this.child=this.return=this.stateNode=this.type=this.elementType=null;this.index=0;this.ref=null;this.pendingProps=b;this.dependencies=this.memoizedState=this.updateQueue=this.memoizedProps=null;this.mode=d;this.subtreeFlags=this.flags=0;this.deletions=null;this.childLanes=this.lanes=0;this.alternate=null}function Bg(a,b,c,d){return new $k(a,b,c,d)}function aj(a){a=a.prototype;return!(!a||!a.isReactComponent)}
function Zk(a){if("function"===typeof a)return aj(a)?1:0;if(void 0!==a&&null!==a){a=a.$$typeof;if(a===Da)return 11;if(a===Ga)return 14}return 2}
function Pg(a,b){var c=a.alternate;null===c?(c=Bg(a.tag,b,a.key,a.mode),c.elementType=a.elementType,c.type=a.type,c.stateNode=a.stateNode,c.alternate=a,a.alternate=c):(c.pendingProps=b,c.type=a.type,c.flags=0,c.subtreeFlags=0,c.deletions=null);c.flags=a.flags&14680064;c.childLanes=a.childLanes;c.lanes=a.lanes;c.child=a.child;c.memoizedProps=a.memoizedProps;c.memoizedState=a.memoizedState;c.updateQueue=a.updateQueue;b=a.dependencies;c.dependencies=null===b?null:{lanes:b.lanes,firstContext:b.firstContext};
c.sibling=a.sibling;c.index=a.index;c.ref=a.ref;return c}
function Rg(a,b,c,d,e,f){var g=2;d=a;if("function"===typeof a)aj(a)&&(g=1);else if("string"===typeof a)g=5;else a:switch(a){case ya:return Tg(c.children,e,f,b);case za:g=8;e|=8;break;case Aa:return a=Bg(12,c,b,e|2),a.elementType=Aa,a.lanes=f,a;case Ea:return a=Bg(13,c,b,e),a.elementType=Ea,a.lanes=f,a;case Fa:return a=Bg(19,c,b,e),a.elementType=Fa,a.lanes=f,a;case Ia:return pj(c,e,f,b);default:if("object"===typeof a&&null!==a)switch(a.$$typeof){case Ba:g=10;break a;case Ca:g=9;break a;case Da:g=11;
break a;case Ga:g=14;break a;case Ha:g=16;d=null;break a}throw Error(p(130,null==a?a:typeof a,""));}b=Bg(g,c,b,e);b.elementType=a;b.type=d;b.lanes=f;return b}function Tg(a,b,c,d){a=Bg(7,a,d,b);a.lanes=c;return a}function pj(a,b,c,d){a=Bg(22,a,d,b);a.elementType=Ia;a.lanes=c;a.stateNode={isHidden:!1};return a}function Qg(a,b,c){a=Bg(6,a,null,b);a.lanes=c;return a}
function Sg(a,b,c){b=Bg(4,null!==a.children?a.children:[],a.key,b);b.lanes=c;b.stateNode={containerInfo:a.containerInfo,pendingChildren:null,implementation:a.implementation};return b}
function al(a,b,c,d,e){this.tag=b;this.containerInfo=a;this.finishedWork=this.pingCache=this.current=this.pendingChildren=null;this.timeoutHandle=-1;this.callbackNode=this.pendingContext=this.context=null;this.callbackPriority=0;this.eventTimes=zc(0);this.expirationTimes=zc(-1);this.entangledLanes=this.finishedLanes=this.mutableReadLanes=this.expiredLanes=this.pingedLanes=this.suspendedLanes=this.pendingLanes=0;this.entanglements=zc(0);this.identifierPrefix=d;this.onRecoverableError=e;this.mutableSourceEagerHydrationData=
null}function bl(a,b,c,d,e,f,g,h,k){a=new al(a,b,c,h,k);1===b?(b=1,!0===f&&(b|=8)):b=0;f=Bg(3,null,null,b);a.current=f;f.stateNode=a;f.memoizedState={element:d,isDehydrated:c,cache:null,transitions:null,pendingSuspenseBoundaries:null};kh(f);return a}function cl(a,b,c){var d=3<arguments.length&&void 0!==arguments[3]?arguments[3]:null;return{$$typeof:wa,key:null==d?null:""+d,children:a,containerInfo:b,implementation:c}}
function dl(a){if(!a)return Vf;a=a._reactInternals;a:{if(Vb(a)!==a||1!==a.tag)throw Error(p(170));var b=a;do{switch(b.tag){case 3:b=b.stateNode.context;break a;case 1:if(Zf(b.type)){b=b.stateNode.__reactInternalMemoizedMergedChildContext;break a}}b=b.return}while(null!==b);throw Error(p(171));}if(1===a.tag){var c=a.type;if(Zf(c))return bg(a,c,b)}return b}
function el(a,b,c,d,e,f,g,h,k){a=bl(c,d,!0,a,e,f,g,h,k);a.context=dl(null);c=a.current;d=R();e=yi(c);f=mh(d,e);f.callback=void 0!==b&&null!==b?b:null;nh(c,f,e);a.current.lanes=e;Ac(a,e,d);Dk(a,d);return a}function fl(a,b,c,d){var e=b.current,f=R(),g=yi(e);c=dl(c);null===b.context?b.context=c:b.pendingContext=c;b=mh(f,g);b.payload={element:a};d=void 0===d?null:d;null!==d&&(b.callback=d);a=nh(e,b,g);null!==a&&(gi(a,e,g,f),oh(a,e,g));return g}
function gl(a){a=a.current;if(!a.child)return null;switch(a.child.tag){case 5:return a.child.stateNode;default:return a.child.stateNode}}function hl(a,b){a=a.memoizedState;if(null!==a&&null!==a.dehydrated){var c=a.retryLane;a.retryLane=0!==c&&c<b?c:b}}function il(a,b){hl(a,b);(a=a.alternate)&&hl(a,b)}function jl(){return null}var kl="function"===typeof reportError?reportError:function(a){console.error(a)};function ll(a){this._internalRoot=a}
ml.prototype.render=ll.prototype.render=function(a){var b=this._internalRoot;if(null===b)throw Error(p(409));fl(a,b,null,null)};ml.prototype.unmount=ll.prototype.unmount=function(){var a=this._internalRoot;if(null!==a){this._internalRoot=null;var b=a.containerInfo;Rk(function(){fl(null,a,null,null)});b[uf]=null}};function ml(a){this._internalRoot=a}
ml.prototype.unstable_scheduleHydration=function(a){if(a){var b=Hc();a={blockedOn:null,target:a,priority:b};for(var c=0;c<Qc.length&&0!==b&&b<Qc[c].priority;c++);Qc.splice(c,0,a);0===c&&Vc(a)}};function nl(a){return!(!a||1!==a.nodeType&&9!==a.nodeType&&11!==a.nodeType)}function ol(a){return!(!a||1!==a.nodeType&&9!==a.nodeType&&11!==a.nodeType&&(8!==a.nodeType||" react-mount-point-unstable "!==a.nodeValue))}function pl(){}
function ql(a,b,c,d,e){if(e){if("function"===typeof d){var f=d;d=function(){var a=gl(g);f.call(a)}}var g=el(b,d,a,0,null,!1,!1,"",pl);a._reactRootContainer=g;a[uf]=g.current;sf(8===a.nodeType?a.parentNode:a);Rk();return g}for(;e=a.lastChild;)a.removeChild(e);if("function"===typeof d){var h=d;d=function(){var a=gl(k);h.call(a)}}var k=bl(a,0,!1,null,null,!1,!1,"",pl);a._reactRootContainer=k;a[uf]=k.current;sf(8===a.nodeType?a.parentNode:a);Rk(function(){fl(b,k,c,d)});return k}
function rl(a,b,c,d,e){var f=c._reactRootContainer;if(f){var g=f;if("function"===typeof e){var h=e;e=function(){var a=gl(g);h.call(a)}}fl(b,g,a,e)}else g=ql(c,b,a,e,d);return gl(g)}Ec=function(a){switch(a.tag){case 3:var b=a.stateNode;if(b.current.memoizedState.isDehydrated){var c=tc(b.pendingLanes);0!==c&&(Cc(b,c|1),Dk(b,B()),0===(K&6)&&(Gj=B()+500,jg()))}break;case 13:Rk(function(){var b=ih(a,1);if(null!==b){var c=R();gi(b,a,1,c)}}),il(a,1)}};
Fc=function(a){if(13===a.tag){var b=ih(a,134217728);if(null!==b){var c=R();gi(b,a,134217728,c)}il(a,134217728)}};Gc=function(a){if(13===a.tag){var b=yi(a),c=ih(a,b);if(null!==c){var d=R();gi(c,a,b,d)}il(a,b)}};Hc=function(){return C};Ic=function(a,b){var c=C;try{return C=a,b()}finally{C=c}};
yb=function(a,b,c){switch(b){case "input":bb(a,c);b=c.name;if("radio"===c.type&&null!=b){for(c=a;c.parentNode;)c=c.parentNode;c=c.querySelectorAll("input[name="+JSON.stringify(""+b)+'][type="radio"]');for(b=0;b<c.length;b++){var d=c[b];if(d!==a&&d.form===a.form){var e=Db(d);if(!e)throw Error(p(90));Wa(d);bb(d,e)}}}break;case "textarea":ib(a,c);break;case "select":b=c.value,null!=b&&fb(a,!!c.multiple,b,!1)}};Gb=Qk;Hb=Rk;
var sl={usingClientEntryPoint:!1,Events:[Cb,ue,Db,Eb,Fb,Qk]},tl={findFiberByHostInstance:Wc,bundleType:0,version:"18.3.1",rendererPackageName:"react-dom"};
var ul={bundleType:tl.bundleType,version:tl.version,rendererPackageName:tl.rendererPackageName,rendererConfig:tl.rendererConfig,overrideHookState:null,overrideHookStateDeletePath:null,overrideHookStateRenamePath:null,overrideProps:null,overridePropsDeletePath:null,overridePropsRenamePath:null,setErrorHandler:null,setSuspenseHandler:null,scheduleUpdate:null,currentDispatcherRef:ua.ReactCurrentDispatcher,findHostInstanceByFiber:function(a){a=Zb(a);return null===a?null:a.stateNode},findFiberByHostInstance:tl.findFiberByHostInstance||
jl,findHostInstancesForRefresh:null,scheduleRefresh:null,scheduleRoot:null,setRefreshHandler:null,getCurrentFiber:null,reconcilerVersion:"18.3.1-next-f1338f8080-20240426"};if("undefined"!==typeof __REACT_DEVTOOLS_GLOBAL_HOOK__){var vl=__REACT_DEVTOOLS_GLOBAL_HOOK__;if(!vl.isDisabled&&vl.supportsFiber)try{kc=vl.inject(ul),lc=vl}catch(a){}}exports.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=sl;
exports.createPortal=function(a,b){var c=2<arguments.length&&void 0!==arguments[2]?arguments[2]:null;if(!nl(b))throw Error(p(200));return cl(a,b,null,c)};exports.createRoot=function(a,b){if(!nl(a))throw Error(p(299));var c=!1,d="",e=kl;null!==b&&void 0!==b&&(!0===b.unstable_strictMode&&(c=!0),void 0!==b.identifierPrefix&&(d=b.identifierPrefix),void 0!==b.onRecoverableError&&(e=b.onRecoverableError));b=bl(a,1,!1,null,null,c,!1,d,e);a[uf]=b.current;sf(8===a.nodeType?a.parentNode:a);return new ll(b)};
exports.findDOMNode=function(a){if(null==a)return null;if(1===a.nodeType)return a;var b=a._reactInternals;if(void 0===b){if("function"===typeof a.render)throw Error(p(188));a=Object.keys(a).join(",");throw Error(p(268,a));}a=Zb(b);a=null===a?null:a.stateNode;return a};exports.flushSync=function(a){return Rk(a)};exports.hydrate=function(a,b,c){if(!ol(b))throw Error(p(200));return rl(null,a,b,!0,c)};
exports.hydrateRoot=function(a,b,c){if(!nl(a))throw Error(p(405));var d=null!=c&&c.hydratedSources||null,e=!1,f="",g=kl;null!==c&&void 0!==c&&(!0===c.unstable_strictMode&&(e=!0),void 0!==c.identifierPrefix&&(f=c.identifierPrefix),void 0!==c.onRecoverableError&&(g=c.onRecoverableError));b=el(b,null,a,1,null!=c?c:null,e,!1,f,g);a[uf]=b.current;sf(a);if(d)for(a=0;a<d.length;a++)c=d[a],e=c._getVersion,e=e(c._source),null==b.mutableSourceEagerHydrationData?b.mutableSourceEagerHydrationData=[c,e]:b.mutableSourceEagerHydrationData.push(c,
e);return new ml(b)};exports.render=function(a,b,c){if(!ol(b))throw Error(p(200));return rl(null,a,b,!1,c)};exports.unmountComponentAtNode=function(a){if(!ol(a))throw Error(p(40));return a._reactRootContainer?(Rk(function(){rl(null,null,a,!1,function(){a._reactRootContainer=null;a[uf]=null})}),!0):!1};exports.unstable_batchedUpdates=Qk;
exports.unstable_renderSubtreeIntoContainer=function(a,b,c,d){if(!ol(c))throw Error(p(200));if(null==a||void 0===a._reactInternals)throw Error(p(38));return rl(a,b,c,!1,d)};exports.version="18.3.1-next-f1338f8080-20240426";


/***/ },

/***/ 659
(module) {



var memo = {};

/* istanbul ignore next  */
function getTarget(target) {
  if (typeof memo[target] === "undefined") {
    var styleTarget = document.querySelector(target);

    // Special case to return head of iframe instead of iframe itself
    if (window.HTMLIFrameElement && styleTarget instanceof window.HTMLIFrameElement) {
      try {
        // This will throw an exception if access to iframe is blocked
        // due to cross-origin restrictions
        styleTarget = styleTarget.contentDocument.head;
      } catch (e) {
        // istanbul ignore next
        styleTarget = null;
      }
    }
    memo[target] = styleTarget;
  }
  return memo[target];
}

/* istanbul ignore next  */
function insertBySelector(insert, style) {
  var target = getTarget(insert);
  if (!target) {
    throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");
  }
  target.appendChild(style);
}
module.exports = insertBySelector;

/***/ },

/***/ 784
(module, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   A: () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(354);
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(314);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `*, ::before, ::after {
  --tw-border-spacing-x: 0;
  --tw-border-spacing-y: 0;
  --tw-translate-x: 0;
  --tw-translate-y: 0;
  --tw-rotate: 0;
  --tw-skew-x: 0;
  --tw-skew-y: 0;
  --tw-scale-x: 1;
  --tw-scale-y: 1;
  --tw-pan-x:  ;
  --tw-pan-y:  ;
  --tw-pinch-zoom:  ;
  --tw-scroll-snap-strictness: proximity;
  --tw-gradient-from-position:  ;
  --tw-gradient-via-position:  ;
  --tw-gradient-to-position:  ;
  --tw-ordinal:  ;
  --tw-slashed-zero:  ;
  --tw-numeric-figure:  ;
  --tw-numeric-spacing:  ;
  --tw-numeric-fraction:  ;
  --tw-ring-inset:  ;
  --tw-ring-offset-width: 0px;
  --tw-ring-offset-color: #fff;
  --tw-ring-color: rgb(59 130 246 / 0.5);
  --tw-ring-offset-shadow: 0 0 #0000;
  --tw-ring-shadow: 0 0 #0000;
  --tw-shadow: 0 0 #0000;
  --tw-shadow-colored: 0 0 #0000;
  --tw-blur:  ;
  --tw-brightness:  ;
  --tw-contrast:  ;
  --tw-grayscale:  ;
  --tw-hue-rotate:  ;
  --tw-invert:  ;
  --tw-saturate:  ;
  --tw-sepia:  ;
  --tw-drop-shadow:  ;
  --tw-backdrop-blur:  ;
  --tw-backdrop-brightness:  ;
  --tw-backdrop-contrast:  ;
  --tw-backdrop-grayscale:  ;
  --tw-backdrop-hue-rotate:  ;
  --tw-backdrop-invert:  ;
  --tw-backdrop-opacity:  ;
  --tw-backdrop-saturate:  ;
  --tw-backdrop-sepia:  ;
  --tw-contain-size:  ;
  --tw-contain-layout:  ;
  --tw-contain-paint:  ;
  --tw-contain-style:  ;
}

::backdrop {
  --tw-border-spacing-x: 0;
  --tw-border-spacing-y: 0;
  --tw-translate-x: 0;
  --tw-translate-y: 0;
  --tw-rotate: 0;
  --tw-skew-x: 0;
  --tw-skew-y: 0;
  --tw-scale-x: 1;
  --tw-scale-y: 1;
  --tw-pan-x:  ;
  --tw-pan-y:  ;
  --tw-pinch-zoom:  ;
  --tw-scroll-snap-strictness: proximity;
  --tw-gradient-from-position:  ;
  --tw-gradient-via-position:  ;
  --tw-gradient-to-position:  ;
  --tw-ordinal:  ;
  --tw-slashed-zero:  ;
  --tw-numeric-figure:  ;
  --tw-numeric-spacing:  ;
  --tw-numeric-fraction:  ;
  --tw-ring-inset:  ;
  --tw-ring-offset-width: 0px;
  --tw-ring-offset-color: #fff;
  --tw-ring-color: rgb(59 130 246 / 0.5);
  --tw-ring-offset-shadow: 0 0 #0000;
  --tw-ring-shadow: 0 0 #0000;
  --tw-shadow: 0 0 #0000;
  --tw-shadow-colored: 0 0 #0000;
  --tw-blur:  ;
  --tw-brightness:  ;
  --tw-contrast:  ;
  --tw-grayscale:  ;
  --tw-hue-rotate:  ;
  --tw-invert:  ;
  --tw-saturate:  ;
  --tw-sepia:  ;
  --tw-drop-shadow:  ;
  --tw-backdrop-blur:  ;
  --tw-backdrop-brightness:  ;
  --tw-backdrop-contrast:  ;
  --tw-backdrop-grayscale:  ;
  --tw-backdrop-hue-rotate:  ;
  --tw-backdrop-invert:  ;
  --tw-backdrop-opacity:  ;
  --tw-backdrop-saturate:  ;
  --tw-backdrop-sepia:  ;
  --tw-contain-size:  ;
  --tw-contain-layout:  ;
  --tw-contain-paint:  ;
  --tw-contain-style:  ;
}/*
! tailwindcss v3.4.19 | MIT License | https://tailwindcss.com
*//*
1. Prevent padding and border from affecting element width. (https://github.com/mozdevs/cssremedy/issues/4)
2. Allow adding a border to an element by just adding a border-width. (https://github.com/tailwindcss/tailwindcss/pull/116)
*/

*,
::before,
::after {
  box-sizing: border-box; /* 1 */
  border-width: 0; /* 2 */
  border-style: solid; /* 2 */
  border-color: #e5e7eb; /* 2 */
}

::before,
::after {
  --tw-content: '';
}

/*
1. Use a consistent sensible line-height in all browsers.
2. Prevent adjustments of font size after orientation changes in iOS.
3. Use a more readable tab size.
4. Use the user's configured \`sans\` font-family by default.
5. Use the user's configured \`sans\` font-feature-settings by default.
6. Use the user's configured \`sans\` font-variation-settings by default.
7. Disable tap highlights on iOS
*/

html,
:host {
  line-height: 1.5; /* 1 */
  -webkit-text-size-adjust: 100%; /* 2 */
  -moz-tab-size: 4; /* 3 */
  -o-tab-size: 4;
     tab-size: 4; /* 3 */
  font-family: ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"; /* 4 */
  font-feature-settings: normal; /* 5 */
  font-variation-settings: normal; /* 6 */
  -webkit-tap-highlight-color: transparent; /* 7 */
}

/*
1. Remove the margin in all browsers.
2. Inherit line-height from \`html\` so users can set them as a class directly on the \`html\` element.
*/

body {
  margin: 0; /* 1 */
  line-height: inherit; /* 2 */
}

/*
1. Add the correct height in Firefox.
2. Correct the inheritance of border color in Firefox. (https://bugzilla.mozilla.org/show_bug.cgi?id=190655)
3. Ensure horizontal rules are visible by default.
*/

hr {
  height: 0; /* 1 */
  color: inherit; /* 2 */
  border-top-width: 1px; /* 3 */
}

/*
Add the correct text decoration in Chrome, Edge, and Safari.
*/

abbr:where([title]) {
  -webkit-text-decoration: underline dotted;
          text-decoration: underline dotted;
}

/*
Remove the default font size and weight for headings.
*/

h1,
h2,
h3,
h4,
h5,
h6 {
  font-size: inherit;
  font-weight: inherit;
}

/*
Reset links to optimize for opt-in styling instead of opt-out.
*/

a {
  color: inherit;
  text-decoration: inherit;
}

/*
Add the correct font weight in Edge and Safari.
*/

b,
strong {
  font-weight: bolder;
}

/*
1. Use the user's configured \`mono\` font-family by default.
2. Use the user's configured \`mono\` font-feature-settings by default.
3. Use the user's configured \`mono\` font-variation-settings by default.
4. Correct the odd \`em\` font sizing in all browsers.
*/

code,
kbd,
samp,
pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; /* 1 */
  font-feature-settings: normal; /* 2 */
  font-variation-settings: normal; /* 3 */
  font-size: 1em; /* 4 */
}

/*
Add the correct font size in all browsers.
*/

small {
  font-size: 80%;
}

/*
Prevent \`sub\` and \`sup\` elements from affecting the line height in all browsers.
*/

sub,
sup {
  font-size: 75%;
  line-height: 0;
  position: relative;
  vertical-align: baseline;
}

sub {
  bottom: -0.25em;
}

sup {
  top: -0.5em;
}

/*
1. Remove text indentation from table contents in Chrome and Safari. (https://bugs.chromium.org/p/chromium/issues/detail?id=999088, https://bugs.webkit.org/show_bug.cgi?id=201297)
2. Correct table border color inheritance in all Chrome and Safari. (https://bugs.chromium.org/p/chromium/issues/detail?id=935729, https://bugs.webkit.org/show_bug.cgi?id=195016)
3. Remove gaps between table borders by default.
*/

table {
  text-indent: 0; /* 1 */
  border-color: inherit; /* 2 */
  border-collapse: collapse; /* 3 */
}

/*
1. Change the font styles in all browsers.
2. Remove the margin in Firefox and Safari.
3. Remove default padding in all browsers.
*/

button,
input,
optgroup,
select,
textarea {
  font-family: inherit; /* 1 */
  font-feature-settings: inherit; /* 1 */
  font-variation-settings: inherit; /* 1 */
  font-size: 100%; /* 1 */
  font-weight: inherit; /* 1 */
  line-height: inherit; /* 1 */
  letter-spacing: inherit; /* 1 */
  color: inherit; /* 1 */
  margin: 0; /* 2 */
  padding: 0; /* 3 */
}

/*
Remove the inheritance of text transform in Edge and Firefox.
*/

button,
select {
  text-transform: none;
}

/*
1. Correct the inability to style clickable types in iOS and Safari.
2. Remove default button styles.
*/

button,
input:where([type='button']),
input:where([type='reset']),
input:where([type='submit']) {
  -webkit-appearance: button; /* 1 */
  background-color: transparent; /* 2 */
  background-image: none; /* 2 */
}

/*
Use the modern Firefox focus style for all focusable elements.
*/

:-moz-focusring {
  outline: auto;
}

/*
Remove the additional \`:invalid\` styles in Firefox. (https://github.com/mozilla/gecko-dev/blob/2f9eacd9d3d995c937b4251a5557d95d494c9be1/layout/style/res/forms.css#L728-L737)
*/

:-moz-ui-invalid {
  box-shadow: none;
}

/*
Add the correct vertical alignment in Chrome and Firefox.
*/

progress {
  vertical-align: baseline;
}

/*
Correct the cursor style of increment and decrement buttons in Safari.
*/

::-webkit-inner-spin-button,
::-webkit-outer-spin-button {
  height: auto;
}

/*
1. Correct the odd appearance in Chrome and Safari.
2. Correct the outline style in Safari.
*/

[type='search'] {
  -webkit-appearance: textfield; /* 1 */
  outline-offset: -2px; /* 2 */
}

/*
Remove the inner padding in Chrome and Safari on macOS.
*/

::-webkit-search-decoration {
  -webkit-appearance: none;
}

/*
1. Correct the inability to style clickable types in iOS and Safari.
2. Change font properties to \`inherit\` in Safari.
*/

::-webkit-file-upload-button {
  -webkit-appearance: button; /* 1 */
  font: inherit; /* 2 */
}

/*
Add the correct display in Chrome and Safari.
*/

summary {
  display: list-item;
}

/*
Removes the default spacing and border for appropriate elements.
*/

blockquote,
dl,
dd,
h1,
h2,
h3,
h4,
h5,
h6,
hr,
figure,
p,
pre {
  margin: 0;
}

fieldset {
  margin: 0;
  padding: 0;
}

legend {
  padding: 0;
}

ol,
ul,
menu {
  list-style: none;
  margin: 0;
  padding: 0;
}

/*
Reset default styling for dialogs.
*/
dialog {
  padding: 0;
}

/*
Prevent resizing textareas horizontally by default.
*/

textarea {
  resize: vertical;
}

/*
1. Reset the default placeholder opacity in Firefox. (https://github.com/tailwindlabs/tailwindcss/issues/3300)
2. Set the default placeholder color to the user's configured gray 400 color.
*/

input::-moz-placeholder, textarea::-moz-placeholder {
  opacity: 1; /* 1 */
  color: #9ca3af; /* 2 */
}

input::placeholder,
textarea::placeholder {
  opacity: 1; /* 1 */
  color: #9ca3af; /* 2 */
}

/*
Set the default cursor for buttons.
*/

button,
[role="button"] {
  cursor: pointer;
}

/*
Make sure disabled buttons don't get the pointer cursor.
*/
:disabled {
  cursor: default;
}

/*
1. Make replaced elements \`display: block\` by default. (https://github.com/mozdevs/cssremedy/issues/14)
2. Add \`vertical-align: middle\` to align replaced elements more sensibly by default. (https://github.com/jensimmons/cssremedy/issues/14#issuecomment-634934210)
   This can trigger a poorly considered lint error in some tools but is included by design.
*/

img,
svg,
video,
canvas,
audio,
iframe,
embed,
object {
  display: block; /* 1 */
  vertical-align: middle; /* 2 */
}

/*
Constrain images and videos to the parent width and preserve their intrinsic aspect ratio. (https://github.com/mozdevs/cssremedy/issues/14)
*/

img,
video {
  max-width: 100%;
  height: auto;
}

/* Make elements with the HTML hidden attribute stay hidden by default */
[hidden]:where(:not([hidden="until-found"])) {
  display: none;
}
.container {
  width: 100%;
}
@media (min-width: 640px) {

  .container {
    max-width: 640px;
  }
}
@media (min-width: 768px) {

  .container {
    max-width: 768px;
  }
}
@media (min-width: 1024px) {

  .container {
    max-width: 1024px;
  }
}
@media (min-width: 1280px) {

  .container {
    max-width: 1280px;
  }
}
@media (min-width: 1536px) {

  .container {
    max-width: 1536px;
  }
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
.pointer-events-none {
  pointer-events: none;
}
.visible {
  visibility: visible;
}
.collapse {
  visibility: collapse;
}
.static {
  position: static;
}
.fixed {
  position: fixed;
}
.absolute {
  position: absolute;
}
.relative {
  position: relative;
}
.inset-0 {
  inset: 0px;
}
.-right-2 {
  right: -0.5rem;
}
.-top-2 {
  top: -0.5rem;
}
.bottom-0 {
  bottom: 0px;
}
.bottom-4 {
  bottom: 1rem;
}
.left-0 {
  left: 0px;
}
.left-1\\/2 {
  left: 50%;
}
.left-2 {
  left: 0.5rem;
}
.left-3 {
  left: 0.75rem;
}
.left-\\[50\\%\\] {
  left: 50%;
}
.right-0 {
  right: 0px;
}
.right-1 {
  right: 0.25rem;
}
.right-2 {
  right: 0.5rem;
}
.right-4 {
  right: 1rem;
}
.top-0 {
  top: 0px;
}
.top-1\\/2 {
  top: 50%;
}
.top-2 {
  top: 0.5rem;
}
.top-2\\.5 {
  top: 0.625rem;
}
.top-4 {
  top: 1rem;
}
.top-\\[50\\%\\] {
  top: 50%;
}
.z-10 {
  z-index: 10;
}
.z-50 {
  z-index: 50;
}
.z-\\[9999\\] {
  z-index: 9999;
}
.col-span-1 {
  grid-column: span 1 / span 1;
}
.col-start-2 {
  grid-column-start: 2;
}
.row-span-2 {
  grid-row: span 2 / span 2;
}
.row-start-1 {
  grid-row-start: 1;
}
.m-3 {
  margin: 0.75rem;
}
.-mx-1 {
  margin-left: -0.25rem;
  margin-right: -0.25rem;
}
.-mx-2 {
  margin-left: -0.5rem;
  margin-right: -0.5rem;
}
.mx-4 {
  margin-left: 1rem;
  margin-right: 1rem;
}
.mx-auto {
  margin-left: auto;
  margin-right: auto;
}
.my-0\\.5 {
  margin-top: 0.125rem;
  margin-bottom: 0.125rem;
}
.my-1 {
  margin-top: 0.25rem;
  margin-bottom: 0.25rem;
}
.my-2 {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
.my-3 {
  margin-top: 0.75rem;
  margin-bottom: 0.75rem;
}
.my-4 {
  margin-top: 1rem;
  margin-bottom: 1rem;
}
.-mb-px {
  margin-bottom: -1px;
}
.mb-1 {
  margin-bottom: 0.25rem;
}
.mb-1\\.5 {
  margin-bottom: 0.375rem;
}
.mb-2 {
  margin-bottom: 0.5rem;
}
.mb-3 {
  margin-bottom: 0.75rem;
}
.mb-4 {
  margin-bottom: 1rem;
}
.mb-8 {
  margin-bottom: 2rem;
}
.ml-1 {
  margin-left: 0.25rem;
}
.ml-2 {
  margin-left: 0.5rem;
}
.ml-3 {
  margin-left: 0.75rem;
}
.ml-6 {
  margin-left: 1.5rem;
}
.ml-auto {
  margin-left: auto;
}
.mr-1 {
  margin-right: 0.25rem;
}
.mr-1\\.5 {
  margin-right: 0.375rem;
}
.mr-2 {
  margin-right: 0.5rem;
}
.mr-3 {
  margin-right: 0.75rem;
}
.mr-4 {
  margin-right: 1rem;
}
.mr-6 {
  margin-right: 1.5rem;
}
.mt-0\\.5 {
  margin-top: 0.125rem;
}
.mt-1 {
  margin-top: 0.25rem;
}
.mt-1\\.5 {
  margin-top: 0.375rem;
}
.mt-2 {
  margin-top: 0.5rem;
}
.mt-3 {
  margin-top: 0.75rem;
}
.mt-4 {
  margin-top: 1rem;
}
.block {
  display: block;
}
.inline-block {
  display: inline-block;
}
.inline {
  display: inline;
}
.flex {
  display: flex;
}
.inline-flex {
  display: inline-flex;
}
.table {
  display: table;
}
.grid {
  display: grid;
}
.hidden {
  display: none;
}
.aspect-square {
  aspect-ratio: 1 / 1;
}
.size-10 {
  width: 2.5rem;
  height: 2.5rem;
}
.size-2 {
  width: 0.5rem;
  height: 0.5rem;
}
.size-3 {
  width: 0.75rem;
  height: 0.75rem;
}
.size-3\\.5 {
  width: 0.875rem;
  height: 0.875rem;
}
.size-4 {
  width: 1rem;
  height: 1rem;
}
.size-5 {
  width: 1.25rem;
  height: 1.25rem;
}
.size-6 {
  width: 1.5rem;
  height: 1.5rem;
}
.size-8 {
  width: 2rem;
  height: 2rem;
}
.size-9 {
  width: 2.25rem;
  height: 2.25rem;
}
.size-full {
  width: 100%;
  height: 100%;
}
.h-1 {
  height: 0.25rem;
}
.h-1\\.5 {
  height: 0.375rem;
}
.h-10 {
  height: 2.5rem;
}
.h-12 {
  height: 3rem;
}
.h-2 {
  height: 0.5rem;
}
.h-2\\.5 {
  height: 0.625rem;
}
.h-3 {
  height: 0.75rem;
}
.h-3\\.5 {
  height: 0.875rem;
}
.h-4 {
  height: 1rem;
}
.h-5 {
  height: 1.25rem;
}
.h-6 {
  height: 1.5rem;
}
.h-7 {
  height: 1.75rem;
}
.h-8 {
  height: 2rem;
}
.h-9 {
  height: 2.25rem;
}
.h-\\[600px\\] {
  height: 600px;
}
.h-\\[var\\(--radix-select-trigger-height\\)\\] {
  height: var(--radix-select-trigger-height);
}
.h-auto {
  height: auto;
}
.h-full {
  height: 100%;
}
.h-px {
  height: 1px;
}
.h-screen {
  height: 100vh;
}
.max-h-32 {
  max-height: 8rem;
}
.max-h-48 {
  max-height: 12rem;
}
.max-h-96 {
  max-height: 24rem;
}
.max-h-\\[300px\\] {
  max-height: 300px;
}
.max-h-\\[500px\\] {
  max-height: 500px;
}
.max-h-\\[90vh\\] {
  max-height: 90vh;
}
.min-h-0 {
  min-height: 0px;
}
.min-h-16 {
  min-height: 4rem;
}
.min-h-\\[200px\\] {
  min-height: 200px;
}
.min-h-\\[36px\\] {
  min-height: 36px;
}
.min-h-\\[400px\\] {
  min-height: 400px;
}
.w-1\\.5 {
  width: 0.375rem;
}
.w-12 {
  width: 3rem;
}
.w-2 {
  width: 0.5rem;
}
.w-2\\.5 {
  width: 0.625rem;
}
.w-28 {
  width: 7rem;
}
.w-3 {
  width: 0.75rem;
}
.w-3\\.5 {
  width: 0.875rem;
}
.w-4 {
  width: 1rem;
}
.w-40 {
  width: 10rem;
}
.w-5 {
  width: 1.25rem;
}
.w-6 {
  width: 1.5rem;
}
.w-64 {
  width: 16rem;
}
.w-72 {
  width: 18rem;
}
.w-8 {
  width: 2rem;
}
.w-80 {
  width: 20rem;
}
.w-9 {
  width: 2.25rem;
}
.w-auto {
  width: auto;
}
.w-fit {
  width: -moz-fit-content;
  width: fit-content;
}
.w-full {
  width: 100%;
}
.min-w-0 {
  min-width: 0px;
}
.min-w-\\[100px\\] {
  min-width: 100px;
}
.min-w-\\[18px\\] {
  min-width: 18px;
}
.min-w-\\[8rem\\] {
  min-width: 8rem;
}
.min-w-\\[var\\(--radix-select-trigger-width\\)\\] {
  min-width: var(--radix-select-trigger-width);
}
.min-w-full {
  min-width: 100%;
}
.max-w-\\[200px\\] {
  max-width: 200px;
}
.max-w-\\[calc\\(100\\%-2rem\\)\\] {
  max-width: calc(100% - 2rem);
}
.max-w-none {
  max-width: none;
}
.max-w-xs {
  max-width: 20rem;
}
.flex-1 {
  flex: 1 1 0%;
}
.flex-shrink-0 {
  flex-shrink: 0;
}
.shrink {
  flex-shrink: 1;
}
.shrink-0 {
  flex-shrink: 0;
}
.caption-bottom {
  caption-side: bottom;
}
.border-collapse {
  border-collapse: collapse;
}
.-translate-x-1\\/2 {
  --tw-translate-x: -50%;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
.-translate-y-1\\/2 {
  --tw-translate-y: -50%;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
.translate-x-\\[-50\\%\\] {
  --tw-translate-x: -50%;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
.translate-y-\\[-50\\%\\] {
  --tw-translate-y: -50%;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
.rotate-180 {
  --tw-rotate: 180deg;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
.scale-110 {
  --tw-scale-x: 1.1;
  --tw-scale-y: 1.1;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
.scale-95 {
  --tw-scale-x: .95;
  --tw-scale-y: .95;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
.transform {
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}
@keyframes pulse {

  50% {
    opacity: .5;
  }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes spin {

  to {
    transform: rotate(360deg);
  }
}
.animate-spin {
  animation: spin 1s linear infinite;
}
.cursor-default {
  cursor: default;
}
.cursor-not-allowed {
  cursor: not-allowed;
}
.cursor-pointer {
  cursor: pointer;
}
.touch-none {
  touch-action: none;
}
.select-none {
  -webkit-user-select: none;
     -moz-user-select: none;
          user-select: none;
}
.resize-none {
  resize: none;
}
.resize {
  resize: both;
}
.scroll-my-1 {
  scroll-margin-top: 0.25rem;
  scroll-margin-bottom: 0.25rem;
}
.scroll-py-1 {
  scroll-padding-top: 0.25rem;
  scroll-padding-bottom: 0.25rem;
}
.list-decimal {
  list-style-type: decimal;
}
.list-disc {
  list-style-type: disc;
}
.auto-rows-min {
  grid-auto-rows: min-content;
}
.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}
.grid-cols-12 {
  grid-template-columns: repeat(12, minmax(0, 1fr));
}
.grid-rows-\\[auto_auto\\] {
  grid-template-rows: auto auto;
}
.flex-col {
  flex-direction: column;
}
.flex-col-reverse {
  flex-direction: column-reverse;
}
.flex-wrap {
  flex-wrap: wrap;
}
.items-start {
  align-items: flex-start;
}
.items-end {
  align-items: flex-end;
}
.items-center {
  align-items: center;
}
.justify-end {
  justify-content: flex-end;
}
.justify-center {
  justify-content: center;
}
.justify-between {
  justify-content: space-between;
}
.gap-0\\.5 {
  gap: 0.125rem;
}
.gap-1 {
  gap: 0.25rem;
}
.gap-1\\.5 {
  gap: 0.375rem;
}
.gap-2 {
  gap: 0.5rem;
}
.gap-3 {
  gap: 0.75rem;
}
.gap-4 {
  gap: 1rem;
}
.gap-6 {
  gap: 1.5rem;
}
.space-x-1 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-x-reverse: 0;
  margin-right: calc(0.25rem * var(--tw-space-x-reverse));
  margin-left: calc(0.25rem * calc(1 - var(--tw-space-x-reverse)));
}
.space-x-2 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-x-reverse: 0;
  margin-right: calc(0.5rem * var(--tw-space-x-reverse));
  margin-left: calc(0.5rem * calc(1 - var(--tw-space-x-reverse)));
}
.space-x-3 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-x-reverse: 0;
  margin-right: calc(0.75rem * var(--tw-space-x-reverse));
  margin-left: calc(0.75rem * calc(1 - var(--tw-space-x-reverse)));
}
.space-x-4 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-x-reverse: 0;
  margin-right: calc(1rem * var(--tw-space-x-reverse));
  margin-left: calc(1rem * calc(1 - var(--tw-space-x-reverse)));
}
.space-y-0\\.5 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.125rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.125rem * var(--tw-space-y-reverse));
}
.space-y-1 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.25rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.25rem * var(--tw-space-y-reverse));
}
.space-y-1\\.5 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.375rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.375rem * var(--tw-space-y-reverse));
}
.space-y-2 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.5rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.5rem * var(--tw-space-y-reverse));
}
.space-y-3 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(0.75rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(0.75rem * var(--tw-space-y-reverse));
}
.space-y-4 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(1rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(1rem * var(--tw-space-y-reverse));
}
.space-y-6 > :not([hidden]) ~ :not([hidden]) {
  --tw-space-y-reverse: 0;
  margin-top: calc(1.5rem * calc(1 - var(--tw-space-y-reverse)));
  margin-bottom: calc(1.5rem * var(--tw-space-y-reverse));
}
.divide-y > :not([hidden]) ~ :not([hidden]) {
  --tw-divide-y-reverse: 0;
  border-top-width: calc(1px * calc(1 - var(--tw-divide-y-reverse)));
  border-bottom-width: calc(1px * var(--tw-divide-y-reverse));
}
.divide-gray-200 > :not([hidden]) ~ :not([hidden]) {
  --tw-divide-opacity: 1;
  border-color: rgb(229 231 235 / var(--tw-divide-opacity, 1));
}
.self-start {
  align-self: flex-start;
}
.justify-self-end {
  justify-self: end;
}
.overflow-auto {
  overflow: auto;
}
.overflow-hidden {
  overflow: hidden;
}
.overflow-x-auto {
  overflow-x: auto;
}
.overflow-y-auto {
  overflow-y: auto;
}
.overflow-x-hidden {
  overflow-x: hidden;
}
.truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.whitespace-nowrap {
  white-space: nowrap;
}
.whitespace-pre-wrap {
  white-space: pre-wrap;
}
.text-balance {
  text-wrap: balance;
}
.break-words {
  overflow-wrap: break-word;
}
.break-all {
  word-break: break-all;
}
.rounded {
  border-radius: 0.25rem;
}
.rounded-\\[4px\\] {
  border-radius: 4px;
}
.rounded-\\[inherit\\] {
  border-radius: inherit;
}
.rounded-full {
  border-radius: 9999px;
}
.rounded-lg {
  border-radius: 0.5rem;
}
.rounded-md {
  border-radius: 0.375rem;
}
.rounded-sm {
  border-radius: 0.125rem;
}
.rounded-xl {
  border-radius: 0.75rem;
}
.rounded-b-xl {
  border-bottom-right-radius: 0.75rem;
  border-bottom-left-radius: 0.75rem;
}
.rounded-t-xl {
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
}
.border {
  border-width: 1px;
}
.border-0 {
  border-width: 0px;
}
.border-2 {
  border-width: 2px;
}
.border-b {
  border-bottom-width: 1px;
}
.border-b-2 {
  border-bottom-width: 2px;
}
.border-l {
  border-left-width: 1px;
}
.border-r {
  border-right-width: 1px;
}
.border-t {
  border-top-width: 1px;
}
.border-none {
  border-style: none;
}
.border-\\[var\\(--color-brand-blue-200\\)\\] {
  border-color: var(--color-brand-blue-200);
}
.border-\\[var\\(--color-brand-blue-300\\)\\] {
  border-color: var(--color-brand-blue-300);
}
.border-\\[var\\(--color-status-green-200\\)\\] {
  border-color: var(--color-status-green-200);
}
.border-\\[var\\(--color-status-red-200\\)\\] {
  border-color: var(--color-status-red-200);
}
.border-\\[var\\(--color-status-yellow-200\\)\\] {
  border-color: var(--color-status-yellow-200);
}
.border-\\[var\\(--color-warm-gray-100\\)\\] {
  border-color: var(--color-warm-gray-100);
}
.border-\\[var\\(--color-warm-gray-200\\)\\] {
  border-color: var(--color-warm-gray-200);
}
.border-\\[var\\(--color-warm-gray-300\\)\\] {
  border-color: var(--color-warm-gray-300);
}
.border-amber-200 {
  --tw-border-opacity: 1;
  border-color: rgb(253 230 138 / var(--tw-border-opacity, 1));
}
.border-amber-600 {
  --tw-border-opacity: 1;
  border-color: rgb(217 119 6 / var(--tw-border-opacity, 1));
}
.border-blue-200 {
  --tw-border-opacity: 1;
  border-color: rgb(191 219 254 / var(--tw-border-opacity, 1));
}
.border-blue-300 {
  --tw-border-opacity: 1;
  border-color: rgb(147 197 253 / var(--tw-border-opacity, 1));
}
.border-blue-500 {
  --tw-border-opacity: 1;
  border-color: rgb(59 130 246 / var(--tw-border-opacity, 1));
}
.border-blue-600 {
  --tw-border-opacity: 1;
  border-color: rgb(37 99 235 / var(--tw-border-opacity, 1));
}
.border-border {
  border-color: var(--border);
}
.border-emerald-200 {
  --tw-border-opacity: 1;
  border-color: rgb(167 243 208 / var(--tw-border-opacity, 1));
}
.border-gray-100 {
  --tw-border-opacity: 1;
  border-color: rgb(243 244 246 / var(--tw-border-opacity, 1));
}
.border-gray-200 {
  --tw-border-opacity: 1;
  border-color: rgb(229 231 235 / var(--tw-border-opacity, 1));
}
.border-gray-300 {
  --tw-border-opacity: 1;
  border-color: rgb(209 213 219 / var(--tw-border-opacity, 1));
}
.border-gray-800 {
  --tw-border-opacity: 1;
  border-color: rgb(31 41 55 / var(--tw-border-opacity, 1));
}
.border-green-200 {
  --tw-border-opacity: 1;
  border-color: rgb(187 247 208 / var(--tw-border-opacity, 1));
}
.border-indigo-100 {
  --tw-border-opacity: 1;
  border-color: rgb(224 231 255 / var(--tw-border-opacity, 1));
}
.border-indigo-200 {
  --tw-border-opacity: 1;
  border-color: rgb(199 210 254 / var(--tw-border-opacity, 1));
}
.border-indigo-500 {
  --tw-border-opacity: 1;
  border-color: rgb(99 102 241 / var(--tw-border-opacity, 1));
}
.border-indigo-600 {
  --tw-border-opacity: 1;
  border-color: rgb(79 70 229 / var(--tw-border-opacity, 1));
}
.border-orange-200 {
  --tw-border-opacity: 1;
  border-color: rgb(254 215 170 / var(--tw-border-opacity, 1));
}
.border-purple-100 {
  --tw-border-opacity: 1;
  border-color: rgb(243 232 255 / var(--tw-border-opacity, 1));
}
.border-purple-200 {
  --tw-border-opacity: 1;
  border-color: rgb(233 213 255 / var(--tw-border-opacity, 1));
}
.border-red-200 {
  --tw-border-opacity: 1;
  border-color: rgb(254 202 202 / var(--tw-border-opacity, 1));
}
.border-red-500 {
  --tw-border-opacity: 1;
  border-color: rgb(239 68 68 / var(--tw-border-opacity, 1));
}
.border-teal-200 {
  --tw-border-opacity: 1;
  border-color: rgb(153 246 228 / var(--tw-border-opacity, 1));
}
.border-transparent {
  border-color: transparent;
}
.border-yellow-300 {
  --tw-border-opacity: 1;
  border-color: rgb(253 224 71 / var(--tw-border-opacity, 1));
}
.border-b-transparent {
  border-bottom-color: transparent;
}
.border-l-transparent {
  border-left-color: transparent;
}
.border-t-transparent {
  border-top-color: transparent;
}
.bg-\\[var\\(--color-brand-blue-500\\)\\] {
  background-color: var(--color-brand-blue-500);
}
.bg-\\[var\\(--color-status-green-100\\)\\] {
  background-color: var(--color-status-green-100);
}
.bg-\\[var\\(--color-status-red-100\\)\\] {
  background-color: var(--color-status-red-100);
}
.bg-\\[var\\(--color-status-yellow-100\\)\\] {
  background-color: var(--color-status-yellow-100);
}
.bg-\\[var\\(--color-status-yellow-200\\)\\] {
  background-color: var(--color-status-yellow-200);
}
.bg-\\[var\\(--color-status-yellow-50\\)\\] {
  background-color: var(--color-status-yellow-50);
}
.bg-\\[var\\(--color-warm-gray-100\\)\\] {
  background-color: var(--color-warm-gray-100);
}
.bg-\\[var\\(--color-warm-gray-50\\)\\] {
  background-color: var(--color-warm-gray-50);
}
.bg-amber-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(254 243 199 / var(--tw-bg-opacity, 1));
}
.bg-amber-100\\/50 {
  background-color: rgb(254 243 199 / 0.5);
}
.bg-amber-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(255 251 235 / var(--tw-bg-opacity, 1));
}
.bg-amber-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(245 158 11 / var(--tw-bg-opacity, 1));
}
.bg-background {
  background-color: var(--background);
}
.bg-black {
  --tw-bg-opacity: 1;
  background-color: rgb(0 0 0 / var(--tw-bg-opacity, 1));
}
.bg-black\\/50 {
  background-color: rgb(0 0 0 / 0.5);
}
.bg-black\\/70 {
  background-color: rgb(0 0 0 / 0.7);
}
.bg-blue-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(219 234 254 / var(--tw-bg-opacity, 1));
}
.bg-blue-400 {
  --tw-bg-opacity: 1;
  background-color: rgb(96 165 250 / var(--tw-bg-opacity, 1));
}
.bg-blue-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(239 246 255 / var(--tw-bg-opacity, 1));
}
.bg-blue-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(59 130 246 / var(--tw-bg-opacity, 1));
}
.bg-blue-600 {
  --tw-bg-opacity: 1;
  background-color: rgb(37 99 235 / var(--tw-bg-opacity, 1));
}
.bg-card {
  background-color: var(--card);
}
.bg-destructive {
  background-color: var(--destructive);
}
.bg-emerald-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(209 250 229 / var(--tw-bg-opacity, 1));
}
.bg-emerald-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(16 185 129 / var(--tw-bg-opacity, 1));
}
.bg-gray-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(243 244 246 / var(--tw-bg-opacity, 1));
}
.bg-gray-200 {
  --tw-bg-opacity: 1;
  background-color: rgb(229 231 235 / var(--tw-bg-opacity, 1));
}
.bg-gray-400 {
  --tw-bg-opacity: 1;
  background-color: rgb(156 163 175 / var(--tw-bg-opacity, 1));
}
.bg-gray-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(249 250 251 / var(--tw-bg-opacity, 1));
}
.bg-gray-900 {
  --tw-bg-opacity: 1;
  background-color: rgb(17 24 39 / var(--tw-bg-opacity, 1));
}
.bg-green-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(220 252 231 / var(--tw-bg-opacity, 1));
}
.bg-green-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(240 253 244 / var(--tw-bg-opacity, 1));
}
.bg-green-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(34 197 94 / var(--tw-bg-opacity, 1));
}
.bg-indigo-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(224 231 255 / var(--tw-bg-opacity, 1));
}
.bg-muted {
  background-color: var(--muted);
}
.bg-orange-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(255 237 213 / var(--tw-bg-opacity, 1));
}
.bg-primary {
  background-color: var(--primary);
}
.bg-purple-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(243 232 255 / var(--tw-bg-opacity, 1));
}
.bg-purple-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(250 245 255 / var(--tw-bg-opacity, 1));
}
.bg-purple-600 {
  --tw-bg-opacity: 1;
  background-color: rgb(147 51 234 / var(--tw-bg-opacity, 1));
}
.bg-red-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(254 226 226 / var(--tw-bg-opacity, 1));
}
.bg-red-50 {
  --tw-bg-opacity: 1;
  background-color: rgb(254 242 242 / var(--tw-bg-opacity, 1));
}
.bg-red-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(239 68 68 / var(--tw-bg-opacity, 1));
}
.bg-red-600 {
  --tw-bg-opacity: 1;
  background-color: rgb(220 38 38 / var(--tw-bg-opacity, 1));
}
.bg-transparent {
  background-color: transparent;
}
.bg-white {
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
}
.bg-white\\/50 {
  background-color: rgb(255 255 255 / 0.5);
}
.bg-yellow-100 {
  --tw-bg-opacity: 1;
  background-color: rgb(254 249 195 / var(--tw-bg-opacity, 1));
}
.bg-yellow-500 {
  --tw-bg-opacity: 1;
  background-color: rgb(234 179 8 / var(--tw-bg-opacity, 1));
}
.bg-opacity-50 {
  --tw-bg-opacity: 0.5;
}
.bg-gradient-to-r {
  background-image: linear-gradient(to right, var(--tw-gradient-stops));
}
.from-gray-50 {
  --tw-gradient-from: #f9fafb var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(249 250 251 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}
.from-indigo-50 {
  --tw-gradient-from: #eef2ff var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(238 242 255 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}
.from-yellow-100 {
  --tw-gradient-from: #fef9c3 var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(254 249 195 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}
.from-yellow-400 {
  --tw-gradient-from: #facc15 var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(250 204 21 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}
.from-yellow-500 {
  --tw-gradient-from: #eab308 var(--tw-gradient-from-position);
  --tw-gradient-to: rgb(234 179 8 / 0) var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), var(--tw-gradient-to);
}
.via-yellow-500 {
  --tw-gradient-to: rgb(234 179 8 / 0)  var(--tw-gradient-to-position);
  --tw-gradient-stops: var(--tw-gradient-from), #eab308 var(--tw-gradient-via-position), var(--tw-gradient-to);
}
.to-amber-100 {
  --tw-gradient-to: #fef3c7 var(--tw-gradient-to-position);
}
.to-amber-500 {
  --tw-gradient-to: #f59e0b var(--tw-gradient-to-position);
}
.to-gray-100 {
  --tw-gradient-to: #f3f4f6 var(--tw-gradient-to-position);
}
.to-purple-50 {
  --tw-gradient-to: #faf5ff var(--tw-gradient-to-position);
}
.bg-cover {
  background-size: cover;
}
.bg-center {
  background-position: center;
}
.bg-no-repeat {
  background-repeat: no-repeat;
}
.fill-black\\/70 {
  fill: rgb(0 0 0 / 0.7);
}
.fill-current {
  fill: currentColor;
}
.object-contain {
  -o-object-fit: contain;
     object-fit: contain;
}
.p-0 {
  padding: 0px;
}
.p-0\\.5 {
  padding: 0.125rem;
}
.p-1 {
  padding: 0.25rem;
}
.p-1\\.5 {
  padding: 0.375rem;
}
.p-2 {
  padding: 0.5rem;
}
.p-3 {
  padding: 0.75rem;
}
.p-4 {
  padding: 1rem;
}
.p-6 {
  padding: 1.5rem;
}
.p-8 {
  padding: 2rem;
}
.p-px {
  padding: 1px;
}
.px-1 {
  padding-left: 0.25rem;
  padding-right: 0.25rem;
}
.px-1\\.5 {
  padding-left: 0.375rem;
  padding-right: 0.375rem;
}
.px-2 {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}
.px-2\\.5 {
  padding-left: 0.625rem;
  padding-right: 0.625rem;
}
.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}
.px-4 {
  padding-left: 1rem;
  padding-right: 1rem;
}
.px-6 {
  padding-left: 1.5rem;
  padding-right: 1.5rem;
}
.py-0\\.5 {
  padding-top: 0.125rem;
  padding-bottom: 0.125rem;
}
.py-1 {
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}
.py-1\\.5 {
  padding-top: 0.375rem;
  padding-bottom: 0.375rem;
}
.py-12 {
  padding-top: 3rem;
  padding-bottom: 3rem;
}
.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}
.py-3 {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}
.py-4 {
  padding-top: 1rem;
  padding-bottom: 1rem;
}
.py-6 {
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
}
.py-8 {
  padding-top: 2rem;
  padding-bottom: 2rem;
}
.py-px {
  padding-top: 1px;
  padding-bottom: 1px;
}
.pb-1 {
  padding-bottom: 0.25rem;
}
.pb-2 {
  padding-bottom: 0.5rem;
}
.pb-3 {
  padding-bottom: 0.75rem;
}
.pb-4 {
  padding-bottom: 1rem;
}
.pb-6 {
  padding-bottom: 1.5rem;
}
.pl-0 {
  padding-left: 0px;
}
.pl-10 {
  padding-left: 2.5rem;
}
.pl-2 {
  padding-left: 0.5rem;
}
.pl-5 {
  padding-left: 1.25rem;
}
.pl-7 {
  padding-left: 1.75rem;
}
.pl-8 {
  padding-left: 2rem;
}
.pr-2 {
  padding-right: 0.5rem;
}
.pr-4 {
  padding-right: 1rem;
}
.pr-7 {
  padding-right: 1.75rem;
}
.pr-8 {
  padding-right: 2rem;
}
.pt-0 {
  padding-top: 0px;
}
.pt-1 {
  padding-top: 0.25rem;
}
.pt-2 {
  padding-top: 0.5rem;
}
.pt-3 {
  padding-top: 0.75rem;
}
.pt-4 {
  padding-top: 1rem;
}
.pt-6 {
  padding-top: 1.5rem;
}
.text-left {
  text-align: left;
}
.text-center {
  text-align: center;
}
.text-right {
  text-align: right;
}
.align-top {
  vertical-align: top;
}
.align-middle {
  vertical-align: middle;
}
.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}
.text-3xl {
  font-size: 1.875rem;
  line-height: 2.25rem;
}
.text-\\[10px\\] {
  font-size: 10px;
}
.text-\\[15px\\] {
  font-size: 15px;
}
.text-base {
  font-size: 1rem;
  line-height: 1.5rem;
}
.text-lg {
  font-size: 1.125rem;
  line-height: 1.75rem;
}
.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}
.text-xl {
  font-size: 1.25rem;
  line-height: 1.75rem;
}
.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}
.font-bold {
  font-weight: 700;
}
.font-medium {
  font-weight: 500;
}
.font-normal {
  font-weight: 400;
}
.font-semibold {
  font-weight: 600;
}
.uppercase {
  text-transform: uppercase;
}
.italic {
  font-style: italic;
}
.leading-none {
  line-height: 1;
}
.leading-relaxed {
  line-height: 1.625;
}
.leading-tight {
  line-height: 1.25;
}
.tracking-tight {
  letter-spacing: -0.025em;
}
.tracking-wide {
  letter-spacing: 0.025em;
}
.tracking-wider {
  letter-spacing: 0.05em;
}
.tracking-widest {
  letter-spacing: 0.1em;
}
.text-\\[var\\(--color-brand-blue-500\\)\\] {
  color: var(--color-brand-blue-500);
}
.text-\\[var\\(--color-brand-blue-600\\)\\] {
  color: var(--color-brand-blue-600);
}
.text-\\[var\\(--color-brand-blue-700\\)\\] {
  color: var(--color-brand-blue-700);
}
.text-\\[var\\(--color-purple-accent\\)\\] {
  color: var(--color-purple-accent);
}
.text-\\[var\\(--color-status-green-500\\)\\] {
  color: var(--color-status-green-500);
}
.text-\\[var\\(--color-status-green-700\\)\\] {
  color: var(--color-status-green-700);
}
.text-\\[var\\(--color-status-red-700\\)\\] {
  color: var(--color-status-red-700);
}
.text-\\[var\\(--color-status-yellow-700\\)\\] {
  color: var(--color-status-yellow-700);
}
.text-\\[var\\(--color-steel-blue\\)\\] {
  color: var(--color-steel-blue);
}
.text-\\[var\\(--color-warm-gray-400\\)\\] {
  color: var(--color-warm-gray-400);
}
.text-\\[var\\(--color-warm-gray-500\\)\\] {
  color: var(--color-warm-gray-500);
}
.text-\\[var\\(--color-warm-gray-600\\)\\] {
  color: var(--color-warm-gray-600);
}
.text-\\[var\\(--color-warm-gray-700\\)\\] {
  color: var(--color-warm-gray-700);
}
.text-\\[var\\(--color-warm-gray-800\\)\\] {
  color: var(--color-warm-gray-800);
}
.text-\\[var\\(--color-warm-gray-900\\)\\] {
  color: var(--color-warm-gray-900);
}
.text-\\[var\\(--color-warning-amber\\)\\] {
  color: var(--color-warning-amber);
}
.text-amber-600 {
  --tw-text-opacity: 1;
  color: rgb(217 119 6 / var(--tw-text-opacity, 1));
}
.text-amber-800 {
  --tw-text-opacity: 1;
  color: rgb(146 64 14 / var(--tw-text-opacity, 1));
}
.text-black {
  --tw-text-opacity: 1;
  color: rgb(0 0 0 / var(--tw-text-opacity, 1));
}
.text-blue-500 {
  --tw-text-opacity: 1;
  color: rgb(59 130 246 / var(--tw-text-opacity, 1));
}
.text-blue-600 {
  --tw-text-opacity: 1;
  color: rgb(37 99 235 / var(--tw-text-opacity, 1));
}
.text-blue-700 {
  --tw-text-opacity: 1;
  color: rgb(29 78 216 / var(--tw-text-opacity, 1));
}
.text-blue-800 {
  --tw-text-opacity: 1;
  color: rgb(30 64 175 / var(--tw-text-opacity, 1));
}
.text-blue-900 {
  --tw-text-opacity: 1;
  color: rgb(30 58 138 / var(--tw-text-opacity, 1));
}
.text-current {
  color: currentColor;
}
.text-emerald-800 {
  --tw-text-opacity: 1;
  color: rgb(6 95 70 / var(--tw-text-opacity, 1));
}
.text-foreground {
  color: var(--foreground);
}
.text-gray-100 {
  --tw-text-opacity: 1;
  color: rgb(243 244 246 / var(--tw-text-opacity, 1));
}
.text-gray-300 {
  --tw-text-opacity: 1;
  color: rgb(209 213 219 / var(--tw-text-opacity, 1));
}
.text-gray-400 {
  --tw-text-opacity: 1;
  color: rgb(156 163 175 / var(--tw-text-opacity, 1));
}
.text-gray-500 {
  --tw-text-opacity: 1;
  color: rgb(107 114 128 / var(--tw-text-opacity, 1));
}
.text-gray-600 {
  --tw-text-opacity: 1;
  color: rgb(75 85 99 / var(--tw-text-opacity, 1));
}
.text-gray-700 {
  --tw-text-opacity: 1;
  color: rgb(55 65 81 / var(--tw-text-opacity, 1));
}
.text-gray-800 {
  --tw-text-opacity: 1;
  color: rgb(31 41 55 / var(--tw-text-opacity, 1));
}
.text-gray-900 {
  --tw-text-opacity: 1;
  color: rgb(17 24 39 / var(--tw-text-opacity, 1));
}
.text-green-600 {
  --tw-text-opacity: 1;
  color: rgb(22 163 74 / var(--tw-text-opacity, 1));
}
.text-green-800 {
  --tw-text-opacity: 1;
  color: rgb(22 101 52 / var(--tw-text-opacity, 1));
}
.text-green-900 {
  --tw-text-opacity: 1;
  color: rgb(20 83 45 / var(--tw-text-opacity, 1));
}
.text-indigo-600 {
  --tw-text-opacity: 1;
  color: rgb(79 70 229 / var(--tw-text-opacity, 1));
}
.text-indigo-700 {
  --tw-text-opacity: 1;
  color: rgb(67 56 202 / var(--tw-text-opacity, 1));
}
.text-indigo-800 {
  --tw-text-opacity: 1;
  color: rgb(55 48 163 / var(--tw-text-opacity, 1));
}
.text-muted-foreground {
  color: var(--muted-foreground);
}
.text-orange-500 {
  --tw-text-opacity: 1;
  color: rgb(249 115 22 / var(--tw-text-opacity, 1));
}
.text-orange-600 {
  --tw-text-opacity: 1;
  color: rgb(234 88 12 / var(--tw-text-opacity, 1));
}
.text-orange-800 {
  --tw-text-opacity: 1;
  color: rgb(154 52 18 / var(--tw-text-opacity, 1));
}
.text-primary-foreground {
  color: var(--primary-foreground);
}
.text-purple-500 {
  --tw-text-opacity: 1;
  color: rgb(168 85 247 / var(--tw-text-opacity, 1));
}
.text-purple-600 {
  --tw-text-opacity: 1;
  color: rgb(147 51 234 / var(--tw-text-opacity, 1));
}
.text-purple-700 {
  --tw-text-opacity: 1;
  color: rgb(126 34 206 / var(--tw-text-opacity, 1));
}
.text-purple-800 {
  --tw-text-opacity: 1;
  color: rgb(107 33 168 / var(--tw-text-opacity, 1));
}
.text-red-500 {
  --tw-text-opacity: 1;
  color: rgb(239 68 68 / var(--tw-text-opacity, 1));
}
.text-red-600 {
  --tw-text-opacity: 1;
  color: rgb(220 38 38 / var(--tw-text-opacity, 1));
}
.text-red-700 {
  --tw-text-opacity: 1;
  color: rgb(185 28 28 / var(--tw-text-opacity, 1));
}
.text-red-800 {
  --tw-text-opacity: 1;
  color: rgb(153 27 27 / var(--tw-text-opacity, 1));
}
.text-red-900 {
  --tw-text-opacity: 1;
  color: rgb(127 29 29 / var(--tw-text-opacity, 1));
}
.text-teal-600 {
  --tw-text-opacity: 1;
  color: rgb(13 148 136 / var(--tw-text-opacity, 1));
}
.text-teal-800 {
  --tw-text-opacity: 1;
  color: rgb(17 94 89 / var(--tw-text-opacity, 1));
}
.text-white {
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}
.text-yellow-800 {
  --tw-text-opacity: 1;
  color: rgb(133 77 14 / var(--tw-text-opacity, 1));
}
.underline {
  text-decoration-line: underline;
}
.underline-offset-4 {
  text-underline-offset: 4px;
}
.placeholder-\\[var\\(--color-warm-gray-400\\)\\]::-moz-placeholder {
  color: var(--color-warm-gray-400);
}
.placeholder-\\[var\\(--color-warm-gray-400\\)\\]::placeholder {
  color: var(--color-warm-gray-400);
}
.placeholder-\\[var\\(--color-warm-gray-500\\)\\]::-moz-placeholder {
  color: var(--color-warm-gray-500);
}
.placeholder-\\[var\\(--color-warm-gray-500\\)\\]::placeholder {
  color: var(--color-warm-gray-500);
}
.opacity-0 {
  opacity: 0;
}
.opacity-20 {
  opacity: 0.2;
}
.opacity-40 {
  opacity: 0.4;
}
.opacity-50 {
  opacity: 0.5;
}
.opacity-70 {
  opacity: 0.7;
}
.shadow-2xl {
  --tw-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25);
  --tw-shadow-colored: 0 25px 50px -12px var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
.shadow-lg {
  --tw-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --tw-shadow-colored: 0 10px 15px -3px var(--tw-shadow-color), 0 4px 6px -4px var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
.shadow-md {
  --tw-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --tw-shadow-colored: 0 4px 6px -1px var(--tw-shadow-color), 0 2px 4px -2px var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
.shadow-none {
  --tw-shadow: 0 0 #0000;
  --tw-shadow-colored: 0 0 #0000;
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
.shadow-sm {
  --tw-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --tw-shadow-colored: 0 1px 2px 0 var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}
.outline-none {
  outline: 2px solid transparent;
  outline-offset: 2px;
}
.outline {
  outline-style: solid;
}
.ring-0 {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(0px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}
.blur {
  --tw-blur: blur(8px);
  filter: var(--tw-blur) var(--tw-brightness) var(--tw-contrast) var(--tw-grayscale) var(--tw-hue-rotate) var(--tw-invert) var(--tw-saturate) var(--tw-sepia) var(--tw-drop-shadow);
}
.drop-shadow {
  --tw-drop-shadow: drop-shadow(0 1px 2px rgb(0 0 0 / 0.1)) drop-shadow(0 1px 1px rgb(0 0 0 / 0.06));
  filter: var(--tw-blur) var(--tw-brightness) var(--tw-contrast) var(--tw-grayscale) var(--tw-hue-rotate) var(--tw-invert) var(--tw-saturate) var(--tw-sepia) var(--tw-drop-shadow);
}
.filter {
  filter: var(--tw-blur) var(--tw-brightness) var(--tw-contrast) var(--tw-grayscale) var(--tw-hue-rotate) var(--tw-invert) var(--tw-saturate) var(--tw-sepia) var(--tw-drop-shadow);
}
.transition {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, filter, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.transition-\\[color\\2c box-shadow\\] {
  transition-property: color,box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.transition-none {
  transition-property: none;
}
.transition-opacity {
  transition-property: opacity;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.transition-transform {
  transition-property: transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.duration-150 {
  transition-duration: 150ms;
}
.duration-200 {
  transition-duration: 200ms;
}
.duration-300 {
  transition-duration: 300ms;
}
.duration-75 {
  transition-duration: 75ms;
}
.ease-out {
  transition-timing-function: cubic-bezier(0, 0, 0.2, 1);
}

@custom-variant dark (&:is(.dark *));

:root {
  --font-size: 14px;
  --font-family-unna: 'Victor Mono', monospace;
  --background: var(--color-warm-gray-50);
  --foreground: var(--color-warm-gray-700);
  --card: #ffffff;
  --card-foreground: var(--color-warm-gray-700);
  --popover: #ffffff;
  --popover-foreground: var(--color-warm-gray-700);
  --primary: var(--color-brand-blue-600);
  --primary-foreground: #ffffff;
  --secondary: var(--color-steel-blue);
  --secondary-foreground: #ffffff;
  --accent-subtle: var(--color-purple-accent);
  --accent-subtle-foreground: #ffffff;
  --muted: var(--color-warm-gray-100);
  --muted-foreground: var(--color-warm-gray-500);
  --accent: var(--color-warm-gray-100);
  --accent-foreground: var(--color-warm-gray-900);
  --destructive: var(--color-status-red-500);
  --destructive-foreground: #ffffff;
  --warning: var(--color-warning-amber);
  --warning-foreground: #ffffff;
  --border: var(--color-warm-gray-200);
  --input: transparent;
  --input-background: var(--color-warm-gray-100);
  --input-border: var(--color-warm-gray-300);
  --switch-background: var(--color-warm-gray-300);
  --font-weight-medium: 500;
  --font-weight-normal: 400;
  --ring: oklch(0.708 0 0);
  --chart-1: oklch(0.646 0.222 41.116);
  --chart-2: oklch(0.6 0.118 184.704);
  --chart-3: oklch(0.398 0.07 227.392);
  --chart-4: oklch(0.828 0.189 84.429);
  --chart-5: oklch(0.769 0.188 70.08);
  --radius: 0.375rem;
  --sidebar: oklch(0.985 0 0);
  --sidebar-foreground: oklch(0.145 0 0);
  --sidebar-primary: #030213;
  --sidebar-primary-foreground: oklch(0.985 0 0);
  --sidebar-accent: oklch(0.97 0 0);
  --sidebar-accent-foreground: oklch(0.205 0 0);
  --sidebar-border: oklch(0.922 0 0);
  --sidebar-ring: oklch(0.708 0 0);
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;
  --color-warm-gray-50: #f5f5f4;
  --color-warm-gray-100: #f0f0ef;
  --color-warm-gray-200: #e7e5e4;
  --color-warm-gray-300: #d6d3d1;
  --color-warm-gray-400: #a8a29e;
  --color-warm-gray-500: #78716c;
  --color-warm-gray-600: #57534e;
  --color-warm-gray-700: #44403c;
  --color-warm-gray-800: #292524;
  --color-warm-gray-900: #1c1917;
  --color-steel-blue: #475569;
  --color-steel-blue-light: #64748b;
  --color-steel-blue-dark: #334155;
  --color-blue-light-bg: #e0f2fe;
  --color-purple-accent: #6366f1;
  --color-purple-accent-light: #a5b4fc;
  --color-purple-accent-dark: #4338ca;
  --color-warning-amber: #f59e0b;
  --color-warning-amber-light: #fbbf24;
  --color-warning-amber-bg: #fffbeb;
  --color-brand-blue-50: #eff6ff;
  --color-brand-blue-100: #dbeafe;
  --color-brand-blue-200: #bfdbfe;
  --color-brand-blue-300: #93c5fd;
  --color-brand-blue-400: #60a5fa;
  --color-brand-blue-500: #3b82f6;
  --color-brand-blue-600: #2563eb;
  --color-brand-blue-700: #1d4ed8;
  --color-brand-blue-800: #1e40af;
  --color-brand-blue-900: #1e3a8a;
  --color-brand-blue-950: #172554;
  --color-aqua-50: #f0f9ff;
  --color-aqua-100: #e0f2fe;
  --color-aqua-200: #bae6fd;
  --color-aqua-300: #7dd3fc;
  --color-aqua-500: #0ea5e9;
  --color-aqua-600: #0284c7;
  --color-aqua-700: #0369a1;
  --color-brand-indigo-50: #eef2ff;
  --color-brand-indigo-100: #e0e7ff;
  --color-brand-indigo-400: #818cf8;
  --color-brand-indigo-600: #4338ca;
  --color-brand-cyan-50: #f0fdff;
  --color-brand-cyan-100: #e0f2fe;
  --color-brand-sky-400: #38bdf8;
  --color-brand-sky-500: #0ea5e9;
  --color-status-green-50: #f0fdf4;
  --color-status-green-100: #dcfce7;
  --color-status-green-200: #bbf7d0;
  --color-status-green-500: #22c55e;
  --color-status-green-600: #16a34a;
  --color-status-green-700: #15803d;
  --color-status-red-50: #fef2f2;
  --color-status-red-100: #fee2e2;
  --color-status-red-200: #fecaca;
  --color-status-red-500: #ef4444;
  --color-status-red-600: #dc2626;
  --color-status-red-700: #b91c1c;
  --color-status-yellow-50: #fefce8;
  --color-status-yellow-100: #fef3c7;
  --color-status-yellow-200: #fde68a;
  --color-status-yellow-500: #eab308;
  --color-status-yellow-600: #ca8a04;
  --color-status-yellow-700: #a16207;
  --brand-shadow-light: 0 12px 24px rgba(37, 99, 235, 0.08);
  --brand-shadow-medium: 0 16px 28px rgba(99, 102, 241, 0.18);
  --brand-shadow-heavy: 0 18px 40px rgba(15, 23, 42, 0.28);
  --brand-border-light: rgba(226, 232, 240, 0.8);
  --brand-border-medium: rgba(37, 99, 235, 0.35);
  --brand-border-strong: rgba(59, 130, 246, 0.35);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.145 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.145 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: var(--color-brand-blue-600);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: var(--color-status-red-500);
  --destructive-foreground: #ffffff;
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);
  --font-weight-medium: 500;
  --font-weight-normal: 400;
}

/* Base styles - matching web-app */
* {
  border-color: var(--border);
}

html {
  font-size: var(--font-size);
}

body {
  background-color: var(--background);
  color: var(--foreground);
  font-family: system-ui, -apple-system, sans-serif;
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

/* Typography hierarchy - matching web-app */
h1 {
  font-size: 1.5rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--foreground);
  margin: 0;
}

h2 {
  font-size: 1.25rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--foreground);
  margin: 0;
}

h3 {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.5;
  color: var(--foreground);
  margin: 0;
}

/* Markdown content styling (for marked HTML output) */
.markdown-content h1 { font-size: 1.125rem; font-weight: 700; margin-top: 0.75rem; margin-bottom: 0.5rem; color: #111827; }
.markdown-content h2 { font-size: 1rem; font-weight: 700; margin-top: 0.75rem; margin-bottom: 0.5rem; color: #111827; }
.markdown-content h3 { font-size: 0.875rem; font-weight: 700; margin-top: 0.5rem; margin-bottom: 0.25rem; color: #111827; }
.markdown-content p { margin-bottom: 0.5rem; }
.markdown-content p:last-child { margin-bottom: 0; }
.markdown-content code { background-color: #e5e7eb; color: #1f2937; padding: 0.125rem 0.25rem; border-radius: 0.25rem; font-size: 0.75rem; font-family: ui-monospace, monospace; }
.markdown-content pre { background-color: #1f2937; color: #f3f4f6; padding: 0.75rem; border-radius: 0.375rem; overflow-x: auto; margin: 0.5rem 0; font-size: 0.75rem; }
.markdown-content pre code { background-color: transparent; color: inherit; padding: 0; font-family: ui-monospace, monospace; }
.markdown-content ul { list-style-type: disc; list-style-position: inside; margin-bottom: 0.5rem; }
.markdown-content ol { list-style-type: decimal; list-style-position: inside; margin-bottom: 0.5rem; }
.markdown-content li { color: #374151; }
.markdown-content a { color: #4f46e5; text-decoration: underline; }
.markdown-content a:hover { color: #6366f1; }
.markdown-content strong { font-weight: 600; color: #111827; }
.markdown-content em { font-style: italic; }
.markdown-content blockquote { border-left: 4px solid #d1d5db; padding-left: 0.75rem; margin: 0.5rem 0; color: #4b5563; font-style: italic; }
.markdown-content table { min-width: 100%; border: 1px solid #d1d5db; font-size: 0.75rem; margin: 0.5rem 0; border-collapse: collapse; }
.markdown-content th { border: 1px solid #d1d5db; padding: 0.25rem 0.5rem; background-color: #f3f4f6; font-weight: 600; text-align: left; }
.markdown-content td { border: 1px solid #d1d5db; padding: 0.25rem 0.5rem; }
.markdown-content hr { margin: 0.75rem 0; border-color: #d1d5db; }

/* Remove manual icon initialization styles */

.selection\\:bg-primary *::-moz-selection {
  background-color: var(--primary);
}

.selection\\:bg-primary *::selection {
  background-color: var(--primary);
}

.selection\\:text-primary-foreground *::-moz-selection {
  color: var(--primary-foreground);
}

.selection\\:text-primary-foreground *::selection {
  color: var(--primary-foreground);
}

.selection\\:bg-primary::-moz-selection {
  background-color: var(--primary);
}

.selection\\:bg-primary::selection {
  background-color: var(--primary);
}

.selection\\:text-primary-foreground::-moz-selection {
  color: var(--primary-foreground);
}

.selection\\:text-primary-foreground::selection {
  color: var(--primary-foreground);
}

.file\\:inline-flex::file-selector-button {
  display: inline-flex;
}

.file\\:h-7::file-selector-button {
  height: 1.75rem;
}

.file\\:border-0::file-selector-button {
  border-width: 0px;
}

.file\\:bg-transparent::file-selector-button {
  background-color: transparent;
}

.file\\:text-sm::file-selector-button {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.file\\:font-medium::file-selector-button {
  font-weight: 500;
}

.file\\:text-foreground::file-selector-button {
  color: var(--foreground);
}

.placeholder\\:text-muted-foreground::-moz-placeholder {
  color: var(--muted-foreground);
}

.placeholder\\:text-muted-foreground::placeholder {
  color: var(--muted-foreground);
}

.hover\\:cursor-pointer:hover {
  cursor: pointer;
}

.hover\\:border-l-2:hover {
  border-left-width: 2px;
}

.hover\\:border-blue-300:hover {
  --tw-border-opacity: 1;
  border-color: rgb(147 197 253 / var(--tw-border-opacity, 1));
}

.hover\\:border-blue-400:hover {
  --tw-border-opacity: 1;
  border-color: rgb(96 165 250 / var(--tw-border-opacity, 1));
}

.hover\\:border-gray-300:hover {
  --tw-border-opacity: 1;
  border-color: rgb(209 213 219 / var(--tw-border-opacity, 1));
}

.hover\\:border-l-\\[var\\(--color-brand-blue-500\\)\\]:hover {
  border-left-color: var(--color-brand-blue-500);
}

.hover\\:bg-\\[var\\(--color-brand-blue-50\\)\\]:hover {
  background-color: var(--color-brand-blue-50);
}

.hover\\:bg-\\[var\\(--color-brand-blue-600\\)\\]:hover {
  background-color: var(--color-brand-blue-600);
}

.hover\\:bg-\\[var\\(--color-warm-gray-100\\)\\]:hover {
  background-color: var(--color-warm-gray-100);
}

.hover\\:bg-\\[var\\(--color-warm-gray-50\\)\\]:hover {
  background-color: var(--color-warm-gray-50);
}

.hover\\:bg-black:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(0 0 0 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-blue-100:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(219 234 254 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-blue-200:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(191 219 254 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-blue-50:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(239 246 255 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-blue-700:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(29 78 216 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-gray-100:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(243 244 246 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-gray-200:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(229 231 235 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-gray-300:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(209 213 219 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-gray-50:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(249 250 251 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-indigo-100\\/50:hover {
  background-color: rgb(224 231 255 / 0.5);
}

.hover\\:bg-indigo-200:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(199 210 254 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-purple-100:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(243 232 255 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-purple-700:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(126 34 206 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-white:hover {
  --tw-bg-opacity: 1;
  background-color: rgb(255 255 255 / var(--tw-bg-opacity, 1));
}

.hover\\:bg-opacity-20:hover {
  --tw-bg-opacity: 0.2;
}

.hover\\:text-\\[var\\(--color-brand-blue-700\\)\\]:hover {
  color: var(--color-brand-blue-700);
}

.hover\\:text-\\[var\\(--color-warm-gray-900\\)\\]:hover {
  color: var(--color-warm-gray-900);
}

.hover\\:text-blue-600:hover {
  --tw-text-opacity: 1;
  color: rgb(37 99 235 / var(--tw-text-opacity, 1));
}

.hover\\:text-blue-700:hover {
  --tw-text-opacity: 1;
  color: rgb(29 78 216 / var(--tw-text-opacity, 1));
}

.hover\\:text-blue-800:hover {
  --tw-text-opacity: 1;
  color: rgb(30 64 175 / var(--tw-text-opacity, 1));
}

.hover\\:text-foreground:hover {
  color: var(--foreground);
}

.hover\\:text-gray-200:hover {
  --tw-text-opacity: 1;
  color: rgb(229 231 235 / var(--tw-text-opacity, 1));
}

.hover\\:text-gray-700:hover {
  --tw-text-opacity: 1;
  color: rgb(55 65 81 / var(--tw-text-opacity, 1));
}

.hover\\:text-gray-800:hover {
  --tw-text-opacity: 1;
  color: rgb(31 41 55 / var(--tw-text-opacity, 1));
}

.hover\\:text-gray-900:hover {
  --tw-text-opacity: 1;
  color: rgb(17 24 39 / var(--tw-text-opacity, 1));
}

.hover\\:text-indigo-500:hover {
  --tw-text-opacity: 1;
  color: rgb(99 102 241 / var(--tw-text-opacity, 1));
}

.hover\\:text-purple-700:hover {
  --tw-text-opacity: 1;
  color: rgb(126 34 206 / var(--tw-text-opacity, 1));
}

.hover\\:text-red-700:hover {
  --tw-text-opacity: 1;
  color: rgb(185 28 28 / var(--tw-text-opacity, 1));
}

.hover\\:text-white:hover {
  --tw-text-opacity: 1;
  color: rgb(255 255 255 / var(--tw-text-opacity, 1));
}

.hover\\:underline:hover {
  text-decoration-line: underline;
}

.hover\\:opacity-100:hover {
  opacity: 1;
}

.hover\\:shadow-md:hover {
  --tw-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --tw-shadow-colored: 0 4px 6px -1px var(--tw-shadow-color), 0 2px 4px -2px var(--tw-shadow-color);
  box-shadow: var(--tw-ring-offset-shadow, 0 0 #0000), var(--tw-ring-shadow, 0 0 #0000), var(--tw-shadow);
}

.focus\\:border-blue-300:focus {
  --tw-border-opacity: 1;
  border-color: rgb(147 197 253 / var(--tw-border-opacity, 1));
}

.focus\\:border-blue-500:focus {
  --tw-border-opacity: 1;
  border-color: rgb(59 130 246 / var(--tw-border-opacity, 1));
}

.focus\\:border-indigo-500:focus {
  --tw-border-opacity: 1;
  border-color: rgb(99 102 241 / var(--tw-border-opacity, 1));
}

.focus\\:border-purple-500:focus {
  --tw-border-opacity: 1;
  border-color: rgb(168 85 247 / var(--tw-border-opacity, 1));
}

.focus\\:outline-none:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.focus\\:ring-1:focus {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(1px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

.focus\\:ring-2:focus {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

.focus\\:ring-blue-200:focus {
  --tw-ring-opacity: 1;
  --tw-ring-color: rgb(191 219 254 / var(--tw-ring-opacity, 1));
}

.focus\\:ring-blue-500:focus {
  --tw-ring-opacity: 1;
  --tw-ring-color: rgb(59 130 246 / var(--tw-ring-opacity, 1));
}

.focus\\:ring-indigo-500:focus {
  --tw-ring-opacity: 1;
  --tw-ring-color: rgb(99 102 241 / var(--tw-ring-opacity, 1));
}

.focus\\:ring-purple-500:focus {
  --tw-ring-opacity: 1;
  --tw-ring-color: rgb(168 85 247 / var(--tw-ring-opacity, 1));
}

.focus\\:ring-offset-2:focus {
  --tw-ring-offset-width: 2px;
}

.focus-visible\\:outline-none:focus-visible {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.focus-visible\\:outline-1:focus-visible {
  outline-width: 1px;
}

.focus-visible\\:ring-2:focus-visible {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

.focus-visible\\:ring-\\[3px\\]:focus-visible {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(3px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

.focus-visible\\:ring-offset-2:focus-visible {
  --tw-ring-offset-width: 2px;
}

.disabled\\:pointer-events-none:disabled {
  pointer-events: none;
}

.disabled\\:cursor-not-allowed:disabled {
  cursor: not-allowed;
}

.disabled\\:bg-gray-100:disabled {
  --tw-bg-opacity: 1;
  background-color: rgb(243 244 246 / var(--tw-bg-opacity, 1));
}

.disabled\\:text-gray-400:disabled {
  --tw-text-opacity: 1;
  color: rgb(156 163 175 / var(--tw-text-opacity, 1));
}

.disabled\\:opacity-50:disabled {
  opacity: 0.5;
}

.group:hover .group-hover\\:opacity-30 {
  opacity: 0.3;
}

.peer:disabled ~ .peer-disabled\\:cursor-not-allowed {
  cursor: not-allowed;
}

.peer:disabled ~ .peer-disabled\\:opacity-50 {
  opacity: 0.5;
}

.has-\\[\\>svg\\]\\:px-2\\.5:has(>svg) {
  padding-left: 0.625rem;
  padding-right: 0.625rem;
}

.has-\\[\\>svg\\]\\:px-3:has(>svg) {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.has-\\[\\>svg\\]\\:px-4:has(>svg) {
  padding-left: 1rem;
  padding-right: 1rem;
}

.data-\\[disabled\\=true\\]\\:pointer-events-none[data-disabled="true"] {
  pointer-events: none;
}

.data-\\[disabled\\]\\:pointer-events-none[data-disabled] {
  pointer-events: none;
}

.data-\\[orientation\\=horizontal\\]\\:h-px[data-orientation="horizontal"] {
  height: 1px;
}

.data-\\[orientation\\=vertical\\]\\:h-full[data-orientation="vertical"] {
  height: 100%;
}

.data-\\[size\\=default\\]\\:h-9[data-size="default"] {
  height: 2.25rem;
}

.data-\\[size\\=sm\\]\\:h-8[data-size="sm"] {
  height: 2rem;
}

.data-\\[orientation\\=horizontal\\]\\:w-full[data-orientation="horizontal"] {
  width: 100%;
}

.data-\\[orientation\\=vertical\\]\\:w-px[data-orientation="vertical"] {
  width: 1px;
}

.data-\\[side\\=bottom\\]\\:translate-y-1[data-side="bottom"] {
  --tw-translate-y: 0.25rem;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.data-\\[side\\=left\\]\\:-translate-x-1[data-side="left"] {
  --tw-translate-x: -0.25rem;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.data-\\[side\\=right\\]\\:translate-x-1[data-side="right"] {
  --tw-translate-x: 0.25rem;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.data-\\[side\\=top\\]\\:-translate-y-1[data-side="top"] {
  --tw-translate-y: -0.25rem;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.data-\\[state\\=checked\\]\\:translate-x-4[data-state="checked"] {
  --tw-translate-x: 1rem;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.data-\\[state\\=unchecked\\]\\:translate-x-0[data-state="unchecked"] {
  --tw-translate-x: 0px;
  transform: translate(var(--tw-translate-x), var(--tw-translate-y)) rotate(var(--tw-rotate)) skewX(var(--tw-skew-x)) skewY(var(--tw-skew-y)) scaleX(var(--tw-scale-x)) scaleY(var(--tw-scale-y));
}

.data-\\[disabled\\]\\:cursor-default[data-disabled] {
  cursor: default;
}

.data-\\[state\\=checked\\]\\:border-\\[var\\(--color-teal-600\\)\\][data-state="checked"] {
  border-color: var(--color-teal-600);
}

.data-\\[state\\=active\\]\\:border-b-\\[var\\(--color-aqua-600\\)\\][data-state="active"] {
  border-bottom-color: var(--color-aqua-600);
}

.data-\\[state\\=checked\\]\\:bg-\\[var\\(--color-teal-600\\)\\][data-state="checked"] {
  background-color: var(--color-teal-600);
}

.data-\\[state\\=selected\\]\\:bg-muted[data-state="selected"] {
  background-color: var(--muted);
}

.data-\\[inset\\]\\:pl-8[data-inset] {
  padding-left: 2rem;
}

.data-\\[placeholder\\]\\:text-muted-foreground[data-placeholder] {
  color: var(--muted-foreground);
}

.data-\\[state\\=active\\]\\:text-foreground[data-state="active"] {
  color: var(--foreground);
}

.data-\\[state\\=checked\\]\\:text-primary-foreground[data-state="checked"] {
  color: var(--primary-foreground);
}

.data-\\[state\\=open\\]\\:text-muted-foreground[data-state="open"] {
  color: var(--muted-foreground);
}

.data-\\[disabled\\=true\\]\\:opacity-50[data-disabled="true"] {
  opacity: 0.5;
}

.data-\\[disabled\\]\\:opacity-50[data-disabled] {
  opacity: 0.5;
}

.\\*\\:data-\\[slot\\=select-value\\]\\:flex-1[data-slot="select-value"] > * {
  flex: 1 1 0%;
}

.\\*\\:data-\\[slot\\=select-value\\]\\:truncate[data-slot="select-value"] > * {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.group[data-disabled="true"] .group-data-\\[disabled\\=true\\]\\:pointer-events-none {
  pointer-events: none;
}

.group[data-disabled="true"] .group-data-\\[disabled\\=true\\]\\:opacity-50 {
  opacity: 0.5;
}

@media (min-width: 640px) {

  .sm\\:max-w-lg {
    max-width: 32rem;
  }

  .sm\\:flex-row {
    flex-direction: row;
  }

  .sm\\:justify-end {
    justify-content: flex-end;
  }

  .sm\\:gap-2\\.5 {
    gap: 0.625rem;
  }

  .sm\\:space-x-2 > :not([hidden]) ~ :not([hidden]) {
    --tw-space-x-reverse: 0;
    margin-right: calc(0.5rem * var(--tw-space-x-reverse));
    margin-left: calc(0.5rem * calc(1 - var(--tw-space-x-reverse)));
  }

  .sm\\:text-left {
    text-align: left;
  }
}

@media (min-width: 768px) {

  .md\\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .md\\:text-sm {
    font-size: 0.875rem;
    line-height: 1.25rem;
  }
}

@media (min-width: 1024px) {

  .lg\\:col-span-2 {
    grid-column: span 2 / span 2;
  }

  .lg\\:block {
    display: block;
  }

  .lg\\:flex {
    display: flex;
  }

  .lg\\:hidden {
    display: none;
  }

  .lg\\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1280px) {

  .xl\\:grid-cols-4 {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (prefers-color-scheme: dark) {

  .dark\\:data-\\[state\\=checked\\]\\:bg-\\[var\\(--color-teal-600\\)\\][data-state="checked"] {
    background-color: var(--color-teal-600);
  }
}

.\\[\\&\\:has\\(\\[role\\=checkbox\\]\\)\\]\\:pr-0:has([role=checkbox]) {
  padding-right: 0px;
}

.\\[\\&\\:last-child\\]\\:pb-6:last-child {
  padding-bottom: 1.5rem;
}

.\\[\\&\\>svg\\]\\:pointer-events-none>svg {
  pointer-events: none;
}

.\\[\\&\\>svg\\]\\:size-3>svg {
  width: 0.75rem;
  height: 0.75rem;
}

.\\[\\&\\>svg\\]\\:size-3\\.5>svg {
  width: 0.875rem;
  height: 0.875rem;
}

.\\[\\&\\>tr\\]\\:last\\:border-b-0:last-child>tr {
  border-bottom-width: 0px;
}

.\\[\\&_\\[cmdk-group-heading\\]\\]\\:px-2 [cmdk-group-heading] {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.\\[\\&_\\[cmdk-group-heading\\]\\]\\:py-1\\.5 [cmdk-group-heading] {
  padding-top: 0.375rem;
  padding-bottom: 0.375rem;
}

.\\[\\&_\\[cmdk-group-heading\\]\\]\\:text-xs [cmdk-group-heading] {
  font-size: 0.75rem;
  line-height: 1rem;
}

.\\[\\&_\\[cmdk-group-heading\\]\\]\\:font-medium [cmdk-group-heading] {
  font-weight: 500;
}

.\\[\\&_\\[cmdk-group-heading\\]\\]\\:text-muted-foreground [cmdk-group-heading] {
  color: var(--muted-foreground);
}

.\\[\\&_\\[cmdk-group\\]\\:not\\(\\[hidden\\]\\)_\\~\\[cmdk-group\\]\\]\\:pt-0 [cmdk-group]:not([hidden]) ~[cmdk-group] {
  padding-top: 0px;
}

.\\[\\&_\\[cmdk-group\\]\\]\\:px-2 [cmdk-group] {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.\\[\\&_\\[cmdk-input-wrapper\\]_svg\\]\\:h-5 [cmdk-input-wrapper] svg {
  height: 1.25rem;
}

.\\[\\&_\\[cmdk-input-wrapper\\]_svg\\]\\:w-5 [cmdk-input-wrapper] svg {
  width: 1.25rem;
}

.\\[\\&_\\[cmdk-input\\]\\]\\:h-12 [cmdk-input] {
  height: 3rem;
}

.\\[\\&_\\[cmdk-item\\]\\]\\:px-2 [cmdk-item] {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.\\[\\&_\\[cmdk-item\\]\\]\\:py-3 [cmdk-item] {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

.\\[\\&_\\[cmdk-item\\]_svg\\]\\:h-5 [cmdk-item] svg {
  height: 1.25rem;
}

.\\[\\&_\\[cmdk-item\\]_svg\\]\\:w-5 [cmdk-item] svg {
  width: 1.25rem;
}

.\\[\\&_code\\]\\:before\\:content-none code::before {
  --tw-content: none;
  content: var(--tw-content);
}

.\\[\\&_code\\]\\:after\\:content-none code::after {
  --tw-content: none;
  content: var(--tw-content);
}

.\\[\\&_svg\\:not\\(\\[class\\*\\=\\'size-\\'\\]\\)\\]\\:size-4 svg:not([class*='size-']) {
  width: 1rem;
  height: 1rem;
}

.\\[\\&_svg\\:not\\(\\[class\\*\\=\\'text-\\'\\]\\)\\]\\:text-muted-foreground svg:not([class*='text-']) {
  color: var(--muted-foreground);
}

.\\[\\&_svg\\]\\:pointer-events-none svg {
  pointer-events: none;
}

.\\[\\&_svg\\]\\:shrink-0 svg {
  flex-shrink: 0;
}

.\\[\\&_tr\\:last-child\\]\\:border-0 tr:last-child {
  border-width: 0px;
}

.\\[\\&_tr\\]\\:border-b tr {
  border-bottom-width: 1px;
}`, "",{"version":3,"sources":["webpack://./src/styles.css"],"names":[],"mappings":"AAAA;EAAA,wBAA0B;EAA1B,wBAA0B;EAA1B,mBAA0B;EAA1B,mBAA0B;EAA1B,cAA0B;EAA1B,cAA0B;EAA1B,cAA0B;EAA1B,eAA0B;EAA1B,eAA0B;EAA1B,aAA0B;EAA1B,aAA0B;EAA1B,kBAA0B;EAA1B,sCAA0B;EAA1B,8BAA0B;EAA1B,6BAA0B;EAA1B,4BAA0B;EAA1B,eAA0B;EAA1B,oBAA0B;EAA1B,sBAA0B;EAA1B,uBAA0B;EAA1B,wBAA0B;EAA1B,kBAA0B;EAA1B,2BAA0B;EAA1B,4BAA0B;EAA1B,sCAA0B;EAA1B,kCAA0B;EAA1B,2BAA0B;EAA1B,sBAA0B;EAA1B,8BAA0B;EAA1B,YAA0B;EAA1B,kBAA0B;EAA1B,gBAA0B;EAA1B,iBAA0B;EAA1B,kBAA0B;EAA1B,cAA0B;EAA1B,gBAA0B;EAA1B,aAA0B;EAA1B,mBAA0B;EAA1B,qBAA0B;EAA1B,2BAA0B;EAA1B,yBAA0B;EAA1B,0BAA0B;EAA1B,2BAA0B;EAA1B,uBAA0B;EAA1B,wBAA0B;EAA1B,yBAA0B;EAA1B,sBAA0B;EAA1B,oBAA0B;EAA1B,sBAA0B;EAA1B,qBAA0B;EAA1B;AAA0B;;AAA1B;EAAA,wBAA0B;EAA1B,wBAA0B;EAA1B,mBAA0B;EAA1B,mBAA0B;EAA1B,cAA0B;EAA1B,cAA0B;EAA1B,cAA0B;EAA1B,eAA0B;EAA1B,eAA0B;EAA1B,aAA0B;EAA1B,aAA0B;EAA1B,kBAA0B;EAA1B,sCAA0B;EAA1B,8BAA0B;EAA1B,6BAA0B;EAA1B,4BAA0B;EAA1B,eAA0B;EAA1B,oBAA0B;EAA1B,sBAA0B;EAA1B,uBAA0B;EAA1B,wBAA0B;EAA1B,kBAA0B;EAA1B,2BAA0B;EAA1B,4BAA0B;EAA1B,sCAA0B;EAA1B,kCAA0B;EAA1B,2BAA0B;EAA1B,sBAA0B;EAA1B,8BAA0B;EAA1B,YAA0B;EAA1B,kBAA0B;EAA1B,gBAA0B;EAA1B,iBAA0B;EAA1B,kBAA0B;EAA1B,cAA0B;EAA1B,gBAA0B;EAA1B,aAA0B;EAA1B,mBAA0B;EAA1B,qBAA0B;EAA1B,2BAA0B;EAA1B,yBAA0B;EAA1B,0BAA0B;EAA1B,2BAA0B;EAA1B,uBAA0B;EAA1B,wBAA0B;EAA1B,yBAA0B;EAA1B,sBAA0B;EAA1B,oBAA0B;EAA1B,sBAA0B;EAA1B,qBAA0B;EAA1B;AAA0B,CAA1B;;CAA0B,CAA1B;;;CAA0B;;AAA1B;;;EAAA,sBAA0B,EAA1B,MAA0B;EAA1B,eAA0B,EAA1B,MAA0B;EAA1B,mBAA0B,EAA1B,MAA0B;EAA1B,qBAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;EAAA,gBAA0B;AAAA;;AAA1B;;;;;;;;CAA0B;;AAA1B;;EAAA,gBAA0B,EAA1B,MAA0B;EAA1B,8BAA0B,EAA1B,MAA0B;EAA1B,gBAA0B,EAA1B,MAA0B;EAA1B,cAA0B;KAA1B,WAA0B,EAA1B,MAA0B;EAA1B,+HAA0B,EAA1B,MAA0B;EAA1B,6BAA0B,EAA1B,MAA0B;EAA1B,+BAA0B,EAA1B,MAA0B;EAA1B,wCAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;;CAA0B;;AAA1B;EAAA,SAA0B,EAA1B,MAA0B;EAA1B,oBAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;;;CAA0B;;AAA1B;EAAA,SAA0B,EAA1B,MAA0B;EAA1B,cAA0B,EAA1B,MAA0B;EAA1B,qBAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,yCAA0B;UAA1B,iCAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;;;;;EAAA,kBAA0B;EAA1B,oBAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,cAA0B;EAA1B,wBAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;EAAA,mBAA0B;AAAA;;AAA1B;;;;;CAA0B;;AAA1B;;;;EAAA,+GAA0B,EAA1B,MAA0B;EAA1B,6BAA0B,EAA1B,MAA0B;EAA1B,+BAA0B,EAA1B,MAA0B;EAA1B,cAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,cAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;EAAA,cAA0B;EAA1B,cAA0B;EAA1B,kBAA0B;EAA1B,wBAA0B;AAAA;;AAA1B;EAAA,eAA0B;AAAA;;AAA1B;EAAA,WAA0B;AAAA;;AAA1B;;;;CAA0B;;AAA1B;EAAA,cAA0B,EAA1B,MAA0B;EAA1B,qBAA0B,EAA1B,MAA0B;EAA1B,yBAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;;;CAA0B;;AAA1B;;;;;EAAA,oBAA0B,EAA1B,MAA0B;EAA1B,8BAA0B,EAA1B,MAA0B;EAA1B,gCAA0B,EAA1B,MAA0B;EAA1B,eAA0B,EAA1B,MAA0B;EAA1B,oBAA0B,EAA1B,MAA0B;EAA1B,oBAA0B,EAA1B,MAA0B;EAA1B,uBAA0B,EAA1B,MAA0B;EAA1B,cAA0B,EAA1B,MAA0B;EAA1B,SAA0B,EAA1B,MAA0B;EAA1B,UAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;EAAA,oBAA0B;AAAA;;AAA1B;;;CAA0B;;AAA1B;;;;EAAA,0BAA0B,EAA1B,MAA0B;EAA1B,6BAA0B,EAA1B,MAA0B;EAA1B,sBAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,aAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,gBAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,wBAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;EAAA,YAA0B;AAAA;;AAA1B;;;CAA0B;;AAA1B;EAAA,6BAA0B,EAA1B,MAA0B;EAA1B,oBAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,wBAA0B;AAAA;;AAA1B;;;CAA0B;;AAA1B;EAAA,0BAA0B,EAA1B,MAA0B;EAA1B,aAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,kBAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;;;;;;;;;;;;EAAA,SAA0B;AAAA;;AAA1B;EAAA,SAA0B;EAA1B,UAA0B;AAAA;;AAA1B;EAAA,UAA0B;AAAA;;AAA1B;;;EAAA,gBAA0B;EAA1B,SAA0B;EAA1B,UAA0B;AAAA;;AAA1B;;CAA0B;AAA1B;EAAA,UAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;EAAA,gBAA0B;AAAA;;AAA1B;;;CAA0B;;AAA1B;EAAA,UAA0B,EAA1B,MAA0B;EAA1B,cAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;EAAA,UAA0B,EAA1B,MAA0B;EAA1B,cAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;EAAA,eAA0B;AAAA;;AAA1B;;CAA0B;AAA1B;EAAA,eAA0B;AAAA;;AAA1B;;;;CAA0B;;AAA1B;;;;;;;;EAAA,cAA0B,EAA1B,MAA0B;EAA1B,sBAA0B,EAA1B,MAA0B;AAAA;;AAA1B;;CAA0B;;AAA1B;;EAAA,eAA0B;EAA1B,YAA0B;AAAA;;AAA1B,wEAA0B;AAA1B;EAAA,aAA0B;AAAA;AAC1B;EAAA;AAAgC;AAAhC;;EAAA;IAAA;EAAgC;AAAA;AAAhC;;EAAA;IAAA;EAAgC;AAAA;AAAhC;;EAAA;IAAA;EAAgC;AAAA;AAAhC;;EAAA;IAAA;EAAgC;AAAA;AAAhC;;EAAA;IAAA;EAAgC;AAAA;AAChC;EAAA,kBAA+B;EAA/B,UAA+B;EAA/B,WAA+B;EAA/B,UAA+B;EAA/B,YAA+B;EAA/B,gBAA+B;EAA/B,sBAA+B;EAA/B,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,qBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,iBAA+B;EAA/B;AAA+B;AAA/B;EAAA,iBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA,gBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,aAA+B;EAA/B;AAA+B;AAA/B;EAAA,aAA+B;EAA/B;AAA+B;AAA/B;EAAA,cAA+B;EAA/B;AAA+B;AAA/B;EAAA,eAA+B;EAA/B;AAA+B;AAA/B;EAAA,WAA+B;EAA/B;AAA+B;AAA/B;EAAA,cAA+B;EAA/B;AAA+B;AAA/B;EAAA,aAA+B;EAA/B;AAA+B;AAA/B;EAAA,WAA+B;EAA/B;AAA+B;AAA/B;EAAA,cAA+B;EAA/B;AAA+B;AAA/B;EAAA,WAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA,iBAA+B;EAA/B,iBAA+B;EAA/B;AAA+B;AAA/B;EAAA,iBAA+B;EAA/B,iBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;;EAAA;IAAA;EAA+B;AAAA;AAA/B;EAAA;AAA+B;AAA/B;;EAAA;IAAA;EAA+B;AAAA;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,yBAA+B;KAA/B,sBAA+B;UAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,0BAA+B;EAA/B;AAA+B;AAA/B;EAAA,2BAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,uDAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,sDAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,uDAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,oDAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,gEAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,+DAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,gEAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,8DAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,+DAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,4DAA+B;EAA/B;AAA+B;AAA/B;EAAA,uBAA+B;EAA/B,8DAA+B;EAA/B;AAA+B;AAA/B;EAAA,wBAA+B;EAA/B,kEAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,gBAA+B;EAA/B,uBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,mCAA+B;EAA/B;AAA+B;AAA/B;EAAA,+BAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,4DAA+B;EAA/B,qEAA+B;EAA/B;AAA+B;AAA/B;EAAA,4DAA+B;EAA/B,qEAA+B;EAA/B;AAA+B;AAA/B;EAAA,4DAA+B;EAA/B,qEAA+B;EAA/B;AAA+B;AAA/B;EAAA,4DAA+B;EAA/B,oEAA+B;EAA/B;AAA+B;AAA/B;EAAA,4DAA+B;EAA/B,mEAA+B;EAA/B;AAA+B;AAA/B;EAAA,oEAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,sBAA+B;KAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,qBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B;AAA+B;AAA/B;EAAA,qBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,qBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,qBAA+B;EAA/B;AAA+B;AAA/B;EAAA,iBAA+B;EAA/B;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,iBAA+B;EAA/B;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA,iBAA+B;EAA/B;AAA+B;AAA/B;EAAA,gBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,eAA+B;EAA/B;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA,mBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,gDAA+B;EAA/B,6DAA+B;EAA/B;AAA+B;AAA/B;EAAA,+EAA+B;EAA/B,mGAA+B;EAA/B;AAA+B;AAA/B;EAAA,6EAA+B;EAA/B,iGAA+B;EAA/B;AAA+B;AAA/B;EAAA,sBAA+B;EAA/B,8BAA+B;EAA/B;AAA+B;AAA/B;EAAA,0CAA+B;EAA/B,uDAA+B;EAA/B;AAA+B;AAA/B;EAAA,8BAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,2GAA+B;EAA/B,yGAA+B;EAA/B;AAA+B;AAA/B;EAAA,oBAA+B;EAA/B;AAA+B;AAA/B;EAAA,kGAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,wJAA+B;EAA/B,wDAA+B;EAA/B;AAA+B;AAA/B;EAAA,qCAA+B;EAA/B,wDAA+B;EAA/B;AAA+B;AAA/B;EAAA,wBAA+B;EAA/B,wDAA+B;EAA/B;AAA+B;AAA/B;EAAA,+FAA+B;EAA/B,wDAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA,4BAA+B;EAA/B,wDAA+B;EAA/B;AAA+B;AAA/B;EAAA,+BAA+B;EAA/B,wDAA+B;EAA/B;AAA+B;AAA/B;EAAA,8BAA+B;EAA/B,wDAA+B;EAA/B;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;AAA/B;EAAA;AAA+B;;AAE/B,oCAAoC;;AAEpC;EACE,iBAAiB;EACjB,4CAA4C;EAC5C,uCAAuC;EACvC,wCAAwC;EACxC,eAAe;EACf,6CAA6C;EAC7C,kBAAkB;EAClB,gDAAgD;EAChD,sCAAsC;EACtC,6BAA6B;EAC7B,oCAAoC;EACpC,+BAA+B;EAC/B,2CAA2C;EAC3C,mCAAmC;EACnC,mCAAmC;EACnC,8CAA8C;EAC9C,oCAAoC;EACpC,+CAA+C;EAC/C,0CAA0C;EAC1C,iCAAiC;EACjC,qCAAqC;EACrC,6BAA6B;EAC7B,oCAAoC;EACpC,oBAAoB;EACpB,8CAA8C;EAC9C,0CAA0C;EAC1C,+CAA+C;EAC/C,yBAAyB;EACzB,yBAAyB;EACzB,wBAAwB;EACxB,oCAAoC;EACpC,mCAAmC;EACnC,oCAAoC;EACpC,oCAAoC;EACpC,mCAAmC;EACnC,kBAAkB;EAClB,2BAA2B;EAC3B,sCAAsC;EACtC,0BAA0B;EAC1B,8CAA8C;EAC9C,iCAAiC;EACjC,6CAA6C;EAC7C,kCAAkC;EAClC,gCAAgC;EAChC,kBAAkB;EAClB,mBAAmB;EACnB,iBAAiB;EACjB,mBAAmB;EACnB,kBAAkB;EAClB,kBAAkB;EAClB,6BAA6B;EAC7B,8BAA8B;EAC9B,8BAA8B;EAC9B,8BAA8B;EAC9B,8BAA8B;EAC9B,8BAA8B;EAC9B,8BAA8B;EAC9B,8BAA8B;EAC9B,8BAA8B;EAC9B,8BAA8B;EAC9B,2BAA2B;EAC3B,iCAAiC;EACjC,gCAAgC;EAChC,8BAA8B;EAC9B,8BAA8B;EAC9B,oCAAoC;EACpC,mCAAmC;EACnC,8BAA8B;EAC9B,oCAAoC;EACpC,iCAAiC;EACjC,8BAA8B;EAC9B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,wBAAwB;EACxB,yBAAyB;EACzB,yBAAyB;EACzB,yBAAyB;EACzB,yBAAyB;EACzB,yBAAyB;EACzB,yBAAyB;EACzB,gCAAgC;EAChC,iCAAiC;EACjC,iCAAiC;EACjC,iCAAiC;EACjC,8BAA8B;EAC9B,+BAA+B;EAC/B,8BAA8B;EAC9B,8BAA8B;EAC9B,gCAAgC;EAChC,iCAAiC;EACjC,iCAAiC;EACjC,iCAAiC;EACjC,iCAAiC;EACjC,iCAAiC;EACjC,8BAA8B;EAC9B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,+BAA+B;EAC/B,iCAAiC;EACjC,kCAAkC;EAClC,kCAAkC;EAClC,kCAAkC;EAClC,kCAAkC;EAClC,kCAAkC;EAClC,yDAAyD;EACzD,2DAA2D;EAC3D,wDAAwD;EACxD,8CAA8C;EAC9C,8CAA8C;EAC9C,+CAA+C;AACjD;;AAEA;EACE,8BAA8B;EAC9B,8BAA8B;EAC9B,wBAAwB;EACxB,mCAAmC;EACnC,2BAA2B;EAC3B,sCAAsC;EACtC,sCAAsC;EACtC,sCAAsC;EACtC,6BAA6B;EAC7B,wCAAwC;EACxC,yBAAyB;EACzB,oCAAoC;EACpC,0BAA0B;EAC1B,qCAAqC;EACrC,0CAA0C;EAC1C,iCAAiC;EACjC,0BAA0B;EAC1B,yBAAyB;EACzB,wBAAwB;EACxB,yBAAyB;EACzB,yBAAyB;AAC3B;;AAEA,mCAAmC;AACnC;EACE,2BAA2B;AAC7B;;AAEA;EACE,2BAA2B;AAC7B;;AAEA;EACE,mCAAmC;EACnC,wBAAwB;EACxB,iDAAiD;EACjD,SAAS;EACT,UAAU;EACV,iBAAiB;AACnB;;AAEA,4CAA4C;AAC5C;EACE,iBAAiB;EACjB,gBAAgB;EAChB,gBAAgB;EAChB,wBAAwB;EACxB,SAAS;AACX;;AAEA;EACE,kBAAkB;EAClB,gBAAgB;EAChB,gBAAgB;EAChB,wBAAwB;EACxB,SAAS;AACX;;AAEA;EACE,mBAAmB;EACnB,gBAAgB;EAChB,gBAAgB;EAChB,wBAAwB;EACxB,SAAS;AACX;;AAEA,sDAAsD;AACtD,uBAAuB,mBAAmB,EAAE,gBAAgB,EAAE,mBAAmB,EAAE,qBAAqB,EAAE,cAAc,EAAE;AAC1H,uBAAuB,eAAe,EAAE,gBAAgB,EAAE,mBAAmB,EAAE,qBAAqB,EAAE,cAAc,EAAE;AACtH,uBAAuB,mBAAmB,EAAE,gBAAgB,EAAE,kBAAkB,EAAE,sBAAsB,EAAE,cAAc,EAAE;AAC1H,sBAAsB,qBAAqB,EAAE;AAC7C,iCAAiC,gBAAgB,EAAE;AACnD,yBAAyB,yBAAyB,EAAE,cAAc,EAAE,yBAAyB,EAAE,sBAAsB,EAAE,kBAAkB,EAAE,oCAAoC,EAAE;AACjL,wBAAwB,yBAAyB,EAAE,cAAc,EAAE,gBAAgB,EAAE,uBAAuB,EAAE,gBAAgB,EAAE,gBAAgB,EAAE,kBAAkB,EAAE;AACtK,6BAA6B,6BAA6B,EAAE,cAAc,EAAE,UAAU,EAAE,oCAAoC,EAAE;AAC9H,uBAAuB,qBAAqB,EAAE,2BAA2B,EAAE,qBAAqB,EAAE;AAClG,uBAAuB,wBAAwB,EAAE,2BAA2B,EAAE,qBAAqB,EAAE;AACrG,uBAAuB,cAAc,EAAE;AACvC,sBAAsB,cAAc,EAAE,0BAA0B,EAAE;AAClE,4BAA4B,cAAc,EAAE;AAC5C,2BAA2B,gBAAgB,EAAE,cAAc,EAAE;AAC7D,uBAAuB,kBAAkB,EAAE;AAC3C,+BAA+B,8BAA8B,EAAE,qBAAqB,EAAE,gBAAgB,EAAE,cAAc,EAAE,kBAAkB,EAAE;AAC5I,0BAA0B,eAAe,EAAE,yBAAyB,EAAE,kBAAkB,EAAE,gBAAgB,EAAE,yBAAyB,EAAE;AACvI,uBAAuB,yBAAyB,EAAE,uBAAuB,EAAE,yBAAyB,EAAE,gBAAgB,EAAE,gBAAgB,EAAE;AAC1I,uBAAuB,yBAAyB,EAAE,uBAAuB,EAAE;AAC3E,uBAAuB,iBAAiB,EAAE,qBAAqB,EAAE;;AAEjE,6CAA6C;;AA1N7C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,mBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,6EA0N8C;EA1N9C,iGA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,8BA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,2GA0N8C;EA1N9C,yGA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,2GA0N8C;EA1N9C,yGA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,8BA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,2GA0N8C;EA1N9C,yGA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,2GA0N8C;EA1N9C,yGA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,qBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,yBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,0BA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,yBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,0BA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,sBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,qBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,gBA0N8C;EA1N9C,uBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;;EAAA;IAAA;EA0N8C;;EA1N9C;IAAA;EA0N8C;;EA1N9C;IAAA;EA0N8C;;EA1N9C;IAAA;EA0N8C;;EA1N9C;IAAA,uBA0N8C;IA1N9C,sDA0N8C;IA1N9C;EA0N8C;;EA1N9C;IAAA;EA0N8C;AAAA;;AA1N9C;;EAAA;IAAA;EA0N8C;;EA1N9C;IAAA,mBA0N8C;IA1N9C;EA0N8C;AAAA;;AA1N9C;;EAAA;IAAA;EA0N8C;;EA1N9C;IAAA;EA0N8C;;EA1N9C;IAAA;EA0N8C;;EA1N9C;IAAA;EA0N8C;;EA1N9C;IAAA;EA0N8C;AAAA;;AA1N9C;;EAAA;IAAA;EA0N8C;AAAA;;AA1N9C;;EAAA;IAAA;EA0N8C;AAAA;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,cA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,eA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,qBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,oBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,kBA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA,WA0N8C;EA1N9C;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C;;AA1N9C;EAAA;AA0N8C","sourcesContent":["@import \"tailwindcss/base\";\n@import \"tailwindcss/components\";\n@import \"tailwindcss/utilities\";\n\n@custom-variant dark (&:is(.dark *));\n\n:root {\n  --font-size: 14px;\n  --font-family-unna: 'Victor Mono', monospace;\n  --background: var(--color-warm-gray-50);\n  --foreground: var(--color-warm-gray-700);\n  --card: #ffffff;\n  --card-foreground: var(--color-warm-gray-700);\n  --popover: #ffffff;\n  --popover-foreground: var(--color-warm-gray-700);\n  --primary: var(--color-brand-blue-600);\n  --primary-foreground: #ffffff;\n  --secondary: var(--color-steel-blue);\n  --secondary-foreground: #ffffff;\n  --accent-subtle: var(--color-purple-accent);\n  --accent-subtle-foreground: #ffffff;\n  --muted: var(--color-warm-gray-100);\n  --muted-foreground: var(--color-warm-gray-500);\n  --accent: var(--color-warm-gray-100);\n  --accent-foreground: var(--color-warm-gray-900);\n  --destructive: var(--color-status-red-500);\n  --destructive-foreground: #ffffff;\n  --warning: var(--color-warning-amber);\n  --warning-foreground: #ffffff;\n  --border: var(--color-warm-gray-200);\n  --input: transparent;\n  --input-background: var(--color-warm-gray-100);\n  --input-border: var(--color-warm-gray-300);\n  --switch-background: var(--color-warm-gray-300);\n  --font-weight-medium: 500;\n  --font-weight-normal: 400;\n  --ring: oklch(0.708 0 0);\n  --chart-1: oklch(0.646 0.222 41.116);\n  --chart-2: oklch(0.6 0.118 184.704);\n  --chart-3: oklch(0.398 0.07 227.392);\n  --chart-4: oklch(0.828 0.189 84.429);\n  --chart-5: oklch(0.769 0.188 70.08);\n  --radius: 0.375rem;\n  --sidebar: oklch(0.985 0 0);\n  --sidebar-foreground: oklch(0.145 0 0);\n  --sidebar-primary: #030213;\n  --sidebar-primary-foreground: oklch(0.985 0 0);\n  --sidebar-accent: oklch(0.97 0 0);\n  --sidebar-accent-foreground: oklch(0.205 0 0);\n  --sidebar-border: oklch(0.922 0 0);\n  --sidebar-ring: oklch(0.708 0 0);\n  --text-xs: 0.75rem;\n  --text-sm: 0.875rem;\n  --text-base: 1rem;\n  --text-lg: 1.125rem;\n  --text-xl: 1.25rem;\n  --text-2xl: 1.5rem;\n  --color-warm-gray-50: #f5f5f4;\n  --color-warm-gray-100: #f0f0ef;\n  --color-warm-gray-200: #e7e5e4;\n  --color-warm-gray-300: #d6d3d1;\n  --color-warm-gray-400: #a8a29e;\n  --color-warm-gray-500: #78716c;\n  --color-warm-gray-600: #57534e;\n  --color-warm-gray-700: #44403c;\n  --color-warm-gray-800: #292524;\n  --color-warm-gray-900: #1c1917;\n  --color-steel-blue: #475569;\n  --color-steel-blue-light: #64748b;\n  --color-steel-blue-dark: #334155;\n  --color-blue-light-bg: #e0f2fe;\n  --color-purple-accent: #6366f1;\n  --color-purple-accent-light: #a5b4fc;\n  --color-purple-accent-dark: #4338ca;\n  --color-warning-amber: #f59e0b;\n  --color-warning-amber-light: #fbbf24;\n  --color-warning-amber-bg: #fffbeb;\n  --color-brand-blue-50: #eff6ff;\n  --color-brand-blue-100: #dbeafe;\n  --color-brand-blue-200: #bfdbfe;\n  --color-brand-blue-300: #93c5fd;\n  --color-brand-blue-400: #60a5fa;\n  --color-brand-blue-500: #3b82f6;\n  --color-brand-blue-600: #2563eb;\n  --color-brand-blue-700: #1d4ed8;\n  --color-brand-blue-800: #1e40af;\n  --color-brand-blue-900: #1e3a8a;\n  --color-brand-blue-950: #172554;\n  --color-aqua-50: #f0f9ff;\n  --color-aqua-100: #e0f2fe;\n  --color-aqua-200: #bae6fd;\n  --color-aqua-300: #7dd3fc;\n  --color-aqua-500: #0ea5e9;\n  --color-aqua-600: #0284c7;\n  --color-aqua-700: #0369a1;\n  --color-brand-indigo-50: #eef2ff;\n  --color-brand-indigo-100: #e0e7ff;\n  --color-brand-indigo-400: #818cf8;\n  --color-brand-indigo-600: #4338ca;\n  --color-brand-cyan-50: #f0fdff;\n  --color-brand-cyan-100: #e0f2fe;\n  --color-brand-sky-400: #38bdf8;\n  --color-brand-sky-500: #0ea5e9;\n  --color-status-green-50: #f0fdf4;\n  --color-status-green-100: #dcfce7;\n  --color-status-green-200: #bbf7d0;\n  --color-status-green-500: #22c55e;\n  --color-status-green-600: #16a34a;\n  --color-status-green-700: #15803d;\n  --color-status-red-50: #fef2f2;\n  --color-status-red-100: #fee2e2;\n  --color-status-red-200: #fecaca;\n  --color-status-red-500: #ef4444;\n  --color-status-red-600: #dc2626;\n  --color-status-red-700: #b91c1c;\n  --color-status-yellow-50: #fefce8;\n  --color-status-yellow-100: #fef3c7;\n  --color-status-yellow-200: #fde68a;\n  --color-status-yellow-500: #eab308;\n  --color-status-yellow-600: #ca8a04;\n  --color-status-yellow-700: #a16207;\n  --brand-shadow-light: 0 12px 24px rgba(37, 99, 235, 0.08);\n  --brand-shadow-medium: 0 16px 28px rgba(99, 102, 241, 0.18);\n  --brand-shadow-heavy: 0 18px 40px rgba(15, 23, 42, 0.28);\n  --brand-border-light: rgba(226, 232, 240, 0.8);\n  --brand-border-medium: rgba(37, 99, 235, 0.35);\n  --brand-border-strong: rgba(59, 130, 246, 0.35);\n}\n\n.dark {\n  --background: oklch(0.145 0 0);\n  --foreground: oklch(0.985 0 0);\n  --card: oklch(0.145 0 0);\n  --card-foreground: oklch(0.985 0 0);\n  --popover: oklch(0.145 0 0);\n  --popover-foreground: oklch(0.985 0 0);\n  --primary: var(--color-brand-blue-600);\n  --primary-foreground: oklch(0.205 0 0);\n  --secondary: oklch(0.269 0 0);\n  --secondary-foreground: oklch(0.985 0 0);\n  --muted: oklch(0.269 0 0);\n  --muted-foreground: oklch(0.708 0 0);\n  --accent: oklch(0.269 0 0);\n  --accent-foreground: oklch(0.985 0 0);\n  --destructive: var(--color-status-red-500);\n  --destructive-foreground: #ffffff;\n  --border: oklch(0.269 0 0);\n  --input: oklch(0.269 0 0);\n  --ring: oklch(0.439 0 0);\n  --font-weight-medium: 500;\n  --font-weight-normal: 400;\n}\n\n/* Base styles - matching web-app */\n* {\n  border-color: var(--border);\n}\n\nhtml {\n  font-size: var(--font-size);\n}\n\nbody {\n  background-color: var(--background);\n  color: var(--foreground);\n  font-family: system-ui, -apple-system, sans-serif;\n  margin: 0;\n  padding: 0;\n  min-height: 100vh;\n}\n\n/* Typography hierarchy - matching web-app */\nh1 {\n  font-size: 1.5rem;\n  font-weight: 600;\n  line-height: 1.3;\n  color: var(--foreground);\n  margin: 0;\n}\n\nh2 {\n  font-size: 1.25rem;\n  font-weight: 600;\n  line-height: 1.4;\n  color: var(--foreground);\n  margin: 0;\n}\n\nh3 {\n  font-size: 1.125rem;\n  font-weight: 600;\n  line-height: 1.5;\n  color: var(--foreground);\n  margin: 0;\n}\n\n/* Markdown content styling (for marked HTML output) */\n.markdown-content h1 { font-size: 1.125rem; font-weight: 700; margin-top: 0.75rem; margin-bottom: 0.5rem; color: #111827; }\n.markdown-content h2 { font-size: 1rem; font-weight: 700; margin-top: 0.75rem; margin-bottom: 0.5rem; color: #111827; }\n.markdown-content h3 { font-size: 0.875rem; font-weight: 700; margin-top: 0.5rem; margin-bottom: 0.25rem; color: #111827; }\n.markdown-content p { margin-bottom: 0.5rem; }\n.markdown-content p:last-child { margin-bottom: 0; }\n.markdown-content code { background-color: #e5e7eb; color: #1f2937; padding: 0.125rem 0.25rem; border-radius: 0.25rem; font-size: 0.75rem; font-family: ui-monospace, monospace; }\n.markdown-content pre { background-color: #1f2937; color: #f3f4f6; padding: 0.75rem; border-radius: 0.375rem; overflow-x: auto; margin: 0.5rem 0; font-size: 0.75rem; }\n.markdown-content pre code { background-color: transparent; color: inherit; padding: 0; font-family: ui-monospace, monospace; }\n.markdown-content ul { list-style-type: disc; list-style-position: inside; margin-bottom: 0.5rem; }\n.markdown-content ol { list-style-type: decimal; list-style-position: inside; margin-bottom: 0.5rem; }\n.markdown-content li { color: #374151; }\n.markdown-content a { color: #4f46e5; text-decoration: underline; }\n.markdown-content a:hover { color: #6366f1; }\n.markdown-content strong { font-weight: 600; color: #111827; }\n.markdown-content em { font-style: italic; }\n.markdown-content blockquote { border-left: 4px solid #d1d5db; padding-left: 0.75rem; margin: 0.5rem 0; color: #4b5563; font-style: italic; }\n.markdown-content table { min-width: 100%; border: 1px solid #d1d5db; font-size: 0.75rem; margin: 0.5rem 0; border-collapse: collapse; }\n.markdown-content th { border: 1px solid #d1d5db; padding: 0.25rem 0.5rem; background-color: #f3f4f6; font-weight: 600; text-align: left; }\n.markdown-content td { border: 1px solid #d1d5db; padding: 0.25rem 0.5rem; }\n.markdown-content hr { margin: 0.75rem 0; border-color: #d1d5db; }\n\n/* Remove manual icon initialization styles */"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ },

/***/ 825
(module) {



/* istanbul ignore next  */
function apply(styleElement, options, obj) {
  var css = "";
  if (obj.supports) {
    css += "@supports (".concat(obj.supports, ") {");
  }
  if (obj.media) {
    css += "@media ".concat(obj.media, " {");
  }
  var needLayer = typeof obj.layer !== "undefined";
  if (needLayer) {
    css += "@layer".concat(obj.layer.length > 0 ? " ".concat(obj.layer) : "", " {");
  }
  css += obj.css;
  if (needLayer) {
    css += "}";
  }
  if (obj.media) {
    css += "}";
  }
  if (obj.supports) {
    css += "}";
  }
  var sourceMap = obj.sourceMap;
  if (sourceMap && typeof btoa !== "undefined") {
    css += "\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap)))), " */");
  }

  // For old IE
  /* istanbul ignore if  */
  options.styleTagTransform(css, styleElement, options.options);
}
function removeStyleElement(styleElement) {
  // istanbul ignore if
  if (styleElement.parentNode === null) {
    return false;
  }
  styleElement.parentNode.removeChild(styleElement);
}

/* istanbul ignore next  */
function domAPI(options) {
  if (typeof document === "undefined") {
    return {
      update: function update() {},
      remove: function remove() {}
    };
  }
  var styleElement = options.insertStyleElement(options);
  return {
    update: function update(obj) {
      apply(styleElement, options, obj);
    },
    remove: function remove() {
      removeStyleElement(styleElement);
    }
  };
}
module.exports = domAPI;

/***/ },

/***/ 848
(module, __unused_webpack_exports, __webpack_require__) {



if (true) {
  module.exports = __webpack_require__(20);
} else // removed by dead control flow
{}


/***/ },

/***/ 961
(module, __unused_webpack_exports, __webpack_require__) {



function checkDCE() {
  /* global __REACT_DEVTOOLS_GLOBAL_HOOK__ */
  if (
    typeof __REACT_DEVTOOLS_GLOBAL_HOOK__ === 'undefined' ||
    typeof __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE !== 'function'
  ) {
    return;
  }
  if (false) // removed by dead control flow
{}
  try {
    // Verify that the code above has been dead code eliminated (DCE'd).
    __REACT_DEVTOOLS_GLOBAL_HOOK__.checkDCE(checkDCE);
  } catch (err) {
    // DevTools shouldn't crash React, no matter what.
    // We should still report in case we break this code.
    console.error(err);
  }
}

if (true) {
  // DCE check should happen before ReactDOM bundle executes so that
  // DevTools can report bad minification during injection.
  checkDCE();
  module.exports = __webpack_require__(551);
} else // removed by dead control flow
{}


/***/ },

/***/ 982
(module, __unused_webpack_exports, __webpack_require__) {



if (true) {
  module.exports = __webpack_require__(463);
} else // removed by dead control flow
{}


/***/ }

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/create fake namespace object */
/******/ 	(() => {
/******/ 		var getProto = Object.getPrototypeOf ? (obj) => (Object.getPrototypeOf(obj)) : (obj) => (obj.__proto__);
/******/ 		var leafPrototypes;
/******/ 		// create a fake namespace object
/******/ 		// mode & 1: value is a module id, require it
/******/ 		// mode & 2: merge all properties of value into the ns
/******/ 		// mode & 4: return value when already ns object
/******/ 		// mode & 16: return value when it's Promise-like
/******/ 		// mode & 8|1: behave like require
/******/ 		__webpack_require__.t = function(value, mode) {
/******/ 			if(mode & 1) value = this(value);
/******/ 			if(mode & 8) return value;
/******/ 			if(typeof value === 'object' && value) {
/******/ 				if((mode & 4) && value.__esModule) return value;
/******/ 				if((mode & 16) && typeof value.then === 'function') return value;
/******/ 			}
/******/ 			var ns = Object.create(null);
/******/ 			__webpack_require__.r(ns);
/******/ 			var def = {};
/******/ 			leafPrototypes = leafPrototypes || [null, getProto({}), getProto([]), getProto(getProto)];
/******/ 			for(var current = mode & 2 && value; (typeof current == 'object' || typeof current == 'function') && !~leafPrototypes.indexOf(current); current = getProto(current)) {
/******/ 				Object.getOwnPropertyNames(current).forEach((key) => (def[key] = () => (value[key])));
/******/ 			}
/******/ 			def['default'] = () => (value);
/******/ 			__webpack_require__.d(ns, def);
/******/ 			return ns;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/nonce */
/******/ 	(() => {
/******/ 		__webpack_require__.nc = undefined;
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};

// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js
var injectStylesIntoStyleTag = __webpack_require__(72);
var injectStylesIntoStyleTag_default = /*#__PURE__*/__webpack_require__.n(injectStylesIntoStyleTag);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/styleDomAPI.js
var styleDomAPI = __webpack_require__(825);
var styleDomAPI_default = /*#__PURE__*/__webpack_require__.n(styleDomAPI);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/insertBySelector.js
var insertBySelector = __webpack_require__(659);
var insertBySelector_default = /*#__PURE__*/__webpack_require__.n(insertBySelector);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js
var setAttributesWithoutAttributes = __webpack_require__(56);
var setAttributesWithoutAttributes_default = /*#__PURE__*/__webpack_require__.n(setAttributesWithoutAttributes);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/insertStyleElement.js
var insertStyleElement = __webpack_require__(540);
var insertStyleElement_default = /*#__PURE__*/__webpack_require__.n(insertStyleElement);
// EXTERNAL MODULE: ./node_modules/style-loader/dist/runtime/styleTagTransform.js
var styleTagTransform = __webpack_require__(113);
var styleTagTransform_default = /*#__PURE__*/__webpack_require__.n(styleTagTransform);
// EXTERNAL MODULE: ./node_modules/css-loader/dist/cjs.js!./node_modules/postcss-loader/dist/cjs.js??ruleSet[1].rules[1].use[2]!./src/styles.css
var styles = __webpack_require__(784);
;// ./src/styles.css

      
      
      
      
      
      
      
      
      

var options = {};

options.styleTagTransform = (styleTagTransform_default());
options.setAttributes = (setAttributesWithoutAttributes_default());
options.insert = insertBySelector_default().bind(null, "head");
options.domAPI = (styleDomAPI_default());
options.insertStyleElement = (insertStyleElement_default());

var update = injectStylesIntoStyleTag_default()(styles/* default */.A, options);




       /* harmony default export */ const src_styles = (styles/* default */.A && styles/* default */.A.locals ? styles/* default */.A.locals : undefined);

// EXTERNAL MODULE: ./node_modules/react/index.js
var react = __webpack_require__(159);
var react_namespaceObject = /*#__PURE__*/__webpack_require__.t(react, 2);
// EXTERNAL MODULE: ./node_modules/react-dom/client.js
var client = __webpack_require__(338);
;// ./node_modules/lucide-react/dist/esm/shared/src/utils.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */

const toKebabCase = (string) => string.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase();
const toCamelCase = (string) => string.replace(
  /^([A-Z])|[\s-_]+(\w)/g,
  (match, p1, p2) => p2 ? p2.toUpperCase() : p1.toLowerCase()
);
const toPascalCase = (string) => {
  const camelCase = toCamelCase(string);
  return camelCase.charAt(0).toUpperCase() + camelCase.slice(1);
};
const mergeClasses = (...classes) => classes.filter((className, index, array) => {
  return Boolean(className) && className.trim() !== "" && array.indexOf(className) === index;
}).join(" ").trim();


//# sourceMappingURL=utils.js.map

;// ./node_modules/lucide-react/dist/esm/defaultAttributes.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */

var defaultAttributes = {
  xmlns: "http://www.w3.org/2000/svg",
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 2,
  strokeLinecap: "round",
  strokeLinejoin: "round"
};


//# sourceMappingURL=defaultAttributes.js.map

;// ./node_modules/lucide-react/dist/esm/Icon.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */





const Icon = (0,react.forwardRef)(
  ({
    color = "currentColor",
    size = 24,
    strokeWidth = 2,
    absoluteStrokeWidth,
    className = "",
    children,
    iconNode,
    ...rest
  }, ref) => {
    return (0,react.createElement)(
      "svg",
      {
        ref,
        ...defaultAttributes,
        width: size,
        height: size,
        stroke: color,
        strokeWidth: absoluteStrokeWidth ? Number(strokeWidth) * 24 / Number(size) : strokeWidth,
        className: mergeClasses("lucide", className),
        ...rest
      },
      [
        ...iconNode.map(([tag, attrs]) => (0,react.createElement)(tag, attrs)),
        ...Array.isArray(children) ? children : [children]
      ]
    );
  }
);


//# sourceMappingURL=Icon.js.map

;// ./node_modules/lucide-react/dist/esm/createLucideIcon.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */





const createLucideIcon = (iconName, iconNode) => {
  const Component = (0,react.forwardRef)(
    ({ className, ...props }, ref) => (0,react.createElement)(Icon, {
      ref,
      iconNode,
      className: mergeClasses(
        `lucide-${toKebabCase(toPascalCase(iconName))}`,
        `lucide-${iconName}`,
        className
      ),
      ...props
    })
  );
  Component.displayName = toPascalCase(iconName);
  return Component;
};


//# sourceMappingURL=createLucideIcon.js.map

;// ./node_modules/lucide-react/dist/esm/icons/waypoints.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const __iconNode = [
  ["circle", { cx: "12", cy: "4.5", r: "2.5", key: "r5ysbb" }],
  ["path", { d: "m10.2 6.3-3.9 3.9", key: "1nzqf6" }],
  ["circle", { cx: "4.5", cy: "12", r: "2.5", key: "jydg6v" }],
  ["path", { d: "M7 12h10", key: "b7w52i" }],
  ["circle", { cx: "19.5", cy: "12", r: "2.5", key: "1piiel" }],
  ["path", { d: "m13.8 17.7 3.9-3.9", key: "1wyg1y" }],
  ["circle", { cx: "12", cy: "19.5", r: "2.5", key: "13o1pw" }]
];
const Waypoints = createLucideIcon("waypoints", __iconNode);


//# sourceMappingURL=waypoints.js.map

;// ./node_modules/lucide-react/dist/esm/icons/radio.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const radio_iconNode = [
  ["path", { d: "M4.9 19.1C1 15.2 1 8.8 4.9 4.9", key: "1vaf9d" }],
  ["path", { d: "M7.8 16.2c-2.3-2.3-2.3-6.1 0-8.5", key: "u1ii0m" }],
  ["circle", { cx: "12", cy: "12", r: "2", key: "1c9p78" }],
  ["path", { d: "M16.2 7.8c2.3 2.3 2.3 6.1 0 8.5", key: "1j5fej" }],
  ["path", { d: "M19.1 4.9C23 8.8 23 15.1 19.1 19", key: "10b0cb" }]
];
const Radio = createLucideIcon("radio", radio_iconNode);


//# sourceMappingURL=radio.js.map

;// ./node_modules/lucide-react/dist/esm/icons/key-round.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const key_round_iconNode = [
  [
    "path",
    {
      d: "M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z",
      key: "1s6t7t"
    }
  ],
  ["circle", { cx: "16.5", cy: "7.5", r: ".5", fill: "currentColor", key: "w0ekpg" }]
];
const KeyRound = createLucideIcon("key-round", key_round_iconNode);


//# sourceMappingURL=key-round.js.map

// EXTERNAL MODULE: ./node_modules/react/jsx-runtime.js
var jsx_runtime = __webpack_require__(848);
;// ./src/components/LocalSidebar.jsx



function LocalSidebar(_ref) {
  var appState = _ref.appState;
  var currentView = appState.currentView,
    showAgentList = appState.showAgentList,
    showTopicsList = appState.showTopicsList,
    showLLMConfig = appState.showLLMConfig;
  var isAgentsActive = currentView === 'agent-list' || currentView === 'agent-details';
  var isTopicsActive = currentView === 'topics-list' || currentView === 'topic-details';
  var isLLMConfigActive = currentView === 'llm-config';
  return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
    className: "flex flex-col m-3 rounded-xl relative transition-all duration-300 ease-out",
    style: {
      width: '244px',
      background: 'linear-gradient(to bottom, rgba(239, 246, 255, 0.8), rgba(219, 234, 254, 0.8))',
      boxShadow: "\n          inset -10px -8px 0px -11px rgba(255, 255, 255, 0.6),\n          inset 0px -9px 0px -8px rgba(255, 255, 255, 0.4),\n          inset 10px 10px 20px -10px rgba(255, 255, 255, 0.3),\n          inset -10px -10px 20px -10px rgba(0, 0, 0, 0.05)\n        ",
      backdropFilter: "blur(2px) saturate(160%)"
    },
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "absolute inset-0 rounded-xl pointer-events-none",
      style: {
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(1px)',
        WebkitBackdropFilter: 'blur(1px)',
        boxShadow: "\n            inset -10px -8px 0px -11px rgba(255, 255, 255, 1),\n            inset 0px -9px 0px -8px rgba(255, 255, 255, 1)\n          ",
        opacity: 0.6,
        zIndex: -1,
        filter: 'blur(8px) drop-shadow(10px 4px 6px rgba(0, 0, 0, 1)) brightness(115%)'
      }
    }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "h-1 bg-gradient-to-r from-yellow-400 via-yellow-500 to-amber-500 rounded-t-xl"
    }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-center gap-3 p-4 pb-2 flex-shrink-0",
      style: {
        filter: 'blur(0px) brightness(100%)'
      },
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
        className: "text-lg font-bold text-[var(--color-brand-blue-700)] tracking-wider uppercase",
        children: "DISPATCH"
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center gap-1 px-2 py-0.5 rounded-full bg-gradient-to-r from-yellow-100 to-amber-100 border border-yellow-300",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "w-1.5 h-1.5 rounded-full bg-gradient-to-r from-yellow-500 to-amber-500"
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
          className: "text-xs text-yellow-800 font-semibold uppercase tracking-wider",
          children: "LOCAL"
        })]
      })]
    }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "flex-1 flex flex-col pt-1 overflow-y-auto",
      style: {
        filter: 'blur(0px) brightness(100%)'
      },
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("nav", {
        className: "mt-1 flex flex-col flex-1 px-2 space-y-0.5",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "px-3 py-1.5",
          children: /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-xs font-semibold text-[var(--color-warm-gray-600)] uppercase tracking-wider",
            children: "Local"
          })
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          children: /*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
            onClick: showAgentList,
            className: "flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors hover:cursor-pointer w-full transition-all duration-200 ease-out ".concat(!isAgentsActive ? 'hover:bg-white hover:bg-opacity-20' : ''),
            style: {
              background: isAgentsActive ? 'rgba(191, 219, 254, 0.4)' : 'transparent',
              color: isAgentsActive ? 'var(--color-brand-blue-800)' : 'var(--color-warm-gray-700)'
            },
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Waypoints, {
              className: "w-4 h-4 mr-3"
            }), "Agents"]
          })
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          children: /*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
            onClick: showTopicsList,
            className: "flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors hover:cursor-pointer w-full transition-all duration-200 ease-out ".concat(!isTopicsActive ? 'hover:bg-white hover:bg-opacity-20' : ''),
            style: {
              background: isTopicsActive ? 'rgba(191, 219, 254, 0.4)' : 'transparent',
              color: isTopicsActive ? 'var(--color-brand-blue-800)' : 'var(--color-warm-gray-700)'
            },
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
              className: "w-4 h-4 mr-3"
            }), "Topics"]
          })
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "px-3 py-1.5 mt-4",
          children: /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-xs font-semibold text-[var(--color-warm-gray-600)] uppercase tracking-wider",
            children: "Settings"
          })
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          children: /*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
            onClick: showLLMConfig,
            className: "flex items-center px-3 py-1.5 text-sm font-medium rounded-md transition-colors hover:cursor-pointer w-full transition-all duration-200 ease-out ".concat(!isLLMConfigActive ? 'hover:bg-white hover:bg-opacity-20' : ''),
            style: {
              background: isLLMConfigActive ? 'rgba(191, 219, 254, 0.4)' : 'transparent',
              color: isLLMConfigActive ? 'var(--color-brand-blue-800)' : 'var(--color-warm-gray-700)'
            },
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(KeyRound, {
              className: "w-4 h-4 mr-3"
            }), "LLM Keys"]
          })
        })]
      })
    })]
  });
}
;// ./node_modules/lucide-react/dist/esm/icons/chevron-right.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const chevron_right_iconNode = [["path", { d: "m9 18 6-6-6-6", key: "mthhwq" }]];
const ChevronRight = createLucideIcon("chevron-right", chevron_right_iconNode);


//# sourceMappingURL=chevron-right.js.map

;// ./src/components/LocalHeader.jsx



function LocalHeader(_ref) {
  var _ref$breadcrumbs = _ref.breadcrumbs,
    breadcrumbs = _ref$breadcrumbs === void 0 ? [] : _ref$breadcrumbs;
  return /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "h-1.5 bg-gradient-to-r from-yellow-400 via-yellow-500 to-amber-500"
    }), /*#__PURE__*/(0,jsx_runtime.jsxs)("header", {
      className: "bg-white px-6 py-3 flex items-center border-b border-[var(--color-warm-gray-100)] z-1",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "flex-1 flex items-center mr-6",
        children: breadcrumbs.length > 0 && /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "flex items-center gap-2 text-sm transition-opacity duration-200 mr-4",
          children: breadcrumbs.map(function (breadcrumb, index) {
            return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "flex items-center gap-2",
              children: [index > 0 && /*#__PURE__*/(0,jsx_runtime.jsx)(ChevronRight, {
                className: "w-3 h-3 text-[var(--color-warm-gray-400)]"
              }), breadcrumb.href || breadcrumb.onClick ? /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
                onClick: function onClick(e) {
                  if (breadcrumb.onClick) {
                    e.preventDefault();
                    breadcrumb.onClick();
                  } else if (breadcrumb.href) {
                    // Handle navigation if needed
                  }
                },
                className: "text-[var(--color-warm-gray-600)] hover:text-[var(--color-warm-gray-900)] font-medium cursor-pointer transition-colors duration-200 text-sm",
                style: {
                  fontSize: '0.875rem',
                  fontWeight: '500'
                },
                children: breadcrumb.label
              }) : /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                className: "text-[var(--color-warm-gray-900)] font-medium cursor-default text-sm",
                style: {
                  fontSize: '0.875rem',
                  fontWeight: '500'
                },
                children: breadcrumb.label
              })]
            }, index);
          })
        })
      }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "flex items-center gap-2",
        children: /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
          className: "text-sm text-[var(--color-warm-gray-600)] font-medium",
          children: "Local Development"
        })
      })]
    })]
  });
}
;// ./node_modules/@radix-ui/react-compose-refs/dist/index.mjs
// packages/react/compose-refs/src/compose-refs.tsx

function setRef(ref, value) {
  if (typeof ref === "function") {
    return ref(value);
  } else if (ref !== null && ref !== void 0) {
    ref.current = value;
  }
}
function composeRefs(...refs) {
  return (node) => {
    let hasCleanup = false;
    const cleanups = refs.map((ref) => {
      const cleanup = setRef(ref, node);
      if (!hasCleanup && typeof cleanup == "function") {
        hasCleanup = true;
      }
      return cleanup;
    });
    if (hasCleanup) {
      return () => {
        for (let i = 0; i < cleanups.length; i++) {
          const cleanup = cleanups[i];
          if (typeof cleanup == "function") {
            cleanup();
          } else {
            setRef(refs[i], null);
          }
        }
      };
    }
  };
}
function useComposedRefs(...refs) {
  return React.useCallback(composeRefs(...refs), refs);
}

//# sourceMappingURL=index.mjs.map

;// ./node_modules/@radix-ui/react-slot/dist/index.mjs
// src/slot.tsx



var REACT_LAZY_TYPE = Symbol.for("react.lazy");
var use = react_namespaceObject[" use ".trim().toString()];
function isPromiseLike(value) {
  return typeof value === "object" && value !== null && "then" in value;
}
function isLazyComponent(element) {
  return element != null && typeof element === "object" && "$$typeof" in element && element.$$typeof === REACT_LAZY_TYPE && "_payload" in element && isPromiseLike(element._payload);
}
// @__NO_SIDE_EFFECTS__
function createSlot(ownerName) {
  const SlotClone = /* @__PURE__ */ createSlotClone(ownerName);
  const Slot2 = react.forwardRef((props, forwardedRef) => {
    let { children, ...slotProps } = props;
    if (isLazyComponent(children) && typeof use === "function") {
      children = use(children._payload);
    }
    const childrenArray = react.Children.toArray(children);
    const slottable = childrenArray.find(isSlottable);
    if (slottable) {
      const newElement = slottable.props.children;
      const newChildren = childrenArray.map((child) => {
        if (child === slottable) {
          if (react.Children.count(newElement) > 1) return react.Children.only(null);
          return react.isValidElement(newElement) ? newElement.props.children : null;
        } else {
          return child;
        }
      });
      return /* @__PURE__ */ (0,jsx_runtime.jsx)(SlotClone, { ...slotProps, ref: forwardedRef, children: react.isValidElement(newElement) ? react.cloneElement(newElement, void 0, newChildren) : null });
    }
    return /* @__PURE__ */ (0,jsx_runtime.jsx)(SlotClone, { ...slotProps, ref: forwardedRef, children });
  });
  Slot2.displayName = `${ownerName}.Slot`;
  return Slot2;
}
var Slot = /* @__PURE__ */ createSlot("Slot");
// @__NO_SIDE_EFFECTS__
function createSlotClone(ownerName) {
  const SlotClone = react.forwardRef((props, forwardedRef) => {
    let { children, ...slotProps } = props;
    if (isLazyComponent(children) && typeof use === "function") {
      children = use(children._payload);
    }
    if (react.isValidElement(children)) {
      const childrenRef = getElementRef(children);
      const props2 = mergeProps(slotProps, children.props);
      if (children.type !== react.Fragment) {
        props2.ref = forwardedRef ? composeRefs(forwardedRef, childrenRef) : childrenRef;
      }
      return react.cloneElement(children, props2);
    }
    return react.Children.count(children) > 1 ? react.Children.only(null) : null;
  });
  SlotClone.displayName = `${ownerName}.SlotClone`;
  return SlotClone;
}
var SLOTTABLE_IDENTIFIER = Symbol("radix.slottable");
// @__NO_SIDE_EFFECTS__
function createSlottable(ownerName) {
  const Slottable2 = ({ children }) => {
    return /* @__PURE__ */ jsx(Fragment2, { children });
  };
  Slottable2.displayName = `${ownerName}.Slottable`;
  Slottable2.__radixId = SLOTTABLE_IDENTIFIER;
  return Slottable2;
}
var Slottable = /* @__PURE__ */ (/* unused pure expression or super */ null && (createSlottable("Slottable")));
function isSlottable(child) {
  return react.isValidElement(child) && typeof child.type === "function" && "__radixId" in child.type && child.type.__radixId === SLOTTABLE_IDENTIFIER;
}
function mergeProps(slotProps, childProps) {
  const overrideProps = { ...childProps };
  for (const propName in childProps) {
    const slotPropValue = slotProps[propName];
    const childPropValue = childProps[propName];
    const isHandler = /^on[A-Z]/.test(propName);
    if (isHandler) {
      if (slotPropValue && childPropValue) {
        overrideProps[propName] = (...args) => {
          const result = childPropValue(...args);
          slotPropValue(...args);
          return result;
        };
      } else if (slotPropValue) {
        overrideProps[propName] = slotPropValue;
      }
    } else if (propName === "style") {
      overrideProps[propName] = { ...slotPropValue, ...childPropValue };
    } else if (propName === "className") {
      overrideProps[propName] = [slotPropValue, childPropValue].filter(Boolean).join(" ");
    }
  }
  return { ...slotProps, ...overrideProps };
}
function getElementRef(element) {
  let getter = Object.getOwnPropertyDescriptor(element.props, "ref")?.get;
  let mayWarn = getter && "isReactWarning" in getter && getter.isReactWarning;
  if (mayWarn) {
    return element.ref;
  }
  getter = Object.getOwnPropertyDescriptor(element, "ref")?.get;
  mayWarn = getter && "isReactWarning" in getter && getter.isReactWarning;
  if (mayWarn) {
    return element.props.ref;
  }
  return element.props.ref || element.ref;
}

//# sourceMappingURL=index.mjs.map

;// ./node_modules/clsx/dist/clsx.mjs
function r(e){var t,f,n="";if("string"==typeof e||"number"==typeof e)n+=e;else if("object"==typeof e)if(Array.isArray(e)){var o=e.length;for(t=0;t<o;t++)e[t]&&(f=r(e[t]))&&(n&&(n+=" "),n+=f)}else for(f in e)e[f]&&(n&&(n+=" "),n+=f);return n}function clsx(){for(var e,t,f=0,n="",o=arguments.length;f<o;f++)(e=arguments[f])&&(t=r(e))&&(n&&(n+=" "),n+=t);return n}/* harmony default export */ const dist_clsx = ((/* unused pure expression or super */ null && (clsx)));
;// ./node_modules/class-variance-authority/dist/index.mjs
/**
 * Copyright 2022 Joe Bell. All rights reserved.
 *
 * This file is licensed to you under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with the
 * License. You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR REPRESENTATIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations under
 * the License.
 */ 
const falsyToString = (value)=>typeof value === "boolean" ? `${value}` : value === 0 ? "0" : value;
const cx = clsx;
const cva = (base, config)=>(props)=>{
        var _config_compoundVariants;
        if ((config === null || config === void 0 ? void 0 : config.variants) == null) return cx(base, props === null || props === void 0 ? void 0 : props.class, props === null || props === void 0 ? void 0 : props.className);
        const { variants, defaultVariants } = config;
        const getVariantClassNames = Object.keys(variants).map((variant)=>{
            const variantProp = props === null || props === void 0 ? void 0 : props[variant];
            const defaultVariantProp = defaultVariants === null || defaultVariants === void 0 ? void 0 : defaultVariants[variant];
            if (variantProp === null) return null;
            const variantKey = falsyToString(variantProp) || falsyToString(defaultVariantProp);
            return variants[variant][variantKey];
        });
        const propsWithoutUndefined = props && Object.entries(props).reduce((acc, param)=>{
            let [key, value] = param;
            if (value === undefined) {
                return acc;
            }
            acc[key] = value;
            return acc;
        }, {});
        const getCompoundVariantClassNames = config === null || config === void 0 ? void 0 : (_config_compoundVariants = config.compoundVariants) === null || _config_compoundVariants === void 0 ? void 0 : _config_compoundVariants.reduce((acc, param)=>{
            let { class: cvClass, className: cvClassName, ...compoundVariantOptions } = param;
            return Object.entries(compoundVariantOptions).every((param)=>{
                let [key, value] = param;
                return Array.isArray(value) ? value.includes({
                    ...defaultVariants,
                    ...propsWithoutUndefined
                }[key]) : ({
                    ...defaultVariants,
                    ...propsWithoutUndefined
                })[key] === value;
            }) ? [
                ...acc,
                cvClass,
                cvClassName
            ] : acc;
        }, []);
        return cx(base, getVariantClassNames, getCompoundVariantClassNames, props === null || props === void 0 ? void 0 : props.class, props === null || props === void 0 ? void 0 : props.className);
    };


;// ./node_modules/tailwind-merge/dist/bundle-mjs.mjs
const CLASS_PART_SEPARATOR = '-';
const createClassGroupUtils = config => {
  const classMap = createClassMap(config);
  const {
    conflictingClassGroups,
    conflictingClassGroupModifiers
  } = config;
  const getClassGroupId = className => {
    const classParts = className.split(CLASS_PART_SEPARATOR);
    // Classes like `-inset-1` produce an empty string as first classPart. We assume that classes for negative values are used correctly and remove it from classParts.
    if (classParts[0] === '' && classParts.length !== 1) {
      classParts.shift();
    }
    return getGroupRecursive(classParts, classMap) || getGroupIdForArbitraryProperty(className);
  };
  const getConflictingClassGroupIds = (classGroupId, hasPostfixModifier) => {
    const conflicts = conflictingClassGroups[classGroupId] || [];
    if (hasPostfixModifier && conflictingClassGroupModifiers[classGroupId]) {
      return [...conflicts, ...conflictingClassGroupModifiers[classGroupId]];
    }
    return conflicts;
  };
  return {
    getClassGroupId,
    getConflictingClassGroupIds
  };
};
const getGroupRecursive = (classParts, classPartObject) => {
  if (classParts.length === 0) {
    return classPartObject.classGroupId;
  }
  const currentClassPart = classParts[0];
  const nextClassPartObject = classPartObject.nextPart.get(currentClassPart);
  const classGroupFromNextClassPart = nextClassPartObject ? getGroupRecursive(classParts.slice(1), nextClassPartObject) : undefined;
  if (classGroupFromNextClassPart) {
    return classGroupFromNextClassPart;
  }
  if (classPartObject.validators.length === 0) {
    return undefined;
  }
  const classRest = classParts.join(CLASS_PART_SEPARATOR);
  return classPartObject.validators.find(({
    validator
  }) => validator(classRest))?.classGroupId;
};
const arbitraryPropertyRegex = /^\[(.+)\]$/;
const getGroupIdForArbitraryProperty = className => {
  if (arbitraryPropertyRegex.test(className)) {
    const arbitraryPropertyClassName = arbitraryPropertyRegex.exec(className)[1];
    const property = arbitraryPropertyClassName?.substring(0, arbitraryPropertyClassName.indexOf(':'));
    if (property) {
      // I use two dots here because one dot is used as prefix for class groups in plugins
      return 'arbitrary..' + property;
    }
  }
};
/**
 * Exported for testing only
 */
const createClassMap = config => {
  const {
    theme,
    prefix
  } = config;
  const classMap = {
    nextPart: new Map(),
    validators: []
  };
  const prefixedClassGroupEntries = getPrefixedClassGroupEntries(Object.entries(config.classGroups), prefix);
  prefixedClassGroupEntries.forEach(([classGroupId, classGroup]) => {
    processClassesRecursively(classGroup, classMap, classGroupId, theme);
  });
  return classMap;
};
const processClassesRecursively = (classGroup, classPartObject, classGroupId, theme) => {
  classGroup.forEach(classDefinition => {
    if (typeof classDefinition === 'string') {
      const classPartObjectToEdit = classDefinition === '' ? classPartObject : getPart(classPartObject, classDefinition);
      classPartObjectToEdit.classGroupId = classGroupId;
      return;
    }
    if (typeof classDefinition === 'function') {
      if (isThemeGetter(classDefinition)) {
        processClassesRecursively(classDefinition(theme), classPartObject, classGroupId, theme);
        return;
      }
      classPartObject.validators.push({
        validator: classDefinition,
        classGroupId
      });
      return;
    }
    Object.entries(classDefinition).forEach(([key, classGroup]) => {
      processClassesRecursively(classGroup, getPart(classPartObject, key), classGroupId, theme);
    });
  });
};
const getPart = (classPartObject, path) => {
  let currentClassPartObject = classPartObject;
  path.split(CLASS_PART_SEPARATOR).forEach(pathPart => {
    if (!currentClassPartObject.nextPart.has(pathPart)) {
      currentClassPartObject.nextPart.set(pathPart, {
        nextPart: new Map(),
        validators: []
      });
    }
    currentClassPartObject = currentClassPartObject.nextPart.get(pathPart);
  });
  return currentClassPartObject;
};
const isThemeGetter = func => func.isThemeGetter;
const getPrefixedClassGroupEntries = (classGroupEntries, prefix) => {
  if (!prefix) {
    return classGroupEntries;
  }
  return classGroupEntries.map(([classGroupId, classGroup]) => {
    const prefixedClassGroup = classGroup.map(classDefinition => {
      if (typeof classDefinition === 'string') {
        return prefix + classDefinition;
      }
      if (typeof classDefinition === 'object') {
        return Object.fromEntries(Object.entries(classDefinition).map(([key, value]) => [prefix + key, value]));
      }
      return classDefinition;
    });
    return [classGroupId, prefixedClassGroup];
  });
};

// LRU cache inspired from hashlru (https://github.com/dominictarr/hashlru/blob/v1.0.4/index.js) but object replaced with Map to improve performance
const createLruCache = maxCacheSize => {
  if (maxCacheSize < 1) {
    return {
      get: () => undefined,
      set: () => {}
    };
  }
  let cacheSize = 0;
  let cache = new Map();
  let previousCache = new Map();
  const update = (key, value) => {
    cache.set(key, value);
    cacheSize++;
    if (cacheSize > maxCacheSize) {
      cacheSize = 0;
      previousCache = cache;
      cache = new Map();
    }
  };
  return {
    get(key) {
      let value = cache.get(key);
      if (value !== undefined) {
        return value;
      }
      if ((value = previousCache.get(key)) !== undefined) {
        update(key, value);
        return value;
      }
    },
    set(key, value) {
      if (cache.has(key)) {
        cache.set(key, value);
      } else {
        update(key, value);
      }
    }
  };
};
const IMPORTANT_MODIFIER = '!';
const createParseClassName = config => {
  const {
    separator,
    experimentalParseClassName
  } = config;
  const isSeparatorSingleCharacter = separator.length === 1;
  const firstSeparatorCharacter = separator[0];
  const separatorLength = separator.length;
  // parseClassName inspired by https://github.com/tailwindlabs/tailwindcss/blob/v3.2.2/src/util/splitAtTopLevelOnly.js
  const parseClassName = className => {
    const modifiers = [];
    let bracketDepth = 0;
    let modifierStart = 0;
    let postfixModifierPosition;
    for (let index = 0; index < className.length; index++) {
      let currentCharacter = className[index];
      if (bracketDepth === 0) {
        if (currentCharacter === firstSeparatorCharacter && (isSeparatorSingleCharacter || className.slice(index, index + separatorLength) === separator)) {
          modifiers.push(className.slice(modifierStart, index));
          modifierStart = index + separatorLength;
          continue;
        }
        if (currentCharacter === '/') {
          postfixModifierPosition = index;
          continue;
        }
      }
      if (currentCharacter === '[') {
        bracketDepth++;
      } else if (currentCharacter === ']') {
        bracketDepth--;
      }
    }
    const baseClassNameWithImportantModifier = modifiers.length === 0 ? className : className.substring(modifierStart);
    const hasImportantModifier = baseClassNameWithImportantModifier.startsWith(IMPORTANT_MODIFIER);
    const baseClassName = hasImportantModifier ? baseClassNameWithImportantModifier.substring(1) : baseClassNameWithImportantModifier;
    const maybePostfixModifierPosition = postfixModifierPosition && postfixModifierPosition > modifierStart ? postfixModifierPosition - modifierStart : undefined;
    return {
      modifiers,
      hasImportantModifier,
      baseClassName,
      maybePostfixModifierPosition
    };
  };
  if (experimentalParseClassName) {
    return className => experimentalParseClassName({
      className,
      parseClassName
    });
  }
  return parseClassName;
};
/**
 * Sorts modifiers according to following schema:
 * - Predefined modifiers are sorted alphabetically
 * - When an arbitrary variant appears, it must be preserved which modifiers are before and after it
 */
const sortModifiers = modifiers => {
  if (modifiers.length <= 1) {
    return modifiers;
  }
  const sortedModifiers = [];
  let unsortedModifiers = [];
  modifiers.forEach(modifier => {
    const isArbitraryVariant = modifier[0] === '[';
    if (isArbitraryVariant) {
      sortedModifiers.push(...unsortedModifiers.sort(), modifier);
      unsortedModifiers = [];
    } else {
      unsortedModifiers.push(modifier);
    }
  });
  sortedModifiers.push(...unsortedModifiers.sort());
  return sortedModifiers;
};
const createConfigUtils = config => ({
  cache: createLruCache(config.cacheSize),
  parseClassName: createParseClassName(config),
  ...createClassGroupUtils(config)
});
const SPLIT_CLASSES_REGEX = /\s+/;
const mergeClassList = (classList, configUtils) => {
  const {
    parseClassName,
    getClassGroupId,
    getConflictingClassGroupIds
  } = configUtils;
  /**
   * Set of classGroupIds in following format:
   * `{importantModifier}{variantModifiers}{classGroupId}`
   * @example 'float'
   * @example 'hover:focus:bg-color'
   * @example 'md:!pr'
   */
  const classGroupsInConflict = [];
  const classNames = classList.trim().split(SPLIT_CLASSES_REGEX);
  let result = '';
  for (let index = classNames.length - 1; index >= 0; index -= 1) {
    const originalClassName = classNames[index];
    const {
      modifiers,
      hasImportantModifier,
      baseClassName,
      maybePostfixModifierPosition
    } = parseClassName(originalClassName);
    let hasPostfixModifier = Boolean(maybePostfixModifierPosition);
    let classGroupId = getClassGroupId(hasPostfixModifier ? baseClassName.substring(0, maybePostfixModifierPosition) : baseClassName);
    if (!classGroupId) {
      if (!hasPostfixModifier) {
        // Not a Tailwind class
        result = originalClassName + (result.length > 0 ? ' ' + result : result);
        continue;
      }
      classGroupId = getClassGroupId(baseClassName);
      if (!classGroupId) {
        // Not a Tailwind class
        result = originalClassName + (result.length > 0 ? ' ' + result : result);
        continue;
      }
      hasPostfixModifier = false;
    }
    const variantModifier = sortModifiers(modifiers).join(':');
    const modifierId = hasImportantModifier ? variantModifier + IMPORTANT_MODIFIER : variantModifier;
    const classId = modifierId + classGroupId;
    if (classGroupsInConflict.includes(classId)) {
      // Tailwind class omitted due to conflict
      continue;
    }
    classGroupsInConflict.push(classId);
    const conflictGroups = getConflictingClassGroupIds(classGroupId, hasPostfixModifier);
    for (let i = 0; i < conflictGroups.length; ++i) {
      const group = conflictGroups[i];
      classGroupsInConflict.push(modifierId + group);
    }
    // Tailwind class not in conflict
    result = originalClassName + (result.length > 0 ? ' ' + result : result);
  }
  return result;
};

/**
 * The code in this file is copied from https://github.com/lukeed/clsx and modified to suit the needs of tailwind-merge better.
 *
 * Specifically:
 * - Runtime code from https://github.com/lukeed/clsx/blob/v1.2.1/src/index.js
 * - TypeScript types from https://github.com/lukeed/clsx/blob/v1.2.1/clsx.d.ts
 *
 * Original code has MIT license: Copyright (c) Luke Edwards <luke.edwards05@gmail.com> (lukeed.com)
 */
function twJoin() {
  let index = 0;
  let argument;
  let resolvedValue;
  let string = '';
  while (index < arguments.length) {
    if (argument = arguments[index++]) {
      if (resolvedValue = toValue(argument)) {
        string && (string += ' ');
        string += resolvedValue;
      }
    }
  }
  return string;
}
const toValue = mix => {
  if (typeof mix === 'string') {
    return mix;
  }
  let resolvedValue;
  let string = '';
  for (let k = 0; k < mix.length; k++) {
    if (mix[k]) {
      if (resolvedValue = toValue(mix[k])) {
        string && (string += ' ');
        string += resolvedValue;
      }
    }
  }
  return string;
};
function createTailwindMerge(createConfigFirst, ...createConfigRest) {
  let configUtils;
  let cacheGet;
  let cacheSet;
  let functionToCall = initTailwindMerge;
  function initTailwindMerge(classList) {
    const config = createConfigRest.reduce((previousConfig, createConfigCurrent) => createConfigCurrent(previousConfig), createConfigFirst());
    configUtils = createConfigUtils(config);
    cacheGet = configUtils.cache.get;
    cacheSet = configUtils.cache.set;
    functionToCall = tailwindMerge;
    return tailwindMerge(classList);
  }
  function tailwindMerge(classList) {
    const cachedResult = cacheGet(classList);
    if (cachedResult) {
      return cachedResult;
    }
    const result = mergeClassList(classList, configUtils);
    cacheSet(classList, result);
    return result;
  }
  return function callTailwindMerge() {
    return functionToCall(twJoin.apply(null, arguments));
  };
}
const fromTheme = key => {
  const themeGetter = theme => theme[key] || [];
  themeGetter.isThemeGetter = true;
  return themeGetter;
};
const arbitraryValueRegex = /^\[(?:([a-z-]+):)?(.+)\]$/i;
const fractionRegex = /^\d+\/\d+$/;
const stringLengths = /*#__PURE__*/new Set(['px', 'full', 'screen']);
const tshirtUnitRegex = /^(\d+(\.\d+)?)?(xs|sm|md|lg|xl)$/;
const lengthUnitRegex = /\d+(%|px|r?em|[sdl]?v([hwib]|min|max)|pt|pc|in|cm|mm|cap|ch|ex|r?lh|cq(w|h|i|b|min|max))|\b(calc|min|max|clamp)\(.+\)|^0$/;
const colorFunctionRegex = /^(rgba?|hsla?|hwb|(ok)?(lab|lch))\(.+\)$/;
// Shadow always begins with x and y offset separated by underscore optionally prepended by inset
const shadowRegex = /^(inset_)?-?((\d+)?\.?(\d+)[a-z]+|0)_-?((\d+)?\.?(\d+)[a-z]+|0)/;
const imageRegex = /^(url|image|image-set|cross-fade|element|(repeating-)?(linear|radial|conic)-gradient)\(.+\)$/;
const isLength = value => isNumber(value) || stringLengths.has(value) || fractionRegex.test(value);
const isArbitraryLength = value => getIsArbitraryValue(value, 'length', isLengthOnly);
const isNumber = value => Boolean(value) && !Number.isNaN(Number(value));
const isArbitraryNumber = value => getIsArbitraryValue(value, 'number', isNumber);
const isInteger = value => Boolean(value) && Number.isInteger(Number(value));
const isPercent = value => value.endsWith('%') && isNumber(value.slice(0, -1));
const isArbitraryValue = value => arbitraryValueRegex.test(value);
const isTshirtSize = value => tshirtUnitRegex.test(value);
const sizeLabels = /*#__PURE__*/new Set(['length', 'size', 'percentage']);
const isArbitrarySize = value => getIsArbitraryValue(value, sizeLabels, isNever);
const isArbitraryPosition = value => getIsArbitraryValue(value, 'position', isNever);
const imageLabels = /*#__PURE__*/new Set(['image', 'url']);
const isArbitraryImage = value => getIsArbitraryValue(value, imageLabels, isImage);
const isArbitraryShadow = value => getIsArbitraryValue(value, '', isShadow);
const isAny = () => true;
const getIsArbitraryValue = (value, label, testValue) => {
  const result = arbitraryValueRegex.exec(value);
  if (result) {
    if (result[1]) {
      return typeof label === 'string' ? result[1] === label : label.has(result[1]);
    }
    return testValue(result[2]);
  }
  return false;
};
const isLengthOnly = value =>
// `colorFunctionRegex` check is necessary because color functions can have percentages in them which which would be incorrectly classified as lengths.
// For example, `hsl(0 0% 0%)` would be classified as a length without this check.
// I could also use lookbehind assertion in `lengthUnitRegex` but that isn't supported widely enough.
lengthUnitRegex.test(value) && !colorFunctionRegex.test(value);
const isNever = () => false;
const isShadow = value => shadowRegex.test(value);
const isImage = value => imageRegex.test(value);
const validators = /*#__PURE__*/Object.defineProperty({
  __proto__: null,
  isAny,
  isArbitraryImage,
  isArbitraryLength,
  isArbitraryNumber,
  isArbitraryPosition,
  isArbitraryShadow,
  isArbitrarySize,
  isArbitraryValue,
  isInteger,
  isLength,
  isNumber,
  isPercent,
  isTshirtSize
}, Symbol.toStringTag, {
  value: 'Module'
});
const getDefaultConfig = () => {
  const colors = fromTheme('colors');
  const spacing = fromTheme('spacing');
  const blur = fromTheme('blur');
  const brightness = fromTheme('brightness');
  const borderColor = fromTheme('borderColor');
  const borderRadius = fromTheme('borderRadius');
  const borderSpacing = fromTheme('borderSpacing');
  const borderWidth = fromTheme('borderWidth');
  const contrast = fromTheme('contrast');
  const grayscale = fromTheme('grayscale');
  const hueRotate = fromTheme('hueRotate');
  const invert = fromTheme('invert');
  const gap = fromTheme('gap');
  const gradientColorStops = fromTheme('gradientColorStops');
  const gradientColorStopPositions = fromTheme('gradientColorStopPositions');
  const inset = fromTheme('inset');
  const margin = fromTheme('margin');
  const opacity = fromTheme('opacity');
  const padding = fromTheme('padding');
  const saturate = fromTheme('saturate');
  const scale = fromTheme('scale');
  const sepia = fromTheme('sepia');
  const skew = fromTheme('skew');
  const space = fromTheme('space');
  const translate = fromTheme('translate');
  const getOverscroll = () => ['auto', 'contain', 'none'];
  const getOverflow = () => ['auto', 'hidden', 'clip', 'visible', 'scroll'];
  const getSpacingWithAutoAndArbitrary = () => ['auto', isArbitraryValue, spacing];
  const getSpacingWithArbitrary = () => [isArbitraryValue, spacing];
  const getLengthWithEmptyAndArbitrary = () => ['', isLength, isArbitraryLength];
  const getNumberWithAutoAndArbitrary = () => ['auto', isNumber, isArbitraryValue];
  const getPositions = () => ['bottom', 'center', 'left', 'left-bottom', 'left-top', 'right', 'right-bottom', 'right-top', 'top'];
  const getLineStyles = () => ['solid', 'dashed', 'dotted', 'double', 'none'];
  const getBlendModes = () => ['normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten', 'color-dodge', 'color-burn', 'hard-light', 'soft-light', 'difference', 'exclusion', 'hue', 'saturation', 'color', 'luminosity'];
  const getAlign = () => ['start', 'end', 'center', 'between', 'around', 'evenly', 'stretch'];
  const getZeroAndEmpty = () => ['', '0', isArbitraryValue];
  const getBreaks = () => ['auto', 'avoid', 'all', 'avoid-page', 'page', 'left', 'right', 'column'];
  const getNumberAndArbitrary = () => [isNumber, isArbitraryValue];
  return {
    cacheSize: 500,
    separator: ':',
    theme: {
      colors: [isAny],
      spacing: [isLength, isArbitraryLength],
      blur: ['none', '', isTshirtSize, isArbitraryValue],
      brightness: getNumberAndArbitrary(),
      borderColor: [colors],
      borderRadius: ['none', '', 'full', isTshirtSize, isArbitraryValue],
      borderSpacing: getSpacingWithArbitrary(),
      borderWidth: getLengthWithEmptyAndArbitrary(),
      contrast: getNumberAndArbitrary(),
      grayscale: getZeroAndEmpty(),
      hueRotate: getNumberAndArbitrary(),
      invert: getZeroAndEmpty(),
      gap: getSpacingWithArbitrary(),
      gradientColorStops: [colors],
      gradientColorStopPositions: [isPercent, isArbitraryLength],
      inset: getSpacingWithAutoAndArbitrary(),
      margin: getSpacingWithAutoAndArbitrary(),
      opacity: getNumberAndArbitrary(),
      padding: getSpacingWithArbitrary(),
      saturate: getNumberAndArbitrary(),
      scale: getNumberAndArbitrary(),
      sepia: getZeroAndEmpty(),
      skew: getNumberAndArbitrary(),
      space: getSpacingWithArbitrary(),
      translate: getSpacingWithArbitrary()
    },
    classGroups: {
      // Layout
      /**
       * Aspect Ratio
       * @see https://tailwindcss.com/docs/aspect-ratio
       */
      aspect: [{
        aspect: ['auto', 'square', 'video', isArbitraryValue]
      }],
      /**
       * Container
       * @see https://tailwindcss.com/docs/container
       */
      container: ['container'],
      /**
       * Columns
       * @see https://tailwindcss.com/docs/columns
       */
      columns: [{
        columns: [isTshirtSize]
      }],
      /**
       * Break After
       * @see https://tailwindcss.com/docs/break-after
       */
      'break-after': [{
        'break-after': getBreaks()
      }],
      /**
       * Break Before
       * @see https://tailwindcss.com/docs/break-before
       */
      'break-before': [{
        'break-before': getBreaks()
      }],
      /**
       * Break Inside
       * @see https://tailwindcss.com/docs/break-inside
       */
      'break-inside': [{
        'break-inside': ['auto', 'avoid', 'avoid-page', 'avoid-column']
      }],
      /**
       * Box Decoration Break
       * @see https://tailwindcss.com/docs/box-decoration-break
       */
      'box-decoration': [{
        'box-decoration': ['slice', 'clone']
      }],
      /**
       * Box Sizing
       * @see https://tailwindcss.com/docs/box-sizing
       */
      box: [{
        box: ['border', 'content']
      }],
      /**
       * Display
       * @see https://tailwindcss.com/docs/display
       */
      display: ['block', 'inline-block', 'inline', 'flex', 'inline-flex', 'table', 'inline-table', 'table-caption', 'table-cell', 'table-column', 'table-column-group', 'table-footer-group', 'table-header-group', 'table-row-group', 'table-row', 'flow-root', 'grid', 'inline-grid', 'contents', 'list-item', 'hidden'],
      /**
       * Floats
       * @see https://tailwindcss.com/docs/float
       */
      float: [{
        float: ['right', 'left', 'none', 'start', 'end']
      }],
      /**
       * Clear
       * @see https://tailwindcss.com/docs/clear
       */
      clear: [{
        clear: ['left', 'right', 'both', 'none', 'start', 'end']
      }],
      /**
       * Isolation
       * @see https://tailwindcss.com/docs/isolation
       */
      isolation: ['isolate', 'isolation-auto'],
      /**
       * Object Fit
       * @see https://tailwindcss.com/docs/object-fit
       */
      'object-fit': [{
        object: ['contain', 'cover', 'fill', 'none', 'scale-down']
      }],
      /**
       * Object Position
       * @see https://tailwindcss.com/docs/object-position
       */
      'object-position': [{
        object: [...getPositions(), isArbitraryValue]
      }],
      /**
       * Overflow
       * @see https://tailwindcss.com/docs/overflow
       */
      overflow: [{
        overflow: getOverflow()
      }],
      /**
       * Overflow X
       * @see https://tailwindcss.com/docs/overflow
       */
      'overflow-x': [{
        'overflow-x': getOverflow()
      }],
      /**
       * Overflow Y
       * @see https://tailwindcss.com/docs/overflow
       */
      'overflow-y': [{
        'overflow-y': getOverflow()
      }],
      /**
       * Overscroll Behavior
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      overscroll: [{
        overscroll: getOverscroll()
      }],
      /**
       * Overscroll Behavior X
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      'overscroll-x': [{
        'overscroll-x': getOverscroll()
      }],
      /**
       * Overscroll Behavior Y
       * @see https://tailwindcss.com/docs/overscroll-behavior
       */
      'overscroll-y': [{
        'overscroll-y': getOverscroll()
      }],
      /**
       * Position
       * @see https://tailwindcss.com/docs/position
       */
      position: ['static', 'fixed', 'absolute', 'relative', 'sticky'],
      /**
       * Top / Right / Bottom / Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      inset: [{
        inset: [inset]
      }],
      /**
       * Right / Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      'inset-x': [{
        'inset-x': [inset]
      }],
      /**
       * Top / Bottom
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      'inset-y': [{
        'inset-y': [inset]
      }],
      /**
       * Start
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      start: [{
        start: [inset]
      }],
      /**
       * End
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      end: [{
        end: [inset]
      }],
      /**
       * Top
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      top: [{
        top: [inset]
      }],
      /**
       * Right
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      right: [{
        right: [inset]
      }],
      /**
       * Bottom
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      bottom: [{
        bottom: [inset]
      }],
      /**
       * Left
       * @see https://tailwindcss.com/docs/top-right-bottom-left
       */
      left: [{
        left: [inset]
      }],
      /**
       * Visibility
       * @see https://tailwindcss.com/docs/visibility
       */
      visibility: ['visible', 'invisible', 'collapse'],
      /**
       * Z-Index
       * @see https://tailwindcss.com/docs/z-index
       */
      z: [{
        z: ['auto', isInteger, isArbitraryValue]
      }],
      // Flexbox and Grid
      /**
       * Flex Basis
       * @see https://tailwindcss.com/docs/flex-basis
       */
      basis: [{
        basis: getSpacingWithAutoAndArbitrary()
      }],
      /**
       * Flex Direction
       * @see https://tailwindcss.com/docs/flex-direction
       */
      'flex-direction': [{
        flex: ['row', 'row-reverse', 'col', 'col-reverse']
      }],
      /**
       * Flex Wrap
       * @see https://tailwindcss.com/docs/flex-wrap
       */
      'flex-wrap': [{
        flex: ['wrap', 'wrap-reverse', 'nowrap']
      }],
      /**
       * Flex
       * @see https://tailwindcss.com/docs/flex
       */
      flex: [{
        flex: ['1', 'auto', 'initial', 'none', isArbitraryValue]
      }],
      /**
       * Flex Grow
       * @see https://tailwindcss.com/docs/flex-grow
       */
      grow: [{
        grow: getZeroAndEmpty()
      }],
      /**
       * Flex Shrink
       * @see https://tailwindcss.com/docs/flex-shrink
       */
      shrink: [{
        shrink: getZeroAndEmpty()
      }],
      /**
       * Order
       * @see https://tailwindcss.com/docs/order
       */
      order: [{
        order: ['first', 'last', 'none', isInteger, isArbitraryValue]
      }],
      /**
       * Grid Template Columns
       * @see https://tailwindcss.com/docs/grid-template-columns
       */
      'grid-cols': [{
        'grid-cols': [isAny]
      }],
      /**
       * Grid Column Start / End
       * @see https://tailwindcss.com/docs/grid-column
       */
      'col-start-end': [{
        col: ['auto', {
          span: ['full', isInteger, isArbitraryValue]
        }, isArbitraryValue]
      }],
      /**
       * Grid Column Start
       * @see https://tailwindcss.com/docs/grid-column
       */
      'col-start': [{
        'col-start': getNumberWithAutoAndArbitrary()
      }],
      /**
       * Grid Column End
       * @see https://tailwindcss.com/docs/grid-column
       */
      'col-end': [{
        'col-end': getNumberWithAutoAndArbitrary()
      }],
      /**
       * Grid Template Rows
       * @see https://tailwindcss.com/docs/grid-template-rows
       */
      'grid-rows': [{
        'grid-rows': [isAny]
      }],
      /**
       * Grid Row Start / End
       * @see https://tailwindcss.com/docs/grid-row
       */
      'row-start-end': [{
        row: ['auto', {
          span: [isInteger, isArbitraryValue]
        }, isArbitraryValue]
      }],
      /**
       * Grid Row Start
       * @see https://tailwindcss.com/docs/grid-row
       */
      'row-start': [{
        'row-start': getNumberWithAutoAndArbitrary()
      }],
      /**
       * Grid Row End
       * @see https://tailwindcss.com/docs/grid-row
       */
      'row-end': [{
        'row-end': getNumberWithAutoAndArbitrary()
      }],
      /**
       * Grid Auto Flow
       * @see https://tailwindcss.com/docs/grid-auto-flow
       */
      'grid-flow': [{
        'grid-flow': ['row', 'col', 'dense', 'row-dense', 'col-dense']
      }],
      /**
       * Grid Auto Columns
       * @see https://tailwindcss.com/docs/grid-auto-columns
       */
      'auto-cols': [{
        'auto-cols': ['auto', 'min', 'max', 'fr', isArbitraryValue]
      }],
      /**
       * Grid Auto Rows
       * @see https://tailwindcss.com/docs/grid-auto-rows
       */
      'auto-rows': [{
        'auto-rows': ['auto', 'min', 'max', 'fr', isArbitraryValue]
      }],
      /**
       * Gap
       * @see https://tailwindcss.com/docs/gap
       */
      gap: [{
        gap: [gap]
      }],
      /**
       * Gap X
       * @see https://tailwindcss.com/docs/gap
       */
      'gap-x': [{
        'gap-x': [gap]
      }],
      /**
       * Gap Y
       * @see https://tailwindcss.com/docs/gap
       */
      'gap-y': [{
        'gap-y': [gap]
      }],
      /**
       * Justify Content
       * @see https://tailwindcss.com/docs/justify-content
       */
      'justify-content': [{
        justify: ['normal', ...getAlign()]
      }],
      /**
       * Justify Items
       * @see https://tailwindcss.com/docs/justify-items
       */
      'justify-items': [{
        'justify-items': ['start', 'end', 'center', 'stretch']
      }],
      /**
       * Justify Self
       * @see https://tailwindcss.com/docs/justify-self
       */
      'justify-self': [{
        'justify-self': ['auto', 'start', 'end', 'center', 'stretch']
      }],
      /**
       * Align Content
       * @see https://tailwindcss.com/docs/align-content
       */
      'align-content': [{
        content: ['normal', ...getAlign(), 'baseline']
      }],
      /**
       * Align Items
       * @see https://tailwindcss.com/docs/align-items
       */
      'align-items': [{
        items: ['start', 'end', 'center', 'baseline', 'stretch']
      }],
      /**
       * Align Self
       * @see https://tailwindcss.com/docs/align-self
       */
      'align-self': [{
        self: ['auto', 'start', 'end', 'center', 'stretch', 'baseline']
      }],
      /**
       * Place Content
       * @see https://tailwindcss.com/docs/place-content
       */
      'place-content': [{
        'place-content': [...getAlign(), 'baseline']
      }],
      /**
       * Place Items
       * @see https://tailwindcss.com/docs/place-items
       */
      'place-items': [{
        'place-items': ['start', 'end', 'center', 'baseline', 'stretch']
      }],
      /**
       * Place Self
       * @see https://tailwindcss.com/docs/place-self
       */
      'place-self': [{
        'place-self': ['auto', 'start', 'end', 'center', 'stretch']
      }],
      // Spacing
      /**
       * Padding
       * @see https://tailwindcss.com/docs/padding
       */
      p: [{
        p: [padding]
      }],
      /**
       * Padding X
       * @see https://tailwindcss.com/docs/padding
       */
      px: [{
        px: [padding]
      }],
      /**
       * Padding Y
       * @see https://tailwindcss.com/docs/padding
       */
      py: [{
        py: [padding]
      }],
      /**
       * Padding Start
       * @see https://tailwindcss.com/docs/padding
       */
      ps: [{
        ps: [padding]
      }],
      /**
       * Padding End
       * @see https://tailwindcss.com/docs/padding
       */
      pe: [{
        pe: [padding]
      }],
      /**
       * Padding Top
       * @see https://tailwindcss.com/docs/padding
       */
      pt: [{
        pt: [padding]
      }],
      /**
       * Padding Right
       * @see https://tailwindcss.com/docs/padding
       */
      pr: [{
        pr: [padding]
      }],
      /**
       * Padding Bottom
       * @see https://tailwindcss.com/docs/padding
       */
      pb: [{
        pb: [padding]
      }],
      /**
       * Padding Left
       * @see https://tailwindcss.com/docs/padding
       */
      pl: [{
        pl: [padding]
      }],
      /**
       * Margin
       * @see https://tailwindcss.com/docs/margin
       */
      m: [{
        m: [margin]
      }],
      /**
       * Margin X
       * @see https://tailwindcss.com/docs/margin
       */
      mx: [{
        mx: [margin]
      }],
      /**
       * Margin Y
       * @see https://tailwindcss.com/docs/margin
       */
      my: [{
        my: [margin]
      }],
      /**
       * Margin Start
       * @see https://tailwindcss.com/docs/margin
       */
      ms: [{
        ms: [margin]
      }],
      /**
       * Margin End
       * @see https://tailwindcss.com/docs/margin
       */
      me: [{
        me: [margin]
      }],
      /**
       * Margin Top
       * @see https://tailwindcss.com/docs/margin
       */
      mt: [{
        mt: [margin]
      }],
      /**
       * Margin Right
       * @see https://tailwindcss.com/docs/margin
       */
      mr: [{
        mr: [margin]
      }],
      /**
       * Margin Bottom
       * @see https://tailwindcss.com/docs/margin
       */
      mb: [{
        mb: [margin]
      }],
      /**
       * Margin Left
       * @see https://tailwindcss.com/docs/margin
       */
      ml: [{
        ml: [margin]
      }],
      /**
       * Space Between X
       * @see https://tailwindcss.com/docs/space
       */
      'space-x': [{
        'space-x': [space]
      }],
      /**
       * Space Between X Reverse
       * @see https://tailwindcss.com/docs/space
       */
      'space-x-reverse': ['space-x-reverse'],
      /**
       * Space Between Y
       * @see https://tailwindcss.com/docs/space
       */
      'space-y': [{
        'space-y': [space]
      }],
      /**
       * Space Between Y Reverse
       * @see https://tailwindcss.com/docs/space
       */
      'space-y-reverse': ['space-y-reverse'],
      // Sizing
      /**
       * Width
       * @see https://tailwindcss.com/docs/width
       */
      w: [{
        w: ['auto', 'min', 'max', 'fit', 'svw', 'lvw', 'dvw', isArbitraryValue, spacing]
      }],
      /**
       * Min-Width
       * @see https://tailwindcss.com/docs/min-width
       */
      'min-w': [{
        'min-w': [isArbitraryValue, spacing, 'min', 'max', 'fit']
      }],
      /**
       * Max-Width
       * @see https://tailwindcss.com/docs/max-width
       */
      'max-w': [{
        'max-w': [isArbitraryValue, spacing, 'none', 'full', 'min', 'max', 'fit', 'prose', {
          screen: [isTshirtSize]
        }, isTshirtSize]
      }],
      /**
       * Height
       * @see https://tailwindcss.com/docs/height
       */
      h: [{
        h: [isArbitraryValue, spacing, 'auto', 'min', 'max', 'fit', 'svh', 'lvh', 'dvh']
      }],
      /**
       * Min-Height
       * @see https://tailwindcss.com/docs/min-height
       */
      'min-h': [{
        'min-h': [isArbitraryValue, spacing, 'min', 'max', 'fit', 'svh', 'lvh', 'dvh']
      }],
      /**
       * Max-Height
       * @see https://tailwindcss.com/docs/max-height
       */
      'max-h': [{
        'max-h': [isArbitraryValue, spacing, 'min', 'max', 'fit', 'svh', 'lvh', 'dvh']
      }],
      /**
       * Size
       * @see https://tailwindcss.com/docs/size
       */
      size: [{
        size: [isArbitraryValue, spacing, 'auto', 'min', 'max', 'fit']
      }],
      // Typography
      /**
       * Font Size
       * @see https://tailwindcss.com/docs/font-size
       */
      'font-size': [{
        text: ['base', isTshirtSize, isArbitraryLength]
      }],
      /**
       * Font Smoothing
       * @see https://tailwindcss.com/docs/font-smoothing
       */
      'font-smoothing': ['antialiased', 'subpixel-antialiased'],
      /**
       * Font Style
       * @see https://tailwindcss.com/docs/font-style
       */
      'font-style': ['italic', 'not-italic'],
      /**
       * Font Weight
       * @see https://tailwindcss.com/docs/font-weight
       */
      'font-weight': [{
        font: ['thin', 'extralight', 'light', 'normal', 'medium', 'semibold', 'bold', 'extrabold', 'black', isArbitraryNumber]
      }],
      /**
       * Font Family
       * @see https://tailwindcss.com/docs/font-family
       */
      'font-family': [{
        font: [isAny]
      }],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      'fvn-normal': ['normal-nums'],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      'fvn-ordinal': ['ordinal'],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      'fvn-slashed-zero': ['slashed-zero'],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      'fvn-figure': ['lining-nums', 'oldstyle-nums'],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      'fvn-spacing': ['proportional-nums', 'tabular-nums'],
      /**
       * Font Variant Numeric
       * @see https://tailwindcss.com/docs/font-variant-numeric
       */
      'fvn-fraction': ['diagonal-fractions', 'stacked-fractions'],
      /**
       * Letter Spacing
       * @see https://tailwindcss.com/docs/letter-spacing
       */
      tracking: [{
        tracking: ['tighter', 'tight', 'normal', 'wide', 'wider', 'widest', isArbitraryValue]
      }],
      /**
       * Line Clamp
       * @see https://tailwindcss.com/docs/line-clamp
       */
      'line-clamp': [{
        'line-clamp': ['none', isNumber, isArbitraryNumber]
      }],
      /**
       * Line Height
       * @see https://tailwindcss.com/docs/line-height
       */
      leading: [{
        leading: ['none', 'tight', 'snug', 'normal', 'relaxed', 'loose', isLength, isArbitraryValue]
      }],
      /**
       * List Style Image
       * @see https://tailwindcss.com/docs/list-style-image
       */
      'list-image': [{
        'list-image': ['none', isArbitraryValue]
      }],
      /**
       * List Style Type
       * @see https://tailwindcss.com/docs/list-style-type
       */
      'list-style-type': [{
        list: ['none', 'disc', 'decimal', isArbitraryValue]
      }],
      /**
       * List Style Position
       * @see https://tailwindcss.com/docs/list-style-position
       */
      'list-style-position': [{
        list: ['inside', 'outside']
      }],
      /**
       * Placeholder Color
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/placeholder-color
       */
      'placeholder-color': [{
        placeholder: [colors]
      }],
      /**
       * Placeholder Opacity
       * @see https://tailwindcss.com/docs/placeholder-opacity
       */
      'placeholder-opacity': [{
        'placeholder-opacity': [opacity]
      }],
      /**
       * Text Alignment
       * @see https://tailwindcss.com/docs/text-align
       */
      'text-alignment': [{
        text: ['left', 'center', 'right', 'justify', 'start', 'end']
      }],
      /**
       * Text Color
       * @see https://tailwindcss.com/docs/text-color
       */
      'text-color': [{
        text: [colors]
      }],
      /**
       * Text Opacity
       * @see https://tailwindcss.com/docs/text-opacity
       */
      'text-opacity': [{
        'text-opacity': [opacity]
      }],
      /**
       * Text Decoration
       * @see https://tailwindcss.com/docs/text-decoration
       */
      'text-decoration': ['underline', 'overline', 'line-through', 'no-underline'],
      /**
       * Text Decoration Style
       * @see https://tailwindcss.com/docs/text-decoration-style
       */
      'text-decoration-style': [{
        decoration: [...getLineStyles(), 'wavy']
      }],
      /**
       * Text Decoration Thickness
       * @see https://tailwindcss.com/docs/text-decoration-thickness
       */
      'text-decoration-thickness': [{
        decoration: ['auto', 'from-font', isLength, isArbitraryLength]
      }],
      /**
       * Text Underline Offset
       * @see https://tailwindcss.com/docs/text-underline-offset
       */
      'underline-offset': [{
        'underline-offset': ['auto', isLength, isArbitraryValue]
      }],
      /**
       * Text Decoration Color
       * @see https://tailwindcss.com/docs/text-decoration-color
       */
      'text-decoration-color': [{
        decoration: [colors]
      }],
      /**
       * Text Transform
       * @see https://tailwindcss.com/docs/text-transform
       */
      'text-transform': ['uppercase', 'lowercase', 'capitalize', 'normal-case'],
      /**
       * Text Overflow
       * @see https://tailwindcss.com/docs/text-overflow
       */
      'text-overflow': ['truncate', 'text-ellipsis', 'text-clip'],
      /**
       * Text Wrap
       * @see https://tailwindcss.com/docs/text-wrap
       */
      'text-wrap': [{
        text: ['wrap', 'nowrap', 'balance', 'pretty']
      }],
      /**
       * Text Indent
       * @see https://tailwindcss.com/docs/text-indent
       */
      indent: [{
        indent: getSpacingWithArbitrary()
      }],
      /**
       * Vertical Alignment
       * @see https://tailwindcss.com/docs/vertical-align
       */
      'vertical-align': [{
        align: ['baseline', 'top', 'middle', 'bottom', 'text-top', 'text-bottom', 'sub', 'super', isArbitraryValue]
      }],
      /**
       * Whitespace
       * @see https://tailwindcss.com/docs/whitespace
       */
      whitespace: [{
        whitespace: ['normal', 'nowrap', 'pre', 'pre-line', 'pre-wrap', 'break-spaces']
      }],
      /**
       * Word Break
       * @see https://tailwindcss.com/docs/word-break
       */
      break: [{
        break: ['normal', 'words', 'all', 'keep']
      }],
      /**
       * Hyphens
       * @see https://tailwindcss.com/docs/hyphens
       */
      hyphens: [{
        hyphens: ['none', 'manual', 'auto']
      }],
      /**
       * Content
       * @see https://tailwindcss.com/docs/content
       */
      content: [{
        content: ['none', isArbitraryValue]
      }],
      // Backgrounds
      /**
       * Background Attachment
       * @see https://tailwindcss.com/docs/background-attachment
       */
      'bg-attachment': [{
        bg: ['fixed', 'local', 'scroll']
      }],
      /**
       * Background Clip
       * @see https://tailwindcss.com/docs/background-clip
       */
      'bg-clip': [{
        'bg-clip': ['border', 'padding', 'content', 'text']
      }],
      /**
       * Background Opacity
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/background-opacity
       */
      'bg-opacity': [{
        'bg-opacity': [opacity]
      }],
      /**
       * Background Origin
       * @see https://tailwindcss.com/docs/background-origin
       */
      'bg-origin': [{
        'bg-origin': ['border', 'padding', 'content']
      }],
      /**
       * Background Position
       * @see https://tailwindcss.com/docs/background-position
       */
      'bg-position': [{
        bg: [...getPositions(), isArbitraryPosition]
      }],
      /**
       * Background Repeat
       * @see https://tailwindcss.com/docs/background-repeat
       */
      'bg-repeat': [{
        bg: ['no-repeat', {
          repeat: ['', 'x', 'y', 'round', 'space']
        }]
      }],
      /**
       * Background Size
       * @see https://tailwindcss.com/docs/background-size
       */
      'bg-size': [{
        bg: ['auto', 'cover', 'contain', isArbitrarySize]
      }],
      /**
       * Background Image
       * @see https://tailwindcss.com/docs/background-image
       */
      'bg-image': [{
        bg: ['none', {
          'gradient-to': ['t', 'tr', 'r', 'br', 'b', 'bl', 'l', 'tl']
        }, isArbitraryImage]
      }],
      /**
       * Background Color
       * @see https://tailwindcss.com/docs/background-color
       */
      'bg-color': [{
        bg: [colors]
      }],
      /**
       * Gradient Color Stops From Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      'gradient-from-pos': [{
        from: [gradientColorStopPositions]
      }],
      /**
       * Gradient Color Stops Via Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      'gradient-via-pos': [{
        via: [gradientColorStopPositions]
      }],
      /**
       * Gradient Color Stops To Position
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      'gradient-to-pos': [{
        to: [gradientColorStopPositions]
      }],
      /**
       * Gradient Color Stops From
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      'gradient-from': [{
        from: [gradientColorStops]
      }],
      /**
       * Gradient Color Stops Via
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      'gradient-via': [{
        via: [gradientColorStops]
      }],
      /**
       * Gradient Color Stops To
       * @see https://tailwindcss.com/docs/gradient-color-stops
       */
      'gradient-to': [{
        to: [gradientColorStops]
      }],
      // Borders
      /**
       * Border Radius
       * @see https://tailwindcss.com/docs/border-radius
       */
      rounded: [{
        rounded: [borderRadius]
      }],
      /**
       * Border Radius Start
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-s': [{
        'rounded-s': [borderRadius]
      }],
      /**
       * Border Radius End
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-e': [{
        'rounded-e': [borderRadius]
      }],
      /**
       * Border Radius Top
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-t': [{
        'rounded-t': [borderRadius]
      }],
      /**
       * Border Radius Right
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-r': [{
        'rounded-r': [borderRadius]
      }],
      /**
       * Border Radius Bottom
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-b': [{
        'rounded-b': [borderRadius]
      }],
      /**
       * Border Radius Left
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-l': [{
        'rounded-l': [borderRadius]
      }],
      /**
       * Border Radius Start Start
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-ss': [{
        'rounded-ss': [borderRadius]
      }],
      /**
       * Border Radius Start End
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-se': [{
        'rounded-se': [borderRadius]
      }],
      /**
       * Border Radius End End
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-ee': [{
        'rounded-ee': [borderRadius]
      }],
      /**
       * Border Radius End Start
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-es': [{
        'rounded-es': [borderRadius]
      }],
      /**
       * Border Radius Top Left
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-tl': [{
        'rounded-tl': [borderRadius]
      }],
      /**
       * Border Radius Top Right
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-tr': [{
        'rounded-tr': [borderRadius]
      }],
      /**
       * Border Radius Bottom Right
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-br': [{
        'rounded-br': [borderRadius]
      }],
      /**
       * Border Radius Bottom Left
       * @see https://tailwindcss.com/docs/border-radius
       */
      'rounded-bl': [{
        'rounded-bl': [borderRadius]
      }],
      /**
       * Border Width
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w': [{
        border: [borderWidth]
      }],
      /**
       * Border Width X
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-x': [{
        'border-x': [borderWidth]
      }],
      /**
       * Border Width Y
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-y': [{
        'border-y': [borderWidth]
      }],
      /**
       * Border Width Start
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-s': [{
        'border-s': [borderWidth]
      }],
      /**
       * Border Width End
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-e': [{
        'border-e': [borderWidth]
      }],
      /**
       * Border Width Top
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-t': [{
        'border-t': [borderWidth]
      }],
      /**
       * Border Width Right
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-r': [{
        'border-r': [borderWidth]
      }],
      /**
       * Border Width Bottom
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-b': [{
        'border-b': [borderWidth]
      }],
      /**
       * Border Width Left
       * @see https://tailwindcss.com/docs/border-width
       */
      'border-w-l': [{
        'border-l': [borderWidth]
      }],
      /**
       * Border Opacity
       * @see https://tailwindcss.com/docs/border-opacity
       */
      'border-opacity': [{
        'border-opacity': [opacity]
      }],
      /**
       * Border Style
       * @see https://tailwindcss.com/docs/border-style
       */
      'border-style': [{
        border: [...getLineStyles(), 'hidden']
      }],
      /**
       * Divide Width X
       * @see https://tailwindcss.com/docs/divide-width
       */
      'divide-x': [{
        'divide-x': [borderWidth]
      }],
      /**
       * Divide Width X Reverse
       * @see https://tailwindcss.com/docs/divide-width
       */
      'divide-x-reverse': ['divide-x-reverse'],
      /**
       * Divide Width Y
       * @see https://tailwindcss.com/docs/divide-width
       */
      'divide-y': [{
        'divide-y': [borderWidth]
      }],
      /**
       * Divide Width Y Reverse
       * @see https://tailwindcss.com/docs/divide-width
       */
      'divide-y-reverse': ['divide-y-reverse'],
      /**
       * Divide Opacity
       * @see https://tailwindcss.com/docs/divide-opacity
       */
      'divide-opacity': [{
        'divide-opacity': [opacity]
      }],
      /**
       * Divide Style
       * @see https://tailwindcss.com/docs/divide-style
       */
      'divide-style': [{
        divide: getLineStyles()
      }],
      /**
       * Border Color
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color': [{
        border: [borderColor]
      }],
      /**
       * Border Color X
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-x': [{
        'border-x': [borderColor]
      }],
      /**
       * Border Color Y
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-y': [{
        'border-y': [borderColor]
      }],
      /**
       * Border Color S
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-s': [{
        'border-s': [borderColor]
      }],
      /**
       * Border Color E
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-e': [{
        'border-e': [borderColor]
      }],
      /**
       * Border Color Top
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-t': [{
        'border-t': [borderColor]
      }],
      /**
       * Border Color Right
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-r': [{
        'border-r': [borderColor]
      }],
      /**
       * Border Color Bottom
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-b': [{
        'border-b': [borderColor]
      }],
      /**
       * Border Color Left
       * @see https://tailwindcss.com/docs/border-color
       */
      'border-color-l': [{
        'border-l': [borderColor]
      }],
      /**
       * Divide Color
       * @see https://tailwindcss.com/docs/divide-color
       */
      'divide-color': [{
        divide: [borderColor]
      }],
      /**
       * Outline Style
       * @see https://tailwindcss.com/docs/outline-style
       */
      'outline-style': [{
        outline: ['', ...getLineStyles()]
      }],
      /**
       * Outline Offset
       * @see https://tailwindcss.com/docs/outline-offset
       */
      'outline-offset': [{
        'outline-offset': [isLength, isArbitraryValue]
      }],
      /**
       * Outline Width
       * @see https://tailwindcss.com/docs/outline-width
       */
      'outline-w': [{
        outline: [isLength, isArbitraryLength]
      }],
      /**
       * Outline Color
       * @see https://tailwindcss.com/docs/outline-color
       */
      'outline-color': [{
        outline: [colors]
      }],
      /**
       * Ring Width
       * @see https://tailwindcss.com/docs/ring-width
       */
      'ring-w': [{
        ring: getLengthWithEmptyAndArbitrary()
      }],
      /**
       * Ring Width Inset
       * @see https://tailwindcss.com/docs/ring-width
       */
      'ring-w-inset': ['ring-inset'],
      /**
       * Ring Color
       * @see https://tailwindcss.com/docs/ring-color
       */
      'ring-color': [{
        ring: [colors]
      }],
      /**
       * Ring Opacity
       * @see https://tailwindcss.com/docs/ring-opacity
       */
      'ring-opacity': [{
        'ring-opacity': [opacity]
      }],
      /**
       * Ring Offset Width
       * @see https://tailwindcss.com/docs/ring-offset-width
       */
      'ring-offset-w': [{
        'ring-offset': [isLength, isArbitraryLength]
      }],
      /**
       * Ring Offset Color
       * @see https://tailwindcss.com/docs/ring-offset-color
       */
      'ring-offset-color': [{
        'ring-offset': [colors]
      }],
      // Effects
      /**
       * Box Shadow
       * @see https://tailwindcss.com/docs/box-shadow
       */
      shadow: [{
        shadow: ['', 'inner', 'none', isTshirtSize, isArbitraryShadow]
      }],
      /**
       * Box Shadow Color
       * @see https://tailwindcss.com/docs/box-shadow-color
       */
      'shadow-color': [{
        shadow: [isAny]
      }],
      /**
       * Opacity
       * @see https://tailwindcss.com/docs/opacity
       */
      opacity: [{
        opacity: [opacity]
      }],
      /**
       * Mix Blend Mode
       * @see https://tailwindcss.com/docs/mix-blend-mode
       */
      'mix-blend': [{
        'mix-blend': [...getBlendModes(), 'plus-lighter', 'plus-darker']
      }],
      /**
       * Background Blend Mode
       * @see https://tailwindcss.com/docs/background-blend-mode
       */
      'bg-blend': [{
        'bg-blend': getBlendModes()
      }],
      // Filters
      /**
       * Filter
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/filter
       */
      filter: [{
        filter: ['', 'none']
      }],
      /**
       * Blur
       * @see https://tailwindcss.com/docs/blur
       */
      blur: [{
        blur: [blur]
      }],
      /**
       * Brightness
       * @see https://tailwindcss.com/docs/brightness
       */
      brightness: [{
        brightness: [brightness]
      }],
      /**
       * Contrast
       * @see https://tailwindcss.com/docs/contrast
       */
      contrast: [{
        contrast: [contrast]
      }],
      /**
       * Drop Shadow
       * @see https://tailwindcss.com/docs/drop-shadow
       */
      'drop-shadow': [{
        'drop-shadow': ['', 'none', isTshirtSize, isArbitraryValue]
      }],
      /**
       * Grayscale
       * @see https://tailwindcss.com/docs/grayscale
       */
      grayscale: [{
        grayscale: [grayscale]
      }],
      /**
       * Hue Rotate
       * @see https://tailwindcss.com/docs/hue-rotate
       */
      'hue-rotate': [{
        'hue-rotate': [hueRotate]
      }],
      /**
       * Invert
       * @see https://tailwindcss.com/docs/invert
       */
      invert: [{
        invert: [invert]
      }],
      /**
       * Saturate
       * @see https://tailwindcss.com/docs/saturate
       */
      saturate: [{
        saturate: [saturate]
      }],
      /**
       * Sepia
       * @see https://tailwindcss.com/docs/sepia
       */
      sepia: [{
        sepia: [sepia]
      }],
      /**
       * Backdrop Filter
       * @deprecated since Tailwind CSS v3.0.0
       * @see https://tailwindcss.com/docs/backdrop-filter
       */
      'backdrop-filter': [{
        'backdrop-filter': ['', 'none']
      }],
      /**
       * Backdrop Blur
       * @see https://tailwindcss.com/docs/backdrop-blur
       */
      'backdrop-blur': [{
        'backdrop-blur': [blur]
      }],
      /**
       * Backdrop Brightness
       * @see https://tailwindcss.com/docs/backdrop-brightness
       */
      'backdrop-brightness': [{
        'backdrop-brightness': [brightness]
      }],
      /**
       * Backdrop Contrast
       * @see https://tailwindcss.com/docs/backdrop-contrast
       */
      'backdrop-contrast': [{
        'backdrop-contrast': [contrast]
      }],
      /**
       * Backdrop Grayscale
       * @see https://tailwindcss.com/docs/backdrop-grayscale
       */
      'backdrop-grayscale': [{
        'backdrop-grayscale': [grayscale]
      }],
      /**
       * Backdrop Hue Rotate
       * @see https://tailwindcss.com/docs/backdrop-hue-rotate
       */
      'backdrop-hue-rotate': [{
        'backdrop-hue-rotate': [hueRotate]
      }],
      /**
       * Backdrop Invert
       * @see https://tailwindcss.com/docs/backdrop-invert
       */
      'backdrop-invert': [{
        'backdrop-invert': [invert]
      }],
      /**
       * Backdrop Opacity
       * @see https://tailwindcss.com/docs/backdrop-opacity
       */
      'backdrop-opacity': [{
        'backdrop-opacity': [opacity]
      }],
      /**
       * Backdrop Saturate
       * @see https://tailwindcss.com/docs/backdrop-saturate
       */
      'backdrop-saturate': [{
        'backdrop-saturate': [saturate]
      }],
      /**
       * Backdrop Sepia
       * @see https://tailwindcss.com/docs/backdrop-sepia
       */
      'backdrop-sepia': [{
        'backdrop-sepia': [sepia]
      }],
      // Tables
      /**
       * Border Collapse
       * @see https://tailwindcss.com/docs/border-collapse
       */
      'border-collapse': [{
        border: ['collapse', 'separate']
      }],
      /**
       * Border Spacing
       * @see https://tailwindcss.com/docs/border-spacing
       */
      'border-spacing': [{
        'border-spacing': [borderSpacing]
      }],
      /**
       * Border Spacing X
       * @see https://tailwindcss.com/docs/border-spacing
       */
      'border-spacing-x': [{
        'border-spacing-x': [borderSpacing]
      }],
      /**
       * Border Spacing Y
       * @see https://tailwindcss.com/docs/border-spacing
       */
      'border-spacing-y': [{
        'border-spacing-y': [borderSpacing]
      }],
      /**
       * Table Layout
       * @see https://tailwindcss.com/docs/table-layout
       */
      'table-layout': [{
        table: ['auto', 'fixed']
      }],
      /**
       * Caption Side
       * @see https://tailwindcss.com/docs/caption-side
       */
      caption: [{
        caption: ['top', 'bottom']
      }],
      // Transitions and Animation
      /**
       * Tranisition Property
       * @see https://tailwindcss.com/docs/transition-property
       */
      transition: [{
        transition: ['none', 'all', '', 'colors', 'opacity', 'shadow', 'transform', isArbitraryValue]
      }],
      /**
       * Transition Duration
       * @see https://tailwindcss.com/docs/transition-duration
       */
      duration: [{
        duration: getNumberAndArbitrary()
      }],
      /**
       * Transition Timing Function
       * @see https://tailwindcss.com/docs/transition-timing-function
       */
      ease: [{
        ease: ['linear', 'in', 'out', 'in-out', isArbitraryValue]
      }],
      /**
       * Transition Delay
       * @see https://tailwindcss.com/docs/transition-delay
       */
      delay: [{
        delay: getNumberAndArbitrary()
      }],
      /**
       * Animation
       * @see https://tailwindcss.com/docs/animation
       */
      animate: [{
        animate: ['none', 'spin', 'ping', 'pulse', 'bounce', isArbitraryValue]
      }],
      // Transforms
      /**
       * Transform
       * @see https://tailwindcss.com/docs/transform
       */
      transform: [{
        transform: ['', 'gpu', 'none']
      }],
      /**
       * Scale
       * @see https://tailwindcss.com/docs/scale
       */
      scale: [{
        scale: [scale]
      }],
      /**
       * Scale X
       * @see https://tailwindcss.com/docs/scale
       */
      'scale-x': [{
        'scale-x': [scale]
      }],
      /**
       * Scale Y
       * @see https://tailwindcss.com/docs/scale
       */
      'scale-y': [{
        'scale-y': [scale]
      }],
      /**
       * Rotate
       * @see https://tailwindcss.com/docs/rotate
       */
      rotate: [{
        rotate: [isInteger, isArbitraryValue]
      }],
      /**
       * Translate X
       * @see https://tailwindcss.com/docs/translate
       */
      'translate-x': [{
        'translate-x': [translate]
      }],
      /**
       * Translate Y
       * @see https://tailwindcss.com/docs/translate
       */
      'translate-y': [{
        'translate-y': [translate]
      }],
      /**
       * Skew X
       * @see https://tailwindcss.com/docs/skew
       */
      'skew-x': [{
        'skew-x': [skew]
      }],
      /**
       * Skew Y
       * @see https://tailwindcss.com/docs/skew
       */
      'skew-y': [{
        'skew-y': [skew]
      }],
      /**
       * Transform Origin
       * @see https://tailwindcss.com/docs/transform-origin
       */
      'transform-origin': [{
        origin: ['center', 'top', 'top-right', 'right', 'bottom-right', 'bottom', 'bottom-left', 'left', 'top-left', isArbitraryValue]
      }],
      // Interactivity
      /**
       * Accent Color
       * @see https://tailwindcss.com/docs/accent-color
       */
      accent: [{
        accent: ['auto', colors]
      }],
      /**
       * Appearance
       * @see https://tailwindcss.com/docs/appearance
       */
      appearance: [{
        appearance: ['none', 'auto']
      }],
      /**
       * Cursor
       * @see https://tailwindcss.com/docs/cursor
       */
      cursor: [{
        cursor: ['auto', 'default', 'pointer', 'wait', 'text', 'move', 'help', 'not-allowed', 'none', 'context-menu', 'progress', 'cell', 'crosshair', 'vertical-text', 'alias', 'copy', 'no-drop', 'grab', 'grabbing', 'all-scroll', 'col-resize', 'row-resize', 'n-resize', 'e-resize', 's-resize', 'w-resize', 'ne-resize', 'nw-resize', 'se-resize', 'sw-resize', 'ew-resize', 'ns-resize', 'nesw-resize', 'nwse-resize', 'zoom-in', 'zoom-out', isArbitraryValue]
      }],
      /**
       * Caret Color
       * @see https://tailwindcss.com/docs/just-in-time-mode#caret-color-utilities
       */
      'caret-color': [{
        caret: [colors]
      }],
      /**
       * Pointer Events
       * @see https://tailwindcss.com/docs/pointer-events
       */
      'pointer-events': [{
        'pointer-events': ['none', 'auto']
      }],
      /**
       * Resize
       * @see https://tailwindcss.com/docs/resize
       */
      resize: [{
        resize: ['none', 'y', 'x', '']
      }],
      /**
       * Scroll Behavior
       * @see https://tailwindcss.com/docs/scroll-behavior
       */
      'scroll-behavior': [{
        scroll: ['auto', 'smooth']
      }],
      /**
       * Scroll Margin
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-m': [{
        'scroll-m': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin X
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-mx': [{
        'scroll-mx': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin Y
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-my': [{
        'scroll-my': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin Start
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-ms': [{
        'scroll-ms': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin End
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-me': [{
        'scroll-me': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin Top
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-mt': [{
        'scroll-mt': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin Right
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-mr': [{
        'scroll-mr': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin Bottom
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-mb': [{
        'scroll-mb': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Margin Left
       * @see https://tailwindcss.com/docs/scroll-margin
       */
      'scroll-ml': [{
        'scroll-ml': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-p': [{
        'scroll-p': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding X
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-px': [{
        'scroll-px': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding Y
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-py': [{
        'scroll-py': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding Start
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-ps': [{
        'scroll-ps': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding End
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-pe': [{
        'scroll-pe': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding Top
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-pt': [{
        'scroll-pt': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding Right
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-pr': [{
        'scroll-pr': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding Bottom
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-pb': [{
        'scroll-pb': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Padding Left
       * @see https://tailwindcss.com/docs/scroll-padding
       */
      'scroll-pl': [{
        'scroll-pl': getSpacingWithArbitrary()
      }],
      /**
       * Scroll Snap Align
       * @see https://tailwindcss.com/docs/scroll-snap-align
       */
      'snap-align': [{
        snap: ['start', 'end', 'center', 'align-none']
      }],
      /**
       * Scroll Snap Stop
       * @see https://tailwindcss.com/docs/scroll-snap-stop
       */
      'snap-stop': [{
        snap: ['normal', 'always']
      }],
      /**
       * Scroll Snap Type
       * @see https://tailwindcss.com/docs/scroll-snap-type
       */
      'snap-type': [{
        snap: ['none', 'x', 'y', 'both']
      }],
      /**
       * Scroll Snap Type Strictness
       * @see https://tailwindcss.com/docs/scroll-snap-type
       */
      'snap-strictness': [{
        snap: ['mandatory', 'proximity']
      }],
      /**
       * Touch Action
       * @see https://tailwindcss.com/docs/touch-action
       */
      touch: [{
        touch: ['auto', 'none', 'manipulation']
      }],
      /**
       * Touch Action X
       * @see https://tailwindcss.com/docs/touch-action
       */
      'touch-x': [{
        'touch-pan': ['x', 'left', 'right']
      }],
      /**
       * Touch Action Y
       * @see https://tailwindcss.com/docs/touch-action
       */
      'touch-y': [{
        'touch-pan': ['y', 'up', 'down']
      }],
      /**
       * Touch Action Pinch Zoom
       * @see https://tailwindcss.com/docs/touch-action
       */
      'touch-pz': ['touch-pinch-zoom'],
      /**
       * User Select
       * @see https://tailwindcss.com/docs/user-select
       */
      select: [{
        select: ['none', 'text', 'all', 'auto']
      }],
      /**
       * Will Change
       * @see https://tailwindcss.com/docs/will-change
       */
      'will-change': [{
        'will-change': ['auto', 'scroll', 'contents', 'transform', isArbitraryValue]
      }],
      // SVG
      /**
       * Fill
       * @see https://tailwindcss.com/docs/fill
       */
      fill: [{
        fill: [colors, 'none']
      }],
      /**
       * Stroke Width
       * @see https://tailwindcss.com/docs/stroke-width
       */
      'stroke-w': [{
        stroke: [isLength, isArbitraryLength, isArbitraryNumber]
      }],
      /**
       * Stroke
       * @see https://tailwindcss.com/docs/stroke
       */
      stroke: [{
        stroke: [colors, 'none']
      }],
      // Accessibility
      /**
       * Screen Readers
       * @see https://tailwindcss.com/docs/screen-readers
       */
      sr: ['sr-only', 'not-sr-only'],
      /**
       * Forced Color Adjust
       * @see https://tailwindcss.com/docs/forced-color-adjust
       */
      'forced-color-adjust': [{
        'forced-color-adjust': ['auto', 'none']
      }]
    },
    conflictingClassGroups: {
      overflow: ['overflow-x', 'overflow-y'],
      overscroll: ['overscroll-x', 'overscroll-y'],
      inset: ['inset-x', 'inset-y', 'start', 'end', 'top', 'right', 'bottom', 'left'],
      'inset-x': ['right', 'left'],
      'inset-y': ['top', 'bottom'],
      flex: ['basis', 'grow', 'shrink'],
      gap: ['gap-x', 'gap-y'],
      p: ['px', 'py', 'ps', 'pe', 'pt', 'pr', 'pb', 'pl'],
      px: ['pr', 'pl'],
      py: ['pt', 'pb'],
      m: ['mx', 'my', 'ms', 'me', 'mt', 'mr', 'mb', 'ml'],
      mx: ['mr', 'ml'],
      my: ['mt', 'mb'],
      size: ['w', 'h'],
      'font-size': ['leading'],
      'fvn-normal': ['fvn-ordinal', 'fvn-slashed-zero', 'fvn-figure', 'fvn-spacing', 'fvn-fraction'],
      'fvn-ordinal': ['fvn-normal'],
      'fvn-slashed-zero': ['fvn-normal'],
      'fvn-figure': ['fvn-normal'],
      'fvn-spacing': ['fvn-normal'],
      'fvn-fraction': ['fvn-normal'],
      'line-clamp': ['display', 'overflow'],
      rounded: ['rounded-s', 'rounded-e', 'rounded-t', 'rounded-r', 'rounded-b', 'rounded-l', 'rounded-ss', 'rounded-se', 'rounded-ee', 'rounded-es', 'rounded-tl', 'rounded-tr', 'rounded-br', 'rounded-bl'],
      'rounded-s': ['rounded-ss', 'rounded-es'],
      'rounded-e': ['rounded-se', 'rounded-ee'],
      'rounded-t': ['rounded-tl', 'rounded-tr'],
      'rounded-r': ['rounded-tr', 'rounded-br'],
      'rounded-b': ['rounded-br', 'rounded-bl'],
      'rounded-l': ['rounded-tl', 'rounded-bl'],
      'border-spacing': ['border-spacing-x', 'border-spacing-y'],
      'border-w': ['border-w-s', 'border-w-e', 'border-w-t', 'border-w-r', 'border-w-b', 'border-w-l'],
      'border-w-x': ['border-w-r', 'border-w-l'],
      'border-w-y': ['border-w-t', 'border-w-b'],
      'border-color': ['border-color-s', 'border-color-e', 'border-color-t', 'border-color-r', 'border-color-b', 'border-color-l'],
      'border-color-x': ['border-color-r', 'border-color-l'],
      'border-color-y': ['border-color-t', 'border-color-b'],
      'scroll-m': ['scroll-mx', 'scroll-my', 'scroll-ms', 'scroll-me', 'scroll-mt', 'scroll-mr', 'scroll-mb', 'scroll-ml'],
      'scroll-mx': ['scroll-mr', 'scroll-ml'],
      'scroll-my': ['scroll-mt', 'scroll-mb'],
      'scroll-p': ['scroll-px', 'scroll-py', 'scroll-ps', 'scroll-pe', 'scroll-pt', 'scroll-pr', 'scroll-pb', 'scroll-pl'],
      'scroll-px': ['scroll-pr', 'scroll-pl'],
      'scroll-py': ['scroll-pt', 'scroll-pb'],
      touch: ['touch-x', 'touch-y', 'touch-pz'],
      'touch-x': ['touch'],
      'touch-y': ['touch'],
      'touch-pz': ['touch']
    },
    conflictingClassGroupModifiers: {
      'font-size': ['leading']
    }
  };
};

/**
 * @param baseConfig Config where other config will be merged into. This object will be mutated.
 * @param configExtension Partial config to merge into the `baseConfig`.
 */
const mergeConfigs = (baseConfig, {
  cacheSize,
  prefix,
  separator,
  experimentalParseClassName,
  extend = {},
  override = {}
}) => {
  overrideProperty(baseConfig, 'cacheSize', cacheSize);
  overrideProperty(baseConfig, 'prefix', prefix);
  overrideProperty(baseConfig, 'separator', separator);
  overrideProperty(baseConfig, 'experimentalParseClassName', experimentalParseClassName);
  for (const configKey in override) {
    overrideConfigProperties(baseConfig[configKey], override[configKey]);
  }
  for (const key in extend) {
    mergeConfigProperties(baseConfig[key], extend[key]);
  }
  return baseConfig;
};
const overrideProperty = (baseObject, overrideKey, overrideValue) => {
  if (overrideValue !== undefined) {
    baseObject[overrideKey] = overrideValue;
  }
};
const overrideConfigProperties = (baseObject, overrideObject) => {
  if (overrideObject) {
    for (const key in overrideObject) {
      overrideProperty(baseObject, key, overrideObject[key]);
    }
  }
};
const mergeConfigProperties = (baseObject, mergeObject) => {
  if (mergeObject) {
    for (const key in mergeObject) {
      const mergeValue = mergeObject[key];
      if (mergeValue !== undefined) {
        baseObject[key] = (baseObject[key] || []).concat(mergeValue);
      }
    }
  }
};
const extendTailwindMerge = (configExtension, ...createConfig) => typeof configExtension === 'function' ? createTailwindMerge(getDefaultConfig, configExtension, ...createConfig) : createTailwindMerge(() => mergeConfigs(getDefaultConfig(), configExtension), ...createConfig);
const twMerge = /*#__PURE__*/createTailwindMerge(getDefaultConfig);

//# sourceMappingURL=bundle-mjs.mjs.map

;// ../../web-app/src/components/ui/utils.ts


function utils_cn() {
  for (var _len = arguments.length, inputs = new Array(_len), _key = 0; _key < _len; _key++) {
    inputs[_key] = arguments[_key];
  }
  return twMerge(clsx(inputs));
}
;// ../../web-app/src/components/ui/button.tsx
function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
var _excluded = ["className", "variant", "size", "asChild"];
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == _typeof(i) ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != _typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function _objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = _objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function _objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }





var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive hover:cursor-pointer", {
  variants: {
    variant: {
      default: "bg-[var(--color-brand-blue-500)] text-white hover:bg-[var(--color-brand-blue-600)] hover:text-white",
      secondary: "bg-white border border-[var(--color-warm-gray-200)] text-[var(--color-warm-gray-800)] hover:bg-[var(--color-warm-gray-100)] hover:text-[var(--color-warm-gray-900)]",
      destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
      outline: "bg-white border border-[var(--color-warm-gray-200)] text-[var(--color-warm-gray-800)] hover:bg-[var(--color-warm-gray-100)] hover:text-[var(--color-warm-gray-900)]",
      lowlight: "bg-[var(--color-warm-gray-50)] text-[var(--color-warm-gray-800)] hover:bg-[var(--color-warm-gray-100)] hover:text-[var(--color-warm-gray-900)]",
      ghost: "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
      link: "text-primary underline-offset-4 hover:underline hover:text-[var(--color-brand-blue-700)]"
    },
    size: {
      default: "h-9 px-4 py-2 has-[>svg]:px-3",
      sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
      lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
      icon: "size-9 rounded-md"
    }
  },
  defaultVariants: {
    variant: "default",
    size: "default"
  }
});
var Button = /*#__PURE__*/react.forwardRef(function (_ref, ref) {
  var className = _ref.className,
    variant = _ref.variant,
    size = _ref.size,
    _ref$asChild = _ref.asChild,
    asChild = _ref$asChild === void 0 ? false : _ref$asChild,
    props = _objectWithoutProperties(_ref, _excluded);
  var Comp = asChild ? Slot : "button";
  return /*#__PURE__*/(0,jsx_runtime.jsx)(Comp, _objectSpread({
    ref: ref,
    "data-slot": "button",
    className: utils_cn(buttonVariants({
      variant: variant,
      size: size,
      className: className
    }))
  }, props));
});
Button.displayName = "Button";

;// ./node_modules/lucide-react/dist/esm/icons/refresh-cw.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const refresh_cw_iconNode = [
  ["path", { d: "M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8", key: "v9h5vc" }],
  ["path", { d: "M21 3v5h-5", key: "1q7to0" }],
  ["path", { d: "M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16", key: "3uifl3" }],
  ["path", { d: "M8 16H3v5", key: "1cv678" }]
];
const RefreshCw = createLucideIcon("refresh-cw", refresh_cw_iconNode);


//# sourceMappingURL=refresh-cw.js.map

;// ../../web-app/src/components/ui/badge.tsx
function badge_typeof(o) { "@babel/helpers - typeof"; return badge_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, badge_typeof(o); }
var badge_excluded = ["className", "variant", "asChild"];
function badge_ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function badge_objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? badge_ownKeys(Object(t), !0).forEach(function (r) { badge_defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : badge_ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function badge_defineProperty(e, r, t) { return (r = badge_toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function badge_toPropertyKey(t) { var i = badge_toPrimitive(t, "string"); return "symbol" == badge_typeof(i) ? i : i + ""; }
function badge_toPrimitive(t, r) { if ("object" != badge_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != badge_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function badge_objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = badge_objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function badge_objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }





var badgeVariants = cva("inline-flex items-center justify-center rounded-md border px-2 py-0.5 text-xs font-normal w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden", {
  variants: {
    variant: {
      default: "border-transparent bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
      secondary: "bg-[var(--color-warm-gray-100)] text-[var(--color-warm-gray-700)] border-[var(--color-warm-gray-200)]",
      accent: "border-transparent bg-accent-subtle text-accent-subtle-foreground [a&]:hover:bg-accent-subtle/90",
      success: "bg-[var(--color-status-green-100)] text-[var(--color-status-green-700)] border-[var(--color-status-green-200)]",
      warning: "bg-[var(--color-status-yellow-100)] text-[var(--color-status-yellow-700)] border-[var(--color-status-yellow-200)]",
      destructive: "bg-[var(--color-status-red-100)] text-[var(--color-status-red-700)] border-[var(--color-status-red-200)] focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40",
      outline: "text-foreground border-[var(--color-warm-gray-300)] [a&]:hover:bg-accent [a&]:hover:text-accent-foreground"
    }
  },
  defaultVariants: {
    variant: "default"
  }
});
var badge_Badge = /*#__PURE__*/react.forwardRef(function (_ref, ref) {
  var className = _ref.className,
    variant = _ref.variant,
    _ref$asChild = _ref.asChild,
    asChild = _ref$asChild === void 0 ? false : _ref$asChild,
    props = badge_objectWithoutProperties(_ref, badge_excluded);
  var Comp = asChild ? Slot : "span";
  return /*#__PURE__*/(0,jsx_runtime.jsx)(Comp, badge_objectSpread({
    ref: ref,
    "data-slot": "badge",
    className: utils_cn(badgeVariants({
      variant: variant
    }), className)
  }, props));
});
badge_Badge.displayName = "Badge";

;// ./src/components/LocalAgentTable.jsx




function LocalAgentTable(_ref) {
  var agents = _ref.agents,
    onAgentSelect = _ref.onAgentSelect,
    _ref$isLoading = _ref.isLoading,
    isLoading = _ref$isLoading === void 0 ? false : _ref$isLoading;
  var formatLastRun = function formatLastRun(lastRun) {
    if (!lastRun || lastRun === 'never') return 'Never';
    return lastRun;
  };
  var getStatusBadgeVariant = function getStatusBadgeVariant(status) {
    var normalized = (status || '').toString().toLowerCase();
    if (['healthy', 'deployed', 'active', 'running'].includes(normalized)) {
      return 'success';
    }
    if (['building', 'pending', 'deploying'].includes(normalized)) {
      return 'secondary';
    }
    return 'secondary';
  };
  var getStatusColor = function getStatusColor(status) {
    var normalized = (status || '').toString().toLowerCase();
    if (['healthy', 'deployed', 'active', 'running'].includes(normalized)) {
      return 'bg-green-500';
    }
    if (['building', 'pending', 'deploying'].includes(normalized)) {
      return 'bg-yellow-500';
    }
    return 'bg-red-500';
  };
  if (isLoading) {
    return /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center justify-center",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
          className: "ml-3 text-gray-600",
          children: "Loading agents..."
        })]
      })
    });
  }
  if (agents.length === 0) {
    return /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "text-center",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Waypoints, {
          className: "mx-auto h-12 w-12 text-gray-400"
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("h3", {
          className: "mt-4 text-sm font-medium text-gray-900",
          children: "No agents found"
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
          className: "mt-2 text-sm text-gray-500",
          children: "Deploy an agent to get started"
        })]
      })
    });
  }
  return /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
    className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] overflow-hidden",
    children: /*#__PURE__*/(0,jsx_runtime.jsxs)("table", {
      className: "min-w-full divide-y divide-gray-200",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("thead", {
        className: "bg-gray-50",
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)("tr", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("th", {
            className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
            children: "Name"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
            className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
            children: "URL"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
            className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
            children: "Status"
          })]
        })
      }), /*#__PURE__*/(0,jsx_runtime.jsx)("tbody", {
        className: "bg-white divide-y divide-gray-200",
        children: agents.map(function (agent, index) {
          return /*#__PURE__*/(0,jsx_runtime.jsxs)("tr", {
            className: "hover:bg-gray-50 cursor-pointer transition-colors duration-150",
            onClick: function onClick() {
              return onAgentSelect(agent);
            },
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("td", {
              className: "px-6 py-4 whitespace-nowrap",
              children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex items-center",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Waypoints, {
                  className: "w-4 h-4 text-[var(--color-brand-blue-500)] mr-3"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "text-sm font-medium text-gray-900",
                  children: agent.name
                })]
              })
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
              className: "px-6 py-4 whitespace-nowrap",
              children: /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                className: "text-sm text-gray-500 font-mono",
                children: agent.url || '-'
              })
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
              className: "px-6 py-4 whitespace-nowrap",
              children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex items-center",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "w-2 h-2 rounded-full mr-2 ".concat(getStatusColor(agent.status))
                }), /*#__PURE__*/(0,jsx_runtime.jsx)(badge_Badge, {
                  variant: getStatusBadgeVariant(agent.status),
                  className: "text-xs",
                  children: agent.status || 'unknown'
                })]
              })
            })]
          }, agent.name || index);
        })
      })]
    })
  });
}
;// ./src/components/AgentListPage.jsx





var AgentListPage = function AgentListPage(_ref) {
  var appState = _ref.appState;
  var loading = appState.loading,
    agents = appState.agents,
    showAgentDetails = appState.showAgentDetails,
    refreshAgents = appState.refreshAgents,
    runningAgents = appState.runningAgents,
    totalTopics = appState.totalTopics;
  var handleAgentSelect = function handleAgentSelect(agent) {
    showAgentDetails(agent);
  };
  return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
    className: "space-y-6",
    children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-center justify-between",
      children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center gap-3",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Waypoints, {
          className: "h-8 w-8 text-[var(--color-brand-blue-600)]"
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
            className: "text-3xl font-bold text-gray-900",
            children: "Local Agents"
          }), /*#__PURE__*/(0,jsx_runtime.jsxs)("p", {
            className: "text-sm text-[var(--color-warm-gray-600)]",
            children: ["Manage and monitor your agents \u2022 ", runningAgents, " running \u2022 ", totalTopics, " topics"]
          })]
        })]
      }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "flex items-center gap-3",
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)(Button, {
          onClick: refreshAgents,
          variant: "outline",
          className: "gap-2",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(RefreshCw, {
            className: "w-4 h-4"
          }), "Refresh"]
        })
      })]
    }), /*#__PURE__*/(0,jsx_runtime.jsx)(LocalAgentTable, {
      agents: agents,
      onAgentSelect: handleAgentSelect,
      isLoading: loading
    })]
  });
};
/* harmony default export */ const components_AgentListPage = (AgentListPage);
;// ../../web-app/src/components/ui/card.tsx
function card_typeof(o) { "@babel/helpers - typeof"; return card_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, card_typeof(o); }
var card_excluded = ["className"],
  _excluded2 = ["className"],
  _excluded3 = ["className"],
  _excluded4 = (/* unused pure expression or super */ null && (["className"])),
  _excluded5 = (/* unused pure expression or super */ null && (["className"])),
  _excluded6 = ["className"],
  _excluded7 = (/* unused pure expression or super */ null && (["className"]));
function card_ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function card_objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? card_ownKeys(Object(t), !0).forEach(function (r) { card_defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : card_ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function card_defineProperty(e, r, t) { return (r = card_toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function card_toPropertyKey(t) { var i = card_toPrimitive(t, "string"); return "symbol" == card_typeof(i) ? i : i + ""; }
function card_toPrimitive(t, r) { if ("object" != card_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != card_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function card_objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = card_objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function card_objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }



function Card(_ref) {
  var className = _ref.className,
    props = card_objectWithoutProperties(_ref, card_excluded);
  return /*#__PURE__*/(0,jsx_runtime.jsx)("div", card_objectSpread({
    "data-slot": "card",
    className: utils_cn("bg-card text-card-foreground flex flex-col gap-6 rounded-xl border border-[var(--color-warm-gray-200)]", className)
  }, props));
}
function CardHeader(_ref2) {
  var className = _ref2.className,
    props = card_objectWithoutProperties(_ref2, _excluded2);
  return /*#__PURE__*/(0,jsx_runtime.jsx)("div", card_objectSpread({
    "data-slot": "card-header",
    className: utils_cn("@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 pt-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6", className)
  }, props));
}
function CardTitle(_ref3) {
  var className = _ref3.className,
    props = card_objectWithoutProperties(_ref3, _excluded3);
  return /*#__PURE__*/(0,jsx_runtime.jsx)("h4", card_objectSpread({
    "data-slot": "card-title",
    className: utils_cn("leading-none font-semibold text-[var(--color-steel-blue)]", className)
  }, props));
}
function CardDescription(_ref4) {
  var className = _ref4.className,
    props = card_objectWithoutProperties(_ref4, _excluded4);
  return /*#__PURE__*/_jsx("p", card_objectSpread({
    "data-slot": "card-description",
    className: cn("text-muted-foreground", className)
  }, props));
}
function CardAction(_ref5) {
  var className = _ref5.className,
    props = card_objectWithoutProperties(_ref5, _excluded5);
  return /*#__PURE__*/_jsx("div", card_objectSpread({
    "data-slot": "card-action",
    className: cn("col-start-2 row-span-2 row-start-1 self-start justify-self-end", className)
  }, props));
}
function CardContent(_ref6) {
  var className = _ref6.className,
    props = card_objectWithoutProperties(_ref6, _excluded6);
  return /*#__PURE__*/(0,jsx_runtime.jsx)("div", card_objectSpread({
    "data-slot": "card-content",
    className: utils_cn("px-6 [&:last-child]:pb-6", className)
  }, props));
}
function CardFooter(_ref7) {
  var className = _ref7.className,
    props = card_objectWithoutProperties(_ref7, _excluded7);
  return /*#__PURE__*/_jsx("div", card_objectSpread({
    "data-slot": "card-footer",
    className: cn("flex items-center px-6 pb-6 [.border-t]:pt-6", className)
  }, props));
}

;// ./node_modules/lucide-react/dist/esm/icons/send.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const send_iconNode = [
  [
    "path",
    {
      d: "M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z",
      key: "1ffxy3"
    }
  ],
  ["path", { d: "m21.854 2.147-10.94 10.939", key: "12cjpa" }]
];
const Send = createLucideIcon("send", send_iconNode);


//# sourceMappingURL=send.js.map

;// ./node_modules/lucide-react/dist/esm/icons/zap.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const zap_iconNode = [
  [
    "path",
    {
      d: "M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z",
      key: "1xq2db"
    }
  ]
];
const zap_Zap = createLucideIcon("zap", zap_iconNode);


//# sourceMappingURL=zap.js.map

;// ./node_modules/lucide-react/dist/esm/icons/sparkles.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const sparkles_iconNode = [
  [
    "path",
    {
      d: "M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z",
      key: "4pj2yx"
    }
  ],
  ["path", { d: "M20 3v4", key: "1olli1" }],
  ["path", { d: "M22 5h-4", key: "1gvqau" }],
  ["path", { d: "M4 17v2", key: "vumght" }],
  ["path", { d: "M5 18H3", key: "zchphs" }]
];
const Sparkles = createLucideIcon("sparkles", sparkles_iconNode);


//# sourceMappingURL=sparkles.js.map

;// ./node_modules/lucide-react/dist/esm/icons/clock.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const clock_iconNode = [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["polyline", { points: "12 6 12 12 16 14", key: "68esgv" }]
];
const clock_Clock = createLucideIcon("clock", clock_iconNode);


//# sourceMappingURL=clock.js.map

;// ./node_modules/lucide-react/dist/esm/icons/loader-circle.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const loader_circle_iconNode = [["path", { d: "M21 12a9 9 0 1 1-6.219-8.56", key: "13zald" }]];
const LoaderCircle = createLucideIcon("loader-circle", loader_circle_iconNode);


//# sourceMappingURL=loader-circle.js.map

;// ./node_modules/lucide-react/dist/esm/icons/circle-check.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const circle_check_iconNode = [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "m9 12 2 2 4-4", key: "dzmm74" }]
];
const CircleCheck = createLucideIcon("circle-check", circle_check_iconNode);


//# sourceMappingURL=circle-check.js.map

;// ./node_modules/lucide-react/dist/esm/icons/circle-x.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const circle_x_iconNode = [
  ["circle", { cx: "12", cy: "12", r: "10", key: "1mglay" }],
  ["path", { d: "m15 9-6 6", key: "1uzhvr" }],
  ["path", { d: "m9 9 6 6", key: "z0biqf" }]
];
const CircleX = createLucideIcon("circle-x", circle_x_iconNode);


//# sourceMappingURL=circle-x.js.map

;// ./node_modules/lucide-react/dist/esm/icons/copy.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const copy_iconNode = [
  ["rect", { width: "14", height: "14", x: "8", y: "8", rx: "2", ry: "2", key: "17jyea" }],
  ["path", { d: "M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2", key: "zix9uf" }]
];
const Copy = createLucideIcon("copy", copy_iconNode);


//# sourceMappingURL=copy.js.map

;// ./src/components/SendTestEventCard.jsx
function _toConsumableArray(r) { return _arrayWithoutHoles(r) || _iterableToArray(r) || _unsupportedIterableToArray(r) || _nonIterableSpread(); }
function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _iterableToArray(r) { if ("undefined" != typeof Symbol && null != r[Symbol.iterator] || null != r["@@iterator"]) return Array.from(r); }
function _arrayWithoutHoles(r) { if (Array.isArray(r)) return _arrayLikeToArray(r); }
function SendTestEventCard_typeof(o) { "@babel/helpers - typeof"; return SendTestEventCard_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, SendTestEventCard_typeof(o); }
function _regenerator() { /*! regenerator-runtime -- Copyright (c) 2014-present, Facebook, Inc. -- license (MIT): https://github.com/babel/babel/blob/main/packages/babel-helpers/LICENSE */ var e, t, r = "function" == typeof Symbol ? Symbol : {}, n = r.iterator || "@@iterator", o = r.toStringTag || "@@toStringTag"; function i(r, n, o, i) { var c = n && n.prototype instanceof Generator ? n : Generator, u = Object.create(c.prototype); return _regeneratorDefine2(u, "_invoke", function (r, n, o) { var i, c, u, f = 0, p = o || [], y = !1, G = { p: 0, n: 0, v: e, a: d, f: d.bind(e, 4), d: function d(t, r) { return i = t, c = 0, u = e, G.n = r, a; } }; function d(r, n) { for (c = r, u = n, t = 0; !y && f && !o && t < p.length; t++) { var o, i = p[t], d = G.p, l = i[2]; r > 3 ? (o = l === n) && (u = i[(c = i[4]) ? 5 : (c = 3, 3)], i[4] = i[5] = e) : i[0] <= d && ((o = r < 2 && d < i[1]) ? (c = 0, G.v = n, G.n = i[1]) : d < l && (o = r < 3 || i[0] > n || n > l) && (i[4] = r, i[5] = n, G.n = l, c = 0)); } if (o || r > 1) return a; throw y = !0, n; } return function (o, p, l) { if (f > 1) throw TypeError("Generator is already running"); for (y && 1 === p && d(p, l), c = p, u = l; (t = c < 2 ? e : u) || !y;) { i || (c ? c < 3 ? (c > 1 && (G.n = -1), d(c, u)) : G.n = u : G.v = u); try { if (f = 2, i) { if (c || (o = "next"), t = i[o]) { if (!(t = t.call(i, u))) throw TypeError("iterator result is not an object"); if (!t.done) return t; u = t.value, c < 2 && (c = 0); } else 1 === c && (t = i.return) && t.call(i), c < 2 && (u = TypeError("The iterator does not provide a '" + o + "' method"), c = 1); i = e; } else if ((t = (y = G.n < 0) ? u : r.call(n, G)) !== a) break; } catch (t) { i = e, c = 1, u = t; } finally { f = 1; } } return { value: t, done: y }; }; }(r, o, i), !0), u; } var a = {}; function Generator() {} function GeneratorFunction() {} function GeneratorFunctionPrototype() {} t = Object.getPrototypeOf; var c = [][n] ? t(t([][n]())) : (_regeneratorDefine2(t = {}, n, function () { return this; }), t), u = GeneratorFunctionPrototype.prototype = Generator.prototype = Object.create(c); function f(e) { return Object.setPrototypeOf ? Object.setPrototypeOf(e, GeneratorFunctionPrototype) : (e.__proto__ = GeneratorFunctionPrototype, _regeneratorDefine2(e, o, "GeneratorFunction")), e.prototype = Object.create(u), e; } return GeneratorFunction.prototype = GeneratorFunctionPrototype, _regeneratorDefine2(u, "constructor", GeneratorFunctionPrototype), _regeneratorDefine2(GeneratorFunctionPrototype, "constructor", GeneratorFunction), GeneratorFunction.displayName = "GeneratorFunction", _regeneratorDefine2(GeneratorFunctionPrototype, o, "GeneratorFunction"), _regeneratorDefine2(u), _regeneratorDefine2(u, o, "Generator"), _regeneratorDefine2(u, n, function () { return this; }), _regeneratorDefine2(u, "toString", function () { return "[object Generator]"; }), (_regenerator = function _regenerator() { return { w: i, m: f }; })(); }
function _regeneratorDefine2(e, r, n, t) { var i = Object.defineProperty; try { i({}, "", {}); } catch (e) { i = 0; } _regeneratorDefine2 = function _regeneratorDefine(e, r, n, t) { function o(r, n) { _regeneratorDefine2(e, r, function (e) { return this._invoke(r, n, e); }); } r ? i ? i(e, r, { value: n, enumerable: !t, configurable: !t, writable: !t }) : e[r] = n : (o("next", 0), o("throw", 1), o("return", 2)); }, _regeneratorDefine2(e, r, n, t); }
function asyncGeneratorStep(n, t, e, r, o, a, c) { try { var i = n[a](c), u = i.value; } catch (n) { return void e(n); } i.done ? t(u) : Promise.resolve(u).then(r, o); }
function _asyncToGenerator(n) { return function () { var t = this, e = arguments; return new Promise(function (r, o) { var a = n.apply(t, e); function _next(n) { asyncGeneratorStep(a, r, o, _next, _throw, "next", n); } function _throw(n) { asyncGeneratorStep(a, r, o, _next, _throw, "throw", n); } _next(void 0); }); }; }
function SendTestEventCard_ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function SendTestEventCard_objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? SendTestEventCard_ownKeys(Object(t), !0).forEach(function (r) { SendTestEventCard_defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : SendTestEventCard_ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function SendTestEventCard_defineProperty(e, r, t) { return (r = SendTestEventCard_toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function SendTestEventCard_toPropertyKey(t) { var i = SendTestEventCard_toPrimitive(t, "string"); return "symbol" == SendTestEventCard_typeof(i) ? i : i + ""; }
function SendTestEventCard_toPrimitive(t, r) { if ("object" != SendTestEventCard_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != SendTestEventCard_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function _createForOfIteratorHelper(r, e) { var t = "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (!t) { if (Array.isArray(r) || (t = _unsupportedIterableToArray(r)) || e && r && "number" == typeof r.length) { t && (r = t); var _n = 0, F = function F() {}; return { s: F, n: function n() { return _n >= r.length ? { done: !0 } : { done: !1, value: r[_n++] }; }, e: function e(r) { throw r; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var o, a = !0, u = !1; return { s: function s() { t = t.call(r); }, n: function n() { var r = t.next(); return a = r.done, r; }, e: function e(r) { u = !0, o = r; }, f: function f() { try { a || null == t.return || t.return(); } finally { if (u) throw o; } } }; }
function _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }
function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function _iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function _arrayWithHoles(r) { if (Array.isArray(r)) return r; }





var SendTestEventCard = function SendTestEventCard(_ref) {
  var appState = _ref.appState;
  var topics = appState.topics,
    selectedAgent = appState.selectedAgent,
    isTopicDetailsPage = appState.isTopicDetailsPage,
    isAgentDetailsPage = appState.isAgentDetailsPage;

  // Invocation type: 'function' or 'topic'
  var _useState = (0,react.useState)('function'),
    _useState2 = _slicedToArray(_useState, 2),
    invocationType = _useState2[0],
    setInvocationType = _useState2[1];
  var _useState3 = (0,react.useState)({
      topic: '',
      functionName: '',
      payload: '{\n  "message": "Hello from UI!"\n}',
      sender_id: 'ui-test',
      timeout_seconds: 3600 // Default 1 hour (matches backend default)
    }),
    _useState4 = _slicedToArray(_useState3, 2),
    eventForm = _useState4[0],
    setEventForm = _useState4[1];
  var _useState5 = (0,react.useState)(null),
    _useState6 = _slicedToArray(_useState5, 2),
    jsonError = _useState6[0],
    setJsonError = _useState6[1];
  var _useState7 = (0,react.useState)(false),
    _useState8 = _slicedToArray(_useState7, 2),
    sendingEvent = _useState8[0],
    setSendingEvent = _useState8[1];
  var _useState9 = (0,react.useState)(null),
    _useState0 = _slicedToArray(_useState9, 2),
    eventResponse = _useState0[0],
    setEventResponse = _useState0[1];
  var _useState1 = (0,react.useState)(null),
    _useState10 = _slicedToArray(_useState1, 2),
    currentTraceId = _useState10[0],
    setCurrentTraceId = _useState10[1];
  var _useState11 = (0,react.useState)(false),
    _useState12 = _slicedToArray(_useState11, 2),
    isLoadingSchema = _useState12[0],
    setIsLoadingSchema = _useState12[1];
  var _useState13 = (0,react.useState)(null),
    _useState14 = _slicedToArray(_useState13, 2),
    schemaError = _useState14[0],
    setSchemaError = _useState14[1];
  var _useState15 = (0,react.useState)(false),
    _useState16 = _slicedToArray(_useState15, 2),
    isAgentReady = _useState16[0],
    setIsAgentReady = _useState16[1];
  var _useState17 = (0,react.useState)(false),
    _useState18 = _slicedToArray(_useState17, 2),
    showAdvanced = _useState18[0],
    setShowAdvanced = _useState18[1];

  // Track which topic we've already loaded schema for to prevent redundant fetches
  var lastLoadedSchemaTopicRef = (0,react.useRef)(null);

  // Function invocation state (similar to FunctionsCard modal)
  var _useState19 = (0,react.useState)({
      status: 'idle',
      // idle | pending | running | completed | error
      invocationId: null,
      traceId: null,
      result: null,
      error: null
    }),
    _useState20 = _slicedToArray(_useState19, 2),
    invocationState = _useState20[0],
    setInvocationState = _useState20[1];

  // Filter topics based on selected agent's capabilities
  var getAgentTopics = function getAgentTopics() {
    if (!selectedAgent) {
      return [];
    }

    // Use agent.topics array directly (simpler and more reliable)
    if (selectedAgent.topics && Array.isArray(selectedAgent.topics)) {
      console.log("Agent ".concat(selectedAgent.name, " subscribes to topics:"), selectedAgent.topics);
      var filteredTopics = topics.filter(function (topic) {
        var topicName = typeof topic === 'string' ? topic : (topic === null || topic === void 0 ? void 0 : topic.topic) || (topic === null || topic === void 0 ? void 0 : topic.name) || topic;
        return selectedAgent.topics.includes(topicName);
      });
      console.log("Filtered topics for agent:", filteredTopics);
      return filteredTopics;
    }

    // Fallback: try to extract from functions (legacy support)
    if (selectedAgent.functions && Array.isArray(selectedAgent.functions)) {
      var agentTopics = selectedAgent.functions.flatMap(function (func) {
        return func.triggers || [];
      }).filter(function (trigger) {
        return trigger.type === 'topic' && trigger.topic;
      }).map(function (trigger) {
        return trigger.topic;
      });
      return topics.filter(function (topic) {
        var topicName = typeof topic === 'string' ? topic : (topic === null || topic === void 0 ? void 0 : topic.topic) || (topic === null || topic === void 0 ? void 0 : topic.name) || topic;
        return agentTopics.includes(topicName);
      });
    }

    // If no topic information available, return empty array instead of all topics
    return [];
  };

  // Get callable @fn functions from agent
  var getAgentFunctions = function getAgentFunctions() {
    if (!selectedAgent || !selectedAgent.functions) {
      return [];
    }
    var callableFunctions = [];
    var _iterator = _createForOfIteratorHelper(selectedAgent.functions),
      _step;
    try {
      for (_iterator.s(); !(_step = _iterator.n()).done;) {
        var func = _step.value;
        var callableTriggers = (func.triggers || []).filter(function (t) {
          return t.type === 'callable';
        });
        var _iterator2 = _createForOfIteratorHelper(callableTriggers),
          _step2;
        try {
          for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
            var trigger = _step2.value;
            callableFunctions.push({
              functionName: trigger.function_name || func.name,
              name: func.name,
              description: func.description,
              inputSchema: func.input_schema,
              outputSchema: func.output_schema
            });
          }
        } catch (err) {
          _iterator2.e(err);
        } finally {
          _iterator2.f();
        }
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
    return callableFunctions;
  };

  // Check if agent has topics
  var hasTopics = function hasTopics() {
    return getAgentTopics().length > 0;
  };

  // Check if agent has callable functions
  var hasFunctions = function hasFunctions() {
    return getAgentFunctions().length > 0;
  };

  // Auto-select first function or topic when agent is selected
  (0,react.useEffect)(function () {
    // On Topic Details page, everything is immediately ready
    if (isTopicDetailsPage) {
      setIsAgentReady(true);
      setInvocationType('topic'); // Force topic mode on topic details page
      return;
    }

    // On Agent Details page, force function mode only
    if (isAgentDetailsPage && selectedAgent) {
      setIsAgentReady(true);
      setInvocationType('function'); // Force function mode on agent details page

      var functions = getAgentFunctions();
      if (functions.length > 0 && !eventForm.functionName) {
        handleFunctionChange(functions[0].functionName);
      }
      return;
    }

    // Regular logic for other pages
    if (selectedAgent) {
      // Agent data is already available from subscription - no delay needed
      setIsAgentReady(true);

      // Auto-select based on what's available
      var _functions = getAgentFunctions();
      var agentTopics = getAgentTopics();
      if (_functions.length > 0) {
        // Default to function mode and select first function
        setInvocationType('function');
        if (!eventForm.functionName) {
          handleFunctionChange(_functions[0].functionName);
        }
      } else if (agentTopics.length > 0) {
        // Fall back to topic mode
        setInvocationType('topic');
        var firstTopic = typeof agentTopics[0] === 'string' ? agentTopics[0] : agentTopics[0].topic;
        if (firstTopic !== eventForm.topic) {
          handleTopicChange(firstTopic);
        }
      }
    } else {
      setIsAgentReady(false);
    }
  }, [selectedAgent, isTopicDetailsPage, isAgentDetailsPage]);

  // Listen for invokeFunction events from FunctionsCard
  (0,react.useEffect)(function () {
    var handleInvokeFunction = function handleInvokeFunction(event) {
      var _event$detail = event.detail,
        functionName = _event$detail.functionName,
        inputSchema = _event$detail.inputSchema;
      setInvocationType('function');
      handleFunctionChange(functionName, inputSchema);
      // Reset invocation state when switching functions
      setInvocationState({
        status: 'idle',
        invocationId: null,
        traceId: null,
        result: null,
        error: null
      });
    };
    window.addEventListener('invokeFunction', handleInvokeFunction);
    return function () {
      return window.removeEventListener('invokeFunction', handleInvokeFunction);
    };
  }, [selectedAgent]);

  // Auto-populate schema when selectedAgent or topic changes (only when agent is ready)
  (0,react.useEffect)(function () {
    if (eventForm.topic && (selectedAgent && isAgentReady || isTopicDetailsPage)) {
      populateWithSchemaExample(eventForm.topic);
    }
  }, [selectedAgent, eventForm.topic, isAgentReady, isTopicDetailsPage]);

  // Initialize form - different behavior for Topic Details vs Agent Details pages
  // This effect only runs once when the page loads, not on every topics array update
  (0,react.useEffect)(function () {
    // On Topic Details page, immediately set the topic from the topics array
    if (isTopicDetailsPage && topics.length > 0 && topics[0]) {
      var topicName = typeof topics[0] === 'string' ? topics[0] : topics[0].topic || topics[0].name || topics[0];
      if (topicName && topicName !== eventForm.topic) {
        setEventForm(function (prev) {
          return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
            topic: topicName
          });
        });
        // Also immediately load schema since we know the topic
        populateWithSchemaExample(topicName);
      }
    }
    // Regular agent details page behavior
    else if (!isTopicDetailsPage && topics.length > 0 && topics[0] && !eventForm.topic && !selectedAgent) {
      var _topicName = typeof topics[0] === 'string' ? topics[0] : topics[0].topic || topics[0].name || 'test';
      setEventForm(function (prev) {
        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
          topic: _topicName
        });
      });
    }
  }, [topics, isTopicDetailsPage]);

  // Initialize icons when component updates

  // Validate JSON payload
  var validateJson = function validateJson(jsonString) {
    try {
      JSON.parse(jsonString);
      setJsonError(null);
      return true;
    } catch (error) {
      setJsonError('Invalid JSON: ' + error.message);
      return false;
    }
  };

  // Handle form input changes
  var handleFormChange = function handleFormChange(field, value) {
    setEventForm(function (prev) {
      return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, SendTestEventCard_defineProperty({}, field, value));
    });
    if (field === 'payload') {
      validateJson(value);
    }
  };

  // Auto-populate form with schema example
  var populateWithSchemaExample = /*#__PURE__*/function () {
    var _ref2 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee(topicName) {
      var forceRefresh,
        topicSchemasResponse,
        topicSchemasData,
        topicSchemas,
        schemas,
        schema,
        examplePayload,
        response,
        schemaInfo,
        _schema,
        _examplePayload,
        _args = arguments,
        _t,
        _t2;
      return _regenerator().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            forceRefresh = _args.length > 1 && _args[1] !== undefined ? _args[1] : false;
            if (topicName) {
              _context.n = 1;
              break;
            }
            return _context.a(2);
          case 1:
            if (!(!forceRefresh && lastLoadedSchemaTopicRef.current === topicName)) {
              _context.n = 2;
              break;
            }
            return _context.a(2);
          case 2:
            setIsLoadingSchema(true);
            setSchemaError(null);
            lastLoadedSchemaTopicRef.current = topicName;
            _context.p = 3;
            _context.n = 4;
            return fetch('/api/unstable/schemas/topics');
          case 4:
            topicSchemasResponse = _context.v;
            if (!topicSchemasResponse.ok) {
              _context.n = 8;
              break;
            }
            _context.n = 5;
            return topicSchemasResponse.json();
          case 5:
            topicSchemasData = _context.v;
            topicSchemas = topicSchemasData.topics || {}; // Find schemas for this topic
            schemas = topicSchemas[topicName] || [];
            if (!(schemas.length > 0)) {
              _context.n = 8;
              break;
            }
            // Try to generate example from first schema
            schema = schemas[0];
            if (!(schema.schema && schema.schema.input_schema)) {
              _context.n = 8;
              break;
            }
            _context.p = 6;
            examplePayload = generateExampleFromSchema(schema.schema.input_schema);
            handleFormChange('payload', JSON.stringify(examplePayload, null, 2));
            setSchemaError(null);
            return _context.a(2);
          case 7:
            _context.p = 7;
            _t = _context.v;
            setSchemaError('Could not generate example from schema');
          case 8:
            _context.n = 9;
            return fetch("/api/unstable/schemas/".concat(encodeURIComponent(topicName)));
          case 9:
            response = _context.v;
            if (!response.ok) {
              _context.n = 11;
              break;
            }
            _context.n = 10;
            return response.json();
          case 10:
            schemaInfo = _context.v;
            if (schemaInfo.canonical_schema) {
              _schema = schemaInfo.canonical_schema.input_schema;
              _examplePayload = generateExampleFromSchema(_schema);
              handleFormChange('payload', JSON.stringify(_examplePayload, null, 2));
              setSchemaError(null);
            } else {
              setSchemaError('No schema available for this topic');
            }
            _context.n = 12;
            break;
          case 11:
            // Schema not available yet - show helpful message
            setSchemaError('Schema not yet available. Agent may still be registering.');
          case 12:
            _context.n = 14;
            break;
          case 13:
            _context.p = 13;
            _t2 = _context.v;
            setSchemaError('Could not load schema. Please try again in a moment.');
          case 14:
            _context.p = 14;
            setIsLoadingSchema(false);
            return _context.f(14);
          case 15:
            return _context.a(2);
        }
      }, _callee, null, [[6, 7], [3, 13, 14, 15]]);
    }));
    return function populateWithSchemaExample(_x) {
      return _ref2.apply(this, arguments);
    };
  }();

  // Simple schema example generator
  var generateExampleFromSchema = function generateExampleFromSchema(schema) {
    if (!schema || SendTestEventCard_typeof(schema) !== 'object') {
      return {
        message: 'Hello from UI!'
      };
    }
    var _generateFromProperties = function generateFromProperties(properties) {
      var result = {};
      for (var _i = 0, _Object$entries = Object.entries(properties); _i < _Object$entries.length; _i++) {
        var _Object$entries$_i = _slicedToArray(_Object$entries[_i], 2),
          key = _Object$entries$_i[0],
          prop = _Object$entries$_i[1];
        if (prop.type === 'string') {
          result[key] = prop.example || "example_".concat(key);
        } else if (prop.type === 'number' || prop.type === 'integer') {
          result[key] = prop.example || 42;
        } else if (prop.type === 'boolean') {
          result[key] = prop.example !== undefined ? prop.example : true;
        } else if (prop.type === 'array') {
          result[key] = [prop.items ? _generateFromProperties({
            item: prop.items
          }).item : 'item'];
        } else if (prop.type === 'object' && prop.properties) {
          result[key] = _generateFromProperties(prop.properties);
        } else {
          result[key] = prop.example || "example_".concat(key);
        }
      }
      return result;
    };
    if (schema.properties) {
      return _generateFromProperties(schema.properties);
    } else if (schema.example) {
      return schema.example;
    }
    return {
      message: 'Hello from UI!'
    };
  };

  // Handle topic change
  var handleTopicChange = function handleTopicChange(newTopic) {
    handleFormChange('topic', newTopic);
    // Auto-populate with schema example when topic changes
    if (newTopic && selectedAgent) {
      populateWithSchemaExample(newTopic);
    }
  };

  // Handle function change
  var handleFunctionChange = function handleFunctionChange(newFunctionName) {
    var inputSchema = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    handleFormChange('functionName', newFunctionName);

    // Find function schema if not provided
    if (!inputSchema) {
      var functions = getAgentFunctions();
      var func = functions.find(function (f) {
        return f.functionName === newFunctionName;
      });
      inputSchema = func === null || func === void 0 ? void 0 : func.inputSchema;
    }

    // Auto-populate payload from function schema
    if (inputSchema) {
      try {
        var example = generateExampleFromSchema(inputSchema);
        handleFormChange('payload', JSON.stringify(example, null, 2));
        setSchemaError(null);
      } catch (e) {
        // Fall back to default payload
        handleFormChange('payload', '{}');
      }
    } else {
      handleFormChange('payload', '{}');
    }
  };

  // Poll for function invocation result
  var pollForResult = (0,react.useCallback)(/*#__PURE__*/function () {
    var _ref3 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee3(invocationId, timeoutSeconds) {
      var maxAttempts, attempts, _poll;
      return _regenerator().w(function (_context3) {
        while (1) switch (_context3.n) {
          case 0:
            // Use 2x the timeout to avoid race conditions with backend timeout
            maxAttempts = (timeoutSeconds || 3600) * 2;
            attempts = 0;
            _poll = /*#__PURE__*/function () {
              var _ref4 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee2() {
                var response, data, _t3;
                return _regenerator().w(function (_context2) {
                  while (1) switch (_context2.p = _context2.n) {
                    case 0:
                      if (!(attempts >= maxAttempts)) {
                        _context2.n = 1;
                        break;
                      }
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: 'error',
                          error: "Invocation timed out after ".concat(Math.round(maxAttempts / 60), " minutes")
                        });
                      });
                      setSendingEvent(false);
                      return _context2.a(2);
                    case 1:
                      _context2.p = 1;
                      _context2.n = 2;
                      return fetch("/api/unstable/invoke/".concat(invocationId));
                    case 2:
                      response = _context2.v;
                      if (response.ok) {
                        _context2.n = 3;
                        break;
                      }
                      throw new Error('Failed to get invocation status');
                    case 3:
                      _context2.n = 4;
                      return response.json();
                    case 4:
                      data = _context2.v;
                      if (!(data.status === 'completed')) {
                        _context2.n = 5;
                        break;
                      }
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: 'completed',
                          result: data.result,
                          traceId: data.trace_id
                        });
                      });
                      setSendingEvent(false);

                      // Dispatch trace event for MessageFeed to poll for enriched events
                      if (data.trace_id) {
                        window.dispatchEvent(new CustomEvent('traceStarted', {
                          detail: {
                            traceId: data.trace_id,
                            startPolling: true,
                            timeoutSeconds: eventForm.timeout_seconds
                          }
                        }));
                      }
                      return _context2.a(2);
                    case 5:
                      if (!(data.status === 'error')) {
                        _context2.n = 6;
                        break;
                      }
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: 'error',
                          error: data.error || 'Unknown error',
                          traceId: data.trace_id
                        });
                      });
                      setSendingEvent(false);
                      return _context2.a(2);
                    case 6:
                      // Still pending or running
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: data.status,
                          traceId: data.trace_id
                        });
                      });
                      attempts++;
                      setTimeout(_poll, 1000);
                      _context2.n = 8;
                      break;
                    case 7:
                      _context2.p = 7;
                      _t3 = _context2.v;
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: 'error',
                          error: _t3.message || 'Failed to get invocation status'
                        });
                      });
                      setSendingEvent(false);
                    case 8:
                      return _context2.a(2);
                  }
                }, _callee2, null, [[1, 7]]);
              }));
              return function poll() {
                return _ref4.apply(this, arguments);
              };
            }();
            _poll();
          case 1:
            return _context3.a(2);
        }
      }, _callee3);
    }));
    return function (_x2, _x3) {
      return _ref3.apply(this, arguments);
    };
  }(), []);

  // Invoke function
  var invokeFunction = /*#__PURE__*/function () {
    var _ref5 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee4() {
      var response, errorData, data, _t4;
      return _regenerator().w(function (_context4) {
        while (1) switch (_context4.p = _context4.n) {
          case 0:
            if (!(!validateJson(eventForm.payload) || !selectedAgent || !eventForm.functionName)) {
              _context4.n = 1;
              break;
            }
            return _context4.a(2);
          case 1:
            setSendingEvent(true);
            setEventResponse(null);
            setInvocationState({
              status: 'pending',
              invocationId: null,
              traceId: null,
              result: null,
              error: null
            });
            _context4.p = 2;
            _context4.n = 3;
            return fetch('/api/unstable/invoke', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                agent_name: selectedAgent.name,
                function_name: eventForm.functionName,
                payload: JSON.parse(eventForm.payload),
                timeout_seconds: eventForm.timeout_seconds
              })
            });
          case 3:
            response = _context4.v;
            if (response.ok) {
              _context4.n = 5;
              break;
            }
            _context4.n = 4;
            return response.json();
          case 4:
            errorData = _context4.v;
            throw new Error(errorData.detail || 'Failed to invoke function');
          case 5:
            _context4.n = 6;
            return response.json();
          case 6:
            data = _context4.v;
            setInvocationState(function (prev) {
              return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                invocationId: data.invocation_id,
                traceId: data.trace_id,
                status: 'running'
              });
            });

            // Start MessageFeed polling immediately so LLM calls appear in real-time
            if (data.trace_id) {
              window.dispatchEvent(new CustomEvent('traceStarted', {
                detail: {
                  traceId: data.trace_id,
                  startPolling: true,
                  timeoutSeconds: eventForm.timeout_seconds
                }
              }));
            }

            // Start polling for result
            pollForResult(data.invocation_id, eventForm.timeout_seconds);
            _context4.n = 8;
            break;
          case 7:
            _context4.p = 7;
            _t4 = _context4.v;
            setInvocationState({
              status: 'error',
              invocationId: null,
              traceId: null,
              result: null,
              error: _t4.message
            });
            setSendingEvent(false);
          case 8:
            return _context4.a(2);
        }
      }, _callee4, null, [[2, 7]]);
    }));
    return function invokeFunction() {
      return _ref5.apply(this, arguments);
    };
  }();

  // Copy to clipboard
  var copyToClipboard = function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
  };

  // Poll for topic publish invocation results (same pattern as function invoke)
  var pollForTopicResults = (0,react.useCallback)(/*#__PURE__*/function () {
    var _ref6 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee7(invocationIds, traceId, timeoutSeconds) {
      var maxAttempts, attempts, pendingInvocations, _poll2;
      return _regenerator().w(function (_context7) {
        while (1) switch (_context7.n) {
          case 0:
            // Use 2x the timeout to avoid race conditions with backend timeout
            maxAttempts = (timeoutSeconds || 3600) * 2;
            attempts = 0;
            pendingInvocations = new Set(invocationIds);
            _poll2 = /*#__PURE__*/function () {
              var _ref7 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee6() {
                var results, allCompleted, anyError, lastError, completedResults, _iterator3, _step3, data, combinedResult, _t5;
                return _regenerator().w(function (_context6) {
                  while (1) switch (_context6.p = _context6.n) {
                    case 0:
                      if (!(attempts >= maxAttempts)) {
                        _context6.n = 1;
                        break;
                      }
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: 'error',
                          error: "Invocation timed out after ".concat(Math.round(maxAttempts / 60), " minutes")
                        });
                      });
                      setSendingEvent(false);
                      return _context6.a(2);
                    case 1:
                      _context6.p = 1;
                      _context6.n = 2;
                      return Promise.all(_toConsumableArray(pendingInvocations).map(/*#__PURE__*/function () {
                        var _ref8 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee5(invId) {
                          var response;
                          return _regenerator().w(function (_context5) {
                            while (1) switch (_context5.n) {
                              case 0:
                                _context5.n = 1;
                                return fetch("/api/unstable/invoke/".concat(invId));
                              case 1:
                                response = _context5.v;
                                if (response.ok) {
                                  _context5.n = 2;
                                  break;
                                }
                                throw new Error('Failed to get invocation status');
                              case 2:
                                return _context5.a(2, response.json());
                            }
                          }, _callee5);
                        }));
                        return function (_x7) {
                          return _ref8.apply(this, arguments);
                        };
                      }()));
                    case 2:
                      results = _context6.v;
                      // Check which invocations are done
                      allCompleted = true;
                      anyError = false;
                      lastError = null;
                      completedResults = [];
                      _iterator3 = _createForOfIteratorHelper(results);
                      try {
                        for (_iterator3.s(); !(_step3 = _iterator3.n()).done;) {
                          data = _step3.value;
                          if (data.status === 'completed') {
                            pendingInvocations.delete(data.invocation_id);
                            completedResults.push(data);
                          } else if (data.status === 'error') {
                            pendingInvocations.delete(data.invocation_id);
                            anyError = true;
                            lastError = data.error;
                          } else {
                            allCompleted = false;
                          }
                        }

                        // All done or all have resolved
                      } catch (err) {
                        _iterator3.e(err);
                      } finally {
                        _iterator3.f();
                      }
                      if (!(pendingInvocations.size === 0)) {
                        _context6.n = 3;
                        break;
                      }
                      if (anyError) {
                        setInvocationState(function (prev) {
                          return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                            status: 'error',
                            error: lastError || 'One or more handlers failed',
                            traceId: traceId
                          });
                        });
                      } else {
                        // Combine all results
                        combinedResult = completedResults.length === 1 ? completedResults[0].result : completedResults.map(function (r) {
                          return {
                            agent: r.agent_name,
                            result: r.result
                          };
                        });
                        setInvocationState(function (prev) {
                          return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                            status: 'completed',
                            result: combinedResult,
                            traceId: traceId
                          });
                        });
                      }
                      setSendingEvent(false);

                      // Dispatch trace event for MessageFeed to poll for enriched events
                      window.dispatchEvent(new CustomEvent('traceStarted', {
                        detail: {
                          traceId: traceId,
                          startPolling: true,
                          timeoutSeconds: eventForm.timeout_seconds
                        }
                      }));
                      return _context6.a(2);
                    case 3:
                      // Still pending - update state and continue polling
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: 'running',
                          traceId: traceId
                        });
                      });
                      attempts++;
                      setTimeout(_poll2, 1000);
                      _context6.n = 5;
                      break;
                    case 4:
                      _context6.p = 4;
                      _t5 = _context6.v;
                      setInvocationState(function (prev) {
                        return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                          status: 'error',
                          error: _t5.message || 'Failed to get invocation status'
                        });
                      });
                      setSendingEvent(false);
                    case 5:
                      return _context6.a(2);
                  }
                }, _callee6, null, [[1, 4]]);
              }));
              return function poll() {
                return _ref7.apply(this, arguments);
              };
            }();
            _poll2();
          case 1:
            return _context7.a(2);
        }
      }, _callee7);
    }));
    return function (_x4, _x5, _x6) {
      return _ref6.apply(this, arguments);
    };
  }(), []);

  // Send event function (for topics) - now uses invocation-based pattern
  var sendEvent = /*#__PURE__*/function () {
    var _ref9 = _asyncToGenerator(/*#__PURE__*/_regenerator().m(function _callee8() {
      var response, result, firstInvocationResponse, firstInvData, _t6;
      return _regenerator().w(function (_context8) {
        while (1) switch (_context8.p = _context8.n) {
          case 0:
            if (validateJson(eventForm.payload)) {
              _context8.n = 1;
              break;
            }
            return _context8.a(2);
          case 1:
            setSendingEvent(true);
            setEventResponse(null);
            setCurrentTraceId(null);
            setInvocationState({
              status: 'pending',
              invocationId: null,
              traceId: null,
              result: null,
              error: null
            });
            _context8.p = 2;
            _context8.n = 3;
            return fetch('/api/unstable/events/publish', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                topic: eventForm.topic,
                payload: JSON.parse(eventForm.payload),
                sender_id: eventForm.sender_id
              })
            });
          case 3:
            response = _context8.v;
            _context8.n = 4;
            return response.json();
          case 4:
            result = _context8.v;
            if (!response.ok) {
              _context8.n = 10;
              break;
            }
            // Store trace info for display
            setCurrentTraceId(result.event_uid);

            // If no handlers, show message
            if (!(result.handler_count === 0)) {
              _context8.n = 5;
              break;
            }
            setInvocationState({
              status: 'completed',
              invocationId: null,
              traceId: null,
              result: {
                message: 'No handlers subscribed to this topic'
              },
              error: null
            });
            setSendingEvent(false);
            return _context8.a(2);
          case 5:
            // Update state with invocation IDs
            setInvocationState(function (prev) {
              return SendTestEventCard_objectSpread(SendTestEventCard_objectSpread({}, prev), {}, {
                status: 'running',
                invocationId: result.invocation_ids.join(', ')
              });
            });

            // Poll for results (like function invocation)
            // First, we need to extract trace_id - fetch it from first invocation
            _context8.n = 6;
            return fetch("/api/unstable/invoke/".concat(result.invocation_ids[0]));
          case 6:
            firstInvocationResponse = _context8.v;
            if (!firstInvocationResponse.ok) {
              _context8.n = 8;
              break;
            }
            _context8.n = 7;
            return firstInvocationResponse.json();
          case 7:
            firstInvData = _context8.v;
            pollForTopicResults(result.invocation_ids, firstInvData.trace_id, eventForm.timeout_seconds);
            _context8.n = 9;
            break;
          case 8:
            // Fallback: poll without trace_id
            pollForTopicResults(result.invocation_ids, result.event_uid, eventForm.timeout_seconds);
          case 9:
            _context8.n = 11;
            break;
          case 10:
            setInvocationState({
              status: 'error',
              invocationId: null,
              traceId: null,
              result: null,
              error: result.detail || 'Failed to publish event'
            });
            setSendingEvent(false);
          case 11:
            _context8.n = 13;
            break;
          case 12:
            _context8.p = 12;
            _t6 = _context8.v;
            console.error('Error sending event:', _t6);
            setInvocationState({
              status: 'error',
              invocationId: null,
              traceId: null,
              result: null,
              error: 'Network error: ' + _t6.message
            });
            setSendingEvent(false);
          case 13:
            return _context8.a(2);
        }
      }, _callee8, null, [[2, 12]]);
    }));
    return function sendEvent() {
      return _ref9.apply(this, arguments);
    };
  }();
  var isInvoking = invocationState.status === 'pending' || invocationState.status === 'running';
  return /*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)(CardTitle, {
        className: "flex items-center",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Send, {
          className: "w-4 h-4 mr-2"
        }), "Test Agent"]
      })
    }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
      className: "pb-6",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "space-y-4",
        children: [!isTopicDetailsPage && !isAgentDetailsPage && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
            className: "block text-sm font-medium text-gray-700 mb-2",
            children: "Invocation Type"
          }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex rounded-lg border border-gray-300 overflow-hidden",
            children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
              type: "button",
              onClick: function onClick() {
                setInvocationType('function');
                setInvocationState({
                  status: 'idle',
                  invocationId: null,
                  traceId: null,
                  result: null,
                  error: null
                });
                // Auto-select first function
                var functions = getAgentFunctions();
                if (functions.length > 0 && !eventForm.functionName) {
                  handleFunctionChange(functions[0].functionName);
                }
              },
              disabled: !hasFunctions() || !isAgentReady,
              className: "flex-1 px-4 py-2 text-sm font-medium flex items-center justify-center gap-2 transition-colors ".concat(invocationType === 'function' ? 'bg-blue-50 text-blue-700 border-r border-blue-200' : 'bg-white text-gray-600 hover:bg-gray-50 border-r border-gray-300', " ").concat(!hasFunctions() || !isAgentReady ? 'opacity-50 cursor-not-allowed' : ''),
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(zap_Zap, {
                className: "w-4 h-4"
              }), "Function Call"]
            }), /*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
              type: "button",
              onClick: function onClick() {
                setInvocationType('topic');
                setInvocationState({
                  status: 'idle',
                  invocationId: null,
                  traceId: null,
                  result: null,
                  error: null
                });
                // Auto-select first topic
                var agentTopics = getAgentTopics();
                if (agentTopics.length > 0 && !eventForm.topic) {
                  var firstTopic = typeof agentTopics[0] === 'string' ? agentTopics[0] : agentTopics[0].topic;
                  handleTopicChange(firstTopic);
                }
              },
              disabled: !hasTopics() || !isAgentReady,
              className: "flex-1 px-4 py-2 text-sm font-medium flex items-center justify-center gap-2 transition-colors ".concat(invocationType === 'topic' ? 'bg-purple-50 text-purple-700' : 'bg-white text-gray-600 hover:bg-gray-50', " ").concat(!hasTopics() || !isAgentReady ? 'opacity-50 cursor-not-allowed' : ''),
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
                className: "w-4 h-4"
              }), "Topic Event"]
            })]
          }), selectedAgent && !isAgentReady && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center text-xs text-amber-600 mt-2",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
              className: "animate-spin rounded-full h-3 w-3 border-b border-amber-600 mr-1"
            }), "Loading agent capabilities..."]
          }), isAgentReady && !hasFunctions() && !hasTopics() && /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-xs text-amber-600 mt-2",
            children: "No handlers registered. Wait for agent to subscribe."
          })]
        }), !isTopicDetailsPage && invocationType === 'function' && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
            className: "block text-sm font-medium text-gray-700 mb-2",
            children: "Function"
          }), /*#__PURE__*/(0,jsx_runtime.jsxs)("select", {
            className: "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed",
            value: eventForm.functionName,
            onChange: function onChange(e) {
              return handleFunctionChange(e.target.value);
            },
            disabled: !isAgentReady || isInvoking,
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("option", {
              value: "",
              children: "Select a function"
            }), getAgentFunctions().map(function (func, index) {
              return /*#__PURE__*/(0,jsx_runtime.jsxs)("option", {
                value: func.functionName,
                children: [func.functionName, "()"]
              }, func.functionName || index);
            })]
          })]
        }), !isTopicDetailsPage && invocationType === 'topic' && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
            className: "block text-sm font-medium text-gray-700 mb-2",
            children: "Topic"
          }), /*#__PURE__*/(0,jsx_runtime.jsxs)("select", {
            className: "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 disabled:bg-gray-100 disabled:cursor-not-allowed",
            value: eventForm.topic,
            onChange: function onChange(e) {
              return handleTopicChange(e.target.value);
            },
            disabled: !isAgentReady || sendingEvent,
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("option", {
              value: "",
              children: "Select a topic"
            }), getAgentTopics().map(function (topicData, index) {
              var topicName = typeof topicData === 'string' ? topicData : (topicData === null || topicData === void 0 ? void 0 : topicData.topic) || 'unknown';
              return /*#__PURE__*/(0,jsx_runtime.jsx)("option", {
                value: topicName,
                children: topicName
              }, topicName || index);
            })]
          })]
        }), isTopicDetailsPage && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
            className: "block text-sm font-medium text-gray-700 mb-2",
            children: "Topic"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
            className: "w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700",
            children: eventForm.topic || 'No topic selected'
          })]
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex justify-between items-center mb-2",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
              className: "block text-sm font-medium text-gray-700",
              children: "JSON Payload"
            }), (eventForm.topic || eventForm.functionName) && /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
              type: "button",
              onClick: function onClick() {
                if (invocationType === 'function' && eventForm.functionName) {
                  handleFunctionChange(eventForm.functionName);
                } else if (eventForm.topic) {
                  populateWithSchemaExample(eventForm.topic, true); // Force refresh on manual click
                }
              },
              disabled: isLoadingSchema || isInvoking,
              className: "text-xs text-indigo-600 hover:text-indigo-500 disabled:text-gray-400 flex items-center",
              children: isLoadingSchema ? /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "animate-spin rounded-full h-3 w-3 border-b border-indigo-600 mr-1"
                }), "Loading..."]
              }) : /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Sparkles, {
                  className: "w-3 h-3 inline mr-1"
                }), "Auto-populate"]
              })
            })]
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("textarea", {
            className: "w-full px-3 py-2 border rounded-md shadow-sm font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 ".concat(jsonError ? 'border-red-500' : 'border-gray-300', " ").concat(isInvoking ? 'bg-gray-100' : ''),
            rows: "6",
            value: eventForm.payload,
            onChange: function onChange(e) {
              return handleFormChange('payload', e.target.value);
            },
            placeholder: "{\\n  \"message\": \"Hello from UI!\"\\n}",
            disabled: isInvoking
          }), jsonError && /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-red-500 text-sm mt-1",
            children: jsonError
          }), schemaError && /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-amber-600 text-sm mt-1",
            children: schemaError
          })]
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
            type: "button",
            onClick: function onClick() {
              return setShowAdvanced(!showAdvanced);
            },
            className: "flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              children: "Advanced Options"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("svg", {
              className: "ml-1 h-4 w-4 transform transition-transform ".concat(showAdvanced ? 'rotate-180' : ''),
              fill: "none",
              viewBox: "0 0 24 24",
              stroke: "currentColor",
              children: /*#__PURE__*/(0,jsx_runtime.jsx)("path", {
                strokeLinecap: "round",
                strokeLinejoin: "round",
                strokeWidth: 2,
                d: "M19 9l-7 7-7-7"
              })
            })]
          }), showAdvanced && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "mt-3 pt-3 border-t border-gray-200 space-y-4",
            children: [invocationType === 'function' && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex items-center justify-between mb-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("label", {
                  className: "text-sm font-medium text-gray-700 flex items-center gap-1",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)(clock_Clock, {
                    className: "w-4 h-4"
                  }), "Timeout"]
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-xs text-gray-500",
                  children: eventForm.timeout_seconds >= 3600 ? "".concat((eventForm.timeout_seconds / 3600).toFixed(1), " hour(s)") : "".concat(Math.round(eventForm.timeout_seconds / 60), " minute(s)")
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex items-center gap-3",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("input", {
                  type: "number",
                  className: "w-28 px-3 py-2 border border-gray-300 rounded-md shadow-sm font-mono text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500",
                  value: eventForm.timeout_seconds,
                  onChange: function onChange(e) {
                    var val = parseInt(e.target.value, 10);
                    if (!isNaN(val) && val >= 1 && val <= 86400) {
                      handleFormChange('timeout_seconds', val);
                    }
                  },
                  min: 1,
                  max: 86400,
                  disabled: isInvoking
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-600",
                  children: "seconds"
                }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "flex gap-1 ml-auto",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)("button", {
                    type: "button",
                    onClick: function onClick() {
                      return handleFormChange('timeout_seconds', 60);
                    },
                    disabled: isInvoking,
                    className: "px-2 py-1 text-xs border rounded transition-colors ".concat(eventForm.timeout_seconds === 60 ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50', " ").concat(isInvoking ? 'opacity-50 cursor-not-allowed' : ''),
                    children: "1m"
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
                    type: "button",
                    onClick: function onClick() {
                      return handleFormChange('timeout_seconds', 300);
                    },
                    disabled: isInvoking,
                    className: "px-2 py-1 text-xs border rounded transition-colors ".concat(eventForm.timeout_seconds === 300 ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50', " ").concat(isInvoking ? 'opacity-50 cursor-not-allowed' : ''),
                    children: "5m"
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
                    type: "button",
                    onClick: function onClick() {
                      return handleFormChange('timeout_seconds', 3600);
                    },
                    disabled: isInvoking,
                    className: "px-2 py-1 text-xs border rounded transition-colors ".concat(eventForm.timeout_seconds === 3600 ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50', " ").concat(isInvoking ? 'opacity-50 cursor-not-allowed' : ''),
                    children: "1h"
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
                    type: "button",
                    onClick: function onClick() {
                      return handleFormChange('timeout_seconds', 86400);
                    },
                    disabled: isInvoking,
                    className: "px-2 py-1 text-xs border rounded transition-colors ".concat(eventForm.timeout_seconds === 86400 ? 'bg-blue-50 border-blue-300 text-blue-700' : 'border-gray-300 text-gray-600 hover:bg-gray-50', " ").concat(isInvoking ? 'opacity-50 cursor-not-allowed' : ''),
                    children: "24h"
                  })]
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
                className: "mt-1 text-xs text-gray-500",
                children: "Maximum execution time for this invocation (1 second to 24 hours)"
              })]
            }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
                className: "block text-sm font-medium text-gray-700 mb-2",
                children: "Sender ID"
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("input", {
                type: "text",
                className: "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                value: eventForm.sender_id,
                onChange: function onChange(e) {
                  return handleFormChange('sender_id', e.target.value);
                },
                placeholder: "ui-test"
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
                className: "mt-1 text-xs text-gray-500",
                children: "Identifier for the sender of this test event"
              })]
            })]
          })]
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          children: invocationType === 'function' && !isTopicDetailsPage ? /*#__PURE__*/(0,jsx_runtime.jsx)(Button, {
            onClick: invokeFunction,
            disabled: sendingEvent || jsonError || !eventForm.functionName || !selectedAgent,
            className: "w-full bg-blue-600 hover:bg-blue-700",
            children: sendingEvent ? /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LoaderCircle, {
                className: "w-4 h-4 mr-2 animate-spin"
              }), "Invoking..."]
            }) : /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(zap_Zap, {
                className: "w-4 h-4 mr-2"
              }), "Invoke Function"]
            })
          }) : /*#__PURE__*/(0,jsx_runtime.jsx)(Button, {
            onClick: sendEvent,
            disabled: sendingEvent || jsonError || !eventForm.topic,
            className: "w-full bg-purple-600 hover:bg-purple-700",
            children: sendingEvent ? /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LoaderCircle, {
                className: "w-4 h-4 mr-2 animate-spin"
              }), "Sending..."]
            }) : /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
                className: "w-4 h-4 mr-2"
              }), "Send Topic Event"]
            })
          })
        }), invocationType === 'function' && invocationState.status !== 'idle' && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "rounded-lg p-4 space-y-3 ".concat(invocationState.status === 'completed' ? 'bg-green-50 border border-green-200' : invocationState.status === 'error' ? 'bg-red-50 border border-red-200' : 'bg-gray-50 border border-gray-200'),
          children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center justify-between",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-sm font-medium text-gray-700",
              children: "Invocation Status"
            }), invocationState.status === 'completed' && /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CircleCheck, {
                className: "w-3 h-3 mr-1"
              }), "Completed"]
            }), invocationState.status === 'error' && /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CircleX, {
                className: "w-3 h-3 mr-1"
              }), "Error"]
            }), (invocationState.status === 'pending' || invocationState.status === 'running') && /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LoaderCircle, {
                className: "w-3 h-3 mr-1 animate-spin"
              }), invocationState.status === 'pending' ? 'Starting...' : 'Running...']
            })]
          }), invocationState.invocationId && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center gap-2 text-xs",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-gray-500",
              children: "Invocation ID:"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("code", {
              className: "px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono",
              children: invocationState.invocationId
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
              onClick: function onClick() {
                return copyToClipboard(invocationState.invocationId);
              },
              className: "p-1 hover:bg-gray-200 rounded",
              title: "Copy to clipboard",
              children: /*#__PURE__*/(0,jsx_runtime.jsx)(Copy, {
                className: "w-3 h-3"
              })
            })]
          }), invocationState.traceId && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center gap-2 text-xs",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-gray-500",
              children: "Trace ID:"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("code", {
              className: "px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono",
              children: invocationState.traceId
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
              onClick: function onClick() {
                return copyToClipboard(invocationState.traceId);
              },
              className: "p-1 hover:bg-gray-200 rounded",
              title: "Copy to clipboard",
              children: /*#__PURE__*/(0,jsx_runtime.jsx)(Copy, {
                className: "w-3 h-3"
              })
            })]
          }), invocationState.status === 'completed' && invocationState.result && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "mt-3",
            children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "flex items-center justify-between mb-1",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                className: "text-sm font-medium text-green-800",
                children: "Result"
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
                onClick: function onClick() {
                  return copyToClipboard(JSON.stringify(invocationState.result, null, 2));
                },
                className: "text-xs text-gray-600 hover:text-gray-800 flex items-center",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Copy, {
                  className: "w-3 h-3 mr-1"
                }), "Copy"]
              })]
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
              className: "text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-gray-800",
              children: JSON.stringify(invocationState.result, null, 2)
            })]
          }), invocationState.status === 'error' && invocationState.error && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "mt-3",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-sm font-medium text-red-800",
              children: "Error"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
              className: "text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-red-700 mt-1",
              children: invocationState.error
            })]
          }), isInvoking && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center gap-2 text-sm text-gray-600",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LoaderCircle, {
              className: "w-4 h-4 animate-spin"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              children: "Waiting for function to complete..."
            })]
          })]
        }), invocationType === 'topic' && invocationState.status !== 'idle' && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "rounded-lg p-4 space-y-3 ".concat(invocationState.status === 'completed' ? 'bg-green-50 border border-green-200' : invocationState.status === 'error' ? 'bg-red-50 border border-red-200' : 'bg-gray-50 border border-gray-200'),
          children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center justify-between",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-sm font-medium text-gray-700",
              children: "Publish Status"
            }), invocationState.status === 'completed' && /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CircleCheck, {
                className: "w-3 h-3 mr-1"
              }), "Completed"]
            }), invocationState.status === 'error' && /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CircleX, {
                className: "w-3 h-3 mr-1"
              }), "Error"]
            }), (invocationState.status === 'pending' || invocationState.status === 'running') && /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LoaderCircle, {
                className: "w-3 h-3 mr-1 animate-spin"
              }), invocationState.status === 'pending' ? 'Publishing...' : 'Running handlers...']
            })]
          }), invocationState.invocationId && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center gap-2 text-xs",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-gray-500",
              children: "Invocation ID(s):"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("code", {
              className: "px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono text-xs",
              children: invocationState.invocationId.length > 40 ? invocationState.invocationId.substring(0, 40) + '...' : invocationState.invocationId
            })]
          }), invocationState.traceId && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center gap-2 text-xs",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-gray-500",
              children: "Trace ID:"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("code", {
              className: "px-1.5 py-0.5 bg-white rounded text-gray-600 font-mono",
              children: invocationState.traceId
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
              onClick: function onClick() {
                return copyToClipboard(invocationState.traceId);
              },
              className: "p-1 hover:bg-gray-200 rounded",
              title: "Copy to clipboard",
              children: /*#__PURE__*/(0,jsx_runtime.jsx)(Copy, {
                className: "w-3 h-3"
              })
            })]
          }), invocationState.status === 'completed' && invocationState.result && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "mt-3",
            children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "flex items-center justify-between mb-1",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                className: "text-sm font-medium text-green-800",
                children: "Result"
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
                onClick: function onClick() {
                  return copyToClipboard(JSON.stringify(invocationState.result, null, 2));
                },
                className: "text-xs text-gray-600 hover:text-gray-800 flex items-center",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Copy, {
                  className: "w-3 h-3 mr-1"
                }), "Copy"]
              })]
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
              className: "text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-gray-800",
              children: JSON.stringify(invocationState.result, null, 2)
            })]
          }), invocationState.status === 'error' && invocationState.error && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "mt-3",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-sm font-medium text-red-800",
              children: "Error"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
              className: "text-xs p-3 bg-white rounded-lg overflow-auto max-h-48 text-red-700 mt-1",
              children: invocationState.error
            })]
          }), (invocationState.status === 'pending' || invocationState.status === 'running') && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center gap-2 text-sm text-gray-600",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LoaderCircle, {
              className: "w-4 h-4 animate-spin"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              children: "Waiting for handlers to complete..."
            })]
          })]
        })]
      })
    })]
  });
};
/* harmony default export */ const components_SendTestEventCard = (SendTestEventCard);
;// ./node_modules/lucide-react/dist/esm/icons/message-circle.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const message_circle_iconNode = [
  ["path", { d: "M7.9 20A9 9 0 1 0 4 16.1L2 22Z", key: "vv11sd" }]
];
const MessageCircle = createLucideIcon("message-circle", message_circle_iconNode);


//# sourceMappingURL=message-circle.js.map

;// ./node_modules/lucide-react/dist/esm/icons/bot.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const bot_iconNode = [
  ["path", { d: "M12 8V4H8", key: "hb8ula" }],
  ["rect", { width: "16", height: "12", x: "4", y: "8", rx: "2", key: "enze0r" }],
  ["path", { d: "M2 14h2", key: "vft8re" }],
  ["path", { d: "M20 14h2", key: "4cs60a" }],
  ["path", { d: "M15 13v2", key: "1xurst" }],
  ["path", { d: "M9 13v2", key: "rq6x2g" }]
];
const bot_Bot = createLucideIcon("bot", bot_iconNode);


//# sourceMappingURL=bot.js.map

;// ./node_modules/lucide-react/dist/esm/icons/trash-2.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const trash_2_iconNode = [
  ["path", { d: "M3 6h18", key: "d0wm0j" }],
  ["path", { d: "M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6", key: "4alrt4" }],
  ["path", { d: "M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2", key: "v07s0e" }],
  ["line", { x1: "10", x2: "10", y1: "11", y2: "17", key: "1uufr5" }],
  ["line", { x1: "14", x2: "14", y1: "11", y2: "17", key: "xtxkd" }]
];
const Trash2 = createLucideIcon("trash-2", trash_2_iconNode);


//# sourceMappingURL=trash-2.js.map

;// ./node_modules/marked/lib/marked.esm.js
/**
 * marked v17.0.2 - a markdown parser
 * Copyright (c) 2018-2026, MarkedJS. (MIT License)
 * Copyright (c) 2011-2018, Christopher Jeffrey. (MIT License)
 * https://github.com/markedjs/marked
 */

/**
 * DO NOT EDIT THIS FILE
 * The code in this file is generated from files in ./src/
 */

function M(){return{async:!1,breaks:!1,extensions:null,gfm:!0,hooks:null,pedantic:!1,renderer:null,silent:!1,tokenizer:null,walkTokens:null}}var T=M();function H(u){T=u}var _={exec:()=>null};function k(u,e=""){let t=typeof u=="string"?u:u.source,n={replace:(r,i)=>{let s=typeof i=="string"?i:i.source;return s=s.replace(m.caret,"$1"),t=t.replace(r,s),n},getRegex:()=>new RegExp(t,e)};return n}var Re=(()=>{try{return!!new RegExp("(?<=1)(?<!1)")}catch{return!1}})(),m={codeRemoveIndent:/^(?: {1,4}| {0,3}\t)/gm,outputLinkReplace:/\\([\[\]])/g,indentCodeCompensation:/^(\s+)(?:```)/,beginningSpace:/^\s+/,endingHash:/#$/,startingSpaceChar:/^ /,endingSpaceChar:/ $/,nonSpaceChar:/[^ ]/,newLineCharGlobal:/\n/g,tabCharGlobal:/\t/g,multipleSpaceGlobal:/\s+/g,blankLine:/^[ \t]*$/,doubleBlankLine:/\n[ \t]*\n[ \t]*$/,blockquoteStart:/^ {0,3}>/,blockquoteSetextReplace:/\n {0,3}((?:=+|-+) *)(?=\n|$)/g,blockquoteSetextReplace2:/^ {0,3}>[ \t]?/gm,listReplaceNesting:/^ {1,4}(?=( {4})*[^ ])/g,listIsTask:/^\[[ xX]\] +\S/,listReplaceTask:/^\[[ xX]\] +/,listTaskCheckbox:/\[[ xX]\]/,anyLine:/\n.*\n/,hrefBrackets:/^<(.*)>$/,tableDelimiter:/[:|]/,tableAlignChars:/^\||\| *$/g,tableRowBlankLine:/\n[ \t]*$/,tableAlignRight:/^ *-+: *$/,tableAlignCenter:/^ *:-+: *$/,tableAlignLeft:/^ *:-+ *$/,startATag:/^<a /i,endATag:/^<\/a>/i,startPreScriptTag:/^<(pre|code|kbd|script)(\s|>)/i,endPreScriptTag:/^<\/(pre|code|kbd|script)(\s|>)/i,startAngleBracket:/^</,endAngleBracket:/>$/,pedanticHrefTitle:/^([^'"]*[^\s])\s+(['"])(.*)\2/,unicodeAlphaNumeric:/[\p{L}\p{N}]/u,escapeTest:/[&<>"']/,escapeReplace:/[&<>"']/g,escapeTestNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/,escapeReplaceNoEncode:/[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/g,unescapeTest:/&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig,caret:/(^|[^\[])\^/g,percentDecode:/%25/g,findPipe:/\|/g,splitPipe:/ \|/,slashPipe:/\\\|/g,carriageReturn:/\r\n|\r/g,spaceLine:/^ +$/gm,notSpaceStart:/^\S*/,endingNewline:/\n$/,listItemRegex:u=>new RegExp(`^( {0,3}${u})((?:[	 ][^\\n]*)?(?:\\n|$))`),nextBulletRegex:u=>new RegExp(`^ {0,${Math.min(3,u-1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`),hrRegex:u=>new RegExp(`^ {0,${Math.min(3,u-1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`),fencesBeginRegex:u=>new RegExp(`^ {0,${Math.min(3,u-1)}}(?:\`\`\`|~~~)`),headingBeginRegex:u=>new RegExp(`^ {0,${Math.min(3,u-1)}}#`),htmlBeginRegex:u=>new RegExp(`^ {0,${Math.min(3,u-1)}}<(?:[a-z].*>|!--)`,"i"),blockquoteBeginRegex:u=>new RegExp(`^ {0,${Math.min(3,u-1)}}>`)},Te=/^(?:[ \t]*(?:\n|$))+/,Oe=/^((?: {4}| {0,3}\t)[^\n]+(?:\n(?:[ \t]*(?:\n|$))*)?)+/,we=/^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/,I=/^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/,ye=/^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/,N=/ {0,3}(?:[*+-]|\d{1,9}[.)])/,re=/^(?!bull |blockCode|fences|blockquote|heading|html|table)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html|table))+?)\n {0,3}(=+|-+) *(?:\n+|$)/,se=k(re).replace(/bull/g,N).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/\|table/g,"").getRegex(),Pe=k(re).replace(/bull/g,N).replace(/blockCode/g,/(?: {4}| {0,3}\t)/).replace(/fences/g,/ {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g,/ {0,3}>/).replace(/heading/g,/ {0,3}#{1,6}/).replace(/html/g,/ {0,3}<[^\n>]+>\n/).replace(/table/g,/ {0,3}\|?(?:[:\- ]*\|)+[\:\- ]*\n/).getRegex(),Q=/^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/,Se=/^[^\n]+/,F=/(?!\s*\])(?:\\[\s\S]|[^\[\]\\])+/,$e=k(/^ {0,3}\[(label)\]: *(?:\n[ \t]*)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n[ \t]*)?| *\n[ \t]*)(title))? *(?:\n+|$)/).replace("label",F).replace("title",/(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(),_e=k(/^(bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g,N).getRegex(),q="address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul",j=/<!--(?:-?>|[\s\S]*?(?:-->|$))/,Le=k("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n[ 	]*)+\\n|$))","i").replace("comment",j).replace("tag",q).replace("attribute",/ +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(),ie=k(Q).replace("hr",I).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("|table","").replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)])[ \\t]").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",q).getRegex(),Me=k(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph",ie).getRegex(),U={blockquote:Me,code:Oe,def:$e,fences:we,heading:ye,hr:I,html:Le,lheading:se,list:_e,newline:Te,paragraph:ie,table:_,text:Se},te=k("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr",I).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("blockquote"," {0,3}>").replace("code","(?: {4}| {0,3}	)[^\\n]").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)])[ \\t]").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",q).getRegex(),ze={...U,lheading:Pe,table:te,paragraph:k(Q).replace("hr",I).replace("heading"," {0,3}#{1,6}(?:\\s|$)").replace("|lheading","").replace("table",te).replace("blockquote"," {0,3}>").replace("fences"," {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list"," {0,3}(?:[*+-]|1[.)])[ \\t]").replace("html","</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag",q).getRegex()},Ce={...U,html:k(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment",j).replace(/tag/g,"(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),def:/^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,heading:/^(#{1,6})(.*)(?:\n+|$)/,fences:_,lheading:/^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,paragraph:k(Q).replace("hr",I).replace("heading",` *#{1,6} *[^
]`).replace("lheading",se).replace("|table","").replace("blockquote"," {0,3}>").replace("|fences","").replace("|list","").replace("|html","").replace("|tag","").getRegex()},Ae=/^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/,Ie=/^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/,oe=/^( {2,}|\\)\n(?!\s*$)/,Ee=/^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/,v=/[\p{P}\p{S}]/u,K=/[\s\p{P}\p{S}]/u,ae=/[^\s\p{P}\p{S}]/u,Be=k(/^((?![*_])punctSpace)/,"u").replace(/punctSpace/g,K).getRegex(),le=/(?!~)[\p{P}\p{S}]/u,De=/(?!~)[\s\p{P}\p{S}]/u,qe=/(?:[^\s\p{P}\p{S}]|~)/u,ue=/(?![*_])[\p{P}\p{S}]/u,ve=/(?![*_])[\s\p{P}\p{S}]/u,Ge=/(?:[^\s\p{P}\p{S}]|[*_])/u,He=k(/link|precode-code|html/,"g").replace("link",/\[(?:[^\[\]`]|(?<a>`+)[^`]+\k<a>(?!`))*?\]\((?:\\[\s\S]|[^\\\(\)]|\((?:\\[\s\S]|[^\\\(\)])*\))*\)/).replace("precode-",Re?"(?<!`)()":"(^^|[^`])").replace("code",/(?<b>`+)[^`]+\k<b>(?!`)/).replace("html",/<(?! )[^<>]*?>/).getRegex(),pe=/^(?:\*+(?:((?!\*)punct)|[^\s*]))|^_+(?:((?!_)punct)|([^\s_]))/,Ze=k(pe,"u").replace(/punct/g,v).getRegex(),Ne=k(pe,"u").replace(/punct/g,le).getRegex(),ce="^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)punct(\\*+)(?=[\\s]|$)|notPunctSpace(\\*+)(?!\\*)(?=punctSpace|$)|(?!\\*)punctSpace(\\*+)(?=notPunctSpace)|[\\s](\\*+)(?!\\*)(?=punct)|(?!\\*)punct(\\*+)(?!\\*)(?=punct)|notPunctSpace(\\*+)(?=notPunctSpace)",Qe=k(ce,"gu").replace(/notPunctSpace/g,ae).replace(/punctSpace/g,K).replace(/punct/g,v).getRegex(),Fe=k(ce,"gu").replace(/notPunctSpace/g,qe).replace(/punctSpace/g,De).replace(/punct/g,le).getRegex(),je=k("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)punct(_+)(?=[\\s]|$)|notPunctSpace(_+)(?!_)(?=punctSpace|$)|(?!_)punctSpace(_+)(?=notPunctSpace)|[\\s](_+)(?!_)(?=punct)|(?!_)punct(_+)(?!_)(?=punct)","gu").replace(/notPunctSpace/g,ae).replace(/punctSpace/g,K).replace(/punct/g,v).getRegex(),Ue=k(/^~~?(?:((?!~)punct)|[^\s~])/,"u").replace(/punct/g,ue).getRegex(),Ke="^[^~]+(?=[^~])|(?!~)punct(~~?)(?=[\\s]|$)|notPunctSpace(~~?)(?!~)(?=punctSpace|$)|(?!~)punctSpace(~~?)(?=notPunctSpace)|[\\s](~~?)(?!~)(?=punct)|(?!~)punct(~~?)(?!~)(?=punct)|notPunctSpace(~~?)(?=notPunctSpace)",We=k(Ke,"gu").replace(/notPunctSpace/g,Ge).replace(/punctSpace/g,ve).replace(/punct/g,ue).getRegex(),Xe=k(/\\(punct)/,"gu").replace(/punct/g,v).getRegex(),Je=k(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme",/[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email",/[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(),Ve=k(j).replace("(?:-->|$)","-->").getRegex(),Ye=k("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment",Ve).replace("attribute",/\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(),D=/(?:\[(?:\\[\s\S]|[^\[\]\\])*\]|\\[\s\S]|`+[^`]*?`+(?!`)|[^\[\]\\`])*?/,et=k(/^!?\[(label)\]\(\s*(href)(?:(?:[ \t]*(?:\n[ \t]*)?)(title))?\s*\)/).replace("label",D).replace("href",/<(?:\\.|[^\n<>\\])+>|[^ \t\n\x00-\x1f]*/).replace("title",/"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(),he=k(/^!?\[(label)\]\[(ref)\]/).replace("label",D).replace("ref",F).getRegex(),ke=k(/^!?\[(ref)\](?:\[\])?/).replace("ref",F).getRegex(),tt=k("reflink|nolink(?!\\()","g").replace("reflink",he).replace("nolink",ke).getRegex(),ne=/[hH][tT][tT][pP][sS]?|[fF][tT][pP]/,W={_backpedal:_,anyPunctuation:Xe,autolink:Je,blockSkip:He,br:oe,code:Ie,del:_,delLDelim:_,delRDelim:_,emStrongLDelim:Ze,emStrongRDelimAst:Qe,emStrongRDelimUnd:je,escape:Ae,link:et,nolink:ke,punctuation:Be,reflink:he,reflinkSearch:tt,tag:Ye,text:Ee,url:_},nt={...W,link:k(/^!?\[(label)\]\((.*?)\)/).replace("label",D).getRegex(),reflink:k(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label",D).getRegex()},Z={...W,emStrongRDelimAst:Fe,emStrongLDelim:Ne,delLDelim:Ue,delRDelim:We,url:k(/^((?:protocol):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/).replace("protocol",ne).replace("email",/[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),_backpedal:/(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,del:/^(~~?)(?=[^\s~])((?:\\[\s\S]|[^\\])*?(?:\\[\s\S]|[^\s~\\]))\1(?=[^~]|$)/,text:k(/^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|protocol:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/).replace("protocol",ne).getRegex()},rt={...Z,br:k(oe).replace("{2,}","*").getRegex(),text:k(Z.text).replace("\\b_","\\b_| {2,}\\n").replace(/\{2,\}/g,"*").getRegex()},E={normal:U,gfm:ze,pedantic:Ce},z={normal:W,gfm:Z,breaks:rt,pedantic:nt};var st={"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"},de=u=>st[u];function O(u,e){if(e){if(m.escapeTest.test(u))return u.replace(m.escapeReplace,de)}else if(m.escapeTestNoEncode.test(u))return u.replace(m.escapeReplaceNoEncode,de);return u}function X(u){try{u=encodeURI(u).replace(m.percentDecode,"%")}catch{return null}return u}function J(u,e){let t=u.replace(m.findPipe,(i,s,a)=>{let o=!1,l=s;for(;--l>=0&&a[l]==="\\";)o=!o;return o?"|":" |"}),n=t.split(m.splitPipe),r=0;if(n[0].trim()||n.shift(),n.length>0&&!n.at(-1)?.trim()&&n.pop(),e)if(n.length>e)n.splice(e);else for(;n.length<e;)n.push("");for(;r<n.length;r++)n[r]=n[r].trim().replace(m.slashPipe,"|");return n}function C(u,e,t){let n=u.length;if(n===0)return"";let r=0;for(;r<n;){let i=u.charAt(n-r-1);if(i===e&&!t)r++;else if(i!==e&&t)r++;else break}return u.slice(0,n-r)}function ge(u,e){if(u.indexOf(e[1])===-1)return-1;let t=0;for(let n=0;n<u.length;n++)if(u[n]==="\\")n++;else if(u[n]===e[0])t++;else if(u[n]===e[1]&&(t--,t<0))return n;return t>0?-2:-1}function fe(u,e=0){let t=e,n="";for(let r of u)if(r==="	"){let i=4-t%4;n+=" ".repeat(i),t+=i}else n+=r,t++;return n}function me(u,e,t,n,r){let i=e.href,s=e.title||null,a=u[1].replace(r.other.outputLinkReplace,"$1");n.state.inLink=!0;let o={type:u[0].charAt(0)==="!"?"image":"link",raw:t,href:i,title:s,text:a,tokens:n.inlineTokens(a)};return n.state.inLink=!1,o}function it(u,e,t){let n=u.match(t.other.indentCodeCompensation);if(n===null)return e;let r=n[1];return e.split(`
`).map(i=>{let s=i.match(t.other.beginningSpace);if(s===null)return i;let[a]=s;return a.length>=r.length?i.slice(r.length):i}).join(`
`)}var w=class{options;rules;lexer;constructor(e){this.options=e||T}space(e){let t=this.rules.block.newline.exec(e);if(t&&t[0].length>0)return{type:"space",raw:t[0]}}code(e){let t=this.rules.block.code.exec(e);if(t){let n=t[0].replace(this.rules.other.codeRemoveIndent,"");return{type:"code",raw:t[0],codeBlockStyle:"indented",text:this.options.pedantic?n:C(n,`
`)}}}fences(e){let t=this.rules.block.fences.exec(e);if(t){let n=t[0],r=it(n,t[3]||"",this.rules);return{type:"code",raw:n,lang:t[2]?t[2].trim().replace(this.rules.inline.anyPunctuation,"$1"):t[2],text:r}}}heading(e){let t=this.rules.block.heading.exec(e);if(t){let n=t[2].trim();if(this.rules.other.endingHash.test(n)){let r=C(n,"#");(this.options.pedantic||!r||this.rules.other.endingSpaceChar.test(r))&&(n=r.trim())}return{type:"heading",raw:t[0],depth:t[1].length,text:n,tokens:this.lexer.inline(n)}}}hr(e){let t=this.rules.block.hr.exec(e);if(t)return{type:"hr",raw:C(t[0],`
`)}}blockquote(e){let t=this.rules.block.blockquote.exec(e);if(t){let n=C(t[0],`
`).split(`
`),r="",i="",s=[];for(;n.length>0;){let a=!1,o=[],l;for(l=0;l<n.length;l++)if(this.rules.other.blockquoteStart.test(n[l]))o.push(n[l]),a=!0;else if(!a)o.push(n[l]);else break;n=n.slice(l);let p=o.join(`
`),c=p.replace(this.rules.other.blockquoteSetextReplace,`
    $1`).replace(this.rules.other.blockquoteSetextReplace2,"");r=r?`${r}
${p}`:p,i=i?`${i}
${c}`:c;let d=this.lexer.state.top;if(this.lexer.state.top=!0,this.lexer.blockTokens(c,s,!0),this.lexer.state.top=d,n.length===0)break;let h=s.at(-1);if(h?.type==="code")break;if(h?.type==="blockquote"){let R=h,f=R.raw+`
`+n.join(`
`),S=this.blockquote(f);s[s.length-1]=S,r=r.substring(0,r.length-R.raw.length)+S.raw,i=i.substring(0,i.length-R.text.length)+S.text;break}else if(h?.type==="list"){let R=h,f=R.raw+`
`+n.join(`
`),S=this.list(f);s[s.length-1]=S,r=r.substring(0,r.length-h.raw.length)+S.raw,i=i.substring(0,i.length-R.raw.length)+S.raw,n=f.substring(s.at(-1).raw.length).split(`
`);continue}}return{type:"blockquote",raw:r,tokens:s,text:i}}}list(e){let t=this.rules.block.list.exec(e);if(t){let n=t[1].trim(),r=n.length>1,i={type:"list",raw:"",ordered:r,start:r?+n.slice(0,-1):"",loose:!1,items:[]};n=r?`\\d{1,9}\\${n.slice(-1)}`:`\\${n}`,this.options.pedantic&&(n=r?n:"[*+-]");let s=this.rules.other.listItemRegex(n),a=!1;for(;e;){let l=!1,p="",c="";if(!(t=s.exec(e))||this.rules.block.hr.test(e))break;p=t[0],e=e.substring(p.length);let d=fe(t[2].split(`
`,1)[0],t[1].length),h=e.split(`
`,1)[0],R=!d.trim(),f=0;if(this.options.pedantic?(f=2,c=d.trimStart()):R?f=t[1].length+1:(f=d.search(this.rules.other.nonSpaceChar),f=f>4?1:f,c=d.slice(f),f+=t[1].length),R&&this.rules.other.blankLine.test(h)&&(p+=h+`
`,e=e.substring(h.length+1),l=!0),!l){let S=this.rules.other.nextBulletRegex(f),V=this.rules.other.hrRegex(f),Y=this.rules.other.fencesBeginRegex(f),ee=this.rules.other.headingBeginRegex(f),xe=this.rules.other.htmlBeginRegex(f),be=this.rules.other.blockquoteBeginRegex(f);for(;e;){let G=e.split(`
`,1)[0],A;if(h=G,this.options.pedantic?(h=h.replace(this.rules.other.listReplaceNesting,"  "),A=h):A=h.replace(this.rules.other.tabCharGlobal,"    "),Y.test(h)||ee.test(h)||xe.test(h)||be.test(h)||S.test(h)||V.test(h))break;if(A.search(this.rules.other.nonSpaceChar)>=f||!h.trim())c+=`
`+A.slice(f);else{if(R||d.replace(this.rules.other.tabCharGlobal,"    ").search(this.rules.other.nonSpaceChar)>=4||Y.test(d)||ee.test(d)||V.test(d))break;c+=`
`+h}R=!h.trim(),p+=G+`
`,e=e.substring(G.length+1),d=A.slice(f)}}i.loose||(a?i.loose=!0:this.rules.other.doubleBlankLine.test(p)&&(a=!0)),i.items.push({type:"list_item",raw:p,task:!!this.options.gfm&&this.rules.other.listIsTask.test(c),loose:!1,text:c,tokens:[]}),i.raw+=p}let o=i.items.at(-1);if(o)o.raw=o.raw.trimEnd(),o.text=o.text.trimEnd();else return;i.raw=i.raw.trimEnd();for(let l of i.items){if(this.lexer.state.top=!1,l.tokens=this.lexer.blockTokens(l.text,[]),l.task){if(l.text=l.text.replace(this.rules.other.listReplaceTask,""),l.tokens[0]?.type==="text"||l.tokens[0]?.type==="paragraph"){l.tokens[0].raw=l.tokens[0].raw.replace(this.rules.other.listReplaceTask,""),l.tokens[0].text=l.tokens[0].text.replace(this.rules.other.listReplaceTask,"");for(let c=this.lexer.inlineQueue.length-1;c>=0;c--)if(this.rules.other.listIsTask.test(this.lexer.inlineQueue[c].src)){this.lexer.inlineQueue[c].src=this.lexer.inlineQueue[c].src.replace(this.rules.other.listReplaceTask,"");break}}let p=this.rules.other.listTaskCheckbox.exec(l.raw);if(p){let c={type:"checkbox",raw:p[0]+" ",checked:p[0]!=="[ ]"};l.checked=c.checked,i.loose?l.tokens[0]&&["paragraph","text"].includes(l.tokens[0].type)&&"tokens"in l.tokens[0]&&l.tokens[0].tokens?(l.tokens[0].raw=c.raw+l.tokens[0].raw,l.tokens[0].text=c.raw+l.tokens[0].text,l.tokens[0].tokens.unshift(c)):l.tokens.unshift({type:"paragraph",raw:c.raw,text:c.raw,tokens:[c]}):l.tokens.unshift(c)}}if(!i.loose){let p=l.tokens.filter(d=>d.type==="space"),c=p.length>0&&p.some(d=>this.rules.other.anyLine.test(d.raw));i.loose=c}}if(i.loose)for(let l of i.items){l.loose=!0;for(let p of l.tokens)p.type==="text"&&(p.type="paragraph")}return i}}html(e){let t=this.rules.block.html.exec(e);if(t)return{type:"html",block:!0,raw:t[0],pre:t[1]==="pre"||t[1]==="script"||t[1]==="style",text:t[0]}}def(e){let t=this.rules.block.def.exec(e);if(t){let n=t[1].toLowerCase().replace(this.rules.other.multipleSpaceGlobal," "),r=t[2]?t[2].replace(this.rules.other.hrefBrackets,"$1").replace(this.rules.inline.anyPunctuation,"$1"):"",i=t[3]?t[3].substring(1,t[3].length-1).replace(this.rules.inline.anyPunctuation,"$1"):t[3];return{type:"def",tag:n,raw:t[0],href:r,title:i}}}table(e){let t=this.rules.block.table.exec(e);if(!t||!this.rules.other.tableDelimiter.test(t[2]))return;let n=J(t[1]),r=t[2].replace(this.rules.other.tableAlignChars,"").split("|"),i=t[3]?.trim()?t[3].replace(this.rules.other.tableRowBlankLine,"").split(`
`):[],s={type:"table",raw:t[0],header:[],align:[],rows:[]};if(n.length===r.length){for(let a of r)this.rules.other.tableAlignRight.test(a)?s.align.push("right"):this.rules.other.tableAlignCenter.test(a)?s.align.push("center"):this.rules.other.tableAlignLeft.test(a)?s.align.push("left"):s.align.push(null);for(let a=0;a<n.length;a++)s.header.push({text:n[a],tokens:this.lexer.inline(n[a]),header:!0,align:s.align[a]});for(let a of i)s.rows.push(J(a,s.header.length).map((o,l)=>({text:o,tokens:this.lexer.inline(o),header:!1,align:s.align[l]})));return s}}lheading(e){let t=this.rules.block.lheading.exec(e);if(t)return{type:"heading",raw:t[0],depth:t[2].charAt(0)==="="?1:2,text:t[1],tokens:this.lexer.inline(t[1])}}paragraph(e){let t=this.rules.block.paragraph.exec(e);if(t){let n=t[1].charAt(t[1].length-1)===`
`?t[1].slice(0,-1):t[1];return{type:"paragraph",raw:t[0],text:n,tokens:this.lexer.inline(n)}}}text(e){let t=this.rules.block.text.exec(e);if(t)return{type:"text",raw:t[0],text:t[0],tokens:this.lexer.inline(t[0])}}escape(e){let t=this.rules.inline.escape.exec(e);if(t)return{type:"escape",raw:t[0],text:t[1]}}tag(e){let t=this.rules.inline.tag.exec(e);if(t)return!this.lexer.state.inLink&&this.rules.other.startATag.test(t[0])?this.lexer.state.inLink=!0:this.lexer.state.inLink&&this.rules.other.endATag.test(t[0])&&(this.lexer.state.inLink=!1),!this.lexer.state.inRawBlock&&this.rules.other.startPreScriptTag.test(t[0])?this.lexer.state.inRawBlock=!0:this.lexer.state.inRawBlock&&this.rules.other.endPreScriptTag.test(t[0])&&(this.lexer.state.inRawBlock=!1),{type:"html",raw:t[0],inLink:this.lexer.state.inLink,inRawBlock:this.lexer.state.inRawBlock,block:!1,text:t[0]}}link(e){let t=this.rules.inline.link.exec(e);if(t){let n=t[2].trim();if(!this.options.pedantic&&this.rules.other.startAngleBracket.test(n)){if(!this.rules.other.endAngleBracket.test(n))return;let s=C(n.slice(0,-1),"\\");if((n.length-s.length)%2===0)return}else{let s=ge(t[2],"()");if(s===-2)return;if(s>-1){let o=(t[0].indexOf("!")===0?5:4)+t[1].length+s;t[2]=t[2].substring(0,s),t[0]=t[0].substring(0,o).trim(),t[3]=""}}let r=t[2],i="";if(this.options.pedantic){let s=this.rules.other.pedanticHrefTitle.exec(r);s&&(r=s[1],i=s[3])}else i=t[3]?t[3].slice(1,-1):"";return r=r.trim(),this.rules.other.startAngleBracket.test(r)&&(this.options.pedantic&&!this.rules.other.endAngleBracket.test(n)?r=r.slice(1):r=r.slice(1,-1)),me(t,{href:r&&r.replace(this.rules.inline.anyPunctuation,"$1"),title:i&&i.replace(this.rules.inline.anyPunctuation,"$1")},t[0],this.lexer,this.rules)}}reflink(e,t){let n;if((n=this.rules.inline.reflink.exec(e))||(n=this.rules.inline.nolink.exec(e))){let r=(n[2]||n[1]).replace(this.rules.other.multipleSpaceGlobal," "),i=t[r.toLowerCase()];if(!i){let s=n[0].charAt(0);return{type:"text",raw:s,text:s}}return me(n,i,n[0],this.lexer,this.rules)}}emStrong(e,t,n=""){let r=this.rules.inline.emStrongLDelim.exec(e);if(!r||r[3]&&n.match(this.rules.other.unicodeAlphaNumeric))return;if(!(r[1]||r[2]||"")||!n||this.rules.inline.punctuation.exec(n)){let s=[...r[0]].length-1,a,o,l=s,p=0,c=r[0][0]==="*"?this.rules.inline.emStrongRDelimAst:this.rules.inline.emStrongRDelimUnd;for(c.lastIndex=0,t=t.slice(-1*e.length+s);(r=c.exec(t))!=null;){if(a=r[1]||r[2]||r[3]||r[4]||r[5]||r[6],!a)continue;if(o=[...a].length,r[3]||r[4]){l+=o;continue}else if((r[5]||r[6])&&s%3&&!((s+o)%3)){p+=o;continue}if(l-=o,l>0)continue;o=Math.min(o,o+l+p);let d=[...r[0]][0].length,h=e.slice(0,s+r.index+d+o);if(Math.min(s,o)%2){let f=h.slice(1,-1);return{type:"em",raw:h,text:f,tokens:this.lexer.inlineTokens(f)}}let R=h.slice(2,-2);return{type:"strong",raw:h,text:R,tokens:this.lexer.inlineTokens(R)}}}}codespan(e){let t=this.rules.inline.code.exec(e);if(t){let n=t[2].replace(this.rules.other.newLineCharGlobal," "),r=this.rules.other.nonSpaceChar.test(n),i=this.rules.other.startingSpaceChar.test(n)&&this.rules.other.endingSpaceChar.test(n);return r&&i&&(n=n.substring(1,n.length-1)),{type:"codespan",raw:t[0],text:n}}}br(e){let t=this.rules.inline.br.exec(e);if(t)return{type:"br",raw:t[0]}}del(e,t,n=""){let r=this.rules.inline.delLDelim.exec(e);if(!r)return;if(!(r[1]||"")||!n||this.rules.inline.punctuation.exec(n)){let s=[...r[0]].length-1,a,o,l=s,p=this.rules.inline.delRDelim;for(p.lastIndex=0,t=t.slice(-1*e.length+s);(r=p.exec(t))!=null;){if(a=r[1]||r[2]||r[3]||r[4]||r[5]||r[6],!a||(o=[...a].length,o!==s))continue;if(r[3]||r[4]){l+=o;continue}if(l-=o,l>0)continue;o=Math.min(o,o+l);let c=[...r[0]][0].length,d=e.slice(0,s+r.index+c+o),h=d.slice(s,-s);return{type:"del",raw:d,text:h,tokens:this.lexer.inlineTokens(h)}}}}autolink(e){let t=this.rules.inline.autolink.exec(e);if(t){let n,r;return t[2]==="@"?(n=t[1],r="mailto:"+n):(n=t[1],r=n),{type:"link",raw:t[0],text:n,href:r,tokens:[{type:"text",raw:n,text:n}]}}}url(e){let t;if(t=this.rules.inline.url.exec(e)){let n,r;if(t[2]==="@")n=t[0],r="mailto:"+n;else{let i;do i=t[0],t[0]=this.rules.inline._backpedal.exec(t[0])?.[0]??"";while(i!==t[0]);n=t[0],t[1]==="www."?r="http://"+t[0]:r=t[0]}return{type:"link",raw:t[0],text:n,href:r,tokens:[{type:"text",raw:n,text:n}]}}}inlineText(e){let t=this.rules.inline.text.exec(e);if(t){let n=this.lexer.state.inRawBlock;return{type:"text",raw:t[0],text:t[0],escaped:n}}}};var x=class u{tokens;options;state;inlineQueue;tokenizer;constructor(e){this.tokens=[],this.tokens.links=Object.create(null),this.options=e||T,this.options.tokenizer=this.options.tokenizer||new w,this.tokenizer=this.options.tokenizer,this.tokenizer.options=this.options,this.tokenizer.lexer=this,this.inlineQueue=[],this.state={inLink:!1,inRawBlock:!1,top:!0};let t={other:m,block:E.normal,inline:z.normal};this.options.pedantic?(t.block=E.pedantic,t.inline=z.pedantic):this.options.gfm&&(t.block=E.gfm,this.options.breaks?t.inline=z.breaks:t.inline=z.gfm),this.tokenizer.rules=t}static get rules(){return{block:E,inline:z}}static lex(e,t){return new u(t).lex(e)}static lexInline(e,t){return new u(t).inlineTokens(e)}lex(e){e=e.replace(m.carriageReturn,`
`),this.blockTokens(e,this.tokens);for(let t=0;t<this.inlineQueue.length;t++){let n=this.inlineQueue[t];this.inlineTokens(n.src,n.tokens)}return this.inlineQueue=[],this.tokens}blockTokens(e,t=[],n=!1){for(this.options.pedantic&&(e=e.replace(m.tabCharGlobal,"    ").replace(m.spaceLine,""));e;){let r;if(this.options.extensions?.block?.some(s=>(r=s.call({lexer:this},e,t))?(e=e.substring(r.raw.length),t.push(r),!0):!1))continue;if(r=this.tokenizer.space(e)){e=e.substring(r.raw.length);let s=t.at(-1);r.raw.length===1&&s!==void 0?s.raw+=`
`:t.push(r);continue}if(r=this.tokenizer.code(e)){e=e.substring(r.raw.length);let s=t.at(-1);s?.type==="paragraph"||s?.type==="text"?(s.raw+=(s.raw.endsWith(`
`)?"":`
`)+r.raw,s.text+=`
`+r.text,this.inlineQueue.at(-1).src=s.text):t.push(r);continue}if(r=this.tokenizer.fences(e)){e=e.substring(r.raw.length),t.push(r);continue}if(r=this.tokenizer.heading(e)){e=e.substring(r.raw.length),t.push(r);continue}if(r=this.tokenizer.hr(e)){e=e.substring(r.raw.length),t.push(r);continue}if(r=this.tokenizer.blockquote(e)){e=e.substring(r.raw.length),t.push(r);continue}if(r=this.tokenizer.list(e)){e=e.substring(r.raw.length),t.push(r);continue}if(r=this.tokenizer.html(e)){e=e.substring(r.raw.length),t.push(r);continue}if(r=this.tokenizer.def(e)){e=e.substring(r.raw.length);let s=t.at(-1);s?.type==="paragraph"||s?.type==="text"?(s.raw+=(s.raw.endsWith(`
`)?"":`
`)+r.raw,s.text+=`
`+r.raw,this.inlineQueue.at(-1).src=s.text):this.tokens.links[r.tag]||(this.tokens.links[r.tag]={href:r.href,title:r.title},t.push(r));continue}if(r=this.tokenizer.table(e)){e=e.substring(r.raw.length),t.push(r);continue}if(r=this.tokenizer.lheading(e)){e=e.substring(r.raw.length),t.push(r);continue}let i=e;if(this.options.extensions?.startBlock){let s=1/0,a=e.slice(1),o;this.options.extensions.startBlock.forEach(l=>{o=l.call({lexer:this},a),typeof o=="number"&&o>=0&&(s=Math.min(s,o))}),s<1/0&&s>=0&&(i=e.substring(0,s+1))}if(this.state.top&&(r=this.tokenizer.paragraph(i))){let s=t.at(-1);n&&s?.type==="paragraph"?(s.raw+=(s.raw.endsWith(`
`)?"":`
`)+r.raw,s.text+=`
`+r.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=s.text):t.push(r),n=i.length!==e.length,e=e.substring(r.raw.length);continue}if(r=this.tokenizer.text(e)){e=e.substring(r.raw.length);let s=t.at(-1);s?.type==="text"?(s.raw+=(s.raw.endsWith(`
`)?"":`
`)+r.raw,s.text+=`
`+r.text,this.inlineQueue.pop(),this.inlineQueue.at(-1).src=s.text):t.push(r);continue}if(e){let s="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(s);break}else throw new Error(s)}}return this.state.top=!0,t}inline(e,t=[]){return this.inlineQueue.push({src:e,tokens:t}),t}inlineTokens(e,t=[]){let n=e,r=null;if(this.tokens.links){let o=Object.keys(this.tokens.links);if(o.length>0)for(;(r=this.tokenizer.rules.inline.reflinkSearch.exec(n))!=null;)o.includes(r[0].slice(r[0].lastIndexOf("[")+1,-1))&&(n=n.slice(0,r.index)+"["+"a".repeat(r[0].length-2)+"]"+n.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex))}for(;(r=this.tokenizer.rules.inline.anyPunctuation.exec(n))!=null;)n=n.slice(0,r.index)+"++"+n.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);let i;for(;(r=this.tokenizer.rules.inline.blockSkip.exec(n))!=null;)i=r[2]?r[2].length:0,n=n.slice(0,r.index+i)+"["+"a".repeat(r[0].length-i-2)+"]"+n.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);n=this.options.hooks?.emStrongMask?.call({lexer:this},n)??n;let s=!1,a="";for(;e;){s||(a=""),s=!1;let o;if(this.options.extensions?.inline?.some(p=>(o=p.call({lexer:this},e,t))?(e=e.substring(o.raw.length),t.push(o),!0):!1))continue;if(o=this.tokenizer.escape(e)){e=e.substring(o.raw.length),t.push(o);continue}if(o=this.tokenizer.tag(e)){e=e.substring(o.raw.length),t.push(o);continue}if(o=this.tokenizer.link(e)){e=e.substring(o.raw.length),t.push(o);continue}if(o=this.tokenizer.reflink(e,this.tokens.links)){e=e.substring(o.raw.length);let p=t.at(-1);o.type==="text"&&p?.type==="text"?(p.raw+=o.raw,p.text+=o.text):t.push(o);continue}if(o=this.tokenizer.emStrong(e,n,a)){e=e.substring(o.raw.length),t.push(o);continue}if(o=this.tokenizer.codespan(e)){e=e.substring(o.raw.length),t.push(o);continue}if(o=this.tokenizer.br(e)){e=e.substring(o.raw.length),t.push(o);continue}if(o=this.tokenizer.del(e,n,a)){e=e.substring(o.raw.length),t.push(o);continue}if(o=this.tokenizer.autolink(e)){e=e.substring(o.raw.length),t.push(o);continue}if(!this.state.inLink&&(o=this.tokenizer.url(e))){e=e.substring(o.raw.length),t.push(o);continue}let l=e;if(this.options.extensions?.startInline){let p=1/0,c=e.slice(1),d;this.options.extensions.startInline.forEach(h=>{d=h.call({lexer:this},c),typeof d=="number"&&d>=0&&(p=Math.min(p,d))}),p<1/0&&p>=0&&(l=e.substring(0,p+1))}if(o=this.tokenizer.inlineText(l)){e=e.substring(o.raw.length),o.raw.slice(-1)!=="_"&&(a=o.raw.slice(-1)),s=!0;let p=t.at(-1);p?.type==="text"?(p.raw+=o.raw,p.text+=o.text):t.push(o);continue}if(e){let p="Infinite loop on byte: "+e.charCodeAt(0);if(this.options.silent){console.error(p);break}else throw new Error(p)}}return t}};var y=class{options;parser;constructor(e){this.options=e||T}space(e){return""}code({text:e,lang:t,escaped:n}){let r=(t||"").match(m.notSpaceStart)?.[0],i=e.replace(m.endingNewline,"")+`
`;return r?'<pre><code class="language-'+O(r)+'">'+(n?i:O(i,!0))+`</code></pre>
`:"<pre><code>"+(n?i:O(i,!0))+`</code></pre>
`}blockquote({tokens:e}){return`<blockquote>
${this.parser.parse(e)}</blockquote>
`}html({text:e}){return e}def(e){return""}heading({tokens:e,depth:t}){return`<h${t}>${this.parser.parseInline(e)}</h${t}>
`}hr(e){return`<hr>
`}list(e){let t=e.ordered,n=e.start,r="";for(let a=0;a<e.items.length;a++){let o=e.items[a];r+=this.listitem(o)}let i=t?"ol":"ul",s=t&&n!==1?' start="'+n+'"':"";return"<"+i+s+`>
`+r+"</"+i+`>
`}listitem(e){return`<li>${this.parser.parse(e.tokens)}</li>
`}checkbox({checked:e}){return"<input "+(e?'checked="" ':"")+'disabled="" type="checkbox"> '}paragraph({tokens:e}){return`<p>${this.parser.parseInline(e)}</p>
`}table(e){let t="",n="";for(let i=0;i<e.header.length;i++)n+=this.tablecell(e.header[i]);t+=this.tablerow({text:n});let r="";for(let i=0;i<e.rows.length;i++){let s=e.rows[i];n="";for(let a=0;a<s.length;a++)n+=this.tablecell(s[a]);r+=this.tablerow({text:n})}return r&&(r=`<tbody>${r}</tbody>`),`<table>
<thead>
`+t+`</thead>
`+r+`</table>
`}tablerow({text:e}){return`<tr>
${e}</tr>
`}tablecell(e){let t=this.parser.parseInline(e.tokens),n=e.header?"th":"td";return(e.align?`<${n} align="${e.align}">`:`<${n}>`)+t+`</${n}>
`}strong({tokens:e}){return`<strong>${this.parser.parseInline(e)}</strong>`}em({tokens:e}){return`<em>${this.parser.parseInline(e)}</em>`}codespan({text:e}){return`<code>${O(e,!0)}</code>`}br(e){return"<br>"}del({tokens:e}){return`<del>${this.parser.parseInline(e)}</del>`}link({href:e,title:t,tokens:n}){let r=this.parser.parseInline(n),i=X(e);if(i===null)return r;e=i;let s='<a href="'+e+'"';return t&&(s+=' title="'+O(t)+'"'),s+=">"+r+"</a>",s}image({href:e,title:t,text:n,tokens:r}){r&&(n=this.parser.parseInline(r,this.parser.textRenderer));let i=X(e);if(i===null)return O(n);e=i;let s=`<img src="${e}" alt="${n}"`;return t&&(s+=` title="${O(t)}"`),s+=">",s}text(e){return"tokens"in e&&e.tokens?this.parser.parseInline(e.tokens):"escaped"in e&&e.escaped?e.text:O(e.text)}};var $=class{strong({text:e}){return e}em({text:e}){return e}codespan({text:e}){return e}del({text:e}){return e}html({text:e}){return e}text({text:e}){return e}link({text:e}){return""+e}image({text:e}){return""+e}br(){return""}checkbox({raw:e}){return e}};var b=class u{options;renderer;textRenderer;constructor(e){this.options=e||T,this.options.renderer=this.options.renderer||new y,this.renderer=this.options.renderer,this.renderer.options=this.options,this.renderer.parser=this,this.textRenderer=new $}static parse(e,t){return new u(t).parse(e)}static parseInline(e,t){return new u(t).parseInline(e)}parse(e){let t="";for(let n=0;n<e.length;n++){let r=e[n];if(this.options.extensions?.renderers?.[r.type]){let s=r,a=this.options.extensions.renderers[s.type].call({parser:this},s);if(a!==!1||!["space","hr","heading","code","table","blockquote","list","html","def","paragraph","text"].includes(s.type)){t+=a||"";continue}}let i=r;switch(i.type){case"space":{t+=this.renderer.space(i);break}case"hr":{t+=this.renderer.hr(i);break}case"heading":{t+=this.renderer.heading(i);break}case"code":{t+=this.renderer.code(i);break}case"table":{t+=this.renderer.table(i);break}case"blockquote":{t+=this.renderer.blockquote(i);break}case"list":{t+=this.renderer.list(i);break}case"checkbox":{t+=this.renderer.checkbox(i);break}case"html":{t+=this.renderer.html(i);break}case"def":{t+=this.renderer.def(i);break}case"paragraph":{t+=this.renderer.paragraph(i);break}case"text":{t+=this.renderer.text(i);break}default:{let s='Token with "'+i.type+'" type was not found.';if(this.options.silent)return console.error(s),"";throw new Error(s)}}}return t}parseInline(e,t=this.renderer){let n="";for(let r=0;r<e.length;r++){let i=e[r];if(this.options.extensions?.renderers?.[i.type]){let a=this.options.extensions.renderers[i.type].call({parser:this},i);if(a!==!1||!["escape","html","link","image","strong","em","codespan","br","del","text"].includes(i.type)){n+=a||"";continue}}let s=i;switch(s.type){case"escape":{n+=t.text(s);break}case"html":{n+=t.html(s);break}case"link":{n+=t.link(s);break}case"image":{n+=t.image(s);break}case"checkbox":{n+=t.checkbox(s);break}case"strong":{n+=t.strong(s);break}case"em":{n+=t.em(s);break}case"codespan":{n+=t.codespan(s);break}case"br":{n+=t.br(s);break}case"del":{n+=t.del(s);break}case"text":{n+=t.text(s);break}default:{let a='Token with "'+s.type+'" type was not found.';if(this.options.silent)return console.error(a),"";throw new Error(a)}}}return n}};var P=class{options;block;constructor(e){this.options=e||T}static passThroughHooks=new Set(["preprocess","postprocess","processAllTokens","emStrongMask"]);static passThroughHooksRespectAsync=new Set(["preprocess","postprocess","processAllTokens"]);preprocess(e){return e}postprocess(e){return e}processAllTokens(e){return e}emStrongMask(e){return e}provideLexer(){return this.block?x.lex:x.lexInline}provideParser(){return this.block?b.parse:b.parseInline}};var B=class{defaults=M();options=this.setOptions;parse=this.parseMarkdown(!0);parseInline=this.parseMarkdown(!1);Parser=b;Renderer=y;TextRenderer=$;Lexer=x;Tokenizer=w;Hooks=P;constructor(...e){this.use(...e)}walkTokens(e,t){let n=[];for(let r of e)switch(n=n.concat(t.call(this,r)),r.type){case"table":{let i=r;for(let s of i.header)n=n.concat(this.walkTokens(s.tokens,t));for(let s of i.rows)for(let a of s)n=n.concat(this.walkTokens(a.tokens,t));break}case"list":{let i=r;n=n.concat(this.walkTokens(i.items,t));break}default:{let i=r;this.defaults.extensions?.childTokens?.[i.type]?this.defaults.extensions.childTokens[i.type].forEach(s=>{let a=i[s].flat(1/0);n=n.concat(this.walkTokens(a,t))}):i.tokens&&(n=n.concat(this.walkTokens(i.tokens,t)))}}return n}use(...e){let t=this.defaults.extensions||{renderers:{},childTokens:{}};return e.forEach(n=>{let r={...n};if(r.async=this.defaults.async||r.async||!1,n.extensions&&(n.extensions.forEach(i=>{if(!i.name)throw new Error("extension name required");if("renderer"in i){let s=t.renderers[i.name];s?t.renderers[i.name]=function(...a){let o=i.renderer.apply(this,a);return o===!1&&(o=s.apply(this,a)),o}:t.renderers[i.name]=i.renderer}if("tokenizer"in i){if(!i.level||i.level!=="block"&&i.level!=="inline")throw new Error("extension level must be 'block' or 'inline'");let s=t[i.level];s?s.unshift(i.tokenizer):t[i.level]=[i.tokenizer],i.start&&(i.level==="block"?t.startBlock?t.startBlock.push(i.start):t.startBlock=[i.start]:i.level==="inline"&&(t.startInline?t.startInline.push(i.start):t.startInline=[i.start]))}"childTokens"in i&&i.childTokens&&(t.childTokens[i.name]=i.childTokens)}),r.extensions=t),n.renderer){let i=this.defaults.renderer||new y(this.defaults);for(let s in n.renderer){if(!(s in i))throw new Error(`renderer '${s}' does not exist`);if(["options","parser"].includes(s))continue;let a=s,o=n.renderer[a],l=i[a];i[a]=(...p)=>{let c=o.apply(i,p);return c===!1&&(c=l.apply(i,p)),c||""}}r.renderer=i}if(n.tokenizer){let i=this.defaults.tokenizer||new w(this.defaults);for(let s in n.tokenizer){if(!(s in i))throw new Error(`tokenizer '${s}' does not exist`);if(["options","rules","lexer"].includes(s))continue;let a=s,o=n.tokenizer[a],l=i[a];i[a]=(...p)=>{let c=o.apply(i,p);return c===!1&&(c=l.apply(i,p)),c}}r.tokenizer=i}if(n.hooks){let i=this.defaults.hooks||new P;for(let s in n.hooks){if(!(s in i))throw new Error(`hook '${s}' does not exist`);if(["options","block"].includes(s))continue;let a=s,o=n.hooks[a],l=i[a];P.passThroughHooks.has(s)?i[a]=p=>{if(this.defaults.async&&P.passThroughHooksRespectAsync.has(s))return(async()=>{let d=await o.call(i,p);return l.call(i,d)})();let c=o.call(i,p);return l.call(i,c)}:i[a]=(...p)=>{if(this.defaults.async)return(async()=>{let d=await o.apply(i,p);return d===!1&&(d=await l.apply(i,p)),d})();let c=o.apply(i,p);return c===!1&&(c=l.apply(i,p)),c}}r.hooks=i}if(n.walkTokens){let i=this.defaults.walkTokens,s=n.walkTokens;r.walkTokens=function(a){let o=[];return o.push(s.call(this,a)),i&&(o=o.concat(i.call(this,a))),o}}this.defaults={...this.defaults,...r}}),this}setOptions(e){return this.defaults={...this.defaults,...e},this}lexer(e,t){return x.lex(e,t??this.defaults)}parser(e,t){return b.parse(e,t??this.defaults)}parseMarkdown(e){return(n,r)=>{let i={...r},s={...this.defaults,...i},a=this.onError(!!s.silent,!!s.async);if(this.defaults.async===!0&&i.async===!1)return a(new Error("marked(): The async option was set to true by an extension. Remove async: false from the parse options object to return a Promise."));if(typeof n>"u"||n===null)return a(new Error("marked(): input parameter is undefined or null"));if(typeof n!="string")return a(new Error("marked(): input parameter is of type "+Object.prototype.toString.call(n)+", string expected"));if(s.hooks&&(s.hooks.options=s,s.hooks.block=e),s.async)return(async()=>{let o=s.hooks?await s.hooks.preprocess(n):n,p=await(s.hooks?await s.hooks.provideLexer():e?x.lex:x.lexInline)(o,s),c=s.hooks?await s.hooks.processAllTokens(p):p;s.walkTokens&&await Promise.all(this.walkTokens(c,s.walkTokens));let h=await(s.hooks?await s.hooks.provideParser():e?b.parse:b.parseInline)(c,s);return s.hooks?await s.hooks.postprocess(h):h})().catch(a);try{s.hooks&&(n=s.hooks.preprocess(n));let l=(s.hooks?s.hooks.provideLexer():e?x.lex:x.lexInline)(n,s);s.hooks&&(l=s.hooks.processAllTokens(l)),s.walkTokens&&this.walkTokens(l,s.walkTokens);let c=(s.hooks?s.hooks.provideParser():e?b.parse:b.parseInline)(l,s);return s.hooks&&(c=s.hooks.postprocess(c)),c}catch(o){return a(o)}}}onError(e,t){return n=>{if(n.message+=`
Please report this to https://github.com/markedjs/marked.`,e){let r="<p>An error occurred:</p><pre>"+O(n.message+"",!0)+"</pre>";return t?Promise.resolve(r):r}if(t)return Promise.reject(n);throw n}}};var L=new B;function g(u,e){return L.parse(u,e)}g.options=g.setOptions=function(u){return L.setOptions(u),g.defaults=L.defaults,H(g.defaults),g};g.getDefaults=M;g.defaults=T;g.use=function(...u){return L.use(...u),g.defaults=L.defaults,H(g.defaults),g};g.walkTokens=function(u,e){return L.walkTokens(u,e)};g.parseInline=L.parseInline;g.Parser=b;g.parser=b.parse;g.Renderer=y;g.TextRenderer=$;g.Lexer=x;g.lexer=x.lex;g.Tokenizer=w;g.Hooks=P;g.parse=g;var Ut=g.options,Kt=g.setOptions,Wt=g.use,Xt=g.walkTokens,Jt=g.parseInline,Vt=(/* unused pure expression or super */ null && (g)),Yt=b.parse,en=x.lex;
//# sourceMappingURL=marked.esm.js.map

;// ./node_modules/lucide-react/dist/esm/icons/settings.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const settings_iconNode = [
  [
    "path",
    {
      d: "M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z",
      key: "1qme2f"
    }
  ],
  ["circle", { cx: "12", cy: "12", r: "3", key: "1v7zrd" }]
];
const Settings = createLucideIcon("settings", settings_iconNode);


//# sourceMappingURL=settings.js.map

;// ./node_modules/lucide-react/dist/esm/icons/user.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const user_iconNode = [
  ["path", { d: "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2", key: "975kel" }],
  ["circle", { cx: "12", cy: "7", r: "4", key: "17ys0d" }]
];
const User = createLucideIcon("user", user_iconNode);


//# sourceMappingURL=user.js.map

;// ./node_modules/lucide-react/dist/esm/icons/wrench.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const wrench_iconNode = [
  [
    "path",
    {
      d: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
      key: "cbrjhi"
    }
  ]
];
const Wrench = createLucideIcon("wrench", wrench_iconNode);


//# sourceMappingURL=wrench.js.map

;// ./node_modules/lucide-react/dist/esm/icons/message-square.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const message_square_iconNode = [
  ["path", { d: "M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z", key: "1lielz" }]
];
const message_square_MessageSquare = createLucideIcon("message-square", message_square_iconNode);


//# sourceMappingURL=message-square.js.map

;// ./node_modules/lucide-react/dist/esm/icons/file-text.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const file_text_iconNode = [
  ["path", { d: "M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z", key: "1rqfz7" }],
  ["path", { d: "M14 2v4a2 2 0 0 0 2 2h4", key: "tnqrlb" }],
  ["path", { d: "M10 9H8", key: "b1mrlr" }],
  ["path", { d: "M16 13H8", key: "t4e002" }],
  ["path", { d: "M16 17H8", key: "z1uh3a" }]
];
const FileText = createLucideIcon("file-text", file_text_iconNode);


//# sourceMappingURL=file-text.js.map

;// ./node_modules/lucide-react/dist/esm/icons/code.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const code_iconNode = [
  ["polyline", { points: "16 18 22 12 16 6", key: "z7tu5w" }],
  ["polyline", { points: "8 6 2 12 8 18", key: "1eg1df" }]
];
const Code = createLucideIcon("code", code_iconNode);


//# sourceMappingURL=code.js.map

;// ./node_modules/lucide-react/dist/esm/icons/chevron-up.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const chevron_up_iconNode = [["path", { d: "m18 15-6-6-6 6", key: "153udz" }]];
const chevron_up_ChevronUp = createLucideIcon("chevron-up", chevron_up_iconNode);


//# sourceMappingURL=chevron-up.js.map

;// ./node_modules/lucide-react/dist/esm/icons/chevron-down.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const chevron_down_iconNode = [["path", { d: "m6 9 6 6 6-6", key: "qrunsl" }]];
const chevron_down_ChevronDown = createLucideIcon("chevron-down", chevron_down_iconNode);


//# sourceMappingURL=chevron-down.js.map

;// ./src/components/LLMCallCard.jsx
function LLMCallCard_slicedToArray(r, e) { return LLMCallCard_arrayWithHoles(r) || LLMCallCard_iterableToArrayLimit(r, e) || LLMCallCard_unsupportedIterableToArray(r, e) || LLMCallCard_nonIterableRest(); }
function LLMCallCard_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function LLMCallCard_unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return LLMCallCard_arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? LLMCallCard_arrayLikeToArray(r, a) : void 0; } }
function LLMCallCard_arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function LLMCallCard_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function LLMCallCard_arrayWithHoles(r) { if (Array.isArray(r)) return r; }





// Configure marked for GFM support

g.setOptions({
  gfm: true,
  breaks: false
});

// Markdown content renderer with toggle
var MarkdownContent = function MarkdownContent(_ref) {
  var content = _ref.content,
    _ref$className = _ref.className,
    className = _ref$className === void 0 ? '' : _ref$className;
  var html = (0,react.useMemo)(function () {
    return g.parse(content || '');
  }, [content]);
  return /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
    className: "markdown-content max-w-none text-sm text-gray-700 ".concat(className),
    dangerouslySetInnerHTML: {
      __html: html
    }
  });
};

// Provider color coding
function getProviderColor(provider) {
  switch (provider === null || provider === void 0 ? void 0 : provider.toLowerCase()) {
    case 'openai':
      return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    case 'anthropic':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'google':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
}

// Finish reason badge
function getFinishReasonBadge(finishReason) {
  switch (finishReason) {
    case 'stop':
      return /*#__PURE__*/_jsx(Badge, {
        className: "text-xs bg-green-100 text-green-800",
        children: "Completed"
      });
    case 'tool_calls':
      return /*#__PURE__*/_jsx(Badge, {
        className: "text-xs bg-amber-100 text-amber-800",
        children: "Tool Calls"
      });
    case 'length':
      return /*#__PURE__*/_jsx(Badge, {
        className: "text-xs bg-gray-100 text-gray-800",
        children: "Max Length"
      });
    default:
      return /*#__PURE__*/_jsx(Badge, {
        variant: "outline",
        className: "text-xs",
        children: finishReason || 'Unknown'
      });
  }
}

// Format cost
function formatCost(cost) {
  if (cost === undefined || cost === null) return '-';
  if (cost < 0.0001) return '<$0.0001';
  if (cost < 0.01) return "$".concat(cost.toFixed(4));
  return "$".concat(cost.toFixed(2));
}

// Format latency
function formatLatency(ms) {
  if (ms === undefined || ms === null) return '-';
  if (ms < 1000) return "".concat(ms, "ms");
  return "".concat((ms / 1000).toFixed(2), "s");
}

// Get role icon and styling
function getRoleConfig(role) {
  switch (role) {
    case 'system':
      return {
        icon: Settings,
        bgColor: 'bg-purple-50',
        borderColor: 'border-purple-200',
        textColor: 'text-purple-800',
        iconColor: 'text-purple-600',
        label: 'System'
      };
    case 'user':
      return {
        icon: User,
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        textColor: 'text-blue-800',
        iconColor: 'text-blue-600',
        label: 'User'
      };
    case 'assistant':
      return {
        icon: bot_Bot,
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
        textColor: 'text-green-800',
        iconColor: 'text-green-600',
        label: 'Assistant'
      };
    case 'tool':
      return {
        icon: Wrench,
        bgColor: 'bg-amber-50',
        borderColor: 'border-amber-200',
        textColor: 'text-amber-800',
        iconColor: 'text-amber-600',
        label: 'Tool Result'
      };
    default:
      return {
        icon: message_square_MessageSquare,
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
        textColor: 'text-gray-800',
        iconColor: 'text-gray-600',
        label: role || 'Message'
      };
  }
}

// Individual message card component
var LLMMessageCard = function LLMMessageCard(_ref2) {
  var message = _ref2.message,
    index = _ref2.index;
  var _useState = (0,react.useState)(false),
    _useState2 = LLMCallCard_slicedToArray(_useState, 2),
    isExpanded = _useState2[0],
    setIsExpanded = _useState2[1];
  var _useState3 = (0,react.useState)(false),
    _useState4 = LLMCallCard_slicedToArray(_useState3, 2),
    showRaw = _useState4[0],
    setShowRaw = _useState4[1]; // Default to markdown view
  var config = getRoleConfig(message.role);
  var Icon = config.icon;

  // Get content - handle string or object
  var content = '';
  if (typeof message.content === 'string') {
    content = message.content;
  } else if (Array.isArray(message.content)) {
    // Handle multi-part content (e.g., images + text)
    content = message.content.map(function (part) {
      if (typeof part === 'string') return part;
      if (part.type === 'text') return part.text;
      if (part.type === 'image_url') return '[Image]';
      return JSON.stringify(part);
    }).join('\n');
  } else if (message.content) {
    content = JSON.stringify(message.content, null, 2);
  }

  // For assistant messages with no content but with tool_calls, show the tool calls inline
  var hasToolCallsOnly = message.role === 'assistant' && !content && message.tool_calls && message.tool_calls.length > 0;
  var maxLength = 500;
  var needsTruncation = content.length > maxLength && showRaw;
  var displayContent = isExpanded || !needsTruncation ? content : content.slice(0, maxLength) + '...';

  // Check if content likely has markdown (heuristic)
  var hasMarkdownSyntax = content && (content.includes('```') || content.includes('**') || content.includes('# ') || content.includes('- ') || content.includes('1. ') || content.includes('[') && content.includes(']('));
  return /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
    className: "rounded-lg border ".concat(config.borderColor, " ").concat(config.bgColor, " p-3"),
    children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-start gap-2",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "flex-shrink-0 w-6 h-6 rounded-full ".concat(config.bgColor, " flex items-center justify-center"),
        children: /*#__PURE__*/(0,jsx_runtime.jsx)(Icon, {
          className: "w-4 h-4 ".concat(config.iconColor)
        })
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex-1 min-w-0",
        children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex items-center justify-between gap-2 mb-1",
          children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center gap-2",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-xs font-semibold ".concat(config.textColor),
              children: config.label
            }), message.role === 'assistant' && message._model && /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-xs text-gray-400 font-mono font-normal",
              children: message._model
            }), message.name && /*#__PURE__*/(0,jsx_runtime.jsx)(badge_Badge, {
              variant: "outline",
              className: "text-xs",
              children: message.name
            }), message.tool_call_id && /*#__PURE__*/(0,jsx_runtime.jsxs)(badge_Badge, {
              variant: "outline",
              className: "text-xs bg-amber-50",
              children: ["ID: ", message.tool_call_id.slice(0, 8), "..."]
            })]
          }), content && /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
            onClick: function onClick(e) {
              e.stopPropagation();
              setShowRaw(!showRaw);
            },
            className: "flex items-center gap-1 px-2 py-0.5 rounded text-xs transition-colors ".concat(showRaw ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' : 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'),
            title: showRaw ? 'Switch to rendered markdown' : 'Switch to raw text',
            children: showRaw ? /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(FileText, {
                className: "w-3 h-3"
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                children: "Markdown"
              })]
            }) : /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Code, {
                className: "w-3 h-3"
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                children: "Raw"
              })]
            })
          })]
        }), hasToolCallsOnly ?
        /*#__PURE__*/
        /* Show tool calls inline when assistant message has no text content */
        (0,jsx_runtime.jsx)("div", {
          className: "space-y-2",
          children: message.tool_calls.map(function (toolCall, idx) {
            var _toolCall$function;
            var functionName = ((_toolCall$function = toolCall.function) === null || _toolCall$function === void 0 ? void 0 : _toolCall$function.name) || 'unknown';
            var args = '';
            try {
              var _toolCall$function2, _toolCall$function3;
              if (typeof ((_toolCall$function2 = toolCall.function) === null || _toolCall$function2 === void 0 ? void 0 : _toolCall$function2.arguments) === 'string') {
                args = JSON.stringify(JSON.parse(toolCall.function.arguments), null, 2);
              } else if ((_toolCall$function3 = toolCall.function) !== null && _toolCall$function3 !== void 0 && _toolCall$function3.arguments) {
                args = JSON.stringify(toolCall.function.arguments, null, 2);
              }
            } catch (_unused) {
              var _toolCall$function4;
              args = ((_toolCall$function4 = toolCall.function) === null || _toolCall$function4 === void 0 ? void 0 : _toolCall$function4.arguments) || '';
            }
            return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "bg-amber-50 border border-amber-200 rounded p-2",
              children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex items-center gap-2 mb-1",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)(zap_Zap, {
                  className: "w-3.5 h-3.5 text-amber-600"
                }), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                  className: "text-xs font-semibold text-amber-800",
                  children: ["Calling: ", functionName]
                }), toolCall.id && /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                  className: "text-xs text-amber-600",
                  children: ["ID: ", toolCall.id.slice(0, 8), "..."]
                })]
              }), args && /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
                className: "text-xs font-mono text-gray-700 whitespace-pre-wrap break-words bg-amber-100/50 rounded p-1.5 mt-1",
                children: args
              })]
            }, idx);
          })
        }) : showRaw ? /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "text-sm text-gray-700 whitespace-pre-wrap break-words font-mono bg-white/50 rounded p-2",
          children: displayContent
        }) : /*#__PURE__*/(0,jsx_runtime.jsx)(MarkdownContent, {
          content: displayContent
        }), needsTruncation && /*#__PURE__*/(0,jsx_runtime.jsx)("button", {
          onClick: function onClick() {
            return setIsExpanded(!isExpanded);
          },
          className: "flex items-center gap-1 mt-2 text-xs text-indigo-600 hover:text-indigo-500",
          children: isExpanded ? /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(chevron_up_ChevronUp, {
              className: "w-3 h-3"
            }), "Show less"]
          }) : /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(chevron_down_ChevronDown, {
              className: "w-3 h-3"
            }), "Show more"]
          })
        })]
      })]
    })
  });
};

// Main LLM Call Card component
var LLMCallCard = function LLMCallCard(_ref3) {
  var _llmCall$input_tokens, _llmCall$output_token;
  var llmCall = _ref3.llmCall;
  var _useState5 = useState(true),
    _useState6 = LLMCallCard_slicedToArray(_useState5, 2),
    isExpanded = _useState6[0],
    setIsExpanded = _useState6[1]; // Default expanded
  var messages = llmCall.messages || [];
  var toolCalls = llmCall.tool_calls || [];
  var totalTokens = (llmCall.input_tokens || 0) + (llmCall.output_tokens || 0);
  return /*#__PURE__*/_jsxs("div", {
    className: "rounded-lg border border-indigo-200 bg-gradient-to-r from-indigo-50 to-purple-50 overflow-hidden",
    children: [/*#__PURE__*/_jsxs("div", {
      className: "p-3 cursor-pointer hover:bg-indigo-100/50 transition-colors",
      onClick: function onClick() {
        return setIsExpanded(!isExpanded);
      },
      children: [/*#__PURE__*/_jsxs("div", {
        className: "flex items-start justify-between gap-3",
        children: [/*#__PURE__*/_jsxs("div", {
          className: "flex items-start gap-3",
          children: [/*#__PURE__*/_jsx("div", {
            className: "flex-shrink-0 w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center",
            children: /*#__PURE__*/_jsx(Bot, {
              className: "w-5 h-5 text-indigo-600"
            })
          }), /*#__PURE__*/_jsx("div", {
            className: "min-w-0",
            children: /*#__PURE__*/_jsxs("div", {
              className: "flex items-center gap-2 flex-wrap",
              children: [/*#__PURE__*/_jsx("span", {
                className: "font-semibold text-gray-900",
                children: llmCall.model || 'Unknown Model'
              }), llmCall.provider && /*#__PURE__*/_jsx(Badge, {
                className: "text-xs border ".concat(getProviderColor(llmCall.provider)),
                children: llmCall.provider
              }), getFinishReasonBadge(llmCall.finish_reason), llmCall.logged_externally && /*#__PURE__*/_jsx(Badge, {
                className: "text-xs bg-gray-100 text-gray-600",
                children: "Logged Externally"
              })]
            })
          })]
        }), /*#__PURE__*/_jsxs("div", {
          className: "flex items-center gap-2",
          children: [/*#__PURE__*/_jsx("span", {
            className: "text-sm font-semibold text-gray-900",
            children: formatCost(llmCall.cost_usd)
          }), isExpanded ? /*#__PURE__*/_jsx(ChevronUp, {
            className: "w-4 h-4 text-gray-500"
          }) : /*#__PURE__*/_jsx(ChevronDown, {
            className: "w-4 h-4 text-gray-500"
          })]
        })]
      }), /*#__PURE__*/_jsxs("div", {
        className: "flex items-center gap-4 mt-2 text-xs text-gray-600",
        children: [/*#__PURE__*/_jsxs("div", {
          className: "flex items-center gap-1",
          children: [/*#__PURE__*/_jsx(Clock, {
            className: "w-3.5 h-3.5"
          }), /*#__PURE__*/_jsx("span", {
            children: formatLatency(llmCall.latency_ms)
          })]
        }), /*#__PURE__*/_jsxs("div", {
          className: "flex items-center gap-1",
          children: [/*#__PURE__*/_jsx(Hash, {
            className: "w-3.5 h-3.5"
          }), /*#__PURE__*/_jsxs("span", {
            children: [totalTokens.toLocaleString(), " tokens"]
          }), /*#__PURE__*/_jsxs("span", {
            className: "text-gray-400",
            children: ["(", ((_llmCall$input_tokens = llmCall.input_tokens) === null || _llmCall$input_tokens === void 0 ? void 0 : _llmCall$input_tokens.toLocaleString()) || 0, " in / ", ((_llmCall$output_token = llmCall.output_tokens) === null || _llmCall$output_token === void 0 ? void 0 : _llmCall$output_token.toLocaleString()) || 0, " out)"]
          })]
        }), toolCalls.length > 0 && /*#__PURE__*/_jsxs("div", {
          className: "flex items-center gap-1 text-amber-600",
          children: [/*#__PURE__*/_jsx(Zap, {
            className: "w-3.5 h-3.5"
          }), /*#__PURE__*/_jsxs("span", {
            children: [toolCalls.length, " tool call", toolCalls.length !== 1 ? 's' : '']
          })]
        }), messages.length > 0 && /*#__PURE__*/_jsxs("div", {
          className: "flex items-center gap-1 text-gray-500",
          children: [/*#__PURE__*/_jsx(MessageSquare, {
            className: "w-3.5 h-3.5"
          }), /*#__PURE__*/_jsxs("span", {
            children: [messages.length, " message", messages.length !== 1 ? 's' : '']
          })]
        })]
      })]
    }), isExpanded && /*#__PURE__*/_jsxs("div", {
      className: "border-t border-indigo-100 bg-white/50 p-3 space-y-2",
      children: [messages.map(function (message, index) {
        return /*#__PURE__*/_jsx(LLMMessageCard, {
          message: message,
          index: index
        }, index);
      }), llmCall.response_content && !messages.some(function (m) {
        return m.role === 'assistant' && m.content === llmCall.response_content;
      }) && /*#__PURE__*/_jsx(LLMMessageCard, {
        message: {
          role: 'assistant',
          content: llmCall.response_content
        },
        index: messages.length
      })]
    })]
  });
};

// Export LLMMessageCard for use in unified trace view

/* harmony default export */ const components_LLMCallCard = ((/* unused pure expression or super */ null && (LLMCallCard)));
;// ./src/components/MessageFeedCard.jsx
function MessageFeedCard_typeof(o) { "@babel/helpers - typeof"; return MessageFeedCard_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, MessageFeedCard_typeof(o); }
var MessageFeedCard_excluded = ["children"];
function MessageFeedCard_ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function MessageFeedCard_objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? MessageFeedCard_ownKeys(Object(t), !0).forEach(function (r) { MessageFeedCard_defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : MessageFeedCard_ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function MessageFeedCard_defineProperty(e, r, t) { return (r = MessageFeedCard_toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function MessageFeedCard_toPropertyKey(t) { var i = MessageFeedCard_toPrimitive(t, "string"); return "symbol" == MessageFeedCard_typeof(i) ? i : i + ""; }
function MessageFeedCard_toPrimitive(t, r) { if ("object" != MessageFeedCard_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != MessageFeedCard_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function MessageFeedCard_toConsumableArray(r) { return MessageFeedCard_arrayWithoutHoles(r) || MessageFeedCard_iterableToArray(r) || MessageFeedCard_unsupportedIterableToArray(r) || MessageFeedCard_nonIterableSpread(); }
function MessageFeedCard_nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function MessageFeedCard_iterableToArray(r) { if ("undefined" != typeof Symbol && null != r[Symbol.iterator] || null != r["@@iterator"]) return Array.from(r); }
function MessageFeedCard_arrayWithoutHoles(r) { if (Array.isArray(r)) return MessageFeedCard_arrayLikeToArray(r); }
function MessageFeedCard_objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = MessageFeedCard_objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function MessageFeedCard_objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }
function MessageFeedCard_createForOfIteratorHelper(r, e) { var t = "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (!t) { if (Array.isArray(r) || (t = MessageFeedCard_unsupportedIterableToArray(r)) || e && r && "number" == typeof r.length) { t && (r = t); var _n = 0, F = function F() {}; return { s: F, n: function n() { return _n >= r.length ? { done: !0 } : { done: !1, value: r[_n++] }; }, e: function e(r) { throw r; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var o, a = !0, u = !1; return { s: function s() { t = t.call(r); }, n: function n() { var r = t.next(); return a = r.done, r; }, e: function e(r) { u = !0, o = r; }, f: function f() { try { a || null == t.return || t.return(); } finally { if (u) throw o; } } }; }
function MessageFeedCard_regenerator() { /*! regenerator-runtime -- Copyright (c) 2014-present, Facebook, Inc. -- license (MIT): https://github.com/babel/babel/blob/main/packages/babel-helpers/LICENSE */ var e, t, r = "function" == typeof Symbol ? Symbol : {}, n = r.iterator || "@@iterator", o = r.toStringTag || "@@toStringTag"; function i(r, n, o, i) { var c = n && n.prototype instanceof Generator ? n : Generator, u = Object.create(c.prototype); return MessageFeedCard_regeneratorDefine2(u, "_invoke", function (r, n, o) { var i, c, u, f = 0, p = o || [], y = !1, G = { p: 0, n: 0, v: e, a: d, f: d.bind(e, 4), d: function d(t, r) { return i = t, c = 0, u = e, G.n = r, a; } }; function d(r, n) { for (c = r, u = n, t = 0; !y && f && !o && t < p.length; t++) { var o, i = p[t], d = G.p, l = i[2]; r > 3 ? (o = l === n) && (u = i[(c = i[4]) ? 5 : (c = 3, 3)], i[4] = i[5] = e) : i[0] <= d && ((o = r < 2 && d < i[1]) ? (c = 0, G.v = n, G.n = i[1]) : d < l && (o = r < 3 || i[0] > n || n > l) && (i[4] = r, i[5] = n, G.n = l, c = 0)); } if (o || r > 1) return a; throw y = !0, n; } return function (o, p, l) { if (f > 1) throw TypeError("Generator is already running"); for (y && 1 === p && d(p, l), c = p, u = l; (t = c < 2 ? e : u) || !y;) { i || (c ? c < 3 ? (c > 1 && (G.n = -1), d(c, u)) : G.n = u : G.v = u); try { if (f = 2, i) { if (c || (o = "next"), t = i[o]) { if (!(t = t.call(i, u))) throw TypeError("iterator result is not an object"); if (!t.done) return t; u = t.value, c < 2 && (c = 0); } else 1 === c && (t = i.return) && t.call(i), c < 2 && (u = TypeError("The iterator does not provide a '" + o + "' method"), c = 1); i = e; } else if ((t = (y = G.n < 0) ? u : r.call(n, G)) !== a) break; } catch (t) { i = e, c = 1, u = t; } finally { f = 1; } } return { value: t, done: y }; }; }(r, o, i), !0), u; } var a = {}; function Generator() {} function GeneratorFunction() {} function GeneratorFunctionPrototype() {} t = Object.getPrototypeOf; var c = [][n] ? t(t([][n]())) : (MessageFeedCard_regeneratorDefine2(t = {}, n, function () { return this; }), t), u = GeneratorFunctionPrototype.prototype = Generator.prototype = Object.create(c); function f(e) { return Object.setPrototypeOf ? Object.setPrototypeOf(e, GeneratorFunctionPrototype) : (e.__proto__ = GeneratorFunctionPrototype, MessageFeedCard_regeneratorDefine2(e, o, "GeneratorFunction")), e.prototype = Object.create(u), e; } return GeneratorFunction.prototype = GeneratorFunctionPrototype, MessageFeedCard_regeneratorDefine2(u, "constructor", GeneratorFunctionPrototype), MessageFeedCard_regeneratorDefine2(GeneratorFunctionPrototype, "constructor", GeneratorFunction), GeneratorFunction.displayName = "GeneratorFunction", MessageFeedCard_regeneratorDefine2(GeneratorFunctionPrototype, o, "GeneratorFunction"), MessageFeedCard_regeneratorDefine2(u), MessageFeedCard_regeneratorDefine2(u, o, "Generator"), MessageFeedCard_regeneratorDefine2(u, n, function () { return this; }), MessageFeedCard_regeneratorDefine2(u, "toString", function () { return "[object Generator]"; }), (MessageFeedCard_regenerator = function _regenerator() { return { w: i, m: f }; })(); }
function MessageFeedCard_regeneratorDefine2(e, r, n, t) { var i = Object.defineProperty; try { i({}, "", {}); } catch (e) { i = 0; } MessageFeedCard_regeneratorDefine2 = function _regeneratorDefine(e, r, n, t) { function o(r, n) { MessageFeedCard_regeneratorDefine2(e, r, function (e) { return this._invoke(r, n, e); }); } r ? i ? i(e, r, { value: n, enumerable: !t, configurable: !t, writable: !t }) : e[r] = n : (o("next", 0), o("throw", 1), o("return", 2)); }, MessageFeedCard_regeneratorDefine2(e, r, n, t); }
function MessageFeedCard_asyncGeneratorStep(n, t, e, r, o, a, c) { try { var i = n[a](c), u = i.value; } catch (n) { return void e(n); } i.done ? t(u) : Promise.resolve(u).then(r, o); }
function MessageFeedCard_asyncToGenerator(n) { return function () { var t = this, e = arguments; return new Promise(function (r, o) { var a = n.apply(t, e); function _next(n) { MessageFeedCard_asyncGeneratorStep(a, r, o, _next, _throw, "next", n); } function _throw(n) { MessageFeedCard_asyncGeneratorStep(a, r, o, _next, _throw, "throw", n); } _next(void 0); }); }; }
function MessageFeedCard_slicedToArray(r, e) { return MessageFeedCard_arrayWithHoles(r) || MessageFeedCard_iterableToArrayLimit(r, e) || MessageFeedCard_unsupportedIterableToArray(r, e) || MessageFeedCard_nonIterableRest(); }
function MessageFeedCard_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function MessageFeedCard_unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return MessageFeedCard_arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? MessageFeedCard_arrayLikeToArray(r, a) : void 0; } }
function MessageFeedCard_arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function MessageFeedCard_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function MessageFeedCard_arrayWithHoles(r) { if (Array.isArray(r)) return r; }







var MessageFeedCard = function MessageFeedCard(_ref) {
  var appState = _ref.appState;
  var selectedAgent = appState.selectedAgent;
  var _useState = (0,react.useState)([]),
    _useState2 = MessageFeedCard_slicedToArray(_useState, 2),
    messages = _useState2[0],
    setMessages = _useState2[1];
  var _useState3 = (0,react.useState)([]),
    _useState4 = MessageFeedCard_slicedToArray(_useState3, 2),
    llmCalls = _useState4[0],
    setLlmCalls = _useState4[1];
  var _useState5 = (0,react.useState)(false),
    _useState6 = MessageFeedCard_slicedToArray(_useState5, 2),
    isLoading = _useState6[0],
    setIsLoading = _useState6[1];
  var _useState7 = (0,react.useState)(null),
    _useState8 = MessageFeedCard_slicedToArray(_useState7, 2),
    activeTraceId = _useState8[0],
    setActiveTraceId = _useState8[1];
  var _useState9 = (0,react.useState)(null),
    _useState0 = MessageFeedCard_slicedToArray(_useState9, 2),
    pollingInterval = _useState0[0],
    setPollingInterval = _useState0[1];
  var _useState1 = (0,react.useState)(new Set()),
    _useState10 = MessageFeedCard_slicedToArray(_useState1, 2),
    expandedMessages = _useState10[0],
    setExpandedMessages = _useState10[1];
  var messagesEndRef = (0,react.useRef)(null);

  // Auto-scroll to bottom when new messages or LLM calls arrive
  var scrollToBottom = function scrollToBottom() {
    var _messagesEndRef$curre;
    (_messagesEndRef$curre = messagesEndRef.current) === null || _messagesEndRef$curre === void 0 || _messagesEndRef$curre.scrollIntoView({
      behavior: 'smooth'
    });
  };
  (0,react.useEffect)(function () {
    scrollToBottom();
  }, [messages, llmCalls]);

  // Load recent messages for the selected agent (disabled in new architecture)
  var loadRecentMessages = /*#__PURE__*/function () {
    var _ref2 = MessageFeedCard_asyncToGenerator(/*#__PURE__*/MessageFeedCard_regenerator().m(function _callee() {
      return MessageFeedCard_regenerator().w(function (_context) {
        while (1) switch (_context.n) {
          case 0:
            return _context.a(2);
        }
      }, _callee);
    }));
    return function loadRecentMessages() {
      return _ref2.apply(this, arguments);
    };
  }();

  // Flatten tree structure into a sorted list for display
  var _flattenEventTree = function flattenEventTree(events) {
    var result = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : [];
    var _iterator = MessageFeedCard_createForOfIteratorHelper(events),
      _step;
    try {
      for (_iterator.s(); !(_step = _iterator.n()).done;) {
        var event = _step.value;
        // Add event to flat list (without children array to avoid circular refs)
        var children = event.children,
          eventWithoutChildren = MessageFeedCard_objectWithoutProperties(event, MessageFeedCard_excluded);
        result.push(eventWithoutChildren);

        // Recursively add children
        if (children && children.length > 0) {
          _flattenEventTree(children, result);
        }
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
    return result;
  };

  // Poll for messages in a specific trace
  var pollTraceMessages = /*#__PURE__*/function () {
    var _ref3 = MessageFeedCard_asyncToGenerator(/*#__PURE__*/MessageFeedCard_regenerator().m(function _callee2(traceId) {
      var response, data, traceEvents, llmCallEvents, nonLlmEvents, legacyLlmCalls, allLlmCalls, _t;
      return MessageFeedCard_regenerator().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            if (traceId) {
              _context2.n = 1;
              break;
            }
            return _context2.a(2);
          case 1:
            _context2.p = 1;
            _context2.n = 2;
            return fetch("/api/unstable/events/trace/".concat(traceId));
          case 2:
            response = _context2.v;
            if (!response.ok) {
              _context2.n = 4;
              break;
            }
            _context2.n = 3;
            return response.json();
          case 3:
            data = _context2.v;
            // New format: events is a tree, LLM calls are merged in with message_type: "llm_call"
            // Old format fallback: events array + separate llm_calls array
            traceEvents = data.events || data.messages || []; // Flatten tree structure if events have children
            if (traceEvents.some(function (e) {
              return e.children && e.children.length > 0;
            })) {
              traceEvents = _flattenEventTree(traceEvents);
            }

            // Sort by effective_timestamp or timestamp
            traceEvents.sort(function (a, b) {
              var timeA = a.effective_timestamp || a.timestamp || a.ts || '';
              var timeB = b.effective_timestamp || b.timestamp || b.ts || '';
              return timeA.localeCompare(timeB);
            });

            // Separate LLM calls from other events
            llmCallEvents = traceEvents.filter(function (e) {
              return e.message_type === 'llm_call';
            });
            nonLlmEvents = traceEvents.filter(function (e) {
              return e.message_type !== 'llm_call';
            }); // Also handle legacy format with separate llm_calls array
            legacyLlmCalls = data.llm_calls || [];
            if (nonLlmEvents.length > 0) {
              setMessages(function (prevMessages) {
                var existingByUid = new Map(prevMessages.map(function (m) {
                  return [m.uid, m];
                }));
                var existingMessageKeys = new Set(prevMessages.map(function (m) {
                  return "".concat(m.trace_id || '', "-").concat(m.topic || m.function_name, "-").concat(m.sender_id, "-").concat(JSON.stringify(m.payload));
                }));

                // Separate into updates (existing UID with changed status) and truly new messages
                var updatedUids = new Set();
                var newMessages = [];
                var _iterator2 = MessageFeedCard_createForOfIteratorHelper(nonLlmEvents),
                  _step2;
                try {
                  for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
                    var m = _step2.value;
                    var existing = existingByUid.get(m.uid);
                    if (existing) {
                      // Check if invocation status changed (e.g. running → completed)
                      if (existing.invocation_status !== m.invocation_status) {
                        updatedUids.add(m.uid);
                        existingByUid.set(m.uid, m); // Replace with updated version
                      }
                    } else {
                      var messageKey = "".concat(m.trace_id || '', "-").concat(m.topic || m.function_name, "-").concat(m.sender_id, "-").concat(JSON.stringify(m.payload));
                      if (!existingMessageKeys.has(messageKey)) {
                        newMessages.push(m);
                      }
                    }
                  }

                  // Check for completion across both new and updated messages
                } catch (err) {
                  _iterator2.e(err);
                } finally {
                  _iterator2.f();
                }
                var allChangedMessages = [].concat(newMessages, MessageFeedCard_toConsumableArray(MessageFeedCard_toConsumableArray(updatedUids).map(function (uid) {
                  return existingByUid.get(uid);
                })));
                var hasCompletedInvocations = allChangedMessages.some(function (msg) {
                  return msg && (msg.topic && msg.topic.includes('.response') || msg.invocation_status === 'completed' || msg.invocation_status === 'error');
                });
                if (hasCompletedInvocations) {
                  stopPolling();
                }
                if (updatedUids.size > 0 || newMessages.length > 0) {
                  // Rebuild: replace updated messages in-place, append new ones
                  var rebuilt = prevMessages.map(function (m) {
                    return updatedUids.has(m.uid) ? existingByUid.get(m.uid) : m;
                  });
                  return [].concat(MessageFeedCard_toConsumableArray(rebuilt), newMessages);
                }
                return prevMessages;
              });
            }

            // Update LLM calls (from both new merged format and legacy format)
            allLlmCalls = [].concat(MessageFeedCard_toConsumableArray(llmCallEvents.map(function (e) {
              return MessageFeedCard_objectSpread(MessageFeedCard_objectSpread({}, e), {}, {
                llm_call_id: e.uid,
                messages: e.request_messages,
                tool_calls: e.response_tool_calls
              });
            })), MessageFeedCard_toConsumableArray(legacyLlmCalls));
            if (allLlmCalls.length > 0) {
              setLlmCalls(function (prevLlmCalls) {
                var existingIds = new Set(prevLlmCalls.map(function (c) {
                  return c.llm_call_id || c.uid;
                }));
                var newCalls = allLlmCalls.filter(function (c) {
                  return !existingIds.has(c.llm_call_id || c.uid);
                });
                if (newCalls.length > 0) {
                  return [].concat(MessageFeedCard_toConsumableArray(prevLlmCalls), MessageFeedCard_toConsumableArray(newCalls));
                }
                return prevLlmCalls;
              });
            }
          case 4:
            _context2.n = 6;
            break;
          case 5:
            _context2.p = 5;
            _t = _context2.v;
            console.error('Error polling trace messages:', _t);
          case 6:
            return _context2.a(2);
        }
      }, _callee2, null, [[1, 5]]);
    }));
    return function pollTraceMessages(_x) {
      return _ref3.apply(this, arguments);
    };
  }();

  // Start polling for a trace
  var startTracePolling = function startTracePolling(traceId) {
    var timeoutSeconds = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 3600;
    // Clear existing polling
    if (pollingInterval) {
      clearInterval(pollingInterval);
    }
    setActiveTraceId(traceId);

    // Poll immediately first
    pollTraceMessages(traceId);

    // Then poll every 2 seconds
    var interval = setInterval(function () {
      pollTraceMessages(traceId);
    }, 2000);
    setPollingInterval(interval);

    // Stop polling after 2x the timeout to avoid race conditions with backend
    var pollingTimeoutMs = timeoutSeconds * 2 * 1000;
    setTimeout(function () {
      if (interval) {
        clearInterval(interval);
        setPollingInterval(null);
        setActiveTraceId(null);
      }
    }, pollingTimeoutMs);
  };

  // Stop polling
  var stopPolling = function stopPolling() {
    if (pollingInterval) {
      clearInterval(pollingInterval);
      setPollingInterval(null);
      setActiveTraceId(null);
    }
  };

  // Clear messages and LLM calls
  var clearMessages = function clearMessages() {
    setMessages([]);
    setLlmCalls([]);
    stopPolling();
  };

  // Clean up polling when agent changes
  (0,react.useEffect)(function () {
    return function () {
      stopPolling();
    };
  }, [selectedAgent]);

  // Listen for trace events from SendTestEventCard
  (0,react.useEffect)(function () {
    var handleTraceEvent = function handleTraceEvent(event) {
      // Handle immediate messages if provided
      if (event.detail.immediateMessages && event.detail.immediateMessages.length > 0) {
        var immediateMessages = event.detail.immediateMessages;
        setMessages(function (prevMessages) {
          var existingUids = new Set(prevMessages.map(function (m) {
            return m.uid;
          }));
          var newMessages = immediateMessages.filter(function (m) {
            return !existingUids.has(m.uid);
          });
          if (newMessages.length > 0) {
            return [].concat(MessageFeedCard_toConsumableArray(prevMessages), MessageFeedCard_toConsumableArray(newMessages));
          }
          return prevMessages;
        });

        // Check if we have agent responses in immediate messages
        var hasAgentResponses = immediateMessages.some(function (msg) {
          return msg.topic && msg.topic.includes('.response');
        });

        // If we have immediate agent responses, no need to poll
        if (hasAgentResponses) {
          return; // Don't start polling
        }
      }

      // Start polling for any additional messages if requested (only if no immediate agent responses)
      if (event.detail.startPolling && event.detail.traceId) {
        startTracePolling(event.detail.traceId, event.detail.timeoutSeconds);
      }
    };
    window.addEventListener('traceStarted', handleTraceEvent);
    return function () {
      window.removeEventListener('traceStarted', handleTraceEvent);
    };
  }, []);
  var formatTimestamp = function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Toggle message expansion
  var toggleMessageExpansion = function toggleMessageExpansion(messageUid) {
    setExpandedMessages(function (prev) {
      var newSet = new Set(prev);
      if (newSet.has(messageUid)) {
        newSet.delete(messageUid);
      } else {
        newSet.add(messageUid);
      }
      return newSet;
    });
  };
  var formatMessageContent = function formatMessageContent(message) {
    var isExpanded = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
    var content;
    if (typeof message.payload === 'string') {
      content = message.payload;
    } else {
      content = JSON.stringify(message.payload, null, 2);
    }

    // Define length threshold for truncation
    var maxLength = 300;
    var needsTruncation = content.length > maxLength;
    if (isExpanded || !needsTruncation) {
      return {
        content: content,
        needsTruncation: needsTruncation
      };
    }
    return {
      content: content.slice(0, maxLength) + '...',
      needsTruncation: needsTruncation
    };
  };

  // Group messages and LLM calls by trace_id into unified traces
  var traceGroups = react.useMemo(function () {
    var groups = new Map();

    // Add messages grouped by trace_id
    messages.forEach(function (msg) {
      var traceId = msg.trace_id || 'no-trace';
      if (!groups.has(traceId)) {
        groups.set(traceId, {
          traceId: traceId,
          invocation: null,
          llmCalls: [],
          timestamp: msg.ts || msg.stored_at || ''
        });
      }
      var group = groups.get(traceId);
      // The first function message is usually the invocation
      if (!group.invocation && (msg.message_type === 'function' || msg.function_name)) {
        group.invocation = msg;
      }
      // Update timestamp if earlier
      var msgTime = msg.ts || msg.stored_at || '';
      if (msgTime && (!group.timestamp || msgTime < group.timestamp)) {
        group.timestamp = msgTime;
      }
    });

    // Add LLM calls to their trace groups
    llmCalls.forEach(function (call) {
      var traceId = call.trace_id || 'no-trace';
      if (!groups.has(traceId)) {
        groups.set(traceId, {
          traceId: traceId,
          invocation: null,
          llmCalls: [],
          timestamp: call.ts || ''
        });
      }
      groups.get(traceId).llmCalls.push(call);
    });

    // Sort LLM calls within each group by timestamp
    groups.forEach(function (group) {
      group.llmCalls.sort(function (a, b) {
        var timeA = a.ts || '';
        var timeB = b.ts || '';
        return timeA.localeCompare(timeB);
      });
    });

    // Convert to array and sort by timestamp (newest first for display)
    var sortedGroups = Array.from(groups.values());
    sortedGroups.sort(function (a, b) {
      var timeA = a.timestamp || '';
      var timeB = b.timestamp || '';
      return timeA.localeCompare(timeB);
    });
    return sortedGroups;
  }, [messages, llmCalls]);
  var hasContent = messages.length > 0 || llmCalls.length > 0;
  return /*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)(CardTitle, {
        className: "flex items-center justify-between",
        children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex items-center",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(MessageCircle, {
            className: "w-5 h-5 mr-2"
          }), "Message Feed", activeTraceId && /*#__PURE__*/(0,jsx_runtime.jsx)(badge_Badge, {
            variant: "secondary",
            className: "ml-2 bg-blue-100 text-blue-800",
            children: "Live"
          }), llmCalls.length > 0 && /*#__PURE__*/(0,jsx_runtime.jsxs)(badge_Badge, {
            variant: "secondary",
            className: "ml-2 bg-indigo-100 text-indigo-800",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)(bot_Bot, {
              className: "w-3 h-3 mr-1"
            }), llmCalls.length, " LLM call", llmCalls.length !== 1 ? 's' : '']
          })]
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "flex items-center space-x-2",
          children: /*#__PURE__*/(0,jsx_runtime.jsx)(Button, {
            variant: "ghost",
            size: "sm",
            onClick: clearMessages,
            children: /*#__PURE__*/(0,jsx_runtime.jsx)(Trash2, {
              className: "w-4 h-4"
            })
          })
        })]
      })
    }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
      className: "pb-6",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "bg-white rounded-md border h-[600px] overflow-y-auto",
        children: [isLoading && !hasContent ? /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "p-4 text-center text-gray-500",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
            className: "animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500 mx-auto mb-2"
          }), "Loading messages..."]
        }) : !hasContent ? /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "p-4 text-center text-gray-500",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(MessageCircle, {
            className: "w-8 h-8 mx-auto mb-2 opacity-50"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            children: "No messages yet"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-xs mt-1",
            children: "Send a test event to see messages appear here"
          })]
        }) : /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "p-4 space-y-4",
          children: [traceGroups.map(function (group, groupIndex) {
            var invocation = group.invocation;
            var llmCallsList = group.llmCalls;

            // Calculate total stats across all LLM calls in this trace
            var totalCost = llmCallsList.reduce(function (sum, c) {
              return sum + (c.cost_usd || 0);
            }, 0);
            var totalInputTokens = llmCallsList.reduce(function (sum, c) {
              return sum + (c.input_tokens || 0);
            }, 0);
            var totalOutputTokens = llmCallsList.reduce(function (sum, c) {
              return sum + (c.output_tokens || 0);
            }, 0);
            var totalLatency = llmCallsList.reduce(function (sum, c) {
              return sum + (c.latency_ms || 0);
            }, 0);

            // Build unified conversation from LLM calls, grouped by subprocess_id.
            // Calls from different subprocesses (orchestrator vs subagent) get separate
            // conversation threads to avoid flickering between different message contexts.
            var conversationMessages = [];
            if (llmCallsList.length > 0) {
              // Group LLM calls by subprocess_id
              var subprocessGroups = new Map();
              llmCallsList.forEach(function (call) {
                var spId = call.subprocess_id || '_default';
                if (!subprocessGroups.has(spId)) {
                  subprocessGroups.set(spId, []);
                }
                subprocessGroups.get(spId).push(call);
              });

              // Use the largest subprocess group as the primary conversation
              // (usually the orchestrator has the most calls)
              var primaryCalls = llmCallsList;
              if (subprocessGroups.size > 1) {
                var maxSize = 0;
                subprocessGroups.forEach(function (calls) {
                  if (calls.length > maxSize) {
                    maxSize = calls.length;
                    primaryCalls = calls;
                  }
                });
              }
              var lastCall = primaryCalls[primaryCalls.length - 1];
              var lastCallMessages = lastCall.messages || [];

              // Add all messages, annotating assistant messages with the model
              lastCallMessages.forEach(function (msg) {
                if (msg.role === 'assistant') {
                  var _primaryCalls$;
                  // Find which call produced this response by matching content
                  var matchingCall = primaryCalls.find(function (c) {
                    return c.response_content && msg.content && typeof msg.content === 'string' && c.response_content === msg.content;
                  });
                  conversationMessages.push(MessageFeedCard_objectSpread(MessageFeedCard_objectSpread({}, msg), {}, {
                    _model: (matchingCall === null || matchingCall === void 0 ? void 0 : matchingCall.model) || ((_primaryCalls$ = primaryCalls[0]) === null || _primaryCalls$ === void 0 ? void 0 : _primaryCalls$.model)
                  }));
                } else {
                  conversationMessages.push(MessageFeedCard_objectSpread({}, msg));
                }
              });

              // Add the final response from the last LLM call
              if (lastCall.response_content && lastCall.response_content !== '[streamed]') {
                conversationMessages.push({
                  role: 'assistant',
                  content: lastCall.response_content,
                  _model: lastCall.model
                });
              } else if (lastCall.tool_calls && lastCall.tool_calls.length > 0) {
                conversationMessages.push({
                  role: 'assistant',
                  content: null,
                  tool_calls: lastCall.tool_calls,
                  _model: lastCall.model
                });
              }
            }
            return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "rounded-lg border border-gray-200 bg-white overflow-hidden shadow-sm",
              children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 border-b border-gray-200",
                children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "flex items-center justify-between",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                    className: "flex items-center gap-2",
                    children: [invocation && /*#__PURE__*/(0,jsx_runtime.jsxs)(jsx_runtime.Fragment, {
                      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                        className: "text-sm text-gray-600",
                        children: invocation.sender_id || 'unknown'
                      }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                        className: "text-gray-400",
                        children: "\u2192"
                      }), /*#__PURE__*/(0,jsx_runtime.jsx)(badge_Badge, {
                        className: "bg-blue-100 text-blue-800 border-blue-200",
                        children: invocation.function_name || invocation.target_agent || 'unknown'
                      })]
                    }), (invocation === null || invocation === void 0 ? void 0 : invocation.invocation_status) === 'completed' && /*#__PURE__*/(0,jsx_runtime.jsx)(badge_Badge, {
                      className: "bg-green-100 text-green-800 text-xs",
                      children: "Completed"
                    }), (invocation === null || invocation === void 0 ? void 0 : invocation.invocation_status) === 'error' && /*#__PURE__*/(0,jsx_runtime.jsx)(badge_Badge, {
                      className: "bg-red-100 text-red-800 text-xs",
                      children: "Error"
                    }), (invocation === null || invocation === void 0 ? void 0 : invocation.invocation_status) === 'running' && /*#__PURE__*/(0,jsx_runtime.jsx)(badge_Badge, {
                      className: "bg-yellow-100 text-yellow-800 text-xs",
                      children: "Running"
                    })]
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                    className: "text-xs text-gray-500",
                    children: formatTimestamp(group.timestamp)
                  })]
                }), llmCallsList.length > 0 && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "flex items-center gap-4 mt-2 text-xs text-gray-600",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                    className: "flex items-center gap-1",
                    children: [/*#__PURE__*/(0,jsx_runtime.jsx)(bot_Bot, {
                      className: "w-3.5 h-3.5"
                    }), llmCallsList.length, " LLM call", llmCallsList.length !== 1 ? 's' : '']
                  }), function () {
                    var models = MessageFeedCard_toConsumableArray(new Set(llmCallsList.map(function (c) {
                      return c.model;
                    }).filter(Boolean)));
                    return models.length > 0 ? /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                      className: "font-medium text-gray-700",
                      children: models.join(', ')
                    }) : null;
                  }(), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                    children: [(totalInputTokens + totalOutputTokens).toLocaleString(), " tokens"]
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                    children: totalCost < 0.0001 ? '<$0.0001' : "$".concat(totalCost.toFixed(4))
                  }), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                    children: [totalLatency, "ms"]
                  })]
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "p-4 space-y-3",
                children: [invocation && invocation.payload && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "bg-blue-50 border border-blue-200 rounded-lg p-3",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                    className: "text-xs font-semibold text-blue-800 mb-1",
                    children: "Input"
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
                    className: "text-xs font-mono text-blue-900 whitespace-pre-wrap break-words",
                    children: JSON.stringify(invocation.payload, null, 2)
                  })]
                }), conversationMessages.length > 0 && /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "space-y-2",
                  children: conversationMessages.map(function (msg, idx) {
                    return /*#__PURE__*/(0,jsx_runtime.jsx)(LLMMessageCard, {
                      message: msg,
                      index: idx
                    }, "msg-".concat(idx));
                  })
                }), (invocation === null || invocation === void 0 ? void 0 : invocation.invocation_status) === 'completed' && (invocation === null || invocation === void 0 ? void 0 : invocation.invocation_result) && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "bg-green-50 border border-green-200 rounded-lg p-3",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                    className: "text-xs font-semibold text-green-800 mb-1",
                    children: ["Response from ", invocation.target_agent || 'agent']
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
                    className: "text-xs font-mono text-green-900 whitespace-pre-wrap break-words",
                    children: JSON.stringify(invocation.invocation_result, null, 2)
                  })]
                }), (invocation === null || invocation === void 0 ? void 0 : invocation.invocation_status) === 'error' && (invocation === null || invocation === void 0 ? void 0 : invocation.invocation_error) && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "bg-red-50 border border-red-200 rounded-lg p-3",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                    className: "text-xs font-semibold text-red-800 mb-1",
                    children: ["Error from ", invocation.target_agent || 'agent']
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
                    className: "text-xs font-mono text-red-900 whitespace-pre-wrap break-words",
                    children: invocation.invocation_error
                  })]
                }), group.traceId && group.traceId !== 'no-trace' && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "text-xs text-gray-400",
                  children: ["Trace: ", group.traceId.substring(0, 8), "..."]
                })]
              })]
            }, "trace-".concat(group.traceId, "-").concat(groupIndex));
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
            ref: messagesEndRef
          })]
        }), activeTraceId && /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
          className: "mt-2 text-center",
          children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center justify-center text-xs text-gray-500",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
              className: "animate-pulse w-1.5 h-1.5 bg-blue-400 rounded-full mr-1.5"
            }), "Listening for messages..."]
          })
        })]
      })
    })]
  });
};
/* harmony default export */ const components_MessageFeedCard = (MessageFeedCard);
;// ./node_modules/lucide-react/dist/esm/icons/play.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const play_iconNode = [["polygon", { points: "6 3 20 12 6 21 6 3", key: "1oa8hb" }]];
const Play = createLucideIcon("play", play_iconNode);


//# sourceMappingURL=play.js.map

;// ./src/components/FunctionsCard.jsx
function FunctionsCard_createForOfIteratorHelper(r, e) { var t = "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (!t) { if (Array.isArray(r) || (t = FunctionsCard_unsupportedIterableToArray(r)) || e && r && "number" == typeof r.length) { t && (r = t); var _n = 0, F = function F() {}; return { s: F, n: function n() { return _n >= r.length ? { done: !0 } : { done: !1, value: r[_n++] }; }, e: function e(r) { throw r; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var o, a = !0, u = !1; return { s: function s() { t = t.call(r); }, n: function n() { var r = t.next(); return a = r.done, r; }, e: function e(r) { u = !0, o = r; }, f: function f() { try { a || null == t.return || t.return(); } finally { if (u) throw o; } } }; }
function FunctionsCard_slicedToArray(r, e) { return FunctionsCard_arrayWithHoles(r) || FunctionsCard_iterableToArrayLimit(r, e) || FunctionsCard_unsupportedIterableToArray(r, e) || FunctionsCard_nonIterableRest(); }
function FunctionsCard_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function FunctionsCard_unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return FunctionsCard_arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? FunctionsCard_arrayLikeToArray(r, a) : void 0; } }
function FunctionsCard_arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function FunctionsCard_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function FunctionsCard_arrayWithHoles(r) { if (Array.isArray(r)) return r; }






/**
 * FunctionsCard - Displays agent functions and allows invoking @fn handlers
 *
 * Supports both:
 * - @on handlers (topic-triggered) - shown with Radio icon
 * - @fn handlers (callable) - shown with Zap icon and Invoke button
 *
 * The Invoke button dispatches a custom event to populate the SendTestEventCard
 * instead of opening its own modal.
 */

var FunctionsCard = function FunctionsCard(_ref) {
  var appState = _ref.appState;
  var selectedAgent = appState.selectedAgent;
  var _useState = (0,react.useState)([]),
    _useState2 = FunctionsCard_slicedToArray(_useState, 2),
    functions = _useState2[0],
    setFunctions = _useState2[1];
  var _useState3 = (0,react.useState)(true),
    _useState4 = FunctionsCard_slicedToArray(_useState3, 2),
    loading = _useState4[0],
    setLoading = _useState4[1];
  var _useState5 = (0,react.useState)(null),
    _useState6 = FunctionsCard_slicedToArray(_useState5, 2),
    expandedFunction = _useState6[0],
    setExpandedFunction = _useState6[1];

  // Load functions from agent data
  (0,react.useEffect)(function () {
    if (!selectedAgent) {
      setFunctions([]);
      setLoading(false);
      return;
    }
    setLoading(true);
    var agentFunctions = selectedAgent.functions || [];

    // Process functions into display format
    var processedFunctions = [];
    var _iterator = FunctionsCard_createForOfIteratorHelper(agentFunctions),
      _step;
    try {
      for (_iterator.s(); !(_step = _iterator.n()).done;) {
        var func = _step.value;
        // Get topic triggers (@on handlers)
        var topicTriggers = (func.triggers || []).filter(function (t) {
          return t.type === 'topic';
        });
        var _iterator2 = FunctionsCard_createForOfIteratorHelper(topicTriggers),
          _step2;
        try {
          for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
            var trigger = _step2.value;
            if (trigger.topic) {
              processedFunctions.push({
                id: "topic-".concat(trigger.topic, "-").concat(func.name),
                triggerType: 'topic',
                topic: trigger.topic,
                functionName: func.name,
                name: func.name,
                description: func.description,
                inputSchema: func.input_schema,
                outputSchema: func.output_schema
              });
            }
          }

          // Get callable triggers (@fn handlers)
        } catch (err) {
          _iterator2.e(err);
        } finally {
          _iterator2.f();
        }
        var callableTriggers = (func.triggers || []).filter(function (t) {
          return t.type === 'callable';
        });
        var _iterator3 = FunctionsCard_createForOfIteratorHelper(callableTriggers),
          _step3;
        try {
          for (_iterator3.s(); !(_step3 = _iterator3.n()).done;) {
            var _trigger = _step3.value;
            var fnName = _trigger.function_name || func.name;
            processedFunctions.push({
              id: "callable-".concat(fnName),
              triggerType: 'callable',
              topic: null,
              functionName: fnName,
              name: func.name,
              description: func.description,
              inputSchema: func.input_schema,
              outputSchema: func.output_schema
            });
          }
        } catch (err) {
          _iterator3.e(err);
        } finally {
          _iterator3.f();
        }
      }
    } catch (err) {
      _iterator.e(err);
    } finally {
      _iterator.f();
    }
    setFunctions(processedFunctions);
    setLoading(false);
  }, [selectedAgent]);

  // Dispatch event to populate SendTestEventCard with this function
  var handleInvokeClick = function handleInvokeClick(func) {
    window.dispatchEvent(new CustomEvent('invokeFunction', {
      detail: {
        functionName: func.functionName,
        inputSchema: func.inputSchema
      }
    }));
  };

  // Trigger type badge
  var getTriggerTypeBadge = function getTriggerTypeBadge(func) {
    if (func.triggerType === 'topic') {
      return /*#__PURE__*/(0,jsx_runtime.jsxs)(badge_Badge, {
        className: "bg-purple-50 text-purple-700 border-purple-200 flex items-center gap-1 text-xs",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
          className: "w-3 h-3"
        }), "@on"]
      });
    } else {
      return /*#__PURE__*/(0,jsx_runtime.jsxs)(badge_Badge, {
        className: "bg-blue-50 text-blue-700 border-blue-200 flex items-center gap-1 text-xs",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(zap_Zap, {
          className: "w-3 h-3"
        }), "@fn"]
      });
    }
  };
  if (loading) {
    return /*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)(CardTitle, {
          className: "flex items-center",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Code, {
            className: "w-4 h-4 mr-2"
          }), "Functions"]
        })
      }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex items-center justify-center py-8",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LoaderCircle, {
            className: "w-6 h-6 animate-spin text-gray-400"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
            className: "ml-2 text-gray-500",
            children: "Loading functions..."
          })]
        })
      })]
    });
  }
  if (functions.length === 0) {
    return /*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)(CardTitle, {
          className: "flex items-center",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Code, {
            className: "w-4 h-4 mr-2"
          }), "Functions"]
        })
      }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "text-center py-8 text-gray-500",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Code, {
            className: "w-12 h-12 mx-auto mb-3 text-gray-300"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            children: "No functions registered"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-sm mt-1",
            children: "This agent hasn't registered any handler functions yet."
          })]
        })
      })]
    });
  }
  return /*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)(CardTitle, {
        className: "flex items-center justify-between",
        children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex items-center",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Code, {
            className: "w-4 h-4 mr-2"
          }), "Functions"]
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
          className: "text-sm font-normal text-gray-500",
          children: [functions.length, " registered"]
        })]
      })
    }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
      className: "pb-6",
      children: /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "space-y-3",
        children: functions.map(function (func) {
          return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "border border-gray-200 rounded-lg overflow-hidden",
            children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "flex items-center justify-between p-3 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors",
              onClick: function onClick() {
                return setExpandedFunction(expandedFunction === func.id ? null : func.id);
              },
              children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex items-center gap-2",
                children: [expandedFunction === func.id ? /*#__PURE__*/(0,jsx_runtime.jsx)(chevron_down_ChevronDown, {
                  className: "w-4 h-4 text-gray-400"
                }) : /*#__PURE__*/(0,jsx_runtime.jsx)(ChevronRight, {
                  className: "w-4 h-4 text-gray-400"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("code", {
                  className: "text-sm font-medium text-gray-900",
                  children: func.functionName || func.name
                }), getTriggerTypeBadge(func)]
              }), func.triggerType === 'callable' && /*#__PURE__*/(0,jsx_runtime.jsxs)(Button, {
                variant: "outline",
                size: "sm",
                onClick: function onClick(e) {
                  e.stopPropagation();
                  handleInvokeClick(func);
                },
                className: "text-xs flex items-center gap-1 text-blue-600 hover:text-blue-800 border-blue-200 hover:border-blue-400",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Play, {
                  className: "w-3 h-3"
                }), "Invoke"]
              })]
            }), expandedFunction === func.id && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "p-3 border-t border-gray-200 bg-white",
              children: [func.description && /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
                className: "text-sm text-gray-600 mb-3",
                children: func.description
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "mb-3",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-xs font-medium text-gray-500 uppercase tracking-wide",
                  children: func.triggerType === 'topic' ? 'Topic Trigger' : 'Function Name'
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "mt-1",
                  children: func.triggerType === 'topic' ? /*#__PURE__*/(0,jsx_runtime.jsx)("code", {
                    className: "px-2 py-1 bg-purple-50 text-purple-700 rounded text-sm",
                    children: func.topic
                  }) : /*#__PURE__*/(0,jsx_runtime.jsxs)("code", {
                    className: "px-2 py-1 bg-blue-50 text-blue-700 rounded text-sm",
                    children: [func.functionName, "()"]
                  })
                })]
              }), func.inputSchema && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-xs font-medium text-gray-500 uppercase tracking-wide",
                  children: "Input Schema"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("pre", {
                  className: "mt-1 p-2 bg-gray-50 rounded text-xs overflow-auto max-h-32",
                  children: JSON.stringify(func.inputSchema, null, 2)
                })]
              })]
            })]
          }, func.id);
        })
      })
    })]
  });
};
/* harmony default export */ const components_FunctionsCard = (FunctionsCard);
;// ./src/components/AgentDetailsPage.jsx
function AgentDetailsPage_typeof(o) { "@babel/helpers - typeof"; return AgentDetailsPage_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, AgentDetailsPage_typeof(o); }
function AgentDetailsPage_ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function AgentDetailsPage_objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? AgentDetailsPage_ownKeys(Object(t), !0).forEach(function (r) { AgentDetailsPage_defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : AgentDetailsPage_ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function AgentDetailsPage_defineProperty(e, r, t) { return (r = AgentDetailsPage_toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function AgentDetailsPage_toPropertyKey(t) { var i = AgentDetailsPage_toPrimitive(t, "string"); return "symbol" == AgentDetailsPage_typeof(i) ? i : i + ""; }
function AgentDetailsPage_toPrimitive(t, r) { if ("object" != AgentDetailsPage_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != AgentDetailsPage_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }








var AgentDetailsPage = function AgentDetailsPage(_ref) {
  var appState = _ref.appState;
  var selectedAgent = appState.selectedAgent,
    statusBadgeClass = appState.statusBadgeClass,
    showAgentList = appState.showAgentList;
  if (!selectedAgent) {
    return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "text-center py-12",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("p", {
        className: "text-gray-500",
        children: "No agent selected"
      }), /*#__PURE__*/(0,jsx_runtime.jsx)(Button, {
        onClick: showAgentList,
        variant: "outline",
        className: "mt-4",
        children: "Back to Agents"
      })]
    });
  }
  var formatLastRun = function formatLastRun(lastRun) {
    if (!lastRun || lastRun === 'never') return 'Never';
    return lastRun;
  };
  var statusLevel = function statusLevel(status) {
    var normalized = (status || '').toString().toLowerCase();
    if (['healthy', 'deployed', 'active', 'running'].includes(normalized)) {
      return 'good';
    }
    if (['building', 'pending', 'deploying'].includes(normalized)) {
      return 'pending';
    }
    return 'bad';
  };
  return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
    className: "space-y-6",
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "flex items-center justify-between mb-8",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center space-x-4",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Waypoints, {
          className: "h-8 w-8 text-[var(--color-brand-blue-600)]"
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
            className: "text-3xl font-bold text-gray-900",
            children: selectedAgent.name
          }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            className: "flex items-center mt-2 space-x-4",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ".concat(statusLevel(selectedAgent.status) === 'good' ? 'bg-green-100 text-green-800' : statusLevel(selectedAgent.status) === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'),
              children: selectedAgent.status || 'unknown'
            }), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "text-sm text-gray-500",
              children: ["Version ", selectedAgent.version || 'v1']
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
              className: "text-sm text-gray-400",
              children: "\u2022"
            }), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "text-sm text-gray-500",
              children: ["Last run ", formatLastRun(selectedAgent.last_run)]
            })]
          })]
        })]
      })
    }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "grid grid-cols-1 lg:grid-cols-3 gap-6",
      children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "lg:col-span-2 space-y-6",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(components_SendTestEventCard, {
          appState: AgentDetailsPage_objectSpread(AgentDetailsPage_objectSpread({}, appState), {}, {
            isAgentDetailsPage: true
          })
        }), /*#__PURE__*/(0,jsx_runtime.jsx)(components_FunctionsCard, {
          appState: appState
        }), /*#__PURE__*/(0,jsx_runtime.jsx)(components_MessageFeedCard, {
          appState: appState
        })]
      }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "space-y-6",
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
          className: "border-0 shadow-sm bg-gray-50",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
            className: "pb-3",
            children: /*#__PURE__*/(0,jsx_runtime.jsx)(CardTitle, {
              className: "text-lg font-semibold text-gray-900",
              children: "Agent Details"
            })
          }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
            className: "pt-0 pb-6",
            children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "grid grid-cols-1 gap-4",
              children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Name"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-900 font-medium",
                  children: selectedAgent.name
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Status"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ".concat(statusLevel(selectedAgent.status) === 'good' ? 'bg-green-100 text-green-800' : statusLevel(selectedAgent.status) === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'),
                  children: selectedAgent.status || 'unknown'
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Version"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-900",
                  children: selectedAgent.version || 'v1'
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Last Run"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-900",
                  children: formatLastRun(selectedAgent.last_run)
                })]
              }), selectedAgent.functions && selectedAgent.functions.length > 0 && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Functions"
                }), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                  className: "text-sm text-gray-900",
                  children: [selectedAgent.functions.length, " available"]
                })]
              }), selectedAgent.image && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Image"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-900 font-mono text-xs break-all max-w-xs truncate",
                  children: selectedAgent.image
                })]
              })]
            })
          })]
        })
      })]
    })]
  });
};
/* harmony default export */ const components_AgentDetailsPage = (AgentDetailsPage);
;// ./src/components/TopicsPage.jsx
function TopicsPage_regenerator() { /*! regenerator-runtime -- Copyright (c) 2014-present, Facebook, Inc. -- license (MIT): https://github.com/babel/babel/blob/main/packages/babel-helpers/LICENSE */ var e, t, r = "function" == typeof Symbol ? Symbol : {}, n = r.iterator || "@@iterator", o = r.toStringTag || "@@toStringTag"; function i(r, n, o, i) { var c = n && n.prototype instanceof Generator ? n : Generator, u = Object.create(c.prototype); return TopicsPage_regeneratorDefine2(u, "_invoke", function (r, n, o) { var i, c, u, f = 0, p = o || [], y = !1, G = { p: 0, n: 0, v: e, a: d, f: d.bind(e, 4), d: function d(t, r) { return i = t, c = 0, u = e, G.n = r, a; } }; function d(r, n) { for (c = r, u = n, t = 0; !y && f && !o && t < p.length; t++) { var o, i = p[t], d = G.p, l = i[2]; r > 3 ? (o = l === n) && (u = i[(c = i[4]) ? 5 : (c = 3, 3)], i[4] = i[5] = e) : i[0] <= d && ((o = r < 2 && d < i[1]) ? (c = 0, G.v = n, G.n = i[1]) : d < l && (o = r < 3 || i[0] > n || n > l) && (i[4] = r, i[5] = n, G.n = l, c = 0)); } if (o || r > 1) return a; throw y = !0, n; } return function (o, p, l) { if (f > 1) throw TypeError("Generator is already running"); for (y && 1 === p && d(p, l), c = p, u = l; (t = c < 2 ? e : u) || !y;) { i || (c ? c < 3 ? (c > 1 && (G.n = -1), d(c, u)) : G.n = u : G.v = u); try { if (f = 2, i) { if (c || (o = "next"), t = i[o]) { if (!(t = t.call(i, u))) throw TypeError("iterator result is not an object"); if (!t.done) return t; u = t.value, c < 2 && (c = 0); } else 1 === c && (t = i.return) && t.call(i), c < 2 && (u = TypeError("The iterator does not provide a '" + o + "' method"), c = 1); i = e; } else if ((t = (y = G.n < 0) ? u : r.call(n, G)) !== a) break; } catch (t) { i = e, c = 1, u = t; } finally { f = 1; } } return { value: t, done: y }; }; }(r, o, i), !0), u; } var a = {}; function Generator() {} function GeneratorFunction() {} function GeneratorFunctionPrototype() {} t = Object.getPrototypeOf; var c = [][n] ? t(t([][n]())) : (TopicsPage_regeneratorDefine2(t = {}, n, function () { return this; }), t), u = GeneratorFunctionPrototype.prototype = Generator.prototype = Object.create(c); function f(e) { return Object.setPrototypeOf ? Object.setPrototypeOf(e, GeneratorFunctionPrototype) : (e.__proto__ = GeneratorFunctionPrototype, TopicsPage_regeneratorDefine2(e, o, "GeneratorFunction")), e.prototype = Object.create(u), e; } return GeneratorFunction.prototype = GeneratorFunctionPrototype, TopicsPage_regeneratorDefine2(u, "constructor", GeneratorFunctionPrototype), TopicsPage_regeneratorDefine2(GeneratorFunctionPrototype, "constructor", GeneratorFunction), GeneratorFunction.displayName = "GeneratorFunction", TopicsPage_regeneratorDefine2(GeneratorFunctionPrototype, o, "GeneratorFunction"), TopicsPage_regeneratorDefine2(u), TopicsPage_regeneratorDefine2(u, o, "Generator"), TopicsPage_regeneratorDefine2(u, n, function () { return this; }), TopicsPage_regeneratorDefine2(u, "toString", function () { return "[object Generator]"; }), (TopicsPage_regenerator = function _regenerator() { return { w: i, m: f }; })(); }
function TopicsPage_regeneratorDefine2(e, r, n, t) { var i = Object.defineProperty; try { i({}, "", {}); } catch (e) { i = 0; } TopicsPage_regeneratorDefine2 = function _regeneratorDefine(e, r, n, t) { function o(r, n) { TopicsPage_regeneratorDefine2(e, r, function (e) { return this._invoke(r, n, e); }); } r ? i ? i(e, r, { value: n, enumerable: !t, configurable: !t, writable: !t }) : e[r] = n : (o("next", 0), o("throw", 1), o("return", 2)); }, TopicsPage_regeneratorDefine2(e, r, n, t); }
function TopicsPage_asyncGeneratorStep(n, t, e, r, o, a, c) { try { var i = n[a](c), u = i.value; } catch (n) { return void e(n); } i.done ? t(u) : Promise.resolve(u).then(r, o); }
function TopicsPage_asyncToGenerator(n) { return function () { var t = this, e = arguments; return new Promise(function (r, o) { var a = n.apply(t, e); function _next(n) { TopicsPage_asyncGeneratorStep(a, r, o, _next, _throw, "next", n); } function _throw(n) { TopicsPage_asyncGeneratorStep(a, r, o, _next, _throw, "throw", n); } _next(void 0); }); }; }
function TopicsPage_slicedToArray(r, e) { return TopicsPage_arrayWithHoles(r) || TopicsPage_iterableToArrayLimit(r, e) || TopicsPage_unsupportedIterableToArray(r, e) || TopicsPage_nonIterableRest(); }
function TopicsPage_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function TopicsPage_unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return TopicsPage_arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? TopicsPage_arrayLikeToArray(r, a) : void 0; } }
function TopicsPage_arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function TopicsPage_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function TopicsPage_arrayWithHoles(r) { if (Array.isArray(r)) return r; }




var TopicsPage = function TopicsPage(_ref) {
  var appState = _ref.appState;
  var topics = appState.topics,
    agents = appState.agents,
    showTopicDetails = appState.showTopicDetails,
    loadTopics = appState.loadTopics,
    appLoading = appState.loading;
  var _useState = (0,react.useState)(false),
    _useState2 = TopicsPage_slicedToArray(_useState, 2),
    loading = _useState2[0],
    setLoading = _useState2[1];

  // Simple: show loading if app is loading AND we don't have topics yet
  // This ensures we show spinner on initial load until topics arrive
  var showLoading = appLoading && topics.length === 0;

  // Get agent count for a topic
  var getAgentCountForTopic = function getAgentCountForTopic(topicName) {
    if (!agents || !Array.isArray(agents)) return 0;
    return agents.filter(function (agent) {
      if (!agent.topics || !Array.isArray(agent.topics)) return false;
      return agent.topics.includes(topicName);
    }).length;
  };

  // Handle refresh
  var handleRefresh = /*#__PURE__*/function () {
    var _ref2 = TopicsPage_asyncToGenerator(/*#__PURE__*/TopicsPage_regenerator().m(function _callee() {
      return TopicsPage_regenerator().w(function (_context) {
        while (1) switch (_context.n) {
          case 0:
            setLoading(true);
            _context.n = 1;
            return loadTopics();
          case 1:
            setLoading(false);
          case 2:
            return _context.a(2);
        }
      }, _callee);
    }));
    return function handleRefresh() {
      return _ref2.apply(this, arguments);
    };
  }();

  // Handle topic click
  var handleTopicClick = function handleTopicClick(topic) {
    var topicName = typeof topic === 'string' ? topic : topic.name; // Changed from topic.topic to topic.name
    var topicData = {
      name: topicName,
      subscribers: getAgentCountForTopic(topicName)
    };
    showTopicDetails(topicData);
  };

  // Format topics data
  var topicsData = Array.isArray(topics) ? topics.map(function (topic) {
    var topicName = typeof topic === 'string' ? topic : topic.topic || topic.name;
    return {
      name: topicName,
      subscribers: getAgentCountForTopic(topicName),
      runs: 0,
      // We don't have runs data in local mode
      lastTriggered: 'Unknown'
    };
  }) : [];
  if (showLoading) {
    return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "space-y-6",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "flex items-center justify-between",
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex items-center space-x-4",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
            className: "h-8 w-8 text-[var(--color-brand-blue-600)]"
          }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
              className: "text-3xl font-bold text-gray-900",
              children: "Topics"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
              className: "text-sm text-gray-500 mt-1",
              children: "Registered topics for local agents"
            })]
          })]
        })
      }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8",
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex items-center justify-center",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
            className: "animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
            className: "ml-3 text-gray-600",
            children: "Loading topics..."
          })]
        })
      })]
    });
  }
  return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
    className: "space-y-6",
    children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-center justify-between",
      children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center space-x-4",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
          className: "h-8 w-8 text-[var(--color-brand-blue-600)]"
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
            className: "text-3xl font-bold text-gray-900",
            children: "Topics"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-sm text-gray-500 mt-1",
            children: "Registered topics that agents can subscribe to"
          })]
        })]
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)(Button, {
        onClick: handleRefresh,
        disabled: loading,
        variant: "outline",
        className: "flex items-center gap-2",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(RefreshCw, {
          className: "w-4 h-4 ".concat(loading ? 'animate-spin' : '')
        }), "Refresh"]
      })]
    }), topicsData.length === 0 ? /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "text-center",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
          className: "mx-auto h-12 w-12 text-gray-400"
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("h3", {
          className: "mt-4 text-sm font-medium text-gray-900",
          children: "No topics found"
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
          className: "mt-2 text-sm text-gray-500",
          children: "Deploy agents with topic subscriptions to see topics here"
        })]
      })
    }) : /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] overflow-hidden",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("table", {
        className: "min-w-full divide-y divide-gray-200",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)("thead", {
          className: "bg-gray-50",
          children: /*#__PURE__*/(0,jsx_runtime.jsxs)("tr", {
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Topic Name"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Subscribers"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Runs"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Last Triggered"
            })]
          })
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("tbody", {
          className: "bg-white divide-y divide-gray-200",
          children: topicsData.map(function (topic, index) {
            return /*#__PURE__*/(0,jsx_runtime.jsxs)("tr", {
              className: "hover:bg-gray-50 cursor-pointer transition-colors duration-150",
              onClick: function onClick() {
                return handleTopicClick(topic);
              },
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "flex items-center",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
                    className: "w-4 h-4 text-[var(--color-brand-blue-500)] mr-3"
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                    className: "text-sm font-medium text-gray-900",
                    children: topic.name
                  })]
                })
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "text-sm text-gray-900",
                  children: topic.subscribers
                })
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "text-sm text-gray-500",
                  children: topic.runs
                })
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
                  className: "text-sm text-gray-500",
                  children: topic.lastTriggered
                })
              })]
            }, topic.name || index);
          })
        })]
      })
    })]
  });
};
/* harmony default export */ const components_TopicsPage = (TopicsPage);
;// ./src/components/TopicDetailsPage.jsx
function TopicDetailsPage_typeof(o) { "@babel/helpers - typeof"; return TopicDetailsPage_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, TopicDetailsPage_typeof(o); }
function TopicDetailsPage_ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function TopicDetailsPage_objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? TopicDetailsPage_ownKeys(Object(t), !0).forEach(function (r) { TopicDetailsPage_defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : TopicDetailsPage_ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function TopicDetailsPage_defineProperty(e, r, t) { return (r = TopicDetailsPage_toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function TopicDetailsPage_toPropertyKey(t) { var i = TopicDetailsPage_toPrimitive(t, "string"); return "symbol" == TopicDetailsPage_typeof(i) ? i : i + ""; }
function TopicDetailsPage_toPrimitive(t, r) { if ("object" != TopicDetailsPage_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != TopicDetailsPage_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }







var TopicDetailsPage = function TopicDetailsPage(_ref) {
  var appState = _ref.appState;
  var selectedTopic = appState.selectedTopic,
    agents = appState.agents,
    showTopicsList = appState.showTopicsList,
    showAgentDetails = appState.showAgentDetails;
  if (!selectedTopic) {
    return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "text-center py-12",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("p", {
        className: "text-gray-500",
        children: "No topic selected"
      }), /*#__PURE__*/(0,jsx_runtime.jsx)(Button, {
        onClick: showTopicsList,
        variant: "outline",
        className: "mt-4",
        children: "Back to Topics"
      })]
    });
  }

  // Get the topic name properly
  var topicName = typeof selectedTopic === 'string' ? selectedTopic : selectedTopic === null || selectedTopic === void 0 ? void 0 : selectedTopic.name;

  // Get agents that subscribe to this topic
  // Use the real data structure from the router
  var subscribingAgents = agents.filter(function (agent) {
    if (!agent.topics || !Array.isArray(agent.topics)) return false;
    return agent.topics.includes(topicName);
  });

  // Create a mock selected agent for the event cards to work properly
  // This allows us to reuse the existing SendTestEventCard and MessageFeedCard
  var mockSelectedAgent = {
    name: topicName,
    // Create mock functions structure for compatibility with SendTestEventCard
    functions: [{
      name: 'topic_handler',
      triggers: [{
        type: 'topic',
        topic: topicName
      }]
    }]
  };

  // Enhanced app state for the cards - configured specifically for Topic Details
  var topicAppState = TopicDetailsPage_objectSpread(TopicDetailsPage_objectSpread({}, appState), {}, {
    selectedAgent: mockSelectedAgent,
    topics: [topicName],
    // Single topic for this page
    isTopicDetailsPage: true // Flag to indicate this is Topic Details page
  });
  return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
    className: "space-y-6",
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "flex items-center justify-between mb-8",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center space-x-4",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Radio, {
          className: "h-8 w-8 text-[var(--color-brand-blue-600)]"
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
            className: "text-3xl font-bold text-gray-900",
            children: topicName
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
            className: "flex items-center mt-2 space-x-4",
            children: /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
              className: "text-sm text-gray-500",
              children: [subscribingAgents.length, " subscribing agents"]
            })
          })]
        })]
      })
    }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "grid grid-cols-1 lg:grid-cols-3 gap-6",
      children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "lg:col-span-2 space-y-6",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(components_SendTestEventCard, {
          appState: topicAppState
        }), /*#__PURE__*/(0,jsx_runtime.jsx)(components_MessageFeedCard, {
          appState: topicAppState
        })]
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "space-y-6",
        children: [/*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
          className: "border-0 shadow-sm bg-gray-50",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
            className: "pb-3",
            children: /*#__PURE__*/(0,jsx_runtime.jsxs)(CardTitle, {
              className: "text-lg font-semibold text-gray-900",
              children: ["Subscribing Agents (", subscribingAgents.length, ")"]
            })
          }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
            className: "pt-0 pb-6",
            children: subscribingAgents.length === 0 ? /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "text-center py-4",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Waypoints, {
                className: "w-8 h-8 mx-auto mb-2 text-gray-400"
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
                className: "text-sm text-gray-500",
                children: "No agents subscribe to this topic"
              })]
            }) : /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
              className: "space-y-3",
              children: subscribingAgents.map(function (agent, index) {
                // Show topics this agent subscribes to
                var relevantTopics = agent.topics || [];
                return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "border border-gray-200 rounded-md p-3 hover:bg-gray-50 cursor-pointer transition-colors",
                  onClick: function onClick() {
                    return showAgentDetails(agent);
                  },
                  children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                    className: "flex items-center mb-2",
                    children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Waypoints, {
                      className: "w-4 h-4 text-[var(--color-brand-blue-500)] mr-2"
                    }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                      className: "text-sm font-medium text-gray-900 hover:text-blue-600 transition-colors",
                      children: agent.name
                    }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                      className: "ml-auto text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full",
                      children: agent.status || 'unknown'
                    })]
                  }), relevantTopics.length > 0 && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                    className: "ml-6",
                    children: [/*#__PURE__*/(0,jsx_runtime.jsx)("p", {
                      className: "text-xs text-gray-500 mb-1",
                      children: "Subscribed topics:"
                    }), relevantTopics.map(function (topic, topicIndex) {
                      return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                        className: "text-xs text-gray-600",
                        children: ["\u2022 ", topic]
                      }, topicIndex);
                    })]
                  })]
                }, agent.name || index);
              })
            })
          })]
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)(Card, {
          className: "border-0 shadow-sm bg-gray-50",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(CardHeader, {
            className: "pb-3",
            children: /*#__PURE__*/(0,jsx_runtime.jsx)(CardTitle, {
              className: "text-lg font-semibold text-gray-900",
              children: "Topic Details"
            })
          }), /*#__PURE__*/(0,jsx_runtime.jsx)(CardContent, {
            className: "pt-0 pb-6",
            children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
              className: "grid grid-cols-1 gap-4",
              children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Name"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-900 font-medium",
                  children: topicName
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Subscribers"
                }), /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                  className: "text-sm text-gray-900",
                  children: [subscribingAgents.length, " agents"]
                })]
              }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                className: "flex justify-between py-2",
                children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm font-medium text-gray-600",
                  children: "Type"
                }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-900",
                  children: "Event Topic"
                })]
              })]
            })
          })]
        })]
      })]
    })]
  });
};
/* harmony default export */ const components_TopicDetailsPage = (TopicDetailsPage);
;// ./node_modules/lucide-react/dist/esm/icons/plus.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const plus_iconNode = [
  ["path", { d: "M5 12h14", key: "1ays0h" }],
  ["path", { d: "M12 5v14", key: "s699le" }]
];
const Plus = createLucideIcon("plus", plus_iconNode);


//# sourceMappingURL=plus.js.map

;// ./node_modules/lucide-react/dist/esm/icons/shield.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const shield_iconNode = [
  [
    "path",
    {
      d: "M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z",
      key: "oel41y"
    }
  ]
];
const Shield = createLucideIcon("shield", shield_iconNode);


//# sourceMappingURL=shield.js.map

;// ./node_modules/lucide-react/dist/esm/icons/check.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const check_iconNode = [["path", { d: "M20 6 9 17l-5-5", key: "1gmf2c" }]];
const Check = createLucideIcon("check", check_iconNode);


//# sourceMappingURL=check.js.map

;// ./node_modules/lucide-react/dist/esm/icons/x.js
/**
 * @license lucide-react v0.487.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */



const x_iconNode = [
  ["path", { d: "M18 6 6 18", key: "1bl5f8" }],
  ["path", { d: "m6 6 12 12", key: "d8bk6v" }]
];
const x_X = createLucideIcon("x", x_iconNode);


//# sourceMappingURL=x.js.map

;// ./src/components/LLMConfigPage.jsx
function LLMConfigPage_regenerator() { /*! regenerator-runtime -- Copyright (c) 2014-present, Facebook, Inc. -- license (MIT): https://github.com/babel/babel/blob/main/packages/babel-helpers/LICENSE */ var e, t, r = "function" == typeof Symbol ? Symbol : {}, n = r.iterator || "@@iterator", o = r.toStringTag || "@@toStringTag"; function i(r, n, o, i) { var c = n && n.prototype instanceof Generator ? n : Generator, u = Object.create(c.prototype); return LLMConfigPage_regeneratorDefine2(u, "_invoke", function (r, n, o) { var i, c, u, f = 0, p = o || [], y = !1, G = { p: 0, n: 0, v: e, a: d, f: d.bind(e, 4), d: function d(t, r) { return i = t, c = 0, u = e, G.n = r, a; } }; function d(r, n) { for (c = r, u = n, t = 0; !y && f && !o && t < p.length; t++) { var o, i = p[t], d = G.p, l = i[2]; r > 3 ? (o = l === n) && (u = i[(c = i[4]) ? 5 : (c = 3, 3)], i[4] = i[5] = e) : i[0] <= d && ((o = r < 2 && d < i[1]) ? (c = 0, G.v = n, G.n = i[1]) : d < l && (o = r < 3 || i[0] > n || n > l) && (i[4] = r, i[5] = n, G.n = l, c = 0)); } if (o || r > 1) return a; throw y = !0, n; } return function (o, p, l) { if (f > 1) throw TypeError("Generator is already running"); for (y && 1 === p && d(p, l), c = p, u = l; (t = c < 2 ? e : u) || !y;) { i || (c ? c < 3 ? (c > 1 && (G.n = -1), d(c, u)) : G.n = u : G.v = u); try { if (f = 2, i) { if (c || (o = "next"), t = i[o]) { if (!(t = t.call(i, u))) throw TypeError("iterator result is not an object"); if (!t.done) return t; u = t.value, c < 2 && (c = 0); } else 1 === c && (t = i.return) && t.call(i), c < 2 && (u = TypeError("The iterator does not provide a '" + o + "' method"), c = 1); i = e; } else if ((t = (y = G.n < 0) ? u : r.call(n, G)) !== a) break; } catch (t) { i = e, c = 1, u = t; } finally { f = 1; } } return { value: t, done: y }; }; }(r, o, i), !0), u; } var a = {}; function Generator() {} function GeneratorFunction() {} function GeneratorFunctionPrototype() {} t = Object.getPrototypeOf; var c = [][n] ? t(t([][n]())) : (LLMConfigPage_regeneratorDefine2(t = {}, n, function () { return this; }), t), u = GeneratorFunctionPrototype.prototype = Generator.prototype = Object.create(c); function f(e) { return Object.setPrototypeOf ? Object.setPrototypeOf(e, GeneratorFunctionPrototype) : (e.__proto__ = GeneratorFunctionPrototype, LLMConfigPage_regeneratorDefine2(e, o, "GeneratorFunction")), e.prototype = Object.create(u), e; } return GeneratorFunction.prototype = GeneratorFunctionPrototype, LLMConfigPage_regeneratorDefine2(u, "constructor", GeneratorFunctionPrototype), LLMConfigPage_regeneratorDefine2(GeneratorFunctionPrototype, "constructor", GeneratorFunction), GeneratorFunction.displayName = "GeneratorFunction", LLMConfigPage_regeneratorDefine2(GeneratorFunctionPrototype, o, "GeneratorFunction"), LLMConfigPage_regeneratorDefine2(u), LLMConfigPage_regeneratorDefine2(u, o, "Generator"), LLMConfigPage_regeneratorDefine2(u, n, function () { return this; }), LLMConfigPage_regeneratorDefine2(u, "toString", function () { return "[object Generator]"; }), (LLMConfigPage_regenerator = function _regenerator() { return { w: i, m: f }; })(); }
function LLMConfigPage_regeneratorDefine2(e, r, n, t) { var i = Object.defineProperty; try { i({}, "", {}); } catch (e) { i = 0; } LLMConfigPage_regeneratorDefine2 = function _regeneratorDefine(e, r, n, t) { function o(r, n) { LLMConfigPage_regeneratorDefine2(e, r, function (e) { return this._invoke(r, n, e); }); } r ? i ? i(e, r, { value: n, enumerable: !t, configurable: !t, writable: !t }) : e[r] = n : (o("next", 0), o("throw", 1), o("return", 2)); }, LLMConfigPage_regeneratorDefine2(e, r, n, t); }
function LLMConfigPage_asyncGeneratorStep(n, t, e, r, o, a, c) { try { var i = n[a](c), u = i.value; } catch (n) { return void e(n); } i.done ? t(u) : Promise.resolve(u).then(r, o); }
function LLMConfigPage_asyncToGenerator(n) { return function () { var t = this, e = arguments; return new Promise(function (r, o) { var a = n.apply(t, e); function _next(n) { LLMConfigPage_asyncGeneratorStep(a, r, o, _next, _throw, "next", n); } function _throw(n) { LLMConfigPage_asyncGeneratorStep(a, r, o, _next, _throw, "throw", n); } _next(void 0); }); }; }
function LLMConfigPage_slicedToArray(r, e) { return LLMConfigPage_arrayWithHoles(r) || LLMConfigPage_iterableToArrayLimit(r, e) || LLMConfigPage_unsupportedIterableToArray(r, e) || LLMConfigPage_nonIterableRest(); }
function LLMConfigPage_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function LLMConfigPage_unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return LLMConfigPage_arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? LLMConfigPage_arrayLikeToArray(r, a) : void 0; } }
function LLMConfigPage_arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function LLMConfigPage_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function LLMConfigPage_arrayWithHoles(r) { if (Array.isArray(r)) return r; }




var LLMConfigPage = function LLMConfigPage() {
  var _useState = (0,react.useState)([]),
    _useState2 = LLMConfigPage_slicedToArray(_useState, 2),
    providers = _useState2[0],
    setProviders = _useState2[1];
  var _useState3 = (0,react.useState)(true),
    _useState4 = LLMConfigPage_slicedToArray(_useState3, 2),
    loading = _useState4[0],
    setLoading = _useState4[1];
  var _useState5 = (0,react.useState)(false),
    _useState6 = LLMConfigPage_slicedToArray(_useState5, 2),
    saving = _useState6[0],
    setSaving = _useState6[1];
  var _useState7 = (0,react.useState)(null),
    _useState8 = LLMConfigPage_slicedToArray(_useState7, 2),
    error = _useState8[0],
    setError = _useState8[1];
  var _useState9 = (0,react.useState)(null),
    _useState0 = LLMConfigPage_slicedToArray(_useState9, 2),
    successMessage = _useState0[0],
    setSuccessMessage = _useState0[1];

  // Add key form state
  var _useState1 = (0,react.useState)(false),
    _useState10 = LLMConfigPage_slicedToArray(_useState1, 2),
    showAddForm = _useState10[0],
    setShowAddForm = _useState10[1];
  var _useState11 = (0,react.useState)(""),
    _useState12 = LLMConfigPage_slicedToArray(_useState11, 2),
    selectedProvider = _useState12[0],
    setSelectedProvider = _useState12[1];
  var _useState13 = (0,react.useState)(""),
    _useState14 = LLMConfigPage_slicedToArray(_useState13, 2),
    apiKey = _useState14[0],
    setApiKey = _useState14[1];
  var loadProviders = /*#__PURE__*/function () {
    var _ref = LLMConfigPage_asyncToGenerator(/*#__PURE__*/LLMConfigPage_regenerator().m(function _callee() {
      var response, data, _t;
      return LLMConfigPage_regenerator().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            _context.p = 0;
            _context.n = 1;
            return fetch("/api/unstable/llm-config/local");
          case 1:
            response = _context.v;
            if (!response.ok) {
              _context.n = 3;
              break;
            }
            _context.n = 2;
            return response.json();
          case 2:
            data = _context.v;
            setProviders(data.providers || []);
            _context.n = 4;
            break;
          case 3:
            setError("Failed to load provider configuration");
          case 4:
            _context.n = 6;
            break;
          case 5:
            _context.p = 5;
            _t = _context.v;
            console.error("Failed to load LLM config:", _t);
            setError("Failed to connect to router");
          case 6:
            _context.p = 6;
            setLoading(false);
            return _context.f(6);
          case 7:
            return _context.a(2);
        }
      }, _callee, null, [[0, 5, 6, 7]]);
    }));
    return function loadProviders() {
      return _ref.apply(this, arguments);
    };
  }();
  (0,react.useEffect)(function () {
    loadProviders();
  }, []);
  var handleRefresh = /*#__PURE__*/function () {
    var _ref2 = LLMConfigPage_asyncToGenerator(/*#__PURE__*/LLMConfigPage_regenerator().m(function _callee2() {
      return LLMConfigPage_regenerator().w(function (_context2) {
        while (1) switch (_context2.n) {
          case 0:
            setLoading(true);
            setError(null);
            _context2.n = 1;
            return loadProviders();
          case 1:
            return _context2.a(2);
        }
      }, _callee2);
    }));
    return function handleRefresh() {
      return _ref2.apply(this, arguments);
    };
  }();
  var handleAddKey = /*#__PURE__*/function () {
    var _ref3 = LLMConfigPage_asyncToGenerator(/*#__PURE__*/LLMConfigPage_regenerator().m(function _callee3(e) {
      var response, data, _data, _t2;
      return LLMConfigPage_regenerator().w(function (_context3) {
        while (1) switch (_context3.p = _context3.n) {
          case 0:
            e.preventDefault();
            if (!(!selectedProvider || !apiKey.trim())) {
              _context3.n = 1;
              break;
            }
            return _context3.a(2);
          case 1:
            setSaving(true);
            setError(null);
            setSuccessMessage(null);
            _context3.p = 2;
            _context3.n = 3;
            return fetch("/api/unstable/llm-config/local", {
              method: "POST",
              headers: {
                "Content-Type": "application/json"
              },
              body: JSON.stringify({
                provider: selectedProvider,
                api_key: apiKey.trim()
              })
            });
          case 3:
            response = _context3.v;
            if (!response.ok) {
              _context3.n = 6;
              break;
            }
            _context3.n = 4;
            return response.json();
          case 4:
            data = _context3.v;
            setSuccessMessage(data.message);
            setShowAddForm(false);
            setSelectedProvider("");
            setApiKey("");
            _context3.n = 5;
            return loadProviders();
          case 5:
            _context3.n = 8;
            break;
          case 6:
            _context3.n = 7;
            return response.json();
          case 7:
            _data = _context3.v;
            setError(_data.detail || "Failed to save API key");
          case 8:
            _context3.n = 10;
            break;
          case 9:
            _context3.p = 9;
            _t2 = _context3.v;
            setError("Failed to connect to router");
          case 10:
            _context3.p = 10;
            setSaving(false);
            return _context3.f(10);
          case 11:
            return _context3.a(2);
        }
      }, _callee3, null, [[2, 9, 10, 11]]);
    }));
    return function handleAddKey(_x) {
      return _ref3.apply(this, arguments);
    };
  }();
  var handleRemoveKey = /*#__PURE__*/function () {
    var _ref4 = LLMConfigPage_asyncToGenerator(/*#__PURE__*/LLMConfigPage_regenerator().m(function _callee4(provider) {
      var response, data, _data2, _t3;
      return LLMConfigPage_regenerator().w(function (_context4) {
        while (1) switch (_context4.p = _context4.n) {
          case 0:
            if (confirm("Remove API key for ".concat(provider, "? This will delete it from your Keychain."))) {
              _context4.n = 1;
              break;
            }
            return _context4.a(2);
          case 1:
            setError(null);
            setSuccessMessage(null);
            _context4.p = 2;
            _context4.n = 3;
            return fetch("/api/unstable/llm-config/local/".concat(provider), {
              method: "DELETE"
            });
          case 3:
            response = _context4.v;
            if (!response.ok) {
              _context4.n = 6;
              break;
            }
            _context4.n = 4;
            return response.json();
          case 4:
            data = _context4.v;
            setSuccessMessage(data.message);
            _context4.n = 5;
            return loadProviders();
          case 5:
            _context4.n = 8;
            break;
          case 6:
            _context4.n = 7;
            return response.json();
          case 7:
            _data2 = _context4.v;
            setError(_data2.detail || "Failed to remove API key");
          case 8:
            _context4.n = 10;
            break;
          case 9:
            _context4.p = 9;
            _t3 = _context4.v;
            setError("Failed to connect to router");
          case 10:
            return _context4.a(2);
        }
      }, _callee4, null, [[2, 9]]);
    }));
    return function handleRemoveKey(_x2) {
      return _ref4.apply(this, arguments);
    };
  }();

  // Auto-clear messages after 4 seconds
  (0,react.useEffect)(function () {
    if (successMessage) {
      var timer = setTimeout(function () {
        return setSuccessMessage(null);
      }, 4000);
      return function () {
        return clearTimeout(timer);
      };
    }
  }, [successMessage]);
  (0,react.useEffect)(function () {
    if (error) {
      var timer = setTimeout(function () {
        return setError(null);
      }, 6000);
      return function () {
        return clearTimeout(timer);
      };
    }
  }, [error]);
  var unconfiguredProviders = providers.filter(function (p) {
    return !p.configured;
  });
  if (loading && providers.length === 0) {
    return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "space-y-6",
      children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center space-x-4",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(KeyRound, {
          className: "h-8 w-8 text-[var(--color-brand-blue-600)]"
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
            className: "text-3xl font-bold text-gray-900",
            children: "LLM Keys"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-sm text-gray-500 mt-1",
            children: "Manage API keys for local LLM providers"
          })]
        })]
      }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
        className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-8",
        children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex items-center justify-center",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("div", {
            className: "animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
            className: "ml-3 text-gray-600",
            children: "Loading provider configuration..."
          })]
        })
      })]
    });
  }
  return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
    className: "space-y-6",
    children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-center justify-between",
      children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center space-x-4",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)(KeyRound, {
          className: "h-8 w-8 text-[var(--color-brand-blue-600)]"
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h1", {
            className: "text-3xl font-bold text-gray-900",
            children: "LLM Keys"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("p", {
            className: "text-sm text-gray-500 mt-1",
            children: "Manage API keys for local LLM providers"
          })]
        })]
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex items-center gap-2",
        children: [unconfiguredProviders.length > 0 && /*#__PURE__*/(0,jsx_runtime.jsxs)(Button, {
          onClick: function onClick() {
            setShowAddForm(true);
            if (unconfiguredProviders.length > 0) {
              setSelectedProvider(unconfiguredProviders[0].provider);
            }
          },
          className: "flex items-center gap-2",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Plus, {
            className: "w-4 h-4"
          }), "Add Key"]
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)(Button, {
          onClick: handleRefresh,
          disabled: loading,
          variant: "outline",
          className: "flex items-center gap-2",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(RefreshCw, {
            className: "w-4 h-4 ".concat(loading ? "animate-spin" : "")
          }), "Refresh"]
        })]
      })]
    }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Shield, {
        className: "w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0"
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "text-sm text-blue-800",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
          className: "font-medium",
          children: "Local Development Only"
        }), " \u2014 API keys are stored securely in your macOS Keychain. Changes take effect immediately without restarting the router."]
      })]
    }), successMessage && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Check, {
        className: "w-4 h-4 flex-shrink-0"
      }), successMessage]
    }), error && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)(x_X, {
        className: "w-4 h-4 flex-shrink-0"
      }), error]
    }), showAddForm && /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] p-6",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)("h3", {
        className: "text-sm font-semibold text-gray-900 mb-4",
        children: "Add API Key"
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)("form", {
        onSubmit: handleAddKey,
        className: "flex items-end gap-4",
        children: [/*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex-shrink-0",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
            className: "block text-xs font-medium text-gray-600 mb-1.5",
            children: "Provider"
          }), /*#__PURE__*/(0,jsx_runtime.jsxs)("select", {
            value: selectedProvider,
            onChange: function onChange(e) {
              return setSelectedProvider(e.target.value);
            },
            className: "block w-40 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500",
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("option", {
              value: "",
              children: "Select..."
            }), providers.map(function (p) {
              return /*#__PURE__*/(0,jsx_runtime.jsxs)("option", {
                value: p.provider,
                children: [p.provider.charAt(0).toUpperCase() + p.provider.slice(1), p.configured ? " (update)" : ""]
              }, p.provider);
            })]
          })]
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex-1",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)("label", {
            className: "block text-xs font-medium text-gray-600 mb-1.5",
            children: "API Key"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)("input", {
            type: "password",
            value: apiKey,
            onChange: function onChange(e) {
              return setApiKey(e.target.value);
            },
            placeholder: selectedProvider ? "Enter ".concat(selectedProvider, " API key...") : "Select a provider first",
            className: "block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500",
            disabled: !selectedProvider
          })]
        }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
          className: "flex gap-2 flex-shrink-0",
          children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Button, {
            type: "submit",
            disabled: !selectedProvider || !apiKey.trim() || saving,
            children: saving ? "Saving..." : "Save"
          }), /*#__PURE__*/(0,jsx_runtime.jsx)(Button, {
            type: "button",
            variant: "outline",
            onClick: function onClick() {
              setShowAddForm(false);
              setSelectedProvider("");
              setApiKey("");
            },
            children: "Cancel"
          })]
        })]
      })]
    }), /*#__PURE__*/(0,jsx_runtime.jsx)("div", {
      className: "bg-white rounded-lg border border-[var(--color-warm-gray-200)] overflow-hidden",
      children: /*#__PURE__*/(0,jsx_runtime.jsxs)("table", {
        className: "min-w-full divide-y divide-gray-200",
        children: [/*#__PURE__*/(0,jsx_runtime.jsx)("thead", {
          className: "bg-gray-50",
          children: /*#__PURE__*/(0,jsx_runtime.jsxs)("tr", {
            children: [/*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Provider"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Status"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Storage"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Environment Variable"
            }), /*#__PURE__*/(0,jsx_runtime.jsx)("th", {
              className: "px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
              children: "Actions"
            })]
          })
        }), /*#__PURE__*/(0,jsx_runtime.jsx)("tbody", {
          className: "bg-white divide-y divide-gray-200",
          children: providers.map(function (provider) {
            return /*#__PURE__*/(0,jsx_runtime.jsxs)("tr", {
              className: "hover:bg-gray-50 transition-colors duration-150",
              children: [/*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "flex items-center",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)(KeyRound, {
                    className: "w-4 h-4 mr-3 ".concat(provider.configured ? "text-[var(--color-brand-blue-500)]" : "text-gray-300")
                  }), /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                    className: "text-sm font-medium text-gray-900",
                    children: provider.provider.charAt(0).toUpperCase() + provider.provider.slice(1)
                  })]
                })
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: provider.configured ? /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                  className: "inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-full bg-green-100 text-green-800",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                    className: "w-1.5 h-1.5 rounded-full bg-green-500"
                  }), "Configured"]
                }) : /*#__PURE__*/(0,jsx_runtime.jsxs)("span", {
                  className: "inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-full bg-gray-100 text-gray-600",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                    className: "w-1.5 h-1.5 rounded-full bg-gray-400"
                  }), "Not configured"]
                })
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: /*#__PURE__*/(0,jsx_runtime.jsx)("span", {
                  className: "text-sm text-gray-500",
                  children: provider.storage_type || (provider.configured ? "unknown" : "\u2014")
                })
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap",
                children: /*#__PURE__*/(0,jsx_runtime.jsx)("code", {
                  className: "text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded",
                  children: provider.env_var
                })
              }), /*#__PURE__*/(0,jsx_runtime.jsx)("td", {
                className: "px-6 py-4 whitespace-nowrap text-right",
                children: /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
                  className: "flex items-center justify-end gap-2",
                  children: [/*#__PURE__*/(0,jsx_runtime.jsx)("button", {
                    onClick: function onClick() {
                      setShowAddForm(true);
                      setSelectedProvider(provider.provider);
                      setApiKey("");
                    },
                    className: "text-xs text-blue-600 hover:text-blue-800 font-medium",
                    children: provider.configured ? "Update" : "Add"
                  }), provider.configured && /*#__PURE__*/(0,jsx_runtime.jsxs)("button", {
                    onClick: function onClick() {
                      return handleRemoveKey(provider.provider);
                    },
                    className: "text-xs text-red-500 hover:text-red-700 font-medium flex items-center gap-1",
                    children: [/*#__PURE__*/(0,jsx_runtime.jsx)(Trash2, {
                      className: "w-3 h-3"
                    }), "Remove"]
                  })]
                })
              })]
            }, provider.provider);
          })
        })]
      })
    })]
  });
};
/* harmony default export */ const components_LLMConfigPage = (LLMConfigPage);
;// ./src/components/App.jsx
function App_typeof(o) { "@babel/helpers - typeof"; return App_typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, App_typeof(o); }
function App_ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function App_objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? App_ownKeys(Object(t), !0).forEach(function (r) { App_defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : App_ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function App_defineProperty(e, r, t) { return (r = App_toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function App_toPropertyKey(t) { var i = App_toPrimitive(t, "string"); return "symbol" == App_typeof(i) ? i : i + ""; }
function App_toPrimitive(t, r) { if ("object" != App_typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != App_typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function App_regenerator() { /*! regenerator-runtime -- Copyright (c) 2014-present, Facebook, Inc. -- license (MIT): https://github.com/babel/babel/blob/main/packages/babel-helpers/LICENSE */ var e, t, r = "function" == typeof Symbol ? Symbol : {}, n = r.iterator || "@@iterator", o = r.toStringTag || "@@toStringTag"; function i(r, n, o, i) { var c = n && n.prototype instanceof Generator ? n : Generator, u = Object.create(c.prototype); return App_regeneratorDefine2(u, "_invoke", function (r, n, o) { var i, c, u, f = 0, p = o || [], y = !1, G = { p: 0, n: 0, v: e, a: d, f: d.bind(e, 4), d: function d(t, r) { return i = t, c = 0, u = e, G.n = r, a; } }; function d(r, n) { for (c = r, u = n, t = 0; !y && f && !o && t < p.length; t++) { var o, i = p[t], d = G.p, l = i[2]; r > 3 ? (o = l === n) && (u = i[(c = i[4]) ? 5 : (c = 3, 3)], i[4] = i[5] = e) : i[0] <= d && ((o = r < 2 && d < i[1]) ? (c = 0, G.v = n, G.n = i[1]) : d < l && (o = r < 3 || i[0] > n || n > l) && (i[4] = r, i[5] = n, G.n = l, c = 0)); } if (o || r > 1) return a; throw y = !0, n; } return function (o, p, l) { if (f > 1) throw TypeError("Generator is already running"); for (y && 1 === p && d(p, l), c = p, u = l; (t = c < 2 ? e : u) || !y;) { i || (c ? c < 3 ? (c > 1 && (G.n = -1), d(c, u)) : G.n = u : G.v = u); try { if (f = 2, i) { if (c || (o = "next"), t = i[o]) { if (!(t = t.call(i, u))) throw TypeError("iterator result is not an object"); if (!t.done) return t; u = t.value, c < 2 && (c = 0); } else 1 === c && (t = i.return) && t.call(i), c < 2 && (u = TypeError("The iterator does not provide a '" + o + "' method"), c = 1); i = e; } else if ((t = (y = G.n < 0) ? u : r.call(n, G)) !== a) break; } catch (t) { i = e, c = 1, u = t; } finally { f = 1; } } return { value: t, done: y }; }; }(r, o, i), !0), u; } var a = {}; function Generator() {} function GeneratorFunction() {} function GeneratorFunctionPrototype() {} t = Object.getPrototypeOf; var c = [][n] ? t(t([][n]())) : (App_regeneratorDefine2(t = {}, n, function () { return this; }), t), u = GeneratorFunctionPrototype.prototype = Generator.prototype = Object.create(c); function f(e) { return Object.setPrototypeOf ? Object.setPrototypeOf(e, GeneratorFunctionPrototype) : (e.__proto__ = GeneratorFunctionPrototype, App_regeneratorDefine2(e, o, "GeneratorFunction")), e.prototype = Object.create(u), e; } return GeneratorFunction.prototype = GeneratorFunctionPrototype, App_regeneratorDefine2(u, "constructor", GeneratorFunctionPrototype), App_regeneratorDefine2(GeneratorFunctionPrototype, "constructor", GeneratorFunction), GeneratorFunction.displayName = "GeneratorFunction", App_regeneratorDefine2(GeneratorFunctionPrototype, o, "GeneratorFunction"), App_regeneratorDefine2(u), App_regeneratorDefine2(u, o, "Generator"), App_regeneratorDefine2(u, n, function () { return this; }), App_regeneratorDefine2(u, "toString", function () { return "[object Generator]"; }), (App_regenerator = function _regenerator() { return { w: i, m: f }; })(); }
function App_regeneratorDefine2(e, r, n, t) { var i = Object.defineProperty; try { i({}, "", {}); } catch (e) { i = 0; } App_regeneratorDefine2 = function _regeneratorDefine(e, r, n, t) { function o(r, n) { App_regeneratorDefine2(e, r, function (e) { return this._invoke(r, n, e); }); } r ? i ? i(e, r, { value: n, enumerable: !t, configurable: !t, writable: !t }) : e[r] = n : (o("next", 0), o("throw", 1), o("return", 2)); }, App_regeneratorDefine2(e, r, n, t); }
function App_asyncGeneratorStep(n, t, e, r, o, a, c) { try { var i = n[a](c), u = i.value; } catch (n) { return void e(n); } i.done ? t(u) : Promise.resolve(u).then(r, o); }
function App_asyncToGenerator(n) { return function () { var t = this, e = arguments; return new Promise(function (r, o) { var a = n.apply(t, e); function _next(n) { App_asyncGeneratorStep(a, r, o, _next, _throw, "next", n); } function _throw(n) { App_asyncGeneratorStep(a, r, o, _next, _throw, "throw", n); } _next(void 0); }); }; }
function App_slicedToArray(r, e) { return App_arrayWithHoles(r) || App_iterableToArrayLimit(r, e) || App_unsupportedIterableToArray(r, e) || App_nonIterableRest(); }
function App_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function App_unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return App_arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? App_arrayLikeToArray(r, a) : void 0; } }
function App_arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function App_iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t.return && (u = t.return(), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function App_arrayWithHoles(r) { if (Array.isArray(r)) return r; }









var App = function App() {
  // Navigation state
  var _useState = (0,react.useState)('agent-list'),
    _useState2 = App_slicedToArray(_useState, 2),
    currentView = _useState2[0],
    setCurrentView = _useState2[1]; // 'agent-list' | 'agent-details' | 'topics-list' | 'topic-details' | 'llm-config'
  var _useState3 = (0,react.useState)(null),
    _useState4 = App_slicedToArray(_useState3, 2),
    selectedAgent = _useState4[0],
    setSelectedAgent = _useState4[1];
  var _useState5 = (0,react.useState)(null),
    _useState6 = App_slicedToArray(_useState5, 2),
    selectedAgentId = _useState6[0],
    setSelectedAgentId = _useState6[1];
  var _useState7 = (0,react.useState)(null),
    _useState8 = App_slicedToArray(_useState7, 2),
    selectedTopic = _useState8[0],
    setSelectedTopic = _useState8[1];

  // Core app state
  var _useState9 = (0,react.useState)(true),
    _useState0 = App_slicedToArray(_useState9, 2),
    loading = _useState0[0],
    setLoading = _useState0[1];
  var _useState1 = (0,react.useState)([]),
    _useState10 = App_slicedToArray(_useState1, 2),
    agents = _useState10[0],
    setAgents = _useState10[1];
  var _useState11 = (0,react.useState)({}),
    _useState12 = App_slicedToArray(_useState11, 2),
    systemStatus = _useState12[0],
    setSystemStatus = _useState12[1];
  var _useState13 = (0,react.useState)([]),
    _useState14 = App_slicedToArray(_useState13, 2),
    topics = _useState14[0],
    setTopics = _useState14[1];
  var _useState15 = (0,react.useState)('loading'),
    _useState16 = App_slicedToArray(_useState15, 2),
    healthStatus = _useState16[0],
    setHealthStatus = _useState16[1];

  // Navigation functions
  var showAgentList = function showAgentList() {
    setCurrentView('agent-list');
    setSelectedAgent(null);
    setSelectedAgentId(null);
  };
  var showAgentDetails = function showAgentDetails(agent) {
    setSelectedAgent(agent);
    setSelectedAgentId(agent.name);
    setSelectedTopic(null);
    setCurrentView('agent-details');
  };
  var showTopicsList = function showTopicsList() {
    setCurrentView('topics-list');
    setSelectedAgent(null);
    setSelectedAgentId(null);
    setSelectedTopic(null);
  };
  var showTopicDetails = function showTopicDetails(topic) {
    setSelectedTopic(topic);
    setSelectedAgent(null);
    setSelectedAgentId(null);
    setCurrentView('topic-details');
  };
  var showLLMConfig = function showLLMConfig() {
    setCurrentView('llm-config');
    setSelectedAgent(null);
    setSelectedAgentId(null);
    setSelectedTopic(null);
  };

  // Status helper methods
  var statusLevel = function statusLevel(status) {
    var normalized = (status || '').toString().toLowerCase();
    if (['healthy', 'deployed', 'active', 'running'].includes(normalized)) {
      return 'good';
    }
    if (['building', 'pending', 'deploying'].includes(normalized)) {
      return 'pending';
    }
    return 'bad';
  };
  var statusBadgeClass = function statusBadgeClass(status) {
    var level = statusLevel(status);
    if (level === 'good') return 'bg-emerald-500 text-white px-2 py-1 text-xs font-medium rounded-md';
    if (level === 'pending') return 'bg-amber-500 text-white px-2 py-1 text-xs font-medium rounded-md';
    return 'bg-red-500 text-white px-2 py-1 text-xs font-medium rounded-md';
  };

  // Computed properties
  var runningAgents = agents.filter(function (agent) {
    return statusLevel(agent.status) === 'good';
  }).length;
  var totalTopics = topics.length || 0;

  // API functions
  var checkHealth = /*#__PURE__*/function () {
    var _ref = App_asyncToGenerator(/*#__PURE__*/App_regenerator().m(function _callee() {
      var response, _t;
      return App_regenerator().w(function (_context) {
        while (1) switch (_context.p = _context.n) {
          case 0:
            _context.p = 0;
            _context.n = 1;
            return fetch('/health');
          case 1:
            response = _context.v;
            setHealthStatus(response.ok ? 'healthy' : 'error');
            _context.n = 3;
            break;
          case 2:
            _context.p = 2;
            _t = _context.v;
            console.error('Health check failed:', _t);
            setHealthStatus('error');
          case 3:
            return _context.a(2);
        }
      }, _callee, null, [[0, 2]]);
    }));
    return function checkHealth() {
      return _ref.apply(this, arguments);
    };
  }();
  var loadSystemStatus = /*#__PURE__*/function () {
    var _ref2 = App_asyncToGenerator(/*#__PURE__*/App_regenerator().m(function _callee2() {
      var response, _t2, _t3;
      return App_regenerator().w(function (_context2) {
        while (1) switch (_context2.p = _context2.n) {
          case 0:
            _context2.p = 0;
            _context2.n = 1;
            return fetch('/system/status');
          case 1:
            response = _context2.v;
            if (!response.ok) {
              _context2.n = 3;
              break;
            }
            _t2 = setSystemStatus;
            _context2.n = 2;
            return response.json();
          case 2:
            _t2(_context2.v);
          case 3:
            _context2.n = 5;
            break;
          case 4:
            _context2.p = 4;
            _t3 = _context2.v;
            console.error('Failed to load system status:', _t3);
          case 5:
            return _context2.a(2);
        }
      }, _callee2, null, [[0, 4]]);
    }));
    return function loadSystemStatus() {
      return _ref2.apply(this, arguments);
    };
  }();
  var loadAgents = /*#__PURE__*/function () {
    var _ref3 = App_asyncToGenerator(/*#__PURE__*/App_regenerator().m(function _callee3() {
      var response, data, _t4;
      return App_regenerator().w(function (_context3) {
        while (1) switch (_context3.p = _context3.n) {
          case 0:
            _context3.p = 0;
            _context3.n = 1;
            return fetch('/api/unstable/agents/list');
          case 1:
            response = _context3.v;
            if (!response.ok) {
              _context3.n = 3;
              break;
            }
            _context3.n = 2;
            return response.json();
          case 2:
            data = _context3.v;
            setAgents((data || []).map(function (agent) {
              return App_objectSpread(App_objectSpread({}, agent), {}, {
                status: agent !== null && agent !== void 0 && agent.status ? agent.status.toString().toLowerCase() : ''
              });
            }));
          case 3:
            _context3.n = 5;
            break;
          case 4:
            _context3.p = 4;
            _t4 = _context3.v;
            console.error('Failed to load agents:', _t4);
            setAgents([]);
          case 5:
            return _context3.a(2);
        }
      }, _callee3, null, [[0, 4]]);
    }));
    return function loadAgents() {
      return _ref3.apply(this, arguments);
    };
  }();
  var loadTopics = /*#__PURE__*/function () {
    var _ref4 = App_asyncToGenerator(/*#__PURE__*/App_regenerator().m(function _callee4() {
      var response, data, _t5;
      return App_regenerator().w(function (_context4) {
        while (1) switch (_context4.p = _context4.n) {
          case 0:
            _context4.p = 0;
            _context4.n = 1;
            return fetch('/ui/topics');
          case 1:
            response = _context4.v;
            if (!response.ok) {
              _context4.n = 3;
              break;
            }
            _context4.n = 2;
            return response.json();
          case 2:
            data = _context4.v;
            setTopics(data.topics || []);
            _context4.n = 4;
            break;
          case 3:
            setTopics([]);
          case 4:
            _context4.n = 6;
            break;
          case 5:
            _context4.p = 5;
            _t5 = _context4.v;
            console.error('Failed to load topics:', _t5);
            setTopics([]);
          case 6:
            return _context4.a(2);
        }
      }, _callee4, null, [[0, 5]]);
    }));
    return function loadTopics() {
      return _ref4.apply(this, arguments);
    };
  }();
  var refreshAgents = /*#__PURE__*/function () {
    var _ref5 = App_asyncToGenerator(/*#__PURE__*/App_regenerator().m(function _callee5() {
      return App_regenerator().w(function (_context5) {
        while (1) switch (_context5.n) {
          case 0:
            setLoading(true);
            _context5.n = 1;
            return loadAgents();
          case 1:
            setLoading(false);
          case 2:
            return _context5.a(2);
        }
      }, _callee5);
    }));
    return function refreshAgents() {
      return _ref5.apply(this, arguments);
    };
  }();

  // Initialization
  (0,react.useEffect)(function () {
    var initializeApp = /*#__PURE__*/function () {
      var _ref6 = App_asyncToGenerator(/*#__PURE__*/App_regenerator().m(function _callee6() {
        var interval;
        return App_regenerator().w(function (_context6) {
          while (1) switch (_context6.n) {
            case 0:
              _context6.n = 1;
              return checkHealth();
            case 1:
              _context6.n = 2;
              return loadSystemStatus();
            case 2:
              _context6.n = 3;
              return loadAgents();
            case 3:
              _context6.n = 4;
              return loadTopics();
            case 4:
              setLoading(false);

              // Set up refresh interval
              interval = setInterval(function () {
                checkHealth();
                if (Math.random() < 0.6) {
                  loadSystemStatus();
                  loadTopics();
                }
                if (currentView === 'agent-list' && Math.random() < 0.8) {
                  loadAgents();
                }
              }, 5000);
              return _context6.a(2, function () {
                return clearInterval(interval);
              });
          }
        }, _callee6);
      }));
      return function initializeApp() {
        return _ref6.apply(this, arguments);
      };
    }();
    initializeApp();
  }, [currentView]);

  // Application state object for passing to components
  var appState = {
    // Navigation
    currentView: currentView,
    selectedAgent: selectedAgent,
    selectedAgentId: selectedAgentId,
    selectedTopic: selectedTopic,
    showAgentList: showAgentList,
    showAgentDetails: showAgentDetails,
    showTopicsList: showTopicsList,
    showTopicDetails: showTopicDetails,
    showLLMConfig: showLLMConfig,
    // Core data
    loading: loading,
    setLoading: setLoading,
    agents: agents,
    setAgents: setAgents,
    systemStatus: systemStatus,
    topics: topics,
    healthStatus: healthStatus,
    // Computed values
    runningAgents: runningAgents,
    totalTopics: totalTopics,
    // Utility functions
    statusLevel: statusLevel,
    statusBadgeClass: statusBadgeClass,
    refreshAgents: refreshAgents,
    // API functions
    checkHealth: checkHealth,
    loadSystemStatus: loadSystemStatus,
    loadAgents: loadAgents,
    loadTopics: loadTopics
  };

  // Generate breadcrumbs based on current view
  var getBreadcrumbs = function getBreadcrumbs() {
    if (currentView === 'agent-list') {
      return [{
        label: 'Agent Registry'
      }];
    }
    if (currentView === 'agent-details' && selectedAgent) {
      return [{
        label: 'Agent Registry',
        onClick: showAgentList
      }, {
        label: selectedAgent.name
      }];
    }
    if (currentView === 'topics-list') {
      return [{
        label: 'Topics'
      }];
    }
    if (currentView === 'topic-details' && selectedTopic) {
      return [{
        label: 'Topics',
        onClick: showTopicsList
      }, {
        label: typeof selectedTopic === 'string' ? selectedTopic : selectedTopic.name
      }];
    }
    if (currentView === 'llm-config') {
      return [{
        label: 'LLM Keys'
      }];
    }
    return [];
  };
  return /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
    className: "h-screen flex relative app-background",
    children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LocalSidebar, {
      appState: appState
    }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
      className: "flex-1 flex flex-col overflow-hidden bg-white m-3 rounded-xl",
      children: [/*#__PURE__*/(0,jsx_runtime.jsx)(LocalHeader, {
        breadcrumbs: getBreadcrumbs()
      }), /*#__PURE__*/(0,jsx_runtime.jsxs)("div", {
        className: "flex-1 overflow-auto bg-white p-6 relative",
        children: [currentView === 'agent-list' && /*#__PURE__*/(0,jsx_runtime.jsx)(components_AgentListPage, {
          appState: appState
        }), currentView === 'agent-details' && /*#__PURE__*/(0,jsx_runtime.jsx)(components_AgentDetailsPage, {
          appState: appState
        }), currentView === 'topics-list' && /*#__PURE__*/(0,jsx_runtime.jsx)(components_TopicsPage, {
          appState: appState
        }), currentView === 'topic-details' && /*#__PURE__*/(0,jsx_runtime.jsx)(components_TopicDetailsPage, {
          appState: appState
        }), currentView === 'llm-config' && /*#__PURE__*/(0,jsx_runtime.jsx)(components_LLMConfigPage, {})]
      })]
    })]
  });
};
/* harmony default export */ const components_App = (App);
;// ./src/index.js
// Import our CSS


// Import React and ReactDOM



// Import our main App component


// Initialize React application
document.addEventListener('DOMContentLoaded', function () {
  console.log('Dispatch Local UI - Pure React Mode');

  // Mount the React app
  var rootElement = document.getElementById('root');
  if (rootElement) {
    var root = (0,client/* createRoot */.H)(rootElement);
    root.render(/*#__PURE__*/react.createElement(components_App));
  } else {
    console.error('Failed to find root element for React app');
  }
});
/******/ })()
;
//# sourceMappingURL=components.js.map