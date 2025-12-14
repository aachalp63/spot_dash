# Streamlit Spotify Analytics Dashboard — Dark Theme + Emojis
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config ---
st.set_page_config(layout="wide", page_title="🎧 Spotify Analytics — Dark Theme", initial_sidebar_state="expanded")

# --- Dark Theme Colors ---
bg_color = "#0e0e0e"
text_color = "#ffffff"
pie_colors = px.colors.sequential.Plasma
bar_colorscale = "Plasma"

# --- CSS for dark theme ---
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .css-1d391kg p, .css-1v0mbdj h1, .css-10trblm {{
        color: {text_color};
    }}
    .stMetricValue {{
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Load Data ---
@st.cache_data
def load_data(path="spotify_synthetic_dashboard.csv"):
    df = pd.read_csv(path)
    df['released_year'] = df['released_year'].astype(int)
    df['released_month'] = df['released_month'].astype(int)
    return df

df = load_data()

# --- Header ---

st.markdown(
    """
    <h1 style='color:#1DB954; display: flex; align-items: center;'>
        <img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg" 
             width="40" style="margin-right:10px;">
           Spotify Analytics Dashboard 
    </h1>
    """,
    unsafe_allow_html=True
)
# --- Sidebar Filters ---
st.sidebar.header("🎛️ Filters")
genre_options = ["All"] + sorted(df['genre'].unique())
selected_genres = st.sidebar.multiselect("🎼 Genre (multi)", options=genre_options, default=["All"])

if "All" in selected_genres:
    filtered_genres = df['genre'].unique()
else:
    filtered_genres = selected_genres

artist_options = ["All"] + sorted(df['artist_name'].unique())
selected_artist = st.sidebar.multiselect("🎤 Artist (multi)", options=artist_options, default=["All"])

year_range = st.sidebar.slider("📅 Released Year Range", int(df['released_year'].min()), int(df['released_year'].max()),
                               (int(df['released_year'].min()), int(df['released_year'].max())))

# --- Apply Filters ---
q = df[df['genre'].isin(filtered_genres)]
if "All" not in selected_artist:
    q = q[q['artist_name'].isin(selected_artist)]
q = q[(q['released_year'] >= year_range[0]) & (q['released_year'] <= year_range[1])]
# Add spacing between rows
st.markdown("<div style='margin:50px 0;'></div>", unsafe_allow_html=True)

# --- KPIs with uniform height --- 
card_height = 130  # adjust as needed

k1, k2, k3, k4, k5 = st.columns([1,1,1,1,1])

def styled_metric(label, value):
    st.markdown(
        f"""
        <div style='
            background-color:#1B1B1B; 
            min-height:{card_height}px; 
            display:flex; 
            flex-direction:column; 
            justify-content:center; 
            align-items:flex-start; 
            border-radius:10px; 
            color:#ffffff; 
            padding:10px;
        '>
            <div style='font-size:16px;'>{label}</div>
            <div style='font-size:28px; font-weight:bold;'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with k1:
    styled_metric("🎵 Total Tracks", f"{len(q):,}")
with k2:
    styled_metric("📊 Total Streams", f"{q['streams'].sum():,}")
with k3:
    styled_metric("🎤 Unique Artists", f"{q['artist_name'].nunique():,}")
with k4:
    styled_metric("💃 Avg Danceability", f"{q['danceability'].mean():.2f}")

# --- Top Track ---
top_track = q.sort_values('streams', ascending=False).iloc[0]
with k5:
    st.markdown(
        f"""
        <div style='
            background-color:#1B1B1B; 
            min-height:{card_height}px; 
            display:flex; 
            flex-direction:column; 
            justify-content:center; 
            align-items:flex-start; 
            border-radius:10px; 
            color:#ffffff; 
            padding:10px;
        '>
            <div style='font-size:16px;'>🏆 Top Track:</div>
            <div style='font-size:24px; font-weight:bold;'>
                "{top_track['track_name']}" by {top_track['artist_name']}<br>🎵 {top_track['streams']:,} streams
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Add spacing between rows
st.markdown("<div style='margin:50px 0;'></div>", unsafe_allow_html=True)
# --- Grid layout ---
row1 = st.columns([1,1,1,1])

# Add spacing between rows
st.markdown("<div style='margin:50px 0;'></div>", unsafe_allow_html=True)
row2 = st.columns([1,1,1,1])

chart_height = 400
margin_opt = dict(t=30, b=10, l=10, r=10)

# --- Chart 1: Treemap ---
with row1[0]:
    st.subheader("🌈 Streams by Genre")
    by_genre = q.groupby("genre", as_index=False)['streams'].sum().sort_values('streams', ascending=False)
    fig1 = px.treemap(by_genre, path=['genre'], values='streams', color='streams', color_continuous_scale=bar_colorscale)
    fig1.update_layout(height=chart_height, margin=margin_opt, paper_bgcolor=bg_color, font_color=text_color)
    st.plotly_chart(fig1, use_container_width=True)

# --- Chart 2: Pie Top Artists ---
with row1[1]:
    st.subheader("🏆 Top 10 Artists — Stream Share")
    top_artists = q.groupby('artist_name', as_index=False)['streams'].sum().sort_values('streams', ascending=False).head(10)
    fig2 = px.pie(top_artists, names='artist_name', values='streams', hole=0.4,
                  color_discrete_sequence=pie_colors, height=chart_height)
    fig2.update_traces(textinfo='percent+label', pull=[0.05]*len(top_artists))
    fig2.update_layout(paper_bgcolor=bg_color, font_color=text_color)
    st.plotly_chart(fig2, use_container_width=True)

# --- Chart 3: Monthly Releases ---
# --- Chart 3: Moving Bubble Chart (Animated) ---
# --- Chart 3: Moving Bubble Chart (Animated) ---
with row1[2]:
    st.subheader("📊 Moving Bubble Chart — Popularity Over Time by Genre")

    # 🎞️ Sidebar control for animation speed
    animation_speed = st.sidebar.slider(
        "⏱️ Animation Speed (milliseconds per frame)",
        min_value=200,
        max_value=2000,
        value=800,
        step=100,
        help="Adjust animation playback speed"
    )

    # Prepare and clean data
    bubble_data = q.copy()
    if not bubble_data.empty:
        # ✅ Clean and standardize genre names
        bubble_data['genre'] = (
            bubble_data['genre']
            .astype(str)
            .str.strip()       # remove spaces
            .str.lower()       # lowercase
            .str.title()       # Title case for clean labels (e.g., Rock, Pop)
        )

        # ✅ Aggregate to one bubble per genre per year
        bubble_data = (
            bubble_data.groupby(['released_year', 'genre'], as_index=False)
            .agg({
                'danceability': 'mean',   # Average popularity
                'streams': 'sum'          # Total streams
            })
        )

        # ✅ Sort and prepare for animation
        bubble_data = bubble_data.sort_values(by='released_year', ascending=True)
        sorted_years = sorted(bubble_data['released_year'].unique(), key=lambda x: int(x))

        # Create animated bubble chart
        fig3 = px.scatter(
            bubble_data,
            x='genre',
            y='danceability',
            size='streams',
            color='genre',
            animation_frame='released_year',
            range_y=[0, 1],
            size_max=60,
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={
                'genre': '🎵 Genre',
                'danceability': '💃 Popularity (Avg Danceability)',
                'released_year': '📅 Year',
                'streams': '🎧 Total Streams'
            },
            category_orders={'released_year': sorted_years}
        )

        # Update layout and animation controls
        fig3.update_layout(
            height=chart_height,
            margin=margin_opt,
            paper_bgcolor=bg_color,
            font_color=text_color,
            plot_bgcolor=bg_color,
            legend_title_text='🎧 Genre',
            xaxis_title='🎵 Genre',
            yaxis_title='💃 Popularity',
            updatemenus=[{
                'buttons': [
                    {
                        'args': [None, {
                            'frame': {'duration': animation_speed, 'redraw': True},
                            'transition': {'duration': 100, 'easing': 'linear'}
                        }],
                        'label': '▶️ Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': '⏸️ Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 70},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }]
        )

        st.plotly_chart(fig3, use_container_width=True)

    else:
        st.info("No data available for popularity-over-time chart.")

# --- Chart 4: Energy Gauge ---
with row1[3]:
    st.subheader("⚡ Energy % (Indicator)")
    energy_percent = (q['energy'].mean() * 100) if not q.empty else 0
    bar_color = 'red' if energy_percent < 30 else 'orange' if energy_percent < 70 else 'green'
    fig4 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=energy_percent,
        number={'suffix': "%", "valueformat": ".2f"},
        delta={'reference': 50, 'increasing': {'color': "green"}},
        title={'text': "Avg Energy %"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': bar_color},
               'steps': [
                   {'range': [0, 30], 'color': "gray"},
                   {'range': [30, 70], 'color': "darkgray"},
                   {'range': [70, 100], 'color': "green"}]
              }
    ))
    fig4.update_layout(height=chart_height, margin=margin_opt, paper_bgcolor=bg_color, font_color=text_color)
    st.plotly_chart(fig4, use_container_width=True)

# --- Chart 5: Area Streams Over Years ---
with row2[0]:
    st.subheader("📈 Streams Over Years")
    yearly = q.groupby('released_year', as_index=False)['streams'].sum().sort_values('released_year')
    fig5 = px.area(yearly, x='released_year', y='streams', markers=True)
    fig5.update_layout(yaxis_tickformat=',', height=chart_height, margin=margin_opt, paper_bgcolor=bg_color, font_color=text_color)
    st.plotly_chart(fig5, use_container_width=True)

# --- Chart 6: Scatter Danceability vs Valence ---
with row2[1]:
    st.subheader("💃 Which Songs Make You Dance & Smile with Popularity?")
    sample = q.sample(n=min(200, len(q)), random_state=42) if len(q) > 0 else q
    sample['size_scaled'] = np.log1p(sample['streams'])
    
    # Normalize bubble sizes between 10 and 60
    if not sample.empty:
        sample['size_scaled'] = sample['streams'] / sample['streams'].max() * 60
        sample['size_scaled'] = sample['size_scaled'].clip(lower=5)  # avoid invisible dots
        
        fig6 = px.scatter(
            sample, 
            x='danceability', 
            y='valence', 
            size='size_scaled', 
            color='genre',
            hover_data=['track_name','artist_name'],
            height=chart_height,
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={
                'danceability': 'Beats',  # x-axis
                'valence': 'Mood',           # y-axis
                'genre': '🎵 Genre'                # legend
            }
        )
        
    fig6.update_layout(
        margin=margin_opt, 
        paper_bgcolor=bg_color, 
        font_color=text_color
    )
    st.plotly_chart(fig6, use_container_width=True)


# --- Chart 7: Top Streams by Region ---
with row2[2]:
    st.subheader("🌍 Top Streams by Region")
    if 'region' in q.columns:
        region_streams = q.groupby('region', as_index=False)['streams'].sum().sort_values('streams', ascending=False).head(10)
        fig7 = px.bar(region_streams[::-1], x='streams', y='region', orientation='h', text='streams',
                      color='streams', color_continuous_scale=bar_colorscale, height=chart_height)
        fig7.update_traces(texttemplate='%{text:,}', textposition='outside')
        fig7.update_layout(margin=margin_opt, paper_bgcolor=bg_color, font_color=text_color)
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("No 'region' column found in the dataset.")

# --- Chart 8: Radar Audio Features ---
with row2[3]:
    st.subheader("🎛️ Audio Feature Radar (Top Genres)")
    features = ['danceability','energy','valence','acousticness','speechiness']
    genre_avg = q.groupby('genre')[features].mean().reset_index()
    top_genres = genre_avg.sort_values('energy', ascending=False).head(4)
    fig8 = go.Figure()
    for _, r in top_genres.iterrows():
        fig8.add_trace(go.Scatterpolar(r=r[features].values, theta=[f.title() for f in features],
                                       fill='toself', name=r['genre']))
    fig8.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,1])), showlegend=True,
                       height=chart_height, margin=margin_opt, paper_bgcolor=bg_color, font_color=text_color)
    st.plotly_chart(fig8, use_container_width=True)
