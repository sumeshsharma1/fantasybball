import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

total_df_with_salaries = pd.read_csv('C:/Users/ssharma2/Desktop/fantasybball/total_df_with_salaries.csv')

def generate_table(dataframe):
    return html.Table(
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))]
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H4(children = 'Full Stats/Salary Table'),
    generate_table(total_df_with_salaries)
])

if __name__ == '__main__':
    app.run_server(debug=True)
