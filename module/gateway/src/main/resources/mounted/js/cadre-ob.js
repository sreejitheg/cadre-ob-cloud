(()=>{var Xa=globalThis,Ka=Xa.ShadowRoot&&(Xa.ShadyCSS===void 0||Xa.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,Ud=Symbol(),Yu=new WeakMap,Vn=class{constructor(t,o,r){if(this._$cssResult$=!0,r!==Ud)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=t,this.t=o}get styleSheet(){let t=this.o,o=this.t;if(Ka&&t===void 0){let r=o!==void 0&&o.length===1;r&&(t=Yu.get(o)),t===void 0&&((this.o=t=new CSSStyleSheet).replaceSync(this.cssText),r&&Yu.set(o,t))}return t}toString(){return this.cssText}},ne=e=>new Vn(typeof e=="string"?e:e+"",void 0,Ud),M=(e,...t)=>{let o=e.length===1?e[0]:t.reduce((r,i,s)=>r+(n=>{if(n._$cssResult$===!0)return n.cssText;if(typeof n=="number")return n;throw Error("Value passed to 'css' function must be a 'css' function result: "+n+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+e[s+1],e[0]);return new Vn(o,e,Ud)},qu=(e,t)=>{if(Ka)e.adoptedStyleSheets=t.map(o=>o instanceof CSSStyleSheet?o:o.styleSheet);else for(let o of t){let r=document.createElement("style"),i=Xa.litNonce;i!==void 0&&r.setAttribute("nonce",i),r.textContent=o.cssText,e.appendChild(r)}},Gd=Ka?e=>e:e=>e instanceof CSSStyleSheet?(t=>{let o="";for(let r of t.cssRules)o+=r.cssText;return ne(o)})(e):e;var{is:i5,defineProperty:s5,getOwnPropertyDescriptor:n5,getOwnPropertyNames:a5,getOwnPropertySymbols:l5,getPrototypeOf:c5}=Object,Qa=globalThis,Xu=Qa.trustedTypes,d5=Xu?Xu.emptyScript:"",h5=Qa.reactiveElementPolyfillSupport,Tn=(e,t)=>e,Dn={toAttribute(e,t){switch(t){case Boolean:e=e?d5:null;break;case Object:case Array:e=e==null?e:JSON.stringify(e)}return e},fromAttribute(e,t){let o=e;switch(t){case Boolean:o=e!==null;break;case Number:o=e===null?null:Number(e);break;case Object:case Array:try{o=JSON.parse(e)}catch{o=null}}return o}},Ja=(e,t)=>!i5(e,t),Ku={attribute:!0,type:String,converter:Dn,reflect:!1,useDefault:!1,hasChanged:Ja};Symbol.metadata??=Symbol("metadata"),Qa.litPropertyMetadata??=new WeakMap;var wr=class extends HTMLElement{static addInitializer(t){this._$Ei(),(this.l??=[]).push(t)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(t,o=Ku){if(o.state&&(o.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(t)&&((o=Object.create(o)).wrapped=!0),this.elementProperties.set(t,o),!o.noAccessor){let r=Symbol(),i=this.getPropertyDescriptor(t,r,o);i!==void 0&&s5(this.prototype,t,i)}}static getPropertyDescriptor(t,o,r){let{get:i,set:s}=n5(this.prototype,t)??{get(){return this[o]},set(n){this[o]=n}};return{get:i,set(n){let a=i?.call(this);s?.call(this,n),this.requestUpdate(t,a,r)},configurable:!0,enumerable:!0}}static getPropertyOptions(t){return this.elementProperties.get(t)??Ku}static _$Ei(){if(this.hasOwnProperty(Tn("elementProperties")))return;let t=c5(this);t.finalize(),t.l!==void 0&&(this.l=[...t.l]),this.elementProperties=new Map(t.elementProperties)}static finalize(){if(this.hasOwnProperty(Tn("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(Tn("properties"))){let o=this.properties,r=[...a5(o),...l5(o)];for(let i of r)this.createProperty(i,o[i])}let t=this[Symbol.metadata];if(t!==null){let o=litPropertyMetadata.get(t);if(o!==void 0)for(let[r,i]of o)this.elementProperties.set(r,i)}this._$Eh=new Map;for(let[o,r]of this.elementProperties){let i=this._$Eu(o,r);i!==void 0&&this._$Eh.set(i,o)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(t){let o=[];if(Array.isArray(t)){let r=new Set(t.flat(1/0).reverse());for(let i of r)o.unshift(Gd(i))}else t!==void 0&&o.push(Gd(t));return o}static _$Eu(t,o){let r=o.attribute;return r===!1?void 0:typeof r=="string"?r:typeof t=="string"?t.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(t=>this.enableUpdating=t),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(t=>t(this))}addController(t){(this._$EO??=new Set).add(t),this.renderRoot!==void 0&&this.isConnected&&t.hostConnected?.()}removeController(t){this._$EO?.delete(t)}_$E_(){let t=new Map,o=this.constructor.elementProperties;for(let r of o.keys())this.hasOwnProperty(r)&&(t.set(r,this[r]),delete this[r]);t.size>0&&(this._$Ep=t)}createRenderRoot(){let t=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return qu(t,this.constructor.elementStyles),t}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(t=>t.hostConnected?.())}enableUpdating(t){}disconnectedCallback(){this._$EO?.forEach(t=>t.hostDisconnected?.())}attributeChangedCallback(t,o,r){this._$AK(t,r)}_$ET(t,o){let r=this.constructor.elementProperties.get(t),i=this.constructor._$Eu(t,r);if(i!==void 0&&r.reflect===!0){let s=(r.converter?.toAttribute!==void 0?r.converter:Dn).toAttribute(o,r.type);this._$Em=t,s==null?this.removeAttribute(i):this.setAttribute(i,s),this._$Em=null}}_$AK(t,o){let r=this.constructor,i=r._$Eh.get(t);if(i!==void 0&&this._$Em!==i){let s=r.getPropertyOptions(i),n=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:Dn;this._$Em=i;let a=n.fromAttribute(o,s.type);this[i]=a??this._$Ej?.get(i)??a,this._$Em=null}}requestUpdate(t,o,r,i=!1,s){if(t!==void 0){let n=this.constructor;if(i===!1&&(s=this[t]),r??=n.getPropertyOptions(t),!((r.hasChanged??Ja)(s,o)||r.useDefault&&r.reflect&&s===this._$Ej?.get(t)&&!this.hasAttribute(n._$Eu(t,r))))return;this.C(t,o,r)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(t,o,{useDefault:r,reflect:i,wrapped:s},n){r&&!(this._$Ej??=new Map).has(t)&&(this._$Ej.set(t,n??o??this[t]),s!==!0||n!==void 0)||(this._$AL.has(t)||(this.hasUpdated||r||(o=void 0),this._$AL.set(t,o)),i===!0&&this._$Em!==t&&(this._$Eq??=new Set).add(t))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(o){Promise.reject(o)}let t=this.scheduleUpdate();return t!=null&&await t,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,s]of this._$Ep)this[i]=s;this._$Ep=void 0}let r=this.constructor.elementProperties;if(r.size>0)for(let[i,s]of r){let{wrapped:n}=s,a=this[i];n!==!0||this._$AL.has(i)||a===void 0||this.C(i,void 0,s,a)}}let t=!1,o=this._$AL;try{t=this.shouldUpdate(o),t?(this.willUpdate(o),this._$EO?.forEach(r=>r.hostUpdate?.()),this.update(o)):this._$EM()}catch(r){throw t=!1,this._$EM(),r}t&&this._$AE(o)}willUpdate(t){}_$AE(t){this._$EO?.forEach(o=>o.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(t)),this.updated(t)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(t){return!0}update(t){this._$Eq&&=this._$Eq.forEach(o=>this._$ET(o,this[o])),this._$EM()}updated(t){}firstUpdated(t){}};wr.elementStyles=[],wr.shadowRootOptions={mode:"open"},wr[Tn("elementProperties")]=new Map,wr[Tn("finalized")]=new Map,h5?.({ReactiveElement:wr}),(Qa.reactiveElementVersions??=[]).push("2.1.2");var qd=globalThis,Qu=e=>e,el=qd.trustedTypes,Ju=el?el.createPolicy("lit-html",{createHTML:e=>e}):void 0,Xd="$lit$",yr=`lit$${Math.random().toFixed(9).slice(2)}$`,Kd="?"+yr,p5=`<${Kd}>`,Ri=document,Rn=()=>Ri.createComment(""),zn=e=>e===null||typeof e!="object"&&typeof e!="function",Qd=Array.isArray,s2=e=>Qd(e)||typeof e?.[Symbol.iterator]=="function",Yd=`[ 	
\f\r]`,En=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,e2=/-->/g,t2=/>/g,Di=RegExp(`>|${Yd}(?:([^\\s"'>=/]+)(${Yd}*=${Yd}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),o2=/'/g,r2=/"/g,n2=/^(?:script|style|textarea|title)$/i,Jd=e=>(t,...o)=>({_$litType$:e,strings:t,values:o}),f=Jd(1),w=Jd(2),a2=Jd(3),Yo=Symbol.for("lit-noChange"),z=Symbol.for("lit-nothing"),i2=new WeakMap,Ei=Ri.createTreeWalker(Ri,129);function l2(e,t){if(!Qd(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ju!==void 0?Ju.createHTML(t):t}var c2=(e,t)=>{let o=e.length-1,r=[],i,s=t===2?"<svg>":t===3?"<math>":"",n=En;for(let a=0;a<o;a++){let l=e[a],c,d,p=-1,u=0;for(;u<l.length&&(n.lastIndex=u,d=n.exec(l),d!==null);)u=n.lastIndex,n===En?d[1]==="!--"?n=e2:d[1]!==void 0?n=t2:d[2]!==void 0?(n2.test(d[2])&&(i=RegExp("</"+d[2],"g")),n=Di):d[3]!==void 0&&(n=Di):n===Di?d[0]===">"?(n=i??En,p=-1):d[1]===void 0?p=-2:(p=n.lastIndex-d[2].length,c=d[1],n=d[3]===void 0?Di:d[3]==='"'?r2:o2):n===r2||n===o2?n=Di:n===e2||n===t2?n=En:(n=Di,i=void 0);let m=n===Di&&e[a+1].startsWith("/>")?" ":"";s+=n===En?l+p5:p>=0?(r.push(c),l.slice(0,p)+Xd+l.slice(p)+yr+m):l+yr+(p===-2?a:m)}return[l2(e,s+(e[o]||"<?>")+(t===2?"</svg>":t===3?"</math>":"")),r]},Hn=class e{constructor({strings:t,_$litType$:o},r){let i;this.parts=[];let s=0,n=0,a=t.length-1,l=this.parts,[c,d]=c2(t,o);if(this.el=e.createElement(c,r),Ei.currentNode=this.el.content,o===2||o===3){let p=this.el.content.firstChild;p.replaceWith(...p.childNodes)}for(;(i=Ei.nextNode())!==null&&l.length<a;){if(i.nodeType===1){if(i.hasAttributes())for(let p of i.getAttributeNames())if(p.endsWith(Xd)){let u=d[n++],m=i.getAttribute(p).split(yr),b=/([.?@])?(.*)/.exec(u);l.push({type:1,index:s,name:b[2],strings:m,ctor:b[1]==="."?ol:b[1]==="?"?rl:b[1]==="@"?il:Hi}),i.removeAttribute(p)}else p.startsWith(yr)&&(l.push({type:6,index:s}),i.removeAttribute(p));if(n2.test(i.tagName)){let p=i.textContent.split(yr),u=p.length-1;if(u>0){i.textContent=el?el.emptyScript:"";for(let m=0;m<u;m++)i.append(p[m],Rn()),Ei.nextNode(),l.push({type:2,index:++s});i.append(p[u],Rn())}}}else if(i.nodeType===8)if(i.data===Kd)l.push({type:2,index:s});else{let p=-1;for(;(p=i.data.indexOf(yr,p+1))!==-1;)l.push({type:7,index:s}),p+=yr.length-1}s++}}static createElement(t,o){let r=Ri.createElement("template");return r.innerHTML=t,r}};function zi(e,t,o=e,r){if(t===Yo)return t;let i=r!==void 0?o._$Co?.[r]:o._$Cl,s=zn(t)?void 0:t._$litDirective$;return i?.constructor!==s&&(i?._$AO?.(!1),s===void 0?i=void 0:(i=new s(e),i._$AT(e,o,r)),r!==void 0?(o._$Co??=[])[r]=i:o._$Cl=i),i!==void 0&&(t=zi(e,i._$AS(e,t.values),i,r)),t}var tl=class{constructor(t,o){this._$AV=[],this._$AN=void 0,this._$AD=t,this._$AM=o}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(t){let{el:{content:o},parts:r}=this._$AD,i=(t?.creationScope??Ri).importNode(o,!0);Ei.currentNode=i;let s=Ei.nextNode(),n=0,a=0,l=r[0];for(;l!==void 0;){if(n===l.index){let c;l.type===2?c=new Hs(s,s.nextSibling,this,t):l.type===1?c=new l.ctor(s,l.name,l.strings,this,t):l.type===6&&(c=new sl(s,this,t)),this._$AV.push(c),l=r[++a]}n!==l?.index&&(s=Ei.nextNode(),n++)}return Ei.currentNode=Ri,i}p(t){let o=0;for(let r of this._$AV)r!==void 0&&(r.strings!==void 0?(r._$AI(t,r,o),o+=r.strings.length-2):r._$AI(t[o])),o++}},Hs=class e{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(t,o,r,i){this.type=2,this._$AH=z,this._$AN=void 0,this._$AA=t,this._$AB=o,this._$AM=r,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let t=this._$AA.parentNode,o=this._$AM;return o!==void 0&&t?.nodeType===11&&(t=o.parentNode),t}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(t,o=this){t=zi(this,t,o),zn(t)?t===z||t==null||t===""?(this._$AH!==z&&this._$AR(),this._$AH=z):t!==this._$AH&&t!==Yo&&this._(t):t._$litType$!==void 0?this.$(t):t.nodeType!==void 0?this.T(t):s2(t)?this.k(t):this._(t)}O(t){return this._$AA.parentNode.insertBefore(t,this._$AB)}T(t){this._$AH!==t&&(this._$AR(),this._$AH=this.O(t))}_(t){this._$AH!==z&&zn(this._$AH)?this._$AA.nextSibling.data=t:this.T(Ri.createTextNode(t)),this._$AH=t}$(t){let{values:o,_$litType$:r}=t,i=typeof r=="number"?this._$AC(t):(r.el===void 0&&(r.el=Hn.createElement(l2(r.h,r.h[0]),this.options)),r);if(this._$AH?._$AD===i)this._$AH.p(o);else{let s=new tl(i,this),n=s.u(this.options);s.p(o),this.T(n),this._$AH=s}}_$AC(t){let o=i2.get(t.strings);return o===void 0&&i2.set(t.strings,o=new Hn(t)),o}k(t){Qd(this._$AH)||(this._$AH=[],this._$AR());let o=this._$AH,r,i=0;for(let s of t)i===o.length?o.push(r=new e(this.O(Rn()),this.O(Rn()),this,this.options)):r=o[i],r._$AI(s),i++;i<o.length&&(this._$AR(r&&r._$AB.nextSibling,i),o.length=i)}_$AR(t=this._$AA.nextSibling,o){for(this._$AP?.(!1,!0,o);t!==this._$AB;){let r=Qu(t).nextSibling;Qu(t).remove(),t=r}}setConnected(t){this._$AM===void 0&&(this._$Cv=t,this._$AP?.(t))}},Hi=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(t,o,r,i,s){this.type=1,this._$AH=z,this._$AN=void 0,this.element=t,this.name=o,this._$AM=i,this.options=s,r.length>2||r[0]!==""||r[1]!==""?(this._$AH=Array(r.length-1).fill(new String),this.strings=r):this._$AH=z}_$AI(t,o=this,r,i){let s=this.strings,n=!1;if(s===void 0)t=zi(this,t,o,0),n=!zn(t)||t!==this._$AH&&t!==Yo,n&&(this._$AH=t);else{let a=t,l,c;for(t=s[0],l=0;l<s.length-1;l++)c=zi(this,a[r+l],o,l),c===Yo&&(c=this._$AH[l]),n||=!zn(c)||c!==this._$AH[l],c===z?t=z:t!==z&&(t+=(c??"")+s[l+1]),this._$AH[l]=c}n&&!i&&this.j(t)}j(t){t===z?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,t??"")}},ol=class extends Hi{constructor(){super(...arguments),this.type=3}j(t){this.element[this.name]=t===z?void 0:t}},rl=class extends Hi{constructor(){super(...arguments),this.type=4}j(t){this.element.toggleAttribute(this.name,!!t&&t!==z)}},il=class extends Hi{constructor(t,o,r,i,s){super(t,o,r,i,s),this.type=5}_$AI(t,o=this){if((t=zi(this,t,o,0)??z)===Yo)return;let r=this._$AH,i=t===z&&r!==z||t.capture!==r.capture||t.once!==r.once||t.passive!==r.passive,s=t!==z&&(r===z||i);i&&this.element.removeEventListener(this.name,this,r),s&&this.element.addEventListener(this.name,this,t),this._$AH=t}handleEvent(t){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,t):this._$AH.handleEvent(t)}},sl=class{constructor(t,o,r){this.element=t,this.type=6,this._$AN=void 0,this._$AM=o,this.options=r}get _$AU(){return this._$AM._$AU}_$AI(t){zi(this,t)}},d2={M:Xd,P:yr,A:Kd,C:1,L:c2,R:tl,D:s2,V:zi,I:Hs,H:Hi,N:rl,U:il,B:ol,F:sl},u5=qd.litHtmlPolyfillSupport;u5?.(Hn,Hs),(qd.litHtmlVersions??=[]).push("3.3.3");var h2=(e,t,o)=>{let r=o?.renderBefore??t,i=r._$litPart$;if(i===void 0){let s=o?.renderBefore??null;r._$litPart$=i=new Hs(t.insertBefore(Rn(),s),s,void 0,o??{})}return i._$AI(e),i};var eh=globalThis,S=class extends wr{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let t=super.createRenderRoot();return this.renderOptions.renderBefore??=t.firstChild,t}update(t){let o=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(t),this._$Do=h2(o,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return Yo}};S._$litElement$=!0,S.finalized=!0,eh.litElementHydrateSupport?.({LitElement:S});var f5=eh.litElementPolyfillSupport;f5?.({LitElement:S});(eh.litElementVersions??=[]).push("4.2.2");var g5={attribute:!0,type:String,converter:Dn,reflect:!1,hasChanged:Ja},m5=(e=g5,t,o)=>{let{kind:r,metadata:i}=o,s=globalThis.litPropertyMetadata.get(i);if(s===void 0&&globalThis.litPropertyMetadata.set(i,s=new Map),r==="setter"&&((e=Object.create(e)).wrapped=!0),s.set(o.name,e),r==="accessor"){let{name:n}=o;return{set(a){let l=t.get.call(this);t.set.call(this,a),this.requestUpdate(n,l,e,!0,a)},init(a){return a!==void 0&&this.C(n,void 0,e,a),a}}}if(r==="setter"){let{name:n}=o;return function(a){let l=this[n];t.call(this,a),this.requestUpdate(n,l,e,!0,a)}}throw Error("Unsupported decorator location: "+r)};function h(e){return(t,o)=>typeof o=="object"?m5(e,t,o):((r,i,s)=>{let n=i.hasOwnProperty(s);return i.constructor.createProperty(s,r),n?Object.getOwnPropertyDescriptor(i,s):void 0})(e,t,o)}function ke(e){return h({...e,state:!0,attribute:!1})}var Kr=(e,t,o)=>(o.configurable=!0,o.enumerable=!0,Reflect.decorate&&typeof t!="object"&&Object.defineProperty(e,t,o),o);function at(e,t){return(o,r,i)=>{let s=n=>n.renderRoot?.querySelector(e)??null;if(t){let{get:n,set:a}=typeof r=="object"?o:i??(()=>{let l=Symbol();return{get(){return this[l]},set(c){this[l]=c}}})();return Kr(o,r,{get(){let l=n.call(this);return l===void 0&&(l=s(this),(l!==null||this.hasUpdated)&&a.call(this,l)),l}})}return Kr(o,r,{get(){return s(this)}})}}function Bi(e){return(t,o)=>{let{slot:r,selector:i}=e??{},s="slot"+(r?`[name=${r}]`:":not([name])");return Kr(t,o,{get(){let n=this.renderRoot?.querySelector(s),a=n?.assignedElements(e)??[];return i===void 0?a:a.filter(l=>l.matches(i))}})}}var L=e=>(t,o)=>{if(o!==void 0)o.addInitializer(()=>{customElements.get(e)||customElements.define(e,t)});else{if(customElements.get(e))return;customElements.define(e,t)}};var v5=Object.defineProperty,b5=Object.getOwnPropertyDescriptor,p2=(e,t,o,r)=>{for(var i=r>1?void 0:r?b5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&v5(t,o,i),i},nl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.8819 13C13.5388 13 14.8819 11.6569 14.8819 10C14.8819 8.34315 13.5388 7 11.8819 7C10.225 7 8.8819 8.34315 8.8819 10C8.8819 11.6569 10.225 13 11.8819 13ZM13.8819 10C13.8819 11.1046 12.9865 12 11.8819 12C10.7773 12 9.8819 11.1046 9.8819 10C9.8819 8.89543 10.7773 8 11.8819 8C12.9865 8 13.8819 8.89543 13.8819 10Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.8819 7C21.4342 7 21.8819 6.55229 21.8819 6V3C21.8819 2.44772 21.4342 2 20.8819 2H11.8819C7.46362 2 3.8819 5.58172 3.8819 10C3.8819 12.1897 4.76167 14.174 6.18702 15.6186L3.83151 18.563C3.0458 19.5451 3.74506 21 5.00282 21H18.7609C20.0187 21 20.718 19.5451 19.9322 18.563L17.5768 15.6186C19.0021 14.174 19.8819 12.1897 19.8819 10C19.8819 9.3094 19.7944 8.63924 19.6299 8C19.5416 7.65724 19.4313 7.32337 19.3004 7H20.8819ZM17.8168 6H20.8819V3H11.8819C8.0159 3 4.8819 6.13401 4.8819 10C4.8819 13.866 8.0159 17 11.8819 17C15.7479 17 18.8819 13.866 18.8819 10C18.8819 9.06987 18.701 8.18446 18.3734 7.37522L17.8168 6ZM4.61238 19.1877L6.93344 16.2863C8.29499 17.3596 10.0137 18 11.8819 18C13.7501 18 15.4688 17.3596 16.8303 16.2864L19.1514 19.1877C19.4133 19.515 19.1802 20 18.7609 20H5.00282C4.58356 20 4.35048 19.515 4.61238 19.1877Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M6.93156 16.2863L4.6105 19.1877C4.3486 19.515 4.58169 20 5.00094 20H18.7591C19.1783 20 19.4114 19.515 19.1495 19.1877L16.8285 16.2864C15.4669 17.3596 13.7483 18 11.88 18C10.0118 18 8.29311 17.3596 6.93156 16.2863Z" fill="currentColor"/>
<path d="M11.88 12C12.9846 12 13.88 11.1046 13.88 10C13.88 8.89543 12.9846 8 11.88 8C10.7755 8 9.88002 8.89543 9.88002 10C9.88002 11.1046 10.7755 12 11.88 12Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.88 6H17.8149L18.3716 7.37522C18.6991 8.18446 18.88 9.06987 18.88 10C18.88 13.866 15.746 17 11.88 17C8.01403 17 4.88002 13.866 4.88002 10C4.88002 6.13401 8.01403 3 11.88 3H20.88V6ZM11.88 13C13.5369 13 14.88 11.6569 14.88 10C14.88 8.34315 13.5369 7 11.88 7C10.2232 7 8.88002 8.34315 8.88002 10C8.88002 11.6569 10.2232 13 11.88 13Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.8819 13C13.5388 13 14.8819 11.6569 14.8819 10C14.8819 8.34315 13.5388 7 11.8819 7C10.225 7 8.8819 8.34315 8.8819 10C8.8819 11.6569 10.225 13 11.8819 13ZM13.8819 10C13.8819 11.1046 12.9865 12 11.8819 12C10.7773 12 9.8819 11.1046 9.8819 10C9.8819 8.89543 10.7773 8 11.8819 8C12.9865 8 13.8819 8.89543 13.8819 10Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.8819 7C21.4342 7 21.8819 6.55229 21.8819 6V3C21.8819 2.44772 21.4342 2 20.8819 2H11.8819C7.46362 2 3.8819 5.58172 3.8819 10C3.8819 12.1897 4.76167 14.174 6.18702 15.6186L3.83151 18.563C3.0458 19.5451 3.74506 21 5.00282 21H18.7609C20.0187 21 20.718 19.5451 19.9322 18.563L17.5768 15.6186C19.0021 14.174 19.8819 12.1897 19.8819 10C19.8819 9.3094 19.7944 8.63924 19.6299 8C19.5416 7.65724 19.4313 7.32337 19.3004 7H20.8819ZM17.8168 6H20.8819V3H11.8819C8.0159 3 4.8819 6.13401 4.8819 10C4.8819 13.866 8.0159 17 11.8819 17C15.7479 17 18.8819 13.866 18.8819 10C18.8819 9.06987 18.701 8.18446 18.3734 7.37522L17.8168 6ZM4.61238 19.1877L6.93344 16.2863C8.29499 17.3596 10.0137 18 11.8819 18C13.7501 18 15.4688 17.3596 16.8303 16.2864L19.1514 19.1877C19.4133 19.515 19.1802 20 18.7609 20H5.00282C4.58356 20 4.35048 19.515 4.61238 19.1877Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M6.93156 16.2863L4.6105 19.1877C4.3486 19.515 4.58169 20 5.00094 20H18.7591C19.1783 20 19.4114 19.515 19.1495 19.1877L16.8285 16.2864C15.4669 17.3596 13.7483 18 11.88 18C10.0118 18 8.29311 17.3596 6.93156 16.2863Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path d="M11.88 12C12.9846 12 13.88 11.1046 13.88 10C13.88 8.89543 12.9846 8 11.88 8C10.7755 8 9.88002 8.89543 9.88002 10C9.88002 11.1046 10.7755 12 11.88 12Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.88 6H17.8149L18.3716 7.37522C18.6991 8.18446 18.88 9.06987 18.88 10C18.88 13.866 15.746 17 11.88 17C8.01403 17 4.88002 13.866 4.88002 10C4.88002 6.13401 8.01403 3 11.88 3H20.88V6ZM11.88 13C13.5369 13 14.88 11.6569 14.88 10C14.88 8.34315 13.5369 7 11.88 7C10.2232 7 8.88002 8.34315 8.88002 10C8.88002 11.6569 10.2232 13 11.88 13Z" style="fill: var(--automation-device-primary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};nl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;p2([h({type:Boolean})],nl.prototype,"useCssColor",2);nl=p2([L("obi-pump-off-horizontal")],nl);var w5=Object.defineProperty,y5=Object.getOwnPropertyDescriptor,u2=(e,t,o,r)=>{for(var i=r>1?void 0:r?y5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&w5(t,o,i),i},al=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.8819 13C13.5388 13 14.8819 11.6569 14.8819 10C14.8819 8.34315 13.5388 7 11.8819 7C10.225 7 8.8819 8.34315 8.8819 10C8.8819 11.6569 10.225 13 11.8819 13ZM13.8819 10C13.8819 11.1046 12.9865 12 11.8819 12C10.7773 12 9.8819 11.1046 9.8819 10C9.8819 8.89543 10.7773 8 11.8819 8C12.9865 8 13.8819 8.89543 13.8819 10Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.8819 7C21.4342 7 21.8819 6.55229 21.8819 6V3C21.8819 2.44772 21.4342 2 20.8819 2H11.8819C7.46362 2 3.8819 5.58172 3.8819 10C3.8819 12.1897 4.76167 14.174 6.18702 15.6186L3.83151 18.563C3.0458 19.5451 3.74506 21 5.00282 21H18.7609C20.0187 21 20.718 19.5451 19.9322 18.563L17.5768 15.6186C19.0021 14.174 19.8819 12.1897 19.8819 10C19.8819 9.3094 19.7944 8.63924 19.6299 8C19.5416 7.65724 19.4313 7.32337 19.3004 7H20.8819ZM17.8168 6H20.8819V3H11.8819C8.0159 3 4.8819 6.13401 4.8819 10C4.8819 13.866 8.0159 17 11.8819 17C15.7479 17 18.8819 13.866 18.8819 10C18.8819 9.06987 18.701 8.18446 18.3734 7.37522L17.8168 6ZM4.61238 19.1877L6.93344 16.2863C8.29499 17.3596 10.0137 18 11.8819 18C13.7501 18 15.4688 17.3596 16.8303 16.2864L19.1514 19.1877C19.4133 19.515 19.1802 20 18.7609 20H5.00282C4.58356 20 4.35048 19.515 4.61238 19.1877Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M6.93156 16.2863L4.6105 19.1877C4.3486 19.515 4.58169 20 5.00094 20H18.7591C19.1783 20 19.4114 19.515 19.1495 19.1877L16.8285 16.2864C15.4669 17.3596 13.7483 18 11.88 18C10.0118 18 8.29311 17.3596 6.93156 16.2863Z" fill="currentColor"/>
<path d="M11.88 12C12.9846 12 13.88 11.1046 13.88 10C13.88 8.89543 12.9846 8 11.88 8C10.7755 8 9.88002 8.89543 9.88002 10C9.88002 11.1046 10.7755 12 11.88 12Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.88 6H17.8149L18.3716 7.37522C18.6991 8.18446 18.88 9.06987 18.88 10C18.88 13.866 15.746 17 11.88 17C8.01403 17 4.88002 13.866 4.88002 10C4.88002 6.13401 8.01403 3 11.88 3H20.88V6ZM11.88 13C13.5369 13 14.88 11.6569 14.88 10C14.88 8.34315 13.5369 7 11.88 7C10.2232 7 8.88002 8.34315 8.88002 10C8.88002 11.6569 10.2232 13 11.88 13Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.8819 13C13.5388 13 14.8819 11.6569 14.8819 10C14.8819 8.34315 13.5388 7 11.8819 7C10.225 7 8.8819 8.34315 8.8819 10C8.8819 11.6569 10.225 13 11.8819 13ZM13.8819 10C13.8819 11.1046 12.9865 12 11.8819 12C10.7773 12 9.8819 11.1046 9.8819 10C9.8819 8.89543 10.7773 8 11.8819 8C12.9865 8 13.8819 8.89543 13.8819 10Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.8819 7C21.4342 7 21.8819 6.55229 21.8819 6V3C21.8819 2.44772 21.4342 2 20.8819 2H11.8819C7.46362 2 3.8819 5.58172 3.8819 10C3.8819 12.1897 4.76167 14.174 6.18702 15.6186L3.83151 18.563C3.0458 19.5451 3.74506 21 5.00282 21H18.7609C20.0187 21 20.718 19.5451 19.9322 18.563L17.5768 15.6186C19.0021 14.174 19.8819 12.1897 19.8819 10C19.8819 9.3094 19.7944 8.63924 19.6299 8C19.5416 7.65724 19.4313 7.32337 19.3004 7H20.8819ZM17.8168 6H20.8819V3H11.8819C8.0159 3 4.8819 6.13401 4.8819 10C4.8819 13.866 8.0159 17 11.8819 17C15.7479 17 18.8819 13.866 18.8819 10C18.8819 9.06987 18.701 8.18446 18.3734 7.37522L17.8168 6ZM4.61238 19.1877L6.93344 16.2863C8.29499 17.3596 10.0137 18 11.8819 18C13.7501 18 15.4688 17.3596 16.8303 16.2864L19.1514 19.1877C19.4133 19.515 19.1802 20 18.7609 20H5.00282C4.58356 20 4.35048 19.515 4.61238 19.1877Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M6.93156 16.2863L4.6105 19.1877C4.3486 19.515 4.58169 20 5.00094 20H18.7591C19.1783 20 19.4114 19.515 19.1495 19.1877L16.8285 16.2864C15.4669 17.3596 13.7483 18 11.88 18C10.0118 18 8.29311 17.3596 6.93156 16.2863Z" style="fill: var(--automation-device-primary-color)"/>
<path d="M11.88 12C12.9846 12 13.88 11.1046 13.88 10C13.88 8.89543 12.9846 8 11.88 8C10.7755 8 9.88002 8.89543 9.88002 10C9.88002 11.1046 10.7755 12 11.88 12Z" style="fill: var(--automation-device-primary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.88 6H17.8149L18.3716 7.37522C18.6991 8.18446 18.88 9.06987 18.88 10C18.88 13.866 15.746 17 11.88 17C8.01403 17 4.88002 13.866 4.88002 10C4.88002 6.13401 8.01403 3 11.88 3H20.88V6ZM11.88 13C13.5369 13 14.88 11.6569 14.88 10C14.88 8.34315 13.5369 7 11.88 7C10.2232 7 8.88002 8.34315 8.88002 10C8.88002 11.6569 10.2232 13 11.88 13Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};al.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;u2([h({type:Boolean})],al.prototype,"useCssColor",2);al=u2([L("obi-pump-on-horizontal")],al);var C5=Object.defineProperty,x5=Object.getOwnPropertyDescriptor,f2=(e,t,o,r)=>{for(var i=r>1?void 0:r?x5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&C5(t,o,i),i},ll=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 14C13.6569 14 15 12.6569 15 11C15 9.34315 13.6569 8 12 8C10.3431 8 9 9.34315 9 11C9 12.6569 10.3431 14 12 14ZM14 11C14 12.1046 13.1046 13 12 13C10.8954 13 10 12.1046 10 11C10 9.89543 10.8954 9 12 9C13.1046 9 14 9.89543 14 11Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 2C9 1.44772 8.55228 1 8 1H5C4.44772 1 4 1.44772 4 2V11C4 13.1846 4.87566 15.1647 6.29514 16.6084L3.83151 19.688C3.0458 20.6701 3.74506 22.125 5.00282 22.125H18.7609C20.0187 22.125 20.718 20.6701 19.9322 19.688L17.5733 16.7392C19.07 15.2855 20 13.2514 20 11C20 6.58172 16.4183 3 12 3C11.3094 3 10.6392 3.08751 10 3.25203C9.65724 3.34026 9.32337 3.45062 9 3.58152V2ZM8 5.06513V2H5V11C5 14.866 8.13401 18 12 18C15.866 18 19 14.866 19 11C19 7.13401 15.866 4 12 4C11.0699 4 10.1845 4.18088 9.37522 4.50845L8 5.06513ZM4.61238 20.3127L7.04045 17.2776C8.40375 18.3561 10.1267 19 12 19C13.8071 19 15.4742 18.4009 16.8136 17.3904L19.1514 20.3127C19.4133 20.64 19.1802 21.125 18.7609 21.125H5.00282C4.58356 21.125 4.35048 20.64 4.61238 20.3127Z" fill="currentColor"/>
<path d="M11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14Z" fill="currentColor"/>
<path d="M7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14ZM11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 14C13.6569 14 15 12.6569 15 11C15 9.34315 13.6569 8 12 8C10.3431 8 9 9.34315 9 11C9 12.6569 10.3431 14 12 14ZM14 11C14 12.1046 13.1046 13 12 13C10.8954 13 10 12.1046 10 11C10 9.89543 10.8954 9 12 9C13.1046 9 14 9.89543 14 11Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 2C9 1.44772 8.55228 1 8 1H5C4.44772 1 4 1.44772 4 2V11C4 13.1846 4.87566 15.1647 6.29514 16.6084L3.83151 19.688C3.0458 20.6701 3.74506 22.125 5.00282 22.125H18.7609C20.0187 22.125 20.718 20.6701 19.9322 19.688L17.5733 16.7392C19.07 15.2855 20 13.2514 20 11C20 6.58172 16.4183 3 12 3C11.3094 3 10.6392 3.08751 10 3.25203C9.65724 3.34026 9.32337 3.45062 9 3.58152V2ZM8 5.06513V2H5V11C5 14.866 8.13401 18 12 18C15.866 18 19 14.866 19 11C19 7.13401 15.866 4 12 4C11.0699 4 10.1845 4.18088 9.37522 4.50845L8 5.06513ZM4.61238 20.3127L7.04045 17.2776C8.40375 18.3561 10.1267 19 12 19C13.8071 19 15.4742 18.4009 16.8136 17.3904L19.1514 20.3127C19.4133 20.64 19.1802 21.125 18.7609 21.125H5.00282C4.58356 21.125 4.35048 20.64 4.61238 20.3127Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path d="M11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path d="M7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14ZM11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" style="fill: var(--automation-device-primary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ll.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;f2([h({type:Boolean})],ll.prototype,"useCssColor",2);ll=f2([L("obi-pump-off-vertical")],ll);var _5=Object.defineProperty,k5=Object.getOwnPropertyDescriptor,g2=(e,t,o,r)=>{for(var i=r>1?void 0:r?k5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&_5(t,o,i),i},cl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 14C13.6569 14 15 12.6569 15 11C15 9.34315 13.6569 8 12 8C10.3431 8 9 9.34315 9 11C9 12.6569 10.3431 14 12 14ZM14 11C14 12.1046 13.1046 13 12 13C10.8954 13 10 12.1046 10 11C10 9.89543 10.8954 9 12 9C13.1046 9 14 9.89543 14 11Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 2C9 1.44772 8.55228 1 8 1H5C4.44772 1 4 1.44772 4 2V11C4 13.1846 4.87566 15.1647 6.29514 16.6084L3.83151 19.688C3.0458 20.6701 3.74506 22.125 5.00282 22.125H18.7609C20.0187 22.125 20.718 20.6701 19.9322 19.688L17.5733 16.7392C19.07 15.2855 20 13.2514 20 11C20 6.58172 16.4183 3 12 3C11.3094 3 10.6392 3.08751 10 3.25203C9.65724 3.34026 9.32337 3.45062 9 3.58152V2ZM8 5.06513V2H5V11C5 14.866 8.13401 18 12 18C15.866 18 19 14.866 19 11C19 7.13401 15.866 4 12 4C11.0699 4 10.1845 4.18088 9.37522 4.50845L8 5.06513ZM4.61238 20.3127L7.04045 17.2776C8.40375 18.3561 10.1267 19 12 19C13.8071 19 15.4742 18.4009 16.8136 17.3904L19.1514 20.3127C19.4133 20.64 19.1802 21.125 18.7609 21.125H5.00282C4.58356 21.125 4.35048 20.64 4.61238 20.3127Z" fill="currentColor"/>
<path d="M11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14Z" fill="currentColor"/>
<path d="M7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14ZM11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 14C13.6569 14 15 12.6569 15 11C15 9.34315 13.6569 8 12 8C10.3431 8 9 9.34315 9 11C9 12.6569 10.3431 14 12 14ZM14 11C14 12.1046 13.1046 13 12 13C10.8954 13 10 12.1046 10 11C10 9.89543 10.8954 9 12 9C13.1046 9 14 9.89543 14 11Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 2C9 1.44772 8.55228 1 8 1H5C4.44772 1 4 1.44772 4 2V11C4 13.1846 4.87566 15.1647 6.29514 16.6084L3.83151 19.688C3.0458 20.6701 3.74506 22.125 5.00282 22.125H18.7609C20.0187 22.125 20.718 20.6701 19.9322 19.688L17.5733 16.7392C19.07 15.2855 20 13.2514 20 11C20 6.58172 16.4183 3 12 3C11.3094 3 10.6392 3.08751 10 3.25203C9.65724 3.34026 9.32337 3.45062 9 3.58152V2ZM8 5.06513V2H5V11C5 14.866 8.13401 18 12 18C15.866 18 19 14.866 19 11C19 7.13401 15.866 4 12 4C11.0699 4 10.1845 4.18088 9.37522 4.50845L8 5.06513ZM4.61238 20.3127L7.04045 17.2776C8.40375 18.3561 10.1267 19 12 19C13.8071 19 15.4742 18.4009 16.8136 17.3904L19.1514 20.3127C19.4133 20.64 19.1802 21.125 18.7609 21.125H5.00282C4.58356 21.125 4.35048 20.64 4.61238 20.3127Z" style="fill: var(--automation-device-tertiary-color)"/>
<path d="M11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" style="fill: var(--automation-device-primary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14Z" style="fill: var(--automation-device-primary-color)"/>
<path d="M7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776Z" style="fill: var(--automation-device-primary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M7.99812 2V5.06513L9.37334 4.50845C10.1826 4.18088 11.068 4 11.9981 4C15.8641 4 18.9981 7.13401 18.9981 11C18.9981 14.866 15.8641 18 11.9981 18C8.13213 18 4.99812 14.866 4.99812 11V2H7.99812ZM7.03857 17.2776L4.6105 20.3127C4.3486 20.64 4.58169 21.125 5.00094 21.125H18.7591C19.1783 21.125 19.4114 20.64 19.1495 20.3127L16.8117 17.3904C15.4723 18.4009 13.8052 19 11.9981 19C10.1248 19 8.40187 18.3561 7.03857 17.2776ZM11.9981 14C13.655 14 14.9981 12.6569 14.9981 11C14.9981 9.34315 13.655 8 11.9981 8C10.3413 8 8.99812 9.34315 8.99812 11C8.99812 12.6569 10.3413 14 11.9981 14ZM11.9981 13C13.1027 13 13.9981 12.1046 13.9981 11C13.9981 9.89543 13.1027 9 11.9981 9C10.8936 9 9.99812 9.89543 9.99812 11C9.99812 12.1046 10.8936 13 11.9981 13Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};cl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;g2([h({type:Boolean})],cl.prototype,"useCssColor",2);cl=g2([L("obi-pump-on-vertical")],cl);var m2=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

.point-wrapper {
  width: 0;
  height: 0;
}

.button-wrapper {
  width: fit-content;
  height: fit-content;
}

.positioning-point.label-bottom {
    top: calc(var(--automation-components-button-touch-target-size) / -2);
    transform: translateX(-50%);
  }

.positioning-point.label-right {
    left: calc(var(--automation-components-button-touch-target-size) / -2);
    transform: translateY(-50%);
  }

.positioning-point.label-top {
    bottom: calc(var(--automation-components-button-touch-target-size) / -2);
    transform: translateX(-50%);
  }

.positioning-point.label-left {
    right: calc(var(--automation-components-button-touch-target-size) / -2);
    transform: translateY(-50%);
  }

.symbol-wrapper {
  position: relative;
  width: var(--automation-components-button-touch-target-size);
  height: var(--automation-components-button-touch-target-size);
  display: flex;
  align-items: flex-start;
  justify-content: center;
}

.symbol-wrapper.label-bottom {
    align-items: flex-start;
  }

.symbol-wrapper.label-top {
    align-items: flex-end;
  }

.symbol-wrapper.label-right {
    align-items: center;
    justify-content: flex-start;
  }

.symbol-wrapper.label-left {
    align-items: center;
    justify-content: flex-end;
  }

.wrapper {
  padding: var(--automation-components-button-new-state-container-padding);
}

.wrapper.positioning-point {
    position: absolute;
  }

.wrapper .badge-spacer {
    width: 0;
    height: 0;
    transition: all 0.1s ease-in-out;
  }

.wrapper.has-badge-spacer .badge-spacer {
    width: var(--automation-components-button-new-spacer-size);
    height: var(--automation-components-button-new-spacer-size);
  }

.wrapper {

  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  width: fit-content;

  appearance: none;
  padding: 0;
  margin: 0;
  border-radius: 6px;
}

.wrapper {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.wrapper:focus {
  outline: none;
}

.wrapper.activated {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.wrapper:hover {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper:active {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.wrapper:focus-visible {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper:disabled {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.disabled {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper {
  border-width: 0;
}

.wrapper.label-top {
    flex-direction: column-reverse;
  }

.wrapper.label-bottom {
    flex-direction: column;
  }

.wrapper.label-left {
    flex-direction: row-reverse;
  }

.wrapper .progress-ring {
    position: absolute;
    top: -1px;
    left: -1px;
    width: calc(100% + 2px);
    height: calc(100% + 2px);
  }

.badge-top-right,
.badge-top-left,
.badge-bottom-right,
.badge-bottom-left {
  position: absolute;
  z-index: 1;
}

.icon-touch-target {
  position: relative;
  display: flex;
  width: var(--automation-components-button-touch-target-size);
  height: var(--automation-components-button-touch-target-size);
  justify-content: center;
  align-items: center;
}

.icon-holder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;

  border-radius: 100%;
  border-width: 1px;
  border-style: solid;
  width: var(--automation-components-button-new-visual-target-round);
  height: var(--automation-components-button-new-visual-target-round);
}

.icon-holder .icon-primary {
    width: var(--automation-components-button-icon-size);
    height: var(--automation-components-button-icon-size);
  }

:is(.variant-double .icon-holder) .icon-direction {
      width: var(--automation-components-button-icon-double-primary-size);
      height: var(--automation-components-button-icon-double-primary-size);
    }

:is(.variant-double .icon-holder) .icon-primary {
      width: var(--automation-components-button-icon-double-secondary-size);
      height: var(--automation-components-button-icon-double-secondary-size);
    }

.variant-square .icon-holder {
    border-radius: var(--automation-components-button-new-border-radius);
    width: var(--automation-components-button-new-visual-target);
    height: var(--automation-components-button-new-visual-target);
  }

.variant-flat .icon-holder,.variant-flat-forward .icon-holder {
    background-color: transparent !important;
    border-color: transparent !important;
  }

:is(.variant-flat .icon-holder,.variant-flat-forward .icon-holder) .icon-primary {
      width: var(--automation-components-button-icon-size-flat);
      height: var(--automation-components-button-icon-size-flat);
    }

.icon-holder .icon-silhouette {
    stroke: var(--border-silhouette-color);
    stroke-width: 2;
    position: absolute;
    width: var(--automation-components-button-icon-size-flat);
    height: var(--automation-components-button-icon-size-flat);
    z-index: -1;
  }

.icon-holder.orientation-verticalRight .icon-primary,.icon-holder.orientation-verticalRight .icon-silhouette {
      transform: rotate(90deg);
    }

.icon-holder.orientation-verticalLeft .icon-primary,.icon-holder.orientation-verticalLeft .icon-silhouette {
      transform: rotate(-90deg);
    }

.badge-top-right {
  top: 0;
  right: 0;
}

.badge-top-left {
  top: 0;
  left: 0;
}

.badge-bottom-right {
  bottom: 0;
  right: 0;
}

.badge-bottom-left {
  bottom: 0;
  left: 0;
}

.progress .icon-holder {
  border-color: transparent !important;
  background: var(--automation-pipe-primary-color) !important;
}

:is(.progress .icon-holder) .icon-primary {
    width: var(--automation-components-button-icon-size);
    height: var(--automation-components-button-icon-size);
  }

.state-closed .icon-holder {
  border-color: var(--automation-button-off-border-color);
  background: var(--automation-button-off-background-color);
}

.state-open .icon-holder {
  border-color: var(--on-border-color);
  background: var(--on-background-color);
}

.static .icon-holder {
  border-color: var(--automation-button-static-border-color);
  background: var(--automation-button-static-background-color);
}

.alert-frame {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  bottom: 0;
}
`;var Bs={ATTRIBUTE:1,CHILD:2,PROPERTY:3,BOOLEAN_ATTRIBUTE:4,EVENT:5,ELEMENT:6},Ii=e=>(...t)=>({_$litDirective$:e,values:t}),Qr=class{constructor(t){}get _$AU(){return this._$AM._$AU}_$AT(t,o,r){this._$Ct=t,this._$AM=o,this._$Ci=r}_$AS(t,o){return this.update(t,o)}update(t,o){return this.render(...o)}};var de=Ii(class extends Qr{constructor(e){if(super(e),e.type!==Bs.ATTRIBUTE||e.name!=="class"||e.strings?.length>2)throw Error("`classMap()` can only be used in the `class` attribute and must be the only part in the attribute.")}render(e){return" "+Object.keys(e).filter(t=>e[t]).join(" ")+" "}update(e,[t]){if(this.st===void 0){this.st=new Set,e.strings!==void 0&&(this.nt=new Set(e.strings.join(" ").split(/\s/).filter(r=>r!=="")));for(let r in t)t[r]&&!this.nt?.has(r)&&this.st.add(r);return this.render(t)}let o=e.element.classList;for(let r of this.st)r in t||(o.remove(r),this.st.delete(r));for(let r in t){let i=!!t[r];i===this.st.has(r)||this.nt?.has(r)||(i?(o.add(r),this.st.add(r)):(o.remove(r),this.st.delete(r)))}return Yo}});var L5=Object.defineProperty,S5=Object.getOwnPropertyDescriptor,v2=(e,t,o,r)=>{for(var i=r>1?void 0:r?S5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&L5(t,o,i),i},dl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5.74904 3.56754C5.90319 3.47808 6.09332 3.47745 6.24807 3.56588L20.2481 11.5659C20.4039 11.6549 20.5 11.8206 20.5 12C20.5 12.1794 20.4039 12.3451 20.2481 12.4341L6.24807 20.4341C6.09332 20.5226 5.90319 20.5219 5.74904 20.4325C5.59488 20.343 5.5 20.1782 5.5 20V4C5.5 3.82176 5.59488 3.65701 5.74904 3.56754ZM6.5 4.86159V19.1384L18.9922 12L6.5 4.86159Z" fill="currentColor"/>
<path d="M6.5 4.86157V19.1384L18.9922 12L6.5 4.86157Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5.74904 3.56754C5.90319 3.47808 6.09332 3.47745 6.24807 3.56588L20.2481 11.5659C20.4039 11.6549 20.5 11.8206 20.5 12C20.5 12.1794 20.4039 12.3451 20.2481 12.4341L6.24807 20.4341C6.09332 20.5226 5.90319 20.5219 5.74904 20.4325C5.59488 20.343 5.5 20.1782 5.5 20V4C5.5 3.82176 5.59488 3.65701 5.74904 3.56754ZM6.5 4.86159V19.1384L18.9922 12L6.5 4.86159Z" style="fill: var(--automation-device-tertiary-color)"/>
<path d="M6.5 4.86157V19.1384L18.9922 12L6.5 4.86157Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};dl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;v2([h({type:Boolean})],dl.prototype,"useCssColor",2);dl=v2([L("obi-forward")],dl);var M5=Object.defineProperty,$5=Object.getOwnPropertyDescriptor,b2=(e,t,o,r)=>{for(var i=r>1?void 0:r?$5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&M5(t,o,i),i},hl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M3.28673 4.59039C3.134 4.48347 2.93446 4.47041 2.76909 4.55651C2.60373 4.64261 2.5 4.81356 2.5 5V19C2.5 19.1864 2.60373 19.3574 2.76909 19.4435C2.93446 19.5296 3.134 19.5165 3.28673 19.4096L12.5 12.9603V19C12.5 19.1864 12.6037 19.3574 12.7691 19.4435C12.9345 19.5296 13.134 19.5165 13.2867 19.4096L23.2867 12.4096C23.4204 12.3161 23.5 12.1632 23.5 12C23.5 11.8368 23.4204 11.6839 23.2867 11.5904L13.2867 4.59039C13.134 4.48347 12.9345 4.47041 12.7691 4.55651C12.6037 4.64261 12.5 4.81356 12.5 5V11.0397L3.28673 4.59039ZM13.5 18.0397L22.1281 12L13.5 5.96033V18.0397ZM12.1281 12L3.5 18.0397V5.96033L12.1281 12Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M13.5 18.0397L22.1281 12L13.5 5.96033V18.0397ZM12.1281 12L3.5 18.0397V5.96033L12.1281 12Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M3.28673 4.59039C3.134 4.48347 2.93446 4.47041 2.76909 4.55651C2.60373 4.64261 2.5 4.81356 2.5 5V19C2.5 19.1864 2.60373 19.3574 2.76909 19.4435C2.93446 19.5296 3.134 19.5165 3.28673 19.4096L12.5 12.9603V19C12.5 19.1864 12.6037 19.3574 12.7691 19.4435C12.9345 19.5296 13.134 19.5165 13.2867 19.4096L23.2867 12.4096C23.4204 12.3161 23.5 12.1632 23.5 12C23.5 11.8368 23.4204 11.6839 23.2867 11.5904L13.2867 4.59039C13.134 4.48347 12.9345 4.47041 12.7691 4.55651C12.6037 4.64261 12.5 4.81356 12.5 5V11.0397L3.28673 4.59039ZM13.5 18.0397L22.1281 12L13.5 5.96033V18.0397ZM12.1281 12L3.5 18.0397V5.96033L12.1281 12Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M13.5 18.0397L22.1281 12L13.5 5.96033V18.0397ZM12.1281 12L3.5 18.0397V5.96033L12.1281 12Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};hl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;b2([h({type:Boolean})],hl.prototype,"useCssColor",2);hl=b2([L("obi-forward-fast")],hl);var A5=Object.defineProperty,P5=Object.getOwnPropertyDescriptor,w2=(e,t,o,r)=>{for(var i=r>1?void 0:r?P5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&A5(t,o,i),i},pl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5.74904 3.56754C5.90319 3.47808 6.09332 3.47745 6.24807 3.56588L20.2481 11.5659C20.4039 11.6549 20.5 11.8206 20.5 12C20.5 12.1794 20.4039 12.3451 20.2481 12.4341L6.24807 20.4341C6.09332 20.5226 5.90319 20.5219 5.74904 20.4325C5.59488 20.343 5.5 20.1782 5.5 20V4C5.5 3.82176 5.59488 3.65701 5.74904 3.56754ZM6.5 4.86159V19.1384L18.9922 12L6.5 4.86159Z" fill="currentColor"/>
<path d="M6.5 4.86157V19.1384L18.9922 12L6.5 4.86157Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5.74904 3.56754C5.90319 3.47808 6.09332 3.47745 6.24807 3.56588L20.2481 11.5659C20.4039 11.6549 20.5 11.8206 20.5 12C20.5 12.1794 20.4039 12.3451 20.2481 12.4341L6.24807 20.4341C6.09332 20.5226 5.90319 20.5219 5.74904 20.4325C5.59488 20.343 5.5 20.1782 5.5 20V4C5.5 3.82176 5.59488 3.65701 5.74904 3.56754ZM6.5 4.86159V19.1384L18.9922 12L6.5 4.86159Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path d="M6.5 4.86157V19.1384L18.9922 12L6.5 4.86157Z" style="fill: var(--automation-device-primary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};pl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;w2([h({type:Boolean})],pl.prototype,"useCssColor",2);pl=w2([L("obi-forward-stopped")],pl);var O5=Object.defineProperty,V5=Object.getOwnPropertyDescriptor,y2=(e,t,o,r)=>{for(var i=r>1?void 0:r?V5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&O5(t,o,i),i},ul=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.251 20.4325C18.0968 20.5219 17.9067 20.5226 17.7519 20.4341L3.75193 12.4341C3.59614 12.3451 3.5 12.1794 3.5 12C3.5 11.8206 3.59614 11.6549 3.75193 11.5659L17.7519 3.56588C17.9067 3.47745 18.0968 3.47808 18.251 3.56754C18.4051 3.657 18.5 3.82176 18.5 4L18.5 20C18.5 20.1782 18.4051 20.343 18.251 20.4325ZM17.5 19.1384L17.5 4.86159L5.00778 12L17.5 19.1384Z" fill="currentColor"/>
<path d="M17.5 19.1386L17.5 4.86182L5.00781 12.0002L17.5 19.1386Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.251 20.4325C18.0968 20.5219 17.9067 20.5226 17.7519 20.4341L3.75193 12.4341C3.59614 12.3451 3.5 12.1794 3.5 12C3.5 11.8206 3.59614 11.6549 3.75193 11.5659L17.7519 3.56588C17.9067 3.47745 18.0968 3.47808 18.251 3.56754C18.4051 3.657 18.5 3.82176 18.5 4L18.5 20C18.5 20.1782 18.4051 20.343 18.251 20.4325ZM17.5 19.1384L17.5 4.86159L5.00778 12L17.5 19.1384Z" style="fill: var(--automation-device-tertiary-color)"/>
<path d="M17.5 19.1386L17.5 4.86182L5.00781 12.0002L17.5 19.1386Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ul.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;y2([h({type:Boolean})],ul.prototype,"useCssColor",2);ul=y2([L("obi-backward")],ul);var T5=Object.defineProperty,D5=Object.getOwnPropertyDescriptor,C2=(e,t,o,r)=>{for(var i=r>1?void 0:r?D5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&T5(t,o,i),i},fl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.7133 19.4096C20.866 19.5165 21.0655 19.5296 21.2309 19.4435C21.3963 19.3574 21.5 19.1864 21.5 19V5C21.5 4.81356 21.3963 4.64261 21.2309 4.55651C21.0655 4.47041 20.866 4.48347 20.7133 4.59039L11.5 11.0397L11.5 5C11.5 4.81356 11.3963 4.64261 11.2309 4.55651C11.0655 4.47041 10.866 4.48347 10.7133 4.59039L0.713268 11.5904C0.579605 11.684 0.5 11.8368 0.5 12C0.5 12.1632 0.579605 12.3161 0.713268 12.4096L10.7133 19.4096C10.866 19.5165 11.0655 19.5296 11.2309 19.4435C11.3963 19.3574 11.5 19.1864 11.5 19L11.5 12.9603L20.7133 19.4096ZM10.5 5.96033L1.8719 12L10.5 18.0397L10.5 5.96033ZM11.8719 12L20.5 5.96033V18.0397L11.8719 12Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.4999 5.96069L1.87183 12.0004L10.4999 18.04L10.4999 5.96069ZM11.8718 12.0004L20.4999 5.96069V18.04L11.8718 12.0004Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.7133 19.4096C20.866 19.5165 21.0655 19.5296 21.2309 19.4435C21.3963 19.3574 21.5 19.1864 21.5 19V5C21.5 4.81356 21.3963 4.64261 21.2309 4.55651C21.0655 4.47041 20.866 4.48347 20.7133 4.59039L11.5 11.0397L11.5 5C11.5 4.81356 11.3963 4.64261 11.2309 4.55651C11.0655 4.47041 10.866 4.48347 10.7133 4.59039L0.713268 11.5904C0.579605 11.684 0.5 11.8368 0.5 12C0.5 12.1632 0.579605 12.3161 0.713268 12.4096L10.7133 19.4096C10.866 19.5165 11.0655 19.5296 11.2309 19.4435C11.3963 19.3574 11.5 19.1864 11.5 19L11.5 12.9603L20.7133 19.4096ZM10.5 5.96033L1.8719 12L10.5 18.0397L10.5 5.96033ZM11.8719 12L20.5 5.96033V18.0397L11.8719 12Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.4999 5.96069L1.87183 12.0004L10.4999 18.04L10.4999 5.96069ZM11.8718 12.0004L20.4999 5.96069V18.04L11.8718 12.0004Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};fl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;C2([h({type:Boolean})],fl.prototype,"useCssColor",2);fl=C2([L("obi-backward-fast")],fl);var E5=Object.defineProperty,R5=Object.getOwnPropertyDescriptor,x2=(e,t,o,r)=>{for(var i=r>1?void 0:r?R5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&E5(t,o,i),i},gl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.251 20.4325C18.0968 20.5219 17.9067 20.5226 17.7519 20.4341L3.75193 12.4341C3.59614 12.3451 3.5 12.1794 3.5 12C3.5 11.8206 3.59614 11.6549 3.75193 11.5659L17.7519 3.56588C17.9067 3.47745 18.0968 3.47808 18.251 3.56754C18.4051 3.657 18.5 3.82176 18.5 4L18.5 20C18.5 20.1782 18.4051 20.343 18.251 20.4325ZM17.5 19.1384L17.5 4.86159L5.00778 12L17.5 19.1384Z" fill="currentColor"/>
<path d="M17.5 19.1386L17.5 4.86182L5.00781 12.0002L17.5 19.1386Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.251 20.4325C18.0968 20.5219 17.9067 20.5226 17.7519 20.4341L3.75193 12.4341C3.59614 12.3451 3.5 12.1794 3.5 12C3.5 11.8206 3.59614 11.6549 3.75193 11.5659L17.7519 3.56588C17.9067 3.47745 18.0968 3.47808 18.251 3.56754C18.4051 3.657 18.5 3.82176 18.5 4L18.5 20C18.5 20.1782 18.4051 20.343 18.251 20.4325ZM17.5 19.1384L17.5 4.86159L5.00778 12L17.5 19.1384Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path d="M17.5 19.1386L17.5 4.86182L5.00781 12.0002L17.5 19.1386Z" style="fill: var(--automation-device-primary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};gl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;x2([h({type:Boolean})],gl.prototype,"useCssColor",2);gl=x2([L("obi-backward-stopped")],gl);var z5=Object.defineProperty,H5=Object.getOwnPropertyDescriptor,_2=(e,t,o,r)=>{for(var i=r>1?void 0:r?H5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&z5(t,o,i),i},ml=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M10 19H6V5H10V19Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 19H14V5H18V19Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M10 19H6V5H10V19Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 19H14V5H18V19Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ml.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;_2([h({type:Boolean})],ml.prototype,"useCssColor",2);ml=_2([L("obi-standby")],ml);var B5=Object.defineProperty,I5=Object.getOwnPropertyDescriptor,k2=(e,t,o,r)=>{for(var i=r>1?void 0:r?I5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&B5(t,o,i),i},vl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M13 20L13 7.83L18.59 13.42L20 12L12 4L4 12L5.41 13.41L11 7.83L11 20L13 20Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M13 20L13 7.83L18.59 13.42L20 12L12 4L4 12L5.41 13.41L11 7.83L11 20L13 20Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};vl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;k2([h({type:Boolean})],vl.prototype,"useCssColor",2);vl=k2([L("obi-arrow-up-google")],vl);var Z5=Object.defineProperty,F5=Object.getOwnPropertyDescriptor,L2=(e,t,o,r)=>{for(var i=r>1?void 0:r?F5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Z5(t,o,i),i},bl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11 4L11 16.17L5.41 10.58L4 12L12 20L20 12L18.59 10.59L13 16.17L13 4L11 4Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11 4L11 16.17L5.41 10.58L4 12L12 20L20 12L18.59 10.59L13 16.17L13 4L11 4Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};bl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;L2([h({type:Boolean})],bl.prototype,"useCssColor",2);bl=L2([L("obi-arrow-down-google")],bl);var N5=Object.defineProperty,j5=Object.getOwnPropertyDescriptor,S2=(e,t,o,r)=>{for(var i=r>1?void 0:r?j5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&N5(t,o,i),i},wl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M7.83 11H20V13H7.83L13.41 18.59L12 20L4 12L12 4L13.42 5.41L7.83 11Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M7.83 11H20V13H7.83L13.41 18.59L12 20L4 12L12 4L13.42 5.41L7.83 11Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};wl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;S2([h({type:Boolean})],wl.prototype,"useCssColor",2);wl=S2([L("obi-arrow-left-google")],wl);var W5=Object.defineProperty,U5=Object.getOwnPropertyDescriptor,M2=(e,t,o,r)=>{for(var i=r>1?void 0:r?U5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&W5(t,o,i),i},yl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M12 4L10.59 5.41L16.17 11H4V13H16.17L10.59 18.59L12 20L20 12L12 4Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 4L10.59 5.41L16.17 11H4V13H16.17L10.59 18.59L12 20L20 12L12 4Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};yl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;M2([h({type:Boolean})],yl.prototype,"useCssColor",2);yl=M2([L("obi-arrow-right-google")],yl);var $2=M`* {
  -webkit-tap-highlight-color: transparent;
}

:host {
  position: absolute;
  inset: 0;
}

:host([wrapcontent]) {
  position: unset;
  width: fit-content;
  height: fit-content;
}

:host([fullwidth]) {
  display: block;
  width: 100%;
}

.wrapper {
  --bg-color: var(--alert-alarm-color);
  --thickness: var(--global-size-spacing-border-weight-alertframe);
  /* 0/1 from the flash-<tempo> classes below; steady when no class applies. */
  --blink-on: 0;
  --blink-off: 1;
  color: var(--on-alarm-active-color);
  position: relative;
  width: 100%;
  height: 100%;
  /* The stroke's centreline follows this radius, like a Figma centre stroke. */
  border-radius: var(--ui-components-button-border-radius);
  outline: var(--thickness) solid var(--bg-color);
  /* Centre stroke: frames on touching components share one edge. */
  outline-offset: calc(-1 * var(--thickness) / 2);
  /* +2 px while on, 1 px each side, both thicknesses (Figma Flash=yes: 2 → 4 px). */
  --blink-width: 2px;
}

.wrapper.thickness-small {
    --thickness: 2px;
  }

.wrapper.wrap-content {
    width: fit-content;
    height: fit-content;
  }

.wrapper.full-width {
    width: 100%;
  }

.wrapper.flash-fast {
    --blink-on: var(--flash-fast-on);
    --blink-off: var(--flash-fast-off);
  }

.wrapper.flash-slow {
    --blink-on: var(--flash-slow-on);
    --blink-off: var(--flash-slow-off);
  }

.wrapper.flash-very-slow {
    --blink-on: var(--flash-very-slow-on);
    --blink-off: var(--flash-very-slow-off);
  }

.wrapper {

  --flash-transition: 50ms linear;
}

.wrapper.flash-effect-outline-eased {
    transition:
      outline-width var(--flash-transition),
      outline-offset var(--flash-transition);
  }

.wrapper.flash-effect-outline-eased .flap {
      transition: box-shadow var(--flash-transition);
    }

.wrapper.flash-effect-outline-eased .mask {
      transition:
        top var(--flash-transition),
        bottom var(--flash-transition),
        left var(--flash-transition),
        right var(--flash-transition);
    }

.wrapper.flash-effect-outline-eased .dash path {
      transition: stroke-width var(--flash-transition);
    }

.wrapper {

  --blink-width-dynamic: calc(var(--blink-width) * var(--blink-on));
  /* One knob for flap and masks, so they cannot drift apart from the outline. */
  --flap-grow: 0px;
}

.wrapper.unacked-active,.wrapper.unacked-rectified {
    outline-width: calc(var(--thickness) + var(--blink-width-dynamic));
    outline-offset: calc(
      -1 * (var(--thickness) + var(--blink-width-dynamic)) / 2
    );
    /* The stroke grows on both sides, so its outer edge moves by half. */
    --flap-grow: calc(var(--blink-width-dynamic) / 2);
  }

.wrapper.unacked-rectified {
    /* The dash pattern (12/6) needs an SVG stroke; outlines have no dash array. */
    outline-style: none;
  }

.wrapper.alarm,.wrapper.level-high {
    --bg-color: var(--alert-alarm-color);
    color: var(--on-alarm-active-color);
  }

.wrapper.warning,.wrapper.level-medium {
    --bg-color: var(--alert-warning-color);
    color: var(--on-warning-active-color);
  }

.wrapper.caution,.wrapper.level-low {
    --bg-color: var(--alert-caution-color);
    color: var(--on-caution-active-color);
  }

.wrapper.level-critical {
    --bg-color: var(--critical-enabled-background-color);
    color: var(--on-critical-active-color);
  }

.wrapper.level-diagnostic {
    --bg-color: var(--notification-enabled-background-color);
    color: var(--on-notification-active-color);
  }

.wrapper.sharp-edge-top-left {
    border-top-left-radius: 0;
  }

.wrapper.sharp-edge-top-right {
    border-top-right-radius: 0;
  }

.wrapper.sharp-edge-bottom-left {
    border-bottom-left-radius: 0;
  }

.wrapper.sharp-edge-bottom-right {
    border-bottom-right-radius: 0;
  }

.flap {
  position: absolute;
  background-color: var(--bg-color);
  border-radius: 0px var(--app-components-alert-frame-small-flip-border-radius)
    var(--app-components-alert-frame-small-flip-border-radius) 0px;
  padding: var(--ui-components-badge-padding);

  display: flex;
  gap: 2px;
}

.flap.small {
    top: calc(-1 * var(--thickness) / 2);
    right: calc(
      -1 * var(--app-components-alert-frame-icon-size) -
        var(--ui-components-badge-padding) * 2
    );
  }

.flap .mask {
    position: absolute;
    width: var(--ui-components-button-border-radius);
    height: var(--ui-components-button-border-radius);
    background-color: var(--bg-color);
  }

.up:is(.flap .mask) {
      width: calc(
        var(--ui-components-button-border-radius) + var(--thickness) + 0.5px
      );
      top: calc(-1 * var(--flap-grow));
      left: calc(
        -1 * var(--ui-components-button-border-radius) - var(--thickness)
      );
      clip-path: polygon(
        0 0,
        100% 0,
        100% 100%,
        calc(100% - var(--thickness)) 50%,
        50% var(--thickness)
      );
    }

.down:is(.flap .mask) {
      width: calc(
        var(--ui-components-button-border-radius) + var(--thickness) + 0.5px
      );
      bottom: calc(-1 * var(--flap-grow));
      left: calc(
        -1 * var(--ui-components-button-border-radius) - var(--thickness)
      );
      clip-path: polygon(
        0 100%,
        100% 100%,
        100% 0,
        50% calc(100% - var(--thickness)),
        calc(100% - var(--thickness)) 50%
      );
    }

.left:is(.flap .mask) {
      height: calc(
        var(--ui-components-button-border-radius) + var(--thickness) + 0.5px
      );
      top: calc(
        -1 * var(--ui-components-button-border-radius) - var(--thickness)
      );
      left: calc(-1 * var(--flap-grow));
      clip-path: polygon(
        0 0,
        0 100%,
        100% 100%,
        50% calc(100% - var(--thickness)),
        var(--thickness) 50%
      );
    }

.top .left:is(.flap .mask) {
        top: unset;
        bottom: calc(
          -1 * var(--ui-components-button-border-radius) - var(--thickness)
        );
        clip-path: polygon(
          0 100%,
          0 0,
          100% 0,
          50% var(--thickness),
          var(--thickness) 50%
        );
      }

.right:is(.flap .mask) {
      height: calc(
        var(--ui-components-button-border-radius) + var(--thickness) + 0.5px
      );
      top: calc(
        -1 * var(--ui-components-button-border-radius) - var(--thickness)
      );
      right: calc(-1 * var(--flap-grow));
      clip-path: polygon(
        100% 0,
        100% 100%,
        0 100%,
        50% calc(100% - var(--thickness)),
        calc(100% - var(--thickness)) 50%
      );
    }

.top .right:is(.flap .mask) {
        top: unset;
        bottom: calc(
          -1 * var(--ui-components-button-border-radius) - var(--thickness)
        );
        clip-path: polygon(
          100% 100%,
          100% 0,
          0 0,
          50% var(--thickness),
          calc(100% - var(--thickness)) 50%
        );
      }

.flap.large {
    flex-direction: column;
    top: calc(-1 * var(--thickness) / 2);
    bottom: calc(-1 * var(--thickness) / 2);
    right: calc(
      -1 * var(--app-components-alert-frame-icon-size) + var(--thickness) -
        var(--ui-components-badge-padding) * 2
    );
    border-radius: 0px
      var(--app-components-alert-frame-large-flip-border-radius)
      var(--app-components-alert-frame-large-flip-border-radius) 0px;
  }

.flap.bottom,.flap.top {
    left: calc(-1 * var(--thickness) / 2);
    right: calc(-1 * var(--thickness) / 2);
    padding: var(--app-components-alert-frame-large-flip-padding-vertical)
      var(--app-components-alert-frame-large-flip-4px-padding-horizontal);
    bottom: calc(
      -1 * var(--global-typography-ui-label-line-height) -
        var(--app-components-alert-frame-large-flip-padding-vertical) * 2
    );
    border-radius: 0px 0px var(--button-border-radius-bottom-right)
      var(--button-border-radius-bottom-right);
    align-items: center;

    font-family: var(--global-typography-font-family);

    font-weight: var(--global-typography-ui-label-font-weight);

    font-size: var(--global-typography-ui-label-font-size);

    line-height: var(--global-typography-ui-label-line-height);

    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    font-weight: var(--font-weight-regular);
  }

:is(.flap.bottom,.flap.top) .spacer {
      flex: 1;
    }

.text-size-large :is(.flap.bottom,.flap.top) {
      font-family: var(--global-typography-font-family);
      font-weight: var(--global-typography-ui-body-font-weight);
      font-size: var(--global-typography-ui-body-font-size);
      line-height: var(--global-typography-ui-body-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      bottom: calc(
        var(--thickness) - var(--global-typography-ui-body-line-height) -
          var(--app-components-alert-frame-large-flip-padding-vertical) * 2
      );
    }

:is(.text-size-large :is(.flap.bottom,.flap.top)) .label {
        font-family: var(--global-typography-font-family);
        font-weight: var(--global-typography-ui-body-active-font-weight);
        font-size: var(--global-typography-ui-body-active-font-size);
        line-height: var(--global-typography-ui-body-active-line-height);
        font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      }

.flap.top {
    bottom: unset !important;
    top: calc(
      -1 * var(--global-typography-ui-label-line-height) -
        var(--app-components-alert-frame-large-flip-padding-vertical) * 2
    );
    border-radius: var(--button-border-radius-bottom-right)
      var(--button-border-radius-bottom-right) 0px 0px;
  }

.text-size-large .flap.top {
      top: calc(
        var(--thickness) - var(--global-typography-ui-body-line-height) -
          var(--app-components-alert-frame-large-flip-padding-vertical) * 2
      );
    }

.flap .label {
    flex-shrink: 1000;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

/* Grows the flap outward with the outline, never toward the content: shifted
   copies leave the inner edge where it is (an outline would cross it). */

.flap.small,
.flap.large {
  box-shadow:
    var(--flap-grow) 0 0 0 var(--bg-color),
    0 calc(-1 * var(--flap-grow)) 0 0 var(--bg-color),
    0 var(--flap-grow) 0 0 var(--bg-color),
    var(--flap-grow) calc(-1 * var(--flap-grow)) 0 0 var(--bg-color),
    var(--flap-grow) var(--flap-grow) 0 0 var(--bg-color);
}

.flap.bottom {
  box-shadow:
    0 var(--flap-grow) 0 0 var(--bg-color),
    calc(-1 * var(--flap-grow)) 0 0 0 var(--bg-color),
    var(--flap-grow) 0 0 0 var(--bg-color),
    calc(-1 * var(--flap-grow)) var(--flap-grow) 0 0 var(--bg-color),
    var(--flap-grow) var(--flap-grow) 0 0 var(--bg-color);
}

.flap.top {
  box-shadow:
    0 calc(-1 * var(--flap-grow)) 0 0 var(--bg-color),
    calc(-1 * var(--flap-grow)) 0 0 0 var(--bg-color),
    var(--flap-grow) 0 0 0 var(--bg-color),
    calc(-1 * var(--flap-grow)) calc(-1 * var(--flap-grow)) 0 0 var(--bg-color),
    var(--flap-grow) calc(-1 * var(--flap-grow)) 0 0 var(--bg-color);
}

::slotted([slot="label"]) {
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.icon {
  width: var(--app-components-alert-frame-icon-size);
  height: var(--app-components-alert-frame-icon-size);
  display: block;
  flex-shrink: 0;
}

.dash {
  /* Overridden inline per render from the measured thickness. */
  --dash-pad: 0px;
  position: absolute;
  top: calc(-1 * var(--dash-pad));
  left: calc(-1 * var(--dash-pad));
  overflow: visible;
  pointer-events: none;
  fill: none;
  stroke: var(--bg-color);
  stroke-dasharray: 12 6;
}

.dash path {
  /* Animated on the one path: a wider second path would drift its dashes. */
  stroke-width: calc(var(--thickness) + var(--blink-width-dynamic));
}
`;var G5=Object.defineProperty,Y5=Object.getOwnPropertyDescriptor,A2=(e,t,o,r)=>{for(var i=r>1?void 0:r?Y5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&G5(t,o,i),i},Cl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M10.5977 3.45245L2.11783 18.6539C1.68126 19.4365 1.46298 19.8278 1.5 20.1481C1.5323 20.4276 1.68084 20.6806 1.90919 20.8449C2.17092 21.0333 2.61899 21.0333 3.51513 21.0333H20.4697C21.3656 21.0333 21.8136 21.0333 22.0753 20.845C22.3036 20.6806 22.4522 20.4277 22.4845 20.1483C22.5216 19.828 22.3034 19.4367 21.8672 18.6542L13.3925 3.45281C12.9361 2.63423 12.7079 2.22495 12.4074 2.08895C12.1454 1.97039 11.8451 1.97035 11.5831 2.08884C11.2825 2.22476 11.0542 2.63399 10.5977 3.45245Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M10.5977 3.45245L2.11783 18.6539C1.68126 19.4365 1.46298 19.8278 1.5 20.1481C1.5323 20.4276 1.68084 20.6806 1.90919 20.8449C2.17092 21.0333 2.61899 21.0333 3.51513 21.0333H20.4697C21.3656 21.0333 21.8136 21.0333 22.0753 20.845C22.3036 20.6806 22.4522 20.4277 22.4845 20.1483C22.5216 19.828 22.3034 19.4367 21.8672 18.6542L13.3925 3.45281C12.9361 2.63423 12.7079 2.22495 12.4074 2.08895C12.1454 1.97039 11.8451 1.97035 11.5831 2.08884C11.2825 2.22476 11.0542 2.63399 10.5977 3.45245Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Cl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;A2([h({type:Boolean})],Cl.prototype,"useCssColor",2);Cl=A2([L("obi-alarm-badge")],Cl);var q5=Object.defineProperty,X5=Object.getOwnPropertyDescriptor,P2=(e,t,o,r)=>{for(var i=r>1?void 0:r?X5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&q5(t,o,i),i},xl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<circle cx="12" cy="12" r="10" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<circle cx="12" cy="12" r="10" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};xl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;P2([h({type:Boolean})],xl.prototype,"useCssColor",2);xl=P2([L("obi-warning-badge")],xl);var K5=Object.defineProperty,Q5=Object.getOwnPropertyDescriptor,O2=(e,t,o,r)=>{for(var i=r>1?void 0:r?Q5(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&K5(t,o,i),i},_l=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M3 4.6C3 4.03995 3 3.75992 3.10899 3.54601C3.20487 3.35785 3.35785 3.20487 3.54601 3.10899C3.75992 3 4.03995 3 4.6 3H19.4C19.9601 3 20.2401 3 20.454 3.10899C20.6422 3.20487 20.7951 3.35785 20.891 3.54601C21 3.75992 21 4.03995 21 4.6V19.4C21 19.9601 21 20.2401 20.891 20.454C20.7951 20.6422 20.6422 20.7951 20.454 20.891C20.2401 21 19.9601 21 19.4 21H4.6C4.03995 21 3.75992 21 3.54601 20.891C3.35785 20.7951 3.20487 20.6422 3.10899 20.454C3 20.2401 3 19.9601 3 19.4V4.6Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3 4.6C3 4.03995 3 3.75992 3.10899 3.54601C3.20487 3.35785 3.35785 3.20487 3.54601 3.10899C3.75992 3 4.03995 3 4.6 3H19.4C19.9601 3 20.2401 3 20.454 3.10899C20.6422 3.20487 20.7951 3.35785 20.891 3.54601C21 3.75992 21 4.03995 21 4.6V19.4C21 19.9601 21 20.2401 20.891 20.454C20.7951 20.6422 20.6422 20.7951 20.454 20.891C20.2401 21 19.9601 21 19.4 21H4.6C4.03995 21 3.75992 21 3.54601 20.891C3.35785 20.7951 3.20487 20.6422 3.10899 20.454C3 20.2401 3 19.9601 3 19.4V4.6Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};_l.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;O2([h({type:Boolean})],_l.prototype,"useCssColor",2);_l=O2([L("obi-caution-badge")],_l);var J5=Object.defineProperty,e9=Object.getOwnPropertyDescriptor,V2=(e,t,o,r)=>{for(var i=r>1?void 0:r?e9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&J5(t,o,i),i},kl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M2.47717 12.8113C2.30349 12.516 2.21665 12.3684 2.18269 12.2111C2.15265 12.072 2.15265 11.9281 2.18269 11.7889C2.21665 11.6317 2.30349 11.484 2.47717 11.1888L6.536 4.28877C6.7051 4.00128 6.78966 3.85754 6.90703 3.75306C7.01089 3.66061 7.13288 3.59084 7.26522 3.54819C7.41479 3.5 7.58155 3.5 7.91509 3.5L16.0849 3.5C16.4184 3.5 16.5852 3.5 16.7347 3.54819C16.8671 3.59084 16.9891 3.66061 17.0929 3.75306C17.2103 3.85754 17.2948 4.00128 17.464 4.28877L21.5228 11.1888C21.6965 11.484 21.7833 11.6317 21.8173 11.7889C21.8473 11.9281 21.8473 12.072 21.8173 12.2111C21.7833 12.3684 21.6965 12.516 21.5228 12.8113L17.464 19.7112C17.2948 19.9987 17.2103 20.1425 17.0929 20.2469C16.9891 20.3394 16.8671 20.4092 16.7347 20.4518C16.5852 20.5 16.4184 20.5 16.0849 20.5H7.91509C7.58155 20.5 7.41479 20.5 7.26522 20.4518C7.13288 20.4092 7.01089 20.3394 6.90703 20.2469C6.78966 20.1425 6.7051 19.9987 6.53599 19.7112L2.47717 12.8113Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M2.47717 12.8113C2.30349 12.516 2.21665 12.3684 2.18269 12.2111C2.15265 12.072 2.15265 11.9281 2.18269 11.7889C2.21665 11.6317 2.30349 11.484 2.47717 11.1888L6.536 4.28877C6.7051 4.00128 6.78966 3.85754 6.90703 3.75306C7.01089 3.66061 7.13288 3.59084 7.26522 3.54819C7.41479 3.5 7.58155 3.5 7.91509 3.5L16.0849 3.5C16.4184 3.5 16.5852 3.5 16.7347 3.54819C16.8671 3.59084 16.9891 3.66061 17.0929 3.75306C17.2103 3.85754 17.2948 4.00128 17.464 4.28877L21.5228 11.1888C21.6965 11.484 21.7833 11.6317 21.8173 11.7889C21.8473 11.9281 21.8473 12.072 21.8173 12.2111C21.7833 12.3684 21.6965 12.516 21.5228 12.8113L17.464 19.7112C17.2948 19.9987 17.2103 20.1425 17.0929 20.2469C16.9891 20.3394 16.8671 20.4092 16.7347 20.4518C16.5852 20.5 16.4184 20.5 16.0849 20.5H7.91509C7.58155 20.5 7.41479 20.5 7.26522 20.4518C7.13288 20.4092 7.01089 20.3394 6.90703 20.2469C6.78966 20.1425 6.7051 19.9987 6.53599 19.7112L2.47717 12.8113Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};kl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;V2([h({type:Boolean})],kl.prototype,"useCssColor",2);kl=V2([L("obi-critical-badge")],kl);var t9=Object.getOwnPropertyDescriptor,o9=(e,t,o,r)=>{for(var i=r>1?void 0:r?t9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=n(i)||i);return i},th=class extends S{constructor(){super(...arguments),this.icon=w`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="100" height="100">
  <path d="M 10.5,2 
           L 13.5,2 
           L 13.5,9.4 
           L 19.91,5.7 
           L 21.41,8.3 
           L 15,12 
           L 21.41,15.7 
           L 19.91,18.3 
           L 13.5,14.6 
           L 13.5,22 
           L 10.5,22 
           L 10.5,14.6 
           L 4.09,18.3 
           L 2.59,15.7 
           L 9,12 
           L 2.59,8.3 
           L 4.09,5.7 
           L 10.5,9.4 
           Z" 
        fill="currentColor" />
</svg>

`}render(){return f` <div class="wrapper">${this.icon}</div> `}};th.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;th=o9([L("obi-diagnostic-badge")],th);var Q=(e=>(e.Alarm="alarm",e.Warning="warning",e.Caution="caution",e.LevelCritical="level-critical",e.LevelHigh="level-high",e.LevelMedium="level-medium",e.LevelLow="level-low",e.LevelDiagnostic="level-diagnostic",e))(Q||{}),Ie=(e=>(e.Default="default",e.Fast="fast",e.Slow="slow",e.VerySlow="very-slow",e.Fixed="fixed",e))(Ie||{}),Ll=["level-critical","alarm","level-high","warning","level-medium","caution","level-low","level-diagnostic"];function Cr(e){return e.active===!0}function Jr(e){return e.acknowledged!==!1&&e.acknowledged!==void 0}function Sl(e){return e.shelved!==!1&&e.shelved!==void 0}function T2(e){return e.blocked!==!1&&e.blocked!==void 0}function oh(e,t){return e.type!==t.type?Ll.indexOf(t.type)-Ll.indexOf(e.type):Cr(e)!==Cr(t)?Cr(e)?1:-1:Jr(e)!==Jr(t)?Jr(e)?-1:1:e.time.getTime()-t.time.getTime()}var D2=e=>typeof e!="string"&&"strTag"in e,rh=(e,t,o)=>{let r=e[0];for(let i=1;i<e.length;i++)r+=t[o?o[i-1]:i-1],r+=e[i];return r};var Ml=(e=>D2(e)?rh(e.strings,e.values):e);var Ge=Ml;var $l=class{constructor(){this.settled=!1,this.promise=new Promise((t,o)=>{this._resolve=t,this._reject=o})}resolve(t){this.settled=!0,this._resolve(t)}reject(t){this.settled=!0,this._reject(t)}};var i9=[];for(let e=0;e<256;e++)i9[e]=(e>>4&15).toString(16)+(e&15).toString(16);var n9=new $l;n9.resolve();var Is=(e=>(e.Alarm="obi-alarm-badge",e.Warning="obi-warning-badge",e.Caution="obi-caution-badge",e.Critical="obi-critical-badge",e.Diagnostic="obi-diagnostic-badge",e))(Is||{});function E2(e){return[Q.Alarm,Q.Warning,Q.LevelCritical,Q.LevelHigh,Q.LevelMedium,Q.LevelLow].includes(e)}var Zi=(e=>(e.Active="active",e.Rectified="rectified",e))(Zi||{});function Bn(e,t,o="active"){if(e!==Ie.Default)return e;if(t===Q.Caution||t===Q.LevelDiagnostic)return Ie.Fixed;if(o==="rectified")return Ie.VerySlow;switch(t){case Q.LevelCritical:case Q.Alarm:case Q.LevelHigh:return Ie.Fast;case Q.Warning:case Q.LevelMedium:return Ie.Slow;case Q.LevelLow:return Ie.VerySlow;default:return Ie.Fixed}}function R2(e){switch(e){case Q.LevelCritical:return"obi-critical-badge";case Q.Warning:case Q.LevelMedium:return"obi-warning-badge";case Q.Caution:case Q.LevelLow:return"obi-caution-badge";case Q.LevelDiagnostic:return"obi-diagnostic-badge";case Q.Alarm:case Q.LevelHigh:default:return"obi-alarm-badge"}}function z2(e){switch(e){case Q.LevelCritical:case Q.LevelHigh:return Q.Alarm;case Q.LevelMedium:return Q.Warning;case Q.LevelLow:return Q.Caution;default:return e}}function ih(e){return[Q.Caution,Q.LevelDiagnostic].includes(e)}function H2(e){return[Q.Alarm,Q.LevelCritical,Q.LevelHigh].includes(e)}var a9={[Q.Alarm]:"countAlarm",[Q.Warning]:"countWarning",[Q.Caution]:"countCaution",[Q.LevelCritical]:"countLevelCritical",[Q.LevelHigh]:"countLevelHigh",[Q.LevelMedium]:"countLevelMedium",[Q.LevelLow]:"countLevelLow",[Q.LevelDiagnostic]:"countLevelDiagnostic"};function B2(e,t=!1){let o=Ll.map(i=>({type:i,count:e[a9[i]]??0})).filter(i=>i.count>0);if(!t||o.length===0)return o;let r=o.reduce((i,s)=>i+s.count,0);return[{type:o[0].type,count:r}]}var S$={[Q.Alarm]:()=>Ge("Alarm"),[Q.Warning]:()=>Ge("Warning"),[Q.Caution]:()=>Ge("Caution"),[Q.LevelCritical]:()=>Ge("Critical"),[Q.LevelHigh]:()=>Ge("High"),[Q.LevelMedium]:()=>Ge("Medium"),[Q.LevelLow]:()=>Ge("Low"),[Q.LevelDiagnostic]:()=>Ge("Diagnostic")};var Z2={[Ie.Fast]:400,[Ie.Slow]:400,[Ie.VerySlow]:400},l9={[Ie.Fast]:400,[Ie.Slow]:1200,[Ie.VerySlow]:2800},A$=[Ie.Fast,Ie.Slow,Ie.VerySlow];function c9(e){return Z2[e]+l9[e]}function I2(e,t){return`--flash-${e}-${t}`}function F2(e,t){let o=I2(t,"on"),r=I2(t,"off"),i=c9(t),s=[{[o]:1,[r]:0,easing:"step-end"},{[o]:0,[r]:1,offset:Z2[t]/i,easing:"step-end"},{[o]:0,[r]:1}],n=e.animate(s,{duration:i,iterations:1/0});return n.startTime=0,()=>n.cancel()}var Zs=class{constructor(t,o){this.host=t,this.resolve=o,t.addController(this)}get tempo(){return this.installed}hostConnected(){this.host.hasUpdated&&this.sync()}hostUpdated(){this.sync()}hostDisconnected(){this.stop()}sync(){let t=this.host.isConnected?this.resolve():Ie.Fixed;if(t===Ie.Fixed){this.stop();return}t!==this.installed&&(this.stop(),this.cancel=F2(this.host,t),this.installed=t)}stop(){this.cancel?.(),this.cancel=void 0,this.installed=void 0}};function N2({x:e,y:t,width:o,height:r,radii:i}){let s=Math.min(o,r)/2,[n,a,l,c]=i.map(m=>Math.max(0,Math.min(m,s))),d=e+o,p=t+r,u=(m,b,C)=>m>0?`A${m} ${m} 0 0 1 ${b} ${C}`:"";return[`M${e+n} ${t}`,`H${d-a}`,u(a,d,t+a),`V${p-l}`,u(l,d-l,p),`H${e+c}`,u(c,e,p-c),`V${t+n}`,u(n,e+n,t),"Z"].filter(Boolean).join(" ")}var d9=Object.defineProperty,h9=Object.getOwnPropertyDescriptor,Rt=(e,t,o,r)=>{for(var i=r>1?void 0:r?h9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&d9(t,o,i),i},xr=(e=>(e.Regular="regular",e.SmallSideFlip="small-side-flip",e.LargeSideFlip="large-side-flip",e.BottomFlip="bottom-flip",e.TopFlip="top-flip",e))(xr||{}),Fi=(e=>(e.Small="small",e.Large="large",e))(Fi||{}),In=(e=>(e.ackedActive="acked-active",e.unackedActive="unacked-active",e.unackedRectified="unacked-rectified",e))(In||{});var p9=2;function u9(e,t){return t!==void 0&&e.width===t.width&&e.height===t.height&&e.thickness===t.thickness&&e.radii.every((o,r)=>o===t.radii[r])}var yt=class extends S{constructor(){super(...arguments),this.type="small-side-flip",this.thickness="small",this.status=Q.Alarm,this.mode="acked-active",this.flashingSpeed=Ie.Default,this.flashEffect="outline",this.flashing=new Zs(this,()=>this.resolvedFlashingSpeed),this.measureDash=()=>{let e=this.wrapper;if(!e)return;let t=getComputedStyle(e),o=i=>parseFloat(i)||0,r={width:e.offsetWidth,height:e.offsetHeight,thickness:o(t.getPropertyValue("--thickness")),radii:[o(t.borderTopLeftRadius),o(t.borderTopRightRadius),o(t.borderBottomRightRadius),o(t.borderBottomLeftRadius)]};u9(r,this.dashBox)||(this.dashBox=r)},this.wrapContent=!1,this.fullWidth=!1,this.sharpEdgeTopLeft=!1,this.sharpEdgeTopRight=!1,this.sharpEdgeBottomLeft=!1,this.sharpEdgeBottomRight=!1,this.textSize="regular",this.showIcon=!1,this.showAlertCategoryIcon=!0}connectedCallback(){super.connectedCallback(),this.hasUpdated&&this.requestUpdate()}updated(){let e=this.mode==="unacked-rectified"&&this.isConnected;e&&!this.dashObserver&&this.wrapper&&(this.dashObserver=new ResizeObserver(this.measureDash),this.dashObserver.observe(this.wrapper)),e&&this.measureDash(),!e&&this.dashObserver&&(this.dashObserver.disconnect(),this.dashObserver=void 0,this.dashBox=void 0)}disconnectedCallback(){super.disconnectedCallback(),this.dashObserver?.disconnect(),this.dashObserver=void 0}renderDash(){let e=this.dashBox;if(this.mode!=="unacked-rectified"||!e)return z;let t=(e.thickness+p9)/2,o={x:t,y:t,width:e.width,height:e.height,radii:e.radii},r=e.width+2*t,i=e.height+2*t;return f`<svg
      class="dash"
      aria-hidden="true"
      width=${r}
      height=${i}
      viewBox="0 0 ${r} ${i}"
      style="--dash-pad: ${t}px"
    >
      <path d=${N2(o)}></path>
    </svg>`}get resolvedFlashingSpeed(){switch(this.mode){case"unacked-active":return Bn(this.flashingSpeed,this.status,Zi.Active);case"unacked-rectified":return Bn(this.flashingSpeed,this.status,Zi.Rectified);default:return Ie.Fixed}}render(){return f`
      <div
        class=${de({wrapper:!0,"wrap-content":this.wrapContent,"full-width":this.fullWidth,["thickness-"+this.thickness]:!0,[this.type]:!0,[this.status]:!0,["text-size-"+this.textSize]:!0,"sharp-edge-top-left":this.sharpEdgeTopLeft,"sharp-edge-top-right":this.sharpEdgeTopRight,"sharp-edge-bottom-left":this.sharpEdgeBottomLeft,"sharp-edge-bottom-right":this.sharpEdgeBottomRight,[this.mode]:!0,["flash-"+this.resolvedFlashingSpeed]:!0,["flash-effect-"+this.flashEffect]:!0})}
      >
        <slot></slot>
        ${this.renderDash()} ${this.flap()}
      </div>
    `}flap(){if(this.type==="regular")return z;if(this.type==="small-side-flip"&&!this.showAlertCategoryIcon)return z;if(this.type==="large-side-flip"&&!this.showIcon&&!this.showAlertCategoryIcon)return z;let e;return this.showAlertCategoryIcon?e=this.renderBadgeIcon():e=z,this.type==="small-side-flip"?f`<div class="flap small">
        ${e}
        <div class="mask up"></div>
      </div>`:this.type==="large-side-flip"?f`<div class="flap large">
        ${e}
        ${this.showIcon?f`<div class="icon"><slot name="icon"></slot></div>`:z}
        <div class="mask up"></div>
        <div class="mask down"></div>
      </div>`:this.type==="bottom-flip"||this.type==="top-flip"?f`<div
        class="flap ${this.type==="bottom-flip"?"bottom":"top"}"
      >
        ${e}
        ${this.showIcon?f`<div class="icon"><slot name="icon"></slot></div>`:z}
        <div class="label"><slot name="label"></slot></div>
        <div class="spacer"></div>
        <div class="timer"><slot name="timer"></slot></div>
        <div class="mask right"></div>
        <div class="mask left"></div>
      </div>`:(console.error("Unknown type of alert frame:",this.type),z)}renderBadgeIcon(){switch(R2(this.status)){case Is.Critical:return f`<obi-critical-badge
          class="icon badge"
        ></obi-critical-badge>`;case Is.Warning:return f`<obi-warning-badge class="icon badge"></obi-warning-badge>`;case Is.Caution:return f`<obi-caution-badge class="icon badge"></obi-caution-badge>`;case Is.Diagnostic:return f`<obi-diagnostic-badge
          class="icon badge"
        ></obi-diagnostic-badge>`;default:return f`<obi-alarm-badge class="icon badge"></obi-alarm-badge>`}}};yt.styles=ne($2);Rt([h({type:String})],yt.prototype,"type",2);Rt([h({type:String})],yt.prototype,"thickness",2);Rt([h({type:String})],yt.prototype,"status",2);Rt([h({type:String})],yt.prototype,"mode",2);Rt([h({type:String})],yt.prototype,"flashingSpeed",2);Rt([h({type:String})],yt.prototype,"flashEffect",2);Rt([ke()],yt.prototype,"dashBox",2);Rt([at(".wrapper")],yt.prototype,"wrapper",2);Rt([h({type:Boolean,reflect:!0})],yt.prototype,"wrapContent",2);Rt([h({type:Boolean,reflect:!0})],yt.prototype,"fullWidth",2);Rt([h({type:Boolean})],yt.prototype,"sharpEdgeTopLeft",2);Rt([h({type:Boolean})],yt.prototype,"sharpEdgeTopRight",2);Rt([h({type:Boolean})],yt.prototype,"sharpEdgeBottomLeft",2);Rt([h({type:Boolean})],yt.prototype,"sharpEdgeBottomRight",2);Rt([h({type:String})],yt.prototype,"textSize",2);Rt([h({type:Boolean})],yt.prototype,"showIcon",2);Rt([h({type:Boolean,attribute:!1})],yt.prototype,"showAlertCategoryIcon",2);yt=Rt([L("obc-alert-frame")],yt);function Al(e,t,o=!1){return typeof e!="object"||e===null?t:f`<obc-alert-frame
    .type=${e.type??"small-side-flip"}
    .thickness=${e.thickness??"small"}
    .status=${e.status??Q.Alarm}
    .mode=${e.mode??"acked-active"}
    .flashingSpeed=${e.flashingSpeed??Ie.Default}
    .showIcon=${e.showIcon??!1}
    .showAlertCategoryIcon=${e.showAlertCategoryIcon??!0}
    .wrapContent=${!0}
    .fullWidth=${o}
    >${t}</obc-alert-frame
  >`}var j2=M`* {
  -webkit-tap-highlight-color: transparent;
}
.readout-stack {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;
  box-sizing: border-box;

  color: var(--element-active-color, #1f1f1f);

  /* Bridge the stack's colours onto the embedded readout blocks: the number
     follows the row colour, the hinted zeros keep the stack's public
     override var. */
  --obc-readout-block-value-color: var(--element-active-color, #1f1f1f);
  --obc-readout-block-hinted-color: var(
    --obc-automation-button-readout-stack-hinted-color,
    var(--element-disabled-color)
  );
}
.readout-stack .icon {
    display: block;
    width: 16px;
    height: 16px;
  }
.readout-stack.small .icon {
    width: 12px;
    height: 12px;
  }
.readout-stack.enhanced .icon {
    width: 24px;
    height: 24px;
  }

/* Slot-projected row icons: the slot hugs its content so an unfilled slot
     collapses like icon 'none'; the projected element takes the icon size. */
.readout-stack slot.icon {
    display: flex;
    width: auto;
    height: auto;
  }
.readout-stack slot.icon::slotted(*) {
    display: block;
    width: 16px;
    height: 16px;
  }
.readout-stack.small slot.icon::slotted(*) {
    width: 12px;
    height: 12px;
  }
.readout-stack.enhanced slot.icon::slotted(*) {
    width: 24px;
    height: 24px;
  }
.readout-stack .readout-item {
    display: inline-flex;
    padding: 0 4px;
    align-items: center;
    box-sizing: border-box;

    font-family: var(--global-typography-font-family);

    font-size: var(--global-typography-instrument-value-regular-font-size);

    line-height: var(--global-typography-instrument-value-regular-line-height);

    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }
.readout-stack .value-container {
    display: flex;
    padding: 0 4px;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    gap: 10px;
    box-sizing: border-box;
  }
.readout-stack .label-container {
    display: flex;
    align-items: baseline;
    gap: var(--Automation-components-readout-item-Enhanced-value-padding, 2px);
    box-sizing: border-box;
  }
.readout-stack .value-text {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 0;
  }
.readout-stack.small .readout-item {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-small-font-size);
    line-height: var(--global-typography-instrument-value-small-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }
.readout-stack.enhanced .readout-item {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-large-font-size);
    line-height: var(--global-typography-instrument-value-large-line-height);
    letter-spacing: var(
    --global-typography-instrument-value-large-letter-spacing
  );
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }
.readout-stack .readout-item.state-off {
    --element-active-color: var(--element-Inactive-color, #707070);
  }
:is(.readout-stack .readout-item.state-off) .value-text {
      font-weight: var(
        --Automation-components-typography-label-font-weight,
        370
      );
    }
.readout-stack .readout-item.state-on {
    /* Styles for state-on type */
  }

/* The setpoint row is a bare 16px line — the gap to the value rows below is
     carried by the fonts' own leading, per the design. */
.readout-stack .readout-item.setpoint {
    height: 16px;
  }
.readout-stack .setpoint-glyph {
    width: 4px;
    height: 5px;
    fill: var(--element-neutral-color);
  }
.readout-stack obc-button::part(wrapper) {
    /* line-height: var(--global-typography-ui-button-line-height), 24px; */
    line-height: 20px;

    /* height: (--ui-components-button-touch-target-size); 48px, 24px,  */
    height: 20px;
  }
.readout-stack obc-button::part(visible-wrapper) {
    padding-left: 0;
    padding-right: 0;
    height: 20px;
  }
.readout-stack obc-button::part(label) {
    padding-left: 0;
    padding-right: 0;
  }
.readout-stack.small obc-button::part(wrapper) {
    height: 16px;
  }
.readout-stack.small obc-button::part(visible-wrapper) {
    height: 16px;
  }
.readout-stack.enhanced obc-button::part(wrapper) {
    height: 40px;
  }
.readout-stack.enhanced obc-button::part(visible-wrapper) {
    height: 40px;
  }
.readout-stack .value-text {
    color: var(--element-active-color, #1f1f1f);
  }
.label-style-enhanced .readout-stack .value-text {
    color: var(--element-active-color, #1f1f1f);
  }
.readout-stack .unit {
    font-family: var(--font-family-main);
    font-weight: var(--automation-components-typography-unit-regular-font-weight);
    font-size: var(--automation-components-typography-unit-regular-font-size);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    margin-left: 2px;
    padding-right: 2px;
    color: var(--element-neutral-color);
  }
.readout-stack.small .unit {
    font-family: var(--font-family-main);
    font-weight: var(--automation-components-typography-unit-regular-font-weight);
    font-size: var(--automation-components-typography-unit-regular-font-size);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }
.readout-stack.enhanced .unit {
    font-family: var(--font-family-main);
    font-weight: var(--automation-components-typography-unit-regular-font-weight);
    font-size: var(--automation-components-typography-unit-regular-font-size);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    position: relative;
  }
.readout-stack .tag {
    display: flex;
    justify-content: center;
    align-items: center;
    align-self: stretch;

    color: var(--element-Inactive-color, #707070);
    font-family: var(--font-family-main);
    font-weight: var(--automation-components-typography-label-font-weight);
    font-size: var(--automation-components-typography-label-font-size);
    line-height: var(--automation-components-typography-label-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }
.readout-stack .tag .hash {
    text-align: center;
    width: 16px;
    margin-right: 4px;
    font-family: var(--font-family-main);
    font-weight: var(--automation-components-typography-label-font-weight);
    font-size: var(--automation-components-typography-label-font-size);
    line-height: var(--automation-components-typography-label-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }
.readout-stack.small .tag .hash {
    width: 12px;
  }
.readout-stack.enhanced .tag .hash {
    width: 24px;
  }
.label-top .readout-stack,.label-bottom .readout-stack {
    padding-right: 0;
  }
`;var f9=Object.defineProperty,g9=Object.getOwnPropertyDescriptor,W2=(e,t,o,r)=>{for(var i=r>1?void 0:r?g9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&f9(t,o,i),i},Pl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M7.11508 18.7051L5.70508 17.2951L11.7051 11.2951L17.7051 17.2951L16.2951 18.7051L11.7051 14.1251L7.11508 18.7051Z" fill="currentColor"/>
<path d="M7.11508 12.7052L5.70508 11.2952L11.7051 5.29517L17.7051 11.2952L16.2951 12.7052L11.7051 8.12517L7.11508 12.7052Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M7.11508 18.7051L5.70508 17.2951L11.7051 11.2951L17.7051 17.2951L16.2951 18.7051L11.7051 14.1251L7.11508 18.7051Z" style="fill: var(--element-active-color)"/>
<path d="M7.11508 12.7052L5.70508 11.2952L11.7051 5.29517L17.7051 11.2952L16.2951 12.7052L11.7051 8.12517L7.11508 12.7052Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Pl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;W2([h({type:Boolean})],Pl.prototype,"useCssColor",2);Pl=W2([L("obi-chevron-double-up-google")],Pl);var m9=Object.defineProperty,v9=Object.getOwnPropertyDescriptor,U2=(e,t,o,r)=>{for(var i=r>1?void 0:r?v9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&m9(t,o,i),i},Ol=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M16.2948 5.29487L17.7048 6.70487L11.7048 12.7049L5.70483 6.70487L7.11483 5.29487L11.7048 9.87487L16.2948 5.29487Z" fill="currentColor"/>
<path d="M16.2948 11.2948L17.7048 12.7048L11.7048 18.7048L5.70483 12.7048L7.11483 11.2948L11.7048 15.8748L16.2948 11.2948Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M16.2948 5.29487L17.7048 6.70487L11.7048 12.7049L5.70483 6.70487L7.11483 5.29487L11.7048 9.87487L16.2948 5.29487Z" style="fill: var(--element-active-color)"/>
<path d="M16.2948 11.2948L17.7048 12.7048L11.7048 18.7048L5.70483 12.7048L7.11483 11.2948L11.7048 15.8748L16.2948 11.2948Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Ol.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;U2([h({type:Boolean})],Ol.prototype,"useCssColor",2);Ol=U2([L("obi-chevron-double-down-google")],Ol);var b9=Object.defineProperty,w9=Object.getOwnPropertyDescriptor,G2=(e,t,o,r)=>{for(var i=r>1?void 0:r?w9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&b9(t,o,i),i},Vl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M18.41 16.59L17 18L11 12L17 6L18.41 7.41L13.83 12L18.41 16.59Z" fill="currentColor"/>
<path d="M12.41 16.59L11 18L5 12L11 6L12.41 7.41L7.83 12L12.41 16.59Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M18.41 16.59L17 18L11 12L17 6L18.41 7.41L13.83 12L18.41 16.59Z" style="fill: var(--element-active-color)"/>
<path d="M12.41 16.59L11 18L5 12L11 6L12.41 7.41L7.83 12L12.41 16.59Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Vl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;G2([h({type:Boolean})],Vl.prototype,"useCssColor",2);Vl=G2([L("obi-chevron-double-left-google")],Vl);var y9=Object.defineProperty,C9=Object.getOwnPropertyDescriptor,Y2=(e,t,o,r)=>{for(var i=r>1?void 0:r?C9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&y9(t,o,i),i},Tl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M5 7.41L6.41 6L12.41 12L6.41 18L5 16.59L9.58 12L5 7.41Z" fill="currentColor"/>
<path d="M11 7.41L12.41 6L18.41 12L12.41 18L11 16.59L15.58 12L11 7.41Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M5 7.41L6.41 6L12.41 12L6.41 18L5 16.59L9.58 12L5 7.41Z" style="fill: var(--element-active-color)"/>
<path d="M11 7.41L12.41 6L18.41 12L12.41 18L11 16.59L15.58 12L11 7.41Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Tl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Y2([h({type:Boolean})],Tl.prototype,"useCssColor",2);Tl=Y2([L("obi-chevron-double-right-google")],Tl);var x9=Object.defineProperty,_9=Object.getOwnPropertyDescriptor,q2=(e,t,o,r)=>{for(var i=r>1?void 0:r?_9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&x9(t,o,i),i},Dl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12ZM20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12Z" fill="currentColor"/>
<path d="M8 11C7.44772 11 7 11.4477 7 12C7 12.5523 7.44772 13 8 13H16C16.5523 13 17 12.5523 17 12C17 11.4477 16.5523 11 16 11H8Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12ZM20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4C16.4183 4 20 7.58172 20 12Z" style="fill: var(--element-active-color)"/>
<path d="M8 11C7.44772 11 7 11.4477 7 12C7 12.5523 7.44772 13 8 13H16C16.5523 13 17 12.5523 17 12C17 11.4477 16.5523 11 16 11H8Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Dl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;q2([h({type:Boolean})],Dl.prototype,"useCssColor",2);Dl=q2([L("obi-off")],Dl);var k9=Object.defineProperty,L9=Object.getOwnPropertyDescriptor,X2=(e,t,o,r)=>{for(var i=r>1?void 0:r?L9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&k9(t,o,i),i},El=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2ZM12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4Z" fill="currentColor"/>
<path d="M12 6C13.1046 6 14 6.89543 14 8L14 16C14 17.1046 13.1046 18 12 18C10.8954 18 10 17.1046 10 16L10 8C10 6.89543 10.8954 6 12 6Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2ZM12 4C16.4183 4 20 7.58172 20 12C20 16.4183 16.4183 20 12 20C7.58172 20 4 16.4183 4 12C4 7.58172 7.58172 4 12 4Z" style="fill: var(--element-active-color)"/>
<path d="M12 6C13.1046 6 14 6.89543 14 8L14 16C14 17.1046 13.1046 18 12 18C10.8954 18 10 17.1046 10 16L10 8C10 6.89543 10.8954 6 12 6Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};El.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;X2([h({type:Boolean})],El.prototype,"useCssColor",2);El=X2([L("obi-on")],El);var S9=Object.defineProperty,M9=Object.getOwnPropertyDescriptor,K2=(e,t,o,r)=>{for(var i=r>1?void 0:r?M9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&S9(t,o,i),i},Rl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M12 2C13.733 2 15.1492 3.35645 15.2449 5.06546L15.25 5.24987L15.251 13.202L15.331 13.2709C16.2565 14.0975 16.8482 15.2418 16.9746 16.4939L16.9936 16.7457L17 17C17 19.7614 14.7614 22 12 22C9.23858 22 7 19.7614 7 17C7 15.6373 7.5496 14.3655 8.48922 13.4396L8.66993 13.2701L8.749 13.202L8.75 5.25C8.75 3.57886 10.0113 2.20232 11.6339 2.0204L11.8156 2.00514L12 2ZM12 3.5C11.0818 3.5 10.3288 4.20711 10.2558 5.10651L10.25 5.25004L10.2495 13.9445L9.94128 14.1691C9.04185 14.8246 8.5 15.8664 8.5 17C8.5 18.933 10.067 20.5 12 20.5C13.933 20.5 15.5 18.933 15.5 17C15.5 15.9376 15.0241 14.9558 14.2239 14.2971L14.0595 14.1697L13.7515 13.9451L13.75 5.25C13.75 4.2835 12.9665 3.5 12 3.5ZM12 7C12.4142 7 12.75 7.33579 12.75 7.75L12.7506 14.6146C13.7646 14.9334 14.5 15.8808 14.5 17C14.5 18.3807 13.3807 19.5 12 19.5C10.6193 19.5 9.5 18.3807 9.5 17C9.5 15.8804 10.2359 14.9328 11.2504 14.6143L11.25 7.75C11.25 7.33579 11.5858 7 12 7Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 2C13.733 2 15.1492 3.35645 15.2449 5.06546L15.25 5.24987L15.251 13.202L15.331 13.2709C16.2565 14.0975 16.8482 15.2418 16.9746 16.4939L16.9936 16.7457L17 17C17 19.7614 14.7614 22 12 22C9.23858 22 7 19.7614 7 17C7 15.6373 7.5496 14.3655 8.48922 13.4396L8.66993 13.2701L8.749 13.202L8.75 5.25C8.75 3.57886 10.0113 2.20232 11.6339 2.0204L11.8156 2.00514L12 2ZM12 3.5C11.0818 3.5 10.3288 4.20711 10.2558 5.10651L10.25 5.25004L10.2495 13.9445L9.94128 14.1691C9.04185 14.8246 8.5 15.8664 8.5 17C8.5 18.933 10.067 20.5 12 20.5C13.933 20.5 15.5 18.933 15.5 17C15.5 15.9376 15.0241 14.9558 14.2239 14.2971L14.0595 14.1697L13.7515 13.9451L13.75 5.25C13.75 4.2835 12.9665 3.5 12 3.5ZM12 7C12.4142 7 12.75 7.33579 12.75 7.75L12.7506 14.6146C13.7646 14.9334 14.5 15.8808 14.5 17C14.5 18.3807 13.3807 19.5 12 19.5C10.6193 19.5 9.5 18.3807 9.5 17C9.5 15.8804 10.2359 14.9328 11.2504 14.6143L11.25 7.75C11.25 7.33579 11.5858 7 12 7Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Rl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;K2([h({type:Boolean})],Rl.prototype,"useCssColor",2);Rl=K2([L("obi-temperature-air")],Rl);var J2=Symbol.for(""),$9=e=>{if(e?.r===J2)return e?._$litStatic$};var Fs=(e,...t)=>({_$litStatic$:t.reduce((o,r,i)=>o+(s=>{if(s._$litStatic$!==void 0)return s._$litStatic$;throw Error(`Value passed to 'literal' function must be a 'literal' result: ${s}. Use 'unsafeStatic' to pass non-literal values, but
            take care to ensure page security.`)})(r)+e[i+1],e[0]),r:J2}),Q2=new Map,sh=e=>(t,...o)=>{let r=o.length,i,s,n=[],a=[],l,c=0,d=!1;for(;c<r;){for(l=t[c];c<r&&(s=o[c],(i=$9(s))!==void 0);)l+=i+t[++c],d=!0;c!==r&&a.push(s),n.push(l),c++}if(c===r&&n.push(t[r]),d){let p=n.join("$$lit$$");(t=Q2.get(p))===void 0&&(n.raw=n,Q2.set(p,t=n)),o=a}return e(t,...o)},ho=sh(f),EA=sh(w),RA=sh(a2);var Ce=e=>e??z;var e0=M`* {
  -webkit-tap-highlight-color: transparent;
}

.wrapper {
  padding: 0;
  user-select: none;
  background: transparent;
  height: var(--ui-components-button-touch-target-size);
  min-width: var(--ui-components-button-touch-target-size);
  appearance: none;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-feature-settings:
    "liga" off,
    "clig" off;
  font-family: var(--font-family-main);
  font-size: var(--global-typography-ui-button-font-size);
  font-style: normal;
  font-weight: var(--global-typography-ui-button-font-weight);
  line-height: var(--global-typography-ui-button-line-height) /* 150% */;
  text-decoration: none;
}

.wrapper.full-width {
    width: 100%;
  }

.wrapper.full-width .visible-wrapper {
      width: 100%;
    }

.wrapper .visible-wrapper {
    border-radius: var(--ui-components-button-border-radius-top-left)
      var(--ui-components-button-border-radius-top-right)
      var(--ui-components-button-border-radius-bottom-right)
      var(--ui-components-button-border-radius-bottom-left);
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-left: calc(2 * var(--ui-components-button-padding-horizontal));
    padding-right: calc(2 * var(--ui-components-button-padding-horizontal));
    height: var(--ui-components-button-visual-size);
  }

.wrapper .icon {
    height: var(--ui-components-button-icon-size);
    width: var(--ui-components-button-icon-size);
  }

.wrapper:not(.hasIconLeading) .icon.leading {
    display: none;
    width: 0;
  }

.wrapper:not(.hasIconTrailing) .icon.trailing {
    display: none;
    width: 0;
  }

.wrapper .label {
    padding-left: var(--ui-components-button-label-spacing);
    padding-right: var(--ui-components-button-label-spacing);
  }

.wrapper.variant-normal {
  cursor: pointer;
}

.wrapper.variant-normal:focus {
  outline: none;
}

.wrapper.variant-normal .visible-wrapper {
  border-color: var(--normal-enabled-border-color);
  background-color: var(--normal-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--normal-enabled-border-color);
  --base-background-color: var(--normal-enabled-background-color);
}

.wrapper.variant-normal.activated .visible-wrapper {
  border-color: var(--normal-activated-border-color);
  background-color: var(--normal-activated-background-color);
  --base-border-color: var(--normal-activated-border-color);
  --base-background-color: var(--normal-activated-background-color);
}

@media (hover:hover) {

.wrapper.variant-normal:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--normal-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--normal-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.variant-normal:active .visible-wrapper {
  border-color: var(--normal-pressed-border-color);
  background-color: var(--normal-pressed-background-color);
}

.wrapper.variant-normal:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.variant-normal:disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.wrapper.variant-normal.disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.wrapper.variant-normal:disabled {
  cursor: not-allowed;
}

.wrapper.variant-normal.disabled {
  cursor: not-allowed;
}

.wrapper.variant-normal {
    color: var(--on-normal-active-color);
}

.wrapper.variant-normal .icon {
      color: var(--on-normal-neutral-color);
    }

.wrapper.variant-normal:disabled .icon {
      color: var(--on-normal-disabled-color);
    }

.wrapper.variant-flat {
  cursor: pointer;
}

.wrapper.variant-flat:focus {
  outline: none;
}

.wrapper.variant-flat .visible-wrapper {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.wrapper.variant-flat.activated .visible-wrapper {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.wrapper.variant-flat:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.variant-flat:active .visible-wrapper {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.wrapper.variant-flat:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.variant-flat:disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.variant-flat.disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.variant-flat:disabled {
  cursor: not-allowed;
}

.wrapper.variant-flat.disabled {
  cursor: not-allowed;
}

.wrapper.variant-flat {
    color: var(--on-flat-active-color);
}

.wrapper.variant-flat .icon {
      color: var(--on-flat-neutral-color);
    }

.wrapper.variant-flat:disabled .icon {
      color: var(--on-flat-disabled-color);
    }

.wrapper.variant-raised {
  cursor: pointer;
}

.wrapper.variant-raised:focus {
  outline: none;
}

.wrapper.variant-raised .visible-wrapper {
  border-color: var(--raised-enabled-border-color);
  background-color: var(--raised-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--raised-enabled-border-color);
  --base-background-color: var(--raised-enabled-background-color);
}

.wrapper.variant-raised.activated .visible-wrapper {
  border-color: var(--raised-activated-border-color);
  background-color: var(--raised-activated-background-color);
  --base-border-color: var(--raised-activated-border-color);
  --base-background-color: var(--raised-activated-background-color);
}

@media (hover:hover) {

.wrapper.variant-raised:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--raised-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--raised-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.variant-raised:active .visible-wrapper {
  border-color: var(--raised-pressed-border-color);
  background-color: var(--raised-pressed-background-color);
}

.wrapper.variant-raised:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.variant-raised:disabled .visible-wrapper {
  border-color: var(--raised-disabled-border-color);
  background-color: var(--raised-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-raised-disabled-color) !important;
}

.wrapper.variant-raised.disabled .visible-wrapper {
  border-color: var(--raised-disabled-border-color);
  background-color: var(--raised-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-raised-disabled-color) !important;
}

.wrapper.variant-raised:disabled {
  cursor: not-allowed;
}

.wrapper.variant-raised.disabled {
  cursor: not-allowed;
}

.wrapper.variant-raised {
    color: var(--on-raised-active-color);
}

.wrapper.variant-raised .icon {
      color: var(--on-raised-neutral-color);
    }

.wrapper.variant-raised:disabled .icon {
      color: var(--on-raised-disabled-color);
    }

.wrapper.segment-position-start {
    margin-right: -1px;
  }

.wrapper.segment-position-start .visible-wrapper {
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }

.wrapper.segment-position-middle .visible-wrapper {
    border-radius: 0;
  }

.wrapper.segment-position-end .visible-wrapper {
    border-top-left-radius: 0;
    border-bottom-left-radius: 0;
  }

:host:has(.segment-position-start),
:host:has(.segment-position-middle) {
  margin-right: -0.5px;
}

:host:has(.segment-position-middle),
:host:has(.segment-position-end) {
  margin-left: -0.5px;
}
`;var A9=Object.defineProperty,P9=Object.getOwnPropertyDescriptor,_r=(e,t,o,r)=>{for(var i=r>1?void 0:r?P9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&A9(t,o,i),i},nh=(e=>(e.normal="normal",e.raised="raised",e.flat="flat",e))(nh||{});var qo=class extends S{constructor(){super(...arguments),this.variant="normal",this.fullWidth=!1,this.disabled=!1,this.showLeadingIcon=!1,this.showTrailingIcon=!1,this.href=void 0,this.target=void 0,this.segmentPosition="single"}renderLeadingIcon(){return this.showLeadingIcon?ho`
        <span class="icon leading" part="icon leading">
          <slot name="leading-icon"></slot>
        </span>
      `:ho``}renderTrailingIcon(){return this.showTrailingIcon?ho`
        <span class="icon trailing" part="icon trailing">
          <slot name="trailing-icon"></slot>
        </span>
      `:ho``}render(){let e=this.href?Fs`a`:Fs`button`;return ho`
      <${e}
        class=${de({wrapper:!0,["variant-"+this.variant]:!0,hasIconLeading:this.showLeadingIcon,hasIconTrailing:this.showTrailingIcon,"full-width":this.fullWidth,["segment-position-"+this.segmentPosition]:!0})}
        ?disabled=${this.disabled}
        href=${Ce(this.href)}
        target=${Ce(this.target)}
        part="wrapper"
      >
        <div class="visible-wrapper" part="visible-wrapper">
          ${this.renderLeadingIcon()}
          <span class="label" part="label">
            <slot></slot>
          </span>
          ${this.renderTrailingIcon()}
        </div>
      </${e}>
    `}};qo.styles=ne(e0);_r([h({type:String})],qo.prototype,"variant",2);_r([h({type:Boolean,reflect:!0})],qo.prototype,"fullWidth",2);_r([h({type:Boolean})],qo.prototype,"disabled",2);_r([h({type:Boolean})],qo.prototype,"showLeadingIcon",2);_r([h({type:Boolean})],qo.prototype,"showTrailingIcon",2);_r([h({type:String})],qo.prototype,"href",2);_r([h({type:String})],qo.prototype,"target",2);_r([h({type:String})],qo.prototype,"segmentPosition",2);qo=_r([L("obc-button")],qo);var t0=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: inline-flex;
  align-items: flex-end;
}

/* ---------- Readout building block (advice / setpoint / value) ---------- */

.block {
  display: inline-flex;
  align-items: flex-end;
}

/* Number + its (setpoint/advice) degree glyph, hugging with no gap — the
   \`.block\` gap only separates the icon from this group. */

.block-content {
  display: inline-flex;
  align-items: flex-end;
}

.block-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: none;
  color: inherit;
  /* Centre the icon against the block's text rather than bottom-aligning it (the
     block is flex-end). Matters for the value block, whose text is taller than
     the icon, so the value icon lines up with the number like the smaller
     setpoint/advice icons do. */
  align-self: center;
}

.block-icon obi-input-right,
.block-icon obi-notification-advice,
.block-icon ::slotted(*) {
  display: block;
  inline-size: 100%;
  block-size: 100%;
}

.hinted-zero {
  /* Figma 6.1 review (node 95:24490): hinted zeros are lighter than the old
     inactive tone and NEVER inherit the value's weight — a bold value must not
     bold its hints. */
  color: var(--obc-readout-block-hinted-color, var(--element-disabled-color));
  font-weight: var(--global-typography-generic-l-font-weight-regular);
}

.sign-spacer {
  /* visibility, not display: the hidden \`-\` must keep its box so the sign
     column stays open while the value is non-negative (\`hasSignSpacer\`). */
  visibility: hidden;
}

/* ---------- Text colours (overridable via custom properties) ----------
 * obc-textbox does not set its own colour, so it inherits these. */

.block-value {
  color: var(--obc-readout-block-value-color, var(--element-neutral-color));
}

.block-value.tone-enhanced {
  color: var(
    --obc-readout-block-value-enhanced-color,
    var(--element-neutral-enhanced-color)
  );
}

/* The setpoint shares the value's colour state: neutral by default, enhanced
   (blue) only when the row is enhanced — never a blue setpoint next to a grey
   value. \`--instrument-enhanced-secondary-color\` is the same #2d548b as the
   value's \`--element-neutral-enhanced-color\`. */

.block-setpoint {
  color: var(--obc-readout-block-setpoint-color, var(--element-neutral-color));
  /* Flip-flop emphasis + pop-up fade animate at 100ms. */
  transition:
    opacity 100ms ease,
    color 100ms ease;
}

.block-setpoint.tone-enhanced {
  color: var(
    --obc-readout-block-setpoint-enhanced-color,
    var(--instrument-enhanced-secondary-color)
  );
}

/* Pop-up: fade the setpoint out once value === setpoint, keeping its space so
   the value stays column-aligned. */

.block-setpoint.is-hiding {
  opacity: 0;
}

.block-setpoint.is-hidden {
  opacity: 0;
  visibility: hidden;
}

/* Touching / focus state: the setpoint triangle takes the marker's focus look — a
   pale fill (--base-blue-100) with a dark 1px edge (--element-neutral-enhanced),
   mirroring \`svghelpers/setpoint.ts\` focus (fill base-blue-100 + 2px stroke).
   The glyph icon is \`fill: currentColor\` and can't take a CSS \`stroke\`, so the
   edge is layered drop-shadows. The setpoint number keeps its normal, readable
   colour. */

.block-setpoint.touching {
  --_touching-outline: var(
    --obc-readout-block-setpoint-touching-outline-color,
    var(--element-neutral-enhanced-color)
  );
}

.block-setpoint.touching .block-icon {
  color: var(--obc-readout-block-setpoint-touching-color, var(--base-blue-100));
  filter: drop-shadow(1px 0 0 var(--_touching-outline))
    drop-shadow(-1px 0 0 var(--_touching-outline))
    drop-shadow(0 1px 0 var(--_touching-outline))
    drop-shadow(0 -1px 0 var(--_touching-outline));
}

.block-advice {
  color: var(--obc-readout-block-advice-color, var(--element-neutral-color));
}

/* ---------- Advice categories (Figma 6.1 Readout-block-advice) ----------
 * Resting categories are neutral; \`advice-active\` (triggered) tints the
 * regular/optimal/eco diamond via currentColor (the IEC status icons of the
 * alert categories carry fixed fills and ignore this) and switches the alert
 * categories' number to the active text colour. */

.block-advice.advice-active.advice-optimal .block-icon {
  color: var(--element-neutral-enhanced-color);
}

.block-advice.advice-active.advice-eco .block-icon {
  color: var(--base-mint-400);
}

.block-advice.advice-active.advice-caution,
.block-advice.advice-active.advice-warning,
.block-advice.advice-active.advice-alarm,
.block-advice.advice-active.advice-running {
  color: var(--element-active-color);
}

/* ---------- Per-block data quality ----------
 * Uses \`outline\` (not \`border\`) so the chip never shifts the block's width — the
 * value stays column-aligned across rows. */

.block.data-low-integrity,
.block.data-invalid {
  outline: 1px solid;
  border-radius: var(--global-border-radius-border-radius-check);
}

.block.data-low-integrity {
  background: var(--alert-low-integrity-background-color);
  outline-color: var(--alert-low-integrity-border-color);
}

.block.data-invalid {
  background: var(--alert-invalid-background-color);
  outline-color: var(--alert-invalid-border-color);
}

/* ---------- Degree column ----------
 * A cap-height \`°\` column whose width scales with the number size; it inherits
 * the block's colour. */

.degree-column {
  flex: none;
  display: inline-flex;
  align-items: flex-end;
  justify-content: center;
  inline-size: var(--_obc-readout-block-degree-width, 0);
  overflow: clip;
}

.degree-column.degree-inherit {
  color: inherit;
}

.degree-column.degree-xs {
  --_obc-readout-block-degree-width: var(
    --global-typography-instrument-value-small-degree-unit-width
  );
}

.degree-column.degree-s {
  --_obc-readout-block-degree-width: var(
    --global-typography-instrument-value-regular-degree-unit-width
  );
}

.degree-column.degree-m {
  --_obc-readout-block-degree-width: var(
    --global-typography-instrument-value-medium-degree-unit-width
  );
}

.degree-column.degree-l,
.degree-column.degree-xl {
  --_obc-readout-block-degree-width: var(
    --global-typography-instrument-value-large-degree-unit-width
  );
}

/* ---------- Size tiers ----------
 * Public small/medium/large map to the design token regular/medium/large
 * tiers. The icon↔number gap follows the tier; the marker ICON size follows
 * the block's rendered number size (\`value-size-*\`) instead — Figma 6.1
 * (Readout-block-setpoint, review node 95:26891): a de-emphasised S setpoint
 * carries the 16px arrow while an emphasised L one carries the 24px arrow,
 * even though both sit in the same large-tier readout.
 * \`--obc-readout-block-icon-size\` is the consumer escape hatch. */

.block.size-small {
  gap: var(--instrument-components-readout-general-regular-icon-gap);
}

.block.size-medium {
  gap: var(--instrument-components-readout-general-medium-icon-gap);
}

.block.size-large {
  gap: var(--instrument-components-readout-general-large-icon-gap);
}

.block.value-size-xs,
.block.value-size-s {
  --_block-icon-size: var(
    --instrument-components-readout-general-regular-icon-size
  );
}

.block.value-size-m {
  --_block-icon-size: var(
    --instrument-components-readout-general-medium-icon-size
  );
}

.block.value-size-l,
.block.value-size-xl {
  --_block-icon-size: var(
    --instrument-components-readout-general-large-icon-size
  );
}

.block .block-icon {
  inline-size: var(--obc-readout-block-icon-size, var(--_block-icon-size));
  block-size: var(--obc-readout-block-icon-size, var(--_block-icon-size));
}
`;var o0=M`* {
  -webkit-tap-highlight-color: transparent;
}

:host {
  display: inline-block;
  line-height: 0;
}

.wrapper {
  display: inline-flex;
  flex-direction: column;
  width: fit-content;
  --height: 24px;
  --padding: 4px;
  font-family: var(--font-family-main);
  letter-spacing: var(--global-typography-generic-l-letter-spacing);
}

/* The inner-wrapper is the box: its height (--height) is the full textbox
   height, padding included. The content is sized to the cap height and
   vertically centered, which leaves the padding as equal space above and
   below. In engines that support text-box-trim the content box collapses to
   the cap height exactly; in Firefox (no text-box-trim) the content keeps its
   natural line box, so align-items:center + overflow:hidden crops it to the
   same height instead. No padding here – the centering provides it.
   (A small top padding could be added later to nudge the text up in Firefox.) */

.inner-wrapper {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: var(--alignment-justify, flex-end);
  height: var(--height);
  overflow: hidden;
  /* Opt-in: animate a \`size\` change (height + font-size below). Defaults to 0s
     (instant, current behavior) so existing usages and snapshots are unchanged;
     a consumer sets \`--obc-textbox-size-transition\` (e.g. 300ms) to animate the
     swap — used by readout-list-item's setpoint flip-flop. */
  transition: height var(--obc-textbox-size-transition, 0s) ease;
}

/* The spacer must share the content's exact font metrics so the width it
   reserves equals the rendered content width. font-size-adjust scales the
   font, so it has to match too. */

.content,
.length-spacer {
  font-size: calc(var(--height) - 2 * var(--padding));
  font-size-adjust: cap-height 1;
  white-space: nowrap;
  /* Opt-in size animation — see \`.inner-wrapper\`. */
  transition: font-size var(--obc-textbox-size-transition, 0s) ease;
}

.content {
  text-box-trim: trim-both;
  text-box-edge: cap alphabetic;
}

/* Opt-in numeric mode: fixed-width lining numerals so values stay
   column-aligned and width-stable. Applied to the spacer too so the reserved
   width matches the rendered digits exactly. */

.wrapper.tabular-nums .content,
.wrapper.tabular-nums .length-spacer {
  font-variant-numeric: tabular-nums lining-nums;
  font-feature-settings:
    "ss04" on,
    "tnum" on,
    "lnum" on;
}

/* Size override is set on \`.wrapper\` (not \`.inner-wrapper\`) so it reaches BOTH
   the visible \`.content\` AND the sibling \`.length-spacer\`; otherwise the spacer
   keeps the default (m) \`--height\` and reserves width at the wrong font size. */

.wrapper.size-xs {
  --height: 16px;
}

.wrapper.size-s {
  --height: 20px;
}

.wrapper.size-m {
  --height: 24px;
}

.wrapper.size-l {
  --height: 32px;
}

.wrapper.size-xl {
  --height: 40px;
}

.wrapper.font-weight-regular {
  font-weight: var(--global-typography-generic-l-font-weight-regular);
}

.wrapper.font-weight-semibold {
  font-weight: var(--global-typography-generic-l-font-weight-medium);
}

.wrapper.font-weight-bold {
  font-weight: var(--global-typography-generic-l-font-weight-bold);
}

.wrapper.alignment-left {
  --alignment-justify: flex-start;
}

.wrapper.alignment-center {
  --alignment-justify: center;
}

.wrapper.alignment-right {
  --alignment-justify: flex-end;
}

/* Reserves the box width from the \`length\` slot without occupying vertical
   space. Acts as a minimum width so the box does not resize as visible
   text changes. */

.length-spacer {
  height: 0;
  opacity: 0;
  visibility: hidden;
  overflow: hidden;
}
`;var O9=Object.defineProperty,V9=Object.getOwnPropertyDescriptor,Zn=(e,t,o,r)=>{for(var i=r>1?void 0:r?V9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&O9(t,o,i),i},ah=(e=>(e.Left="left",e.Center="center",e.Right="right",e))(ah||{}),kr=(e=>(e.xs="xs",e.s="s",e.m="m",e.l="l",e.xl="xl",e))(kr||{}),zl=(e=>(e.regular="regular",e.semibold="semibold",e.bold="bold",e))(zl||{}),Ni=class extends S{constructor(){super(...arguments),this.alignment="right",this.size="m",this.fontWeight="regular",this.tabularNums=!1}render(){return f`
      <div
        class=${de({wrapper:!0,[`alignment-${this.alignment}`]:!0,[`size-${this.size}`]:!0,[`font-weight-${this.fontWeight}`]:!0,"tabular-nums":this.tabularNums})}
      >
        <div class="inner-wrapper">
          <div class="content">
            <slot></slot>
          </div>
        </div>
        <div class="length-spacer" aria-hidden="true">
          <slot name="length"></slot>
        </div>
      </div>
    `}};Ni.styles=ne(o0);Zn([h({type:String})],Ni.prototype,"alignment",2);Zn([h({type:String})],Ni.prototype,"size",2);Zn([h({type:String})],Ni.prototype,"fontWeight",2);Zn([h({type:Boolean})],Ni.prototype,"tabularNums",2);Ni=Zn([L("obc-textbox")],Ni);var T9=Object.defineProperty,D9=Object.getOwnPropertyDescriptor,r0=(e,t,o,r)=>{for(var i=r>1?void 0:r?D9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&T9(t,o,i),i},Hl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M7 7.20382C7 6.21532 8.17595 5.65107 9 6.24417L16.2777 11.1724C16.8633 11.5689 16.8634 12.4315 16.2779 12.8282L9 17.76C8.17595 18.3531 7 17.7888 7 16.8003L7 7.20382Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M7 7.20382C7 6.21532 8.17595 5.65107 9 6.24417L16.2777 11.1724C16.8633 11.5689 16.8634 12.4315 16.2779 12.8282L9 17.76C8.17595 18.3531 7 17.7888 7 16.8003L7 7.20382Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Hl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;r0([h({type:Boolean})],Hl.prototype,"useCssColor",2);Hl=r0([L("obi-input-right")],Hl);var E9=Object.defineProperty,R9=Object.getOwnPropertyDescriptor,i0=(e,t,o,r)=>{for(var i=r>1?void 0:r?R9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&E9(t,o,i),i},Bl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 19L12 22L15 19H20C21.1046 19 22 18.1046 22 17V5C22 3.89543 21.1046 3 20 3H4C2.89543 3 2 3.89543 2 5V17C2 18.1046 2.89543 19 4 19H9ZM12 19.1716L14.1716 17H20V5H4L4 17H9.82843L12 19.1716Z" fill="currentColor"/>
<path d="M9.73374 14.6603L11.9999 13.3297L14.2661 14.6603C14.5878 14.8492 14.9786 14.5593 14.8912 14.1967L14.2965 11.7277L16.279 10.0676C16.5695 9.82438 16.4181 9.35125 16.0403 9.32191L13.4152 9.11796L12.3877 6.75425C12.2403 6.41525 11.7595 6.41525 11.6122 6.75425L10.5846 9.11796L7.95951 9.32191C7.58176 9.35125 7.43032 9.82438 7.72082 10.0676L9.70335 11.7277L9.10859 14.1967C9.02124 14.5593 9.41208 14.8492 9.73374 14.6603Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 19L12 22L15 19H20C21.1046 19 22 18.1046 22 17V5C22 3.89543 21.1046 3 20 3H4C2.89543 3 2 3.89543 2 5V17C2 18.1046 2.89543 19 4 19H9ZM12 19.1716L14.1716 17H20V5H4L4 17H9.82843L12 19.1716Z" style="fill: var(--element-active-color)"/>
<path d="M9.73374 14.6603L11.9999 13.3297L14.2661 14.6603C14.5878 14.8492 14.9786 14.5593 14.8912 14.1967L14.2965 11.7277L16.279 10.0676C16.5695 9.82438 16.4181 9.35125 16.0403 9.32191L13.4152 9.11796L12.3877 6.75425C12.2403 6.41525 11.7595 6.41525 11.6122 6.75425L10.5846 9.11796L7.95951 9.32191C7.58176 9.35125 7.43032 9.82438 7.72082 10.0676L9.70335 11.7277L9.10859 14.1967C9.02124 14.5593 9.41208 14.8492 9.73374 14.6603Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Bl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;i0([h({type:Boolean})],Bl.prototype,"useCssColor",2);Bl=i0([L("obi-notification-advice")],Bl);var z9=Object.defineProperty,H9=Object.getOwnPropertyDescriptor,s0=(e,t,o,r)=>{for(var i=r>1?void 0:r?H9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&z9(t,o,i),i},Il=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 19C2.89543 19 2 18.1046 2 17V5C2 3.89543 2.89543 3 4 3H20C21.1046 3 22 3.89543 22 5V17C22 18.1046 21.1046 19 20 19H15L12 22L9 19H4ZM11.9999 13.5759L9.32009 15.1495C8.93971 15.3728 8.47753 15.03 8.58083 14.6012L9.28416 11.6815L6.93972 9.7184C6.5962 9.43075 6.77528 8.87125 7.22199 8.83654L10.3263 8.59537L11.5414 5.80017C11.7157 5.39929 12.2842 5.39929 12.4585 5.80017L13.6736 8.59537L16.7779 8.83654C17.2246 8.87125 17.4037 9.43075 17.0602 9.7184L14.7157 11.6815L15.4191 14.6012C15.5224 15.03 15.0602 15.3728 14.6798 15.1495L11.9999 13.5759Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 19C2.89543 19 2 18.1046 2 17V5C2 3.89543 2.89543 3 4 3H20C21.1046 3 22 3.89543 22 5V17C22 18.1046 21.1046 19 20 19H15L12 22L9 19H4ZM11.9999 13.5759L9.32009 15.1495C8.93971 15.3728 8.47753 15.03 8.58083 14.6012L9.28416 11.6815L6.93972 9.7184C6.5962 9.43075 6.77528 8.87125 7.22199 8.83654L10.3263 8.59537L11.5414 5.80017C11.7157 5.39929 12.2842 5.39929 12.4585 5.80017L13.6736 8.59537L16.7779 8.83654C17.2246 8.87125 17.4037 9.43075 17.0602 9.7184L14.7157 11.6815L15.4191 14.6012C15.5224 15.03 15.0602 15.3728 14.6798 15.1495L11.9999 13.5759Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Il.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;s0([h({type:Boolean})],Il.prototype,"useCssColor",2);Il=s0([L("obi-notification-advice-active")],Il);var B9=Object.defineProperty,I9=Object.getOwnPropertyDescriptor,n0=(e,t,o,r)=>{for(var i=r>1?void 0:r?I9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&B9(t,o,i),i},Zl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 4V20H20V4L4 4ZM2 4C2 2.89543 2.89543 2 4 2H20C21.1046 2 22 2.89543 22 4V20C22 21.1046 21.1046 22 20 22H4C2.89543 22 2 21.1046 2 20V4Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M11 6H13V14H11V6ZM13 16V18H11V16H13Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 4V20H20V4L4 4ZM2 4C2 2.89543 2.89543 2 4 2H20C21.1046 2 22 2.89543 22 4V20C22 21.1046 21.1046 22 20 22H4C2.89543 22 2 21.1046 2 20V4Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M11 6H13V14H11V6ZM13 16V18H11V16H13Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Zl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;n0([h({type:Boolean})],Zl.prototype,"useCssColor",2);Zl=n0([L("obi-caution-google")],Zl);var Z9=Object.defineProperty,F9=Object.getOwnPropertyDescriptor,a0=(e,t,o,r)=>{for(var i=r>1?void 0:r?F9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Z9(t,o,i),i},Fl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="currentColor"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="currentColor"/>
<path d="M11 14V6H13V14H11Z" fill="currentColor"/>
<path d="M13 16H11V18H13V16Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" style="fill: var(--alert-caution-color)"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" style="stroke: var(--alert-caution-outline-color)"/>
<path d="M11 14V6H13V14H11Z" style="fill: var(--on-caution-active-color)"/>
<path d="M13 16H11V18H13V16Z" style="fill: var(--on-caution-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Fl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;a0([h({type:Boolean})],Fl.prototype,"useCssColor",2);Fl=a0([L("obi-caution-color-iec")],Fl);var N9=Object.defineProperty,j9=Object.getOwnPropertyDescriptor,l0=(e,t,o,r)=>{for(var i=r>1?void 0:r?j9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&N9(t,o,i),i},Nl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="currentColor"/>
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H11L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.7606 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" style="fill: var(--element-active-color)"/>
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H11L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.7606 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Nl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;l0([h({type:Boolean})],Nl.prototype,"useCssColor",2);Nl=l0([L("obi-warning-unacknowledged-outlined")],Nl);var W9=Object.defineProperty,U9=Object.getOwnPropertyDescriptor,c0=(e,t,o,r)=>{for(var i=r>1?void 0:r?U9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&W9(t,o,i),i},jl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" fill="currentColor"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" stroke="currentColor"/>
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H10.6686C10.7909 9.99993 10.8521 9.99993 10.9096 9.98611C10.9606 9.97386 11.0094 9.95366 11.0541 9.92625C11.1046 9.89533 11.1478 9.85209 11.2343 9.76561L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.76061 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11.2343 14.2342C11.1478 14.1478 11.1046 14.1045 11.0541 14.0736C11.0094 14.0462 10.9606 14.026 10.9096 14.0137C10.8521 13.9999 10.7909 13.9999 10.6686 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" style="fill: var(--alert-warning-color)"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" style="stroke: var(--alert-warning-outline-color)"/>
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H10.6686C10.7909 9.99993 10.8521 9.99993 10.9096 9.98611C10.9606 9.97386 11.0094 9.95366 11.0541 9.92625C11.1046 9.89533 11.1478 9.85209 11.2343 9.76561L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.76061 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11.2343 14.2342C11.1478 14.1478 11.1046 14.1045 11.0541 14.0736C11.0094 14.0462 10.9606 14.026 10.9096 14.0137C10.8521 13.9999 10.7909 13.9999 10.6686 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" style="fill: var(--on-warning-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};jl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;c0([h({type:Boolean})],jl.prototype,"useCssColor",2);jl=c0([L("obi-warning-unacknowledged-iec")],jl);var G9=Object.defineProperty,Y9=Object.getOwnPropertyDescriptor,d0=(e,t,o,r)=>{for(var i=r>1?void 0:r?Y9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&G9(t,o,i),i},Wl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.3426 20L12.0005 4.14753L3.65752 20L20.3426 20ZM11.1158 1.53427L1.11648 20.5339C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.9995 8.99999H12.9995V14H10.9995V8.99999ZM12.9995 16V18H10.9995V16H12.9995Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.3426 20L12.0005 4.14753L3.65752 20L20.3426 20ZM11.1158 1.53427L1.11648 20.5339C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.9995 8.99999H12.9995V14H10.9995V8.99999ZM12.9995 16V18H10.9995V16H12.9995Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Wl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;d0([h({type:Boolean})],Wl.prototype,"useCssColor",2);Wl=d0([L("obi-alarm")],Wl);var q9=Object.defineProperty,X9=Object.getOwnPropertyDescriptor,h0=(e,t,o,r)=>{for(var i=r>1?void 0:r?X9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&q9(t,o,i),i},Ul=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" fill="currentColor" stroke="currentColor"/>
<path d="M7.5 15.7V13.3C7.5 13.02 7.5 12.88 7.5545 12.7731C7.60243 12.679 7.67892 12.6025 7.773 12.5545C7.87996 12.5 8.01997 12.5 8.3 12.5H10.6686C10.7909 12.5 10.8521 12.5 10.9096 12.4862C10.9606 12.474 11.0094 12.4538 11.0541 12.4264C11.1046 12.3954 11.1478 12.3522 11.2343 12.2657L13.6343 9.86573C14.0627 9.43736 14.2769 9.22317 14.4608 9.2087C14.6203 9.19614 14.7763 9.26073 14.8802 9.38243C15 9.5227 15 9.8256 15 10.4314V18.5687C15 19.1745 15 19.4774 14.8802 19.6177C14.7763 19.7394 14.6203 19.804 14.4608 19.7914C14.2769 19.7769 14.0627 19.5627 13.6343 19.1344L11.2343 16.7344C11.1478 16.6479 11.1046 16.6047 11.0541 16.5737C11.0094 16.5463 10.9606 16.5261 10.9096 16.5139C10.8521 16.5 10.7909 16.5 10.6686 16.5H8.3C8.01997 16.5 7.87996 16.5 7.773 16.4456C7.67892 16.3976 7.60243 16.3211 7.5545 16.227C7.5 16.1201 7.5 15.9801 7.5 15.7Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" style="fill: var(--alert-alarm-color); stroke: var(--alert-alarm-outline-color)"/>
<path d="M7.5 15.7V13.3C7.5 13.02 7.5 12.88 7.5545 12.7731C7.60243 12.679 7.67892 12.6025 7.773 12.5545C7.87996 12.5 8.01997 12.5 8.3 12.5H10.6686C10.7909 12.5 10.8521 12.5 10.9096 12.4862C10.9606 12.474 11.0094 12.4538 11.0541 12.4264C11.1046 12.3954 11.1478 12.3522 11.2343 12.2657L13.6343 9.86573C14.0627 9.43736 14.2769 9.22317 14.4608 9.2087C14.6203 9.19614 14.7763 9.26073 14.8802 9.38243C15 9.5227 15 9.8256 15 10.4314V18.5687C15 19.1745 15 19.4774 14.8802 19.6177C14.7763 19.7394 14.6203 19.804 14.4608 19.7914C14.2769 19.7769 14.0627 19.5627 13.6343 19.1344L11.2343 16.7344C11.1478 16.6479 11.1046 16.6047 11.0541 16.5737C11.0094 16.5463 10.9606 16.5261 10.9096 16.5139C10.8521 16.5 10.7909 16.5 10.6686 16.5H8.3C8.01997 16.5 7.87996 16.5 7.773 16.4456C7.67892 16.3976 7.60243 16.3211 7.5545 16.227C7.5 16.1201 7.5 15.9801 7.5 15.7Z" style="fill: var(--on-alarm-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Ul.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;h0([h({type:Boolean})],Ul.prototype,"useCssColor",2);Ul=h0([L("obi-alarm-unacknowledged-iec")],Ul);var K9=Object.defineProperty,Q9=Object.getOwnPropertyDescriptor,p0=(e,t,o,r)=>{for(var i=r>1?void 0:r?Q9(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&K9(t,o,i),i},Gl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12.0005 20C16.4188 20 20.0005 16.4183 20.0005 12C20.0005 7.58172 16.4188 4 12.0005 4C7.58221 4 4.00049 7.58172 4.00049 12C4.00049 16.4183 7.58221 20 12.0005 20ZM12.0005 22C17.5233 22 22.0005 17.5228 22.0005 12C22.0005 6.47715 17.5233 2 12.0005 2C6.47764 2 2.00049 6.47715 2.00049 12C2.00049 17.5228 6.47764 22 12.0005 22Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.7072 9.70706L10.5001 16.9142L6.29297 12.7071L7.70718 11.2928L10.5001 14.0857L16.293 8.29285L17.7072 9.70706Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12.0005 20C16.4188 20 20.0005 16.4183 20.0005 12C20.0005 7.58172 16.4188 4 12.0005 4C7.58221 4 4.00049 7.58172 4.00049 12C4.00049 16.4183 7.58221 20 12.0005 20ZM12.0005 22C17.5233 22 22.0005 17.5228 22.0005 12C22.0005 6.47715 17.5233 2 12.0005 2C6.47764 2 2.00049 6.47715 2.00049 12C2.00049 17.5228 6.47764 22 12.0005 22Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.7072 9.70706L10.5001 16.9142L6.29297 12.7071L7.70718 11.2928L10.5001 14.0857L16.293 8.29285L17.7072 9.70706Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Gl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;p0([h({type:Boolean})],Gl.prototype,"useCssColor",2);Gl=p0([L("obi-running")],Gl);var J9=Object.defineProperty,e3=Object.getOwnPropertyDescriptor,u0=(e,t,o,r)=>{for(var i=r>1?void 0:r?e3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&J9(t,o,i),i},Yl=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20718L10.5 16.9143L5.79291 12.2072L7.20712 10.793L10.5 14.0859L16.7929 7.79297L18.2071 9.20718Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" style="fill: var(--alert-running-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20718L10.5 16.9143L5.79291 12.2072L7.20712 10.793L10.5 14.0859L16.7929 7.79297L18.2071 9.20718Z" style="fill: var(--on-running-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Yl.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;u0([h({type:Boolean})],Yl.prototype,"useCssColor",2);Yl=u0([L("obi-running-color-iec")],Yl);var Fn=(e=>(e.number="number",e.text="text",e))(Fn||{}),f0=Object.values(Fn);function t3(e){return typeof e=="string"&&f0.includes(e)}var lh=100;function o3(e){return e==null||Number.isNaN(e)?0:Math.trunc(e)}function g0(e,t){let o=o3(t);if(!(Number.isFinite(o)&&o>=0&&o<=lh))throw new RangeError(`<${e}>: fractionDigits must be between 0 and ${lh} (got ${String(t)}).`)}function m0(e){let t=Math.trunc(e??0);return Number.isNaN(t)||t<=0?0:Math.min(t,lh)}function ql(e){return e==null||Number.isNaN(e)}function ch(e){return e.trim()===""}function v0(e,t,o){let r=o??"number";if(!t3(r))throw new TypeError(`<${e}>: valueType must be ${f0.map(i=>`"${i}"`).join(" or ")} (got ${JSON.stringify(o)}).`);if(!(r!=="number"||typeof t!="string"||ch(t))&&!Number.isFinite(Number(t)))throw new TypeError(`<${e}>: value must be a number when valueType is "number" (got ${JSON.stringify(t)}). Set valueType="text" to render text.`)}function b0(e,t){if(t==="text"||e===null||e===void 0)return;if(typeof e=="number")return Number.isFinite(e)?e:void 0;if(ch(e))return;let o=Number(e);return Number.isFinite(o)?o:void 0}function w0(e,t){if(t!=="text"||e===null||e===void 0)return;let o=typeof e=="number"?String(e):e;return ch(o)?void 0:o}var Lr="\u2012";function r3({showZeroPadding:e,minValueLength:t,fractionDigits:o}){let r=e?Math.max(t,1):1,i=Number.isNaN(o)?0:o;return i<1?Lr.repeat(r):Lr.repeat(r)+"."+Lr.repeat(i)}function y0(e,t){return e===void 0||!Number.isFinite(e)||Number.isNaN(t.fractionDigits)?r3(t):e.toFixed(t.fractionDigits)}function i3(e){let t=e.trim();if(!t)return 0;let o=t.startsWith("-")?t.slice(1):t,r=o.indexOf(".");return r===-1?o.length:r}function C0(e,t){if(!/\d/.test(e))return{sign:"",hinted:"",magnitude:e};let o=e.startsWith("-"),r=o?e.slice(1):e,i=Math.max(t-i3(r),0);return{sign:o?"-":"",hinted:i>0?"0".repeat(i):"",magnitude:r}}var s3=Object.defineProperty,n3=Object.getOwnPropertyDescriptor,rt=(e,t,o,r)=>{for(var i=r>1?void 0:r?n3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&s3(t,o,i),i},Nn=(e=>(e.value="value",e.setpoint="setpoint",e.advice="advice",e))(Nn||{}),Sr=(e=>(e.small="small",e.medium="medium",e.large="large",e))(Sr||{});var Ye=class extends S{constructor(){super(...arguments),this.variant="value",this.value=null,this.valueType=Fn.number,this.size="small",this.enhanced=!1,this.weight=zl.regular,this.hasDegree=!1,this.hasIcon=!1,this.fractionDigits=0,this.maxDigits=0,this.hintedZeros=!1,this.hasSignSpacer=!1,this.off=!1,this.offText="OFF",this.alignment=ah.Right,this.category="regular",this.active=!1,this.alert=!1,this.touching=!1,this.hidePhase="none",this.hasAssignedIcon=!1,this.onIconSlotChange=e=>{this.hasAssignedIcon=e.target.assignedElements({flatten:!0}).length>0}}get resolvedValueSize(){if(this.valueSize)return this.valueSize;switch(this.size){case"large":return kr.l;case"medium":return kr.m;default:return kr.s}}get resolvedMaxDigits(){return m0(this.maxDigits)}get digitCountsMissing(){return ql(this.fractionDigits)||ql(this.maxDigits)}get numericFormatOptions(){return{showZeroPadding:this.hintedZeros,minValueLength:this.resolvedMaxDigits,fractionDigits:ql(this.fractionDigits)?0:this.fractionDigits}}get reserverText(){let e=this.resolvedMaxDigits;if(e<=0)return"";let t="0".repeat(e);return this.fractionDigits>0?`${t}.${"0".repeat(this.fractionDigits)}`:t}widerReserver(e,t){return e?t?e.length>=t.length?e:t:e:t}dataQualityClasses(){return{"data-low-integrity":this.dataQuality==="low-integrity","data-invalid":this.dataQuality==="invalid"}}renderIcon(){if(!(this.variant!=="value"||this.hasIcon))return z;let t=z;return this.variant==="setpoint"?t=f`<obi-input-right></obi-input-right>`:this.variant==="advice"&&(t=this.adviceFallbackIcon()),f`<span class="block-icon" part="block-icon" aria-hidden="true">
      <slot name="icon" @slotchange=${this.onIconSlotChange}></slot>
      ${this.hasAssignedIcon?z:t}
    </span>`}adviceFallbackIcon(){let e=this.active;switch(this.category){case"caution":return e?f`<obi-caution-color-iec useCssColor></obi-caution-color-iec>`:f`<obi-caution-google></obi-caution-google>`;case"warning":return e?f`<obi-warning-unacknowledged-iec
              useCssColor
            ></obi-warning-unacknowledged-iec>`:f`<obi-warning-unacknowledged-outlined></obi-warning-unacknowledged-outlined>`;case"alarm":return e?f`<obi-alarm-unacknowledged-iec
              useCssColor
            ></obi-alarm-unacknowledged-iec>`:f`<obi-alarm></obi-alarm>`;case"running":return e?f`<obi-running-color-iec useCssColor></obi-running-color-iec>`:f`<obi-running></obi-running>`;default:return e?f`<obi-notification-advice-active></obi-notification-advice-active>`:f`<obi-notification-advice></obi-notification-advice>`}}renderDegreeGlyph(e){return f`
      <span
        class=${de({"degree-column":!0,[`degree-${e}`]:!0,"degree-inherit":!0})}
        part="degree"
      >
        <obc-textbox class="degree-glyph" .size=${e} alignment="center"
          >°</obc-textbox
        >
      </span>
    `}willUpdate(e){super.willUpdate(e),v0("obc-readout-block",this.value,this.valueType),g0("obc-readout-block",this.fractionDigits)}render(){let e=this.resolvedValueSize,t=this.variant==="advice",r=t&&this.active&&(this.category==="regular"||this.category==="optimal"||this.category==="eco")?zl.semibold:this.weight,i=this.numericFormatOptions,s=this.valueType===Fn.text,n=this.digitCountsMissing?void 0:b0(this.value,this.valueType),a=w0(this.value,this.valueType),l=this.off?this.offText:s?a??Lr:y0(n,i),c=!this.off&&!s&&this.hintedZeros&&n!==void 0,{sign:d,hinted:p,magnitude:u}=c?C0(l,this.resolvedMaxDigits):{sign:"",hinted:"",magnitude:l},m=this.hasSignSpacer&&!s&&d===""&&!u.startsWith("-"),b=s?this.spaceReserver??"":this.widerReserver(this.spaceReserver,this.reserverText),C=!s&&this.hasSignSpacer&&!b.startsWith("-")?`-${b}`:b,y=f`
      <div
        class=${de({block:!0,[`block-${this.variant}`]:!0,[`size-${this.size}`]:!0,[`value-size-${e}`]:!0,[`advice-${this.category}`]:t,"advice-active":t&&this.active,"tone-enhanced":this.enhanced,touching:this.touching,"is-hiding":this.hidePhase==="hiding","is-hidden":this.hidePhase==="hidden",...this.dataQualityClasses()})}
        part="block block-${this.variant}"
      >
        ${this.renderIcon()}
        <span class="block-content" part="block-content">
          <obc-textbox
            class="block-text"
            part="block-text"
            .size=${e}
            .fontWeight=${r}
            .alignment=${this.alignment}
            .tabularNums=${!0}
          >
            ${d}${m?f`<span class="sign-spacer" aria-hidden="true">-</span>`:z}${p?f`<span class="hinted-zero" aria-hidden="true"
                  >${p}</span
                >`:z}${u}
            ${C?f`<span slot="length">${C}</span>`:z}
          </obc-textbox>
          ${this.hasDegree?this.renderDegreeGlyph(e):z}
        </span>
      </div>
    `;return Al(this.alert??!1,y)}};Ye.styles=ne(t0);rt([h({type:String})],Ye.prototype,"variant",2);rt([h({type:String})],Ye.prototype,"value",2);rt([h({type:String})],Ye.prototype,"valueType",2);rt([h({type:String})],Ye.prototype,"size",2);rt([h({type:String})],Ye.prototype,"valueSize",2);rt([h({type:Boolean})],Ye.prototype,"enhanced",2);rt([h({type:String})],Ye.prototype,"weight",2);rt([h({type:Boolean})],Ye.prototype,"hasDegree",2);rt([h({type:Boolean})],Ye.prototype,"hasIcon",2);rt([h({type:Number})],Ye.prototype,"fractionDigits",2);rt([h({type:Number})],Ye.prototype,"maxDigits",2);rt([h({type:Boolean})],Ye.prototype,"hintedZeros",2);rt([h({type:Boolean})],Ye.prototype,"hasSignSpacer",2);rt([h({type:String})],Ye.prototype,"spaceReserver",2);rt([h({type:Boolean})],Ye.prototype,"off",2);rt([h({type:String})],Ye.prototype,"offText",2);rt([h({type:String})],Ye.prototype,"alignment",2);rt([h({type:String})],Ye.prototype,"category",2);rt([h({type:Boolean})],Ye.prototype,"active",2);rt([h({type:String})],Ye.prototype,"dataQuality",2);rt([h({type:Object})],Ye.prototype,"alert",2);rt([h({type:Boolean})],Ye.prototype,"touching",2);rt([h({type:String})],Ye.prototype,"hidePhase",2);rt([ke()],Ye.prototype,"hasAssignedIcon",2);Ye=rt([L("obc-readout-block")],Ye);function x0(e,t,o){return Math.min(Math.max(e,t),o)}function Xl(e){return e*Math.PI/180}var to=(e=>(e.active="active",e.loading="loading",e.off="off",e))(to||{}),zt=(e=>(e.regular="regular",e.enhanced="enhanced",e))(zt||{}),Mr=(e=>(e.regular="regular",e.flat="flat",e.framed="framed",e.instrument="instrument",e))(Mr||{}),Qe=(e=>(e.innerFirstChild="innerFirstChild",e.middleChild="middleChild",e.middleRoundedChild="middleRoundedChild",e.outerLastChild="outerLastChild",e))(Qe||{});var ji=(e=>(e.notEqual="notEqual",e.equal="equal",e.equalZero="equalZero",e.focus="focus",e))(ji||{}),Kl=(e=>(e.enhanced="enhanced",e.regular="regular",e))(Kl||{}),dh="M22.5918 0.5C25.014 0.50013 26.3186 3.34437 24.917 5.29199L15.0244 19.0371C14.0268 20.423 11.9635 20.423 10.9658 19.0371L1.07326 5.29199C-0.328328 3.34437 0.97623 0.500124 3.39845 0.5L22.5918 0.5Z";var k0=21,l3=13,c3=21,d3=.8,h3=4,hh=8,_0=300,ph="--setpoint-animation-duration",L0="300ms";function S0(e){let t=getComputedStyle(e).getPropertyValue(ph).trim();if(!t)return _0;let o=parseFloat(t);return Number.isNaN(o)?_0:t.endsWith("s")&&!t.endsWith("ms")?o*1e3:o}function p3(e,t,o=!1){return o?"var(--instrument-frame-tertiary-color)":e==="focus"?t==="enhanced"?"var(--base-blue-100)":"var(--instrument-regular-tertiary-color)":t==="enhanced"?"var(--instrument-enhanced-primary-color)":"var(--instrument-regular-primary-color)"}function u3(e,t){return e==="focus"?t==="enhanced"?"var(--element-neutral-enhanced-color)":"var(--instrument-regular-secondary-color)":"var(--border-silhouette-color)"}function f3(e){return dh}function g3(e){switch(e){case"equal":case"equalZero":return d3;default:return 1}}function M0(e){switch(e){case"equalZero":return hh;case"notEqual":case"focus":return h3;default:return 0}}function $0(e="setpoint"){return`${e}-${Math.random().toString(36).slice(2,9)}`}function uh(e){let{visualState:t,colorMode:o,disabled:r=!1,id:i}=e,s=p3(t,o,r),n=u3(t,o),a=f3(),l=g3(t),c=`${i}-marker`,d=`${i}-mask`,p=-l3,u=-c3,m=`scale(${l})`;return w`
    <defs>
      <g id="${c}">
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          transform="translate(${p}, ${u})"
          d="${a}"
          vector-effect="non-scaling-stroke"
        />
      </g>
      <mask id="${d}">
        <rect x="-20" y="-30" width="50" height="50" fill="white" />
        <use href="#${c}" fill="black" />
      </mask>
    </defs>
    <g transform="${m}" style="transition: transform 200ms ease-in-out;">
      <use href="#${c}" fill="${s}" stroke="none" />
      ${t==="focus"?w`
          <!-- Focus state: 1px silhouette (outer) + 2px colored border (inner) -->
          <!-- First: masked silhouette stroke for outer 1px edge -->
          <use
            href="#${c}"
            mask="url(#${d})"
            fill="none"
            stroke="var(--border-silhouette-color)"
            stroke-width="4"
            stroke-linejoin="round"
            vector-effect="non-scaling-stroke"
          />
          <!-- Second: 2px colored border on top -->
          <use
            href="#${c}"
            fill="none"
            stroke="${n}"
            stroke-width="2"
            stroke-linejoin="round"
            vector-effect="non-scaling-stroke"
          />
        `:w`
          <use
            href="#${c}"
            mask="url(#${d})"
            fill="none"
            stroke="${n}"
            stroke-width="2"
            stroke-linejoin="round"
            vector-effect="non-scaling-stroke"
          />
        `}
    </g>
  `}function Ql(e){let{value:t,setpoint:o,touching:r,auto:i,deadband:s,atSetpointManual:n,angularWraparound:a=!1}=e;if(t===void 0||o===void 0||r)return!1;if(i){let l=Math.abs(t-o);a&&l>180&&(l=360-l);let c=Number.isFinite(s)?s:0;return l<=c}return n}var m3=Object.defineProperty,v3=Object.getOwnPropertyDescriptor,jn=(e,t,o,r)=>{for(var i=r>1?void 0:r?v3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&m3(t,o,i),i},Wn=(e=>(e.small="small",e.regular="regular",e.enhanced="enhanced",e))(Wn||{}),Jl=(e=>(e.top="top",e.bottom="bottom",e))(Jl||{}),b3={small:Sr.small,regular:Sr.small,enhanced:Sr.large},w3={small:kr.xs,regular:kr.s,enhanced:kr.l},Wi=class extends S{constructor(){super(...arguments),this.readouts=[],this.tag=null,this.size="regular",this.idTagOrientation="top"}renderTag(){return this.tag===null?z:f`<div class="tag">${this.tag}</div>`}renderValueContainer(e,t,o){return f`<div class="readout-item ${e}">
      ${t}
      <div class="value-container">
        <div class="label-container">${o}</div>
      </div>
    </div>`}renderValueText(e){return f`<span class="value-text">${e}</span>`}renderNumber(e,t){return f`<obc-readout-block
      class="number"
      .value=${e}
      .size=${b3[this.size]}
      .valueSize=${w3[this.size]}
      .maxDigits=${t.maxDigits??0}
      .fractionDigits=${t.fractionDigits??0}
      .hintedZeros=${t.hintedZeros??!1}
    ></obc-readout-block>`}renderValue(e){let t=z;e.icon=="arrow"?e.direction=="up"?t=f`<obi-arrow-up-google
          class="icon"
          useCssColor
        ></obi-arrow-up-google>`:e.direction=="down"?t=f`<obi-arrow-down-google
          class="icon"
          useCssColor
        ></obi-arrow-down-google>`:e.direction=="left"?t=f`<obi-arrow-left-google
          class="icon"
          useCssColor
        ></obi-arrow-left-google>`:e.direction=="right"&&(t=f`<obi-arrow-right-google
          class="icon"
          useCssColor
        ></obi-arrow-right-google>`):e.icon=="chevron"?e.direction=="up"?t=f`<obi-chevron-double-up-google
          class="icon"
          useCssColor
        ></obi-chevron-double-up-google>`:e.direction=="down"?t=f`<obi-chevron-double-down-google
          class="icon"
          useCssColor
        ></obi-chevron-double-down-google>`:e.direction=="left"?t=f`<obi-chevron-double-left-google
          class="icon"
          useCssColor
        ></obi-chevron-double-left-google>`:e.direction=="right"&&(t=f`<obi-chevron-double-right-google
          class="icon"
          useCssColor
        ></obi-chevron-double-right-google>`):e.icon=="slot"&&e.slotName&&(t=f`<slot class="icon" name=${e.slotName}></slot>`);let o=f`
      ${this.renderNumber(e.value,{maxDigits:e.nDigits,hintedZeros:!0})}
      <span class="unit">${e.unit}</span>
    `;return this.renderValueContainer("value",t,o)}renderSetpoint(e){let t=f`<svg
      class="setpoint-glyph"
      viewBox="2.5 -2.5 21 26"
      aria-hidden="true"
    >
      <path d=${dh} transform="rotate(-90 13 10.5)" />
    </svg>`,o=f`
      ${this.renderNumber(e.value,{maxDigits:e.nDigits,hintedZeros:!0})}
      ${e.unit?f`<span class="unit">${e.unit}</span>`:z}
    `;return this.renderValueContainer("setpoint",t,o)}renderStateOff(e){let t=f``;e.hasIcon&&(t=f`<obi-off class="icon" useCssColor></obi-off>`);let o=this.renderValueText(e.value);return this.renderValueContainer("state-off",t,o)}renderStateOn(e){let t=f``;e.hasIcon&&(t=f`<obi-on class="icon" useCssColor></obi-on>`);let o=this.renderValueText(e.value);return this.renderValueContainer("state-on",t,o)}renderButton(e){let t=f``;e.hasIcon&&(t=f`<obi-temperature-air
        class="icon"
        useCssColor
      ></obi-temperature-air>`);let o=f`
      ${this.renderNumber(e.value,{fractionDigits:1})}
      <span class="unit">${e.unit}</span>
    `;return f`<obc-button class="readout-button" part="readout-button">
      ${this.renderValueContainer("button",t,o)}
    </obc-button>`}renderReadout(e){if(e.type==="value")return this.renderValue(e);if(e.type==="state-on")return this.renderStateOn(e);if(e.type==="state-off")return this.renderStateOff(e);if(e.type==="button")return this.renderButton(e);if(e.type==="setpoint")return this.renderSetpoint(e);throw new Error("Invalid readout type")}render(){let t=this.readouts.filter(i=>i.type==="value"||i.type==="state-off"||i.type==="state-on"||i.type==="button"||i.type==="setpoint").map(i=>this.renderReadout(i)),o=this.renderTag(),r=[];return this.idTagOrientation==="top"?(r.push(o),r.push(...t)):(r.push(...t),r.push(o)),f`<div class="readout-stack ${this.size}">${r}</div>`}};Wi.styles=ne(j2);jn([h({type:Array,attribute:!1})],Wi.prototype,"readouts",2);jn([h({type:String})],Wi.prototype,"tag",2);jn([h()],Wi.prototype,"size",2);jn([h()],Wi.prototype,"idTagOrientation",2);Wi=jn([L("obc-automation-button-readout-stack")],Wi);var A0=M`* {
  -webkit-tap-highlight-color: transparent;
}

:host {
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.circular-progress-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.circular-progress-svg {
  width: 100%;
  height: 100%;
}

.circular-background {
  stroke: var(--container-backdrop-color);
}

.circular-progress {
  stroke: var(--instrument-enhanced-secondary-color);
  transition: stroke-dashoffset 0.3s ease-in-out;
}

.circular-progress.determinate {
  stroke-linecap: round;
}

.circular-progress.indeterminate {
  stroke-linecap: round;
  animation: circular-rotate 1.5s linear infinite;
}

.circular-progress.progressive-indeterminate {
  stroke-linecap: round;
  animation: circular-rotate 1.5s linear infinite;
  transition: stroke-dasharray 0s ease-in-out;
}

@keyframes circular-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
`;var y3=Object.defineProperty,C3=Object.getOwnPropertyDescriptor,Ns=(e,t,o,r)=>{for(var i=r>1?void 0:r?C3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&y3(t,o,i),i},Un=(e=>(e.determinate="determinate",e.indeterminate="indeterminate",e.progressiveIndeterminate="progressive-indeterminate",e))(Un||{}),ei=class extends S{constructor(){super(...arguments),this.mode="indeterminate",this.value=0,this.strokeWidth=4,this.viewBoxSize=42,this.padding=0}render(){let e=this.viewBoxSize,t=this.strokeWidth,o=e/2,r=Math.max(0,(e-t)/2-this.padding),i=2*Math.PI*r,s=Number.isFinite(this.value)?this.value:0,n=x0(s,0,100),a;if(this.mode==="progressive-indeterminate"){let l=i*.02,c=n>=100?i:Math.max(l,n/100*i*.97),d=i-c;a=w`
        <circle
          class="circular-progress progressive-indeterminate"
          cx="${o}"
          cy="${o}"
          r="${r}"
          stroke-width="${t}"
          fill="none"
          stroke-dasharray="${c} ${d}"
          transform-origin="${o} ${o}"
        />
      `}else if(this.mode==="determinate"){let l=n>=100?100:n*.97,c=i-l/100*i;a=w`
        <circle
          class="circular-progress determinate"
          cx="${o}"
          cy="${o}"
          r="${r}"
          stroke-width="${t}"
          fill="none"
          stroke-dasharray="${i}"
          stroke-dashoffset="${c}"
          transform="rotate(-90 ${o} ${o})"
        />
      `}else a=w`
        <circle
          class="circular-progress indeterminate"
          cx="${o}"
          cy="${o}"
          r="${r}"
          stroke-width="${t}"
          fill="none"
          stroke-dasharray="${i*.25} ${i*.75}"
          transform-origin="${o} ${o}"
        />
      `;return f`
      <div class="circular-progress-container">
        <svg
          class="circular-progress-svg"
          viewBox="0 0 ${e} ${e}"
          preserveAspectRatio="xMidYMid meet"
        >
          <circle
            class="circular-background"
            cx="${o}"
            cy="${o}"
            r="${r}"
            stroke-width="${t}"
            fill="none"
          />
          ${a}
        </svg>
      </div>
    `}};ei.styles=ne(A0);Ns([h({type:String})],ei.prototype,"mode",2);Ns([h({type:Number})],ei.prototype,"value",2);Ns([h({type:Number})],ei.prototype,"strokeWidth",2);Ns([h({type:Number})],ei.prototype,"viewBoxSize",2);Ns([h({type:Number})],ei.prototype,"padding",2);ei=Ns([L("obc-circular-progress")],ei);var x3=Object.defineProperty,_3=Object.getOwnPropertyDescriptor,lt=(e,t,o,r)=>{for(var i=r>1?void 0:r?_3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&x3(t,o,i),i};var ec=(e=>(e.closed="closed",e.open="open",e))(ec||{}),Ui=(e=>(e.top="top",e.bottom="bottom",e.left="left",e.right="right",e))(Ui||{}),Gn=(e=>(e.forward="forward",e.forwardFast="forward-fast",e.forwardStopped="forward-stopped",e.backward="backward",e.backwardFast="backward-fast",e.backwardStopped="backward-stopped",e.standby="standby",e))(Gn||{}),Gi=(e=>(e.up="up",e.down="down",e.left="left",e.right="right",e.none="none",e))(Gi||{}),fh=(e=>(e.horizontal="horizontal",e.verticalRight="verticalRight",e.verticalLeft="verticalLeft",e))(fh||{}),gh=(e=>(e.point="point",e.symbol="symbol",e.button="button",e))(gh||{}),Je=class extends S{constructor(){super(...arguments),this.variant="regular",this.state="open",this.static=!1,this.activated=!1,this.showReadoutStack=!0,this.readouts=[],this.tag=null,this.readoutPosition="bottom",this.readoutSize=Wn.regular,this.alert=!1,this.alertFrameType=xr.SmallSideFlip,this.alertFrameThickness=Fi.Small,this.alertFrameStatus=Q.Alarm,this.alertFrameMode=In.ackedActive,this.showAlertCategoryIcon=!0,this.showAlertIcon=!1,this.progress=!1,this.progressMode=Un.indeterminate,this.progressValue=0,this.direction="forward",this.positioning="point",this.orientation="horizontal",this.hasBadgeSpacer=!1}render(){let e=this.effectiveVariant,t=this.showReadoutStack&&(this.readouts.length>0||this.tag!==null);return this.wrapContent(f`
      <button
        class=${de({wrapper:!0,["positioning-"+this.positioning]:!0,["variant-"+e]:!0,["state-"+this.state]:!0,"label-empty":!t,["label-"+this.readoutPosition]:!0,"has-badge-spacer":this.hasBadgeSpacer,alert:this.alert,progress:this.progress,static:this.static,activated:this.activated})}
      >
        <div class="icon-touch-target">
          ${this.renderIconHolder()}
          <div class="badge-top-right">
            <slot name="badge-top-right"></slot>
          </div>
          <div class="badge-top-left">
            <slot name="badge-top-left"></slot>
          </div>
          <div class="badge-bottom-left">
            <slot name="badge-bottom-left"></slot>
          </div>
          <div class="badge-bottom-right">
            <slot name="badge-bottom-right"></slot>
          </div>
        </div>
        ${this.showReadoutStack?f`
              <div class="badge-spacer"></div>
              <obc-automation-button-readout-stack
                .readouts=${this.readouts}
                .tag=${this.tag}
                .size=${this.readoutSize}
                .idTagOrientation=${this.getIdTagOrientation()}
              ></obc-automation-button-readout-stack>
            `:z}
        ${this.alert&&this.positioning==="point"?f` <obc-alert-frame
              class="alert-frame"
              .type=${this.alertFrameType}
              .thickness=${this.alertFrameThickness}
              .status=${this.alertFrameStatus}
              .mode=${this.alertFrameMode}
              .showAlertCategoryIcon=${this.showAlertCategoryIcon}
              .showIcon=${this.showAlertIcon}
            >
              <span slot="icon"><slot name="alert-icon"></slot></span>
              <span slot="label"><slot name="alert-label"></slot></span>
              <span slot="timer"><slot name="alert-timer"></slot></span>
            </obc-alert-frame>`:z}
      </button>
    `)}wrapContent(e){if(this.positioning==="point")return f`<div class="point-wrapper">${e}</div>`;let t=Al(this.alert?{type:this.alertFrameType,thickness:this.alertFrameThickness,status:this.alertFrameStatus,mode:this.alertFrameMode,showIcon:this.showAlertIcon,showAlertCategoryIcon:this.showAlertCategoryIcon}:!1,e);return this.positioning==="symbol"?f`<div
        class=${de({"symbol-wrapper":!0,["label-"+this.readoutPosition]:!0})}
      >
        ${t}
      </div> `:t}get effectiveVariant(){return this.progress?"regular":this.variant}renderIconHolder(){let e=this.effectiveVariant,t=this.getProgressRing(),o=de({"icon-holder":!0,["orientation-"+this.orientation]:!0});if(this.variant==="flat-forward")return f`<div class=${o}>
        ${this.getDirectionIcon(e,"icon-primary")}
        ${this.getDirectionIcon(e,"icon-silhouette")}
        ${t}
      </div>`;if(this.variant==="forward")return f`<div class=${o}>
        ${this.getDirectionIcon(e,"icon-primary")}
        ${t}
      </div>`;let r=this.getDirectionIcon(e),i=["regular","double","flat","square"].includes(e);return f`<div class=${o}>
      ${r}
      ${i?f`<div class="icon-primary">
              <slot name="icon"></slot>
            </div>
            ${e==="flat"?f` <div class="icon-silhouette">
                  <slot name="icon-silhouette"></slot>
                </div>`:z} `:z}
      ${t}
    </div>`}getProgressRing(){return this.progress?f`<obc-circular-progress
      class="progress-ring"
      .mode=${this.progressMode}
      .value=${this.progressValue}
    ></obc-circular-progress>`:null}getDirectionIcon(e,t="icon-direction"){if(["double","forward","flat-forward"].includes(e)){if(this.direction==="forward")return f`<svg
        class="${t}"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M8 5 v 14 L 20 12Z"
          stroke="var(--automation-device-tertiary-color)"
          fill="var(--automation-device-primary-color)"
          vector-effect="non-scaling-stroke"
        />
      </svg> `;if(this.direction==="forward-fast")return f`<svg
        class="${t}"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M3.5 5 v 14 l 8.5 -7 Z M14.5 5 v 14 l 8.5 -7 Z"
          stroke="var(--automation-device-tertiary-color)"
          fill="var(--automation-device-primary-color)"
          vector-effect="non-scaling-stroke"
        />
      </svg> `;if(this.direction==="forward-stopped")return f`<svg
        class="${t}"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M8 5 v 14 L 20 12Z"
          fill="var(--automation-device-tertiary-color)"
          stroke="var(--automation-device-tertiary-inverted-color)"
          vector-effect="non-scaling-stroke"
        />
      </svg> `;if(this.direction==="backward")return f`<svg
        class="${t}"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M16 5 v 14 L 4 12Z"
          stroke="var(--automation-device-tertiary-color)"
          fill="var(--automation-device-primary-color)"
          vector-effect="non-scaling-stroke"
        />
      </svg>`;if(this.direction==="backward-fast")return f`<svg
        class="${t}"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M20.5 5 v 14 l -8.5 -7 Z M9.5 5 v 14 l -8.5 -7 Z"
          stroke="var(--automation-device-tertiary-color)"
          fill="var(--automation-device-primary-color)"
          vector-effect="non-scaling-stroke"
        />
      </svg>`;if(this.direction==="backward-stopped")return f`<svg
        class="${t}"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M16 5 v 14 L 4 12Z"
          fill="var(--automation-device-tertiary-color)"
          stroke="var(--automation-device-tertiary-inverted-color)"
          vector-effect="non-scaling-stroke"
        />
      </svg> `;if(this.direction==="standby")return f`<obi-standby class="${t}" usecsscolor></obi-standby>`}else return z;throw new Error("Invalid direction")}getIdTagOrientation(){return this.readoutPosition==="top"?Jl.top:Jl.bottom}};Je.styles=ne(m2);lt([h({type:String})],Je.prototype,"variant",2);lt([h({type:String})],Je.prototype,"state",2);lt([h({type:Boolean})],Je.prototype,"static",2);lt([h({type:Boolean})],Je.prototype,"activated",2);lt([h({type:Boolean,attribute:!1})],Je.prototype,"showReadoutStack",2);lt([h({type:Array,attribute:!1})],Je.prototype,"readouts",2);lt([h({type:String})],Je.prototype,"tag",2);lt([h({type:String})],Je.prototype,"readoutPosition",2);lt([h({type:String})],Je.prototype,"readoutSize",2);lt([h({type:Boolean})],Je.prototype,"alert",2);lt([h({type:String})],Je.prototype,"alertFrameType",2);lt([h({type:String})],Je.prototype,"alertFrameThickness",2);lt([h({type:String})],Je.prototype,"alertFrameStatus",2);lt([h({type:String})],Je.prototype,"alertFrameMode",2);lt([h({type:Boolean,attribute:!1})],Je.prototype,"showAlertCategoryIcon",2);lt([h({type:Boolean})],Je.prototype,"showAlertIcon",2);lt([h({type:Boolean})],Je.prototype,"progress",2);lt([h({type:String})],Je.prototype,"progressMode",2);lt([h({type:Number})],Je.prototype,"progressValue",2);lt([h({type:String})],Je.prototype,"direction",2);lt([h({type:String})],Je.prototype,"positioning",2);lt([h({type:String})],Je.prototype,"orientation",2);lt([h({type:Boolean})],Je.prototype,"hasBadgeSpacer",2);Je=lt([L("obc-automation-button")],Je);var P0=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

.wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--automation-components-badge-new-size);
  height: var(--automation-components-badge-new-size);
  border-radius: var(--automation-components-badge-new-border-radius);
}

.wrapper .badge {
    position: relative;
  }

.wrapper ::slotted([slot="icon-silhouette"]),.wrapper .icon.siluette {
    stroke-width: 2px;
    stroke: var(--border-silhouette-color);
    /* TODO: replace the typo 'siluette' with 'silhouette', probably in Figma as well */
  }

.wrapper:not(.flat) ::slotted([slot="icon-silhouette"]),.wrapper:not(.flat) .icon.siluette {
    display: none;
    /* TODO: replace the typo 'siluette' with 'silhouette', probably in Figma as well */
  }

.wrapper ::slotted(*),.wrapper .icon {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
  }

.wrapper.flat .badge {
    width: var(--automation-components-badge-new-icon-size-flat);
    height: var(--automation-components-badge-new-icon-size-flat);
    color: var(--element-neutral-color);
  }

.wrapper.regular {
  border-color: var(--normal-enabled-border-color);
  background-color: var(--normal-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--normal-enabled-border-color);
  --base-background-color: var(--normal-enabled-background-color);
    color: var(--element-neutral-color);
}

.wrapper.regular .badge {
      width: var(--automation-components-badge-new-icon-size);
      height: var(--automation-components-badge-new-icon-size);
    }

.wrapper.enhanced {
  border-color: var(--raised-enabled-border-color);
  background-color: var(--raised-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--raised-enabled-border-color);
  --base-background-color: var(--raised-enabled-background-color);
    color: var(--element-active-inverted-color);
}

.wrapper.enhanced .badge {
      width: var(--automation-components-badge-new-icon-size);
      height: var(--automation-components-badge-new-icon-size);
    }
`;var k3=Object.defineProperty,L3=Object.getOwnPropertyDescriptor,O0=(e,t,o,r)=>{for(var i=r>1?void 0:r?L3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&k3(t,o,i),i},tc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.5875 21.4125C10.9792 21.8042 11.45 22 12 22C12.55 22 13.0209 21.8042 13.4125 21.4125C13.8042 21.0208 14 20.55 14 20H10C10 20.55 10.1959 21.0208 10.5875 21.4125Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 15.15V10C18 8.61667 17.5834 7.3875 16.75 6.3125C15.9167 5.2375 14.8334 4.53333 13.5 4.2V3.5C13.5 3.08333 13.3542 2.72917 13.0625 2.4375C12.7709 2.14583 12.4167 2 12 2C11.5834 2 11.2292 2.14583 10.9375 2.4375C10.6459 2.72917 10.5 3.08333 10.5 3.5V4.2C10.0667 4.3 9.65836 4.45 9.27502 4.65C8.89169 4.85 8.53336 5.08333 8.20003 5.35L18 15.15Z" fill="currentColor"/>
<path d="M1.40002 4.2L6.09697 8.89694C6.03234 9.26083 6.00002 9.62851 6.00002 10V17H4.00002V19H16.15L19.8 22.6L21.2 21.2L2.80002 2.8L1.40002 4.2Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.5875 21.4125C10.9792 21.8042 11.45 22 12 22C12.55 22 13.0209 21.8042 13.4125 21.4125C13.8042 21.0208 14 20.55 14 20H10C10 20.55 10.1959 21.0208 10.5875 21.4125Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 15.15V10C18 8.61667 17.5834 7.3875 16.75 6.3125C15.9167 5.2375 14.8334 4.53333 13.5 4.2V3.5C13.5 3.08333 13.3542 2.72917 13.0625 2.4375C12.7709 2.14583 12.4167 2 12 2C11.5834 2 11.2292 2.14583 10.9375 2.4375C10.6459 2.72917 10.5 3.08333 10.5 3.5V4.2C10.0667 4.3 9.65836 4.45 9.27502 4.65C8.89169 4.85 8.53336 5.08333 8.20003 5.35L18 15.15Z" style="fill: var(--element-active-color)"/>
<path d="M1.40002 4.2L6.09697 8.89694C6.03234 9.26083 6.00002 9.62851 6.00002 10V17H4.00002V19H16.15L19.8 22.6L21.2 21.2L2.80002 2.8L1.40002 4.2Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};tc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;O0([h({type:Boolean})],tc.prototype,"useCssColor",2);tc=O0([L("obi-alert-off-filled")],tc);var S3=Object.defineProperty,M3=Object.getOwnPropertyDescriptor,V0=(e,t,o,r)=>{for(var i=r>1?void 0:r?M3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&S3(t,o,i),i},oc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M9.42846 3L3 20.9997H7.49992L8.94642 17.1426H15.0548L16.5013 20.9997H21.0012L14.5728 3H9.42846ZM12.0006 8.99864L10.3929 13.2855H13.6083L12.0006 8.99864Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M9.42846 3L3 20.9997H7.49992L8.94642 17.1426H15.0548L16.5013 20.9997H21.0012L14.5728 3H9.42846ZM12.0006 8.99864L10.3929 13.2855H13.6083L12.0006 8.99864Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};oc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;V0([h({type:Boolean})],oc.prototype,"useCssColor",2);oc=V0([L("obi-auto")],oc);var $3=Object.defineProperty,A3=Object.getOwnPropertyDescriptor,T0=(e,t,o,r)=>{for(var i=r>1?void 0:r?A3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&$3(t,o,i),i},rc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M5.75 3L2 21H6.44325L8.12573 12.7744L10.125 21H13.875L15.8942 12.6923L17.625 21H22L18.25 3H13.875L12 12L10.125 3H5.75Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M5.75 3L2 21H6.44325L8.12573 12.7744L10.125 21H13.875L15.8942 12.6923L17.625 21H22L18.25 3H13.875L12 12L10.125 3H5.75Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};rc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;T0([h({type:Boolean})],rc.prototype,"useCssColor",2);rc=T0([L("obi-manual")],rc);var P3=Object.defineProperty,O3=Object.getOwnPropertyDescriptor,D0=(e,t,o,r)=>{for(var i=r>1?void 0:r?O3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&P3(t,o,i),i},ic=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M6.375 2L3 17.5556H6.99893L8.51315 10.447L10.3125 17.5556H13.6875L15.5048 10.3761L17.0625 17.5556H21L17.625 2H13.6875L12 9.77778L10.3125 2H6.375Z" fill="currentColor"/>
<path d="M3 19.7778H21V22H3V19.7778Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M6.375 2L3 17.5556H6.99893L8.51315 10.447L10.3125 17.5556H13.6875L15.5048 10.3761L17.0625 17.5556H21L17.625 2H13.6875L12 9.77778L10.3125 2H6.375Z" style="fill: var(--element-active-color)"/>
<path d="M3 19.7778H21V22H3V19.7778Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ic.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;D0([h({type:Boolean})],ic.prototype,"useCssColor",2);ic=D0([L("obi-manual-only")],ic);var V3=Object.defineProperty,T3=Object.getOwnPropertyDescriptor,E0=(e,t,o,r)=>{for(var i=r>1?void 0:r?T3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&V3(t,o,i),i},sc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M5 3V21H19V16.5H9.66667V3H5Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M5 3V21H19V16.5H9.66667V3H5Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};sc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;E0([h({type:Boolean})],sc.prototype,"useCssColor",2);sc=E0([L("obi-local")],sc);var D3=Object.defineProperty,E3=Object.getOwnPropertyDescriptor,R0=(e,t,o,r)=>{for(var i=r>1?void 0:r?E3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&D3(t,o,i),i},nc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M6 3V17H18V13H10V3H6Z" fill="currentColor"/>
<path d="M6 19H18V21H6V19Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M6 3V17H18V13H10V3H6Z" style="fill: var(--element-active-color)"/>
<path d="M6 19H18V21H6V19Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};nc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;R0([h({type:Boolean})],nc.prototype,"useCssColor",2);nc=R0([L("obi-local-only")],nc);var R3=Object.defineProperty,z3=Object.getOwnPropertyDescriptor,z0=(e,t,o,r)=>{for(var i=r>1?void 0:r?z3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&R3(t,o,i),i},ac=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 21H10V3H14V21Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 21H10V3H14V21Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ac.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;z0([h({type:Boolean})],ac.prototype,"useCssColor",2);ac=z0([L("obi-duty")],ac);var H3=Object.defineProperty,B3=Object.getOwnPropertyDescriptor,H0=(e,t,o,r)=>{for(var i=r>1?void 0:r?B3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&H3(t,o,i),i},lc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 8H17V6C17 3.24 14.76 1 12 1C9.24 1 7 3.24 7 6V8H6C4.9 8 4 8.9 4 10V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V10C20 8.9 19.1 8 18 8ZM9 6C9 4.34 10.34 3 12 3C13.66 3 15 4.34 15 6V8H9V6ZM14 15C14 16.1 13.1 17 12 17C10.9 17 10 16.1 10 15C10 13.9 10.9 13 12 13C13.1 13 14 13.9 14 15Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 8H17V6C17 3.24 14.76 1 12 1C9.24 1 7 3.24 7 6V8H6C4.9 8 4 8.9 4 10V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V10C20 8.9 19.1 8 18 8ZM9 6C9 4.34 10.34 3 12 3C13.66 3 15 4.34 15 6V8H9V6ZM14 15C14 16.1 13.1 17 12 17C10.9 17 10 16.1 10 15C10 13.9 10.9 13 12 13C13.1 13 14 13.9 14 15Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};lc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;H0([h({type:Boolean})],lc.prototype,"useCssColor",2);lc=H0([L("obi-command-locked-f")],lc);var I3=Object.defineProperty,Z3=Object.getOwnPropertyDescriptor,mh=(e,t,o,r)=>{for(var i=r>1?void 0:r?Z3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&I3(t,o,i),i};var Ae=(e=>(e.Auto="auto",e.Manual="manual",e.ManualOnly="manual-only",e.Local="local",e.LocalOnly="local-only",e.CommandLocked="command-locked",e.Interlock="interlock",e.InterlockInhibit="interlock-inhibit",e.AlertSilenced="alert-silenced",e.Caution="caution",e.Warning="warning",e.Alarm="alarm",e.LevelCritical="level-critical",e.LevelHigh="level-high",e.LevelMedium="level-medium",e.LevelLow="level-low",e.LevelDiagnostic="level-diagnostic",e))(Ae||{}),F3=["caution","warning","alarm","level-critical","level-high","level-medium","level-low","level-diagnostic"],Yn=class extends S{constructor(){super(...arguments),this.mode="flat",this.type=void 0}get effectiveMode(){return this.type&&F3.includes(this.type)?"flat":this.mode}isAlertType(...e){return!!this.type&&e.includes(this.type)}renderLevelCriticalIcon(e){return e?f`<svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M14.667 8L11.3337 13.77H4.66634L1.33301 8L4.66634 2.23H11.3337L14.667 8Z"
          fill="var(--critical-enabled-background-color)"
        />
        <path
          d="M11.1543 2.72998H4.8457L2.51237 7.99998L4.8457 13.27H11.1543L13.4876 7.99998L11.1543 2.72998Z"
          stroke="var(--critical-enabled-border-color)"
        />
        <path
          d="M7.66754 10.3343V5.00098H9.00087V10.3343H7.66754Z"
          fill="var(--on-critical-active-color)"
        />
        <path
          d="M9.00087 11.6676H7.66754V13.001H9.00087V11.6676Z"
          fill="var(--on-critical-active-color)"
        />
      </svg>`:f`<svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
        fill="var(--critical-enabled-background-color)"
      />
      <path
        d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
        stroke="var(--critical-enabled-border-color)"
      />
      <path
        d="M14 8L10.9282 13.33H5.0718L2 8L5.0718 2.67H10.9282L14 8Z"
        fill="var(--on-critical-active-color)"
      />
    </svg>`}renderLevelDiagnosticIcon(){return f`<svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M7 1.33301H9V7.53301L13.2147 5.13301L14.2147 6.86634L10 9.33301L14.2147 11.7997L13.2147 13.533L9 11.133V15.667H7V11.133L2.78534 13.533L1.78534 11.7997L6 9.33301L1.78534 6.86634L2.78534 5.13301L7 7.53301V1.33301Z"
        fill="var(--notification-enabled-background-color)"
      />
    </svg>`}getIcon(){return this.type==="auto"?f`<obi-auto class="icon siluette"></obi-auto
        ><obi-auto class="icon"></obi-auto>`:this.type==="manual"?f`<obi-manual class="icon siluette"></obi-manual
        ><obi-manual class="icon"></obi-manual>`:this.type==="manual-only"?f`<obi-manual-only class="icon siluette"></obi-manual-only
        ><obi-manual-only class="icon"></obi-manual-only>`:this.type==="local"?f`<obi-local class="icon siluette"></obi-local
        ><obi-local class="icon"></obi-local>`:this.type==="local-only"?f`<obi-local-only class="icon siluette"></obi-local-only
        ><obi-local-only class="icon"></obi-local-only>`:this.type==="command-locked"?f`<obi-command-locked-f
          class="icon siluette"
        ></obi-command-locked-f
        ><obi-command-locked-f class="icon"></obi-command-locked-f>`:this.type==="interlock-inhibit"?f`<obi-standby class="icon siluette"></obi-standby
        ><obi-standby class="icon"></obi-standby>`:this.type==="interlock"?f`<obi-duty class="icon siluette"></obi-duty
        ><obi-duty class="icon"></obi-duty>`:this.type==="alert-silenced"?f`<obi-alert-off-filled
          class="icon siluette"
        ></obi-alert-off-filled
        ><obi-alert-off-filled class="icon"></obi-alert-off-filled>`:this.type==="level-critical"?this.renderLevelCriticalIcon(this.effectiveMode==="flat"):this.type==="level-diagnostic"?this.renderLevelDiagnosticIcon():this.isAlertType("caution","level-low")&&this.effectiveMode==="flat"?f`<svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <mask
          id="path-2-outside-1_37206_122649"
          maskUnits="userSpaceOnUse"
          x="0.333008"
          y="0.333008"
          width="16"
          height="16"
          fill="black"
        >
          <rect fill="white" x="0.333008" y="0.333008" width="16" height="16" />
          <path
            d="M13.333 1.33301C14.0694 1.33301 14.667 1.93061 14.667 2.66699V13.333C14.667 14.0694 14.0694 14.667 13.333 14.667H2.66699C1.93061 14.667 1.33301 14.0694 1.33301 13.333V2.66699C1.33301 1.93061 1.93061 1.33301 2.66699 1.33301H13.333Z"
          />
        </mask>
        <path
          d="M13.333 1.33301V2.33301C13.5171 2.33301 13.667 2.4829 13.667 2.66699H14.667H15.667C15.667 1.37833 14.6217 0.333008 13.333 0.333008V1.33301ZM14.667 2.66699H13.667V13.333H14.667H15.667V2.66699H14.667ZM14.667 13.333H13.667C13.667 13.5171 13.5171 13.667 13.333 13.667V14.667V15.667C14.6217 15.667 15.667 14.6217 15.667 13.333H14.667ZM13.333 14.667V13.667H2.66699V14.667V15.667H13.333V14.667ZM2.66699 14.667V13.667C2.4829 13.667 2.33301 13.5171 2.33301 13.333H1.33301H0.333008C0.333008 14.6217 1.37833 15.667 2.66699 15.667V14.667ZM1.33301 13.333H2.33301V2.66699H1.33301H0.333008V13.333H1.33301ZM1.33301 2.66699H2.33301C2.33301 2.4829 2.4829 2.33301 2.66699 2.33301V1.33301V0.333008C1.37833 0.333008 0.333008 1.37833 0.333008 2.66699H1.33301ZM2.66699 1.33301V2.33301H13.333V1.33301V0.333008H2.66699V1.33301Z"
          fill="var(--border-silhouette-color)"
          mask="url(#path-2-outside-1_37206_122649)"
        />
        <path
          fill-rule="evenodd"
          clip-rule="evenodd"
          d="M2.66665 1.33301C1.93027 1.33301 1.33331 1.92996 1.33331 2.66634V13.333C1.33331 14.0694 1.93027 14.6663 2.66665 14.6663H13.3333C14.0697 14.6663 14.6666 14.0694 14.6666 13.333V2.66634C14.6666 1.92996 14.0697 1.33301 13.3333 1.33301H2.66665Z"
          fill="var(--alert-caution-color)"
        />
        <path
          d="M2.66632 1.83301H13.3333C13.7934 1.83301 14.1661 2.20593 14.1663 2.66602V13.333C14.1663 13.7932 13.7936 14.166 13.3333 14.166H2.66632C2.20623 14.1658 1.83331 13.7931 1.83331 13.333V2.66602C1.83348 2.2347 2.16127 1.8796 2.58136 1.83691L2.66632 1.83301Z"
          stroke="var(--alert-caution-outline-color)"
        />
        <path
          d="M7.33331 9.33333V4H8.66665V9.33333H7.33331Z"
          fill="var(--on-caution-active-color)"
        />
        <path
          d="M8.66665 10.6667H7.33331V12H8.66665V10.6667Z"
          fill="var(--on-caution-active-color)"
        />
      </svg>`:this.isAlertType("caution","level-low")?f`<svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
          fill="var(--alert-caution-color)"
        />
        <path
          d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
          stroke="var(--alert-caution-outline-color)"
        />
        <path
          d="M3.5 4.3C3.5 4.01997 3.5 3.87996 3.5545 3.773C3.60243 3.67892 3.67892 3.60243 3.773 3.5545C3.87996 3.5 4.01997 3.5 4.3 3.5H11.7C11.98 3.5 12.12 3.5 12.227 3.5545C12.3211 3.60243 12.3976 3.67892 12.4455 3.773C12.5 3.87996 12.5 4.01997 12.5 4.3V11.7C12.5 11.98 12.5 12.12 12.4455 12.227C12.3976 12.3211 12.3211 12.3976 12.227 12.4455C12.12 12.5 11.98 12.5 11.7 12.5H4.3C4.01997 12.5 3.87996 12.5 3.773 12.4455C3.67892 12.3976 3.60243 12.3211 3.5545 12.227C3.5 12.12 3.5 11.98 3.5 11.7V4.3Z"
          fill="var(--on-caution-active-color)"
        />
      </svg> `:this.isAlertType("warning","level-medium")&&this.effectiveMode==="flat"?f`
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <mask
            id="path-2-outside-1_37206_122675"
            maskUnits="userSpaceOnUse"
            x="0.333008"
            y="0.333008"
            width="16"
            height="16"
            fill="black"
          >
            <rect
              fill="white"
              x="0.333008"
              y="0.333008"
              width="16"
              height="16"
            />
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M8 1.33301C11.6819 1.33301 14.667 4.3181 14.667 8C14.667 11.6819 11.6819 14.667 8 14.667C4.3181 14.667 1.33301 11.6819 1.33301 8C1.33301 4.3181 4.3181 1.33301 8 1.33301Z"
            />
          </mask>
          <path
            d="M8 1.33301V0.333008V0.333008V1.33301ZM14.667 8H15.667V8H14.667ZM8 14.667V15.667V15.667V14.667ZM1.33301 8H0.333008V8H1.33301ZM8 1.33301V2.33301C11.1296 2.33301 13.667 4.87039 13.667 8H14.667H15.667C15.667 3.76582 12.2342 0.333008 8 0.333008V1.33301ZM14.667 8H13.667C13.667 11.1296 11.1296 13.667 8 13.667V14.667V15.667C12.2342 15.667 15.667 12.2342 15.667 8H14.667ZM8 14.667V13.667C4.87039 13.667 2.33301 11.1296 2.33301 8H1.33301H0.333008C0.333008 12.2342 3.76582 15.667 8 15.667V14.667ZM1.33301 8H2.33301C2.33301 4.87039 4.87039 2.33301 8 2.33301V1.33301V0.333008C3.76582 0.333008 0.333008 3.76582 0.333008 8H1.33301Z"
            fill="var(--border-silhouette-color)"
            mask="url(#path-2-outside-1_37206_122675)"
          />
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M14.6666 7.99967C14.6666 11.6816 11.6819 14.6663 7.99998 14.6663C4.31808 14.6663 1.33331 11.6816 1.33331 7.99967C1.33331 4.31778 4.31808 1.33301 7.99998 1.33301C11.6819 1.33301 14.6666 4.31778 14.6666 7.99967Z"
            fill="var(--alert-warning-color)"
          />
          <path
            d="M8.00031 1.83301C11.4059 1.83318 14.1663 4.59435 14.1663 8C14.1661 11.4055 11.4058 14.1658 8.00031 14.166C4.59466 14.166 1.83349 11.4056 1.83331 8C1.83331 4.59424 4.59455 1.83301 8.00031 1.83301Z"
            stroke="var(--alert-warning-outline-color)"
          />
          <path
            d="M8.66665 8.66699V4.66699H7.33331V8.66699H8.66665Z"
            fill="var(--on-warning-active-color)"
          />
          <path
            d="M8.66665 11.3337V10.0003H7.33331V11.3337H8.66665Z"
            fill="var(--on-warning-active-color)"
          />
        </svg>
      `:this.isAlertType("warning","level-medium")?f`<svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
          fill="var(--alert-warning-color)"
        />
        <path
          d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
          stroke="var(--alert-warning-outline-color)"
        />
        <circle cx="8" cy="8" r="5" fill="var(--on-warning-active-color)" />
      </svg> `:this.isAlertType("alarm","level-high")&&this.effectiveMode==="flat"?f`<svg
        width="16"
        height="16"
        viewBox="0.5 0.5 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <mask
          id="path-2-outside-1_37206_122701"
          maskUnits="userSpaceOnUse"
          x="-0.998657"
          y="0"
          width="18"
          height="17"
          fill="black"
        >
          <rect fill="white" x="-0.998657" width="18" height="17" />
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M7.74502 1.35587C7.99509 0.881431 8.67474 0.881322 8.9247 1.35587L15.5897 14.0229C15.8233 14.4669 15.5015 15.0004 14.9999 15.0004H1.66884C1.16718 15.0004 0.845307 14.4669 1.079 14.0229L7.74502 1.35587Z"
          />
        </mask>
        <path
          d="M7.74502 1.35587L6.86038 0.889586L6.86007 0.89017L7.74502 1.35587ZM8.9247 1.35587L9.80967 0.890223L9.80947 0.889831L8.9247 1.35587ZM15.5897 14.0229L16.4748 13.5573L16.4747 13.5572L15.5897 14.0229ZM1.079 14.0229L1.96393 14.4886L1.96394 14.4886L1.079 14.0229ZM7.74502 1.35587L8.62965 1.82216C8.50484 2.05895 8.16519 2.0597 8.03994 1.82191L8.9247 1.35587L9.80947 0.889831C9.18429 -0.297052 7.48534 -0.296087 6.86038 0.889586L7.74502 1.35587ZM8.9247 1.35587L8.03973 1.82152L14.7048 14.4885L15.5897 14.0229L16.4747 13.5572L9.80967 0.890223L8.9247 1.35587ZM15.5897 14.0229L14.7047 14.4884C14.5885 14.2675 14.7481 14.0004 14.9999 14.0004V15.0004V16.0004C16.255 16.0004 17.0582 14.6663 16.4748 13.5573L15.5897 14.0229ZM14.9999 15.0004V14.0004H1.66884V15.0004V16.0004H14.9999V15.0004ZM1.66884 15.0004V14.0004C1.92039 14.0004 2.08037 14.2673 1.96393 14.4886L1.079 14.0229L0.194074 13.5571C-0.389754 14.6665 0.413976 16.0004 1.66884 16.0004V15.0004ZM1.079 14.0229L1.96394 14.4886L8.62996 1.82157L7.74502 1.35587L6.86007 0.89017L0.194059 13.5572L1.079 14.0229Z"
          fill="var(--border-silhouette-color)"
          mask="url(#path-2-outside-1_37206_122701)"
        />
        <path
          d="M1.07857 14.0235L7.74479 1.35716C7.99473 0.882236 8.6746 0.882252 8.92453 1.35719L15.5899 14.0236C15.8236 14.4676 15.5017 15.001 15.0001 15.001L1.66843 15.001C1.16677 15.001 0.844878 14.4676 1.07857 14.0235Z"
          fill="var(--alert-alarm-color)"
        />
        <path
          d="M8.18744 1.58984C8.25002 1.47134 8.41991 1.4712 8.48236 1.58984L15.1474 14.2568C15.2057 14.3681 15.125 14.501 14.9999 14.501H1.66888C1.54379 14.501 1.46302 14.3681 1.52142 14.2568L8.18744 1.58984Z"
          stroke="var(--alert-alarm-outline-color)"
        />
        <path
          d="M7.66754 10.3343V5.00098H9.00087V10.3343H7.66754Z"
          fill="var(--on-alarm-active-color)"
        />
        <path
          d="M9.00087 11.6676H7.66754V13.001H9.00087V11.6676Z"
          fill="var(--on-alarm-active-color)"
        />
      </svg> `:this.isAlertType("alarm","level-high")?f`
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
            fill="var(--alert-alarm-color)"
          />
          <path
            d="M2 0.5H14C14.8284 0.5 15.5 1.17157 15.5 2V14C15.5 14.8284 14.8284 15.5 14 15.5H2C1.17157 15.5 0.5 14.8284 0.5 14V2C0.5 1.17157 1.17157 0.5 2 0.5Z"
            stroke="var(--alert-alarm-outline-color)"
          />
          <path
            d="M7.29883 3.72622L3.05891 11.3269C2.84063 11.7182 2.73149 11.9139 2.75 12.0741C2.76615 12.2138 2.84042 12.3403 2.9546 12.4225C3.08546 12.5167 3.30949 12.5167 3.75756 12.5167H12.2348C12.6828 12.5167 12.9068 12.5167 13.0376 12.4225C13.1518 12.3403 13.2261 12.2139 13.2422 12.0741C13.2608 11.914 13.1517 11.7184 12.9336 11.3271L8.69623 3.7264C8.46805 3.31712 8.35396 3.11247 8.2037 3.04447C8.07271 2.98519 7.92254 2.98517 7.79153 3.04442C7.64125 3.11238 7.52711 3.317 7.29883 3.72622Z"
            fill="var(--on-alarm-active-color)"
          />
        </svg>
      `:f`<slot name="icon-silhouette"></slot><slot></slot>`}render(){return f`
      <div class=${de({wrapper:!0,[this.effectiveMode]:!0})}>
        <div class="badge">${this.getIcon()}</div>
      </div>
    `}};Yn.styles=ne(P0);mh([h({type:String})],Yn.prototype,"mode",2);mh([h({type:String})],Yn.prototype,"type",2);Yn=mh([L("obc-automation-badge")],Yn);var N3=Object.defineProperty,it=(e,t,o,r)=>{for(var i=void 0,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=n(t,o,i)||i);return i&&N3(t,o,i),i},Ho=(e=>(e.None="none",e.Silence="silence",e.Caution="caution",e.Warning="warning",e.Alarm="alarm",e.LevelCritical="level-critical",e.LevelHigh="level-high",e.LevelMedium="level-medium",e.LevelLow="level-low",e.LevelDiagnostic="level-diagnostic",e))(Ho||{}),qn=(e=>(e.None="none",e.Interlock="interlock",e.InterlockInhibit="interlock-inhibit",e))(qn||{}),ti=(e=>(e.None="none",e.Local="local",e.LocalOnly="local-only",e.Manual="manual",e.ManualOnly="manual-only",e.Auto="auto",e))(ti||{}),cc=(e=>(e.None="none",e.CommandLocked="command-locked",e))(cc||{}),Te=class extends S{constructor(){super(...arguments),this.showReadoutStack=!0,this.readoutPosition=Ui.bottom,this.showStatus=!0,this.readoutSize=Wn.regular,this.tag=null,this.positioning=gh.point,this.activated=!1,this.alert=!1,this.alertFrameType=xr.SmallSideFlip,this.alertFrameThickness=Fi.Small,this.alertFrameStatus=Q.Alarm,this.alertFrameMode=In.ackedActive,this.showAlertCategoryIcon=!0,this.showAlertIcon=!1,this.progress=!1,this.progressMode=Un.indeterminate,this.progressValue=0,this.badgeControl="none",this.badgeCommandLocked="none",this.badgeInterlock="none",this.badgeAlert="none"}get icon(){throw new Error('Method "icon" must be implemented in subclass')}get _on(){throw new Error('Method "_on" must be implemented in subclass')}get _variant(){return this.variant}get _orientation(){return fh.horizontal}get _direction(){return"direction"in this?this.direction:Gn.forward}get extraReadouts(){return[]}getBadgeSpacer(){if(!this.showReadoutStack)return!1;let t=this.badgeTopLeft.length>0||this.getBadgeControlType()!==null,o=this.badgeTopRight.length>0||this.getBadgeAlertType()!==null,r=this.badgeBottomLeft.length>0||this.getBadgeInterlockType()!==null,i=this.badgeBottomRight.length>0||this.getBadgeCommandLockedType()!==null;return this.readoutPosition===Ui.top?o||t:this.readoutPosition===Ui.bottom?r||i:this.readoutPosition===Ui.left?t||r:this.readoutPosition===Ui.right?o||i:!1}handleBadgeSlotChange(){this.requestUpdate()}getBadgeAlertType(){return this.badgeAlert==="silence"?Ae.AlertSilenced:this.badgeAlert==="caution"?Ae.Caution:this.badgeAlert==="warning"?Ae.Warning:this.badgeAlert==="alarm"?Ae.Alarm:this.badgeAlert==="level-critical"?Ae.LevelCritical:this.badgeAlert==="level-high"?Ae.LevelHigh:this.badgeAlert==="level-medium"?Ae.LevelMedium:this.badgeAlert==="level-low"?Ae.LevelLow:this.badgeAlert==="level-diagnostic"?Ae.LevelDiagnostic:null}getBadgeControlType(){return this.badgeControl==="local"?Ae.Local:this.badgeControl==="local-only"?Ae.LocalOnly:this.badgeControl==="manual"?Ae.Manual:this.badgeControl==="manual-only"?Ae.ManualOnly:this.badgeControl==="auto"?Ae.Auto:null}getBadgeInterlockType(){return this.badgeInterlock==="interlock"?Ae.Interlock:this.badgeInterlock==="interlock-inhibit"?Ae.InterlockInhibit:null}getBadgeCommandLockedType(){return this.badgeCommandLocked==="command-locked"?Ae.CommandLocked:null}render(){let t=[...this.extraReadouts],o=this.getBadgeAlertType(),r=this.getBadgeControlType(),i=this.getBadgeInterlockType(),s=this.getBadgeCommandLockedType();return f`<obc-automation-button
      .state=${this._on?ec.open:ec.closed}
      .readouts=${t}
      .tag=${this.tag}
      .showReadoutStack=${this.showReadoutStack}
      .readoutPosition=${this.readoutPosition}
      .readoutSize=${this.readoutSize}
      ?alert=${this.alert}
      .alertFrameType=${this.alertFrameType}
      .alertFrameThickness=${this.alertFrameThickness}
      .alertFrameStatus=${this.alertFrameStatus}
      .alertFrameMode=${this.alertFrameMode}
      .showAlertCategoryIcon=${this.showAlertCategoryIcon}
      .showAlertIcon=${this.showAlertIcon}
      ?progress=${this.progress}
      .progressMode=${this.progressMode}
      .progressValue=${this.progressValue}
      .variant=${this._variant}
      .direction=${this._direction}
      .orientation=${this._orientation}
      .hasBadgeSpacer=${this.getBadgeSpacer()}
      .positioning=${this.positioning}
      ?activated=${this.activated}
    >
      ${this.icon}
      <slot
        name="badge-top-right"
        slot="badge-top-right"
        @slotchange=${this.handleBadgeSlotChange}
      >
        ${o?f`<obc-automation-badge
              .type=${o}
            ></obc-automation-badge>`:z}
      </slot>
      <slot
        name="badge-top-left"
        slot="badge-top-left"
        @slotchange=${this.handleBadgeSlotChange}
      >
        ${r?f`<obc-automation-badge
              .type=${r}
            ></obc-automation-badge>`:z}
      </slot>
      <slot
        name="badge-bottom-left"
        slot="badge-bottom-left"
        @slotchange=${this.handleBadgeSlotChange}
      >
        ${i?f`<obc-automation-badge
              .type=${i}
            ></obc-automation-badge>`:z}
      </slot>
      <slot
        name="badge-bottom-right"
        slot="badge-bottom-right"
        @slotchange=${this.handleBadgeSlotChange}
      >
        ${s?f`<obc-automation-badge
              .type=${s}
            ></obc-automation-badge>`:z}
      </slot>
    </obc-automation-button>`}};it([h({type:Boolean,attribute:!1})],Te.prototype,"showReadoutStack");it([h({type:String})],Te.prototype,"readoutPosition");it([h({type:Boolean,attribute:!1})],Te.prototype,"showStatus");it([h({type:String})],Te.prototype,"readoutSize");it([h({type:String})],Te.prototype,"tag");it([h({type:String})],Te.prototype,"positioning");it([h({type:Boolean})],Te.prototype,"activated");it([h({type:Boolean})],Te.prototype,"alert");it([h({type:String})],Te.prototype,"alertFrameType");it([h({type:String})],Te.prototype,"alertFrameThickness");it([h({type:String})],Te.prototype,"alertFrameStatus");it([h({type:String})],Te.prototype,"alertFrameMode");it([h({type:Boolean,attribute:!1})],Te.prototype,"showAlertCategoryIcon");it([h({type:Boolean})],Te.prototype,"showAlertIcon");it([h({type:Boolean})],Te.prototype,"progress");it([h({type:String})],Te.prototype,"progressMode");it([h({type:Number})],Te.prototype,"progressValue");it([h({type:String})],Te.prototype,"badgeControl");it([h({type:String})],Te.prototype,"badgeCommandLocked");it([h({type:String})],Te.prototype,"badgeInterlock");it([h({type:String})],Te.prototype,"badgeAlert");it([Bi({slot:"badge-top-right"})],Te.prototype,"badgeTopRight");it([Bi({slot:"badge-top-left"})],Te.prototype,"badgeTopLeft");it([Bi({slot:"badge-bottom-left"})],Te.prototype,"badgeBottomLeft");it([Bi({slot:"badge-bottom-right"})],Te.prototype,"badgeBottomRight");var j3=Object.defineProperty,oi=(e,t,o,r)=>{for(var i=void 0,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=n(t,o,i)||i);return i&&j3(t,o,i),i};var Gt=class extends Te{constructor(){super(...arguments),this.on=!1,this.speedInPercent=0,this.speedUnit="%",this.speedMaxDigits=3,this.labelDirection=Gi.right,this.variant="regular",this.direction=Gn.forward}get extraReadouts(){let t=this.speed??this.speedInPercent;return this.showStatus?t!=null&&this.on?[{type:"value",value:t,nDigits:this.speedMaxDigits,unit:this.speedUnit,direction:this.labelDirection,icon:this.labelDirection===Gi.none?"none":"chevron"}]:this.on?[]:[{type:"state-off",value:"Off",hasIcon:!0}]:[]}get _on(){return this.on}};oi([h({type:Boolean})],Gt.prototype,"on");oi([h({type:Number})],Gt.prototype,"speedInPercent");oi([h({type:Number})],Gt.prototype,"speed");oi([h({type:String})],Gt.prototype,"speedUnit");oi([h({type:Number})],Gt.prototype,"speedMaxDigits");oi([h({type:String})],Gt.prototype,"labelDirection");oi([h({type:String})],Gt.prototype,"variant");oi([h({type:String})],Gt.prototype,"direction");var W3=Object.defineProperty,U3=Object.getOwnPropertyDescriptor,B0=(e,t,o,r)=>{for(var i=r>1?void 0:r?U3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&W3(t,o,i),i},vh=class extends Gt{constructor(){super(...arguments),this.vertical=!1}get icon(){return this.vertical?this.on?f`<obi-pump-on-vertical
            usecsscolor
            slot="icon"
          ></obi-pump-on-vertical>
          <obi-pump-on-vertical
            usecsscolor
            slot="icon-silhouette"
          ></obi-pump-on-vertical>`:f`<obi-pump-off-vertical
            usecsscolor
            slot="icon"
          ></obi-pump-off-vertical>
          <obi-pump-off-vertical
            usecsscolor
            slot="icon-silhouette"
          ></obi-pump-off-vertical>`:this.on?f`<obi-pump-on-horizontal
            usecsscolor
            slot="icon"
          ></obi-pump-on-horizontal>
          <obi-pump-on-horizontal
            usecsscolor
            slot="icon-silhouette"
          ></obi-pump-on-horizontal>`:f`<obi-pump-off-horizontal
            usecsscolor
            slot="icon"
          ></obi-pump-off-horizontal>
          <obi-pump-off-horizontal
            usecsscolor
            slot="icon-silhouette"
          ></obi-pump-off-horizontal>`}};B0([h({type:Boolean})],vh.prototype,"vertical",2);vh=B0([L("obc-pump")],vh);var I0=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

/* ---------- Default host sizes ----------
 *
 *   Vertical regular:    256×376   (halo fills host; 4px padding)
 *   Horizontal regular:  420×256   (halo fills host; 4px padding)
 *   Vertical compact:    170×282   (fixed; halo fills host; 4px padding)
 *   Horizontal compact:  244×208   (fixed; halo fills host; 4px padding)
 *
 * In compact/static mode the halo is a fixed-size column flex container
 * holding: 4px padding + badges + 4px gap + tank-frame + 4px gap + readout
 * (compact only) + 4px gap + tag + 4px padding. The tank-frame uses
 * \`flex: 1 1 auto; min-height: 0\` so it absorbs whatever space the other
 * cells don't use. Empty \`.badges\` / \`.tag\` cells collapse to 0 via the
 * \`hidden\` attribute set by the component (slotchange-driven), allowing
 * the tank-frame to grow into the freed space.
 *
 * Inside the tank-frame, all textual cells (tag, badges, readout) size to
 * \`min-content\`; the chart cell takes \`1fr\` in both axes so any host resize
 * flows entirely into the chart.
 */

:host {
  display: inline-block;
  width: 256px;
  height: 376px;
  /* Floor matches the compact-mode halo footprint so the host cannot be
   * resized below a still-legible tank. */
  min-width: 170px;
  min-height: 282px;
  /* P&ID anchor: top-center of host = drop coord; visual tank centers under it. */
  position: relative;
}

:host([orientation="horizontal"]) {
  width: 420px;
  height: 256px;
  min-width: 244px;
  min-height: 208px;
}

:host([compact]) {
  width: 170px;
  height: 282px;
}

:host([orientation="horizontal"][compact]) {
  width: 244px;
  height: 208px;
}

:host([static]) {
  width: 170px;
  height: 282px;
}

:host([orientation="horizontal"][static]) {
  width: 244px;
  height: 208px;
}

/* ---------- positioning="button" ----------
 * Host fills its parent (100% × 100%) with no P&ID anchor offset. The
 * parent container is responsible for placement and sizing; the tank
 * renders responsively inside it. Overrides all the fixed default
 * dimensions above (regular / compact / static, both orientations) and
 * also drops the min-width / min-height floors so the tank can shrink to
 * whatever the parent allows. Inner layout (compact / static / chart
 * mode / orientation) is unaffected — only the host box and the .root
 * anchor transform change.
 */

:host([positioning="button"]),
:host([positioning="button"][orientation="horizontal"]),
:host([positioning="button"][compact]),
:host([positioning="button"][orientation="horizontal"][compact]),
:host([positioning="button"][static]),
:host([positioning="button"][orientation="horizontal"][static]) {
  display: block;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
}

/* Indefinite-axis fallback.
 *
 * \`width\`/\`height: 100%\` only resolve when the parent's corresponding axis is
 * definite. In a flex/grid dashboard slot one axis is very often left to
 * content — \`align-self: center\` makes the cross axis shrink-to-fit, and a
 * parent sized with \`min-height\`/\`max-height\` (rather than \`height\`) leaves the
 * block axis indefinite. In those cases the percentage computes to \`auto\` and
 * the tank would size to its own content, which includes the chart cell — and
 * the chart sizes itself from the cell it was measured in. That is a circular
 * constraint, and it resolves as a collapsed cell, unbounded growth or
 * pixel-level ringing depending on the loop gain (issue #1121).
 *
 * \`aspect-ratio\` supplies the missing axis from the design footprint the
 * \`point\` variant uses above, so an indefinite axis lands on a definite value
 * that no longer depends on the tank's own content. It is inert when the parent
 * makes both axes definite, so the normal "fill my slot" behavior is unchanged.
 */

:host([positioning="button"]) {
  aspect-ratio: 256 / 376;
}

:host([positioning="button"][orientation="horizontal"]) {
  aspect-ratio: 420 / 256;
}

:host([positioning="button"][compact]),
:host([positioning="button"][static]) {
  aspect-ratio: 170 / 282;
}

:host([positioning="button"][orientation="horizontal"][compact]),
:host([positioning="button"][orientation="horizontal"][static]) {
  aspect-ratio: 244 / 208;
}

:host([positioning="button"]) .root {
  position: static;
  top: auto;
  left: auto;
  transform: none;
}

/* Trend icon sizing follows the design-token icon-size ladders so it scales
 * with \`obc-component-size-*\` (set on an ancestor; tokens cross the shadow
 * boundary via CSS variable inheritance):
 *   - Non-compact (default): \`regular\` ladder → 24 / 32 / 40 / 48
 *     across regular → medium → large → xl.
 *   - Compact (and the compact readout in \`.halo\`, outside \`.tank-frame\`,
 *     so we scope via the reflected host attribute): \`small\` ladder →
 *     16 / 20 / 24 / 32. Static mode renders capacity (no trend icon) so
 *     it's unaffected. */

.trend-icon {
  display: block;
  width: var(--global-size-spacing-icon-icon-size-regular);
  height: var(--global-size-spacing-icon-icon-size-regular);
}

:host([compact]) .trend-icon {
  width: var(--global-size-spacing-icon-icon-size-small);
  height: var(--global-size-spacing-icon-icon-size-small);
}

/* ---------- Root + halo ----------
 * The root <button> is the touch target; its visual styling is transparent.
 * The visible interactive surround (border/bg on hover/pressed/focus-visible/
 * disabled) is painted on \`.halo\` via the flat mixin's \`visibleWrapperClass\`
 * parameter. The halo wraps the bordered area only:
 *   - non-compact: just the tank-frame (4px padding)
 *   - compact: badges + tank-frame + readout + tag (4px padding, fixed
 *     halo height; empty cells collapse so tank-frame absorbs the space)
 *   - static:  badges + tank-frame + tag (readout is INSIDE the frame)
 *
 * P&ID anchor: \`translateX(-50%)\` shifts the root left by half its own width
 * so the tank centerline aligns with the host's left edge (= drop coord).
 * \`top: -20px\` keeps the original vertical offset that lifts the visual tank
 * above the host's top-left placement origin. This matches the legacy
 * \`.outer\` pattern from develop and the compact rule below.
 */

.root {
  position: absolute;
  top: -20px;
  left: 0;
  transform: translateX(-50%);
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  appearance: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Interactive (\`clickable\`, the default): the full six-state flat mixin —
 * enabled, activated, hover, pressed, focus-visible, disabled — painted on
 * \`.halo\`. */

.root.clickable {
  cursor: pointer;
  /* prettier-ignore */
}

.root.clickable {
  cursor: pointer;
}

.root.clickable:focus {
  outline: none;
}

.root.clickable .halo {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.root.clickable.activated .halo {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.root.clickable:hover .halo {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.root.clickable:active .halo {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.root.clickable:focus-visible .halo {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.root.clickable:disabled .halo {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.root.clickable.disabled .halo {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.root.clickable:disabled {
  cursor: not-allowed;
}

.root.clickable.disabled {
  cursor: not-allowed;
}

/* Non-interactive (\`clickable\` is \`false\`, and \`static\`, which is display-only
 * by definition): the mixin's \`noClick\` variant emits the enabled state ONLY, so
 * the halo keeps exactly the same resting colors and the same 1px border box
 * — no layout shift, nothing else in the tank changes — while hover, pressed
 * and focus-visible disappear. The root is a \`<div>\` in this case, so there is
 * no focus ring or tab stop to suppress either. Same split as
 * \`obc-elevated-card\`'s \`.not-clickable\` / \`:not(.not-clickable)\` pair. */

.root:not(.clickable) {
  cursor: default;
  /* prettier-ignore */
}

.root:not(.clickable) .halo {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.root:focus {
  outline: none;
}

/* Compact/static now have a fixed host height (matching the halo), so the
 * root can fill the host like the non-compact case. We still drop the
 * \`top: -20px\` offset that lifts non-compact tanks above their placement
 * origin (in compact/static the visible content starts at the host's top
 * edge so there's nothing external to skip). \`position: static\` keeps the
 * root in normal flow; \`translateX(-50%)\` preserves the P&ID horizontal
 * anchor convention (centerline aligned with host left edge). */

:host([compact]) .root,
:host([static]) .root {
  position: static;
  height: 100%;
  top: auto;
}

/* Static is display-only, so it never gets the \`.clickable\` class and the
 * hover/pressed visuals are already gone via the \`noClick\` rule above. Static
 * additionally refuses pointer events outright — unlike a non-clickable tank,
 * which still lets clicks reach the host so a consumer can opt into handling
 * them. */

:host([static]) .root {
  pointer-events: none;
}

.halo {
  padding: 4px;
  border-radius: 10px;
  box-sizing: border-box;
  /* Positioned ancestor for the alert-frame overlay. */
  position: relative;
}

/* Alert-frame overlay mirrors \`obc-automation-button\`: -1px inset so the
 * ring sits on the halo's outer edge without clipping. */

.alert-frame {
  position: absolute;
  inset: -1px;
}

/* Non-compact (and not static): halo is the only child of root and fills the host. */

:host(:not([compact]):not([static])) .halo {
  width: 100%;
  height: 100%;
}

:host(:not([compact]):not([static])) .halo > .tank-frame {
  width: 100%;
  height: 100%;
}

/* Compact/static: halo is a fixed-size column flex container holding all
 * cells. It fills the host (host is fixed-size in these modes). */

:host([compact]) .halo,
:host([static]) .halo {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  height: 100%;
}

:host([compact]) .halo > .tank-frame,
:host([static]) .halo > .tank-frame {
  flex: 1 1 auto;
  min-height: 0;
  min-width: 0;
}

/* Badges / readout / tag are fixed-size cells inside the halo column. */

:host([compact]) .halo > .badges,
:host([static]) .halo > .badges,
:host([compact]) .halo > .readout,
:host([compact]) .halo > .tag,
:host([static]) .halo > .tag {
  flex: 0 0 auto;
}

/* \`hidden\` attribute support: needed because the cells set an explicit
 * display value (\`flex\` / \`block\`), which would otherwise override
 * \`hidden\`'s default \`display: none\`. Removing the cell from the flex
 * layout entirely lets the tank-frame absorb the freed space AND removes
 * the column gap that would remain for an empty-but-displayed child. */

.badges[hidden],
.tag[hidden] {
  display: none !important;
}

/* ---------- Tank frame (3 sections: cap-start / middle / cap-end) ----------
 * The frame is purely decorative (no pointer events) so the surrounding button
 * receives the click on every pixel of the tank.
 *
 * Cap dimensions are exposed as custom properties so the compact variant only
 * needs to override the numeric values (see \`.tank-frame.compact\` below). */

.tank-frame {
  --cap-thickness: 14px;
  --cap-corner-w: 12px;
  --cap-radius: 5px;
  pointer-events: none;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  color: var(--instrument-regular-secondary-color);
}

.tank-frame.compact {
  --cap-thickness: 10px;
  --cap-corner-w: 7px;
  --cap-radius: 4px;
}

.tank-frame.orientation-horizontal {
  flex-direction: row;
  align-items: stretch;
}

.middle {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-height: 0;
  min-width: 0;
  background: var(--instrument-frame-primary-color);
  border-left: 1px solid var(--instrument-frame-tertiary-color);
  border-right: 1px solid var(--instrument-frame-tertiary-color);
  padding: 8px;
}

.tank-frame.orientation-horizontal .middle {
  border-left: none;
  border-right: none;
  border-top: 1px solid var(--instrument-frame-tertiary-color);
  border-bottom: 1px solid var(--instrument-frame-tertiary-color);
}

/* Compact tightens the inner padding from 8px to 4px to give the chart /
 * bar cell more breathing room inside the smaller fixed footprint. */

.tank-frame.compact .middle {
  padding: 4px;
}

/* generic / battery: middle owns the full border + radius (no caps to draw it). */

.tank-frame.type-generic .middle,
.tank-frame.type-battery .middle {
  border: 1px solid var(--instrument-frame-tertiary-color);
  border-radius: 6px;
}

/* Atmospheric (non-compact): the seam between the cap and the middle is
 * drawn by a 1px CSS border on \`.middle\` rather than an SVG stroke on the
 * cap. CSS \`border: 1px\` pixel-snaps consistently with the pressurized
 * cap's border, while SVG \`stroke-width: 1\` renders thinner / blurrier
 * because of sub-pixel anti-aliasing. Compact atmospheric intentionally
 * omits this border so the cap merges into the middle, matching the
 * compact-pressurized behavior. */

.tank-frame.type-atmospheric:not(.compact):not(.orientation-horizontal)
  .middle {
  border-top: 1px solid var(--instrument-frame-tertiary-color);
  border-bottom: 1px solid var(--instrument-frame-tertiary-color);
}

.tank-frame.type-atmospheric:not(.compact).orientation-horizontal .middle {
  border-left: 1px solid var(--instrument-frame-tertiary-color);
  border-right: 1px solid var(--instrument-frame-tertiary-color);
}

/* ---------- Inner grid (non-compact only) ----------
 * Vertical: 3 rows × 2 cols.   Row 1 = tag | badges, Row 2 = readout, Row 3 = chart.
 * Horizontal: 2 rows × 2 cols. Row 1 = tag | badges, Row 2 = chart | readout.
 * Chart cell = 1fr × 1fr, textual cells = min-content. */

.grid {
  display: grid;
  width: 100%;
  height: 100%;
  gap: 8px;
}

.tank-frame:not(.orientation-horizontal) .grid {
  grid-template-columns: minmax(0, 1fr) min-content;
  grid-template-rows: min-content min-content minmax(0, 1fr);
}

.tank-frame:not(.orientation-horizontal) .grid > .tag {
  grid-row: 1;
  grid-column: 1;
  justify-self: start;
  align-self: start;
  line-height: 1;
}

.tank-frame:not(.orientation-horizontal) .grid > .badges {
  grid-row: 1;
  grid-column: 2;
  justify-self: end;
  align-self: start;
}

.tank-frame:not(.orientation-horizontal) .grid > .readout {
  grid-row: 2;
  grid-column: 1 / -1;
}

.tank-frame:not(.orientation-horizontal) .grid > .bar-container {
  grid-row: 3;
  grid-column: 1 / -1;
}

.tank-frame.orientation-horizontal .grid {
  grid-template-columns: minmax(0, 1fr) min-content;
  grid-template-rows: min-content minmax(0, 1fr);
}

.tank-frame.orientation-horizontal .grid > .tag {
  grid-row: 1;
  grid-column: 1;
  justify-self: start;
  align-self: start;
  line-height: 1;
}

.tank-frame.orientation-horizontal .grid > .badges {
  grid-row: 1;
  grid-column: 2;
  justify-self: end;
  align-self: start;
}

.tank-frame.orientation-horizontal .grid > .bar-container {
  grid-row: 2;
  grid-column: 1;
}

.tank-frame.orientation-horizontal .grid > .readout {
  grid-row: 2;
  grid-column: 2;
  align-self: stretch;
  min-width: 96px;
}

/* ---------- Cells ---------- */

.badges {
  display: flex;
  justify-content: end;
  gap: 4px;
  pointer-events: auto;
}

.tag {
  display: block;
  pointer-events: auto;
  font-family: var(--global-typography-font-family);
  font-size: var(--global-typography-instrument-label-font-size);
  line-height: var(--global-typography-instrument-label-line-height);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  color: var(--element-neutral-color);
  /* Tag text must never break across lines — it is a fixed identifier
   * (e.g. \`FUEL\`, \`#0000\`) that loses meaning if hyphenated or wrapped. */
  white-space: nowrap;
}

.readout {
  display: block;
  pointer-events: auto;
}

/* Compact readout: single line — trend icon + percent only (per design spec). */

.readout-compact {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  /* Keep \`90%\` together — the parent flex prevents flex-item wrapping but
   * not text wrapping inside \`.percent\` (number + \`<span>%</span>\`). */
  white-space: nowrap;
  color: var(--element-neutral-color);
}

.readout-compact .percent {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-regular-font-size);
    line-height: var(--global-typography-instrument-value-regular-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.readout-compact .percent-symbol {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-unit-font-size);
    line-height: var(--global-typography-instrument-unit-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    margin-left: 1px;
  }

/* Static readout: max-value + unit (no percent, no trend icon). Tighter
 * 2px gap and small-neutral value sizing per design spec. Color is
 * inherited from \`.readout-compact\`. */

.readout-static {
  gap: 2px;
}

.readout-static slot[name="max-value"] {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-small-font-size);
    line-height: var(--global-typography-instrument-value-small-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.readout-static slot[name="unit"] {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-unit-font-size);
    line-height: var(--global-typography-instrument-unit-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
}

.header .percent {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-large-font-size);
    line-height: var(--global-typography-instrument-value-large-line-height);
    letter-spacing: var(
    --global-typography-instrument-value-large-letter-spacing
  );
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    color: var(--element-neutral-color);
    padding-bottom: var(
      --global-typography-instrument-value-large-padding-bottom
    );
    /* Keep the number and the trailing \`%\` symbol on one line. */
    white-space: nowrap;
  }

.header .percent-symbol {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-unit-font-size);
    line-height: var(--global-typography-instrument-unit-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    /* \`inline-block\` so \`padding-bottom\` actually applies (ignored on
     * plain inline text). */
    display: inline-block;
    padding-bottom: var(--global-typography-instrument-unit-padding-bottom);
  }

.value {
  display: flex;
  align-items: baseline;
  justify-content: flex-end;
  padding-top: 4px;
  /* Keep \`<current> / <max> <unit>\` together — in horizontal layout the
   * readout cell is min-content + 96px floor, and very narrow hosts can
   * still squeeze it. The numbers and unit must stay on a single line. */
  white-space: nowrap;

  font-family: var(--global-typography-font-family);

  font-size: var(--global-typography-instrument-unit-font-size);

  line-height: var(--global-typography-instrument-unit-line-height);

  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
}

.value .current-value {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-regular-font-size);
    line-height: var(--global-typography-instrument-value-regular-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    padding-bottom: var(
      --global-typography-instrument-value-regular-padding-bottom
    );
  }

.value .divider {
    padding-left: 4px;
    padding-right: 4px;
    padding-bottom: var(--global-typography-instrument-unit-padding-bottom);
  }

.value .max-value {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-regular-font-size);
    line-height: var(--global-typography-instrument-value-regular-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    padding-bottom: var(
      --global-typography-instrument-value-regular-padding-bottom
    );
  }

.value .unit {
    padding-bottom: var(--global-typography-instrument-unit-padding-bottom);
  }

.rich-divider {
  border-top: 1px solid var(--border-divider-color);
  margin-top: 8px;
}

/* Rich detail rows are consumer-slotted into \`slot="rich"\` — canonical usage is
 * an \`<obc-readout-list>\` of \`<obc-readout-list-item>\` rows, which owns its own
 * cap-height (textbox) typography and cross-row column alignment. The tank only
 * spaces the slotted content below the divider; the divider itself is shown only
 * when the slot is filled (\`?hidden\` bound to \`_hasRichSlot\`). */

::slotted(obc-readout-list) {
  display: block;
  margin-top: 8px;
}

/* The chart cell is a plain sizing/clipping box. Both child renderers —
 * \`obc-gauge-trend\` (graph / graph-and-bar modes) and \`obc-bar-vertical\`
 * (bar mode) — paint their own background, border and border-radius. */

.bar-container {
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  position: relative;
  overflow: hidden;
}

/* The renderers are taken out of flow so the cell sizes them, never the other
 * way round. Both of them derive a pixel size from the box they are measured
 * in — \`obc-gauge-trend\` publishes an inline \`--chart-height\` computed from its
 * own measured width, and \`obc-bar-vertical\` writes \`height: 100%; width: auto\`
 * onto its own host — so while they are in flow the cell's content height is a
 * function of the cell's own height. Absolute positioning severs that return
 * path: \`.bar-container\` is \`position: relative\`, so \`inset: 0\` pins the
 * renderer to the cell the tank's grid/flex layout already decided on, and a
 * rounding difference between the two can no longer relayout the tank
 * (issue #1121). */

.bar-container > obc-gauge-trend,
.bar-container > obc-bar-vertical {
  display: block;
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

/* ---------- Decorative chart-cell icon overlay (hasGraphIcon) ----------
 * Centered on \`.bar-container\` in all chart modes (bar / graph / graph-and-bar)
 * and both orientations. The icon lives in the host CSS layer (not inside the
 * SVG meet transform), so it stays a constant size regardless of cell size.
 *
 * Stroke halo: the back \`<obi-tank>\` inherits \`stroke\` + \`stroke-width\`,
 * which crosses the icon's shadow DOM via SVG inheritance and paints a 2px
 * outline around the same shape painted by the front (fill) layer.
 *
 * Size ladder: scales via the design token
 * \`--automation-components-tanks-graphs-graph-icon-size\`, which is set per
 * \`.obc-component-size-*\` class on \`:root\` in palettes/variables.css and
 * inherits across shadow boundaries through the normal cascade. */

.graph-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
  /* Lift above the gauge-trend's chart-fill area (graph / graph-and-bar
   * modes) — without this the area-chart paint layer can occlude the icon
   * even though the overlay is a later DOM sibling. */
  z-index: 1;
}

.graph-icon > obi-tank,
.graph-icon > obi-energy-battery {
  position: absolute;
  width: var(--automation-components-tanks-graphs-graph-icon-size);
  height: var(--automation-components-tanks-graphs-graph-icon-size);
}

.graph-icon-fill {
  color: var(--instrument-regular-secondary-color);
}

.graph-icon.priority-enhanced .graph-icon-fill {
  color: var(--instrument-enhanced-secondary-color);
}

.graph-icon-stroke {
  stroke: var(--border-silhouette-color);
  stroke-width: 2;
}

/* ---------- Caps ---------- */

.cap {
  position: relative;
  flex-shrink: 0;
}

/* Vertical atmospheric cap: 3-piece row (corner-start / stretchable middle
 * arc / corner-end). Compact variant only changes the numeric values via the
 * \`--cap-*\` custom properties on \`.tank-frame.compact\`. */

.cap-atmospheric {
  display: flex;
  align-items: stretch;
  height: var(--cap-thickness);
  width: 100%;
}

.cap-atmospheric .cap-corner {
  flex: 0 0 var(--cap-corner-w);
  height: var(--cap-thickness);
  display: block;
}

.cap-atmospheric .cap-mid {
  flex: 1 1 auto;
  height: var(--cap-thickness);
  min-width: 0;
  display: block;
}

.cap-fill {
  fill: var(--instrument-frame-primary-color);
}

.cap-stroke {
  stroke: var(--instrument-frame-tertiary-color);
  stroke-width: 1;
}

.cap-atmospheric.cap-end {
  transform: scaleY(-1);
}

/* Pressurized cap (vertical). */

.cap-pressurized {
  height: var(--cap-thickness);
  width: 100%;
  background: var(--instrument-frame-primary-color);
  border: 1px solid var(--instrument-frame-tertiary-color);
}

.cap-pressurized.cap-start {
  border-top-left-radius: var(--cap-radius);
  border-top-right-radius: var(--cap-radius);
}

.cap-pressurized.cap-end {
  border-bottom-left-radius: var(--cap-radius);
  border-bottom-right-radius: var(--cap-radius);
}

/* Compact pressurized (vertical): inner-edge border is dropped so the cap
 * merges seamlessly into the middle section (the middle section's own
 * top/bottom edge takes over). Scoped to vertical only — in horizontal
 * orientation the inner edge is left/right, handled by the rules further
 * down. Without the \`:not(.orientation-horizontal)\` guard these would
 * also fire in horizontal mode and erroneously strip the outer
 * bottom/top edges of the left/right caps. */

.tank-frame.compact:not(.orientation-horizontal) .cap-pressurized.cap-start {
  border-bottom: none;
}

.tank-frame.compact:not(.orientation-horizontal) .cap-pressurized.cap-end {
  border-top: none;
}

/* Battery cap (vertical). Width is ~35% of the tank inner width giving
 * ~90px regular and ~58px compact. The bottom border is omitted so the cap
 * blends into the middle section. */

.cap-battery {
  height: var(--cap-thickness);
  width: 35%;
  margin: 0 auto;
  background: var(--instrument-frame-primary-color);
  border: 1px solid var(--instrument-frame-tertiary-color);
  border-bottom: none;
  border-top-left-radius: var(--cap-radius);
  border-top-right-radius: var(--cap-radius);
}

/* Horizontal cap variants */

.tank-frame.orientation-horizontal .cap-pressurized {
  width: var(--cap-thickness);
  height: auto;
  align-self: stretch;
}

.tank-frame.orientation-horizontal .cap-pressurized.cap-start {
  border-radius: 0;
  border-top-left-radius: var(--cap-radius);
  border-bottom-left-radius: var(--cap-radius);
}

.tank-frame.orientation-horizontal .cap-pressurized.cap-end {
  border-radius: 0;
  border-top-right-radius: var(--cap-radius);
  border-bottom-right-radius: var(--cap-radius);
}

/* Compact pressurized (horizontal): inner edge merges into the middle section. */

.tank-frame.orientation-horizontal.compact .cap-pressurized.cap-start {
  border-right: none;
}

.tank-frame.orientation-horizontal.compact .cap-pressurized.cap-end {
  border-left: none;
}

.tank-frame.orientation-horizontal .cap-battery {
  width: var(--cap-thickness);
  height: 35%;
  align-self: center;
  margin: 0;
  border: 1px solid var(--instrument-frame-tertiary-color);
  border-right: none;
  border-radius: 0;
  border-top-left-radius: var(--cap-radius);
  border-bottom-left-radius: var(--cap-radius);
}

/* Horizontal atmospheric: 3-piece column with rotated SVGs (see render). */

.tank-frame.orientation-horizontal .cap-atmospheric {
  display: flex;
  flex-direction: column-reverse;
  width: var(--cap-thickness);
  height: auto;
  align-self: stretch;
  background: transparent;
  border: none;
  transform: none;
}

.tank-frame.orientation-horizontal .cap-atmospheric > svg {
  display: block;
}

.tank-frame.orientation-horizontal .cap-atmospheric .cap-corner {
  flex: 0 0 var(--cap-corner-w);
  width: var(--cap-thickness);
  height: var(--cap-corner-w);
}

.tank-frame.orientation-horizontal .cap-atmospheric .cap-mid {
  flex: 1 1 auto;
  width: var(--cap-thickness);
  height: auto;
  min-height: 0;
}

.tank-frame.orientation-horizontal .cap-atmospheric.cap-end {
  transform: scaleX(-1);
}

/* ---------- Static mode ----------
 * Display-only: chart/bar is hidden, the bordered area is filled with
 * --container-section-color, and the readout is centered inside the frame.
 * Outer borders/strokes are kept as the regular outline color so the
 * silhouette and dimensions stay identical to the compact variant. */

.tank-frame.static .middle {
  background: var(--container-section-color);
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tank-frame.static .static-readout {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

/* Match the compact readout layout: in compact the \`.readout.readout-compact\`
 * is a direct child of \`.halo\` (column flex with default \`align-items: stretch\`)
 * so it spans the full width and its own \`justify-content: center\` centers
 * the trend icon + percent. In static the same div is wrapped in
 * \`.static-readout\` — without an explicit \`width: 100%\` it would shrink to
 * content width, so its internal centering would be relative to a smaller
 * box rather than the full middle. */

.tank-frame.static .static-readout > .readout-compact {
  width: 100%;
}

/* \`<slot>\` defaults to \`display: contents\`, which makes the slot's fallback
 * children become direct children of the \`.readout-compact\` flex container
 * and pick up its \`gap: 4px\` — producing an unwanted gap inside \`m³\` (between
 * the \`m\` text node and the \`<sup>3</sup>\` element). Restoring an explicit
 * inline-block box on the slot keeps the slot itself as a single flex item
 * so its inline children render tight. Scoped to the static readout to
 * avoid disturbing the compact layout. */

.tank-frame.static .readout-static > slot {
  display: inline-block;
}

/* In static mode the tag sits in its own halo cell and should read as a
 * centered label under the device (matching the centered capacity readout
 * above it). The compact tag layout intentionally stays as-is. */

:host([static]) .halo > .tag {
  text-align: center;
}

.tank-frame.static .cap-fill {
  fill: var(--container-section-color);
}

.tank-frame.static .cap-pressurized,
.tank-frame.static .cap-battery {
  background: var(--container-section-color);
}
`;var bh=(e=>(e.normal="normal",e.empty="empty",e.water="water",e.air="air",e))(bh||{});function Z0(e){if(e==="electric")return 2;if(e==="connector")return 1;if(e==="fluid")return 4;if(e==="air")return 10;throw new Error("Unknown line type")}var G3=Object.defineProperty,Y3=Object.getOwnPropertyDescriptor,F0=(e,t,o,r)=>{for(var i=r>1?void 0:r?Y3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&G3(t,o,i),i},dc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M6 14.0002L7.41 15.4102L12 10.8302L16.59 15.4102L18 14.0002L12 8.00016L6 14.0002Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M6 14.0002L7.41 15.4102L12 10.8302L16.59 15.4102L18 14.0002L12 8.00016L6 14.0002Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};dc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;F0([h({type:Boolean})],dc.prototype,"useCssColor",2);dc=F0([L("obi-chevron-up-google")],dc);var q3=Object.defineProperty,X3=Object.getOwnPropertyDescriptor,N0=(e,t,o,r)=>{for(var i=r>1?void 0:r?X3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&q3(t,o,i),i},hc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 9.41L16.59 8L12 12.58L7.41 8L6 9.41L12 15.41L18 9.41Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 9.41L16.59 8L12 12.58L7.41 8L6 9.41L12 15.41L18 9.41Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};hc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;N0([h({type:Boolean})],hc.prototype,"useCssColor",2);hc=N0([L("obi-chevron-down-google")],hc);var K3=Object.defineProperty,Q3=Object.getOwnPropertyDescriptor,j0=(e,t,o,r)=>{for(var i=r>1?void 0:r?Q3(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&K3(t,o,i),i},pc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M9 3H15V4.89474H9V3Z" fill="currentColor"/>
<path d="M5.52983 17.4141C3.58026 17.4141 2 15.0364 2 12.1018C2 9.16714 3.58026 6.78947 5.52983 6.78947H18.4702C20.4197 6.78947 22 9.16714 22 12.1018C22 15.0364 20.4197 17.4141 18.4702 17.4141H16.968L16.5455 21H14.7273V17.4141H9.27273V21H7.45455L7.03196 17.4141H5.52983Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M9 3H15V4.89474H9V3Z" style="fill: var(--element-active-color)"/>
<path d="M5.52983 17.4141C3.58026 17.4141 2 15.0364 2 12.1018C2 9.16714 3.58026 6.78947 5.52983 6.78947H18.4702C20.4197 6.78947 22 9.16714 22 12.1018C22 15.0364 20.4197 17.4141 18.4702 17.4141H16.968L16.5455 21H14.7273V17.4141H9.27273V21H7.45455L7.03196 17.4141H5.52983Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};pc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;j0([h({type:Boolean})],pc.prototype,"useCssColor",2);pc=j0([L("obi-tank")],pc);var J3=Object.defineProperty,e8=Object.getOwnPropertyDescriptor,W0=(e,t,o,r)=>{for(var i=r>1?void 0:r?e8(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&J3(t,o,i),i},uc=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M11.9472 18.1056C11.7113 18.5775 11 18.4096 11 17.882V14H9L12.0528 7.89443C12.2887 7.42252 13 7.59042 13 8.11803V12H15L11.9472 18.1056Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10 3C10 2.44772 10.4477 2 11 2H13C13.5523 2 14 2.44772 14 3V4H17C18.1046 4 19 4.89543 19 6V20C19 21.1046 18.1046 22 17 22H7C5.89543 22 5 21.1046 5 20V6C5 4.89543 5.89543 4 7 4H10V3ZM17 6H7V20H17V6Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11.9472 18.1056C11.7113 18.5775 11 18.4096 11 17.882V14H9L12.0528 7.89443C12.2887 7.42252 13 7.59042 13 8.11803V12H15L11.9472 18.1056Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10 3C10 2.44772 10.4477 2 11 2H13C13.5523 2 14 2.44772 14 3V4H17C18.1046 4 19 4.89543 19 6V20C19 21.1046 18.1046 22 17 22H7C5.89543 22 5 21.1046 5 20V6C5 4.89543 5.89543 4 7 4H10V3ZM17 6H7V20H17V6Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};uc.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;W0([h({type:Boolean})],uc.prototype,"useCssColor",2);uc=W0([L("obi-energy-battery")],uc);var U0=M`* {
  -webkit-tap-highlight-color: transparent;
}

.canvas-and-slots-container {
  position: relative;
}

canvas {
  z-index: 1;
  position: relative;
}

/* Scale slots - absolutely positioned at edges */

slot[name="top-scale"],
slot[name="bottom-scale"],
slot[name="left-scale"],
slot[name="right-scale"] {
  position: absolute;
  display: block;
  pointer-events: none;
}

slot[name="top-scale"] {
  top: 0;
  left: 0;
  right: 0;
}

slot[name="bottom-scale"] {
  bottom: 0;
  left: 0;
  right: 0;
}

slot[name="left-scale"] {
  top: 0;
  bottom: 0;
  left: 0;
}

slot[name="right-scale"] {
  top: 0;
  bottom: 0;
  right: 0;
}
`;var G0=M`* {
  -webkit-tap-highlight-color: transparent;
}

:host {
  display: inline-flex;
  line-height: 0;
}

/* Fixed aspect ratio scaling mode: fill parent width, height from aspect ratio */

:host([fixedaspectratioscaling]) {
  display: flex;
  width: 100%;
}

.wrapper {
  width: auto; /* since we can have an optional legend */
  height: var(--chart-height, auto);
  display: inline-flex;
  justify-content: center;
  align-items: center;
  position: relative;
  line-height: 0;
  min-width: 48px;
}

/* Fixed aspect ratio scaling mode: wrapper fills parent */

:host([fixedaspectratioscaling]) .wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
}

canvas {
  width: var(--chart-width, 100%);
  height: var(--chart-height, auto);
  min-width: 48px;
  margin: 0 auto;
  display: block;
}

/* Fixed aspect ratio scaling mode: the canvas container must be a definite
   box, not shrink-to-fit. The wrapper is a column flex with align-items:
   center, so the container would otherwise size to the canvas' max-content
   width — and a canvas with an auto width and a definite height resolves
   against its intrinsic 2:1 ratio, capping the chart at height * 2. */

:host([fixedaspectratioscaling]) .canvas-and-slots-container {
  width: 100%;
}

/* Fixed aspect ratio scaling mode: canvas fills wrapper.

   \`!important\` is load-bearing, not a shortcut. Chart.js measures the
   container with getBoundingClientRect() — which is scaled by any ancestor
   CSS \`zoom\` — and writes that number straight back as an inline
   \`style="width/height: Npx"\`. The browser then scales that CSS-pixel value
   by the same zoom a second time, so the canvas lands at zoom² of its cell
   (64% at zoom 0.8, 156% at zoom 1.25). Overriding the inline style pins the
   canvas to the box the layout actually gave it at every zoom level; Chart.js
   keeps using its own measurement for the drawing buffer, which only affects
   raster resolution, not geometry.

   No auto margins here either: Chart.js subtracts the canvas' resolved
   margins from the container width, so centring it with \`margin: 0 auto\`
   makes the leftover space permanently unavailable to it. */

:host([fixedaspectratioscaling]) canvas {
  width: 100% !important;
  height: var(--chart-height, auto) !important;
  margin: 0;
}
`;var Y0=M`* {
  -webkit-tap-highlight-color: transparent;
}
/* Debug overlay styles - targets host element with showDebugOverlay attribute */
:host([showDebugOverlay]) .wrapper {
  box-shadow: 0 0 0 1px rgba(255, 0, 0, 0.25) inset;
  overflow: hidden;
}
:host([showDebugOverlay]) .wrapper::before {
  /* 256px circle (CHART_WIDTH - the actual chart area) */
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 254px;
  height: 254px;
  transform: translate(-50%, -50%);
  border: 1px dashed rgba(255, 0, 0, 0.25);
  border-radius: 50%;
  pointer-events: none;
  z-index: 10;
}
:host([showDebugOverlay][half]) .wrapper::before {
  /* 256px half-circle (CHART_WIDTH - the actual chart area, top half only) */
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 254px;
  height: 127px;
  transform: translate(-50%, -50%);
  border: 1px dashed rgba(255, 0, 0, 0.25);
  border-radius: 127px 127px 0 0;
  pointer-events: none;
  z-index: 10;
}
:host([showDebugOverlay]) .wrapper::after {
  /* 320px square (full canvas with default padding) */
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 318px;
  height: 318px;
  transform: translate(-50%, -50%);
  border: 1px dashed rgba(255, 0, 0, 0.25);
  pointer-events: none;
  z-index: 10;
}
`;var q0=M`* {
  -webkit-tap-highlight-color: transparent;
}

.legend {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-left: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px; /* TODO(CSS): 16px from Figma but brainstorm not enough height use case */
  min-height: 16px;
}

.legend-group {
  display: flex;
  align-items: center;
}

.legend-group--value-unit {
  align-items: baseline;
}

.legend-color {
  display: inline-flex;
  width: 16px;
  height: 16px;
  border-radius: var(
    --infographic-components-legend-item-indicator-border-radius
  );
  margin-right: 8px;
  flex-shrink: 0;
}

.legend-label,
.legend-value,
.legend-unit {
  display: inline-flex;
  font-family: var(--font-family-main);
  color: var(--element-neutral-color);
  white-space: nowrap;
}

.legend-label {
  margin-right: 24px;
  font-size: var(--global-typography-ui-body-font-size);
}

.legend-value {
  font-size: var(--global-typography-ui-body-font-size);
  color: var(--element-active-color);
}

.legend-unit {
  font-size: var(--global-typography-instrument-unit-font-size);
}
`;function Qn(e){return e+.5|0}var ri=(e,t,o)=>Math.max(Math.min(e,o),t);function Xn(e){return ri(Qn(e*2.55),0,255)}function ii(e){return ri(Qn(e*255),0,255)}function $r(e){return ri(Qn(e/2.55)/100,0,1)}function X0(e){return ri(Qn(e*100),0,100)}var Bo={0:0,1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9,A:10,B:11,C:12,D:13,E:14,F:15,a:10,b:11,c:12,d:13,e:14,f:15},yh=[..."0123456789ABCDEF"],t8=e=>yh[e&15],o8=e=>yh[(e&240)>>4]+yh[e&15],fc=e=>(e&240)>>4===(e&15),r8=e=>fc(e.r)&&fc(e.g)&&fc(e.b)&&fc(e.a);function i8(e){var t=e.length,o;return e[0]==="#"&&(t===4||t===5?o={r:255&Bo[e[1]]*17,g:255&Bo[e[2]]*17,b:255&Bo[e[3]]*17,a:t===5?Bo[e[4]]*17:255}:(t===7||t===9)&&(o={r:Bo[e[1]]<<4|Bo[e[2]],g:Bo[e[3]]<<4|Bo[e[4]],b:Bo[e[5]]<<4|Bo[e[6]],a:t===9?Bo[e[7]]<<4|Bo[e[8]]:255})),o}var s8=(e,t)=>e<255?t(e):"";function n8(e){var t=r8(e)?t8:o8;return e?"#"+t(e.r)+t(e.g)+t(e.b)+s8(e.a,t):void 0}var a8=/^(hsla?|hwb|hsv)\(\s*([-+.e\d]+)(?:deg)?[\s,]+([-+.e\d]+)%[\s,]+([-+.e\d]+)%(?:[\s,]+([-+.e\d]+)(%)?)?\s*\)$/;function ef(e,t,o){let r=t*Math.min(o,1-o),i=(s,n=(s+e/30)%12)=>o-r*Math.max(Math.min(n-3,9-n,1),-1);return[i(0),i(8),i(4)]}function l8(e,t,o){let r=(i,s=(i+e/60)%6)=>o-o*t*Math.max(Math.min(s,4-s,1),0);return[r(5),r(3),r(1)]}function c8(e,t,o){let r=ef(e,1,.5),i;for(t+o>1&&(i=1/(t+o),t*=i,o*=i),i=0;i<3;i++)r[i]*=1-t-o,r[i]+=t;return r}function d8(e,t,o,r,i){return e===i?(t-o)/r+(t<o?6:0):t===i?(o-e)/r+2:(e-t)/r+4}function Ch(e){let o=e.r/255,r=e.g/255,i=e.b/255,s=Math.max(o,r,i),n=Math.min(o,r,i),a=(s+n)/2,l,c,d;return s!==n&&(d=s-n,c=a>.5?d/(2-s-n):d/(s+n),l=d8(o,r,i,d,s),l=l*60+.5),[l|0,c||0,a]}function xh(e,t,o,r){return(Array.isArray(t)?e(t[0],t[1],t[2]):e(t,o,r)).map(ii)}function _h(e,t,o){return xh(ef,e,t,o)}function h8(e,t,o){return xh(c8,e,t,o)}function p8(e,t,o){return xh(l8,e,t,o)}function tf(e){return(e%360+360)%360}function u8(e){let t=a8.exec(e),o=255,r;if(!t)return;t[5]!==r&&(o=t[6]?Xn(+t[5]):ii(+t[5]));let i=tf(+t[2]),s=+t[3]/100,n=+t[4]/100;return t[1]==="hwb"?r=h8(i,s,n):t[1]==="hsv"?r=p8(i,s,n):r=_h(i,s,n),{r:r[0],g:r[1],b:r[2],a:o}}function f8(e,t){var o=Ch(e);o[0]=tf(o[0]+t),o=_h(o),e.r=o[0],e.g=o[1],e.b=o[2]}function g8(e){if(!e)return;let t=Ch(e),o=t[0],r=X0(t[1]),i=X0(t[2]);return e.a<255?`hsla(${o}, ${r}%, ${i}%, ${$r(e.a)})`:`hsl(${o}, ${r}%, ${i}%)`}var K0={x:"dark",Z:"light",Y:"re",X:"blu",W:"gr",V:"medium",U:"slate",A:"ee",T:"ol",S:"or",B:"ra",C:"lateg",D:"ights",R:"in",Q:"turquois",E:"hi",P:"ro",O:"al",N:"le",M:"de",L:"yello",F:"en",K:"ch",G:"arks",H:"ea",I:"ightg",J:"wh"},Q0={OiceXe:"f0f8ff",antiquewEte:"faebd7",aqua:"ffff",aquamarRe:"7fffd4",azuY:"f0ffff",beige:"f5f5dc",bisque:"ffe4c4",black:"0",blanKedOmond:"ffebcd",Xe:"ff",XeviTet:"8a2be2",bPwn:"a52a2a",burlywood:"deb887",caMtXe:"5f9ea0",KartYuse:"7fff00",KocTate:"d2691e",cSO:"ff7f50",cSnflowerXe:"6495ed",cSnsilk:"fff8dc",crimson:"dc143c",cyan:"ffff",xXe:"8b",xcyan:"8b8b",xgTMnPd:"b8860b",xWay:"a9a9a9",xgYF:"6400",xgYy:"a9a9a9",xkhaki:"bdb76b",xmagFta:"8b008b",xTivegYF:"556b2f",xSange:"ff8c00",xScEd:"9932cc",xYd:"8b0000",xsOmon:"e9967a",xsHgYF:"8fbc8f",xUXe:"483d8b",xUWay:"2f4f4f",xUgYy:"2f4f4f",xQe:"ced1",xviTet:"9400d3",dAppRk:"ff1493",dApskyXe:"bfff",dimWay:"696969",dimgYy:"696969",dodgerXe:"1e90ff",fiYbrick:"b22222",flSOwEte:"fffaf0",foYstWAn:"228b22",fuKsia:"ff00ff",gaRsbSo:"dcdcdc",ghostwEte:"f8f8ff",gTd:"ffd700",gTMnPd:"daa520",Way:"808080",gYF:"8000",gYFLw:"adff2f",gYy:"808080",honeyMw:"f0fff0",hotpRk:"ff69b4",RdianYd:"cd5c5c",Rdigo:"4b0082",ivSy:"fffff0",khaki:"f0e68c",lavFMr:"e6e6fa",lavFMrXsh:"fff0f5",lawngYF:"7cfc00",NmoncEffon:"fffacd",ZXe:"add8e6",ZcSO:"f08080",Zcyan:"e0ffff",ZgTMnPdLw:"fafad2",ZWay:"d3d3d3",ZgYF:"90ee90",ZgYy:"d3d3d3",ZpRk:"ffb6c1",ZsOmon:"ffa07a",ZsHgYF:"20b2aa",ZskyXe:"87cefa",ZUWay:"778899",ZUgYy:"778899",ZstAlXe:"b0c4de",ZLw:"ffffe0",lime:"ff00",limegYF:"32cd32",lRF:"faf0e6",magFta:"ff00ff",maPon:"800000",VaquamarRe:"66cdaa",VXe:"cd",VScEd:"ba55d3",VpurpN:"9370db",VsHgYF:"3cb371",VUXe:"7b68ee",VsprRggYF:"fa9a",VQe:"48d1cc",VviTetYd:"c71585",midnightXe:"191970",mRtcYam:"f5fffa",mistyPse:"ffe4e1",moccasR:"ffe4b5",navajowEte:"ffdead",navy:"80",Tdlace:"fdf5e6",Tive:"808000",TivedBb:"6b8e23",Sange:"ffa500",SangeYd:"ff4500",ScEd:"da70d6",pOegTMnPd:"eee8aa",pOegYF:"98fb98",pOeQe:"afeeee",pOeviTetYd:"db7093",papayawEp:"ffefd5",pHKpuff:"ffdab9",peru:"cd853f",pRk:"ffc0cb",plum:"dda0dd",powMrXe:"b0e0e6",purpN:"800080",YbeccapurpN:"663399",Yd:"ff0000",Psybrown:"bc8f8f",PyOXe:"4169e1",saddNbPwn:"8b4513",sOmon:"fa8072",sandybPwn:"f4a460",sHgYF:"2e8b57",sHshell:"fff5ee",siFna:"a0522d",silver:"c0c0c0",skyXe:"87ceeb",UXe:"6a5acd",UWay:"708090",UgYy:"708090",snow:"fffafa",sprRggYF:"ff7f",stAlXe:"4682b4",tan:"d2b48c",teO:"8080",tEstN:"d8bfd8",tomato:"ff6347",Qe:"40e0d0",viTet:"ee82ee",JHt:"f5deb3",wEte:"ffffff",wEtesmoke:"f5f5f5",Lw:"ffff00",LwgYF:"9acd32"};function m8(){let e={},t=Object.keys(Q0),o=Object.keys(K0),r,i,s,n,a;for(r=0;r<t.length;r++){for(n=a=t[r],i=0;i<o.length;i++)s=o[i],a=a.replace(s,K0[s]);s=parseInt(Q0[n],16),e[a]=[s>>16&255,s>>8&255,s&255]}return e}var gc;function v8(e){gc||(gc=m8(),gc.transparent=[0,0,0,0]);let t=gc[e.toLowerCase()];return t&&{r:t[0],g:t[1],b:t[2],a:t.length===4?t[3]:255}}var b8=/^rgba?\(\s*([-+.\d]+)(%)?[\s,]+([-+.e\d]+)(%)?[\s,]+([-+.e\d]+)(%)?(?:[\s,/]+([-+.e\d]+)(%)?)?\s*\)$/;function w8(e){let t=b8.exec(e),o=255,r,i,s;if(t){if(t[7]!==r){let n=+t[7];o=t[8]?Xn(n):ri(n*255,0,255)}return r=+t[1],i=+t[3],s=+t[5],r=255&(t[2]?Xn(r):ri(r,0,255)),i=255&(t[4]?Xn(i):ri(i,0,255)),s=255&(t[6]?Xn(s):ri(s,0,255)),{r,g:i,b:s,a:o}}}function y8(e){return e&&(e.a<255?`rgba(${e.r}, ${e.g}, ${e.b}, ${$r(e.a)})`:`rgb(${e.r}, ${e.g}, ${e.b})`)}var wh=e=>e<=.0031308?e*12.92:Math.pow(e,1/2.4)*1.055-.055,js=e=>e<=.04045?e/12.92:Math.pow((e+.055)/1.055,2.4);function C8(e,t,o){let r=js($r(e.r)),i=js($r(e.g)),s=js($r(e.b));return{r:ii(wh(r+o*(js($r(t.r))-r))),g:ii(wh(i+o*(js($r(t.g))-i))),b:ii(wh(s+o*(js($r(t.b))-s))),a:e.a+o*(t.a-e.a)}}function mc(e,t,o){if(e){let r=Ch(e);r[t]=Math.max(0,Math.min(r[t]+r[t]*o,t===0?360:1)),r=_h(r),e.r=r[0],e.g=r[1],e.b=r[2]}}function of(e,t){return e&&Object.assign(t||{},e)}function J0(e){var t={r:0,g:0,b:0,a:255};return Array.isArray(e)?e.length>=3&&(t={r:e[0],g:e[1],b:e[2],a:255},e.length>3&&(t.a=ii(e[3]))):(t=of(e,{r:0,g:0,b:0,a:1}),t.a=ii(t.a)),t}function x8(e){return e.charAt(0)==="r"?w8(e):u8(e)}var Kn=class e{constructor(t){if(t instanceof e)return t;let o=typeof t,r;o==="object"?r=J0(t):o==="string"&&(r=i8(t)||v8(t)||x8(t)),this._rgb=r,this._valid=!!r}get valid(){return this._valid}get rgb(){var t=of(this._rgb);return t&&(t.a=$r(t.a)),t}set rgb(t){this._rgb=J0(t)}rgbString(){return this._valid?y8(this._rgb):void 0}hexString(){return this._valid?n8(this._rgb):void 0}hslString(){return this._valid?g8(this._rgb):void 0}mix(t,o){if(t){let r=this.rgb,i=t.rgb,s,n=o===s?.5:o,a=2*n-1,l=r.a-i.a,c=((a*l===-1?a:(a+l)/(1+a*l))+1)/2;s=1-c,r.r=255&c*r.r+s*i.r+.5,r.g=255&c*r.g+s*i.g+.5,r.b=255&c*r.b+s*i.b+.5,r.a=n*r.a+(1-n)*i.a,this.rgb=r}return this}interpolate(t,o){return t&&(this._rgb=C8(this._rgb,t._rgb,o)),this}clone(){return new e(this.rgb)}alpha(t){return this._rgb.a=ii(t),this}clearer(t){let o=this._rgb;return o.a*=1-t,this}greyscale(){let t=this._rgb,o=Qn(t.r*.3+t.g*.59+t.b*.11);return t.r=t.g=t.b=o,this}opaquer(t){let o=this._rgb;return o.a*=1+t,this}negate(){let t=this._rgb;return t.r=255-t.r,t.g=255-t.g,t.b=255-t.b,this}lighten(t){return mc(this._rgb,2,t),this}darken(t){return mc(this._rgb,2,-t),this}saturate(t){return mc(this._rgb,1,t),this}desaturate(t){return mc(this._rgb,1,-t),this}rotate(t){return f8(this._rgb,t),this}};function lr(){}var ff=(()=>{let e=0;return()=>e++})();function Ze(e){return e==null}function ct(e){if(Array.isArray&&Array.isArray(e))return!0;let t=Object.prototype.toString.call(e);return t.slice(0,7)==="[object"&&t.slice(-6)==="Array]"}function Ve(e){return e!==null&&Object.prototype.toString.call(e)==="[object Object]"}function ht(e){return(typeof e=="number"||e instanceof Number)&&isFinite(+e)}function po(e,t){return ht(e)?e:t}function ze(e,t){return typeof e>"u"?t:e}var gf=(e,t)=>typeof e=="string"&&e.endsWith("%")?parseFloat(e)/100*t:+e;function pt(e,t,o){if(e&&typeof e.call=="function")return e.apply(o,t)}function Fe(e,t,o,r){let i,s,n;if(ct(e))if(s=e.length,r)for(i=s-1;i>=0;i--)t.call(o,e[i],i);else for(i=0;i<s;i++)t.call(o,e[i],i);else if(Ve(e))for(n=Object.keys(e),s=n.length,i=0;i<s;i++)t.call(o,e[n[i]],n[i])}function ta(e,t){let o,r,i,s;if(!e||!t||e.length!==t.length)return!1;for(o=0,r=e.length;o<r;++o)if(i=e[o],s=t[o],i.datasetIndex!==s.datasetIndex||i.index!==s.index)return!1;return!0}function yc(e){if(ct(e))return e.map(yc);if(Ve(e)){let t=Object.create(null),o=Object.keys(e),r=o.length,i=0;for(;i<r;++i)t[o[i]]=yc(e[o[i]]);return t}return e}function mf(e){return["__proto__","prototype","constructor"].indexOf(e)===-1}function _8(e,t,o,r){if(!mf(e))return;let i=t[e],s=o[e];Ve(i)&&Ve(s)?Us(i,s,r):t[e]=yc(s)}function Us(e,t,o){let r=ct(t)?t:[t],i=r.length;if(!Ve(e))return e;o=o||{};let s=o.merger||_8,n;for(let a=0;a<i;++a){if(n=r[a],!Ve(n))continue;let l=Object.keys(n);for(let c=0,d=l.length;c<d;++c)s(l[c],e,n,o)}return e}function Ys(e,t){return Us(e,t,{merger:k8})}function k8(e,t,o){if(!mf(e))return;let r=t[e],i=o[e];Ve(r)&&Ve(i)?Ys(r,i):Object.prototype.hasOwnProperty.call(t,e)||(t[e]=yc(i))}var rf={"":e=>e,x:e=>e.x,y:e=>e.y};function L8(e){let t=e.split("."),o=[],r="";for(let i of t)r+=i,r.endsWith("\\")?r=r.slice(0,-1)+".":(o.push(r),r="");return o}function S8(e){let t=L8(e);return o=>{for(let r of t){if(r==="")break;o=o&&o[r]}return o}}function oa(e,t){return(rf[t]||(rf[t]=S8(t)))(e)}function kc(e){return e.charAt(0).toUpperCase()+e.slice(1)}var ra=e=>typeof e<"u",Ar=e=>typeof e=="function",Mh=(e,t)=>{if(e.size!==t.size)return!1;for(let o of e)if(!t.has(o))return!1;return!0};function vf(e){return e.type==="mouseup"||e.type==="click"||e.type==="contextmenu"}var Ue=Math.PI,vt=2*Ue,M8=vt+Ue,Cc=Number.POSITIVE_INFINITY,$8=Ue/180,Ct=Ue/2,Yi=Ue/4,sf=Ue*2/3,Pr=Math.log10,Xi=Math.sign;function qs(e,t,o){return Math.abs(e-t)<o}function $h(e){let t=Math.round(e);e=qs(e,t,e/1e3)?t:e;let o=Math.pow(10,Math.floor(Pr(e))),r=e/o;return(r<=1?1:r<=2?2:r<=5?5:10)*o}function bf(e){let t=[],o=Math.sqrt(e),r;for(r=1;r<o;r++)e%r===0&&(t.push(r),t.push(e/r));return o===(o|0)&&t.push(o),t.sort((i,s)=>i-s).pop(),t}function A8(e){return typeof e=="symbol"||typeof e=="object"&&e!==null&&!(Symbol.toPrimitive in e||"toString"in e||"valueOf"in e)}function Xs(e){return!A8(e)&&!isNaN(parseFloat(e))&&isFinite(e)}function wf(e,t){let o=Math.round(e);return o-t<=e&&o+t>=e}function Ah(e,t,o){let r,i,s;for(r=0,i=e.length;r<i;r++)s=e[r][o],isNaN(s)||(t.min=Math.min(t.min,s),t.max=Math.max(t.max,s))}function Or(e){return e*(Ue/180)}function Lc(e){return e*(180/Ue)}function Ph(e){if(!ht(e))return;let t=1,o=0;for(;Math.round(e*t)/t!==e;)t*=10,o++;return o}function Oh(e,t){let o=t.x-e.x,r=t.y-e.y,i=Math.sqrt(o*o+r*r),s=Math.atan2(r,o);return s<-.5*Ue&&(s+=vt),{angle:s,distance:i}}function xc(e,t){return Math.sqrt(Math.pow(t.x-e.x,2)+Math.pow(t.y-e.y,2))}function P8(e,t){return(e-t+M8)%vt-Ue}function Ft(e){return(e%vt+vt)%vt}function Sc(e,t,o,r){let i=Ft(e),s=Ft(t),n=Ft(o),a=Ft(s-i),l=Ft(n-i),c=Ft(i-s),d=Ft(i-n);return i===s||i===n||r&&s===n||a>l&&c<d}function Yt(e,t,o){return Math.max(t,Math.min(o,e))}function yf(e){return Yt(e,-32768,32767)}function Mc(e,t,o,r=1e-6){return e>=Math.min(t,o)-r&&e<=Math.max(t,o)+r}function $c(e,t,o){o=o||(n=>e[n]<t);let r=e.length-1,i=0,s;for(;r-i>1;)s=i+r>>1,o(s)?i=s:r=s;return{lo:i,hi:r}}var ni=(e,t,o,r)=>$c(e,o,r?i=>{let s=e[i][t];return s<o||s===o&&e[i+1][t]===o}:i=>e[i][t]<o),Cf=(e,t,o)=>$c(e,o,r=>e[r][t]>=o);function xf(e,t,o){let r=0,i=e.length;for(;r<i&&e[r]<t;)r++;for(;i>r&&e[i-1]>o;)i--;return r>0||i<e.length?e.slice(r,i):e}var _f=["push","pop","shift","splice","unshift"];function kf(e,t){if(e._chartjs){e._chartjs.listeners.push(t);return}Object.defineProperty(e,"_chartjs",{configurable:!0,enumerable:!1,value:{listeners:[t]}}),_f.forEach(o=>{let r="_onData"+kc(o),i=e[o];Object.defineProperty(e,o,{configurable:!0,enumerable:!1,value(...s){let n=i.apply(this,s);return e._chartjs.listeners.forEach(a=>{typeof a[r]=="function"&&a[r](...s)}),n}})})}function Vh(e,t){let o=e._chartjs;if(!o)return;let r=o.listeners,i=r.indexOf(t);i!==-1&&r.splice(i,1),!(r.length>0)&&(_f.forEach(s=>{delete e[s]}),delete e._chartjs)}function Lf(e){let t=new Set(e);return t.size===e.length?e:Array.from(t)}var Th=(function(){return typeof window>"u"?function(e){return e()}:window.requestAnimationFrame})();function Dh(e,t){let o=[],r=!1;return function(...i){o=i,r||(r=!0,Th.call(window,()=>{r=!1,e.apply(t,o)}))}}function Sf(e,t){let o;return function(...r){return t?(clearTimeout(o),o=setTimeout(e,t,r)):e.apply(this,r),t}}var Mf=e=>e==="start"?"left":e==="end"?"right":"center",Eh=(e,t,o)=>e==="start"?t:e==="end"?o:(t+o)/2;function $f(e,t,o){let r=t.length,i=0,s=r;if(e._sorted){let{iScale:n,vScale:a,_parsed:l}=e,c=e.dataset&&e.dataset.options?e.dataset.options.spanGaps:null,d=n.axis,{min:p,max:u,minDefined:m,maxDefined:b}=n.getUserBounds();if(m){if(i=Math.min(ni(l,d,p).lo,o?r:ni(t,d,n.getPixelForValue(p)).lo),c){let C=l.slice(0,i+1).reverse().findIndex(y=>!Ze(y[a.axis]));i-=Math.max(0,C)}i=Yt(i,0,r-1)}if(b){let C=Math.max(ni(l,n.axis,u,!0).hi+1,o?0:ni(t,d,n.getPixelForValue(u),!0).hi+1);if(c){let y=l.slice(C-1).findIndex(k=>!Ze(k[a.axis]));C+=Math.max(0,y)}s=Yt(C,i,r)-i}else s=r-i}return{start:i,count:s}}function Af(e){let{xScale:t,yScale:o,_scaleRanges:r}=e,i={xmin:t.min,xmax:t.max,ymin:o.min,ymax:o.max};if(!r)return e._scaleRanges=i,!0;let s=r.xmin!==t.min||r.xmax!==t.max||r.ymin!==o.min||r.ymax!==o.max;return Object.assign(r,i),s}var vc=e=>e===0||e===1,nf=(e,t,o)=>-(Math.pow(2,10*(e-=1))*Math.sin((e-t)*vt/o)),af=(e,t,o)=>Math.pow(2,-10*e)*Math.sin((e-t)*vt/o)+1,Ws={linear:e=>e,easeInQuad:e=>e*e,easeOutQuad:e=>-e*(e-2),easeInOutQuad:e=>(e/=.5)<1?.5*e*e:-.5*(--e*(e-2)-1),easeInCubic:e=>e*e*e,easeOutCubic:e=>(e-=1)*e*e+1,easeInOutCubic:e=>(e/=.5)<1?.5*e*e*e:.5*((e-=2)*e*e+2),easeInQuart:e=>e*e*e*e,easeOutQuart:e=>-((e-=1)*e*e*e-1),easeInOutQuart:e=>(e/=.5)<1?.5*e*e*e*e:-.5*((e-=2)*e*e*e-2),easeInQuint:e=>e*e*e*e*e,easeOutQuint:e=>(e-=1)*e*e*e*e+1,easeInOutQuint:e=>(e/=.5)<1?.5*e*e*e*e*e:.5*((e-=2)*e*e*e*e+2),easeInSine:e=>-Math.cos(e*Ct)+1,easeOutSine:e=>Math.sin(e*Ct),easeInOutSine:e=>-.5*(Math.cos(Ue*e)-1),easeInExpo:e=>e===0?0:Math.pow(2,10*(e-1)),easeOutExpo:e=>e===1?1:-Math.pow(2,-10*e)+1,easeInOutExpo:e=>vc(e)?e:e<.5?.5*Math.pow(2,10*(e*2-1)):.5*(-Math.pow(2,-10*(e*2-1))+2),easeInCirc:e=>e>=1?e:-(Math.sqrt(1-e*e)-1),easeOutCirc:e=>Math.sqrt(1-(e-=1)*e),easeInOutCirc:e=>(e/=.5)<1?-.5*(Math.sqrt(1-e*e)-1):.5*(Math.sqrt(1-(e-=2)*e)+1),easeInElastic:e=>vc(e)?e:nf(e,.075,.3),easeOutElastic:e=>vc(e)?e:af(e,.075,.3),easeInOutElastic(e){return vc(e)?e:e<.5?.5*nf(e*2,.1125,.45):.5+.5*af(e*2-1,.1125,.45)},easeInBack(e){return e*e*((1.70158+1)*e-1.70158)},easeOutBack(e){return(e-=1)*e*((1.70158+1)*e+1.70158)+1},easeInOutBack(e){let t=1.70158;return(e/=.5)<1?.5*(e*e*(((t*=1.525)+1)*e-t)):.5*((e-=2)*e*(((t*=1.525)+1)*e+t)+2)},easeInBounce:e=>1-Ws.easeOutBounce(1-e),easeOutBounce(e){return e<1/2.75?7.5625*e*e:e<2/2.75?7.5625*(e-=1.5/2.75)*e+.75:e<2.5/2.75?7.5625*(e-=2.25/2.75)*e+.9375:7.5625*(e-=2.625/2.75)*e+.984375},easeInOutBounce:e=>e<.5?Ws.easeInBounce(e*2)*.5:Ws.easeOutBounce(e*2-1)*.5+.5};function Rh(e){if(e&&typeof e=="object"){let t=e.toString();return t==="[object CanvasPattern]"||t==="[object CanvasGradient]"}return!1}function zh(e){return Rh(e)?e:new Kn(e)}function kh(e){return Rh(e)?e:new Kn(e).saturate(.5).darken(.1).hexString()}var O8=["x","y","borderWidth","radius","tension"],V8=["color","borderColor","backgroundColor"];function T8(e){e.set("animation",{delay:void 0,duration:1e3,easing:"easeOutQuart",fn:void 0,from:void 0,loop:void 0,to:void 0,type:void 0}),e.describe("animation",{_fallback:!1,_indexable:!1,_scriptable:t=>t!=="onProgress"&&t!=="onComplete"&&t!=="fn"}),e.set("animations",{colors:{type:"color",properties:V8},numbers:{type:"number",properties:O8}}),e.describe("animations",{_fallback:"animation"}),e.set("transitions",{active:{animation:{duration:400}},resize:{animation:{duration:0}},show:{animations:{colors:{from:"transparent"},visible:{type:"boolean",duration:0}}},hide:{animations:{colors:{to:"transparent"},visible:{type:"boolean",easing:"linear",fn:t=>t|0}}}})}function D8(e){e.set("layout",{autoPadding:!0,padding:{top:0,right:0,bottom:0,left:0}})}var lf=new Map;function E8(e,t){t=t||{};let o=e+JSON.stringify(t),r=lf.get(o);return r||(r=new Intl.NumberFormat(e,t),lf.set(o,r)),r}function Ac(e,t,o){return E8(t,o).format(e)}var Pf={values(e){return ct(e)?e:""+e},numeric(e,t,o){if(e===0)return"0";let r=this.chart.options.locale,i,s=e;if(o.length>1){let c=Math.max(Math.abs(o[0].value),Math.abs(o[o.length-1].value));(c<1e-4||c>1e15)&&(i="scientific"),s=R8(e,o)}let n=Pr(Math.abs(s)),a=isNaN(n)?1:Math.max(Math.min(-1*Math.floor(n),20),0),l={notation:i,minimumFractionDigits:a,maximumFractionDigits:a};return Object.assign(l,this.options.ticks.format),Ac(e,r,l)},logarithmic(e,t,o){if(e===0)return"0";let r=o[t].significand||e/Math.pow(10,Math.floor(Pr(e)));return[1,2,3,5,10,15].includes(r)||t>.8*o.length?Pf.numeric.call(this,e,t,o):""}};function R8(e,t){let o=t.length>3?t[2].value-t[1].value:t[1].value-t[0].value;return Math.abs(o)>=1&&e!==Math.floor(e)&&(o=e-Math.floor(e)),o}var ia={formatters:Pf};function z8(e){e.set("scale",{display:!0,offset:!1,reverse:!1,beginAtZero:!1,bounds:"ticks",clip:!0,grace:0,grid:{display:!0,lineWidth:1,drawOnChartArea:!0,drawTicks:!0,tickLength:8,tickWidth:(t,o)=>o.lineWidth,tickColor:(t,o)=>o.color,offset:!1},border:{display:!0,dash:[],dashOffset:0,width:1},title:{display:!1,text:"",padding:{top:4,bottom:4}},ticks:{minRotation:0,maxRotation:50,mirror:!1,textStrokeWidth:0,textStrokeColor:"",padding:3,display:!0,autoSkip:!0,autoSkipPadding:3,labelOffset:0,callback:ia.formatters.values,minor:{},major:{},align:"center",crossAlign:"near",showLabelBackdrop:!1,backdropColor:"rgba(255, 255, 255, 0.75)",backdropPadding:2}}),e.route("scale.ticks","color","","color"),e.route("scale.grid","color","","borderColor"),e.route("scale.border","color","","borderColor"),e.route("scale.title","color","","color"),e.describe("scale",{_fallback:!1,_scriptable:t=>!t.startsWith("before")&&!t.startsWith("after")&&t!=="callback"&&t!=="parser",_indexable:t=>t!=="borderDash"&&t!=="tickBorderDash"&&t!=="dash"}),e.describe("scales",{_fallback:"scale"}),e.describe("scale.ticks",{_scriptable:t=>t!=="backdropPadding"&&t!=="callback",_indexable:t=>t!=="backdropPadding"})}var li=Object.create(null),Pc=Object.create(null);function Jn(e,t){if(!t)return e;let o=t.split(".");for(let r=0,i=o.length;r<i;++r){let s=o[r];e=e[s]||(e[s]=Object.create(null))}return e}function Lh(e,t,o){return typeof t=="string"?Us(Jn(e,t),o):Us(Jn(e,""),t)}var Sh=class{constructor(t,o){this.animation=void 0,this.backgroundColor="rgba(0,0,0,0.1)",this.borderColor="rgba(0,0,0,0.1)",this.color="#666",this.datasets={},this.devicePixelRatio=r=>r.chart.platform.getDevicePixelRatio(),this.elements={},this.events=["mousemove","mouseout","click","touchstart","touchmove"],this.font={family:"'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",size:12,style:"normal",lineHeight:1.2,weight:null},this.hover={},this.hoverBackgroundColor=(r,i)=>kh(i.backgroundColor),this.hoverBorderColor=(r,i)=>kh(i.borderColor),this.hoverColor=(r,i)=>kh(i.color),this.indexAxis="x",this.interaction={mode:"nearest",intersect:!0,includeInvisible:!1},this.maintainAspectRatio=!0,this.onHover=null,this.onClick=null,this.parsing=!0,this.plugins={},this.responsive=!0,this.scale=void 0,this.scales={},this.showLine=!0,this.drawActiveElementsOnTop=!0,this.describe(t),this.apply(o)}set(t,o){return Lh(this,t,o)}get(t){return Jn(this,t)}describe(t,o){return Lh(Pc,t,o)}override(t,o){return Lh(li,t,o)}route(t,o,r,i){let s=Jn(this,t),n=Jn(this,r),a="_"+o;Object.defineProperties(s,{[a]:{value:s[o],writable:!0},[o]:{enumerable:!0,get(){let l=this[a],c=n[i];return Ve(l)?Object.assign({},c,l):ze(l,c)},set(l){this[a]=l}}})}apply(t){t.forEach(o=>o(this))}},gt=new Sh({_scriptable:e=>!e.startsWith("on"),_indexable:e=>e!=="events",hover:{_fallback:"interaction"},interaction:{_scriptable:!1,_indexable:!1}},[T8,D8,z8]);function H8(e){return!e||Ze(e.size)||Ze(e.family)?null:(e.style?e.style+" ":"")+(e.weight?e.weight+" ":"")+e.size+"px "+e.family}function ea(e,t,o,r,i){let s=t[i];return s||(s=t[i]=e.measureText(i).width,o.push(i)),s>r&&(r=s),r}function Of(e,t,o,r){r=r||{};let i=r.data=r.data||{},s=r.garbageCollect=r.garbageCollect||[];r.font!==t&&(i=r.data={},s=r.garbageCollect=[],r.font=t),e.save(),e.font=t;let n=0,a=o.length,l,c,d,p,u;for(l=0;l<a;l++)if(p=o[l],p!=null&&!ct(p))n=ea(e,i,s,n,p);else if(ct(p))for(c=0,d=p.length;c<d;c++)u=p[c],u!=null&&!ct(u)&&(n=ea(e,i,s,n,u));e.restore();let m=s.length/2;if(m>o.length){for(l=0;l<m;l++)delete i[s[l]];s.splice(0,m)}return n}function ci(e,t,o){let r=e.currentDevicePixelRatio,i=o!==0?Math.max(o/2,.5):0;return Math.round((t-i)*r)/r+i}function Hh(e,t){!t&&!e||(t=t||e.getContext("2d"),t.save(),t.resetTransform(),t.clearRect(0,0,e.width,e.height),t.restore())}function Oc(e,t,o,r){Vf(e,t,o,r,null)}function Vf(e,t,o,r,i){let s,n,a,l,c,d,p,u,m=t.pointStyle,b=t.rotation,C=t.radius,y=(b||0)*$8;if(m&&typeof m=="object"&&(s=m.toString(),s==="[object HTMLImageElement]"||s==="[object HTMLCanvasElement]")){e.save(),e.translate(o,r),e.rotate(y),e.drawImage(m,-m.width/2,-m.height/2,m.width,m.height),e.restore();return}if(!(isNaN(C)||C<=0)){switch(e.beginPath(),m){default:i?e.ellipse(o,r,i/2,C,0,0,vt):e.arc(o,r,C,0,vt),e.closePath();break;case"triangle":d=i?i/2:C,e.moveTo(o+Math.sin(y)*d,r-Math.cos(y)*C),y+=sf,e.lineTo(o+Math.sin(y)*d,r-Math.cos(y)*C),y+=sf,e.lineTo(o+Math.sin(y)*d,r-Math.cos(y)*C),e.closePath();break;case"rectRounded":c=C*.516,l=C-c,n=Math.cos(y+Yi)*l,p=Math.cos(y+Yi)*(i?i/2-c:l),a=Math.sin(y+Yi)*l,u=Math.sin(y+Yi)*(i?i/2-c:l),e.arc(o-p,r-a,c,y-Ue,y-Ct),e.arc(o+u,r-n,c,y-Ct,y),e.arc(o+p,r+a,c,y,y+Ct),e.arc(o-u,r+n,c,y+Ct,y+Ue),e.closePath();break;case"rect":if(!b){l=Math.SQRT1_2*C,d=i?i/2:l,e.rect(o-d,r-l,2*d,2*l);break}y+=Yi;case"rectRot":p=Math.cos(y)*(i?i/2:C),n=Math.cos(y)*C,a=Math.sin(y)*C,u=Math.sin(y)*(i?i/2:C),e.moveTo(o-p,r-a),e.lineTo(o+u,r-n),e.lineTo(o+p,r+a),e.lineTo(o-u,r+n),e.closePath();break;case"crossRot":y+=Yi;case"cross":p=Math.cos(y)*(i?i/2:C),n=Math.cos(y)*C,a=Math.sin(y)*C,u=Math.sin(y)*(i?i/2:C),e.moveTo(o-p,r-a),e.lineTo(o+p,r+a),e.moveTo(o+u,r-n),e.lineTo(o-u,r+n);break;case"star":p=Math.cos(y)*(i?i/2:C),n=Math.cos(y)*C,a=Math.sin(y)*C,u=Math.sin(y)*(i?i/2:C),e.moveTo(o-p,r-a),e.lineTo(o+p,r+a),e.moveTo(o+u,r-n),e.lineTo(o-u,r+n),y+=Yi,p=Math.cos(y)*(i?i/2:C),n=Math.cos(y)*C,a=Math.sin(y)*C,u=Math.sin(y)*(i?i/2:C),e.moveTo(o-p,r-a),e.lineTo(o+p,r+a),e.moveTo(o+u,r-n),e.lineTo(o-u,r+n);break;case"line":n=i?i/2:Math.cos(y)*C,a=Math.sin(y)*C,e.moveTo(o-n,r-a),e.lineTo(o+n,r+a);break;case"dash":e.moveTo(o,r),e.lineTo(o+Math.cos(y)*(i?i/2:C),r+Math.sin(y)*C);break;case!1:e.closePath();break}e.fill(),t.borderWidth>0&&e.stroke()}}function ar(e,t,o){return o=o||.5,!t||e&&e.x>t.left-o&&e.x<t.right+o&&e.y>t.top-o&&e.y<t.bottom+o}function Vc(e,t){e.save(),e.beginPath(),e.rect(t.left,t.top,t.right-t.left,t.bottom-t.top),e.clip()}function Tc(e){e.restore()}function Tf(e,t,o,r,i){if(!t)return e.lineTo(o.x,o.y);if(i==="middle"){let s=(t.x+o.x)/2;e.lineTo(s,t.y),e.lineTo(s,o.y)}else i==="after"!=!!r?e.lineTo(t.x,o.y):e.lineTo(o.x,t.y);e.lineTo(o.x,o.y)}function Df(e,t,o,r){if(!t)return e.lineTo(o.x,o.y);e.bezierCurveTo(r?t.cp1x:t.cp2x,r?t.cp1y:t.cp2y,r?o.cp2x:o.cp1x,r?o.cp2y:o.cp1y,o.x,o.y)}function B8(e,t){t.translation&&e.translate(t.translation[0],t.translation[1]),Ze(t.rotation)||e.rotate(t.rotation),t.color&&(e.fillStyle=t.color),t.textAlign&&(e.textAlign=t.textAlign),t.textBaseline&&(e.textBaseline=t.textBaseline)}function I8(e,t,o,r,i){if(i.strikethrough||i.underline){let s=e.measureText(r),n=t-s.actualBoundingBoxLeft,a=t+s.actualBoundingBoxRight,l=o-s.actualBoundingBoxAscent,c=o+s.actualBoundingBoxDescent,d=i.strikethrough?(l+c)/2:c;e.strokeStyle=e.fillStyle,e.beginPath(),e.lineWidth=i.decorationWidth||2,e.moveTo(n,d),e.lineTo(a,d),e.stroke()}}function Z8(e,t){let o=e.fillStyle;e.fillStyle=t.color,e.fillRect(t.left,t.top,t.width,t.height),e.fillStyle=o}function sa(e,t,o,r,i,s={}){let n=ct(t)?t:[t],a=s.strokeWidth>0&&s.strokeColor!=="",l,c;for(e.save(),e.font=i.string,B8(e,s),l=0;l<n.length;++l)c=n[l],s.backdrop&&Z8(e,s.backdrop),a&&(s.strokeColor&&(e.strokeStyle=s.strokeColor),Ze(s.strokeWidth)||(e.lineWidth=s.strokeWidth),e.strokeText(c,o,r,s.maxWidth)),e.fillText(c,o,r,s.maxWidth),I8(e,o,r,c,s),r+=Number(i.lineHeight);e.restore()}function Dc(e,t){let{x:o,y:r,w:i,h:s,radius:n}=t;e.arc(o+n.topLeft,r+n.topLeft,n.topLeft,1.5*Ue,Ue,!0),e.lineTo(o,r+s-n.bottomLeft),e.arc(o+n.bottomLeft,r+s-n.bottomLeft,n.bottomLeft,Ue,Ct,!0),e.lineTo(o+i-n.bottomRight,r+s),e.arc(o+i-n.bottomRight,r+s-n.bottomRight,n.bottomRight,Ct,0,!0),e.lineTo(o+i,r+n.topRight),e.arc(o+i-n.topRight,r+n.topRight,n.topRight,0,-Ct,!0),e.lineTo(o+n.topLeft,r)}var F8=/^(normal|(\d+(?:\.\d+)?)(px|em|%)?)$/,N8=/^(normal|italic|initial|inherit|unset|(oblique( -?[0-9]?[0-9]deg)?))$/;function j8(e,t){let o=(""+e).match(F8);if(!o||o[1]==="normal")return t*1.2;switch(e=+o[2],o[3]){case"px":return e;case"%":e/=100;break}return t*e}var W8=e=>+e||0;function Ec(e,t){let o={},r=Ve(t),i=r?Object.keys(t):t,s=Ve(e)?r?n=>ze(e[n],e[t[n]]):n=>e[n]:()=>e;for(let n of i)o[n]=W8(s(n));return o}function Ef(e){return Ec(e,{top:"y",right:"x",bottom:"y",left:"x"})}function Ks(e){return Ec(e,["topLeft","topRight","bottomLeft","bottomRight"])}function ko(e){let t=Ef(e);return t.width=t.left+t.right,t.height=t.top+t.bottom,t}function uo(e,t){e=e||{},t=t||gt.font;let o=ze(e.size,t.size);typeof o=="string"&&(o=parseInt(o,10));let r=ze(e.style,t.style);r&&!(""+r).match(N8)&&(console.warn('Invalid font style specified: "'+r+'"'),r=void 0);let i={family:ze(e.family,t.family),lineHeight:j8(ze(e.lineHeight,t.lineHeight),o),size:o,style:r,weight:ze(e.weight,t.weight),string:""};return i.string=H8(i),i}function na(e,t,o,r){let i=!0,s,n,a;for(s=0,n=e.length;s<n;++s)if(a=e[s],a!==void 0&&(t!==void 0&&typeof a=="function"&&(a=a(t),i=!1),o!==void 0&&ct(a)&&(a=a[o%a.length],i=!1),a!==void 0))return r&&!i&&(r.cacheable=!1),a}function Rf(e,t,o){let{min:r,max:i}=e,s=gf(t,(i-r)/2),n=(a,l)=>o&&a===0?0:a+l;return{min:n(r,-Math.abs(s)),max:n(i,s)}}function Vr(e,t){return Object.assign(Object.create(e),t)}function Rc(e,t=[""],o,r,i=()=>e[0]){let s=o||e;typeof r>"u"&&(r=Bf("_fallback",e));let n={[Symbol.toStringTag]:"Object",_cacheable:!0,_scopes:e,_rootScopes:s,_fallback:r,_getTarget:i,override:a=>Rc([a,...e],t,s,r)};return new Proxy(n,{deleteProperty(a,l){return delete a[l],delete a._keys,delete e[0][l],!0},get(a,l){return zf(a,l,()=>J8(l,t,e,a))},getOwnPropertyDescriptor(a,l){return Reflect.getOwnPropertyDescriptor(a._scopes[0],l)},getPrototypeOf(){return Reflect.getPrototypeOf(e[0])},has(a,l){return df(a).includes(l)},ownKeys(a){return df(a)},set(a,l,c){let d=a._storage||(a._storage=i());return a[l]=d[l]=c,delete a._keys,!0}})}function Ki(e,t,o,r){let i={_cacheable:!1,_proxy:e,_context:t,_subProxy:o,_stack:new Set,_descriptors:Bh(e,r),setContext:s=>Ki(e,s,o,r),override:s=>Ki(e.override(s),t,o,r)};return new Proxy(i,{deleteProperty(s,n){return delete s[n],delete e[n],!0},get(s,n,a){return zf(s,n,()=>G8(s,n,a))},getOwnPropertyDescriptor(s,n){return s._descriptors.allKeys?Reflect.has(e,n)?{enumerable:!0,configurable:!0}:void 0:Reflect.getOwnPropertyDescriptor(e,n)},getPrototypeOf(){return Reflect.getPrototypeOf(e)},has(s,n){return Reflect.has(e,n)},ownKeys(){return Reflect.ownKeys(e)},set(s,n,a){return e[n]=a,delete s[n],!0}})}function Bh(e,t={scriptable:!0,indexable:!0}){let{_scriptable:o=t.scriptable,_indexable:r=t.indexable,_allKeys:i=t.allKeys}=e;return{allKeys:i,scriptable:o,indexable:r,isScriptable:Ar(o)?o:()=>o,isIndexable:Ar(r)?r:()=>r}}var U8=(e,t)=>e?e+kc(t):t,Ih=(e,t)=>Ve(t)&&e!=="adapters"&&(Object.getPrototypeOf(t)===null||t.constructor===Object);function zf(e,t,o){if(Object.prototype.hasOwnProperty.call(e,t)||t==="constructor")return e[t];let r=o();return e[t]=r,r}function G8(e,t,o){let{_proxy:r,_context:i,_subProxy:s,_descriptors:n}=e,a=r[t];return Ar(a)&&n.isScriptable(t)&&(a=Y8(t,a,e,o)),ct(a)&&a.length&&(a=q8(t,a,e,n.isIndexable)),Ih(t,a)&&(a=Ki(a,i,s&&s[t],n)),a}function Y8(e,t,o,r){let{_proxy:i,_context:s,_subProxy:n,_stack:a}=o;if(a.has(e))throw new Error("Recursion detected: "+Array.from(a).join("->")+"->"+e);a.add(e);let l=t(s,n||r);return a.delete(e),Ih(e,l)&&(l=Zh(i._scopes,i,e,l)),l}function q8(e,t,o,r){let{_proxy:i,_context:s,_subProxy:n,_descriptors:a}=o;if(typeof s.index<"u"&&r(e))return t[s.index%t.length];if(Ve(t[0])){let l=t,c=i._scopes.filter(d=>d!==l);t=[];for(let d of l){let p=Zh(c,i,e,d);t.push(Ki(p,s,n&&n[e],a))}}return t}function Hf(e,t,o){return Ar(e)?e(t,o):e}var X8=(e,t)=>e===!0?t:typeof e=="string"?oa(t,e):void 0;function K8(e,t,o,r,i){for(let s of t){let n=X8(o,s);if(n){e.add(n);let a=Hf(n._fallback,o,i);if(typeof a<"u"&&a!==o&&a!==r)return a}else if(n===!1&&typeof r<"u"&&o!==r)return null}return!1}function Zh(e,t,o,r){let i=t._rootScopes,s=Hf(t._fallback,o,r),n=[...e,...i],a=new Set;a.add(r);let l=cf(a,n,o,s||o,r);return l===null||typeof s<"u"&&s!==o&&(l=cf(a,n,s,l,r),l===null)?!1:Rc(Array.from(a),[""],i,s,()=>Q8(t,o,r))}function cf(e,t,o,r,i){for(;o;)o=K8(e,t,o,r,i);return o}function Q8(e,t,o){let r=e._getTarget();t in r||(r[t]={});let i=r[t];return ct(i)&&Ve(o)?o:i||{}}function J8(e,t,o,r){let i;for(let s of t)if(i=Bf(U8(s,e),o),typeof i<"u")return Ih(e,i)?Zh(o,r,e,i):i}function Bf(e,t){for(let o of t){if(!o)continue;let r=o[e];if(typeof r<"u")return r}}function df(e){let t=e._keys;return t||(t=e._keys=e7(e._scopes)),t}function e7(e){let t=new Set;for(let o of e)for(let r of Object.keys(o).filter(i=>!i.startsWith("_")))t.add(r);return Array.from(t)}var t7=Number.EPSILON||1e-14,Gs=(e,t)=>t<e.length&&!e[t].skip&&e[t],If=e=>e==="x"?"y":"x";function o7(e,t,o,r){let i=e.skip?t:e,s=t,n=o.skip?t:o,a=xc(s,i),l=xc(n,s),c=a/(a+l),d=l/(a+l);c=isNaN(c)?0:c,d=isNaN(d)?0:d;let p=r*c,u=r*d;return{previous:{x:s.x-p*(n.x-i.x),y:s.y-p*(n.y-i.y)},next:{x:s.x+u*(n.x-i.x),y:s.y+u*(n.y-i.y)}}}function r7(e,t,o){let r=e.length,i,s,n,a,l,c=Gs(e,0);for(let d=0;d<r-1;++d)if(l=c,c=Gs(e,d+1),!(!l||!c)){if(qs(t[d],0,t7)){o[d]=o[d+1]=0;continue}i=o[d]/t[d],s=o[d+1]/t[d],a=Math.pow(i,2)+Math.pow(s,2),!(a<=9)&&(n=3/Math.sqrt(a),o[d]=i*n*t[d],o[d+1]=s*n*t[d])}}function i7(e,t,o="x"){let r=If(o),i=e.length,s,n,a,l=Gs(e,0);for(let c=0;c<i;++c){if(n=a,a=l,l=Gs(e,c+1),!a)continue;let d=a[o],p=a[r];n&&(s=(d-n[o])/3,a[`cp1${o}`]=d-s,a[`cp1${r}`]=p-s*t[c]),l&&(s=(l[o]-d)/3,a[`cp2${o}`]=d+s,a[`cp2${r}`]=p+s*t[c])}}function s7(e,t="x"){let o=If(t),r=e.length,i=Array(r).fill(0),s=Array(r),n,a,l,c=Gs(e,0);for(n=0;n<r;++n)if(a=l,l=c,c=Gs(e,n+1),!!l){if(c){let d=c[t]-l[t];i[n]=d!==0?(c[o]-l[o])/d:0}s[n]=a?c?Xi(i[n-1])!==Xi(i[n])?0:(i[n-1]+i[n])/2:i[n-1]:i[n]}r7(e,i,s),i7(e,s,t)}function bc(e,t,o){return Math.max(Math.min(e,o),t)}function n7(e,t){let o,r,i,s,n,a=ar(e[0],t);for(o=0,r=e.length;o<r;++o)n=s,s=a,a=o<r-1&&ar(e[o+1],t),s&&(i=e[o],n&&(i.cp1x=bc(i.cp1x,t.left,t.right),i.cp1y=bc(i.cp1y,t.top,t.bottom)),a&&(i.cp2x=bc(i.cp2x,t.left,t.right),i.cp2y=bc(i.cp2y,t.top,t.bottom)))}function Zf(e,t,o,r,i){let s,n,a,l;if(t.spanGaps&&(e=e.filter(c=>!c.skip)),t.cubicInterpolationMode==="monotone")s7(e,i);else{let c=r?e[e.length-1]:e[0];for(s=0,n=e.length;s<n;++s)a=e[s],l=o7(c,a,e[Math.min(s+1,n-(r?0:1))%n],t.tension),a.cp1x=l.previous.x,a.cp1y=l.previous.y,a.cp2x=l.next.x,a.cp2y=l.next.y,c=a}t.capBezierPoints&&n7(e,o)}function zc(){return typeof window<"u"&&typeof document<"u"}function Hc(e){let t=e.parentNode;return t&&t.toString()==="[object ShadowRoot]"&&(t=t.host),t}function _c(e,t,o){let r;return typeof e=="string"?(r=parseInt(e,10),e.indexOf("%")!==-1&&(r=r/100*t.parentNode[o])):r=e,r}var Bc=e=>e.ownerDocument.defaultView.getComputedStyle(e,null);function a7(e,t){return Bc(e).getPropertyValue(t)}var l7=["top","right","bottom","left"];function qi(e,t,o){let r={};o=o?"-"+o:"";for(let i=0;i<4;i++){let s=l7[i];r[s]=parseFloat(e[t+"-"+s+o])||0}return r.width=r.left+r.right,r.height=r.top+r.bottom,r}var c7=(e,t,o)=>(e>0||t>0)&&(!o||!o.shadowRoot);function d7(e,t){let o=e.touches,r=o&&o.length?o[0]:e,{offsetX:i,offsetY:s}=r,n=!1,a,l;if(c7(i,s,e.target))a=i,l=s;else{let c=t.getBoundingClientRect();a=r.clientX-c.left,l=r.clientY-c.top,n=!0}return{x:a,y:l,box:n}}function di(e,t){if("native"in e)return e;let{canvas:o,currentDevicePixelRatio:r}=t,i=Bc(o),s=i.boxSizing==="border-box",n=qi(i,"padding"),a=qi(i,"border","width"),{x:l,y:c,box:d}=d7(e,o),p=n.left+(d&&a.left),u=n.top+(d&&a.top),{width:m,height:b}=t;return s&&(m-=n.width+a.width,b-=n.height+a.height),{x:Math.round((l-p)/m*o.width/r),y:Math.round((c-u)/b*o.height/r)}}function h7(e,t,o){let r,i;if(t===void 0||o===void 0){let s=e&&Hc(e);if(!s)t=e.clientWidth,o=e.clientHeight;else{let n=s.getBoundingClientRect(),a=Bc(s),l=qi(a,"border","width"),c=qi(a,"padding");t=n.width-c.width-l.width,o=n.height-c.height-l.height,r=_c(a.maxWidth,s,"clientWidth"),i=_c(a.maxHeight,s,"clientHeight")}}return{width:t,height:o,maxWidth:r||Cc,maxHeight:i||Cc}}var ai=e=>Math.round(e*10)/10;function Ff(e,t,o,r){let i=Bc(e),s=qi(i,"margin"),n=_c(i.maxWidth,e,"clientWidth")||Cc,a=_c(i.maxHeight,e,"clientHeight")||Cc,l=h7(e,t,o),{width:c,height:d}=l;if(i.boxSizing==="content-box"){let u=qi(i,"border","width"),m=qi(i,"padding");c-=m.width+u.width,d-=m.height+u.height}return c=Math.max(0,c-s.width),d=Math.max(0,r?c/r:d-s.height),c=ai(Math.min(c,n,l.maxWidth)),d=ai(Math.min(d,a,l.maxHeight)),c&&!d&&(d=ai(c/2)),(t!==void 0||o!==void 0)&&r&&l.height&&d>l.height&&(d=l.height,c=ai(Math.floor(d*r))),{width:c,height:d}}function Fh(e,t,o){let r=t||1,i=ai(e.height*r),s=ai(e.width*r);e.height=ai(e.height),e.width=ai(e.width);let n=e.canvas;return n.style&&(o||!n.style.height&&!n.style.width)&&(n.style.height=`${e.height}px`,n.style.width=`${e.width}px`),e.currentDevicePixelRatio!==r||n.height!==i||n.width!==s?(e.currentDevicePixelRatio=r,n.height=i,n.width=s,e.ctx.setTransform(r,0,0,r,0,0),!0):!1}var Nf=(function(){let e=!1;try{let t={get passive(){return e=!0,!1}};zc()&&(window.addEventListener("test",null,t),window.removeEventListener("test",null,t))}catch{}return e})();function Nh(e,t){let o=a7(e,t),r=o&&o.match(/^(\d+)(\.\d+)?px$/);return r?+r[1]:void 0}function si(e,t,o,r){return{x:e.x+o*(t.x-e.x),y:e.y+o*(t.y-e.y)}}function jf(e,t,o,r){return{x:e.x+o*(t.x-e.x),y:r==="middle"?o<.5?e.y:t.y:r==="after"?o<1?e.y:t.y:o>0?t.y:e.y}}function Wf(e,t,o,r){let i={x:e.cp2x,y:e.cp2y},s={x:t.cp1x,y:t.cp1y},n=si(e,i,o),a=si(i,s,o),l=si(s,t,o),c=si(n,a,o),d=si(a,l,o);return si(c,d,o)}var p7=function(e,t){return{x(o){return e+e+t-o},setWidth(o){t=o},textAlign(o){return o==="center"?o:o==="right"?"left":"right"},xPlus(o,r){return o-r},leftForLtr(o,r){return o-r}}},u7=function(){return{x(e){return e},setWidth(e){},textAlign(e){return e},xPlus(e,t){return e+t},leftForLtr(e,t){return e}}};function Ic(e,t,o){return e?p7(t,o):u7()}function Uf(e,t){let o,r;(t==="ltr"||t==="rtl")&&(o=e.canvas.style,r=[o.getPropertyValue("direction"),o.getPropertyPriority("direction")],o.setProperty("direction",t,"important"),e.prevTextDirection=r)}function Gf(e,t){t!==void 0&&(delete e.prevTextDirection,e.canvas.style.setProperty("direction",t[0],t[1]))}function Yf(e){return e==="angle"?{between:Sc,compare:P8,normalize:Ft}:{between:Mc,compare:(t,o)=>t-o,normalize:t=>t}}function hf({start:e,end:t,count:o,loop:r,style:i}){return{start:e%o,end:t%o,loop:r&&(t-e+1)%o===0,style:i}}function f7(e,t,o){let{property:r,start:i,end:s}=o,{between:n,normalize:a}=Yf(r),l=t.length,{start:c,end:d,loop:p}=e,u,m;if(p){for(c+=l,d+=l,u=0,m=l;u<m&&n(a(t[c%l][r]),i,s);++u)c--,d--;c%=l,d%=l}return d<c&&(d+=l),{start:c,end:d,loop:p,style:e.style}}function jh(e,t,o){if(!o)return[e];let{property:r,start:i,end:s}=o,n=t.length,{compare:a,between:l,normalize:c}=Yf(r),{start:d,end:p,loop:u,style:m}=f7(e,t,o),b=[],C=!1,y=null,k,$,V,O=()=>l(i,V,k)&&a(i,V)!==0,P=()=>a(s,k)===0||l(s,V,k),T=()=>C||O(),Z=()=>!C||P();for(let R=d,D=d;R<=p;++R)$=t[R%n],!$.skip&&(k=c($[r]),k!==V&&(C=l(k,i,s),y===null&&T()&&(y=a(k,i)===0?R:D),y!==null&&Z()&&(b.push(hf({start:y,end:R,loop:u,count:n,style:m})),y=null),D=R,V=k));return y!==null&&b.push(hf({start:y,end:p,loop:u,count:n,style:m})),b}function Wh(e,t){let o=[],r=e.segments;for(let i=0;i<r.length;i++){let s=jh(r[i],e.points,t);s.length&&o.push(...s)}return o}function g7(e,t,o,r){let i=0,s=t-1;if(o&&!r)for(;i<t&&!e[i].skip;)i++;for(;i<t&&e[i].skip;)i++;for(i%=t,o&&(s+=i);s>i&&e[s%t].skip;)s--;return s%=t,{start:i,end:s}}function m7(e,t,o,r){let i=e.length,s=[],n=t,a=e[t],l;for(l=t+1;l<=o;++l){let c=e[l%i];c.skip||c.stop?a.skip||(r=!1,s.push({start:t%i,end:(l-1)%i,loop:r}),t=n=c.stop?l:null):(n=l,a.skip&&(t=l)),a=c}return n!==null&&s.push({start:t%i,end:n%i,loop:r}),s}function qf(e,t){let o=e.points,r=e.options.spanGaps,i=o.length;if(!i)return[];let s=!!e._loop,{start:n,end:a}=g7(o,i,s,r);if(r===!0)return pf(e,[{start:n,end:a,loop:s}],o,t);let l=a<n?a+i:a,c=!!e._fullLoop&&n===0&&a===i-1;return pf(e,m7(o,n,l,c),o,t)}function pf(e,t,o,r){return!r||!r.setContext||!o?t:v7(e,t,o,r)}function v7(e,t,o,r){let i=e._chart.getContext(),s=uf(e.options),{_datasetIndex:n,options:{spanGaps:a}}=e,l=o.length,c=[],d=s,p=t[0].start,u=p;function m(b,C,y,k){let $=a?-1:1;if(b!==C){for(b+=l;o[b%l].skip;)b-=$;for(;o[C%l].skip;)C+=$;b%l!==C%l&&(c.push({start:b%l,end:C%l,loop:y,style:k}),d=k,p=C%l)}}for(let b of t){p=a?p:b.start;let C=o[p%l],y;for(u=p+1;u<=b.end;u++){let k=o[u%l];y=uf(r.setContext(Vr(i,{type:"segment",p0:C,p1:k,p0DataIndex:(u-1)%l,p1DataIndex:u%l,datasetIndex:n}))),b7(y,d)&&m(p,u-1,b.loop,d),C=k,d=y}p<u-1&&m(p,u-1,b.loop,d)}return c}function uf(e){return{backgroundColor:e.backgroundColor,borderCapStyle:e.borderCapStyle,borderDash:e.borderDash,borderDashOffset:e.borderDashOffset,borderJoinStyle:e.borderJoinStyle,borderWidth:e.borderWidth,borderColor:e.borderColor}}function b7(e,t){if(!t)return!1;let o=[],r=function(i,s){return Rh(s)?(o.includes(s)||o.push(s),o.indexOf(s)):s};return JSON.stringify(e,r)!==JSON.stringify(t,r)}function wc(e,t,o){return e.options.clip?e[o]:t[o]}function w7(e,t){let{xScale:o,yScale:r}=e;return o&&r?{left:wc(o,t,"left"),right:wc(o,t,"right"),top:wc(r,t,"top"),bottom:wc(r,t,"bottom")}:t}function Uh(e,t){let o=t._clip;if(o.disabled)return!1;let r=w7(t,e.chartArea);return{left:o.left===!1?0:r.left-(o.left===!0?0:o.left),right:o.right===!1?e.width:r.right+(o.right===!0?0:o.right),top:o.top===!1?0:r.top-(o.top===!0?0:o.top),bottom:o.bottom===!1?e.height:r.bottom+(o.bottom===!0?0:o.bottom)}}var tp=class{constructor(){this._request=null,this._charts=new Map,this._running=!1,this._lastDate=void 0}_notify(t,o,r,i){let s=o.listeners[i],n=o.duration;s.forEach(a=>a({chart:t,initial:o.initial,numSteps:n,currentStep:Math.min(r-o.start,n)}))}_refresh(){this._request||(this._running=!0,this._request=Th.call(window,()=>{this._update(),this._request=null,this._running&&this._refresh()}))}_update(t=Date.now()){let o=0;this._charts.forEach((r,i)=>{if(!r.running||!r.items.length)return;let s=r.items,n=s.length-1,a=!1,l;for(;n>=0;--n)l=s[n],l._active?(l._total>r.duration&&(r.duration=l._total),l.tick(t),a=!0):(s[n]=s[s.length-1],s.pop());a&&(i.draw(),this._notify(i,r,t,"progress")),s.length||(r.running=!1,this._notify(i,r,t,"complete"),r.initial=!1),o+=s.length}),this._lastDate=t,o===0&&(this._running=!1)}_getAnims(t){let o=this._charts,r=o.get(t);return r||(r={running:!1,initial:!0,items:[],listeners:{complete:[],progress:[]}},o.set(t,r)),r}listen(t,o,r){this._getAnims(t).listeners[o].push(r)}add(t,o){!o||!o.length||this._getAnims(t).items.push(...o)}has(t){return this._getAnims(t).items.length>0}start(t){let o=this._charts.get(t);o&&(o.running=!0,o.start=Date.now(),o.duration=o.items.reduce((r,i)=>Math.max(r,i._duration),0),this._refresh())}running(t){if(!this._running)return!1;let o=this._charts.get(t);return!(!o||!o.running||!o.items.length)}stop(t){let o=this._charts.get(t);if(!o||!o.items.length)return;let r=o.items,i=r.length-1;for(;i>=0;--i)r[i].cancel();o.items=[],this._notify(t,o,Date.now(),"complete")}remove(t){return this._charts.delete(t)}},Tr=new tp,Xf="transparent",y7={boolean(e,t,o){return o>.5?t:e},color(e,t,o){let r=zh(e||Xf),i=r.valid&&zh(t||Xf);return i&&i.valid?i.mix(r,o).hexString():t},number(e,t,o){return e+(t-e)*o}},op=class{constructor(t,o,r,i){let s=o[r];i=na([t.to,i,s,t.from]);let n=na([t.from,s,i]);this._active=!0,this._fn=t.fn||y7[t.type||typeof n],this._easing=Ws[t.easing]||Ws.linear,this._start=Math.floor(Date.now()+(t.delay||0)),this._duration=this._total=Math.floor(t.duration),this._loop=!!t.loop,this._target=o,this._prop=r,this._from=n,this._to=i,this._promises=void 0}active(){return this._active}update(t,o,r){if(this._active){this._notify(!1);let i=this._target[this._prop],s=r-this._start,n=this._duration-s;this._start=r,this._duration=Math.floor(Math.max(n,t.duration)),this._total+=s,this._loop=!!t.loop,this._to=na([t.to,o,i,t.from]),this._from=na([t.from,i,o])}}cancel(){this._active&&(this.tick(Date.now()),this._active=!1,this._notify(!1))}tick(t){let o=t-this._start,r=this._duration,i=this._prop,s=this._from,n=this._loop,a=this._to,l;if(this._active=s!==a&&(n||o<r),!this._active){this._target[i]=a,this._notify(!0);return}if(o<0){this._target[i]=s;return}l=o/r%2,l=n&&l>1?2-l:l,l=this._easing(Math.min(1,Math.max(0,l))),this._target[i]=this._fn(s,a,l)}wait(){let t=this._promises||(this._promises=[]);return new Promise((o,r)=>{t.push({res:o,rej:r})})}_notify(t){let o=t?"res":"rej",r=this._promises||[];for(let i=0;i<r.length;i++)r[i][o]()}},qc=class{constructor(t,o){this._chart=t,this._properties=new Map,this.configure(o)}configure(t){if(!Ve(t))return;let o=Object.keys(gt.animation),r=this._properties;Object.getOwnPropertyNames(t).forEach(i=>{let s=t[i];if(!Ve(s))return;let n={};for(let a of o)n[a]=s[a];(ct(s.properties)&&s.properties||[i]).forEach(a=>{(a===i||!r.has(a))&&r.set(a,n)})})}_animateOptions(t,o){let r=o.options,i=x7(t,r);if(!i)return[];let s=this._createAnimations(i,r);return r.$shared&&C7(t.options.$animations,r).then(()=>{t.options=r},()=>{}),s}_createAnimations(t,o){let r=this._properties,i=[],s=t.$animations||(t.$animations={}),n=Object.keys(o),a=Date.now(),l;for(l=n.length-1;l>=0;--l){let c=n[l];if(c.charAt(0)==="$")continue;if(c==="options"){i.push(...this._animateOptions(t,o));continue}let d=o[c],p=s[c],u=r.get(c);if(p)if(u&&p.active()){p.update(u,d,a);continue}else p.cancel();if(!u||!u.duration){t[c]=d;continue}s[c]=p=new op(u,t,c,d),i.push(p)}return i}update(t,o){if(this._properties.size===0){Object.assign(t,o);return}let r=this._createAnimations(t,o);if(r.length)return Tr.add(this._chart,r),!0}};function C7(e,t){let o=[],r=Object.keys(t);for(let i=0;i<r.length;i++){let s=e[r[i]];s&&s.active()&&o.push(s.wait())}return Promise.all(o)}function x7(e,t){if(!t)return;let o=e.options;if(!o){e.options=t;return}return o.$shared&&(e.options=o=Object.assign({},o,{$shared:!1,$animations:{}})),o}function Kf(e,t){let o=e&&e.options||{},r=o.reverse,i=o.min===void 0?t:0,s=o.max===void 0?t:0;return{start:r?s:i,end:r?i:s}}function _7(e,t,o){if(o===!1)return!1;let r=Kf(e,o),i=Kf(t,o);return{top:i.end,right:r.end,bottom:i.start,left:r.start}}function k7(e){let t,o,r,i;return Ve(e)?(t=e.top,o=e.right,r=e.bottom,i=e.left):t=o=r=i=e,{top:t,right:o,bottom:r,left:i,disabled:e===!1}}function Wg(e,t){let o=[],r=e._getSortedDatasetMetas(t),i,s;for(i=0,s=r.length;i<s;++i)o.push(r[i].index);return o}function Qf(e,t,o,r={}){let i=e.keys,s=r.mode==="single",n,a,l,c;if(t===null)return;let d=!1;for(n=0,a=i.length;n<a;++n){if(l=+i[n],l===o){if(d=!0,r.all)continue;break}c=e.values[l],ht(c)&&(s||t===0||Xi(t)===Xi(c))&&(t+=c)}return!d&&!r.all?0:t}function L7(e,t){let{iScale:o,vScale:r}=t,i=o.axis==="x"?"x":"y",s=r.axis==="x"?"x":"y",n=Object.keys(e),a=new Array(n.length),l,c,d;for(l=0,c=n.length;l<c;++l)d=n[l],a[l]={[i]:d,[s]:e[d]};return a}function Gh(e,t){let o=e&&e.options.stacked;return o||o===void 0&&t.stack!==void 0}function S7(e,t,o){return`${e.id}.${t.id}.${o.stack||o.type}`}function M7(e){let{min:t,max:o,minDefined:r,maxDefined:i}=e.getUserBounds();return{min:r?t:Number.NEGATIVE_INFINITY,max:i?o:Number.POSITIVE_INFINITY}}function $7(e,t,o){let r=e[t]||(e[t]={});return r[o]||(r[o]={})}function Jf(e,t,o,r){for(let i of t.getMatchingVisibleMetas(r).reverse()){let s=e[i.index];if(o&&s>0||!o&&s<0)return i.index}return null}function eg(e,t){let{chart:o,_cachedMeta:r}=e,i=o._stacks||(o._stacks={}),{iScale:s,vScale:n,index:a}=r,l=s.axis,c=n.axis,d=S7(s,n,r),p=t.length,u;for(let m=0;m<p;++m){let b=t[m],{[l]:C,[c]:y}=b,k=b._stacks||(b._stacks={});u=k[c]=$7(i,d,C),u[a]=y,u._top=Jf(u,n,!0,r.type),u._bottom=Jf(u,n,!1,r.type);let $=u._visualValues||(u._visualValues={});$[a]=y}}function Yh(e,t){let o=e.scales;return Object.keys(o).filter(r=>o[r].axis===t).shift()}function A7(e,t){return Vr(e,{active:!1,dataset:void 0,datasetIndex:t,index:t,mode:"default",type:"dataset"})}function P7(e,t,o){return Vr(e,{active:!1,dataIndex:t,parsed:void 0,raw:void 0,element:o,index:t,mode:"default",type:"data"})}function aa(e,t){let o=e.controller.index,r=e.vScale&&e.vScale.axis;if(r){t=t||e._parsed;for(let i of t){let s=i._stacks;if(!s||s[r]===void 0||s[r][o]===void 0)return;delete s[r][o],s[r]._visualValues!==void 0&&s[r]._visualValues[o]!==void 0&&delete s[r]._visualValues[o]}}}var qh=e=>e==="reset"||e==="none",tg=(e,t)=>t?e:Object.assign({},e),O7=(e,t,o)=>e&&!t.hidden&&t._stacked&&{keys:Wg(o,!0),values:null},Xc=class{static defaults={};static datasetElementType=null;static dataElementType=null;constructor(t,o){this.chart=t,this._ctx=t.ctx,this.index=o,this._cachedDataOpts={},this._cachedMeta=this.getMeta(),this._type=this._cachedMeta.type,this.options=void 0,this._parsing=!1,this._data=void 0,this._objectData=void 0,this._sharedOptions=void 0,this._drawStart=void 0,this._drawCount=void 0,this.enableOptionSharing=!1,this.supportsDecimation=!1,this.$context=void 0,this._syncList=[],this.datasetElementType=new.target.datasetElementType,this.dataElementType=new.target.dataElementType,this.initialize()}initialize(){let t=this._cachedMeta;this.configure(),this.linkScales(),t._stacked=Gh(t.vScale,t),this.addElements(),this.options.fill&&!this.chart.isPluginEnabled("filler")&&console.warn("Tried to use the 'fill' option without the 'Filler' plugin enabled. Please import and register the 'Filler' plugin and make sure it is not disabled in the options")}updateIndex(t){this.index!==t&&aa(this._cachedMeta),this.index=t}linkScales(){let t=this.chart,o=this._cachedMeta,r=this.getDataset(),i=(p,u,m,b)=>p==="x"?u:p==="r"?b:m,s=o.xAxisID=ze(r.xAxisID,Yh(t,"x")),n=o.yAxisID=ze(r.yAxisID,Yh(t,"y")),a=o.rAxisID=ze(r.rAxisID,Yh(t,"r")),l=o.indexAxis,c=o.iAxisID=i(l,s,n,a),d=o.vAxisID=i(l,n,s,a);o.xScale=this.getScaleForId(s),o.yScale=this.getScaleForId(n),o.rScale=this.getScaleForId(a),o.iScale=this.getScaleForId(c),o.vScale=this.getScaleForId(d)}getDataset(){return this.chart.data.datasets[this.index]}getMeta(){return this.chart.getDatasetMeta(this.index)}getScaleForId(t){return this.chart.scales[t]}_getOtherScale(t){let o=this._cachedMeta;return t===o.iScale?o.vScale:o.iScale}reset(){this._update("reset")}_destroy(){let t=this._cachedMeta;this._data&&Vh(this._data,this),t._stacked&&aa(t)}_dataCheck(){let t=this.getDataset(),o=t.data||(t.data=[]),r=this._data;if(Ve(o)){let i=this._cachedMeta;this._data=L7(o,i)}else if(r!==o){if(r){Vh(r,this);let i=this._cachedMeta;aa(i),i._parsed=[]}o&&Object.isExtensible(o)&&kf(o,this),this._syncList=[],this._data=o}}addElements(){let t=this._cachedMeta;this._dataCheck(),this.datasetElementType&&(t.dataset=new this.datasetElementType)}buildOrUpdateElements(t){let o=this._cachedMeta,r=this.getDataset(),i=!1;this._dataCheck();let s=o._stacked;o._stacked=Gh(o.vScale,o),o.stack!==r.stack&&(i=!0,aa(o),o.stack=r.stack),this._resyncElements(t),(i||s!==o._stacked)&&(eg(this,o._parsed),o._stacked=Gh(o.vScale,o))}configure(){let t=this.chart.config,o=t.datasetScopeKeys(this._type),r=t.getOptionScopes(this.getDataset(),o,!0);this.options=t.createResolver(r,this.getContext()),this._parsing=this.options.parsing,this._cachedDataOpts={}}parse(t,o){let{_cachedMeta:r,_data:i}=this,{iScale:s,_stacked:n}=r,a=s.axis,l=t===0&&o===i.length?!0:r._sorted,c=t>0&&r._parsed[t-1],d,p,u;if(this._parsing===!1)r._parsed=i,r._sorted=!0,u=i;else{ct(i[t])?u=this.parseArrayData(r,i,t,o):Ve(i[t])?u=this.parseObjectData(r,i,t,o):u=this.parsePrimitiveData(r,i,t,o);let m=()=>p[a]===null||c&&p[a]<c[a];for(d=0;d<o;++d)r._parsed[d+t]=p=u[d],l&&(m()&&(l=!1),c=p);r._sorted=l}n&&eg(this,u)}parsePrimitiveData(t,o,r,i){let{iScale:s,vScale:n}=t,a=s.axis,l=n.axis,c=s.getLabels(),d=s===n,p=new Array(i),u,m,b;for(u=0,m=i;u<m;++u)b=u+r,p[u]={[a]:d||s.parse(c[b],b),[l]:n.parse(o[b],b)};return p}parseArrayData(t,o,r,i){let{xScale:s,yScale:n}=t,a=new Array(i),l,c,d,p;for(l=0,c=i;l<c;++l)d=l+r,p=o[d],a[l]={x:s.parse(p[0],d),y:n.parse(p[1],d)};return a}parseObjectData(t,o,r,i){let{xScale:s,yScale:n}=t,{xAxisKey:a="x",yAxisKey:l="y"}=this._parsing,c=new Array(i),d,p,u,m;for(d=0,p=i;d<p;++d)u=d+r,m=o[u],c[d]={x:s.parse(oa(m,a),u),y:n.parse(oa(m,l),u)};return c}getParsed(t){return this._cachedMeta._parsed[t]}getDataElement(t){return this._cachedMeta.data[t]}applyStack(t,o,r){let i=this.chart,s=this._cachedMeta,n=o[t.axis],a={keys:Wg(i,!0),values:o._stacks[t.axis]._visualValues};return Qf(a,n,s.index,{mode:r})}updateRangeFromParsed(t,o,r,i){let s=r[o.axis],n=s===null?NaN:s,a=i&&r._stacks[o.axis];i&&a&&(i.values=a,n=Qf(i,s,this._cachedMeta.index)),t.min=Math.min(t.min,n),t.max=Math.max(t.max,n)}getMinMax(t,o){let r=this._cachedMeta,i=r._parsed,s=r._sorted&&t===r.iScale,n=i.length,a=this._getOtherScale(t),l=O7(o,r,this.chart),c={min:Number.POSITIVE_INFINITY,max:Number.NEGATIVE_INFINITY},{min:d,max:p}=M7(a),u,m;function b(){m=i[u];let C=m[a.axis];return!ht(m[t.axis])||d>C||p<C}for(u=0;u<n&&!(!b()&&(this.updateRangeFromParsed(c,t,m,l),s));++u);if(s){for(u=n-1;u>=0;--u)if(!b()){this.updateRangeFromParsed(c,t,m,l);break}}return c}getAllParsedValues(t){let o=this._cachedMeta._parsed,r=[],i,s,n;for(i=0,s=o.length;i<s;++i)n=o[i][t.axis],ht(n)&&r.push(n);return r}getMaxOverflow(){return!1}getLabelAndValue(t){let o=this._cachedMeta,r=o.iScale,i=o.vScale,s=this.getParsed(t);return{label:r?""+r.getLabelForValue(s[r.axis]):"",value:i?""+i.getLabelForValue(s[i.axis]):""}}_update(t){let o=this._cachedMeta;this.update(t||"default"),o._clip=k7(ze(this.options.clip,_7(o.xScale,o.yScale,this.getMaxOverflow())))}update(t){}draw(){let t=this._ctx,o=this.chart,r=this._cachedMeta,i=r.data||[],s=o.chartArea,n=[],a=this._drawStart||0,l=this._drawCount||i.length-a,c=this.options.drawActiveElementsOnTop,d;for(r.dataset&&r.dataset.draw(t,s,a,l),d=a;d<a+l;++d){let p=i[d];p.hidden||(p.active&&c?n.push(p):p.draw(t,s))}for(d=0;d<n.length;++d)n[d].draw(t,s)}getStyle(t,o){let r=o?"active":"default";return t===void 0&&this._cachedMeta.dataset?this.resolveDatasetElementOptions(r):this.resolveDataElementOptions(t||0,r)}getContext(t,o,r){let i=this.getDataset(),s;if(t>=0&&t<this._cachedMeta.data.length){let n=this._cachedMeta.data[t];s=n.$context||(n.$context=P7(this.getContext(),t,n)),s.parsed=this.getParsed(t),s.raw=i.data[t],s.index=s.dataIndex=t}else s=this.$context||(this.$context=A7(this.chart.getContext(),this.index)),s.dataset=i,s.index=s.datasetIndex=this.index;return s.active=!!o,s.mode=r,s}resolveDatasetElementOptions(t){return this._resolveElementOptions(this.datasetElementType.id,t)}resolveDataElementOptions(t,o){return this._resolveElementOptions(this.dataElementType.id,o,t)}_resolveElementOptions(t,o="default",r){let i=o==="active",s=this._cachedDataOpts,n=t+"-"+o,a=s[n],l=this.enableOptionSharing&&ra(r);if(a)return tg(a,l);let c=this.chart.config,d=c.datasetElementScopeKeys(this._type,t),p=i?[`${t}Hover`,"hover",t,""]:[t,""],u=c.getOptionScopes(this.getDataset(),d),m=Object.keys(gt.elements[t]),b=()=>this.getContext(r,i,o),C=c.resolveNamedOptions(u,m,b,p);return C.$shared&&(C.$shared=l,s[n]=Object.freeze(tg(C,l))),C}_resolveAnimations(t,o,r){let i=this.chart,s=this._cachedDataOpts,n=`animation-${o}`,a=s[n];if(a)return a;let l;if(i.options.animation!==!1){let d=this.chart.config,p=d.datasetAnimationScopeKeys(this._type,o),u=d.getOptionScopes(this.getDataset(),p);l=d.createResolver(u,this.getContext(t,r,o))}let c=new qc(i,l&&l.animations);return l&&l._cacheable&&(s[n]=Object.freeze(c)),c}getSharedOptions(t){if(t.$shared)return this._sharedOptions||(this._sharedOptions=Object.assign({},t))}includeOptions(t,o){return!o||qh(t)||this.chart._animationsDisabled}_getSharedOptions(t,o){let r=this.resolveDataElementOptions(t,o),i=this._sharedOptions,s=this.getSharedOptions(r),n=this.includeOptions(o,s)||s!==i;return this.updateSharedOptions(s,o,r),{sharedOptions:s,includeOptions:n}}updateElement(t,o,r,i){qh(i)?Object.assign(t,r):this._resolveAnimations(o,i).update(t,r)}updateSharedOptions(t,o,r){t&&!qh(o)&&this._resolveAnimations(void 0,o).update(t,r)}_setStyle(t,o,r,i){t.active=i;let s=this.getStyle(o,i);this._resolveAnimations(o,r,i).update(t,{options:!i&&this.getSharedOptions(s)||s})}removeHoverStyle(t,o,r){this._setStyle(t,r,"active",!1)}setHoverStyle(t,o,r){this._setStyle(t,r,"active",!0)}_removeDatasetHoverStyle(){let t=this._cachedMeta.dataset;t&&this._setStyle(t,void 0,"active",!1)}_setDatasetHoverStyle(){let t=this._cachedMeta.dataset;t&&this._setStyle(t,void 0,"active",!0)}_resyncElements(t){let o=this._data,r=this._cachedMeta.data;for(let[a,l,c]of this._syncList)this[a](l,c);this._syncList=[];let i=r.length,s=o.length,n=Math.min(s,i);n&&this.parse(0,n),s>i?this._insertElements(i,s-i,t):s<i&&this._removeElements(s,i-s)}_insertElements(t,o,r=!0){let i=this._cachedMeta,s=i.data,n=t+o,a,l=c=>{for(c.length+=o,a=c.length-1;a>=n;a--)c[a]=c[a-o]};for(l(s),a=t;a<n;++a)s[a]=new this.dataElementType;this._parsing&&l(i._parsed),this.parse(t,o),r&&this.updateElements(s,t,o,"reset")}updateElements(t,o,r,i){}_removeElements(t,o){let r=this._cachedMeta;if(this._parsing){let i=r._parsed.splice(t,o);r._stacked&&aa(r,i)}r.data.splice(t,o)}_sync(t){if(this._parsing)this._syncList.push(t);else{let[o,r,i]=t;this[o](r,i)}this.chart._dataChanges.push([this.index,...t])}_onDataPush(){let t=arguments.length;this._sync(["_insertElements",this.getDataset().data.length-t,t])}_onDataPop(){this._sync(["_removeElements",this._cachedMeta.data.length-1,1])}_onDataShift(){this._sync(["_removeElements",0,1])}_onDataSplice(t,o){o&&this._sync(["_removeElements",t,o]);let r=arguments.length-2;r&&this._sync(["_insertElements",t,r])}_onDataUnshift(){this._sync(["_insertElements",0,arguments.length])}};var Kc=class extends Xc{static id="line";static defaults={datasetElementType:"line",dataElementType:"point",showLine:!0,spanGaps:!1};static overrides={scales:{_index_:{type:"category"},_value_:{type:"linear"}}};initialize(){this.enableOptionSharing=!0,this.supportsDecimation=!0,super.initialize()}update(t){let o=this._cachedMeta,{dataset:r,data:i=[],_dataset:s}=o,n=this.chart._animationsDisabled,{start:a,count:l}=$f(o,i,n);this._drawStart=a,this._drawCount=l,Af(o)&&(a=0,l=i.length),r._chart=this.chart,r._datasetIndex=this.index,r._decimated=!!s._decimated,r.points=i;let c=this.resolveDatasetElementOptions(t);this.options.showLine||(c.borderWidth=0),c.segment=this.options.segment,this.updateElement(r,void 0,{animated:!n,options:c},t),this.updateElements(i,a,l,t)}updateElements(t,o,r,i){let s=i==="reset",{iScale:n,vScale:a,_stacked:l,_dataset:c}=this._cachedMeta,{sharedOptions:d,includeOptions:p}=this._getSharedOptions(o,i),u=n.axis,m=a.axis,{spanGaps:b,segment:C}=this.options,y=Xs(b)?b:Number.POSITIVE_INFINITY,k=this.chart._animationsDisabled||s||i==="none",$=o+r,V=t.length,O=o>0&&this.getParsed(o-1);for(let P=0;P<V;++P){let T=t[P],Z=k?T:{};if(P<o||P>=$){Z.skip=!0;continue}let R=this.getParsed(P),D=Ze(R[m]),N=Z[u]=n.getPixelForValue(R[u],P),B=Z[m]=s||D?a.getBasePixel():a.getPixelForValue(l?this.applyStack(a,R,l):R[m],P);Z.skip=isNaN(N)||isNaN(B)||D,Z.stop=P>0&&Math.abs(R[u]-O[u])>y,C&&(Z.parsed=R,Z.raw=c.data[P]),p&&(Z.options=d||this.resolveDataElementOptions(P,T.active?"active":i)),k||this.updateElement(T,P,Z,i),O=R}}getMaxOverflow(){let t=this._cachedMeta,o=t.dataset,r=o.options&&o.options.borderWidth||0,i=t.data||[];if(!i.length)return r;let s=i[0].size(this.resolveDataElementOptions(0)),n=i[i.length-1].size(this.resolveDataElementOptions(i.length-1));return Math.max(r,s,n)/2}draw(){let t=this._cachedMeta;t.dataset.updateControlPoints(this.chart.chartArea,t.iScale.axis),super.draw()}};function Qi(){throw new Error("This method is not implemented: Check that a complete date adapter is provided.")}var rp=class e{static override(t){Object.assign(e.prototype,t)}options;constructor(t){this.options=t||{}}init(){}formats(){return Qi()}parse(){return Qi()}format(){return Qi()}add(){return Qi()}diff(){return Qi()}startOf(){return Qi()}endOf(){return Qi()}},V7={_date:rp};function T7(e,t,o,r){let{controller:i,data:s,_sorted:n}=e,a=i._cachedMeta.iScale,l=e.dataset&&e.dataset.options?e.dataset.options.spanGaps:null;if(a&&t===a.axis&&t!=="r"&&n&&s.length){let c=a._reversePixels?Cf:ni;if(r){if(i._sharedOptions){let d=s[0],p=typeof d.getRange=="function"&&d.getRange(t);if(p){let u=c(s,t,o-p),m=c(s,t,o+p);return{lo:u.lo,hi:m.hi}}}}else{let d=c(s,t,o);if(l){let{vScale:p}=i._cachedMeta,{_parsed:u}=e,m=u.slice(0,d.lo+1).reverse().findIndex(C=>!Ze(C[p.axis]));d.lo-=Math.max(0,m);let b=u.slice(d.hi).findIndex(C=>!Ze(C[p.axis]));d.hi+=Math.max(0,b)}return d}}return{lo:0,hi:s.length-1}}function ma(e,t,o,r,i){let s=e.getSortedVisibleDatasetMetas(),n=o[t];for(let a=0,l=s.length;a<l;++a){let{index:c,data:d}=s[a],{lo:p,hi:u}=T7(s[a],t,n,i);for(let m=p;m<=u;++m){let b=d[m];b.skip||r(b,c,m)}}}function D7(e){let t=e.indexOf("x")!==-1,o=e.indexOf("y")!==-1;return function(r,i){let s=t?Math.abs(r.x-i.x):0,n=o?Math.abs(r.y-i.y):0;return Math.sqrt(Math.pow(s,2)+Math.pow(n,2))}}function Xh(e,t,o,r,i){let s=[];return!i&&!e.isPointInArea(t)||ma(e,o,t,function(a,l,c){!i&&!ar(a,e.chartArea,0)||a.inRange(t.x,t.y,r)&&s.push({element:a,datasetIndex:l,index:c})},!0),s}function E7(e,t,o,r){let i=[];function s(n,a,l){let{startAngle:c,endAngle:d}=n.getProps(["startAngle","endAngle"],r),{angle:p}=Oh(n,{x:t.x,y:t.y});Sc(p,c,d)&&i.push({element:n,datasetIndex:a,index:l})}return ma(e,o,t,s),i}function R7(e,t,o,r,i,s){let n=[],a=D7(o),l=Number.POSITIVE_INFINITY;function c(d,p,u){let m=d.inRange(t.x,t.y,i);if(r&&!m)return;let b=d.getCenterPoint(i);if(!(!!s||e.isPointInArea(b))&&!m)return;let y=a(t,b);y<l?(n=[{element:d,datasetIndex:p,index:u}],l=y):y===l&&n.push({element:d,datasetIndex:p,index:u})}return ma(e,o,t,c),n}function Kh(e,t,o,r,i,s){return!s&&!e.isPointInArea(t)?[]:o==="r"&&!r?E7(e,t,o,i):R7(e,t,o,r,i,s)}function og(e,t,o,r,i){let s=[],n=o==="x"?"inXRange":"inYRange",a=!1;return ma(e,o,t,(l,c,d)=>{l[n]&&l[n](t[o],i)&&(s.push({element:l,datasetIndex:c,index:d}),a=a||l.inRange(t.x,t.y,i))}),r&&!a?[]:s}var z7={evaluateInteractionItems:ma,modes:{index(e,t,o,r){let i=di(t,e),s=o.axis||"x",n=o.includeInvisible||!1,a=o.intersect?Xh(e,i,s,r,n):Kh(e,i,s,!1,r,n),l=[];return a.length?(e.getSortedVisibleDatasetMetas().forEach(c=>{let d=a[0].index,p=c.data[d];p&&!p.skip&&l.push({element:p,datasetIndex:c.index,index:d})}),l):[]},dataset(e,t,o,r){let i=di(t,e),s=o.axis||"xy",n=o.includeInvisible||!1,a=o.intersect?Xh(e,i,s,r,n):Kh(e,i,s,!1,r,n);if(a.length>0){let l=a[0].datasetIndex,c=e.getDatasetMeta(l).data;a=[];for(let d=0;d<c.length;++d)a.push({element:c[d],datasetIndex:l,index:d})}return a},point(e,t,o,r){let i=di(t,e),s=o.axis||"xy",n=o.includeInvisible||!1;return Xh(e,i,s,r,n)},nearest(e,t,o,r){let i=di(t,e),s=o.axis||"xy",n=o.includeInvisible||!1;return Kh(e,i,s,o.intersect,r,n)},x(e,t,o,r){let i=di(t,e);return og(e,i,"x",o.intersect,r)},y(e,t,o,r){let i=di(t,e);return og(e,i,"y",o.intersect,r)}}},Ug=["left","top","right","bottom"];function la(e,t){return e.filter(o=>o.pos===t)}function rg(e,t){return e.filter(o=>Ug.indexOf(o.pos)===-1&&o.box.axis===t)}function ca(e,t){return e.sort((o,r)=>{let i=t?r:o,s=t?o:r;return i.weight===s.weight?i.index-s.index:i.weight-s.weight})}function H7(e){let t=[],o,r,i,s,n,a;for(o=0,r=(e||[]).length;o<r;++o)i=e[o],{position:s,options:{stack:n,stackWeight:a=1}}=i,t.push({index:o,box:i,pos:s,horizontal:i.isHorizontal(),weight:i.weight,stack:n&&s+n,stackWeight:a});return t}function B7(e){let t={};for(let o of e){let{stack:r,pos:i,stackWeight:s}=o;if(!r||!Ug.includes(i))continue;let n=t[r]||(t[r]={count:0,placed:0,weight:0,size:0});n.count++,n.weight+=s}return t}function I7(e,t){let o=B7(e),{vBoxMaxWidth:r,hBoxMaxHeight:i}=t,s,n,a;for(s=0,n=e.length;s<n;++s){a=e[s];let{fullSize:l}=a.box,c=o[a.stack],d=c&&a.stackWeight/c.weight;a.horizontal?(a.width=d?d*r:l&&t.availableWidth,a.height=i):(a.width=r,a.height=d?d*i:l&&t.availableHeight)}return o}function Z7(e){let t=H7(e),o=ca(t.filter(c=>c.box.fullSize),!0),r=ca(la(t,"left"),!0),i=ca(la(t,"right")),s=ca(la(t,"top"),!0),n=ca(la(t,"bottom")),a=rg(t,"x"),l=rg(t,"y");return{fullSize:o,leftAndTop:r.concat(s),rightAndBottom:i.concat(l).concat(n).concat(a),chartArea:la(t,"chartArea"),vertical:r.concat(i).concat(l),horizontal:s.concat(n).concat(a)}}function ig(e,t,o,r){return Math.max(e[o],t[o])+Math.max(e[r],t[r])}function Gg(e,t){e.top=Math.max(e.top,t.top),e.left=Math.max(e.left,t.left),e.bottom=Math.max(e.bottom,t.bottom),e.right=Math.max(e.right,t.right)}function F7(e,t,o,r){let{pos:i,box:s}=o,n=e.maxPadding;if(!Ve(i)){o.size&&(e[i]-=o.size);let p=r[o.stack]||{size:0,count:1};p.size=Math.max(p.size,o.horizontal?s.height:s.width),o.size=p.size/p.count,e[i]+=o.size}s.getPadding&&Gg(n,s.getPadding());let a=Math.max(0,t.outerWidth-ig(n,e,"left","right")),l=Math.max(0,t.outerHeight-ig(n,e,"top","bottom")),c=a!==e.w,d=l!==e.h;return e.w=a,e.h=l,o.horizontal?{same:c,other:d}:{same:d,other:c}}function N7(e){let t=e.maxPadding;function o(r){let i=Math.max(t[r]-e[r],0);return e[r]+=i,i}e.y+=o("top"),e.x+=o("left"),o("right"),o("bottom")}function j7(e,t){let o=t.maxPadding;function r(i){let s={left:0,top:0,right:0,bottom:0};return i.forEach(n=>{s[n]=Math.max(t[n],o[n])}),s}return r(e?["left","right"]:["top","bottom"])}function pa(e,t,o,r){let i=[],s,n,a,l,c,d;for(s=0,n=e.length,c=0;s<n;++s){a=e[s],l=a.box,l.update(a.width||t.w,a.height||t.h,j7(a.horizontal,t));let{same:p,other:u}=F7(t,o,a,r);c|=p&&i.length,d=d||u,l.fullSize||i.push(a)}return c&&pa(i,t,o,r)||d}function Zc(e,t,o,r,i){e.top=o,e.left=t,e.right=t+r,e.bottom=o+i,e.width=r,e.height=i}function sg(e,t,o,r){let i=o.padding,{x:s,y:n}=t;for(let a of e){let l=a.box,c=r[a.stack]||{count:1,placed:0,weight:1},d=a.stackWeight/c.weight||1;if(a.horizontal){let p=t.w*d,u=c.size||l.height;ra(c.start)&&(n=c.start),l.fullSize?Zc(l,i.left,n,o.outerWidth-i.right-i.left,u):Zc(l,t.left+c.placed,n,p,u),c.start=n,c.placed+=p,n=l.bottom}else{let p=t.h*d,u=c.size||l.width;ra(c.start)&&(s=c.start),l.fullSize?Zc(l,s,i.top,u,o.outerHeight-i.bottom-i.top):Zc(l,s,t.top+c.placed,u,p),c.start=s,c.placed+=p,s=l.right}}t.x=s,t.y=n}var Fc={addBox(e,t){e.boxes||(e.boxes=[]),t.fullSize=t.fullSize||!1,t.position=t.position||"top",t.weight=t.weight||0,t._layers=t._layers||function(){return[{z:0,draw(o){t.draw(o)}}]},e.boxes.push(t)},removeBox(e,t){let o=e.boxes?e.boxes.indexOf(t):-1;o!==-1&&e.boxes.splice(o,1)},configure(e,t,o){t.fullSize=o.fullSize,t.position=o.position,t.weight=o.weight},update(e,t,o,r){if(!e)return;let i=ko(e.options.layout.padding),s=Math.max(t-i.width,0),n=Math.max(o-i.height,0),a=Z7(e.boxes),l=a.vertical,c=a.horizontal;Fe(e.boxes,C=>{typeof C.beforeLayout=="function"&&C.beforeLayout()});let d=l.reduce((C,y)=>y.box.options&&y.box.options.display===!1?C:C+1,0)||1,p=Object.freeze({outerWidth:t,outerHeight:o,padding:i,availableWidth:s,availableHeight:n,vBoxMaxWidth:s/2/d,hBoxMaxHeight:n/2}),u=Object.assign({},i);Gg(u,ko(r));let m=Object.assign({maxPadding:u,w:s,h:n,x:i.left,y:i.top},i),b=I7(l.concat(c),p);pa(a.fullSize,m,p,b),pa(l,m,p,b),pa(c,m,p,b)&&pa(l,m,p,b),N7(m),sg(a.leftAndTop,m,p,b),m.x+=m.w,m.y+=m.h,sg(a.rightAndBottom,m,p,b),e.chartArea={left:m.left,top:m.top,right:m.left+m.w,bottom:m.top+m.h,height:m.h,width:m.w},Fe(a.chartArea,C=>{let y=C.box;Object.assign(y,e.chartArea),y.update(m.w,m.h,{left:0,top:0,right:0,bottom:0})})}},Qc=class{acquireContext(t,o){}releaseContext(t){return!1}addEventListener(t,o,r){}removeEventListener(t,o,r){}getDevicePixelRatio(){return 1}getMaximumSize(t,o,r,i){return o=Math.max(0,o||t.width),r=r||t.height,{width:o,height:Math.max(0,i?Math.floor(o/i):r)}}isAttached(t){return!0}updateConfig(t){}},ip=class extends Qc{acquireContext(t){return t&&t.getContext&&t.getContext("2d")||null}updateConfig(t){t.options.animation=!1}},Gc="$chartjs",W7={touchstart:"mousedown",touchmove:"mousemove",touchend:"mouseup",pointerenter:"mouseenter",pointerdown:"mousedown",pointermove:"mousemove",pointerup:"mouseup",pointerleave:"mouseout",pointerout:"mouseout"},ng=e=>e===null||e==="";function U7(e,t){let o=e.style,r=e.getAttribute("height"),i=e.getAttribute("width");if(e[Gc]={initial:{height:r,width:i,style:{display:o.display,height:o.height,width:o.width}}},o.display=o.display||"block",o.boxSizing=o.boxSizing||"border-box",ng(i)){let s=Nh(e,"width");s!==void 0&&(e.width=s)}if(ng(r))if(e.style.height==="")e.height=e.width/(t||2);else{let s=Nh(e,"height");s!==void 0&&(e.height=s)}return e}var Yg=Nf?{passive:!0}:!1;function G7(e,t,o){e&&e.addEventListener(t,o,Yg)}function Y7(e,t,o){e&&e.canvas&&e.canvas.removeEventListener(t,o,Yg)}function q7(e,t){let o=W7[e.type]||e.type,{x:r,y:i}=di(e,t);return{type:o,chart:t,native:e,x:r!==void 0?r:null,y:i!==void 0?i:null}}function Jc(e,t){for(let o of e)if(o===t||o.contains(t))return!0}function X7(e,t,o){let r=e.canvas,i=new MutationObserver(s=>{let n=!1;for(let a of s)n=n||Jc(a.addedNodes,r),n=n&&!Jc(a.removedNodes,r);n&&o()});return i.observe(document,{childList:!0,subtree:!0}),i}function K7(e,t,o){let r=e.canvas,i=new MutationObserver(s=>{let n=!1;for(let a of s)n=n||Jc(a.removedNodes,r),n=n&&!Jc(a.addedNodes,r);n&&o()});return i.observe(document,{childList:!0,subtree:!0}),i}var fa=new Map,ag=0;function qg(){let e=window.devicePixelRatio;e!==ag&&(ag=e,fa.forEach((t,o)=>{o.currentDevicePixelRatio!==e&&t()}))}function Q7(e,t){fa.size||window.addEventListener("resize",qg),fa.set(e,t)}function J7(e){fa.delete(e),fa.size||window.removeEventListener("resize",qg)}function e6(e,t,o){let r=e.canvas,i=r&&Hc(r);if(!i)return;let s=Dh((a,l)=>{let c=i.clientWidth;o(a,l),c<i.clientWidth&&o()},window),n=new ResizeObserver(a=>{let l=a[0],c=l.contentRect.width,d=l.contentRect.height;c===0&&d===0||s(c,d)});return n.observe(i),Q7(e,s),n}function Qh(e,t,o){o&&o.disconnect(),t==="resize"&&J7(e)}function t6(e,t,o){let r=e.canvas,i=Dh(s=>{e.ctx!==null&&o(q7(s,e))},e);return G7(r,t,i),i}var sp=class extends Qc{acquireContext(t,o){let r=t&&t.getContext&&t.getContext("2d");return r&&r.canvas===t?(U7(t,o),r):null}releaseContext(t){let o=t.canvas;if(!o[Gc])return!1;let r=o[Gc].initial;["height","width"].forEach(s=>{let n=r[s];Ze(n)?o.removeAttribute(s):o.setAttribute(s,n)});let i=r.style||{};return Object.keys(i).forEach(s=>{o.style[s]=i[s]}),o.width=o.width,delete o[Gc],!0}addEventListener(t,o,r){this.removeEventListener(t,o);let i=t.$proxies||(t.$proxies={}),n={attach:X7,detach:K7,resize:e6}[o]||t6;i[o]=n(t,o,r)}removeEventListener(t,o){let r=t.$proxies||(t.$proxies={}),i=r[o];if(!i)return;({attach:Qh,detach:Qh,resize:Qh}[o]||Y7)(t,o,i),r[o]=void 0}getDevicePixelRatio(){return window.devicePixelRatio}getMaximumSize(t,o,r,i){return Ff(t,o,r,i)}isAttached(t){let o=t&&Hc(t);return!!(o&&o.isConnected)}};function o6(e){return!zc()||typeof OffscreenCanvas<"u"&&e instanceof OffscreenCanvas?ip:sp}var hi=class{static defaults={};static defaultRoutes=void 0;x;y;active=!1;options;$animations;tooltipPosition(t){let{x:o,y:r}=this.getProps(["x","y"],t);return{x:o,y:r}}hasValue(){return Xs(this.x)&&Xs(this.y)}getProps(t,o){let r=this.$animations;if(!o||!r)return this;let i={};return t.forEach(s=>{i[s]=r[s]&&r[s].active()?r[s]._to:this[s]}),i}};function r6(e,t){let o=e.options.ticks,r=i6(e),i=Math.min(o.maxTicksLimit||r,r),s=o.major.enabled?n6(t):[],n=s.length,a=s[0],l=s[n-1],c=[];if(n>i)return a6(t,c,s,n/i),c;let d=s6(s,t,i);if(n>0){let p,u,m=n>1?Math.round((l-a)/(n-1)):null;for(Nc(t,c,d,Ze(m)?0:a-m,a),p=0,u=n-1;p<u;p++)Nc(t,c,d,s[p],s[p+1]);return Nc(t,c,d,l,Ze(m)?t.length:l+m),c}return Nc(t,c,d),c}function i6(e){let t=e.options.offset,o=e._tickSize(),r=e._length/o+(t?0:1),i=e._maxLength/o;return Math.floor(Math.min(r,i))}function s6(e,t,o){let r=l6(e),i=t.length/o;if(!r)return Math.max(i,1);let s=bf(r);for(let n=0,a=s.length-1;n<a;n++){let l=s[n];if(l>i)return l}return Math.max(i,1)}function n6(e){let t=[],o,r;for(o=0,r=e.length;o<r;o++)e[o].major&&t.push(o);return t}function a6(e,t,o,r){let i=0,s=o[0],n;for(r=Math.ceil(r),n=0;n<e.length;n++)n===s&&(t.push(e[n]),i++,s=o[i*r])}function Nc(e,t,o,r,i){let s=ze(r,0),n=Math.min(ze(i,e.length),e.length),a=0,l,c,d;for(o=Math.ceil(o),i&&(l=i-r,o=l/Math.floor(l/o)),d=s;d<0;)a++,d=Math.round(s+a*o);for(c=Math.max(s,0);c<n;c++)c===d&&(t.push(e[c]),a++,d=Math.round(s+a*o))}function l6(e){let t=e.length,o,r;if(t<2)return!1;for(r=e[0],o=1;o<t;++o)if(e[o]-e[o-1]!==r)return!1;return r}var c6=e=>e==="left"?"right":e==="right"?"left":e,lg=(e,t,o)=>t==="top"||t==="left"?e[t]+o:e[t]-o,cg=(e,t)=>Math.min(t||e,e);function dg(e,t){let o=[],r=e.length/t,i=e.length,s=0;for(;s<i;s+=r)o.push(e[Math.floor(s)]);return o}function d6(e,t,o){let r=e.ticks.length,i=Math.min(t,r-1),s=e._startPixel,n=e._endPixel,a=1e-6,l=e.getPixelForTick(i),c;if(!(o&&(r===1?c=Math.max(l-s,n-l):t===0?c=(e.getPixelForTick(1)-l)/2:c=(l-e.getPixelForTick(i-1))/2,l+=i<t?c:-c,l<s-a||l>n+a)))return l}function h6(e,t){Fe(e,o=>{let r=o.gc,i=r.length/2,s;if(i>t){for(s=0;s<i;++s)delete o.data[r[s]];r.splice(0,i)}})}function da(e){return e.drawTicks?e.tickLength:0}function hg(e,t){if(!e.display)return 0;let o=uo(e.font,t),r=ko(e.padding);return(ct(e.text)?e.text.length:1)*o.lineHeight+r.height}function p6(e,t){return Vr(e,{scale:t,type:"scale"})}function u6(e,t,o){return Vr(e,{tick:o,index:t,type:"tick"})}function f6(e,t,o){let r=Mf(e);return(o&&t!=="right"||!o&&t==="right")&&(r=c6(r)),r}function g6(e,t,o,r){let{top:i,left:s,bottom:n,right:a,chart:l}=e,{chartArea:c,scales:d}=l,p=0,u,m,b,C=n-i,y=a-s;if(e.isHorizontal()){if(m=Eh(r,s,a),Ve(o)){let k=Object.keys(o)[0],$=o[k];b=d[k].getPixelForValue($)+C-t}else o==="center"?b=(c.bottom+c.top)/2+C-t:b=lg(e,o,t);u=a-s}else{if(Ve(o)){let k=Object.keys(o)[0],$=o[k];m=d[k].getPixelForValue($)-y+t}else o==="center"?m=(c.left+c.right)/2-y+t:m=lg(e,o,t);b=Eh(r,n,i),p=o==="left"?-Ct:Ct}return{titleX:m,titleY:b,maxWidth:u,rotation:p}}var es=class e extends hi{constructor(t){super(),this.id=t.id,this.type=t.type,this.options=void 0,this.ctx=t.ctx,this.chart=t.chart,this.top=void 0,this.bottom=void 0,this.left=void 0,this.right=void 0,this.width=void 0,this.height=void 0,this._margins={left:0,right:0,top:0,bottom:0},this.maxWidth=void 0,this.maxHeight=void 0,this.paddingTop=void 0,this.paddingBottom=void 0,this.paddingLeft=void 0,this.paddingRight=void 0,this.axis=void 0,this.labelRotation=void 0,this.min=void 0,this.max=void 0,this._range=void 0,this.ticks=[],this._gridLineItems=null,this._labelItems=null,this._labelSizes=null,this._length=0,this._maxLength=0,this._longestTextCache={},this._startPixel=void 0,this._endPixel=void 0,this._reversePixels=!1,this._userMax=void 0,this._userMin=void 0,this._suggestedMax=void 0,this._suggestedMin=void 0,this._ticksLength=0,this._borderValue=0,this._cache={},this._dataLimitsCached=!1,this.$context=void 0}init(t){this.options=t.setContext(this.getContext()),this.axis=t.axis,this._userMin=this.parse(t.min),this._userMax=this.parse(t.max),this._suggestedMin=this.parse(t.suggestedMin),this._suggestedMax=this.parse(t.suggestedMax)}parse(t,o){return t}getUserBounds(){let{_userMin:t,_userMax:o,_suggestedMin:r,_suggestedMax:i}=this;return t=po(t,Number.POSITIVE_INFINITY),o=po(o,Number.NEGATIVE_INFINITY),r=po(r,Number.POSITIVE_INFINITY),i=po(i,Number.NEGATIVE_INFINITY),{min:po(t,r),max:po(o,i),minDefined:ht(t),maxDefined:ht(o)}}getMinMax(t){let{min:o,max:r,minDefined:i,maxDefined:s}=this.getUserBounds(),n;if(i&&s)return{min:o,max:r};let a=this.getMatchingVisibleMetas();for(let l=0,c=a.length;l<c;++l)n=a[l].controller.getMinMax(this,t),i||(o=Math.min(o,n.min)),s||(r=Math.max(r,n.max));return o=s&&o>r?r:o,r=i&&o>r?o:r,{min:po(o,po(r,o)),max:po(r,po(o,r))}}getPadding(){return{left:this.paddingLeft||0,top:this.paddingTop||0,right:this.paddingRight||0,bottom:this.paddingBottom||0}}getTicks(){return this.ticks}getLabels(){let t=this.chart.data;return this.options.labels||(this.isHorizontal()?t.xLabels:t.yLabels)||t.labels||[]}getLabelItems(t=this.chart.chartArea){return this._labelItems||(this._labelItems=this._computeLabelItems(t))}beforeLayout(){this._cache={},this._dataLimitsCached=!1}beforeUpdate(){pt(this.options.beforeUpdate,[this])}update(t,o,r){let{beginAtZero:i,grace:s,ticks:n}=this.options,a=n.sampleSize;this.beforeUpdate(),this.maxWidth=t,this.maxHeight=o,this._margins=r=Object.assign({left:0,right:0,top:0,bottom:0},r),this.ticks=null,this._labelSizes=null,this._gridLineItems=null,this._labelItems=null,this.beforeSetDimensions(),this.setDimensions(),this.afterSetDimensions(),this._maxLength=this.isHorizontal()?this.width+r.left+r.right:this.height+r.top+r.bottom,this._dataLimitsCached||(this.beforeDataLimits(),this.determineDataLimits(),this.afterDataLimits(),this._range=Rf(this,s,i),this._dataLimitsCached=!0),this.beforeBuildTicks(),this.ticks=this.buildTicks()||[],this.afterBuildTicks();let l=a<this.ticks.length;this._convertTicksToLabels(l?dg(this.ticks,a):this.ticks),this.configure(),this.beforeCalculateLabelRotation(),this.calculateLabelRotation(),this.afterCalculateLabelRotation(),n.display&&(n.autoSkip||n.source==="auto")&&(this.ticks=r6(this,this.ticks),this._labelSizes=null,this.afterAutoSkip()),l&&this._convertTicksToLabels(this.ticks),this.beforeFit(),this.fit(),this.afterFit(),this.afterUpdate()}configure(){let t=this.options.reverse,o,r;this.isHorizontal()?(o=this.left,r=this.right):(o=this.top,r=this.bottom,t=!t),this._startPixel=o,this._endPixel=r,this._reversePixels=t,this._length=r-o,this._alignToPixels=this.options.alignToPixels}afterUpdate(){pt(this.options.afterUpdate,[this])}beforeSetDimensions(){pt(this.options.beforeSetDimensions,[this])}setDimensions(){this.isHorizontal()?(this.width=this.maxWidth,this.left=0,this.right=this.width):(this.height=this.maxHeight,this.top=0,this.bottom=this.height),this.paddingLeft=0,this.paddingTop=0,this.paddingRight=0,this.paddingBottom=0}afterSetDimensions(){pt(this.options.afterSetDimensions,[this])}_callHooks(t){this.chart.notifyPlugins(t,this.getContext()),pt(this.options[t],[this])}beforeDataLimits(){this._callHooks("beforeDataLimits")}determineDataLimits(){}afterDataLimits(){this._callHooks("afterDataLimits")}beforeBuildTicks(){this._callHooks("beforeBuildTicks")}buildTicks(){return[]}afterBuildTicks(){this._callHooks("afterBuildTicks")}beforeTickToLabelConversion(){pt(this.options.beforeTickToLabelConversion,[this])}generateTickLabels(t){let o=this.options.ticks,r,i,s;for(r=0,i=t.length;r<i;r++)s=t[r],s.label=pt(o.callback,[s.value,r,t],this)}afterTickToLabelConversion(){pt(this.options.afterTickToLabelConversion,[this])}beforeCalculateLabelRotation(){pt(this.options.beforeCalculateLabelRotation,[this])}calculateLabelRotation(){let t=this.options,o=t.ticks,r=cg(this.ticks.length,t.ticks.maxTicksLimit),i=o.minRotation||0,s=o.maxRotation,n=i,a,l,c;if(!this._isVisible()||!o.display||i>=s||r<=1||!this.isHorizontal()){this.labelRotation=i;return}let d=this._getLabelSizes(),p=d.widest.width,u=d.highest.height,m=Yt(this.chart.width-p,0,this.maxWidth);a=t.offset?this.maxWidth/r:m/(r-1),p+6>a&&(a=m/(r-(t.offset?.5:1)),l=this.maxHeight-da(t.grid)-o.padding-hg(t.title,this.chart.options.font),c=Math.sqrt(p*p+u*u),n=Lc(Math.min(Math.asin(Yt((d.highest.height+6)/a,-1,1)),Math.asin(Yt(l/c,-1,1))-Math.asin(Yt(u/c,-1,1)))),n=Math.max(i,Math.min(s,n))),this.labelRotation=n}afterCalculateLabelRotation(){pt(this.options.afterCalculateLabelRotation,[this])}afterAutoSkip(){}beforeFit(){pt(this.options.beforeFit,[this])}fit(){let t={width:0,height:0},{chart:o,options:{ticks:r,title:i,grid:s}}=this,n=this._isVisible(),a=this.isHorizontal();if(n){let l=hg(i,o.options.font);if(a?(t.width=this.maxWidth,t.height=da(s)+l):(t.height=this.maxHeight,t.width=da(s)+l),r.display&&this.ticks.length){let{first:c,last:d,widest:p,highest:u}=this._getLabelSizes(),m=r.padding*2,b=Or(this.labelRotation),C=Math.cos(b),y=Math.sin(b);if(a){let k=r.mirror?0:y*p.width+C*u.height;t.height=Math.min(this.maxHeight,t.height+k+m)}else{let k=r.mirror?0:C*p.width+y*u.height;t.width=Math.min(this.maxWidth,t.width+k+m)}this._calculatePadding(c,d,y,C)}}this._handleMargins(),a?(this.width=this._length=o.width-this._margins.left-this._margins.right,this.height=t.height):(this.width=t.width,this.height=this._length=o.height-this._margins.top-this._margins.bottom)}_calculatePadding(t,o,r,i){let{ticks:{align:s,padding:n},position:a}=this.options,l=this.labelRotation!==0,c=a!=="top"&&this.axis==="x";if(this.isHorizontal()){let d=this.getPixelForTick(0)-this.left,p=this.right-this.getPixelForTick(this.ticks.length-1),u=0,m=0;l?c?(u=i*t.width,m=r*o.height):(u=r*t.height,m=i*o.width):s==="start"?m=o.width:s==="end"?u=t.width:s!=="inner"&&(u=t.width/2,m=o.width/2),this.paddingLeft=Math.max((u-d+n)*this.width/(this.width-d),0),this.paddingRight=Math.max((m-p+n)*this.width/(this.width-p),0)}else{let d=o.height/2,p=t.height/2;s==="start"?(d=0,p=t.height):s==="end"&&(d=o.height,p=0),this.paddingTop=d+n,this.paddingBottom=p+n}}_handleMargins(){this._margins&&(this._margins.left=Math.max(this.paddingLeft,this._margins.left),this._margins.top=Math.max(this.paddingTop,this._margins.top),this._margins.right=Math.max(this.paddingRight,this._margins.right),this._margins.bottom=Math.max(this.paddingBottom,this._margins.bottom))}afterFit(){pt(this.options.afterFit,[this])}isHorizontal(){let{axis:t,position:o}=this.options;return o==="top"||o==="bottom"||t==="x"}isFullSize(){return this.options.fullSize}_convertTicksToLabels(t){this.beforeTickToLabelConversion(),this.generateTickLabels(t);let o,r;for(o=0,r=t.length;o<r;o++)Ze(t[o].label)&&(t.splice(o,1),r--,o--);this.afterTickToLabelConversion()}_getLabelSizes(){let t=this._labelSizes;if(!t){let o=this.options.ticks.sampleSize,r=this.ticks;o<r.length&&(r=dg(r,o)),this._labelSizes=t=this._computeLabelSizes(r,r.length,this.options.ticks.maxTicksLimit)}return t}_computeLabelSizes(t,o,r){let{ctx:i,_longestTextCache:s}=this,n=[],a=[],l=Math.floor(o/cg(o,r)),c=0,d=0,p,u,m,b,C,y,k,$,V,O,P;for(p=0;p<o;p+=l){if(b=t[p].label,C=this._resolveTickFontOptions(p),i.font=y=C.string,k=s[y]=s[y]||{data:{},gc:[]},$=C.lineHeight,V=O=0,!Ze(b)&&!ct(b))V=ea(i,k.data,k.gc,V,b),O=$;else if(ct(b))for(u=0,m=b.length;u<m;++u)P=b[u],!Ze(P)&&!ct(P)&&(V=ea(i,k.data,k.gc,V,P),O+=$);n.push(V),a.push(O),c=Math.max(V,c),d=Math.max(O,d)}h6(s,o);let T=n.indexOf(c),Z=a.indexOf(d),R=D=>({width:n[D]||0,height:a[D]||0});return{first:R(0),last:R(o-1),widest:R(T),highest:R(Z),widths:n,heights:a}}getLabelForValue(t){return t}getPixelForValue(t,o){return NaN}getValueForPixel(t){}getPixelForTick(t){let o=this.ticks;return t<0||t>o.length-1?null:this.getPixelForValue(o[t].value)}getPixelForDecimal(t){this._reversePixels&&(t=1-t);let o=this._startPixel+t*this._length;return yf(this._alignToPixels?ci(this.chart,o,0):o)}getDecimalForPixel(t){let o=(t-this._startPixel)/this._length;return this._reversePixels?1-o:o}getBasePixel(){return this.getPixelForValue(this.getBaseValue())}getBaseValue(){let{min:t,max:o}=this;return t<0&&o<0?o:t>0&&o>0?t:0}getContext(t){let o=this.ticks||[];if(t>=0&&t<o.length){let r=o[t];return r.$context||(r.$context=u6(this.getContext(),t,r))}return this.$context||(this.$context=p6(this.chart.getContext(),this))}_tickSize(){let t=this.options.ticks,o=Or(this.labelRotation),r=Math.abs(Math.cos(o)),i=Math.abs(Math.sin(o)),s=this._getLabelSizes(),n=t.autoSkipPadding||0,a=s?s.widest.width+n:0,l=s?s.highest.height+n:0;return this.isHorizontal()?l*r>a*i?a/r:l/i:l*i<a*r?l/r:a/i}_isVisible(){let t=this.options.display;return t!=="auto"?!!t:this.getMatchingVisibleMetas().length>0}_computeGridLineItems(t){let o=this.axis,r=this.chart,i=this.options,{grid:s,position:n,border:a}=i,l=s.offset,c=this.isHorizontal(),p=this.ticks.length+(l?1:0),u=da(s),m=[],b=a.setContext(this.getContext()),C=b.display?b.width:0,y=C/2,k=function(j){return ci(r,j,C)},$,V,O,P,T,Z,R,D,N,B,Y,I;if(n==="top")$=k(this.bottom),Z=this.bottom-u,D=$-y,B=k(t.top)+y,I=t.bottom;else if(n==="bottom")$=k(this.top),B=t.top,I=k(t.bottom)-y,Z=$+y,D=this.top+u;else if(n==="left")$=k(this.right),T=this.right-u,R=$-y,N=k(t.left)+y,Y=t.right;else if(n==="right")$=k(this.left),N=t.left,Y=k(t.right)-y,T=$+y,R=this.left+u;else if(o==="x"){if(n==="center")$=k((t.top+t.bottom)/2+.5);else if(Ve(n)){let j=Object.keys(n)[0],F=n[j];$=k(this.chart.scales[j].getPixelForValue(F))}B=t.top,I=t.bottom,Z=$+y,D=Z+u}else if(o==="y"){if(n==="center")$=k((t.left+t.right)/2);else if(Ve(n)){let j=Object.keys(n)[0],F=n[j];$=k(this.chart.scales[j].getPixelForValue(F))}T=$-y,R=T-u,N=t.left,Y=t.right}let H=ze(i.ticks.maxTicksLimit,p),W=Math.max(1,Math.ceil(p/H));for(V=0;V<p;V+=W){let j=this.getContext(V),F=s.setContext(j),me=a.setContext(j),ae=F.lineWidth,le=F.color,ve=me.dash||[],X=me.dashOffset,G=F.tickWidth,he=F.tickColor,fe=F.tickBorderDash||[],J=F.tickBorderDashOffset;O=d6(this,V,l),O!==void 0&&(P=ci(r,O,ae),c?T=R=N=Y=P:Z=D=B=I=P,m.push({tx1:T,ty1:Z,tx2:R,ty2:D,x1:N,y1:B,x2:Y,y2:I,width:ae,color:le,borderDash:ve,borderDashOffset:X,tickWidth:G,tickColor:he,tickBorderDash:fe,tickBorderDashOffset:J}))}return this._ticksLength=p,this._borderValue=$,m}_computeLabelItems(t){let o=this.axis,r=this.options,{position:i,ticks:s}=r,n=this.isHorizontal(),a=this.ticks,{align:l,crossAlign:c,padding:d,mirror:p}=s,u=da(r.grid),m=u+d,b=p?-d:m,C=-Or(this.labelRotation),y=[],k,$,V,O,P,T,Z,R,D,N,B,Y,I="middle";if(i==="top")T=this.bottom-b,Z=this._getXAxisLabelAlignment();else if(i==="bottom")T=this.top+b,Z=this._getXAxisLabelAlignment();else if(i==="left"){let W=this._getYAxisLabelAlignment(u);Z=W.textAlign,P=W.x}else if(i==="right"){let W=this._getYAxisLabelAlignment(u);Z=W.textAlign,P=W.x}else if(o==="x"){if(i==="center")T=(t.top+t.bottom)/2+m;else if(Ve(i)){let W=Object.keys(i)[0],j=i[W];T=this.chart.scales[W].getPixelForValue(j)+m}Z=this._getXAxisLabelAlignment()}else if(o==="y"){if(i==="center")P=(t.left+t.right)/2-m;else if(Ve(i)){let W=Object.keys(i)[0],j=i[W];P=this.chart.scales[W].getPixelForValue(j)}Z=this._getYAxisLabelAlignment(u).textAlign}o==="y"&&(l==="start"?I="top":l==="end"&&(I="bottom"));let H=this._getLabelSizes();for(k=0,$=a.length;k<$;++k){V=a[k],O=V.label;let W=s.setContext(this.getContext(k));R=this.getPixelForTick(k)+s.labelOffset,D=this._resolveTickFontOptions(k),N=D.lineHeight,B=ct(O)?O.length:1;let j=B/2,F=W.color,me=W.textStrokeColor,ae=W.textStrokeWidth,le=Z;n?(P=R,Z==="inner"&&(k===$-1?le=this.options.reverse?"left":"right":k===0?le=this.options.reverse?"right":"left":le="center"),i==="top"?c==="near"||C!==0?Y=-B*N+N/2:c==="center"?Y=-H.highest.height/2-j*N+N:Y=-H.highest.height+N/2:c==="near"||C!==0?Y=N/2:c==="center"?Y=H.highest.height/2-j*N:Y=H.highest.height-B*N,p&&(Y*=-1),C!==0&&!W.showLabelBackdrop&&(P+=N/2*Math.sin(C))):(T=R,Y=(1-B)*N/2);let ve;if(W.showLabelBackdrop){let X=ko(W.backdropPadding),G=H.heights[k],he=H.widths[k],fe=Y-X.top,J=0-X.left;switch(I){case"middle":fe-=G/2;break;case"bottom":fe-=G;break}switch(Z){case"center":J-=he/2;break;case"right":J-=he;break;case"inner":k===$-1?J-=he:k>0&&(J-=he/2);break}ve={left:J,top:fe,width:he+X.width,height:G+X.height,color:W.backdropColor}}y.push({label:O,font:D,textOffset:Y,options:{rotation:C,color:F,strokeColor:me,strokeWidth:ae,textAlign:le,textBaseline:I,translation:[P,T],backdrop:ve}})}return y}_getXAxisLabelAlignment(){let{position:t,ticks:o}=this.options;if(-Or(this.labelRotation))return t==="top"?"left":"right";let i="center";return o.align==="start"?i="left":o.align==="end"?i="right":o.align==="inner"&&(i="inner"),i}_getYAxisLabelAlignment(t){let{position:o,ticks:{crossAlign:r,mirror:i,padding:s}}=this.options,n=this._getLabelSizes(),a=t+s,l=n.widest.width,c,d;return o==="left"?i?(d=this.right+s,r==="near"?c="left":r==="center"?(c="center",d+=l/2):(c="right",d+=l)):(d=this.right-a,r==="near"?c="right":r==="center"?(c="center",d-=l/2):(c="left",d=this.left)):o==="right"?i?(d=this.left+s,r==="near"?c="right":r==="center"?(c="center",d-=l/2):(c="left",d-=l)):(d=this.left+a,r==="near"?c="left":r==="center"?(c="center",d+=l/2):(c="right",d=this.right)):c="right",{textAlign:c,x:d}}_computeLabelArea(){if(this.options.ticks.mirror)return;let t=this.chart,o=this.options.position;if(o==="left"||o==="right")return{top:0,left:this.left,bottom:t.height,right:this.right};if(o==="top"||o==="bottom")return{top:this.top,left:0,bottom:this.bottom,right:t.width}}drawBackground(){let{ctx:t,options:{backgroundColor:o},left:r,top:i,width:s,height:n}=this;o&&(t.save(),t.fillStyle=o,t.fillRect(r,i,s,n),t.restore())}getLineWidthForValue(t){let o=this.options.grid;if(!this._isVisible()||!o.display)return 0;let i=this.ticks.findIndex(s=>s.value===t);return i>=0?o.setContext(this.getContext(i)).lineWidth:0}drawGrid(t){let o=this.options.grid,r=this.ctx,i=this._gridLineItems||(this._gridLineItems=this._computeGridLineItems(t)),s,n,a=(l,c,d)=>{!d.width||!d.color||(r.save(),r.lineWidth=d.width,r.strokeStyle=d.color,r.setLineDash(d.borderDash||[]),r.lineDashOffset=d.borderDashOffset,r.beginPath(),r.moveTo(l.x,l.y),r.lineTo(c.x,c.y),r.stroke(),r.restore())};if(o.display)for(s=0,n=i.length;s<n;++s){let l=i[s];o.drawOnChartArea&&a({x:l.x1,y:l.y1},{x:l.x2,y:l.y2},l),o.drawTicks&&a({x:l.tx1,y:l.ty1},{x:l.tx2,y:l.ty2},{color:l.tickColor,width:l.tickWidth,borderDash:l.tickBorderDash,borderDashOffset:l.tickBorderDashOffset})}}drawBorder(){let{chart:t,ctx:o,options:{border:r,grid:i}}=this,s=r.setContext(this.getContext()),n=r.display?s.width:0;if(!n)return;let a=i.setContext(this.getContext(0)).lineWidth,l=this._borderValue,c,d,p,u;this.isHorizontal()?(c=ci(t,this.left,n)-n/2,d=ci(t,this.right,a)+a/2,p=u=l):(p=ci(t,this.top,n)-n/2,u=ci(t,this.bottom,a)+a/2,c=d=l),o.save(),o.lineWidth=s.width,o.strokeStyle=s.color,o.beginPath(),o.moveTo(c,p),o.lineTo(d,u),o.stroke(),o.restore()}drawLabels(t){if(!this.options.ticks.display)return;let r=this.ctx,i=this._computeLabelArea();i&&Vc(r,i);let s=this.getLabelItems(t);for(let n of s){let a=n.options,l=n.font,c=n.label,d=n.textOffset;sa(r,c,0,d,l,a)}i&&Tc(r)}drawTitle(){let{ctx:t,options:{position:o,title:r,reverse:i}}=this;if(!r.display)return;let s=uo(r.font),n=ko(r.padding),a=r.align,l=s.lineHeight/2;o==="bottom"||o==="center"||Ve(o)?(l+=n.bottom,ct(r.text)&&(l+=s.lineHeight*(r.text.length-1))):l+=n.top;let{titleX:c,titleY:d,maxWidth:p,rotation:u}=g6(this,l,o,a);sa(t,r.text,0,0,s,{color:r.color,maxWidth:p,rotation:u,textAlign:f6(a,o,i),textBaseline:"middle",translation:[c,d]})}draw(t){this._isVisible()&&(this.drawBackground(),this.drawGrid(t),this.drawBorder(),this.drawTitle(),this.drawLabels(t))}_layers(){let t=this.options,o=t.ticks&&t.ticks.z||0,r=ze(t.grid&&t.grid.z,-1),i=ze(t.border&&t.border.z,0);return!this._isVisible()||this.draw!==e.prototype.draw?[{z:o,draw:s=>{this.draw(s)}}]:[{z:r,draw:s=>{this.drawBackground(),this.drawGrid(s),this.drawTitle()}},{z:i,draw:()=>{this.drawBorder()}},{z:o,draw:s=>{this.drawLabels(s)}}]}getMatchingVisibleMetas(t){let o=this.chart.getSortedVisibleDatasetMetas(),r=this.axis+"AxisID",i=[],s,n;for(s=0,n=o.length;s<n;++s){let a=o[s];a[r]===this.id&&(!t||a.type===t)&&i.push(a)}return i}_resolveTickFontOptions(t){let o=this.options.ticks.setContext(this.getContext(t));return uo(o.font)}_maxDigits(){let t=this._resolveTickFontOptions(0).lineHeight;return(this.isHorizontal()?this.width:this.height)/t}},Js=class{constructor(t,o,r){this.type=t,this.scope=o,this.override=r,this.items=Object.create(null)}isForType(t){return Object.prototype.isPrototypeOf.call(this.type.prototype,t.prototype)}register(t){let o=Object.getPrototypeOf(t),r;b6(o)&&(r=this.register(o));let i=this.items,s=t.id,n=this.scope+"."+s;if(!s)throw new Error("class does not have id: "+t);return s in i||(i[s]=t,m6(t,n,r),this.override&&gt.override(t.id,t.overrides)),n}get(t){return this.items[t]}unregister(t){let o=this.items,r=t.id,i=this.scope;r in o&&delete o[r],i&&r in gt[i]&&(delete gt[i][r],this.override&&delete li[r])}};function m6(e,t,o){let r=Us(Object.create(null),[o?gt.get(o):{},gt.get(t),e.defaults]);gt.set(t,r),e.defaultRoutes&&v6(t,e.defaultRoutes),e.descriptors&&gt.describe(t,e.descriptors)}function v6(e,t){Object.keys(t).forEach(o=>{let r=o.split("."),i=r.pop(),s=[e].concat(r).join("."),n=t[o].split("."),a=n.pop(),l=n.join(".");gt.route(s,i,l,a)})}function b6(e){return"id"in e&&"defaults"in e}var np=class{constructor(){this.controllers=new Js(Xc,"datasets",!0),this.elements=new Js(hi,"elements"),this.plugins=new Js(Object,"plugins"),this.scales=new Js(es,"scales"),this._typedRegistries=[this.controllers,this.scales,this.elements]}add(...t){this._each("register",t)}remove(...t){this._each("unregister",t)}addControllers(...t){this._each("register",t,this.controllers)}addElements(...t){this._each("register",t,this.elements)}addPlugins(...t){this._each("register",t,this.plugins)}addScales(...t){this._each("register",t,this.scales)}getController(t){return this._get(t,this.controllers,"controller")}getElement(t){return this._get(t,this.elements,"element")}getPlugin(t){return this._get(t,this.plugins,"plugin")}getScale(t){return this._get(t,this.scales,"scale")}removeControllers(...t){this._each("unregister",t,this.controllers)}removeElements(...t){this._each("unregister",t,this.elements)}removePlugins(...t){this._each("unregister",t,this.plugins)}removeScales(...t){this._each("unregister",t,this.scales)}_each(t,o,r){[...o].forEach(i=>{let s=r||this._getRegistryForType(i);r||s.isForType(i)||s===this.plugins&&i.id?this._exec(t,s,i):Fe(i,n=>{let a=r||this._getRegistryForType(n);this._exec(t,a,n)})})}_exec(t,o,r){let i=kc(t);pt(r["before"+i],[],r),o[t](r),pt(r["after"+i],[],r)}_getRegistryForType(t){for(let o=0;o<this._typedRegistries.length;o++){let r=this._typedRegistries[o];if(r.isForType(t))return r}return this.plugins}_get(t,o,r){let i=o.get(t);if(i===void 0)throw new Error('"'+t+'" is not a registered '+r+".");return i}},dr=new np,ap=class{constructor(){this._init=void 0}notify(t,o,r,i){if(o==="beforeInit"&&(this._init=this._createDescriptors(t,!0),this._notify(this._init,t,"install")),this._init===void 0)return;let s=i?this._descriptors(t).filter(i):this._descriptors(t),n=this._notify(s,t,o,r);return o==="afterDestroy"&&(this._notify(s,t,"stop"),this._notify(this._init,t,"uninstall"),this._init=void 0),n}_notify(t,o,r,i){i=i||{};for(let s of t){let n=s.plugin,a=n[r],l=[o,i,s.options];if(pt(a,l,n)===!1&&i.cancelable)return!1}return!0}invalidate(){Ze(this._cache)||(this._oldCache=this._cache,this._cache=void 0)}_descriptors(t){if(this._cache)return this._cache;let o=this._cache=this._createDescriptors(t);return this._notifyStateChanges(t),o}_createDescriptors(t,o){let r=t&&t.config,i=ze(r.options&&r.options.plugins,{}),s=w6(r);return i===!1&&!o?[]:C6(t,s,i,o)}_notifyStateChanges(t){let o=this._oldCache||[],r=this._cache,i=(s,n)=>s.filter(a=>!n.some(l=>a.plugin.id===l.plugin.id));this._notify(i(o,r),t,"stop"),this._notify(i(r,o),t,"start")}};function w6(e){let t={},o=[],r=Object.keys(dr.plugins.items);for(let s=0;s<r.length;s++)o.push(dr.getPlugin(r[s]));let i=e.plugins||[];for(let s=0;s<i.length;s++){let n=i[s];o.indexOf(n)===-1&&(o.push(n),t[n.id]=!0)}return{plugins:o,localIds:t}}function y6(e,t){return!t&&e===!1?null:e===!0?{}:e}function C6(e,{plugins:t,localIds:o},r,i){let s=[],n=e.getContext();for(let a of t){let l=a.id,c=y6(r[l],i);c!==null&&s.push({plugin:a,options:x6(e.config,{plugin:a,local:o[l]},c,n)})}return s}function x6(e,{plugin:t,local:o},r,i){let s=e.pluginScopeKeys(t),n=e.getOptionScopes(r,s);return o&&t.defaults&&n.push(t.defaults),e.createResolver(n,i,[""],{scriptable:!1,indexable:!1,allKeys:!0})}function lp(e,t){let o=gt.datasets[e]||{};return((t.datasets||{})[e]||{}).indexAxis||t.indexAxis||o.indexAxis||"x"}function _6(e,t){let o=e;return e==="_index_"?o=t:e==="_value_"&&(o=t==="x"?"y":"x"),o}function k6(e,t){return e===t?"_index_":"_value_"}function pg(e){if(e==="x"||e==="y"||e==="r")return e}function L6(e){if(e==="top"||e==="bottom")return"x";if(e==="left"||e==="right")return"y"}function cp(e,...t){if(pg(e))return e;for(let o of t){let r=o.axis||L6(o.position)||e.length>1&&pg(e[0].toLowerCase());if(r)return r}throw new Error(`Cannot determine type of '${e}' axis. Please provide 'axis' or 'position' option.`)}function ug(e,t,o){if(o[t+"AxisID"]===e)return{axis:t}}function S6(e,t){if(t.data&&t.data.datasets){let o=t.data.datasets.filter(r=>r.xAxisID===e||r.yAxisID===e);if(o.length)return ug(e,"x",o[0])||ug(e,"y",o[0])}return{}}function M6(e,t){let o=li[e.type]||{scales:{}},r=t.scales||{},i=lp(e.type,t),s=Object.create(null);return Object.keys(r).forEach(n=>{let a=r[n];if(!Ve(a))return console.error(`Invalid scale configuration for scale: ${n}`);if(a._proxy)return console.warn(`Ignoring resolver passed as options for scale: ${n}`);let l=cp(n,a,S6(n,e),gt.scales[a.type]),c=k6(l,i),d=o.scales||{};s[n]=Ys(Object.create(null),[{axis:l},a,d[l],d[c]])}),e.data.datasets.forEach(n=>{let a=n.type||e.type,l=n.indexAxis||lp(a,t),d=(li[a]||{}).scales||{};Object.keys(d).forEach(p=>{let u=_6(p,l),m=n[u+"AxisID"]||u;s[m]=s[m]||Object.create(null),Ys(s[m],[{axis:u},r[m],d[p]])})}),Object.keys(s).forEach(n=>{let a=s[n];Ys(a,[gt.scales[a.type],gt.scale])}),s}function Xg(e){let t=e.options||(e.options={});t.plugins=ze(t.plugins,{}),t.scales=M6(e,t)}function Kg(e){return e=e||{},e.datasets=e.datasets||[],e.labels=e.labels||[],e}function $6(e){return e=e||{},e.data=Kg(e.data),Xg(e),e}var fg=new Map,Qg=new Set;function jc(e,t){let o=fg.get(e);return o||(o=t(),fg.set(e,o),Qg.add(o)),o}var ha=(e,t,o)=>{let r=oa(t,o);r!==void 0&&e.add(r)},dp=class{constructor(t){this._config=$6(t),this._scopeCache=new Map,this._resolverCache=new Map}get platform(){return this._config.platform}get type(){return this._config.type}set type(t){this._config.type=t}get data(){return this._config.data}set data(t){this._config.data=Kg(t)}get options(){return this._config.options}set options(t){this._config.options=t}get plugins(){return this._config.plugins}update(){let t=this._config;this.clearCache(),Xg(t)}clearCache(){this._scopeCache.clear(),this._resolverCache.clear()}datasetScopeKeys(t){return jc(t,()=>[[`datasets.${t}`,""]])}datasetAnimationScopeKeys(t,o){return jc(`${t}.transition.${o}`,()=>[[`datasets.${t}.transitions.${o}`,`transitions.${o}`],[`datasets.${t}`,""]])}datasetElementScopeKeys(t,o){return jc(`${t}-${o}`,()=>[[`datasets.${t}.elements.${o}`,`datasets.${t}`,`elements.${o}`,""]])}pluginScopeKeys(t){let o=t.id,r=this.type;return jc(`${r}-plugin-${o}`,()=>[[`plugins.${o}`,...t.additionalOptionScopes||[]]])}_cachedScopes(t,o){let r=this._scopeCache,i=r.get(t);return(!i||o)&&(i=new Map,r.set(t,i)),i}getOptionScopes(t,o,r){let{options:i,type:s}=this,n=this._cachedScopes(t,r),a=n.get(o);if(a)return a;let l=new Set;o.forEach(d=>{t&&(l.add(t),d.forEach(p=>ha(l,t,p))),d.forEach(p=>ha(l,i,p)),d.forEach(p=>ha(l,li[s]||{},p)),d.forEach(p=>ha(l,gt,p)),d.forEach(p=>ha(l,Pc,p))});let c=Array.from(l);return c.length===0&&c.push(Object.create(null)),Qg.has(o)&&n.set(o,c),c}chartOptionScopes(){let{options:t,type:o}=this;return[t,li[o]||{},gt.datasets[o]||{},{type:o},gt,Pc]}resolveNamedOptions(t,o,r,i=[""]){let s={$shared:!0},{resolver:n,subPrefixes:a}=gg(this._resolverCache,t,i),l=n;if(P6(n,o)){s.$shared=!1,r=Ar(r)?r():r;let c=this.createResolver(t,r,a);l=Ki(n,r,c)}for(let c of o)s[c]=l[c];return s}createResolver(t,o,r=[""],i){let{resolver:s}=gg(this._resolverCache,t,r);return Ve(o)?Ki(s,o,void 0,i):s}};function gg(e,t,o){let r=e.get(t);r||(r=new Map,e.set(t,r));let i=o.join(),s=r.get(i);return s||(s={resolver:Rc(t,o),subPrefixes:o.filter(a=>!a.toLowerCase().includes("hover"))},r.set(i,s)),s}var A6=e=>Ve(e)&&Object.getOwnPropertyNames(e).some(t=>Ar(e[t]));function P6(e,t){let{isScriptable:o,isIndexable:r}=Bh(e);for(let i of t){let s=o(i),n=r(i),a=(n||s)&&e[i];if(s&&(Ar(a)||A6(a))||n&&ct(a))return!0}return!1}var O6="4.5.1",V6=["top","bottom","left","right","chartArea"];function mg(e,t){return e==="top"||e==="bottom"||V6.indexOf(e)===-1&&t==="x"}function vg(e,t){return function(o,r){return o[e]===r[e]?o[t]-r[t]:o[e]-r[e]}}function bg(e){let t=e.chart,o=t.options.animation;t.notifyPlugins("afterRender"),pt(o&&o.onComplete,[e],t)}function T6(e){let t=e.chart,o=t.options.animation;pt(o&&o.onProgress,[e],t)}function Jg(e){return zc()&&typeof e=="string"?e=document.getElementById(e):e&&e.length&&(e=e[0]),e&&e.canvas&&(e=e.canvas),e}var Yc={},wg=e=>{let t=Jg(e);return Object.values(Yc).filter(o=>o.canvas===t).pop()};function D6(e,t,o){let r=Object.keys(e);for(let i of r){let s=+i;if(s>=t){let n=e[i];delete e[i],(o>0||s>t)&&(e[s+o]=n)}}}function E6(e,t,o,r){return!o||e.type==="mouseout"?null:r?t:e}var en=class{static defaults=gt;static instances=Yc;static overrides=li;static registry=dr;static version=O6;static getChart=wg;static register(...t){dr.add(...t),yg()}static unregister(...t){dr.remove(...t),yg()}constructor(t,o){let r=this.config=new dp(o),i=Jg(t),s=wg(i);if(s)throw new Error("Canvas is already in use. Chart with ID '"+s.id+"' must be destroyed before the canvas with ID '"+s.canvas.id+"' can be reused.");let n=r.createResolver(r.chartOptionScopes(),this.getContext());this.platform=new(r.platform||o6(i)),this.platform.updateConfig(r);let a=this.platform.acquireContext(i,n.aspectRatio),l=a&&a.canvas,c=l&&l.height,d=l&&l.width;if(this.id=ff(),this.ctx=a,this.canvas=l,this.width=d,this.height=c,this._options=n,this._aspectRatio=this.aspectRatio,this._layers=[],this._metasets=[],this._stacks=void 0,this.boxes=[],this.currentDevicePixelRatio=void 0,this.chartArea=void 0,this._active=[],this._lastEvent=void 0,this._listeners={},this._responsiveListeners=void 0,this._sortedMetasets=[],this.scales={},this._plugins=new ap,this.$proxies={},this._hiddenIndices={},this.attached=!1,this._animationsDisabled=void 0,this.$context=void 0,this._doResize=Sf(p=>this.update(p),n.resizeDelay||0),this._dataChanges=[],Yc[this.id]=this,!a||!l){console.error("Failed to create chart: can't acquire context from the given item");return}Tr.listen(this,"complete",bg),Tr.listen(this,"progress",T6),this._initialize(),this.attached&&this.update()}get aspectRatio(){let{options:{aspectRatio:t,maintainAspectRatio:o},width:r,height:i,_aspectRatio:s}=this;return Ze(t)?o&&s?s:i?r/i:null:t}get data(){return this.config.data}set data(t){this.config.data=t}get options(){return this._options}set options(t){this.config.options=t}get registry(){return dr}_initialize(){return this.notifyPlugins("beforeInit"),this.options.responsive?this.resize():Fh(this,this.options.devicePixelRatio),this.bindEvents(),this.notifyPlugins("afterInit"),this}clear(){return Hh(this.canvas,this.ctx),this}stop(){return Tr.stop(this),this}resize(t,o){Tr.running(this)?this._resizeBeforeDraw={width:t,height:o}:this._resize(t,o)}_resize(t,o){let r=this.options,i=this.canvas,s=r.maintainAspectRatio&&this.aspectRatio,n=this.platform.getMaximumSize(i,t,o,s),a=r.devicePixelRatio||this.platform.getDevicePixelRatio(),l=this.width?"resize":"attach";this.width=n.width,this.height=n.height,this._aspectRatio=this.aspectRatio,Fh(this,a,!0)&&(this.notifyPlugins("resize",{size:n}),pt(r.onResize,[this,n],this),this.attached&&this._doResize(l)&&this.render())}ensureScalesHaveIDs(){let o=this.options.scales||{};Fe(o,(r,i)=>{r.id=i})}buildOrUpdateScales(){let t=this.options,o=t.scales,r=this.scales,i=Object.keys(r).reduce((n,a)=>(n[a]=!1,n),{}),s=[];o&&(s=s.concat(Object.keys(o).map(n=>{let a=o[n],l=cp(n,a),c=l==="r",d=l==="x";return{options:a,dposition:c?"chartArea":d?"bottom":"left",dtype:c?"radialLinear":d?"category":"linear"}}))),Fe(s,n=>{let a=n.options,l=a.id,c=cp(l,a),d=ze(a.type,n.dtype);(a.position===void 0||mg(a.position,c)!==mg(n.dposition))&&(a.position=n.dposition),i[l]=!0;let p=null;if(l in r&&r[l].type===d)p=r[l];else{let u=dr.getScale(d);p=new u({id:l,type:d,ctx:this.ctx,chart:this}),r[p.id]=p}p.init(a,t)}),Fe(i,(n,a)=>{n||delete r[a]}),Fe(r,n=>{Fc.configure(this,n,n.options),Fc.addBox(this,n)})}_updateMetasets(){let t=this._metasets,o=this.data.datasets.length,r=t.length;if(t.sort((i,s)=>i.index-s.index),r>o){for(let i=o;i<r;++i)this._destroyDatasetMeta(i);t.splice(o,r-o)}this._sortedMetasets=t.slice(0).sort(vg("order","index"))}_removeUnreferencedMetasets(){let{_metasets:t,data:{datasets:o}}=this;t.length>o.length&&delete this._stacks,t.forEach((r,i)=>{o.filter(s=>s===r._dataset).length===0&&this._destroyDatasetMeta(i)})}buildOrUpdateControllers(){let t=[],o=this.data.datasets,r,i;for(this._removeUnreferencedMetasets(),r=0,i=o.length;r<i;r++){let s=o[r],n=this.getDatasetMeta(r),a=s.type||this.config.type;if(n.type&&n.type!==a&&(this._destroyDatasetMeta(r),n=this.getDatasetMeta(r)),n.type=a,n.indexAxis=s.indexAxis||lp(a,this.options),n.order=s.order||0,n.index=r,n.label=""+s.label,n.visible=this.isDatasetVisible(r),n.controller)n.controller.updateIndex(r),n.controller.linkScales();else{let l=dr.getController(a),{datasetElementType:c,dataElementType:d}=gt.datasets[a];Object.assign(l,{dataElementType:dr.getElement(d),datasetElementType:c&&dr.getElement(c)}),n.controller=new l(this,r),t.push(n.controller)}}return this._updateMetasets(),t}_resetElements(){Fe(this.data.datasets,(t,o)=>{this.getDatasetMeta(o).controller.reset()},this)}reset(){this._resetElements(),this.notifyPlugins("reset")}update(t){let o=this.config;o.update();let r=this._options=o.createResolver(o.chartOptionScopes(),this.getContext()),i=this._animationsDisabled=!r.animation;if(this._updateScales(),this._checkEventBindings(),this._updateHiddenIndices(),this._plugins.invalidate(),this.notifyPlugins("beforeUpdate",{mode:t,cancelable:!0})===!1)return;let s=this.buildOrUpdateControllers();this.notifyPlugins("beforeElementsUpdate");let n=0;for(let c=0,d=this.data.datasets.length;c<d;c++){let{controller:p}=this.getDatasetMeta(c),u=!i&&s.indexOf(p)===-1;p.buildOrUpdateElements(u),n=Math.max(+p.getMaxOverflow(),n)}n=this._minPadding=r.layout.autoPadding?n:0,this._updateLayout(n),i||Fe(s,c=>{c.reset()}),this._updateDatasets(t),this.notifyPlugins("afterUpdate",{mode:t}),this._layers.sort(vg("z","_idx"));let{_active:a,_lastEvent:l}=this;l?this._eventHandler(l,!0):a.length&&this._updateHoverStyles(a,a,!0),this.render()}_updateScales(){Fe(this.scales,t=>{Fc.removeBox(this,t)}),this.ensureScalesHaveIDs(),this.buildOrUpdateScales()}_checkEventBindings(){let t=this.options,o=new Set(Object.keys(this._listeners)),r=new Set(t.events);(!Mh(o,r)||!!this._responsiveListeners!==t.responsive)&&(this.unbindEvents(),this.bindEvents())}_updateHiddenIndices(){let{_hiddenIndices:t}=this,o=this._getUniformDataChanges()||[];for(let{method:r,start:i,count:s}of o){let n=r==="_removeElements"?-s:s;D6(t,i,n)}}_getUniformDataChanges(){let t=this._dataChanges;if(!t||!t.length)return;this._dataChanges=[];let o=this.data.datasets.length,r=s=>new Set(t.filter(n=>n[0]===s).map((n,a)=>a+","+n.splice(1).join(","))),i=r(0);for(let s=1;s<o;s++)if(!Mh(i,r(s)))return;return Array.from(i).map(s=>s.split(",")).map(s=>({method:s[1],start:+s[2],count:+s[3]}))}_updateLayout(t){if(this.notifyPlugins("beforeLayout",{cancelable:!0})===!1)return;Fc.update(this,this.width,this.height,t);let o=this.chartArea,r=o.width<=0||o.height<=0;this._layers=[],Fe(this.boxes,i=>{r&&i.position==="chartArea"||(i.configure&&i.configure(),this._layers.push(...i._layers()))},this),this._layers.forEach((i,s)=>{i._idx=s}),this.notifyPlugins("afterLayout")}_updateDatasets(t){if(this.notifyPlugins("beforeDatasetsUpdate",{mode:t,cancelable:!0})!==!1){for(let o=0,r=this.data.datasets.length;o<r;++o)this.getDatasetMeta(o).controller.configure();for(let o=0,r=this.data.datasets.length;o<r;++o)this._updateDataset(o,Ar(t)?t({datasetIndex:o}):t);this.notifyPlugins("afterDatasetsUpdate",{mode:t})}}_updateDataset(t,o){let r=this.getDatasetMeta(t),i={meta:r,index:t,mode:o,cancelable:!0};this.notifyPlugins("beforeDatasetUpdate",i)!==!1&&(r.controller._update(o),i.cancelable=!1,this.notifyPlugins("afterDatasetUpdate",i))}render(){this.notifyPlugins("beforeRender",{cancelable:!0})!==!1&&(Tr.has(this)?this.attached&&!Tr.running(this)&&Tr.start(this):(this.draw(),bg({chart:this})))}draw(){let t;if(this._resizeBeforeDraw){let{width:r,height:i}=this._resizeBeforeDraw;this._resizeBeforeDraw=null,this._resize(r,i)}if(this.clear(),this.width<=0||this.height<=0||this.notifyPlugins("beforeDraw",{cancelable:!0})===!1)return;let o=this._layers;for(t=0;t<o.length&&o[t].z<=0;++t)o[t].draw(this.chartArea);for(this._drawDatasets();t<o.length;++t)o[t].draw(this.chartArea);this.notifyPlugins("afterDraw")}_getSortedDatasetMetas(t){let o=this._sortedMetasets,r=[],i,s;for(i=0,s=o.length;i<s;++i){let n=o[i];(!t||n.visible)&&r.push(n)}return r}getSortedVisibleDatasetMetas(){return this._getSortedDatasetMetas(!0)}_drawDatasets(){if(this.notifyPlugins("beforeDatasetsDraw",{cancelable:!0})===!1)return;let t=this.getSortedVisibleDatasetMetas();for(let o=t.length-1;o>=0;--o)this._drawDataset(t[o]);this.notifyPlugins("afterDatasetsDraw")}_drawDataset(t){let o=this.ctx,r={meta:t,index:t.index,cancelable:!0},i=Uh(this,t);this.notifyPlugins("beforeDatasetDraw",r)!==!1&&(i&&Vc(o,i),t.controller.draw(),i&&Tc(o),r.cancelable=!1,this.notifyPlugins("afterDatasetDraw",r))}isPointInArea(t){return ar(t,this.chartArea,this._minPadding)}getElementsAtEventForMode(t,o,r,i){let s=z7.modes[o];return typeof s=="function"?s(this,t,r,i):[]}getDatasetMeta(t){let o=this.data.datasets[t],r=this._metasets,i=r.filter(s=>s&&s._dataset===o).pop();return i||(i={type:null,data:[],dataset:null,controller:null,hidden:null,xAxisID:null,yAxisID:null,order:o&&o.order||0,index:t,_dataset:o,_parsed:[],_sorted:!1},r.push(i)),i}getContext(){return this.$context||(this.$context=Vr(null,{chart:this,type:"chart"}))}getVisibleDatasetCount(){return this.getSortedVisibleDatasetMetas().length}isDatasetVisible(t){let o=this.data.datasets[t];if(!o)return!1;let r=this.getDatasetMeta(t);return typeof r.hidden=="boolean"?!r.hidden:!o.hidden}setDatasetVisibility(t,o){let r=this.getDatasetMeta(t);r.hidden=!o}toggleDataVisibility(t){this._hiddenIndices[t]=!this._hiddenIndices[t]}getDataVisibility(t){return!this._hiddenIndices[t]}_updateVisibility(t,o,r){let i=r?"show":"hide",s=this.getDatasetMeta(t),n=s.controller._resolveAnimations(void 0,i);ra(o)?(s.data[o].hidden=!r,this.update()):(this.setDatasetVisibility(t,r),n.update(s,{visible:r}),this.update(a=>a.datasetIndex===t?i:void 0))}hide(t,o){this._updateVisibility(t,o,!1)}show(t,o){this._updateVisibility(t,o,!0)}_destroyDatasetMeta(t){let o=this._metasets[t];o&&o.controller&&o.controller._destroy(),delete this._metasets[t]}_stop(){let t,o;for(this.stop(),Tr.remove(this),t=0,o=this.data.datasets.length;t<o;++t)this._destroyDatasetMeta(t)}destroy(){this.notifyPlugins("beforeDestroy");let{canvas:t,ctx:o}=this;this._stop(),this.config.clearCache(),t&&(this.unbindEvents(),Hh(t,o),this.platform.releaseContext(o),this.canvas=null,this.ctx=null),delete Yc[this.id],this.notifyPlugins("afterDestroy")}toBase64Image(...t){return this.canvas.toDataURL(...t)}bindEvents(){this.bindUserEvents(),this.options.responsive?this.bindResponsiveEvents():this.attached=!0}bindUserEvents(){let t=this._listeners,o=this.platform,r=(s,n)=>{o.addEventListener(this,s,n),t[s]=n},i=(s,n,a)=>{s.offsetX=n,s.offsetY=a,this._eventHandler(s)};Fe(this.options.events,s=>r(s,i))}bindResponsiveEvents(){this._responsiveListeners||(this._responsiveListeners={});let t=this._responsiveListeners,o=this.platform,r=(l,c)=>{o.addEventListener(this,l,c),t[l]=c},i=(l,c)=>{t[l]&&(o.removeEventListener(this,l,c),delete t[l])},s=(l,c)=>{this.canvas&&this.resize(l,c)},n,a=()=>{i("attach",a),this.attached=!0,this.resize(),r("resize",s),r("detach",n)};n=()=>{this.attached=!1,i("resize",s),this._stop(),this._resize(0,0),r("attach",a)},o.isAttached(this.canvas)?a():n()}unbindEvents(){Fe(this._listeners,(t,o)=>{this.platform.removeEventListener(this,o,t)}),this._listeners={},Fe(this._responsiveListeners,(t,o)=>{this.platform.removeEventListener(this,o,t)}),this._responsiveListeners=void 0}updateHoverStyle(t,o,r){let i=r?"set":"remove",s,n,a,l;for(o==="dataset"&&(s=this.getDatasetMeta(t[0].datasetIndex),s.controller["_"+i+"DatasetHoverStyle"]()),a=0,l=t.length;a<l;++a){n=t[a];let c=n&&this.getDatasetMeta(n.datasetIndex).controller;c&&c[i+"HoverStyle"](n.element,n.datasetIndex,n.index)}}getActiveElements(){return this._active||[]}setActiveElements(t){let o=this._active||[],r=t.map(({datasetIndex:s,index:n})=>{let a=this.getDatasetMeta(s);if(!a)throw new Error("No dataset found at index "+s);return{datasetIndex:s,element:a.data[n],index:n}});!ta(r,o)&&(this._active=r,this._lastEvent=null,this._updateHoverStyles(r,o))}notifyPlugins(t,o,r){return this._plugins.notify(this,t,o,r)}isPluginEnabled(t){return this._plugins._cache.filter(o=>o.plugin.id===t).length===1}_updateHoverStyles(t,o,r){let i=this.options.hover,s=(l,c)=>l.filter(d=>!c.some(p=>d.datasetIndex===p.datasetIndex&&d.index===p.index)),n=s(o,t),a=r?t:s(t,o);n.length&&this.updateHoverStyle(n,i.mode,!1),a.length&&i.mode&&this.updateHoverStyle(a,i.mode,!0)}_eventHandler(t,o){let r={event:t,replay:o,cancelable:!0,inChartArea:this.isPointInArea(t)},i=n=>(n.options.events||this.options.events).includes(t.native.type);if(this.notifyPlugins("beforeEvent",r,i)===!1)return;let s=this._handleEvent(t,o,r.inChartArea);return r.cancelable=!1,this.notifyPlugins("afterEvent",r,i),(s||r.changed)&&this.render(),this}_handleEvent(t,o,r){let{_active:i=[],options:s}=this,n=o,a=this._getActiveElements(t,i,r,n),l=vf(t),c=E6(t,this._lastEvent,r,l);r&&(this._lastEvent=null,pt(s.onHover,[t,a,this],this),l&&pt(s.onClick,[t,a,this],this));let d=!ta(a,i);return(d||o)&&(this._active=a,this._updateHoverStyles(a,i,o)),this._lastEvent=c,d}_getActiveElements(t,o,r,i){if(t.type==="mouseout")return[];if(!r)return o;let s=this.options.hover;return this.getElementsAtEventForMode(t,s.mode,s,i)}};function yg(){return Fe(en.instances,e=>e._plugins.invalidate())}function R6(e,t,o){let{startAngle:r,x:i,y:s,outerRadius:n,innerRadius:a,options:l}=t,{borderWidth:c,borderJoinStyle:d}=l,p=Math.min(c/n,Ft(r-o));if(e.beginPath(),e.arc(i,s,n-c/2,r+p/2,o-p/2),a>0){let u=Math.min(c/a,Ft(r-o));e.arc(i,s,a+c/2,o-u/2,r+u/2,!0)}else{let u=Math.min(c/2,n*Ft(r-o));if(d==="round")e.arc(i,s,u,o-Ue/2,r+Ue/2,!0);else if(d==="bevel"){let m=2*u*u,b=-m*Math.cos(o+Ue/2)+i,C=-m*Math.sin(o+Ue/2)+s,y=m*Math.cos(r+Ue/2)+i,k=m*Math.sin(r+Ue/2)+s;e.lineTo(b,C),e.lineTo(y,k)}}e.closePath(),e.moveTo(0,0),e.rect(0,0,e.canvas.width,e.canvas.height),e.clip("evenodd")}function z6(e,t,o){let{startAngle:r,pixelMargin:i,x:s,y:n,outerRadius:a,innerRadius:l}=t,c=i/a;e.beginPath(),e.arc(s,n,a,r-c,o+c),l>i?(c=i/l,e.arc(s,n,l,o+c,r-c,!0)):e.arc(s,n,i,o+Ct,r-Ct),e.closePath(),e.clip()}function H6(e){return Ec(e,["outerStart","outerEnd","innerStart","innerEnd"])}function B6(e,t,o,r){let i=H6(e.options.borderRadius),s=(o-t)/2,n=Math.min(s,r*t/2),a=l=>{let c=(o-Math.min(s,l))*r/2;return Yt(l,0,Math.min(s,c))};return{outerStart:a(i.outerStart),outerEnd:a(i.outerEnd),innerStart:Yt(i.innerStart,0,n),innerEnd:Yt(i.innerEnd,0,n)}}function Qs(e,t,o,r){return{x:o+e*Math.cos(t),y:r+e*Math.sin(t)}}function e1(e,t,o,r,i,s){let{x:n,y:a,startAngle:l,pixelMargin:c,innerRadius:d}=t,p=Math.max(t.outerRadius+r+o-c,0),u=d>0?d+r+o+c:0,m=0,b=i-l;if(r){let W=d>0?d-r:0,j=p>0?p-r:0,F=(W+j)/2,me=F!==0?b*F/(F+r):b;m=(b-me)/2}let C=Math.max(.001,b*p-o/Ue)/p,y=(b-C)/2,k=l+y+m,$=i-y-m,{outerStart:V,outerEnd:O,innerStart:P,innerEnd:T}=B6(t,u,p,$-k),Z=p-V,R=p-O,D=k+V/Z,N=$-O/R,B=u+P,Y=u+T,I=k+P/B,H=$-T/Y;if(e.beginPath(),s){let W=(D+N)/2;if(e.arc(n,a,p,D,W),e.arc(n,a,p,W,N),O>0){let ae=Qs(R,N,n,a);e.arc(ae.x,ae.y,O,N,$+Ct)}let j=Qs(Y,$,n,a);if(e.lineTo(j.x,j.y),T>0){let ae=Qs(Y,H,n,a);e.arc(ae.x,ae.y,T,$+Ct,H+Math.PI)}let F=($-T/u+(k+P/u))/2;if(e.arc(n,a,u,$-T/u,F,!0),e.arc(n,a,u,F,k+P/u,!0),P>0){let ae=Qs(B,I,n,a);e.arc(ae.x,ae.y,P,I+Math.PI,k-Ct)}let me=Qs(Z,k,n,a);if(e.lineTo(me.x,me.y),V>0){let ae=Qs(Z,D,n,a);e.arc(ae.x,ae.y,V,k-Ct,D)}}else{e.moveTo(n,a);let W=Math.cos(D)*p+n,j=Math.sin(D)*p+a;e.lineTo(W,j);let F=Math.cos(N)*p+n,me=Math.sin(N)*p+a;e.lineTo(F,me)}e.closePath()}function I6(e,t,o,r,i){let{fullCircles:s,startAngle:n,circumference:a}=t,l=t.endAngle;if(s){e1(e,t,o,r,l,i);for(let c=0;c<s;++c)e.fill();isNaN(a)||(l=n+(a%vt||vt))}return e1(e,t,o,r,l,i),e.fill(),l}function Z6(e,t,o,r,i){let{fullCircles:s,startAngle:n,circumference:a,options:l}=t,{borderWidth:c,borderJoinStyle:d,borderDash:p,borderDashOffset:u,borderRadius:m}=l,b=l.borderAlign==="inner";if(!c)return;e.setLineDash(p||[]),e.lineDashOffset=u,b?(e.lineWidth=c*2,e.lineJoin=d||"round"):(e.lineWidth=c,e.lineJoin=d||"bevel");let C=t.endAngle;if(s){e1(e,t,o,r,C,i);for(let y=0;y<s;++y)e.stroke();isNaN(a)||(C=n+(a%vt||vt))}b&&z6(e,t,C),l.selfJoin&&C-n>=Ue&&m===0&&d!=="miter"&&R6(e,t,C),s||(e1(e,t,o,r,C,i),e.stroke())}var t1=class extends hi{static id="arc";static defaults={borderAlign:"center",borderColor:"#fff",borderDash:[],borderDashOffset:0,borderJoinStyle:void 0,borderRadius:0,borderWidth:2,offset:0,spacing:0,angle:void 0,circular:!0,selfJoin:!1};static defaultRoutes={backgroundColor:"backgroundColor"};static descriptors={_scriptable:!0,_indexable:t=>t!=="borderDash"};circumference;endAngle;fullCircles;innerRadius;outerRadius;pixelMargin;startAngle;constructor(t){super(),this.options=void 0,this.circumference=void 0,this.startAngle=void 0,this.endAngle=void 0,this.innerRadius=void 0,this.outerRadius=void 0,this.pixelMargin=0,this.fullCircles=0,t&&Object.assign(this,t)}inRange(t,o,r){let i=this.getProps(["x","y"],r),{angle:s,distance:n}=Oh(i,{x:t,y:o}),{startAngle:a,endAngle:l,innerRadius:c,outerRadius:d,circumference:p}=this.getProps(["startAngle","endAngle","innerRadius","outerRadius","circumference"],r),u=(this.options.spacing+this.options.borderWidth)/2,m=ze(p,l-a),b=Sc(s,a,l)&&a!==l,C=m>=vt||b,y=Mc(n,c+u,d+u);return C&&y}getCenterPoint(t){let{x:o,y:r,startAngle:i,endAngle:s,innerRadius:n,outerRadius:a}=this.getProps(["x","y","startAngle","endAngle","innerRadius","outerRadius"],t),{offset:l,spacing:c}=this.options,d=(i+s)/2,p=(n+a+c+l)/2;return{x:o+Math.cos(d)*p,y:r+Math.sin(d)*p}}tooltipPosition(t){return this.getCenterPoint(t)}draw(t){let{options:o,circumference:r}=this,i=(o.offset||0)/4,s=(o.spacing||0)/2,n=o.circular;if(this.pixelMargin=o.borderAlign==="inner"?.33:0,this.fullCircles=r>vt?Math.floor(r/vt):0,r===0||this.innerRadius<0||this.outerRadius<0)return;t.save();let a=(this.startAngle+this.endAngle)/2;t.translate(Math.cos(a)*i,Math.sin(a)*i);let l=1-Math.sin(Math.min(Ue,r||0)),c=i*l;t.fillStyle=o.backgroundColor,t.strokeStyle=o.borderColor,I6(t,this,c,s,n),Z6(t,this,c,s,n),t.restore()}};function em(e,t,o=t){e.lineCap=ze(o.borderCapStyle,t.borderCapStyle),e.setLineDash(ze(o.borderDash,t.borderDash)),e.lineDashOffset=ze(o.borderDashOffset,t.borderDashOffset),e.lineJoin=ze(o.borderJoinStyle,t.borderJoinStyle),e.lineWidth=ze(o.borderWidth,t.borderWidth),e.strokeStyle=ze(o.borderColor,t.borderColor)}function F6(e,t,o){e.lineTo(o.x,o.y)}function N6(e){return e.stepped?Tf:e.tension||e.cubicInterpolationMode==="monotone"?Df:F6}function tm(e,t,o={}){let r=e.length,{start:i=0,end:s=r-1}=o,{start:n,end:a}=t,l=Math.max(i,n),c=Math.min(s,a),d=i<n&&s<n||i>a&&s>a;return{count:r,start:l,loop:t.loop,ilen:c<l&&!d?r+c-l:c-l}}function j6(e,t,o,r){let{points:i,options:s}=t,{count:n,start:a,loop:l,ilen:c}=tm(i,o,r),d=N6(s),{move:p=!0,reverse:u}=r||{},m,b,C;for(m=0;m<=c;++m)b=i[(a+(u?c-m:m))%n],!b.skip&&(p?(e.moveTo(b.x,b.y),p=!1):d(e,C,b,u,s.stepped),C=b);return l&&(b=i[(a+(u?c:0))%n],d(e,C,b,u,s.stepped)),!!l}function W6(e,t,o,r){let i=t.points,{count:s,start:n,ilen:a}=tm(i,o,r),{move:l=!0,reverse:c}=r||{},d=0,p=0,u,m,b,C,y,k,$=O=>(n+(c?a-O:O))%s,V=()=>{C!==y&&(e.lineTo(d,y),e.lineTo(d,C),e.lineTo(d,k))};for(l&&(m=i[$(0)],e.moveTo(m.x,m.y)),u=0;u<=a;++u){if(m=i[$(u)],m.skip)continue;let O=m.x,P=m.y,T=O|0;T===b?(P<C?C=P:P>y&&(y=P),d=(p*d+O)/++p):(V(),e.lineTo(O,P),b=T,p=0,C=y=P),k=P}V()}function hp(e){let t=e.options,o=t.borderDash&&t.borderDash.length;return!e._decimated&&!e._loop&&!t.tension&&t.cubicInterpolationMode!=="monotone"&&!t.stepped&&!o?W6:j6}function U6(e){return e.stepped?jf:e.tension||e.cubicInterpolationMode==="monotone"?Wf:si}function G6(e,t,o,r){let i=t._path;i||(i=t._path=new Path2D,t.path(i,o,r)&&i.closePath()),em(e,t.options),e.stroke(i)}function Y6(e,t,o,r){let{segments:i,options:s}=t,n=hp(t);for(let a of i)em(e,s,a.style),e.beginPath(),n(e,t,a,{start:o,end:o+r-1})&&e.closePath(),e.stroke()}var q6=typeof Path2D=="function";function X6(e,t,o,r){q6&&!t.options.segment?G6(e,t,o,r):Y6(e,t,o,r)}var ts=class extends hi{static id="line";static defaults={borderCapStyle:"butt",borderDash:[],borderDashOffset:0,borderJoinStyle:"miter",borderWidth:3,capBezierPoints:!0,cubicInterpolationMode:"default",fill:!1,spanGaps:!1,stepped:!1,tension:0};static defaultRoutes={backgroundColor:"backgroundColor",borderColor:"borderColor"};static descriptors={_scriptable:!0,_indexable:t=>t!=="borderDash"&&t!=="fill"};constructor(t){super(),this.animated=!0,this.options=void 0,this._chart=void 0,this._loop=void 0,this._fullLoop=void 0,this._path=void 0,this._points=void 0,this._segments=void 0,this._decimated=!1,this._pointsUpdated=!1,this._datasetIndex=void 0,t&&Object.assign(this,t)}updateControlPoints(t,o){let r=this.options;if((r.tension||r.cubicInterpolationMode==="monotone")&&!r.stepped&&!this._pointsUpdated){let i=r.spanGaps?this._loop:this._fullLoop;Zf(this._points,r,t,i,o),this._pointsUpdated=!0}}set points(t){this._points=t,delete this._segments,delete this._path,this._pointsUpdated=!1}get points(){return this._points}get segments(){return this._segments||(this._segments=qf(this,this.options.segment))}first(){let t=this.segments,o=this.points;return t.length&&o[t[0].start]}last(){let t=this.segments,o=this.points,r=t.length;return r&&o[t[r-1].end]}interpolate(t,o){let r=this.options,i=t[o],s=this.points,n=Wh(this,{property:o,start:i,end:i});if(!n.length)return;let a=[],l=U6(r),c,d;for(c=0,d=n.length;c<d;++c){let{start:p,end:u}=n[c],m=s[p],b=s[u];if(m===b){a.push(m);continue}let C=Math.abs((i-m[o])/(b[o]-m[o])),y=l(m,b,C,r.stepped);y[o]=t[o],a.push(y)}return a.length===1?a[0]:a}pathSegment(t,o,r){return hp(this)(t,this,o,r)}path(t,o,r){let i=this.segments,s=hp(this),n=this._loop;o=o||0,r=r||this.points.length-o;for(let a of i)n&=s(t,this,a,{start:o,end:o+r-1});return!!n}draw(t,o,r,i){let s=this.options||{};(this.points||[]).length&&s.borderWidth&&(t.save(),X6(t,this,r,i),t.restore()),this.animated&&(this._pointsUpdated=!1,this._path=void 0)}};function Cg(e,t,o,r){let i=e.options,{[o]:s}=e.getProps([o],r);return Math.abs(t-s)<i.radius+i.hitRadius}var o1=class extends hi{static id="point";parsed;skip;stop;static defaults={borderWidth:1,hitRadius:1,hoverBorderWidth:1,hoverRadius:4,pointStyle:"circle",radius:3,rotation:0};static defaultRoutes={backgroundColor:"backgroundColor",borderColor:"borderColor"};constructor(t){super(),this.options=void 0,this.parsed=void 0,this.skip=void 0,this.stop=void 0,t&&Object.assign(this,t)}inRange(t,o,r){let i=this.options,{x:s,y:n}=this.getProps(["x","y"],r);return Math.pow(t-s,2)+Math.pow(o-n,2)<Math.pow(i.hitRadius+i.radius,2)}inXRange(t,o){return Cg(this,t,"x",o)}inYRange(t,o){return Cg(this,t,"y",o)}getCenterPoint(t){let{x:o,y:r}=this.getProps(["x","y"],t);return{x:o,y:r}}size(t){t=t||this.options||{};let o=t.radius||0;o=Math.max(o,o&&t.hoverRadius||0);let r=o&&t.borderWidth||0;return(o+r)*2}draw(t,o){let r=this.options;this.skip||r.radius<.1||!ar(this,o,this.size(r)/2)||(t.strokeStyle=r.borderColor,t.lineWidth=r.borderWidth,t.fillStyle=r.backgroundColor,Oc(t,r,this.x,this.y))}getRange(){let t=this.options||{};return t.radius+t.hitRadius}};function K6(e,t,o){let r=e.segments,i=e.points,s=t.points,n=[];for(let a of r){let{start:l,end:c}=a;c=a1(l,c,i);let d=pp(o,i[l],i[c],a.loop);if(!t.segments){n.push({source:a,target:d,start:i[l],end:i[c]});continue}let p=Wh(t,d);for(let u of p){let m=pp(o,s[u.start],s[u.end],u.loop),b=jh(a,i,m);for(let C of b)n.push({source:C,target:u,start:{[o]:xg(d,m,"start",Math.max)},end:{[o]:xg(d,m,"end",Math.min)}})}}return n}function pp(e,t,o,r){if(r)return;let i=t[e],s=o[e];return e==="angle"&&(i=Ft(i),s=Ft(s)),{property:e,start:i,end:s}}function Q6(e,t){let{x:o=null,y:r=null}=e||{},i=t.points,s=[];return t.segments.forEach(({start:n,end:a})=>{a=a1(n,a,i);let l=i[n],c=i[a];r!==null?(s.push({x:l.x,y:r}),s.push({x:c.x,y:r})):o!==null&&(s.push({x:o,y:l.y}),s.push({x:o,y:c.y}))}),s}function a1(e,t,o){for(;t>e;t--){let r=o[t];if(!isNaN(r.x)&&!isNaN(r.y))break}return t}function xg(e,t,o,r){return e&&t?r(e[o],t[o]):e?e[o]:t?t[o]:0}function om(e,t){let o=[],r=!1;return ct(e)?(r=!0,o=e):o=Q6(e,t),o.length?new ts({points:o,options:{tension:0},_loop:r,_fullLoop:r}):null}function _g(e){return e&&e.fill!==!1}function J6(e,t,o){let i=e[t].fill,s=[t],n;if(!o)return i;for(;i!==!1&&s.indexOf(i)===-1;){if(!ht(i))return i;if(n=e[i],!n)return!1;if(n.visible)return i;s.push(i),i=n.fill}return!1}function ew(e,t,o){let r=iw(e);if(Ve(r))return isNaN(r.value)?!1:r;let i=parseFloat(r);return ht(i)&&Math.floor(i)===i?tw(r[0],t,i,o):["origin","start","end","stack","shape"].indexOf(r)>=0&&r}function tw(e,t,o,r){return(e==="-"||e==="+")&&(o=t+o),o===t||o<0||o>=r?!1:o}function ow(e,t){let o=null;return e==="start"?o=t.bottom:e==="end"?o=t.top:Ve(e)?o=t.getPixelForValue(e.value):t.getBasePixel&&(o=t.getBasePixel()),o}function rw(e,t,o){let r;return e==="start"?r=o:e==="end"?r=t.options.reverse?t.min:t.max:Ve(e)?r=e.value:r=t.getBaseValue(),r}function iw(e){let t=e.options,o=t.fill,r=ze(o&&o.target,o);return r===void 0&&(r=!!t.backgroundColor),r===!1||r===null?!1:r===!0?"origin":r}function sw(e){let{scale:t,index:o,line:r}=e,i=[],s=r.segments,n=r.points,a=nw(t,o);a.push(om({x:null,y:t.bottom},r));for(let l=0;l<s.length;l++){let c=s[l];for(let d=c.start;d<=c.end;d++)aw(i,n[d],a)}return new ts({points:i,options:{}})}function nw(e,t){let o=[],r=e.getMatchingVisibleMetas("line");for(let i=0;i<r.length;i++){let s=r[i];if(s.index===t)break;s.hidden||o.unshift(s.dataset)}return o}function aw(e,t,o){let r=[];for(let i=0;i<o.length;i++){let s=o[i],{first:n,last:a,point:l}=lw(s,t,"x");if(!(!l||n&&a)){if(n)r.unshift(l);else if(e.push(l),!a)break}}e.push(...r)}function lw(e,t,o){let r=e.interpolate(t,o);if(!r)return{};let i=r[o],s=e.segments,n=e.points,a=!1,l=!1;for(let c=0;c<s.length;c++){let d=s[c],p=n[d.start][o],u=n[d.end][o];if(Mc(i,p,u)){a=i===p,l=i===u;break}}return{first:a,last:l,point:r}}var r1=class{constructor(t){this.x=t.x,this.y=t.y,this.radius=t.radius}pathSegment(t,o,r){let{x:i,y:s,radius:n}=this;return o=o||{start:0,end:vt},t.arc(i,s,n,o.end,o.start,!0),!r.bounds}interpolate(t){let{x:o,y:r,radius:i}=this,s=t.angle;return{x:o+Math.cos(s)*i,y:r+Math.sin(s)*i,angle:s}}};function cw(e){let{chart:t,fill:o,line:r}=e;if(ht(o))return dw(t,o);if(o==="stack")return sw(e);if(o==="shape")return!0;let i=hw(e);return i instanceof r1?i:om(i,r)}function dw(e,t){let o=e.getDatasetMeta(t);return o&&e.isDatasetVisible(t)?o.dataset:null}function hw(e){return(e.scale||{}).getPointPositionForValue?uw(e):pw(e)}function pw(e){let{scale:t={},fill:o}=e,r=ow(o,t);if(ht(r)){let i=t.isHorizontal();return{x:i?r:null,y:i?null:r}}return null}function uw(e){let{scale:t,fill:o}=e,r=t.options,i=t.getLabels().length,s=r.reverse?t.max:t.min,n=rw(o,t,s),a=[];if(r.grid.circular){let l=t.getPointPositionForValue(0,s);return new r1({x:l.x,y:l.y,radius:t.getDistanceFromCenterForValue(n)})}for(let l=0;l<i;++l)a.push(t.getPointPositionForValue(l,n));return a}function Jh(e,t,o){let r=cw(t),{chart:i,index:s,line:n,scale:a,axis:l}=t,c=n.options,d=c.fill,p=c.backgroundColor,{above:u=p,below:m=p}=d||{},b=i.getDatasetMeta(s),C=Uh(i,b);r&&n.points.length&&(Vc(e,o),fw(e,{line:n,target:r,above:u,below:m,area:o,scale:a,axis:l,clip:C}),Tc(e))}function fw(e,t){let{line:o,target:r,above:i,below:s,area:n,scale:a,clip:l}=t,c=o._loop?"angle":t.axis;e.save();let d=s;s!==i&&(c==="x"?(kg(e,r,n.top),ep(e,{line:o,target:r,color:i,scale:a,property:c,clip:l}),e.restore(),e.save(),kg(e,r,n.bottom)):c==="y"&&(Lg(e,r,n.left),ep(e,{line:o,target:r,color:s,scale:a,property:c,clip:l}),e.restore(),e.save(),Lg(e,r,n.right),d=i)),ep(e,{line:o,target:r,color:d,scale:a,property:c,clip:l}),e.restore()}function kg(e,t,o){let{segments:r,points:i}=t,s=!0,n=!1;e.beginPath();for(let a of r){let{start:l,end:c}=a,d=i[l],p=i[a1(l,c,i)];s?(e.moveTo(d.x,d.y),s=!1):(e.lineTo(d.x,o),e.lineTo(d.x,d.y)),n=!!t.pathSegment(e,a,{move:n}),n?e.closePath():e.lineTo(p.x,o)}e.lineTo(t.first().x,o),e.closePath(),e.clip()}function Lg(e,t,o){let{segments:r,points:i}=t,s=!0,n=!1;e.beginPath();for(let a of r){let{start:l,end:c}=a,d=i[l],p=i[a1(l,c,i)];s?(e.moveTo(d.x,d.y),s=!1):(e.lineTo(o,d.y),e.lineTo(d.x,d.y)),n=!!t.pathSegment(e,a,{move:n}),n?e.closePath():e.lineTo(o,p.y)}e.lineTo(o,t.first().y),e.closePath(),e.clip()}function ep(e,t){let{line:o,target:r,property:i,color:s,scale:n,clip:a}=t,l=K6(o,r,i);for(let{source:c,target:d,start:p,end:u}of l){let{style:{backgroundColor:m=s}={}}=c,b=r!==!0;e.save(),e.fillStyle=m,gw(e,n,a,b&&pp(i,p,u)),e.beginPath();let C=!!o.pathSegment(e,c),y;if(b){C?e.closePath():Sg(e,r,u,i);let k=!!r.pathSegment(e,d,{move:C,reverse:!0});y=C&&k,y||Sg(e,r,p,i)}e.closePath(),e.fill(y?"evenodd":"nonzero"),e.restore()}}function gw(e,t,o,r){let i=t.chart.chartArea,{property:s,start:n,end:a}=r||{};if(s==="x"||s==="y"){let l,c,d,p;s==="x"?(l=n,c=i.top,d=a,p=i.bottom):(l=i.left,c=n,d=i.right,p=a),e.beginPath(),o&&(l=Math.max(l,o.left),d=Math.min(d,o.right),c=Math.max(c,o.top),p=Math.min(p,o.bottom)),e.rect(l,c,d-l,p-c),e.clip()}}function Sg(e,t,o,r){let i=t.interpolate(o,r);i&&e.lineTo(i.x,i.y)}var rm={id:"filler",afterDatasetsUpdate(e,t,o){let r=(e.data.datasets||[]).length,i=[],s,n,a,l;for(n=0;n<r;++n)s=e.getDatasetMeta(n),a=s.dataset,l=null,a&&a.options&&a instanceof ts&&(l={visible:e.isDatasetVisible(n),index:n,fill:ew(a,n,r),chart:e,axis:s.controller.options.indexAxis,scale:s.vScale,line:a}),s.$filler=l,i.push(l);for(n=0;n<r;++n)l=i[n],!(!l||l.fill===!1)&&(l.fill=J6(i,n,o.propagate))},beforeDraw(e,t,o){let r=o.drawTime==="beforeDraw",i=e.getSortedVisibleDatasetMetas(),s=e.chartArea;for(let n=i.length-1;n>=0;--n){let a=i[n].$filler;a&&(a.line.updateControlPoints(s,a.axis),r&&a.fill&&Jh(e.ctx,a,s))}},beforeDatasetsDraw(e,t,o){if(o.drawTime!=="beforeDatasetsDraw")return;let r=e.getSortedVisibleDatasetMetas();for(let i=r.length-1;i>=0;--i){let s=r[i].$filler;_g(s)&&Jh(e.ctx,s,e.chartArea)}},beforeDatasetDraw(e,t,o){let r=t.meta.$filler;!_g(r)||o.drawTime!=="beforeDatasetDraw"||Jh(e.ctx,r,e.chartArea)},defaults:{propagate:!0,drawTime:"beforeDatasetDraw"}};var ua={average(e){if(!e.length)return!1;let t,o,r=new Set,i=0,s=0;for(t=0,o=e.length;t<o;++t){let a=e[t].element;if(a&&a.hasValue()){let l=a.tooltipPosition();r.add(l.x),i+=l.y,++s}}return s===0||r.size===0?!1:{x:[...r].reduce((a,l)=>a+l)/r.size,y:i/s}},nearest(e,t){if(!e.length)return!1;let o=t.x,r=t.y,i=Number.POSITIVE_INFINITY,s,n,a;for(s=0,n=e.length;s<n;++s){let l=e[s].element;if(l&&l.hasValue()){let c=l.getCenterPoint(),d=xc(t,c);d<i&&(i=d,a=l)}}if(a){let l=a.tooltipPosition();o=l.x,r=l.y}return{x:o,y:r}}};function cr(e,t){return t&&(ct(t)?Array.prototype.push.apply(e,t):e.push(t)),e}function Dr(e){return(typeof e=="string"||e instanceof String)&&e.indexOf(`
`)>-1?e.split(`
`):e}function mw(e,t){let{element:o,datasetIndex:r,index:i}=t,s=e.getDatasetMeta(r).controller,{label:n,value:a}=s.getLabelAndValue(i);return{chart:e,label:n,parsed:s.getParsed(i),raw:e.data.datasets[r].data[i],formattedValue:a,dataset:s.getDataset(),dataIndex:i,datasetIndex:r,element:o}}function Mg(e,t){let o=e.chart.ctx,{body:r,footer:i,title:s}=e,{boxWidth:n,boxHeight:a}=t,l=uo(t.bodyFont),c=uo(t.titleFont),d=uo(t.footerFont),p=s.length,u=i.length,m=r.length,b=ko(t.padding),C=b.height,y=0,k=r.reduce((O,P)=>O+P.before.length+P.lines.length+P.after.length,0);if(k+=e.beforeBody.length+e.afterBody.length,p&&(C+=p*c.lineHeight+(p-1)*t.titleSpacing+t.titleMarginBottom),k){let O=t.displayColors?Math.max(a,l.lineHeight):l.lineHeight;C+=m*O+(k-m)*l.lineHeight+(k-1)*t.bodySpacing}u&&(C+=t.footerMarginTop+u*d.lineHeight+(u-1)*t.footerSpacing);let $=0,V=function(O){y=Math.max(y,o.measureText(O).width+$)};return o.save(),o.font=c.string,Fe(e.title,V),o.font=l.string,Fe(e.beforeBody.concat(e.afterBody),V),$=t.displayColors?n+2+t.boxPadding:0,Fe(r,O=>{Fe(O.before,V),Fe(O.lines,V),Fe(O.after,V)}),$=0,o.font=d.string,Fe(e.footer,V),o.restore(),y+=b.width,{width:y,height:C}}function vw(e,t){let{y:o,height:r}=t;return o<r/2?"top":o>e.height-r/2?"bottom":"center"}function bw(e,t,o,r){let{x:i,width:s}=r,n=o.caretSize+o.caretPadding;if(e==="left"&&i+s+n>t.width||e==="right"&&i-s-n<0)return!0}function ww(e,t,o,r){let{x:i,width:s}=o,{width:n,chartArea:{left:a,right:l}}=e,c="center";return r==="center"?c=i<=(a+l)/2?"left":"right":i<=s/2?c="left":i>=n-s/2&&(c="right"),bw(c,e,t,o)&&(c="center"),c}function $g(e,t,o){let r=o.yAlign||t.yAlign||vw(e,o);return{xAlign:o.xAlign||t.xAlign||ww(e,t,o,r),yAlign:r}}function yw(e,t){let{x:o,width:r}=e;return t==="right"?o-=r:t==="center"&&(o-=r/2),o}function Cw(e,t,o){let{y:r,height:i}=e;return t==="top"?r+=o:t==="bottom"?r-=i+o:r-=i/2,r}function Ag(e,t,o,r){let{caretSize:i,caretPadding:s,cornerRadius:n}=e,{xAlign:a,yAlign:l}=o,c=i+s,{topLeft:d,topRight:p,bottomLeft:u,bottomRight:m}=Ks(n),b=yw(t,a),C=Cw(t,l,c);return l==="center"?a==="left"?b+=c:a==="right"&&(b-=c):a==="left"?b-=Math.max(d,u)+i:a==="right"&&(b+=Math.max(p,m)+i),{x:Yt(b,0,r.width-t.width),y:Yt(C,0,r.height-t.height)}}function Wc(e,t,o){let r=ko(o.padding);return t==="center"?e.x+e.width/2:t==="right"?e.x+e.width-r.right:e.x+r.left}function Pg(e){return cr([],Dr(e))}function xw(e,t,o){return Vr(e,{tooltip:t,tooltipItems:o,type:"tooltip"})}function Og(e,t){let o=t&&t.dataset&&t.dataset.tooltip&&t.dataset.tooltip.callbacks;return o?e.override(o):e}var im={beforeTitle:lr,title(e){if(e.length>0){let t=e[0],o=t.chart.data.labels,r=o?o.length:0;if(this&&this.options&&this.options.mode==="dataset")return t.dataset.label||"";if(t.label)return t.label;if(r>0&&t.dataIndex<r)return o[t.dataIndex]}return""},afterTitle:lr,beforeBody:lr,beforeLabel:lr,label(e){if(this&&this.options&&this.options.mode==="dataset")return e.label+": "+e.formattedValue||e.formattedValue;let t=e.dataset.label||"";t&&(t+=": ");let o=e.formattedValue;return Ze(o)||(t+=o),t},labelColor(e){let o=e.chart.getDatasetMeta(e.datasetIndex).controller.getStyle(e.dataIndex);return{borderColor:o.borderColor,backgroundColor:o.backgroundColor,borderWidth:o.borderWidth,borderDash:o.borderDash,borderDashOffset:o.borderDashOffset,borderRadius:0}},labelTextColor(){return this.options.bodyColor},labelPointStyle(e){let o=e.chart.getDatasetMeta(e.datasetIndex).controller.getStyle(e.dataIndex);return{pointStyle:o.pointStyle,rotation:o.rotation}},afterLabel:lr,afterBody:lr,beforeFooter:lr,footer:lr,afterFooter:lr};function fo(e,t,o,r){let i=e[t].call(o,r);return typeof i>"u"?im[t].call(o,r):i}var i1=class extends hi{static positioners=ua;constructor(t){super(),this.opacity=0,this._active=[],this._eventPosition=void 0,this._size=void 0,this._cachedAnimations=void 0,this._tooltipItems=[],this.$animations=void 0,this.$context=void 0,this.chart=t.chart,this.options=t.options,this.dataPoints=void 0,this.title=void 0,this.beforeBody=void 0,this.body=void 0,this.afterBody=void 0,this.footer=void 0,this.xAlign=void 0,this.yAlign=void 0,this.x=void 0,this.y=void 0,this.height=void 0,this.width=void 0,this.caretX=void 0,this.caretY=void 0,this.labelColors=void 0,this.labelPointStyles=void 0,this.labelTextColors=void 0}initialize(t){this.options=t,this._cachedAnimations=void 0,this.$context=void 0}_resolveAnimations(){let t=this._cachedAnimations;if(t)return t;let o=this.chart,r=this.options.setContext(this.getContext()),i=r.enabled&&o.options.animation&&r.animations,s=new qc(this.chart,i);return i._cacheable&&(this._cachedAnimations=Object.freeze(s)),s}getContext(){return this.$context||(this.$context=xw(this.chart.getContext(),this,this._tooltipItems))}getTitle(t,o){let{callbacks:r}=o,i=fo(r,"beforeTitle",this,t),s=fo(r,"title",this,t),n=fo(r,"afterTitle",this,t),a=[];return a=cr(a,Dr(i)),a=cr(a,Dr(s)),a=cr(a,Dr(n)),a}getBeforeBody(t,o){return Pg(fo(o.callbacks,"beforeBody",this,t))}getBody(t,o){let{callbacks:r}=o,i=[];return Fe(t,s=>{let n={before:[],lines:[],after:[]},a=Og(r,s);cr(n.before,Dr(fo(a,"beforeLabel",this,s))),cr(n.lines,fo(a,"label",this,s)),cr(n.after,Dr(fo(a,"afterLabel",this,s))),i.push(n)}),i}getAfterBody(t,o){return Pg(fo(o.callbacks,"afterBody",this,t))}getFooter(t,o){let{callbacks:r}=o,i=fo(r,"beforeFooter",this,t),s=fo(r,"footer",this,t),n=fo(r,"afterFooter",this,t),a=[];return a=cr(a,Dr(i)),a=cr(a,Dr(s)),a=cr(a,Dr(n)),a}_createItems(t){let o=this._active,r=this.chart.data,i=[],s=[],n=[],a=[],l,c;for(l=0,c=o.length;l<c;++l)a.push(mw(this.chart,o[l]));return t.filter&&(a=a.filter((d,p,u)=>t.filter(d,p,u,r))),t.itemSort&&(a=a.sort((d,p)=>t.itemSort(d,p,r))),Fe(a,d=>{let p=Og(t.callbacks,d);i.push(fo(p,"labelColor",this,d)),s.push(fo(p,"labelPointStyle",this,d)),n.push(fo(p,"labelTextColor",this,d))}),this.labelColors=i,this.labelPointStyles=s,this.labelTextColors=n,this.dataPoints=a,a}update(t,o){let r=this.options.setContext(this.getContext()),i=this._active,s,n=[];if(!i.length)this.opacity!==0&&(s={opacity:0});else{let a=ua[r.position].call(this,i,this._eventPosition);n=this._createItems(r),this.title=this.getTitle(n,r),this.beforeBody=this.getBeforeBody(n,r),this.body=this.getBody(n,r),this.afterBody=this.getAfterBody(n,r),this.footer=this.getFooter(n,r);let l=this._size=Mg(this,r),c=Object.assign({},a,l),d=$g(this.chart,r,c),p=Ag(r,c,d,this.chart);this.xAlign=d.xAlign,this.yAlign=d.yAlign,s={opacity:1,x:p.x,y:p.y,width:l.width,height:l.height,caretX:a.x,caretY:a.y}}this._tooltipItems=n,this.$context=void 0,s&&this._resolveAnimations().update(this,s),t&&r.external&&r.external.call(this,{chart:this.chart,tooltip:this,replay:o})}drawCaret(t,o,r,i){let s=this.getCaretPosition(t,r,i);o.lineTo(s.x1,s.y1),o.lineTo(s.x2,s.y2),o.lineTo(s.x3,s.y3)}getCaretPosition(t,o,r){let{xAlign:i,yAlign:s}=this,{caretSize:n,cornerRadius:a}=r,{topLeft:l,topRight:c,bottomLeft:d,bottomRight:p}=Ks(a),{x:u,y:m}=t,{width:b,height:C}=o,y,k,$,V,O,P;return s==="center"?(O=m+C/2,i==="left"?(y=u,k=y-n,V=O+n,P=O-n):(y=u+b,k=y+n,V=O-n,P=O+n),$=y):(i==="left"?k=u+Math.max(l,d)+n:i==="right"?k=u+b-Math.max(c,p)-n:k=this.caretX,s==="top"?(V=m,O=V-n,y=k-n,$=k+n):(V=m+C,O=V+n,y=k+n,$=k-n),P=V),{x1:y,x2:k,x3:$,y1:V,y2:O,y3:P}}drawTitle(t,o,r){let i=this.title,s=i.length,n,a,l;if(s){let c=Ic(r.rtl,this.x,this.width);for(t.x=Wc(this,r.titleAlign,r),o.textAlign=c.textAlign(r.titleAlign),o.textBaseline="middle",n=uo(r.titleFont),a=r.titleSpacing,o.fillStyle=r.titleColor,o.font=n.string,l=0;l<s;++l)o.fillText(i[l],c.x(t.x),t.y+n.lineHeight/2),t.y+=n.lineHeight+a,l+1===s&&(t.y+=r.titleMarginBottom-a)}}_drawColorBox(t,o,r,i,s){let n=this.labelColors[r],a=this.labelPointStyles[r],{boxHeight:l,boxWidth:c}=s,d=uo(s.bodyFont),p=Wc(this,"left",s),u=i.x(p),m=l<d.lineHeight?(d.lineHeight-l)/2:0,b=o.y+m;if(s.usePointStyle){let C={radius:Math.min(c,l)/2,pointStyle:a.pointStyle,rotation:a.rotation,borderWidth:1},y=i.leftForLtr(u,c)+c/2,k=b+l/2;t.strokeStyle=s.multiKeyBackground,t.fillStyle=s.multiKeyBackground,Oc(t,C,y,k),t.strokeStyle=n.borderColor,t.fillStyle=n.backgroundColor,Oc(t,C,y,k)}else{t.lineWidth=Ve(n.borderWidth)?Math.max(...Object.values(n.borderWidth)):n.borderWidth||1,t.strokeStyle=n.borderColor,t.setLineDash(n.borderDash||[]),t.lineDashOffset=n.borderDashOffset||0;let C=i.leftForLtr(u,c),y=i.leftForLtr(i.xPlus(u,1),c-2),k=Ks(n.borderRadius);Object.values(k).some($=>$!==0)?(t.beginPath(),t.fillStyle=s.multiKeyBackground,Dc(t,{x:C,y:b,w:c,h:l,radius:k}),t.fill(),t.stroke(),t.fillStyle=n.backgroundColor,t.beginPath(),Dc(t,{x:y,y:b+1,w:c-2,h:l-2,radius:k}),t.fill()):(t.fillStyle=s.multiKeyBackground,t.fillRect(C,b,c,l),t.strokeRect(C,b,c,l),t.fillStyle=n.backgroundColor,t.fillRect(y,b+1,c-2,l-2))}t.fillStyle=this.labelTextColors[r]}drawBody(t,o,r){let{body:i}=this,{bodySpacing:s,bodyAlign:n,displayColors:a,boxHeight:l,boxWidth:c,boxPadding:d}=r,p=uo(r.bodyFont),u=p.lineHeight,m=0,b=Ic(r.rtl,this.x,this.width),C=function(R){o.fillText(R,b.x(t.x+m),t.y+u/2),t.y+=u+s},y=b.textAlign(n),k,$,V,O,P,T,Z;for(o.textAlign=n,o.textBaseline="middle",o.font=p.string,t.x=Wc(this,y,r),o.fillStyle=r.bodyColor,Fe(this.beforeBody,C),m=a&&y!=="right"?n==="center"?c/2+d:c+2+d:0,O=0,T=i.length;O<T;++O){for(k=i[O],$=this.labelTextColors[O],o.fillStyle=$,Fe(k.before,C),V=k.lines,a&&V.length&&(this._drawColorBox(o,t,O,b,r),u=Math.max(p.lineHeight,l)),P=0,Z=V.length;P<Z;++P)C(V[P]),u=p.lineHeight;Fe(k.after,C)}m=0,u=p.lineHeight,Fe(this.afterBody,C),t.y-=s}drawFooter(t,o,r){let i=this.footer,s=i.length,n,a;if(s){let l=Ic(r.rtl,this.x,this.width);for(t.x=Wc(this,r.footerAlign,r),t.y+=r.footerMarginTop,o.textAlign=l.textAlign(r.footerAlign),o.textBaseline="middle",n=uo(r.footerFont),o.fillStyle=r.footerColor,o.font=n.string,a=0;a<s;++a)o.fillText(i[a],l.x(t.x),t.y+n.lineHeight/2),t.y+=n.lineHeight+r.footerSpacing}}drawBackground(t,o,r,i){let{xAlign:s,yAlign:n}=this,{x:a,y:l}=t,{width:c,height:d}=r,{topLeft:p,topRight:u,bottomLeft:m,bottomRight:b}=Ks(i.cornerRadius);o.fillStyle=i.backgroundColor,o.strokeStyle=i.borderColor,o.lineWidth=i.borderWidth,o.beginPath(),o.moveTo(a+p,l),n==="top"&&this.drawCaret(t,o,r,i),o.lineTo(a+c-u,l),o.quadraticCurveTo(a+c,l,a+c,l+u),n==="center"&&s==="right"&&this.drawCaret(t,o,r,i),o.lineTo(a+c,l+d-b),o.quadraticCurveTo(a+c,l+d,a+c-b,l+d),n==="bottom"&&this.drawCaret(t,o,r,i),o.lineTo(a+m,l+d),o.quadraticCurveTo(a,l+d,a,l+d-m),n==="center"&&s==="left"&&this.drawCaret(t,o,r,i),o.lineTo(a,l+p),o.quadraticCurveTo(a,l,a+p,l),o.closePath(),o.fill(),i.borderWidth>0&&o.stroke()}_updateAnimationTarget(t){let o=this.chart,r=this.$animations,i=r&&r.x,s=r&&r.y;if(i||s){let n=ua[t.position].call(this,this._active,this._eventPosition);if(!n)return;let a=this._size=Mg(this,t),l=Object.assign({},n,this._size),c=$g(o,t,l),d=Ag(t,l,c,o);(i._to!==d.x||s._to!==d.y)&&(this.xAlign=c.xAlign,this.yAlign=c.yAlign,this.width=a.width,this.height=a.height,this.caretX=n.x,this.caretY=n.y,this._resolveAnimations().update(this,d))}}_willRender(){return!!this.opacity}draw(t){let o=this.options.setContext(this.getContext()),r=this.opacity;if(!r)return;this._updateAnimationTarget(o);let i={width:this.width,height:this.height},s={x:this.x,y:this.y};r=Math.abs(r)<.001?0:r;let n=ko(o.padding),a=this.title.length||this.beforeBody.length||this.body.length||this.afterBody.length||this.footer.length;o.enabled&&a&&(t.save(),t.globalAlpha=r,this.drawBackground(s,t,i,o),Uf(t,o.textDirection),s.y+=n.top,this.drawTitle(s,t,o),this.drawBody(s,t,o),this.drawFooter(s,t,o),Gf(t,o.textDirection),t.restore())}getActiveElements(){return this._active||[]}setActiveElements(t,o){let r=this._active,i=t.map(({datasetIndex:a,index:l})=>{let c=this.chart.getDatasetMeta(a);if(!c)throw new Error("Cannot find a dataset at index "+a);return{datasetIndex:a,element:c.data[l],index:l}}),s=!ta(r,i),n=this._positionChanged(i,o);(s||n)&&(this._active=i,this._eventPosition=o,this._ignoreReplayEvents=!0,this.update(!0))}handleEvent(t,o,r=!0){if(o&&this._ignoreReplayEvents)return!1;this._ignoreReplayEvents=!1;let i=this.options,s=this._active||[],n=this._getActiveElements(t,s,o,r),a=this._positionChanged(n,t),l=o||!ta(n,s)||a;return l&&(this._active=n,(i.enabled||i.external)&&(this._eventPosition={x:t.x,y:t.y},this.update(!0,o))),l}_getActiveElements(t,o,r,i){let s=this.options;if(t.type==="mouseout")return[];if(!i)return o.filter(a=>this.chart.data.datasets[a.datasetIndex]&&this.chart.getDatasetMeta(a.datasetIndex).controller.getParsed(a.index)!==void 0);let n=this.chart.getElementsAtEventForMode(t,s.mode,s,r);return s.reverse&&n.reverse(),n}_positionChanged(t,o){let{caretX:r,caretY:i,options:s}=this,n=ua[s.position].call(this,t,o);return n!==!1&&(r!==n.x||i!==n.y)}},sm={id:"tooltip",_element:i1,positioners:ua,afterInit(e,t,o){o&&(e.tooltip=new i1({chart:e,options:o}))},beforeUpdate(e,t,o){e.tooltip&&e.tooltip.initialize(o)},reset(e,t,o){e.tooltip&&e.tooltip.initialize(o)},afterDraw(e){let t=e.tooltip;if(t&&t._willRender()){let o={tooltip:t};if(e.notifyPlugins("beforeTooltipDraw",{...o,cancelable:!0})===!1)return;t.draw(e.ctx),e.notifyPlugins("afterTooltipDraw",o)}},afterEvent(e,t){if(e.tooltip){let o=t.replay;e.tooltip.handleEvent(t.event,o,t.inChartArea)&&(t.changed=!0)}},defaults:{enabled:!0,external:null,position:"average",backgroundColor:"rgba(0,0,0,0.8)",titleColor:"#fff",titleFont:{weight:"bold"},titleSpacing:2,titleMarginBottom:6,titleAlign:"left",bodyColor:"#fff",bodySpacing:2,bodyFont:{},bodyAlign:"left",footerColor:"#fff",footerSpacing:2,footerMarginTop:6,footerFont:{weight:"bold"},footerAlign:"left",padding:6,caretPadding:2,caretSize:5,cornerRadius:6,boxHeight:(e,t)=>t.bodyFont.size,boxWidth:(e,t)=>t.bodyFont.size,multiKeyBackground:"#fff",displayColors:!0,boxPadding:0,borderColor:"rgba(0,0,0,0)",borderWidth:0,animation:{duration:400,easing:"easeOutQuart"},animations:{numbers:{type:"number",properties:["x","y","width","height","caretX","caretY"]},opacity:{easing:"linear",duration:200}},callbacks:im},defaultRoutes:{bodyFont:"font",footerFont:"font",titleFont:"font"},descriptors:{_scriptable:e=>e!=="filter"&&e!=="itemSort"&&e!=="external",_indexable:!1,callbacks:{_scriptable:!1,_indexable:!1},animation:{_fallback:!1},animations:{_fallback:"animation"}},additionalOptionScopes:["interaction"]};var _w=(e,t,o,r)=>(typeof t=="string"?(o=e.push(t)-1,r.unshift({index:o,label:t})):isNaN(t)&&(o=null),o);function kw(e,t,o,r){let i=e.indexOf(t);if(i===-1)return _w(e,t,o,r);let s=e.lastIndexOf(t);return i!==s?o:i}var Lw=(e,t)=>e===null?null:Yt(Math.round(e),0,t);function Vg(e){let t=this.getLabels();return e>=0&&e<t.length?t[e]:e}var s1=class extends es{static id="category";static defaults={ticks:{callback:Vg}};constructor(t){super(t),this._startValue=void 0,this._valueRange=0,this._addedLabels=[]}init(t){let o=this._addedLabels;if(o.length){let r=this.getLabels();for(let{index:i,label:s}of o)r[i]===s&&r.splice(i,1);this._addedLabels=[]}super.init(t)}parse(t,o){if(Ze(t))return null;let r=this.getLabels();return o=isFinite(o)&&r[o]===t?o:kw(r,t,ze(o,t),this._addedLabels),Lw(o,r.length-1)}determineDataLimits(){let{minDefined:t,maxDefined:o}=this.getUserBounds(),{min:r,max:i}=this.getMinMax(!0);this.options.bounds==="ticks"&&(t||(r=0),o||(i=this.getLabels().length-1)),this.min=r,this.max=i}buildTicks(){let t=this.min,o=this.max,r=this.options.offset,i=[],s=this.getLabels();s=t===0&&o===s.length-1?s:s.slice(t,o+1),this._valueRange=Math.max(s.length-(r?0:1),1),this._startValue=this.min-(r?.5:0);for(let n=t;n<=o;n++)i.push({value:n});return i}getLabelForValue(t){return Vg.call(this,t)}configure(){super.configure(),this.isHorizontal()||(this._reversePixels=!this._reversePixels)}getPixelForValue(t){return typeof t!="number"&&(t=this.parse(t)),t===null?NaN:this.getPixelForDecimal((t-this._startValue)/this._valueRange)}getPixelForTick(t){let o=this.ticks;return t<0||t>o.length-1?null:this.getPixelForValue(o[t].value)}getValueForPixel(t){return Math.round(this._startValue+this.getDecimalForPixel(t)*this._valueRange)}getBasePixel(){return this.bottom}};function Sw(e,t){let o=[],{bounds:i,step:s,min:n,max:a,precision:l,count:c,maxTicks:d,maxDigits:p,includeBounds:u}=e,m=s||1,b=d-1,{min:C,max:y}=t,k=!Ze(n),$=!Ze(a),V=!Ze(c),O=(y-C)/(p+1),P=$h((y-C)/b/m)*m,T,Z,R,D;if(P<1e-14&&!k&&!$)return[{value:C},{value:y}];D=Math.ceil(y/P)-Math.floor(C/P),D>b&&(P=$h(D*P/b/m)*m),Ze(l)||(T=Math.pow(10,l),P=Math.ceil(P*T)/T),i==="ticks"?(Z=Math.floor(C/P)*P,R=Math.ceil(y/P)*P):(Z=C,R=y),k&&$&&s&&wf((a-n)/s,P/1e3)?(D=Math.round(Math.min((a-n)/P,d)),P=(a-n)/D,Z=n,R=a):V?(Z=k?n:Z,R=$?a:R,D=c-1,P=(R-Z)/D):(D=(R-Z)/P,qs(D,Math.round(D),P/1e3)?D=Math.round(D):D=Math.ceil(D));let N=Math.max(Ph(P),Ph(Z));T=Math.pow(10,Ze(l)?N:l),Z=Math.round(Z*T)/T,R=Math.round(R*T)/T;let B=0;for(k&&(u&&Z!==n?(o.push({value:n}),Z<n&&B++,qs(Math.round((Z+B*P)*T)/T,n,Tg(n,O,e))&&B++):Z<n&&B++);B<D;++B){let Y=Math.round((Z+B*P)*T)/T;if($&&Y>a)break;o.push({value:Y})}return $&&u&&R!==a?o.length&&qs(o[o.length-1].value,a,Tg(a,O,e))?o[o.length-1].value=a:o.push({value:a}):(!$||R===a)&&o.push({value:R}),o}function Tg(e,t,{horizontal:o,minRotation:r}){let i=Or(r),s=(o?Math.sin(i):Math.cos(i))||.001,n=.75*t*(""+e).length;return Math.min(t/s,n)}var tn=class extends es{constructor(t){super(t),this.start=void 0,this.end=void 0,this._startValue=void 0,this._endValue=void 0,this._valueRange=0}parse(t,o){return Ze(t)||(typeof t=="number"||t instanceof Number)&&!isFinite(+t)?null:+t}handleTickRangeOptions(){let{beginAtZero:t}=this.options,{minDefined:o,maxDefined:r}=this.getUserBounds(),{min:i,max:s}=this,n=l=>i=o?i:l,a=l=>s=r?s:l;if(t){let l=Xi(i),c=Xi(s);l<0&&c<0?a(0):l>0&&c>0&&n(0)}if(i===s){let l=s===0?1:Math.abs(s*.05);a(s+l),t||n(i-l)}this.min=i,this.max=s}getTickLimit(){let t=this.options.ticks,{maxTicksLimit:o,stepSize:r}=t,i;return r?(i=Math.ceil(this.max/r)-Math.floor(this.min/r)+1,i>1e3&&(console.warn(`scales.${this.id}.ticks.stepSize: ${r} would result generating up to ${i} ticks. Limiting to 1000.`),i=1e3)):(i=this.computeTickLimit(),o=o||11),o&&(i=Math.min(o,i)),i}computeTickLimit(){return Number.POSITIVE_INFINITY}buildTicks(){let t=this.options,o=t.ticks,r=this.getTickLimit();r=Math.max(2,r);let i={maxTicks:r,bounds:t.bounds,min:t.min,max:t.max,precision:o.precision,step:o.stepSize,count:o.count,maxDigits:this._maxDigits(),horizontal:this.isHorizontal(),minRotation:o.minRotation||0,includeBounds:o.includeBounds!==!1},s=this._range||this,n=Sw(i,s);return t.bounds==="ticks"&&Ah(n,this,"value"),t.reverse?(n.reverse(),this.start=this.max,this.end=this.min):(this.start=this.min,this.end=this.max),n}configure(){let t=this.ticks,o=this.min,r=this.max;if(super.configure(),this.options.offset&&t.length){let i=(r-o)/Math.max(t.length-1,1)/2;o-=i,r+=i}this._startValue=o,this._endValue=r,this._valueRange=r-o}getLabelForValue(t){return Ac(t,this.chart.options.locale,this.options.ticks.format)}},n1=class extends tn{static id="linear";static defaults={ticks:{callback:ia.formatters.numeric}};determineDataLimits(){let{min:t,max:o}=this.getMinMax(!0);this.min=ht(t)?t:0,this.max=ht(o)?o:1,this.handleTickRangeOptions()}computeTickLimit(){let t=this.isHorizontal(),o=t?this.width:this.height,r=Or(this.options.ticks.minRotation),i=(t?Math.sin(r):Math.cos(r))||.001,s=this._resolveTickFontOptions(0);return Math.ceil(o/Math.min(40,s.lineHeight/i))}getPixelForValue(t){return t===null?NaN:this.getPixelForDecimal((t-this._startValue)/this._valueRange)}getValueForPixel(t){return this._startValue+this.getDecimalForPixel(t)*this._valueRange}},ga=e=>Math.floor(Pr(e)),Ji=(e,t)=>Math.pow(10,ga(e)+t);function Dg(e){return e/Math.pow(10,ga(e))===1}function Eg(e,t,o){let r=Math.pow(10,o),i=Math.floor(e/r);return Math.ceil(t/r)-i}function Mw(e,t){let o=t-e,r=ga(o);for(;Eg(e,t,r)>10;)r++;for(;Eg(e,t,r)<10;)r--;return Math.min(r,ga(e))}function $w(e,{min:t,max:o}){t=po(e.min,t);let r=[],i=ga(t),s=Mw(t,o),n=s<0?Math.pow(10,Math.abs(s)):1,a=Math.pow(10,s),l=i>s?Math.pow(10,i):0,c=Math.round((t-l)*n)/n,d=Math.floor((t-l)/a/10)*a*10,p=Math.floor((c-d)/Math.pow(10,s)),u=po(e.min,Math.round((l+d+p*Math.pow(10,s))*n)/n);for(;u<o;)r.push({value:u,major:Dg(u),significand:p}),p>=10?p=p<15?15:20:p++,p>=20&&(s++,p=2,n=s>=0?1:n),u=Math.round((l+d+p*Math.pow(10,s))*n)/n;let m=po(e.max,u);return r.push({value:m,major:Dg(m),significand:p}),r}var Rg=class extends es{static id="logarithmic";static defaults={ticks:{callback:ia.formatters.logarithmic,major:{enabled:!0}}};constructor(t){super(t),this.start=void 0,this.end=void 0,this._startValue=void 0,this._valueRange=0}parse(t,o){let r=tn.prototype.parse.apply(this,[t,o]);if(r===0){this._zero=!0;return}return ht(r)&&r>0?r:null}determineDataLimits(){let{min:t,max:o}=this.getMinMax(!0);this.min=ht(t)?Math.max(0,t):null,this.max=ht(o)?Math.max(0,o):null,this.options.beginAtZero&&(this._zero=!0),this._zero&&this.min!==this._suggestedMin&&!ht(this._userMin)&&(this.min=t===Ji(this.min,0)?Ji(this.min,-1):Ji(this.min,0)),this.handleTickRangeOptions()}handleTickRangeOptions(){let{minDefined:t,maxDefined:o}=this.getUserBounds(),r=this.min,i=this.max,s=a=>r=t?r:a,n=a=>i=o?i:a;r===i&&(r<=0?(s(1),n(10)):(s(Ji(r,-1)),n(Ji(i,1)))),r<=0&&s(Ji(i,-1)),i<=0&&n(Ji(r,1)),this.min=r,this.max=i}buildTicks(){let t=this.options,o={min:this._userMin,max:this._userMax},r=$w(o,this);return t.bounds==="ticks"&&Ah(r,this,"value"),t.reverse?(r.reverse(),this.start=this.max,this.end=this.min):(this.start=this.min,this.end=this.max),r}getLabelForValue(t){return t===void 0?"0":Ac(t,this.chart.options.locale,this.options.ticks.format)}configure(){let t=this.min;super.configure(),this._startValue=Pr(t),this._valueRange=Pr(this.max)-Pr(t)}getPixelForValue(t){return(t===void 0||t===0)&&(t=this.min),t===null||isNaN(t)?NaN:this.getPixelForDecimal(t===this.min?0:(Pr(t)-this._startValue)/this._valueRange)}getValueForPixel(t){let o=this.getDecimalForPixel(t);return Math.pow(10,this._startValue+o*this._valueRange)}};function up(e){let t=e.ticks;if(t.display&&e.display){let o=ko(t.backdropPadding);return ze(t.font&&t.font.size,gt.font.size)+o.height}return 0}function Aw(e,t,o){return o=ct(o)?o:[o],{w:Of(e,t.string,o),h:o.length*t.lineHeight}}function zg(e,t,o,r,i){return e===r||e===i?{start:t-o/2,end:t+o/2}:e<r||e>i?{start:t-o,end:t}:{start:t,end:t+o}}function Pw(e){let t={l:e.left+e._padding.left,r:e.right-e._padding.right,t:e.top+e._padding.top,b:e.bottom-e._padding.bottom},o=Object.assign({},t),r=[],i=[],s=e._pointLabels.length,n=e.options.pointLabels,a=n.centerPointLabels?Ue/s:0;for(let l=0;l<s;l++){let c=n.setContext(e.getPointLabelContext(l));i[l]=c.padding;let d=e.getPointPosition(l,e.drawingArea+i[l],a),p=uo(c.font),u=Aw(e.ctx,p,e._pointLabels[l]);r[l]=u;let m=Ft(e.getIndexAngle(l)+a),b=Math.round(Lc(m)),C=zg(b,d.x,u.w,0,180),y=zg(b,d.y,u.h,90,270);Ow(o,t,m,C,y)}e.setCenterPoint(t.l-o.l,o.r-t.r,t.t-o.t,o.b-t.b),e._pointLabelItems=Dw(e,r,i)}function Ow(e,t,o,r,i){let s=Math.abs(Math.sin(o)),n=Math.abs(Math.cos(o)),a=0,l=0;r.start<t.l?(a=(t.l-r.start)/s,e.l=Math.min(e.l,t.l-a)):r.end>t.r&&(a=(r.end-t.r)/s,e.r=Math.max(e.r,t.r+a)),i.start<t.t?(l=(t.t-i.start)/n,e.t=Math.min(e.t,t.t-l)):i.end>t.b&&(l=(i.end-t.b)/n,e.b=Math.max(e.b,t.b+l))}function Vw(e,t,o){let r=e.drawingArea,{extra:i,additionalAngle:s,padding:n,size:a}=o,l=e.getPointPosition(t,r+i+n,s),c=Math.round(Lc(Ft(l.angle+Ct))),d=zw(l.y,a.h,c),p=Ew(c),u=Rw(l.x,a.w,p);return{visible:!0,x:l.x,y:d,textAlign:p,left:u,top:d,right:u+a.w,bottom:d+a.h}}function Tw(e,t){if(!t)return!0;let{left:o,top:r,right:i,bottom:s}=e;return!(ar({x:o,y:r},t)||ar({x:o,y:s},t)||ar({x:i,y:r},t)||ar({x:i,y:s},t))}function Dw(e,t,o){let r=[],i=e._pointLabels.length,s=e.options,{centerPointLabels:n,display:a}=s.pointLabels,l={extra:up(s)/2,additionalAngle:n?Ue/i:0},c;for(let d=0;d<i;d++){l.padding=o[d],l.size=t[d];let p=Vw(e,d,l);r.push(p),a==="auto"&&(p.visible=Tw(p,c),p.visible&&(c=p))}return r}function Ew(e){return e===0||e===180?"center":e<180?"left":"right"}function Rw(e,t,o){return o==="right"?e-=t:o==="center"&&(e-=t/2),e}function zw(e,t,o){return o===90||o===270?e-=t/2:(o>270||o<90)&&(e-=t),e}function Hw(e,t,o){let{left:r,top:i,right:s,bottom:n}=o,{backdropColor:a}=t;if(!Ze(a)){let l=Ks(t.borderRadius),c=ko(t.backdropPadding);e.fillStyle=a;let d=r-c.left,p=i-c.top,u=s-r+c.width,m=n-i+c.height;Object.values(l).some(b=>b!==0)?(e.beginPath(),Dc(e,{x:d,y:p,w:u,h:m,radius:l}),e.fill()):e.fillRect(d,p,u,m)}}function Bw(e,t){let{ctx:o,options:{pointLabels:r}}=e;for(let i=t-1;i>=0;i--){let s=e._pointLabelItems[i];if(!s.visible)continue;let n=r.setContext(e.getPointLabelContext(i));Hw(o,n,s);let a=uo(n.font),{x:l,y:c,textAlign:d}=s;sa(o,e._pointLabels[i],l,c+a.lineHeight/2,a,{color:n.color,textAlign:d,textBaseline:"middle"})}}function nm(e,t,o,r){let{ctx:i}=e;if(o)i.arc(e.xCenter,e.yCenter,t,0,vt);else{let s=e.getPointPosition(0,t);i.moveTo(s.x,s.y);for(let n=1;n<r;n++)s=e.getPointPosition(n,t),i.lineTo(s.x,s.y)}}function Iw(e,t,o,r,i){let s=e.ctx,n=t.circular,{color:a,lineWidth:l}=t;!n&&!r||!a||!l||o<0||(s.save(),s.strokeStyle=a,s.lineWidth=l,s.setLineDash(i.dash||[]),s.lineDashOffset=i.dashOffset,s.beginPath(),nm(e,o,n,r),s.closePath(),s.stroke(),s.restore())}function Zw(e,t,o){return Vr(e,{label:o,index:t,type:"pointLabel"})}var Hg=class extends tn{static id="radialLinear";static defaults={display:!0,animate:!0,position:"chartArea",angleLines:{display:!0,lineWidth:1,borderDash:[],borderDashOffset:0},grid:{circular:!1},startAngle:0,ticks:{showLabelBackdrop:!0,callback:ia.formatters.numeric},pointLabels:{backdropColor:void 0,backdropPadding:2,display:!0,font:{size:10},callback(t){return t},padding:5,centerPointLabels:!1}};static defaultRoutes={"angleLines.color":"borderColor","pointLabels.color":"color","ticks.color":"color"};static descriptors={angleLines:{_fallback:"grid"}};constructor(t){super(t),this.xCenter=void 0,this.yCenter=void 0,this.drawingArea=void 0,this._pointLabels=[],this._pointLabelItems=[]}setDimensions(){let t=this._padding=ko(up(this.options)/2),o=this.width=this.maxWidth-t.width,r=this.height=this.maxHeight-t.height;this.xCenter=Math.floor(this.left+o/2+t.left),this.yCenter=Math.floor(this.top+r/2+t.top),this.drawingArea=Math.floor(Math.min(o,r)/2)}determineDataLimits(){let{min:t,max:o}=this.getMinMax(!1);this.min=ht(t)&&!isNaN(t)?t:0,this.max=ht(o)&&!isNaN(o)?o:0,this.handleTickRangeOptions()}computeTickLimit(){return Math.ceil(this.drawingArea/up(this.options))}generateTickLabels(t){tn.prototype.generateTickLabels.call(this,t),this._pointLabels=this.getLabels().map((o,r)=>{let i=pt(this.options.pointLabels.callback,[o,r],this);return i||i===0?i:""}).filter((o,r)=>this.chart.getDataVisibility(r))}fit(){let t=this.options;t.display&&t.pointLabels.display?Pw(this):this.setCenterPoint(0,0,0,0)}setCenterPoint(t,o,r,i){this.xCenter+=Math.floor((t-o)/2),this.yCenter+=Math.floor((r-i)/2),this.drawingArea-=Math.min(this.drawingArea/2,Math.max(t,o,r,i))}getIndexAngle(t){let o=vt/(this._pointLabels.length||1),r=this.options.startAngle||0;return Ft(t*o+Or(r))}getDistanceFromCenterForValue(t){if(Ze(t))return NaN;let o=this.drawingArea/(this.max-this.min);return this.options.reverse?(this.max-t)*o:(t-this.min)*o}getValueForDistanceFromCenter(t){if(Ze(t))return NaN;let o=t/(this.drawingArea/(this.max-this.min));return this.options.reverse?this.max-o:this.min+o}getPointLabelContext(t){let o=this._pointLabels||[];if(t>=0&&t<o.length){let r=o[t];return Zw(this.getContext(),t,r)}}getPointPosition(t,o,r=0){let i=this.getIndexAngle(t)-Ct+r;return{x:Math.cos(i)*o+this.xCenter,y:Math.sin(i)*o+this.yCenter,angle:i}}getPointPositionForValue(t,o){return this.getPointPosition(t,this.getDistanceFromCenterForValue(o))}getBasePosition(t){return this.getPointPositionForValue(t||0,this.getBaseValue())}getPointLabelPosition(t){let{left:o,top:r,right:i,bottom:s}=this._pointLabelItems[t];return{left:o,top:r,right:i,bottom:s}}drawBackground(){let{backgroundColor:t,grid:{circular:o}}=this.options;if(t){let r=this.ctx;r.save(),r.beginPath(),nm(this,this.getDistanceFromCenterForValue(this._endValue),o,this._pointLabels.length),r.closePath(),r.fillStyle=t,r.fill(),r.restore()}}drawGrid(){let t=this.ctx,o=this.options,{angleLines:r,grid:i,border:s}=o,n=this._pointLabels.length,a,l,c;if(o.pointLabels.display&&Bw(this,n),i.display&&this.ticks.forEach((d,p)=>{if(p!==0||p===0&&this.min<0){l=this.getDistanceFromCenterForValue(d.value);let u=this.getContext(p),m=i.setContext(u),b=s.setContext(u);Iw(this,m,l,n,b)}}),r.display){for(t.save(),a=n-1;a>=0;a--){let d=r.setContext(this.getPointLabelContext(a)),{color:p,lineWidth:u}=d;!u||!p||(t.lineWidth=u,t.strokeStyle=p,t.setLineDash(d.borderDash),t.lineDashOffset=d.borderDashOffset,l=this.getDistanceFromCenterForValue(o.reverse?this.min:this.max),c=this.getPointPosition(a,l),t.beginPath(),t.moveTo(this.xCenter,this.yCenter),t.lineTo(c.x,c.y),t.stroke())}t.restore()}}drawBorder(){}drawLabels(){let t=this.ctx,o=this.options,r=o.ticks;if(!r.display)return;let i=this.getIndexAngle(0),s,n;t.save(),t.translate(this.xCenter,this.yCenter),t.rotate(i),t.textAlign="center",t.textBaseline="middle",this.ticks.forEach((a,l)=>{if(l===0&&this.min>=0&&!o.reverse)return;let c=r.setContext(this.getContext(l)),d=uo(c.font);if(s=this.getDistanceFromCenterForValue(this.ticks[l].value),c.showLabelBackdrop){t.font=d.string,n=t.measureText(a.label).width,t.fillStyle=c.backdropColor;let p=ko(c.backdropPadding);t.fillRect(-n/2-p.left,-s-d.size/2-p.top,n+p.width,d.size+p.height)}sa(t,a.label,0,-s,d,{color:c.color,strokeColor:c.textStrokeColor,strokeWidth:c.textStrokeWidth})}),t.restore()}drawTitle(){}},l1={millisecond:{common:!0,size:1,steps:1e3},second:{common:!0,size:1e3,steps:60},minute:{common:!0,size:6e4,steps:60},hour:{common:!0,size:36e5,steps:24},day:{common:!0,size:864e5,steps:30},week:{common:!1,size:6048e5,steps:4},month:{common:!0,size:2628e6,steps:12},quarter:{common:!1,size:7884e6,steps:4},year:{common:!0,size:3154e7}},go=Object.keys(l1);function Bg(e,t){return e-t}function Ig(e,t){if(Ze(t))return null;let o=e._adapter,{parser:r,round:i,isoWeekday:s}=e._parseOpts,n=t;return typeof r=="function"&&(n=r(n)),ht(n)||(n=typeof r=="string"?o.parse(n,r):o.parse(n)),n===null?null:(i&&(n=i==="week"&&(Xs(s)||s===!0)?o.startOf(n,"isoWeek",s):o.startOf(n,i)),+n)}function Zg(e,t,o,r){let i=go.length;for(let s=go.indexOf(e);s<i-1;++s){let n=l1[go[s]],a=n.steps?n.steps:Number.MAX_SAFE_INTEGER;if(n.common&&Math.ceil((o-t)/(a*n.size))<=r)return go[s]}return go[i-1]}function Fw(e,t,o,r,i){for(let s=go.length-1;s>=go.indexOf(o);s--){let n=go[s];if(l1[n].common&&e._adapter.diff(i,r,n)>=t-1)return n}return go[o?go.indexOf(o):0]}function Nw(e){for(let t=go.indexOf(e)+1,o=go.length;t<o;++t)if(l1[go[t]].common)return go[t]}function Fg(e,t,o){if(!o)e[t]=!0;else if(o.length){let{lo:r,hi:i}=$c(o,t),s=o[r]>=t?o[r]:o[i];e[s]=!0}}function jw(e,t,o,r){let i=e._adapter,s=+i.startOf(t[0].value,r),n=t[t.length-1].value,a,l;for(a=s;a<=n;a=+i.add(a,1,r))l=o[a],l>=0&&(t[l].major=!0);return t}function Ng(e,t,o){let r=[],i={},s=t.length,n,a;for(n=0;n<s;++n)a=t[n],i[a]=n,r.push({value:a,major:!1});return s===0||!o?r:jw(e,r,i,o)}var on=class extends es{static id="time";static defaults={bounds:"data",adapters:{},time:{parser:!1,unit:!1,round:!1,isoWeekday:!1,minUnit:"millisecond",displayFormats:{}},ticks:{source:"auto",callback:!1,major:{enabled:!1}}};constructor(t){super(t),this._cache={data:[],labels:[],all:[]},this._unit="day",this._majorUnit=void 0,this._offsets={},this._normalized=!1,this._parseOpts=void 0}init(t,o={}){let r=t.time||(t.time={}),i=this._adapter=new V7._date(t.adapters.date);i.init(o),Ys(r.displayFormats,i.formats()),this._parseOpts={parser:r.parser,round:r.round,isoWeekday:r.isoWeekday},super.init(t),this._normalized=o.normalized}parse(t,o){return t===void 0?null:Ig(this,t)}beforeLayout(){super.beforeLayout(),this._cache={data:[],labels:[],all:[]}}determineDataLimits(){let t=this.options,o=this._adapter,r=t.time.unit||"day",{min:i,max:s,minDefined:n,maxDefined:a}=this.getUserBounds();function l(c){!n&&!isNaN(c.min)&&(i=Math.min(i,c.min)),!a&&!isNaN(c.max)&&(s=Math.max(s,c.max))}(!n||!a)&&(l(this._getLabelBounds()),(t.bounds!=="ticks"||t.ticks.source!=="labels")&&l(this.getMinMax(!1))),i=ht(i)&&!isNaN(i)?i:+o.startOf(Date.now(),r),s=ht(s)&&!isNaN(s)?s:+o.endOf(Date.now(),r)+1,this.min=Math.min(i,s-1),this.max=Math.max(i+1,s)}_getLabelBounds(){let t=this.getLabelTimestamps(),o=Number.POSITIVE_INFINITY,r=Number.NEGATIVE_INFINITY;return t.length&&(o=t[0],r=t[t.length-1]),{min:o,max:r}}buildTicks(){let t=this.options,o=t.time,r=t.ticks,i=r.source==="labels"?this.getLabelTimestamps():this._generate();t.bounds==="ticks"&&i.length&&(this.min=this._userMin||i[0],this.max=this._userMax||i[i.length-1]);let s=this.min,n=this.max,a=xf(i,s,n);return this._unit=o.unit||(r.autoSkip?Zg(o.minUnit,this.min,this.max,this._getLabelCapacity(s)):Fw(this,a.length,o.minUnit,this.min,this.max)),this._majorUnit=!r.major.enabled||this._unit==="year"?void 0:Nw(this._unit),this.initOffsets(i),t.reverse&&a.reverse(),Ng(this,a,this._majorUnit)}afterAutoSkip(){this.options.offsetAfterAutoskip&&this.initOffsets(this.ticks.map(t=>+t.value))}initOffsets(t=[]){let o=0,r=0,i,s;this.options.offset&&t.length&&(i=this.getDecimalForValue(t[0]),t.length===1?o=1-i:o=(this.getDecimalForValue(t[1])-i)/2,s=this.getDecimalForValue(t[t.length-1]),t.length===1?r=s:r=(s-this.getDecimalForValue(t[t.length-2]))/2);let n=t.length<3?.5:.25;o=Yt(o,0,n),r=Yt(r,0,n),this._offsets={start:o,end:r,factor:1/(o+1+r)}}_generate(){let t=this._adapter,o=this.min,r=this.max,i=this.options,s=i.time,n=s.unit||Zg(s.minUnit,o,r,this._getLabelCapacity(o)),a=ze(i.ticks.stepSize,1),l=n==="week"?s.isoWeekday:!1,c=Xs(l)||l===!0,d={},p=o,u,m;if(c&&(p=+t.startOf(p,"isoWeek",l)),p=+t.startOf(p,c?"day":n),t.diff(r,o,n)>1e5*a)throw new Error(o+" and "+r+" are too far apart with stepSize of "+a+" "+n);let b=i.ticks.source==="data"&&this.getDataTimestamps();for(u=p,m=0;u<r;u=+t.add(u,a,n),m++)Fg(d,u,b);return(u===r||i.bounds==="ticks"||m===1)&&Fg(d,u,b),Object.keys(d).sort(Bg).map(C=>+C)}getLabelForValue(t){let o=this._adapter,r=this.options.time;return r.tooltipFormat?o.format(t,r.tooltipFormat):o.format(t,r.displayFormats.datetime)}format(t,o){let i=this.options.time.displayFormats,s=this._unit,n=o||i[s];return this._adapter.format(t,n)}_tickFormatFunction(t,o,r,i){let s=this.options,n=s.ticks.callback;if(n)return pt(n,[t,o,r],this);let a=s.time.displayFormats,l=this._unit,c=this._majorUnit,d=l&&a[l],p=c&&a[c],u=r[o],m=c&&p&&u&&u.major;return this._adapter.format(t,i||(m?p:d))}generateTickLabels(t){let o,r,i;for(o=0,r=t.length;o<r;++o)i=t[o],i.label=this._tickFormatFunction(i.value,o,t)}getDecimalForValue(t){return t===null?NaN:(t-this.min)/(this.max-this.min)}getPixelForValue(t){let o=this._offsets,r=this.getDecimalForValue(t);return this.getPixelForDecimal((o.start+r)*o.factor)}getValueForPixel(t){let o=this._offsets,r=this.getDecimalForPixel(t)/o.factor-o.end;return this.min+r*(this.max-this.min)}_getLabelSize(t){let o=this.options.ticks,r=this.ctx.measureText(t).width,i=Or(this.isHorizontal()?o.maxRotation:o.minRotation),s=Math.cos(i),n=Math.sin(i),a=this._resolveTickFontOptions(0).size;return{w:r*s+a*n,h:r*n+a*s}}_getLabelCapacity(t){let o=this.options.time,r=o.displayFormats,i=r[o.unit]||r.millisecond,s=this._tickFormatFunction(t,0,Ng(this,[t],this._majorUnit),i),n=this._getLabelSize(s),a=Math.floor(this.isHorizontal()?this.width/n.w:this.height/n.h)-1;return a>0?a:1}getDataTimestamps(){let t=this._cache.data||[],o,r;if(t.length)return t;let i=this.getMatchingVisibleMetas();if(this._normalized&&i.length)return this._cache.data=i[0].controller.getAllParsedValues(this);for(o=0,r=i.length;o<r;++o)t=t.concat(i[o].controller.getAllParsedValues(this));return this._cache.data=this.normalize(t)}getLabelTimestamps(){let t=this._cache.labels||[],o,r;if(t.length)return t;let i=this.getLabels();for(o=0,r=i.length;o<r;++o)t.push(Ig(this,i[o]));return this._cache.labels=this._normalized?t:this.normalize(t)}normalize(t){return Lf(t.sort(Bg))}};function Uc(e,t,o){let r=0,i=e.length-1,s,n,a,l;o?(t>=e[r].pos&&t<=e[i].pos&&({lo:r,hi:i}=ni(e,"pos",t)),{pos:s,time:a}=e[r],{pos:n,time:l}=e[i]):(t>=e[r].time&&t<=e[i].time&&({lo:r,hi:i}=ni(e,"time",t)),{time:s,pos:a}=e[r],{time:n,pos:l}=e[i]);let c=n-s;return c?a+(l-a)*(t-s)/c:a}var jg=class extends on{static id="timeseries";static defaults=on.defaults;constructor(t){super(t),this._table=[],this._minPos=void 0,this._tableRange=void 0}initOffsets(){let t=this._getTimestampsForTable(),o=this._table=this.buildLookupTable(t);this._minPos=Uc(o,this.min),this._tableRange=Uc(o,this.max)-this._minPos,super.initOffsets(t)}buildLookupTable(t){let{min:o,max:r}=this,i=[],s=[],n,a,l,c,d;for(n=0,a=t.length;n<a;++n)c=t[n],c>=o&&c<=r&&i.push(c);if(i.length<2)return[{time:o,pos:0},{time:r,pos:1}];for(n=0,a=i.length;n<a;++n)d=i[n+1],l=i[n-1],c=i[n],Math.round((d+l)/2)!==c&&s.push({time:c,pos:n/(a-1)});return s}_generate(){let t=this.min,o=this.max,r=super.getDataTimestamps();return(!r.includes(t)||!r.length)&&r.splice(0,0,t),(!r.includes(o)||r.length===1)&&r.push(o),r.sort((i,s)=>i-s)}_getTimestampsForTable(){let t=this._cache.all||[];if(t.length)return t;let o=this.getDataTimestamps(),r=this.getLabelTimestamps();return o.length&&r.length?t=this.normalize(o.concat(r)):t=o.length?o:r,t=this._cache.all=t,t}getDecimalForValue(t){return(Uc(this._table,t)-this._minPos)/this._tableRange}getValueForPixel(t){let o=this._offsets,r=this.getDecimalForPixel(t)/o.factor-o.end;return Uc(this._table,r*this._tableRange+this._minPos,!0)}};var fp=["--base-gray-500","--base-gray-400","--base-gray-300","--base-gray-200","--base-gray-100"],gp=["--base-blue-500","--base-blue-400","--base-blue-300","--base-blue-200","--base-blue-100"],Xo={CANVAS_PADDING:32,CHART_WIDTH:256,MIN_CHART_WIDTH:48,MIN_HEIGHT_WITH_LABELS:192};var os={bgColorVar:"--container-global-color",borderColorVar:"--normal-enabled-border-color",BORDER_RADIUS:6,fontColorVar:"--element-neutral-color",label:{fontSizeVar:"--global-typography-instrument-label-font-size",fontWeightVar:"--global-typography-instrument-label-font-weight",fontColorVar:"--instrument-regular-secondary-color"},unit:{fontSizeVar:"--global-typography-instrument-unit-font-size",fontWeightVar:"--global-typography-instrument-unit-font-weight",fontColorVar:"--instrument-regular-secondary-color"}},Er={fontFamily:"--font-family-main",fontSizeVar:"--global-typography-ui-label-font-size",fontWeightVar:"--global-typography-ui-label-font-weight",fontColorVar:"--instrument-tick-mark-label-secondary-color"},pi={gridColorVar:"--instrument-tick-mark-tertiary-color",tickColorVar:"--border-outline-color",thresholdLowColorVar:"--base-red-500",thresholdHighColorVar:"--base-blue-500",stackedDividerColorVar:"--overlay-border-silhouette-color"},am="--instrument-frame-primary-color",Rr={DEFAULT_ASPECT_RATIO:1.5,MIN_HEIGHT_WITH_LABELS:192};function dt(e,t){return getComputedStyle(e).getPropertyValue(t).trim()}function mp(e,t,o){return t.length>0?t:o.map(r=>dt(e,r))}function rs(e,t,o=.5){if(!t||typeof t!="string")return"rgba(0, 0, 0, 0)";let r=t.trim();if(r.startsWith("var(")){let s=r.replace(/^var\(/,"").replace(/\)$/,"").trim();if(s.startsWith("--")){let n=dt(e,s);n&&(r=n.trim())}}else if(r.startsWith("--")){let s=dt(e,r);s&&(r=s.trim())}if(r.startsWith("#")){let s=r.slice(1);if(s.length===3){let n=parseInt(s[0]+s[0],16),a=parseInt(s[1]+s[1],16),l=parseInt(s[2]+s[2],16);return`rgba(${n}, ${a}, ${l}, ${o})`}if(s.length===6){let n=parseInt(s.slice(0,2),16),a=parseInt(s.slice(2,4),16),l=parseInt(s.slice(4,6),16);return`rgba(${n}, ${a}, ${l}, ${o})`}}let i=r.match(/rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)/);if(i){let s=parseInt(i[1],10),n=parseInt(i[2],10),a=parseInt(i[3],10);return`rgba(${s}, ${n}, ${a}, ${o})`}return r}function lm(e){let t=document.documentElement,o=new MutationObserver(r=>{for(let i of r)if(i.type==="attributes"&&i.attributeName==="data-obc-theme"){e();break}});return o.observe(t,{attributes:!0,attributeFilter:["data-obc-theme"]}),o}function cm(e,t,o,r=0){return o?(e/t*100).toFixed(r):e.toFixed(r)}function dm(e){return{enabled:!0,displayColors:!0,caretSize:0,boxPadding:4,boxWidth:16,boxHeight:16,backgroundColor:dt(e,os.bgColorVar),borderColor:dt(e,os.borderColorVar),borderWidth:1,cornerRadius:os.BORDER_RADIUS,titleColor:dt(e,os.fontColorVar),bodyColor:dt(e,os.fontColorVar),footerColor:dt(e,os.fontColorVar),animation:!1,padding:12}}function hm(e){return e.map(t=>`
        <div class="legend-item">
          <span class="legend-group legend-group--label">
            <span class="legend-color" style="background-color: ${t.fillStyle};"></span>
            <span class="legend-label">${t.label}</span>
          </span>
          <span class="legend-group legend-group--value-unit">
            <span class="legend-value">${t.value}</span>
            <span class="legend-unit">${t.unit}</span>
          </span>
        </div>
      `).join("")}var rn=(e=>(e.time="time",e.number="number",e))(rn||{});function Ww(e){return typeof e.epochMilliseconds=="number"}function Uw(e){let t=e;return typeof t.year=="number"&&typeof t.month=="number"&&typeof t.day=="number"}function va(e,t){if(typeof e=="number")return Number.isFinite(e)?e:NaN;if(e instanceof Date)return e.getTime();if(typeof e=="object"&&e!==null)return Ww(e)?e.epochMilliseconds:Uw(e)?new Date(e.year,e.month-1,e.day,e.hour??0,e.minute??0,e.second??0,e.millisecond??0).getTime():NaN;if(typeof e=="string"){if(e.trim()==="")return NaN;if(t==="time"){let r=Date.parse(e);if(Number.isFinite(r))return r}let o=Number(e);return Number.isFinite(o)?o:NaN}return NaN}function ba(e,t,o){return Number.isFinite(e)?t==="number"?String(e):o!==void 0&&Number.isFinite(o)?`${Math.round((e-o)/6e4)}min`:new Date(e).toLocaleDateString():""}function pm(e,t,o){let r=t(),i=new ResizeObserver(()=>{if(!e.isConnected)return;let s=t(),n=s!==r;r=s,n?o.rebuild():o.update()});return i.observe(e),i}function vp(e){return`${e.weight} ${e.sizePx}px ${e.family}`}function bp(e){return Math.round(e.sizePx*1.2)}function um(e,t,o){let r=Number.isInteger(t)&&Number.isInteger(o)?0:1;return e.toFixed(r)}function c1(e,t){return e<0&&t>0?[e,0,t]:[e,t]}var Gw=8,Yw=4;function d1(e,t,o,r){e.save(),e.font=vp(t);let i=o.reduce((s,n)=>Math.max(s,e.measureText(n).width),0);return e.restore(),{side:o.length?Math.ceil(i)+Gw:0,bottom:r.length?bp(t)+Yw:0}}var zr=(e=>(e.regular="regular",e.enhanced="enhanced",e))(zr||{});function fm(e,t){return e==="regular"?"var(--instrument-tick-mark-tertiary-color)":t==="tertiary"?"var(--instrument-tick-mark-secondary-color)":"var(--instrument-tick-mark-primary-color)"}var wp=(e=>(e.advice="advice",e.caution="caution",e))(wp||{}),Ko=(e=>(e.regular="regular",e.hinted="hinted",e.triggered="triggered",e))(Ko||{}),qw=16/2+8,wE=Math.atan2(qw,672/2);function gm(e,t=1){return e-t}function mm(e,t,o,r,i=1){let s=gm(r,i),n=o-t;return(-e+t)*s/n+s/2+i/2}function vm(e,t,o,r,i=1){let s=gm(r,i),n=o-t;return(e-t)*s/n+i/2}function wa(e,t,o,r,i=1){let s=i/2,n=e,a=t;return e===o&&(n=e+s,a=t-s),e+t===r&&(a=a-s),{x:n,width:a}}function ya(e,t,o,r,i=1){let s=i/2,n=e,a=t;return e===o&&(n=e+s,a=t-s),e+t===r&&(a=a-s),{y:n,height:a}}var Lo=(e=>(e.vertical="vertical",e.horizontal="horizontal",e))(Lo||{}),Hr=(e=>(e.left="left",e.right="right",e.top="top",e.bottom="bottom",e))(Hr||{}),oo=(e=>(e.regular="regular",e.condensed="condensed",e))(oo||{}),Io=(e=>(e.fill="fill",e.tint="tint",e))(Io||{}),Br=(e=>(e.center="center",e.inner="inner",e.outer="outer",e))(Br||{}),Ca=(e=>(e.primary="primary",e.secondary="secondary",e))(Ca||{}),_p="--instrument-components-watchface-frame-regular-border-radius";function Xw(e,t){if(!e)return;let o=e.trim(),r=Number.parseFloat(o);if(!Number.isFinite(r))return;if(o.endsWith("px"))return r;let i=typeof getComputedStyle=="function";if(o.endsWith("rem")){if(!i)return;let s=t?.documentElement??(typeof document<"u"?document.documentElement:void 0);if(!s)return;let n=Number.parseFloat(getComputedStyle(s).fontSize);return Number.isFinite(n)?r*n:void 0}if(o.endsWith("em")){if(!i)return;let s=t?.element;if(!s)return;let n=Number.parseFloat(getComputedStyle(s).fontSize);return Number.isFinite(n)?r*n:void 0}return r}function sn(e,t,o=_p){let r=t==="condensed"?4:8;if(typeof getComputedStyle!="function")return r;let i=getComputedStyle(e).getPropertyValue(o).trim();return Xw(i,{element:e,documentElement:e.ownerDocument?.documentElement??(typeof document<"u"?document.documentElement:void 0)})??r}function nn(e,t){if(typeof MutationObserver>"u")return;let o=new MutationObserver(()=>t()),r=[e],i=e.parentElement;for(;i;)r.push(i),i=i.parentElement;let s=e.ownerDocument?.documentElement;s&&r.push(s);for(let n of r)o.observe(n,{attributes:!0,attributeFilter:["class","style"]});return o}function Kw(e){return e==="condensed"?4:8}function Qw(e){let t=Kw(e.scaleType),o=e.borderRadius;return typeof o=="number"&&Number.isFinite(o)&&o>=0?o:t}function an(e){let t=Number.isFinite(e.barThickness)?e.barThickness:0;if(!e.hasBar)return t;let o=Qw(e);return Math.max(t,o*2)}function xa(e){let t=Number.isFinite(e.tickThickness)?e.tickThickness:0;return e.scaleType==="condensed"?Math.min(t,14):t}function u1(e){return{orientation:e.orientation,side:e.side,hasBar:e.hasBar,hasScale:e.hasScale,labels:e.labels,barThickness:an(e),tickThickness:xa(e),labelThickness:e.labelThickness,length:e.length,scaleType:e.scaleType,advicePosition:e.advicePosition,hasAdvice:!!e.advices&&e.advices.length>0,hasSetpoint:e.setpoint!==void 0||e.newSetpoint!==void 0||e.departingNewSetpoint!==void 0}}function _a(e,t){return e.orientation==="vertical"?{x:t.viewBoxPerpStart,y:-e.length/2,width:t.viewBoxThickness,height:e.length}:{x:0,y:t.viewBoxPerpStart,width:e.length,height:t.viewBoxThickness}}function fi(e){let{containerMainAxisSize:t,scaleReferenceSize:o}=e;return t<=0||o<=0?1:t/o}function ka(e){let t=e.hasBar?e.barThickness:0,o=xa(e),r=e.hasScale?o:0,i=e.labels?e.labelThickness:0,s=Jw(e),n=kp(e),a=Math.max(r+i,s,n),l=t+a,d=e.orientation==="vertical"&&e.side==="right"||e.orientation==="horizontal"&&e.side==="bottom"?0:-l;return{thickness:l,viewBoxPerpStart:d,viewBoxLength:e.length,viewBoxThickness:l}}function Jw(e){if(!e.hasAdvice)return 0;let t=e.hasBar?e.advicePosition??"inner":"inner";return t==="center"?0:t==="outer"?24:16}function kp(e){return e.hasSetpoint?Sa()+hh+k0:0}function Ht(e){return e.orientation==="vertical"}function Ne(e){return e.orientation==="vertical"&&e.side==="right"||e.orientation==="horizontal"&&e.side==="bottom"}function Lp(e,t){return e<=0&&t>=0}function xm(e){let t=e.mainTickmarks?.length?e.mainTickmarks:[e.minValue,0,e.maxValue];return[...new Set(t)].filter(o=>o>=e.minValue&&o<=e.maxValue).sort((o,r)=>o-r)}var bm=1e3,ey=64,h1=new Set;function _m(e,t){let o=Math.floor((e.maxValue-e.minValue)/t)+1;if(!(o>bm))return!1;let r=`${e.minValue}/${e.maxValue}/${t}`;return h1.has(r)||(h1.size>=ey&&h1.clear(),h1.add(r),console.warn(`[external-scale] tick interval ${t} over the range ${e.minValue}\u2026${e.maxValue} is ${o} ticks; the ladder is not drawn (limit ${bm}). A range in epoch milliseconds needs an interval in milliseconds.`)),!0}function ty(e){let t=e.touching??!1;return Ql({value:e.value,setpoint:e.setpoint,touching:t,auto:e.autoAtSetpoint,deadband:e.autoAtSetpointDeadband,atSetpointManual:e.atSetpoint})}function oy(e){return(e.touching??!1)&&e.newSetpoint===void 0?ji.focus:ty(e)?e.setpoint!==void 0&&Math.abs(e.setpoint)<e.setpointAtZeroDeadband?ji.equalZero:ji.equal:ji.notEqual}function wm(e){return e.priority===zt.enhanced?Kl.enhanced:Kl.regular}function ry(e){return e.setpointDisabled!==void 0?e.setpointDisabled:e.setpointOverride?!1:e.state===to.loading||e.state===to.off}function km(e){let t=e.priority===zt.enhanced,o=e.fillMode==="tint"?t?"var(--instrument-enhanced-tertiary-color)":"var(--instrument-regular-tertiary-color)":t?"var(--instrument-enhanced-secondary-color)":"var(--instrument-regular-secondary-color)",r=t?"var(--instrument-enhanced-secondary-color)":"var(--instrument-regular-secondary-color)",i=t?"var(--instrument-enhanced-tertiary-color)":"var(--instrument-regular-tertiary-color)",s=t?"var(--instrument-enhanced-primary-color)":"var(--instrument-regular-primary-color)";return(e.state===to.loading||e.state===to.off)&&(o="transparent",r="var(--instrument-frame-tertiary-color)",i="var(--instrument-frame-tertiary-color)",s="var(--instrument-frame-tertiary-color)"),{barFillColor:o,markerFillColor:r,markerStrokeColor:i,setpointColor:s}}function iy(e,t){return e.map(o=>{let i=t!==void 0&&t>=o.min&&t<=o.max?Ko.triggered:o.hinted?Ko.hinted:Ko.regular;return{min:o.min,max:o.max,type:o.type,state:i}})}function ui(e){return Ht(e)?(e.paddingStart-e.paddingEnd)/2:e.paddingStart}function f1(e){return Math.max(0,e.length-e.paddingStart-e.paddingEnd)}function Lt(e,t){let o=f1(e);return Ht(e)?mm(t,e.minValue,e.maxValue,o)+ui(e):vm(t,e.minValue,e.maxValue,o)+ui(e)}function Lm(e){let t=e==="condensed";return{primary:t?10:20,secondary:t?4:8,tertiary:t?2:4,main:t?10:20}}function La(e){return e.hasBar?Ne(e)?e.barThickness:-e.barThickness:0}function Sa(){return 4}function ym(){return 8}function xp(e,t,o,r){let i="var(--instrument-frame-tertiary-color)";if(Ht(e)){let c=o,d=o+r,p=t;return w`<line x1=${c} x2=${d} y1=${p} y2=${p} stroke=${i} stroke-width=${1} vector-effect="non-scaling-stroke"/>`}let n=o,a=o+r,l=t;return w`<line x1=${l} x2=${l} y1=${n} y2=${a} stroke=${i} stroke-width=${1} vector-effect="non-scaling-stroke"/>`}function yp(e,t,o,r,i){let s=[],n=[];if(t<=0||!Number.isFinite(t))return{svgs:s,values:n};if(_m(e,t))return{svgs:s,values:n};let a=Lp(e.minValue,e.maxValue),l=c=>{i.includes(c)||(n.push(c),s.push(xp(e,Lt(e,c),o,r)))};if(a){for(let c=t;c<=e.maxValue;c+=t)l(c);for(let c=-t;c>=e.minValue;c-=t)l(c)}else{let c=Math.ceil(e.minValue/t)*t;for(let d=c;d<=e.maxValue;d+=t)l(d)}return{svgs:s,values:n}}function sy(e){if(!e.hasScale)return[];let t=[],o=[],r=La(e),i=Sa(),s=Ne(e)?r+i:r-i,{primary:n,secondary:a,tertiary:l,main:c}=Lm(e.scaleType);if(Lp(e.minValue,e.maxValue)){let d=e.minValue===0||e.maxValue===0;if(!(e.scaleBackground&&d)){let u=n,m=s;t.push(xp(e,Lt(e,0),m,Ne(e)?u:-u))}o.push(0)}if(e.mainTickmarks){let d=e.frameStyle==="flat"?r:s,p=e.frameStyle==="flat"?c+4:c,u=Ne(e)?p:-p;for(let m of xm(e)){if(e.scaleBackground&&(m===e.minValue||m===e.maxValue)){o.push(m);continue}t.push(xp(e,Lt(e,m),d,u)),o.push(m)}}if(e.primaryTickmarkInterval!==void 0&&e.primaryTickmarkInterval>0){let{svgs:d,values:p}=yp(e,e.primaryTickmarkInterval,s,Ne(e)?n:-n,o);t.push(...d),o.push(...p)}if(e.secondaryTickmarkInterval!==void 0&&e.secondaryTickmarkInterval>0){let{svgs:d}=yp(e,e.secondaryTickmarkInterval,s,Ne(e)?a:-a,o);t.push(...d)}if(e.tertiaryTickmarkInterval!==void 0&&e.tertiaryTickmarkInterval>0){let{svgs:d}=yp(e,e.tertiaryTickmarkInterval,s,Ne(e)?l:-l,o);t.push(...d)}return t}function ny(e){if(!e.labels)return[];let t="var(--font-family-main)",o="var(--instrument-tick-mark-label-secondary-color)",r="calc(var(--global-typography-ui-label-font-size) / var(--scale, 1))",i=La(e),s=xa(e),n=Ne(e)?i+(e.hasScale?s:0)+ym():i-(e.hasScale?s:0)-ym(),a=[],l=(d,p)=>{let u=Lt(e,d);if(Ht(e)){let k=n,$=u,V=Ne(e)?"start":"end",O=p?.baseline??"middle";a.push(w`<text x=${k} y=${$} text-anchor=${V} dominant-baseline=${O} font-family=${t} style="font-size: ${r}" fill=${o}>${d}</text>`);return}let m=n,b=u,C=Ne(e)?"hanging":"auto",y=p?.anchor??"middle";a.push(w`<text x=${b} y=${m} text-anchor=${y} dominant-baseline=${C} font-family=${t} style="font-size: ${r}" fill=${o}>${d}</text>`)};if(e.mainTickmarkLabels){for(let d of xm(e)){let p=d===e.minValue?{anchor:"start",baseline:"auto"}:d===e.maxValue?{anchor:"end",baseline:"hanging"}:void 0;l(d,p)}return a}let c=e.primaryTickmarkInterval;if(c===void 0||c<=0||!Number.isFinite(c))return[];if(_m(e,c))return[];if(Lp(e.minValue,e.maxValue)){for(let d=0;d<=e.maxValue;d+=c)l(d);for(let d=-c;d>=e.minValue;d-=c)l(d)}else{let d=Math.ceil(e.minValue/c)*c;for(let p=d;p<=e.maxValue;p+=c)l(p)}return a}function ay(e){if(!e.hasBar)return z;let t=e.scaleType==="condensed"?4:8,o=e.borderRadius??t,r=1,i;e.barContainerStyle!==void 0?i=e.barContainerStyle==="secondary"?"var(--instrument-frame-secondary-color)":"var(--instrument-frame-primary-color)":i=e.scaleBackground?"var(--instrument-frame-secondary-color)":"var(--instrument-frame-primary-color)";let s="var(--instrument-frame-tertiary-color)",n=f1(e),a=ui(e),l=!0,c=!0,d=!0,p=!0;if(e.borderRadiusPosition)if(e.borderRadiusPosition===Qe.middleChild||e.borderRadiusPosition===Qe.middleRoundedChild)l=!1,c=!1,d=!1,p=!1;else if(Ht(e)){let I=e.side==="right",H=e.borderRadiusPosition===Qe.innerFirstChild;I?(l=H,d=H,c=!H,p=!H):(l=!H,d=!H,c=H,p=H)}else{let I=e.side==="bottom",H=e.borderRadiusPosition===Qe.innerFirstChild;I?(l=H,c=H,d=!H,p=!H):(l=!H,c=!H,d=H,p=H)}let u=o,m=l&&c&&d&&p,b=!l&&!c&&!d&&!p;if(Ht(e)){let I=Ne(e)?0:-e.barThickness,H=-n/2+a,W=e.barThickness,j=n,F=e.side==="right",me,ae;e.scaleBackground?F?(me=0,ae=e.barThickness+1):(me=-e.barThickness-1,ae=0):(me=F?0:-e.barThickness,ae=F?e.barThickness:0);let le=wa(I,W,me,ae,r);I=le.x,W=le.width;let ve=ya(H,j,-n/2+a,n/2+a,r);if(H=ve.y,j=ve.height,m||b){let re=m?u:0,pe=m?u:0;if(e.scaleBackground){let Be=e.side==="right",se;return Be?(se=`M ${I} ${H+(b?0:u)} L ${I} ${H+j-(b?0:u)}`,b||(se+=` Q ${I} ${H+j} ${I+u} ${H+j}`),se+=` L ${I+W-(b?0:u)} ${H+j}`,b||(se+=` Q ${I+W} ${H+j} ${I+W} ${H+j-u}`),se+=` M ${I+W} ${H+(b?0:u)}`,b||(se+=` Q ${I+W} ${H} ${I+W-u} ${H}`),se+=` L ${I+(b?0:u)} ${H}`,b||(se+=` Q ${I} ${H} ${I} ${H+u}`)):(se=`M ${I+(b?0:u)} ${H}`,se+=` L ${I+W-(b?0:u)} ${H}`,b||(se+=` Q ${I+W} ${H} ${I+W} ${H+u}`),se+=` L ${I+W} ${H+j-(b?0:u)}`,b||(se+=` Q ${I+W} ${H+j} ${I+W-u} ${H+j}`),se+=` L ${I+(b?0:u)} ${H+j}`,b||(se+=` Q ${I} ${H+j} ${I} ${H+j-u}`),se+=` M ${I} ${H+(b?0:u)}`,b||(se+=` Q ${I} ${H} ${I+u} ${H}`)),w`
          <rect x=${I} y=${H} width=${W} height=${j} rx=${re} ry=${pe} fill=${i} stroke="none"/>
          <path d="${se}" fill="none" stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>
        `}return w`<rect x=${I} y=${H} width=${W} height=${j} rx=${re} ry=${pe} fill=${i} stroke=${s} vector-effect="non-scaling-stroke"/>`}let X=I,G=H,he=W,fe=j,J=`M ${X+(l?u:0)} ${G}`;if(J+=` L ${X+he-(c?u:0)} ${G}`,c&&(J+=` Q ${X+he} ${G} ${X+he} ${G+u}`),J+=` L ${X+he} ${G+fe-(p?u:0)}`,p&&(J+=` Q ${X+he} ${G+fe} ${X+he-u} ${G+fe}`),J+=` L ${X+(d?u:0)} ${G+fe}`,d&&(J+=` Q ${X} ${G+fe} ${X} ${G+fe-u}`),J+=` L ${X} ${G+(l?u:0)}`,l&&(J+=` Q ${X} ${G} ${X+u} ${G}`),J+=" Z",e.scaleBackground){let re=e.side==="right",pe;return re?(pe=`M ${X} ${G+(l?u:0)}`,l&&(pe+=` Q ${X} ${G} ${X+u} ${G}`),pe+=` L ${X+he-(c?u:0)} ${G}`,c&&(pe+=` Q ${X+he} ${G} ${X+he} ${G+u}`),pe+=` M ${X+he} ${G+fe-(p?u:0)}`,p&&(pe+=` Q ${X+he} ${G+fe} ${X+he-u} ${G+fe}`),pe+=` L ${X+(d?u:0)} ${G+fe}`,d&&(pe+=` Q ${X} ${G+fe} ${X} ${G+fe-u}`),pe+=` L ${X} ${G+(l?u:0)}`):(pe=`M ${X+(l?u:0)} ${G}`,pe+=` L ${X+he-(c?u:0)} ${G}`,c&&(pe+=` Q ${X+he} ${G} ${X+he} ${G+u}`),pe+=` L ${X+he} ${G+fe-(p?u:0)}`,p&&(pe+=` Q ${X+he} ${G+fe} ${X+he-u} ${G+fe}`),pe+=` L ${X+(d?u:0)} ${G+fe}`,d&&(pe+=` Q ${X} ${G+fe} ${X} ${G+fe-u}`),pe+=` M ${X} ${G+(l?u:0)}`,l&&(pe+=` Q ${X} ${G} ${X+u} ${G}`)),w`
        <path d=${J} fill=${i} stroke="none"/>
        <path d="${pe}" fill="none" stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>
      `}return w`<path d=${J} fill=${i} stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>`}let C=ui(e),y=Ne(e)?0:-e.barThickness,k=n,$=e.barThickness,V=e.side==="bottom",O,P;e.scaleBackground?V?(O=0,P=e.barThickness+1):(O=-e.barThickness-1,P=0):(O=V?0:-e.barThickness,P=V?e.barThickness:0);let T=wa(C,k,C,C+k,r);C=T.x,k=T.width;let Z=ya(y,$,O,P,r);if(y=Z.y,$=Z.height,m||b){let I=m?u:0,H=m?u:0;if(e.scaleBackground){let W=e.side==="bottom",j;return W?(j=`M ${C+(b?0:u)} ${y}`,j+=` L ${C+k-(b?0:u)} ${y}`,b||(j+=` Q ${C+k} ${y} ${C+k} ${y+u}`),j+=` L ${C+k} ${y+$-(b?0:u)}`,b||(j+=` Q ${C+k} ${y+$} ${C+k-u} ${y+$}`),j+=` M ${C+(b?0:u)} ${y+$}`,b||(j+=` Q ${C} ${y+$} ${C} ${y+$-u}`),j+=` L ${C} ${y+(b?0:u)}`,b||(j+=` Q ${C} ${y} ${C+u} ${y}`)):(j=`M ${C} ${y+(b?0:u)}`,j+=` L ${C} ${y+$-(b?0:u)}`,b||(j+=` Q ${C} ${y+$} ${C+u} ${y+$}`),j+=` L ${C+k-(b?0:u)} ${y+$}`,b||(j+=` Q ${C+k} ${y+$} ${C+k} ${y+$-u}`),j+=` L ${C+k} ${y+(b?0:u)}`,b||(j+=` Q ${C+k} ${y} ${C+k-u} ${y}`),j+=` M ${C+(b?0:u)} ${y}`,b||(j+=` Q ${C} ${y} ${C} ${y+u}`)),w`
        <rect x=${C} y=${y} width=${k} height=${$} rx=${I} ry=${H} fill=${i} stroke="none"/>
        <path d="${j}" fill="none" stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>
      `}return w`<rect x=${C} y=${y} width=${k} height=${$} rx=${I} ry=${H} fill=${i} stroke=${s} vector-effect="non-scaling-stroke"/>`}let R=C,D=y,N=k,B=$,Y=`M ${R+(l?u:0)} ${D}`;if(Y+=` L ${R+N-(c?u:0)} ${D}`,c&&(Y+=` Q ${R+N} ${D} ${R+N} ${D+u}`),Y+=` L ${R+N} ${D+B-(p?u:0)}`,p&&(Y+=` Q ${R+N} ${D+B} ${R+N-u} ${D+B}`),Y+=` L ${R+(d?u:0)} ${D+B}`,d&&(Y+=` Q ${R} ${D+B} ${R} ${D+B-u}`),Y+=` L ${R} ${D+(l?u:0)}`,l&&(Y+=` Q ${R} ${D} ${R+u} ${D}`),Y+=" Z",e.scaleBackground){let I=e.side==="bottom",H;return I?(H=`M ${R+(l?u:0)} ${D}`,H+=` L ${R+N-(c?u:0)} ${D}`,c&&(H+=` Q ${R+N} ${D} ${R+N} ${D+u}`),H+=` L ${R+N} ${D+B-(p?u:0)}`,p&&(H+=` Q ${R+N} ${D+B} ${R+N-u} ${D+B}`),H+=` M ${R+(d?u:0)} ${D+B}`,d&&(H+=` Q ${R} ${D+B} ${R} ${D+B-u}`),H+=` L ${R} ${D+(l?u:0)}`,l&&(H+=` Q ${R} ${D} ${R+u} ${D}`)):(H=`M ${R} ${D+(l?u:0)}`,l&&(H+=` Q ${R} ${D} ${R+u} ${D}`),H+=` M ${R+N-(c?u:0)} ${D}`,c&&(H+=` Q ${R+N} ${D} ${R+N} ${D+u}`),H+=` L ${R+N} ${D+B-(p?u:0)}`,p&&(H+=` Q ${R+N} ${D+B} ${R+N-u} ${D+B}`),H+=` L ${R+(d?u:0)} ${D+B}`,d&&(H+=` Q ${R} ${D+B} ${R} ${D+B-u}`),H+=` L ${R} ${D+(l?u:0)}`),w`
      <path d=${Y} fill=${i} stroke="none"/>
      <path d="${H}" fill="none" stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>
    `}return w`<path d=${Y} fill=${i} stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>`}function ly(e){if(!e.hasBar||e.value===void 0)return z;let t=`obc-bar-fill-clip-${Math.random().toString(36).slice(2)}`,o=e.scaleType==="condensed"?4:8,i=e.borderRadius??o,s=km(e),n=e.fillMin??0,a=e.fillMax??e.value,l=Math.max(Math.min(n,e.maxValue),e.minValue),c=Math.max(Math.min(a,e.maxValue),e.minValue),d=Lt(e,l),p=Lt(e,c),u=8,m=4,b=f1(e),C=ui(e),y=!0,k=!0,$=!0,V=!0;if(e.borderRadiusPosition)if(e.borderRadiusPosition===Qe.middleChild||e.borderRadiusPosition===Qe.middleRoundedChild)y=!1,k=!1,$=!1,V=!1;else if(Ht(e)){let j=e.side==="right",F=e.borderRadiusPosition===Qe.innerFirstChild;j?(y=F,$=F,k=!F,V=!F):(y=!F,$=!F,k=F,V=F)}else{let j=e.side==="bottom",F=e.borderRadiusPosition===Qe.innerFirstChild;j?(y=F,k=F,$=!F,V=!F):(y=!F,k=!F,$=F,V=F)}let O=y&&k&&$&&V,P=!y&&!k&&!$&&!V;if(Ht(e)){let j=Ne(e)?0:-e.barThickness,F=e.barThickness,me=Math.min(d,p),ae=Math.abs(p-d),le=Ne(e)?0:-e.barThickness,ve=-b/2+C,X=e.barThickness,G=b,he=P?w`<rect x=${le} y=${ve} width=${X} height=${G} rx=${0} ry=${0}/>`:O?w`<rect x=${le} y=${ve} width=${X} height=${G} rx=${i} ry=${i}/>`:w`<path d=${(()=>{let J=le,re=ve,pe=X,Be=G,se=`M ${J+(y?i:0)} ${re}`;return se+=` L ${J+pe-(k?i:0)} ${re}`,k&&(se+=` Q ${J+pe} ${re} ${J+pe} ${re+i}`),se+=` L ${J+pe} ${re+Be-(V?i:0)}`,V&&(se+=` Q ${J+pe} ${re+Be} ${J+pe-i} ${re+Be}`),se+=` L ${J+($?i:0)} ${re+Be}`,$&&(se+=` Q ${J} ${re+Be} ${J} ${re+Be-i}`),se+=` L ${J} ${re+(y?i:0)}`,y&&(se+=` Q ${J} ${re} ${J+i} ${re}`),se+=" Z",se})()}/>`,fe=w`<rect x=${j} y=${me} width=${F} height=${ae} fill=${s.barFillColor} stroke="none"/>`;if(e.fillMode==="tint"){let J=Lt(e,e.value)-u/2,re=w`<rect x=${j} y=${J} width=${F} height=${u} rx=${m} fill=${s.markerFillColor} stroke=${s.markerStrokeColor} vector-effect="non-scaling-stroke"/>`;return w`<defs>
        <clipPath id=${t} clipPathUnits="userSpaceOnUse">${he}</clipPath>
      </defs>
      <g clip-path=${`url(#${t})`}>
        ${fe}
        ${re}
      </g>`}return w`<defs>
      <clipPath id=${t} clipPathUnits="userSpaceOnUse">${he}</clipPath>
    </defs>
    <g clip-path=${`url(#${t})`}>
      ${fe}
    </g>`}let T=Ne(e)?0:-e.barThickness,Z=e.barThickness,R=Math.min(d,p),D=Math.abs(p-d),N=ui(e),B=Ne(e)?0:-e.barThickness,Y=b,I=e.barThickness,H=P?w`<rect x=${N} y=${B} width=${Y} height=${I} rx=${0} ry=${0}/>`:O?w`<rect x=${N} y=${B} width=${Y} height=${I} rx=${i} ry=${i}/>`:w`<path d=${(()=>{let j=N,F=B,me=Y,ae=I,le=`M ${j+(y?i:0)} ${F}`;return le+=` L ${j+me-(k?i:0)} ${F}`,k&&(le+=` Q ${j+me} ${F} ${j+me} ${F+i}`),le+=` L ${j+me} ${F+ae-(V?i:0)}`,V&&(le+=` Q ${j+me} ${F+ae} ${j+me-i} ${F+ae}`),le+=` L ${j+($?i:0)} ${F+ae}`,$&&(le+=` Q ${j} ${F+ae} ${j} ${F+ae-i}`),le+=` L ${j} ${F+(y?i:0)}`,y&&(le+=` Q ${j} ${F} ${j+i} ${F}`),le+=" Z",le})()}/>`,W=w`<rect x=${R} y=${T} width=${D} height=${Z} fill=${s.barFillColor} stroke="none"/>`;if(e.fillMode==="tint"){let j=Lt(e,e.value)-u/2,F=w`<rect x=${j} y=${T} width=${u} height=${Z} rx=${m} fill=${s.markerFillColor} stroke=${s.markerStrokeColor} vector-effect="non-scaling-stroke"/>`;return w`<defs>
      <clipPath id=${t} clipPathUnits="userSpaceOnUse">${H}</clipPath>
    </defs>
    <g clip-path=${`url(#${t})`}>
      ${W}
      ${F}
    </g>`}return w`<defs>
    <clipPath id=${t} clipPathUnits="userSpaceOnUse">${H}</clipPath>
  </defs>
  <g clip-path=${`url(#${t})`}>
    ${W}
  </g>`}function cy(e){if(!e.scaleBackground)return z;let t=e.scaleType==="condensed"?4:8,o=e.borderRadius??t,r=1,i="var(--instrument-frame-primary-color)",s="var(--instrument-frame-tertiary-color)",{main:n}=Lm(e.scaleType),a=n+Sa(),l=f1(e),c=ui(e),d=e.orientation==="vertical"&&e.side==="left"||e.orientation==="horizontal"&&e.side==="top",p=e.orientation==="vertical"&&e.side==="right"||e.orientation==="horizontal"&&e.side==="top",u=e.orientation==="vertical"&&e.side==="left"||e.orientation==="horizontal"&&e.side==="bottom",m=e.orientation==="vertical"&&e.side==="right"||e.orientation==="horizontal"&&e.side==="bottom",b=o;if(Ht(e)){let j=e.hasBar?Ne(e)?e.barThickness:-e.barThickness:0,F=Ne(e)?j:j-a,me=-l/2+c,ae=a,le=l,ve=e.side==="right",X,G;e.hasBar?ve?(X=F-1,G=F+ae):(X=F,G=F+ae+1):(X=F,G=F+ae);let he=wa(F,ae,X,G,r);F=he.x,ae=he.width;let fe=ya(me,le,-l/2+c,l/2+c,r);me=fe.y,le=fe.height;let J=F,re=me,pe=ae,Be=le,se=`M ${J+(d?b:0)} ${re}`;se+=` L ${J+pe-(p?b:0)} ${re}`,p&&(se+=` Q ${J+pe} ${re} ${J+pe} ${re+b}`),se+=` L ${J+pe} ${re+Be-(m?b:0)}`,m&&(se+=` Q ${J+pe} ${re+Be} ${J+pe-b} ${re+Be}`),se+=` L ${J+(u?b:0)} ${re+Be}`,u&&(se+=` Q ${J} ${re+Be} ${J} ${re+Be-b}`),se+=` L ${J} ${re+(d?b:0)}`,d&&(se+=` Q ${J} ${re} ${J+b} ${re}`),se+=" Z";let wo=ve?J:J+pe,Oo=r/2;return w`<path d=${se} fill=${i} stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>
      <line x1=${wo} x2=${wo} y1=${re+Oo} y2=${re+Be-Oo} stroke=${i} stroke-width=${r+.5} vector-effect="non-scaling-stroke"/>`}let C=e.hasBar?Ne(e)?e.barThickness:-e.barThickness:0,y=ui(e),k=Ne(e)?C:C-a,$=l,V=a,O=e.side==="bottom",P,T;e.hasBar?O?(P=k-1,T=k+V):(P=k,T=k+V+1):(P=k,T=k+V);let Z=wa(y,$,y,y+$,r);y=Z.x,$=Z.width;let R=ya(k,V,P,T,r);k=R.y,V=R.height;let D=y,N=k,B=$,Y=V,I=`M ${D+(d?b:0)} ${N}`;I+=` L ${D+B-(p?b:0)} ${N}`,p&&(I+=` Q ${D+B} ${N} ${D+B} ${N+b}`),I+=` L ${D+B} ${N+Y-(m?b:0)}`,m&&(I+=` Q ${D+B} ${N+Y} ${D+B-b} ${N+Y}`),I+=` L ${D+(u?b:0)} ${N+Y}`,u&&(I+=` Q ${D} ${N+Y} ${D} ${N+Y-b}`),I+=` L ${D} ${N+(d?b:0)}`,d&&(I+=` Q ${D} ${N} ${D+b} ${N}`),I+=" Z";let H=O?N:N+Y,W=r/2;return w`<path d=${I} fill=${i} stroke=${s} stroke-width=${r} vector-effect="non-scaling-stroke"/>
    <line x1=${D+W} x2=${D+B-W} y1=${H} y2=${H} stroke=${i} stroke-width=${r+.5} vector-effect="non-scaling-stroke"/>`}function dy(e){return Ht(e)?e.side==="right"?90:-90:e.side==="bottom"?180:0}function Cm(e,t,o,r,i,s,n=1,a=!1){let l=$0(`external-scale-setpoint-${s}`),c=M0(o),p=Math.abs(t)<e.setpointAtZeroDeadband?Lt(e,0):Lt(e,t),u=La(e),b=Sa()+c,C=Ne(e)?u+b:u-b,y=dy(e),k=Ht(e)?C:p,$=Ht(e)?p:C;if(a){let V=`var(${ph}, ${L0})`;return w`
      <g style="transform: translate(${k}px, ${$}px) rotate(${y}deg); opacity: ${n}; transition: transform ${V} ease-out, opacity ${V} ease-out;">
        ${uh({visualState:o,colorMode:r,disabled:i,id:l})}
      </g>
    `}return w`
    <g transform="translate(${k}, ${$}) rotate(${y})" opacity="${n}">
      ${uh({visualState:o,colorMode:r,disabled:i,id:l})}
    </g>
  `}function hy(e){let t=e.setpoint!==void 0,o=e.newSetpoint!==void 0,r=e.departingNewSetpoint!==void 0,i=e.animateSetpoint===!0;if(!t&&!o&&!r)return z;let s=[];if(t){let n=oy(e),a=wm(e),l=ry(e),c=o?.75:1;s.push(Cm(e,e.setpoint,n,a,l,"original",c,i))}if(o||r){let n=o,a=n?e.newSetpoint:e.departingNewSetpoint,l=n?1:0,c=ji.focus,d=wm(e);s.push(Cm(e,a,c,d,!1,"new",l,i))}return w`${s}`}function py(e){if(!e.highlightCurrentValue||e.value===void 0||!e.hasScale)return z;let t=12,o=2,r=t/2+o/2,i=t/2,s=Lt(e,e.value),n=La(e),a=Ne(e)?n+r:n-r,c=km(e).markerFillColor,d="var(--instrument-frame-primary-color)";return Ht(e)?w`
      <circle
        cx=${a}
        cy=${s}
        r=${i}
        fill=${c}
        stroke=${d}
        stroke-width=${o}
        vector-effect="non-scaling-stroke"
      />
    `:w`
    <circle
      cx=${s}
      cy=${a}
      r=${i}
      fill=${c}
      stroke=${d}
      stroke-width=${o}
      vector-effect="non-scaling-stroke"
    />
  `}function p1(e,t,o,r){if(t>=e.maxValue||t<=e.minValue)return null;let i=fm(o),s=Lt(e,t),n=Sa(),a=Ne(e)?r+n:r-n,l=xa(e),c=Ne(e)?a+l:a-l;return Ht(e)?w`<line x1=${a} x2=${c} y1=${s} y2=${s} stroke=${i} stroke-width="1" vector-effect="non-scaling-stroke"/>`:w`<line x1=${s} x2=${s} y1=${a} y2=${c} stroke=${i} stroke-width="1" vector-effect="non-scaling-stroke"/>`}function Cp(e,t,o,r,i){if(Ht(e)){let y=Lt(e,t.min),k=Lt(e,t.max),$=Math.min(y,k),V=Math.max(y,k),O=o+4,P=$+4,T=Math.max(0,V-$-8);return w`<rect x=${O} y=${P} width=${8} height=${T} rx=${4} ry=${4} fill=${r} stroke=${i} stroke-width="1" vector-effect="non-scaling-stroke"/>`}let c=Lt(e,t.min),d=Lt(e,t.max),p=Math.min(c,d),u=Math.max(c,d),m=p+4,b=o+4,C=Math.max(0,u-p-8);return w`<rect x=${m} y=${b} width=${C} height=${8} rx=${4} ry=${4} fill=${r} stroke=${i} stroke-width="1" vector-effect="non-scaling-stroke"/>`}function uy(e,t){let o=La(e),i=e.hasBar?e.advicePosition:"inner",s;if(i==="center"){let k=e.barThickness/2-4;Ht(e),s=Ne(e)?k-4:-e.barThickness+k-4}else i==="inner"?s=Ne(e)?o:o-16:s=Ne(e)?e.barThickness+10:-e.barThickness-xa(e)+14;let n=[],a="var(--instrument-frame-tertiary-color)",l=t.min>e.minValue,c=t.max<e.maxValue,d=Ne(e)?0:-e.barThickness,p=Ne(e)?e.barThickness:0,u=y=>{let k=Lt(e,y);Ht(e)?n.push(w`<line x1=${d} x2=${p} y1=${k} y2=${k} stroke=${a} stroke-width="1" vector-effect="non-scaling-stroke" stroke-dasharray="4 4"/>`):n.push(w`<line x1=${k} x2=${k} y1=${d} y2=${p} stroke=${a} stroke-width="1" vector-effect="non-scaling-stroke" stroke-dasharray="4 4"/>`)};if(l&&u(t.min),c&&u(t.max),t.type===wp.caution){let y,k="var(--instrument-frame-primary-color)";t.state===Ko.hinted?y="var(--instrument-frame-tertiary-color)":t.state===Ko.regular?y="var(--instrument-tick-mark-tertiary-color)":(y="var(--on-caution-active-color)",k="var(--alert-caution-color)");let $=[],V=50,O=Lt(e,t.min),P=Lt(e,t.max),T=Math.min(O,P),R=Math.max(O,P)-T;if(Ht(e)){let B=s+8-25,Y=T-25;for(let I=-64;I<R+64;I+=16){let H=`translate(${B} ${Y+I})`,W=`M 50 0 L 0 ${V}`;$.push(w`<g transform=${H}><path d=${W} stroke=${y} stroke-width="6"/></g>`)}}else{let B=s+8-25,Y=T-25;for(let I=-64;I<R+64;I+=16){let H=`translate(${Y+I} ${B})`,W=`M 0 50 L ${V} 0`;$.push(w`<g transform=${H}><path d=${W} stroke=${y} stroke-width="6"/></g>`)}}let D=`externalScaleAdviceMask-${t.min}-${t.max}-${Math.random().toString(36).slice(2)}`,N=zr.regular;return t.state===Ko.regular?N=zr.regular:t.state===Ko.triggered&&(N=zr.enhanced),w`
      <defs>
        <mask id=${D} maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="-4096" y="-4096" width="8192" height="8192">
          ${Cp(e,t,s,"white","none")}
        </mask>
      </defs>
      <g mask="url(#${D})">
        ${k?w`<rect x="-2048" y="-2048" width="4096" height="4096" fill=${k}/>`:z}
        ${$}
      </g>
      ${Cp(e,t,s,"none",y)}
      ${p1(e,t.min,N,o)??z}
      ${p1(e,t.max,N,o)??z}
      ${n}
    `}let m,b,C;return t.state===Ko.hinted?(m="var(--instrument-frame-tertiary-color)",C="var(--instrument-frame-primary-color)",b=zr.regular):t.state===Ko.regular?(m="var(--instrument-regular-secondary-color)",C="var(--instrument-frame-primary-color)",b=zr.regular):(m="var(--instrument-enhanced-secondary-color)",C=m,b=zr.regular),w`
    ${Cp(e,t,s,C,m)}
    ${p1(e,t.min,b,o)??z}
    ${p1(e,t.max,b,o)??z}
    ${n}
  `}function fy(e){return!e.advices||!e.advices.length?[]:iy(e.advices,e.setpoint).map(o=>uy(e,o))}function g1(e){let t=ka(e),o=_a({orientation:e.orientation,length:e.length},t),r=e.orientation==="vertical"?o.width:o.height;return{side:e.side,thickness:r}}function m1(e){let t=an(e),o=t===e.barThickness?e:{...e,barThickness:t};return{barContainer:ay(o),barFill:ly(o),scaleBackground:cy(o),tickmarks:sy(o),labels:ny(o),adviceOverlays:fy(o),currentValueDot:py(o),setpoint:hy(o)}}var gy=Object.defineProperty,ye=(e,t,o,r)=>{for(var i=void 0,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=n(t,o,i)||i);return i&&gy(t,o,i),i};en.register(Kc,ts,o1,t1,s1,n1,on,rm,sm);var ln=(e=>(e.category="category",e.time="time",e.number="number",e))(ln||{}),Sp=(e=>(e.left="left",e.right="right",e))(Sp||{}),Mp=(e=>(e.smooth="smooth",e.straight="straight",e.stepped="stepped",e))(Mp||{}),$p=(e=>(e.minutes="minutes",e.date="date",e))($p||{});var my=["data","datasets","labels","colors","xAxisType","yAxisPosition","yAxes","xAxis","showGrid","showGridX","showGridY","showTickMarks","showPoints","lineMode","unit","timeDisplay","xTicksLimit","xStepSize","yTicksLimit","yStepSize","priority","borderRadiusPosition","borderRadiusPositionExternalScales","width","height","fixedAspectRatioScaling","hasLabelPadding","rangeLabels"],vy=["showDebugOverlay","width","height","fixedAspectRatioScaling","rangeLabels"],by=["width","height","fixedAspectRatioScaling"],Sm=class extends S{constructor(){super(...arguments),this.data=[],this.datasets=void 0,this.labels=void 0,this.colors=[],this.legend=!1,this.showDebugOverlay=!1,this.width=480,this.height=320,this.fixedAspectRatioScaling=!1,this.scaleReferenceSize=384,this.xAxisType="category",this.yAxisPosition="left",this.yAxes=void 0,this.xAxis=void 0,this.showGrid=!1,this.showGridX=!1,this.showGridY=!1,this.showTickMarks=!1,this.hasLabelPadding=!0,this.rangeLabels="none",this.warnedDateDisplayScale=!1,this.DEFAULT_TENSION=.4,this.POINT_RADIUS=3,this.showPoints=!1,this.lineMode="smooth",this.unit="",this.timeDisplay="date",this.xTicksLimit=void 0,this.xStepSize=void 0,this.yTicksLimit=void 0,this.yStepSize=void 0,this.state=to.active,this.priority=zt.regular,this.frameStyle=Mr.regular,this.borderRadiusPosition=void 0,this.borderRadiusPositionExternalScales=void 0,this.instrumentMode=!1,this.borderRadius=void 0,this.externalScaleDimensions=new Map,this.isUpdatingScales=!1,this.currentBorderRadiusPx=8,this.computedWidth=480,this.computedHeight=320,this.savedLabelThickness=new WeakMap,this.savedMainTickmarkLabels=new WeakMap,this.lastRangeLabels=[],this.rangeLabelCache={y:[],x:[]},this.updateBorderRadius=()=>{if(!this.canvasEl)return;let t;this.instrumentMode?t=this.borderRadius??8:t=sn(this.canvasEl,oo.regular,_p),this.currentBorderRadiusPx!==t&&(this.currentBorderRadiusPx=t,this.chart&&(this.chart.destroy(),this.createChart()))},this.handleSlotChange=()=>{this.externalScaleDimensions.clear(),this.waitForScaleDimensions()},this.handleScaleDimensionsChanged=t=>{if(this.isUpdatingScales)return;let o=t,{side:r,thickness:i}=o.detail;this.externalScaleDimensions.get(r)!==i&&(this.externalScaleDimensions.set(r,i),this.dimensionUpdateTimer&&clearTimeout(this.dimensionUpdateTimer),this.dimensionUpdateTimer=setTimeout(()=>{this.syncScalesAndChart()},16))}}get rangeLabelsY(){return this.hasLabelPadding&&(this.rangeLabels==="y"||this.rangeLabels==="xy")}get rangeLabelsX(){return this.hasLabelPadding&&(this.rangeLabels==="x"||this.rangeLabels==="xy")}get isNumericXAxis(){return this.xAxisType==="time"||this.xAxisType==="number"}get primaryYAxisId(){return this.yAxes?.length?this.yAxes[0].id??"y0":"y"}get xValueMode(){return this.xAxisType==="number"?rn.number:rn.time}warnOnInvalidX(t,o){let r=t.filter(i=>!Number.isFinite(i)).length;r===0||this.lastWarnedXSource===o||(this.lastWarnedXSource=o,console.warn(`[obc-chart] ${r} x value(s) could not be parsed for xAxisType='${this.xAxisType}'; the points render as gaps.`))}shouldApplyFill(){throw new Error("shouldApplyFill() must be implemented in subclass")}getFillMode(){throw new Error("getFillMode() must be implemented in subclass")}shouldStack(){throw new Error("shouldStack() must be implemented in subclass")}compactLabelThickness(t){let o=this.canvasEl?.getContext("2d");if(!o)return;let r=this.rangeLabelFont(),i;if(t==="y"){let n=this.rangeLabelCache.bounds;if(!n)return;let a=c1(n.min,n.max).map(String);i=d1(o,r,a,[]).side+4}else i=d1(o,r,[],["x"]).bottom+8;if(!this.fixedAspectRatioScaling)return Math.ceil(i);let s=t==="y"?this.getEffectiveHeight():this.getEffectiveWidth();return Math.ceil(i*this.scaleReferenceSize/s)}slotFor(t){return{left:this.leftScaleSlot,right:this.rightScaleSlot,top:this.topScaleSlot,bottom:this.bottomScaleSlot}[t]}hasSlottedScale(t){return(this.slotFor(t)?.assignedElements().length??0)>0}isBelowThreshold(){return this.getEffectiveWidth()<Rr.MIN_HEIGHT_WITH_LABELS||this.getEffectiveHeight()<Rr.MIN_HEIGHT_WITH_LABELS}get ySide(){return(this.yAxes?.[0]?.position??this.yAxisPosition)==="right"?"right":"left"}rangeLabelFont(){let t=Number.parseFloat(dt(this,Er.fontSizeVar));return{family:dt(this,Er.fontFamily),sizePx:Number.isFinite(t)?t:12,weight:dt(this,Er.fontWeightVar)}}dataExtents(t){let o={min:1/0,max:-1/0},r=new Map,i=(s,n)=>{Number.isFinite(n)&&(s.min=Math.min(s.min,n),s.max=Math.max(s.max,n))};return t.datasets.forEach(s=>{let n=s.yAxisID??this.primaryYAxisId,a=r.get(n)??{min:1/0,max:-1/0};r.set(n,a),s.data.forEach(l=>{typeof l=="number"?i(a,l):l&&(i(o,l.x),i(a,l.y))})}),r.forEach((s,n)=>{s.min<=s.max||r.delete(n)}),{x:o.min<=o.max?o:void 0,y:r}}yRangeBounds(t){let o,r="y";if(this.yAxes?.length){let l=this.yAxes.findIndex(d=>(d.position??"left")===this.ySide),c=l===-1?0:l;o=this.yAxes[c],r=o.id??`y${c}`}let i=t.get(r),s=this.shouldStack()?this.chart?.scales[r]:void 0,n=o?.min??s?.min??i?.min,a=o?.max??s?.max??i?.max;return n!==void 0&&a!==void 0?{min:n,max:a}:void 0}xEdgeLabelTexts(t,o){if(!this.isNumericXAxis){let n=t.labels.map(String),a=n[0],l=n[n.length-1];return n.length>1&&a!==l?[a,l]:[]}let r=this.xAxis?.min??o?.min,i=this.xAxis?.max??o?.max;if(r===void 0||i===void 0||r===i)return[];let s=this.timeDisplay==="minutes"?this.computeTimeReference():void 0;return[ba(r,this.xValueMode,s),ba(i,this.xValueMode,s)]}refreshRangeLabels(){let t={y:[],x:[]};if(this.isBelowThreshold()&&(this.rangeLabelsY||this.rangeLabelsX)){let o=this.prepareChartDataAndLabels(),r=this.dataExtents(o);if(this.rangeLabelsY&&(t.bounds=this.yRangeBounds(r.y),t.bounds&&!this.hasSlottedScale("left")&&!this.hasSlottedScale("right"))){let{min:i,max:s}=t.bounds;t.y=c1(i,s).map(n=>um(n,i,s))}this.rangeLabelsX&&!this.hasSlottedScale("top")&&!this.hasSlottedScale("bottom")&&(t.x=this.xEdgeLabelTexts(o,r.x))}return this.rangeLabelCache=t,t}createRangeLabelsPlugin(){return{id:"rangeLabels",afterDraw:t=>{this.lastRangeLabels=[];let{y:o,x:r,bounds:i}=this.rangeLabelCache;if(!o.length&&!r.length)return;let s=t.chartArea,n=t.ctx,a=this.rangeLabelFont(),l=bp(a);n.save(),n.font=vp(a),n.fillStyle=dt(this,Er.fontColorVar);let c=t.scales[this.primaryYAxisId];if(o.length&&i&&c){let d=this.ySide==="right",p=d?s.right+8:s.left-8;n.textAlign=d?"left":"right";let u=c1(i.min,i.max);for(let m=u.length-1;m>=0;m--){let b=m===u.length-1,C=m===0,y=b?s.top:C?s.bottom:c.getPixelForValue(u[m]);!b&&!C&&(y-s.top<l||s.bottom-y<l)||(n.textBaseline=b?"top":C?"bottom":"middle",n.fillText(o[m],p,y),this.lastRangeLabels.push({axis:"y",text:o[m],x:p,y}))}}if(r.length===2){let d=s.bottom+4;n.textBaseline="top",n.textAlign="left",n.fillText(r[0],s.left,d),this.lastRangeLabels.push({axis:"x",text:r[0],x:s.left,y:d}),n.textAlign="right",n.fillText(r[1],s.right,d),this.lastRangeLabels.push({axis:"x",text:r[1],x:s.right,y:d})}n.restore()}}}hasVisibleScale(t){return(this.slotFor(t)?.assignedElements()??[]).some(i=>{let s=i;return"hasBar"in s&&"hasScale"in s?s.hasBar===!0||s.hasScale===!0:!0})}computeRoundedCorners(){if(!this.borderRadiusPosition)return{topLeft:!1,topRight:!1,bottomLeft:!1,bottomRight:!1};if(this.borderRadiusPosition===Qe.middleChild)return{topLeft:!1,topRight:!1,bottomLeft:!1,bottomRight:!1};if(this.borderRadiusPosition===Qe.middleRoundedChild)return{topLeft:!0,topRight:!0,bottomLeft:!0,bottomRight:!0};let t=this.hasVisibleScale("left"),o=this.hasVisibleScale("right"),r=this.hasVisibleScale("top"),i=this.hasVisibleScale("bottom");if(t&&o||r&&i)return{topLeft:!1,topRight:!1,bottomLeft:!1,bottomRight:!1};let s={topLeft:!1,topRight:!1,bottomLeft:!1,bottomRight:!1},n=this.borderRadiusPosition===Qe.innerFirstChild,a=this.borderRadiusPosition===Qe.outerLastChild;return o&&i?n?s.bottomRight=!0:a&&(s.topLeft=!0):o&&r?n?s.topRight=!0:a&&(s.bottomLeft=!0):t&&i?n?s.bottomLeft=!0:a&&(s.topRight=!0):t&&r?n?s.topLeft=!0:a&&(s.bottomRight=!0):o&&!t?n?(s.topLeft=!0,s.bottomLeft=!0):a&&(s.topRight=!0,s.bottomRight=!0):t&&!o?n?(s.topRight=!0,s.bottomRight=!0):a&&(s.topLeft=!0,s.bottomLeft=!0):i&&!r?n?(s.topLeft=!0,s.topRight=!0):a&&(s.bottomLeft=!0,s.bottomRight=!0):r&&!i&&(n?(s.bottomLeft=!0,s.bottomRight=!0):a&&(s.topLeft=!0,s.topRight=!0)),s}createBorderPlugin(){let t=this.computeRoundedCorners(),o=this.currentBorderRadiusPx,r=!1,i=(s,n,a)=>{let{x:l,y:c,width:d,height:p}=n;if(d<=0||p<=0)return;let u=Math.max(0,Math.min(a,Math.min(d,p)/2));s.moveTo(l+(t.topLeft?u:0),c),s.lineTo(l+d-(t.topRight?u:0),c),t.topRight&&s.arcTo(l+d,c,l+d,c+u,u),s.lineTo(l+d,c+p-(t.bottomRight?u:0)),t.bottomRight&&s.arcTo(l+d,c+p,l+d-u,c+p,u),s.lineTo(l+(t.bottomLeft?u:0),c+p),t.bottomLeft&&s.arcTo(l,c+p,l,c+p-u,u),s.lineTo(l,c+(t.topLeft?u:0)),t.topLeft&&s.arcTo(l,c,l+u,c,u)};return{id:"chartAreaBorder",beforeDatasetsDraw:s=>{let n=s.ctx,a=s.chartArea;if(!a)return;let c=1,{top:d,right:p,bottom:u,left:m}=a,b={x:m+c,y:d+c,width:p-m-c*2,height:u-d-c*2},C=Math.max(0,o-c);if(n.save(),r=!0,n.beginPath(),i(n,b,C),n.closePath(),this.instrumentMode){let y=dt(this,am);n.fillStyle=y,n.fill()}n.clip()},afterDraw:s=>{let n=s.ctx,a=s.chartArea;if(!a)return;let l=1,c=l/2,{top:d,right:p,bottom:u,left:m}=a,b={x:m+c,y:d+c,width:p-m-c*2,height:u-d-c*2},C=Math.max(0,o-c),y=this.hasVisibleScale("top"),k=this.hasVisibleScale("right"),$=this.hasVisibleScale("bottom"),V=this.hasVisibleScale("left"),O=dt(this,"--instrument-frame-tertiary-color");n.save(),n.strokeStyle=O,n.lineWidth=l;let{x:P,y:T,width:Z,height:R}=b,D=Math.max(0,Math.min(C,Math.min(Z,R)/2));!y&&!k&&!$&&!V?(n.beginPath(),i(n,b,C),n.closePath(),n.stroke()):(y||(n.beginPath(),!V&&t.topLeft?n.moveTo(P+D,T):n.moveTo(P,T),!k&&t.topRight?n.lineTo(P+Z-D,T):n.lineTo(P+Z,T),n.stroke()),k||(n.beginPath(),!y&&t.topRight?n.moveTo(P+Z,T+D):n.moveTo(P+Z,T),!$&&t.bottomRight?n.lineTo(P+Z,T+R-D):n.lineTo(P+Z,T+R),n.stroke()),$||(n.beginPath(),!k&&t.bottomRight?n.moveTo(P+Z-D,T+R):n.moveTo(P+Z,T+R),!V&&t.bottomLeft?n.lineTo(P+D,T+R):n.lineTo(P,T+R),n.stroke()),V||(n.beginPath(),!$&&t.bottomLeft?n.moveTo(P,T+R-D):n.moveTo(P,T+R),!y&&t.topLeft?n.lineTo(P,T+D):n.lineTo(P,T),n.stroke()),!y&&!V&&t.topLeft&&(n.beginPath(),n.arc(P+D,T+D,D,Math.PI,Math.PI*1.5),n.stroke()),!y&&!k&&t.topRight&&(n.beginPath(),n.arc(P+Z-D,T+D,D,Math.PI*1.5,Math.PI*2),n.stroke()),!k&&!$&&t.bottomRight&&(n.beginPath(),n.arc(P+Z-D,T+R-D,D,0,Math.PI*.5),n.stroke()),!$&&!V&&t.bottomLeft&&(n.beginPath(),n.arc(P+D,T+R-D,D,Math.PI*.5,Math.PI),n.stroke())),n.restore(),this.showPoints&&(n.save(),s.data.datasets.forEach((N,B)=>{let Y=s.getDatasetMeta(B);!Y||Y.hidden||(Y.data??[]).forEach(I=>{let H=I;if(H.skip)return;let W=H.options?.radius;typeof W=="number"&&W<=0||H.draw(n)})}),n.restore())},afterDatasetsDraw:s=>{r&&(s.ctx.restore(),r=!1)}}}hasExternalScales(){let t=this.topScaleSlot?.assignedElements()??[],o=this.bottomScaleSlot?.assignedElements()??[],r=this.leftScaleSlot?.assignedElements()??[],i=this.rightScaleSlot?.assignedElements()??[];return t.length>0||o.length>0||r.length>0||i.length>0}async waitForScaleDimensions(){if(!this.hasExternalScales()){this.requestUpdate();return}let t=[];[this.topScaleSlot,this.bottomScaleSlot,this.leftScaleSlot,this.rightScaleSlot].forEach(r=>{if(r){let i=r.assignedElements();t.push(...i)}});let o=r=>{if(!r)return;r.assignedElements().forEach(s=>{s.fixedAspectRatio=this.fixedAspectRatioScaling,s.scaleReferenceSize=this.scaleReferenceSize})};o(this.leftScaleSlot),o(this.rightScaleSlot),o(this.topScaleSlot),o(this.bottomScaleSlot),await Promise.all(t.map(r=>"updateComplete"in r&&typeof r.updateComplete=="object"?r.updateComplete:Promise.resolve())),this.externalScaleDimensions.size===0&&t.length>0&&await new Promise(r=>setTimeout(r,50)),this.syncScalesAndChart()}syncScalesAndChart(){if(this.isUpdatingScales)return!1;this.isUpdatingScales=!0;try{let t=this.computeChartPadding(),o=this.getEffectiveWidth()-t.left-t.right,r=this.getEffectiveHeight()-t.top-t.bottom;return o<=0||r<=0?(console.warn("[chart-line-base] Invalid effective dimensions",{width:this.getEffectiveWidth(),height:this.getEffectiveHeight(),padding:t,effectiveWidth:o,effectiveHeight:r}),!1):(this.updateScaleProperties(t),this.chart&&this.chart.destroy(),this.createChart(),!0)}finally{this.isUpdatingScales=!1}}calculatePaddingFromScales(){let t=this.hasLabelPadding?Xo.CANVAS_PADDING:0;return{top:this.externalScaleDimensions.get("top")??t,right:this.externalScaleDimensions.get("right")??t,bottom:this.externalScaleDimensions.get("bottom")??t,left:this.externalScaleDimensions.get("left")??t}}resolveAxisRange(t){let o=t==="x"?"x":"y",r;if(t==="x")r=this.isNumericXAxis?this.xAxis:void 0;else if(this.yAxes?.length){let s=this.yAxes.findIndex(l=>(l.position??"left")===t),n=s===-1?0:s,a=this.yAxes[n];o=a.id??`y${n}`,r=a}if(r?.min!==void 0&&r.max!==void 0)return{min:r.min,max:r.max};let i=this.chart?.scales[o];return{min:i?.min??r?.min??0,max:i?.max??r?.max??100}}resolveSlottedXRange(){let t=this.resolveAxisRange("x");if(this.xAxisType!=="time")return t;if(this.timeDisplay!=="minutes"){this.warnedDateDisplayScale||(this.warnedDateDisplayScale=!0,console.warn("[obc-chart] a slotted horizontal scale cannot label a time axis in 'date' display and keeps its own range; use timeDisplay='minutes' or a number axis."));return}let o=this.xAxis?.min!==void 0&&this.xAxis?.max!==void 0,r=this.computeTimeReference();if(r===void 0||!this.chart&&!o)return;let i=6e4;return{min:(t.min-r)/i,max:(t.max-r)/i}}updateScaleProperties(t){let o=this.resolveAxisRange("left"),r=this.resolveAxisRange("right"),i=this.resolveSlottedXRange(),s=this.getEffectiveWidth(),n=this.getEffectiveHeight(),a=s>=Rr.MIN_HEIGHT_WITH_LABELS&&n>=Rr.MIN_HEIGHT_WITH_LABELS,l=this.hasLabelPadding&&a,c=!a&&this.rangeLabelsY,d=!a&&this.rangeLabelsX,p=c?this.compactLabelThickness("y"):void 0,u=d?this.compactLabelThickness("x"):void 0,m=(V,O)=>{if(O)return this.savedMainTickmarkLabels.has(V)||this.savedMainTickmarkLabels.set(V,V.showMainTickmarkLabels??!1),!0;if(!this.savedMainTickmarkLabels.has(V))return;let P=this.savedMainTickmarkLabels.get(V);return this.savedMainTickmarkLabels.delete(V),P},b=(V,O,P)=>{if(O)return P===void 0||typeof V.labelThickness!="number"?void 0:(this.savedLabelThickness.has(V)||this.savedLabelThickness.set(V,V.labelThickness),P);let T=this.savedLabelThickness.get(V);return this.savedLabelThickness.delete(V),T},C=this.fixedAspectRatioScaling?{top:Math.round(t.top*this.scaleReferenceSize/n),bottom:Math.round(t.bottom*this.scaleReferenceSize/n)}:{top:t.top,bottom:t.bottom},y=this.fixedAspectRatioScaling?{left:Math.round(t.left*this.scaleReferenceSize/s),right:Math.round(t.right*this.scaleReferenceSize/s)}:{left:t.left,right:t.right},k=[],$=(V,O)=>this.ownsSlottedScaleRange(V)?{minValue:O.min,maxValue:O.max}:{};this.leftScaleSlot&&this.leftScaleSlot.assignedElements().forEach(O=>{let P={...$("left",o),height:n,paddingTop:C.top,paddingBottom:C.bottom,paddingStart:C.top,paddingEnd:C.bottom,showLabels:l||c,fixedAspectRatio:this.fixedAspectRatioScaling,scaleReferenceSize:this.scaleReferenceSize,state:this.state,priority:this.priority,frameStyle:this.frameStyle,borderRadiusPosition:this.borderRadiusPositionExternalScales};this.yStepSize!==void 0&&(P.primaryTickmarkInterval=this.yStepSize);let T=b(O,c,p),Z=m(O,c);Z!==void 0&&(P.showMainTickmarkLabels=Z),T!==void 0&&(P.labelThickness=T),k.push([this.leftScaleSlot,O,P])}),this.rightScaleSlot&&this.rightScaleSlot.assignedElements().forEach(O=>{let P={...$("right",r),height:n,paddingTop:C.top,paddingBottom:C.bottom,paddingStart:C.top,paddingEnd:C.bottom,showLabels:l||c,fixedAspectRatio:this.fixedAspectRatioScaling,scaleReferenceSize:this.scaleReferenceSize,state:this.state,priority:this.priority,frameStyle:this.frameStyle,borderRadiusPosition:this.borderRadiusPositionExternalScales};this.yStepSize!==void 0&&(P.primaryTickmarkInterval=this.yStepSize);let T=b(O,c,p),Z=m(O,c);Z!==void 0&&(P.showMainTickmarkLabels=Z),T!==void 0&&(P.labelThickness=T),k.push([this.rightScaleSlot,O,P])}),this.topScaleSlot&&this.topScaleSlot.assignedElements().forEach(O=>{let P={...i,width:s,paddingLeft:y.left,paddingRight:y.right,paddingStart:y.left,paddingEnd:y.right,showLabels:l||d,fixedAspectRatio:this.fixedAspectRatioScaling,scaleReferenceSize:this.scaleReferenceSize,state:this.state,priority:this.priority,frameStyle:this.frameStyle,borderRadiusPosition:this.borderRadiusPositionExternalScales};this.xStepSize!==void 0&&(P.primaryTickmarkInterval=this.xStepSize);let T=b(O,d,u),Z=m(O,d);Z!==void 0&&(P.showMainTickmarkLabels=Z),T!==void 0&&(P.labelThickness=T),k.push([this.topScaleSlot,O,P])}),this.bottomScaleSlot&&this.bottomScaleSlot.assignedElements().forEach(O=>{let P={...i,width:s,paddingLeft:y.left,paddingRight:y.right,paddingStart:y.left,paddingEnd:y.right,showLabels:l||d,fixedAspectRatio:this.fixedAspectRatioScaling,scaleReferenceSize:this.scaleReferenceSize,state:this.state,priority:this.priority,frameStyle:this.frameStyle,borderRadiusPosition:this.borderRadiusPositionExternalScales};this.xStepSize!==void 0&&(P.primaryTickmarkInterval=this.xStepSize);let T=b(O,d,u),Z=m(O,d);Z!==void 0&&(P.showMainTickmarkLabels=Z),T!==void 0&&(P.labelThickness=T),k.push([this.bottomScaleSlot,O,P])}),k.forEach(([V,O,P])=>{Object.assign(O,P)})}ownsSlottedScaleRange(t){return!0}syncSlottedScaleRanges(){let t=(r,i,s)=>{!i||!s||!this.ownsSlottedScaleRange(r)||i.assignedElements().forEach(n=>{n.minValue=s.min,n.maxValue=s.max})};t("left",this.leftScaleSlot,this.resolveAxisRange("left")),t("right",this.rightScaleSlot,this.resolveAxisRange("right"));let o=this.resolveSlottedXRange();t("top",this.topScaleSlot,o),t("bottom",this.bottomScaleSlot,o)}hasAnyChanged(t,o){return o.some(r=>t.has(r))}applyFillModes(){if(!this.chart||!this.canvasEl||!this.canvasEl.isConnected)return;let t=this.chart,o=t.ctx;if(!o)return;let r=this.shouldApplyFill();this.getFillMode()!=="threshold"||!r||t.data.datasets.forEach((s,n)=>{let a=s;if(a.fill===!1||!r)return;let l=a.yAxisID??"y",c=t.scales[l];if(!c)return;let d=a.data.map(T=>typeof T=="number"?T:T.y).filter(T=>Number.isFinite(T));if(d.length===0)return;let p=Math.min(...d),u=Math.max(...d),m=(p+u)/2,b=c.getPixelForValue(m),C=c.bottom-c.top,y=(b-c.top)/C;!Number.isFinite(y)||C===0?y=.5:y=Math.max(0,Math.min(1,y));let k=pi.thresholdLowColorVar,$=pi.thresholdHighColorVar,V=(T,Z)=>{let R=rs(this,k,T),D=rs(this,$,Z),N=o.createLinearGradient(0,c.top,0,c.bottom);return N.addColorStop(0,D),N.addColorStop(y,D),N.addColorStop(y,R),N.addColorStop(1,R),N},O=V(.35,.35),P=V(.8,.8);a.backgroundColor=O,a.borderColor=P})}updated(t){if(super.updated(t),!this.hasAnyChanged(t,my)||this.hasAnyChanged(t,by)&&this.updateComputedDimensions())return;let o=this.isBelowThreshold(),r=this.wasBelowThreshold!==void 0&&this.wasBelowThreshold!==o;if(this.wasBelowThreshold=o,(t.has("hasLabelPadding")||t.has("rangeLabels")||r)&&this.hasExternalScales()){this.syncScalesAndChart();return}this.hasAnyChanged(t,vy)?(this.chart?.destroy(),this.createChart()):this.updateChart()}async firstUpdated(){await this.waitForScaleDimensions(),this.hasExternalScales()||this.createChart(),this.themeObserver=lm(()=>{this.updateChartColors(),this.updateBorderRadius()}),this.setupResizeObserver(),this.setupAspectRatioResizeObserver(),this.canvasEl&&(this.instrumentMode||(this.borderRadiusObserver=nn(this.canvasEl,this.updateBorderRadius)),this.updateBorderRadius())}disconnectedCallback(){super.disconnectedCallback(),this.chart?.destroy(),this.themeObserver?.disconnect(),this.resizeObserver?.disconnect(),this.aspectRatioResizeObserver?.disconnect(),this.borderRadiusObserver?.disconnect(),this.dimensionUpdateTimer&&clearTimeout(this.dimensionUpdateTimer)}setupResizeObserver(){this.canvasEl&&(this.resizeObserver=pm(this.canvasEl,()=>(this.canvasEl?.clientHeight??0)>=Rr.MIN_HEIGHT_WITH_LABELS&&(this.canvasEl?.clientWidth??0)>=Rr.MIN_HEIGHT_WITH_LABELS,{rebuild:()=>{this.chart?.destroy(),this.createChart()},update:()=>this.updateChart()}))}setupAspectRatioResizeObserver(){let t=this.renderRoot.querySelector(".wrapper");t&&(this.updateComputedDimensions(),this.aspectRatioResizeObserver=new ResizeObserver(()=>{this.fixedAspectRatioScaling&&this.updateComputedDimensions()}),this.aspectRatioResizeObserver.observe(t))}updateComputedDimensions(){if(!this.fixedAspectRatioScaling)return this.computedWidth=this.width,this.computedHeight=this.height,!1;let t=this.renderRoot.querySelector(".wrapper");if(!t)return!1;let o=t.clientWidth;if(o<=0)return!1;let r=this.width/this.height,i=o,s=Math.round(o/r);if(this.computedWidth!==i||this.computedHeight!==s){if(this.computedWidth=i,this.computedHeight=s,this.hasExternalScales())return this.syncScalesAndChart();if(this.chart)return this.chart.destroy(),this.createChart(),!0}return!1}getEffectiveWidth(){return this.fixedAspectRatioScaling?this.computedWidth:this.width}getEffectiveHeight(){return this.fixedAspectRatioScaling?this.computedHeight:this.height}getScaleFactor(){return this.fixedAspectRatioScaling?this.computedWidth/this.width:1}buildDataset(t,o,r,i=1){let s=r[o%r.length],n=Array.isArray(t)?null:t,a=Array.isArray(t)?t:null,l=n?.borderColor??s,c=n?.fill??this.shouldApplyFill(),d=this.lineMode==="smooth"?this.DEFAULT_TENSION:0,u=this.shouldStack()&&this.getFillMode()!=="threshold"&&o<i-1,m="transparent",b=this.getFillMode();if(c&&b){let y=r[(o+1)%r.length];b==="solid"?m=String(l):b==="semitransparent"?m=rs(this,y,.5):b==="threshold"&&(m=rs(this,y,.5))}return{...n||{},data:n?.data??a,yAxisID:n?.yAxisID??this.primaryYAxisId,borderColor:l,backgroundColor:m,borderWidth:n?.borderWidth??2,showLine:n?.showLine??!0,tension:n?.tension??d,pointRadius:n?.pointRadius??(this.showPoints?this.POINT_RADIUS:0),pointBackgroundColor:n?.pointBackgroundColor??"#fff",pointBorderColor:n?.pointBorderColor??l,pointBorderWidth:n?.pointBorderWidth??2,stepped:n?.stepped??this.lineMode==="stepped",fill:c?"start":!1,spanGaps:n?.spanGaps??!0,...u&&{segment:{borderColor:dt(this,pi.stackedDividerColorVar),borderWidth:1}}}}createThresholdDatasets(t,o){let r=t.map(b=>typeof b=="number"?b:b.y).filter(b=>Number.isFinite(b)),i=r.length?Math.min(...r):0,s=r.length?Math.max(...r):100,n=(i+s)/2,a=t.map(b=>typeof b=="number"?n:{x:b.x,y:n}),l=pi.thresholdLowColorVar,c=pi.thresholdHighColorVar,d=rs(this,c,.35),p=rs(this,l,.35),u={label:"threshold-baseline",data:a,yAxisID:this.primaryYAxisId,borderColor:"transparent",backgroundColor:"transparent",borderWidth:0,pointRadius:0,showLine:!1,fill:!1,spanGaps:!0},m=this.buildDataset(t,0,o);return m.fill={target:0,above:d,below:p},m.borderWidth=2,[u,m]}prepareMultiSeriesDatasets(){let t=this.priority===zt.enhanced?gp:fp,o=mp(this,this.colors,t),r=this.datasets.map(s=>this.normalizeDatasetX(s));this.isNumericXAxis&&this.warnOnInvalidX(r.flatMap(s=>(s.data??[]).map(n=>n&&typeof n=="object"?n.x:0)),this.datasets);let i=this.datasets.length;return r.map((s,n)=>this.buildDataset(s,n,o,i))}normalizeDatasetX(t){if(!this.isNumericXAxis||!t.data)return t;let o=t.data.map(r=>r&&typeof r=="object"&&"x"in r?{...r,x:va(r.x,this.xValueMode)}:r);return{...t,data:o}}prepareSingleSeriesDatasets(){let t=this.priority===zt.enhanced?gp:fp,o=mp(this,this.colors,t),r=this.shouldApplyFill(),i=this.getFillMode();if(this.isNumericXAxis){let l=this.data.map(d=>({x:va(d.x??d.label??NaN,this.xValueMode),y:d.value}));return this.warnOnInvalidX(l.map(d=>d.x),this.data),{datasets:r&&i==="threshold"?this.createThresholdDatasets(l,o):[this.buildDataset(l,0,o)],labels:[]}}let s=this.data.map(l=>l.value),n=this.data.map(l=>l.label??String(l.x??""));return{datasets:r&&i==="threshold"?this.createThresholdDatasets(s,o):[this.buildDataset(s,0,o)],labels:n}}computeChartPadding(){let t=this.isBelowThreshold(),o=this.getScaleFactor(),r=this.hasLabelPadding?this.fixedAspectRatioScaling?Math.round(Xo.CANVAS_PADDING*o):Xo.CANVAS_PADDING:0,{y:i,x:s}=this.refreshRangeLabels(),n=this.canvasEl?.getContext("2d"),a=(i.length||s.length)&&n?d1(n,this.rangeLabelFont(),i,s):{side:0,bottom:0},l=this.calculatePaddingFromScales(),c=p=>t?p==="bottom"?a.bottom:p===this.ySide?a.side:0:r;return{top:this.externalScaleDimensions.has("top")?l.top:c("top"),right:this.externalScaleDimensions.has("right")?l.right:c("right"),bottom:this.externalScaleDimensions.has("bottom")?l.bottom:c("bottom"),left:this.externalScaleDimensions.has("left")?l.left:c("left")}}getChartOptions(){let t=this.getEffectiveWidth(),o=this.getEffectiveHeight(),r=t<Rr.MIN_HEIGHT_WITH_LABELS||o<Rr.MIN_HEIGHT_WITH_LABELS,i=this.computeChartPadding();this.fixedAspectRatioScaling?(this.style.setProperty("--chart-width","100%"),this.style.setProperty("--chart-height",`${o}px`)):(this.style.setProperty("--chart-width",`${this.width}px`),this.style.setProperty("--chart-height",`${this.height}px`));let s=this.computeTimeReference(),n=this.hasExternalScales()?!1:this.showTickMarks;return{responsive:!0,maintainAspectRatio:!1,layout:{padding:i},plugins:{legend:{display:!1,labels:{generateLabels:()=>[]},onClick:()=>{}},tooltip:{...dm(this),enabled:!r,callbacks:{title:()=>"",label:a=>{let l=typeof a.parsed=="object"&&a.parsed!==null?a.parsed.y:a.parsed,c=cm(l,1,!1,0),d=this.unit?`${this.unit}`:"",p=a.label??"";if(this.isNumericXAxis){let u=typeof a.parsed=="object"&&a.parsed!==null?a.parsed.x:NaN,m=this.timeDisplay==="minutes"?s:void 0;p=ba(u,this.xValueMode,m)}return`${p} ${c}${d}`}}}},animation:!1,scales:this.buildScalesConfig(s,r,n)}}computeTimeReference(){if(this.xAxisType!=="time")return;let t=this.timeDisplay==="minutes"?this.xAxis?.max:this.xAxis?.min;if(t!==void 0&&Number.isFinite(t))return t;let o=[];return this.datasets?.length?this.datasets.forEach(r=>{r.data&&r.data.forEach(i=>{if(i&&typeof i=="object"&&"x"in i){let s=va(i.x,rn.time);Number.isFinite(s)&&o.push(s)}})}):this.data?.length&&this.data.forEach(r=>{let i=va(r.x??r.label??NaN,rn.time);Number.isFinite(i)&&o.push(i)}),!o.length&&this.labels?.length&&this.labels.forEach(r=>{if(typeof r=="string"){let i=new Date(r).getTime();Number.isFinite(i)&&o.push(i)}}),o.length?this.timeDisplay==="minutes"?Math.max(...o):Math.min(...o):void 0}buildScalesConfig(t,o=!1,r=!0){let i=dt(this,pi.gridColorVar),s=dt(this,pi.tickColorVar),n=dt(this,Er.fontFamily),a=dt(this,Er.fontSizeVar),l=dt(this,Er.fontWeightVar),c=dt(this,Er.fontColorVar),d=r&&!o&&this.hasLabelPadding,p=r&&!o&&this.hasLabelPadding,u={family:n,size:a,weight:l},m={type:this.xAxisType==="category"?"category":"linear",offset:!1,grace:0,bounds:"data",min:this.isNumericXAxis?this.xAxis?.min:void 0,max:this.isNumericXAxis?this.xAxis?.max:void 0,grid:{display:this.showGrid&&this.showGridX,color:i,offset:!1,drawTicks:p},ticks:{display:d,color:c,font:u,maxRotation:0,minRotation:0,maxTicksLimit:this.xTicksLimit,stepSize:this.xStepSize,callback:y=>{if(!this.isNumericXAxis)return String(y);let k=Number(y);if(!Number.isFinite(k))return String(y);let $=this.timeDisplay==="minutes"?t:void 0;return ba(k,this.xValueMode,$)}},border:{display:d,color:s}},b=this.yAxes?.length?this.yAxes.map((y,k)=>({id:y.id??`y${k}`,position:y.position??"left",min:y.min,max:y.max,gridDisplay:y.grid??(this.showGrid&&this.showGridY)})):[{id:"y",position:this.yAxisPosition,min:void 0,max:void 0,gridDisplay:this.showGrid&&this.showGridY}],C={x:m};return b.forEach(({id:y,position:k,min:$,max:V,gridDisplay:O})=>{C[y]={type:"linear",display:!0,position:k,stacked:this.shouldStack()&&this.getFillMode()!=="threshold",grace:o?0:void 0,bounds:o?"data":"ticks",grid:{display:O,color:i,drawTicks:p},ticks:{display:d,color:c,font:u,maxTicksLimit:this.yTicksLimit,stepSize:this.yStepSize},border:{display:d,color:s},min:$,max:V}}),C}prepareChartDataAndLabels(){return this.datasets?.length?{datasets:this.prepareMultiSeriesDatasets(),labels:this.labels??[]}:this.prepareSingleSeriesDatasets()}createChart(){if(!this.canvasEl||!this.canvasEl.isConnected)return;let t=this.canvasEl.getContext("2d");if(!t)return;this.chart&&(this.chart.destroy(),this.chart=void 0);let{datasets:o,labels:r}=this.prepareChartDataAndLabels();this.chart=new en(t,{type:"line",data:{labels:r,datasets:o},options:this.getChartOptions(),plugins:[...this.borderRadiusPosition?[this.createBorderPlugin()]:[],...this.rangeLabels!=="none"?[this.createRangeLabelsPlugin()]:[]]}),requestAnimationFrame(()=>this.updateLegend()),this.applyFillModes(),this.syncSlottedScaleRanges()}updateChart(){if(!this.chart||!this.canvasEl||!this.canvasEl.isConnected)return;let{datasets:t,labels:o}=this.prepareChartDataAndLabels();this.chart.data.labels=o,this.chart.data.datasets=t,Object.assign(this.chart.options,this.getChartOptions()),this.applyFillModes(),this.chart.update(),this.syncSlottedScaleRanges(),requestAnimationFrame(()=>this.updateLegend())}updateChartColors(){!this.chart||!this.canvasEl||!this.canvasEl.isConnected||(this.applyFillModes(),this.chart.update("none"),requestAnimationFrame(()=>this.updateLegend()))}updateLegend(){if(!(!this.legend||!this.legendDiv||!this.chart)){if(!this.chart.data.datasets||this.chart.data.datasets.length===0){this.legendDiv.innerHTML="";return}try{let t=this.chart.data.datasets.map((o,r)=>{let i=this.chart.getDatasetMeta(r);if(!i||!i.controller)return null;let s=i.controller.getStyle(0,!1),n=o;return{fillStyle:n.borderColor??s.borderColor??"",label:n.label||`Series ${r+1}`,value:"",unit:""}}).filter(o=>o!==null);if(t.length>0){let o=hm(t);this.legendDiv.innerHTML=o}}catch(t){console.debug("[chart-line-base] updateLegend: error generating legend HTML",t)}}}render(){return f`
      <div class="wrapper">
        <div class="canvas-and-slots-container">
          <slot
            name="top-scale"
            @slotchange=${this.handleSlotChange}
            @scale-dimensions-changed=${this.handleScaleDimensionsChanged}
          ></slot>
          <slot
            name="bottom-scale"
            @slotchange=${this.handleSlotChange}
            @scale-dimensions-changed=${this.handleScaleDimensionsChanged}
          ></slot>
          <slot
            name="left-scale"
            @slotchange=${this.handleSlotChange}
            @scale-dimensions-changed=${this.handleScaleDimensionsChanged}
          ></slot>
          <slot
            name="right-scale"
            @slotchange=${this.handleSlotChange}
            @scale-dimensions-changed=${this.handleScaleDimensionsChanged}
          ></slot>
          <canvas></canvas>
        </div>

        ${this.legend?f`<div class="legend"></div>`:""}
      </div>
    `}};Sm.styles=[ne(U0),ne(G0),ne(q0),ne(Y0)];var be=Sm;ye([h({type:Array,attribute:!1})],be.prototype,"data");ye([h({type:Array,attribute:!1})],be.prototype,"datasets");ye([h({type:Array,attribute:!1})],be.prototype,"labels");ye([h({type:Array,attribute:!1})],be.prototype,"colors");ye([h({type:Boolean,reflect:!0})],be.prototype,"legend");ye([h({type:Boolean,reflect:!0})],be.prototype,"showDebugOverlay");ye([h({type:Number,reflect:!0})],be.prototype,"width");ye([h({type:Number,reflect:!0})],be.prototype,"height");ye([h({type:Boolean,reflect:!0})],be.prototype,"fixedAspectRatioScaling");ye([h({type:Number})],be.prototype,"scaleReferenceSize");ye([h({type:String})],be.prototype,"xAxisType");ye([h({type:String})],be.prototype,"yAxisPosition");ye([h({type:Array,attribute:!1})],be.prototype,"yAxes");ye([h({type:Object,attribute:!1})],be.prototype,"xAxis");ye([h({type:Boolean})],be.prototype,"showGrid");ye([h({type:Boolean})],be.prototype,"showGridX");ye([h({type:Boolean})],be.prototype,"showGridY");ye([h({type:Boolean})],be.prototype,"showTickMarks");ye([h({type:Boolean,attribute:!1})],be.prototype,"hasLabelPadding");ye([h({type:String})],be.prototype,"rangeLabels");ye([h({type:Boolean})],be.prototype,"showPoints");ye([h({type:String})],be.prototype,"lineMode");ye([h({type:String})],be.prototype,"unit");ye([h({type:String})],be.prototype,"timeDisplay");ye([h({type:Number})],be.prototype,"xTicksLimit");ye([h({type:Number})],be.prototype,"xStepSize");ye([h({type:Number})],be.prototype,"yTicksLimit");ye([h({type:Number})],be.prototype,"yStepSize");ye([h({type:String})],be.prototype,"state");ye([h({type:String})],be.prototype,"priority");ye([h({type:String})],be.prototype,"frameStyle");ye([h({type:String})],be.prototype,"borderRadiusPosition");ye([h({type:String})],be.prototype,"borderRadiusPositionExternalScales");ye([h({type:Boolean})],be.prototype,"instrumentMode");ye([h({type:Number})],be.prototype,"borderRadius");ye([at("canvas")],be.prototype,"canvasEl");ye([at(".legend")],be.prototype,"legendDiv");ye([at('slot[name="top-scale"]')],be.prototype,"topScaleSlot");ye([at('slot[name="bottom-scale"]')],be.prototype,"bottomScaleSlot");ye([at('slot[name="left-scale"]')],be.prototype,"leftScaleSlot");ye([at('slot[name="right-scale"]')],be.prototype,"rightScaleSlot");var{I:wy}=d2,Mm=e=>e;var Am=e=>e.strings===void 0,$m=()=>document.createComment(""),cn=(e,t,o)=>{let r=e._$AA.parentNode,i=t===void 0?e._$AB:t._$AA;if(o===void 0){let s=r.insertBefore($m(),i),n=r.insertBefore($m(),i);o=new wy(s,n,e,e.options)}else{let s=o._$AB.nextSibling,n=o._$AM,a=n!==e;if(a){let l;o._$AQ?.(e),o._$AM=e,o._$AP!==void 0&&(l=e._$AU)!==n._$AU&&o._$AP(l)}if(s!==i||a){let l=o._$AA;for(;l!==s;){let c=Mm(l).nextSibling;Mm(r).insertBefore(l,i),l=c}}}return o},gi=(e,t,o=e)=>(e._$AI(t,o),e),yy={},Pm=(e,t=yy)=>e._$AH=t,Om=e=>e._$AH,v1=e=>{e._$AR(),e._$AA.remove()};var Ma=(e,t)=>{let o=e._$AN;if(o===void 0)return!1;for(let r of o)r._$AO?.(t,!1),Ma(r,t);return!0},b1=e=>{let t,o;do{if((t=e._$AM)===void 0)break;o=t._$AN,o.delete(e),e=t}while(o?.size===0)},Vm=e=>{for(let t;t=e._$AM;e=t){let o=t._$AN;if(o===void 0)t._$AN=o=new Set;else if(o.has(e))break;o.add(e),_y(t)}};function Cy(e){this._$AN!==void 0?(b1(this),this._$AM=e,Vm(this)):this._$AM=e}function xy(e,t=!1,o=0){let r=this._$AH,i=this._$AN;if(i!==void 0&&i.size!==0)if(t)if(Array.isArray(r))for(let s=o;s<r.length;s++)Ma(r[s],!1),b1(r[s]);else r!=null&&(Ma(r,!1),b1(r));else Ma(this,e)}var _y=e=>{e.type==Bs.CHILD&&(e._$AP??=xy,e._$AQ??=Cy)},w1=class extends Qr{constructor(){super(...arguments),this._$AN=void 0}_$AT(t,o,r){super._$AT(t,o,r),Vm(this),this.isConnected=t._$AU}_$AO(t,o=!0){t!==this.isConnected&&(this.isConnected=t,t?this.reconnected?.():this.disconnected?.()),o&&(Ma(this,t),b1(this))}setValue(t){if(Am(this._$Ct))this._$Ct._$AI(t,this);else{let o=[...this._$Ct._$AH];o[this._$Ci]=t,this._$Ct._$AI(o,this,0)}}disconnected(){}reconnected(){}};var mi=class{constructor(t,{target:o,config:r,callback:i,skipInitial:s}){this.t=new Set,this.o=!1,this.i=!1,this.h=t,o!==null&&this.t.add(o??t),this.l=r,this.o=s??this.o,this.callback=i,window.ResizeObserver?(this.u=new ResizeObserver(n=>{this.handleChanges(n),this.h.requestUpdate()}),t.addController(this)):console.warn("ResizeController error: browser does not support ResizeObserver.")}handleChanges(t){this.value=this.callback?.(t,this.u)}hostConnected(){for(let t of this.t)this.observe(t)}hostDisconnected(){this.disconnect()}async hostUpdated(){!this.o&&this.i&&this.handleChanges([]),this.i=!1}observe(t){this.t.add(t),this.u.observe(t,this.l),this.i=!0,this.h.requestUpdate()}unobserve(t){this.t.delete(t),this.u.unobserve(t)}disconnect(){this.u.disconnect()}target(t){return Ly(this,t)}},Ly=Ii(class extends w1{constructor(){super(...arguments),this.observing=!1}render(e,t){}update(e,[t,o]){this.controller=t,this.part=e,this.observe=o,o===!1?(t.unobserve(e.element),this.observing=!1):this.observing===!1&&(t.observe(e.element),this.observing=!0)}disconnected(){this.controller?.unobserve(this.part.element),this.observing=!1}reconnected(){this.observe!==!1&&this.observing===!1&&(this.controller?.observe(this.part.element),this.observing=!0)}});var Sy=Object.defineProperty,hr=(e,t,o,r)=>{for(var i=void 0,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=n(t,o,i)||i);return i&&Sy(t,o,i),i};function vi(e,t){let{defaultDeadband:o=2,defaultZeroDeadband:r=.5,angularWraparound:i=!1}=t??{};class s extends e{constructor(){super(...arguments),this.atSetpoint=!1,this.touching=!1,this.autoAtSetpoint=!0,this.autoAtSetpointDeadband=o,this.setpointAtZeroDeadband=r,this.setpointOverride=!1,this.animateSetpoint=!1}get departingNewSetpoint(){return this._departingNewSetpoint}setpointPresenceChanged(a){return a.has("setpoint")||a.has("newSetpoint")||a.has("_departingNewSetpoint")}computeAtSetpoint(a){return Ql({value:a,setpoint:this.setpoint,touching:this.touching,auto:this.autoAtSetpoint,deadband:this.autoAtSetpointDeadband,atSetpointManual:this.atSetpoint,angularWraparound:i})}willUpdate(a){if(super.willUpdate(a),a.has("newSetpoint")&&this.animateSetpoint){let l=a.get("newSetpoint");if(l!==void 0&&this.newSetpoint===void 0){this._departingNewSetpoint=l,clearTimeout(this._animationTimer);let c=S0(this);this._animationTimer=setTimeout(()=>{this._departingNewSetpoint=void 0},c)}}}disconnectedCallback(){super.disconnectedCallback(),clearTimeout(this._animationTimer)}}return hr([h({type:Number})],s.prototype,"setpoint"),hr([h({type:Number})],s.prototype,"newSetpoint"),hr([h({type:Boolean,attribute:!1})],s.prototype,"atSetpoint"),hr([h({type:Boolean})],s.prototype,"touching"),hr([h({type:Boolean,attribute:!1})],s.prototype,"autoAtSetpoint"),hr([h({type:Number})],s.prototype,"autoAtSetpointDeadband"),hr([h({type:Number})],s.prototype,"setpointAtZeroDeadband"),hr([h({type:Boolean})],s.prototype,"setpointOverride"),hr([h({type:Boolean})],s.prototype,"animateSetpoint"),hr([ke()],s.prototype,"_departingNewSetpoint"),s}var My=Object.defineProperty,$y=Object.getOwnPropertyDescriptor,Le=(e,t,o,r)=>{for(var i=r>1?void 0:r?$y(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&My(t,o,i),i},xe=class extends vi(S,{defaultDeadband:1}){constructor(){super(...arguments),this.minValue=0,this.maxValue=100,this.height=320,this.paddingTop=Xo.CANVAS_PADDING,this.paddingBottom=Xo.CANVAS_PADDING,this.side=Hr.right,this.fixedAspectRatio=!1,this.scaleReferenceSize=384,this._scale=1,this._resizeController=new mi(this,{callback:e=>{if(!this.fixedAspectRatio)return;let t=e[0];if(!t)return;let o=t.contentRect.height;this._scale=fi({orientation:Lo.vertical,containerMainAxisSize:o,scaleReferenceSize:this.scaleReferenceSize}),this.reportDimensions()}}),this.hasScale=!0,this.showLabels=!0,this.showMainTickmarkLabels=!1,this.hasBar=!1,this.scaleBackground=!1,this.barContainerStyle=void 0,this.barThickness=24,this.tickThickness=24,this.labelThickness=60,this.mainTickmarks=[],this.primaryTickmarkInterval=void 0,this.secondaryTickmarkInterval=void 0,this.tertiaryTickmarkInterval=void 0,this.scaleType=oo.regular,this.frameStyle=Mr.regular,this.borderRadiusPosition=void 0,this.instrumentMode=!1,this.borderRadius=void 0,this._borderRadiusResizeController=new mi(this,{callback:()=>{this.instrumentMode||this._refreshBorderRadiusFromCssVar()}}),this.priority=zt.regular,this.fillMode=Io.fill,this.fillMin=void 0,this.fillMax=void 0,this.value=void 0,this.state=to.active,this.advicePosition=Br.inner,this.advices=[],this.highlightCurrentValue=!1}render(){let e=this.fixedAspectRatio?this.scaleReferenceSize:this.height,t={orientation:Lo.vertical,side:this.side,length:e,paddingStart:this.paddingTop,paddingEnd:this.paddingBottom,minValue:this.minValue,maxValue:this.maxValue,hasScale:this.hasScale,labels:this.showLabels,mainTickmarkLabels:this.showMainTickmarkLabels,hasBar:this.hasBar,scaleBackground:this.scaleBackground,barContainerStyle:this.barContainerStyle,barThickness:this.barThickness,tickThickness:this.tickThickness,labelThickness:this.labelThickness,borderRadius:this._getEffectiveBorderRadius(),mainTickmarks:this.mainTickmarks,primaryTickmarkInterval:this.primaryTickmarkInterval,secondaryTickmarkInterval:this.secondaryTickmarkInterval,tertiaryTickmarkInterval:this.tertiaryTickmarkInterval,scaleType:this.scaleType,frameStyle:this.frameStyle,borderRadiusPosition:this.borderRadiusPosition,priority:this.priority,setpointOverride:this.setpointOverride,fillMode:this.fillMode,fillMin:this.fillMin,fillMax:this.fillMax,value:this.value,setpoint:this.setpoint,newSetpoint:this.newSetpoint,atSetpoint:this.atSetpoint,autoAtSetpoint:this.autoAtSetpoint,autoAtSetpointDeadband:this.autoAtSetpointDeadband,setpointAtZeroDeadband:this.setpointAtZeroDeadband,animateSetpoint:this.animateSetpoint,departingNewSetpoint:this.departingNewSetpoint,state:this.state,touching:this.touching,advicePosition:this.advicePosition,advices:this.advices,fixedAspectRatio:this.fixedAspectRatio,instrumentMode:this.instrumentMode,highlightCurrentValue:this.highlightCurrentValue},o=ka(u1(t)),r=m1(t),i=_a({orientation:t.orientation,length:e},o),s=this.fixedAspectRatio?"xMidYMid meet":"none";return f`
      <svg
        width=${this.fixedAspectRatio?"100%":`${i.width}px`}
        height=${this.fixedAspectRatio?"100%":`${this.height}px`}
        viewBox="${i.x} ${i.y} ${i.width} ${i.height}"
        preserveAspectRatio="${s}"
        style="--scale: ${this.fixedAspectRatio?this._scale:1};"
        part="svg"
      >
        ${r.barContainer} ${r.barFill} ${r.scaleBackground}
        ${r.tickmarks} ${r.labels} ${r.adviceOverlays}
        ${r.currentValueDot} ${r.setpoint}
      </svg>
    `}updated(e){super.updated(e),e.has("scaleType")&&this._refreshBorderRadiusFromCssVar(),e.has("fixedAspectRatio")&&(this.fixedAspectRatio?(this._applyFixedAspectRatioStyles(),this._updateScaleFromCurrentSize()):(this._removeFixedAspectRatioStyles(),this._scale=1)),e.has("scaleReferenceSize")&&this.fixedAspectRatio&&this._updateScaleFromCurrentSize();let t=e.has("side")||e.has("showLabels")||e.has("showMainTickmarkLabels")||e.has("hasScale")||e.has("hasBar")||e.has("barThickness")||e.has("tickThickness")||e.has("labelThickness")||e.has("scaleType")||e.has("borderRadiusPosition")||e.has("borderRadius")||e.has("advices")||e.has("advicePosition")||this.setpointPresenceChanged(e);(!this.fixedAspectRatio||t)&&this.reportDimensions()}reportDimensions(){let e=an({hasBar:this.hasBar,barThickness:this.barThickness,borderRadius:this._getEffectiveBorderRadius(),scaleType:this.scaleType}),t=this.fixedAspectRatio?this.scaleReferenceSize:this.height,o=g1({orientation:Lo.vertical,side:this.side,hasBar:this.hasBar,hasScale:this.hasScale,labels:this.showLabels,barThickness:e,tickThickness:this.tickThickness,labelThickness:this.labelThickness,length:t,scaleType:this.scaleType,advicePosition:this.advicePosition,hasAdvice:!!this.advices&&this.advices.length>0,hasSetpoint:this.setpoint!==void 0||this.newSetpoint!==void 0||this.departingNewSetpoint!==void 0}),r=this.fixedAspectRatio?{...o,thickness:Math.round(o.thickness*this._scale)}:o;this.dispatchEvent(new CustomEvent("scale-dimensions-changed",{detail:r,bubbles:!0,composed:!0}))}createRenderRoot(){return this}connectedCallback(){super.connectedCallback(),this.instrumentMode||(this._refreshBorderRadiusFromCssVar(),this._startBorderRadiusObserver()),this.fixedAspectRatio&&this._applyFixedAspectRatioStyles()}disconnectedCallback(){this._borderRadiusObserver?.disconnect(),this._borderRadiusObserver=void 0,super.disconnectedCallback()}_startBorderRadiusObserver(){this._borderRadiusObserver?.disconnect(),this._borderRadiusObserver=nn(this,()=>this._refreshBorderRadiusFromCssVar())}_applyFixedAspectRatioStyles(){this.style.display="block",this.style.height="100%",this.style.width="auto"}_removeFixedAspectRatioStyles(){this.style.display="",this.style.height="",this.style.width=""}_updateScaleFromCurrentSize(){requestAnimationFrame(()=>{let e=this.clientHeight;e>0&&(this._scale=fi({orientation:Lo.vertical,containerMainAxisSize:e,scaleReferenceSize:this.scaleReferenceSize}),this.requestUpdate(),this.reportDimensions())})}_refreshBorderRadiusFromCssVar(){if(this.instrumentMode)return;let e=sn(this,this.scaleType);if(this._computedBorderRadius!==e&&(this._computedBorderRadius=e),this.fixedAspectRatio){let t=this.getBoundingClientRect();t.height>0&&(this._scale=fi({orientation:Lo.vertical,containerMainAxisSize:t.height,scaleReferenceSize:this.scaleReferenceSize}),this.reportDimensions())}}_getEffectiveBorderRadius(){return this.instrumentMode?this.borderRadius!==void 0?this.borderRadius:this.scaleType===oo.condensed?4:8:this._computedBorderRadius??(this.scaleType===oo.condensed?4:8)}};Le([h({type:Number})],xe.prototype,"minValue",2);Le([h({type:Number})],xe.prototype,"maxValue",2);Le([h({type:Number})],xe.prototype,"height",2);Le([h({type:Number})],xe.prototype,"paddingTop",2);Le([h({type:Number})],xe.prototype,"paddingBottom",2);Le([h({type:String})],xe.prototype,"side",2);Le([h({type:Boolean})],xe.prototype,"fixedAspectRatio",2);Le([h({type:Number})],xe.prototype,"scaleReferenceSize",2);Le([ke()],xe.prototype,"_scale",2);Le([h({type:Boolean,attribute:!1})],xe.prototype,"hasScale",2);Le([h({type:Boolean,attribute:!1})],xe.prototype,"showLabels",2);Le([h({type:Boolean})],xe.prototype,"showMainTickmarkLabels",2);Le([h({type:Boolean})],xe.prototype,"hasBar",2);Le([h({type:Boolean})],xe.prototype,"scaleBackground",2);Le([h({type:String})],xe.prototype,"barContainerStyle",2);Le([h({type:Number})],xe.prototype,"barThickness",2);Le([h({type:Number})],xe.prototype,"tickThickness",2);Le([h({type:Number})],xe.prototype,"labelThickness",2);Le([h({type:Array,attribute:!1})],xe.prototype,"mainTickmarks",2);Le([h({type:Number})],xe.prototype,"primaryTickmarkInterval",2);Le([h({type:Number})],xe.prototype,"secondaryTickmarkInterval",2);Le([h({type:Number})],xe.prototype,"tertiaryTickmarkInterval",2);Le([h({type:String})],xe.prototype,"scaleType",2);Le([h({type:String})],xe.prototype,"frameStyle",2);Le([h({type:String})],xe.prototype,"borderRadiusPosition",2);Le([h({type:Boolean})],xe.prototype,"instrumentMode",2);Le([h({type:Number})],xe.prototype,"borderRadius",2);Le([ke()],xe.prototype,"_computedBorderRadius",2);Le([h({type:String})],xe.prototype,"priority",2);Le([h({type:String})],xe.prototype,"fillMode",2);Le([h({type:Number})],xe.prototype,"fillMin",2);Le([h({type:Number})],xe.prototype,"fillMax",2);Le([h({type:Number})],xe.prototype,"value",2);Le([h({type:String})],xe.prototype,"state",2);Le([h({type:String})],xe.prototype,"advicePosition",2);Le([h({type:Array,attribute:!1})],xe.prototype,"advices",2);Le([h({type:Boolean})],xe.prototype,"highlightCurrentValue",2);xe=Le([L("obc-bar-vertical")],xe);var Ay=Object.defineProperty,Py=Object.getOwnPropertyDescriptor,Bt=(e,t,o,r)=>{for(var i=r>1?void 0:r?Py(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ay(t,o,i),i},St=class extends vi(be){constructor(){super(),this._isFirstUpdate=!1,this._explicitXAxisType=!1,this.scaleType=oo.regular,this.minValue=0,this.maxValue=100,this.chartMinValue=void 0,this.chartMaxValue=void 0,this.value=void 0,this.hasBar=!1,this.hasScale=!1,this.hasAdvice=!1,this.fillMode=Io.fill,this.fillMin=0,this.fillMax=void 0,this.advice=[],this.primaryTickmarkInterval=void 0,this.secondaryTickmarkInterval=.5,this.tertiaryTickmarkInterval=void 0,this.chartFill=!1,this.legend=!1,this.showDebugOverlay=!1,this.showGrid=!1,this.showTickMarks=!1,this.showPoints=!1,this.xAxisType=ln.category,this.yAxisPosition=Sp.left,this.lineMode=Mp.smooth,this.unit="",this.timeDisplay=$p.date,this.fixedAspectRatioScaling=!0,this.instrumentMode=!0,this.borderRadius=8,this.borderRadiusPosition=Qe.innerFirstChild,this.borderRadiusPositionExternalScales=Qe.middleChild,this.yAxes=[{id:"y",position:"left",min:this.chartMinValue??this.minValue,max:this.chartMaxValue??this.maxValue}]}async firstUpdated(){this._createBarVerticalElement(),this._updateBorderRadiusPosition(),await super.firstUpdated(),this._isFirstUpdate=!1}disconnectedCallback(){super.disconnectedCallback()}_createBarVerticalElement(){if(!this._barVerticalElement){let e=document.createElement("obc-bar-vertical");e.setAttribute("slot","right-scale"),this._barVerticalElement=e,this.appendChild(e),this._updateBarVerticalProperties()}}_updateBorderRadiusPosition(){!this.hasBar&&!this.hasScale?this.borderRadiusPosition=Qe.middleRoundedChild:this.borderRadiusPosition=Qe.innerFirstChild}_updateBarVerticalProperties(){if(!this._barVerticalElement)return;let e=this._barVerticalElement,t=this.getEffectiveHeight();e.minValue=this.minValue,e.maxValue=this.maxValue,e.height=t,e.side="right",e.hasScale=this.hasScale,e.hasBar=this.hasBar,e.barThickness=this.hasScale?48:24,e.scaleType=this.scaleType,e.fillMode=this.fillMode,e.fillMin=this.fillMin,e.fillMax=this.fillMode===Io.fill?this.value:this.fillMax??this.value,e.value=this.value,e.setpoint=this.setpoint,e.newSetpoint=this.newSetpoint,e.touching=this.touching,e.atSetpoint=this.atSetpoint,e.autoAtSetpoint=this.autoAtSetpoint,e.autoAtSetpointDeadband=this.autoAtSetpointDeadband,e.setpointAtZeroDeadband=this.setpointAtZeroDeadband,e.animateSetpoint=this.animateSetpoint,e.setpointOverride=this.setpointOverride,e.advicePosition=Br.inner,e.advices=this.hasAdvice?this.advice:[],e.primaryTickmarkInterval=this.primaryTickmarkInterval,e.secondaryTickmarkInterval=this.secondaryTickmarkInterval,e.tertiaryTickmarkInterval=this.tertiaryTickmarkInterval,e.scaleBackground=this.hasScale,e.barContainerStyle=this.hasScale?void 0:Ca.secondary,e.fixedAspectRatio=this.fixedAspectRatioScaling,e.scaleReferenceSize=this.scaleReferenceSize,e.hasPrimaryTickmarks=this.primaryTickmarkInterval!==void 0,e.hasTertiaryTickmarks=this.tertiaryTickmarkInterval!==void 0,e.priority=this.priority,e.state=this.state,e.instrumentMode=!0,e.borderRadius=8,e.borderRadiusPosition=this.hasScale?Qe.middleChild:Qe.outerLastChild,e.highlightCurrentValue=!this.hasBar}shouldApplyFill(){return this.chartFill}getFillMode(){return this.chartFill?"semitransparent":void 0}shouldStack(){return!1}ownsSlottedScaleRange(e){return e!=="right"}willUpdate(e){if(e.has("xAxisType")&&this.xAxisType!==this._autoAppliedXAxisType&&(this.hasUpdated||this.xAxisType!==ln.category)&&(this._explicitXAxisType=!0),!this._explicitXAxisType&&e.has("data")){let o=(this.data?.length??0)>0&&this.data.every(r=>r.x!=null)?ln.time:ln.category;this.xAxisType!==o&&(this._autoAppliedXAxisType=o,this.xAxisType=o)}if(super.willUpdate(e),e.has("chartMinValue")||e.has("chartMaxValue")||e.has("minValue")||e.has("maxValue")){let t=this.chartMinValue??this.minValue,o=this.chartMaxValue??this.maxValue;this.yAxes=[{id:"y",position:"left",min:t,max:o}]}e.has("hasScale")&&(this.borderRadiusPositionExternalScales=this.hasScale?Qe.middleChild:Qe.outerLastChild)}updated(e){if(e.has("chartFill")&&this.data&&(this.data=[...this.data]),super.updated(e),(e.has("hasBar")||e.has("hasScale"))&&this._updateBorderRadiusPosition(),!this._barVerticalElement||this._isFirstUpdate)return;(e.has("minValue")||e.has("maxValue")||e.has("value")||e.has("setpoint")||e.has("newSetpoint")||e.has("touching")||e.has("atSetpoint")||e.has("autoAtSetpoint")||e.has("autoAtSetpointDeadband")||e.has("setpointAtZeroDeadband")||e.has("setpointOverride")||e.has("hasBar")||e.has("hasScale")||e.has("hasAdvice")||e.has("fillMode")||e.has("fillMin")||e.has("fillMax")||e.has("advice")||e.has("primaryTickmarkInterval")||e.has("secondaryTickmarkInterval")||e.has("tertiaryTickmarkInterval")||e.has("scaleType")||e.has("state")||e.has("priority")||e.has("height")||e.has("width")||e.has("scaleReferenceSize")||e.has("chartMinValue")||e.has("chartMaxValue"))&&this._updateBarVerticalProperties()}};Bt([h({type:String})],St.prototype,"scaleType",2);Bt([h({type:Number})],St.prototype,"minValue",2);Bt([h({type:Number})],St.prototype,"maxValue",2);Bt([h({type:Number})],St.prototype,"chartMinValue",2);Bt([h({type:Number})],St.prototype,"chartMaxValue",2);Bt([h({type:Number})],St.prototype,"value",2);Bt([h({type:Boolean})],St.prototype,"hasBar",2);Bt([h({type:Boolean})],St.prototype,"hasScale",2);Bt([h({type:Boolean})],St.prototype,"hasAdvice",2);Bt([h({type:String})],St.prototype,"fillMode",2);Bt([h({type:Number})],St.prototype,"fillMin",2);Bt([h({type:Number})],St.prototype,"fillMax",2);Bt([h({type:Array,attribute:!1})],St.prototype,"advice",2);Bt([h({type:Number})],St.prototype,"primaryTickmarkInterval",2);Bt([h({type:Number})],St.prototype,"secondaryTickmarkInterval",2);Bt([h({type:Number})],St.prototype,"tertiaryTickmarkInterval",2);Bt([h({type:Boolean})],St.prototype,"chartFill",2);St=Bt([L("obc-gauge-trend")],St);var Ap=(e=>(e.point="point",e.button="button",e))(Ap||{});var Oy=Object.defineProperty,Vy=Object.getOwnPropertyDescriptor,Pe=(e,t,o,r)=>{for(var i=r>1?void 0:r?Vy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Oy(t,o,i),i};var Se=class extends vi(S){constructor(){super(...arguments),this.medium=bh.water,this.value=0,this.max=100,this.trend="stable",this.type="generic",this.orientation="vertical",this.compact=!1,this.positioning=Ap.button,this.static=!1,this.clickable=!0,this.activated=!1,this.tag="",this.chartMode="bar",this.chartData=[],this.priority=zt.regular,this.advice=[],this.hasAdvice=!1,this.hasGraphIcon=!1,this.alert=!1,this.alertFrameType=xr.SmallSideFlip,this.alertFrameThickness=Fi.Small,this.alertFrameStatus=Q.Alarm,this.showAlertCategoryIcon=!0,this.showAlertIcon=!1,this.showTrendSymbol=!0,this.percentFractionDigits=0,this.badgeControl=ti.None,this.badgeAlert=Ho.None,this.badgeInterlock=qn.None,this.badgeCommandLocked=cc.None,this._cellWidth=0,this._cellHeight=0,this._hasBadges=!1,this._hasTagSlot=!1,this._hasRichSlot=!1}get isCompact(){return this.compact||this.static}_badgeAlertType(){switch(this.badgeAlert){case Ho.Silence:return Ae.AlertSilenced;case Ho.Caution:return Ae.Caution;case Ho.Warning:return Ae.Warning;case Ho.Alarm:return Ae.Alarm;case Ho.LevelCritical:return Ae.LevelCritical;case Ho.LevelHigh:return Ae.LevelHigh;case Ho.LevelMedium:return Ae.LevelMedium;case Ho.LevelLow:return Ae.LevelLow;case Ho.LevelDiagnostic:return Ae.LevelDiagnostic;default:return null}}_badgeControlType(){switch(this.badgeControl){case ti.Local:return Ae.Local;case ti.LocalOnly:return Ae.LocalOnly;case ti.Manual:return Ae.Manual;case ti.ManualOnly:return Ae.ManualOnly;case ti.Auto:return Ae.Auto;default:return null}}_badgeInterlockType(){switch(this.badgeInterlock){case qn.Interlock:return Ae.Interlock;case qn.InterlockInhibit:return Ae.InterlockInhibit;default:return null}}_badgeCommandLockedType(){return this.badgeCommandLocked===cc.CommandLocked?Ae.CommandLocked:null}get _usesGaugeTrend(){return this.chartMode==="graph"||this.chartMode==="graph-and-bar"}_onBadgesSlotChange(e){let t=e.target;this._hasBadges=t.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||o.nodeType===Node.TEXT_NODE&&!!o.textContent?.trim())}_onTagSlotChange(e){let t=e.target;this._hasTagSlot=t.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||o.nodeType===Node.TEXT_NODE&&!!o.textContent?.trim())}_onRichSlotChange(e){let t=e.target;this._hasRichSlot=t.assignedNodes({flatten:!0}).some(o=>o.nodeType===Node.ELEMENT_NODE||o.nodeType===Node.TEXT_NODE&&!!o.textContent?.trim())}disconnectedCallback(){super.disconnectedCallback(),this._chartResizeObserver?.disconnect(),this._chartResizeObserver=void 0,this._observedCell=void 0}updated(e){super.updated(e),this._syncChartResizeObserver()}_syncChartResizeObserver(){let e=this.renderRoot.querySelector(".bar-container");if(!e){this._chartResizeObserver&&(this._chartResizeObserver.disconnect(),this._observedCell=void 0);return}e!==this._observedCell&&(this._chartResizeObserver?this._chartResizeObserver.disconnect():this._chartResizeObserver=new ResizeObserver(t=>{let o=t[0];if(!o)return;let r=Math.round(o.contentRect.width),i=Math.round(o.contentRect.height);r!==this._cellWidth&&(this._cellWidth=r),i!==this._cellHeight&&(this._cellHeight=i)}),this._chartResizeObserver.observe(e),this._observedCell=e)}trendIcon(){return this.trend==="fast-rising"?f`<obi-chevron-double-up-google
        class="trend-icon"
      ></obi-chevron-double-up-google>`:this.trend==="rising"?f`<obi-chevron-up-google
        class="trend-icon"
      ></obi-chevron-up-google>`:this.trend==="fast-falling"?f`<obi-chevron-double-down-google
        class="trend-icon"
      ></obi-chevron-double-down-google>`:this.trend==="falling"?f`<obi-chevron-down-google
        class="trend-icon"
      ></obi-chevron-down-google>`:this.trend==="closed"?f`<obi-off class="trend-icon"></obi-off>`:f`<obi-arrow-right-google
        class="trend-icon"
      ></obi-arrow-right-google>`}renderAtmosphericCap(e){let t=this.orientation==="horizontal",o,r,i,s,n,a,l,c,d;return this.isCompact?(l=7,c=10,d=149,o="M 6.374 4.8214 C 6.138 4.8429, 6.005 4.8543, 5.83 4.8771 C 2.937 5.2557, 0.669 7.0957, 0.51 9.1936 C 0.5 9.3214, 0.5 9.4357, 0.5 9.6429 L 0.5 10 L 6.374 10 Z",r="M 6.374 4.8214 C 6.138 4.8429, 6.005 4.8543, 5.83 4.8771 C 2.937 5.2557, 0.669 7.0957, 0.51 9.1936 C 0.5 9.3214, 0.5 9.4357, 0.5 9.6429 L 0.5 10",i="M 0 4.8214 C 10.97 3.8214, 37.83 1.7857, 74.626 1.7857 C 111.42 1.7857, 138.28 3.8214, 149.252 4.8214 L 149.252 10 L 0 10 Z",s="M 0 4.8214 C 10.97 3.8214, 37.83 1.7857, 74.626 1.7857 C 111.42 1.7857, 138.28 3.8214, 149.252 4.8214",n="M 0 4.8214 C 0.236 4.8429, 0.369 4.8543, 0.544 4.8771 C 3.437 5.2557, 5.705 7.0957, 5.864 9.1936 C 5.874 9.3214, 5.874 9.4357, 5.874 9.6429 L 5.874 10 L 0 10 Z",a="M 0 4.8214 C 0.236 4.8429, 0.369 4.8543, 0.544 4.8771 C 3.437 5.2557, 5.705 7.0957, 5.864 9.1936 C 5.874 9.3214, 5.874 9.4357, 5.874 9.6429 L 5.874 10"):(l=12,c=14,d=224,o="M 12 6.5837 C 6.346 6.7737, 5.176 6.8744, 4.168 7.2537 C 2.6445 7.8272, 1.418 8.8983, 0.8613 10.1415 C 0.493 10.9641, 0.5 11.9099, 0.5 13.6111 L 0.5 14 L 12 14 Z",r="M 12 6.5837 C 6.346 6.7737, 5.176 6.8744, 4.168 7.2537 C 2.6445 7.8272, 1.418 8.8983, 0.8613 10.1415 C 0.493 10.9641, 0.5 11.9099, 0.5 13.6111 L 0.5 14",i="M 0 6.5837 C 16 5.1124, 56 1.9444, 112 1.9444 C 168 1.9444, 208 5.1124, 224 6.5837 L 224 14 L 0 14 Z",s="M 0 6.5837 C 16 5.1124, 56 1.9444, 112 1.9444 C 168 1.9444, 208 5.1124, 224 6.5837",n="M 0 6.5837 C 5.654 6.7737, 6.824 6.8744, 7.832 7.2537 C 9.3555 7.8272, 10.582 8.8983, 11.1387 10.1415 C 11.507 10.9641, 11.5 11.9099, 11.5 13.6111 L 11.5 14 L 0 14 Z",a="M 0 6.5837 C 5.654 6.7737, 6.824 6.8744, 7.832 7.2537 C 9.3555 7.8272, 10.582 8.8983, 11.1387 10.1415 C 11.507 10.9641, 11.5 11.9099, 11.5 13.6111 L 11.5 14"),t?f`
        <div class="cap cap-atmospheric cap-${e}">
          <svg
            class="cap-corner cap-corner-start"
            viewBox="0 0 ${c} ${l}"
            preserveAspectRatio="xMidYMax meet"
            aria-hidden="true"
          >
            ${w`
              <g transform="translate(0 ${l}) rotate(-90)">
                <path class="cap-fill" d="${o}" />
                <path class="cap-stroke" fill="none" d="${r}" />
              </g>
            `}
          </svg>
          <svg
            class="cap-mid"
            viewBox="0 0 ${c} ${d}"
            preserveAspectRatio="none"
            aria-hidden="true"
          >
            ${w`
              <g transform="translate(0 ${d}) rotate(-90)">
                <path class="cap-fill" d="${i}" />
                <path class="cap-stroke" fill="none" vector-effect="non-scaling-stroke" d="${s}" />
              </g>
            `}
          </svg>
          <svg
            class="cap-corner cap-corner-end"
            viewBox="0 0 ${c} ${l}"
            preserveAspectRatio="xMidYMin meet"
            aria-hidden="true"
          >
            ${w`
              <g transform="translate(0 ${l}) rotate(-90)">
                <path class="cap-fill" d="${n}" />
                <path class="cap-stroke" fill="none" d="${a}" />
              </g>
            `}
          </svg>
        </div>
      `:f`
      <div class="cap cap-atmospheric cap-${e}">
        <svg
          class="cap-corner cap-corner-start"
          viewBox="0 0 ${l} ${c}"
          preserveAspectRatio="xMaxYMid meet"
          aria-hidden="true"
        >
          ${w`
            <path class="cap-fill" d="${o}" />
            <path class="cap-stroke" fill="none" d="${r}" />
          `}
        </svg>
        <svg
          class="cap-mid"
          viewBox="0 0 ${d} ${c}"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          ${w`
            <path class="cap-fill" d="${i}" />
            <path class="cap-stroke" fill="none" vector-effect="non-scaling-stroke" d="${s}" />
          `}
        </svg>
        <svg
          class="cap-corner cap-corner-end"
          viewBox="0 0 ${l} ${c}"
          preserveAspectRatio="xMinYMid meet"
          aria-hidden="true"
        >
          ${w`
            <path class="cap-fill" d="${n}" />
            <path class="cap-stroke" fill="none" d="${a}" />
          `}
        </svg>
      </div>
    `}renderCap(e){return this.type==="generic"||this.type==="battery"&&e==="end"?null:this.type==="atmospheric"?this.renderAtmosphericCap(e):this.type==="pressurized"?f`<div class="cap cap-pressurized cap-${e}"></div>`:f`<div class="cap cap-battery cap-${e}"></div>`}render(){let e=this.max>0?this.max:1,t=Math.max(0,Math.min(100,this.value/e*100)),o=this.isCompact,r=this._badgeControlType(),i=this._badgeAlertType(),s=this._badgeInterlockType(),n=this._badgeCommandLockedType(),a=r!==null||i!==null||s!==null||n!==null,l=o&&!this._hasBadges&&!a,c=o&&!this._hasTagSlot&&!this.tag,d=f`
      <div class="badges" ?hidden=${l}>
        <slot name="badges" @slotchange=${this._onBadgesSlotChange}>
          ${r?f`<obc-automation-badge
                .type=${r}
              ></obc-automation-badge>`:z}
          ${i?f`<obc-automation-badge
                .type=${i}
              ></obc-automation-badge>`:z}
          ${s?f`<obc-automation-badge
                .type=${s}
              ></obc-automation-badge>`:z}
          ${n?f`<obc-automation-badge
                .type=${n}
              ></obc-automation-badge>`:z}
        </slot>
      </div>
    `,p=f`
      <div class="tag" ?hidden=${c}>
        <slot name="tag" @slotchange=${this._onTagSlotChange}>${this.tag}</slot>
      </div>
    `,u=this.static?f`
          <div class="readout readout-compact readout-static">
            <slot name="readout">
              <slot name="max-value">${this.max.toFixed(0)}</slot>
              <slot name="unit">m<sup>3</sup></slot>
            </slot>
          </div>
        `:o?f`
            <div class="readout readout-compact">
              <slot name="readout">
                ${this.showTrendSymbol?this.trendIcon():null}
                <span class="percent"
                  >${t.toFixed(0)}<span class="percent-symbol"
                    >%</span
                  ></span
                >
              </slot>
            </div>
          `:f`
            <div class="readout">
              <slot name="readout">
                <div class="header">
                  ${this.showTrendSymbol?this.trendIcon():null}
                  <div class="percent">
                    ${t.toFixed(this.percentFractionDigits)}<span
                      class="percent-symbol"
                      >%</span
                    >
                  </div>
                </div>
                <div class="value">
                  <div class="current">
                    <slot name="current-value" class="current-value"
                      >${this.value.toFixed(0)}</slot
                    ><span class="divider">/</span>
                  </div>
                  <div class="max">
                    <slot class="max-value" name="max-value"
                      >${this.max.toFixed(0)}</slot
                    >
                    <slot class="unit" name="unit">m<sup>3</sup></slot>
                  </div>
                </div>
                <div class="rich-divider" ?hidden=${!this._hasRichSlot}></div>
                <slot name="rich" @slotchange=${this._onRichSlotChange}></slot>
              </slot>
            </div>
          `,m=de({"graph-icon":!0,"priority-enhanced":this.priority===zt.enhanced}),b=this.type==="battery"?f`
            <div class=${m} aria-hidden="true">
              <obi-energy-battery
                class="graph-icon-stroke"
              ></obi-energy-battery>
              <obi-energy-battery class="graph-icon-fill"></obi-energy-battery>
            </div>
          `:f`
            <div class=${m} aria-hidden="true">
              <obi-tank class="graph-icon-stroke"></obi-tank>
              <obi-tank class="graph-icon-fill"></obi-tank>
            </div>
          `,C=this.alert?f`<obc-alert-frame
          class="alert-frame"
          .type=${this.alertFrameType}
          .thickness=${this.alertFrameThickness}
          .status=${this.alertFrameStatus}
          .showAlertCategoryIcon=${this.showAlertCategoryIcon}
          .showIcon=${this.showAlertIcon}
        >
          <span slot="icon"><slot name="alert-icon"></slot></span>
          <span slot="label"><slot name="alert-label"></slot></span>
          <span slot="timer"><slot name="alert-timer"></slot></span>
        </obc-alert-frame>`:null,y;if(this._usesGaugeTrend){let R=this._cellWidth>0&&this._cellHeight>0;y=f`
        <div class="bar-container chart-cell">
          ${R?f`<obc-gauge-trend
                .data=${this.chartData}
                .minValue=${0}
                .maxValue=${e}
                .value=${this.value}
                .hasBar=${this.chartMode==="graph-and-bar"}
                .hasScale=${!1}
                .hasLabelPadding=${!1}
                .chartFill=${!0}
                .hasAdvice=${this.hasAdvice}
                .advice=${this.advice}
                .width=${this._cellWidth}
                .height=${this._cellHeight}
                .setpoint=${this.setpoint}
                .newSetpoint=${this.newSetpoint}
                .touching=${this.touching}
                .atSetpoint=${this.atSetpoint}
                .autoAtSetpoint=${this.autoAtSetpoint}
                .autoAtSetpointDeadband=${this.autoAtSetpointDeadband}
                .setpointAtZeroDeadband=${this.setpointAtZeroDeadband}
                .setpointOverride=${this.setpointOverride}
                .animateSetpoint=${this.animateSetpoint}
                style="width: 100%; height: 100%;"
                .priority=${this.priority}
              ></obc-gauge-trend>`:null}
          ${this.hasGraphIcon?b:null}
        </div>
      `}else{let R=this._cellWidth>0&&this._cellHeight>0,D=384,N=this.setpoint!==void 0||this.newSetpoint!==void 0||this.departingNewSetpoint!==void 0,B=Math.max(this.hasAdvice?16:0,kp({hasSetpoint:N})),Y=Math.max(1,this._cellHeight),I=this._cellWidth*D/Y,H=Math.max(0,I-B),W=f`<obc-bar-vertical
        .minValue=${0}
        .maxValue=${e}
        .value=${this.value}
        .height=${this._cellHeight}
        .fixedAspectRatio=${!0}
        .scaleReferenceSize=${D}
        .paddingTop=${0}
        .paddingBottom=${0}
        .side=${Hr.right}
        .hasBar=${!0}
        .hasScale=${!1}
        .showLabels=${!1}
        .barThickness=${H}
        .fillMode=${Io.tint}
        .instrumentMode=${!0}
        .borderRadius=${2}
        .advices=${this.hasAdvice?this.advice:[]}
        .advicePosition=${Br.inner}
        .setpoint=${this.setpoint}
        .newSetpoint=${this.newSetpoint}
        .touching=${this.touching}
        .atSetpoint=${this.atSetpoint}
        .autoAtSetpoint=${this.autoAtSetpoint}
        .autoAtSetpointDeadband=${this.autoAtSetpointDeadband}
        .setpointAtZeroDeadband=${this.setpointAtZeroDeadband}
        .setpointOverride=${this.setpointOverride}
        .animateSetpoint=${this.animateSetpoint}
        style="width: 100%; height: 100%;"
        .priority=${this.priority}
      ></obc-bar-vertical>`;y=f`
        <div class="bar-container bar-cell">
          ${R?W:null}
          ${this.hasGraphIcon?b:null}
        </div>
      `}let k=de({"tank-frame":!0,[`type-${this.type}`]:!0,[`orientation-${this.orientation}`]:!0,[this.medium]:!0,compact:o,static:this.static}),$;this.static?$=f`<div class="static-readout">${u}</div>`:this.compact?$=y:$=f`<div class="grid">
        ${p}${d}${u}${y}
      </div>`;let V=f`
      <div class=${k}>
        ${this.renderCap("start")}
        <div class="middle">${$}</div>
        ${this.renderCap("end")}
      </div>
    `,O;this.static?O=f`${d}${V}${p}`:this.compact?O=f`${d}${V}${u}${p}`:O=V;let P=f`
      <div class="halo">${O}${C}</div>
    `,T=this.clickable&&!this.static,Z=de({root:!0,activated:this.activated,clickable:T});return this.static?f`<div
        class=${Z}
        role="img"
        aria-label=${this.tag||"Tank"}
        aria-live="polite"
        aria-atomic="true"
      >
        ${P}
      </div>`:T?f`<button
      class=${Z}
      type="button"
      aria-label=${this.tag||"Tank"}
      aria-live="polite"
      aria-atomic="true"
    >
      ${P}
    </button>`:f`<div
        class=${Z}
        aria-live="polite"
        aria-atomic="true"
      >
        ${P}
      </div>`}};Se.styles=ne(I0);Pe([h({type:String})],Se.prototype,"medium",2);Pe([h({type:Number})],Se.prototype,"value",2);Pe([h({type:Number})],Se.prototype,"max",2);Pe([h({type:String})],Se.prototype,"trend",2);Pe([h({type:String,reflect:!0})],Se.prototype,"type",2);Pe([h({type:String,reflect:!0})],Se.prototype,"orientation",2);Pe([h({type:Boolean,reflect:!0})],Se.prototype,"compact",2);Pe([h({type:String,reflect:!0})],Se.prototype,"positioning",2);Pe([h({type:Boolean,reflect:!0})],Se.prototype,"static",2);Pe([h({type:Boolean,attribute:!1})],Se.prototype,"clickable",2);Pe([h({type:Boolean})],Se.prototype,"activated",2);Pe([h({type:String})],Se.prototype,"tag",2);Pe([h({type:String,reflect:!0,attribute:"chart-mode"})],Se.prototype,"chartMode",2);Pe([h({type:Array,attribute:!1})],Se.prototype,"chartData",2);Pe([h({type:String})],Se.prototype,"priority",2);Pe([h({type:Array,attribute:!1})],Se.prototype,"advice",2);Pe([h({type:Boolean})],Se.prototype,"hasAdvice",2);Pe([h({type:Boolean,attribute:!1})],Se.prototype,"hasGraphIcon",2);Pe([h({type:Boolean})],Se.prototype,"alert",2);Pe([h({type:String})],Se.prototype,"alertFrameType",2);Pe([h({type:String})],Se.prototype,"alertFrameThickness",2);Pe([h({type:String})],Se.prototype,"alertFrameStatus",2);Pe([h({type:Boolean,attribute:!1})],Se.prototype,"showAlertCategoryIcon",2);Pe([h({type:Boolean})],Se.prototype,"showAlertIcon",2);Pe([h({type:Boolean,attribute:!1})],Se.prototype,"showTrendSymbol",2);Pe([h({type:Number})],Se.prototype,"percentFractionDigits",2);Pe([h({type:String})],Se.prototype,"badgeControl",2);Pe([h({type:String})],Se.prototype,"badgeAlert",2);Pe([h({type:String})],Se.prototype,"badgeInterlock",2);Pe([h({type:String})],Se.prototype,"badgeCommandLocked",2);Pe([ke()],Se.prototype,"_cellWidth",2);Pe([ke()],Se.prototype,"_cellHeight",2);Pe([ke()],Se.prototype,"_hasBadges",2);Pe([ke()],Se.prototype,"_hasTagSlot",2);Pe([ke()],Se.prototype,"_hasRichSlot",2);Se=Pe([L("obc-automation-tank")],Se);var Ty=Object.defineProperty,Dy=Object.getOwnPropertyDescriptor,Tm=(e,t,o,r)=>{for(var i=r>1?void 0:r?Dy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ty(t,o,i),i},y1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M6 15C6 16.1046 6.89543 17 8 17L8 18C8 19.1046 8.89543 20 10 20H11V22C11 22.5523 11.4477 23 12 23C12.5523 23 13 22.5523 13 22V20H14C15.1046 20 16 19.1046 16 18V17C17.1046 17 18 16.1046 18 15V7.5C18 6.39543 17.1046 5.5 16 5.5V4C16 2.89543 15.1046 2 14 2H10C8.89543 2 8 2.89543 8 4V5.5C6.89543 5.5 6 6.39543 6 7.5V15ZM14 19C14.5523 19 15 18.5523 15 18V17H9L9 18C9 18.5523 9.44772 19 10 19H14ZM7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5L8 6.5C7.44771 6.5 7 6.94772 7 7.5ZM9 4V5.5L15 5.5V4C15 3.44772 14.5523 3 14 3L10 3C9.44772 3 9 3.44772 9 4Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M2 9C2 8.17157 2.67157 7.5 3.5 7.5C4.32843 7.5 5 8.17157 5 9L5 14C5 14.8284 4.32843 15.5 3.5 15.5C2.67157 15.5 2 14.8284 2 14V9ZM3 14L3 9C3 8.72386 3.22386 8.5 3.5 8.5C3.77614 8.5 4 8.72386 4 9L4 14C4 14.2761 3.77614 14.5 3.5 14.5C3.22386 14.5 3 14.2761 3 14Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.5 7.5C19.6716 7.5 19 8.17157 19 9V14C19 14.8284 19.6716 15.5 20.5 15.5C21.3284 15.5 22 14.8284 22 14V9C22 8.17157 21.3284 7.5 20.5 7.5ZM20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5C20.2239 8.5 20 8.72386 20 9Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 19C14.5523 19 15 18.5523 15 18V17H9L9 18C9 18.5523 9.44772 19 10 19H14ZM7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5L8 6.5C7.44771 6.5 7 6.94772 7 7.5ZM9 4V5.5L15 5.5V4C15 3.44772 14.5523 3 14 3L10 3C9.44772 3 9 3.44772 9 4Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3 14L3 9C3 8.72386 3.22386 8.5 3.5 8.5C3.77614 8.5 4 8.72386 4 9L4 14C4 14.2761 3.77614 14.5 3.5 14.5C3.22386 14.5 3 14.2761 3 14Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5C20.2239 8.5 20 8.72386 20 9Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M6 15C6 16.1046 6.89543 17 8 17L8 18C8 19.1046 8.89543 20 10 20H11V22C11 22.5523 11.4477 23 12 23C12.5523 23 13 22.5523 13 22V20H14C15.1046 20 16 19.1046 16 18V17C17.1046 17 18 16.1046 18 15V7.5C18 6.39543 17.1046 5.5 16 5.5V4C16 2.89543 15.1046 2 14 2H10C8.89543 2 8 2.89543 8 4V5.5C6.89543 5.5 6 6.39543 6 7.5V15ZM14 19C14.5523 19 15 18.5523 15 18V17H9L9 18C9 18.5523 9.44772 19 10 19H14ZM7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5L8 6.5C7.44771 6.5 7 6.94772 7 7.5ZM9 4V5.5L15 5.5V4C15 3.44772 14.5523 3 14 3L10 3C9.44772 3 9 3.44772 9 4Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M2 9C2 8.17157 2.67157 7.5 3.5 7.5C4.32843 7.5 5 8.17157 5 9L5 14C5 14.8284 4.32843 15.5 3.5 15.5C2.67157 15.5 2 14.8284 2 14V9ZM3 14L3 9C3 8.72386 3.22386 8.5 3.5 8.5C3.77614 8.5 4 8.72386 4 9L4 14C4 14.2761 3.77614 14.5 3.5 14.5C3.22386 14.5 3 14.2761 3 14Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.5 7.5C19.6716 7.5 19 8.17157 19 9V14C19 14.8284 19.6716 15.5 20.5 15.5C21.3284 15.5 22 14.8284 22 14V9C22 8.17157 21.3284 7.5 20.5 7.5ZM20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5C20.2239 8.5 20 8.72386 20 9Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 19C14.5523 19 15 18.5523 15 18V17H9L9 18C9 18.5523 9.44772 19 10 19H14ZM7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5L8 6.5C7.44771 6.5 7 6.94772 7 7.5ZM9 4V5.5L15 5.5V4C15 3.44772 14.5523 3 14 3L10 3C9.44772 3 9 3.44772 9 4Z" style="fill: var(--automation-device-primary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3 14L3 9C3 8.72386 3.22386 8.5 3.5 8.5C3.77614 8.5 4 8.72386 4 9L4 14C4 14.2761 3.77614 14.5 3.5 14.5C3.22386 14.5 3 14.2761 3 14Z" style="fill: var(--automation-device-primary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5C20.2239 8.5 20 8.72386 20 9Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};y1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Tm([h({type:Boolean})],y1.prototype,"useCssColor",2);y1=Tm([L("obi-motor-on-vertical")],y1);var Ey=Object.defineProperty,Ry=Object.getOwnPropertyDescriptor,Dm=(e,t,o,r)=>{for(var i=r>1?void 0:r?Ry(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ey(t,o,i),i},C1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 19C14.5523 19 15 18.5523 15 18V17H9L9 18C9 18.5523 9.44772 19 10 19H14ZM7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5L8 6.5C7.44771 6.5 7 6.94772 7 7.5ZM9 4V5.5L15 5.5V4C15 3.44772 14.5523 3 14 3L10 3C9.44772 3 9 3.44772 9 4Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3 14L3 9C3 8.72386 3.22386 8.5 3.5 8.5C3.77614 8.5 4 8.72386 4 9L4 14C4 14.2761 3.77614 14.5 3.5 14.5C3.22386 14.5 3 14.2761 3 14Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5C20.2239 8.5 20 8.72386 20 9Z" fill="currentColor"/>
<path d="M11 20H13V21C13 21.5523 12.5523 22 12 22C11.4477 22 11 21.5523 11 21V20Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 2C15.1046 2 16 2.89543 16 4V5.5C17.1046 5.5 18 6.39543 18 7.5V15C18 16.1046 17.1046 17 16 17V18C16 19.1046 15.1046 20 14 20V21C14 22.1046 13.1046 23 12 23C10.8954 23 10 22.1046 10 21V20C8.89543 20 8 19.1046 8 18V17C6.89543 17 6 16.1046 6 15V7.5C6 6.39543 6.89543 5.5 8 5.5V4C8 2.89543 8.89543 2 10 2H14ZM11 20V21C11 21.5523 11.4477 22 12 22C12.5523 22 13 21.5523 13 21V20H11ZM9 18C9 18.5523 9.44772 19 10 19H14C14.5523 19 15 18.5523 15 18V17H9V18ZM8 6.5C7.44772 6.5 7 6.94772 7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5H8ZM10 3C9.44772 3 9 3.44772 9 4V5.5H15V4C15 3.44772 14.5523 3 14 3H10Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3.5 7.5C4.32843 7.5 5 8.17157 5 9V14C5 14.8284 4.32843 15.5 3.5 15.5C2.67157 15.5 2 14.8284 2 14V9C2 8.17157 2.67157 7.5 3.5 7.5ZM3.5 8.5C3.22386 8.5 3 8.72386 3 9V14C3 14.2761 3.22386 14.5 3.5 14.5C3.77614 14.5 4 14.2761 4 14V9C4 8.72386 3.77614 8.5 3.5 8.5Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.5 7.5C21.3284 7.5 22 8.17157 22 9V14C22 14.8284 21.3284 15.5 20.5 15.5C19.6716 15.5 19 14.8284 19 14V9C19 8.17157 19.6716 7.5 20.5 7.5ZM20.5 8.5C20.2239 8.5 20 8.72386 20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 19C14.5523 19 15 18.5523 15 18V17H9L9 18C9 18.5523 9.44772 19 10 19H14ZM7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5L8 6.5C7.44771 6.5 7 6.94772 7 7.5ZM9 4V5.5L15 5.5V4C15 3.44772 14.5523 3 14 3L10 3C9.44772 3 9 3.44772 9 4Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3 14L3 9C3 8.72386 3.22386 8.5 3.5 8.5C3.77614 8.5 4 8.72386 4 9L4 14C4 14.2761 3.77614 14.5 3.5 14.5C3.22386 14.5 3 14.2761 3 14Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5C20.2239 8.5 20 8.72386 20 9Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path d="M11 20H13V21C13 21.5523 12.5523 22 12 22C11.4477 22 11 21.5523 11 21V20Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 2C15.1046 2 16 2.89543 16 4V5.5C17.1046 5.5 18 6.39543 18 7.5V15C18 16.1046 17.1046 17 16 17V18C16 19.1046 15.1046 20 14 20V21C14 22.1046 13.1046 23 12 23C10.8954 23 10 22.1046 10 21V20C8.89543 20 8 19.1046 8 18V17C6.89543 17 6 16.1046 6 15V7.5C6 6.39543 6.89543 5.5 8 5.5V4C8 2.89543 8.89543 2 10 2H14ZM11 20V21C11 21.5523 11.4477 22 12 22C12.5523 22 13 21.5523 13 21V20H11ZM9 18C9 18.5523 9.44772 19 10 19H14C14.5523 19 15 18.5523 15 18V17H9V18ZM8 6.5C7.44772 6.5 7 6.94772 7 7.5V15C7 15.5523 7.44772 16 8 16H16C16.5523 16 17 15.5523 17 15V7.5C17 6.94771 16.5523 6.5 16 6.5H8ZM10 3C9.44772 3 9 3.44772 9 4V5.5H15V4C15 3.44772 14.5523 3 14 3H10Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3.5 7.5C4.32843 7.5 5 8.17157 5 9V14C5 14.8284 4.32843 15.5 3.5 15.5C2.67157 15.5 2 14.8284 2 14V9C2 8.17157 2.67157 7.5 3.5 7.5ZM3.5 8.5C3.22386 8.5 3 8.72386 3 9V14C3 14.2761 3.22386 14.5 3.5 14.5C3.77614 14.5 4 14.2761 4 14V9C4 8.72386 3.77614 8.5 3.5 8.5Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M20.5 7.5C21.3284 7.5 22 8.17157 22 9V14C22 14.8284 21.3284 15.5 20.5 15.5C19.6716 15.5 19 14.8284 19 14V9C19 8.17157 19.6716 7.5 20.5 7.5ZM20.5 8.5C20.2239 8.5 20 8.72386 20 9V14C20 14.2761 20.2239 14.5 20.5 14.5C20.7761 14.5 21 14.2761 21 14V9C21 8.72386 20.7761 8.5 20.5 8.5Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};C1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Dm([h({type:Boolean})],C1.prototype,"useCssColor",2);C1=Dm([L("obi-motor-off-vertical")],C1);var zy=Object.defineProperty,Hy=Object.getOwnPropertyDescriptor,Em=(e,t,o,r)=>{for(var i=r>1?void 0:r?Hy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&zy(t,o,i),i},x1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.89543 7.89543 3 9 3H16.5C17.6046 3 18.5 3.89543 18.5 5H20C21.1046 5 22 5.89543 22 7V11C22 12.1046 21.1046 13 20 13H18.5C18.5 14.1046 17.6046 15 16.5 15V19H19C19.8284 19 20.5 19.6716 20.5 20.5C20.5 21.3284 19.8284 22 19 22H6.5C5.67157 22 5 21.3284 5 20.5C5 19.6716 5.67157 19 6.5 19H9V15C7.89543 15 7 14.1046 7 13H6C4.89543 13 4 12.1046 4 11V10H2C1.44772 10 1 9.55228 1 9C1 8.44772 1.44772 8 2 8H4V7C4 5.89543 4.89543 5 6 5H7ZM9 4H16.5C17.0523 4 17.5 4.44772 17.5 5V13C17.5 13.5523 17.0523 14 16.5 14H9C8.44772 14 8 13.5523 8 13V5C8 4.44772 8.44772 4 9 4ZM7 6H6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6ZM18.5 6H20C20.5523 6 21 6.44772 21 7V11C21 11.5523 20.5523 12 20 12H18.5V6ZM15.5 15H10V20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 4H16.5C17.0523 4 17.5 4.44772 17.5 5V13C17.5 13.5523 17.0523 14 16.5 14H9C8.44772 14 8 13.5523 8 13V5C8 4.44772 8.44772 4 9 4ZM7 6H6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6ZM18.5 6H20C20.5523 6 21 6.44772 21 7V11C21 11.5523 20.5523 12 20 12H18.5V6ZM15.5 15H10V20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.89543 7.89543 3 9 3H16.5C17.6046 3 18.5 3.89543 18.5 5H20C21.1046 5 22 5.89543 22 7V11C22 12.1046 21.1046 13 20 13H18.5C18.5 14.1046 17.6046 15 16.5 15V19H19C19.8284 19 20.5 19.6716 20.5 20.5C20.5 21.3284 19.8284 22 19 22H6.5C5.67157 22 5 21.3284 5 20.5C5 19.6716 5.67157 19 6.5 19H9V15C7.89543 15 7 14.1046 7 13H6C4.89543 13 4 12.1046 4 11V10H2C1.44772 10 1 9.55228 1 9C1 8.44772 1.44772 8 2 8H4V7C4 5.89543 4.89543 5 6 5H7ZM9 4H16.5C17.0523 4 17.5 4.44772 17.5 5V13C17.5 13.5523 17.0523 14 16.5 14H9C8.44772 14 8 13.5523 8 13V5C8 4.44772 8.44772 4 9 4ZM7 6H6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6ZM18.5 6H20C20.5523 6 21 6.44772 21 7V11C21 11.5523 20.5523 12 20 12H18.5V6ZM15.5 15H10V20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 4H16.5C17.0523 4 17.5 4.44772 17.5 5V13C17.5 13.5523 17.0523 14 16.5 14H9C8.44772 14 8 13.5523 8 13V5C8 4.44772 8.44772 4 9 4ZM7 6H6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6ZM18.5 6H20C20.5523 6 21 6.44772 21 7V11C21 11.5523 20.5523 12 20 12H18.5V6ZM15.5 15H10V20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};x1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Em([h({type:Boolean})],x1.prototype,"useCssColor",2);x1=Em([L("obi-motor-on-horizontal")],x1);var By=Object.defineProperty,Iy=Object.getOwnPropertyDescriptor,Rm=(e,t,o,r)=>{for(var i=r>1?void 0:r?Iy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&By(t,o,i),i},_1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 4H16.5C17.0523 4 17.5 4.44772 17.5 5V13C17.5 13.5523 17.0523 14 16.5 14H9C8.44772 14 8 13.5523 8 13V5C8 4.44772 8.44772 4 9 4ZM7 6H6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6ZM18.5 6H20C20.5523 6 21 6.44772 21 7V11C21 11.5523 20.5523 12 20 12H18.5V6ZM15.5 15H10V20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15Z" fill="currentColor"/>
<path d="M2 9C2 8.44772 2.44772 8 3 8H4V10H3C2.44772 10 2 9.55228 2 9Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M16.5 3C17.6046 3 18.5 3.89543 18.5 5H20C21.1046 5 22 5.89543 22 7V11C22 12.1046 21.1046 13 20 13H18.5C18.5 14.1046 17.6046 15 16.5 15V19H19C19.8284 19 20.5 19.6716 20.5 20.5C20.5 21.3284 19.8284 22 19 22H6.5C5.67157 22 5 21.3284 5 20.5C5 19.6716 5.67157 19 6.5 19H9V15C7.89543 15 7 14.1046 7 13H6C4.89543 13 4 12.1046 4 11H3C1.89543 11 1 10.1046 1 9C1 7.89543 1.89543 7 3 7H4C4 5.89543 4.89543 5 6 5H7C7 3.89543 7.89543 3 9 3H16.5ZM10 20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15H10V20ZM9 4C8.44772 4 8 4.44772 8 5V13C8 13.5523 8.44772 14 9 14H16.5C17.0523 14 17.5 13.5523 17.5 13V5C17.5 4.44772 17.0523 4 16.5 4H9ZM6 6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6H6ZM18.5 12H20C20.5523 12 21 11.5523 21 11V7C21 6.44772 20.5523 6 20 6H18.5V12ZM3 8C2.44772 8 2 8.44772 2 9C2 9.55228 2.44772 10 3 10H4V8H3Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M9 4H16.5C17.0523 4 17.5 4.44772 17.5 5V13C17.5 13.5523 17.0523 14 16.5 14H9C8.44772 14 8 13.5523 8 13V5C8 4.44772 8.44772 4 9 4ZM7 6H6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6ZM18.5 6H20C20.5523 6 21 6.44772 21 7V11C21 11.5523 20.5523 12 20 12H18.5V6ZM15.5 15H10V20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path d="M2 9C2 8.44772 2.44772 8 3 8H4V10H3C2.44772 10 2 9.55228 2 9Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M16.5 3C17.6046 3 18.5 3.89543 18.5 5H20C21.1046 5 22 5.89543 22 7V11C22 12.1046 21.1046 13 20 13H18.5C18.5 14.1046 17.6046 15 16.5 15V19H19C19.8284 19 20.5 19.6716 20.5 20.5C20.5 21.3284 19.8284 22 19 22H6.5C5.67157 22 5 21.3284 5 20.5C5 19.6716 5.67157 19 6.5 19H9V15C7.89543 15 7 14.1046 7 13H6C4.89543 13 4 12.1046 4 11H3C1.89543 11 1 10.1046 1 9C1 7.89543 1.89543 7 3 7H4C4 5.89543 4.89543 5 6 5H7C7 3.89543 7.89543 3 9 3H16.5ZM10 20H6.5C6.22386 20 6 20.2239 6 20.5C6 20.7761 6.22386 21 6.5 21H19C19.2761 21 19.5 20.7761 19.5 20.5C19.5 20.2239 19.2761 20 19 20H15.5V15H10V20ZM9 4C8.44772 4 8 4.44772 8 5V13C8 13.5523 8.44772 14 9 14H16.5C17.0523 14 17.5 13.5523 17.5 13V5C17.5 4.44772 17.0523 4 16.5 4H9ZM6 6C5.44772 6 5 6.44772 5 7V11C5 11.5523 5.44772 12 6 12H7V6H6ZM18.5 12H20C20.5523 12 21 11.5523 21 11V7C21 6.44772 20.5523 6 20 6H18.5V12ZM3 8C2.44772 8 2 8.44772 2 9C2 9.55228 2.44772 10 3 10H4V8H3Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};_1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Rm([h({type:Boolean})],_1.prototype,"useCssColor",2);_1=Rm([L("obi-motor-off-horizontal")],_1);var Zy=Object.defineProperty,Fy=Object.getOwnPropertyDescriptor,zm=(e,t,o,r)=>{for(var i=r>1?void 0:r?Fy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Zy(t,o,i),i},Pp=class extends Gt{constructor(){super(...arguments),this.vertical=!1}get icon(){return this.vertical?this.on?f`<obi-motor-on-vertical
            usecsscolor
            slot="icon"
          ></obi-motor-on-vertical>
          <obi-motor-on-vertical
            usecsscolor
            slot="icon-silhouette"
          ></obi-motor-on-vertical>`:f`<obi-motor-off-vertical
            usecsscolor
            slot="icon"
          ></obi-motor-off-vertical>
          <obi-motor-off-vertical
            usecsscolor
            slot="icon-silhouette"
          ></obi-motor-off-vertical>`:this.on?f`<obi-motor-on-horizontal
            usecsscolor
            slot="icon"
          ></obi-motor-on-horizontal>
          <obi-motor-on-horizontal
            usecsscolor
            slot="icon-silhouette"
          ></obi-motor-on-horizontal>`:f`<obi-motor-off-horizontal
            usecsscolor
            slot="icon"
          ></obi-motor-off-horizontal>
          <obi-motor-off-horizontal
            usecsscolor
            slot="icon-silhouette"
          ></obi-motor-off-horizontal>`}};zm([h({type:Boolean})],Pp.prototype,"vertical",2);Pp=zm([L("obc-motor")],Pp);var Ny=Object.defineProperty,jy=Object.getOwnPropertyDescriptor,Hm=(e,t,o,r)=>{for(var i=r>1?void 0:r?jy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ny(t,o,i),i},k1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M15.1468 12.69C14.1646 13.2513 13.843 14.5149 14.4375 15.4774L17.9336 21.1383C17.9688 21.1953 17.9391 21.2701 17.8744 21.2875L15.3354 21.9678C12.7878 22.6504 10.2884 20.7237 10.3001 18.0863L10.3134 15.0998C10.3185 13.9685 9.38497 13.0582 8.25416 13.0918L1.60362 13.2891C1.53666 13.2911 1.48673 13.2279 1.50406 13.1632L2.18439 10.6242C2.86703 8.07658 5.78526 6.87542 8.0635 8.20432L10.6432 9.70909C11.6204 10.2791 12.8755 9.92579 13.4119 8.9297L16.5663 3.0715C16.5981 3.01252 16.6777 3.00083 16.7251 3.0482L18.5838 4.9069C20.4487 6.77188 20.0299 9.89973 17.7399 11.2083L15.1468 12.69Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M15.2883 14.952L18.7844 20.6129C19.1716 21.2398 18.845 22.0627 18.1332 22.2534L15.5942 22.9337C12.4097 23.787 9.28548 21.3787 9.30016 18.0818L9.31346 15.0954C9.31598 14.5297 8.84922 14.0746 8.28381 14.0913L1.63327 14.2886C0.896753 14.3105 0.347426 13.6162 0.538138 12.9044L1.21847 10.3654C2.07176 7.18086 5.71955 5.6794 8.56735 7.34053L11.1471 8.8453C11.6357 9.1303 12.2632 8.95365 12.5314 8.4556L15.6858 2.5974C16.0352 1.94862 16.9111 1.82006 17.4322 2.34109L19.2909 4.19979C21.6221 6.53102 21.0985 10.4408 18.236 12.0765L15.643 13.5583C15.1519 13.8389 14.9911 14.4707 15.2883 14.952ZM18.5838 4.9069C20.4487 6.77188 20.0299 9.89973 17.7399 11.2083L15.1468 12.69C14.1646 13.2513 13.843 14.5149 14.4375 15.4774L17.9336 21.1383C17.9688 21.1953 17.9391 21.2701 17.8744 21.2875L15.3354 21.9678C12.7878 22.6504 10.2884 20.7237 10.3001 18.0863L10.3134 15.0998C10.3185 13.9685 9.38497 13.0582 8.25416 13.0918L1.60362 13.2891C1.53666 13.2911 1.48673 13.2279 1.50406 13.1632L2.18439 10.6242C2.86703 8.07658 5.78526 6.87542 8.0635 8.20432L10.6432 9.70909C11.6204 10.2791 12.8755 9.92579 13.4119 8.9297L16.5663 3.0715C16.5981 3.01252 16.6777 3.00083 16.7251 3.0482L18.5838 4.9069Z" fill="currentColor"/>
<path d="M12.4227 11.0508C13.2229 11.2652 13.6978 12.0877 13.4834 12.8879C13.269 13.6881 12.4465 14.1629 11.6463 13.9485C10.8461 13.7341 10.3712 12.9116 10.5856 12.1114C10.8 11.3112 11.6225 10.8363 12.4227 11.0508Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14.2296 2.74357C11.6421 2.16183 8.92937 2.63183 6.68833 4.05017C6.45499 4.19785 6.14612 4.12841 5.99844 3.89507C5.85076 3.66173 5.92021 3.35286 6.15354 3.20518C8.61869 1.645 11.6027 1.12801 14.449 1.76792C14.7184 1.82849 14.8877 2.096 14.8271 2.36541C14.7666 2.63483 14.4991 2.80414 14.2296 2.74357ZM13.3719 4.61233C12.3777 4.44398 11.3607 4.46509 10.3744 4.67454C10.1043 4.7319 9.83881 4.55943 9.78144 4.28931C9.72408 4.01919 9.89656 3.75371 10.1667 3.69635C11.2763 3.46072 12.4204 3.43698 13.5388 3.62636C13.8111 3.67247 13.9944 3.93056 13.9483 4.20282C13.9022 4.47509 13.6441 4.65843 13.3719 4.61233ZM22.5072 11.5737C22.7831 11.5625 23.0159 11.777 23.0271 12.0529C23.1457 14.9679 22.1014 17.8106 20.1241 19.9556C19.9369 20.1587 19.6206 20.1715 19.4176 19.9844C19.2145 19.7972 19.2017 19.4809 19.3888 19.2779C21.1864 17.3278 22.1357 14.7436 22.0279 12.0936C22.0167 11.8177 22.2313 11.5849 22.5072 11.5737ZM20.2743 14.6527C20.5369 14.7381 20.6806 15.0202 20.5952 15.2828C20.2444 16.3616 19.6929 17.3643 18.9697 18.2382C18.7937 18.4509 18.4785 18.4807 18.2657 18.3046C18.053 18.1285 18.0233 17.8134 18.1993 17.6006C18.8422 16.8238 19.3324 15.9325 19.6442 14.9736C19.7296 14.711 20.0117 14.5674 20.2743 14.6527ZM3.89454 14.9927C4.15338 14.8965 4.4412 15.0283 4.53741 15.2872C4.88869 16.2323 5.41547 17.1025 6.09001 17.8519C6.27475 18.0572 6.25812 18.3733 6.05287 18.5581C5.84762 18.7428 5.53148 18.7262 5.34674 18.5209C4.58788 17.6778 3.99525 16.6988 3.60006 15.6356C3.50385 15.3767 3.63569 15.0889 3.89454 14.9927ZM1.86388 15.1503C2.12749 15.0681 2.40786 15.2151 2.49012 15.4787C3.28011 18.0105 5.04348 20.1247 7.39233 21.3564C7.63689 21.4846 7.73119 21.7868 7.60295 22.0314C7.47471 22.2759 7.1725 22.3702 6.92794 22.242C4.34421 20.8872 2.4045 18.5615 1.53551 15.7766C1.45326 15.513 1.60027 15.2326 1.86388 15.1503Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.9335 21.1384L14.4374 15.4775C13.8429 14.5149 14.1645 13.2513 15.1467 12.6901L17.7398 11.2083C20.0298 9.89976 20.4486 6.77191 18.5836 4.90692L16.7249 3.04822C16.6776 3.00086 16.5979 3.01254 16.5662 3.07152L13.4118 8.92973C12.8754 9.92581 11.6203 10.2791 10.6431 9.70911L8.06339 8.20435C5.78515 6.87544 2.86692 8.07661 2.18429 10.6242L1.50396 13.1633C1.48662 13.228 1.53656 13.2911 1.60351 13.2891L8.25405 13.0918C9.38486 13.0583 10.3184 13.9685 10.3133 15.0998L10.3 18.0863C10.2883 20.7238 12.7877 22.6505 15.3353 21.9678L17.8743 21.2875C17.939 21.2702 17.9687 21.1953 17.9335 21.1384ZM13.4833 12.8879C13.6977 12.0877 13.2228 11.2652 12.4226 11.0508C11.6224 10.8364 10.7999 11.3112 10.5855 12.1114C10.3711 12.9116 10.846 13.7341 11.6462 13.9486C12.4464 14.163 13.2689 13.6881 13.4833 12.8879Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M15.1468 12.69C14.1646 13.2513 13.843 14.5149 14.4375 15.4774L17.9336 21.1383C17.9688 21.1953 17.9391 21.2701 17.8744 21.2875L15.3354 21.9678C12.7878 22.6504 10.2884 20.7237 10.3001 18.0863L10.3134 15.0998C10.3185 13.9685 9.38497 13.0582 8.25416 13.0918L1.60362 13.2891C1.53666 13.2911 1.48673 13.2279 1.50406 13.1632L2.18439 10.6242C2.86703 8.07658 5.78526 6.87542 8.0635 8.20432L10.6432 9.70909C11.6204 10.2791 12.8755 9.92579 13.4119 8.9297L16.5663 3.0715C16.5981 3.01252 16.6777 3.00083 16.7251 3.0482L18.5838 4.9069C20.4487 6.77188 20.0299 9.89973 17.7399 11.2083L15.1468 12.69Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M15.2883 14.952L18.7844 20.6129C19.1716 21.2398 18.845 22.0627 18.1332 22.2534L15.5942 22.9337C12.4097 23.787 9.28548 21.3787 9.30016 18.0818L9.31346 15.0954C9.31598 14.5297 8.84922 14.0746 8.28381 14.0913L1.63327 14.2886C0.896753 14.3105 0.347426 13.6162 0.538138 12.9044L1.21847 10.3654C2.07176 7.18086 5.71955 5.6794 8.56735 7.34053L11.1471 8.8453C11.6357 9.1303 12.2632 8.95365 12.5314 8.4556L15.6858 2.5974C16.0352 1.94862 16.9111 1.82006 17.4322 2.34109L19.2909 4.19979C21.6221 6.53102 21.0985 10.4408 18.236 12.0765L15.643 13.5583C15.1519 13.8389 14.9911 14.4707 15.2883 14.952ZM18.5838 4.9069C20.4487 6.77188 20.0299 9.89973 17.7399 11.2083L15.1468 12.69C14.1646 13.2513 13.843 14.5149 14.4375 15.4774L17.9336 21.1383C17.9688 21.1953 17.9391 21.2701 17.8744 21.2875L15.3354 21.9678C12.7878 22.6504 10.2884 20.7237 10.3001 18.0863L10.3134 15.0998C10.3185 13.9685 9.38497 13.0582 8.25416 13.0918L1.60362 13.2891C1.53666 13.2911 1.48673 13.2279 1.50406 13.1632L2.18439 10.6242C2.86703 8.07658 5.78526 6.87542 8.0635 8.20432L10.6432 9.70909C11.6204 10.2791 12.8755 9.92579 13.4119 8.9297L16.5663 3.0715C16.5981 3.01252 16.6777 3.00083 16.7251 3.0482L18.5838 4.9069Z" style="fill: var(--automation-device-tertiary-color)"/>
<path d="M12.4227 11.0508C13.2229 11.2652 13.6978 12.0877 13.4834 12.8879C13.269 13.6881 12.4465 14.1629 11.6463 13.9485C10.8461 13.7341 10.3712 12.9116 10.5856 12.1114C10.8 11.3112 11.6225 10.8363 12.4227 11.0508Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14.2296 2.74357C11.6421 2.16183 8.92937 2.63183 6.68833 4.05017C6.45499 4.19785 6.14612 4.12841 5.99844 3.89507C5.85076 3.66173 5.92021 3.35286 6.15354 3.20518C8.61869 1.645 11.6027 1.12801 14.449 1.76792C14.7184 1.82849 14.8877 2.096 14.8271 2.36541C14.7666 2.63483 14.4991 2.80414 14.2296 2.74357ZM13.3719 4.61233C12.3777 4.44398 11.3607 4.46509 10.3744 4.67454C10.1043 4.7319 9.83881 4.55943 9.78144 4.28931C9.72408 4.01919 9.89656 3.75371 10.1667 3.69635C11.2763 3.46072 12.4204 3.43698 13.5388 3.62636C13.8111 3.67247 13.9944 3.93056 13.9483 4.20282C13.9022 4.47509 13.6441 4.65843 13.3719 4.61233ZM22.5072 11.5737C22.7831 11.5625 23.0159 11.777 23.0271 12.0529C23.1457 14.9679 22.1014 17.8106 20.1241 19.9556C19.9369 20.1587 19.6206 20.1715 19.4176 19.9844C19.2145 19.7972 19.2017 19.4809 19.3888 19.2779C21.1864 17.3278 22.1357 14.7436 22.0279 12.0936C22.0167 11.8177 22.2313 11.5849 22.5072 11.5737ZM20.2743 14.6527C20.5369 14.7381 20.6806 15.0202 20.5952 15.2828C20.2444 16.3616 19.6929 17.3643 18.9697 18.2382C18.7937 18.4509 18.4785 18.4807 18.2657 18.3046C18.053 18.1285 18.0233 17.8134 18.1993 17.6006C18.8422 16.8238 19.3324 15.9325 19.6442 14.9736C19.7296 14.711 20.0117 14.5674 20.2743 14.6527ZM3.89454 14.9927C4.15338 14.8965 4.4412 15.0283 4.53741 15.2872C4.88869 16.2323 5.41547 17.1025 6.09001 17.8519C6.27475 18.0572 6.25812 18.3733 6.05287 18.5581C5.84762 18.7428 5.53148 18.7262 5.34674 18.5209C4.58788 17.6778 3.99525 16.6988 3.60006 15.6356C3.50385 15.3767 3.63569 15.0889 3.89454 14.9927ZM1.86388 15.1503C2.12749 15.0681 2.40786 15.2151 2.49012 15.4787C3.28011 18.0105 5.04348 20.1247 7.39233 21.3564C7.63689 21.4846 7.73119 21.7868 7.60295 22.0314C7.47471 22.2759 7.1725 22.3702 6.92794 22.242C4.34421 20.8872 2.4045 18.5615 1.53551 15.7766C1.45326 15.513 1.60027 15.2326 1.86388 15.1503Z" style="fill: var(--automation-device-tertiary-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.9335 21.1384L14.4374 15.4775C13.8429 14.5149 14.1645 13.2513 15.1467 12.6901L17.7398 11.2083C20.0298 9.89976 20.4486 6.77191 18.5836 4.90692L16.7249 3.04822C16.6776 3.00086 16.5979 3.01254 16.5662 3.07152L13.4118 8.92973C12.8754 9.92581 11.6203 10.2791 10.6431 9.70911L8.06339 8.20435C5.78515 6.87544 2.86692 8.07661 2.18429 10.6242L1.50396 13.1633C1.48662 13.228 1.53656 13.2911 1.60351 13.2891L8.25405 13.0918C9.38486 13.0583 10.3184 13.9685 10.3133 15.0998L10.3 18.0863C10.2883 20.7238 12.7877 22.6505 15.3353 21.9678L17.8743 21.2875C17.939 21.2702 17.9687 21.1953 17.9335 21.1384ZM13.4833 12.8879C13.6977 12.0877 13.2228 11.2652 12.4226 11.0508C11.6224 10.8364 10.7999 11.3112 10.5855 12.1114C10.3711 12.9116 10.846 13.7341 11.6462 13.9486C12.4464 14.163 13.2689 13.6881 13.4833 12.8879Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};k1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Hm([h({type:Boolean})],k1.prototype,"useCssColor",2);k1=Hm([L("obi-fan-on")],k1);var Wy=Object.defineProperty,Uy=Object.getOwnPropertyDescriptor,Bm=(e,t,o,r)=>{for(var i=r>1?void 0:r?Uy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Wy(t,o,i),i},L1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M11.9517 15.0554C11.1553 14.2519 9.85157 14.2684 9.07569 15.0917L4.51256 19.9338C4.46662 19.9826 4.38667 19.9733 4.35318 19.9153L3.03888 17.6388C1.72014 15.3547 2.93428 12.4418 5.48492 11.7705L8.37308 11.0104C9.46713 10.7225 10.1048 9.58519 9.7797 8.5016L7.86784 2.12874C7.84859 2.06457 7.89664 2 7.96362 2H10.5922C13.2297 2 15.1452 4.50791 14.4513 7.05247L13.6655 9.93376C13.3678 11.0252 14.0339 12.1461 15.1349 12.4063L21.6099 13.9371C21.6751 13.9525 21.707 14.0264 21.6735 14.0844L20.3592 16.3608C19.0404 18.645 15.9108 19.0499 14.0541 17.1766L11.9517 15.0554Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9.80345 15.7775L5.24032 20.6197C4.73497 21.1559 3.85558 21.0534 3.48715 20.4153L2.17286 18.1388C0.524423 15.2836 2.04211 11.6426 5.23041 10.8035L8.11856 10.0434C8.66559 9.8994 8.98441 9.33074 8.82188 8.78895L6.91002 2.41608C6.69829 1.71031 7.22677 1 7.96362 1H10.5922C13.8891 1 16.2835 4.13489 15.416 7.31559L14.6302 10.1969C14.4814 10.7426 14.8145 11.303 15.3649 11.4332L21.84 12.9639C22.557 13.1334 22.9079 13.9463 22.5395 14.5844L21.2252 16.8608C19.5768 19.716 15.6647 20.2222 13.3438 17.8806L11.2415 15.7594C10.8433 15.3576 10.1914 15.3658 9.80345 15.7775ZM20.3592 16.3608C19.0404 18.645 15.9108 19.0499 14.0541 17.1766L11.9517 15.0554C11.1553 14.2519 9.85157 14.2684 9.07569 15.0917L4.51256 19.9338C4.46662 19.9826 4.38667 19.9733 4.35318 19.9153L3.03888 17.6388C1.72014 15.3547 2.93428 12.4418 5.48492 11.7705L8.37308 11.0104C9.46713 10.7225 10.1048 9.58519 9.7797 8.5016L7.86784 2.12874C7.84859 2.06457 7.89664 2 7.96362 2H10.5922C13.2297 2 15.1452 4.50791 14.4513 7.05247L13.6655 9.93376C13.3678 11.0252 14.0339 12.1461 15.1349 12.4063L21.6099 13.9371C21.6751 13.9525 21.707 14.0264 21.6735 14.0844L20.3592 16.3608Z" fill="currentColor"/>
<path d="M12.8307 12C12.8307 12.8284 12.1591 13.5 11.3307 13.5C10.5022 13.5 9.83068 12.8284 9.83068 12C9.83068 11.1716 10.5022 10.5 11.3307 10.5C12.1591 10.5 12.8307 11.1716 12.8307 12Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.9516 15.0554C11.1552 14.2519 9.85146 14.2684 9.07558 15.0917L4.51245 19.9338C4.46651 19.9826 4.38656 19.9733 4.35307 19.9153L3.03877 17.6388C1.72003 15.3547 2.93418 12.4418 5.48481 11.7705L8.37297 11.0104C9.46702 10.7225 10.1047 9.58519 9.77959 8.5016L7.86773 2.12874C7.84848 2.06457 7.89653 2 7.96352 2H10.5921C13.2296 2 15.1451 4.50791 14.4512 7.05247L13.6654 9.93376C13.3677 11.0252 14.0338 12.1461 15.1348 12.4063L21.6098 13.9371C21.675 13.9525 21.7069 14.0264 21.6734 14.0844L20.3591 16.3608C19.0403 18.645 15.9107 19.0499 14.054 17.1766L11.9516 15.0554ZM11.3306 13.5C12.159 13.5 12.8306 12.8284 12.8306 12C12.8306 11.1716 12.159 10.5 11.3306 10.5C10.5021 10.5 9.83057 11.1716 9.83057 12C9.83057 12.8284 10.5021 13.5 11.3306 13.5Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11.9517 15.0554C11.1553 14.2519 9.85157 14.2684 9.07569 15.0917L4.51256 19.9338C4.46662 19.9826 4.38667 19.9733 4.35318 19.9153L3.03888 17.6388C1.72014 15.3547 2.93428 12.4418 5.48492 11.7705L8.37308 11.0104C9.46713 10.7225 10.1048 9.58519 9.7797 8.5016L7.86784 2.12874C7.84859 2.06457 7.89664 2 7.96362 2H10.5922C13.2297 2 15.1452 4.50791 14.4513 7.05247L13.6655 9.93376C13.3678 11.0252 14.0339 12.1461 15.1349 12.4063L21.6099 13.9371C21.6751 13.9525 21.707 14.0264 21.6735 14.0844L20.3592 16.3608C19.0404 18.645 15.9108 19.0499 14.0541 17.1766L11.9517 15.0554Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M9.80345 15.7775L5.24032 20.6197C4.73497 21.1559 3.85558 21.0534 3.48715 20.4153L2.17286 18.1388C0.524423 15.2836 2.04211 11.6426 5.23041 10.8035L8.11856 10.0434C8.66559 9.8994 8.98441 9.33074 8.82188 8.78895L6.91002 2.41608C6.69829 1.71031 7.22677 1 7.96362 1H10.5922C13.8891 1 16.2835 4.13489 15.416 7.31559L14.6302 10.1969C14.4814 10.7426 14.8145 11.303 15.3649 11.4332L21.84 12.9639C22.557 13.1334 22.9079 13.9463 22.5395 14.5844L21.2252 16.8608C19.5768 19.716 15.6647 20.2222 13.3438 17.8806L11.2415 15.7594C10.8433 15.3576 10.1914 15.3658 9.80345 15.7775ZM20.3592 16.3608C19.0404 18.645 15.9108 19.0499 14.0541 17.1766L11.9517 15.0554C11.1553 14.2519 9.85157 14.2684 9.07569 15.0917L4.51256 19.9338C4.46662 19.9826 4.38667 19.9733 4.35318 19.9153L3.03888 17.6388C1.72014 15.3547 2.93428 12.4418 5.48492 11.7705L8.37308 11.0104C9.46713 10.7225 10.1048 9.58519 9.7797 8.5016L7.86784 2.12874C7.84859 2.06457 7.89664 2 7.96362 2H10.5922C13.2297 2 15.1452 4.50791 14.4513 7.05247L13.6655 9.93376C13.3678 11.0252 14.0339 12.1461 15.1349 12.4063L21.6099 13.9371C21.6751 13.9525 21.707 14.0264 21.6735 14.0844L20.3592 16.3608Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path d="M12.8307 12C12.8307 12.8284 12.1591 13.5 11.3307 13.5C10.5022 13.5 9.83068 12.8284 9.83068 12C9.83068 11.1716 10.5022 10.5 11.3307 10.5C12.1591 10.5 12.8307 11.1716 12.8307 12Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.9516 15.0554C11.1552 14.2519 9.85146 14.2684 9.07558 15.0917L4.51245 19.9338C4.46651 19.9826 4.38656 19.9733 4.35307 19.9153L3.03877 17.6388C1.72003 15.3547 2.93418 12.4418 5.48481 11.7705L8.37297 11.0104C9.46702 10.7225 10.1047 9.58519 9.77959 8.5016L7.86773 2.12874C7.84848 2.06457 7.89653 2 7.96352 2H10.5921C13.2296 2 15.1451 4.50791 14.4512 7.05247L13.6654 9.93376C13.3677 11.0252 14.0338 12.1461 15.1348 12.4063L21.6098 13.9371C21.675 13.9525 21.7069 14.0264 21.6734 14.0844L20.3591 16.3608C19.0403 18.645 15.9107 19.0499 14.054 17.1766L11.9516 15.0554ZM11.3306 13.5C12.159 13.5 12.8306 12.8284 12.8306 12C12.8306 11.1716 12.159 10.5 11.3306 10.5C10.5021 10.5 9.83057 11.1716 9.83057 12C9.83057 12.8284 10.5021 13.5 11.3306 13.5Z" style="fill: var(--automation-device-primary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};L1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Bm([h({type:Boolean})],L1.prototype,"useCssColor",2);L1=Bm([L("obi-fan-off")],L1);var Gy=Object.getOwnPropertyDescriptor,Yy=(e,t,o,r)=>{for(var i=r>1?void 0:r?Gy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=n(i)||i);return i},Im=class extends Gt{get icon(){return this.on?f`<obi-fan-on usecsscolor slot="icon"></obi-fan-on>
        <obi-fan-on usecsscolor slot="icon-silhouette"></obi-fan-on>`:f`<obi-fan-off usecsscolor slot="icon"></obi-fan-off>
        <obi-fan-off usecsscolor slot="icon-silhouette"></obi-fan-off>`}};Im=Yy([L("obc-fan")],Im);var qy=Object.defineProperty,Xy=Object.getOwnPropertyDescriptor,Zm=(e,t,o,r)=>{for(var i=r>1?void 0:r?Xy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&qy(t,o,i),i},S1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M3.5547 5.03682L11 10.0004H13L20.4453 5.03682C21.1099 4.59378 22 5.07017 22 5.86887V18.1318C22 18.9305 21.1099 19.4069 20.4453 18.9639L13 14.0004H11L3.5547 18.9639C2.89015 19.4069 2 18.9305 2 18.1318V5.86887C2 5.07017 2.89015 4.59378 3.5547 5.03682Z" fill="currentColor"/>
<path d="M10.6972 10.9996H13.3028L21 5.86816V18.1311L13.3028 12.9996H10.6972L3 18.1311V5.86816L10.6972 10.9996Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M3.5547 5.03682L11 10.0004H13L20.4453 5.03682C21.1099 4.59378 22 5.07017 22 5.86887V18.1318C22 18.9305 21.1099 19.4069 20.4453 18.9639L13 14.0004H11L3.5547 18.9639C2.89015 19.4069 2 18.9305 2 18.1318V5.86887C2 5.07017 2.89015 4.59378 3.5547 5.03682Z" style="fill: var(--automation-device-tertiary-color)"/>
<path d="M10.6972 10.9996H13.3028L21 5.86816V18.1311L13.3028 12.9996H10.6972L3 18.1311V5.86816L10.6972 10.9996Z" style="fill: var(--automation-device-primary-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};S1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Zm([h({type:Boolean})],S1.prototype,"useCssColor",2);S1=Zm([L("obi-twoway-digital-open")],S1);var Ky=Object.defineProperty,Qy=Object.getOwnPropertyDescriptor,Fm=(e,t,o,r)=>{for(var i=r>1?void 0:r?Qy(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ky(t,o,i),i},M1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M14 13.4645V10.5348L21 5.86816V18.1311L14 13.4645Z" fill="currentColor"/>
<path d="M3 18.1311L10 13.4645V10.5348L3 5.86816V18.1311Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 10.5355V13.4652L21 18.1318V5.86887L14 10.5355ZM13 14.0004V10.0004L20.4453 5.03682C21.1099 4.59378 22 5.07017 22 5.86887V18.1318C22 18.9305 21.1099 19.4069 20.4453 18.9639L13 14.0004ZM10 13.4652L3 18.1318L3 5.86887L10 10.5355V13.4652ZM11 10.0004L3.5547 5.03682C2.89015 4.59378 2 5.07017 2 5.86887V18.1318C2 18.9305 2.89015 19.4069 3.5547 18.9639L11 14.0004V10.0004Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M14 13.4645V10.5348L21 5.86816V18.1311L14 13.4645Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path d="M3 18.1311L10 13.4645V10.5348L3 5.86816V18.1311Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M14 10.5355V13.4652L21 18.1318V5.86887L14 10.5355ZM13 14.0004V10.0004L20.4453 5.03682C21.1099 4.59378 22 5.07017 22 5.86887V18.1318C22 18.9305 21.1099 19.4069 20.4453 18.9639L13 14.0004ZM10 13.4652L3 18.1318L3 5.86887L10 10.5355V13.4652ZM11 10.0004L3.5547 5.03682C2.89015 4.59378 2 5.07017 2 5.86887V18.1318C2 18.9305 2.89015 19.4069 3.5547 18.9639L11 14.0004V10.0004Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};M1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Fm([h({type:Boolean})],M1.prototype,"useCssColor",2);M1=Fm([L("obi-twoway-digital-closed")],M1);var Jy=Object.defineProperty,eC=Object.getOwnPropertyDescriptor,$1=(e,t,o,r)=>{for(var i=r>1?void 0:r?eC(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Jy(t,o,i),i};var $a=class extends Te{constructor(){super(...arguments),this.open=!1,this.vertical=!1,this.variant="regular"}get _on(){return this.open}get extraReadouts(){return this.showStatus?this.open?[{type:"state-on",value:"On",hasIcon:!0}]:[{type:"state-off",value:"Off",hasIcon:!0}]:[]}get icon(){let e=this.vertical?"transform: rotate(90deg);":"";return this.open?f` <obi-twoway-digital-open
          usecsscolor
          slot="icon"
          style="display: block; ${e} line-height: 0;"
        ></obi-twoway-digital-open>
        <obi-twoway-digital-open
          usecsscolor
          slot="icon-silhouette"
          style="display: block; ${e} line-height: 0;"
        ></obi-twoway-digital-open>`:f` <obi-twoway-digital-closed
          usecsscolor
          slot="icon"
          style="display: block; ${e} line-height: 0;"
        ></obi-twoway-digital-closed>
        <obi-twoway-digital-closed
          usecsscolor
          slot="icon-silhouette"
          style="display: block; ${e} line-height: 0;"
        ></obi-twoway-digital-closed>`}};$1([h({type:Boolean})],$a.prototype,"open",2);$1([h({type:Boolean})],$a.prototype,"vertical",2);$1([h({type:String})],$a.prototype,"variant",2);$a=$1([L("obc-digital-valve")],$a);var Nm=M`* {
  -webkit-tap-highlight-color: transparent;
}

.wrapper {
  height: 100%;
  width: 100%;
  line-height: 0;
}

.wrapper > * {
  height: 100%;
  width: 100%;
}
`;var tC=Object.defineProperty,oC=Object.getOwnPropertyDescriptor,jm=(e,t,o,r)=>{for(var i=r>1?void 0:r?oC(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&tC(t,o,i),i},A1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M13 11V15L20.4453 19.9635C21.1099 20.4066 22 19.9302 22 19.1315V6.8685C22 6.06981 21.1099 5.59342 20.4453 6.03645L13 11ZM14 14.4648V11.5352L21 6.8685V19.1315L14 14.4648Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3.5547 6.03645L11 11V15L3.5547 19.9635C2.89015 20.4066 2 19.9302 2 19.1315V6.8685C2 6.06981 2.89015 5.59342 3.5547 6.03645ZM3 19.1315L10 14.4648V11.5352L3 6.8685L3 19.1315Z" fill="currentColor"/>
<path d="M13 3C13 2.44772 12.5523 2 12 2C11.4477 2 11 2.44772 11 3V8C11 8.55228 11.4477 9 12 9C12.5523 9 13 8.55228 13 8V3ZM14 8C14 9.10457 13.1046 10 12 10C10.8954 10 10 9.10457 10 8V3C10 1.89543 10.8954 1 12 1C13.1046 1 14 1.89543 14 3V8Z" fill="currentColor"/>
<path d="M14 14.4645V11.5348L21 6.86816V19.1311L14 14.4645Z" fill="currentColor"/>
<path d="M3 19.1311L10 14.4645V11.5348L3 6.86816V19.1311Z" fill="currentColor"/>
<path d="M11 8C11 8.55228 11.4477 9 12 9C12.5523 9 13 8.55228 13 8V3C13 2.44772 12.5523 2 12 2C11.4477 2 11 2.44772 11 3V8Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M13 11V15L20.4453 19.9635C21.1099 20.4066 22 19.9302 22 19.1315V6.8685C22 6.06981 21.1099 5.59342 20.4453 6.03645L13 11ZM14 14.4648V11.5352L21 6.8685V19.1315L14 14.4648Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M3.5547 6.03645L11 11V15L3.5547 19.9635C2.89015 20.4066 2 19.9302 2 19.1315V6.8685C2 6.06981 2.89015 5.59342 3.5547 6.03645ZM3 19.1315L10 14.4648V11.5352L3 6.8685L3 19.1315Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path d="M13 3C13 2.44772 12.5523 2 12 2C11.4477 2 11 2.44772 11 3V8C11 8.55228 11.4477 9 12 9C12.5523 9 13 8.55228 13 8V3ZM14 8C14 9.10457 13.1046 10 12 10C10.8954 10 10 9.10457 10 8V3C10 1.89543 10.8954 1 12 1C13.1046 1 14 1.89543 14 3V8Z" style="fill: var(--automation-device-tertiary-inverted-color)"/>
<path d="M14 14.4645V11.5348L21 6.86816V19.1311L14 14.4645Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path d="M3 19.1311L10 14.4645V11.5348L3 6.86816V19.1311Z" style="fill: var(--automation-device-primary-inverted-color)"/>
<path d="M11 8C11 8.55228 11.4477 9 12 9C12.5523 9 13 8.55228 13 8V3C13 2.44772 12.5523 2 12 2C11.4477 2 11 2.44772 11 3V8Z" style="fill: var(--automation-device-primary-inverted-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};A1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;jm([h({type:Boolean})],A1.prototype,"useCssColor",2);A1=jm([L("obi-twoway-analog-closed")],A1);var rC=Object.defineProperty,iC=Object.getOwnPropertyDescriptor,P1=(e,t,o,r)=>{for(var i=r>1?void 0:r?iC(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&rC(t,o,i),i},dn=class extends S{constructor(){super(...arguments),this.value=0,this.closed=!1,this.vertical=!1}render(){let e=this.vertical?"transform: rotate(90deg);":"";if(this.closed)return f` <div class="wrapper" style="${e}">
        <obi-twoway-analog-closed useCssColor> </obi-twoway-analog-closed>
      </div>`;let t=-(1-this.value/100)*90,o=(1-this.value/100)*2,r=w`
      <g transform="translate(0, ${o}) rotate(${t} 12 3.5) ">
        <path fill-rule="evenodd" clip-rule="evenodd" d="M9.5 5H14.5C15.3284 5 16 4.32843 16 3.5C16 2.67157 15.3284 2 14.5 2H9.5C8.67157 2 8 2.67157 8 3.5C8 4.32843 8.67157 5 9.5 5ZM9.5 4L14.5 4C14.7761 4 15 3.77614 15 3.5C15 3.22386 14.7761 3 14.5 3L9.5 3C9.22386 3 9 3.22386 9 3.5C9 3.77614 9.22386 4 9.5 4Z" fill="var(--automation-device-tertiary-color)"/>
        <path d="M9.5 4L14.5 4C14.7761 4 15 3.77614 15 3.5C15 3.22386 14.7761 3 14.5 3L9.5 3C9.22386 3 9 3.22386 9 3.5C9 3.77614 9.22386 4 9.5 4Z" fill="var(--automation-device-primary-color)"/>
      </g>
    `,i=10.5,s=2.5,n=i+(s-i)*this.value/100;return f`
      <div class="wrapper" style="${e}">
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M11 11L3.5547 6.03645C2.89015 5.59342 2 6.06981 2 6.8685V19.1315C2 19.9302 2.89015 20.4066 3.5547 19.9635L11 15H13L20.4453 19.9635C21.1099 20.4066 22 19.9302 22 19.1315V6.8685C22 6.06981 21.1099 5.59342 20.4453 6.03645L13 11H11ZM3 6.8685L3 19.1315L10.6972 14H13.3028L21 19.1315V6.8685L13.3028 12H10.6972L3 6.8685Z"
            fill="var(--automation-device-tertiary-color)"
          />
          <path
            d="M10.6972 12H13.3028L21 6.8685V19.1315L13.3028 14H10.6972L3 19.1315V6.8685L10.6972 12Z"
            fill="var(--automation-device-primary-color)"
          />
          ${r}
          <g clip-path="url(#clip0)">
            <rect
              x=${s}
              y="0"
              width=${n-s}
              height="24"
              fill="var(--automation-device-secondary-color)"
            />
            <line
              x1=${n}
              y1="0"
              x2=${n}
              y2="24"
              stroke="var(--automation-device-tertiary-color)"
              stroke-width="1"
            />

            <rect
              x=${24-n}
              y="0"
              width=${n-s}
              height="24"
              fill="var(--automation-device-secondary-color)"
            />
            <line
              x1=${24-n}
              y1="0"
              x2=${24-n}
              y2="24"
              stroke="var(--automation-device-tertiary-color)"
              stroke-width="1"
            />
          </g>
          <defs>
            <clipPath id="clip0">
              <path
                d="M10.6972 12H13.3028L21 6.8685V19.1315L13.3028 14H10.6972L3 19.1315V6.8685L10.6972 12Z"
              />
            </clipPath>
          </defs>
        </svg>
      </div>
    `}};dn.styles=ne(Nm);P1([h({type:Number})],dn.prototype,"value",2);P1([h({type:Boolean})],dn.prototype,"closed",2);P1([h({type:Boolean})],dn.prototype,"vertical",2);dn=P1([L("obc-valve-analog-two-way-icon")],dn);var sC=Object.defineProperty,nC=Object.getOwnPropertyDescriptor,hn=(e,t,o,r)=>{for(var i=r>1?void 0:r?nC(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&sC(t,o,i),i};var is=class extends Te{constructor(){super(...arguments),this.open=!1,this.value=0,this.vertical=!1,this.labelDirection=Gi.right,this.variant="regular"}get extraReadouts(){return this.showStatus?this.open?[{type:"value",icon:this.labelDirection===Gi.none?"none":"arrow",value:this.value,nDigits:3,unit:"%",direction:this.labelDirection}]:[{type:"state-off",value:"Off",hasIcon:!0}]:[]}get _on(){return this.open}get icon(){return f`<obc-valve-analog-two-way-icon
        .value=${this.value}
        .closed=${!this.open}
        .vertical=${this.vertical}
        slot="icon"
      ></obc-valve-analog-two-way-icon>
      <obc-valve-analog-two-way-icon
        .value=${this.value}
        .closed=${!this.open}
        .vertical=${this.vertical}
        slot="icon-silhouette"
      ></obc-valve-analog-two-way-icon> `}};hn([h({type:Boolean})],is.prototype,"open",2);hn([h({type:Number})],is.prototype,"value",2);hn([h({type:Boolean})],is.prototype,"vertical",2);hn([h({type:String})],is.prototype,"labelDirection",2);hn([h({type:String})],is.prototype,"variant",2);is=hn([L("obc-analog-valve")],is);var Wm=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: block;
}

.transmitter {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
}

.transmitter.orientation-bottom {
    padding-top: 8px;
    top: calc(1px + var(--offset));
    transform: translateX(-50%);
  }

.transmitter.orientation-top {
    padding-bottom: 8px;
    transform: translate(-50%, calc(-100% - 1px - var(--offset)));
  }

.transmitter.orientation-left {
    padding-right: 8px;
    transform: translate(calc(-100% - 4px - var(--offset)), -50%);
  }

.transmitter.orientation-right {
    padding-left: 8px;
    transform: translateY(-50%);
    right: calc(-4px - var(--offset));
  }

.transmitter::before {
    content: "";
    display: block;
    position: absolute;
    border: var(--normal-enabled-border-color) solid 1px;
  }

.transmitter.orientation-bottom::before,.transmitter.orientation-top::before {
    width: 0;
    height: 8px;
  }

.transmitter.orientation-bottom::before {
    top: -1px;
  }

.transmitter.orientation-top::before {
    bottom: -1px;
  }

.transmitter.orientation-left::before,.transmitter.orientation-right::before {
    height: 0;
    width: 8px;
  }

.transmitter.orientation-left::before {
    right: -4px;
  }

.transmitter.orientation-right::before {
    left: -4px;
  }

.content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.alert-frame .content {
  padding: 4px;
}

/* Top orientation places the id-tag above the chip (leader line below). */

.orientation-top .content {
  flex-direction: column-reverse;
}

.body {
  display: flex;
}

.type-horizontal-graph .body {
  flex-direction: row;
  align-items: stretch;
}

.type-vertical-graph .body {
  flex-direction: column;
  align-items: stretch;
}

.graph-box {
  overflow: hidden;
  border: 1px solid var(--instrument-regular-tertiary-color);
}

.type-horizontal-graph .graph-box {
  width: 64px;
  border-left: none;
  border-radius: 0 4px 4px 0;
}

.type-vertical-graph .graph-box {
  height: 48px;
  border-top: none;
  border-radius: 0 0 4px 4px;
}

/* Flatten the chip corners and drop the shared border where the graph joins. */

.type-horizontal-graph .chip::part(button) {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-right: none;
}

.type-vertical-graph .chip::part(button) {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  border-bottom: none;
}

.type-vertical-graph .chip {
  width: 100%;
}

.id-tag {
  color: var(--element-neutral-color);
  color: var(--element-neutral-color);
  font-variant-numeric: lining-nums tabular-nums;
  font-feature-settings: "ss04" on;
  font-family: var(--global-typography-font-family);
  font-size: var(--global-typography-instrument-label-font-size);
  font-style: normal;
  font-weight: 570;
  line-height: var(--global-typography-instrument-label-line-height);
}
`;var Um=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: inline-block;
}

.button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  padding: 0;
  appearance: none;
  background: none;
  border: none;
  cursor: pointer;
}

.button {
  cursor: pointer;
}

.button:focus {
  outline: none;
}

.button .visible-wrapper {
  border-color: var(--normal-enabled-border-color);
  background-color: var(--normal-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--normal-enabled-border-color);
  --base-background-color: var(--normal-enabled-background-color);
}

.button.activated .visible-wrapper {
  border-color: var(--normal-activated-border-color);
  background-color: var(--normal-activated-background-color);
  --base-border-color: var(--normal-activated-border-color);
  --base-background-color: var(--normal-activated-background-color);
}

@media (hover:hover) {

.button:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--normal-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--normal-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.button:active .visible-wrapper {
  border-color: var(--normal-pressed-border-color);
  background-color: var(--normal-pressed-background-color);
}

.button:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.button:disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.button.disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.button:disabled {
  cursor: not-allowed;
}

.button.disabled {
  cursor: not-allowed;
}

.visible-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 4px;
  border: 1px solid var(--normal-enabled-border-color);
  border-radius: 4px;
}

.value-container {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 0 2px;
}

.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.unit {
  font-family: var(--global-typography-font-family);
  font-size: var(--global-typography-instrument-unit-font-size);
  line-height: var(--global-typography-instrument-unit-line-height);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  align-self: flex-end;
  color: var(--element-neutral-color);
}

.size-regular .icon ::slotted(*) {
  width: 16px;
  height: 16px;
}

.size-medium .icon ::slotted(*) {
  width: 20px;
  height: 20px;
}

.size-large .icon ::slotted(*) {
  width: 24px;
  height: 24px;
}

.size-medium .visible-wrapper:not(.tag),
.size-large .visible-wrapper:not(.tag) {
  padding: 4px 8px;
  border-radius: 6px;
}

.visible-wrapper.tag {
  min-height: 24px;
  padding: 2px 8px;
  border-radius: 100px;
  background-color: var(--container-section-color);
}

.label {
  font-family: var(--global-typography-font-family);
  font-size: var(--global-typography-instrument-value-regular-font-size);
  line-height: var(--global-typography-instrument-value-regular-line-height);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  color: var(--element-neutral-color);
}
`;var aC=Object.defineProperty,lC=Object.getOwnPropertyDescriptor,ro=(e,t,o,r)=>{for(var i=r>1?void 0:r?lC(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&aC(t,o,i),i},O1=(e=>(e.value="value",e.tag="tag",e))(O1||{}),Op=(e=>(e.regular="regular",e.medium="medium",e.large="large",e))(Op||{}),cC={regular:Sr.small,medium:Sr.medium,large:Sr.large},Nt=class extends S{constructor(){super(...arguments),this.variant="value",this.size="regular",this.unit="",this.fractionDigits=1,this.maxDigits=0,this.hintedZeros=!1,this.hasSignSpacer=!1,this.hasIcon=!1,this.hasAdvice=!1,this.hasSetPoint=!1,this.label=""}get isTag(){return this.variant==="tag"}renderBlock(e,t){return f`<obc-readout-block
      .variant=${e}
      .value=${t??null}
      .size=${cC[this.size]}
      .fractionDigits=${this.fractionDigits}
      .maxDigits=${this.maxDigits}
      .hintedZeros=${this.hintedZeros}
      .hasSignSpacer=${this.hasSignSpacer}
    ></obc-readout-block>`}renderAdvice(){return this.hasAdvice?this.renderBlock(Nn.advice,this.adviceValue):z}renderSetpoint(){return this.hasSetPoint?this.renderBlock(Nn.setpoint,this.setpointValue):z}renderContent(){return this.isTag?f`<span class="label">${this.label}</span>`:f`
      ${this.renderAdvice()} ${this.renderSetpoint()}
      <div class="value-container">
        ${this.hasIcon?f`<div class="icon"><slot name="icon"></slot></div>`:z}
        ${this.renderBlock(Nn.value,this.value)}
        ${this.unit?f`<span class="unit">${this.unit}</span>`:z}
      </div>
    `}render(){return f`
      <button type="button" class="button ${this.variant} size-${this.size}">
        <div
          part="button"
          class=${de({"visible-wrapper":!0,tag:this.isTag})}
        >
          ${this.renderContent()}
        </div>
      </button>
    `}};Nt.styles=ne(Um);ro([h({type:String})],Nt.prototype,"variant",2);ro([h({type:String})],Nt.prototype,"size",2);ro([h({type:Number})],Nt.prototype,"value",2);ro([h({type:String})],Nt.prototype,"unit",2);ro([h({type:Number})],Nt.prototype,"fractionDigits",2);ro([h({type:Number})],Nt.prototype,"maxDigits",2);ro([h({type:Boolean})],Nt.prototype,"hintedZeros",2);ro([h({type:Boolean})],Nt.prototype,"hasSignSpacer",2);ro([h({type:Boolean})],Nt.prototype,"hasIcon",2);ro([h({type:Boolean})],Nt.prototype,"hasAdvice",2);ro([h({type:Number})],Nt.prototype,"adviceValue",2);ro([h({type:Boolean})],Nt.prototype,"hasSetPoint",2);ro([h({type:Number})],Nt.prototype,"setpointValue",2);ro([h({type:String})],Nt.prototype,"label",2);Nt=ro([L("obc-transmitter-button")],Nt);var Gm=M`* {
  -webkit-tap-highlight-color: transparent;
}

.chart-container {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;

  padding-bottom: 0.5px;

  --dot-width: 6px;
  --dot-radius: calc(var(--dot-width) / 2);
}

.chart-container.medium {
    --dot-width: 8px;
  }

.chart-container.large {
    --dot-width: 10px;
  }

.u-over {
  position: absolute;
}

#chart {
  position: absolute;
  width: calc(100% - var(--dot-radius));
  left: 0;
  top: var(--dot-radius);
  bottom: var(--dot-radius);
}

canvas {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

#dot {
  box-sizing: border-box;
  position: absolute;
  width: var(--dot-width);
  height: var(--dot-width);
  right: 0;
  bottom: 0;
  border-radius: 50%;
  background: var(--element-neutral-color);
  border: 1px solid var(--border-silhouette-color);
  z-index: 1;
}

.enhanced #dot {
  background: var(--element-neutral-enhanced-color);
}

#zero-line {
  position: absolute;
  left: 0;
  right: var(--dot-radius);
  height: 1px;
  bottom: calc(var(--dot-radius) - 0.5px);
  background: var(--element-disabled-color);
  border-radius: 2px;
}
`;var dC="uplot",hC="u-hz",pC="u-vt",uC="u-title",fC="u-wrap",gC="u-under",mC="u-over",vC="u-axis",as="u-off",bC="u-select",wC="u-cursor-x",yC="u-cursor-y",CC="u-cursor-pt",xC="u-legend",_C="u-live",kC="u-inline",LC="u-series",SC="u-marker",Ym="u-label",MC="u-value",Pa="width",Oa="height";var qm="bottom",pn="left",Vp="right",qp="#000",Xm=qp+"0",Tp="mousemove",Km="mousedown",Dp="mouseup",Qm="mouseenter",Jm="mouseleave",e4="dblclick",$C="resize",AC="scroll",t4="change",R1="dppxchange",Xp="--",wn=typeof window<"u",Bp=wn?document:null,fn=wn?window:null,PC=wn?navigator:null,He,V1;function Ip(){let e=devicePixelRatio;He!=e&&(He=e,V1&&Fp(t4,V1,Ip),V1=matchMedia(`(min-resolution: ${He-.001}dppx) and (max-resolution: ${He+.001}dppx)`),ls(t4,V1,Ip),fn.dispatchEvent(new CustomEvent(R1)))}function So(e,t){if(t!=null){let o=e.classList;!o.contains(t)&&o.add(t)}}function Zp(e,t){let o=e.classList;o.contains(t)&&o.remove(t)}function st(e,t,o){e.style[t]=o+"px"}function Qo(e,t,o,r){let i=Bp.createElement(e);return t!=null&&So(i,t),o?.insertBefore(i,r),i}function Zo(e,t){return Qo("div",e,t)}var o4=new WeakMap;function pr(e,t,o,r,i){let s="translate("+t+"px,"+o+"px)",n=o4.get(e);s!=n&&(e.style.transform=s,o4.set(e,s),t<0||o<0||t>r||o>i?So(e,as):Zp(e,as))}var r4=new WeakMap;function i4(e,t,o){let r=t+o,i=r4.get(e);r!=i&&(r4.set(e,r),e.style.background=t,e.style.borderColor=o)}var s4=new WeakMap;function n4(e,t,o,r){let i=t+""+o,s=s4.get(e);i!=s&&(s4.set(e,i),e.style.height=o+"px",e.style.width=t+"px",e.style.marginLeft=r?-t/2+"px":0,e.style.marginTop=r?-o/2+"px":0)}var Kp={passive:!0},OC={...Kp,capture:!0};function ls(e,t,o,r){t.addEventListener(e,o,r?OC:Kp)}function Fp(e,t,o,r){t.removeEventListener(e,o,Kp)}wn&&Ip();function Jo(e,t,o,r){let i;o=o||0,r=r||t.length-1;let s=r<=2147483647;for(;r-o>1;)i=s?o+r>>1:Mo((o+r)/2),t[i]<e?o=i:r=i;return e-t[o]<=t[r]-e?o:r}function D4(e){return(o,r,i)=>{let s=-1,n=-1;for(let a=r;a<=i;a++)if(e(o[a])){s=a;break}for(let a=i;a>=r;a--)if(e(o[a])){n=a;break}return[s,n]}}var E4=e=>e!=null,R4=e=>e!=null&&e>0,B1=D4(E4),VC=D4(R4);function TC(e,t,o,r=0,i=!1){let s=i?VC:B1,n=i?R4:E4;[t,o]=s(e,t,o);let a=e[t],l=e[t];if(t>-1)if(r==1)a=e[t],l=e[o];else if(r==-1)a=e[o],l=e[t];else for(let c=t;c<=o;c++){let d=e[c];n(d)&&(d<a?a=d:d>l&&(l=d))}return[a??qe,l??-qe]}function I1(e,t,o,r){let i=c4(e),s=c4(t);e==t&&(i==-1?(e*=o,t/=o):(e/=o,t*=o));let n=o==10?Ir:z4,a=i==1?Mo:Fo,l=s==1?Fo:Mo,c=a(n($t(e))),d=l(n($t(t))),p=gn(o,c),u=gn(o,d);return o==10&&(c<0&&(p=Xe(p,-c)),d<0&&(u=Xe(u,-d))),r||o==2?(e=p*i,t=u*s):(e=Z4(e,p),t=Z1(t,u)),[e,t]}function Qp(e,t,o,r){let i=I1(e,t,o,r);return e==0&&(i[0]=0),t==0&&(i[1]=0),i}var Jp=.1,a4={mode:3,pad:Jp},Ta={pad:0,soft:null,mode:0},DC={min:Ta,max:Ta};function z1(e,t,o,r){return F1(o)?l4(e,t,o):(Ta.pad=o,Ta.soft=r?0:null,Ta.mode=r?3:0,l4(e,t,DC))}function Ee(e,t){return e??t}function EC(e,t,o){for(t=Ee(t,0),o=Ee(o,e.length-1);t<=o;){if(e[t]!=null)return!0;t++}return!1}function l4(e,t,o){let r=o.min,i=o.max,s=Ee(r.pad,0),n=Ee(i.pad,0),a=Ee(r.hard,-qe),l=Ee(i.hard,qe),c=Ee(r.soft,qe),d=Ee(i.soft,-qe),p=Ee(r.mode,0),u=Ee(i.mode,0),m=t-e,b=Ir(m),C=io($t(e),$t(t)),y=Ir(C),k=$t(y-b);(m<1e-24||k>10)&&(m=0,(e==0||t==0)&&(m=1e-24,p==2&&c!=qe&&(s=0),u==2&&d!=-qe&&(n=0)));let $=m||C||1e3,V=Ir($),O=gn(10,Mo(V)),P=$*(m==0?e==0?.1:1:s),T=Xe(Z4(e-P,O/10),24),Z=e>=c&&(p==1||p==3&&T<=c||p==2&&T>=c)?c:qe,R=io(a,T<Z&&e>=Z?Z:er(Z,T)),D=$*(m==0?t==0?.1:1:n),N=Xe(Z1(t+D,O/10),24),B=t<=d&&(u==1||u==3&&N>=d||u==2&&N<=d)?d:-qe,Y=er(l,N>B&&t<=B?B:io(B,N));return R==Y&&R==0&&(Y=100),[R,Y]}var RC=new Intl.NumberFormat(wn?PC.language:"en-US"),eu=e=>RC.format(e),$o=Math,E1=$o.PI,$t=$o.abs,Mo=$o.floor,Mt=$o.round,Fo=$o.ceil,er=$o.min,io=$o.max,gn=$o.pow,c4=$o.sign,Ir=$o.log10,z4=$o.log2,zC=(e,t=1)=>$o.sinh(e)*t,Ep=(e,t=1)=>$o.asinh(e/t),qe=1/0;function d4(e){return(Ir((e^e>>31)-(e>>31))|0)+1}function Np(e,t,o){return er(io(e,t),o)}function H4(e){return typeof e=="function"}function Oe(e){return H4(e)?e:()=>e}var HC=()=>{},B4=e=>e,I4=(e,t)=>t,BC=e=>null,h4=e=>!0,p4=(e,t)=>e==t,IC=/\.\d*?(?=9{6,}|0{6,})/gm,cs=e=>{if(N4(e)||wi.has(e))return e;let t=`${e}`,o=t.match(IC);if(o==null)return e;let r=o[0].length-1;if(t.indexOf("e-")!=-1){let[i,s]=t.split("e");return+`${cs(i)}e${s}`}return Xe(e,r)};function ss(e,t){return cs(Xe(cs(e/t))*t)}function Z1(e,t){return cs(Fo(cs(e/t))*t)}function Z4(e,t){return cs(Mo(cs(e/t))*t)}function Xe(e,t=0){if(N4(e))return e;let o=10**t,r=e*o*(1+Number.EPSILON);return Mt(r)/o}var wi=new Map;function F4(e){return((""+e).split(".")[1]||"").length}function Ea(e,t,o,r){let i=[],s=r.map(F4);for(let n=t;n<o;n++){let a=$t(n),l=Xe(gn(e,n),a);for(let c=0;c<r.length;c++){let d=e==10?+`${r[c]}e${n}`:r[c]*l,p=(n>=0?0:a)+(n>=s[c]?0:s[c]),u=e==10?d:Xe(d,p);i.push(u),wi.set(u,p)}}return i}var Da={},tu=[],mn=[null,null],bi=Array.isArray,N4=Number.isInteger,ZC=e=>e===void 0;function u4(e){return typeof e=="string"}function F1(e){let t=!1;if(e!=null){let o=e.constructor;t=o==null||o==Object}return t}function FC(e){return e!=null&&typeof e=="object"}var NC=Object.getPrototypeOf(Uint8Array),j4="__proto__";function vn(e,t=F1){let o;if(bi(e)){let r=e.find(i=>i!=null);if(bi(r)||t(r)){o=Array(e.length);for(let i=0;i<e.length;i++)o[i]=vn(e[i],t)}else o=e.slice()}else if(e instanceof NC)o=e.slice();else if(t(e)){o={};for(let r in e)r!=j4&&(o[r]=vn(e[r],t))}else o=e;return o}function xt(e){let t=arguments;for(let o=1;o<t.length;o++){let r=t[o];for(let i in r)i!=j4&&(F1(e[i])?xt(e[i],vn(r[i])):e[i]=vn(r[i]))}return e}var jC=0,WC=1,UC=2;function GC(e,t,o){for(let r=0,i,s=-1;r<t.length;r++){let n=t[r];if(n>s){for(i=n-1;i>=0&&e[i]==null;)e[i--]=null;for(i=n+1;i<o&&e[i]==null;)e[s=i++]=null}}}function YC(e,t){if(KC(e)){let n=e[0].slice();for(let a=1;a<e.length;a++)n.push(...e[a].slice(1));return QC(n[0])||(n=XC(n)),n}let o=new Set;for(let n=0;n<e.length;n++){let l=e[n][0],c=l.length;for(let d=0;d<c;d++)o.add(l[d])}let r=[Array.from(o).sort((n,a)=>n-a)],i=r[0].length,s=new Map;for(let n=0;n<i;n++)s.set(r[0][n],n);for(let n=0;n<e.length;n++){let a=e[n],l=a[0];for(let c=1;c<a.length;c++){let d=a[c],p=Array(i).fill(void 0),u=t?t[n][c]:WC,m=[];for(let b=0;b<d.length;b++){let C=d[b],y=s.get(l[b]);C===null?u!=jC&&(p[y]=C,u==UC&&m.push(y)):p[y]=C}GC(p,m,i),r.push(p)}}return r}var qC=typeof queueMicrotask>"u"?e=>Promise.resolve().then(e):queueMicrotask;function XC(e){let t=e[0],o=t.length,r=Array(o);for(let s=0;s<r.length;s++)r[s]=s;r.sort((s,n)=>t[s]-t[n]);let i=[];for(let s=0;s<e.length;s++){let n=e[s],a=Array(o);for(let l=0;l<o;l++)a[l]=n[r[l]];i.push(a)}return i}function KC(e){let t=e[0][0],o=t.length;for(let r=1;r<e.length;r++){let i=e[r][0];if(i.length!=o)return!1;if(i!=t){for(let s=0;s<o;s++)if(i[s]!=t[s])return!1}}return!0}function QC(e,t=100){let o=e.length;if(o<=1)return!0;let r=0,i=o-1;for(;r<=i&&e[r]==null;)r++;for(;i>=r&&e[i]==null;)i--;if(i<=r)return!0;let s=io(1,Mo((i-r+1)/t));for(let n=e[r],a=r+s;a<=i;a+=s){let l=e[a];if(l!=null){if(l<=n)return!1;n=l}}return!0}var W4=["January","February","March","April","May","June","July","August","September","October","November","December"],U4=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];function G4(e){return e.slice(0,3)}var JC=U4.map(G4),ex=W4.map(G4),tx={MMMM:W4,MMM:ex,WWWW:U4,WWW:JC};function Aa(e){return(e<10?"0":"")+e}function ox(e){return(e<10?"00":e<100?"0":"")+e}var rx={YYYY:e=>e.getFullYear(),YY:e=>(e.getFullYear()+"").slice(2),MMMM:(e,t)=>t.MMMM[e.getMonth()],MMM:(e,t)=>t.MMM[e.getMonth()],MM:e=>Aa(e.getMonth()+1),M:e=>e.getMonth()+1,DD:e=>Aa(e.getDate()),D:e=>e.getDate(),WWWW:(e,t)=>t.WWWW[e.getDay()],WWW:(e,t)=>t.WWW[e.getDay()],HH:e=>Aa(e.getHours()),H:e=>e.getHours(),h:e=>{let t=e.getHours();return t==0?12:t>12?t-12:t},AA:e=>e.getHours()>=12?"PM":"AM",aa:e=>e.getHours()>=12?"pm":"am",a:e=>e.getHours()>=12?"p":"a",mm:e=>Aa(e.getMinutes()),m:e=>e.getMinutes(),ss:e=>Aa(e.getSeconds()),s:e=>e.getSeconds(),fff:e=>ox(e.getMilliseconds())};function ou(e,t){t=t||tx;let o=[],r=/\{([a-z]+)\}|[^{]+/gi,i;for(;i=r.exec(e);)o.push(i[0][0]=="{"?rx[i[1]]:i[0]);return s=>{let n="";for(let a=0;a<o.length;a++)n+=typeof o[a]=="string"?o[a]:o[a](s,t);return n}}var ix=new Intl.DateTimeFormat().resolvedOptions().timeZone;function sx(e,t){let o;return t=="UTC"||t=="Etc/UTC"?o=new Date(+e+e.getTimezoneOffset()*6e4):t==ix?o=e:(o=new Date(e.toLocaleString("en-US",{timeZone:t})),o.setMilliseconds(e.getMilliseconds())),o}var Y4=e=>e%1==0,H1=[1,2,2.5,5],nx=Ea(10,-32,0,H1),q4=Ea(10,0,32,H1),ax=q4.filter(Y4),ns=nx.concat(q4),ru=`
`,X4="{YYYY}",f4=ru+X4,K4="{M}/{D}",Va=ru+K4,T1=Va+"/{YY}",Q4="{aa}",lx="{h}:{mm}",un=lx+Q4,g4=ru+un,m4=":{ss}",je=null;function J4(e){let t=e*1e3,o=t*60,r=o*60,i=r*24,s=i*30,n=i*365,l=(e==1?Ea(10,0,3,H1).filter(Y4):Ea(10,-3,0,H1)).concat([t,t*5,t*10,t*15,t*30,o,o*5,o*10,o*15,o*30,r,r*2,r*3,r*4,r*6,r*8,r*12,i,i*2,i*3,i*4,i*5,i*6,i*7,i*8,i*9,i*10,i*15,s,s*2,s*3,s*4,s*6,n,n*2,n*5,n*10,n*25,n*50,n*100]),c=[[n,X4,je,je,je,je,je,je,1],[i*28,"{MMM}",f4,je,je,je,je,je,1],[i,K4,f4,je,je,je,je,je,1],[r,"{h}"+Q4,T1,je,Va,je,je,je,1],[o,un,T1,je,Va,je,je,je,1],[t,m4,T1+" "+un,je,Va+" "+un,je,g4,je,1],[e,m4+".{fff}",T1+" "+un,je,Va+" "+un,je,g4,je,1]];function d(p){return(u,m,b,C,y,k)=>{let $=[],V=y>=n,O=y>=s&&y<n,P=p(b),T=Xe(P*e,3),Z=Rp(P.getFullYear(),V?0:P.getMonth(),O||V?1:P.getDate()),R=Xe(Z*e,3);if(O||V){let D=O?y/s:0,N=V?y/n:0,B=T==R?T:Xe(Rp(Z.getFullYear()+N,Z.getMonth()+D,1)*e,3),Y=new Date(Mt(B/e)),I=Y.getFullYear(),H=Y.getMonth();for(let W=0;B<=C;W++){let j=Rp(I+N*W,H+D*W,1),F=j-p(Xe(j*e,3));B=Xe((+j+F)*e,3),B<=C&&$.push(B)}}else{let D=y>=i?i:y,N=Mo(b)-Mo(T),B=R+N+Z1(T-R,D);$.push(B);let Y=p(B),I=Y.getHours()+Y.getMinutes()/o+Y.getSeconds()/r,H=y/r,W=u.axes[m]._space,j=k/W;for(;B=Xe(B+y,e==1?0:3),!(B>C);)if(H>1){let F=Mo(Xe(I+H,6))%24,le=p(B).getHours()-F;le>1&&(le=-1),B-=le*r,I=(I+H)%24;let ve=$[$.length-1];Xe((B-ve)/y,3)*j>=.7&&$.push(B)}else $.push(B)}return $}}return[l,c,d]}var[cx,dx,hx]=J4(1),[px,ux,fx]=J4(.001);Ea(2,-53,53,[1]);function v4(e,t){return e.map(o=>o.map((r,i)=>i==0||i==8||r==null?r:t(i==1||o[8]==0?r:o[1]+r)))}function b4(e,t){return(o,r,i,s,n)=>{let a=t.find(b=>n>=b[0])||t[t.length-1],l,c,d,p,u,m;return r.map(b=>{let C=e(b),y=C.getFullYear(),k=C.getMonth(),$=C.getDate(),V=C.getHours(),O=C.getMinutes(),P=C.getSeconds(),T=y!=l&&a[2]||k!=c&&a[3]||$!=d&&a[4]||V!=p&&a[5]||O!=u&&a[6]||P!=m&&a[7]||a[1];return l=y,c=k,d=$,p=V,u=O,m=P,T(C)})}}function gx(e,t){let o=ou(t);return(r,i,s,n,a)=>i.map(l=>o(e(l)))}function Rp(e,t,o){return new Date(e,t,o)}function w4(e,t){return t(e)}var mx="{YYYY}-{MM}-{DD} {h}:{mm}{aa}";function y4(e,t){return(o,r,i,s)=>s==null?Xp:t(e(r))}function vx(e,t){let o=e.series[t];return o.width?o.stroke(e,t):o.points.width?o.points.stroke(e,t):null}function bx(e,t){return e.series[t].fill(e,t)}var wx={show:!0,live:!0,isolate:!1,mount:HC,markers:{show:!0,width:2,stroke:vx,fill:bx,dash:"solid"},idx:null,idxs:null,values:[]};function yx(e,t){let o=e.cursor.points,r=Zo(),i=o.size(e,t);st(r,Pa,i),st(r,Oa,i);let s=i/-2;st(r,"marginLeft",s),st(r,"marginTop",s);let n=o.width(e,t,i);return n&&st(r,"borderWidth",n),r}function Cx(e,t){let o=e.series[t].points;return o._fill||o._stroke}function xx(e,t){let o=e.series[t].points;return o._stroke||o._fill}function _x(e,t){return e.series[t].points.size}var zp=[0,0];function kx(e,t,o){return zp[0]=t,zp[1]=o,zp}function D1(e,t,o,r=!0){return i=>{i.button==0&&(!r||i.target==t)&&o(i)}}function Hp(e,t,o,r=!0){return i=>{(!r||i.target==t)&&o(i)}}var Lx={show:!0,x:!0,y:!0,lock:!1,move:kx,points:{one:!1,show:yx,size:_x,width:0,stroke:xx,fill:Cx},bind:{mousedown:D1,mouseup:D1,click:D1,dblclick:D1,mousemove:Hp,mouseleave:Hp,mouseenter:Hp},drag:{setScale:!0,x:!0,y:!1,dist:0,uni:null,click:(e,t)=>{t.stopPropagation(),t.stopImmediatePropagation()},_x:!1,_y:!1},focus:{dist:(e,t,o,r,i)=>r-i,prox:-1,bias:0},hover:{skip:[void 0],prox:null,bias:0},left:-10,top:-10,idx:null,dataIdx:null,idxs:null,event:null},ev={show:!0,stroke:"rgba(0,0,0,0.07)",width:2},iu=xt({},ev,{filter:I4}),tv=xt({},iu,{size:10}),ov=xt({},ev,{show:!1}),su='12px system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"',rv="bold "+su,iv=1.5,C4={show:!0,scale:"x",stroke:qp,space:50,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:rv,side:2,grid:iu,ticks:tv,border:ov,font:su,lineGap:iv,rotate:0},Sx="Value",Mx="Time",x4={show:!0,scale:"x",auto:!1,sorted:1,min:qe,max:-qe,idxs:[]};function $x(e,t,o,r,i){return t.map(s=>s==null?"":eu(s))}function Ax(e,t,o,r,i,s,n){let a=[],l=wi.get(i)||0;o=n?o:Xe(Z1(o,i),l);for(let c=o;c<=r;c=Xe(c+i,l))a.push(Object.is(c,-0)?0:c);return a}function jp(e,t,o,r,i,s,n){let a=[],l=e.scales[e.axes[t].scale].log,c=l==10?Ir:z4,d=Mo(c(o));i=gn(l,d),l==10&&(i=ns[Jo(i,ns)]);let p=o,u=i*l;l==10&&(u=ns[Jo(u,ns)]);do a.push(p),p=p+i,l==10&&!wi.has(p)&&(p=Xe(p,wi.get(i))),p>=u&&(i=p,u=i*l,l==10&&(u=ns[Jo(u,ns)]));while(p<=r);return a}function Px(e,t,o,r,i,s,n){let l=e.scales[e.axes[t].scale].asinh,c=r>l?jp(e,t,io(l,o),r,i):[l],d=r>=0&&o<=0?[0]:[];return(o<-l?jp(e,t,io(l,-r),-o,i):[l]).reverse().map(u=>-u).concat(d,c)}var sv=/./,Ox=/[12357]/,Vx=/[125]/,_4=/1/,Wp=(e,t,o,r)=>e.map((i,s)=>t==4&&i==0||s%r==0&&o.test(i.toExponential()[i<0?1:0])?i:null);function Tx(e,t,o,r,i){let s=e.axes[o],n=s.scale,a=e.scales[n],l=e.valToPos,c=s._space,d=l(10,n),p=l(9,n)-d>=c?sv:l(7,n)-d>=c?Ox:l(5,n)-d>=c?Vx:_4;if(p==_4){let u=$t(l(1,n)-d);if(u<c)return Wp(t.slice().reverse(),a.distr,p,Fo(c/u)).reverse()}return Wp(t,a.distr,p,1)}function Dx(e,t,o,r,i){let s=e.axes[o],n=s.scale,a=s._space,l=e.valToPos,c=$t(l(1,n)-l(2,n));return c<a?Wp(t.slice().reverse(),3,sv,Fo(a/c)).reverse():t}function Ex(e,t,o,r){return r==null?Xp:t==null?"":eu(t)}var k4={show:!0,scale:"y",stroke:qp,space:30,gap:5,alignTo:1,size:50,labelGap:0,labelSize:30,labelFont:rv,side:3,grid:iu,ticks:tv,border:ov,font:su,lineGap:iv,rotate:0};function Rx(e,t){let o=3+(e||1)*2;return Xe(o*t,3)}function zx(e,t){let{scale:o,idxs:r}=e.series[0],i=e._data[0],s=e.valToPos(i[r[0]],o,!0),n=e.valToPos(i[r[1]],o,!0),a=$t(n-s),l=e.series[t],c=a/(l.points.space*He);return r[1]-r[0]<=c}var L4={scale:null,auto:!0,sorted:0,min:qe,max:-qe},nv=(e,t,o,r,i)=>i,S4={show:!0,auto:!0,sorted:0,gaps:nv,alpha:1,facets:[xt({},L4,{scale:"x"}),xt({},L4,{scale:"y"})]},M4={scale:"y",auto:!0,sorted:0,show:!0,spanGaps:!1,gaps:nv,alpha:1,points:{show:zx,filter:null},values:null,min:qe,max:-qe,idxs:[],path:null,clip:null};function Hx(e,t,o,r,i){return o/10}var av={time:!0,auto:!0,distr:1,log:10,asinh:1,min:null,max:null,dir:1,ori:0},Bx=xt({},av,{time:!1,ori:1}),$4={};function lv(e,t){let o=$4[e];return o||(o={key:e,plots:[],sub(r){o.plots.push(r)},unsub(r){o.plots=o.plots.filter(i=>i!=r)},pub(r,i,s,n,a,l,c){for(let d=0;d<o.plots.length;d++)o.plots[d]!=i&&o.plots[d].pub(r,i,s,n,a,l,c)}},e!=null&&($4[e]=o)),o}var bn=1,Up=2;function ds(e,t,o){let r=e.mode,i=e.series[t],s=r==2?e._data[t]:e._data,n=e.scales,a=e.bbox,l=s[0],c=r==2?s[1]:s[t],d=r==2?n[i.facets[0].scale]:n[e.series[0].scale],p=r==2?n[i.facets[1].scale]:n[i.scale],u=a.left,m=a.top,b=a.width,C=a.height,y=e.valToPosH,k=e.valToPosV;return d.ori==0?o(i,l,c,d,p,y,k,u,m,b,C,j1,yn,U1,dv,pv):o(i,l,c,d,p,k,y,m,u,C,b,W1,Cn,lu,hv,uv)}function nu(e,t){let o=0,r=0,i=Ee(e.bands,tu);for(let s=0;s<i.length;s++){let n=i[s];n.series[0]==t?o=n.dir:n.series[1]==t&&(n.dir==1?r|=1:r|=2)}return[o,r==1?-1:r==2?1:r==3?2:0]}function Ix(e,t,o,r,i){let s=e.mode,n=e.series[t],a=s==2?n.facets[1].scale:n.scale,l=e.scales[a];return i==-1?l.min:i==1?l.max:l.distr==3?l.dir==1?l.min:l.max:0}function Zr(e,t,o,r,i,s){return ds(e,t,(n,a,l,c,d,p,u,m,b,C,y)=>{let k=n.pxRound,$=c.dir*(c.ori==0?1:-1),V=c.ori==0?yn:Cn,O,P;$==1?(O=o,P=r):(O=r,P=o);let T=k(p(a[O],c,C,m)),Z=k(u(l[O],d,y,b)),R=k(p(a[P],c,C,m)),D=k(u(s==1?d.max:d.min,d,y,b)),N=new Path2D(i);return V(N,R,D),V(N,T,D),V(N,T,Z),N})}function N1(e,t,o,r,i,s){let n=null;if(e.length>0){n=new Path2D;let a=t==0?U1:lu,l=o;for(let p=0;p<e.length;p++){let u=e[p];if(u[1]>u[0]){let m=u[0]-l;m>0&&a(n,l,r,m,r+s),l=u[1]}}let c=o+i-l,d=10;c>0&&a(n,l,r-d/2,c,r+s+d)}return n}function Zx(e,t,o){let r=e[e.length-1];r&&r[0]==t?r[1]=o:e.push([t,o])}function au(e,t,o,r,i,s,n){let a=[],l=e.length;for(let c=i==1?o:r;c>=o&&c<=r;c+=i)if(t[c]===null){let p=c,u=c;if(i==1)for(;++c<=r&&t[c]===null;)u=c;else for(;--c>=o&&t[c]===null;)u=c;let m=s(e[p]),b=u==p?m:s(e[u]),C=p-i;m=n<=0&&C>=0&&C<l?s(e[C]):m;let k=u+i;b=n>=0&&k>=0&&k<l?s(e[k]):b,b>=m&&a.push([m,b])}return a}function A4(e){return e==0?B4:e==1?Mt:t=>ss(t,e)}function cv(e){let t=e==0?j1:W1,o=e==0?(i,s,n,a,l,c)=>{i.arcTo(s,n,a,l,c)}:(i,s,n,a,l,c)=>{i.arcTo(n,s,l,a,c)},r=e==0?(i,s,n,a,l)=>{i.rect(s,n,a,l)}:(i,s,n,a,l)=>{i.rect(n,s,l,a)};return(i,s,n,a,l,c=0,d=0)=>{c==0&&d==0?r(i,s,n,a,l):(c=er(c,a/2,l/2),d=er(d,a/2,l/2),t(i,s+c,n),o(i,s+a,n,s+a,n+l,c),o(i,s+a,n+l,s,n+l,d),o(i,s,n+l,s,n,d),o(i,s,n,s+a,n,c),i.closePath())}}var j1=(e,t,o)=>{e.moveTo(t,o)},W1=(e,t,o)=>{e.moveTo(o,t)},yn=(e,t,o)=>{e.lineTo(t,o)},Cn=(e,t,o)=>{e.lineTo(o,t)},U1=cv(0),lu=cv(1),dv=(e,t,o,r,i,s)=>{e.arc(t,o,r,i,s)},hv=(e,t,o,r,i,s)=>{e.arc(o,t,r,i,s)},pv=(e,t,o,r,i,s,n)=>{e.bezierCurveTo(t,o,r,i,s,n)},uv=(e,t,o,r,i,s,n)=>{e.bezierCurveTo(o,t,i,r,n,s)};function fv(e){return(t,o,r,i,s)=>ds(t,o,(n,a,l,c,d,p,u,m,b,C,y)=>{let{pxRound:k,points:$}=n,V,O;c.ori==0?(V=j1,O=dv):(V=W1,O=hv);let P=Xe($.width*He,3),T=($.size-$.width)/2*He,Z=Xe(T*2,3),R=new Path2D,D=new Path2D,{left:N,top:B,width:Y,height:I}=t.bbox;U1(D,N-Z,B-Z,Y+Z*2,I+Z*2);let H=W=>{if(l[W]!=null){let j=k(p(a[W],c,C,m)),F=k(u(l[W],d,y,b));V(R,j+T,F),O(R,j,F,T,0,E1*2)}};if(s)s.forEach(H);else for(let W=r;W<=i;W++)H(W);return{stroke:P>0?R:null,fill:R,clip:D,flags:bn|Up}})}function gv(e){return(t,o,r,i,s,n)=>{r!=i&&(s!=r&&n!=r&&e(t,o,r),s!=i&&n!=i&&e(t,o,i),e(t,o,n))}}var Fx=gv(yn),Nx=gv(Cn);function mv(e){let t=Ee(e?.alignGaps,0);return(o,r,i,s)=>ds(o,r,(n,a,l,c,d,p,u,m,b,C,y)=>{[i,s]=B1(l,i,s);let k=n.pxRound,$=I=>k(p(I,c,C,m)),V=I=>k(u(I,d,y,b)),O,P;c.ori==0?(O=yn,P=Fx):(O=Cn,P=Nx);let T=c.dir*(c.ori==0?1:-1),Z={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:bn},R=Z.stroke,D=!1;if(s-i>=C*4){let I=G=>o.posToVal(G,c.key,!0),H=null,W=null,j,F,me,ae=$(a[T==1?i:s]),le=$(a[i]),ve=$(a[s]),X=I(T==1?le+1:ve-1);for(let G=T==1?i:s;G>=i&&G<=s;G+=T){let he=a[G],J=(T==1?he<X:he>X)?ae:$(he),re=l[G];J==ae?re!=null?(F=re,H==null?(O(R,J,V(F)),j=H=W=F):F<H?H=F:F>W&&(W=F)):re===null&&(D=!0):(H!=null&&P(R,ae,V(H),V(W),V(j),V(F)),re!=null?(F=re,O(R,J,V(F)),H=W=j=F):(H=W=null,re===null&&(D=!0)),ae=J,X=I(ae+T))}H!=null&&H!=W&&me!=ae&&P(R,ae,V(H),V(W),V(j),V(F))}else for(let I=T==1?i:s;I>=i&&I<=s;I+=T){let H=l[I];H===null?D=!0:H!=null&&O(R,$(a[I]),V(H))}let[B,Y]=nu(o,r);if(n.fill!=null||B!=0){let I=Z.fill=new Path2D(R),H=n.fillTo(o,r,n.min,n.max,B),W=V(H),j=$(a[i]),F=$(a[s]);T==-1&&([F,j]=[j,F]),O(I,F,W),O(I,j,W)}if(!n.spanGaps){let I=[];D&&I.push(...au(a,l,i,s,T,$,t)),Z.gaps=I=n.gaps(o,r,i,s,I),Z.clip=N1(I,c.ori,m,b,C,y)}return Y!=0&&(Z.band=Y==2?[Zr(o,r,i,s,R,-1),Zr(o,r,i,s,R,1)]:Zr(o,r,i,s,R,Y)),Z})}function jx(e){let t=Ee(e.align,1),o=Ee(e.ascDesc,!1),r=Ee(e.alignGaps,0),i=Ee(e.extend,!1);return(s,n,a,l)=>ds(s,n,(c,d,p,u,m,b,C,y,k,$,V)=>{[a,l]=B1(p,a,l);let O=c.pxRound,{left:P,width:T}=s.bbox,Z=le=>O(b(le,u,$,y)),R=le=>O(C(le,m,V,k)),D=u.ori==0?yn:Cn,N={stroke:new Path2D,fill:null,clip:null,band:null,gaps:null,flags:bn},B=N.stroke,Y=u.dir*(u.ori==0?1:-1),I=R(p[Y==1?a:l]),H=Z(d[Y==1?a:l]),W=H,j=H;i&&t==-1&&(j=P,D(B,j,I)),D(B,H,I);for(let le=Y==1?a:l;le>=a&&le<=l;le+=Y){let ve=p[le];if(ve==null)continue;let X=Z(d[le]),G=R(ve);t==1?D(B,X,I):D(B,W,G),D(B,X,G),I=G,W=X}let F=W;i&&t==1&&(F=P+T,D(B,F,I));let[me,ae]=nu(s,n);if(c.fill!=null||me!=0){let le=N.fill=new Path2D(B),ve=c.fillTo(s,n,c.min,c.max,me),X=R(ve);D(le,F,X),D(le,j,X)}if(!c.spanGaps){let le=[];le.push(...au(d,p,a,l,Y,Z,r));let ve=c.width*He/2,X=o||t==1?ve:-ve,G=o||t==-1?-ve:ve;le.forEach(he=>{he[0]+=X,he[1]+=G}),N.gaps=le=c.gaps(s,n,a,l,le),N.clip=N1(le,u.ori,y,k,$,V)}return ae!=0&&(N.band=ae==2?[Zr(s,n,a,l,B,-1),Zr(s,n,a,l,B,1)]:Zr(s,n,a,l,B,ae)),N})}function P4(e,t,o,r,i,s,n=qe){if(e.length>1){let a=null;for(let l=0,c=1/0;l<e.length;l++)if(t[l]!==void 0){if(a!=null){let d=$t(e[l]-e[a]);d<c&&(c=d,n=$t(o(e[l],r,i,s)-o(e[a],r,i,s)))}a=l}}return n}function Wx(e){e=e||Da;let t=Ee(e.size,[.6,qe,1]),o=e.align||0,r=e.gap||0,i=e.radius;i=i==null?[0,0]:typeof i=="number"?[i,0]:i;let s=Oe(i),n=1-t[0],a=Ee(t[1],qe),l=Ee(t[2],1),c=Ee(e.disp,Da),d=Ee(e.each,m=>{}),{fill:p,stroke:u}=c;return(m,b,C,y)=>ds(m,b,(k,$,V,O,P,T,Z,R,D,N,B)=>{let Y=k.pxRound,I=o,H=r*He,W=a*He,j=l*He,F,me;O.ori==0?[F,me]=s(m,b):[me,F]=s(m,b);let ae=O.dir*(O.ori==0?1:-1),le=O.ori==0?U1:lu,ve=O.ori==0?d:(oe,Ke,kt,xs,Si,tr,Mi)=>{d(oe,Ke,kt,Si,xs,Mi,tr)},X=Ee(m.bands,tu).find(oe=>oe.series[0]==b),G=X!=null?X.dir:0,he=k.fillTo(m,b,k.min,k.max,G),fe=Y(Z(he,P,B,D)),J,re,pe,Be=N,se=Y(k.width*He),wo=!1,Oo=null,Vo=null,Wr=null,ws=null;p!=null&&(se==0||u!=null)&&(wo=!0,Oo=p.values(m,b,C,y),Vo=new Map,new Set(Oo).forEach(oe=>{oe!=null&&Vo.set(oe,new Path2D)}),se>0&&(Wr=u.values(m,b,C,y),ws=new Map,new Set(Wr).forEach(oe=>{oe!=null&&ws.set(oe,new Path2D)})));let{x0:ys,size:kn}=c;if(ys!=null&&kn!=null){I=1,$=ys.values(m,b,C,y),ys.unit==2&&($=$.map(kt=>m.posToVal(R+kt*N,O.key,!0)));let oe=kn.values(m,b,C,y);kn.unit==2?re=oe[0]*N:re=T(oe[0],O,N,R)-T(0,O,N,R),Be=P4($,V,T,O,N,R,Be),pe=Be-re+H}else Be=P4($,V,T,O,N,R,Be),pe=Be*n+H,re=Be-pe;pe<1&&(pe=0),se>=re/2&&(se=0),pe<5&&(Y=B4);let Ia=pe>0,ki=Be-pe-(Ia?se:0);re=Y(Np(ki,j,W)),J=(I==0?re/2:I==ae?0:re)-I*ae*((I==0?H/2:0)+(Ia?se/2:0));let Kt={stroke:null,fill:null,clip:null,band:null,gaps:null,flags:0},Cs=wo?null:new Path2D,vr=null;if(X!=null)vr=m.data[X.series[1]];else{let{y0:oe,y1:Ke}=c;oe!=null&&Ke!=null&&(V=Ke.values(m,b,C,y),vr=oe.values(m,b,C,y))}let Li=F*re,we=me*re;for(let oe=ae==1?C:y;oe>=C&&oe<=y;oe+=ae){let Ke=V[oe];if(Ke==null)continue;if(vr!=null){let lo=vr[oe]??0;if(Ke-lo==0)continue;fe=Z(lo,P,B,D)}let kt=O.distr!=2||c!=null?$[oe]:oe,xs=T(kt,O,N,R),Si=Z(Ee(Ke,he),P,B,D),tr=Y(xs-J),Mi=Y(io(Si,fe)),yo=Y(er(Si,fe)),To=Mi-yo;if(Ke!=null){let lo=Ke<0?we:Li,jo=Ke<0?Li:we;wo?(se>0&&Wr[oe]!=null&&le(ws.get(Wr[oe]),tr,yo+Mo(se/2),re,io(0,To-se),lo,jo),Oo[oe]!=null&&le(Vo.get(Oo[oe]),tr,yo+Mo(se/2),re,io(0,To-se),lo,jo)):le(Cs,tr,yo+Mo(se/2),re,io(0,To-se),lo,jo),ve(m,b,oe,tr-se/2,yo,re+se,To)}}return se>0?Kt.stroke=wo?ws:Cs:wo||(Kt._fill=k.width==0?k._fill:k._stroke??k._fill,Kt.width=0),Kt.fill=wo?Vo:Cs,Kt})}function Ux(e,t){let o=Ee(t?.alignGaps,0);return(r,i,s,n)=>ds(r,i,(a,l,c,d,p,u,m,b,C,y,k)=>{[s,n]=B1(c,s,n);let $=a.pxRound,V=F=>$(u(F,d,y,b)),O=F=>$(m(F,p,k,C)),P,T,Z;d.ori==0?(P=j1,Z=yn,T=pv):(P=W1,Z=Cn,T=uv);let R=d.dir*(d.ori==0?1:-1),D=V(l[R==1?s:n]),N=D,B=[],Y=[];for(let F=R==1?s:n;F>=s&&F<=n;F+=R)if(c[F]!=null){let ae=l[F],le=V(ae);B.push(N=le),Y.push(O(c[F]))}let I={stroke:e(B,Y,P,Z,T,$),fill:null,clip:null,band:null,gaps:null,flags:bn},H=I.stroke,[W,j]=nu(r,i);if(a.fill!=null||W!=0){let F=I.fill=new Path2D(H),me=a.fillTo(r,i,a.min,a.max,W),ae=O(me);Z(F,N,ae),Z(F,D,ae)}if(!a.spanGaps){let F=[];F.push(...au(l,c,s,n,R,V,o)),I.gaps=F=a.gaps(r,i,s,n,F),I.clip=N1(F,d.ori,b,C,y,k)}return j!=0&&(I.band=j==2?[Zr(r,i,s,n,H,-1),Zr(r,i,s,n,H,1)]:Zr(r,i,s,n,H,j)),I})}function Gx(e){return Ux(Yx,e)}function Yx(e,t,o,r,i,s){let n=e.length;if(n<2)return null;let a=new Path2D;if(o(a,e[0],t[0]),n==2)r(a,e[1],t[1]);else{let l=Array(n),c=Array(n-1),d=Array(n-1),p=Array(n-1);for(let u=0;u<n-1;u++)d[u]=t[u+1]-t[u],p[u]=e[u+1]-e[u],c[u]=d[u]/p[u];l[0]=c[0];for(let u=1;u<n-1;u++)c[u]===0||c[u-1]===0||c[u-1]>0!=c[u]>0?l[u]=0:(l[u]=3*(p[u-1]+p[u])/((2*p[u]+p[u-1])/c[u-1]+(p[u]+2*p[u-1])/c[u]),isFinite(l[u])||(l[u]=0));l[n-1]=c[n-2];for(let u=0;u<n-1;u++)i(a,e[u]+p[u]/3,t[u]+l[u]*p[u]/3,e[u+1]-p[u]/3,t[u+1]-l[u+1]*p[u]/3,e[u+1],t[u+1])}return a}var Gp=new Set;function O4(){for(let e of Gp)e.syncRect(!0)}wn&&(ls($C,fn,O4),ls(AC,fn,O4,!0),ls(R1,fn,()=>{jt.pxRatio=He}));var qx=mv(),Xx=fv();function V4(e,t,o,r){return(r?[e[0],e[1]].concat(e.slice(2)):[e[0]].concat(e.slice(1))).map((s,n)=>Yp(s,n,t,o))}function Kx(e,t){return e.map((o,r)=>r==0?{}:xt({},t,o))}function Yp(e,t,o,r){return xt({},t==0?o:r,e)}function vv(e,t,o){return t==null?mn:[t,o]}var Qx=vv;function Jx(e,t,o){return t==null?mn:z1(t,o,Jp,!0)}function bv(e,t,o,r){return t==null?mn:I1(t,o,e.scales[r].log,!1)}var e_=bv;function wv(e,t,o,r){return t==null?mn:Qp(t,o,e.scales[r].log,!1)}var t_=wv;function o_(e,t,o,r,i){let s=io(d4(e),d4(t)),n=t-e,a=Jo(i/r*n,o);do{let l=o[a],c=r*l/n;if(c>=i&&s+(l<5?wi.get(l):0)<=17)return[l,c]}while(++a<o.length);return[0,0]}function T4(e){let t,o;return e=e.replace(/(\d+)px/,(r,i)=>(t=Mt((o=+i)*He))+"px"),[e,t,o]}function r_(e){e.show&&[e.font,e.labelFont].forEach(t=>{let o=Xe(t[2]*He,1);t[0]=t[0].replace(/[0-9.]+px/,o+"px"),t[1]=o})}function jt(e,t,o){let r={mode:Ee(e.mode,1)},i=r.mode;function s(g,v,x,_){let A=v.valToPct(g);return _+x*(v.dir==-1?1-A:A)}function n(g,v,x,_){let A=v.valToPct(g);return _+x*(v.dir==-1?A:1-A)}function a(g,v,x,_){return v.ori==0?s(g,v,x,_):n(g,v,x,_)}r.valToPosH=s,r.valToPosV=n;let l=!1;r.status=0;let c=r.root=Zo(dC);if(e.id!=null&&(c.id=e.id),So(c,e.class),e.title){let g=Zo(uC,c);g.textContent=e.title}let d=Qo("canvas"),p=r.ctx=d.getContext("2d"),u=Zo(fC,c);ls("click",u,g=>{g.target===b&&(et!=Ts||nt!=Ds)&&Zt.click(r,g)},!0);let m=r.under=Zo(gC,u);u.appendChild(d);let b=r.over=Zo(mC,u);e=vn(e);let C=+Ee(e.pxAlign,1),y=A4(C);(e.plugins||[]).forEach(g=>{g.opts&&(e=g.opts(r,e)||e)});let k=e.ms||.001,$=r.series=i==1?V4(e.series||[],x4,M4,!1):Kx(e.series||[null],S4),V=r.axes=V4(e.axes||[],C4,k4,!0),O=r.scales={},P=r.bands=e.bands||[];P.forEach(g=>{g.fill=Oe(g.fill||null),g.dir=Ee(g.dir,-1)});let T=i==2?$[1].facets[0].scale:$[0].scale,Z={axes:Nb,series:Hb},R=(e.drawOrder||["axes","series"]).map(g=>Z[g]);function D(g){let v=g.distr==3?x=>Ir(x>0?x:g.clamp(r,x,g.min,g.max,g.key)):g.distr==4?x=>Ep(x,g.asinh):g.distr==100?x=>g.fwd(x):x=>x;return x=>{let _=v(x),{_min:A,_max:E}=g,U=E-A;return(_-A)/U}}function N(g){let v=O[g];if(v==null){let x=(e.scales||Da)[g]||Da;if(x.from!=null){N(x.from);let _=xt({},O[x.from],x,{key:g});_.valToPct=D(_),O[g]=_}else{v=O[g]=xt({},g==T?av:Bx,x),v.key=g;let _=v.time,A=v.range,E=bi(A);if((g!=T||i==2&&!_)&&(E&&(A[0]==null||A[1]==null)&&(A={min:A[0]==null?a4:{mode:1,hard:A[0],soft:A[0]},max:A[1]==null?a4:{mode:1,hard:A[1],soft:A[1]}},E=!1),!E&&F1(A))){let U=A;A=(q,K,ee)=>K==null?mn:z1(K,ee,U)}v.range=Oe(A||(_?Qx:g==T?v.distr==3?e_:v.distr==4?t_:vv:v.distr==3?bv:v.distr==4?wv:Jx)),v.auto=Oe(E?!1:v.auto),v.clamp=Oe(v.clamp||Hx),v._min=v._max=null,v.valToPct=D(v)}}}N("x"),N("y"),i==1&&$.forEach(g=>{N(g.scale)}),V.forEach(g=>{N(g.scale)});for(let g in e.scales)N(g);let B=O[T],Y=B.distr,I,H;B.ori==0?(So(c,hC),I=s,H=n):(So(c,pC),I=n,H=s);let W={};for(let g in O){let v=O[g];(v.min!=null||v.max!=null)&&(W[g]={min:v.min,max:v.max},v.min=v.max=null)}let j=e.tzDate||(g=>new Date(Mt(g/k))),F=e.fmtDate||ou,me=k==1?hx(j):fx(j),ae=b4(j,v4(k==1?dx:ux,F)),le=y4(j,w4(mx,F)),ve=[],X=r.legend=xt({},wx,e.legend),G=r.cursor=xt({},Lx,{drag:{y:i==2}},e.cursor),he=X.show,fe=G.show,J=X.markers;X.idxs=ve,J.width=Oe(J.width),J.dash=Oe(J.dash),J.stroke=Oe(J.stroke),J.fill=Oe(J.fill);let re,pe,Be,se=[],wo=[],Oo,Vo=!1,Wr={};if(X.live){let g=$[1]?$[1].values:null;Vo=g!=null,Oo=Vo?g(r,1,0):{_:0};for(let v in Oo)Wr[v]=Xp}if(he)if(re=Qo("table",xC,c),Be=Qo("tbody",null,re),X.mount(r,re),Vo){pe=Qo("thead",null,re,Be);let g=Qo("tr",null,pe);Qo("th",null,g);for(var ws in Oo)Qo("th",Ym,g).textContent=ws}else So(re,kC),X.live&&So(re,_C);let ys={show:!0},kn={show:!1};function Ia(g,v){if(v==0&&(Vo||!X.live||i==2))return mn;let x=[],_=Qo("tr",LC,Be,Be.childNodes[v]);So(_,g.class),g.show||So(_,as);let A=Qo("th",null,_);if(J.show){let q=Zo(SC,A);if(v>0){let K=J.width(r,v);K&&(q.style.border=K+"px "+J.dash(r,v)+" "+J.stroke(r,v)),q.style.background=J.fill(r,v)}}let E=Zo(Ym,A);g.label instanceof HTMLElement?E.appendChild(g.label):E.textContent=g.label,v>0&&(J.show||(E.style.color=g.width>0?J.stroke(r,v):J.fill(r,v)),Kt("click",A,q=>{if(G._lock)return;Ai(q);let K=$.indexOf(g);if((q.ctrlKey||q.metaKey)!=X.isolate){let ee=$.some((te,ie)=>ie>0&&ie!=K&&te.show);$.forEach((te,ie)=>{ie>0&&rr(ie,ee?ie==K?ys:kn:ys,!0,wt.setSeries)})}else rr(K,{show:!g.show},!0,wt.setSeries)},!1),ks&&Kt(Qm,A,q=>{G._lock||(Ai(q),rr($.indexOf(g),Rs,!0,wt.setSeries))},!1));for(var U in Oo){let q=Qo("td",MC,_);q.textContent="--",x.push(q)}return[_,x]}let ki=new Map;function Kt(g,v,x,_=!0){let A=ki.get(v)||{},E=G.bind[g](r,v,x,_);E&&(ls(g,v,A[g]=E),ki.set(v,A))}function Cs(g,v,x){let _=ki.get(v)||{};for(let A in _)(g==null||A==g)&&(Fp(A,v,_[A]),delete _[A]);g==null&&ki.delete(v)}let vr=0,Li=0,we=0,oe=0,Ke=0,kt=0,xs=Ke,Si=kt,tr=we,Mi=oe,yo=0,To=0,lo=0,jo=0;r.bbox={};let _d=!1,Za=!1,_s=!1,$i=!1,Fa=!1,Do=!1;function kd(g,v,x){(x||g!=r.width||v!=r.height)&&bu(g,v),As(!1),_s=!0,Za=!0,Ps()}function bu(g,v){r.width=vr=we=g,r.height=Li=oe=v,Ke=kt=0,Ob(),Vb();let x=r.bbox;yo=x.left=ss(Ke*He,.5),To=x.top=ss(kt*He,.5),lo=x.width=ss(we*He,.5),jo=x.height=ss(oe*He,.5)}let $b=3;function Ab(){let g=!1,v=0;for(;!g;){v++;let x=Zb(v),_=Fb(v);g=v==$b||x&&_,g||(bu(r.width,r.height),Za=!0)}}function Pb({width:g,height:v}){kd(g,v)}r.setSize=Pb;function Ob(){let g=!1,v=!1,x=!1,_=!1;V.forEach((A,E)=>{if(A.show&&A._show){let{side:U,_size:q}=A,K=U%2,ee=A.label!=null?A.labelSize:0,te=q+ee;te>0&&(K?(we-=te,U==3?(Ke+=te,_=!0):x=!0):(oe-=te,U==0?(kt+=te,g=!0):v=!0))}}),Pi[0]=g,Pi[1]=x,Pi[2]=v,Pi[3]=_,we-=Ur[1]+Ur[3],Ke+=Ur[3],oe-=Ur[2]+Ur[0],kt+=Ur[0]}function Vb(){let g=Ke+we,v=kt+oe,x=Ke,_=kt;function A(E,U){switch(E){case 1:return g+=U,g-U;case 2:return v+=U,v-U;case 3:return x-=U,x+U;case 0:return _-=U,_+U}}V.forEach((E,U)=>{if(E.show&&E._show){let q=E.side;E._pos=A(q,E._size),E.label!=null&&(E._lpos=A(q,E.labelSize))}})}if(G.dataIdx==null){let g=G.hover,v=g.skip=new Set(g.skip??[]);v.add(void 0);let x=g.prox=Oe(g.prox),_=g.bias??=0;G.dataIdx=(A,E,U,q)=>{if(E==0)return U;let K=U,ee=x(A,E,U,q)??qe,te=ee>=0&&ee<qe,ie=B.ori==0?we:oe,ge=G.left,Re=t[0],De=t[E];if(v.has(De[U])){K=null;let $e=null,ue=null,ce;if(_==0||_==-1)for(ce=U;$e==null&&ce-- >0;)v.has(De[ce])||($e=ce);if(_==0||_==1)for(ce=U;ue==null&&ce++<De.length;)v.has(De[ce])||(ue=ce);if($e!=null||ue!=null)if(te){let ot=$e==null?-1/0:I(Re[$e],B,ie,0),ut=ue==null?1/0:I(Re[ue],B,ie,0),Et=ge-ot,We=ut-ge;Et<=We?Et<=ee&&(K=$e):We<=ee&&(K=ue)}else K=ue==null?$e:$e==null?ue:U-$e<=ue-U?$e:ue}else te&&$t(ge-I(Re[U],B,ie,0))>ee&&(K=null);return K}}let Ai=g=>{G.event=g};G.idxs=ve,G._lock=!1;let Ut=G.points;Ut.show=Oe(Ut.show),Ut.size=Oe(Ut.size),Ut.stroke=Oe(Ut.stroke),Ut.width=Oe(Ut.width),Ut.fill=Oe(Ut.fill);let or=r.focus=xt({},e.focus||{alpha:.3},G.focus),ks=or.prox>=0,Ls=ks&&Ut.one,Eo=[],Ss=[],Ms=[];function wu(g,v){let x=Ut.show(r,v);if(x instanceof HTMLElement)return So(x,CC),So(x,g.class),pr(x,-10,-10,we,oe),b.insertBefore(x,Eo[v]),x}function yu(g,v){if(i==1||v>0){let x=i==1&&O[g.scale].time,_=g.value;g.value=x?u4(_)?y4(j,w4(_,F)):_||le:_||Ex,g.label=g.label||(x?Mx:Sx)}if(Ls||v>0){g.width=g.width==null?1:g.width,g.paths=g.paths||qx||BC,g.fillTo=Oe(g.fillTo||Ix),g.pxAlign=+Ee(g.pxAlign,C),g.pxRound=A4(g.pxAlign),g.stroke=Oe(g.stroke||null),g.fill=Oe(g.fill||null),g._stroke=g._fill=g._paths=g._focus=null;let x=Rx(io(1,g.width),1),_=g.points=xt({},{size:x,width:io(1,x*.2),stroke:g.stroke,space:x*2,paths:Xx,_stroke:null,_fill:null},g.points);_.show=Oe(_.show),_.filter=Oe(_.filter),_.fill=Oe(_.fill),_.stroke=Oe(_.stroke),_.paths=Oe(_.paths),_.pxAlign=g.pxAlign}if(he){let x=Ia(g,v);se.splice(v,0,x[0]),wo.splice(v,0,x[1]),X.values.push(null)}if(fe){ve.splice(v,0,null);let x=null;Ls?v==0&&(x=wu(g,v)):v>0&&(x=wu(g,v)),Eo.splice(v,0,x),Ss.splice(v,0,0),Ms.splice(v,0,0)}Dt("addSeries",v)}function Tb(g,v){v=v??$.length,g=i==1?Yp(g,v,x4,M4):Yp(g,v,{},S4),$.splice(v,0,g),yu($[v],v)}r.addSeries=Tb;function Db(g){if($.splice(g,1),he){X.values.splice(g,1),wo.splice(g,1);let v=se.splice(g,1)[0];Cs(null,v.firstChild),v.remove()}fe&&(ve.splice(g,1),Eo.splice(g,1)[0].remove(),Ss.splice(g,1),Ms.splice(g,1)),Dt("delSeries",g)}r.delSeries=Db;let Pi=[!1,!1,!1,!1];function Eb(g,v){if(g._show=g.show,g.show){let x=g.side%2,_=O[g.scale];_==null&&(g.scale=x?$[1].scale:T,_=O[g.scale]);let A=_.time;g.size=Oe(g.size),g.space=Oe(g.space),g.rotate=Oe(g.rotate),bi(g.incrs)&&g.incrs.forEach(U=>{!wi.has(U)&&wi.set(U,F4(U))}),g.incrs=Oe(g.incrs||(_.distr==2?ax:A?k==1?cx:px:ns)),g.splits=Oe(g.splits||(A&&_.distr==1?me:_.distr==3?jp:_.distr==4?Px:Ax)),g.stroke=Oe(g.stroke),g.grid.stroke=Oe(g.grid.stroke),g.ticks.stroke=Oe(g.ticks.stroke),g.border.stroke=Oe(g.border.stroke);let E=g.values;g.values=bi(E)&&!bi(E[0])?Oe(E):A?bi(E)?b4(j,v4(E,F)):u4(E)?gx(j,E):E||ae:E||$x,g.filter=Oe(g.filter||(_.distr>=3&&_.log==10?Tx:_.distr==3&&_.log==2?Dx:I4)),g.font=T4(g.font),g.labelFont=T4(g.labelFont),g._size=g.size(r,null,v,0),g._space=g._rotate=g._incrs=g._found=g._splits=g._values=null,g._size>0&&(Pi[v]=!0,g._el=Zo(vC,u))}}function Ln(g,v,x,_){let[A,E,U,q]=x,K=v%2,ee=0;return K==0&&(q||E)&&(ee=v==0&&!A||v==2&&!U?Mt(C4.size/3):0),K==1&&(A||U)&&(ee=v==1&&!E||v==3&&!q?Mt(k4.size/2):0),ee}let Cu=r.padding=(e.padding||[Ln,Ln,Ln,Ln]).map(g=>Oe(Ee(g,Ln))),Ur=r._padding=Cu.map((g,v)=>g(r,v,Pi,0)),It,Pt=null,Ot=null,Na=i==1?$[0].idxs:null,Wo=null,Sn=!1;function xu(g,v){if(t=g??[],r.data=r._data=t,i==2){It=0;for(let x=1;x<$.length;x++)It+=t[x][0].length}else{t.length==0&&(r.data=r._data=t=[[]]),Wo=t[0],It=Wo.length;let x=t;if(Y==2){x=t.slice();let _=x[0]=Array(It);for(let A=0;A<It;A++)_[A]=A}r._data=t=x}if(As(!0),Dt("setData"),Y==2&&(_s=!0),v!==!1){let x=B;x.auto(r,Sn)?Ld():Yr(T,x.min,x.max),$i=$i||G.left>=0,Do=!0,Ps()}}r.setData=xu;function Ld(){Sn=!0;let g,v;i==1&&(It>0?(Pt=Na[0]=0,Ot=Na[1]=It-1,g=t[0][Pt],v=t[0][Ot],Y==2?(g=Pt,v=Ot):g==v&&(Y==3?[g,v]=I1(g,g,B.log,!1):Y==4?[g,v]=Qp(g,g,B.log,!1):B.time?v=g+Mt(86400/k):[g,v]=z1(g,v,Jp,!0))):(Pt=Na[0]=g=null,Ot=Na[1]=v=null)),Yr(T,g,v)}let ja,$s,Sd,Md,$d,Ad,Pd,Od,Vd,co;function _u(g,v,x,_,A,E){g??=Xm,x??=tu,_??="butt",A??=Xm,E??="round",g!=ja&&(p.strokeStyle=ja=g),A!=$s&&(p.fillStyle=$s=A),v!=Sd&&(p.lineWidth=Sd=v),E!=$d&&(p.lineJoin=$d=E),_!=Ad&&(p.lineCap=Ad=_),x!=Md&&p.setLineDash(Md=x)}function ku(g,v,x,_){v!=$s&&(p.fillStyle=$s=v),g!=Pd&&(p.font=Pd=g),x!=Od&&(p.textAlign=Od=x),_!=Vd&&(p.textBaseline=Vd=_)}function Td(g,v,x,_,A=0){if(_.length>0&&g.auto(r,Sn)&&(v==null||v.min==null)){let E=Ee(Pt,0),U=Ee(Ot,_.length-1),q=x.min==null?TC(_,E,U,A,g.distr==3):[x.min,x.max];g.min=er(g.min,x.min=q[0]),g.max=io(g.max,x.max=q[1])}}let Lu={min:null,max:null};function Rb(){for(let _ in O){let A=O[_];W[_]==null&&(A.min==null||W[T]!=null&&A.auto(r,Sn))&&(W[_]=Lu)}for(let _ in O){let A=O[_];W[_]==null&&A.from!=null&&W[A.from]!=null&&(W[_]=Lu)}W[T]!=null&&As(!0);let g={};for(let _ in W){let A=W[_];if(A!=null){let E=g[_]=vn(O[_],FC);if(A.min!=null)xt(E,A);else if(_!=T||i==2)if(It==0&&E.from==null){let U=E.range(r,null,null,_);E.min=U[0],E.max=U[1]}else E.min=qe,E.max=-qe}}if(It>0){$.forEach((_,A)=>{if(i==1){let E=_.scale,U=W[E];if(U==null)return;let q=g[E];if(A==0){let K=q.range(r,q.min,q.max,E);q.min=K[0],q.max=K[1],Pt=Jo(q.min,t[0]),Ot=Jo(q.max,t[0]),Ot-Pt>1&&(t[0][Pt]<q.min&&Pt++,t[0][Ot]>q.max&&Ot--),_.min=Wo[Pt],_.max=Wo[Ot]}else _.show&&_.auto&&Td(q,U,_,t[A],_.sorted);_.idxs[0]=Pt,_.idxs[1]=Ot}else if(A>0&&_.show&&_.auto){let[E,U]=_.facets,q=E.scale,K=U.scale,[ee,te]=t[A],ie=g[q],ge=g[K];ie!=null&&Td(ie,W[q],E,ee,E.sorted),ge!=null&&Td(ge,W[K],U,te,U.sorted),_.min=U.min,_.max=U.max}});for(let _ in g){let A=g[_],E=W[_];if(A.from==null&&(E==null||E.min==null)){let U=A.range(r,A.min==qe?null:A.min,A.max==-qe?null:A.max,_);A.min=U[0],A.max=U[1]}}}for(let _ in g){let A=g[_];if(A.from!=null){let E=g[A.from];if(E.min==null)A.min=A.max=null;else{let U=A.range(r,E.min,E.max,_);A.min=U[0],A.max=U[1]}}}let v={},x=!1;for(let _ in g){let A=g[_],E=O[_];if(E.min!=A.min||E.max!=A.max){E.min=A.min,E.max=A.max;let U=E.distr;E._min=U==3?Ir(E.min):U==4?Ep(E.min,E.asinh):U==100?E.fwd(E.min):E.min,E._max=U==3?Ir(E.max):U==4?Ep(E.max,E.asinh):U==100?E.fwd(E.max):E.max,v[_]=x=!0}}if(x){$.forEach((_,A)=>{i==2?A>0&&v.y&&(_._paths=null):v[_.scale]&&(_._paths=null)});for(let _ in v)_s=!0,Dt("setScale",_);fe&&G.left>=0&&($i=Do=!0)}for(let _ in W)W[_]=null}function zb(g){let v=Np(Pt-1,0,It-1),x=Np(Ot+1,0,It-1);for(;g[v]==null&&v>0;)v--;for(;g[x]==null&&x<It-1;)x++;return[v,x]}function Hb(){if(It>0){let g=$.some(v=>v._focus)&&co!=or.alpha;g&&(p.globalAlpha=co=or.alpha),$.forEach((v,x)=>{if(x>0&&v.show&&(Su(x,!1),Su(x,!0),v._paths==null)){let _=co;co!=v.alpha&&(p.globalAlpha=co=v.alpha);let A=i==2?[0,t[x][0].length-1]:zb(t[x]);v._paths=v.paths(r,x,A[0],A[1]),co!=_&&(p.globalAlpha=co=_)}}),$.forEach((v,x)=>{if(x>0&&v.show){let _=co;co!=v.alpha&&(p.globalAlpha=co=v.alpha),v._paths!=null&&Mu(x,!1);{let A=v._paths!=null?v._paths.gaps:null,E=v.points.show(r,x,Pt,Ot,A),U=v.points.filter(r,x,E,A);(E||U)&&(v.points._paths=v.points.paths(r,x,Pt,Ot,U),Mu(x,!0))}co!=_&&(p.globalAlpha=co=_),Dt("drawSeries",x)}}),g&&(p.globalAlpha=co=1)}}function Su(g,v){let x=v?$[g].points:$[g];x._stroke=x.stroke(r,g),x._fill=x.fill(r,g)}function Mu(g,v){let x=v?$[g].points:$[g],{stroke:_,fill:A,clip:E,flags:U,_stroke:q=x._stroke,_fill:K=x._fill,_width:ee=x.width}=x._paths;ee=Xe(ee*He,3);let te=null,ie=ee%2/2;v&&K==null&&(K=ee>0?"#fff":q);let ge=x.pxAlign==1&&ie>0;if(ge&&p.translate(ie,ie),!v){let Re=yo-ee/2,De=To-ee/2,$e=lo+ee,ue=jo+ee;te=new Path2D,te.rect(Re,De,$e,ue)}v?Dd(q,ee,x.dash,x.cap,K,_,A,U,E):Bb(g,q,ee,x.dash,x.cap,K,_,A,U,te,E),ge&&p.translate(-ie,-ie)}function Bb(g,v,x,_,A,E,U,q,K,ee,te){let ie=!1;K!=0&&P.forEach((ge,Re)=>{if(ge.series[0]==g){let De=$[ge.series[1]],$e=t[ge.series[1]],ue=(De._paths||Da).band;bi(ue)&&(ue=ge.dir==1?ue[0]:ue[1]);let ce,ot=null;De.show&&ue&&EC($e,Pt,Ot)?(ot=ge.fill(r,Re)||E,ce=De._paths.clip):ue=null,Dd(v,x,_,A,ot,U,q,K,ee,te,ce,ue),ie=!0}}),ie||Dd(v,x,_,A,E,U,q,K,ee,te)}let $u=bn|Up;function Dd(g,v,x,_,A,E,U,q,K,ee,te,ie){_u(g,v,x,_,A),(K||ee||ie)&&(p.save(),K&&p.clip(K),ee&&p.clip(ee)),ie?(q&$u)==$u?(p.clip(ie),te&&p.clip(te),Ua(A,U),Wa(g,E,v)):q&Up?(Ua(A,U),p.clip(ie),Wa(g,E,v)):q&bn&&(p.save(),p.clip(ie),te&&p.clip(te),Ua(A,U),p.restore(),Wa(g,E,v)):(Ua(A,U),Wa(g,E,v)),(K||ee||ie)&&p.restore()}function Wa(g,v,x){x>0&&(v instanceof Map?v.forEach((_,A)=>{p.strokeStyle=ja=A,p.stroke(_)}):v!=null&&g&&p.stroke(v))}function Ua(g,v){v instanceof Map?v.forEach((x,_)=>{p.fillStyle=$s=_,p.fill(x)}):v!=null&&g&&p.fill(v)}function Ib(g,v,x,_){let A=V[g],E;if(_<=0)E=[0,0];else{let U=A._space=A.space(r,g,v,x,_),q=A._incrs=A.incrs(r,g,v,x,_,U);E=o_(v,x,q,_,U)}return A._found=E}function Ed(g,v,x,_,A,E,U,q,K,ee){let te=U%2/2;C==1&&p.translate(te,te),_u(q,U,K,ee,q),p.beginPath();let ie,ge,Re,De,$e=A+(_==0||_==3?-E:E);x==0?(ge=A,De=$e):(ie=A,Re=$e);for(let ue=0;ue<g.length;ue++)v[ue]!=null&&(x==0?ie=Re=g[ue]:ge=De=g[ue],p.moveTo(ie,ge),p.lineTo(Re,De));p.stroke(),C==1&&p.translate(-te,-te)}function Zb(g){let v=!0;return V.forEach((x,_)=>{if(!x.show)return;let A=O[x.scale];if(A.min==null){x._show&&(v=!1,x._show=!1,As(!1));return}else x._show||(v=!1,x._show=!0,As(!1));let E=x.side,U=E%2,{min:q,max:K}=A,[ee,te]=Ib(_,q,K,U==0?we:oe);if(te==0)return;let ie=A.distr==2,ge=x._splits=x.splits(r,_,q,K,ee,te,ie),Re=A.distr==2?ge.map(ce=>Wo[ce]):ge,De=A.distr==2?Wo[ge[1]]-Wo[ge[0]]:ee,$e=x._values=x.values(r,x.filter(r,Re,_,te,De),_,te,De);x._rotate=E==2?x.rotate(r,$e,_,te):0;let ue=x._size;x._size=Fo(x.size(r,$e,_,g)),ue!=null&&x._size!=ue&&(v=!1)}),v}function Fb(g){let v=!0;return Cu.forEach((x,_)=>{let A=x(r,_,Pi,g);A!=Ur[_]&&(v=!1),Ur[_]=A}),v}function Nb(){for(let g=0;g<V.length;g++){let v=V[g];if(!v.show||!v._show)continue;let x=v.side,_=x%2,A,E,U=v.stroke(r,g),q=x==0||x==3?-1:1,[K,ee]=v._found;if(v.label!=null){let Jt=v.labelGap*q,_o=Mt((v._lpos+Jt)*He);ku(v.labelFont[0],U,"center",x==2?"top":qm),p.save(),_==1?(A=E=0,p.translate(_o,Mt(To+jo/2)),p.rotate((x==3?-E1:E1)/2)):(A=Mt(yo+lo/2),E=_o);let Ti=H4(v.label)?v.label(r,g,K,ee):v.label;p.fillText(Ti,A,E),p.restore()}if(ee==0)continue;let te=O[v.scale],ie=_==0?lo:jo,ge=_==0?yo:To,Re=v._splits,De=te.distr==2?Re.map(Jt=>Wo[Jt]):Re,$e=te.distr==2?Wo[Re[1]]-Wo[Re[0]]:K,ue=v.ticks,ce=v.border,ot=ue.show?ue.size:0,ut=Mt(ot*He),Et=Mt((v.alignTo==2?v._size-ot-v.gap:v.gap)*He),We=v._rotate*-E1/180,ft=y(v._pos*He),Co=(ut+Et)*q,Qt=ft+Co;E=_==0?Qt:0,A=_==1?Qt:0;let Ro=v.font[0],Uo=v.align==1?pn:v.align==2?Vp:We>0?pn:We<0?Vp:_==0?"center":x==3?Vp:pn,sr=We||_==1?"middle":x==2?"top":qm;ku(Ro,U,Uo,sr);let xo=v.font[1]*v.lineGap,zo=Re.map(Jt=>y(a(Jt,te,ie,ge))),Go=v._values;for(let Jt=0;Jt<Go.length;Jt++){let _o=Go[Jt];if(_o!=null){_==0?A=zo[Jt]:E=zo[Jt],_o=""+_o;let Ti=_o.indexOf(`
`)==-1?[_o]:_o.split(/\n/gm);for(let eo=0;eo<Ti.length;eo++){let Gu=Ti[eo];We?(p.save(),p.translate(A,E+eo*xo),p.rotate(We),p.fillText(Gu,0,0),p.restore()):p.fillText(Gu,A,E+eo*xo)}}}ue.show&&Ed(zo,ue.filter(r,De,g,ee,$e),_,x,ft,ut,Xe(ue.width*He,3),ue.stroke(r,g),ue.dash,ue.cap);let nr=v.grid;nr.show&&Ed(zo,nr.filter(r,De,g,ee,$e),_,_==0?2:1,_==0?To:yo,_==0?jo:lo,Xe(nr.width*He,3),nr.stroke(r,g),nr.dash,nr.cap),ce.show&&Ed([ft],[1],_==0?1:0,_==0?1:2,_==1?To:yo,_==1?jo:lo,Xe(ce.width*He,3),ce.stroke(r,g),ce.dash,ce.cap)}Dt("drawAxes")}function As(g){$.forEach((v,x)=>{x>0&&(v._paths=null,g&&(i==1?(v.min=null,v.max=null):v.facets.forEach(_=>{_.min=null,_.max=null})))})}let Ga=!1,Rd=!1,Mn=[];function jb(){Rd=!1;for(let g=0;g<Mn.length;g++)Dt(...Mn[g]);Mn.length=0}function Ps(){Ga||(qC(Au),Ga=!0)}function Wb(g,v=!1){Ga=!0,Rd=v,g(r),Au(),v&&Mn.length>0&&queueMicrotask(jb)}r.batch=Wb;function Au(){if(_d&&(Rb(),_d=!1),_s&&(Ab(),_s=!1),Za){if(st(m,pn,Ke),st(m,"top",kt),st(m,Pa,we),st(m,Oa,oe),st(b,pn,Ke),st(b,"top",kt),st(b,Pa,we),st(b,Oa,oe),st(u,Pa,vr),st(u,Oa,Li),d.width=Mt(vr*He),d.height=Mt(Li*He),V.forEach(({_el:g,_show:v,_size:x,_pos:_,side:A})=>{if(g!=null)if(v){let E=A===3||A===0?x:0,U=A%2==1;st(g,U?"left":"top",_-E),st(g,U?"width":"height",x),st(g,U?"top":"left",U?kt:Ke),st(g,U?"height":"width",U?oe:we),Zp(g,as)}else So(g,as)}),ja=$s=Sd=$d=Ad=Pd=Od=Vd=Md=null,co=1,Pn(!0),Ke!=xs||kt!=Si||we!=tr||oe!=Mi){As(!1);let g=we/tr,v=oe/Mi;if(fe&&!$i&&G.left>=0){G.left*=g,G.top*=v,Os&&pr(Os,Mt(G.left),0,we,oe),Vs&&pr(Vs,0,Mt(G.top),we,oe);for(let x=0;x<Eo.length;x++){let _=Eo[x];_!=null&&(Ss[x]*=g,Ms[x]*=v,pr(_,Fo(Ss[x]),Fo(Ms[x]),we,oe))}}if(tt.show&&!Fa&&tt.left>=0&&tt.width>0){tt.left*=g,tt.width*=g,tt.top*=v,tt.height*=v;for(let x in Fd)st(Es,x,tt[x])}xs=Ke,Si=kt,tr=we,Mi=oe}Dt("setSize"),Za=!1}vr>0&&Li>0&&(p.clearRect(0,0,d.width,d.height),Dt("drawClear"),R.forEach(g=>g()),Dt("draw")),tt.show&&Fa&&(Ya(tt),Fa=!1),fe&&$i&&(Vi(null,!0,!1),$i=!1),X.show&&X.live&&Do&&(Id(),Do=!1),l||(l=!0,r.status=1,Dt("ready")),Sn=!1,Ga=!1}r.redraw=(g,v)=>{_s=v||!1,g!==!1?Yr(T,B.min,B.max):Ps()};function zd(g,v){let x=O[g];if(x.from==null){if(It==0){let _=x.range(r,v.min,v.max,g);v.min=_[0],v.max=_[1]}if(v.min>v.max){let _=v.min;v.min=v.max,v.max=_}if(It>1&&v.min!=null&&v.max!=null&&v.max-v.min<1e-16)return;g==T&&x.distr==2&&It>0&&(v.min=Jo(v.min,t[0]),v.max=Jo(v.max,t[0]),v.min==v.max&&v.max++),W[g]=v,_d=!0,Ps()}}r.setScale=zd;let Hd,Bd,Os,Vs,Pu,Ou,Ts,Ds,Vu,Tu,et,nt,Gr=!1,Zt=G.drag,Vt=Zt.x,Tt=Zt.y;fe&&(G.x&&(Hd=Zo(wC,b)),G.y&&(Bd=Zo(yC,b)),B.ori==0?(Os=Hd,Vs=Bd):(Os=Bd,Vs=Hd),et=G.left,nt=G.top);let tt=r.select=xt({show:!0,over:!0,left:0,width:0,top:0,height:0},e.select),Es=tt.show?Zo(bC,tt.over?b:m):null;function Ya(g,v){if(tt.show){for(let x in g)tt[x]=g[x],x in Fd&&st(Es,x,g[x]);v!==!1&&Dt("setSelect")}}r.setSelect=Ya;function Ub(g){if($[g].show)he&&Zp(se[g],as);else if(he&&So(se[g],as),fe){let x=Ls?Eo[0]:Eo[g];x!=null&&pr(x,-10,-10,we,oe)}}function Yr(g,v,x){zd(g,{min:v,max:x})}function rr(g,v,x,_){v.focus!=null&&Kb(g),v.show!=null&&$.forEach((A,E)=>{E>0&&(g==E||g==null)&&(A.show=v.show,Ub(E),i==2?(Yr(A.facets[0].scale,null,null),Yr(A.facets[1].scale,null,null)):Yr(A.scale,null,null),Ps())}),x!==!1&&Dt("setSeries",g,v),_&&On("setSeries",r,g,v)}r.setSeries=rr;function Gb(g,v){xt(P[g],v)}function Yb(g,v){g.fill=Oe(g.fill||null),g.dir=Ee(g.dir,-1),v=v??P.length,P.splice(v,0,g)}function qb(g){g==null?P.length=0:P.splice(g,1)}r.addBand=Yb,r.setBand=Gb,r.delBand=qb;function Xb(g,v){$[g].alpha=v,fe&&Eo[g]!=null&&(Eo[g].style.opacity=v),he&&se[g]&&(se[g].style.opacity=v)}let br,qr,Oi,Rs={focus:!0};function Kb(g){if(g!=Oi){let v=g==null,x=or.alpha!=1;$.forEach((_,A)=>{if(i==1||A>0){let E=v||A==0||A==g;_._focus=v?null:E,x&&Xb(A,E?1:or.alpha)}}),Oi=g,x&&Ps()}}he&&ks&&Kt(Jm,re,g=>{G._lock||(Ai(g),Oi!=null&&rr(null,Rs,!0,wt.setSeries))});function ir(g,v,x){let _=O[v];x&&(g=g/He-(_.ori==1?kt:Ke));let A=we;_.ori==1&&(A=oe,g=A-g),_.dir==-1&&(g=A-g);let E=_._min,U=_._max,q=g/A,K=E+(U-E)*q,ee=_.distr;return ee==3?gn(10,K):ee==4?zC(K,_.asinh):ee==100?_.bwd(K):K}function Qb(g,v){let x=ir(g,T,v);return Jo(x,t[0],Pt,Ot)}r.valToIdx=g=>Jo(g,t[0]),r.posToIdx=Qb,r.posToVal=ir,r.valToPos=(g,v,x)=>O[v].ori==0?s(g,O[v],x?lo:we,x?yo:0):n(g,O[v],x?jo:oe,x?To:0),r.setCursor=(g,v,x)=>{et=g.left,nt=g.top,Vi(null,v,x)};function Du(g,v){st(Es,pn,tt.left=g),st(Es,Pa,tt.width=v)}function Eu(g,v){st(Es,"top",tt.top=g),st(Es,Oa,tt.height=v)}let $n=B.ori==0?Du:Eu,An=B.ori==1?Du:Eu;function Jb(){if(he&&X.live)for(let g=i==2?1:0;g<$.length;g++){if(g==0&&Vo)continue;let v=X.values[g],x=0;for(let _ in v)wo[g][x++].firstChild.nodeValue=v[_]}}function Id(g,v){if(g!=null&&(g.idxs?g.idxs.forEach((x,_)=>{ve[_]=x}):ZC(g.idx)||ve.fill(g.idx),X.idx=ve[0]),he&&X.live){for(let x=0;x<$.length;x++)(x>0||i==1&&!Vo)&&e5(x,ve[x]);Jb()}Do=!1,v!==!1&&Dt("setLegend")}r.setLegend=Id;function e5(g,v){let x=$[g],_=g==0&&Y==2?Wo:t[g],A;Vo?A=x.values(r,g,v)??Wr:(A=x.value(r,v==null?null:_[v],g,v),A=A==null?Wr:{_:A}),X.values[g]=A}function Vi(g,v,x){Vu=et,Tu=nt,[et,nt]=G.move(r,et,nt),G.left=et,G.top=nt,fe&&(Os&&pr(Os,Mt(et),0,we,oe),Vs&&pr(Vs,0,Mt(nt),we,oe));let _,A=Pt>Ot;br=qe,qr=null;let E=B.ori==0?we:oe,U=B.ori==1?we:oe;if(et<0||It==0||A){_=G.idx=null;for(let q=0;q<$.length;q++){let K=Eo[q];K!=null&&pr(K,-10,-10,we,oe)}ks&&rr(null,Rs,!0,g==null&&wt.setSeries),X.live&&(ve.fill(_),Do=!0)}else{let q,K,ee;i==1&&(q=B.ori==0?et:nt,K=ir(q,T),_=G.idx=Jo(K,t[0],Pt,Ot),ee=I(t[0][_],B,E,0));let te=-10,ie=-10,ge=0,Re=0,De=!0,$e="",ue="";for(let ce=i==2?1:0;ce<$.length;ce++){let ot=$[ce],ut=ve[ce],Et=ut==null?null:i==1?t[ce][ut]:t[ce][1][ut],We=G.dataIdx(r,ce,_,K),ft=We==null?null:i==1?t[ce][We]:t[ce][1][We];if(Do=Do||ft!=Et||We!=ut,ve[ce]=We,ce>0&&ot.show){let Co=We==null?-10:We==_?ee:I(i==1?t[0][We]:t[ce][0][We],B,E,0),Qt=ft==null?-10:H(ft,i==1?O[ot.scale]:O[ot.facets[1].scale],U,0);if(ks&&ft!=null){let Ro=B.ori==1?et:nt,Uo=$t(or.dist(r,ce,We,Qt,Ro));if(Uo<br){let sr=or.bias;if(sr!=0){let xo=ir(Ro,ot.scale),zo=ft>=0?1:-1,Go=xo>=0?1:-1;Go==zo&&(Go==1?sr==1?ft>=xo:ft<=xo:sr==1?ft<=xo:ft>=xo)&&(br=Uo,qr=ce)}else br=Uo,qr=ce}}if(Do||Ls){let Ro,Uo;B.ori==0?(Ro=Co,Uo=Qt):(Ro=Qt,Uo=Co);let sr,xo,zo,Go,nr,Jt,_o=!0,Ti=Ut.bbox;if(Ti!=null){_o=!1;let eo=Ti(r,ce);zo=eo.left,Go=eo.top,sr=eo.width,xo=eo.height}else zo=Ro,Go=Uo,sr=xo=Ut.size(r,ce);if(Jt=Ut.fill(r,ce),nr=Ut.stroke(r,ce),Ls)ce==qr&&br<=or.prox&&(te=zo,ie=Go,ge=sr,Re=xo,De=_o,$e=Jt,ue=nr);else{let eo=Eo[ce];eo!=null&&(Ss[ce]=zo,Ms[ce]=Go,n4(eo,sr,xo,_o),i4(eo,Jt,nr),pr(eo,Fo(zo),Fo(Go),we,oe))}}}}if(Ls){let ce=or.prox,ot=Oi==null?br<=ce:br>ce||qr!=Oi;if(Do||ot){let ut=Eo[0];ut!=null&&(Ss[0]=te,Ms[0]=ie,n4(ut,ge,Re,De),i4(ut,$e,ue),pr(ut,Fo(te),Fo(ie),we,oe))}}}if(tt.show&&Gr)if(g!=null){let[q,K]=wt.scales,[ee,te]=wt.match,[ie,ge]=g.cursor.sync.scales,Re=g.cursor.drag;if(Vt=Re._x,Tt=Re._y,Vt||Tt){let{left:De,top:$e,width:ue,height:ce}=g.select,ot=g.scales[ie].ori,ut=g.posToVal,Et,We,ft,Co,Qt,Ro=q!=null&&ee(q,ie),Uo=K!=null&&te(K,ge);Ro&&Vt?(ot==0?(Et=De,We=ue):(Et=$e,We=ce),ft=O[q],Co=I(ut(Et,ie),ft,E,0),Qt=I(ut(Et+We,ie),ft,E,0),$n(er(Co,Qt),$t(Qt-Co))):$n(0,E),Uo&&Tt?(ot==1?(Et=De,We=ue):(Et=$e,We=ce),ft=O[K],Co=H(ut(Et,ge),ft,U,0),Qt=H(ut(Et+We,ge),ft,U,0),An(er(Co,Qt),$t(Qt-Co))):An(0,U)}else Nd()}else{let q=$t(Vu-Pu),K=$t(Tu-Ou);if(B.ori==1){let ge=q;q=K,K=ge}Vt=Zt.x&&q>=Zt.dist,Tt=Zt.y&&K>=Zt.dist;let ee=Zt.uni;ee!=null?Vt&&Tt&&(Vt=q>=ee,Tt=K>=ee,!Vt&&!Tt&&(K>q?Tt=!0:Vt=!0)):Zt.x&&Zt.y&&(Vt||Tt)&&(Vt=Tt=!0);let te,ie;Vt&&(B.ori==0?(te=Ts,ie=et):(te=Ds,ie=nt),$n(er(te,ie),$t(ie-te)),Tt||An(0,U)),Tt&&(B.ori==1?(te=Ts,ie=et):(te=Ds,ie=nt),An(er(te,ie),$t(ie-te)),Vt||$n(0,E)),!Vt&&!Tt&&($n(0,0),An(0,0))}if(Zt._x=Vt,Zt._y=Tt,g==null){if(x){if(Uu!=null){let[q,K]=wt.scales;wt.values[0]=q!=null?ir(B.ori==0?et:nt,q):null,wt.values[1]=K!=null?ir(B.ori==1?et:nt,K):null}On(Tp,r,et,nt,we,oe,_)}if(ks){let q=x&&wt.setSeries,K=or.prox;Oi==null?br<=K&&rr(qr,Rs,!0,q):br>K?rr(null,Rs,!0,q):qr!=Oi&&rr(qr,Rs,!0,q)}}Do&&(X.idx=_,Id()),v!==!1&&Dt("setCursor")}let Xr=null;Object.defineProperty(r,"rect",{get(){return Xr==null&&Pn(!1),Xr}});function Pn(g=!1){g?Xr=null:(Xr=b.getBoundingClientRect(),Dt("syncRect",Xr))}function Ru(g,v,x,_,A,E,U){G._lock||Gr&&g!=null&&g.movementX==0&&g.movementY==0||(Zd(g,v,x,_,A,E,U,!1,g!=null),g!=null?Vi(null,!0,!0):Vi(v,!0,!1))}function Zd(g,v,x,_,A,E,U,q,K){if(Xr==null&&Pn(!1),Ai(g),g!=null)x=g.clientX-Xr.left,_=g.clientY-Xr.top;else{if(x<0||_<0){et=-10,nt=-10;return}let[ee,te]=wt.scales,ie=v.cursor.sync,[ge,Re]=ie.values,[De,$e]=ie.scales,[ue,ce]=wt.match,ot=v.axes[0].side%2==1,ut=B.ori==0?we:oe,Et=B.ori==1?we:oe,We=ot?E:A,ft=ot?A:E,Co=ot?_:x,Qt=ot?x:_;if(De!=null?x=ue(ee,De)?a(ge,O[ee],ut,0):-10:x=ut*(Co/We),$e!=null?_=ce(te,$e)?a(Re,O[te],Et,0):-10:_=Et*(Qt/ft),B.ori==1){let Ro=x;x=_,_=Ro}}K&&(v==null||v.cursor.event.type==Tp)&&((x<=1||x>=we-1)&&(x=ss(x,we)),(_<=1||_>=oe-1)&&(_=ss(_,oe))),q?(Pu=x,Ou=_,[Ts,Ds]=G.move(r,x,_)):(et=x,nt=_)}let Fd={width:0,height:0,left:0,top:0};function Nd(){Ya(Fd,!1)}let zu,Hu,Bu,Iu;function Zu(g,v,x,_,A,E,U){Gr=!0,Vt=Tt=Zt._x=Zt._y=!1,Zd(g,v,x,_,A,E,U,!0,!1),g!=null&&(Kt(Dp,Bp,Fu,!1),On(Km,r,Ts,Ds,we,oe,null));let{left:q,top:K,width:ee,height:te}=tt;zu=q,Hu=K,Bu=ee,Iu=te}function Fu(g,v,x,_,A,E,U){Gr=Zt._x=Zt._y=!1,Zd(g,v,x,_,A,E,U,!1,!0);let{left:q,top:K,width:ee,height:te}=tt,ie=ee>0||te>0,ge=zu!=q||Hu!=K||Bu!=ee||Iu!=te;if(ie&&ge&&Ya(tt),Zt.setScale&&ie&&ge){let Re=q,De=ee,$e=K,ue=te;if(B.ori==1&&(Re=K,De=te,$e=q,ue=ee),Vt&&Yr(T,ir(Re,T),ir(Re+De,T)),Tt)for(let ce in O){let ot=O[ce];ce!=T&&ot.from==null&&ot.min!=qe&&Yr(ce,ir($e+ue,ce),ir($e,ce))}Nd()}else G.lock&&(G._lock=!G._lock,Vi(v,!0,g!=null));g!=null&&(Cs(Dp,Bp),On(Dp,r,et,nt,we,oe,null))}function t5(g,v,x,_,A,E,U){if(G._lock)return;Ai(g);let q=Gr;if(Gr){let K=!0,ee=!0,te=10,ie,ge;B.ori==0?(ie=Vt,ge=Tt):(ie=Tt,ge=Vt),ie&&ge&&(K=et<=te||et>=we-te,ee=nt<=te||nt>=oe-te),ie&&K&&(et=et<Ts?0:we),ge&&ee&&(nt=nt<Ds?0:oe),Vi(null,!0,!0),Gr=!1}et=-10,nt=-10,ve.fill(null),Vi(null,!0,!0),q&&(Gr=q)}function Nu(g,v,x,_,A,E,U){G._lock||(Ai(g),Ld(),Nd(),g!=null&&On(e4,r,et,nt,we,oe,null))}function ju(){V.forEach(r_),kd(r.width,r.height,!0)}ls(R1,fn,ju);let zs={};zs.mousedown=Zu,zs.mousemove=Ru,zs.mouseup=Fu,zs.dblclick=Nu,zs.setSeries=(g,v,x,_)=>{let A=wt.match[2];x=A(r,v,x),x!=-1&&rr(x,_,!0,!1)},fe&&(Kt(Km,b,Zu),Kt(Tp,b,Ru),Kt(Qm,b,g=>{Ai(g),Pn(!1)}),Kt(Jm,b,t5),Kt(e4,b,Nu),Gp.add(r),r.syncRect=Pn);let qa=r.hooks=e.hooks||{};function Dt(g,v,x){Rd?Mn.push([g,v,x]):g in qa&&qa[g].forEach(_=>{_.call(null,r,v,x)})}(e.plugins||[]).forEach(g=>{for(let v in g.hooks)qa[v]=(qa[v]||[]).concat(g.hooks[v])});let Wu=(g,v,x)=>x,wt=xt({key:null,setSeries:!1,filters:{pub:h4,sub:h4},scales:[T,$[1]?$[1].scale:null],match:[p4,p4,Wu],values:[null,null]},G.sync);wt.match.length==2&&wt.match.push(Wu),G.sync=wt;let Uu=wt.key,jd=lv(Uu);function On(g,v,x,_,A,E,U){wt.filters.pub(g,v,x,_,A,E,U)&&jd.pub(g,v,x,_,A,E,U)}jd.sub(r);function o5(g,v,x,_,A,E,U){wt.filters.sub(g,v,x,_,A,E,U)&&zs[g](null,v,x,_,A,E,U)}r.pub=o5;function r5(){jd.unsub(r),Gp.delete(r),ki.clear(),Fp(R1,fn,ju),c.remove(),re?.remove(),Dt("destroy")}r.destroy=r5;function Wd(){Dt("init",e,t),xu(t||e.data,!1),W[T]?zd(T,W[T]):Ld(),Fa=tt.show&&(tt.width>0||tt.height>0),$i=Do=!0,kd(e.width,e.height)}return $.forEach(yu),V.forEach(Eb),o?o instanceof HTMLElement?(o.appendChild(c),Wd()):o(r,Wd):Wd(),r}jt.assign=xt;jt.fmtNum=eu;jt.rangeNum=z1;jt.rangeLog=I1;jt.rangeAsinh=Qp;jt.orient=ds;jt.pxRatio=He;jt.join=YC;jt.fmtDate=ou,jt.tzDate=sx;jt.sync=lv;{jt.addGap=Zx,jt.clipGaps=N1;let e=jt.paths={points:fv};e.linear=mv,e.stepped=jx,e.bars=Wx,e.spline=Gx}var i_=Object.defineProperty,s_=Object.getOwnPropertyDescriptor,xn=(e,t,o,r)=>{for(var i=r>1?void 0:r?s_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&i_(t,o,i),i},cu=(e=>(e.small="small",e.medium="medium",e.large="large",e))(cu||{});var yi=class extends S{constructor(){super(...arguments),this.data=[[],[]],this.layout={},this.y=void 0,this.zeroLineY=void 0,this.uplot=null,this.resizeObserver=null}getCssColor(e){return getComputedStyle(this).getPropertyValue(e).trim()}firstUpdated(){let e={width:this.chart.clientWidth,height:this.chart.clientHeight,scales:{x:{time:!1,show:!1},y:{auto:!0,show:!1,range:this._range.bind(this)}},series:[{},{stroke:this._getStrokeColor(),width:this._getStrokeWidth(),fill:this._effectiveFill?()=>this._getFillColor():void 0,points:{show:!1}}],axes:[{show:!1},{ticks:{show:!1},show:!1,grid:{show:!1}}],legend:{show:!1},cursor:{show:!1}};this.uplot=new jt(e,this.data,this.chart),requestAnimationFrame(()=>this.updateY()),this.resizeObserver=new ResizeObserver(()=>this.updateSize()),this.resizeObserver.observe(this.chart)}disconnectedCallback(){super.disconnectedCallback(),this.resizeObserver?.disconnect(),this.resizeObserver=null,this.uplot?.destroy(),this.uplot=null}updateSize(){this.uplot&&(this.uplot.setSize({width:this.chart.clientWidth,height:this.chart.clientHeight}),this.updateY())}_range(e,t,o,r){let{min:i,max:s}=this.layout.y??{},n=s??o-(i??t),a=i??t-n*.1;return i===void 0&&this.layout.y?.showZeroLine!==!1&&(a=Math.min(0,a)),[a,s??o+n*.1]}get _effectiveSize(){return this.layout.size??"medium"}get _effectivePriority(){return this.layout.priority??"regular"}get _effectiveFill(){return this.layout.fill??!1}_getFillColor(){return this.getCssColor("--instrument-regular-tertiary-color")||"#bebebe"}_getStrokeWidth(){switch(this._effectiveSize){case"small":return 1;case"medium":return 1.5;case"large":return 2}}_getStrokeColor(){switch(this._effectivePriority){case"regular":return this.getCssColor("--element-neutral-color");case"enhanced":return this.getCssColor("--element-neutral-enhanced-color")}}updatePalette(){if(!this.uplot)return;let e=this.uplot.series[1];e.stroke=()=>this._getStrokeColor(),e.width=this._getStrokeWidth(),this._effectiveFill&&(e.fill=()=>this._getFillColor()),this.uplot.redraw()}updateY(){if(!this.uplot)return;let e=this.data[1][this.data[1].length-1],t=this.uplot.scales.y.valToPct(e);t<0||t>1?this.y=void 0:this.y=t*this.chart.clientHeight,this.updateZeroLine()}updateZeroLine(){if(!this.uplot)return;let e=this.uplot.scales.y.valToPct(0);if(e<0||e>1){this.zeroLineY=void 0;return}this.zeroLineY=e*this.chart.clientHeight}updated(e){(e.has("data")||e.has("layout"))&&(this.updatePalette(),this.uplot?.setData(this.data),requestAnimationFrame(()=>this.updateY()))}render(){return f`
      <div
        class="chart-container ${this._effectivePriority} ${this._effectiveSize}"
      >
        <div id="chart"></div>
        <div
          id="zero-line"
          style="transform: translateY(${-(this.zeroLineY??0)}px);
          display: ${this.zeroLineY!==void 0?"block":"none"};
          "
        ></div>
        <div
          id="dot"
          style="transform: translateY(${-(this.y??0)}px);
          display: ${this.y!==void 0?"block":"none"};
          "
        ></div>
      </div>
    `}};yi.styles=ne(Gm);xn([h({type:Array})],yi.prototype,"data",2);xn([h({type:Object})],yi.prototype,"layout",2);xn([at("#chart")],yi.prototype,"chart",2);xn([ke()],yi.prototype,"y",2);xn([ke()],yi.prototype,"zeroLineY",2);yi=xn([L("obc-indicator-graph")],yi);var n_=Object.defineProperty,a_=Object.getOwnPropertyDescriptor,_t=(e,t,o,r)=>{for(var i=r>1?void 0:r?a_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&n_(t,o,i),i};var mt=class extends S{constructor(){super(...arguments),this.orientation="bottom",this.type="value",this.lineType=void 0,this.unit="",this.fractionDigits=1,this.maxDigits=0,this.hintedZeros=!1,this.hasSignSpacer=!1,this.size=Op.regular,this.hasIcon=!1,this.hasAdvice=!1,this.hasAlert=!1,this.hasSetPoint=!1,this.tag="",this.idTag="",this.data=[[],[]]}get hasGraph(){return this.type==="horizontal-graph"||this.type==="vertical-graph"}get lineOffset(){return this.lineType===void 0?0:Z0(this.lineType)/2}renderButton(){let e=this.type==="indicator";return f`
      <obc-transmitter-button
        class="chip"
        .variant=${e?O1.tag:O1.value}
        .size=${this.size}
        .value=${this.value}
        .unit=${this.unit}
        .fractionDigits=${this.fractionDigits}
        .maxDigits=${this.maxDigits}
        .hintedZeros=${this.hintedZeros}
        .hasSignSpacer=${this.hasSignSpacer}
        .hasIcon=${this.hasIcon}
        .hasAdvice=${this.hasAdvice}
        .adviceValue=${this.adviceValue}
        .hasSetPoint=${this.hasSetPoint}
        .setpointValue=${this.setpointValue}
        .label=${this.tag}
      >
        <slot name="icon" slot="icon"></slot>
      </obc-transmitter-button>
    `}renderGraph(){if(!this.hasGraph)return z;let e={size:cu.small,fill:!0};return f`
      <div class="graph-box">
        <obc-indicator-graph .data=${this.data} .layout=${e}>
        </obc-indicator-graph>
      </div>
    `}renderLabel(){return this.idTag?f`<div class="id-tag">${this.idTag}</div>`:z}renderContent(){return f`
      <div class="content">
        <div class="body">${this.renderButton()} ${this.renderGraph()}</div>
        ${this.renderLabel()}
      </div>
    `}render(){let e=this.hasAlert?f`
          <obc-alert-frame
            class="alert-frame"
            .type=${xr.Regular}
            .wrapContent=${!0}
          >
            ${this.renderContent()}
          </obc-alert-frame>
        `:this.renderContent();return f`
      <div
        class=${de({transmitter:!0,"has-alert":this.hasAlert,[`orientation-${this.orientation}`]:!0,[`type-${this.type}`]:!0})}
        style="--offset: ${this.lineOffset}px;"
      >
        ${e}
      </div>
    `}};mt.styles=ne(Wm);_t([h({type:String})],mt.prototype,"orientation",2);_t([h({type:String})],mt.prototype,"type",2);_t([h({type:String})],mt.prototype,"lineType",2);_t([h({type:Number})],mt.prototype,"value",2);_t([h({type:String})],mt.prototype,"unit",2);_t([h({type:Number})],mt.prototype,"fractionDigits",2);_t([h({type:Number})],mt.prototype,"maxDigits",2);_t([h({type:Boolean})],mt.prototype,"hintedZeros",2);_t([h({type:Boolean})],mt.prototype,"hasSignSpacer",2);_t([h({type:String})],mt.prototype,"size",2);_t([h({type:Boolean})],mt.prototype,"hasIcon",2);_t([h({type:Boolean})],mt.prototype,"hasAdvice",2);_t([h({type:Boolean})],mt.prototype,"hasAlert",2);_t([h({type:Number})],mt.prototype,"adviceValue",2);_t([h({type:Boolean})],mt.prototype,"hasSetPoint",2);_t([h({type:Number})],mt.prototype,"setpointValue",2);_t([h({type:String})],mt.prototype,"tag",2);_t([h({type:String})],mt.prototype,"idTag",2);_t([h({type:Array})],mt.prototype,"data",2);mt=_t([L("obc-transmitter")],mt);var yv=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: block;
  width: fit-content;
}

.wrapper {
  display: flex;
  flex-direction: column;
  width: fit-content;
  padding: var(--instrument-components-readout-padding-vertical)
    var(--instrument-components-readout-padding-horizontal);
}

.wrapper.horizontal {
    flex-direction: row;
    align-items: center;
  }

.wrapper .setpoint,.wrapper .value,.wrapper .label,.wrapper .src {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    padding: 0px var(--instrument-components-readout-padding-horizontal);
  }

.wrapper .setpoint {
    color: var(--instrument-enhanced-secondary-color);
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-regular-font-size);
    line-height: var(--global-typography-instrument-value-regular-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    transition: opacity 10ms ease-in-out;
  }

.wrapper.hide-setpoint .setpoint {
      opacity: 0;
      transition: opacity 0.2s ease-in-out;
    }

.wrapper.horizontal.enhanced .setpoint {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-large-font-size);
    line-height: var(--global-typography-instrument-value-large-line-height);
    letter-spacing: var(
    --global-typography-instrument-value-large-letter-spacing
  );
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.wrapper .value {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-value-regular-font-size);
    line-height: var(--global-typography-instrument-value-regular-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    padding: 0px var(--instrument-components-readout-padding-horizontal);
    justify-content: end;
  }

:is(.wrapper .value) .value-hint-zero {
      opacity: 0;
      color: var(--border-outline-color);
    }

:is(.wrapper .value) .value-blue {
      color: var(--instrument-enhanced-secondary-color);
    }

.wrapper.show-zero-padding .value-hint-zero {
      opacity: 1;
    }

.wrapper .label {
    justify-content: end;
    gap: var(--instrument-components-readout-icon-spacing);
    color: var(--element-neutral-color);
    text-wrap: nowrap;
  }

:is(.wrapper .label) .tag {
      font-family: var(--global-typography-font-family);
      font-size: var(--global-typography-instrument-label-font-size);
      line-height: var(--global-typography-instrument-label-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      width: var(--obc-instrument-field-tag-width, auto);
    }

:is(.wrapper .label) .unit {
      font-family: var(--global-typography-font-family);
      font-size: var(--global-typography-instrument-unit-font-size);
      line-height: var(--global-typography-instrument-unit-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    }

.wrapper.off .label {
    color: var(--element-inactive-color);
  }

.wrapper.horizontal.enhanced {
    height: 48px;
  }

.wrapper.horizontal.enhanced .label {
      flex-direction: column;
      align-items: start;
      justify-content: center;
      gap: 0;
    }

.wrapper.horizontal .label {
      align-items: start;
    }

.wrapper .src {
    font-family: var(--global-typography-font-family);
    font-size: var(--global-typography-instrument-unit-font-size);
    line-height: var(--global-typography-instrument-unit-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    color: var(--element-neutral-color);
    justify-content: end;
    width: var(--obc-instrument-field-source-width, auto);
    box-sizing: content-box;
  }

.wrapper.off .src {
    color: var(--element-inactive-color);
  }

.wrapper.horizontal .src {
    justify-content: start;
  }

.wrapper.horizontal.enhanced .src {
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-body-font-weight);
    font-size: var(--global-typography-ui-body-font-size);
    line-height: var(--global-typography-ui-body-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.wrapper.neutral-color .value-blue {
      color: var(--element-neutral-color);
    }

.wrapper.off .value-blue {
      color: var(--element-inactive-color);
    }

.wrapper.enhanced .value {
      font-family: var(--global-typography-font-family);
      font-weight: var(
    --global-typography-instrument-value-large-font-weight-active
  );
      font-size: var(--global-typography-instrument-value-large-font-size);
      line-height: var(--global-typography-instrument-value-large-line-height);
      letter-spacing: var(
    --global-typography-instrument-value-large-letter-spacing
  );
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    }

.wrapper .divider {
    height: var(--instrument-components-readout-divider-height-regular);
    width: 1px;
    background-color: var(--border-outline-color);
    border-radius: 1px;
    margin: 0
      calc(var(--instrument-components-readout-padding-horizontal) - 0.5px);
  }

.wrapper.regular .divider {
    height: var(--instrument-components-readout-divider-height-small);
  }

.wrapper:has(.src-picker) .src-divider {
    margin-right: 0;
  }

.wrapper .src:has(.src-picker) {
    padding-left: 0;
  }

.wrapper .src-picker {
    anchor-name: --src-picker;
  }

.wrapper .src-picker::part(visible-wrapper) {
    padding: 0;
    padding-left: calc(
      var(--instrument-components-readout-padding-horizontal) - 0.5px +
        var(--instrument-components-readout-icon-spacing)
    );
    border: 0;
  }

.wrapper .src-picker::part(label) {
    padding: 0;
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-body-font-weight);
    font-size: var(--global-typography-ui-body-font-size);
    line-height: var(--global-typography-ui-body-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    color: var(--element-neutral-color);
  }

.wrapper.center .label {
  justify-content: center;
}

.src-picker-content {
  position: absolute;
  position-anchor: --src-picker;
  top: calc(anchor(bottom) - 8px);
  left: anchor(left);
}
`;var l_=Object.defineProperty,c_=Object.getOwnPropertyDescriptor,Cv=(e,t,o,r)=>{for(var i=r>1?void 0:r?c_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&l_(t,o,i),i},G1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M8.9313 10C8.32548 10 8.02257 10 7.88231 10.1198C7.76061 10.2237 7.69602 10.3797 7.70858 10.5392C7.72305 10.7231 7.93724 10.9373 8.36561 11.3657L11.4342 14.4343C11.6323 14.6323 11.7313 14.7313 11.8454 14.7684C11.9458 14.8011 12.054 14.8011 12.1544 14.7684C12.2686 14.7313 12.3676 14.6323 12.5656 14.4343L15.6342 11.3657C16.0626 10.9373 16.2768 10.7231 16.2913 10.5392C16.3038 10.3797 16.2392 10.2237 16.1175 10.1198C15.9773 10 15.6744 10 15.0686 10H8.9313Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M8.9313 10C8.32548 10 8.02257 10 7.88231 10.1198C7.76061 10.2237 7.69602 10.3797 7.70858 10.5392C7.72305 10.7231 7.93724 10.9373 8.36561 11.3657L11.4342 14.4343C11.6323 14.6323 11.7313 14.7313 11.8454 14.7684C11.9458 14.8011 12.054 14.8011 12.1544 14.7684C12.2686 14.7313 12.3676 14.6323 12.5656 14.4343L15.6342 11.3657C16.0626 10.9373 16.2768 10.7231 16.2913 10.5392C16.3038 10.3797 16.2392 10.2237 16.1175 10.1198C15.9773 10 15.6744 10 15.0686 10H8.9313Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};G1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Cv([h({type:Boolean})],G1.prototype,"useCssColor",2);G1=Cv([L("obi-drop-down-google")],G1);var xv=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

.wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  height: var(--menu-navigation-components-navigation-item-touch-target-size);
  transition: height 200ms;
  text-decoration: none;
  user-select: none;
}

.wrapper:focus-visible {
    outline-offset: -2px;
  }

.wrapper {
  cursor: pointer;
}

.wrapper:focus {
  outline: none;
}

.wrapper .visible-wrapper {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.wrapper.activated .visible-wrapper {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.wrapper:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper:active .visible-wrapper {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.wrapper:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper:disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper:disabled {
  cursor: not-allowed;
}

.wrapper.disabled {
  cursor: not-allowed;
}

.wrapper {
  color: var(--on-flat-active-color);
}

.wrapper .visible-wrapper {
    display: flex;
    align-items: center;
    width: 100%;
    height: 100%;
    border-radius: var(
      --menu-navigation-components-navigation-item-border-radius
    );
    padding: 0px
      calc(
        var(
            --menu-navigation-components-navigation-item-margin-horizontal-list-item
          ) +
          var(--menu-navigation-components-navigation-item-padding-horizontal)
      );
  }

.wrapper {

  font-family: var(--global-typography-font-family);

  font-weight: var(--global-typography-ui-body-font-weight);

  font-size: var(--global-typography-ui-body-font-size);

  line-height: var(--global-typography-ui-body-line-height);

  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
}

.wrapper.full .flyout-wrapper {
    display: flex;
    width: var(
      --menu-navigation-components-navigation-item-flyout-icon-container-size
    );
    align-items: center;
  }

:is(.wrapper.full .flyout-wrapper) .icon {
      flex-shrink: 0;
    }

.wrapper.icon-only,.wrapper.icon-only-large {
    width: var(--menu-navigation-components-navigation-item-touch-target-size);
    padding: var(
        --menu-navigation-components-navigation-item-margin-vertical-icon-button
      )
      var(
        --menu-navigation-components-navigation-item-margin-horizontal-icon-button
      );
  }

:is(.wrapper.icon-only,.wrapper.icon-only-large) .visible-wrapper {
      position: relative;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

.wrapper.icon-only-large {
    width: var(--menu-navigation-components-navigation-item-touch-target-size);
    height: var(--menu-navigation-components-navigation-item-touch-target-size);
    padding: 0;
  }

.wrapper.icon-only-large .icon.leading {
      anchor-name: --leading-icon;
    }

.wrapper.icon-only-large .icon.trailing {
      width: var(--menu-navigation-components-navigation-item-icon-size);
      height: var(--menu-navigation-components-navigation-item-icon-size);
      flex-shrink: 0;
      position: absolute;
      right: anchor(right);
      transform: translateX(60%);
      position-anchor: --leading-icon;
      top: anchor(top);
      bottom: anchor(bottom);
      margin: auto;
    }

.wrapper.compact {
    position: relative;
    width: var(
      --menu-navigation-components-navigation-item-touch-target-size-large
    );
    height: var(
      --menu-navigation-components-navigation-item-touch-target-size-large
    );
    padding: var(
        --menu-navigation-components-navigation-item-margin-vertical-icon-button
      )
      var(
        --menu-navigation-components-navigation-item-margin-horizontal-icon-button
      );
  }

.wrapper.compact .visible-wrapper {
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

.wrapper.compact .icon.leading {
      anchor-name: --leading-icon;
    }

.wrapper.compact .icon.trailing {
      width: var(--menu-navigation-components-navigation-item-icon-size);
      height: var(--menu-navigation-components-navigation-item-icon-size);
      flex-shrink: 0;
      position: absolute;
      right: anchor(right);
      transform: translateX(60%);
      position-anchor: --leading-icon;
      top: anchor(top);
      bottom: anchor(bottom);
      margin: auto;
    }

.wrapper.compact .label {
      font-family: var(--global-typography-font-family);
      font-weight: var(--global-typography-ui-label-font-weight);
      font-size: var(--global-typography-ui-label-font-size);
      line-height: var(--global-typography-ui-label-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      flex-grow: 0;
      flex-basis: auto;
    }

.checked :is(.wrapper.compact .label) {
        font-family: var(--global-typography-font-family);
        font-weight: var(--global-typography-ui-label-active-font-weight);
        font-size: var(--global-typography-ui-label-active-font-size);
        line-height: var(--global-typography-ui-label-active-line-height);
        font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      }

.wrapper.checked {
  cursor: pointer;
}

.wrapper.checked:focus {
  outline: none;
}

.wrapper.checked .visible-wrapper {
  border-color: var(--amplified-enabled-border-color);
  background-color: var(--amplified-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--amplified-enabled-border-color);
  --base-background-color: var(--amplified-enabled-background-color);
}

.wrapper.checked.activated .visible-wrapper {
  border-color: var(--amplified-activated-border-color);
  background-color: var(--amplified-activated-background-color);
  --base-border-color: var(--amplified-activated-border-color);
  --base-background-color: var(--amplified-activated-background-color);
}

@media (hover:hover) {

.wrapper.checked:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--amplified-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--amplified-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.checked:active .visible-wrapper {
  border-color: var(--amplified-pressed-border-color);
  background-color: var(--amplified-pressed-background-color);
}

.wrapper.checked:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.checked:disabled .visible-wrapper {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.wrapper.checked.disabled .visible-wrapper {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.wrapper.checked:disabled {
  cursor: not-allowed;
}

.wrapper.checked.disabled {
  cursor: not-allowed;
}

.wrapper.checked {
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-body-active-font-weight);
    font-size: var(--global-typography-ui-body-active-font-size);
    line-height: var(--global-typography-ui-body-active-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
}

.wrapper.checked .icon.leading {
      color: var(--instrument-enhanced-secondary-color);
    }

.wrapper.group-selected .visible-wrapper {
    background: var(--flat-pressed-background-color);
    border-color: var(--flat-hover-border-color);
  }

.wrapper .icon {
    display: flex;
    align-items: center;
    color: var(--on-flat-neutral-color);
  }

.wrapper.full.has-icon .icon.leading {
    margin-right: var(
      --menu-navigation-components-navigation-item-label-spacing
    );
  }

.wrapper ::slotted([slot="icon"]),.wrapper ::slotted([slot="trailing-icon"]) {
    display: block;
    width: var(--menu-navigation-components-navigation-item-icon-size);
    height: var(--menu-navigation-components-navigation-item-icon-size);
  }

.wrapper .icon.trailing {
    width: var(--menu-navigation-components-navigation-item-icon-size);
    height: var(--menu-navigation-components-navigation-item-icon-size);
  }

.wrapper .label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
  }

obc-tree-navigation-item.tree {
  display: block;
  width: 100%;
}
`;var d_=Object.defineProperty,h_=Object.getOwnPropertyDescriptor,_v=(e,t,o,r)=>{for(var i=r>1?void 0:r?h_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&d_(t,o,i),i},Y1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M9.5 15.0687C9.5 15.6745 9.5 15.9774 9.6198 16.1177C9.72374 16.2394 9.87967 16.304 10.0392 16.2914C10.2231 16.2769 10.4373 16.0627 10.8657 15.6344L13.9343 12.5657C14.1323 12.3677 14.2313 12.2687 14.2684 12.1546C14.3011 12.0541 14.3011 11.946 14.2684 11.8455C14.2313 11.7314 14.1323 11.6324 13.9343 11.4344L10.8657 8.36573C10.4373 7.93736 10.2231 7.72317 10.0392 7.7087C9.87967 7.69614 9.72374 7.76073 9.6198 7.88243C9.5 8.0227 9.5 8.3256 9.5 8.93142L9.5 15.0687Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M9.5 15.0687C9.5 15.6745 9.5 15.9774 9.6198 16.1177C9.72374 16.2394 9.87967 16.304 10.0392 16.2914C10.2231 16.2769 10.4373 16.0627 10.8657 15.6344L13.9343 12.5657C14.1323 12.3677 14.2313 12.2687 14.2684 12.1546C14.3011 12.0541 14.3011 11.946 14.2684 11.8455C14.2313 11.7314 14.1323 11.6324 13.9343 11.4344L10.8657 8.36573C10.4373 7.93736 10.2231 7.72317 10.0392 7.7087C9.87967 7.69614 9.72374 7.76073 9.6198 7.88243C9.5 8.0227 9.5 8.3256 9.5 8.93142L9.5 15.0687Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Y1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;_v([h({type:Boolean})],Y1.prototype,"useCssColor",2);Y1=_v([L("obi-arrow-flyout-google")],Y1);var kv=M`* {
  -webkit-tap-highlight-color: transparent;
}

.wrapper {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 100%;
  width: 320px;
  background: var(--container-global-color, #fcfcfc);
  box-shadow: var(--shadow-flat);
}

.wrapper nav {
    padding: var(--app-components-navigation-menu-margin-vertical)
      var(--app-components-navigation-menu-footer-margin-horizontal);
  }

.wrapper.icon-only,.wrapper.compact {
    width: fit-content;
  }

:is(.wrapper.icon-only,.wrapper.compact) nav.main {
      padding: var(--app-components-navigation-menu-margin-vertical) 0px;
    }

:is(.wrapper.icon-only,.wrapper.compact) .footer nav {
      padding: 0;
    }

.wrapper.icon-only-large {
    width: fit-content;
  }

.wrapper .main {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
  }

.wrapper .footer {
    display: flex;
    flex-direction: column;
    border-top: 1px solid var(--border-outline-color);
    flex: 0 0 auto;
  }

.wrapper.small-screen .footer nav ol {
    display: flex;
    justify-content: space-around;
    width: 100%;
  }

.full .footer.has-footer nav {
  border-bottom: 1px solid var(--border-outline-color);
}

.full .logo {
  height: 96px;
  width: 100%;
}

.icon-only-large .footer nav {
  padding-bottom: 0;
}

.icon-only-large .logo {
  padding: var(--app-components-navigation-menu-margin-vertical)
    var(--app-components-navigation-menu-footer-margin-horizontal);
  padding-top: 0;
  height: calc(
    var(--menu-navigation-components-navigation-item-touch-target-size) +
      var(--app-components-navigation-menu-margin-vertical)
  );
}

.icon-only .logo {
  height: var(--menu-navigation-components-navigation-item-touch-target-size);
}

.compact .logo {
  height: var(
    --menu-navigation-components-navigation-item-touch-target-size-large
  );
}

.logo {
  transition: height 200ms;
}

.wrapper:not(.small-screen) ::slotted([slot="logo"]) {
  width: 100%;
}

ol {
  list-style: none;
  margin: 0;
  padding: 0;
}
`;var Lv=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: block;
}

.wrapper {
  display: flex;
  align-items: center;
  width: 100%;
  height: var(--menu-navigation-components-tree-navigation-item-touch-target);
  user-select: none;
}

.wrapper:focus-visible {
    outline-offset: -2px;
  }

.wrapper {
  cursor: pointer;
}

.wrapper:focus {
  outline: none;
}

.wrapper .visible-wrapper {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.wrapper.activated .visible-wrapper {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.wrapper:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper:active .visible-wrapper {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.wrapper:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper:disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper:disabled {
  cursor: not-allowed;
}

.wrapper.disabled {
  cursor: not-allowed;
}

.wrapper {
  font-family: var(--global-typography-font-family);
  font-weight: var(--global-typography-ui-body-font-weight);
  font-size: var(--global-typography-ui-body-font-size);
  line-height: var(--global-typography-ui-body-line-height);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  color: var(--on-flat-active-color);
}

.wrapper .visible-wrapper {
    display: flex;
    align-items: center;
    width: 100%;
    height: 100%;
    border-radius: var(--global-border-radius-border-radius-base);
    padding: 0
      var(--menu-navigation-components-tree-navigation-item-padding-horizontal);
  }

/*
   * A checked row is not re-selectable, so it stays on the amplified enabled
   * style with no hover/pressed feedback.
   */

.wrapper.checked {
  cursor: pointer;
}

.wrapper.checked:focus {
  outline: none;
}

.wrapper.checked .visible-wrapper {
  border-color: var(--amplified-enabled-border-color);
  background-color: var(--amplified-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--amplified-enabled-border-color);
  --base-background-color: var(--amplified-enabled-background-color);
}

.wrapper.checked.activated .visible-wrapper {
  border-color: var(--amplified-activated-border-color);
  background-color: var(--amplified-activated-background-color);
  --base-border-color: var(--amplified-activated-border-color);
  --base-background-color: var(--amplified-activated-background-color);
}

@media (hover:hover) {

.wrapper.checked:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--amplified-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--amplified-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.checked:active .visible-wrapper {
  border-color: var(--amplified-pressed-border-color);
  background-color: var(--amplified-pressed-background-color);
}

.wrapper.checked:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.checked:disabled .visible-wrapper {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.wrapper.checked.disabled .visible-wrapper {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.wrapper.checked:disabled {
  cursor: not-allowed;
}

.wrapper.checked.disabled {
  cursor: not-allowed;
}

.wrapper.checked {
    cursor: default;
}

.wrapper.checked .visible-wrapper,.wrapper.checked:hover .visible-wrapper,.wrapper.checked:active .visible-wrapper {
      background-color: var(--amplified-enabled-background-color);
      border-color: var(--amplified-enabled-border-color);
    }

.wrapper.checked .label {
      font-family: var(--global-typography-font-family);
      font-weight: var(--global-typography-ui-body-active-font-weight);
      font-size: var(--global-typography-ui-body-active-font-size);
      line-height: var(--global-typography-ui-body-active-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      color: var(--on-flat-active-color);
    }

.wrapper.checked .leading-icon {
      color: var(--on-amplified-active-color);
    }

/* Guide lines are tree structure, not row state, so they do not dim here. */

.wrapper.disabled {
    color: var(--on-flat-disabled-color);
  }

.wrapper.disabled .leading-icon {
      color: var(--on-flat-disabled-color);
    }

.tree-node-row {
  display: flex;
  align-items: center;
  height: 100%;
  flex-shrink: 0;
}

.branch {
  position: relative;
  height: 100%;
  width: var(--menu-navigation-components-branch-width);
  flex-shrink: 0;
}

/*
 * Guide lines all run on a rail at 75% of each 32px column and share the faint
 * outline color. Verticals and the dropdown bleed 1px past the row edges so they
 * cross the visible-wrapper's 1px transparent flat border and meet the adjacent
 * row's line with no seam gap.
 */

.branch-vertical {
  position: absolute;
  top: -1px;
  bottom: -1px;
  left: 75%;
  width: 1px;
  transform: translateX(-0.5px);
  background: var(--border-outline-color);
}

.branch-horizontal {
  position: absolute;
  top: 50%;
  transform: translateY(-0.5px);
  left: 75%;
  right: 0;
  height: 1px;
  background: var(--border-outline-color);
}

/*
 * Corner (└, last child): a single bordered box replaces the straight rects so
 * the bend can be rounded. The box bleeds 1px past the column's right edge so its
 * bottom border overlaps the terminal connector with no break, and translateY
 * drops it 0.5px so that border lands on the connector's pixel row (else the join
 * reads as a \`---___\` step). The radius stays tight — the stub is only 8px, so a
 * larger fillet would consume the whole flat run.
 */

.branch-corner .branch-vertical,
.branch-corner .branch-horizontal {
  display: none;
}

.branch-corner .branch-elbow {
  position: absolute;
  top: -1px;
  bottom: 50%;
  left: 75%;
  right: -1px;
  transform: translate(-0.5px, 0.5px);
  border-left: 1px solid var(--border-outline-color);
  border-bottom: 1px solid var(--border-outline-color);
  border-bottom-left-radius: var(
    --menu-navigation-components-branch-corner-radius,
    2px
  );
}

.terminal {
  position: relative;
  height: 100%;
  width: var(--global-size-spacing-touch-target-min);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Stub entering the terminal, continuing the guide line up to the chevron gap. */

.terminal-connector {
  position: absolute;
  top: 50%;
  transform: translateY(-0.5px);
  left: 0;
  width: 25%;
  height: 1px;
  background: var(--border-outline-color);
}

/* On a leaf (no chevron) the stub runs further, stopping ~13px before the icon. */

.terminal:not(:has(.chevron)) .terminal-connector {
  width: calc(100% - 13px);
}

/* Descends from below the chevron to connect an expanded node to its children. */

.terminal-dropdown {
  position: absolute;
  left: 50%;
  transform: translateX(-0.5px);
  top: 75%;
  bottom: -1px;
  width: 1px;
  background: var(--border-outline-color);
}

/* Visual expand/collapse indicator only — not a separate control. */

.chevron {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--menu-navigation-components-tree-navigation-item-icon-size);
  height: var(--menu-navigation-components-tree-navigation-item-icon-size);
  color: var(--element-neutral-color);
  transition: transform 100ms ease-in-out;
}

@media (prefers-reduced-motion: reduce) {
  .chevron {
    transition: none;
  }
}

.wrapper.disabled .chevron {
  color: var(--on-flat-disabled-color);
}

:host([expanded]) .chevron {
  transform: rotate(90deg);
}

/* Alert-header marker for non-regular terminal types, at the terminal's top-right. */

.terminal-header {
  position: absolute;
  inset: 0;
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  padding: var(--menu-navigation-components-terminal-padding-aggregated-icon);
  color: var(--element-neutral-color);
  pointer-events: none;
}

.terminal-header > * {
  width: var(--menu-navigation-components-tree-navigation-item-icon-size);
  height: var(--menu-navigation-components-tree-navigation-item-icon-size);
}

.wrapper.disabled .terminal-header {
  color: var(--on-flat-disabled-color);
}

.label-container {
  display: flex;
  flex: 1;
  gap: var(
    --menu-navigation-components-tree-navigation-item-padding-horizontal
  );
  align-items: center;
  min-width: 0;
  padding-right: var(
    --menu-navigation-components-tree-navigation-item-padding-horizontal
  );
}

.leading-icon {
  position: relative;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--menu-navigation-components-tree-navigation-item-icon-size);
  height: var(--menu-navigation-components-tree-navigation-item-icon-size);
  color: var(--on-flat-neutral-color);
}

::slotted([slot="icon"]) {
  display: block;
  width: var(--menu-navigation-components-tree-navigation-item-icon-size);
  height: var(--menu-navigation-components-tree-navigation-item-icon-size);
}

.label {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}

/*
 * Trailing badge area. A row can carry more than one alert badge (e.g. a
 * critical count beside a warning count); they sit in a flex row spaced by the
 * shared alert-counter spacing token.
 */

.alert-badges {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: var(--app-components-alert-counter-item-badge-spacing);
}

.alert-badge {
  flex-shrink: 0;
}
`;var p_=Object.defineProperty,u_=Object.getOwnPropertyDescriptor,Sv=(e,t,o,r)=>{for(var i=r>1?void 0:r?u_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&p_(t,o,i),i},q1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M8.59009 7.41L10.0001 6L16.0001 12L10.0001 18L8.59009 16.59L13.1701 12L8.59009 7.41Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M8.59009 7.41L10.0001 6L16.0001 12L10.0001 18L8.59009 16.59L13.1701 12L8.59009 7.41Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};q1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Sv([h({type:Boolean})],q1.prototype,"useCssColor",2);q1=Sv([L("obi-chevron-right-google")],q1);var f_=Object.defineProperty,g_=Object.getOwnPropertyDescriptor,Mv=(e,t,o,r)=>{for(var i=r>1?void 0:r?g_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&f_(t,o,i),i},X1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M13 2H11V5H8V7H11V10H13V7H16V5H13V2Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M13 2H11V5H8V7H11V10H13V7H16V5H13V2Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};X1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Mv([h({type:Boolean})],X1.prototype,"useCssColor",2);X1=Mv([L("obi-alert-header-aggregated-iec")],X1);var m_=Object.defineProperty,v_=Object.getOwnPropertyDescriptor,$v=(e,t,o,r)=>{for(var i=r>1?void 0:r?v_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&m_(t,o,i),i},K1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M13 2H11V5H8V7H11V10H13V7H16V5H13V2Z" fill="currentColor"/>
<path d="M19 8H17V11H14V13H17V16H19V13H22V11H19V8Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M13 2H11V5H8V7H11V10H13V7H16V5H13V2Z" style="fill: var(--element-active-color)"/>
<path d="M19 8H17V11H14V13H17V16H19V13H22V11H19V8Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};K1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;$v([h({type:Boolean})],K1.prototype,"useCssColor",2);K1=$v([L("obi-alert-header-group-iec")],K1);var Av=M`* {
  -webkit-tap-highlight-color: transparent;
}

.wrapper {
  user-select: none;
  display: flex;
  align-items: center;
  justify-content: center;
  border-style: solid;
  border-radius: var(--ui-components-badge-border-radius);
  padding: calc(var(--ui-components-badge-padding) - 1px);
  border: 1px solid var(--alert-alarm-outline-color);
  background: var(--alert-alarm-color);
  width: fit-content;
  height: 16px;
  box-sizing: border-box;
}

.wrapper .badge-icon {
    width: 100%;
    height: 100%;
  }

.wrapper .icon {
    width: var(--ui-components-badge-icon-size);
    height: var(--ui-components-badge-icon-size);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

.wrapper .number {
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-label-active-font-weight);
    font-size: var(--global-typography-ui-label-active-font-size);
    line-height: var(--global-typography-ui-label-active-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 0 var(--ui-components-badge-label-spacing) 1px
      var(--ui-components-badge-label-spacing);
    height: var(--ui-components-badge-icon-size);
    min-width: var(--ui-components-badge-icon-size);
  }

.wrapper.size-large {
    display: inline-flex;
    width: fit-content;
    height: 24px;
    min-width: var(--ui-components-badge-min-size-large);
    min-height: var(--ui-components-badge-min-size-large);

    padding: calc(var(--ui-components-badge-padding) - 1px);
    justify-content: center;
    align-items: center;
    background: var(--alert-alarm-color);
  }

.wrapper.size-large .number {
      padding-bottom: 0;
    }

.wrapper.size-large .number-text {
      font-family: var(--global-typography-font-family);
      font-weight: var(--global-typography-ui-body-active-font-weight);
      font-size: var(--global-typography-ui-body-active-font-size);
      line-height: var(--global-typography-ui-body-active-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    }

.wrapper.size-large .icon {
      width: var(--ui-components-badge-icon-size-large);
      height: var(--ui-components-badge-icon-size-large);
      display: flex;
      align-items: center;
      justify-content: center;
    }

.wrapper.size-large.type-empty {
      min-width: 38px;
      height: 24px;
    }

.wrapper.type-regular {
    color: var(--on-normal-neutral-color);
    background-color: var(--normal-enabled-background-color);
    border-color: var(--normal-enabled-border-color);
  }

.wrapper.type-alarm {
    background-color: var(--alert-alarm-color);
    border-color: var(--alert-alarm-outline-color);
    color: var(--on-alarm-color);
  }

.wrapper.type-warning {
    background-color: var(--alert-warning-color);
    border-color: var(--alert-warning-outline-color);
    color: var(--on-warning-color);
  }

.wrapper.type-caution,.wrapper.type-level-low {
    background-color: var(--alert-caution-color);
    border-color: var(--alert-caution-outline-color);
    color: var(--on-caution-color);
  }

.wrapper.type-level-critical {
    background-color: var(--critical-enabled-background-color);
    border-color: var(--critical-enabled-border-color);
    color: var(--on-critical-color);
  }

.wrapper.type-level-high {
    background-color: var(--alert-alarm-color);
    border-color: var(--alert-alarm-outline-color);
    color: var(--on-alarm-color);
  }

.wrapper.type-level-medium {
    background-color: var(--alert-warning-color);
    border-color: var(--alert-warning-outline-color);
    color: var(--on-warning-color);
  }

.wrapper.type-level-diagnostic {
    background-color: var(--notification-enabled-background-color);
    border-color: var(--notification-enabled-border-color);
    color: var(--on-notification-active-color);
  }

.wrapper.type-running {
    background-color: var(--alert-running-color);
    border-color: var(--alert-running-color);
    color: var(--on-running-color);
  }

.wrapper.type-notification {
    background-color: var(--instrument-enhanced-primary-color);
    border-color: var(--instrument-enhanced-primary-color);
    color: var(--on-selected-active-color);
  }

.wrapper.type-enhance {
    background-color: var(--instrument-enhanced-secondary-color);
    border-color: var(--instrument-enhanced-secondary-color);
    color: var(--on-selected-active-color);
  }

.wrapper.type-empty {
    background-color: var(--flat-enabled-background-color);
    border-color: var(--normal-enabled-border-color);
    min-width: 28px;
  }

.wrapper.type-automation {
    background-color: var(--container-background-color);
    border-color: var(--container-background-color);
    color: var(--on-flat-neutral-color);
  }

.wrapper.variant-flat {
    background-color: var(--flat-enabled-background-color);
    border-color: var(--flat-enabled-background-color);
  }

.wrapper.variant-flat .icon {
      min-width: var(--ui-components-badge-icon-size);
      min-height: var(--ui-components-badge-icon-size);
    }

.wrapper.variant-flat .icon.type-alarm {
      color: unset;
      border-color: var(--alert-alarm-outline-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-warning {
      color: unset;
      border-color: var(--alert-warning-outline-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-caution,.wrapper.variant-flat .icon.type-level-low {
      color: unset;
      border-color: var(--alert-caution-outline-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-level-critical {
      color: unset;
      border-color: var(--critical-enabled-border-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-level-high {
      color: unset;
      border-color: var(--alert-alarm-outline-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-level-medium {
      color: unset;
      border-color: var(--alert-warning-outline-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-level-diagnostic {
      color: unset;
      border-color: var(--notification-enabled-border-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-regular {
      color: unset;
      border-color: var(--normal-enabled-border-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-notification {
      color: var(--instrument-enhanced-primary-color);
      border-color: var(
        --instrument-enhanced-primary-outline-color,
        transparent
      );
      background: none;
    }

.wrapper.variant-flat .icon.type-enhance {
      color: var(--instrument-enhanced-secondary-color);
      background: none;
    }

.wrapper.variant-flat .icon.type-regular {
      color: var(--on-normal-neutral-color);
    }

.wrapper.variant-flat .number {
      color: var(--element-active-color);
    }

.wrapper.variant-flat .icon.type-automation {
      color: unset;
      background: none;
    }

.wrapper.variant-flat .icon.type-outline {
      width: var(--ui-components-badge-icon-size-flat);
      height: var(--ui-components-badge-icon-size-flat);
    }

.wrapper.variant-flat .icon.type-outline + .number {
      color: var(--on-normal-neutral-color);
    }

.icon.type-alarm path {
  stroke: var(--alert-alarm-outline-color);
}

.icon.type-warning circle {
  stroke: var(--alert-warning-outline-color);
}

.icon.type-caution path {
  stroke: var(--alert-caution-outline-color);
}

.icon.type-running path {
  stroke: none;
}
`;var b_=Object.defineProperty,w_=Object.getOwnPropertyDescriptor,hs=(e,t,o,r)=>{for(var i=r>1?void 0:r?w_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&b_(t,o,i),i};var Fr=class extends S{constructor(){super(...arguments),this.number=0,this.showNumber=!0,this.type="regular",this.size="regular",this.variant="default",this.showIcon=!1}get effectiveType(){return!this.showIcon&&!this.showNumber?"empty":this.type}renderIcon(){let e=this.variant==="flat";switch(this.type){case"alarm":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <path
              d="M5.29694 1.72622L1.05702 9.32693C0.838739 9.71823 0.729598 9.91388 0.748108 10.0741C0.764257 10.2138 0.83853 10.3403 0.952704 10.4225C1.08357 10.5167 1.3076 10.5167 1.75567 10.5167H10.233C10.6809 10.5167 10.9049 10.5167 11.0357 10.4225C11.1499 10.3403 11.2242 10.2139 11.2404 10.0741C11.2589 9.914 11.1498 9.71837 10.9317 9.3271L6.69433 1.7264C6.46616 1.31712 6.35207 1.11247 6.20181 1.04447C6.07082 0.985194 5.92064 0.985175 5.78964 1.04442C5.63936 1.11238 5.52522 1.317 5.29694 1.72622Z"
              fill=${e?"var(--alert-alarm-color)":"currentColor"}
            />
          </svg>
        `;case"warning":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <circle
              cx="6"
              cy="6"
              r="4.5"
              fill=${e?"var(--alert-warning-color)":"currentColor"}
              stroke=${e?"var(--alert-warning-outline-color)":"currentColor"}
            />
          </svg>
        `;case"caution":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <path
              d="M2.2998 2H9.7002C9.848 2 9.92907 2.00015 9.9873 2.00488C9.98955 2.00507 9.99213 2.0047 9.99414 2.00488C9.99436 2.0072 9.9949 2.01006 9.99512 2.0127C9.99985 2.07093 10 2.152 10 2.2998V9.7002C10 9.848 9.99985 9.92907 9.99512 9.9873C9.99493 9.98958 9.99433 9.9921 9.99414 9.99414C9.9921 9.99433 9.98958 9.99493 9.9873 9.99512C9.92907 9.99985 9.848 10 9.7002 10H2.2998C2.152 10 2.07093 9.99985 2.0127 9.99512C2.01006 9.9949 2.0072 9.99436 2.00488 9.99414C2.0047 9.99213 2.00507 9.98955 2.00488 9.9873C2.00015 9.92907 2 9.848 2 9.7002V2.2998L2.00488 2.0127C2.0051 2.01009 2.00467 2.00718 2.00488 2.00488C2.00718 2.00467 2.01009 2.0051 2.0127 2.00488L2.2998 2Z"
              fill=${e?"var(--alert-caution-color)":"currentColor"}
              stroke=${e?"var(--alert-caution-outline-color)":"currentColor"}
            />
          </svg>
        `;case"level-high":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <path
              d="M5.29694 1.72622L1.05702 9.32693C0.838739 9.71823 0.729598 9.91388 0.748108 10.0741C0.764257 10.2138 0.83853 10.3403 0.952704 10.4225C1.08357 10.5167 1.3076 10.5167 1.75567 10.5167H10.233C10.6809 10.5167 10.9049 10.5167 11.0357 10.4225C11.1499 10.3403 11.2242 10.2139 11.2404 10.0741C11.2589 9.914 11.1498 9.71837 10.9317 9.3271L6.69433 1.7264C6.46616 1.31712 6.35207 1.11247 6.20181 1.04447C6.07082 0.985194 5.92064 0.985175 5.78964 1.04442C5.63936 1.11238 5.52522 1.317 5.29694 1.72622Z"
              fill=${e?"var(--alert-alarm-color)":"currentColor"}
            />
          </svg>
        `;case"level-medium":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <circle
              cx="6"
              cy="6"
              r="4.5"
              fill=${e?"var(--alert-warning-color)":"currentColor"}
              stroke=${e?"var(--alert-warning-outline-color)":"currentColor"}
            />
          </svg>
        `;case"level-low":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <path
              d="M2.2998 2H9.7002C9.848 2 9.92907 2.00015 9.9873 2.00488C9.98955 2.00507 9.99213 2.0047 9.99414 2.00488C9.99436 2.0072 9.9949 2.01006 9.99512 2.0127C9.99985 2.07093 10 2.152 10 2.2998V9.7002C10 9.848 9.99985 9.92907 9.99512 9.9873C9.99493 9.98958 9.99433 9.9921 9.99414 9.99414C9.9921 9.99433 9.98958 9.99493 9.9873 9.99512C9.92907 9.99985 9.848 10 9.7002 10H2.2998C2.152 10 2.07093 9.99985 2.0127 9.99512C2.01006 9.9949 2.0072 9.99436 2.00488 9.99414C2.0047 9.99213 2.00507 9.98955 2.00488 9.9873C2.00015 9.92907 2 9.848 2 9.7002V2.2998L2.00488 2.0127C2.0051 2.01009 2.00467 2.00718 2.00488 2.00488C2.00718 2.00467 2.01009 2.0051 2.0127 2.00488L2.2998 2Z"
              fill=${e?"var(--alert-caution-color)":"currentColor"}
              stroke=${e?"var(--alert-caution-outline-color)":"currentColor"}
            />
          </svg>
        `;case"level-critical":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <path
              d="M11 6L8.5 10.33H3.5L1 6L3.5 1.67H8.5L11 6Z"
              fill=${e?"var(--critical-enabled-background-color)":"currentColor"}
            />
          </svg>
        `;case"level-diagnostic":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <path
              d="M5.25 1H6.75V5.7L9.955 3.85L10.705 5.15L7.5 7L10.705 8.85L9.955 10.15L6.75 8.3V11H5.25V8.3L2.045 10.15L1.295 8.85L4.5 7L1.295 5.15L2.045 3.85L5.25 5.7V1Z"
              fill=${e?"var(--notification-enabled-background-color)":"currentColor"}
            />
          </svg>
        `;case"running":return f`
          <svg width="100%" height="100%" viewBox="0 0 12 12" fill="none">
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M11 6C11 8.76142 8.76142 11 6 11C3.23858 11 1 8.76142 1 6C1 3.23858 3.23858 1 6 1C8.76142 1 11 3.23858 11 6ZM2.89624 6.10353L3.60335 5.39642L5.24979 7.04287L8.39624 3.89642L9.10335 4.60353L5.24979 8.45708L2.89624 6.10353Z"
              fill=${e?"var(--alert-running-color)":"currentColor"}
            />
          </svg>
        `;default:return f`<slot class="badge-icon" name="badge-icon"></slot>`}}render(){let e=this.variant==="flat";return f`
      <div
        class=${de({wrapper:!0,["size-"+this.size]:!0,["type-"+this.effectiveType]:!e,"variant-flat":e,hideNumber:!this.showNumber})}
      >
        ${this.effectiveType!=="empty"?f`
              ${this.showIcon?f`
                    <div
                      class=${de({icon:!0,["type-"+this.type]:e})}
                    >
                      ${this.renderIcon()}
                    </div>
                  `:z}
              ${this.showNumber?f`<div class="number">
                    <span class="number-text">${this.number}</span>
                  </div>`:""}
            `:""}
      </div>
    `}};Fr.styles=ne(Av);hs([h({type:Number})],Fr.prototype,"number",2);hs([h({type:Boolean,attribute:!1})],Fr.prototype,"showNumber",2);hs([h({type:String})],Fr.prototype,"type",2);hs([h({type:String})],Fr.prototype,"size",2);hs([h({type:String})],Fr.prototype,"variant",2);hs([h({type:Boolean})],Fr.prototype,"showIcon",2);Fr=hs([L("obc-badge")],Fr);var y_=Object.defineProperty,C_=Object.getOwnPropertyDescriptor,Ao=(e,t,o,r)=>{for(var i=r>1?void 0:r?C_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&y_(t,o,i),i},du=(e=>(e.straight="straight",e.intersection="intersection",e.corner="corner",e.blank="blank",e))(du||{}),hu=(e=>(e.regular="regular",e.aggregatedHeader="aggregated-header",e.groupHeader="group-header",e))(hu||{}),so=class extends S{constructor(){super(...arguments),this.label="List item",this.branches=[],this.expandable=!1,this.expanded=!1,this.checked=!1,this.disabled=!1,this.focusable=!0,this.hasLeadingIcon=!0,this.terminalType="regular"}focus(e){this.wrapperElement?.focus(e)}get alertBadges(){return this.alerts?B2(this.alerts,this.alerts.combine):[]}get isRoot(){return this.branches.length===0}get isBlankAncestry(){return this.branches.length>0&&this.branches.every(e=>e==="blank")}activate(){this.disabled||(this.expandable&&this.dispatchEvent(new CustomEvent("expand-toggle",{detail:!this.expanded})),!this.checked&&(this.dispatchEvent(new CustomEvent("click")),this.href!==void 0&&(window.location.href=this.href)))}handleKeydown(e){this.disabled||e.key!=="Enter"&&e.key!==" "||(e.preventDefault(),this.activate())}renderBranch(e){let t=e==="straight"||e==="intersection"||e==="corner",o=e==="intersection"||e==="corner";return f`<div
      class=${de({branch:!0,["branch-"+e]:!0})}
    >
      ${t?f`<div class="branch-vertical"></div>`:z}
      ${o?f`<div class="branch-horizontal"></div>`:z}
      ${e==="corner"?f`<div class="branch-elbow"></div>`:z}
    </div>`}renderTerminalHeader(){return this.terminalType==="aggregated-header"?f`<div class="terminal-header" aria-hidden="true">
        <obi-alert-header-aggregated-iec></obi-alert-header-aggregated-iec>
      </div>`:this.terminalType==="group-header"?f`<div class="terminal-header" aria-hidden="true">
        <obi-alert-header-group-iec></obi-alert-header-group-iec>
      </div>`:z}render(){return f`
      <div
        class=${de({wrapper:!0,checked:this.checked,disabled:this.disabled,"has-icon":this.hasLeadingIcon})}
        role="treeitem"
        aria-expanded=${Ce(this.expandable?this.expanded:void 0)}
        aria-current=${Ce(this.checked?"page":void 0)}
        aria-selected=${Ce(this.checked?"true":void 0)}
        aria-disabled=${Ce(this.disabled?"true":void 0)}
        tabindex=${this.disabled?-1:this.focusable?0:-1}
        @click=${this.activate}
        @keydown=${this.handleKeydown}
      >
        <div class="visible-wrapper">
          <div class="tree-node-row">
            ${this.branches.map(e=>this.renderBranch(e))}
            <div class="terminal">
              ${this.isRoot||this.isBlankAncestry?z:f`<div class="terminal-connector"></div>`}
              ${!this.isRoot&&!this.isBlankAncestry&&this.expandable&&this.expanded?f`<div class="terminal-dropdown"></div>`:z}
              ${this.expandable?f`<div class="chevron" aria-hidden="true">
                    <obi-chevron-right-google></obi-chevron-right-google>
                  </div>`:z}
              ${this.renderTerminalHeader()}
            </div>
          </div>
          <div class="label-container">
            ${this.hasLeadingIcon?f`<div class="leading-icon">
                  <slot name="icon"></slot>
                </div>`:z}
            <span part="label" class="label">${this.label}</span>
          </div>
          ${this.alertBadges.length>0?f`<div class="alert-badges">
                ${this.alertBadges.map(e=>f`<obc-badge
                      class="alert-badge"
                      .type=${e.type}
                      .number=${e.count}
                    ></obc-badge>`)}
              </div>`:z}
        </div>
      </div>
    `}};so.styles=ne(Lv);Ao([h({type:String})],so.prototype,"label",2);Ao([h({type:Array})],so.prototype,"branches",2);Ao([h({type:Boolean})],so.prototype,"expandable",2);Ao([h({type:Boolean,reflect:!0})],so.prototype,"expanded",2);Ao([h({type:Boolean,reflect:!0})],so.prototype,"checked",2);Ao([h({type:Boolean,reflect:!0})],so.prototype,"disabled",2);Ao([h({type:Boolean,attribute:!1})],so.prototype,"focusable",2);Ao([h({type:Boolean,attribute:!1})],so.prototype,"hasLeadingIcon",2);Ao([h({type:String})],so.prototype,"terminalType",2);Ao([h({type:Object})],so.prototype,"alerts",2);Ao([h({type:String})],so.prototype,"href",2);Ao([at(".wrapper")],so.prototype,"wrapperElement",2);so=Ao([L("obc-tree-navigation-item")],so);var Q1=class{constructor(t,o){this.adapter=o,this.host=t}isDisabled(t){return this.adapter.isDisabled?.(t)??!1}visibleRows(){let t=[],o=r=>{for(let i of r)t.push(i),this.adapter.isGroup(i)&&this.adapter.isExpanded(i)&&o(this.adapter.childRows(i))};return o(this.adapter.getRows()),t}navigableRows(){return this.visibleRows().filter(t=>!this.isDisabled(t))}parentRow(t){let o,r=(i,s)=>{for(let n of i){if(n===t){o=s;return}if(this.adapter.isGroup(n)&&(r(this.adapter.childRows(n),n),o!==void 0))return}};return r(this.adapter.getRows(),void 0),o}refresh(){let t=this.navigableRows();if(t.length===0){this.activeRow=void 0;return}let o;if(this.activeRow&&t.includes(this.activeRow))o=this.activeRow;else if(this.activeRow){let r=this.parentRow(this.activeRow);for(;r&&!t.includes(r);)r=this.parentRow(r);o=r??t[0]}else o=t[0];this.setActiveRow(o,!1)}setActiveRow(t,o){this.activeRow=t;for(let i of this.visibleRows()){let s=this.adapter.innerItem(i);s&&(s.focusable=i===t)}if(!o)return;let r=this.adapter.innerItem(t);r?r.focus():queueMicrotask(()=>this.adapter.innerItem(t)?.focus())}rowFromEvent(t){let o=this.host.getRootNode();for(let r of t.composedPath())if(r instanceof HTMLElement&&r.getRootNode()===o&&this.isRow(r))return r}isRow(t){let r=[...this.adapter.getRows()];for(;r.length;){let i=r.pop();if(i===t)return!0;this.adapter.isGroup(i)&&r.push(...this.adapter.childRows(i))}return!1}handleKeydown(t){let o=this.rowFromEvent(t);if(!o)return!1;switch(t.key){case"ArrowDown":return this.moveByOffset(o,1),!0;case"ArrowUp":return this.moveByOffset(o,-1),!0;case"ArrowRight":return this.onArrowRight(o),!0;case"ArrowLeft":return this.onArrowLeft(o),!0;case"Home":return this.moveToEdge(!0),!0;case"End":return this.moveToEdge(!1),!0;default:return!1}}moveByOffset(t,o){let r=this.navigableRows(),i=r.indexOf(t);if(i===-1)return;let s=r[i+o];s&&this.setActiveRow(s,!0)}moveToEdge(t){let o=this.navigableRows();o.length!==0&&this.setActiveRow(t?o[0]:o[o.length-1],!0)}onArrowRight(t){if(!this.adapter.isGroup(t))return;if(!this.adapter.isExpanded(t)){this.adapter.setExpanded(t,!0),this.refresh();return}let o=this.adapter.childRows(t).find(r=>!this.isDisabled(r));o&&this.setActiveRow(o,!0)}onArrowLeft(t){if(this.adapter.isGroup(t)&&this.adapter.isExpanded(t)){this.adapter.setExpanded(t,!1),this.refresh();return}let o=this.parentRow(t);o&&this.setActiveRow(o,!0)}};var x_=Object.defineProperty,__=Object.getOwnPropertyDescriptor,Ra=(e,t,o,r)=>{for(var i=r>1?void 0:r?__(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&x_(t,o,i),i},k_="obc-navigation-item",Ov="obc-navigation-item-group";function pu(e){return e.tagName.toLowerCase()===Ov}function Pv(e){let t=e.tagName.toLowerCase();return t===k_||t===Ov}var us=(e=>(e.Full="full",e.IconOnly="icon-only",e.IconOnlyLarge="icon-only-large",e.Compact="compact",e.Tree="tree",e))(us||{});var ps=class extends S{constructor(){super(...arguments),this.variant="full",this.flyoutVariant="full",this.smallScreen=!1,this.slotObservers=[],this.hasFooter=!1,this.treeNavigator=new Q1(this,{getRows:()=>this.treeRootRows(),childRows:e=>this.treeChildRows(e),isGroup:e=>pu(e),isExpanded:e=>pu(e)&&e.expanded,setExpanded:(e,t)=>{pu(e)&&(t?e.open():e.close())},innerItem:e=>this.treeInnerItem(e)}),this.onTreeKeydown=e=>{this.variant==="tree"&&this.treeNavigator.handleKeydown(e)&&e.preventDefault()}}treeRootRows(){return Array.from(this.children).filter(e=>{if(!Pv(e))return!1;let t=e.getAttribute("slot");return t===null||t==="main"})}treeChildRows(e){return Array.from(e.children).filter(Pv)}treeInnerItem(e){return e.shadowRoot?.querySelector("obc-tree-navigation-item")??null}connectedCallback(){super.connectedCallback(),this.addEventListener("keydown",this.onTreeKeydown)}findAllElements(e,t,{slot:o,stopTag:r}={}){let i=[];for(let s of e.children)if(s.tagName.toLowerCase()===t){if(o&&s.getAttribute("slot")!==o)continue;i.push(s)}else{if(r&&s.tagName.toLowerCase()===r)continue;if(o&&s.getAttribute("slot")!==o)continue;i.push(...this.findAllElements(s,t,{stopTag:r}))}return i}findAllGroups(e){return this.findAllElements(e,"obc-navigation-item-group")}findRootItems(e){return this.findAllElements(e,"obc-navigation-item",{stopTag:"obc-navigation-item-group"})}findAllItems(e,t){return this.findAllElements(e,"obc-navigation-item",{slot:t})}closeAllGroups(){this.findAllGroups(this).forEach(t=>{t.close()})}registerGroup(e){e.forEach(t=>{t.addEventListener("open",()=>{this.variant!=="tree"&&e.forEach(r=>{r!==t&&r.close()})});let o=this.findAllGroups(t);this.registerGroup(o)})}cleanupSlotObservers(){this.slotObservers.forEach(e=>e.disconnect()),this.slotObservers=[]}setupSlotObservers(){this.cleanupSlotObservers();let e=this.shadowRoot?.querySelector('slot[name="main"]'),t=this.shadowRoot?.querySelector('slot[name="footer"]');this.hasFooter=t?.assignedElements().length>0,[e,t].forEach(o=>{o&&o.assignedElements().forEach(i=>{let s=new MutationObserver(()=>{this.setupItems()});s.observe(i,{childList:!0,subtree:!0}),this.slotObservers.push(s)})})}firstUpdated(e){super.firstUpdated(e);let t=this.findAllGroups(this);this.registerGroup(t)}updated(e){super.updated(e),(e.has("variant")||e.has("flyoutVariant"))&&this.setupItems()}setVariantToFlyoutItems(e){this.findAllElements(e,"obc-navigation-item").forEach(r=>{r.variant="full"}),this.findAllGroups(e).forEach(r=>{r.variant="full",this.setVariantToFlyoutItems(r)})}disconnectedCallback(){super.disconnectedCallback(),this.cleanupSlotObservers(),this.removeEventListener("keydown",this.onTreeKeydown)}handleSlotChange(){this.setupItems(),this.setupSlotObservers()}assignTreeBranches(e,t){for(let o of e.children){let r=o.tagName.toLowerCase(),i=r==="obc-navigation-item",s=r==="obc-navigation-item-group";if(!i&&!s)continue;if(t===0){let l=o.getAttribute("slot");if(l!==null&&l!=="main")continue}let n=Array.from({length:t},()=>du.blank),a=o;a.treeMode=!0,a.treeBranches=n,s&&this.assignTreeBranches(o,t+1)}}clearTreeMode(e){for(let t of e.children){let o=t.tagName.toLowerCase(),r=o==="obc-navigation-item",i=o==="obc-navigation-item-group";if(!r&&!i)continue;let s=t;s.treeMode=!1,s.treeBranches=[],i&&this.clearTreeMode(t)}}setupItems(){if(this.variant==="tree"){this.assignTreeBranches(this,0),["footer","logo"].forEach(r=>{this.findAllItems(this,r).forEach(i=>{i.treeMode=!1,i.treeBranches=[],i.variant="full"})}),queueMicrotask(()=>this.treeNavigator.refresh());return}this.clearTreeMode(this);let e=this.variant!=="full"||this.flyoutVariant==="compact";this.setHugToGroups(this,e),this.findAllGroups(this).forEach(r=>{r.variant=this.variant,this.setVariantToFlyoutItems(r)}),this.findRootItems(this).forEach(r=>{r.variant=this.variant});let o=this.smallScreen&&this.variant==="full"?"compact":this.variant;this.findAllItems(this,"footer").forEach(r=>{r.variant=o}),this.findAllItems(this,"logo").forEach(r=>{r.variant=o}),this.findAllItems(this).forEach(r=>{r.addEventListener("click",()=>{this.closeAllGroups()})})}setHugToGroups(e,t){this.findAllGroups(e).forEach(r=>{r.hug=t,this.setHugToGroups(r,t)})}render(){return f`
      <div
        class="wrapper ${this.variant} ${this.smallScreen?"small-screen":""}"
      >
        <nav class="main">
          <ol>
            <slot name="main" @slotchange=${this.handleSlotChange}></slot>
          </ol>
        </nav>
        <div class="footer ${this.hasFooter?"has-footer":""}">
          <nav>
            <ol>
              <slot name="footer" @slotchange=${this.handleSlotChange}></slot>
              ${this.smallScreen?f` <slot name="logo"></slot> `:z}
            </ol>
          </nav>
          ${this.smallScreen?z:f`
                <div class="logo">
                  <slot name="logo"></slot>
                </div>
              `}
        </div>
      </div>
    `}};ps.styles=ne(kv);Ra([h({type:String})],ps.prototype,"variant",2);Ra([h({type:String})],ps.prototype,"flyoutVariant",2);Ra([h({type:Boolean})],ps.prototype,"smallScreen",2);Ra([ke()],ps.prototype,"hasFooter",2);ps=Ra([L("obc-navigation-menu")],ps);var L_=Object.defineProperty,S_=Object.getOwnPropertyDescriptor,no=(e,t,o,r)=>{for(var i=r>1?void 0:r?S_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&L_(t,o,i),i},Wt=class extends S{constructor(){super(...arguments),this.label="Label",this.checked=!1,this.variant=us.Full,this.group=!1,this.groupSelected=!1,this.hasIcon=!1,this.hasTrailingIcon=!1,this.treeMode=!1,this.treeBranches=[],this.terminalType=hu.regular}handleKeydown(e){let t=this.getAttribute("role")==="menuitem";this.href!==void 0&&!t||e.key!=="Enter"&&e.key!==" "||(e.preventDefault(),this.anchorElement?.click())}focus(e){(this.treeItemElement??this.anchorElement)?.focus(e)}getItemRole(){return this.getAttribute("role")==="menuitem"?"menuitem":this.href===void 0?"button":void 0}getItemTabIndex(){let e=this.getAttribute("tabindex");if(e!==null){let t=Number(e);return Number.isNaN(t)?void 0:t}return this.href===void 0?0:void 0}render(){if(this.treeMode)return f`
        <obc-tree-navigation-item
          class="tree"
          .label=${this.label}
          .branches=${this.treeBranches}
          ?checked=${this.checked}
          .hasLeadingIcon=${this.hasIcon}
          .href=${this.href}
          .terminalType=${this.terminalType}
          .alerts=${this.alerts}
        >
          ${this.hasIcon?f`<slot name="icon" slot="icon"></slot>`:z}
        </obc-tree-navigation-item>
      `;let e=this.group&&this.variant!==us.IconOnly,t=this.variant===us.Compact;return f`
      <a
        class="${de({wrapper:!0,checked:this.checked,"group-selected":this.groupSelected&&this.group,"has-icon":this.hasIcon,[this.variant]:!0})}"
        href=${Ce(this.href)}
        @keydown=${this.handleKeydown}
        tabindex=${Ce(this.getItemTabIndex())}
        role=${Ce(this.getItemRole())}
      >
        <div class="visible-wrapper">
          ${this.hasIcon?f`<slot name="icon" class="icon leading"></slot>`:z}
          ${[us.IconOnly,us.IconOnlyLarge].includes(this.variant)?z:f`
                <span
                  part="label"
                  class=${de({label:!0,"label-flyout":e&&!t})}
                >
                  ${this.label}
                </span>
              `}
          ${e?f`
                <div class="flyout-wrapper">
                  <obi-arrow-flyout-google
                    class="icon trailing"
                  ></obi-arrow-flyout-google>
                </div>
              `:z}
          ${this.hasTrailingIcon&&!e?f`<slot name="trailing-icon" class="icon trailing"></slot>`:z}
        </div>
      </a>
    `}};Wt.styles=ne(xv);no([h({type:String})],Wt.prototype,"label",2);no([h({type:String})],Wt.prototype,"href",2);no([h({type:Boolean})],Wt.prototype,"checked",2);no([h({type:String})],Wt.prototype,"variant",2);no([h({type:Boolean})],Wt.prototype,"group",2);no([h({type:Boolean})],Wt.prototype,"groupSelected",2);no([h({type:Boolean,reflect:!0})],Wt.prototype,"hasIcon",2);no([h({type:Boolean})],Wt.prototype,"hasTrailingIcon",2);no([h({type:Boolean})],Wt.prototype,"treeMode",2);no([h({type:Array})],Wt.prototype,"treeBranches",2);no([h({type:String})],Wt.prototype,"terminalType",2);no([h({type:Object})],Wt.prototype,"alerts",2);no([at("a")],Wt.prototype,"anchorElement",2);no([at("obc-tree-navigation-item")],Wt.prototype,"treeItemElement",2);Wt=no([L("obc-navigation-item")],Wt);var M_=Object.defineProperty,$_=Object.getOwnPropertyDescriptor,At=(e,t,o,r)=>{for(var i=r>1?void 0:r?$_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&M_(t,o,i),i};var bt=class extends S{constructor(){super(...arguments),this.size="regular",this.hasSetpoint=!1,this.hasSrc=!1,this.maxDigits=1,this.showZeroPadding=!1,this.fractionDigits=0,this.tag="",this.unit="",this.src="",this.neutralColor=!1,this.horizontal=!1,this.center=!1,this.labelOnly=!1,this.off=!1,this.autoHideSetpoint=!1,this.autoHideDeadband=0}dashedGenerator(){let e=this.showZeroPadding?Math.max(this.maxDigits,1):1;if(this.fractionDigits<1)return Lr.repeat(e);{let t=e-this.fractionDigits;return Lr.repeat(Math.max(t,1))+"."+Lr.repeat(this.fractionDigits)}}render(){let e=this.hasSetpoint&&this.autoHideSetpoint&&this.setpoint!==void 0&&this.value!==void 0&&Math.abs(this.setpoint-this.value)<=this.autoHideDeadband;return f`
      <div
        class=${de({wrapper:!0,[this.size]:!0,"neutral-color":this.neutralColor,off:this.off,horizontal:this.horizontal,center:this.center,"left-aligned":this.labelOnly||this.horizontal&&!this.hasSetpoint,"hide-setpoint":e,"show-zero-padding":this.showZeroPadding})}
      >
        ${this.horizontal&&this.size==="regular"?f`<div class="label">
              <div class="tag" part="tag">${this.tag}</div>
            </div>`:z}
        ${this.hasSetpoint?f`<div class="setpoint">
              <svg
                class="setpoint-arrow"
                width="16"
                height="16"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  fill="var(--instrument-enhanced-secondary-color)"
                  d="M4.66797 4.80263C4.66797 4.14363 5.45194 3.76746 6.0013 4.16286L10.4456 7.17243C11.0312 7.56899 11.0314 8.43154 10.4459 8.82828L6.0013 11.8401C5.45194 12.2355 4.66797 11.8593 4.66797 11.2003L4.66797 4.80263Z"
                  fill="var(--instrument-enhanced-primary-color)"
                />
              </svg>
              <div class="setpoint-value">${this.setpointValueBlueNumbers}</div>
            </div>`:z}
        ${this.horizontal&&!this.labelOnly&&this.hasSetpoint?f`<div class="divider"></div>`:z}
        ${this.labelOnly?z:f` <div class="value">
              ${this.off?f`<div class="value-blue">
                    <slot name="off-value">OFF</slot>
                  </div>`:f` <div class="value-hint-zero">${this.hintZeros}</div>
                    <div class="value-blue">${this.valueBlueNumbers}</div>`}
            </div>`}
        <div class="label" part="label">
          ${this.horizontal&&this.size==="regular"?z:f`<div class="tag" part="tag">${this.tag}</div>`}
          <div class="unit">${this.unit}</div>
        </div>
        ${this.hasSrc&&this.horizontal?f`<div class="divider src-divider"></div>`:z}
        ${this.hasSrc?f`<div class="src">${this.src}</div>`:z}
      </div>
    `}get setpointValueBlueNumbers(){return this.setpoint===void 0?this.dashedGenerator():this.setpoint.toFixed(this.fractionDigits)}get valueBlueNumbers(){return this.value===void 0?this.dashedGenerator():this.value.toFixed(this.fractionDigits)}get hintZeros(){if(this.value===void 0||this.value<0)return"";let e=this.valueBlueNumbers.length,t=this.maxDigits-e;return t>0?"0".repeat(t):""}};bt.styles=ne(yv);At([h({type:String})],bt.prototype,"size",2);At([h({type:Number})],bt.prototype,"setpoint",2);At([h({type:Boolean})],bt.prototype,"hasSetpoint",2);At([h({type:Boolean})],bt.prototype,"hasSrc",2);At([h({type:Number})],bt.prototype,"value",2);At([h({type:Number})],bt.prototype,"maxDigits",2);At([h({type:Boolean})],bt.prototype,"showZeroPadding",2);At([h({type:Number})],bt.prototype,"fractionDigits",2);At([h({type:String})],bt.prototype,"tag",2);At([h({type:String})],bt.prototype,"unit",2);At([h({type:String})],bt.prototype,"src",2);At([h({type:Boolean})],bt.prototype,"neutralColor",2);At([h({type:Boolean})],bt.prototype,"horizontal",2);At([h({type:Boolean})],bt.prototype,"center",2);At([h({type:Boolean})],bt.prototype,"labelOnly",2);At([h({type:Boolean})],bt.prototype,"off",2);At([h({type:Boolean})],bt.prototype,"autoHideSetpoint",2);At([h({type:Number})],bt.prototype,"autoHideDeadband",2);bt=At([L("obc-instrument-field")],bt);var Vv=M`* {
  -webkit-tap-highlight-color: transparent;
}

.wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  user-select: none;
}

.alert-list {
  min-height: 0;
  flex-grow: 0;
}

.spacer {
  flex-grow: 1;
}

.action {
  display: flex;
  height: var(--app-components-tool-bar-touch-target-size);
  padding: 0px var(--app-components-alert-toolbar-margin-horizontal);
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  flex-grow: 0;
  border-top: 1px solid var(--border-divider-color);
  background: var(--container-section-color);
  box-shadow: var(--shadow-flat);
}

.action .btn-group {
    display: flex;
  }

obc-table::part(grid) {
  grid-template-columns: 1fr repeat(4, min-content);
}

.wrapper.small obc-table::part(grid) {
  grid-template-columns: 1fr min-content var(
      --app-components-alert-table-row-ack-container-width-small
    );
}

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--app-components-alert-menu-button-spacing);
}

.empty-list .icon {
    height: 96px;
    width: 96px;
    color: var(--on-flat-neutral-color);
  }

.empty-list .empty-title {
    color: var(--element-active-color);
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-body-active-font-weight);
    font-size: var(--global-typography-ui-body-active-font-size);
    line-height: var(--global-typography-ui-body-active-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.empty-list .empty-description {
    color: var(--element-neutral-color);
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-body-font-weight);
    font-size: var(--global-typography-ui-body-font-size);
    line-height: var(--global-typography-ui-body-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    max-width: 344px;
    text-align: center;
  }
`;var Tv=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

.wrapper {
  background: transparent;
  position: relative;
  min-height: var(--ui-components-button-touch-target-size);
  min-width: var(--ui-components-button-touch-target-size);
  padding: 0;

  appearance: none;
  border: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.wrapper .visible-wrapper {
    position: relative;
    height: var(--ui-components-icon-button-visual-target-size);
    width: var(--ui-components-icon-button-visual-target-size);
    box-sizing: border-box;
    border-radius: var(--ui-components-button-border-radius-top-left)
      var(--ui-components-button-border-radius-top-right)
      var(--ui-components-button-border-radius-bottom-right)
      var(--ui-components-button-border-radius-bottom-left);
    display: flex;
    align-items: center;
    justify-content: center;
  }

.wrapper.corner-left {
    align-items: flex-end;
    padding-right: 0;
  }

.wrapper.corner-left .visible-wrapper {
      width: calc(
        var(--ui-components-icon-button-visual-target-size) +
          var(--ui-components-icon-button-padding-right)
      );
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }

.wrapper.corner-left.hide-divider .visible-wrapper {
      border-right: none;
    }

.wrapper.corner-right {
    align-items: flex-start;
    padding-left: 0;
  }

.wrapper.corner-right .visible-wrapper {
      width: calc(
        var(--ui-components-icon-button-visual-target-size) +
          var(--ui-components-icon-button-padding-left)
      );
      border-top-left-radius: 0;
      border-bottom-left-radius: 0;
    }

.wrapper.corner-right.hide-divider .visible-wrapper {
      border-left: none;
    }

.wrapper.corner-left.corner-right .visible-wrapper {
      width: var(--ui-components-button-touch-target-size);
    }

.wrapper.wide .visible-wrapper {
    width: var(--ui-components-button-touch-target-size);
  }

.wrapper .icon {
    width: var(--ui-components-icon-button-icon-size);
    height: var(--ui-components-icon-button-icon-size);
  }

.wrapper .progress-spinner {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

.wrapper.has-label {
    padding: var(--ui-components-icon-button-padding-vertical) 0;
  }

.wrapper .label {
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-label-font-weight);
    font-size: var(--global-typography-ui-label-font-size);
    line-height: var(--global-typography-ui-label-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.wrapper.variant-normal {
  cursor: pointer;
}

.wrapper.variant-normal:focus {
  outline: none;
}

.wrapper.variant-normal .visible-wrapper {
  border-color: var(--normal-enabled-border-color);
  background-color: var(--normal-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--normal-enabled-border-color);
  --base-background-color: var(--normal-enabled-background-color);
}

.wrapper.variant-normal.activated .visible-wrapper {
  border-color: var(--normal-activated-border-color);
  background-color: var(--normal-activated-background-color);
  --base-border-color: var(--normal-activated-border-color);
  --base-background-color: var(--normal-activated-background-color);
}

@media (hover:hover) {

.wrapper.variant-normal:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--normal-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--normal-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.variant-normal:active .visible-wrapper {
  border-color: var(--normal-pressed-border-color);
  background-color: var(--normal-pressed-background-color);
}

.wrapper.variant-normal:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.variant-normal:disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.wrapper.variant-normal.disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.wrapper.variant-normal:disabled {
  cursor: not-allowed;
}

.wrapper.variant-normal.disabled {
  cursor: not-allowed;
}

.wrapper.variant-normal {
    color: var(--on-normal-neutral-color);
}

.wrapper.variant-normal.active-color {
      color: var(--on-normal-active-color);
    }

.wrapper.variant-normal.activated .visible-wrapper {
      border-color: var(--normal-pressed-border-color);
      background-color: var(--normal-pressed-background-color);
    }

.wrapper.variant-flat {
  cursor: pointer;
}

.wrapper.variant-flat:focus {
  outline: none;
}

.wrapper.variant-flat .visible-wrapper {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.wrapper.variant-flat.activated .visible-wrapper {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.wrapper.variant-flat:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.variant-flat:active .visible-wrapper {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.wrapper.variant-flat:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.variant-flat:disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.variant-flat.disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.variant-flat:disabled {
  cursor: not-allowed;
}

.wrapper.variant-flat.disabled {
  cursor: not-allowed;
}

.wrapper.variant-flat {
    color: var(--on-flat-neutral-color);
}

.wrapper.variant-flat.active-color {
      color: var(--on-flat-active-color);
    }

.wrapper.variant-raised {
  cursor: pointer;
}

.wrapper.variant-raised:focus {
  outline: none;
}

.wrapper.variant-raised .visible-wrapper {
  border-color: var(--raised-enabled-border-color);
  background-color: var(--raised-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--raised-enabled-border-color);
  --base-background-color: var(--raised-enabled-background-color);
}

.wrapper.variant-raised.activated .visible-wrapper {
  border-color: var(--raised-activated-border-color);
  background-color: var(--raised-activated-background-color);
  --base-border-color: var(--raised-activated-border-color);
  --base-background-color: var(--raised-activated-background-color);
}

@media (hover:hover) {

.wrapper.variant-raised:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--raised-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--raised-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.variant-raised:active .visible-wrapper {
  border-color: var(--raised-pressed-border-color);
  background-color: var(--raised-pressed-background-color);
}

.wrapper.variant-raised:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.variant-raised:disabled .visible-wrapper {
  border-color: var(--raised-disabled-border-color);
  background-color: var(--raised-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-raised-disabled-color) !important;
}

.wrapper.variant-raised.disabled .visible-wrapper {
  border-color: var(--raised-disabled-border-color);
  background-color: var(--raised-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-raised-disabled-color) !important;
}

.wrapper.variant-raised:disabled {
  cursor: not-allowed;
}

.wrapper.variant-raised.disabled {
  cursor: not-allowed;
}

.wrapper.variant-raised {
    color: var(--on-raised-active-color);
}

.wrapper.variant-raised.active-color {
      color: var(--on-raised-active-color);
    }

.wrapper.variant-integration {
  cursor: pointer;
}

.wrapper.variant-integration:focus {
  outline: none;
}

.wrapper.variant-integration .visible-wrapper {
  border-color: var(--integration-flat-enabled-border-color);
  background-color: var(--integration-flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--integration-flat-enabled-border-color);
  --base-background-color: var(--integration-flat-enabled-background-color);
}

.wrapper.variant-integration.activated .visible-wrapper {
  border-color: var(--integration-flat-activated-border-color);
  background-color: var(--integration-flat-activated-background-color);
  --base-border-color: var(--integration-flat-activated-border-color);
  --base-background-color: var(--integration-flat-activated-background-color);
}

@media (hover:hover) {

.wrapper.variant-integration:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--integration-flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--integration-flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.variant-integration:active .visible-wrapper {
  border-color: var(--integration-flat-pressed-border-color);
  background-color: var(--integration-flat-pressed-background-color);
}

.wrapper.variant-integration:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.variant-integration:disabled .visible-wrapper {
  border-color: var(--integration-flat-disabled-border-color);
  background-color: var(--integration-flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--integration-on-flat-disabled-color) !important;
}

.wrapper.variant-integration.disabled .visible-wrapper {
  border-color: var(--integration-flat-disabled-border-color);
  background-color: var(--integration-flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--integration-on-flat-disabled-color) !important;
}

.wrapper.variant-integration:disabled {
  cursor: not-allowed;
}

.wrapper.variant-integration.disabled {
  cursor: not-allowed;
}

.wrapper.variant-integration {
    color: var(--integration-on-normal-neutral-color);
}

.wrapper.variant-integration .visible-wrapper {
      border: 0;
    }
`;var A_=Object.defineProperty,P_=Object.getOwnPropertyDescriptor,No=(e,t,o,r)=>{for(var i=r>1?void 0:r?P_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&A_(t,o,i),i};var mo=class extends S{constructor(){super(...arguments),this.variant="normal",this.activated=!1,this.cornerLeft=!1,this.cornerRight=!1,this.activeColor=!1,this.wide=!1,this.disabled=!1,this.progress=void 0,this.hasLabel=!1,this.showDivider=!0,this.ariaLabel=null}get progressSpinner(){if(this.progress===void 0)return z;if(this.progress===100)return f`<div class="progress-spinner">
        <svg
          width="40"
          height="40"
          viewBox="0 0 40 40"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle
            cx="20"
            cy="20"
            r="18"
            stroke="#325B9A"
            stroke-width="4"
            fill="none"
          />
        </svg>
      </div>`;let e=Xl(this.progress*.95*3.6),t=20+18*Math.sin(e),o=20-18*Math.cos(e),r=e>Math.PI?1:0;return f`<div class="progress-spinner">
      <svg
        width="40"
        height="40"
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle
          cx="20"
          cy="20"
          r="18"
          stroke="var(--container-backdrop-color)"
          stroke-width="4"
          fill="none"
        />
        <path
          d="M18 2 A18 18 0 ${r} 1 ${t} ${o}"
          stroke="var(--instrument-enhanced-secondary-color)"
          stroke-width="4"
          stroke-linecap="round"
        />
      </svg>
    </div>`}render(){return f`
      <button
        class=${de({wrapper:!0,["variant-"+this.variant]:!0,activated:this.activated,"corner-left":this.cornerLeft,"corner-right":this.cornerRight,"active-color":this.activeColor,"has-label":this.hasLabel,wide:this.wide,progress:this.progress!==void 0,"hide-divider":!this.showDivider})}
        ?disabled=${this.disabled}
        aria-label=${Ce(this.ariaLabel??void 0)}
        part="wrapper"
      >
        ${this.progress!==void 0?this.progressSpinner:z}
        <div class="visible-wrapper" part="visible-wrapper">
          <div class="icon" part="icon">
            <slot></slot>
          </div>
        </div>
        ${this.hasLabel?f`<div class="label" part="label">
              <slot name="label"></slot>
            </div>`:z}
      </button>
    `}};mo.styles=ne(Tv);No([h({type:String})],mo.prototype,"variant",2);No([h({type:Boolean})],mo.prototype,"activated",2);No([h({type:Boolean})],mo.prototype,"cornerLeft",2);No([h({type:Boolean})],mo.prototype,"cornerRight",2);No([h({type:Boolean})],mo.prototype,"activeColor",2);No([h({type:Boolean})],mo.prototype,"wide",2);No([h({type:Boolean})],mo.prototype,"disabled",2);No([h({type:Number})],mo.prototype,"progress",2);No([h({type:Boolean})],mo.prototype,"hasLabel",2);No([h({type:Boolean,attribute:!1})],mo.prototype,"showDivider",2);No([h({type:String,attribute:"aria-label"})],mo.prototype,"ariaLabel",2);mo=No([L("obc-icon-button")],mo);var O_=Object.defineProperty,V_=Object.getOwnPropertyDescriptor,Dv=(e,t,o,r)=>{for(var i=r>1?void 0:r?V_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&O_(t,o,i),i},J1=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4.51477 2.10051L3.10056 3.51473L7.58576 7.99993H4.6C4.03995 7.99993 3.75992 7.99993 3.54601 8.10892C3.35785 8.20479 3.20487 8.35777 3.10899 8.54594C3 8.75985 3 9.03987 3 9.59993V14.3999C3 14.96 3 15.24 3.10899 15.4539C3.20487 15.6421 3.35785 15.7951 3.54601 15.8909C3.75992 15.9999 4.03995 15.9999 4.6 15.9999H11L16.6343 21.6342C17.0627 22.0626 17.2769 22.2768 17.4608 22.2913C17.6203 22.3038 17.7763 22.2393 17.8802 22.1175C18 21.9773 18 21.6744 18 21.0686V18.4142L20.4853 20.8995L21.8995 19.4853L4.51477 2.10051ZM5 9.99993H9.58576L16 16.4142V18.1715L11.8284 13.9999H5V9.99993Z" fill="currentColor"/>
<path d="M12.1213 6.8786L13.5355 8.29282L16 5.82835V10.7573L18 12.7573V2.9313C18 2.32548 18 2.02257 17.8802 1.88231C17.7763 1.76061 17.6203 1.69602 17.4608 1.70858C17.2769 1.72305 17.0627 1.93724 16.6343 2.36561L12.1213 6.8786Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4.51477 2.10051L3.10056 3.51473L7.58576 7.99993H4.6C4.03995 7.99993 3.75992 7.99993 3.54601 8.10892C3.35785 8.20479 3.20487 8.35777 3.10899 8.54594C3 8.75985 3 9.03987 3 9.59993V14.3999C3 14.96 3 15.24 3.10899 15.4539C3.20487 15.6421 3.35785 15.7951 3.54601 15.8909C3.75992 15.9999 4.03995 15.9999 4.6 15.9999H11L16.6343 21.6342C17.0627 22.0626 17.2769 22.2768 17.4608 22.2913C17.6203 22.3038 17.7763 22.2393 17.8802 22.1175C18 21.9773 18 21.6744 18 21.0686V18.4142L20.4853 20.8995L21.8995 19.4853L4.51477 2.10051ZM5 9.99993H9.58576L16 16.4142V18.1715L11.8284 13.9999H5V9.99993Z" style="fill: var(--element-active-color)"/>
<path d="M12.1213 6.8786L13.5355 8.29282L16 5.82835V10.7573L18 12.7573V2.9313C18 2.32548 18 2.02257 17.8802 1.88231C17.7763 1.76061 17.6203 1.69602 17.4608 1.70858C17.2769 1.72305 17.0627 1.93724 16.6343 2.36561L12.1213 6.8786Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};J1.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Dv([h({type:Boolean})],J1.prototype,"useCssColor",2);J1=Dv([L("obi-silence-iec")],J1);var T_=Object.defineProperty,D_=Object.getOwnPropertyDescriptor,Ev=(e,t,o,r)=>{for(var i=r>1?void 0:r?D_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&T_(t,o,i),i},ed=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M4 19V17H6V10C6 8.61667 6.41667 7.3875 7.25 6.3125C8.08333 5.2375 9.16667 4.53333 10.5 4.2V3.5C10.5 3.08333 10.6458 2.72917 10.9375 2.4375C11.2292 2.14583 11.5833 2 12 2C12.4167 2 12.7708 2.14583 13.0625 2.4375C13.3542 2.72917 13.5 3.08333 13.5 3.5V4.2C14.8333 4.53333 15.9167 5.2375 16.75 6.3125C17.5833 7.3875 18 8.61667 18 10V17H20V19H4ZM12 22C11.45 22 10.9792 21.8042 10.5875 21.4125C10.1958 21.0208 10 20.55 10 20H14C14 20.55 13.8042 21.0208 13.4125 21.4125C13.0208 21.8042 12.55 22 12 22ZM8 17H16V10C16 8.9 15.6083 7.95833 14.825 7.175C14.0417 6.39167 13.1 6 12 6C10.9 6 9.95833 6.39167 9.175 7.175C8.39167 7.95833 8 8.9 8 10V17Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M4 19V17H6V10C6 8.61667 6.41667 7.3875 7.25 6.3125C8.08333 5.2375 9.16667 4.53333 10.5 4.2V3.5C10.5 3.08333 10.6458 2.72917 10.9375 2.4375C11.2292 2.14583 11.5833 2 12 2C12.4167 2 12.7708 2.14583 13.0625 2.4375C13.3542 2.72917 13.5 3.08333 13.5 3.5V4.2C14.8333 4.53333 15.9167 5.2375 16.75 6.3125C17.5833 7.3875 18 8.61667 18 10V17H20V19H4ZM12 22C11.45 22 10.9792 21.8042 10.5875 21.4125C10.1958 21.0208 10 20.55 10 20H14C14 20.55 13.8042 21.0208 13.4125 21.4125C13.0208 21.8042 12.55 22 12 22ZM8 17H16V10C16 8.9 15.6083 7.95833 14.825 7.175C14.0417 6.39167 13.1 6 12 6C10.9 6 9.95833 6.39167 9.175 7.175C8.39167 7.95833 8 8.9 8 10V17Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ed.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Ev([h({type:Boolean})],ed.prototype,"useCssColor",2);ed=Ev([L("obi-alerts")],ed);var E_=Object.defineProperty,R_=Object.getOwnPropertyDescriptor,Rv=(e,t,o,r)=>{for(var i=r>1?void 0:r?R_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&E_(t,o,i),i},td=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 23C16.6167 23 15.4375 22.5125 14.4625 21.5375C13.4875 20.5625 13 19.3833 13 18C13 16.6167 13.4875 15.4375 14.4625 14.4625C15.4375 13.4875 16.6167 13 18 13C19.3833 13 20.5625 13.4875 21.5375 14.4625C22.5125 15.4375 23 16.6167 23 18C23 19.3833 22.5125 20.5625 21.5375 21.5375C20.5625 22.5125 19.3833 23 18 23ZM20.35 19.65L19.65 20.35L17.5 18.2V15H18.5V17.8L20.35 19.65Z" fill="currentColor"/>
<path d="M4 17V19H11.5764C11.5261 18.674 11.5 18.3401 11.5 18C11.5 17.6599 11.5261 17.326 11.5764 17H8V10C8 8.9 8.39167 7.95833 9.175 7.175C9.95833 6.39167 10.9 6 12 6C13.1 6 14.0417 6.39167 14.825 7.175C15.6083 7.95833 16 8.9 16 10V11.8135C16.6301 11.61 17.3022 11.5 18 11.5V10C18 8.61667 17.5833 7.3875 16.75 6.3125C15.9167 5.2375 14.8333 4.53333 13.5 4.2V3.5C13.5 3.08333 13.3542 2.72917 13.0625 2.4375C12.7708 2.14583 12.4167 2 12 2C11.5833 2 11.2292 2.14583 10.9375 2.4375C10.6458 2.72917 10.5 3.08333 10.5 3.5V4.2C9.16667 4.53333 8.08333 5.2375 7.25 6.3125C6.41667 7.3875 6 8.61667 6 10V17H4Z" fill="currentColor"/>
<path d="M11.8135 20C12.0307 20.6723 12.3545 21.2968 12.7649 21.8534C12.5297 21.9511 12.2747 22 12 22C11.45 22 10.9792 21.8042 10.5875 21.4125C10.1958 21.0208 10 20.55 10 20H11.8135Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18 23C16.6167 23 15.4375 22.5125 14.4625 21.5375C13.4875 20.5625 13 19.3833 13 18C13 16.6167 13.4875 15.4375 14.4625 14.4625C15.4375 13.4875 16.6167 13 18 13C19.3833 13 20.5625 13.4875 21.5375 14.4625C22.5125 15.4375 23 16.6167 23 18C23 19.3833 22.5125 20.5625 21.5375 21.5375C20.5625 22.5125 19.3833 23 18 23ZM20.35 19.65L19.65 20.35L17.5 18.2V15H18.5V17.8L20.35 19.65Z" style="fill: var(--element-active-color)"/>
<path d="M4 17V19H11.5764C11.5261 18.674 11.5 18.3401 11.5 18C11.5 17.6599 11.5261 17.326 11.5764 17H8V10C8 8.9 8.39167 7.95833 9.175 7.175C9.95833 6.39167 10.9 6 12 6C13.1 6 14.0417 6.39167 14.825 7.175C15.6083 7.95833 16 8.9 16 10V11.8135C16.6301 11.61 17.3022 11.5 18 11.5V10C18 8.61667 17.5833 7.3875 16.75 6.3125C15.9167 5.2375 14.8333 4.53333 13.5 4.2V3.5C13.5 3.08333 13.3542 2.72917 13.0625 2.4375C12.7708 2.14583 12.4167 2 12 2C11.5833 2 11.2292 2.14583 10.9375 2.4375C10.6458 2.72917 10.5 3.08333 10.5 3.5V4.2C9.16667 4.53333 8.08333 5.2375 7.25 6.3125C6.41667 7.3875 6 8.61667 6 10V17H4Z" style="fill: var(--element-active-color)"/>
<path d="M11.8135 20C12.0307 20.6723 12.3545 21.2968 12.7649 21.8534C12.5297 21.9511 12.2747 22 12 22C11.45 22 10.9792 21.8042 10.5875 21.4125C10.1958 21.0208 10 20.55 10 20H11.8135Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};td.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Rv([h({type:Boolean})],td.prototype,"useCssColor",2);td=Rv([L("obi-alerts-shelf")],td);var z_=Object.defineProperty,H_=Object.getOwnPropertyDescriptor,zv=(e,t,o,r)=>{for(var i=r>1?void 0:r?H_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&z_(t,o,i),i},od=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M4 19V17H6V10C6 8.61667 6.41667 7.3875 7.25 6.3125C8.08333 5.2375 9.16667 4.53333 10.5 4.2V3.5C10.5 3.08333 10.6458 2.72917 10.9375 2.4375C11.2292 2.14583 11.5833 2 12 2C12.4167 2 12.7708 2.14583 13.0625 2.4375C13.3542 2.72917 13.5 3.08333 13.5 3.5V4.2C14.8333 4.53333 15.9167 5.2375 16.75 6.3125C17.5833 7.3875 18 8.61667 18 10V17H20V19H4ZM12 22C11.45 22 10.9792 21.8042 10.5875 21.4125C10.1958 21.0208 10 20.55 10 20H14C14 20.55 13.8042 21.0208 13.4125 21.4125C13.0208 21.8042 12.55 22 12 22Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M4 19V17H6V10C6 8.61667 6.41667 7.3875 7.25 6.3125C8.08333 5.2375 9.16667 4.53333 10.5 4.2V3.5C10.5 3.08333 10.6458 2.72917 10.9375 2.4375C11.2292 2.14583 11.5833 2 12 2C12.4167 2 12.7708 2.14583 13.0625 2.4375C13.3542 2.72917 13.5 3.08333 13.5 3.5V4.2C14.8333 4.53333 15.9167 5.2375 16.75 6.3125C17.5833 7.3875 18 8.61667 18 10V17H20V19H4ZM12 22C11.45 22 10.9792 21.8042 10.5875 21.4125C10.1958 21.0208 10 20.55 10 20H14C14 20.55 13.8042 21.0208 13.4125 21.4125C13.0208 21.8042 12.55 22 12 22Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};od.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;zv([h({type:Boolean})],od.prototype,"useCssColor",2);od=zv([L("obi-alerts-active")],od);var B_=Object.defineProperty,I_=Object.getOwnPropertyDescriptor,Hv=(e,t,o,r)=>{for(var i=r>1?void 0:r?I_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&B_(t,o,i),i},rd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M1.11648 20.5339L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5339Z" fill="currentColor"/>
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" stroke="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.2071 12.7071L10 19.9142L5.79291 15.7071L7.20712 14.2928L10 17.0857L15.7929 11.2928L17.2071 12.7071Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M1.11648 20.5339L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5339Z" style="fill: var(--alert-alarm-color)"/>
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" style="stroke: var(--alert-alarm-outline-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.2071 12.7071L10 19.9142L5.79291 15.7071L7.20712 14.2928L10 17.0857L15.7929 11.2928L17.2071 12.7071Z" style="fill: var(--on-alarm-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};rd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Hv([h({type:Boolean})],rd.prototype,"useCssColor",2);rd=Hv([L("obi-alarm-rectified-iec")],rd);var Z_=Object.defineProperty,F_=Object.getOwnPropertyDescriptor,Bv=(e,t,o,r)=>{for(var i=r>1?void 0:r?F_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Z_(t,o,i),i},id=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4.60003 7.99993C4.03998 7.99993 3.75995 7.99993 3.54604 8.10892C3.35788 8.20479 3.2049 8.35778 3.10902 8.54594C3.00003 8.75985 3.00003 9.03988 3.00003 9.59993V14.3999C3.00003 14.96 3.00003 15.24 3.10902 15.4539C3.2049 15.6421 3.35788 15.7951 3.54604 15.8909C3.75995 15.9999 4.03998 15.9999 4.60003 15.9999H11L16.6343 21.6342C17.0627 22.0626 17.2769 22.2768 17.4608 22.2913C17.6204 22.3038 17.7763 22.2393 17.8802 22.1175C18 21.9773 18 21.6744 18 21.0686V2.9313C18 2.32548 18 2.02257 17.8802 1.88231C17.7763 1.76061 17.6204 1.69602 17.4608 1.70858C17.2769 1.72305 17.0627 1.93724 16.6343 2.36561L11 7.99993H4.60003ZM16 18.1715L11.8285 13.9999H5.00003V9.99993H11.8285L16 5.82835V18.1715Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4.60003 7.99993C4.03998 7.99993 3.75995 7.99993 3.54604 8.10892C3.35788 8.20479 3.2049 8.35778 3.10902 8.54594C3.00003 8.75985 3.00003 9.03988 3.00003 9.59993V14.3999C3.00003 14.96 3.00003 15.24 3.10902 15.4539C3.2049 15.6421 3.35788 15.7951 3.54604 15.8909C3.75995 15.9999 4.03998 15.9999 4.60003 15.9999H11L16.6343 21.6342C17.0627 22.0626 17.2769 22.2768 17.4608 22.2913C17.6204 22.3038 17.7763 22.2393 17.8802 22.1175C18 21.9773 18 21.6744 18 21.0686V2.9313C18 2.32548 18 2.02257 17.8802 1.88231C17.7763 1.76061 17.6204 1.69602 17.4608 1.70858C17.2769 1.72305 17.0627 1.93724 16.6343 2.36561L11 7.99993H4.60003ZM16 18.1715L11.8285 13.9999H5.00003V9.99993H11.8285L16 5.82835V18.1715Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};id.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Bv([h({type:Boolean})],id.prototype,"useCssColor",2);id=Bv([L("obi-unacknowledged")],id);var N_=Object.defineProperty,j_=Object.getOwnPropertyDescriptor,Iv=(e,t,o,r)=>{for(var i=r>1?void 0:r?j_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&N_(t,o,i),i},sd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<mask id="path-1-inside-1_2002_1087" fill="currentColor">
<path d="M1.11648 20.5339L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5339Z"/>
</mask>
<path d="M1.11648 20.5339L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5339Z" fill="currentColor"/>
<path d="M11.1158 1.53427L12.0007 2V2L11.1158 1.53427ZM1.11648 20.5339L2.00141 20.9996V20.9996L1.11648 20.5339ZM2.00128 22V23H2.00128L2.00128 22ZM21.9987 22V21H21.9987L21.9987 22ZM22.8835 20.5339L21.9986 20.9996H21.9986L22.8835 20.5339ZM12.8854 1.53432L13.7704 1.06863V1.06863L12.8854 1.53432ZM21.9987 22V23C23.5042 23 24.4692 21.3997 23.7685 20.0682L22.8835 20.5339L21.9986 20.9996L21.9987 21V22ZM1.11648 20.5339L0.231556 20.0681C-0.469216 21.3996 0.495789 23 2.00128 23V22V21L2.00141 20.9996L1.11648 20.5339ZM11.1158 1.53427L12.0007 2L12.0005 2L12.8854 1.53432L13.7704 1.06863C13.0206 -0.356171 10.9807 -0.356221 10.2309 1.06855L11.1158 1.53427ZM11.1158 1.53427L10.2309 1.06855L0.231556 20.0681L1.11648 20.5339L2.00141 20.9996L12.0007 2L11.1158 1.53427ZM21.9987 22L21.9987 21L2.00128 21L2.00128 22L2.00128 23L21.9987 23L21.9987 22ZM12.8854 1.53432L12.0005 2L21.9986 20.9996L22.8835 20.5339L23.7685 20.0682L13.7704 1.06863L12.8854 1.53432Z" fill="currentColor" mask="url(#path-1-inside-1_2002_1087)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.6718 15.0001L6.52379 10.2595L7.5219 8.36304L12.0006 13.4815L16.479 8.36338L17.477 10.26L13.3294 15.0001L19.4543 22.0001L16.7968 22.0001L12.0006 16.5187L7.20441 22.0001L4.54688 22.0001L10.6718 15.0001Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<mask id="path-1-inside-1_2002_1087" style="fill: var(--on-alarm-color)">
<path d="M1.11648 20.5339L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5339Z"/>
</mask>
<path d="M1.11648 20.5339L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5339Z" style="fill: var(--alert-alarm-color)"/>
<path d="M11.1158 1.53427L12.0007 2V2L11.1158 1.53427ZM1.11648 20.5339L2.00141 20.9996V20.9996L1.11648 20.5339ZM2.00128 22V23H2.00128L2.00128 22ZM21.9987 22V21H21.9987L21.9987 22ZM22.8835 20.5339L21.9986 20.9996H21.9986L22.8835 20.5339ZM12.8854 1.53432L13.7704 1.06863V1.06863L12.8854 1.53432ZM21.9987 22V23C23.5042 23 24.4692 21.3997 23.7685 20.0682L22.8835 20.5339L21.9986 20.9996L21.9987 21V22ZM1.11648 20.5339L0.231556 20.0681C-0.469216 21.3996 0.495789 23 2.00128 23V22V21L2.00141 20.9996L1.11648 20.5339ZM11.1158 1.53427L12.0007 2L12.0005 2L12.8854 1.53432L13.7704 1.06863C13.0206 -0.356171 10.9807 -0.356221 10.2309 1.06855L11.1158 1.53427ZM11.1158 1.53427L10.2309 1.06855L0.231556 20.0681L1.11648 20.5339L2.00141 20.9996L12.0007 2L11.1158 1.53427ZM21.9987 22L21.9987 21L2.00128 21L2.00128 22L2.00128 23L21.9987 23L21.9987 22ZM12.8854 1.53432L12.0005 2L21.9986 20.9996L22.8835 20.5339L23.7685 20.0682L13.7704 1.06863L12.8854 1.53432Z" style="fill: var(--alert-alarm-outline-color)" mask="url(#path-1-inside-1_2002_1087)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M10.6718 15.0001L6.52379 10.2595L7.5219 8.36304L12.0006 13.4815L16.479 8.36338L17.477 10.26L13.3294 15.0001L19.4543 22.0001L16.7968 22.0001L12.0006 16.5187L7.20441 22.0001L4.54688 22.0001L10.6718 15.0001Z" style="fill: var(--on-alarm-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};sd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Iv([h({type:Boolean})],sd.prototype,"useCssColor",2);sd=Iv([L("obi-alarm-noack-iec")],sd);var W_=Object.defineProperty,U_=Object.getOwnPropertyDescriptor,Zv=(e,t,o,r)=>{for(var i=r>1?void 0:r?U_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&W_(t,o,i),i},nd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" fill="currentColor" stroke="currentColor"/>
<path d="M19.743 5.67138L13.4143 12.0001L19.7429 18.3288C19.3198 18.8459 18.8458 19.3198 18.3287 19.743L12.0001 13.4143L5.67135 19.743C5.15423 19.3199 4.68029 18.8459 4.25712 18.3288L10.5859 12.0001L4.25705 5.67129C4.68021 5.15419 5.15416 4.68024 5.67126 4.25708L12.0001 10.5859L18.3288 4.25715C18.8459 4.68032 19.3199 5.15426 19.743 5.67138Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" style="fill: var(--alert-warning-color); stroke: var(--alert-warning-outline-color)"/>
<path d="M19.743 5.67138L13.4143 12.0001L19.7429 18.3288C19.3198 18.8459 18.8458 19.3198 18.3287 19.743L12.0001 13.4143L5.67135 19.743C5.15423 19.3199 4.68029 18.8459 4.25712 18.3288L10.5859 12.0001L4.25705 5.67129C4.68021 5.15419 5.15416 4.68024 5.67126 4.25708L12.0001 10.5859L18.3288 4.25715C18.8459 4.68032 19.3199 5.15426 19.743 5.67138Z" style="fill: var(--on-warning-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};nd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Zv([h({type:Boolean})],nd.prototype,"useCssColor",2);nd=Zv([L("obi-warning-noack-iec")],nd);var G_=Object.defineProperty,Y_=Object.getOwnPropertyDescriptor,Fv=(e,t,o,r)=>{for(var i=r>1?void 0:r?Y_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&G_(t,o,i),i},ad=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.9947 5.05318L4.19618 19.0333H19.7886L11.9947 5.05318ZM2.11772 18.6539L10.5975 3.45245C11.0541 2.63399 11.2824 2.22476 11.5829 2.08884C11.845 1.97035 12.1453 1.97039 12.4073 2.08895C12.7078 2.22495 12.936 2.63423 13.3923 3.45281L21.8671 18.6542C22.3033 19.4367 22.5215 19.828 22.4844 20.1483C22.452 20.4277 22.3035 20.6806 22.0752 20.845C21.8134 21.0333 21.3655 21.0333 20.4696 21.0333H3.51502C2.61888 21.0333 2.17081 21.0333 1.90908 20.8449C1.68073 20.6806 1.53219 20.4276 1.49989 20.1481C1.46287 19.8278 1.68115 19.4365 2.11772 18.6539Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M11.9947 5.05318L4.19618 19.0333H19.7886L11.9947 5.05318ZM2.11772 18.6539L10.5975 3.45245C11.0541 2.63399 11.2824 2.22476 11.5829 2.08884C11.845 1.97035 12.1453 1.97039 12.4073 2.08895C12.7078 2.22495 12.936 2.63423 13.3923 3.45281L21.8671 18.6542C22.3033 19.4367 22.5215 19.828 22.4844 20.1483C22.452 20.4277 22.3035 20.6806 22.0752 20.845C21.8134 21.0333 21.3655 21.0333 20.4696 21.0333H3.51502C2.61888 21.0333 2.17081 21.0333 1.90908 20.8449C1.68073 20.6806 1.53219 20.4276 1.49989 20.1481C1.46287 19.8278 1.68115 19.4365 2.11772 18.6539Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ad.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Fv([h({type:Boolean})],ad.prototype,"useCssColor",2);ad=Fv([L("obi-alarm-badge-outline")],ad);var q_=Object.defineProperty,X_=Object.getOwnPropertyDescriptor,Nv=(e,t,o,r)=>{for(var i=r>1?void 0:r?X_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&q_(t,o,i),i},ld=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ld.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Nv([h({type:Boolean})],ld.prototype,"useCssColor",2);ld=Nv([L("obi-warning-badge-outline")],ld);var K_=Object.defineProperty,Q_=Object.getOwnPropertyDescriptor,jv=(e,t,o,r)=>{for(var i=r>1?void 0:r?Q_(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&K_(t,o,i),i},cd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5 5V19H19V5H5ZM3.10899 3.54601C3 3.75992 3 4.03995 3 4.6V19.4C3 19.9601 3 20.2401 3.10899 20.454C3.20487 20.6422 3.35785 20.7951 3.54601 20.891C3.75992 21 4.03995 21 4.6 21H19.4C19.9601 21 20.2401 21 20.454 20.891C20.6422 20.7951 20.7951 20.6422 20.891 20.454C21 20.2401 21 19.9601 21 19.4V4.6C21 4.03995 21 3.75992 20.891 3.54601C20.7951 3.35785 20.6422 3.20487 20.454 3.10899C20.2401 3 19.9601 3 19.4 3H4.6C4.03995 3 3.75992 3 3.54601 3.10899C3.35785 3.20487 3.20487 3.35785 3.10899 3.54601Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M5 5V19H19V5H5ZM3.10899 3.54601C3 3.75992 3 4.03995 3 4.6V19.4C3 19.9601 3 20.2401 3.10899 20.454C3.20487 20.6422 3.35785 20.7951 3.54601 20.891C3.75992 21 4.03995 21 4.6 21H19.4C19.9601 21 20.2401 21 20.454 20.891C20.6422 20.7951 20.7951 20.6422 20.891 20.454C21 20.2401 21 19.9601 21 19.4V4.6C21 4.03995 21 3.75992 20.891 3.54601C20.7951 3.35785 20.6422 3.20487 20.454 3.10899C20.2401 3 19.9601 3 19.4 3H4.6C4.03995 3 3.75992 3 3.54601 3.10899C3.35785 3.20487 3.20487 3.35785 3.10899 3.54601Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};cd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;jv([h({type:Boolean})],cd.prototype,"useCssColor",2);cd=jv([L("obi-caution-badge-outline")],cd);var J_=Object.defineProperty,ek=Object.getOwnPropertyDescriptor,Wv=(e,t,o,r)=>{for(var i=r>1?void 0:r?ek(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&J_(t,o,i),i},dd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M1.11648 20.5338L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5338Z" fill="currentColor"/>
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" stroke="currentColor"/>
<path d="M11 15V7H13V15H11Z" fill="currentColor"/>
<path d="M13 17H11V19H13V17Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M1.11648 20.5338L11.1158 1.53427C11.4907 0.821889 12.5105 0.821913 12.8854 1.53432L22.8835 20.5339C23.234 21.1999 22.7512 22 21.9987 22L2.00128 22C1.24879 22 0.765943 21.1999 1.11648 20.5338Z" style="fill: var(--alert-alarm-color)"/>
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" style="stroke: var(--alert-alarm-outline-color)"/>
<path d="M11 15V7H13V15H11Z" style="fill: var(--on-alarm-color)"/>
<path d="M13 17H11V19H13V17Z" style="fill: var(--on-alarm-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};dd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Wv([h({type:Boolean})],dd.prototype,"useCssColor",2);dd=Wv([L("obi-alarm-acknowledged-iec")],dd);var tk=Object.defineProperty,ok=Object.getOwnPropertyDescriptor,Uv=(e,t,o,r)=>{for(var i=r>1?void 0:r?ok(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&tk(t,o,i),i},hd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" fill="currentColor"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" stroke="currentColor"/>
<path d="M13 13V7H11V13H13Z" fill="currentColor"/>
<path d="M13 17V15H11V17H13Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" style="fill: var(--alert-warning-color)"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" style="stroke: var(--alert-warning-outline-color)"/>
<path d="M13 13V7H11V13H13Z" style="fill: var(--on-warning-active-color)"/>
<path d="M13 17V15H11V17H13Z" style="fill: var(--on-warning-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};hd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Uv([h({type:Boolean})],hd.prototype,"useCssColor",2);hd=Uv([L("obi-warning-acknowledged-iec")],hd);var rk=Object.defineProperty,ik=Object.getOwnPropertyDescriptor,Gv=(e,t,o,r)=>{for(var i=r>1?void 0:r?ik(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&rk(t,o,i),i},pd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" fill="currentColor"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" stroke="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" style="fill: var(--alert-warning-color)"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" style="stroke: var(--alert-warning-outline-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" style="fill: var(--on-warning-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};pd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Gv([h({type:Boolean})],pd.prototype,"useCssColor",2);pd=Gv([L("obi-warning-rectified-iec")],pd);var sk=Object.defineProperty,nk=Object.getOwnPropertyDescriptor,Yv=(e,t,o,r)=>{for(var i=r>1?void 0:r?nk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&sk(t,o,i),i},ud=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12.0006 2.00026L2.00141 20.9996L21.9987 21L12.0006 2.00026ZM11.1158 1.53427L1.11648 20.5338C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.2071 12.7071L10 19.9142L5.79291 15.7071L7.20712 14.2928L10 17.0857L15.7929 11.2928L17.2071 12.7071Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12.0006 2.00026L2.00141 20.9996L21.9987 21L12.0006 2.00026ZM11.1158 1.53427L1.11648 20.5338C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M17.2071 12.7071L10 19.9142L5.79291 15.7071L7.20712 14.2928L10 17.0857L15.7929 11.2928L17.2071 12.7071Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};ud.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Yv([h({type:Boolean})],ud.prototype,"useCssColor",2);ud=Yv([L("obi-alarm-rectified-outlined")],ud);var ak=Object.defineProperty,lk=Object.getOwnPropertyDescriptor,qv=(e,t,o,r)=>{for(var i=r>1?void 0:r?lk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&ak(t,o,i),i},fd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="currentColor"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" style="fill: var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};fd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;qv([h({type:Boolean})],fd.prototype,"useCssColor",2);fd=qv([L("obi-warning-rectified-outlined")],fd);var ck=Object.defineProperty,dk=Object.getOwnPropertyDescriptor,Xv=(e,t,o,r)=>{for(var i=r>1?void 0:r?dk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&ck(t,o,i),i},gd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" fill="currentColor" stroke="currentColor"/>
<path d="M9.40418 9.40624L8.34559 10.4648L10.3807 12.4999H8.3C8.01997 12.4999 7.87996 12.4999 7.773 12.5544C7.67892 12.6024 7.60243 12.6789 7.5545 12.7729C7.5 12.8799 7.5 13.0199 7.5 13.2999V15.6999C7.5 15.98 7.5 16.12 7.5545 16.2269C7.60243 16.321 7.67892 16.3975 7.773 16.4454C7.87996 16.4999 8.01997 16.4999 8.3 16.4999H10.6686C10.7909 16.4999 10.8521 16.4999 10.9096 16.5137C10.9606 16.526 11.0094 16.5462 11.0541 16.5736C11.1046 16.6045 11.1478 16.6478 11.2343 16.7342L13.6343 19.1342C14.0627 19.5626 14.2769 19.7768 14.4608 19.7913C14.6203 19.8038 14.7763 19.7393 14.8802 19.6175C15 19.4773 15 19.1744 15 18.5686V17.1192L17.538 19.6572L18.5966 18.5986L9.40418 9.40624Z" fill="currentColor"/>
<path d="M15 12.8807V10.4313C15 9.82548 15 9.52257 14.8802 9.38231C14.7763 9.26061 14.6203 9.19602 14.4608 9.20858C14.2769 9.22305 14.0627 9.43724 13.6343 9.86561L12.8096 10.6903L15 12.8807Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M11.5586 1.76758C11.7461 1.41138 12.2559 1.41137 12.4434 1.76758L22.4414 20.7666C22.6167 21.0998 22.3748 21.4998 21.999 21.5H2.00098C1.62518 21.4998 1.38327 21.0998 1.55859 20.7666L11.5586 1.76758Z" style="fill: var(--alert-alarm-color); stroke: var(--alert-alarm-outline-color)"/>
<path d="M9.40418 9.40624L8.34559 10.4648L10.3807 12.4999H8.3C8.01997 12.4999 7.87996 12.4999 7.773 12.5544C7.67892 12.6024 7.60243 12.6789 7.5545 12.7729C7.5 12.8799 7.5 13.0199 7.5 13.2999V15.6999C7.5 15.98 7.5 16.12 7.5545 16.2269C7.60243 16.321 7.67892 16.3975 7.773 16.4454C7.87996 16.4999 8.01997 16.4999 8.3 16.4999H10.6686C10.7909 16.4999 10.8521 16.4999 10.9096 16.5137C10.9606 16.526 11.0094 16.5462 11.0541 16.5736C11.1046 16.6045 11.1478 16.6478 11.2343 16.7342L13.6343 19.1342C14.0627 19.5626 14.2769 19.7768 14.4608 19.7913C14.6203 19.8038 14.7763 19.7393 14.8802 19.6175C15 19.4773 15 19.1744 15 18.5686V17.1192L17.538 19.6572L18.5966 18.5986L9.40418 9.40624Z" style="fill: var(--on-alarm-active-color)"/>
<path d="M15 12.8807V10.4313C15 9.82548 15 9.52257 14.8802 9.38231C14.7763 9.26061 14.6203 9.19602 14.4608 9.20858C14.2769 9.22305 14.0627 9.43724 13.6343 9.86561L12.8096 10.6903L15 12.8807Z" style="fill: var(--on-alarm-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};gd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Xv([h({type:Boolean})],gd.prototype,"useCssColor",2);gd=Xv([L("obi-alarm-silenced-iec")],gd);var hk=Object.defineProperty,pk=Object.getOwnPropertyDescriptor,Kv=(e,t,o,r)=>{for(var i=r>1?void 0:r?pk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&hk(t,o,i),i},md=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M21.9986 20.9996L12.0006 2.00026L2.00141 20.9996L21.9986 20.9996ZM11.1158 1.53427L1.11648 20.5339C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" fill="currentColor"/>
<path d="M9.40418 9.40624L8.34559 10.4648L10.3807 12.4999H8.3C8.01997 12.4999 7.87996 12.4999 7.773 12.5544C7.67892 12.6024 7.60243 12.6789 7.5545 12.7729C7.5 12.8799 7.5 13.0199 7.5 13.2999V15.6999C7.5 15.98 7.5 16.12 7.5545 16.2269C7.60243 16.321 7.67892 16.3975 7.773 16.4454C7.87996 16.4999 8.01997 16.4999 8.3 16.4999H10.6686C10.7909 16.4999 10.8521 16.4999 10.9096 16.5137C10.9606 16.526 11.0094 16.5462 11.0541 16.5736C11.1046 16.6045 11.1478 16.6478 11.2343 16.7342L13.6343 19.1342C14.0627 19.5626 14.2769 19.7768 14.4608 19.7913C14.6203 19.8038 14.7763 19.7393 14.8802 19.6175C15 19.4773 15 19.1744 15 18.5686V17.1192L17.538 19.6572L18.5966 18.5986L9.40418 9.40624Z" fill="currentColor"/>
<path d="M15 12.8807V10.4313C15 9.82548 15 9.52257 14.8802 9.38231C14.7763 9.2606 14.6203 9.19602 14.4608 9.20858C14.2769 9.22305 14.0627 9.43724 13.6343 9.86561L12.8096 10.6903L15 12.8807Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M21.9986 20.9996L12.0006 2.00026L2.00141 20.9996L21.9986 20.9996ZM11.1158 1.53427L1.11648 20.5339C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" style="fill: var(--element-active-color)"/>
<path d="M9.40418 9.40624L8.34559 10.4648L10.3807 12.4999H8.3C8.01997 12.4999 7.87996 12.4999 7.773 12.5544C7.67892 12.6024 7.60243 12.6789 7.5545 12.7729C7.5 12.8799 7.5 13.0199 7.5 13.2999V15.6999C7.5 15.98 7.5 16.12 7.5545 16.2269C7.60243 16.321 7.67892 16.3975 7.773 16.4454C7.87996 16.4999 8.01997 16.4999 8.3 16.4999H10.6686C10.7909 16.4999 10.8521 16.4999 10.9096 16.5137C10.9606 16.526 11.0094 16.5462 11.0541 16.5736C11.1046 16.6045 11.1478 16.6478 11.2343 16.7342L13.6343 19.1342C14.0627 19.5626 14.2769 19.7768 14.4608 19.7913C14.6203 19.8038 14.7763 19.7393 14.8802 19.6175C15 19.4773 15 19.1744 15 18.5686V17.1192L17.538 19.6572L18.5966 18.5986L9.40418 9.40624Z" style="fill: var(--element-active-color)"/>
<path d="M15 12.8807V10.4313C15 9.82548 15 9.52257 14.8802 9.38231C14.7763 9.2606 14.6203 9.19602 14.4608 9.20858C14.2769 9.22305 14.0627 9.43724 13.6343 9.86561L12.8096 10.6903L15 12.8807Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};md.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Kv([h({type:Boolean})],md.prototype,"useCssColor",2);md=Kv([L("obi-alarm-silenced-outlined")],md);var uk=Object.defineProperty,fk=Object.getOwnPropertyDescriptor,Qv=(e,t,o,r)=>{for(var i=r>1?void 0:r?fk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&uk(t,o,i),i},vd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" fill="currentColor"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" stroke="currentColor"/>
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" fill="currentColor"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" style="fill: var(--alert-warning-color)"/>
<path d="M12 2.5C17.2467 2.5 21.5 6.75329 21.5 12C21.5 17.2467 17.2467 21.5 12 21.5C6.75329 21.5 2.5 17.2467 2.5 12C2.5 6.75329 6.75329 2.5 12 2.5Z" style="stroke: var(--alert-warning-outline-color)"/>
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" style="fill: var(--on-warning-active-color)"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" style="fill: var(--on-warning-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};vd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Qv([h({type:Boolean})],vd.prototype,"useCssColor",2);vd=Qv([L("obi-warning-silenced-iec")],vd);var gk=Object.defineProperty,mk=Object.getOwnPropertyDescriptor,Jv=(e,t,o,r)=>{for(var i=r>1?void 0:r?mk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&gk(t,o,i),i},bd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="currentColor"/>
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" fill="currentColor"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M12 21C16.9706 21 21 16.9706 21 12C21 7.02944 16.9706 3 12 3C7.02944 3 3 7.02944 3 12C3 16.9706 7.02944 21 12 21ZM12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" style="fill: var(--element-active-color)"/>
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" style="fill: var(--element-active-color)"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};bd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;Jv([h({type:Boolean})],bd.prototype,"useCssColor",2);bd=Jv([L("obi-warning-silenced-outlined")],bd);var vk=Object.defineProperty,bk=Object.getOwnPropertyDescriptor,eb=(e,t,o,r)=>{for(var i=r>1?void 0:r?bk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&vk(t,o,i),i},wd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M21.9986 20.9996L12.0006 2.00026L2.00141 20.9996L21.9986 20.9996ZM11.1158 1.53427L1.11648 20.5339C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" fill="currentColor"/>
<path d="M7.5 15.7V13.3C7.5 13.02 7.5 12.88 7.5545 12.7731C7.60243 12.679 7.67892 12.6025 7.773 12.5545C7.87996 12.5 8.01997 12.5 8.3 12.5H11L13.6343 9.86574C14.0627 9.43736 14.2769 9.22317 14.4608 9.2087C14.6203 9.19614 14.7763 9.26073 14.8802 9.38243C15 9.5227 15 9.8256 15 10.4314V18.5687C15 19.1745 15 19.4774 14.8802 19.6177C14.7763 19.7394 14.6203 19.804 14.4608 19.7914C14.2769 19.7769 14.0627 19.5627 13.6343 19.1344L11 16.5H8.3C8.01997 16.5 7.87996 16.5 7.773 16.4456C7.67892 16.3976 7.60243 16.3211 7.5545 16.227C7.5 16.1201 7.5 15.9801 7.5 15.7Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M21.9986 20.9996L12.0006 2.00026L2.00141 20.9996L21.9986 20.9996ZM11.1158 1.53427L1.11648 20.5339C0.765943 21.1999 1.24879 22 2.00128 22L21.9987 22C22.7512 22 23.234 21.1999 22.8835 20.5339L12.8854 1.53432C12.5105 0.821913 11.4907 0.821889 11.1158 1.53427Z" style="fill: var(--element-active-color)"/>
<path d="M7.5 15.7V13.3C7.5 13.02 7.5 12.88 7.5545 12.7731C7.60243 12.679 7.67892 12.6025 7.773 12.5545C7.87996 12.5 8.01997 12.5 8.3 12.5H11L13.6343 9.86574C14.0627 9.43736 14.2769 9.22317 14.4608 9.2087C14.6203 9.19614 14.7763 9.26073 14.8802 9.38243C15 9.5227 15 9.8256 15 10.4314V18.5687C15 19.1745 15 19.4774 14.8802 19.6177C14.7763 19.7394 14.6203 19.804 14.4608 19.7914C14.2769 19.7769 14.0627 19.5627 13.6343 19.1344L11 16.5H8.3C8.01997 16.5 7.87996 16.5 7.773 16.4456C7.67892 16.3976 7.60243 16.3211 7.5545 16.227C7.5 16.1201 7.5 15.9801 7.5 15.7Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};wd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;eb([h({type:Boolean})],wd.prototype,"useCssColor",2);wd=eb([L("obi-alarm-acknowledged-outlined")],wd);var tb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12 
           L 17,20.66 
           L 7,20.66 
           L 2,12 
           L 7,3.34 
           L 17,3.34 
           Z" 
        fill="var(--alert-critical-color)" stroke="var(--alert-critical-outline-color)" />
</svg>`,ob=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12 
           L 17,20.66 
           L 7,20.66 
           L 2,12 
           L 7,3.34 
           L 17,3.34 
           Z" 
        fill="none" stroke="var(--element-active-color)" />
</svg>`;var rb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12
           L 17,20.66
           L 7,20.66
           L 2,12
           L 7,3.34
           L 17,3.34
           Z"
        fill="var(--alert-critical-color)" stroke="var(--alert-critical-outline-color)" />
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H10.6686C10.7909 9.99993 10.8521 9.99993 10.9096 9.98611C10.9606 9.97386 11.0094 9.95366 11.0541 9.92625C11.1046 9.89533 11.1478 9.85209 11.2343 9.76561L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.76061 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11.2343 14.2342C11.1478 14.1478 11.1046 14.1045 11.0541 14.0736C11.0094 14.0462 10.9606 14.026 10.9096 14.0137C10.8521 13.9999 10.7909 13.9999 10.6686 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" fill="var(--on-critical-active-color)"/>
</svg>`,ib=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12
           L 17,20.66
           L 7,20.66
           L 2,12
           L 7,3.34
           L 17,3.34
           Z"
        fill="none" stroke="var(--element-active-color)" />
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H10.6686C10.7909 9.99993 10.8521 9.99993 10.9096 9.98611C10.9606 9.97386 11.0094 9.95366 11.0541 9.92625C11.1046 9.89533 11.1478 9.85209 11.2343 9.76561L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.76061 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11.2343 14.2342C11.1478 14.1478 11.1046 14.1045 11.0541 14.0736C11.0094 14.0462 10.9606 14.026 10.9096 14.0137C10.8521 13.9999 10.7909 13.9999 10.6686 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" fill="var(--element-active-color)"/>
</svg>`;var sb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12
           L 17,20.66
           L 7,20.66
           L 2,12
           L 7,3.34
           L 17,3.34
           Z"
        fill="var(--alert-critical-color)" stroke="var(--alert-critical-outline-color)" />
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" fill="var(--on-critical-active-color)"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" fill="var(--on-critical-active-color)"/>
</svg>`,nb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12
           L 17,20.66
           L 7,20.66
           L 2,12
           L 7,3.34
           L 17,3.34
           Z"
        fill="none" stroke="var(--element-active-color)" />
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" fill="var(--element-active-color)"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" fill="var(--element-active-color)"/>
</svg>`;var ab=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12
           L 17,20.66
           L 7,20.66
           L 2,12
           L 7,3.34
           L 17,3.34
           Z"
        fill="var(--alert-critical-color)" stroke="var(--alert-critical-outline-color)" />
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" fill="var(--on-critical-active-color)"/>
</svg>`,uu=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12
           L 17,20.66
           L 7,20.66
           L 2,12
           L 7,3.34
           L 17,3.34
           Z"
        fill="none" stroke="var(--element-active-color)" />
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" fill="var(--element-active-color)"/>
</svg>`;var lb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M 22,12
           L 17,20.66
           L 7,20.66
           L 2,12
           L 7,3.34
           L 17,3.34
           Z"
        fill="var(--alert-critical-color)" stroke="var(--alert-critical-outline-color)" />
<path d="M13 13V7H11V13H13Z" fill="var(--on-critical-active-color)"/>
<path d="M13 17V15H11V17H13Z" fill="var(--on-critical-active-color)"/>
</svg>`;var cb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="var(--alert-caution-color)"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="var(--alert-caution-outline-color)"/>
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H10.6686C10.7909 9.99993 10.8521 9.99993 10.9096 9.98611C10.9606 9.97386 11.0094 9.95366 11.0541 9.92625C11.1046 9.89533 11.1478 9.85209 11.2343 9.76561L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.76061 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11.2343 14.2342C11.1478 14.1478 11.1046 14.1045 11.0541 14.0736C11.0094 14.0462 10.9606 14.026 10.9096 14.0137C10.8521 13.9999 10.7909 13.9999 10.6686 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" fill="var(--on-caution-active-color)"/>
</svg>`,db=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="none"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="var(--element-active-color)"/>
<path d="M7.5 13.1999V10.7999C7.5 10.5199 7.5 10.3799 7.5545 10.2729C7.60243 10.1789 7.67892 10.1024 7.773 10.0544C7.87996 9.99993 8.01997 9.99993 8.3 9.99993H10.6686C10.7909 9.99993 10.8521 9.99993 10.9096 9.98611C10.9606 9.97386 11.0094 9.95366 11.0541 9.92625C11.1046 9.89533 11.1478 9.85209 11.2343 9.76561L13.6343 7.36561C14.0627 6.93724 14.2769 6.72305 14.4608 6.70858C14.6203 6.69602 14.7763 6.76061 14.8802 6.88231C15 7.02257 15 7.32548 15 7.9313V16.0686C15 16.6744 15 16.9773 14.8802 17.1175C14.7763 17.2392 14.6203 17.3038 14.4608 17.2913C14.2769 17.2768 14.0627 17.0626 13.6343 16.6342L11.2343 14.2342C11.1478 14.1478 11.1046 14.1045 11.0541 14.0736C11.0094 14.0462 10.9606 14.026 10.9096 14.0137C10.8521 13.9999 10.7909 13.9999 10.6686 13.9999H8.3C8.01997 13.9999 7.87996 13.9999 7.773 13.9454C7.67892 13.8975 7.60243 13.821 7.5545 13.7269C7.5 13.62 7.5 13.48 7.5 13.1999Z" fill="var(--element-active-color)"/>
</svg>`;var hb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="var(--alert-caution-color)"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="var(--alert-caution-outline-color)"/>
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" fill="var(--on-caution-active-color)"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" fill="var(--on-caution-active-color)"/>
</svg>`,pb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="none"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="var(--element-active-color)"/>
<path d="M8.876 6.68796L7.81255 5.62451L6.75189 6.68517L10.0666 9.99993H8.29999C8.01997 9.99993 7.87995 9.99993 7.773 10.0544C7.67892 10.1024 7.60243 10.1789 7.55449 10.2729C7.49999 10.3799 7.49999 10.5199 7.49999 10.7999V13.1999C7.49999 13.48 7.49999 13.62 7.55449 13.7269C7.60243 13.821 7.67892 13.8975 7.773 13.9454C7.87995 13.9999 8.01997 13.9999 8.29999 13.9999H10.6686C10.7909 13.9999 10.8521 13.9999 10.9096 14.0137C10.9606 14.026 11.0094 14.0462 11.0541 14.0736C11.1046 14.1045 11.1478 14.1478 11.2343 14.2342L13.6343 16.6342C14.0627 17.0626 14.2769 17.2768 14.4608 17.2913C14.6203 17.3038 14.7762 17.2393 14.8802 17.1175C15 16.9773 15 16.6744 15 16.0686V14.9333L17.3585 17.2918L18.4192 16.2311L18.0684 15.8803L18.067 15.8817L8.87464 6.68932L8.876 6.68796Z" fill="var(--element-active-color)"/>
<path d="M15 10.6933V7.9313C15 7.32548 15 7.02257 14.8802 6.88231C14.7762 6.7606 14.6203 6.69602 14.4608 6.70858C14.2769 6.72305 14.0627 6.93724 13.6343 7.36561L12.6533 8.34664L15 10.6933Z" fill="var(--element-active-color)"/>
</svg>`;var ub=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="var(--alert-caution-color)"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="var(--alert-caution-outline-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" fill="var(--on-caution-active-color)"/>
</svg>`,fu=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="none"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="var(--element-active-color)"/>
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.2071 9.20706L10.5 16.9142L5.79291 12.2071L7.20712 10.7928L10.5 14.0857L16.7929 7.79285L18.2071 9.20706Z" fill="var(--element-active-color)"/>
</svg>`;var fb=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M4 2C2.89543 2 2 2.89543 2 4V20C2 21.1046 2.89543 22 4 22H20C21.1046 22 22 21.1046 22 20V4C22 2.89543 21.1046 2 20 2H4Z" fill="var(--alert-caution-color)"/>
<path d="M4 2.5H20C20.8284 2.5 21.5 3.17157 21.5 4V20C21.5 20.8284 20.8284 21.5 20 21.5H4C3.17157 21.5 2.5 20.8284 2.5 20V4C2.5 3.17157 3.17157 2.5 4 2.5Z" stroke="var(--alert-caution-outline-color)"/>
<path d="M13 13V7H11V13H13Z" fill="var(--on-caution-active-color)"/>
<path d="M13 17V15H11V17H13Z" fill="var(--on-caution-active-color)"/>
</svg>`;var wk=Object.defineProperty,yk=Object.getOwnPropertyDescriptor,fs=(e,t,o,r)=>{for(var i=r>1?void 0:r?yk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&wk(t,o,i),i},vo={"alarm-silenced":{a:f`<obi-alarm-silenced-iec usecsscolor></obi-alarm-silenced-iec>`,b:f`<obi-alarm-silenced-outlined
      usecsscolor
    ></obi-alarm-silenced-outlined>`},"alarm-unack":{a:f`<obi-alarm-unacknowledged-iec
      usecsscolor
    ></obi-alarm-unacknowledged-iec>`,b:f`<obi-alarm-acknowledged-outlined
      usecsscolor
    ></obi-alarm-acknowledged-outlined>`},"alarm-rectified":{a:f`<obi-alarm-rectified-iec usecsscolor></obi-alarm-rectified-iec>`,b:f`<obi-alarm-rectified-outlined
      usecsscolor
    ></obi-alarm-rectified-outlined>`},"warning-unack":{a:f`<obi-warning-unacknowledged-iec
      usecsscolor
    ></obi-warning-unacknowledged-iec>`,b:f`<obi-warning-unacknowledged-outlined
      usecsscolor
    ></obi-warning-unacknowledged-outlined>`},"warning-rectified":{a:f`<obi-warning-rectified-iec
      usecsscolor
    ></obi-warning-rectified-iec>`,b:f`<obi-warning-rectified-outlined
      usecsscolor
    ></obi-warning-rectified-outlined>`},"warning-silenced":{a:f`<obi-warning-silenced-iec usecsscolor></obi-warning-silenced-iec>`,b:f`<obi-warning-silenced-outlined
      usecsscolor
    ></obi-warning-silenced-outlined>`},critical:{a:tb,b:ob},"critical-unack":{a:rb,b:ib},"critical-silenced":{a:sb,b:nb},"critical-rectified":{a:ab,b:uu},"low-unack":{a:cb,b:db},"low-silenced":{a:hb,b:pb},"low-rectified":{a:ub,b:fu}},Nr=class extends S{constructor(){super(...arguments),this.alertType=Q.Alarm,this.flashingSpeed=Ie.Default,this.flashing=new Zs(this,()=>this.resolvedFlashingSpeed)}get resolvedFlashingSpeed(){return this.acknowledged||!this.icon?Ie.Fixed:Bn(this.flashingSpeed,this._effectiveType,this.active===!1?Zi.Rectified:Zi.Active)}get _effectiveType(){return this.type?this.type:this.alertType}get bamType(){return z2(this._effectiveType)}get _effectiveState(){return this.active===!1?"rectified":this.acknowledged?"acknowledged":this.silenced?"silenced":(this.active===!0,"unacknowledged")}get icon(){if(this._effectiveType===Q.LevelCritical)switch(this._effectiveState){case"rectified":return vo["critical-rectified"];case"silenced":return vo["critical-silenced"];case"unacknowledged":return vo["critical-unack"];default:return vo.critical}else if(this._effectiveType===Q.LevelLow)switch(this._effectiveState){case"rectified":return vo["low-rectified"];case"silenced":return vo["low-silenced"];case"unacknowledged":return vo["low-unack"];default:return vo["low-unack"]}else if(this.bamType===Q.Alarm)switch(this._effectiveState){case"rectified":return vo["alarm-rectified"];case"silenced":return vo["alarm-silenced"];case"unacknowledged":return vo["alarm-unack"];default:return null}else if(this.bamType===Q.Warning)return this.active===!1?vo["warning-rectified"]:this.acknowledged?vo["warning-silenced"]:vo["warning-unack"];return null}renderStaticIcon(){if(this._effectiveType===Q.Caution)return f`<obi-caution-color-iec usecsscolor></obi-caution-color-iec>`;if(this._effectiveType===Q.LevelDiagnostic)return f`<obi-diagnostic-badge
        style="color: var(--alert-diagnostic-color);"
      ></obi-diagnostic-badge>`;if(this._effectiveState==="acknowledged"){if(this._effectiveType===Q.LevelCritical)return f`${lb}`;if(this._effectiveType===Q.LevelLow)return f`${fb}`;switch(this.bamType){case Q.Alarm:return f`<obi-alarm-acknowledged-iec
            usecsscolor
          ></obi-alarm-acknowledged-iec>`;case Q.Warning:return f`<obi-warning-acknowledged-iec
            usecsscolor
          ></obi-warning-acknowledged-iec>`;default:return z}}else if(this._effectiveState==="rectified"){if(this._effectiveType===Q.LevelCritical)return f`${uu}`;if(this._effectiveType===Q.LevelLow)return f`${fu}`;switch(this.bamType){case Q.Alarm:return f`<obi-alarm-rectified-outlined
            usecsscolor
          ></obi-alarm-rectified-outlined>`;case Q.Warning:return f`<obi-warning-rectified-outlined
            usecsscolor
          ></obi-warning-rectified-outlined>`;default:return z}}return z}render(){if(!this._effectiveType)return f`<div>No alarm</div>`;let e=this.resolvedFlashingSpeed,t=this.icon;return e!==Ie.Fixed&&t?f`
        <div class=${de({wrapper:!0,[`flash-${e}`]:!0})}>
          <span class="a">${t.a}</span>
          <span class="b">${t.b}</span>
        </div>
      `:f`<div class="wrapper">${this.renderStaticIcon()}</div>`}};Nr.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      position: relative;

      obi-diagnostic-badge,
      obi-critical-badge {
        display: block;
        height: 100%;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
      }

      svg,
      .a,
      .b {
        height: 100%;
        width: 100%;
        position: absolute;
        top: 0;
        left: 0;
      }
      &.flash-fast .a {
        opacity: var(--flash-fast-on);
      }

      &.flash-fast .b {
        opacity: var(--flash-fast-off);
      }

      &.flash-slow .a {
        opacity: var(--flash-slow-on);
      }

      &.flash-slow .b {
        opacity: var(--flash-slow-off);
      }

      &.flash-very-slow .a {
        opacity: var(--flash-very-slow-on);
      }

      &.flash-very-slow .b {
        opacity: var(--flash-very-slow-off);
      }
    }
  `;fs([h({type:String})],Nr.prototype,"alertType",2);fs([h({type:String})],Nr.prototype,"type",2);fs([h({type:Boolean})],Nr.prototype,"acknowledged",2);fs([h({type:Boolean})],Nr.prototype,"active",2);fs([h({type:Boolean})],Nr.prototype,"silenced",2);fs([h({type:String})],Nr.prototype,"flashingSpeed",2);Nr=fs([L("obc-alert-icon")],Nr);var gb=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: block;
  user-select: none;
}

.grid-container {
  display: grid;
  height: 100%;
  grid-template-columns: repeat(var(--grid-columns, 1), auto);
  align-content: start;
  grid-template-rows: min-content min-content 1fr;
}

.grid-container.has-selection-column {
    grid-template-columns:
      var(
        --selection-column-width,
        var(--menu-navigation-components-table-item-touch-target-size)
      )
      repeat(var(--grid-columns-rest, 1), minmax(0, 1fr));
  }

.grid-container .grid-header {
    grid-row: 1;
    display: grid;
    grid-column: 1/-1;
    grid-template-columns: subgrid;
    padding: 0 var(--menu-navigation-components-table-header-row-margin);
  }

.grid-container .grid-header .selection-header {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    min-width: var(
      --selection-column-width,
      var(--menu-navigation-components-table-item-touch-target-size)
    );
    min-height: var(
      --menu-navigation-components-table-header-item-touch-target-size
    );
  }

.grid-container .grid-header-divider {
    grid-row: 2;
    grid-column: 1/-1;
    margin: 0 8px;
    border-bottom: 1px solid var(--border-divider-color);
  }

.grid-container .grid-column-divider {
    grid-row: 1/-1;
    width: 1px;
    background: var(--border-divider-color);
    height: 100%;
    right: 0;
    margin-left: auto;
    z-index: 1;
    pointer-events: none;
  }

.grid-container {

  --offset: calc(
    (
        var(--obc-scrollbar-touch-target-size) -
          var(--obc-scrollbar-visual-target-size)
      ) /
      2
  );
}

.grid-container ::-webkit-scrollbar {
    width: var(--obc-scrollbar-touch-target-size);
    height: var(--obc-scrollbar-touch-target-size);
  }

.grid-container ::-webkit-scrollbar-track-piece {
    border: var(--offset) solid transparent;
    border-radius: 9999px;
    background-color: var(--indent-enabled-background-color);
    margin-top: calc(-1 * var(--offset));
    margin-bottom: calc(-1 * var(--offset));
    box-sizing: border-box;
    background-clip: content-box;
  }

.grid-container ::-webkit-scrollbar-track-piece:vertical:start {
    border-bottom-width: 0;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

.grid-container ::-webkit-scrollbar-track-piece:vertical:end {
    border-top-width: 0;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

.grid-container ::-webkit-scrollbar-track-piece:hover {
    outline-color: var(--indent-hover-border-color);
    background-color: var(--indent-hover-background-color);
  }

.grid-container ::-webkit-scrollbar-track-piece:active {
    outline-color: var(--indent-pressed-border-color);
    background-color: var(--indent-pressed-background-color);
  }

.grid-container ::-webkit-scrollbar-thumb {
    border: calc(var(--offset) + 1px) solid transparent;
    outline: 1px solid var(--obc-scrollbar-thumb-border-color);
    outline-offset: calc(-1 * var(--offset) - 1px);
    background-clip: content-box;
    border-radius: 9999px;
    background-color: var(--obc-scrollbar-thumb-background-color);
    min-height: calc(var(--obc-scrollbar-touch-target-size) * 1.5);
  }

.grid-container ::-webkit-scrollbar-thumb:hover {
    outline-color: var(--obc-scrollbar-thumb-hover-border-color);
    background-color: var(--obc-scrollbar-thumb-hover-background-color);
  }

.grid-container ::-webkit-scrollbar-thumb:active {
    outline-color: var(--obc-scrollbar-thumb-active-border-color);
    background-color: var(--obc-scrollbar-thumb-active-background-color);
  }

.grid-container ::-webkit-scrollbar-button:start:decrement,.grid-container ::-webkit-scrollbar-button:end:increment {
    display: var(--obc-scrollbar-button-display);
    height: var(--obc-scrollbar-button-size);
    width: var(--obc-scrollbar-button-size);
    box-sizing: border-box;
    background-clip: content-box;
    background-repeat: no-repeat;
    background-position: center;
    border: var(--obc-scrollbar-button-margin) solid transparent;
    border-radius: var(--obc-scrollbar-button-radius);
    background-clip: padding-box;
    background-color: var(--flat-enabled-background-color);
  }

.grid-container ::-webkit-scrollbar-button:start:decrement:hover,.grid-container ::-webkit-scrollbar-button:end:increment:hover {
    background-color: var(--flat-hover-background-color);
  }

.grid-container ::-webkit-scrollbar-button:start:decrement:active,.grid-container ::-webkit-scrollbar-button:end:increment:active {
    background-color: var(--flat-pressed-background-color);
  }

.grid-container ::-webkit-scrollbar-button:vertical:start:decrement {
    background-image: var(--icon-02-chevron-up);
  }

.grid-container ::-webkit-scrollbar-button:vertical:end:increment {
    background-image: var(--icon-02-chevron-down);
  }

.grid-container .grid-body {
    grid-row: 3;
    overflow: auto;
    scrollbar-gutter: stable;
    display: grid;
    grid-column: 1/-1;
    grid-template-columns: subgrid;
    padding: 0 var(--menu-navigation-components-table-header-row-margin);
  }

.grid-container .grid-row {
    display: grid;
    grid-column: 1/-1;
    grid-template-columns: subgrid;
    min-height: var(--menu-navigation-components-table-item-touch-target-size);
    will-change: transform, opacity;
    position: relative;
    padding: 0;
  }

.striped:is(.grid-container .grid-row) {
      background: var(--container-section-color);
    }

:is(.grid-container .grid-row) {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

:is(.grid-container .grid-row):focus {
  outline: none;
}

.activated:is(.grid-container .grid-row) {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

:is(.grid-container .grid-row):hover {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

:is(.grid-container .grid-row):active {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

:is(.grid-container .grid-row):focus-visible {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

:is(.grid-container .grid-row):disabled {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.disabled:is(.grid-container .grid-row) {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.grid-container .grid-row {
    border: 1px solid transparent;
    --flat-active-background-color: transparent;
  }

:is(.grid-container .grid-row):focus-visible {
    outline-offset: -2px;
  }

.grid-container .grid-row {
    border-radius: var(--global-border-radius-border-radius-base);
  }

.selected:is(.grid-container .grid-row) {
  border-color: var(--amplified-enabled-border-color);
  background-color: var(--amplified-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--amplified-enabled-border-color);
  --base-background-color: var(--amplified-enabled-background-color);
}

.selected:is(.grid-container .grid-row):focus {
  outline: none;
}

.selected.activated:is(.grid-container .grid-row) {
  border-color: var(--amplified-activated-border-color);
  background-color: var(--amplified-activated-background-color);
  --base-border-color: var(--amplified-activated-border-color);
  --base-background-color: var(--amplified-activated-background-color);
}

@media (hover:hover) {

.selected:is(.grid-container .grid-row):hover {
    border-color: color-mix(in srgb, var(--amplified-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--amplified-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.selected:is(.grid-container .grid-row):active {
  border-color: var(--amplified-pressed-border-color);
  background-color: var(--amplified-pressed-background-color);
}

.selected:is(.grid-container .grid-row):focus-visible {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.selected:is(.grid-container .grid-row):disabled {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.selected.disabled:is(.grid-container .grid-row) {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.selected-with-prev:is(.grid-container .grid-row) {
      border-top-color: transparent;
      border-top-left-radius: 0;
      border-top-right-radius: 0;
    }

.selected-with-next:is(.grid-container .grid-row) {
      border-bottom-color: transparent;
      border-bottom-left-radius: 0;
      border-bottom-right-radius: 0;
    }

.selected-with-next:is(.grid-container .grid-row) .grid-row-divider {
      display: none;
    }

.animating:is(.grid-container .grid-row) {
      pointer-events: none;
    }

:is(.grid-container .grid-row) .grid-cell {
      position: relative;
      display: flex;
      align-items: center;
      justify-content: flex-start;
      padding: 0 var(--menu-navigation-components-table-item-padding-horizontal);
      min-height: 100%;
      min-width: var(--menu-navigation-components-table-item-touch-target-size);
      gap: var(--menu-navigation-components-table-item-label-spacing);
      font-family: var(--global-typography-font-family);
      font-weight: var(--global-typography-ui-body-font-weight);
      font-size: var(--global-typography-ui-body-font-size);
      line-height: var(--global-typography-ui-body-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      color: var(--on-flat-active-color);
    }

.selection:is(:is(.grid-container .grid-row) .grid-cell) {
        min-width: var(
          --selection-column-width,
          var(--menu-navigation-components-table-item-touch-target-size)
        );
        width: var(
          --selection-column-width,
          var(--menu-navigation-components-table-item-touch-target-size)
        );
        max-width: var(
          --selection-column-width,
          var(--menu-navigation-components-table-item-touch-target-size)
        );
        padding: 0;
      }

.neutral:is(:is(.grid-container .grid-row) .grid-cell) {
        color: var(--on-flat-neutral-color);
      }

.vertical:is(:is(.grid-container .grid-row) .grid-cell) {
        flex-direction: column;
        align-items: flex-start;
        justify-content: flex-start;
        gap: 0;
        padding-top: var(--menu-navigation-components-table-item-label-spacing);
        padding-bottom: var(
          --menu-navigation-components-table-item-label-spacing
        );
      }

.align-center:is(:is(.grid-container .grid-row) .grid-cell) {
        justify-content: center;
      }

.align-right:is(:is(.grid-container .grid-row) .grid-cell) {
        justify-content: flex-end;
      }

.align-left:is(:is(.grid-container .grid-row) .grid-cell) {
        justify-content: flex-start;
      }

.no-wrap:is(:is(.grid-container .grid-row) .grid-cell) > * {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

.no-wrap:is(:is(.grid-container .grid-row) .grid-cell) {
        width: 100%;
      }

.no-wrap:is(:is(.grid-container .grid-row) .grid-cell) .title {
          flex-shrink: 0;
        }

.no-wrap:is(:is(.grid-container .grid-row) .grid-cell) .text {
          flex-shrink: 10000;
        }

:is(:is(.grid-container .grid-row) .grid-cell) .icon {
        width: var(--menu-navigation-components-table-item-icon-size);
        height: var(--menu-navigation-components-table-item-icon-size);
        flex-shrink: 0;
      }

/* ---- Hierarchy ---- */

/*
       * Indent gutter for a hierarchical row. One step per level plus one for
       * the chevron itself, so a leaf and a group at the same level align.
       */

:is(:is(.grid-container .grid-row) .grid-cell) .row-expander {
        --row-indent-step: var(
          --menu-navigation-components-table-item-icon-size
        );
        /* Depth of this row; the row's inline style overrides it. */
        --row-level: 0;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        flex-shrink: 0;
        align-self: stretch;
        width: calc((var(--row-level) + 1) * var(--row-indent-step));
      }

:is(:is(.grid-container .grid-row) .grid-cell) .row-expander .chevron {
        display: flex;
        align-items: center;
        justify-content: center;
        /* Pointer target floor, and the gutter is only one step wide. */
        min-width: var(--row-indent-step);
        min-height: var(--row-indent-step);
        align-self: stretch;
        color: var(--on-flat-neutral-color);
        transition: transform 100ms ease-in-out;
      }

:is(:is(.grid-container .grid-row) .grid-cell) .row-expander .chevron.expanded {
        transform: rotate(90deg);
      }

@media (prefers-reduced-motion: reduce) {
        :is(:is(.grid-container .grid-row) .grid-cell) .row-expander .chevron {
          transition: none;
        }
      }

.large-icon:is(:is(.grid-container .grid-row) .grid-cell) .icon {
        min-width: var(--menu-navigation-components-table-item-icon-size-large);
        min-height: var(
          --menu-navigation-components-table-item-icon-size-large
        );
        width: fit-content;
        height: fit-content;
        display: grid;
      }

:is(:is(.grid-container .grid-row) .grid-cell) .title {
        font-family: var(--global-typography-font-family);
        font-weight: var(--global-typography-ui-body-active-font-weight);
        font-size: var(--global-typography-ui-body-active-font-size);
        line-height: var(--global-typography-ui-body-active-line-height);
        font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
      }

.button:is(:is(.grid-container .grid-row) .grid-cell) obc-button {
          width: 100%;
        }

.checkbox:is(:is(.grid-container .grid-row) .grid-cell) {
        min-width: 0;
      }

.checkbox:is(:is(.grid-container .grid-row) .grid-cell) {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
        background: transparent;
        --flat-active-background-color: transparent;
        --flat-hover-background-color: transparent;
}

.horizontal-bar:is(:is(.grid-container .grid-row) .grid-cell) {
        padding: 0
          var(--menu-navigation-components-table-item-padding-horizontal);
      }

.horizontal-bar:is(:is(.grid-container .grid-row) .grid-cell) obc-bar-horizontal {
        display: block;
        width: 100%;
        height: 100%;
      }

.tags:is(:is(.grid-container .grid-row) .grid-cell) {
        gap: calc(
          var(--menu-navigation-components-table-item-badge-spacing) * 2
        );
      }

.tags:is(:is(.grid-container .grid-row) .grid-cell) .tag-overflow {
          font-family: var(--global-typography-font-family);
          font-weight: var(--global-typography-ui-label-font-weight);
          font-size: var(--global-typography-ui-label-font-size);
          line-height: var(--global-typography-ui-label-line-height);
          font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
          color: var(--on-flat-neutral-color);
          white-space: nowrap;
          margin: 0;
        }

.tags.wrap:is(:is(.grid-container .grid-row) .grid-cell) {
          flex-wrap: wrap;
          align-content: center;
        }

.grid-container .grid-row-divider {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    margin: 0 8px;
    border-radius: 100px;
    background: var(--border-divider-color);
    height: 1px;
    margin-bottom: -1.5px;
    z-index: -1;
  }
`;var mb=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: flex;
  width: 100%;
}

.wrapper {
  width: 100%;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: stretch;
  user-select: none;
  -webkit-user-select: none;
  appearance: none;
  border: none;
  background: transparent;
  font-family: var(--global-typography-font-family);
  font-weight: var(--global-typography-ui-overline-font-weight);
  font-size: var(--global-typography-ui-overline-font-size);
  line-height: var(--global-typography-ui-overline-line-height);
  letter-spacing: var(--global-typography-ui-overline-letter-spacing);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  height: var(--menu-navigation-components-table-header-item-touch-target-size);
  padding: 0
    var(--menu-navigation-components-table-header-item-margin-horizontal);

  color: var(--element-neutral-color);
}

.wrapper.sortable {
  cursor: pointer;
}

.wrapper.sortable:focus {
  outline: none;
}

.wrapper.sortable .visible-wrapper {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.wrapper.sortable.activated .visible-wrapper {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.wrapper.sortable:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.sortable:active .visible-wrapper {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.wrapper.sortable:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.sortable:disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.sortable.disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.sortable:disabled {
  cursor: not-allowed;
}

.wrapper.sortable.disabled {
  cursor: not-allowed;
}

.wrapper.checked {
  cursor: pointer;
}

.wrapper.checked:focus {
  outline: none;
}

.wrapper.checked .visible-wrapper {
  border-color: var(--amplified-enabled-border-color);
  background-color: var(--amplified-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--amplified-enabled-border-color);
  --base-background-color: var(--amplified-enabled-background-color);
}

.wrapper.checked.activated .visible-wrapper {
  border-color: var(--amplified-activated-border-color);
  background-color: var(--amplified-activated-background-color);
  --base-border-color: var(--amplified-activated-border-color);
  --base-background-color: var(--amplified-activated-background-color);
}

@media (hover:hover) {

.wrapper.checked:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--amplified-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--amplified-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.checked:active .visible-wrapper {
  border-color: var(--amplified-pressed-border-color);
  background-color: var(--amplified-pressed-background-color);
}

.wrapper.checked:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.checked:disabled .visible-wrapper {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.wrapper.checked.disabled .visible-wrapper {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.wrapper.checked:disabled {
  cursor: not-allowed;
}

.wrapper.checked.disabled {
  cursor: not-allowed;
}

.wrapper.checked {
  color: var(--instrument-enhanced-secondary-color);
}

.wrapper.style-narrow {
  padding: 0;
  height: var(--menu-navigation-components-table-header-item-icon-size);
}

.wrapper.style-narrow .visible-wrapper {
    border-radius: 0;
    border-width: 0;
    min-height: var(--menu-navigation-components-table-header-item-icon-size);
  }

.wrapper .visible-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  min-height: var(
    --menu-navigation-components-table-header-item-visual-target-size
  );
  border-radius: var(
    --menu-navigation-components-table-header-item-border-radius
  );
  padding: 0
    var(--menu-navigation-components-table-header-item-padding-horizontal);
}

.wrapper .label {
  padding: 0 var(--menu-navigation-components-table-header-item-label-spacing);
  white-space: nowrap;
  flex-grow: 1;
  text-align: left;
}

/* Icon containers */

.wrapper .leading,
.wrapper .trailing,
.wrapper .sort-icon {
  display: inline-flex;
  align-items: center;
}

.wrapper.has-leading-icon .leading,
.wrapper .sort-icon {
  width: var(--menu-navigation-components-table-header-item-icon-size);
  height: var(--menu-navigation-components-table-header-item-icon-size);
}

/* Disabled text color alignment */

.wrapper:disabled .label,
.wrapper.disabled .label {
  color: var(--element-disabled-color);
}

.divider {
  display: flex;
  height: 24px;
  align-items: center;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  margin: auto;
  width: 1px;
  background-color: var(--border-divider-color);
}
`;var Ck=Object.defineProperty,xk=Object.getOwnPropertyDescriptor,Ci=(e,t,o,r)=>{for(var i=r>1?void 0:r?xk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ck(t,o,i),i},yd=(e=>(e.Regular="Regular",e.IconOnly="IconOnly",e.Narrow="Narrow",e))(yd||{});var ur=class extends S{constructor(){super(...arguments),this.type="Regular",this.disabled=!1,this.hasLeadingIcon=!1,this.sortDirection="none",this.showDivider=!1,this.checked=!1,this.sortable=!1}render(){let e={wrapper:!0,[`style-${(this.type??"Regular").toLowerCase()}`]:!0,sortable:this.sortable,disabled:this.disabled,"has-leading-icon":this.hasLeadingIcon,"sorted-asc":this.sortDirection==="asc","sorted-desc":this.sortDirection==="desc",checked:this.checked},t=this.sortable?Fs`button`:Fs`div`;return ho`
      <${t}
        class=${de(e)}
        ?disabled=${this.disabled}
        part="wrapper"
      >
        <div class="visible-wrapper" part="visible-wrapper">
          ${this.hasLeadingIcon?ho`<span class="leading" part="leading"
                  ><slot name="leading-icon"></slot
                ></span>`:z}
          ${this.type!=="IconOnly"?ho`<span class="label" part="label"><slot></slot></span>`:z}
          ${this.sortable?ho`<span class="trailing sort-icon" part="sort-icon"
                  >${this._renderSortIcon()}</span
                >`:z}
        </div>
        ${this.showDivider?ho`<div class="divider" part="divider"></div>`:z}
      </${t}>
    `}_renderSortIcon(){switch(this.sortDirection){case"asc":return ho`<obi-chevron-up-google></obi-chevron-up-google>`;case"desc":return ho`<obi-chevron-down-google></obi-chevron-down-google>`;default:return z}}};ur.styles=ne(mb);Ci([h({type:String})],ur.prototype,"type",2);Ci([h({type:Boolean})],ur.prototype,"disabled",2);Ci([h({type:Boolean})],ur.prototype,"hasLeadingIcon",2);Ci([h({type:String})],ur.prototype,"sortDirection",2);Ci([h({type:Boolean})],ur.prototype,"showDivider",2);Ci([h({type:Boolean})],ur.prototype,"checked",2);Ci([h({type:Boolean})],ur.prototype,"sortable",2);ur=Ci([L("obc-table-header-item")],ur);var _k=Object.defineProperty,kk=Object.getOwnPropertyDescriptor,vb=(e,t,o,r)=>{for(var i=r>1?void 0:r?kk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&_k(t,o,i),i},Cd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.9998 13.0002H4.99976V11.0002H18.9998V13.0002Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M18.9998 13.0002H4.99976V11.0002H18.9998V13.0002Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};Cd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;vb([h({type:Boolean})],Cd.prototype,"useCssColor",2);Cd=vb([L("obi-check-mixed")],Cd);var Lk=Object.defineProperty,Sk=Object.getOwnPropertyDescriptor,bb=(e,t,o,r)=>{for(var i=r>1?void 0:r?Sk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Lk(t,o,i),i},xd=class extends S{constructor(){super(...arguments),this.useCssColor=!1,this.icon=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
<path d="M8.99991 16.17L4.82991 12L3.40991 13.41L8.99991 19L20.9999 7L19.5899 5.59L8.99991 16.17Z" fill="currentColor"/>
</svg>
`,this.iconCss=w`<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M8.99991 16.17L4.82991 12L3.40991 13.41L8.99991 19L20.9999 7L19.5899 5.59L8.99991 16.17Z" style="fill: var(--element-active-color)"/>
</svg>
`}render(){return f`
      <div class="wrapper">${this.useCssColor?this.iconCss:this.icon}</div>
    `}};xd.styles=M`
    .wrapper {
      height: 100%;
      width: 100%;
      line-height: 0;
    }
    .wrapper > * {
      height: 100%;
      width: 100%;
    }
  `;bb([h({type:Boolean})],xd.prototype,"useCssColor",2);xd=bb([L("obi-check-google")],xd);var wb=M`* {
  -webkit-tap-highlight-color: transparent;
}

.visually-hidden {
  box-sizing: border-box;
  display: flex;
  height: var(--ui-components-checkbox-touch-target-size);
  min-width: var(--ui-components-checkbox-touch-target-size);
  min-height: var(--ui-components-checkbox-touch-target-size);
  padding: 0px var(--ui-components-checkbox-margin);
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  user-select: none;
  cursor: pointer;
  outline: none;
}

.visually-hidden.state-loading {
    cursor: progress;
  }

.visually-hidden.disabled {
    cursor: not-allowed;
  }

.checkbox-container {
  display: flex;
  padding: 0px;
  align-items: center;
  justify-content: center;
}

.checkbox-loading-spinner {
  width: var(--global-size-spacing-icon-icon-size-small);
  height: var(--global-size-spacing-icon-icon-size-small);
  align-self: center;
  margin: auto;
  animation: checkbox-loading-spin 1000ms linear infinite;
}

.checkbox-loading-spinner circle {
    fill: none;
    stroke: currentColor;
    stroke-width: var(
      --ui-components-progressbars-progress-bar--circular-bar-weight-small
    );
    stroke-linecap: round;
    stroke-dasharray: 24 14;
  }

.state-loading.status-unchecked .checkbox-loading-spinner {
    color: var(--element-neutral-color);
  }

.state-loading.status-checked .checkbox-loading-spinner {
    color: var(--element-active-inverted-color);
  }

.state-loading.status-mixed .checkbox-loading-spinner {
    color: var(--instrument-enhanced-secondary-color);
  }

.checkbox-container.status-unchecked:not(.disabled):hover .checkbox-box {
  background: var(--indent-hover-background-color);
  border-color: var(--indent-hover-border-color);
}

.checkbox-container.status-unchecked:not(.disabled):active .checkbox-box {
  background: var(--indent-pressed-background-color);
  border-color: var(--indent-pressed-border-color);
}

.checkbox-container.status-unchecked:not(.disabled):focus-visible
  .checkbox-box {
  background: var(--indent-focused-background-color);
  border-color: var(--indent-focused-border-color);
}

.checkbox-container.status-checked:not(.disabled):hover .checkbox-box,
.checkbox-container.status-mixed:not(.disabled):hover .checkbox-box {
  background: var(--selected-hover-background-color);
  border-color: var(--selected-hover-border-color);
}

.checkbox-container.status-checked:not(.disabled):active .checkbox-box,
.checkbox-container.status-mixed:not(.disabled):active .checkbox-box {
  background: var(--selected-pressed-background-color);
  border-color: var(--selected-pressed-border-color);
}

.checkbox-container.status-checked:not(.disabled):focus-visible .checkbox-box,
.checkbox-container.status-mixed:not(.disabled):focus-visible .checkbox-box {
  background: var(--selected-focused-background-color);
  border-color: var(--selected-focused-border-color);
}

.checkbox-icon {
  width: var(--global-size-spacing-icon-icon-size-regular);
  height: var(--global-size-spacing-icon-icon-size-regular);
  flex-shrink: 0;
}

.status-checked .checkbox-icon {
    color: var(--on-selected-active-color);
  }

.status-unchecked:not(.no-hover-effects) {
  cursor: pointer;
}

.status-unchecked:not(.no-hover-effects):focus {
  outline: none;
}

.status-unchecked:not(.no-hover-effects) .checkbox-box {
  border-color: var(--indent-enabled-border-color);
  background-color: var(--indent-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--indent-enabled-border-color);
  --base-background-color: var(--indent-enabled-background-color);
}

.status-unchecked.activated:not(.no-hover-effects) .checkbox-box {
  border-color: var(--indent-activated-border-color);
  background-color: var(--indent-activated-background-color);
  --base-border-color: var(--indent-activated-border-color);
  --base-background-color: var(--indent-activated-background-color);
}

@media (hover:hover) {

.status-unchecked:not(.no-hover-effects):hover .checkbox-box {
    border-color: color-mix(in srgb, var(--indent-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--indent-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.status-unchecked:not(.no-hover-effects):active .checkbox-box {
  border-color: var(--indent-pressed-border-color);
  background-color: var(--indent-pressed-background-color);
}

.status-unchecked:not(.no-hover-effects):focus-visible .checkbox-box {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.status-unchecked:not(.no-hover-effects):disabled .checkbox-box {
  border-color: var(--indent-disabled-border-color);
  background-color: var(--indent-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-indent-disabled-color) !important;
}

.status-unchecked.disabled:not(.no-hover-effects) .checkbox-box {
  border-color: var(--indent-disabled-border-color);
  background-color: var(--indent-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-indent-disabled-color) !important;
}

.status-unchecked:not(.no-hover-effects):disabled {
  cursor: not-allowed;
}

.status-unchecked.disabled:not(.no-hover-effects) {
  cursor: not-allowed;
}

.status-unchecked:not(.no-hover-effects):not(.disabled) .checkbox-box,.status-unchecked:not(.no-hover-effects):not(.disabled):hover .checkbox-box {
    border-color: var(--element-symbol-color);
  }

.status-unchecked.no-hover-effects .checkbox-box {
  border-color: var(--indent-enabled-border-color);
  background-color: var(--indent-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--indent-enabled-border-color);
  --base-background-color: var(--indent-enabled-background-color);
}

.status-checked.no-hover-effects .checkbox-box {
  border-color: var(--selected-enabled-border-color);
  background-color: var(--selected-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--selected-enabled-border-color);
  --base-background-color: var(--selected-enabled-background-color);
}

.status-mixed.no-hover-effects .checkbox-box {
  border-color: var(--amplified-enabled-border-color);
  background-color: var(--amplified-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--amplified-enabled-border-color);
  --base-background-color: var(--amplified-enabled-background-color);
}

.status-checked:not(.no-hover-effects) {
  cursor: pointer;
}

.status-checked:not(.no-hover-effects):focus {
  outline: none;
}

.status-checked:not(.no-hover-effects) .checkbox-box {
  border-color: var(--selected-enabled-border-color);
  background-color: var(--selected-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--selected-enabled-border-color);
  --base-background-color: var(--selected-enabled-background-color);
}

.status-checked.activated:not(.no-hover-effects) .checkbox-box {
  border-color: var(--selected-activated-border-color);
  background-color: var(--selected-activated-background-color);
  --base-border-color: var(--selected-activated-border-color);
  --base-background-color: var(--selected-activated-background-color);
}

@media (hover:hover) {

.status-checked:not(.no-hover-effects):hover .checkbox-box {
    border-color: color-mix(in srgb, var(--selected-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--selected-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.status-checked:not(.no-hover-effects):active .checkbox-box {
  border-color: var(--selected-pressed-border-color);
  background-color: var(--selected-pressed-background-color);
}

.status-checked:not(.no-hover-effects):focus-visible .checkbox-box {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.status-checked:not(.no-hover-effects):disabled .checkbox-box {
  border-color: var(--selected-disabled-border-color);
  background-color: var(--selected-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-selected-disabled-color) !important;
}

.status-checked.disabled:not(.no-hover-effects) .checkbox-box {
  border-color: var(--selected-disabled-border-color);
  background-color: var(--selected-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-selected-disabled-color) !important;
}

.status-checked:not(.no-hover-effects):disabled {
  cursor: not-allowed;
}

.status-checked.disabled:not(.no-hover-effects) {
  cursor: not-allowed;
}

.status-mixed:not(.no-hover-effects) {
  cursor: pointer;
}

.status-mixed:not(.no-hover-effects):focus {
  outline: none;
}

.status-mixed:not(.no-hover-effects) .checkbox-box {
  border-color: var(--amplified-enabled-border-color);
  background-color: var(--amplified-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--amplified-enabled-border-color);
  --base-background-color: var(--amplified-enabled-background-color);
}

.status-mixed.activated:not(.no-hover-effects) .checkbox-box {
  border-color: var(--amplified-activated-border-color);
  background-color: var(--amplified-activated-background-color);
  --base-border-color: var(--amplified-activated-border-color);
  --base-background-color: var(--amplified-activated-background-color);
}

@media (hover:hover) {

.status-mixed:not(.no-hover-effects):hover .checkbox-box {
    border-color: color-mix(in srgb, var(--amplified-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--amplified-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.status-mixed:not(.no-hover-effects):active .checkbox-box {
  border-color: var(--amplified-pressed-border-color);
  background-color: var(--amplified-pressed-background-color);
}

.status-mixed:not(.no-hover-effects):focus-visible .checkbox-box {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.status-mixed:not(.no-hover-effects):disabled .checkbox-box {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.status-mixed.disabled:not(.no-hover-effects) .checkbox-box {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

.status-mixed:not(.no-hover-effects):disabled {
  cursor: not-allowed;
}

.status-mixed.disabled:not(.no-hover-effects) {
  cursor: not-allowed;
}

.checkbox-box {
  box-sizing: border-box;
  position: relative;
  display: flex;
  width: var(--ui-components-checkbox-visual-target-size);
  height: var(--ui-components-checkbox-visual-target-size);
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: var(--ui-components-checkbox-border-radius);
  border: 1px solid transparent;
  background: transparent;
}

.status-mixed:not(.disabled) .checkbox-box,.status-mixed:not(.disabled):hover .checkbox-box,.status-mixed:not(.disabled):active .checkbox-box {
    border-color: var(--instrument-enhanced-secondary-color);
  }

:is(.status-unchecked.no-hover-effects .checkbox-box) {
  border-color: var(--indent-enabled-border-color);
  background-color: var(--indent-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  --base-border-color: var(--indent-enabled-border-color);
  --base-background-color: var(--indent-enabled-background-color);
}

.status-unchecked.no-hover-effects .checkbox-box {
    border-color: var(--element-symbol-color);
  }

.status-unchecked.state-enabled:not(.disabled):not(
    .no-hover-effects
  ):focus-visible
  .checkbox-box {
  border-color: transparent;
}

@keyframes checkbox-loading-spin {
  to {
    transform: rotate(360deg);
  }
}
`;var Mk=Object.defineProperty,$k=Object.getOwnPropertyDescriptor,_n=(e,t,o,r)=>{for(var i=r>1?void 0:r?$k(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Mk(t,o,i),i},fr=(e=>(e.unchecked="unchecked",e.checked="checked",e.mixed="mixed",e))(fr||{});var xi=class extends S{constructor(){super(...arguments),this.status="unchecked",this.state="enabled",this.disabled=!1,this.hasHoverEffects=!0}get _isInteractionLocked(){return this.disabled||this.state==="loading"}updated(e){e.has("disabled")&&this.dispatchEvent(new CustomEvent("disabled",{detail:{status:this.status,disabled:this.disabled}}))}toggleStatus(){this._isInteractionLocked||(this.status==="checked"?this.status="unchecked":this.status="checked",this.dispatchEvent(new CustomEvent("change",{detail:{status:this.status,disabled:this.disabled}})))}handleKeydown(e){(e.key===" "||e.key==="Space"||e.key==="Enter")&&(e.preventDefault(),this.toggleStatus())}get _computedAriaChecked(){switch(this.status){case"checked":return"true";case"mixed":return"mixed";case"unchecked":default:return"false"}}focus(e){this.checkboxControl?.focus(e)}syncFocusVisibleAttribute(){let e=this.checkboxControl?.matches(":focus-visible");this.toggleAttribute("data-focus-visible",!!e)}handleControlFocus(){queueMicrotask(()=>this.syncFocusVisibleAttribute())}handleControlBlur(){this.removeAttribute("data-focus-visible")}render(){let e=this.getAttribute("aria-label")??void 0,t=this.getAttribute("aria-labelledby")??void 0,o=this.getAttribute("aria-describedby")??void 0,r=t?void 0:e??"Checkbox item";return f`
      <div
        class=${de({"visually-hidden":!0,[`status-${this.status}`]:!0,[`state-${this.state}`]:!0,disabled:this.disabled,"no-hover-effects":!this.hasHoverEffects})}
        role="checkbox"
        aria-checked=${this._computedAriaChecked}
        aria-label=${Ce(r)}
        aria-labelledby=${Ce(t)}
        aria-describedby=${Ce(o)}
        aria-disabled=${this._isInteractionLocked?"true":"false"}
        aria-busy=${this.state==="loading"?"true":"false"}
        tabindex=${this._isInteractionLocked?"-1":"0"}
        @click=${this.toggleStatus}
        @keydown=${this.handleKeydown}
        @focus=${this.handleControlFocus}
        @blur=${this.handleControlBlur}
      >
        <div class="checkbox-container">
          <div class="checkbox-box">
            ${this.state==="loading"?f`
                  <svg
                    class="checkbox-loading-spinner type-indeterminate size-small style-regular"
                    viewBox="0 0 16 16"
                    aria-hidden="true"
                  >
                    <circle cx="8" cy="8" r="6"></circle>
                  </svg>
                `:this.status==="checked"?f`<obi-check-google
                    class="checkbox-icon"
                  ></obi-check-google>`:this.status==="mixed"?f`<obi-check-mixed
                      class="checkbox-icon"
                    ></obi-check-mixed>`:f`<span class="checkbox-icon"></span>`}
          </div>
        </div>
      </div>
    `}};xi.styles=[ne(wb)];_n([h({type:String})],xi.prototype,"status",2);_n([h({type:String})],xi.prototype,"state",2);_n([h({type:Boolean})],xi.prototype,"disabled",2);_n([h({type:Boolean,attribute:!1})],xi.prototype,"hasHoverEffects",2);_n([at(".visually-hidden")],xi.prototype,"checkboxControl",2);xi=_n([L("obc-checkbox")],xi);var yb=M`* {
  -webkit-tap-highlight-color: transparent;
}

:host {
  display: inline-block;
}

.wrapper {
  box-sizing: border-box;
  display: inline-flex;
  align-items: center;
  gap: var(--ui-components-tag-label-spacing-large);
  height: var(--ui-components-tag-visual-target);
  padding: var(--global-size-spacing-target-padding)
    var(--ui-components-tag-padding-horizontal);
  border: var(--ui-components-badge-icon-size-flat-border-weight) solid
    var(--indent-enabled-border-color);
  border-radius: var(--ui-components-tag-border-radius);
  background: var(--indent-enabled-background-color);
}

.wrapper .tag-icon-wrapper {
    display: flex;
    width: var(--ui-components-tag-icon-size);
    height: var(--ui-components-tag-icon-size);
    max-width: calc(
      var(--ui-components-tag-visual-target) -
        var(--global-size-spacing-target-padding) * 2 -
        var(--ui-components-badge-icon-size-flat-border-weight) * 2
    );
    max-height: calc(
      var(--ui-components-tag-visual-target) -
        var(--global-size-spacing-target-padding) * 2 -
        var(--ui-components-badge-icon-size-flat-border-weight) * 2
    );
  }

:is(.wrapper .tag-icon-wrapper) ::slotted(*) {
      display: block;
      width: 100%;
      height: 100%;
    }

.wrapper .tag-label-container {
    display: flex;
  }

.wrapper .tag-label {
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-label-font-weight);
    font-size: var(--global-typography-ui-label-font-size);
    line-height: var(--global-typography-ui-label-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.wrapper.size-large {
    height: var(--ui-components-tag-visual-target-large);
    padding: var(--global-size-spacing-target-padding)
      var(--ui-components-tag-padding-horizontal-large);
  }

.wrapper.size-large .tag-icon-wrapper {
      width: var(--ui-components-tag-icon-size-large);
      height: var(--ui-components-tag-icon-size-large);
      max-width: calc(
        var(--ui-components-tag-visual-target-large) -
          var(--global-size-spacing-target-padding) * 2 -
          var(--ui-components-badge-icon-size-flat-border-weight) * 2
      );
      max-height: calc(
        var(--ui-components-tag-visual-target-large) -
          var(--global-size-spacing-target-padding) * 2 -
          var(--ui-components-badge-icon-size-flat-border-weight) * 2
      );
    }

.wrapper.size-large .tag-label {
      font-family: var(--global-typography-font-family);
      font-weight: var(--global-typography-ui-body-font-weight);
      font-size: var(--global-typography-ui-body-font-size);
      line-height: var(--global-typography-ui-body-line-height);
      font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    }

.wrapper.color-gray {
    color: var(--on-indent-active-color);
    background: var(--indent-enabled-background-color);
    border-color: var(--indent-enabled-border-color);
  }

.wrapper.color-gray .tag-icon-wrapper {
      color: var(--on-indent-neutral-color);
    }

.wrapper.color-blue {
    color: var(--base-blue-600);
    background-color: var(--base-blue-050);
    border-color: var(--base-blue-100);
  }

.wrapper.color-blue .tag-icon-wrapper {
      color: var(--base-blue-500);
    }

.wrapper.color-cyan {
    color: var(--base-cyan-600);
    background-color: var(--base-cyan-050);
    border-color: var(--base-cyan-100);
  }

.wrapper.color-cyan .tag-icon-wrapper {
      color: var(--base-cyan-500);
    }

.wrapper.color-teal {
    color: var(--base-teal-600);
    background-color: var(--base-teal-050);
    border-color: var(--base-teal-100);
  }

.wrapper.color-teal .tag-icon-wrapper {
      color: var(--base-teal-500);
    }

.wrapper.color-green {
    color: var(--base-mint-600);
    background-color: var(--base-mint-050);
    border-color: var(--base-mint-100);
  }

.wrapper.color-green .tag-icon-wrapper {
      color: var(--base-mint-500);
    }

.wrapper.color-yellow {
    color: var(--base-yellow-600);
    background-color: var(--base-yellow-050);
    border-color: var(--base-yellow-100);
  }

.wrapper.color-yellow .tag-icon-wrapper {
      color: var(--base-yellow-500);
    }

.wrapper.color-orange {
    color: var(--base-orange-600);
    background-color: var(--base-orange-050);
    border-color: var(--base-orange-100);
  }

.wrapper.color-orange .tag-icon-wrapper {
      color: var(--base-orange-500);
    }

.wrapper.color-red {
    color: var(--base-red-600);
    background-color: var(--base-red-050);
    border-color: var(--base-red-100);
  }

.wrapper.color-red .tag-icon-wrapper {
      color: var(--base-red-500);
    }

.wrapper.color-purple {
    color: var(--base-purple-600);
    background-color: var(--base-purple-050);
    border-color: var(--base-purple-100);
  }

.wrapper.color-purple .tag-icon-wrapper {
      color: var(--base-purple-500);
    }

.wrapper.color-indigo {
    color: var(--base-indigo-600);
    background-color: var(--base-indigo-050);
    border-color: var(--base-indigo-100);
  }

.wrapper.color-indigo .tag-icon-wrapper {
      color: var(--base-indigo-500);
    }
`;var Ak=Object.defineProperty,Pk=Object.getOwnPropertyDescriptor,za=(e,t,o,r)=>{for(var i=r>1?void 0:r?Pk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ak(t,o,i),i},gu=(e=>(e.gray="gray",e.blue="blue",e.cyan="cyan",e.teal="teal",e.green="green",e.yellow="yellow",e.orange="orange",e.red="red",e.purple="purple",e.indigo="indigo",e))(gu||{});var gs=class extends S{constructor(){super(...arguments),this.label="Label",this.color="gray",this.size="regular",this.hasIcon=!1}renderLeadingIcon(){return this.hasIcon?f`
      <div class="tag-icon-wrapper">
        <slot></slot>
      </div>
    `:z}render(){return f`
      <div
        class=${de({wrapper:!0,["color-"+this.color]:!0,["size-"+this.size]:!0})}
      >
        ${this.renderLeadingIcon()}
        <div class="tag-label-container">
          <span class="tag-label">${this.label}</span>
        </div>
      </div>
    `}};gs.styles=ne(yb);za([h({type:String})],gs.prototype,"label",2);za([h({type:String})],gs.prototype,"color",2);za([h({type:String})],gs.prototype,"size",2);za([h({type:Boolean})],gs.prototype,"hasIcon",2);gs=za([L("obc-tag")],gs);var Ok=Object.defineProperty,Vk=Object.getOwnPropertyDescriptor,Me=(e,t,o,r)=>{for(var i=r>1?void 0:r?Vk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ok(t,o,i),i},_e=class extends vi(S,{defaultDeadband:1}){constructor(){super(...arguments),this.minValue=0,this.maxValue=100,this.width=320,this.paddingLeft=Xo.CANVAS_PADDING,this.paddingRight=Xo.CANVAS_PADDING,this.side=Hr.bottom,this.fixedAspectRatio=!1,this.scaleReferenceSize=384,this._scale=1,this._resizeController=new mi(this,{callback:e=>{if(!this.fixedAspectRatio)return;let t=e[0];if(!t)return;let o=t.contentRect.width;this._scale=fi({orientation:Lo.horizontal,containerMainAxisSize:o,scaleReferenceSize:this.scaleReferenceSize}),this.reportDimensions()}}),this.hasScale=!0,this.showLabels=!0,this.showMainTickmarkLabels=!1,this.hasBar=!1,this.scaleBackground=!1,this.barContainerStyle=void 0,this.barThickness=24,this.tickThickness=24,this.labelThickness=60,this.mainTickmarks=[],this.primaryTickmarkInterval=void 0,this.secondaryTickmarkInterval=void 0,this.tertiaryTickmarkInterval=void 0,this.scaleType=oo.regular,this.frameStyle=Mr.regular,this.borderRadiusPosition=void 0,this.instrumentMode=!1,this.borderRadius=void 0,this._borderRadiusResizeController=new mi(this,{callback:()=>{this.instrumentMode||this._refreshBorderRadiusFromCssVar()}}),this.priority=zt.regular,this.fillMode=Io.fill,this.fillMin=void 0,this.fillMax=void 0,this.value=void 0,this.state=to.active,this.advicePosition=Br.inner,this.advices=[],this.highlightCurrentValue=!1}render(){let e=this.fixedAspectRatio?this.scaleReferenceSize:this.width,t={orientation:Lo.horizontal,side:this.side,length:e,paddingStart:this.paddingLeft,paddingEnd:this.paddingRight,minValue:this.minValue,maxValue:this.maxValue,hasScale:this.hasScale,labels:this.showLabels,mainTickmarkLabels:this.showMainTickmarkLabels,hasBar:this.hasBar,scaleBackground:this.scaleBackground,barContainerStyle:this.barContainerStyle,barThickness:this.barThickness,tickThickness:this.tickThickness,labelThickness:this.labelThickness,borderRadius:this._getEffectiveBorderRadius(),mainTickmarks:this.mainTickmarks,primaryTickmarkInterval:this.primaryTickmarkInterval,secondaryTickmarkInterval:this.secondaryTickmarkInterval,tertiaryTickmarkInterval:this.tertiaryTickmarkInterval,scaleType:this.scaleType,frameStyle:this.frameStyle,borderRadiusPosition:this.borderRadiusPosition,priority:this.priority,setpointOverride:this.setpointOverride,fillMode:this.fillMode,fillMin:this.fillMin,fillMax:this.fillMax,value:this.value,setpoint:this.setpoint,newSetpoint:this.newSetpoint,atSetpoint:this.atSetpoint,autoAtSetpoint:this.autoAtSetpoint,autoAtSetpointDeadband:this.autoAtSetpointDeadband,setpointAtZeroDeadband:this.setpointAtZeroDeadband,animateSetpoint:this.animateSetpoint,departingNewSetpoint:this.departingNewSetpoint,state:this.state,touching:this.touching,advicePosition:this.advicePosition,advices:this.advices,fixedAspectRatio:this.fixedAspectRatio,instrumentMode:this.instrumentMode,highlightCurrentValue:this.highlightCurrentValue},o=ka(u1(t)),r=m1(t),i=_a({orientation:t.orientation,length:e},o),s=this.fixedAspectRatio?"xMidYMid meet":"none";return f`
      <svg
        width=${this.fixedAspectRatio?"100%":`${this.width}px`}
        height=${this.fixedAspectRatio?"100%":`${i.height}px`}
        viewBox="${i.x} ${i.y} ${i.width} ${i.height}"
        preserveAspectRatio="${s}"
        style="--scale: ${this.fixedAspectRatio?this._scale:1};"
        part="svg"
      >
        ${r.barContainer} ${r.barFill} ${r.scaleBackground}
        ${r.tickmarks} ${r.labels} ${r.adviceOverlays}
        ${r.currentValueDot} ${r.setpoint}
      </svg>
    `}updated(e){super.updated(e),e.has("scaleType")&&this._refreshBorderRadiusFromCssVar(),e.has("fixedAspectRatio")&&(this.fixedAspectRatio?(this._applyFixedAspectRatioStyles(),this._updateScaleFromCurrentSize()):(this._removeFixedAspectRatioStyles(),this._scale=1)),e.has("scaleReferenceSize")&&this.fixedAspectRatio&&this._updateScaleFromCurrentSize();let t=e.has("side")||e.has("showLabels")||e.has("showMainTickmarkLabels")||e.has("hasScale")||e.has("hasBar")||e.has("barThickness")||e.has("tickThickness")||e.has("labelThickness")||e.has("scaleType")||e.has("borderRadiusPosition")||e.has("borderRadius")||e.has("advices")||e.has("advicePosition")||this.setpointPresenceChanged(e);(!this.fixedAspectRatio||t)&&this.reportDimensions()}reportDimensions(){let e=an({hasBar:this.hasBar,barThickness:this.barThickness,borderRadius:this._getEffectiveBorderRadius(),scaleType:this.scaleType}),t=this.fixedAspectRatio?this.scaleReferenceSize:this.width,o=g1({orientation:Lo.horizontal,side:this.side,hasBar:this.hasBar,hasScale:this.hasScale,labels:this.showLabels,barThickness:e,tickThickness:this.tickThickness,labelThickness:this.labelThickness,length:t,scaleType:this.scaleType,advicePosition:this.advicePosition,hasAdvice:!!this.advices&&this.advices.length>0,hasSetpoint:this.setpoint!==void 0||this.newSetpoint!==void 0||this.departingNewSetpoint!==void 0}),r=this.fixedAspectRatio?{...o,thickness:Math.round(o.thickness*this._scale)}:o;this.dispatchEvent(new CustomEvent("scale-dimensions-changed",{detail:r,bubbles:!0,composed:!0}))}createRenderRoot(){return this}connectedCallback(){super.connectedCallback(),this.instrumentMode||(this._refreshBorderRadiusFromCssVar(),this._startBorderRadiusObserver()),this.fixedAspectRatio&&this._applyFixedAspectRatioStyles()}disconnectedCallback(){this._borderRadiusObserver?.disconnect(),this._borderRadiusObserver=void 0,super.disconnectedCallback()}_startBorderRadiusObserver(){this._borderRadiusObserver?.disconnect(),this._borderRadiusObserver=nn(this,()=>this._refreshBorderRadiusFromCssVar())}_applyFixedAspectRatioStyles(){this.style.display="block",this.style.width="100%",this.style.height="auto"}_removeFixedAspectRatioStyles(){this.style.display="",this.style.width="",this.style.height=""}_updateScaleFromCurrentSize(){requestAnimationFrame(()=>{let e=this.clientWidth;e>0&&(this._scale=fi({orientation:Lo.horizontal,containerMainAxisSize:e,scaleReferenceSize:this.scaleReferenceSize}),this.requestUpdate(),this.reportDimensions())})}_refreshBorderRadiusFromCssVar(){if(this.instrumentMode)return;let e=sn(this,this.scaleType);if(this._computedBorderRadius!==e&&(this._computedBorderRadius=e),this.fixedAspectRatio){let t=this.getBoundingClientRect();t.width>0&&(this._scale=fi({orientation:Lo.horizontal,containerMainAxisSize:t.width,scaleReferenceSize:this.scaleReferenceSize}),this.reportDimensions())}}_getEffectiveBorderRadius(){return this.instrumentMode?this.borderRadius!==void 0?this.borderRadius:this.scaleType===oo.condensed?4:8:this._computedBorderRadius??(this.scaleType===oo.condensed?4:8)}};Me([h({type:Number})],_e.prototype,"minValue",2);Me([h({type:Number})],_e.prototype,"maxValue",2);Me([h({type:Number})],_e.prototype,"width",2);Me([h({type:Number})],_e.prototype,"paddingLeft",2);Me([h({type:Number})],_e.prototype,"paddingRight",2);Me([h({type:String})],_e.prototype,"side",2);Me([h({type:Boolean})],_e.prototype,"fixedAspectRatio",2);Me([h({type:Number})],_e.prototype,"scaleReferenceSize",2);Me([ke()],_e.prototype,"_scale",2);Me([h({type:Boolean,attribute:!1})],_e.prototype,"hasScale",2);Me([h({type:Boolean,attribute:!1})],_e.prototype,"showLabels",2);Me([h({type:Boolean})],_e.prototype,"showMainTickmarkLabels",2);Me([h({type:Boolean})],_e.prototype,"hasBar",2);Me([h({type:Boolean})],_e.prototype,"scaleBackground",2);Me([h({type:String})],_e.prototype,"barContainerStyle",2);Me([h({type:Number})],_e.prototype,"barThickness",2);Me([h({type:Number})],_e.prototype,"tickThickness",2);Me([h({type:Number})],_e.prototype,"labelThickness",2);Me([h({type:Array,attribute:!1})],_e.prototype,"mainTickmarks",2);Me([h({type:Number})],_e.prototype,"primaryTickmarkInterval",2);Me([h({type:Number})],_e.prototype,"secondaryTickmarkInterval",2);Me([h({type:Number})],_e.prototype,"tertiaryTickmarkInterval",2);Me([h({type:String})],_e.prototype,"scaleType",2);Me([h({type:String})],_e.prototype,"frameStyle",2);Me([h({type:String})],_e.prototype,"borderRadiusPosition",2);Me([h({type:Boolean})],_e.prototype,"instrumentMode",2);Me([h({type:Number})],_e.prototype,"borderRadius",2);Me([ke()],_e.prototype,"_computedBorderRadius",2);Me([h({type:String})],_e.prototype,"priority",2);Me([h({type:String})],_e.prototype,"fillMode",2);Me([h({type:Number})],_e.prototype,"fillMin",2);Me([h({type:Number})],_e.prototype,"fillMax",2);Me([h({type:Number})],_e.prototype,"value",2);Me([h({type:String})],_e.prototype,"state",2);Me([h({type:String})],_e.prototype,"advicePosition",2);Me([h({type:Array,attribute:!1})],_e.prototype,"advices",2);Me([h({type:Boolean})],_e.prototype,"highlightCurrentValue",2);_e=Me([L("obc-bar-horizontal")],_e);var Cb=(e,t,o)=>{let r=new Map;for(let i=t;i<=o;i++)r.set(e[i],i);return r},mu=Ii(class extends Qr{constructor(e){if(super(e),e.type!==Bs.CHILD)throw Error("repeat() can only be used in text expressions")}dt(e,t,o){let r;o===void 0?o=t:t!==void 0&&(r=t);let i=[],s=[],n=0;for(let a of e)i[n]=r?r(a,n):n,s[n]=o(a,n),n++;return{values:s,keys:i}}render(e,t,o){return this.dt(e,t,o).values}update(e,[t,o,r]){let i=Om(e),{values:s,keys:n}=this.dt(t,o,r);if(!Array.isArray(i))return this.ut=n,s;let a=this.ut??=[],l=[],c,d,p=0,u=i.length-1,m=0,b=s.length-1;for(;p<=u&&m<=b;)if(i[p]===null)p++;else if(i[u]===null)u--;else if(a[p]===n[m])l[m]=gi(i[p],s[m]),p++,m++;else if(a[u]===n[b])l[b]=gi(i[u],s[b]),u--,b--;else if(a[p]===n[b])l[b]=gi(i[p],s[b]),cn(e,l[b+1],i[p]),p++,b--;else if(a[u]===n[m])l[m]=gi(i[u],s[m]),cn(e,i[p],i[u]),u--,m++;else if(c===void 0&&(c=Cb(n,m,b),d=Cb(a,p,u)),c.has(a[p]))if(c.has(a[u])){let C=d.get(n[m]),y=C!==void 0?i[C]:null;if(y===null){let k=cn(e,i[p]);gi(k,s[m]),l[m]=k}else l[m]=gi(y,s[m]),cn(e,i[p],y),i[C]=null;m++}else v1(i[u]),u--;else v1(i[p]),p++;for(;m<=b;){let C=cn(e,l[b+1]);gi(C,s[m]),l[m++]=C}for(;p<=u;){let C=i[p++];C!==null&&v1(C)}return this.ut=n,Pm(e,l),Yo}});function*xb(e,t){if(e!==void 0){let o=0;for(let r of e)yield t(r,o++)}}var Tk=Object.defineProperty,Dk=Object.getOwnPropertyDescriptor,bo=(e,t,o,r)=>{for(var i=r>1?void 0:r?Dk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Tk(t,o,i),i},gr=(e=>(e.Regular="regular",e.Button="button",e.Checkbox="checkbox",e.Tag="tag",e.HorizontalBar="horizontal-bar",e))(gr||{}),Ek='button, a[href], input, select, textarea, [role="button"], [role="link"], [role="checkbox"]';function qt(e,t){if(e.cssPart)return`${e.cssPart} ${t}`}var Xt=class extends S{constructor(){super(...arguments),this.data=[],this.columns=[],this.rowDivider=!1,this.narrowHeader=!1,this.showHeader=!0,this.striped=!1,this.selectable=!1,this.selectAllAriaLabel="Select all rows",this._sortByColumnIdx=void 0,this._sortDirection="asc",this._selectedRowIds=new Set,this._previousPositions=[],this._hasRenderedRows=!1}get hasHierarchy(){return this.data.some(e=>e.parentId!==void 0||(e.level??0)>0||e.expandable===!0)}sortWithinSiblings(e,t){let o=new Set(e.map(l=>l.id)),r=new Map,i=[];for(let l of e){let c=l.parentId;if(c!==void 0&&c!==l.id&&o.has(c)){let d=r.get(c)??[];d.push(l),r.set(c,d)}else i.push(l)}let s=[],n=new Set,a=l=>{for(let c of[...l].sort(t))n.has(c.id)||(n.add(c.id),s.push(c),a(r.get(c.id)??[]))};return a(i),a(e.filter(l=>!n.has(l.id))),s}get sortedData(){if(this._sortByColumnIdx===void 0)return this.data;let e=this.columns[this._sortByColumnIdx];if(e===void 0)return console.warn("Sort by column is undefined"),this.data;let t=this._sortDirection,o=(i,s)=>{let n=i[e.key],a=s[e.key];return t==="asc"?e.compareFunction(n,a,i,s):e.compareFunction(a,n,s,i)};if(this.hasHierarchy)return this.sortWithinSiblings(this.data,o);let r=[...this.data];return r.sort(o),r}_handleSortClick(e){if(!e.sortable)return;let t=this.columns.indexOf(e);t===this._sortByColumnIdx?this._sortDirection=this._sortDirection==="asc"?"desc":"asc":(this._sortByColumnIdx=t,this._sortDirection="asc")}_handleRowClick(e,t){let o=e.currentTarget;for(let r of e.composedPath()){if(r===o)break;if(r instanceof Element&&r.matches(Ek))return}this.dispatchEvent(new CustomEvent("row-click",{detail:{row:t}}))}_handleExpandToggle(e,t){e.expandable&&this.dispatchEvent(new CustomEvent("expand-toggle",{detail:{rowId:e.id,expanded:t}}))}_renderRowExpander(e){if(!this.hasHierarchy)return z;let t=e.level??0;return f`<span
      class="row-expander"
      style="--row-level: ${t}"
      aria-hidden="true"
    >
      ${e.expandable?f`<span
            class=${de({chevron:!0,expanded:e.expanded??!1})}
            @click=${o=>{o.preventDefault(),o.stopPropagation(),this._handleExpandToggle(e,!(e.expanded??!1))}}
          >
            <obi-chevron-right-google></obi-chevron-right-google>
          </span>`:z}
    </span>`}_focusFirstRow(){this.renderRoot.querySelector('button[role="row"].grid-row')?.focus()}_focusLeftHeaderItem(){this._focusHeaderByIndex(0)}_focusHeaderByIndex(e){let t=Array.from(this.renderRoot.querySelectorAll('.grid-header [role="columnheader"]'));if(t.length===0)return;let o=Math.max(0,Math.min(e,t.length-1)),r=t[o];(r.shadowRoot?.querySelector("button")??null??r).focus()}_handleHeaderKeyDown(e){let t=e.key;if(t==="ArrowDown"){this._focusFirstRow(),e.preventDefault(),e.stopPropagation();return}if(t!=="ArrowLeft"&&t!=="ArrowRight")return;let o=Array.from(this.renderRoot.querySelectorAll('.grid-header [role="columnheader"]'));if(o.length===0)return;let r=e.currentTarget,i=r?o.indexOf(r):-1;if(i===-1)return;let s=t==="ArrowRight"?Math.min(i+1,o.length-1):Math.max(i-1,0);s!==i&&(this._focusHeaderByIndex(s),e.preventDefault(),e.stopPropagation())}_handleRowKeyDown(e){let t=e.key;if(this.hasHierarchy&&(t==="ArrowRight"||t==="ArrowLeft")&&this._handleRowExpandKey(e,t)||t!=="ArrowDown"&&t!=="ArrowUp"&&t!=="Home"&&t!=="End")return;let o=e.currentTarget;if(!o)return;let r=Array.from(this.renderRoot.querySelectorAll('button[role="row"].grid-row')),i=r.indexOf(o);if(i===-1)return;let s=i;switch(t){case"ArrowDown":s=Math.min(i+1,r.length-1);break;case"ArrowUp":if(i===0){this._focusLeftHeaderItem(),e.preventDefault(),e.stopPropagation();return}s=Math.max(i-1,0);break;case"Home":s=0;break;case"End":s=r.length-1;break}s!==i?(r[s]?.focus(),e.preventDefault(),e.stopPropagation()):(t==="Home"||t==="End")&&(e.preventDefault(),e.stopPropagation())}_handleRowExpandKey(e,t){let r=e.currentTarget?.dataset.rowId,i=this.sortedData.find(n=>n.id===r);if(!i)return!1;let s=i.expanded??!1;if(t==="ArrowRight"&&i.expandable&&!s)this._handleExpandToggle(i,!0);else if(t==="ArrowLeft"&&i.expandable&&s)this._handleExpandToggle(i,!1);else if(t==="ArrowLeft"){let n=this.renderRoot.querySelector(`button[role="row"].grid-row[data-row-id="${CSS.escape(i.parentId??"")}"]`);if(!n)return!1;n.focus()}else return!1;return e.preventDefault(),e.stopPropagation(),!0}_getAllPositions(){let e=Array.from(this.renderRoot.querySelectorAll('button[role="row"].grid-row')),t=e[0];if(!t)return[];let r=t.getBoundingClientRect().height,i=getComputedStyle(t),n=parseFloat(i.height)/r;return e.map(a=>{let l=a.getBoundingClientRect();return{top:l.top*n,height:l.height*n,index:a.getAttribute("data-row-id")??"",element:a}})}_animateRowChanges(){let e=this._previousPositions,t=this._getAllPositions();t.forEach(o=>{let r=e.find(i=>i.index===o.index);r?o.element.style.transform=`translateY(${r.top-o.top}px)`:(o.element.style.transform=`translateY(-${o.height}px)`,o.element.style.opacity="0"),o.element.style.transition="none",o.element.offsetHeight,o.element.style.transition="transform 100ms ease-in-out, opacity 100ms ease-in-out",o.element.style.transform="translateY(0px)",o.element.style.opacity="1"}),this._previousPositions=t}willUpdate(e){if(e.has("defaultSelectedRowIds")&&this.selectedRowIds===void 0&&this._selectedRowIds.size===0&&(this._selectedRowIds=new Set(this.defaultSelectedRowIds??[])),e.has("selectedRowIds")&&this.selectedRowIds!==void 0&&(this._selectedRowIds=new Set(this.selectedRowIds)),e.has("data")){let t=new Set(this.data.map(o=>o.id));this._selectedRowIds.forEach(o=>{t.has(o)||this._selectedRowIds.delete(o)})}(e.has("data")||e.has("_sortByColumnIdx")||e.has("_sortDirection"))&&(this._hasRenderedRows?this._updatePositions():this.updateComplete.then(()=>{this._hasRenderedRows=!0}))}updated(e){e.has("columns")&&(this._sortByColumnIdx=this.columns.findIndex(t=>"sortDirection"in t&&t.sortDirection!==void 0),this._sortByColumnIdx===-1?(this._sortByColumnIdx=void 0,this._sortDirection="asc"):this._sortDirection=this.columns[this._sortByColumnIdx]?.sortDirection??"asc"),(e.has("data")||e.has("_sortByColumnIdx")||e.has("_sortDirection"))&&this._hasRenderedRows&&this._animateRowChanges()}_updatePositions(){let e=this._getAllPositions();this._previousPositions=e}render(){let e=this.selectable?[{label:"",key:"__selection__"},...this.columns]:this.columns,t=this.selectable?Math.max(0,e.length-1):e.length;return f`
      <div
        class=${de({"grid-container":!0,"has-selection-column":this.selectable})}
        part="grid"
        style="
          --grid-columns: ${e.length};
          --grid-columns-rest: ${t};
          --selection-column-width: var(--menu-navigation-components-table-item-touch-target-size);
        "
        role=${this.hasHierarchy?"treegrid":"table"}
      >
        ${this.showHeader?f`
              <div class="grid-header" role="row">
                ${e.map(o=>{let r=this.selectable&&o.key==="__selection__",i=e.indexOf(o)!==e.length-1,s=o.renderHeaderIcon?f`<span slot="leading-icon"
                        >${o.renderHeaderIcon()}</span
                      >`:z,n=this.columns.findIndex(d=>d.key===o.key),l="sortable"in o&&o.sortable&&this._sortByColumnIdx===n?this._sortDirection:"none",c=o.headerType??(this.narrowHeader?yd.Narrow:yd.Regular);return"sortable"in o&&o.sortable&&!r?f`<obc-table-header-item
                      role="columnheader"
                      class=${r?"selection-header":""}
                      .showDivider=${i}
                      ?hasLeadingIcon=${s!==z}
                      .sortDirection=${l}
                      .sortable=${!0}
                      type=${c}
                      @click=${()=>this._handleSortClick(o)}
                      @keydown=${this._handleHeaderKeyDown}
                      >${s}${o.label}</obc-table-header-item
                    > `:r?f`<div
                        role="columnheader"
                        class=${de({"selection-header":!0})}
                        tabindex="0"
                        @keydown=${this._handleHeaderKeyDown}
                      >
                        <obc-checkbox
                          .status=${this._getSelectionStatus()}
                          .disabled=${!1}
                          aria-label=${this.selectAllAriaLabel}
                          @click=${d=>{d.preventDefault(),d.stopPropagation()}}
                          @change=${()=>this._toggleAllSelection()}
                        ></obc-checkbox>
                      </div>`:f`<obc-table-header-item
                      role="columnheader"
                      class=${r?"selection-header":""}
                      .showDivider=${i}
                      ?hasLeadingIcon=${s!==z}
                      type=${c}
                      >${s}${o.label}</obc-table-header-item
                    >`})}
              </div>
              <div class="grid-header-divider"></div>
            `:z}
        <div
          class="grid-body"
          part="body"
          style="grid-template-rows: repeat(${this.sortedData.length}, min-content)"
        >
          ${mu(this.sortedData,o=>o.id,(o,r)=>{let i=this.rowDivider&&this.data.length-1!==r,s=this.striped&&r%2===1,n=(o.selected??!1)||this.selectable&&this._selectedRowIds.has(o.id),a=r>0?this.sortedData[r-1]:void 0,l=r<this.sortedData.length-1?this.sortedData[r+1]:void 0,c=a!==void 0&&((a.selected??!1)||this.selectable&&this._selectedRowIds.has(a.id)),d=l!==void 0&&((l.selected??!1)||this.selectable&&this._selectedRowIds.has(l.id));return f`
                <button
                  role="row"
                  class=${de({"grid-row":!0,selected:n,"selected-with-prev":n&&c,"selected-with-next":n&&d,striped:s})}
                  @click=${p=>this._handleRowClick(p,o)}
                  @keydown=${this._handleRowKeyDown}
                  data-row-id=${o.id}
                  style="grid-row: ${r+1}"
                  part="row"
                  aria-level=${Ce(this.hasHierarchy?(o.level??0)+1:void 0)}
                  aria-expanded=${Ce(o.expandable?o.expanded??!1:void 0)}
                >
                  ${xb(e,(p,u)=>{let m=u===(this.selectable?1:0)?this._renderRowExpander(o):z;if(this.selectable&&p.key==="__selection__"){let C=this._selectedRowIds.has(o.id);return f`<div
                        class="grid-cell checkbox align-center selection"
                        role="cell"
                      >
                        <obc-checkbox
                          .status=${C?fr.checked:fr.unchecked}
                          .disabled=${!1}
                          aria-label=${`Select row ${o.id}`}
                          @click=${y=>{y.preventDefault(),y.stopPropagation()}}
                          @change=${()=>this._toggleRowSelection(o.id)}
                        ></obc-checkbox>
                      </div>`}let b=o[p.key];return b===void 0?f`<div class="grid-cell" role="cell">
                        ${m}
                      </div>`:p.renderCell?f`<div
                        class="grid-cell ${p.dividerRight?"divider-right":""}"
                        role="cell"
                        part=${Ce(b.cssPart)}
                      >
                        ${m}${p.renderCell(b,o,o.id)}
                      </div>`:this._renderCell(b,o,p,m)})}
                  ${i?f`<div class="grid-row-divider"></div>`:z}
                </button>
              `})}
          ${mu(e,o=>o.key,(o,r)=>o.dividerRight?f`<div
                    class="grid-column-divider"
                    style="grid-column: ${r+1}; grid-row: 1/${this.sortedData.length+1}"
                  ></div>`:z)}
        </div>
      </div>
    `}getAllVisibleRows(){let e=Array.from(this.renderRoot.querySelectorAll('button[role="row"].grid-row')),t=this.renderRoot.querySelector(".grid-body")?.getBoundingClientRect();if(!t)return[];let o=t.top,r=t.height,i=o+r;return e.filter(s=>s.checkVisibility()).filter(s=>s.getBoundingClientRect().top>=o&&s.getBoundingClientRect().bottom<=i).map(s=>s.getAttribute("data-row-id")).filter(s=>s!==null)}_handleCellButtonClick(e,t,o){e.preventDefault(),e.stopPropagation();let r=new CustomEvent("cell-button-click",{detail:{rowId:t.id,columnKey:o}});this.dispatchEvent(r)}_handleCellTagClick(e,t,o,r){e.preventDefault(),e.stopPropagation();let i=new CustomEvent("cell-tag-click",{detail:{rowId:t.id,columnKey:o,tagId:r}});this.dispatchEvent(i)}_handleCellCheckboxChange(e,t,o){e.preventDefault(),e.stopPropagation();let r=new CustomEvent("cell-checkbox-change",{detail:{rowId:t.id,columnKey:o,status:e.detail.status,disabled:e.detail.disabled}});this.dispatchEvent(r)}_getSelectableRowIds(){return this.data.map(e=>e.id)}_getSelectionStatus(){let e=this._getSelectableRowIds();if(e.length===0)return fr.unchecked;let t=e.filter(o=>this._selectedRowIds.has(o)).length;return t===0?fr.unchecked:t===e.length?fr.checked:fr.mixed}_emitSelectionChange(e,t){let o=this.data.filter(i=>e.includes(i.id)),r=new CustomEvent("selection-change",{detail:{selectedRowIds:e,selectedRows:o,source:t}});this.dispatchEvent(r)}_applySelectionChange(e,t){let o=Array.from(e);this._emitSelectionChange(o,t),this.selectedRowIds===void 0&&(this._selectedRowIds=e,this.requestUpdate())}_toggleRowSelection(e){let t=new Set(this._selectedRowIds);t.has(e)?t.delete(e):t.add(e),this._applySelectionChange(t,"row")}_toggleAllSelection(){let e=this._getSelectableRowIds(),o=this._getSelectionStatus()===fr.checked?new Set:new Set(e);this._applySelectionChange(o,"header")}_renderCell(e,t,o,r=z){if(e.type==="regular")return f`<div
        class=${de({"grid-cell":!0,regular:!0,neutral:e.neutral??!1,"large-icon":e.largeIcon??!1,"no-wrap":e.noWrap??!1,[`align-${e.align??"left"}`]:!0,"divider-right":o.dividerRight??!1,vertical:e.vertical??!1})}
        role="cell"
        part=${Ce(qt(e,"cell"))}
      >
        ${r}${e.icon3?f`<span class="icon" part=${Ce(qt(e,"icon3"))}
              >${e.icon3}</span
            >`:z}
        ${e.icon2?f`<span class="icon" part=${Ce(qt(e,"icon2"))}
              >${e.icon2}</span
            >`:z}
        ${e.icon?f`<span class="icon" part=${Ce(qt(e,"icon"))}
              >${e.icon}</span
            >`:z}
        ${e.title?f`<span class="title" part=${Ce(qt(e,"title"))}
              >${e.title}</span
            >`:z}
        ${e.text?f`<span part=${Ce(qt(e,"text"))}
              >${e.text}</span
            >`:z}
      </div>`;if(e.type==="button")return f`<div
        class="grid-cell button ${o.dividerRight?"divider-right":""}"
        role="cell"
      >
        ${r}
        <obc-button
          variant="normal"
          fullWidth
          .disabled=${e.disabled??!1}
          ?showLeadingIcon=${e.icon!==void 0}
          part=${Ce(qt(e,"button"))}
          @click=${i=>this._handleCellButtonClick(i,t,o.key)}
        >
          ${e.icon?f`<span
                slot="leading-icon"
                part=${Ce(qt(e,"icon"))}
                >${e.icon}</span
              >`:z}
          ${e.text?f`<span part=${Ce(qt(e,"text"))}
                >${e.text}</span
              >`:z}
        </obc-button>
      </div>`;if(e.type==="checkbox"){let s=(e.label??e.text??"").trim()||o.label?.trim()||"Checkbox";return f`<div
        class=${de({"grid-cell":!0,checkbox:!0,[`align-${e.align??"center"}`]:!0,"divider-right":o.dividerRight??!1})}
        role="cell"
        part=${Ce(qt(e,"cell"))}
      >
        ${r}
        <obc-checkbox
          .status=${e.status??fr.unchecked}
          .disabled=${e.disabled??!1}
          aria-describedby=${Ce(e.ariaDescribedBy)}
          aria-label=${s}
          part=${Ce(qt(e,"checkbox"))}
          @click=${n=>{n.preventDefault(),n.stopPropagation()}}
          @change=${n=>this._handleCellCheckboxChange(n,t,o.key)}
        ></obc-checkbox>
      </div>`}else if(e.type==="tag"){let i=e.tags??(e.tag?[e.tag]:void 0)??[{id:e.tagId??"tag",label:e.label??e.text??"Label",color:e.color,hasIcon:e.hasIcon,icon:e.icon}],s=e.wrap??e.tags!==void 0,n=e.tags?2:void 0,a=(e.maxTags??n)!==void 0?Math.max(0,Math.floor(e.maxTags??n??0)):void 0,l=a!==void 0?i.slice(0,a):i,c=a!==void 0?Math.max(0,i.length-a):0,d=e.overflowLabel??`+${c.toString()}`;return f`<div
        class=${de({"grid-cell":!0,tags:i.length>1,wrap:s,[`align-${e.align??"left"}`]:!0,"divider-right":o.dividerRight??!1})}
        role="cell"
        part=${Ce(qt(e,"cell"))}
      >
        ${r}${l.map(p=>{let u=p.hasIcon??p.icon!==void 0;return f`<obc-tag
            .label=${p.label}
            color=${p.color??gu.gray}
            ?hasIcon=${u}
            part=${Ce([qt(e,"tag"),p.cssPart].filter(Boolean).join(" ")||void 0)}
            @click=${m=>this._handleCellTagClick(m,t,o.key,p.id)}
          >
            ${u&&p.icon?p.icon:z}
          </obc-tag>`})}
        ${c>0?f`<span
              class="tag-overflow"
              part=${Ce(qt(e,"tag-overflow"))}
              >${d}</span
            >`:z}
      </div>`}else if(e.type==="horizontal-bar"){let i=e.hasBar??!0,s=e.hasScale??!1,n=!(e.hideLabels??!0),a=e.fixedAspectRatio??!0;return f`<div
        class=${de({"grid-cell":!0,"horizontal-bar":!0,[`align-${e.align??"left"}`]:!0,"divider-right":o.dividerRight??!1})}
        role="cell"
        part=${Ce(qt(e,"cell"))}
      >
        ${r}
        <obc-bar-horizontal
          .minValue=${e.minValue??0}
          .maxValue=${e.maxValue??100}
          .value=${e.value}
          .setpoint=${e.setpoint}
          .hasBar=${i}
          .hasScale=${s}
          .showLabels=${n}
          .priority=${e.priority??zt.regular}
          .fillMode=${e.fillMode??Io.fill}
          .fillMin=${e.fillMin}
          .fillMax=${e.fillMax}
          .barThickness=${e.barThickness??24}
          .scaleType=${e.scaleType??oo.regular}
          .frameStyle=${e.frameStyle??Mr.regular}
          .side=${e.side??Hr.bottom}
          .state=${e.state??to.active}
          .fixedAspectRatio=${a}
          .scaleReferenceSize=${e.scaleReferenceSize??384}
          part=${Ce(qt(e,"bar"))}
        ></obc-bar-horizontal>
      </div>`}else return z}};Xt.styles=ne(gb);bo([h({type:Array})],Xt.prototype,"data",2);bo([h({type:Array})],Xt.prototype,"columns",2);bo([h({type:Boolean})],Xt.prototype,"rowDivider",2);bo([h({type:Boolean})],Xt.prototype,"narrowHeader",2);bo([h({type:Boolean,attribute:!1})],Xt.prototype,"showHeader",2);bo([h({type:Boolean})],Xt.prototype,"striped",2);bo([h({type:Boolean})],Xt.prototype,"selectable",2);bo([h({type:Array})],Xt.prototype,"selectedRowIds",2);bo([h({type:Array})],Xt.prototype,"defaultSelectedRowIds",2);bo([h({type:String})],Xt.prototype,"selectAllAriaLabel",2);bo([ke()],Xt.prototype,"_sortByColumnIdx",2);bo([ke()],Xt.prototype,"_sortDirection",2);bo([ke()],Xt.prototype,"_selectedRowIds",2);Xt=bo([L("obc-table")],Xt);var _b=M`* {
  -webkit-tap-highlight-color: transparent;
}

:host {
  display: block;
  /* On the host, not .wrapper: the mixin nests its rules as \`:host ::-webkit-scrollbar-*\`,
     which is what reaches the wrapper's own scrollbar; --offset inherits down to it. */
  --offset: calc(
    (
        var(--obc-scrollbar-touch-target-size) -
          var(--obc-scrollbar-visual-target-size)
      ) /
      2
  );
}

:host ::-webkit-scrollbar {
    width: var(--obc-scrollbar-touch-target-size);
    height: var(--obc-scrollbar-touch-target-size);
  }

:host ::-webkit-scrollbar-track-piece {
    border: var(--offset) solid transparent;
    border-radius: 9999px;
    background-color: var(--indent-enabled-background-color);
    margin-top: calc(-1 * var(--offset));
    margin-bottom: calc(-1 * var(--offset));
    box-sizing: border-box;
    background-clip: content-box;
  }

:host ::-webkit-scrollbar-track-piece:vertical:start {
    border-bottom-width: 0;
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
  }

:host ::-webkit-scrollbar-track-piece:vertical:end {
    border-top-width: 0;
    border-top-left-radius: 0;
    border-top-right-radius: 0;
  }

:host ::-webkit-scrollbar-track-piece:hover {
    outline-color: var(--indent-hover-border-color);
    background-color: var(--indent-hover-background-color);
  }

:host ::-webkit-scrollbar-track-piece:active {
    outline-color: var(--indent-pressed-border-color);
    background-color: var(--indent-pressed-background-color);
  }

:host ::-webkit-scrollbar-thumb {
    border: calc(var(--offset) + 1px) solid transparent;
    outline: 1px solid var(--obc-scrollbar-thumb-border-color);
    outline-offset: calc(-1 * var(--offset) - 1px);
    background-clip: content-box;
    border-radius: 9999px;
    background-color: var(--obc-scrollbar-thumb-background-color);
    min-height: calc(var(--obc-scrollbar-touch-target-size) * 1.5);
  }

:host ::-webkit-scrollbar-thumb:hover {
    outline-color: var(--obc-scrollbar-thumb-hover-border-color);
    background-color: var(--obc-scrollbar-thumb-hover-background-color);
  }

:host ::-webkit-scrollbar-thumb:active {
    outline-color: var(--obc-scrollbar-thumb-active-border-color);
    background-color: var(--obc-scrollbar-thumb-active-background-color);
  }

:host ::-webkit-scrollbar-button:start:decrement,:host ::-webkit-scrollbar-button:end:increment {
    display: var(--obc-scrollbar-button-display);
    height: var(--obc-scrollbar-button-size);
    width: var(--obc-scrollbar-button-size);
    box-sizing: border-box;
    background-clip: content-box;
    background-repeat: no-repeat;
    background-position: center;
    border: var(--obc-scrollbar-button-margin) solid transparent;
    border-radius: var(--obc-scrollbar-button-radius);
    background-clip: padding-box;
    background-color: var(--flat-enabled-background-color);
  }

:host ::-webkit-scrollbar-button:start:decrement:hover,:host ::-webkit-scrollbar-button:end:increment:hover {
    background-color: var(--flat-hover-background-color);
  }

:host ::-webkit-scrollbar-button:start:decrement:active,:host ::-webkit-scrollbar-button:end:increment:active {
    background-color: var(--flat-pressed-background-color);
  }

:host ::-webkit-scrollbar-button:vertical:start:decrement {
    background-image: var(--icon-02-chevron-up);
  }

:host ::-webkit-scrollbar-button:vertical:end:increment {
    background-image: var(--icon-02-chevron-down);
  }

.wrapper {
  overflow-x: var(--obc-scrollbar-overflow-x, auto);
  overflow-y: auto;
  height: 100%;
}

/* Transparent-track mode: native scrollbar hidden, custom overlay thumb shown */

.transparent-track {
  scrollbar-width: none;
}

.transparent-track::-webkit-scrollbar {
  display: none;
}

:host {
  position: relative;
}

.overlay-track {
  --_pad: var(--menu-navigation-components-scroll-bar-padding, 4px);
  --_radius: var(--menu-navigation-components-scroll-bar-border-radius, 1000px);

  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: calc(var(--_pad) * 2 + 4px);
  pointer-events: none;
  padding: var(--_pad);
  box-sizing: border-box;
}

.overlay-track::before {
  content: "";
  position: absolute;
  inset: var(--_pad);
  background: var(--border-outline-color, #ddd);
  border-radius: var(--_radius);
}

.overlay-thumb {
  position: absolute;
  left: var(--_pad);
  right: var(--_pad);
  background: var(--element-symbol-color, #8e8e8e);
  border-radius: var(--_radius);
  min-height: 24px;
}
`;var Rk=Object.defineProperty,zk=Object.getOwnPropertyDescriptor,Ha=(e,t,o,r)=>{for(var i=r>1?void 0:r?zk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Rk(t,o,i),i},ms=class extends S{constructor(){super(...arguments),this.transparentTrack=!1,this._thumbTop=0,this._thumbHeight=0,this._showOverlayThumb=!1,this._resizeObserver=null,this._scrollHandler=null,this._wrapper=null}render(){return f`
      <div
        class=${de({wrapper:!0,"transparent-track":this.transparentTrack})}
      >
        <slot></slot>
      </div>
      ${this.transparentTrack&&this._showOverlayThumb?f`<div class="overlay-track">
            <div
              class="overlay-thumb"
              style="top:${this._thumbTop}%;height:${this._thumbHeight}%"
            ></div>
          </div>`:z}
    `}firstUpdated(){this._wrapper=this.shadowRoot?.querySelector(".wrapper")??null,this._wrapper&&(this._resizeObserver=new ResizeObserver(()=>{this._checkOverflow(),this._updateOverlayThumb()}),this._resizeObserver.observe(this._wrapper),this._wrapper.querySelector("slot")?.addEventListener("slotchange",()=>{this._checkOverflow(),this._updateOverlayThumb()}),this.transparentTrack&&(this._scrollHandler=()=>this._updateOverlayThumb(),this._wrapper.addEventListener("scroll",this._scrollHandler,{passive:!0})))}disconnectedCallback(){super.disconnectedCallback(),this._resizeObserver?.disconnect(),this._resizeObserver=null,this._scrollHandler&&this._wrapper&&(this._wrapper.removeEventListener("scroll",this._scrollHandler),this._scrollHandler=null),this._wrapper=null}_updateOverlayThumb(){if(!this.transparentTrack||!this._wrapper)return;let{scrollHeight:e,clientHeight:t,scrollTop:o}=this._wrapper;if(e<=t){this._showOverlayThumb=!1;return}this._showOverlayThumb=!0;let r=t,i=parseFloat(getComputedStyle(this._wrapper).getPropertyValue("--menu-navigation-components-scroll-bar-padding"))||4,s=r-i*2,n=t/e*s,a=i+o/e*s;this._thumbTop=a/r*100,this._thumbHeight=n/r*100}_checkOverflow(){if(!this._wrapper)return;let e=this._wrapper.scrollHeight>this._wrapper.clientHeight;this.toggleAttribute("overflowing",e)}scrollToBottom(){if(!this._wrapper)throw new Error("Wrapper not found");this._wrapper.scrollTop=this._wrapper.scrollHeight}};ms.styles=ne(_b);Ha([h({type:Boolean,attribute:"transparent-track"})],ms.prototype,"transparentTrack",2);Ha([ke()],ms.prototype,"_thumbTop",2);Ha([ke()],ms.prototype,"_thumbHeight",2);Ha([ke()],ms.prototype,"_showOverlayThumb",2);ms=Ha([L("obc-scrollbar")],ms);var Hk=Object.defineProperty,Bk=Object.getOwnPropertyDescriptor,vs=(e,t,o,r)=>{for(var i=r>1?void 0:r?Bk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Hk(t,o,i),i};function vu(e){if(e==="all")return{name:"all",title:Ge("All"),emptyTitle:Ge("No active alerts"),emptyIcon:f`<obi-alerts></obi-alerts>`,filter:t=>!Sl(t)&&Cr(t)};if(e==="unacked")return{name:"unacked",title:Ge("Unacked"),emptyTitle:Ge("No unacknowledged alerts"),emptyIcon:f`<obi-unacknowledged></obi-unacknowledged>`,filter:t=>!Jr(t)&&Cr(t)&&!ih(t.type)&&!Sl(t)};if(e==="shelved")return{name:"shelved",title:Ge("Shelved"),emptyTitle:Ge("No shelved alerts"),emptyIcon:f`<obi-alerts-shelf></obi-alerts-shelf>`,filter:t=>Sl(t)};if(e==="blocked")return{name:"blocked",title:Ge("Blocked"),emptyTitle:Ge("No blocked alerts"),emptyIcon:f`<obi-alerts-active></obi-alerts-active>`,filter:t=>T2(t)};if(e==="rectified")return{name:"rectified",title:Ge("Rectified"),emptyTitle:Ge("No rectified alerts"),emptyIcon:f`<obi-alarm-rectified-iec></obi-alarm-rectified-iec>`,filter:t=>!Cr(t)};throw new Error("Invalid selected mode")}function kb(e){return t=>!Jr(t)&&!t.noAck&&!ih(t.type)&&e(t)}var jr=class extends S{constructor(){super(...arguments),this.selectedMode="all",this.alerts=[],this.showTime=!1,this.timeFormatter=e=>e.toLocaleTimeString(void 0,{hour12:!1}),this.small=!1}getVisibleAlerts(){return this.alertList.getAllVisibleRows().map(t=>this.alerts.find(o=>o.id===t)).filter(t=>t!==void 0)}onRowClick(e){let t=this.alerts.find(o=>o.id===e.detail.row.id);t&&this.dispatchEvent(new CustomEvent("row-click",{detail:{alert:t}}))}onCellButtonClick(e){let t=this.alerts.find(o=>o.id===e.detail.rowId);t&&this.dispatchEvent(new CustomEvent("ack-click",{detail:{alert:t},bubbles:!1}))}get columns(){if(this.small){let e=[{label:"Status",key:"status",sortDirection:"desc",sortable:!0,compareFunction:(t,o,r,i)=>{let s=this.alerts.find(a=>a.id===r.id),n=this.alerts.find(a=>a.id===i.id);return s&&n?oh(s,n):0}}];return this.showTime&&e.push({label:"Activated",key:"time"}),e.push({label:"ACK-status",key:"action"}),e}else{let e=[{label:"Status",key:"status",sortDirection:"desc",sortable:!0,compareFunction:(t,o,r,i)=>{let s=this.alerts.find(a=>a.id===r.id),n=this.alerts.find(a=>a.id===i.id);return s&&n?oh(s,n):0}},{label:"ACK-status",key:"action",dividerRight:!0}];return this.showTime&&e.push({label:"Activated",key:"time",sortable:!0,compareFunction:(t,o,r,i)=>{let s=this.alerts.find(a=>a.id===r.id),n=this.alerts.find(a=>a.id===i.id);if(s&&n){let a=new Date(s.time),l=new Date(n.time);return a.getTime()-l.getTime()}return 0}}),e.push({label:"Tag ID",key:"tagId",sortable:!0,compareFunction:(t,o)=>{let r=t?.type===gr.Regular?String(t.text??""):"",i=o?.type===gr.Regular?String(o.text??""):"";return r.localeCompare(i)}}),e}}get metadata(){return vu(this.selectedMode)}get filteredAlerts(){return this.alerts.filter(this.metadata.filter)}render(){let e=this.metadata,t=this.filteredAlerts.map(o=>{let r={type:gr.Regular};if(!Jr(o)&&Cr(o)&&E2(o.type))if(o.noAck){let a=H2(o.type)?f`<obi-alarm-noack-iec usecsscolor></obi-alarm-noack-iec>`:f`<obi-warning-noack-iec usecsscolor></obi-warning-noack-iec>`;r={type:gr.Regular,largeIcon:!0,icon:a,align:"center"}}else r={type:gr.Button,text:Ge("ACK")};let i={type:gr.Regular,largeIcon:!0,text:o.text,title:o.source,noWrap:!0,icon:f`<obc-alert-icon
          .type=${o.type}
          .acknowledged=${Jr(o)}
          .active=${Cr(o)}
        ></obc-alert-icon>`},s=this.showTime?{type:gr.Regular,text:this.timeFormatter(o.time),align:"center",neutral:!0}:void 0,n=this.small?void 0:{type:gr.Regular,text:"#"+o.id,align:"right"};return{id:o.id,status:i,time:s,action:r,tagId:n}});return f`
      <div class="wrapper ${this.small?"small":""}">
        ${t.length>0?f` <obc-table
                class="alert-list"
                .data=${t}
                .columns=${this.columns}
                .striped=${!0}
                .showHeader=${!this.small}
                @row-click=${this.onRowClick}
                @cell-button-click=${this.onCellButtonClick}
              ></obc-table>
              <div class="spacer"></div>`:f` <div class="empty-list">
              <div class="icon">${e.emptyIcon}</div>
              <div class="empty-title">${e.emptyTitle}</div>
            </div>`}
      </div>
    `}};jr.styles=ne(Vv);vs([h({type:String})],jr.prototype,"selectedMode",2);vs([h({type:Array})],jr.prototype,"alerts",2);vs([h({type:Boolean})],jr.prototype,"showTime",2);vs([h({attribute:!1})],jr.prototype,"timeFormatter",2);vs([h({type:Boolean})],jr.prototype,"small",2);vs([at("obc-table")],jr.prototype,"alertList",2);jr=vs([L("obc-alert-list-details")],jr);var Lb=M`* {
  -webkit-tap-highlight-color: transparent;
}

.wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
}

.alert-list {
  min-height: 0;
  flex-grow: 1;
}

.action {
  display: flex;
  height: var(--app-components-tool-bar-touch-target-size);
  padding: 0px var(--app-components-alert-toolbar-margin-horizontal);
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  flex-grow: 0;
  border-top: 1px solid var(--border-divider-color);
  background: var(--container-section-color);
  box-shadow: var(--shadow-flat);
}

.action .btn-group {
    display: flex;
  }
`;var Sb=M`* {
  -webkit-tap-highlight-color: transparent;
}

* {
  box-sizing: border-box;
}

:host {
  display: block;
}

.alert-list {
  height: 100%;
}

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: var(--app-components-alert-menu-button-spacing);
}

.empty-list .icon {
    height: 96px;
    width: 96px;
  }

.empty-list .empty-title {
    color: var(--element-active-color);
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-body-active-font-weight);
    font-size: var(--global-typography-ui-body-active-font-size);
    line-height: var(--global-typography-ui-body-active-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  }

.empty-list .empty-description {
    color: var(--element-neutral-color);
    font-family: var(--global-typography-font-family);
    font-weight: var(--global-typography-ui-body-font-weight);
    font-size: var(--global-typography-ui-body-font-size);
    line-height: var(--global-typography-ui-body-line-height);
    font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
    max-width: 344px;
    text-align: center;
  }

::slotted(*) {
  display: block;
  will-change: transform;
}
`;var Ik=Object.defineProperty,Zk=Object.getOwnPropertyDescriptor,Ba=(e,t,o,r)=>{for(var i=r>1?void 0:r?Zk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Ik(t,o,i),i},bs=class extends S{constructor(){super(...arguments),this.filter=()=>!0,this.oldElementTop=new Map,this.mutationObserver=null,this.intersectionObserver=null,this.hasRenderedPanel=!1,this._empty=!1}firstUpdated(){this.updateEmpty(),this.setupMutationObserver()}connectedCallback(){super.connectedCallback();let e=new IntersectionObserver(t=>{t[0].intersectionRatio===0&&(this.hasRenderedPanel=!1)});e.observe(this),this.intersectionObserver=e,this.setupMutationObserver()}disconnectedCallback(){this.mutationObserver&&(this.mutationObserver.disconnect(),this.mutationObserver=null),this.intersectionObserver&&(this.intersectionObserver.disconnect(),this.intersectionObserver=null)}willUpdate(e){e.has("filter")&&(this.updateEmpty(),this.updateOldElementTop())}updateEmpty(){this._empty=this.getAlertItems().length===0}getAlertItems(){return this.alertItems.filter(this.filter)}updateOldElementTop(){let e=this.getAlertItems();if(e.length===0)return;let r=e[0].getBoundingClientRect().top;this.oldElementTop.clear(),e.forEach(i=>{let s=i.getBoundingClientRect();s.height!==0&&(this.oldElementTop.set(i,r),r+=s.height)})}setupMutationObserver(){this.mutationObserver&&(this.mutationObserver.disconnect(),this.mutationObserver=null),this.mutationObserver=new MutationObserver(()=>{this.handleElementsChange()}),this.alertItems.forEach(t=>{this.mutationObserver?.observe(t,{attributes:!0,attributeFilter:["status","shelved"]})})}handleSlotChange(){this.handleElementsChange(),this.setupMutationObserver()}handleElementsChange(){if(this.mutationObserver?.takeRecords(),this.updateEmpty(),!this.checkVisibility())return;let e=this.getAlertItems(),t=new Map(this.oldElementTop);requestAnimationFrame(()=>{this.updateOldElementTop();let o=!1;e.forEach(r=>{let i=r.getBoundingClientRect(),s=t.get(r);if(s===void 0){r.animateIntro=this.hasRenderedPanel,o=!0,setTimeout(()=>{r.animateIntro=!1},101);return}let n=s-i.top;n!==0&&(r.style.transform=`translateY(${n}px)`,r.style.transition="none",r.offsetHeight,r.style.transition="transform 100ms ease-in-out",r.style.transform="translateY(0px)")}),this.hasRenderedPanel=!0,o&&setTimeout(()=>{this.updateOldElementTop()},101)})}getVisibleElements(){let e=this.scrollbar.getBoundingClientRect();return this.getAlertItems().map((o,r)=>({element:o,index:r})).filter(({element:o})=>{let r=window.getComputedStyle(o);if(r.display==="none"||r.visibility==="hidden")return!1;let i=o.getBoundingClientRect();return!(i.top<e.top||i.bottom>e.bottom)})}render(){return f` <obc-scrollbar class="alert-list" id="scrollbar">
      <slot @slotchange=${this.handleSlotChange}></slot>
      ${this._empty?f` <div class="empty-list">
            <div class="icon">
              <slot name="empty-icon"></slot>
            </div>
            <div class="empty-title">
              <slot name="empty-title"></slot>
            </div>
            <div class="empty-description">
              <slot name="empty-description"></slot>
            </div>
          </div>`:z}
    </obc-scrollbar>`}};bs.styles=ne(Sb);Ba([h({attribute:!1})],bs.prototype,"filter",2);Ba([ke()],bs.prototype,"_empty",2);Ba([Bi({flatten:!0})],bs.prototype,"alertItems",2);Ba([at("#scrollbar",!0)],bs.prototype,"scrollbar",2);bs=Ba([L("obc-alert-list")],bs);var Mb=M`* {
  -webkit-tap-highlight-color: transparent;
}

.wrapper {
  position: relative;
  user-select: none;
  padding: 0;
  background: transparent;
  width: fit-content;
  height: var(--ui-components-button-touch-target-size);
  appearance: none;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--global-typography-font-family);
  font-weight: var(--global-typography-ui-button-font-weight);
  font-size: var(--global-typography-ui-button-font-size);
  line-height: var(--global-typography-ui-button-line-height);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
}

.wrapper.full-width {
    width: 100%;
  }

.wrapper.full-width .visible-wrapper {
      width: 100%;
      justify-content: space-between;
    }

.wrapper .visible-wrapper {
    height: var(--ui-components-button-visual-size);
    border-radius: var(--ui-components-button-border-radius-top-left)
      var(--ui-components-button-border-radius-top-right)
      var(--ui-components-button-border-radius-bottom-right)
      var(--ui-components-button-border-radius-bottom-left);
    box-sizing: border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-left: calc(var(--ui-components-button-padding-horizontal) * 2);
    padding-right: var(--ui-components-button-padding-horizontal);
  }

.wrapper .icon-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: var(--global-size-spacing-icon-icon-size-regular);
    width: var(--global-size-spacing-icon-icon-size-regular);
  }

.wrapper .icon {
    height: var(--global-size-spacing-icon-icon-size-regular);
    width: var(--global-size-spacing-icon-icon-size-regular);
  }

.wrapper.disabled .icon-container {
    color: var(--on-normal-disabled-color);
  }

.wrapper.disabled .icon {
    color: var(--on-normal-disabled-color);
  }

.wrapper .label {
    padding-left: var(--ui-components-button-label-spacing);
    padding-right: var(--ui-components-button-label-spacing);
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }

.wrapper {
  cursor: pointer;
}

.wrapper:focus {
  outline: none;
}

.wrapper .visible-wrapper {
  border-color: var(--normal-enabled-border-color);
  background-color: var(--normal-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--normal-enabled-border-color);
  --base-background-color: var(--normal-enabled-background-color);
}

.wrapper.activated .visible-wrapper {
  border-color: var(--normal-activated-border-color);
  background-color: var(--normal-activated-background-color);
  --base-border-color: var(--normal-activated-border-color);
  --base-background-color: var(--normal-activated-background-color);
}

@media (hover:hover) {

.wrapper:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--normal-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--normal-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper:active .visible-wrapper {
  border-color: var(--normal-pressed-border-color);
  background-color: var(--normal-pressed-background-color);
}

.wrapper:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper:disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.wrapper.disabled .visible-wrapper {
  border-color: var(--normal-disabled-border-color);
  background-color: var(--normal-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-normal-disabled-color) !important;
}

.wrapper:disabled {
  cursor: not-allowed;
}

.wrapper.disabled {
  cursor: not-allowed;
}

.wrapper {
  color: var(--on-normal-active-color);
}

.wrapper .icon {
    color: var(--on-normal-neutral-color);
  }

.wrapper:disabled .icon {
    color: var(--on-normal-disabled-color);
  }

.wrapper select {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    appearance: none;
    appearance: base-select;
    opacity: 0;
  }

.wrapper:has(select:focus-visible) .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

::picker(select) {
  appearance: base-select;
  border: none;
  min-width: var(--ui-components-context-menu-menu-width);
  border-radius: 12px;
  background: var(--container-global-color);
  box-shadow: var(--shadow-floating);
  padding: var(--ui-components-context-menu-margin-vertical)
    var(--ui-components-context-menu-margin-horizontal);

  overflow-y: auto;
}

.wrapper.open-top select::picker(select) {
  position-area: block-start span-inline-end;
}

option {
  height: var(--menu-navigation-components-navigation-item-touch-target-size);
  min-height: var(
    --menu-navigation-components-navigation-item-touch-target-size
  );
  padding: 0px
    var(--menu-navigation-components-navigation-item-padding-horizontal);
  border-radius: var(
    --menu-navigation-components-navigation-item-border-radius
  );
}

option {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

option:focus {
  outline: none;
}

option.activated {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

option:hover {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

option:active {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

option:focus-visible {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

option:disabled {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

option.disabled {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

option {
  font-family: var(--global-typography-font-family);
  font-weight: var(--global-typography-ui-body-font-weight);
  font-size: var(--global-typography-ui-body-font-size);
  line-height: var(--global-typography-ui-body-line-height);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
  color: var(--on-flat-neutral-color);
}

option:checked {
  border-color: var(--amplified-enabled-border-color);
  background-color: var(--amplified-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--amplified-enabled-border-color);
  --base-background-color: var(--amplified-enabled-background-color);
}

option:checked:focus {
  outline: none;
}

option.activated:checked {
  border-color: var(--amplified-activated-border-color);
  background-color: var(--amplified-activated-background-color);
  --base-border-color: var(--amplified-activated-border-color);
  --base-background-color: var(--amplified-activated-background-color);
}

@media (hover:hover) {

option:checked:hover {
    border-color: color-mix(in srgb, var(--amplified-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--amplified-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

option:checked:active {
  border-color: var(--amplified-pressed-border-color);
  background-color: var(--amplified-pressed-background-color);
}

option:checked:focus-visible {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

option:checked:disabled {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

option.disabled:checked {
  border-color: var(--amplified-disabled-border-color);
  background-color: var(--amplified-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-amplified-disabled-color) !important;
}

option:checked {
  color: var(--on-flat-active-color);
  font-family: var(--global-typography-font-family);
  font-weight: var(--global-typography-ui-body-active-font-weight);
  font-size: var(--global-typography-ui-body-active-font-size);
  line-height: var(--global-typography-ui-body-active-line-height);
  font-feature-settings:
    "liga" off,
    "clig" off,
    "ss04" on;
}

option::checkmark {
  display: none;
}

.wrapper.flat {
  cursor: pointer;
}

.wrapper.flat:focus {
  outline: none;
}

.wrapper.flat .visible-wrapper {
  border-color: var(--flat-enabled-border-color);
  background-color: var(--flat-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--flat-enabled-border-color);
  --base-background-color: var(--flat-enabled-background-color);
}

.wrapper.flat.activated .visible-wrapper {
  border-color: var(--flat-activated-border-color);
  background-color: var(--flat-activated-background-color);
  --base-border-color: var(--flat-activated-border-color);
  --base-background-color: var(--flat-activated-background-color);
}

@media (hover:hover) {

.wrapper.flat:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--flat-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--flat-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.flat:active .visible-wrapper {
  border-color: var(--flat-pressed-border-color);
  background-color: var(--flat-pressed-background-color);
}

.wrapper.flat:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.flat:disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.flat.disabled .visible-wrapper {
  border-color: var(--flat-disabled-border-color);
  background-color: var(--flat-disabled-background-color);
  cursor: not-allowed;
  color: var(--on-flat-disabled-color) !important;
}

.wrapper.flat:disabled {
  cursor: not-allowed;
}

.wrapper.flat.disabled {
  cursor: not-allowed;
}

.wrapper.integration {
  cursor: pointer;
}

.wrapper.integration:focus {
  outline: none;
}

.wrapper.integration .visible-wrapper {
  border-color: var(--integration-selected-enabled-border-color);
  background-color: var(--integration-selected-enabled-background-color);
  border-width: 1px;
  border-style: solid;
  cursor: pointer;
  --base-border-color: var(--integration-selected-enabled-border-color);
  --base-background-color: var(--integration-selected-enabled-background-color);
}

.wrapper.integration.activated .visible-wrapper {
  border-color: var(--integration-selected-activated-border-color);
  background-color: var(--integration-selected-activated-background-color);
  --base-border-color: var(--integration-selected-activated-border-color);
  --base-background-color: var(--integration-selected-activated-background-color);
}

@media (hover:hover) {

.wrapper.integration:hover .visible-wrapper {
    border-color: color-mix(in srgb, var(--integration-selected-hover-border-color) calc(var(--obc-can-hover) * 100%), var(--base-border-color));
    background-color: color-mix(in srgb, var(--integration-selected-hover-background-color) calc(var(--obc-can-hover) * 100%), var(--base-background-color));
  }
}

.wrapper.integration:active .visible-wrapper {
  border-color: var(--integration-selected-pressed-border-color);
  background-color: var(--integration-selected-pressed-background-color);
}

.wrapper.integration:focus-visible .visible-wrapper {
  outline-color: var(--border-focus-color);
  outline-width: var(--global-size-spacing-border-weight-focusframe);
  outline-style: solid;
  border-color: var(--container-global-color);
  z-index: 1;
}

.wrapper.integration:disabled .visible-wrapper {
  border-color: var(--integration-selected-disabled-border-color);
  background-color: var(--integration-selected-disabled-background-color);
  cursor: not-allowed;
  color: var(--integration-on-selected-disabled-color) !important;
}

.wrapper.integration.disabled .visible-wrapper {
  border-color: var(--integration-selected-disabled-border-color);
  background-color: var(--integration-selected-disabled-background-color);
  cursor: not-allowed;
  color: var(--integration-on-selected-disabled-color) !important;
}

.wrapper.integration:disabled {
  cursor: not-allowed;
}

.wrapper.integration.disabled {
  cursor: not-allowed;
}

.wrapper.integration .visible-wrapper {
    box-sizing: border-box;
    height: 40px;
  }
`;var Fk=Object.defineProperty,Nk=Object.getOwnPropertyDescriptor,Po=(e,t,o,r)=>{for(var i=r>1?void 0:r?Nk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&Fk(t,o,i),i};var ao=class extends S{constructor(){super(...arguments),this.options=[],this.disabled=!1,this.fullWidth=!1,this.allowEmptySelection=!1,this.placeholder="",this.type="label",this.openTop=!1,this.integration=!1,this.flat=!1,this.selectedValue="",this.selectedLabel=""}connectedCallback(){super.connectedCallback(),this.updateSelectedValues()}willUpdate(e){(e.has("value")||e.has("options"))&&this.updateSelectedValues()}updateSelectedValues(){if(this.options.length===0){this.selectedValue="",this.selectedLabel="";return}let e=this.value?this.options.find(t=>t.value===this.value):void 0;if(e){this.selectedValue=e.value,this.selectedLabel=e.label;return}if(this.allowEmptySelection){this.selectedValue="",this.selectedLabel=this.placeholder;return}this.selectedValue=this.options[0].value,this.selectedLabel=this.options[0].label}render(){return f`
      <div
        class=${de({wrapper:!0,"full-width":this.fullWidth,"open-top":this.openTop,integration:this.integration,flat:this.flat&&!this.integration,disabled:this.disabled})}
      >
        <div class="visible-wrapper">
          ${this.type!=="label"?f`<div class="icon-container"><slot name="icon"></slot></div>`:z}
          ${this.type!=="icon"?f`<div class="label">${this.selectedLabel}</div>`:z}
          <div class="icon">
            <obi-drop-down-google></obi-drop-down-google>
          </div>
        </div>
        <select @change=${this.changeHandler} ?disabled=${this.disabled}>
          ${this.allowEmptySelection&&this.selectedValue===""?f`<option value="" disabled selected hidden>
                ${this.placeholder}
              </option>`:z}
          ${this.options.map(e=>{let t=e.level?(e.level-1)*2:0,o=[];for(let r=0;r<t;r++)o.push(f`&nbsp;`);return f`<option
              value=${e.value}
              ?selected=${e.value===this.selectedValue}
            >
              ${o}${e.label}
            </option>`})}
        </select>
      </div>
    `}changeHandler(e){let t=e.target;this.selectedValue=t.value,this.selectedLabel=this.options.find(o=>o.value===this.selectedValue).label.trim(),this.dispatchEvent(new CustomEvent("dropdown-change",{detail:{value:this.selectedValue,label:this.selectedLabel}})),this.dispatchEvent(new CustomEvent("change",{detail:{value:this.selectedValue,label:this.selectedLabel}}))}};ao.styles=ne(Mb);Po([h({type:Array})],ao.prototype,"options",2);Po([h({type:String})],ao.prototype,"value",2);Po([h({type:Boolean})],ao.prototype,"disabled",2);Po([h({type:Boolean})],ao.prototype,"fullWidth",2);Po([h({type:Boolean})],ao.prototype,"allowEmptySelection",2);Po([h({type:String})],ao.prototype,"placeholder",2);Po([h({type:String})],ao.prototype,"type",2);Po([h({type:Boolean})],ao.prototype,"openTop",2);Po([h({type:Boolean})],ao.prototype,"integration",2);Po([h({type:Boolean})],ao.prototype,"flat",2);Po([ke()],ao.prototype,"selectedValue",2);Po([ke()],ao.prototype,"selectedLabel",2);ao=Po([L("obc-dropdown-button")],ao);var jk=Object.defineProperty,Wk=Object.getOwnPropertyDescriptor,_i=(e,t,o,r)=>{for(var i=r>1?void 0:r?Wk(t,o):t,s=e.length-1,n;s>=0;s--)(n=e[s])&&(i=(r?n(t,o,i):n(i))||i);return r&&i&&jk(t,o,i),i};var mr=class extends S{constructor(){super(...arguments),this.hasShelved=!1,this.selectedMode="all",this.alerts=[],this.showTime=!1,this.timeFormatter=e=>e.toLocaleTimeString(void 0,{hour12:!1}),this._mode="all"}willUpdate(e){e.has("selectedMode")&&this._mode!==this.selectedMode&&(this._mode=this.selectedMode)}handleAckAllVisibleClick(){let e=this.selectedMode,t=this.alertList.getVisibleAlerts();this.dispatchEvent(new CustomEvent("ack-all-visible-click",{detail:{alerts:t,mode:e}}))}onModeSelect(e){this._mode=e.detail.value}get metadata(){return vu(this.selectedMode)}onAckClick(e){this.dispatchEvent(new CustomEvent("ack-click",{detail:{alert:e.detail.alert}}))}onRowClick(e){this.dispatchEvent(new CustomEvent("row-click",{detail:{alert:e.detail.alert}}))}render(){let e=[{name:"all",title:Ge("All")},{name:"unacked",title:Ge("Unacked")}];this.hasShelved&&e.push({name:"shelved",title:Ge("Shelved")});let t=this.metadata,o=this.alerts.some(kb(t.filter));return f`
      <div class="wrapper">
        <obc-alert-list-details
          class="alert-list"
          .small=${!0}
          .alerts=${this.alerts}
          .selectedMode=${this._mode}
          .showTime=${this.showTime}
          .timeFormatter=${this.timeFormatter}
          @ack-click=${this.onAckClick}
          @row-click=${this.onRowClick}
        ></obc-alert-list-details>
        <div class="action">
          <div class="btn-group">
            <obc-dropdown-button
              .value=${this._mode}
              @change=${this.onModeSelect}
              .options=${e.map(r=>({value:r.name,label:r.title}))}
            >
            </obc-dropdown-button>
          </div>

          <div class="btn-group">
            <obc-icon-button
              variant="normal"
              @click=${()=>this.dispatchEvent(new CustomEvent("silence-click"))}
            >
              <obi-silence-iec></obi-silence-iec>
            </obc-icon-button>
            <obc-button
              .variant=${nh.raised}
              .disabled=${!o}
              fullWidth
              class="btn"
              data-testid="ack-all-visible-button"
              @click=${()=>this.handleAckAllVisibleClick()}
            >
              ${Ge("ACK visible")}
            </obc-button>
          </div>
        </div>
      </div>
    `}};mr.styles=ne(Lb);_i([h({type:Boolean})],mr.prototype,"hasShelved",2);_i([h({type:String})],mr.prototype,"selectedMode",2);_i([h({type:Array})],mr.prototype,"alerts",2);_i([h({type:Boolean})],mr.prototype,"showTime",2);_i([h({attribute:!1})],mr.prototype,"timeFormatter",2);_i([ke()],mr.prototype,"_mode",2);_i([at("obc-alert-list-details")],mr.prototype,"alertList",2);mr=_i([L("obc-alert-list-page-small")],mr);})();
/*! For license information please see ob-components.js.LEGAL.txt */


/* Cadre OpenBridge module: Perspective wrappers for OpenBridge web components.
   Generated by module/tools/gen_module_assets.py; do not edit. */
(function () {
  'use strict';
  var PC = window.PerspectiveClient;
  var h = window.React.createElement;
  var COMPONENTS = [{"type":"cadre.ob.pump","tag":"obc-pump","size":{"width":96,"height":96},"fields":[{"name":"vertical","kind":"boolean","def":false},{"name":"on","kind":"boolean","def":false},{"name":"speedInPercent","kind":"number","def":0},{"name":"speed","kind":"nnumber","def":null},{"name":"speedUnit","kind":"string","def":"%"},{"name":"speedMaxDigits","kind":"number","def":3},{"name":"labelDirection","kind":"string","def":"right"},{"name":"variant","kind":"string","def":"regular"},{"name":"direction","kind":"string","def":"forward"},{"name":"readoutPosition","kind":"string","def":"bottom"},{"name":"readoutSize","kind":"string","def":"regular"},{"name":"tag","kind":"nstring","def":""},{"name":"positioning","kind":"string","def":"point"},{"name":"activated","kind":"boolean","def":false},{"name":"alert","kind":"boolean","def":false},{"name":"alertFrameType","kind":"string","def":"small-side-flip"},{"name":"alertFrameThickness","kind":"string","def":"small"},{"name":"alertFrameStatus","kind":"string","def":"alarm"},{"name":"alertFrameMode","kind":"string","def":"acked-active"},{"name":"showAlertIcon","kind":"boolean","def":false},{"name":"progress","kind":"boolean","def":false},{"name":"progressMode","kind":"string","def":"indeterminate"},{"name":"progressValue","kind":"number","def":0},{"name":"badgeControl","kind":"string","def":"none"},{"name":"badgeCommandLocked","kind":"string","def":"none"},{"name":"badgeInterlock","kind":"string","def":"none"},{"name":"badgeAlert","kind":"string","def":"none"}],"extras":[{"name":"hasSpeed","kind":"boolean","def":true},{"name":"showStatus","kind":"boolean","def":true},{"name":"statusText","kind":"string","def":""},{"name":"badgeDuty","kind":"boolean","def":false},{"name":"outOfService","kind":"boolean","def":false}],"speedless":true,"tankSlots":false,"sheet":"","chipSheet":"","selection":false,"status":true,"endAligned":false,"data":[],"events":[]},{"type":"cadre.ob.tank","tag":"obc-automation-tank","size":{"width":168,"height":216},"fields":[{"name":"medium","kind":"string","def":"water"},{"name":"value","kind":"number","def":0},{"name":"max","kind":"number","def":100},{"name":"trend","kind":"string","def":"stable"},{"name":"type","kind":"string","def":"generic"},{"name":"orientation","kind":"string","def":"vertical"},{"name":"compact","kind":"boolean","def":false},{"name":"positioning","kind":"string","def":"button"},{"name":"static","kind":"boolean","def":false},{"name":"activated","kind":"boolean","def":false},{"name":"tag","kind":"string","def":""},{"name":"chartMode","kind":"string","def":"bar"},{"name":"priority","kind":"string","def":"regular"},{"name":"hasAdvice","kind":"boolean","def":false},{"name":"alert","kind":"boolean","def":false},{"name":"alertFrameType","kind":"string","def":"small-side-flip"},{"name":"alertFrameThickness","kind":"string","def":"small"},{"name":"alertFrameStatus","kind":"string","def":"alarm"},{"name":"showAlertIcon","kind":"boolean","def":false},{"name":"percentFractionDigits","kind":"number","def":0},{"name":"badgeControl","kind":"string","def":"none"},{"name":"badgeAlert","kind":"string","def":"none"},{"name":"badgeInterlock","kind":"string","def":"none"},{"name":"badgeCommandLocked","kind":"string","def":"none"},{"name":"setpoint","kind":"nnumber","def":null},{"name":"newSetpoint","kind":"nnumber","def":null},{"name":"autoAtSetpointDeadband","kind":"number","def":2},{"name":"setpointAtZeroDeadband","kind":"number","def":0.5},{"name":"setpointOverride","kind":"boolean","def":false},{"name":"animateSetpoint","kind":"boolean","def":false}],"extras":[{"name":"unit","kind":"string","def":"m\u00b3"},{"name":"hasCapacity","kind":"boolean","def":true}],"speedless":false,"tankSlots":true,"sheet":"","chipSheet":"","selection":false,"status":false,"endAligned":false,"data":[],"events":[]},{"type":"cadre.ob.motor","tag":"obc-motor","size":{"width":96,"height":96},"fields":[{"name":"vertical","kind":"boolean","def":false},{"name":"on","kind":"boolean","def":false},{"name":"speedInPercent","kind":"number","def":0},{"name":"speed","kind":"nnumber","def":null},{"name":"speedUnit","kind":"string","def":"%"},{"name":"speedMaxDigits","kind":"number","def":3},{"name":"labelDirection","kind":"string","def":"right"},{"name":"variant","kind":"string","def":"regular"},{"name":"direction","kind":"string","def":"forward"},{"name":"readoutPosition","kind":"string","def":"bottom"},{"name":"readoutSize","kind":"string","def":"regular"},{"name":"tag","kind":"nstring","def":""},{"name":"positioning","kind":"string","def":"point"},{"name":"activated","kind":"boolean","def":false},{"name":"alert","kind":"boolean","def":false},{"name":"alertFrameType","kind":"string","def":"small-side-flip"},{"name":"alertFrameThickness","kind":"string","def":"small"},{"name":"alertFrameStatus","kind":"string","def":"alarm"},{"name":"alertFrameMode","kind":"string","def":"acked-active"},{"name":"showAlertIcon","kind":"boolean","def":false},{"name":"progress","kind":"boolean","def":false},{"name":"progressMode","kind":"string","def":"indeterminate"},{"name":"progressValue","kind":"number","def":0},{"name":"badgeControl","kind":"string","def":"none"},{"name":"badgeCommandLocked","kind":"string","def":"none"},{"name":"badgeInterlock","kind":"string","def":"none"},{"name":"badgeAlert","kind":"string","def":"none"}],"extras":[{"name":"hasSpeed","kind":"boolean","def":true},{"name":"showStatus","kind":"boolean","def":true},{"name":"statusText","kind":"string","def":""},{"name":"badgeDuty","kind":"boolean","def":false},{"name":"outOfService","kind":"boolean","def":false}],"speedless":true,"tankSlots":false,"sheet":"","chipSheet":"","selection":false,"status":true,"endAligned":false,"data":[],"events":[]},{"type":"cadre.ob.fan","tag":"obc-fan","size":{"width":96,"height":96},"fields":[{"name":"on","kind":"boolean","def":false},{"name":"speedInPercent","kind":"number","def":0},{"name":"speed","kind":"nnumber","def":null},{"name":"speedUnit","kind":"string","def":"%"},{"name":"speedMaxDigits","kind":"number","def":3},{"name":"labelDirection","kind":"string","def":"right"},{"name":"variant","kind":"string","def":"regular"},{"name":"direction","kind":"string","def":"forward"},{"name":"readoutPosition","kind":"string","def":"bottom"},{"name":"readoutSize","kind":"string","def":"regular"},{"name":"tag","kind":"nstring","def":""},{"name":"positioning","kind":"string","def":"point"},{"name":"activated","kind":"boolean","def":false},{"name":"alert","kind":"boolean","def":false},{"name":"alertFrameType","kind":"string","def":"small-side-flip"},{"name":"alertFrameThickness","kind":"string","def":"small"},{"name":"alertFrameStatus","kind":"string","def":"alarm"},{"name":"alertFrameMode","kind":"string","def":"acked-active"},{"name":"showAlertIcon","kind":"boolean","def":false},{"name":"progress","kind":"boolean","def":false},{"name":"progressMode","kind":"string","def":"indeterminate"},{"name":"progressValue","kind":"number","def":0},{"name":"badgeControl","kind":"string","def":"none"},{"name":"badgeCommandLocked","kind":"string","def":"none"},{"name":"badgeInterlock","kind":"string","def":"none"},{"name":"badgeAlert","kind":"string","def":"none"}],"extras":[{"name":"hasSpeed","kind":"boolean","def":true},{"name":"showStatus","kind":"boolean","def":true},{"name":"statusText","kind":"string","def":""},{"name":"badgeDuty","kind":"boolean","def":false},{"name":"outOfService","kind":"boolean","def":false}],"speedless":true,"tankSlots":false,"sheet":"","chipSheet":"","selection":false,"status":true,"endAligned":false,"data":[],"events":[]},{"type":"cadre.ob.valve","tag":"obc-digital-valve","size":{"width":96,"height":96},"fields":[{"name":"open","kind":"boolean","def":false},{"name":"vertical","kind":"boolean","def":false},{"name":"variant","kind":"string","def":"regular"},{"name":"readoutPosition","kind":"string","def":"bottom"},{"name":"readoutSize","kind":"string","def":"regular"},{"name":"tag","kind":"nstring","def":""},{"name":"positioning","kind":"string","def":"point"},{"name":"activated","kind":"boolean","def":false},{"name":"alert","kind":"boolean","def":false},{"name":"alertFrameType","kind":"string","def":"small-side-flip"},{"name":"alertFrameThickness","kind":"string","def":"small"},{"name":"alertFrameStatus","kind":"string","def":"alarm"},{"name":"alertFrameMode","kind":"string","def":"acked-active"},{"name":"showAlertIcon","kind":"boolean","def":false},{"name":"progress","kind":"boolean","def":false},{"name":"progressMode","kind":"string","def":"indeterminate"},{"name":"progressValue","kind":"number","def":0},{"name":"badgeControl","kind":"string","def":"none"},{"name":"badgeCommandLocked","kind":"string","def":"none"},{"name":"badgeInterlock","kind":"string","def":"none"},{"name":"badgeAlert","kind":"string","def":"none"},{"name":"showStatus","kind":"boolean","def":true}],"extras":[],"speedless":false,"tankSlots":false,"sheet":"","chipSheet":"","selection":false,"status":false,"endAligned":false,"data":[],"events":[]},{"type":"cadre.ob.analogvalve","tag":"obc-analog-valve","size":{"width":96,"height":96},"fields":[{"name":"open","kind":"boolean","def":false},{"name":"value","kind":"number","def":0},{"name":"vertical","kind":"boolean","def":false},{"name":"labelDirection","kind":"string","def":"right"},{"name":"variant","kind":"string","def":"regular"},{"name":"readoutPosition","kind":"string","def":"bottom"},{"name":"readoutSize","kind":"string","def":"regular"},{"name":"tag","kind":"nstring","def":""},{"name":"positioning","kind":"string","def":"point"},{"name":"activated","kind":"boolean","def":false},{"name":"alert","kind":"boolean","def":false},{"name":"alertFrameType","kind":"string","def":"small-side-flip"},{"name":"alertFrameThickness","kind":"string","def":"small"},{"name":"alertFrameStatus","kind":"string","def":"alarm"},{"name":"alertFrameMode","kind":"string","def":"acked-active"},{"name":"showAlertIcon","kind":"boolean","def":false},{"name":"progress","kind":"boolean","def":false},{"name":"progressMode","kind":"string","def":"indeterminate"},{"name":"progressValue","kind":"number","def":0},{"name":"badgeControl","kind":"string","def":"none"},{"name":"badgeCommandLocked","kind":"string","def":"none"},{"name":"badgeInterlock","kind":"string","def":"none"},{"name":"badgeAlert","kind":"string","def":"none"},{"name":"showStatus","kind":"boolean","def":true}],"extras":[],"speedless":false,"tankSlots":false,"sheet":"","chipSheet":"","selection":false,"status":false,"endAligned":false,"data":[],"events":[]},{"type":"cadre.ob.readout","tag":"obc-transmitter","size":{"width":72,"height":24},"fields":[{"name":"orientation","kind":"string","def":"bottom"},{"name":"type","kind":"string","def":"value"},{"name":"value","kind":"nnumber","def":null},{"name":"unit","kind":"string","def":""},{"name":"fractionDigits","kind":"number","def":1},{"name":"maxDigits","kind":"number","def":0},{"name":"hintedZeros","kind":"boolean","def":false},{"name":"hasSignSpacer","kind":"boolean","def":false},{"name":"size","kind":"string","def":"regular"},{"name":"hasIcon","kind":"boolean","def":false},{"name":"hasAdvice","kind":"boolean","def":false},{"name":"hasAlert","kind":"boolean","def":false},{"name":"adviceValue","kind":"nnumber","def":null},{"name":"hasSetPoint","kind":"boolean","def":false},{"name":"setpointValue","kind":"nnumber","def":null},{"name":"tag","kind":"string","def":""},{"name":"idTag","kind":"string","def":""}],"extras":[{"name":"stretch","kind":"boolean","def":false}],"speedless":false,"tankSlots":false,"sheet":"readout","chipSheet":"readoutchip","selection":false,"status":false,"endAligned":false,"data":[],"events":[]},{"type":"cadre.ob.instrumentfield","tag":"obc-instrument-field","size":{"width":96,"height":64},"fields":[{"name":"size","kind":"string","def":"regular"},{"name":"setpoint","kind":"nnumber","def":null},{"name":"hasSetpoint","kind":"boolean","def":false},{"name":"hasSrc","kind":"boolean","def":false},{"name":"value","kind":"nnumber","def":null},{"name":"maxDigits","kind":"number","def":1},{"name":"showZeroPadding","kind":"boolean","def":false},{"name":"fractionDigits","kind":"number","def":0},{"name":"tag","kind":"string","def":""},{"name":"unit","kind":"string","def":""},{"name":"src","kind":"string","def":""},{"name":"neutralColor","kind":"boolean","def":false},{"name":"horizontal","kind":"boolean","def":false},{"name":"center","kind":"boolean","def":false},{"name":"labelOnly","kind":"boolean","def":false},{"name":"off","kind":"boolean","def":false},{"name":"autoHideSetpoint","kind":"boolean","def":false},{"name":"autoHideDeadband","kind":"number","def":0}],"extras":[],"speedless":false,"tankSlots":false,"sheet":"instrumentfield","chipSheet":"","selection":false,"status":false,"endAligned":true,"data":[],"events":[]},{"type":"cadre.ob.alertlist","tag":"obc-alert-list-details","size":{"width":368,"height":480},"fields":[{"name":"selectedMode","kind":"string","def":"all"},{"name":"showTime","kind":"boolean","def":false},{"name":"small","kind":"boolean","def":false}],"extras":[{"name":"selectable","kind":"boolean","def":false},{"name":"selectedIds","kind":"array","def":[]}],"speedless":false,"tankSlots":false,"sheet":"","chipSheet":"","selection":true,"status":false,"endAligned":false,"data":[{"name":"alerts","kind":"alerts"}],"events":[{"dom":"ack-click","name":"onAckClick","payload":"alert"},{"dom":"row-click","name":"onRowClick","payload":"alert"}]},{"type":"cadre.ob.alertpanel","tag":"obc-alert-list-page-small","size":{"width":640,"height":420},"fields":[{"name":"hasShelved","kind":"boolean","def":false},{"name":"selectedMode","kind":"string","def":"all"},{"name":"showTime","kind":"boolean","def":false}],"extras":[{"name":"selectable","kind":"boolean","def":false},{"name":"selectedIds","kind":"array","def":[]}],"speedless":false,"tankSlots":false,"sheet":"","chipSheet":"","selection":true,"status":false,"endAligned":false,"data":[{"name":"alerts","kind":"alerts"}],"events":[{"dom":"ack-click","name":"onAckClick","payload":"alert"},{"dom":"row-click","name":"onRowClick","payload":"alert"},{"dom":"silence-click","name":"onSilenceClick","payload":"none"},{"dom":"ack-all-visible-click","name":"onAckAllClick","payload":"visible"}]}];
  var SHEETS = {"readout":".transmitter { transform: none !important; top: auto !important; right: auto !important; padding: 0 !important; }\n.transmitter::before { display: none !important; }\n:host([data-stretch]), :host([data-stretch]) .transmitter, :host([data-stretch]) .content, :host([data-stretch]) .body { width: 100% !important; }\n:host([data-stretch]) .chip { display: block; flex: 1 1 auto; width: 100%; }","readoutchip":":host([data-stretch]) { display: block; width: 100%; }\n:host([data-stretch]) .button { display: flex; width: 100%; }\n:host([data-stretch]) .visible-wrapper { width: 100%; justify-content: center; }","instrumentfield":":host([data-center]) .setpoint, :host([data-center]) .value { justify-content: center !important; }"};

  function read(tree, f) {
    switch (f.kind) {
      case 'boolean': return tree.readBoolean(f.name, f.def);
      case 'number': return tree.readNumber(f.name, f.def);
      case 'array': return tree.readArray(f.name, f.def);
      case 'nnumber': { var v = tree.read(f.name); return (v === null || v === undefined || v === '') ? undefined : Number(v); }
      case 'nstring': { var s = tree.readString(f.name, ''); return s === '' ? null : s; }
      default: return tree.readString(f.name, f.def);
    }
  }

  // Alert records arrive with epoch millisecond times (cadre.hmi.alarm_list); the elements expect Dates.
  function toDate(v) { return (v === null || v === undefined || v === '') ? v : new Date(Number(v)); }
  function toAlerts(list) {
    if (!Array.isArray(list)) return [];
    return list.map(function (a) {
      var o = Object.assign({}, a);
      o.time = toDate(a.time);
      if (a.lastModified !== undefined) o.lastModified = toDate(a.lastModified);
      if (a.acknowledged && typeof a.acknowledged === 'object')
        o.acknowledged = Object.assign({}, a.acknowledged, { acknowledgedAt: toDate(a.acknowledged.acknowledgedAt) });
      if (a.active && typeof a.active === 'object')
        o.active = Object.assign({}, a.active, { rectifiedTime: toDate(a.active.rectifiedTime) });
      if (a.shelved && typeof a.shelved === 'object')
        o.shelved = Object.assign({}, a.shelved, { shelvedStartTime: toDate(a.shelved.shelvedStartTime),
                                                    shelvedEndTime: toDate(a.shelved.shelvedEndTime) });
      return o;
    });
  }
  var CONVERT = { alerts: toAlerts };

  // The payload of a Perspective component event, from the element's event detail.
  function payload(kind, e, el) {
    var d = (e && e.detail) || {};
    if (kind === 'alert') {
      var a = d.alert || {};
      return { ids: a.id ? [String(a.id)] : [], id: String(a.id || ''), tagId: String(a.tagId || ''),
               source: String(a.source || ''), text: String(a.text || '') };
    }
    if (kind === 'visible') {
      var mode = d.mode || 'unacked';
      var shown = (el && el.alerts || []).filter(function (a) {
        return mode === 'shelved' ? !!a.shelved : (mode === 'all' ? true : !a.acknowledged);
      });
      return { mode: String(mode), ids: shown.filter(function (a) { return !a.acknowledged; })
                                            .map(function (a) { return String(a.id); }) };
    }
    return {};
  }

  function wrapper(spec) {
    class ObWrapper extends PC.Component {
      constructor(props) {
        super(props);
        this.el = null;
        this.handlers = [];
        this.applied = {};
        // row selection (alarm lists, module 0.4.2): the ids shown and sent, the table and what watches it
        this.selIds = [];
        this.selSent = [];
        this.selOn = false;
        this.selTouched = false;
        this.selQueued = false;
        this.table = null;
        this.selHost = null;
        this.tableKey = null;
        this.onTick = (e) => {
          var t = this.table;
          if (!t) return;
          this.writeSelection(((e && e.detail && e.detail.selectedRowIds) || []).map(String));
          this.showSelection(t);
        };
        this.selWatch = (spec.selection && typeof MutationObserver === 'function')
          ? new MutationObserver(() => { if (this.selOn || this.selTouched) this.syncSelection(); }) : null;
        this.setRef = (el) => {
          this.unlisten();
          this.selDetach();
          this.el = el;
          this.applied = {};
          if (el && spec.sheet) this.sheets();
          if (el) {
            (spec.events || []).forEach((ev) => {
              var f = (e) => this.fire(ev, e);
              el.addEventListener(ev.dom, f);
              this.handlers.push([el, ev.dom, f]);
            });
          }
          this.apply();
        };
      }
      componentDidUpdate() { this.apply(); }
      componentWillUnmount() { this.unlisten(); this.selDetach(); }
      // Rules added to the shadow root of the element, and of the chip inside a readout (spec.chipSheet). The
      // shadow root exists once the element is connected and has drawn once, so the work waits for that; it
      // runs again after each update, because an alert frame around a readout draws a new chip.
      sheets() {
        var el = this.el;
        if (!el) return;
        Promise.resolve(el.updateComplete).then(() => {
          var put = function (root, css) {
            if (!root || root.querySelector('style[data-cadre]')) return;
            var st = document.createElement('style');
            st.setAttribute('data-cadre', '');
            st.textContent = css;
            root.appendChild(st);
          };
          put(el.shadowRoot, SHEETS[spec.sheet]);
          if (spec.chipSheet && el.shadowRoot) {
            var chip = el.shadowRoot.querySelector('obc-transmitter-button');
            if (chip) {
              put(chip.shadowRoot, SHEETS[spec.chipSheet]);
              chip.toggleAttribute('data-stretch', el.hasAttribute('data-stretch'));
            }
          }
        });
      }
      unlisten() {
        this.handlers.forEach(function (h) { h[0].removeEventListener(h[1], h[2]); });
        this.handlers = [];
      }
      fire(ev, e) {
        var ce = this.props.componentEvents;
        if (ce && typeof ce.fireComponentEvent === 'function') ce.fireComponentEvent(ev.name, payload(ev.payload, e, this.el));
      }
      apply() {
        var el = this.el;
        if (!el) return;
        var p = this.props.props;
        // no speed: the element prints one unless both its speed properties are undefined
        var speedless = spec.speedless && p.hasSpeed === false;
        for (var i = 0; i < spec.fields.length; i++) {
          var n = spec.fields[i].name;
          if (speedless && (n === 'speed' || n === 'speedInPercent')) { if (el[n] !== undefined) el[n] = undefined; continue; }
          if (el[n] !== p[n]) el[n] = p[n];
        }
        if (spec.endAligned) el.toggleAttribute('data-center', !!p.center);
        if (spec.chipSheet) { el.toggleAttribute('data-stretch', !!p.stretch); this.sheets(); }
        if (spec.status) this.applyStatus(el, p);
        (spec.data || []).forEach((d) => {
          var key = JSON.stringify(p[d.name] === undefined ? null : p[d.name]);
          if (this.applied[d.name] !== key) { this.applied[d.name] = key; el[d.name] = CONVERT[d.kind](p[d.name]); }
        });
        if (spec.selection) this.applySelection(p);
      }
      // ---- Row selection of the two alarm lists (module 0.4.2). OpenBridge's table draws the tick column (an
      // obc-checkbox in each row, and one in the header of the full list) when its `selectable` is true, takes the
      // ticked ids from `selectedRowIds` and reports a toggle as `selection-change`; the alert list sets none of the
      // three, so the wrapper sets them on the table inside the list (the alert panel nests the list in its shadow
      // root). A tick stops its own click, so a toggle never reaches the row click. The wrapper keeps the ids itself,
      // shows a toggle at once and writes it to `selectedIds`; a value that comes back is either the wrapper's own
      // echo (ignored) or an outside change, such as the library clearing the selection after an acknowledgement
      // (it wins). Ids of rows the list no longer shows are dropped (pruneSelection).
      applySelection(p) {
        var on = !!p.selectable;
        if (!on && !this.selTouched) return;
        this.selTouched = true;
        this.selOn = on;
        var incoming = Array.isArray(p.selectedIds) ? p.selectedIds.map(String) : [];
        var at = this.selSent.indexOf(JSON.stringify(incoming));
        if (at >= 0) this.selSent.splice(0, at + 1);
        else { this.selSent = []; this.selIds = incoming; }
        this.syncSelection();
      }
      selectionHost() {
        var el = this.el;
        if (!el) return null;
        if (el.tagName === 'OBC-ALERT-LIST-DETAILS') return el;
        return el.shadowRoot ? el.shadowRoot.querySelector('obc-alert-list-details') : null;
      }
      // Waits until the element, the list inside it and the table have drawn, then binds the table.
      syncSelection() {
        var el = this.el;
        if (!el || this.selQueued) return;
        this.selQueued = true;
        var table = null;
        Promise.resolve(el.updateComplete).then(() => {
          var host = this.selectionHost();
          return host && host !== el ? host.updateComplete : null;
        }).then(() => {
          var host = this.selectionHost();
          table = host && host.shadowRoot ? host.shadowRoot.querySelector('obc-table') : null;
          return table ? table.updateComplete : null;
        }).then(() => {
          this.selQueued = false;
          if (this.el === el) this.bindSelection(table);
        }).catch(() => { this.selQueued = false; });
      }
      bindSelection(t) {
        var host = this.selectionHost();
        if (this.table !== t || this.selHost !== host) {
          if (this.table) this.table.removeEventListener('selection-change', this.onTick);
          if (this.selWatch) this.selWatch.disconnect();
          this.table = t;
          this.selHost = host;
          this.tableKey = null;
          if (t) t.addEventListener('selection-change', this.onTick);
          // the list draws a new table when it was empty, and the table draws new rows when its data changes
          if (this.selWatch && host && host.shadowRoot) this.selWatch.observe(host.shadowRoot, { childList: true, subtree: true });
          if (this.selWatch && t && t.renderRoot) this.selWatch.observe(t.renderRoot, { childList: true, subtree: true });
        }
        // no table: the list shows no row (an empty list draws a message instead), so nothing stays selected
        if (!t) { if (host && this.selOn && this.selIds.length) this.writeSelection([]); return; }
        if (t.selectable !== this.selOn) t.selectable = this.selOn;
        if (!this.selOn) { if (t.selectedRowIds !== undefined) t.selectedRowIds = undefined; this.tableKey = null; return; }
        this.pruneSelection(t);
        this.showSelection(t);
      }
      // The table's own ids (as the rows carry them) for the selected strings that its rows still show.
      rowIds(t, ids) {
        var byKey = {};
        (t.data || []).forEach(function (r) { byKey[String(r.id)] = r.id; });
        return ids.filter(function (i) { return Object.prototype.hasOwnProperty.call(byKey, i); })
                  .map(function (i) { return byKey[i]; });
      }
      showSelection(t) {
        var ids = this.rowIds(t, this.selIds), key = JSON.stringify(ids);
        if (this.tableKey !== key) { this.tableKey = key; t.selectedRowIds = ids; }
      }
      pruneSelection(t) {
        var kept = this.rowIds(t, this.selIds).map(String);
        if (kept.length !== this.selIds.length) this.writeSelection(kept);
      }
      writeSelection(ids) {
        this.selIds = ids;
        this.selSent.push(JSON.stringify(ids));
        this.put('selectedIds', ids);
      }
      put(name, value) {
        try {
          var store = this.props.store;
          if (store && store.props && typeof store.props.write === 'function') store.props.write(name, value);
        } catch (e) { /* a write refused is not a reason to break the page */ }
      }
      selDetach() {
        if (this.table) this.table.removeEventListener('selection-change', this.onTick);
        if (this.selWatch) this.selWatch.disconnect();
        this.table = null;
        this.selHost = null;
        this.selQueued = false;
      }

      // The status word of a pump, motor or fan. The element draws its status readouts from `extraReadouts`:
      // its speed while it runs and the word Off while it stands, none at all when its showStatus is false. The
      // wrapper passes showStatus on, and, when statusText is given, replaces the element's readouts with the one
      // word in the element's status place (the stock library view's status row does the same).
      applyStatus(el, p) {
        var show = p.showStatus !== false;
        if (el.showStatus !== show) el.showStatus = show;
        var text = typeof p.statusText === 'string' ? p.statusText : '';
        if (!this.statusInstalled) {
          this.statusInstalled = true;
          var base = null;
          for (var o = Object.getPrototypeOf(el); o && !base; o = Object.getPrototypeOf(o)) {
            var d = Object.getOwnPropertyDescriptor(o, 'extraReadouts');
            if (d && d.get) base = d.get;
          }
          var self = this;
          Object.defineProperty(el, 'extraReadouts', { configurable: true, get: function () {
            var own = base ? base.call(el) : [];
            if (!self.statusText || el.showStatus === false) return own;
            return [{ type: el.on ? 'state-on' : 'state-off', value: self.statusText, hasIcon: true }];
          } });
        }
        if (this.statusText !== text) { this.statusText = text; if (el.requestUpdate) el.requestUpdate(); }
      }
      // The duty badge goes into the first free corner of the element, unless its interlock badge, which draws
      // the same icon, is already there.
      dutySlot(p) {
        if (p.badgeInterlock === 'interlock') return null;
        var corners = [['badge-bottom-left', p.badgeInterlock], ['badge-bottom-right', p.badgeCommandLocked],
                       ['badge-top-left', p.badgeControl], ['badge-top-right', p.badgeAlert]];
        for (var i = 0; i < corners.length; i++) if (!corners[i][1] || corners[i][1] === 'none') return corners[i][0];
        return null;
      }
      render() {
        var size = this.props.props.componentSize || 'regular';
        var p = this.props.props, kids = [];
        if (spec.tankSlots) {
          // slotted content replaces the tank's own: its unit (cubic metres by default) and, for a static
          // tank with no capacity, its whole readout
          if (p.unit && p.unit !== 'm\u00b3') kids.push(h('span', { slot: 'unit', key: 'unit' }, p.unit));
          if (p.static && p.hasCapacity === false) kids.push(h('span', { slot: 'readout', key: 'readout' }));
        }
        if (spec.status && p.badgeDuty) {
          var slot = this.dutySlot(p);
          if (slot) kids.push(h('obc-automation-badge', { slot: slot, key: 'duty', type: 'interlock' }));
        }
        // an out of service symbol: the library view's veil of the page colour and the word OOS, over the symbol
        var oos = (spec.status && p.outOfService) ? h('div', { className: 'cadre-ob-oos', key: 'oos' }, 'OOS') : null;
        // an element that sits at the end of its box unless the symbol is centred
        var at = spec.endAligned ? { justifyContent: p.center ? 'center' : 'flex-end' } : undefined;
        return h('div', this.props.emit(),
          h('div', { className: 'cadre-ob obc-component-size-' + size, style: at },
            h.apply(null, [spec.tag, { ref: this.setRef }].concat(kids)), oos));
      }
    }
    return ObWrapper;
  }

  COMPONENTS.forEach(function (spec) {
    var View = wrapper(spec);
    PC.ComponentRegistry.register({
      getComponentType: function () { return spec.type; },
      getViewComponent: function () { return View; },
      getDefaultSize: function () { return spec.size; },
      getPropsReducer: function (tree) {
        var out = { componentSize: tree.readString('componentSize', 'regular') };
        spec.fields.forEach(function (f) { out[f.name] = read(tree, f); });
        (spec.extras || []).forEach(function (f) { out[f.name] = read(tree, f); });
        (spec.data || []).forEach(function (d) { out[d.name] = tree.readArray(d.name, []); });
        return out;
      }
    });
  });
})();

/* Cadre OpenBridge module: the canvas zoom component (cadre.ob.canvaszoom).
   Read by module/tools/gen_module_assets.py and appended to cadre-ob.js after the generated wrappers;
   it is plain script (no bundler) and runs in the Perspective client, where PerspectiveClient and React
   are globals (GF-31).

   A leaf component that draws nothing. It finds its target (the scrolling canvas of a diagram screen) by
   its DOM id, and turns three gestures into a number, the `zoom` property, which the view binds two ways
   to its own `zoom` custom property and the canvas scales by:

     Ctrl + wheel (a trackpad pinch arrives the same way), a two finger pinch, Ctrl + plus, minus and 0.

   The point under the pointer stays where it is: once the new scale shows, the target's scroll position is
   set so that the content point that lay under the pointer lies under it again. With guardBrowserZoom the
   same gestures anywhere else on the document are prevented, so the browser never zooms the whole frame,
   and the viewport meta gains maximum-scale=1 on touch devices. Every listener is removed on unmount. */
(function () {
  'use strict';
  var PC = window.PerspectiveClient;
  if (!PC || !PC.ComponentRegistry) return;
  var h = window.React.createElement;
  var TYPE = 'cadre.ob.canvaszoom';
  var STEP = 1.25;            // one key press or one wheel notch (a mouse wheel notch is 100 units)
  var WHEEL_RATE = Math.log(STEP) / 100;
  var SETTLE_MS = 600;        // how long the scroll anchoring waits for the new scale to show

  var TOUCH = 'ontouchstart' in window || (navigator.maxTouchPoints || 0) > 0;

  function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }

  function viewportMeta(create) {
    var m = document.querySelector('meta[name="viewport"]');
    if (!m && create) {
      m = document.createElement('meta');
      m.setAttribute('name', 'viewport');
      m.setAttribute('data-cadre-zoom', '');
      document.head.appendChild(m);
    }
    return m;
  }

  class CanvasZoom extends PC.Component {
    constructor(props) {
      super(props);
      this.cur = null;            // the zoom the component last wrote, ahead of the echoed property
      this.wroteAt = 0;
      this.target = null;
      this.listeners = [];        // [node, type, handler, options] for removal
      this.touchPrev = null;      // the previous distance of a two finger pinch
      this.pointers = new Map();
      this.anchor = null;         // the scroll anchoring in progress
      this.raf = 0;
      this.touchAction = null;
      this.metaSaved = null;
    }

    // ---- the properties
    settings() {
      var p = this.props.props || {};
      var min = typeof p.min === 'number' && p.min > 0 ? p.min : 0.5;
      var max = typeof p.max === 'number' && p.max >= min ? p.max : 4;
      return { zoom: typeof p.zoom === 'number' ? p.zoom : 1, min: min, max: max,
               id: p.targetDomId || 'cadre-canvas', guard: p.guardBrowserZoom !== false };
    }

    // The zoom now: what the component wrote a moment ago, else what the property says.
    current() {
      var s = this.settings();
      if (this.cur !== null && Date.now() - this.wroteAt < 1500) return this.cur;
      this.cur = null;
      return s.zoom;
    }

    write(zoom) {
      this.cur = zoom;
      this.wroteAt = Date.now();
      this.put('zoom', zoom);
    }

    put(name, value) {
      try {
        var store = this.props.store;
        if (store && store.props && typeof store.props.write === 'function') store.props.write(name, value);
      } catch (e) { /* a write refused is not a reason to break the page */ }
    }

    // The target's box, written as viewWidth and viewHeight whenever it changes by a pixel or more: the page's fit
    // reads the canvas it really has (a docked faceplate, a reload, a second tab) instead of the viewport.
    measure() {
      if (!this.target) return;
      var r = this.target.getBoundingClientRect();
      var w = Math.round(r.width), hh = Math.round(r.height);
      if (w <= 0 || hh <= 0) return;
      if (this.measured && Math.abs(this.measured[0] - w) < 1 && Math.abs(this.measured[1] - hh) < 1) return;
      this.measured = [w, hh];
      this.put('viewWidth', w);
      this.put('viewHeight', hh);
    }

    // ---- zooming
    // Zoom by a factor, or to an absolute value, about a client point (cx, cy) of the target.
    zoomTo(next, cx, cy) {
      var s = this.settings(), t = this.target;
      var old = this.current();
      next = clamp(next, s.min, s.max);
      if (Math.abs(next - old) < 1e-6) return;
      if (t && !this.anchor) {
        var r = t.getBoundingClientRect();
        this.anchor = { left: t.scrollLeft, top: t.scrollTop, zoom: old, sw: t.scrollWidth, sh: t.scrollHeight,
                        px: 0, py: 0, last: 0, changed: false };
        this.anchor.px = (cx === undefined ? r.left + r.width / 2 : cx) - r.left;
        this.anchor.py = (cy === undefined ? r.top + r.height / 2 : cy) - r.top;
      }
      if (this.anchor) {
        this.anchor.last = Date.now();
        if (cx !== undefined && t) {
          var rr = t.getBoundingClientRect();
          this.anchor.px = cx - rr.left;
          this.anchor.py = cy - rr.top;
        }
      }
      this.write(next);
      this.settle();
    }

    zoomBy(factor, cx, cy) { this.zoomTo(this.current() * factor, cx, cy); }

    // Once the new scale shows (the target's scrollable size changes), set the scroll position so that the
    // point under the pointer has not moved: (scroll + p) * ratio - p, where ratio is new zoom over the zoom
    // at the start of the burst. Tried every frame until the size has settled.
    settle() {
      if (this.raf) return;
      var self = this;
      var tick = function () {
        self.raf = 0;
        var a = self.anchor, t = self.target;
        if (!a || !t) { self.anchor = null; return; }
        var ratio = self.current() / a.zoom;
        if (t.scrollWidth !== a.sw || t.scrollHeight !== a.sh) a.changed = true;
        if (a.changed || Date.now() - a.last > SETTLE_MS) {
          t.scrollLeft = (a.left + a.px) * ratio - a.px;
          t.scrollTop = (a.top + a.py) * ratio - a.py;
        }
        if (Date.now() - a.last > SETTLE_MS * 1.5) { self.anchor = null; return; }
        self.raf = window.requestAnimationFrame(tick);
      };
      this.raf = window.requestAnimationFrame(tick);
    }

    // ---- the gestures
    over(node) { return !!(this.target && node && this.target.contains(node)); }

    onWheel(e) {
      if (!e.ctrlKey) return;
      var s = this.settings();
      if (this.over(e.target)) {
        e.preventDefault();
        var d = e.deltaY * (e.deltaMode === 1 ? 33 : (e.deltaMode === 2 ? 400 : 1));
        this.zoomBy(Math.exp(-d * WHEEL_RATE), e.clientX, e.clientY);
      } else if (s.guard) {
        e.preventDefault();
      }
    }

    onKey(e) {
      if (!(e.ctrlKey || e.metaKey) || e.altKey) return;
      var k = e.key, code = e.code;
      var plus = k === '+' || k === '=' || code === 'NumpadAdd';
      var minus = k === '-' || k === '_' || code === 'NumpadSubtract';
      var zero = k === '0' || code === 'Numpad0';
      if (!(plus || minus || zero) || !this.target) return;
      e.preventDefault();
      if (zero) this.zoomTo(1);
      else this.zoomBy(plus ? STEP : 1 / STEP);
    }

    // Two finger pinch from touch events: the distance between the fingers drives the zoom, their midpoint
    // is the point that stays put.
    onTouch(e) {
      var s = this.settings(), over = this.over(e.target);
      if (e.touches && e.touches.length >= 2) {
        if (over || s.guard) e.preventDefault();
        if (!over) return;
        var a = e.touches[0], b = e.touches[1];
        var dist = Math.hypot(a.clientX - b.clientX, a.clientY - b.clientY);
        if (this.touchPrev && dist > 0) {
          this.zoomBy(dist / this.touchPrev, (a.clientX + b.clientX) / 2, (a.clientY + b.clientY) / 2);
        }
        this.touchPrev = dist;
      } else {
        this.touchPrev = null;
      }
    }

    // The same pinch from pointer events (pens, and touch where the browser reports pointers only).
    onPointer(e) {
      if (!this.over(e.target) && !this.pointers.has(e.pointerId)) return;
      if (e.type === 'pointerdown' || e.type === 'pointermove') {
        // a mouse never pinches; a touch pinch is read from touch events where the browser has them
        if (e.pointerType === 'mouse' || (e.pointerType === 'touch' && TOUCH)) return;
        if (e.type === 'pointermove' && !this.pointers.has(e.pointerId)) return;
        this.pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
        if (this.pointers.size === 2) {
          var pts = Array.from(this.pointers.values());
          var dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
          if (this.pointerPrev && dist > 0 && e.type === 'pointermove') {
            this.zoomBy(dist / this.pointerPrev, (pts[0].x + pts[1].x) / 2, (pts[0].y + pts[1].y) / 2);
          }
          this.pointerPrev = dist;
        }
      } else {
        this.pointers.delete(e.pointerId);
        if (this.pointers.size < 2) this.pointerPrev = null;
      }
    }

    // Safari reports a pinch as gesture events that zoom the page unless prevented.
    onGesture(e) {
      if (this.settings().guard || this.over(e.target)) e.preventDefault();
    }

    // ---- life cycle
    listen(node, type, handler, options) {
      node.addEventListener(type, handler, options);
      this.listeners.push([node, type, handler, options]);
    }

    attach() {
      this.detach();
      var s = this.settings();
      this.target = document.getElementById(s.id);
      var self = this;
      var wheel = function (e) { self.onWheel(e); };
      var key = function (e) { self.onKey(e); };
      var touch = function (e) { self.onTouch(e); };
      var pointer = function (e) { self.onPointer(e); };
      var gesture = function (e) { self.onGesture(e); };
      // non-passive and in the capture phase, so that preventDefault is honoured before Perspective's handlers
      var opt = { passive: false, capture: true };
      this.listen(document, 'wheel', wheel, opt);
      this.listen(document, 'keydown', key, opt);
      if (TOUCH) {     // a non-passive touch listener makes the browser wait for it, so only where there is touch
        this.listen(document, 'touchstart', touch, opt);
        this.listen(document, 'touchmove', touch, opt);
        this.listen(document, 'touchend', touch, opt);
        this.listen(document, 'touchcancel', touch, opt);
      }
      this.listen(document, 'pointerdown', pointer, opt);
      this.listen(document, 'pointermove', pointer, opt);
      this.listen(document, 'pointerup', pointer, opt);
      this.listen(document, 'pointercancel', pointer, opt);
      this.listen(document, 'gesturestart', gesture, opt);
      this.listen(document, 'gesturechange', gesture, opt);
      if (this.target) {
        // the browser keeps one finger scrolling and gives the pinch to the script
        this.touchAction = this.target.style.touchAction;
        this.target.style.touchAction = 'pan-x pan-y';
        this.measured = null;
        if (typeof window.ResizeObserver === 'function') {
          this.resizer = new window.ResizeObserver(function () { self.measure(); });
          this.resizer.observe(this.target);
        }
        this.measure();
      }
      this.guarded = s.guard;
      if (s.guard && TOUCH) {
        var m = viewportMeta(true);
        this.metaSaved = { meta: m, content: m.getAttribute('content'), made: m.hasAttribute('data-cadre-zoom') };
        var c = (m.getAttribute('content') || 'width=device-width, initial-scale=1').replace(/,?\s*maximum-scale=[^,]*/i, '');
        m.setAttribute('content', c + ', maximum-scale=1');
      }
    }

    detach() {
      this.listeners.forEach(function (l) { l[0].removeEventListener(l[1], l[2], l[3]); });
      this.listeners = [];
      if (this.resizer) { this.resizer.disconnect(); this.resizer = null; }
      if (this.raf) { window.cancelAnimationFrame(this.raf); this.raf = 0; }
      this.anchor = null;
      this.pointers.clear();
      this.touchPrev = null;
      this.pointerPrev = null;
      if (this.target && this.touchAction !== null) this.target.style.touchAction = this.touchAction;
      this.touchAction = null;
      this.target = null;
      var ms = this.metaSaved;
      if (ms) {
        if (ms.made) { if (ms.meta.parentNode) ms.meta.parentNode.removeChild(ms.meta); }
        else if (ms.content === null) ms.meta.removeAttribute('content');
        else ms.meta.setAttribute('content', ms.content);
        this.metaSaved = null;
      }
    }

    componentDidMount() { this.attach(); }

    componentDidUpdate() {
      var s = this.settings();
      var t = document.getElementById(s.id);
      // the target or the guard changed, or the target was drawn after this component
      if (t !== this.target || this.guarded !== s.guard) this.attach();
    }

    componentWillUnmount() { this.detach(); }

    // Draws nothing: a zero sized, hidden box that takes no part in the layout and catches no pointer.
    render() {
      var e = this.props.emit ? this.props.emit() : {};
      var style = Object.assign({}, e.style, { position: 'absolute', left: 0, top: 0, width: 0, height: 0,
                                               overflow: 'hidden', visibility: 'hidden', pointerEvents: 'none' });
      return h('div', Object.assign({}, e, { style: style }));
    }
  }

  PC.ComponentRegistry.register({
    getComponentType: function () { return TYPE; },
    getViewComponent: function () { return CanvasZoom; },
    getDefaultSize: function () { return { width: 1, height: 1 }; },
    getPropsReducer: function (tree) {
      return {
        zoom: tree.readNumber('zoom', 1),
        min: tree.readNumber('min', 0.5),
        max: tree.readNumber('max', 4),
        targetDomId: tree.readString('targetDomId', 'cadre-canvas'),
        guardBrowserZoom: tree.readBoolean('guardBrowserZoom', true),
        viewWidth: tree.readNumber('viewWidth', 0),
        viewHeight: tree.readNumber('viewHeight', 0)
      };
    }
  });
})();
