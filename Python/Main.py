import pandas as pd 
import chardet

# Miramos que codificacion tienen los archivos y pasamos el resultados a df con ayuda
# de pandas para ayudarnos mejor
with open("src/ventas(in).csv", "rb") as f:
    result = chardet.detect(f.read())
df_ventas = pd.read_csv("src/ventas(in).csv",sep=';',encoding=result["encoding"], parse_dates=["Fecha de venta"], dayfirst=True)
print("Codificacion de ventas -> "+result["encoding"])

with open("src/vendedores(in).csv", "rb") as f:
    result = chardet.detect(f.read())
df_vendedores = pd.read_csv("src/vendedores(in).csv",sep=';',encoding=result["encoding"])
print("Codificacion de vendedores -> "+result["encoding"])

with open("src/paises(in).csv", "rb") as f:
    result = chardet.detect(f.read())
df_paises = pd.read_csv("src/paises(in).csv", sep=',',encoding=result["encoding"])
print("Codificacion de paises -> "+result["encoding"])


#Creamos 2 DataFrames, donde buscamos y separamos por valores de df_paises
#Luego, volvemos a juntarlo en uno solo
df_semi_1 = df_ventas.merge(df_paises,left_on='Región',right_on='ISO2', how='left')
df_semi_1 = df_semi_1.dropna()

df_semi_2 = df_ventas.merge(df_paises,left_on='Región',right_on='País', how='left')
df_semi_2 = df_semi_2.dropna()

df_ventas = df_semi_1.merge(df_semi_2, how='outer')

df_ventas.drop(columns=["Región","ISO2"], inplace=True)
df_ventas.rename(columns={"País":"Región"}, inplace=True)

print(df_ventas)

#Para saber los idiomas (EN,ES) en distintos paises y de personas
#Lo necesitaremos para después
df_equipos = df_vendedores[df_vendedores["Status"] != "baja"]
df_equipos = df_equipos.groupby(["Idioma","País","Equipo","Status"]).size().reset_index(name="E")
df_equipos.rename(columns={"País":"Región"}, inplace=True)

print(df_equipos)

# Tras obtener un DF de vendedores que podamos usar,
# Ahora toca crear DF para ventas diarias y acumuladas
# mensuales

df_ventas["Día"] = df_ventas["Fecha de venta"].dt.strftime("%Y-%m-%d")
df_ventas["Mensual"] = df_ventas["Fecha de venta"].dt.strftime("%Y-%m")

# Realizamos merge de DF ventas y vendedores
df_ventas_final = df_ventas.merge(df_equipos[["Región", "Idioma", "Equipo"]], on="Región", how="left")

#Guardamos un df con las ventas diarias
df_ventas_diarias = df_ventas_final.groupby(["Día", "Región", "Idioma","Equipo","Tipo de venta"]).agg({"Cantidad vendida": "sum"}).reset_index()
print(df_ventas_diarias)
#Guardamos un df con las ventas por mes
df_ventas_mensuales = df_ventas_final.groupby(["Mensual", "Región", "Idioma","Equipo","Tipo de venta"]).agg({"Cantidad vendida": "sum"}).reset_index()
print(df_ventas_mensuales)

# Finalmente, generamos los reportes en Excel
with pd.ExcelWriter("Reportes_Ventas.xlsx") as writer:
    df_ventas_diarias.to_excel(writer,sheet_name="Ventas diarias",index=False)
    df_ventas_mensuales.to_excel(writer,sheet_name="Ventas acumuladas",index=False)
    
print("Reporte generado con éxito")