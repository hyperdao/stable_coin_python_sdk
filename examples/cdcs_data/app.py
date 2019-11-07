from flask import Flask, render_template
from pyecharts.charts import Bar,Line,Page,Grid,Tab,Liquid,Gauge,Pie
from pyecharts import options as opts
from cdc_charts_data import Cdc_Charts_Data

app = Flask(__name__, static_folder="templates")

wallet_rpc_url = 'http://192.168.1.121:30088/'
sqlite_db_path = 'sqlite:///cdcs.db'
time_intervals = {"day":int(60 * 60 * 24 / 5),"week":int(60 * 60 * 24 * 7 / 5),"mounth":int(60 * 60 * 24 * 30 / 5)}
PRESISION = 100000000
token_SYMBOL = "USD"

def get_chart_page(interval):
    bar_cdcSum = Bar()
    bar_cdcCount = Bar()
    barItems = ['opencdc', 'payback', 'expandloan', 'closecdc', 'liquidate']

    if interval not in time_intervals.keys():
        return None

    per_blocks = time_intervals[interval]
    cdb = Cdc_Charts_Data(wallet_rpc_url, sqlite_db_path)

    pies_config = [{"name":"0~10"+token_SYMBOL,"low":0,"hign":10},{"name":"10~100"+token_SYMBOL,"low":10,"hign":100},{"name":"100~1000"+token_SYMBOL,"low":100,"hign":1000},
                   {"name":"1000~10000"+token_SYMBOL,"low":1000,"hign":10000},{"name":"10000~100000"+token_SYMBOL,"low":1000,"hign":100000},{"name":"100000~∞"+token_SYMBOL,"low":100000,"hign":None}]

    pie_attrs = []
    pie_values = []
    for pie_config in pies_config:
        low = pie_config["low"]*PRESISION
        hign = pie_config["hign"]
        if(hign is not None):
            hign = hign*PRESISION
        count = cdb.get_cdc_count_by_tokenAmount_data(low,hign)[0]
        pie_attrs.append(pie_config["name"])
        pie_values.append(count)
    pie = Pie()

    pie.add("",[list(z) for z in zip(pie_attrs, pie_values)])\
        .set_global_opts(title_opts=opts.TitleOpts(title="cdc仓位数量分布图"),legend_opts=opts.LegendOpts(pos_bottom="90%"),)\
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    res = cdb.get_bars_data(per_blocks)

    bar_cdcSum.add_xaxis(res['x_values'])
    bar_cdcCount.add_xaxis(res['x_values'])

    for bitem in barItems:
        bar_cdcSum.add_yaxis(bitem + "_sum", res['y_values_' + bitem + "_sum"], stack="stack1")
        bar_cdcCount.add_yaxis(bitem + "_count", res['y_values_' + bitem + "_count"], stack="stack1")

    bar_cdcSum.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar_cdcSum.set_global_opts(
        title_opts=opts.TitleOpts(title="cdc交易金额统计"),
        legend_opts=opts.LegendOpts(pos_bottom="90%"),
        yaxis_opts=opts.AxisOpts(name="sum（USD)"),
        xaxis_opts=opts.AxisOpts(name="time("+interval+")"),
        datazoom_opts=[opts.DataZoomOpts(type_="inside")]
    )
#,opts.DataZoomOpts(pos_bottom="50%")
    bar_cdcCount.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

    bar_cdcCount.set_global_opts(
        title_opts=opts.TitleOpts(title="cdc交易数量统计"),
        legend_opts = opts.LegendOpts(pos_bottom="90%"),
        yaxis_opts=opts.AxisOpts(name="count"),
        xaxis_opts=opts.AxisOpts(name="time("+interval+")"),
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
    )

    blocks_n = []
    supplys = []

    res = cdb.get_supply_history_data()
    for r in res:
        blocks_n.append(str(r[0]))
        supplys.append(r[1]/100000000)

    line = Line()

    line.add_xaxis(blocks_n)
    line.add_yaxis('supply', supplys,label_opts=opts.LabelOpts(is_show=False),is_step=True)
    line.set_global_opts(title_opts=opts.TitleOpts(title="stable token supply"),
                         yaxis_opts=opts.AxisOpts(name="supply（USD)"),
                         xaxis_opts=opts.AxisOpts(name="block hight"),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")])

    ##################################################################################################
    rate = cdb.get_collateral_rate()
    #rate = Decimal(rate).quantize(Decimal('0.00'))
    c = (
        Liquid()
            .add("lq", [rate])
            .set_global_opts(title_opts=opts.TitleOpts(title="cdc平均抵押率"))
    )
    #rate_per = "%.2f%%" % (rate * 100)

    gauge = Gauge()
    gauge.add("", [("抵押率", rate)], min_=0, max_=4).set_global_opts(title_opts=opts.TitleOpts(title="collateral rate"))

    page = (
        Page()
            .add(bar_cdcCount)
            .add(bar_cdcSum)
            .add(line)
    )

    tab = Tab()
    tab.add(bar_cdcCount, "cdc trx counts")
    tab.add(bar_cdcSum, "cdc trx sums")
    tab.add(line, "stable token supply")
    tab.add(c, "average collateral rate")
    tab.add(pie,"cdc count pie")
    return tab


@app.route("/")
def index():
    r = get_chart_page("day")
    return render_template('index.html',myechart=r.render_embed())



if __name__ == "__main__":
    app.run()