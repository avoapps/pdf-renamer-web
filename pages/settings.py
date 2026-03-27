def run():
    import streamlit as st

    st.set_page_config(layout="wide")

    st.title("⚙️ Settings")

    # =========================================================
    # DEFAULT VALUES
    # =========================================================
    st.markdown("### 🧾 Default Values")

    default_company = st.text_input(
        "Default Company Name",
        value=st.session_state.get("default_company", "")
    )

    default_prefix = st.text_input(
        "Default Prefix",
        value=st.session_state.get("default_prefix", "100")
    )

    # =========================================================
    # STAMP SETTINGS
    # =========================================================
    st.markdown("### 🏷️ Stamp Settings")

    col1, col2 = st.columns(2)

    with col1:
        default_offset_x = st.number_input(
            "Default Offset X",
            value=st.session_state.get("default_offset_x", 0)
        )

    with col2:
        default_offset_y = st.number_input(
            "Default Offset Y",
            value=st.session_state.get("default_offset_y", 0)
        )

    # =========================================================
    # SAVE BUTTON
    # =========================================================
    st.markdown("---")

    if st.button("💾 Save Settings", use_container_width=True):

        st.session_state.default_company = default_company
        st.session_state.default_prefix = default_prefix
        st.session_state.default_offset_x = default_offset_x
        st.session_state.default_offset_y = default_offset_y

        st.success("✅ Settings saved!")

    # =========================================================
    # DEBUG VIEW
    # =========================================================
    with st.expander("🔍 Current Settings"):
        st.write(dict(st.session_state))