from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
from dividend_analysis import get_dividend_data_from_baostock, dividend_analysis_main
from plot_yearly_price import plot_yearly_price_comparison, get_stock_data
import os
from pathlib import Path
import matplotlib
import baostock as bs
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt

app = Flask(__name__)

# 确保输出目录存在
Path('out').mkdir(exist_ok=True)

def get_stock_info(stock_code):
    """
    获取股票的基本信息
    """
    bs.login()
    try:
        queryCode = f"sh.{stock_code}" if stock_code.startswith('6') else f"sz.{stock_code}"
        rs = bs.query_stock_basic(code=queryCode)
        if rs.error_code != '0':
            return None
        data_list = rs.get_data()
        if not data_list.empty:
            # 获取股票最新交易日数据
            rs_latest = bs.query_history_k_data_plus(queryCode,
                "date,close",
                start_date=None,
                end_date=None,
                frequency="d", 
                adjustflag="3")
            
            market_cap = 0
            if rs_latest.error_code == '0':
                latest_data = rs_latest.get_data()
                if not latest_data.empty:
                    latest_close = float(latest_data['close'].iloc[-1])  # 获取最新收盘价
                    # 获取总股本
                    rs_profit = bs.query_profit_data(code=queryCode, year=2023, quarter=4)
                    if rs_profit.error_code == '0':
                        profit_data = rs_profit.get_data()
                        if not profit_data.empty:
                            total_shares = float(profit_data['totalShare'].iloc[0])
                            market_cap = latest_close * total_shares
            
            return {
                'code': stock_code,
                'name': data_list['code_name'].iloc[0],
                'market_cap': f"{market_cap/100000000:.2f}亿" if market_cap > 0 else "未知"
            }
    finally:
        bs.logout()
    return None

@app.route('/')
def index():
    return '''
    <html>
        <head>
            <title>股票分析</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 800px; margin: 0 auto; }
                .form { margin-bottom: 20px; }
                .stock-info { margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
                .stock-info span { margin-right: 20px; }
                img { max-width: 100%; margin-top: 20px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f5f5f5; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>股票分红分析</h1>
                <div class="form">
                    <form action="/analyze" method="post">
                        <label for="stock_code">股票代码：</label>
                        <input type="text" id="stock_code" name="stock_code" value="600755">
                        <button type="submit">分析</button>
                    </form>
                </div>
                <div id="result"></div>
            </div>
        </body>
    </html>
    '''

@app.route('/analyze', methods=['POST'])
def analyze():
    stock_code = request.form.get('stock_code', '600755')
    print(f"stock_code:{stock_code}")
    
    # 获取股票基本信息
    stock_info = get_stock_info(stock_code)
    if not stock_info:
        return '获取股票信息失败，请检查股票代码是否正确'
    
    # 执行分红分析
    cachedFilePath = dividend_analysis_main(stock_code)
    
    # 读取分析结果
    if os.path.exists(cachedFilePath):
        df = pd.read_csv(cachedFilePath)
        df['报告期'] = pd.to_datetime(df['报告期'])
        
        # 获取股票数据并绘制图表
        stock_data = get_stock_data(stock_code)
        saveImagePath = plot_yearly_price_comparison(stock_code, stock_data, df)
        
        # 从路径中获取文件名带后缀
        image_path = Path(saveImagePath)
        image_filename = image_path.name

        # 将DataFrame转换为HTML表格
        table_html = df.to_html(classes='table', index=False)
        
        imgSrc = f"/static/{image_filename}?{image_path.stat().st_mtime}"
        print(imgSrc)
        
        # 返回结果，包含股票基本信息
        return f'''
            <div class="stock-info">
                <span>股票代码：{stock_info['code']}</span>
                <span>股票名称：{stock_info['name']}</span>
                <span>总市值：{stock_info['market_cap']}</span>
            </div>
            <h2>分析结果</h2>
            <h3>分红数据表</h3>
            {table_html}
            <h3>价格走势图</h3>
            <img src={imgSrc}>
        '''
    else:
        return '分析失败，请检查股票代码是否正确'

# 添加静态文件路由
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # 创建static目录用于存放图片
    Path('static').mkdir(exist_ok=True)
    app.run(debug=True, port=5000)