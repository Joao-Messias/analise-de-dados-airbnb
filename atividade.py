import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Carregar o dataset
df = pd.read_csv('AB_NYC_2019.csv')

# Preencher valores ausentes com 'Unknown'
df['name'] = df['name'].fillna('Unknown')
df['host_name'] = df['host_name'].fillna('Unknown')

# Preencher valores ausentes com 0
df['reviews_per_month'] = df['reviews_per_month'].fillna(0)

# Converter 'last_review' para datetime
df['last_review'] = pd.to_datetime(df['last_review'])

df['no_reviews'] = df['last_review'].isna()

# Histograma da distribuição de preços - Seaborn
plt.figure(figsize=(12, 6))
sns.histplot(df['price'], bins=100, kde=True)
plt.title('Distribuição de Preços dos Imóveis')
plt.xlabel('Preço')
plt.ylabel('Frequência')
plt.xlim(0, 500)  # Limitar o eixo x para evitar outliers extremos
plt.show()

# Boxplot do preço por grupo de bairro
plt.figure(figsize=(12, 6))
sns.boxplot(x='neighbourhood_group', y='price', data=df)
plt.title('Preço por Grupo de Bairro')
plt.xlabel('Grupo de Bairro')
plt.ylabel('Preço')
plt.ylim(0, 500)  # Limitar o eixo y para evitar outliers extremos
plt.show()

# Boxplot do preço por tipo de quarto
plt.figure(figsize=(12, 6))
sns.boxplot(x='room_type', y='price', data=df)
plt.title('Preço por Tipo de Quarto')
plt.xlabel('Tipo de Quarto')
plt.ylabel('Preço')
plt.ylim(0, 500)
plt.show()

# Top 10 bairros com mais imóveis
top_neighbourhoods = df['neighbourhood'].value_counts().head(10)
# Gráfico de barras dos top 10 bairros
plt.figure(figsize=(12, 6))
sns.barplot(x=top_neighbourhoods.values, y=top_neighbourhoods.index, orient='h')
plt.title('Top 10 Bairros com Mais Imóveis')
plt.xlabel('Número de Imóveis')
plt.ylabel('Bairro')
plt.show()

# Criar o mapa interativo com Plotly Express
# Filtrar imóveis com preço até $500
df_filtered = df[df['price'] <= 500]

fig = px.scatter_mapbox(
    df_filtered,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    hover_data=["neighbourhood", "price", "room_type"],
    color="price",
    color_continuous_scale=px.colors.cyclical.IceFire,
    zoom=10,
    height=600
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()

# Criar a coluna 'price_review_ratio' em df
df['price_review_ratio'] = df['price'] / (df['number_of_reviews'] + 1)

# Filtrar imóveis com preço até $500 e criar uma cópia
df_filtered = df[df['price'] <= 500].copy()

# Criar o mapa usando a métrica de custo-benefício
fig = px.scatter_mapbox(
    df_filtered,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    hover_data=["neighbourhood", "price", "number_of_reviews"],
    color="price_review_ratio",
    color_continuous_scale=px.colors.sequential.Viridis_r,
    zoom=10,
    height=600
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()

# Criar o mapa destacando o tipo de quarto
fig = px.scatter_mapbox(
    df_filtered,
    lat="latitude",
    lon="longitude",
    hover_name="name",
    hover_data=["neighbourhood", "price"],
    color="room_type",
    zoom=10,
    height=600
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()

# Calcular estatísticas descritivas dos preços por bairro
price_stats = df.groupby('neighbourhood')['price'].agg(['mean', 'median', 'min', 'max', 'count']).reset_index()
price_stats.rename(columns={'mean': 'price_mean', 'median': 'price_median', 'min': 'price_min', 'max': 'price_max',
                            'count': 'listing_count'}, inplace=True)

# Calcular o número médio de avaliações por bairro
reviews_stats = df.groupby('neighbourhood')['number_of_reviews'].agg(['mean', 'median']).reset_index()
reviews_stats.rename(columns={'mean': 'reviews_mean', 'median': 'reviews_median'}, inplace=True)

# Combinar as estatísticas em um único dataframe
neighbourhood_stats = pd.merge(price_stats, reviews_stats, on='neighbourhood')

# Visualizar as primeiras linhas
print(neighbourhood_stats.head())

# Filtrar bairros com preço médio abaixo de um certo limite
affordable_neighbourhoods = neighbourhood_stats[neighbourhood_stats['price_mean'] < 300]

# Ordenar pelos bairros com maior número médio de avaliações
affordable_neighbourhoods = affordable_neighbourhoods.sort_values(by='reviews_mean', ascending=False)

# Exibir os top 10 bairros
print(affordable_neighbourhoods.head(10))

# Criar a métrica de custo-benefício
neighbourhood_stats['cost_benefit'] = neighbourhood_stats['price_mean'] / (neighbourhood_stats['reviews_mean'] + 1)

# Ordenar os bairros com base na métrica de custo-benefício
neighbourhood_stats = neighbourhood_stats.sort_values('cost_benefit')

# Exibir os top 10 bairros com melhor custo-benefício
best_value_neighbourhoods = neighbourhood_stats.head(10)
print(best_value_neighbourhoods[['neighbourhood', 'price_mean', 'reviews_mean', 'cost_benefit']])

# Gráfico de barras dos top 10 bairros com melhor custo-benefício
plt.figure(figsize=(12, 6))
sns.barplot(
    x='neighbourhood',
    y='cost_benefit',
    data=best_value_neighbourhoods
)
plt.title('Top 10 Bairros com Melhor Custo-Benefício')
plt.xlabel('Bairro')
plt.ylabel('Métrica de Custo-Benefício')
plt.xticks(rotation=45)
plt.show()

# Calcular as coordenadas médias de cada bairro
neighbourhood_locations = df.groupby('neighbourhood')[['latitude', 'longitude']].mean().reset_index()

# Combinar com a métrica de custo-benefício
neighbourhood_map_data = pd.merge(neighbourhood_stats, neighbourhood_locations, on='neighbourhood')

# Criar o mapa temático
fig = px.scatter_mapbox(
    neighbourhood_map_data,
    lat="latitude",
    lon="longitude",
    hover_name="neighbourhood",
    hover_data=["price_mean", "reviews_mean", "cost_benefit"],
    color="cost_benefit",
    color_continuous_scale=px.colors.sequential.Viridis_r,
    zoom=10,
    height=600
)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.show()
