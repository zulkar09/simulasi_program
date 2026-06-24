# Mengimpor library yang dibutuhkan
import pandas as pd  # Untuk manipulasi data dalam bentuk tabel/dataframe
import plotly.graph_objects as go  # Untuk membuat grafik visualisasi yang interaktif
import streamlit as st  # Framework utama untuk membuat aplikasi web

# Mengatur konfigurasi halaman aplikasi Streamlit
st.set_page_config(page_title="Simulasi Ekonomi Komunitas Mandiri", layout="wide")

# Membuat judul utama aplikasi
st.title("📊 Simulasi & Visualisasi Ekonomi Komunitas vs Sistem Fiat")
st.markdown(
    "Menampilkan bagaimana dana **Rp1 Miliar** dari 1.000 anggota berkembang menggunakan strategi Anda."
)

# --- BAGIAN INPUT PARAMETER (BISA DIUBAH DI SIDEBAR) ---
st.sidebar.header("⚙️ Pengaturan Parameter")

# Input jumlah anggota komunitas
jumlah_anggota = st.sidebar.number_input(
    "Jumlah Anggota (Orang)", value=1000, step=100
)

# Input patungan fiat awal per orang
iuran_per_orang = st.sidebar.number_input(
    "Iuran Awal Per Orang (Rp)", value=1000000, step=100000
)

# Input perkiraan keuntungan bulanan dari bisnis fiat yang dibangun di luar
profit_bisnis_luar = (
    st.sidebar.slider("Profit Bisnis Luar per Bulan (%)", 1, 15, 5) / 100
)

# Input tingkat kebocoran uang jika menggunakan sistem fiat konvensional (belanja ke oligarki/biaya bank)
kebocoran_fiat_biasa = (
    st.sidebar.slider("Kebocoran Ekonomi Sistem Fiat per Bulan (%)", 5, 30, 10)
    / 100
)

# --- BAGIAN LOGIKA & PERHITUNGAN MATEMATIKA ---

# Menghitung total modal fiat awal yang terkumpul
modal_awal = jumlah_anggota * iuran_per_orang

# Menyiapkan list kosong untuk menampung data perkembangan bulan demi bulan (selama 12 bulan)
data_bulan = []
saldo_fiat_konvensional = modal_awal
saldo_kripto_internal = (
    modal_awal  # Nilai token kripto di dalam dijamin oleh aset awal
)
saldo_fiat_bisnis = modal_awal  # Uang fisik yang dipakai buat bisnis di luar

# Melakukan perulangan (looping) selama 12 bulan untuk simulasi
for bulan in range(0, 13):
    if bulan == 0:
        data_bulan.append(
            {
                "Bulan": "Bulan 0",
                "Sistem Fiat Biasa": saldo_fiat_konvensional,
                "Sistem Komunitas Anda": saldo_kripto_internal
                + saldo_fiat_bisnis,
            }
        )
    else:
        # 1. Jalur Konvensional (Tetap menyusut seperti biasa)
        saldo_fiat_konvensional = saldo_fiat_konvensional * (
            1 - kebocoran_fiat_biasa
        )

        # 2. Jalur Komunitas Anda (SEKARANG BERKAITAN DENGAN LEAKED)
        # Bisnis luar menghasilkan keuntungan (Pendapatan Komunitas)
        keuntungan_bisnis = saldo_fiat_bisnis * profit_bisnis_luar

        # DANA LEAKED: Kas bisnis berkurang karena komunitas terpaksa belanja keluar
        dana_bocor_keluar = saldo_fiat_bisnis * kebocoran_fiat_biasa

        # Saldo bisnis luar sekarang = Saldo bulan lalu + Keuntungan - Dana Bocor
        saldo_fiat_bisnis = (
            saldo_fiat_bisnis + keuntungan_bisnis - dana_bocor_keluar
        )

        # Total kekayaan komunitas dihitung dari sisa saldo bisnis luar + nilai kripto internal
        total_kekayaan_komunitas = saldo_kripto_internal + saldo_fiat_bisnis

        data_bulan.append(
            {
                "Bulan": f"Bulan {bulan}",
                "Sistem Fiat Biasa": saldo_fiat_konvensional,
                "Sistem Komunitas Anda": total_kekayaan_komunitas,
            }
        )

# Mengubah data list menjadi DataFrame (format tabel agar bisa dibaca oleh sistem grafik)
df = pd.DataFrame(data_bulan)

# --- BAGIAN VISUALISASI GRAFIK ---

# Membuat objek grafik menggunakan Plotly
fig = go.Figure()

# Menambahkan garis untuk simulasi Sistem Fiat Biasa (Warna Merah)
fig.add_trace(
    go.Scatter(
        x=df["Bulan"],
        y=df["Sistem Fiat Biasa"],
        mode="lines+markers",
        name="Sistem Fiat Biasa (Uang Bocor Keluar)",
        line=dict(color="#FF4B4B", width=3),
    )
)

# Menambahkan garis untuk simulasi Sistem Komunitas Kripto Anda (Warna Hijau)
fig.add_trace(
    go.Scatter(
        x=df["Bulan"],
        y=df["Sistem Komunitas Anda"],
        mode="lines+markers",
        name="Sistem Komunitas Anda (Kripto + Bisnis Mandiri)",
        line=dict(color="#00E676", width=4),
    )
)

# Mengatur tampilan layout grafik (judul, warna background, dan format mata uang)
fig.update_layout(
    title="Perbandingan Pertumbuhan Kekayaan Komunitas dalam 12 Bulan",
    xaxis_title="Periode Waktu",
    yaxis_title="Total Nilai Ekonomi (Rp)",
    hovermode="x unified",
    template="plotly_dark",  # Menggunakan tema gelap agar terlihat futuristik dan bersih
)

# Menampilkan grafik di halaman web Streamlit
st.plotly_chart(fig, use_container_width=True)

# --- BAGIAN RINGKASAN DATA (METRICS) ---
st.subheader("📌 Kesimpulan Hasil Analisis")
kolom1, kolom2 = st.columns(2)

# Mengambil nilai akhir di bulan ke-12
fiat_akhir = df["Sistem Fiat Biasa"].iloc[-1]
komunitas_akhir = df["Sistem Komunitas Anda"].iloc[-1]

# Menampilkan ringkasan angka pada kolom 1 (Sistem Fiat)
with kolom1:
    st.metric(
        label="Sisa Nilai Ekonomi Sistem Fiat Biasa (Bulan 12)",
        value=f"Rp {fiat_akhir:,.0f}",
        delta=f"-{((modal_awal - fiat_akhir)/modal_awal)*100:.1f}% Menyusut",
    )
    st.caption(
        "Kekayaan menyusut karena anggota terus belanja ke jaringan retail milik elit/1% dan terkena biaya perbankan."
    )

# Menampilkan ringkasan angka pada kolom 2 (Sistem Komunitas)
with kolom2:
    st.metric(
        label="Total Kekayaan Ekosistem Komunitas Anda (Bulan 12)",
        value=f"Rp {komunitas_akhir:,.0f}",
        delta=f"+{((komunitas_akhir - modal_awal)/modal_awal)*100:.1f}% Tumbuh",
        delta_color="normal",
    )
    st.caption(
        "Kekayaan melonjak karena sirkulasi internal menggunakan kripto 100% aman, sementara dana fiat awal beranak-pinak di bisnis riil."
    )