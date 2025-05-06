import streamlit as st
import ipaddress

st.set_page_config(page_title="IPv4/IPv6 Subnetzrechner", layout="wide")
st.title("🌐 IPv4 & IPv6 Subnetzrechner mit Rechenweg")

col1, col2 = st.columns([2, 2])

# Eingaben
with col1:
    modus = st.selectbox("Modus", ["IPv4", "IPv6"])
    ip_input = st.text_input("IP-Adresse inkl. CIDR", "192.168.1.0/24")
    subnet_count = st.number_input("Anzahl gewünschter Subnetze", min_value=0, value=0)
    host_count = st.number_input("Benötigte Hosts pro Subnetz", min_value=0, value=0)
    erklaer_modus = st.checkbox("Erklärmodus aktivieren", value=True)

if st.button("🔍 Berechnen"):
    try:
        netz = ipaddress.ip_network(ip_input, strict=False)
        lines = []

        def naechste_2er_potenz(n):
            p = 0
            while 2 ** p < n:
                p += 1
            return p

        st.subheader("📄 Ergebnis")
        if modus == "IPv4" and isinstance(netz, ipaddress.IPv4Network):
            lines.append(f"Netzwerkadresse: {netz.network_address}")
            lines.append(f"Broadcastadresse: {netz.broadcast_address}")
            lines.append(f"1. Host: {list(netz.hosts())[0]}")
            lines.append(f"Letzter Host: {list(netz.hosts())[-1]}")
            lines.append(f"Nutzbare Hosts: {netz.num_addresses - 2}")
            lines.append(f"Subnetzmaske: {netz.netmask}")
            lines.append(f"CIDR: /{netz.prefixlen}")

            if erklaer_modus:
                lines.append("\n🔎 Erklärung:")
                lines.append(f"Host-Bits: {32 - netz.prefixlen}, Adressen = 2^{32 - netz.prefixlen} - 2")
                lines.append("Broadcast = alle Hostbits auf 1")

        elif modus == "IPv6" and isinstance(netz, ipaddress.IPv6Network):
            lines.append(f"Netzwerkadresse: {netz.network_address}")
            lines.append(f"Prefix: /{netz.prefixlen}")
            lines.append(f"Adressen gesamt: {netz.num_addresses}")
            lines.append(f"Erste Adresse: {list(netz.hosts())[0]}")
            lines.append(f"Letzte Adresse: {list(netz.hosts())[-1]}")
            if erklaer_modus:
                lines.append("IPv6 hat keinen Broadcast. Der Adressraum ist riesig.")

        else:
            st.error("Die IP passt nicht zum gewählten Modus.")

        # Subnetze berechnen
        if subnet_count > 0:
            lines.append("\n📦 Subnetze nach Anzahl:")
            exponent = naechste_2er_potenz(subnet_count)
            neue_prefix = netz.prefixlen + exponent

            if (modus == "IPv4" and neue_prefix > 32) or (modus == "IPv6" and neue_prefix > 128):
                lines.append("❌ Zu viele Subnetze.")
            else:
                subnets = list(netz.subnets(new_prefix=neue_prefix))
                lines.append(f"Neuer Präfix: /{neue_prefix} → 2^{exponent} = {2**exponent} Subnetze")
                for i, sn in enumerate(subnets[:5]):
                    hostanzahl = sn.num_addresses - 2 if isinstance(sn, ipaddress.IPv4Network) else sn.num_addresses
                    lines.append(f"{i+1}. {sn} – Hosts: {hostanzahl}")

        if host_count > 0 and modus == "IPv4":
            lines.append("\n📦 Subnetze nach Host-Anforderung:")
            needed_hosts = host_count + 2
            bits = naechste_2er_potenz(needed_hosts)
            neue_prefix = 32 - bits

            if neue_prefix < netz.prefixlen:
                lines.append("❌ Zu viele Hosts für dieses Netz.")
            else:
                subnets = list(netz.subnets(new_prefix=neue_prefix))
                lines.append(f"Neuer Präfix: /{neue_prefix} → 2^{bits} = {2**bits} Adressen")
                for i, sn in enumerate(subnets[:5]):
                    lines.append(f"{i+1}. {sn} – Hosts: {sn.num_addresses - 2}")

        st.code("\n".join(lines), language="text")

    except Exception as e:
        st.error(f"Fehler: {e}")