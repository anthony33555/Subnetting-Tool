import streamlit as st
import ipaddress
import math

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
                host_bits = 32 - netz.prefixlen
                total_addresses = 2 ** host_bits
                usable_hosts = total_addresses - 2
                lines.append(f"IPv4-Adressen bestehen aus 32 Bit.")
                lines.append(f"Prefix: /{netz.prefixlen} → verbleiben {host_bits} Bit für Hosts")
                lines.append(f"2^{host_bits} = {total_addresses} Adressen → -2 (Netz & Broadcast) = {usable_hosts} nutzbar")
                lines.append("Broadcast-Adresse = alle Hostbits auf 1 gesetzt")

        elif modus == "IPv6" and isinstance(netz, ipaddress.IPv6Network):
            lines.append(f"Netzwerkadresse: {netz.network_address}")
            lines.append(f"Prefix: /{netz.prefixlen}")
            lines.append(f"Adressen gesamt: {netz.num_addresses}")
            lines.append(f"Erste Adresse: {list(netz.hosts())[0]}")
            lines.append(f"Letzte Adresse: {list(netz.hosts())[-1]}")
            if erklaer_modus:
                lines.append("IPv6 hat keinen Broadcast. Der Adressraum ist sehr groß (128 Bit).")

        else:
            st.error("Die IP passt nicht zum gewählten Modus.")

        if subnet_count > 0:
            lines.append("\n📦 Subnetze nach Anzahl:")
            exponent = naechste_2er_potenz(subnet_count)
            neue_prefix = netz.prefixlen + exponent
            if (modus == "IPv4" and neue_prefix > 32) or (modus == "IPv6" and neue_prefix > 128):
                lines.append("❌ Zu viele Subnetze für das gewählte Netz möglich.")
            else:
                subnets = list(netz.subnets(new_prefix=neue_prefix))
                lines.append(f"Benötigte zusätzliche Bits: log2({subnet_count}) → {exponent}")
                lines.append(f"Neuer Präfix: /{netz.prefixlen} + {exponent} = /{neue_prefix}")
                hosts_pro_subnetz = 2 ** (32 - neue_prefix) if modus == "IPv4" else 2 ** (128 - neue_prefix)
                usable = hosts_pro_subnetz - 2 if modus == "IPv4" else hosts_pro_subnetz
                lines.append(f"Adressen pro Subnetz: 2^{32 - neue_prefix} = {hosts_pro_subnetz} → Nutzbar: {usable}")
                lines.append(f"Erste {min(5, len(subnets))} Subnetze:")
                for i, sn in enumerate(subnets[:5]):
                    lines.append(f"{i+1}. {sn}")

        if host_count > 0 and modus == "IPv4":
            lines.append("\n📦 Subnetze nach Host-Anforderung:")
            needed_hosts = host_count + 2
            bits = naechste_2er_potenz(needed_hosts)
            neue_prefix = 32 - bits
            if neue_prefix < netz.prefixlen:
                lines.append("❌ Die benötigte Hostanzahl passt nicht in das ursprüngliche Netz.")
            else:
                lines.append(f"Benötigte Adressen (inkl. Netz+Broadcast): {needed_hosts}")
                lines.append(f"Benötigte Hostbits: log2({needed_hosts}) → {bits}")
                lines.append(f"Neuer Präfix: 32 - {bits} = /{neue_prefix}")
                subnets = list(netz.subnets(new_prefix=neue_prefix))
                lines.append(f"Adressen pro Subnetz: 2^{bits} = {2 ** bits} → Nutzbare Hosts: {2 ** bits - 2}")
                lines.append(f"Erste {min(5, len(subnets))} Subnetze:")
                for i, sn in enumerate(subnets[:5]):
                    lines.append(f"{i+1}. {sn}")

        st.code("\n".join(lines), language="text")

    except Exception as e:
        st.error(f"Fehler: {e}")
