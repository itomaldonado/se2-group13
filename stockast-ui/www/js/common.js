//  base64转码
const Base64 = {
  _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
  encode: function(e) {
    let t = "";
    let n, r, i, s, o, u, a;
    let f = 0;
    e = Base64._utf8_encode(e);
    while (f < e.length) {
      n = e.charCodeAt(f++);
      r = e.charCodeAt(f++);
      i = e.charCodeAt(f++);
      s = n >> 2;
      o = ((n & 3) << 4) | (r >> 4);
      u = ((r & 15) << 2) | (i >> 6);
      a = i & 63;
      if (isNaN(r)) {
        u = a = 64;
      } else if (isNaN(i)) {
        a = 64;
      }
      t =
        t +
        this._keyStr.charAt(s) +
        this._keyStr.charAt(o) +
        this._keyStr.charAt(u) +
        this._keyStr.charAt(a);
    }
    return t;
  },
  decode: function(e) {
    let t = "";
    let n, r, i;
    let s, o, u, a;
    let f = 0;
    e = e.replace(/[^A-Za-z0-9+/=]/g, "");
    while (f < e.length) {
      s = this._keyStr.indexOf(e.charAt(f++));
      o = this._keyStr.indexOf(e.charAt(f++));
      u = this._keyStr.indexOf(e.charAt(f++));
      a = this._keyStr.indexOf(e.charAt(f++));
      n = (s << 2) | (o >> 4);
      r = ((o & 15) << 4) | (u >> 2);
      i = ((u & 3) << 6) | a;
      t = t + String.fromCharCode(n);
      if (u != 64) {
        t = t + String.fromCharCode(r);
      }
      if (a != 64) {
        t = t + String.fromCharCode(i);
      }
    }
    t = Base64._utf8_decode(t);
    return t;
  },
  _utf8_encode: function(e) {
    e = e.replace(/rn/g, "n");
    let t = "";
    for (let n = 0; n < e.length; n++) {
      let r = e.charCodeAt(n);
      if (r < 128) {
        t += String.fromCharCode(r);
      } else if (r > 127 && r < 2048) {
        t += String.fromCharCode((r >> 6) | 192);
        t += String.fromCharCode((r & 63) | 128);
      } else {
        t += String.fromCharCode((r >> 12) | 224);
        t += String.fromCharCode(((r >> 6) & 63) | 128);
        t += String.fromCharCode((r & 63) | 128);
      }
    }
    return t;
  },
  _utf8_decode: function(e) {
    let t = "";
    let n = 0;
    let r = (c1 = c2 = 0);
    while (n < e.length) {
      r = e.charCodeAt(n);
      if (r < 128) {
        t += String.fromCharCode(r);
        n++;
      } else if (r > 191 && r < 224) {
        c2 = e.charCodeAt(n + 1);
        t += String.fromCharCode(((r & 31) << 6) | (c2 & 63));
        n += 2;
      } else {
        c2 = e.charCodeAt(n + 1);
        c3 = e.charCodeAt(n + 2);
        t += String.fromCharCode(
          ((r & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63)
        );
        n += 3;
      }
    }
    return t;
  }
};

let account = localStorage.getItem('account');
let password = localStorage.getItem('password');
let author = `${account}:${password}`;
let Base = {
  url:'https://stockast.itomaldonado.com/',//请求地址
  api:'api/',//请求二级地址
}
function commonAxios(type, url, params) {
  //  get delete -- params
  if (type.toUpperCase() == "GET") {
    // || type.toUpperCase() == "DELETE"
	console.log(localStorage.getItem('account') , localStorage.getItem('password'), `Basic ${Base64.encode(localStorage.getItem('account') +':'+ localStorage.getItem('password'))}` )
      return axios({
        method: type,
        url: `${Base.url}${Base.api}${url}`,
        params: params,
        headers: {
          "Content-Type": "application/json",
          "Authorization": localStorage.getItem('account') && localStorage.getItem('password')? `Basic ${Base64.encode(localStorage.getItem('account') +':'+ localStorage.getItem('password'))}` : '',
          //"Authorization": 'Basic c29tZW9uZUBleGFtcGxlLmNvbToxMjM0',
        }
      });
  } else {
    //  put post -- data
    return axios({
      method: type,
      url: `${Base.url}${Base.api}${url}`,
      data: params,
      headers: {
        "Content-Type": "application/json",
        "Authorization": localStorage.getItem('account') && localStorage.getItem('password')? `Basic ${Base64.encode(localStorage.getItem('account') +':'+ localStorage.getItem('password'))}` : '',
          //"Authorization": 'Basic c29tZW9uZUBleGFtcGxlLmNvbToxMjM0',
      }
    });
  }
}
const msgDuration = 1500;//$message关闭时间
// User
const User = {
  //  Follows -- List New
  Follows : (type, params, user_id)=>{
    return commonAxios(type, `users/${user_id}/follows`, params)
  },
  //  Follows -- Single Remove
  FollowsSingle : (type, params, user_id, symbol)=>{
    return commonAxios(type, `users/${user_id}/follows/${symbol}`, params)
  },
  //  UserLogin
  UserLogin : (params)=>{
    return commonAxios('get', 'login', params)
  },
  //  User -- List New Single Update
  User : (type, params, user_id)=>{
    return commonAxios(type, `users${user_id?'/'+user_id:''}`, params)
  }
}

// Companies
const Companies = {
  //  Company -- List New Single
  CompanyList : (type, params, symbol)=>{
    return commonAxios(type, `companies${symbol?'/'+symbol:''}`, params)
  }
}

// Stocks
const Stocks = {
  //  StocksHistorySearch
  StocksHistorySearch : (params)=>{
    return commonAxios('get', 'stocks/history', params)
  },
  //  StocksRealtime Search
  StocksRealtimeSearch : (params)=>{
    return commonAxios('get', 'stocks/realtime', params)
  },
}

//	Predictions
const Predictions = {
  Predictions_short : (params, symbol)=>{
    return commonAxios('get', `predict/short${symbol?'/'+symbol:''}`, params)
  },
  Predictions_long : (params, symbol)=>{
    return commonAxios('get', `predict/long${symbol?'/'+symbol:''}`, params)
  },
}

// stocks
const stockinformation = {
  //  StocksHistorySearch
  StocksHistorySearch : (params)=>{
    return commonAxios('get', 'stocks/history', params)
  },
  //  StocksRealtime Search
  StocksRealtimeSearch : (params)=>{
    return commonAxios('get', 'stocks/realtime', params)
  },
}