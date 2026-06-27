import streamlit as st


# ---- Helper functions (unchanged from your original script) ----
def parse_msds(text):
    """Convert a string like '12x14x15' to a list of floats."""
    return [float(p) for p in text.replace(" ", "").split("x") if p]


def fibrosis_class(x):
    if x < 1.22:
        return {"stage": "F0", "description": "normal"}
    elif 1.22 <= x <= 1.37:
        return {"stage": "F0-F1", "description": "normal-mild"}
    elif 1.38 <= x <= 2.00:
        return {"stage": "F2-F3", "description": "mild-moderate"}
    else:
        return {"stage": "F3-F4", "description": "moderate-severe"}


# ---- Streamlit UI ----
st.title("FibroScan Evaluation")


# --- Spleen ---
st.subheader("Spleen")
sp_length = st.number_input("Spleen length (mm)", min_value=0.0, format="%.1f")
sp_width  = st.number_input("Spleen width (mm)", min_value=0.0, format="%.1f")


# --- Liver stiffness ---
st.subheader("Liver Stiffness")
ls2 = st.number_input("LS2 (kPa)", min_value=0.0, format="%.1f")


# --- Portal vein ---
st.subheader("Portal Vein")
pv_caliber = st.number_input("Portal vein caliber (mm)", min_value=0.0, format="%.1f")
pv_velocity = st.number_input("Portal vein velocity (cm/s)", min_value=0.0, format="%.1f")


# --- Liver segments (use text input with 'x' separator) ---
st.subheader("Liver Segments")
seg5_input = st.text_input("Segment 5 measurements (e.g., 12.3x14.1x15.8)", value="")
seg8_input = st.text_input("Segment 8 measurements (e.g., 10.0x11.5)", value="")
seg7_input = st.text_input("Segment 7 measurements (e.g., 9.8)", value="")


# --- Other findings ---
st.subheader("Other Findings")
other_findings = st.text_area("Enter any additional notes (one per line)")


# --- Evaluate button ---
if st.button("Evaluate"):
    # Build patient dictionary
    patient = {
        "spleen": {"length": sp_length, "width": sp_width},
        "liver": {"ls2": ls2},
        "portal vein": {"caliber": pv_caliber, "velocity": pv_velocity}
    }


    # Parse segment inputs
    seg5_values = parse_msds(seg5_input) if seg5_input else []
    seg8_values = parse_msds(seg8_input) if seg8_input else []
    seg7_values = parse_msds(seg7_input) if seg7_input else []


    # Check that we have values for all three segments
    if not (seg5_values and seg8_values and seg7_values):
        st.error("Please enter measurements for all three liver segments.")
    else:
        # Calculate averages
        seg5_avg = sum(seg5_values) / len(seg5_values)
        seg8_avg = sum(seg8_values) / len(seg8_values)
        seg7_avg = sum(seg7_values) / len(seg7_values)
        overall_avg = (seg5_avg + seg8_avg + seg7_avg) / 3


        patient["segments"] = {
            "5": {"values": seg5_values, "average": seg5_avg},
            "8": {"values": seg8_values, "average": seg8_avg},
            "7": {"values": seg7_values, "average": seg7_avg},
            "overall average": overall_avg
        }


        # Fibrosis classification
        patient["fibrosis"] = fibrosis_class(overall_avg)


        # Other findings
        if other_findings.strip():
            patient["other_findings"] = [line.strip() for line in other_findings.splitlines() if line.strip()]
        else:
            patient["other_findings"] = []


        # ---- Display Report ----
        st.markdown("---")
        st.markdown("## 📋 FIBROSCAN EVALUATION REPORT")


        st.markdown(f"**Spleen:** {patient['spleen']['length']:.1f} mm × {patient['spleen']['width']:.1f} mm")
        st.markdown(f"**Liver stiffness (LS2):** {patient['liver']['ls2']:.1f} kPa")
        st.markdown(f"**Portal vein:** caliber {patient['portal vein']['caliber']:.1f} mm, velocity {patient['portal vein']['velocity']:.1f} cm/s")


        st.markdown("### Liver Segments")
        for seg in ["5", "8", "7"]:
            data = patient["segments"][seg]
            vals_str = ", ".join(f"{v:.1f}" for v in data["values"])
            st.markdown(f"- **Segment {seg}:** {vals_str}  →  avg: {data['average']:.2f}")
        st.markdown(f"**Overall segment average:** {patient['segments']['overall average']:.2f}")


        st.markdown("### Fibrosis Stage")
        fib = patient["fibrosis"]
        st.markdown(f"**{fib['stage']}** — {fib['description'].capitalize()}")


        st.markdown("### Other Findings")
        notes = patient["other_findings"]
        if notes:
            for i, note in enumerate(notes, 1):
                st.markdown(f"{i}. {note}")
        else:
            st.markdown("*None*")