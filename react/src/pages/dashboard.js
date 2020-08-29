// /src/pages/dashboard.js

import React from 'react';
import axios from 'axios';

class Dashboard extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            date: new Date(),
            usage: {},
            wired: {},
            version: {},
        };
        const _this = this;
        axios.get('/api/dashboard/usage')
            .then(function (response) {
                _this.setState({
                    usage: response.data
                });
            })
            .catch(function (error) {
                console.log(error);
            });
        axios.get('/api/dashboard/net/wired')
            .then(function (response) {
                _this.setState({
                    wired: response.data
                });
            })
            .catch(function (error) {
                console.log(error);
            });
        axios.get('/api/dashboard/version')
            .then(function (response) {
                _this.setState({
                    version: response.data
                });
            })
            .catch(function (error) {
                console.log(error);
            });
    }

    // 掛載函數
    componentDidMount() {
        this.timerID = setInterval(
            () => this.tick(),
            5000
        );
    }

    // 卸載函數
    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    tick() {
        const _this = this;
        axios.get('/api/dashboard/usage')
            .then(function (response) {
                _this.setState({
                    usage: response.data
                });
            })
            .catch(function (error) {
                console.log(error);
            });
        _this.setState({
            date: new Date()
        });
    }

    render() {
        const { usage, wired, version, log_url } = this.state;
        return (
            <div>
                <h4>Usage Information:</h4>
                <table>
                    <tr><td width="160" align="right">CPU usage</td><td width="120" align="right">{usage.cpu}%</td></tr>
                    <tr><td width="160" align="right">MEM usage</td><td width="120" align="right">{usage.mem}%</td></tr>
                    <tr><td width="160" align="right">SWAP usage</td><td width="120" align="right">{usage.swap}%</td></tr>
                    <tr><td width="160" align="right">File system usage</td><td width="120" align="right">{usage.fs}%</td></tr>
                </table>
                <h4>Network Information:</h4>
                <table>
                    <tr><td width="160" align="right">IP Address</td><td width="150" align="right">{wired.ipv4_addr}</td></tr>
                    <tr><td width="160" align="right">Subnet Mask</td><td width="150" align="right">{wired.ipv4_mask}</td></tr>
                    <tr><td width="160" align="right">MAC Address</td><td width="150" align="right">{wired.mac_addr}</td></tr>
                </table>
                <h4>Version Information:</h4>
                <table>
                    <tr><td width="160" align="right">Build datetime</td><td width="220" align="right">{version.build_ver}</td></tr>
                </table>
                {/* <pre>{JSON.stringify(this.state, null, 2)}</pre> */}
            </div>
        );
    }
}

export { Dashboard };
