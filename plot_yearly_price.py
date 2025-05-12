import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from pathlib import Path
from Utils.dataUtil import get_stock_data
import platform

# 根据操作系统设置中文字体
system = platform.system()
if system == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
elif system == 'Linux':  # Ubuntu
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
plt.rcParams['axes.unicode_minus'] = False

# 创建缓存目录
CACHE_DIR = Path('stock_data_cache')
CACHE_DIR.mkdir(exist_ok=True)

def get_cache_path(stock_code, date):
    """
    获取缓存文件路径
    
    Args:
        stock_code (str): 股票代码
        date (str): 日期字符串，格式为'YYYY-MM-DD'
    
    Returns:
        Path: 缓存文件路径
    """
    return CACHE_DIR / f"{stock_code}_{date}.pkl"

def plot_yearly_price_comparison(stock_code, stock_data, dividend_data):
    """
    绘制过去5年的价格走势对比图，并标记股权登记日
    """
    plt.figure(figsize=(15, 8))

    # 获取上证指数数据
    index_data = get_stock_data('1.000001')  # 修改为正确的上证指数代码
    # 确保上证指数数据使用正确的点位
    if '收盘' in index_data.columns:
        index_data['收盘'] = index_data['收盘']  # 不需要乘以1000，因为数据已经是正确的点位
    
    # 获取股票数据中的所有年份
    years = dividend_data['报告期'].dt.year.unique()
    
    # 确保包含当前年份
    current_year = pd.Timestamp.now().year
    if current_year not in years:
        years = np.append(years, current_year)
    
    # 使用更鲜明的颜色组合
    colors = ['#FF0000', '#00FF00', '#0000FF', '#FFA500', '#800080', '#008080']  # 红、绿、蓝、橙、紫、青
    if len(years) > len(colors):
        colors = colors * (len(years) // len(colors) + 1)  # 确保颜色足够使用

    # 创建两个子图
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12), height_ratios=[2, 1])
    
    # 对每一年的数据进行处理
    for year, color in zip(years, colors):
        # 获取该年的股票数据
        year_data = stock_data[stock_data['日期'].dt.year == year].copy()
        
        if not year_data.empty:
            # 将日期转换为一年中的天数（1-366）
            year_data['day_of_year'] = year_data['日期'].dt.dayofyear
            
            # 计算股票价格的相对变化（以年初为基准）
            first_price = year_data['收盘'].iloc[0]
            year_data['price_change'] = (year_data['收盘'] / first_price - 1) * 100
            
            # 绘制该年的价格曲线
            ax1.plot(year_data['day_of_year'], year_data['收盘'], 
                    label=f'{year}年', color=color, alpha=0.8, linewidth=2)
            
            # 获取该年的上证指数数据
            year_index = index_data[index_data['日期'].dt.year == year].copy()
            if not year_index.empty:
                year_index['day_of_year'] = year_index['日期'].dt.dayofyear
                # 绘制指数实际点位
                ax2.plot(year_index['day_of_year'], year_index['收盘'],
                        label=f'{year}年上证指数', color=color, alpha=0.8, linewidth=2)
            
            # 获取该年的股权登记日
            year_dividend = dividend_data[dividend_data['报告期'].dt.year == year]
            if not year_dividend.empty:
                register_date = pd.to_datetime(year_dividend['股权登记日'].iloc[0])
                if pd.notna(register_date):
                    day_of_year = register_date.dayofyear
                    # 获取股权登记日的收盘价
                    price_on_date = stock_data[stock_data['日期'] == register_date]['收盘']
                    if not price_on_date.empty:
                        price_on_date = price_on_date.iloc[0]
                        
                        # 标记股权登记日
                        ax1.scatter(day_of_year, price_on_date, 
                                marker='*', s=200, color=color, 
                                label=f'{year}年股权登记日')
                        
                        # 添加垂直虚线
                        ax1.axvline(x=day_of_year, color=color, linestyle='--', alpha=0.3)

    # 设置x轴刻度为月份
    months = pd.date_range(start=f'{years[0]}-01-01', end=f'{years[0]}-12-31', freq='M')
    month_ticks = [d.dayofyear for d in months]
    month_labels = [d.strftime('%m月') for d in months]
    
    for ax in [ax1, ax2]:
        ax.set_xticks(month_ticks)
        ax.set_xticklabels(month_labels, rotation=45)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

    # 设置标题和轴标签
    ax1.set_title('过去5年价格走势及股权登记日对比')
    ax1.set_xlabel('月份')
    ax1.set_ylabel('价格')
    
    ax2.set_title('上证指数走势')
    ax2.set_xlabel('月份')
    ax2.set_ylabel('指数值')

    # 设置上证指数y轴的格式
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: '{:,.0f}'.format(x)))
    
    # 调整布局
    plt.tight_layout()

    # 保存图片
    saveImagePath = f'static/yearly_price_comparison_{stock_code}.png'
    plt.savefig(saveImagePath, bbox_inches='tight')
    plt.close()
    return saveImagePath

def main():
    """
    主函数：读取数据并绘制图表
    """
    # 读取数据
    df = pd.read_csv('out/dividend_analysis_result.csv')
    df['报告期'] = pd.to_datetime(df['报告期'])
    
    stock_code = '600755'
    # 使用 get_stock_data 获取股票数据
    stock_data = get_stock_data(stock_code)  # 使用默认的股票代码
    
    # 绘制图表
    saveImagePath = plot_yearly_price_comparison(stock_code,stock_data, df)
    print(f"图表已保存为 {saveImagePath}")

if __name__ == "__main__":
    main()