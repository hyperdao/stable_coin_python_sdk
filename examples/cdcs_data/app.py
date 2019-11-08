from flask import Flask, render_template
from pyecharts.charts import Bar,Line,Page,Grid,Tab,Liquid,Gauge,Pie
from pyecharts import options as opts
from cdc_charts_data import Cdc_Charts_Data

app = Flask(__name__, static_folder="templates")

wallet_rpc_url = 'http://192.168.1.121:30088/'
sqlite_db_path = 'sqlite:///cdcs.db'
time_intervals = {"day":int(60 * 60 * 24 / 5),"week":int(60 * 60 * 24 * 7 / 5),"mounth":int(60 * 60 * 24 * 30 / 5)}
PRESISION = 100000000
stable_token_SYMBOL = "USD"

cdb = Cdc_Charts_Data(wallet_rpc_url, sqlite_db_path)

def get_cdc_trx_counts_sums_bars(interval="week"):
    bar_cdcSum = Bar()
    bar_cdcCount = Bar()
    barItems = ['opencdc', 'payback', 'expandloan', 'closecdc', 'liquidate']

    if interval not in time_intervals.keys():
        return None

    per_blocks = time_intervals[interval]

    res = cdb.get_bars_data(per_blocks)
    bar_cdcSum.add_xaxis(res['x_values'])
    bar_cdcCount.add_xaxis(res['x_values'])

    for bitem in barItems:
        key_sum = 'y_values_' + bitem + "_sum"
        key_count = 'y_values_' + bitem + "_count"
        if (key_sum in res.keys() and key_count in res.keys()):
            bar_cdcSum.add_yaxis(bitem + "_sum", res[key_sum], stack="stack1")
            bar_cdcCount.add_yaxis(bitem + "_count", res[key_count], stack="stack1")

    bar_cdcSum.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar_cdcSum.set_global_opts(
        title_opts=opts.TitleOpts(title="cdc交易金额统计"),
        legend_opts=opts.LegendOpts(pos_bottom="90%"),
        yaxis_opts=opts.AxisOpts(name="sum（" + stable_token_SYMBOL + ")"),
        xaxis_opts=opts.AxisOpts(name="time(" + interval + ")"),
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
    )
    # ,opts.DataZoomOpts(pos_bottom="50%")
    bar_cdcCount.set_series_opts(label_opts=opts.LabelOpts(is_show=False))

    bar_cdcCount.set_global_opts(
        title_opts=opts.TitleOpts(title="cdc交易数量统计"),
        legend_opts=opts.LegendOpts(pos_bottom="90%"),
        yaxis_opts=opts.AxisOpts(name="count"),
        xaxis_opts=opts.AxisOpts(name="time(" + interval + ")"),
        datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")]
    )
    return bar_cdcCount,bar_cdcSum


def get_cdc_count_pie():
    # stable_token>=low and stable_token<hign
    pies_config = [{"name": "0~1" + stable_token_SYMBOL, "low": 0, "hign": 1},
                    {"name": "1~10" + stable_token_SYMBOL, "low": 1, "hign": 10},
                   {"name": "10~100" + stable_token_SYMBOL, "low": 10, "hign": 100},
                   {"name": "100~1000" + stable_token_SYMBOL, "low": 100, "hign": 1000},
                   {"name": "1000~10000" + stable_token_SYMBOL, "low": 1000, "hign": 10000},
                   {"name": "10000~100000" + stable_token_SYMBOL, "low": 1000, "hign": 100000},
                   {"name": "100000~∞" + stable_token_SYMBOL, "low": 100000, "hign": None}]

    pie_attrs = []
    pie_values = []
    for pie_config in pies_config:
        low = pie_config["low"] * PRESISION
        hign = pie_config["hign"]
        if (hign is not None):
            hign = hign * PRESISION
        count = cdb.get_cdc_count_by_tokenAmount_data(low, hign)[0]
        pie_attrs.append(pie_config["name"])
        pie_values.append(count)

    pie = Pie()
    pie.add("", [list(z) for z in zip(pie_attrs, pie_values)],center=["40%", "50%"]) \
        .set_global_opts(title_opts=opts.TitleOpts(title="cdc仓位数量分布图"), legend_opts=opts.LegendOpts(
                pos_left="80%", pos_top="33.33%", orient="vertical") ) \
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    return pie

def get_average_collateral_rate_picture():
    rate = cdb.get_collateral_rate()
    # rate = Decimal(rate).quantize(Decimal('0.00'))
    c = (
        Liquid()
            .add("lq", [rate])
            .set_global_opts(title_opts=opts.TitleOpts(title="cdc平均抵押率"))
    )
    #gauge = Gauge()
    #gauge.add("", [("抵押率", rate)], min_=0, max_=4).set_global_opts(title_opts=opts.TitleOpts(title="collateral rate"))
    return c

def get_supply_line(startblocknum = None):
    blocks_n = []
    supplys = []

    res = cdb.get_supply_history_data(startblocknum)
    for r in res:
        blocks_n.append(str(r[0]))
        supplys.append(r[1] / PRESISION)

    line = Line()
    line.add_xaxis(blocks_n)
    line.add_yaxis('supply', supplys, label_opts=opts.LabelOpts(is_show=False), is_step=True)
    line.set_global_opts(title_opts=opts.TitleOpts(title="stable token supply"),
                         yaxis_opts=opts.AxisOpts(name="supply（" + stable_token_SYMBOL + ")"),
                         xaxis_opts=opts.AxisOpts(name="block hight"),
                         datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")])
    return line

############################################################################################################
def get_chart_tab_page(interval):
    bars = get_cdc_trx_counts_sums_bars(interval)

    tab = Tab()
    tab.add(bars[0], "cdc trx counts")
    tab.add(bars[1], "cdc trx sums")
    tab.add(get_supply_line(), "stable token supply")
    tab.add(get_average_collateral_rate_picture(), "average collateral rate")
    tab.add(get_cdc_count_pie(),"cdc count pie")
    return tab


@app.route("/")
def index():
    r = get_chart_tab_page("day")
    return render_template('index.html',myechart=r.render_embed())



@app.route("/cdc_count_pie")
def index_cdc_count_pie():
    r = get_cdc_count_pie()
    return render_template('index.html',myechart=r.render_embed())


@app.route("/supply_line")
def index_supply_line():
    r = get_supply_line()
    return render_template('index.html',myechart=r.render_embed())



if __name__ == "__main__":
    app.run(host = "127.0.0.1",port = 5000,debug=True)