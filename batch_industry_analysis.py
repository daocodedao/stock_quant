import pandas as pd
import baostock as bs

def get_stock_industry(stock_code):
    """
    获取股票的行业信息
    
    Args:
        stock_code (str): 股票代码
    
    Returns:
        dict: 包含股票代码、名称和行业信息的字典
    """
    try:
        # 处理股票代码格式
        queryCode = f"sh.{stock_code}" if stock_code.startswith('6') else f"sz.{stock_code}"
        
        # 获取股票基本信息
        rs = bs.query_stock_basic(code=queryCode)
        if rs.error_code != '0':
            return None
        
        stock_info = rs.get_data()
        if stock_info.empty:
            return None
            
        stock_name = stock_info['code_name'].iloc[0]
        
        # 获取行业信息
        rs_industry = bs.query_stock_industry(code=queryCode)
        industry = '未知'
        
        while (rs_industry.error_code == '0') & rs_industry.next():
            row = rs_industry.get_row_data()
            if row[4] == '证监会行业分类':  # 使用证监会行业分类
                industry = row[3]
                break
                
        return {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'industry': industry
        }
        
    except Exception as e:
        print(f"获取{stock_code}信息时发生错误：{e}")
        return None

def main():
    # 股票代码列表
    stock_codes = [
        '601919', '601717', '000651', '600096', '600546', '601225', '688516', 
        '600502', '601166', '601001', '600188', '601598', '600985', '601857', 
        '000001', '600008', '300441', '600582', '601336', '600036', '002532', 
        '601998', '600015', '601818', '601328', '601898', '601318', '600970', 
        '000933', '000685', '600016', '601658', '601939', '002839', '600741', 
        '601288', '601668', '601398', '600820', '601988', '600795', '600938', 
        '600219', '002128', '605090', '002788', '603368', '002478', '600704', 
        '300761', '000543', '601156', '600000', '600998', '600064', '600888', 
        '603619', '600035', '002714', '600531', '000498', '601186', '600018', 
        '002001', '601601', '600248', '600483', '601518', '603357', '002061', 
        '600269'
    ]
    
    # 登录系统
    bs.login()
    
    try:
        # 获取所有股票的行业信息
        results = []
        for code in stock_codes:
            info = get_stock_industry(code)
            if info:
                results.append(info)
            
        # 创建DataFrame并保存为CSV
        if results:
            df = pd.DataFrame(results)
            df.columns = ['股票代码', '股票名称', '所属行业']
            df.to_csv('out/stock_industry_analysis.csv', index=False, encoding='utf-8-sig')
            print("行业分析结果已保存到 out/stock_industry_analysis.csv")
        else:
            print("未获取到任何股票信息")
            
    finally:
        # 退出系统
        bs.logout()

if __name__ == "__main__":
    main()