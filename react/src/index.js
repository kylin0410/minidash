// /src/index.js

import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter, Switch } from 'react-router-dom';
import './index.css';
import Main from './main';
import * as serviceWorker from './serviceWorker';
import axios from 'axios';

// Add a 401 response interceptor
axios.interceptors.response.use(function (response) {
  return response;
}, function (error) {
  if (401 === error.response.status) {
    delete axios.defaults.headers.common['Authorization'];
    sessionStorage.removeItem("access_token");
    window.location = "/";
  } else {
    return Promise.reject(error);
  }
});

ReactDOM.render(
  <BrowserRouter>
    <Switch>
      <Main />
    </Switch>
  </BrowserRouter>,
  document.getElementById('root')
);

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
