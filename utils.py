def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

DIC_COLORES = {'verde':["#009966"],
               'ro_am_na':["#FFE9C5", "#F7B261","#D8841C", "#dd722a","#C24C31", "#	BC3B26"],
               'az_verd': ["#CBECEF", "#81D3CD", "#0FB7B3", "#	#009999"],
               'ax_viol': ["#D9D9ED", "#2F399B", "#1A1F63", "#262947"],
               'ofiscal': ["#F9F9F9", "#2635bf"]}

