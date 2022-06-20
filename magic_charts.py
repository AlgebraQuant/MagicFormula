# Here were going to make some charts to use in the article.
import pandas as pd
import altair as alt

pd.options.display.max_colwidth = 10
pd.options.display.max_rows = 5
pd.options.display.max_columns = 7

# The first chart will be in the x axis the days when the
# the statements were published, and in the y axis the ebit

# First we need to load the days when the docs were published.
df_financials = pd.read_csv("4_total_assets.csv")

df_financials["net_debt"]
# # Second the market cap.

# Change type of column 'doc_env' from object to datetime
df_financials["doc_env"] = pd.to_datetime(df_financials["doc_env"])

# Make a new DataFrame with 2 columns: (i) the cia_nome and (ii) the difference
# between doc_env and the beggining of each row year.
df_chart = pd.DataFrame({"cia_nome": df_financials["cia_nome"]})
df_chart["total_dias"] = df_financials["doc_env"].dt.day_of_year
df_chart["doc_env"] = df_financials["doc_env"]
df_chart["per_ini"] = df_financials["per_ini"]
df_chart["per_fim"] = df_financials["per_fim"]
df_chart["doc_ver"] = df_financials["doc_ver"]

df_chart

# Add base 2 log total assets to the DataFrame
# df_chart["log_assets"] = df_financials["total_assets"].apply(np.log2)
df_chart["total_assets"] = df_financials["total_assets"]  # .apply(np.log2)

# Sort the DataFrame by 'total_dias'
df_chart = df_chart.sort_values(by="total_dias")

# Add a new column to the DataFrame with the quantile, in respect to the 'total
# dias' column, that row belongs.

df_chart_ver_1 = df_chart[df_chart["doc_ver"] == 1].reset_index(drop=True)

df_chart_ver_1["Quantile"] = pd.qcut(df_chart_ver_1["total_dias"], 5, labels=False)

renaming = {0: "Q1", 1: "Q2", 2: "Q3", 3: "Q4", 4: "Q5"}
df_chart_ver_1["Quantile"] = df_chart_ver_1["Quantile"].map(renaming)

eventos = pd.DataFrame(
    [
        # {"start": "90", "end": "91", "evento": " ld"},
        {"start": "100", "end": "101", "evento": " 100 days"},
    ]
)
# Chart
axis_labels = "datum.value == 10000 ? '10k' : datum.value == 100000 ? '100k'\
: datum.value == 1000000 ? '1M' : datum.value == 10000000 ? '10M'\
: datum.value == 100000000 ? '100M' : datum.value == 1000000000 ? '1Bn'\
: datum.value == 10000000000 ? '10Bn' : datum.value == 100000000000 ? '100Bn'\
: '1tn'"

selector = alt.selection_single(empty="all", fields=["cia_nome"])

highlight = alt.selection(
    type="single", on="mouseover", fields=["cia_nome"], nearest=True
)

opacity_cond = alt.condition(selector, alt.value(1), alt.value(0.05))

rule = alt.Chart(eventos).mark_rule(color="black", strokeWidth=1).encode(x="start:Q")
text = (
    alt.Chart(eventos)
    .mark_text(align="left", baseline="top", dy=-140, size=8)  # , size=9)
    .encode(
        alt.X("start:Q"),
        text="evento",
        color=alt.value("#000000"),
    )
)

chart_total_dias = (
    alt.Chart(df_chart_ver_1, width=700, height=300)
    .mark_point()
    .encode(
        alt.X(
            "total_dias:Q",
            title="Days until statement release",
            scale=alt.Scale(domain=(0, 370), nice=False),
        ),
        alt.Y(
            "total_assets:Q",
            title="Total Assets (log) - R$",
            # scale=alt.Scale(domain=(14, 43), nice=False),
            scale=alt.Scale(
                type="log",
                nice=False,
                domain=(10_000, 2_000_000_000_000),
            ),
            axis=alt.Axis(
                format="~s",
                values=[
                    10_000,
                    100_000,
                    1_000_000,
                    10_000_000,
                    100_000_000,
                    1_000_000_000,
                    10_000_000_000,
                    100_000_000_000,
                    1_000_000_000_000,
                ],
                labelExpr=(axis_labels),
            ),
        ),
        color=alt.condition(
            selector,
            alt.Color("Quantile:N", scale=alt.Scale(scheme="dark2")),
            alt.value("lightgray"),
        ),
        size=alt.condition(~highlight, alt.value(20), alt.value(65)),
        tooltip=["cia_nome:N", "doc_env:T", "per_ini:N", "per_fim:N"],
        opacity=opacity_cond,
    )
    .add_selection(highlight)
    .add_selection(selector)
)
# base.mark_line().encode(
#     size=alt.condition(~highlight, alt.value(1), alt.value(3))

chart_total = (chart_total_dias + rule + text).configure_axis(grid=False)
chart_total.save("chart_total_dias.html")
