import pandas as pd
import qstock as qs
from datetime import datetime
import pickle
from pathlib import Path

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

def get_stock_data(stock_code='600755', end_date=None):
    """
    获取指定股票的日线数据，支持缓存
    
    Args:
        stock_code (str): 股票代码，默认为'600755'
        end_date (str): 结束日期，格式为'YYYY-MM-DD'，默认为None（使用当前日期）
    
    Returns:
        pandas.DataFrame: 包含日期、最高价、最低价、收盘价等信息的数据框
    """
    # 如果未指定结束日期，使用当前日期
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # 检查缓存
    cache_path = get_cache_path(stock_code, end_date)
    if cache_path.exists():
        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"读取缓存失败：{e}")
    
    # 使用qstock获取股票日线数据
    stock_data = qs.get_data(stock_code, freq='d', end=end_date)
    # 将索引重置为列
    stock_data = stock_data.reset_index()
    # 重命名列以匹配我们的需求
    stock_data = stock_data.rename(columns={
        'date': '日期',
        'high': '最高',
        'low': '最低',
        'close': '收盘'
    })
    stock_data['日期'] = pd.to_datetime(stock_data['日期'])
    
    # 保存到缓存
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(stock_data, f)
    except Exception as e:
        print(f"保存缓存失败：{e}")
    
    return stock_data