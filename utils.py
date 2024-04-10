import pandas as pd

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

def get_dic_colors(filtro):
    dic_colors = {}
    rank = filtro.groupby('Sector')['apropiacion_cons_2024'].sum().rank().reset_index(name='rank')
    for _, info in rank.iterrows():
        sector_ = info['Sector']
        rank_ = info['rank']

        if rank_ > 26:
            dic_colors[sector_] = DIC_COLORES['ax_viol'][1]
        elif rank_ > 20:
            dic_colors[sector_] = DIC_COLORES['az_verd'][2]
        else:
            dic_colors[sector_] = DIC_COLORES['ro_am_na'][3]
    return dic_colors

def get_dic_colors_area(df):
    dic_colors = {}
    filtro = df[df['Año'] == 2024]
    rank = filtro.groupby('Sector')['apropiacion_cons_2024'].sum().rank().reset_index(name='rank')
    for _, info in rank.iterrows():
        sector_ = info['Sector']
        rank_ = info['rank']

        if rank_ > 26:
            dic_colors[sector_] = DIC_COLORES['ax_viol'][1]
        elif rank_ > 20:
            dic_colors[sector_] = DIC_COLORES['az_verd'][2]
        else:
            dic_colors[sector_] = DIC_COLORES['ro_am_na'][3]
    return dic_colors

DIC_COLORES = {'verde':["#009966"],
               'ro_am_na':["#FFE9C5", "#F7B261","#D8841C", "#dd722a","#C24C31", "#BC3B26"],
               'az_verd': ["#CBECEF", "#81D3CD", "#0FB7B3", "#009999"],
               'ax_viol': ["#D9D9ED", "#2F399B", "#1A1F63", "#262947"],
               'ofiscal': ["#F9F9F9", "#2635bf"]}

def create_dataframe_sankey(data, value_column, *columns, **filtros):
    for col in columns:
        if col not in data.columns:
            raise ValueError
    
    groupbys = []
    for idx, col in enumerate(columns[:-1]):
        i = data.groupby([columns[idx], columns[idx + 1]])[value_column].sum().reset_index()
        i.columns = ['source', 'target', 'value']
        groupbys.append(i)

    conc = pd.concat(groupbys, ignore_index=True)

    for key, values in filtros.items():
        for value in values:
            conc = conc[conc[key] != value]

    info = enumerate(list(set(conc['source'].unique().tolist() + conc['target'].unique().tolist())))

    dic_info = dict(info)

    rev_info = {}
    for key, value in dic_info.items():
        rev_info[value] = key

    conc['source'] = conc['source'].map(rev_info)
    conc['target'] = conc['target'].map(rev_info)



    return rev_info, conc



