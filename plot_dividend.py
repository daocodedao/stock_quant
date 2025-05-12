import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # macOS系统使用
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('out/dividend_analysis_result.csv')
df['报告期'] = pd.to_datetime(df['报告期'])

# 创建图1：分红方案和股息率趋势
plt.figure(figsize=(12, 6))
ax1 = plt.gca()
ax2 = ax1.twinx()

# 绘制分红方案柱状图
ax1.bar(df['报告期'], df['分红方案(元/股)'], color='skyblue', alpha=0.6, label='分红方案(元/股)')
ax1.set_ylabel('分红方案(元/股)', color='skyblue')

# 绘制股息率折线图
ax2.plot(df['报告期'], df['股息率(%)'], color='red', marker='o', label='股息率(%)')
ax2.set_ylabel('股息率(%)', color='red')

# 设置x轴格式
plt.gcf().autofmt_xdate()
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# 添加图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.title('分红方案和股息率趋势对比')
plt.savefig('dividend_trend.png')
plt.close()

# 创建图2：年内股价波动范围
plt.figure(figsize=(12, 6))
for idx, row in df.iterrows():
    plt.vlines(x=row['报告期'], ymin=row['年内最低价'], ymax=row['年内最高价'], 
               color='blue', alpha=0.5)
    plt.plot(row['报告期'], row['年内最高价'], 'ro')
    plt.plot(row['报告期'], row['年内最低价'], 'go')

plt.gcf().autofmt_xdate()
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.title('年内股价波动范围')
plt.ylabel('股价')
plt.savefig('price_range.png')
plt.close()

# 创建图3：重要日期前后的价格波动箱线图
dates_data = []
for idx, row in df.iterrows():
    year = row['报告期'].year
    for date_type in ['公告日期', '股权登记日', '除权除息日']:
        high = row[f'{date_type}_最高价']
        low = row[f'{date_type}_最低价']
        dates_data.append({
            '日期类型': f"{date_type}\n{year}",  # 添加年份信息
            '价格': high,
            '类型': '最高价'
        })
        dates_data.append({
            '日期类型': f"{date_type}\n{year}",
            '价格': low,
            '类型': '最低价'
        })

dates_df = pd.DataFrame(dates_data)

# 创建图3：按时间顺序展示所有价格数据
plt.figure(figsize=(15, 8))

# 设置颜色方案
colors = {
    '年内': '#1f77b4',
    '公告日期': '#ff7f0e',
    '股权登记日': '#2ca02c',
    '除权除息日': '#d62728'
}

# 按报告期排序
df = df.sort_values('报告期')

# 绘制每个报告期的价格数据
x = range(len(df))
width = 0.2  # 柱状图的宽度

# 绘制年内价格范围
plt.vlines(x, df['年内最低价'], df['年内最高价'], color=colors['年内'], label='年内价格范围', linewidth=2)
plt.scatter(x, df['年内最高价'], color=colors['年内'], marker='^', s=100)
plt.scatter(x, df['年内最低价'], color=colors['年内'], marker='v', s=100)

# 绘制公告日期价格范围
plt.vlines([i+width] for i in x, df['公告日期_最低价'], df['公告日期_最高价'], 
          color=colors['公告日期'], label='公告日期价格范围', linewidth=2)
plt.scatter([i+width for i in x], df['公告日期_最高价'], color=colors['公告日期'], marker='^', s=100)
plt.scatter([i+width for i in x], df['公告日期_最低价'], color=colors['公告日期'], marker='v', s=100)

# 绘制股权登记日价格范围
plt.vlines([i+width*2 for i in x], df['股权登记日_最低价'], df['股权登记日_最高价'], 
          color=colors['股权登记日'], label='股权登记日价格范围', linewidth=2)
plt.scatter([i+width*2 for i in x], df['股权登记日_最高价'], color=colors['股权登记日'], marker='^', s=100)
plt.scatter([i+width*2 for i in x], df['股权登记日_最低价'], color=colors['股权登记日'], marker='v', s=100)

# 绘制除权除息日价格范围
plt.vlines([i+width*3 for i in x], df['除权除息日_最低价'], df['除权除息日_最高价'], 
          color=colors['除权除息日'], label='除权除息日价格范围', linewidth=2)
plt.scatter([i+width*3 for i in x], df['除权除息日_最高价'], color=colors['除权除息日'], marker='^', s=100)
plt.scatter([i+width*3 for i in x], df['除权除息日_最低价'], color=colors['除权除息日'], marker='v', s=100)

# 设置x轴标签
plt.xticks([i+width*1.5 for i in x], df['报告期'].dt.strftime('%Y-%m'), rotation=45)

# 添加图例
plt.legend(loc='upper left')

# 设置标题和轴标签
plt.title('各时期价格波动范围对比')
plt.xlabel('报告期')
plt.ylabel('价格')

# 调整布局
plt.tight_layout()

# 保存图片
plt.savefig('price_range_comparison.png')
plt.close()