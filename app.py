
import streamlit as st
import pandas as pd
import datetime
import re


# -----------------------------------
# APP CONFIGURATION
# -----------------------------------

st.set_page_config(
    page_title="Manufacturing Performance Engine",
    layout="wide"
)

st.title("Manufacturing Performance Engine")


# -----------------------------------
# HELPER FUNCTIONS
# -----------------------------------

def detect_time_unit(column_name):

    name = column_name.lower()

    if "hours" in name or "hrs" in name or "hr" in name:
        return "Hours"

    if "minutes" in name or "mins" in name or "min" in name:
        return "Minutes"

    if "seconds" in name or "secs" in name or "sec" in name:
        return "Seconds"

    return "Unknown"


def convert_to_seconds(value, unit):

    if pd.isna(value):
        return None

    if unit == "Hours":
        return value * 3600

    elif unit == "Minutes":
        return value * 60

    elif unit == "Seconds":
        return value

    else:
        return None


def format_time(seconds):

    if seconds is None or pd.isna(seconds):
        return "Not Available"

    if seconds < 0:
        return "Invalid Duration"

    elif seconds < 1:
        return f"{seconds * 1000:.0f} milliseconds"

    elif seconds < 60:
        return f"{seconds:.1f} seconds"

    elif seconds < 3600:
        return f"{seconds / 60:.1f} minutes"

    elif seconds < 86400:
        return f"{seconds / 3600:.1f} hours"

    else:
        return f"{seconds / 86400:.1f} days"


# -----------------------------------
# TIME NORMALISATION
# -----------------------------------

def convert_timestamp(value):

    if pd.isna(value):
        return None, None

    if isinstance(value, datetime.datetime):
        return value, value.time()

    elif isinstance(value, datetime.time):
        return value, value

    elif isinstance(value, str):

        try:

            if " " in value and (
                "AM" in value.upper() or "PM" in value.upper()
            ):
                original_timestamp = datetime.datetime.strptime(
                    value, "%I:%M:%S %p"
                )

            elif " " in value or "T" in value:
                original_timestamp = datetime.datetime.fromisoformat(value)

            else:
                original_timestamp = datetime.time.fromisoformat(value)

            converted_value = (
                original_timestamp.time()
                if isinstance(original_timestamp, datetime.datetime)
                else original_timestamp
            )

            return original_timestamp, converted_value

        except ValueError:
            return None, None

    else:
        return None, None


# -----------------------------------
# DURATION CALCULATOR
# -----------------------------------

def calculate_duration(starttime, endtime, is_time_only):

    if starttime is None or endtime is None:
        return None

    if is_time_only:

        reference_date = datetime.date(2000, 1, 1)

        start_datetime = datetime.datetime.combine(
            reference_date, starttime
        )

        end_datetime = datetime.datetime.combine(
            reference_date, endtime
        )

        if end_datetime < start_datetime:
            end_datetime += datetime.timedelta(days=1)

        duration = end_datetime - start_datetime

    else:
        duration = endtime - starttime

    return duration.total_seconds()

# -----------------------------------
# DURATION COLUMN DETECTOR
# -----------------------------------
def detect_timestamp_pairs(columns):
    pairs = {}

    for column in columns:
        name = column.lower()

        if "start" in name:
            prefix = re.sub(r"[_\s-]+", "_", name.replace("start", "")).strip("_")
            pairs.setdefault(prefix, {})["start"] = column

        elif "end" in name:
            prefix = re.sub(r"[_\s-]+", "_", name.replace("end", "")).strip("_")
            pairs.setdefault(prefix, {})["end"] = column

    return {
        prefix: pair
        for prefix, pair in pairs.items()
        if "start" in pair and "end" in pair
    }
# -----------------------------------
# BLOCK 1: FILE UPLOAD
# -----------------------------------

uploaded_file = st.file_uploader(
    "Upload your manufacturing dataset",
    type=["csv", "xlsx"]
)


# Only continue after a file is uploaded

if uploaded_file is not None:

    try:

        # -----------------------------------
        # READ CSV FILE
        # -----------------------------------

        if uploaded_file.name.lower().endswith(".csv"):

            df = pd.read_csv(uploaded_file)


        # -----------------------------------
        # READ EXCEL FILE
        # -----------------------------------

        elif uploaded_file.name.lower().endswith(".xlsx"):

            excel_file = pd.ExcelFile(uploaded_file)

            selected_sheet = st.selectbox(
                "Select worksheet",
                excel_file.sheet_names
            )

            df = pd.read_excel(
                excel_file,
                sheet_name=selected_sheet
            )

        else:
            raise ValueError("Unsupported file format.")

        # -----------------------------------
        # CHECK EMPTY DATASET
        # -----------------------------------

        if df.empty:

            st.warning("The uploaded dataset is empty.")
            st.stop()
        # -----------------------------------
        # DYNAMIC TIMESTAMP PROCESSING
        # -----------------------------------

        timestamp_pairs = detect_timestamp_pairs(df.columns)

        for prefix, pair in timestamp_pairs.items():

            start_column = pair["start"]
            end_column = pair["end"]

            start_values = df[start_column].apply(convert_timestamp)
            end_values = df[end_column].apply(convert_timestamp)

            duration_column = f"normalised_{prefix}_seconds"
            df[duration_column] = [
            calculate_duration(
                start[1],
                end[1],
                isinstance(start[1], datetime.time)
            )
            if start[1] is not None and end[1] is not None
            else None
            for start, end in zip(start_values, end_values)
        ]

        # -----------------------------------
        # BLOCK 2: SIDEBAR
        # MANUAL COLUMN MAPPING
        # -----------------------------------

        mapping_options = (
            ["-- Not Available --"]
            + list(df.columns)
        )

        st.sidebar.header("Column Mapping")


        # -----------------------------------
        # CORE PRODUCTION DATA
        # -----------------------------------

        with st.sidebar.expander(
            "Core Production Data",
            expanded=True
        ):

            production_output = st.selectbox(
                "Production Output",
                mapping_options,
                key="production_output"
            )

            available_production_time = st.selectbox(
                "Available Production Time",
                mapping_options,
                key="available_production_time"
            )

            processing_cycle_time = st.selectbox(
                "Processing / Cycle Time",
                mapping_options,
                key="processing_cycle_time"
            )


        # -----------------------------------
        # PLANNING DATA
        # -----------------------------------

        with st.sidebar.expander("Planning Data"):

            customer_demand = st.selectbox(
                "Customer Demand",
                mapping_options,
                key="customer_demand"
            )


        # -----------------------------------
        # OPERATIONAL PERFORMANCE
        # -----------------------------------

        with st.sidebar.expander("Operational Performance"):

            operating_time = st.selectbox(
                "Operating Time",
                mapping_options,
                key="operating_time"
            )

            downtime = st.selectbox(
                "Downtime",
                mapping_options,
                key="downtime"
            )

            good_units = st.selectbox(
                "Good Units",
                mapping_options,
                key="good_units"
            )

            defect_units = st.selectbox(
                "Defect Units",
                mapping_options,
                key="defect_units"
            )

            ideal_cycle_time = st.selectbox(
                "Ideal Cycle Time",
                mapping_options,
                key="ideal_cycle_time"
            )


        # -----------------------------------
        # PRODUCTION STRUCTURE
        # -----------------------------------

        with st.sidebar.expander("Production Structure"):

            resource_machine = st.selectbox(
                "Resource / Machine",
                mapping_options,
                key="resource_machine"
            )

            process_station = st.selectbox(
                "Process / Station",
                mapping_options,
                key="process_station"
            )


        # -----------------------------------
        # TIME CONFIGURATION
        # -----------------------------------

        st.sidebar.header("Time Configuration")

        available_time_unit = st.sidebar.selectbox(
            "Available Production Time Unit",
            ["Hours", "Minutes", "Seconds"]
        )

        processing_time_unit = st.sidebar.selectbox(
            "Processing / Cycle Time Unit",
            ["Hours", "Minutes", "Seconds"]
        )


        # -----------------------------------
        # DETECT TIME UNITS
        # -----------------------------------

        available_time_unit_detected = (
            detect_time_unit(available_production_time)
            if available_production_time != "-- Not Available --"
            else "Unknown"
        )

        processing_time_unit_detected = (
            detect_time_unit(processing_cycle_time)
            if processing_cycle_time != "-- Not Available --"
            else "Unknown"
        )


        # -----------------------------------
        # FINAL TIME UNITS
        # -----------------------------------

        available_time_unit_final = (
            available_time_unit_detected
            if available_time_unit_detected != "Unknown"
            else available_time_unit
        )

        processing_time_unit_final = (
            processing_time_unit_detected
            if processing_time_unit_detected != "Unknown"
            else processing_time_unit
        )


        # -----------------------------------
        # DISPLAY DETECTED UNITS
        # -----------------------------------

        col1, col2 = st.columns(2)

        with col1:
            st.write(
                "Available Time Unit:",
                available_time_unit_final
            )

        with col2:
            st.write(
                "Processing Time Unit:",
                processing_time_unit_final
            )


        # -----------------------------------
        # BLOCK 3: INPUT VALIDATION
        # -----------------------------------

        numeric_fields = {
            "Production Output": production_output,
            "Customer Demand": customer_demand,
            "Available Production Time": available_production_time,
            "Processing / Cycle Time": processing_cycle_time,
            "Operating Time": operating_time,
            "Downtime": downtime,
            "Good Units": good_units,
            "Defect Units": defect_units,
            "Ideal Cycle Time": ideal_cycle_time
        }

        validated_inputs = {}

        working_df = df.copy()

        # Convert selected numeric columns to numeric values

        for field_name, column_name in numeric_fields.items():

            if column_name == "-- Not Available --":

                validated_inputs[field_name] = None

            else:

                numeric_values = pd.to_numeric(
                    working_df[column_name],
                    errors="coerce"
                )

                valid_values = numeric_values.dropna()

                if valid_values.empty:

                    st.warning(
                        f"{field_name}: The selected column "
                        f"'{column_name}' does not contain usable "
                        f"numeric values."
                    )

                    validated_inputs[field_name] = None

                else:

                    working_df[column_name] = numeric_values

                    validated_inputs[field_name] = valid_values


        # -----------------------------------
        # TIME NORMALIZATION
        # -----------------------------------

        time_columns = {
            available_production_time: available_time_unit_final,
            operating_time: available_time_unit_final,
            processing_cycle_time: processing_time_unit_final,
            ideal_cycle_time: processing_time_unit_final
        }

        for column_name, unit in time_columns.items():

            if column_name != "-- Not Available --":

                working_df[column_name] = (
                    working_df[column_name].apply(
                        convert_to_seconds,
                        args=(unit,)
                    )
                )


        # -----------------------------------
        # DATASET INFORMATION
        # -----------------------------------

        st.write(
            f"Dataset loaded successfully: "
            f"{df.shape[0]} rows × {df.shape[1]} columns"
        )


        # -----------------------------------
        # DATA PREVIEW
        # -----------------------------------

        st.subheader("Data Preview")

        st.dataframe(
            df.head(5),
            use_container_width=True
        )


        # -----------------------------------
        # BLOCK 4A: CALCULATIONS
        # -----------------------------------

        flow_rate = None
        takt_time = None
        process_capacity = None
        cycle_time = None
        idle_time = None
        utilisation = None
        oee = None
        total_units = None


        # -----------------------------------
        # TOTAL UNITS
        # -----------------------------------

        if production_output != "-- Not Available --":

            total_units = working_df[production_output].sum()


        # -----------------------------------
        # FLOW RATE
        # -----------------------------------

        if (
            production_output != "-- Not Available --"
            and available_production_time != "-- Not Available --"
            and working_df[available_production_time].sum() > 0
        ):

            flow_rate = (
                working_df[production_output].sum()
                / working_df[available_production_time].sum()
            )


        # -----------------------------------
        # TAKT TIME
        # -----------------------------------

        if (
            available_production_time != "-- Not Available --"
            and customer_demand != "-- Not Available --"
            and working_df[available_production_time].sum() > 0
            and working_df[customer_demand].sum() > 0
        ):

            takt_time = (
                working_df[available_production_time].sum()
                / working_df[customer_demand].sum()
            )


        # -----------------------------------
        # PROCESS CAPACITY
        # -----------------------------------

        if (
            available_production_time != "-- Not Available --"
            and processing_cycle_time != "-- Not Available --"
            and working_df[processing_cycle_time].mean() > 0
        ):

            process_capacity = (
                working_df[available_production_time].sum()
                / working_df[processing_cycle_time].mean()
            )


        # -----------------------------------
        # CYCLE TIME
        # -----------------------------------

        if processing_cycle_time != "-- Not Available --":

            cycle_time = working_df[processing_cycle_time].mean()


        # -----------------------------------
        # IDLE TIME
        # -----------------------------------

        if (
            available_production_time != "-- Not Available --"
            and operating_time != "-- Not Available --"
        ):

            idle_time = (
                working_df[available_production_time].sum()
                - working_df[operating_time].sum()
            )


        # -----------------------------------
        # UTILISATION
        # -----------------------------------

        if (
            available_production_time != "-- Not Available --"
            and operating_time != "-- Not Available --"
            and working_df[available_production_time].sum() > 0
        ):

            utilisation = (
                working_df[operating_time].sum()
                / working_df[available_production_time].sum()
            ) * 100


        # -----------------------------------
        # OEE - DIRECT FORMULA
        # -----------------------------------

        if (
            good_units != "-- Not Available --"
            and ideal_cycle_time != "-- Not Available --"
            and available_production_time != "-- Not Available --"
            and working_df[available_production_time].sum() > 0
        ):

            oee = (
                working_df[good_units].sum()
                * working_df[ideal_cycle_time].mean()
                / working_df[available_production_time].sum()
            )


        # -----------------------------------
        # BLOCK 4B: KPI DISPLAY VALUES
        # -----------------------------------

        flow_rate_display = (
            f"{flow_rate * 3600:.2f} units/hour"
            if flow_rate is not None
            else "Not Available"
        )

        capacity_display = (
            f"{process_capacity:.2f} units"
            if process_capacity is not None
            else "Not Available"
        )

        cycle_time_display = format_time(cycle_time)
        takt_time_display = format_time(takt_time)
        idle_time_display = format_time(idle_time)

        utilisation_display = (
            f"{utilisation:.2f}%"
            if utilisation is not None
            else "Not Available"
        )

        oee_display = (
            f"{oee * 100:.2f}%"
            if oee is not None
            else "Not Available"
        )

        total_units_display = (
            f"{total_units:,.0f}"
            if total_units is not None
            else "Not Available"
        )


        # -----------------------------------
        # BLOCK 4C: DASHBOARD DISPLAY
        # -----------------------------------

        row1 = st.columns(3)

        row1[0].metric("Total Units", total_units_display)
        row1[1].metric("Flow Rate", flow_rate_display)
        row1[2].metric("Process Capacity", capacity_display)


        row2 = st.columns(3)

        row2[0].metric("Cycle Time", cycle_time_display)
        row2[1].metric("Takt Time", takt_time_display)
        row2[2].metric("Idle Time", idle_time_display)


        row3 = st.columns(3)

        row3[0].metric("Bottleneck", "Not Available")
        row3[1].metric("Utilisation", utilisation_display)
        row3[2].metric("OEE", oee_display)


    # -----------------------------------
    # ERROR HANDLING
    # -----------------------------------

    except Exception as e:

        st.error(
            f"Unable to process the uploaded file: {e}"
        )
