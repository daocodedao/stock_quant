<!--
 * @Author       : adolf
 * @Date         : 2022-11-18 00:21:42
 * @LastEditors  : adolf adolf1321794021@gmail.com
 * @LastEditTime : 2022-11-18 00:21:42
 * @FilePath     : /stock_quant/README.md
-->
# stock_quant

用于股票量化策略的研究，欢迎一起讨论交流。目前主要针对择时和择股两种策略的回测框架进行开发，因对缠论较为感兴趣，对缠论有单独的代码进行开发。

## TODO LIST

- [x] 支持工业板块的历史数据获取
- [ ] 支持概念板块的历史数据获取
- [ ] 完善缠论对股票的分析
- [x] 开发选股策略基本回测框架
- [x] 优化回测代码交易核心代码部分
- [ ] 构建多机器分布式机器学习框架

## 项目的安装

### 1.1 安装项目的依赖

```bash
brew install ta-lib
pip install poetry
poetry install
```

## 项目的基础设定

### 2.1 用于控制台使用代理

```bash
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
```

### 2.2 设置python运行路径

```bash
export PYTHONPATH=$(pwd):$PYTHONPATH
```

### 2.3 设置python不生成pyc(__pycache__)

```bash
export PYTHONDONTWRITEBYTECODE=1
```

### 2.4 国内配置github的真实ip

- 通过网址```https://ipaddress.com/website/github.com```获取到github的真实ip
- 通过修改```sudo vi /etc/hosts```文件，向其中添加```140.82.112.4 github.com```
- 安装nscd,如果已经安装了忽略。centos使用```sudo yum install -y nscd```
- 刷新本地dns缓存```service nscd restart```
- 备选刷新dns缓存命令```sudo /etc/init.d/nscd restart```

## 获取需要使用到的基本数据

### 3.1 获取基础股票数据

&nbsp; 从东方财富官网获取个股的历史数据，包含前复权，后复权，未复权。

```bash
python GetBaseData/get_dc_data.py
```

### 3.2 获取基础的个股资金流量数据

&nbsp; 从东方财富官网获取不同股票的近100日的超大、大、中、小单数据变化。

```bash
python GetBaseData/get_cash_flow_data.py
```

### 3.3 获取不同板块的历史数据

&nbsp; 从东方财富官网获取板块的历史数据。
目前仅支持行业板块，暂不支持概念板块的数据

```bash
python GetBaseData/get_board_data.py
```

## 如果要使用前端展示缠论结果

```bash
streamlit run StrategyLib/ChanStrategy/automatic_drawing.py
```

### frp
```
cat /data/work/frp/frpc.ini 
vim /data/work/frp/frpc.ini


[ssh-stockquant5000]
type = tcp
local_ip = 127.0.0.1
local_port = 5000
remote_port = 5000
use_encryption = false
use_compression = false

# 重启frp
sudo systemctl restart  supervisor
sudo supervisorctl reload
sudo supervisord
```
