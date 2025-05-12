# 导入所需的库
import pandas as pd
import akshare as ak
from datetime import datetime, timedelta
import os
from pathlib import Path
from Utils.dataUtil import get_stock_data



def get_dividend_data(stock_code='600755'):
    """
    获取指定股票的分红数据
    
    Args:
        stock_code (str): 股票代码，默认为'600755'
    
    Returns:
        pandas.DataFrame: 包含报告期、公告日期、股权登记日、除权除息日等信息的数据框
    """
    # 使用akshare获取分红数据
    # 注意：akshare需要的股票代码格式可能需要调整
    if stock_code.startswith('6'):
        full_code = f"sh{stock_code}"
    else:
        full_code = f"sz{stock_code}"
    
    try:
        # 获取分红数据，使用正确的方法名
        dividend_data = ak.stock_dividend_cninfo(symbol=full_code)
        # 重命名列以匹配我们的需求
        dividend_data = dividend_data.rename(columns={
            '分红年度': '报告期',
            '预案公告日': '公告日期',
            '股权登记日': '股权登记日',
            '除权除息日': '除权除息日'
        })
        # 选择需要的列
        dividend_data = dividend_data[['报告期', '公告日期', '股权登记日', '除权除息日']]
        return dividend_data
    except Exception as e:
        print(f"获取分红数据时发生错误：{e}")
        return pd.DataFrame(columns=['报告期', '公告日期', '股权登记日', '除权除息日'])

def get_dividend_data_from_baostock(stock_code='600755'):
    """
    获取指定股票的分红数据（过去5年）
    
    Args:
        stock_code (str): 股票代码，默认为'600755'
    
    Returns:
        pandas.DataFrame: 包含报告期、公告日期、股权登记日、除权除息日、分红方案等信息的数据框
    """
    try:
        import baostock as bs
        from datetime import datetime
        
        # 登录系统
        bs.login()
        
        # 获取当前年份
        current_year = datetime.now().year
        
        # 存储所有年份的数据
        all_data_list = []
        queryCode = f"sh.{stock_code}" if stock_code.startswith('6') else f"sz.{stock_code}"
        # 获取过去5年的数据
        for year in range(current_year - 4, current_year + 1):
            # 获取分红数据
            rs = bs.query_dividend_data(code=queryCode, year=year)
            while (rs.error_code == '0') & rs.next():
                all_data_list.append(rs.get_row_data())
        
        # 注销登录
        bs.logout()
        
        # 如果没有数据，返回空DataFrame
        if not all_data_list:
            return pd.DataFrame(columns=['报告期', '公告日期', '股权登记日', '除权除息日', '分红方案(元/股)'])
        
        # 转换为DataFrame
        df = pd.DataFrame(all_data_list, columns=rs.fields)
        
        # 重命名列
        df = df.rename(columns={
            'dividPlanAnnounceDate': '报告期',
            'dividPlanDate': '公告日期',
            'dividRegistDate': '股权登记日',
            'dividOperateDate': '除权除息日',
            'dividCashPsBeforeTax': '分红方案(元/股)'
        })
        
        # 选择需要的列
        df = df[['报告期', '公告日期', '股权登记日', '除权除息日', '分红方案(元/股)']]
        return df
        
    except Exception as e:
        print(f"获取分红数据时发生错误：{e}")
        return pd.DataFrame(columns=['报告期', '公告日期', '股权登记日', '除权除息日', '分红方案(元/股)'])


def analyze_price_around_date(stock_data, target_date, days=30):
    """
    分析指定日期前后一定天数范围内的股价波动情况
    
    Args:
        stock_data (pandas.DataFrame): 股票日线数据
        target_date (str): 目标日期
        days (int): 前后分析的天数范围，默认为30天
    
    Returns:
        dict: 包含目标日期、最高价及其日期、最低价及其日期的字典，如果无数据则返回None
    """
    if pd.isna(target_date):
        return None
    
    target_date = pd.to_datetime(target_date)
    start_date = target_date - timedelta(days=days)
    end_date = target_date + timedelta(days=days)
    
    # 获取日期范围内的数据
    mask = (stock_data['日期'] >= start_date) & (stock_data['日期'] <= end_date)
    period_data = stock_data[mask]
    
    if len(period_data) == 0:
        return None
    
    # 获取最高价和最低价及其对应日期
    highest_price_row = period_data.loc[period_data['最高'].idxmax()]
    lowest_price_row = period_data.loc[period_data['最低'].idxmin()]
    
    return {
        '目标日期': target_date.strftime('%Y/%m/%d'),
        '最高价': highest_price_row['最高'],
        '最高价日期': highest_price_row['日期'].strftime('%Y/%m/%d'),
        '最低价': lowest_price_row['最低'],
        '最低价日期': lowest_price_row['日期'].strftime('%Y/%m/%d')
    }

def get_year_price_range(stock_data, report_date):
    """
    获取报告期对应的上一个自然年的股价最高价和最低价
    
    Args:
        stock_data (pandas.DataFrame): 股票日线数据
        report_date (str): 报告期日期
    
    Returns:
        dict: 包含年内最高价和最低价及其对应日期的字典
    """
    if pd.isna(report_date):
        return None
        
    # 将报告期转换为datetime对象
    report_date = pd.to_datetime(report_date)
    
    # 获取报告期的上一年的起始日期和结束日期
    year = report_date.year - 1
    start_date = pd.to_datetime(f"{year}-01-01")
    end_date = pd.to_datetime(f"{year}-12-31")
    
    # 获取指定日期范围内的数据
    mask = (stock_data['日期'] >= start_date) & (stock_data['日期'] <= end_date)
    year_data = stock_data[mask]
    
    if len(year_data) == 0:
        return None
    
    # 获取最高价和最低价及其对应日期
    highest_price_row = year_data.loc[year_data['最高'].idxmax()]
    lowest_price_row = year_data.loc[year_data['最低'].idxmin()]
    
    return {
        '年内最高价': highest_price_row['最高'],
        '年内最高价日期': highest_price_row['日期'].strftime('%Y/%m/%d'),
        '年内最低价': lowest_price_row['最低'],
        '年内最低价日期': lowest_price_row['日期'].strftime('%Y/%m/%d')
    }

def dividend_analysis_main(stock_code='600755'):
    """
    主函数：分析股票在分红相关日期前后的价格波动情况
    """

    # 获取分红数据
    dividend_data = get_dividend_data_from_baostock(stock_code=stock_code)
    # 获取股票数据
    stock_data = get_stock_data(stock_code=stock_code)
    
    # 准备CSV数据
    csv_data = []
    
    # 分析每个重要日期前后的价格变动
    for _, row in dividend_data.iterrows():
        report_period = row['报告期']
        
        # 获取年内价格范围（基于报告期的上一个自然年）
        year_price_range = get_year_price_range(stock_data, report_period)
        if not year_price_range:
            continue
            
        # 分析三个重要日期
        dates = {
            '公告日期': row['公告日期'],
            '股权登记日': row['股权登记日'],
            '除权除息日': row['除权除息日']
        }
        
        # 计算股息率
        # 获取股权登记日前一天的收盘价
        register_date = pd.to_datetime(row['股权登记日'])
        if not pd.isna(register_date):
            prev_day = register_date - timedelta(days=1)
            prev_day_data = stock_data[stock_data['日期'] == prev_day]
            if not prev_day_data.empty:
                prev_close = prev_day_data.iloc[0]['收盘']
                # 修改这里的类型转换逻辑
                try:
                    dividend_str = str(row['分红方案(元/股)']).strip()
                    dividend_amount = float(dividend_str) if dividend_str else 0
                except (ValueError, TypeError):
                    dividend_amount = 0
                dividend_yield = (dividend_amount / prev_close * 100) if prev_close > 0 else 0
                dividend_yield = round(dividend_yield, 2)
            else:
                dividend_yield = None
        else:
            dividend_yield = None
        
        record = {
            '报告期': report_period,
            '分红方案(元/股)': row['分红方案(元/股)'],
            '股息率(%)': dividend_yield,
            '年内最高价': year_price_range['年内最高价'],
            '年内最高价日期': year_price_range['年内最高价日期'],
            '年内最低价': year_price_range['年内最低价'],
            '年内最低价日期': year_price_range['年内最低价日期']
        }
        
        # 添加各个重要日期的分析结果
        for date_type, date in dates.items():
            analysis = analyze_price_around_date(stock_data, date)
            if analysis:
                record.update({
                    f'{date_type}': analysis['目标日期'],
                    f'{date_type}_最高价': analysis['最高价'],
                    f'{date_type}_最高价日期': analysis['最高价日期'],
                    f'{date_type}_最低价': analysis['最低价'],
                    f'{date_type}_最低价日期': analysis['最低价日期']
                })
        
        csv_data.append(record)
    
    # 将结果保存为CSV文件
    if csv_data:
        df = pd.DataFrame(csv_data)
        saveFilePath = f'out/dividend_analysis_result_{stock_code}.csv'
        df.to_csv(saveFilePath, index=False, encoding='utf-8-sig')
        print(f"分析结果已保存到 {saveFilePath}")
        return saveFilePath
    else:
        print("没有找到可分析的数据")
        return None

if __name__ == "__main__":
    dividend_analysis_main()