// /src/main.js

import React, { Component } from 'react';
import axios from 'axios';
import logo from './logo.svg';
import { Link, Route } from 'react-router-dom';
import { List, InputItem } from 'antd-mobile';
import { Navbar } from './navbar';
import { Dashboard } from './pages/dashboard';
import './main.css';

function LoginButton(props) {
  return (
    <button onClick={props.onClick}>
      Login
    </button>
  );
}

function LogoutButton(props) {
  return (
    <button onClick={props.onClick}>
      Logout
    </button>
  );
}

class Main extends Component {
  constructor(props) {
    super(props);
    this.handleLoginClick = this.handleLoginClick.bind(this);
    this.handleLogoutClick = this.handleLogoutClick.bind(this);
    this.state = { isLoggedIn: false, name: "", passwd: "", msg: "" };
  }

  // 按下F5重新整理後，此處可讓頁面維持在登入狀態。
  componentDidMount() {
    const _this = this;
    if ("access_token" in sessionStorage) {
      let access_token = sessionStorage.getItem("access_token")
      axios.defaults.headers.common['Authorization'] = 'Bearer ' + access_token;
      _this.setState({ isLoggedIn: true });
    }
  }

  // antd-mobile的InputItem必須用List元件包裹，其輸入值就是value
  username = value => {
    this.setState({
      name: value
    });
  };

  password = value => {
    this.setState({
      passwd: value
    });
  };

  handleLoginClick() {
    const _this = this;
    _this.setState({ msg: "Logining" })
    axios.post('/api/auth/login', { username: _this.state.name, password: _this.state.passwd })
      .then(function (response) {
        console.log(response.data);
        axios.defaults.headers.common['Authorization'] = 'Bearer ' + response.data.access_token;
        _this.setState({ isLoggedIn: true });
        _this.setState({ msg: response.data.msg });
        sessionStorage.setItem("access_token", response.data.access_token);
      })
      .catch(function (error) {
        _this.setState({ isLoggedIn: false });
        _this.setState({ msg: error.response.data.msg });
        delete axios.defaults.headers.common['Authorization'];
        sessionStorage.removeItem("access_token");
        console.log(error);
      });
  }

  handleLogoutClick() {
    this.setState({ isLoggedIn: false });
    delete axios.defaults.headers.common['Authorization'];
    sessionStorage.removeItem("access_token");
  }

  render() {
    let isLoggedIn = this.state.isLoggedIn;
    const msg = this.state.msg;

    if (isLoggedIn) {
      return (
        <div className="container">
          {/* The corresponding component will show here if the current URL matches the path */}
          <nav className="navbar navbar-expand-sm navbar-light bg-light">
            <Link className="navbar-brand" to="/">
              <img src={logo} alt="react-router-breadcrumb" width="30" height="30" />
            </Link>
            <button
              className="navbar-toggler"
              type="button"
              data-toggle="collapse"
              data-target="#navbarContent"
              aria-controls="navbarContent"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon" />
            </button>
            <div className="collapse navbar-collapse" id="navbarContent">
              <Navbar />
              <LogoutButton onClick={this.handleLogoutClick} />
            </div>
          </nav>
          <Route path="/" exact component={Dashboard} />
          {/* <pre>{JSON.stringify(this.state, null, 2)}</pre> */}
        </div >
      );
    } else {
      return (
        <div className="container">
          <nav className="navbar navbar-expand-sm navbar-light bg-light" >
            <Link className="navbar-brand" to="/">
              <img src={logo} alt="react-router-breadcrumb" width="30" height="30" />
            </Link>
            <button
              className="navbar-toggler"
              type="button"
              data-toggle="collapse"
              data-target="#navbarContent"
              aria-controls="navbarContent"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon" />
            </button>
            <div className="collapse navbar-collapse" id="navbarContent">
              <ul className="navbar-nav">
                <List>
                  <InputItem
                    type="text"
                    placeholder="Please input user name..."
                    onChange={this.username}
                    value={this.state.name}
                  />
                  <InputItem
                    type="password"
                    placeholder="Please input password..."
                    onChange={this.password}
                    value={this.state.passwd}
                  />
                  <LoginButton onClick={this.handleLoginClick} />
                  <br></br>
                  {msg}
                </List>
              </ul>
            </div>
          </nav>
          {/* <pre>{JSON.stringify(this.state, null, 2)}</pre> */}
        </div>
      );
    }
  }
}

export default Main;
