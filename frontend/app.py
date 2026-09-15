import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Receipt Extractor",
    page_icon="🧾",
    layout="wide",
)


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>

        .section-title {
            font-size: 1.35rem;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        /* Hero Card */

        .hero-card {
            position: relative;
            max-width: 850px;
            margin: 1rem auto 2rem auto;
            padding: 1rem 2rem;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            background: linear-gradient(
                135deg,
                rgba(30, 30, 40, 0.95),
                rgba(15, 15, 22, 0.98)
            );
            overflow: hidden;
            box-shadow: 0 15px 45px rgba(0, 0, 0, 0.35);
        }

        .hero-card::before {
            content: "";
            position: absolute;
            top: 0;
            left: -100%;
            width: 60%;
            height: 2px;
            background: linear-gradient(
                90deg,
                transparent,
                #60a5fa,
                #a78bfa,
                transparent
            );
            animation: scan 3s ease-in-out infinite;
        }

        .hero-card::after {
            content: "";
            position: absolute;
            width: 250px;
            height: 250px;
            top: -120px;
            right: -80px;
            border-radius: 50%;
            background: rgba(99, 102, 241, 0.12);
            filter: blur(50px);
            animation: pulseGlow 4s ease-in-out infinite;
        }

        .hero-icon {
            font-size: 3rem;
            margin-bottom: 0.75rem;
            animation: floatIcon 3s ease-in-out infinite;
        }

        .hero-title {
            position: relative;
            z-index: 1;
            font-size: 3rem;
            font-weight: 750;
            margin: 0;
            letter-spacing: -1px;
        }

        .hero-subtitle {
            position: relative;
            z-index: 1;
            margin-top: 0.75rem;
            color: #9ca3af;
            font-size: 1.1rem;
        }

        .hero-badge {
            position: relative;
            z-index: 1;
            display: inline-block;
            margin-top: 1.25rem;
            padding: 0.4rem 0.9rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            color: #c4b5fd;
            border: 1px solid rgba(167, 139, 250, 0.3);
            background: rgba(139, 92, 246, 0.08);
        }

        @keyframes scan {
            0% {
                left: -60%;
            }

            50% {
                left: 100%;
            }

            100% {
                left: 100%;
            }
        }

        @keyframes pulseGlow {
            0%, 100% {
                transform: scale(1);
                opacity: 0.5;
            }

            50% {
                transform: scale(1.25);
                opacity: 0.9;
            }
        }

        @keyframes floatIcon {
            0%, 100% {
                transform: translateY(0);
            }

            50% {
                transform: translateY(-6px);
            }
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Receipt Extractor</div>
        <div class="hero-subtitle">
            AI-powered receipt extraction and expense capture
        </div>
        <div class="hero-badge">
            AI • OCR • Structured Data
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Upload
# --------------------------------------------------

st.markdown(
    '<div class="section-title">Upload Receipt</div>',
    unsafe_allow_html=True,
)

# Session state for resetting the uploader
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

uploaded_file = st.file_uploader(
    "Upload a receipt image or PDF",
    type=["png", "jpg", "jpeg", "pdf"],
    help="Supported formats: PNG, JPG, JPEG, PDF",
    key=f"receipt_uploader_{st.session_state.uploader_key}",
)


if uploaded_file:

    st.caption(
        f"Selected file: **{uploaded_file.name}**"
    )

    col_process, col_clear = st.columns([1, 1])

    with col_process:
        process_button = st.button(
            "Process Receipt",
            type="primary",
            use_container_width=True,
        )

    with col_clear:
        clear_button = st.button(
            "Clear",
            use_container_width=True,
        )

    if clear_button:
        st.session_state.uploader_key += 1
        st.rerun()

    if process_button:

        with st.spinner(
            "Extracting receipt information..."
        ):
            try:
                response = requests.post(
                    f"{API_URL}/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    },
                    timeout=120,
                )

                if response.status_code == 200:

                    result = response.json()

                    st.success(
                        "Receipt processed successfully."
                    )

                    # ----------------------------------
                    # Summary metrics
                    # ----------------------------------

                    st.markdown(
                        '<div class="section-title">'
                        'Extracted Information'
                        '</div>',
                        unsafe_allow_html=True,
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Merchant",
                            result.get(
                                "merchant_name"
                            ) or "Unknown",
                        )

                    with col2:
                        st.metric(
                            "Date",
                            result.get(
                                "date"
                            ) or "Unknown",
                        )

                    with col3:
                        total = result.get(
                            "total_amount"
                        )

                        st.metric(
                            "Total",
                            (
                                f"${total:,.2f}"
                                if total is not None
                                else "Unknown"
                            ),
                        )

                    # ----------------------------------
                    # Line items
                    # ----------------------------------

                    line_items = result.get(
                        "line_items",
                        [],
                    )

                    if line_items:

                        st.markdown(
                            '<div class="section-title">'
                            'Line Items'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        st.dataframe(
                            [
                                {
                                    "Item": item[
                                        "item_name"
                                    ],
                                    "Price": (
                                        f"${item['price']:,.2f}"
                                    ),
                                }
                                for item in line_items
                            ],
                            use_container_width=True,
                            hide_index=True,
                        )

                    # ----------------------------------
                    # Tax / Tip
                    # ----------------------------------

                    tax = result.get("tax")
                    tip = result.get("tip")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Tax",
                            (
                                f"${tax:,.2f}"
                                if tax is not None
                                else "N/A"
                            ),
                        )

                    with col2:
                        st.metric(
                            "Tip",
                            (
                                f"${tip:,.2f}"
                                if tip is not None
                                else "N/A"
                            ),
                        )

                    # ----------------------------------
                    # Raw structured result
                    # ----------------------------------

                    with st.expander(
                        "View extracted JSON"
                    ):
                        st.json(result)

                else:

                    try:
                        error = response.json()
                    except Exception:
                        error = response.text

                    st.error(
                        f"Processing failed: {error}"
                    )

            except requests.exceptions.Timeout:

                st.error(
                    "The extraction request timed out. "
                    "Please try again."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the backend. "
                    "Make sure FastAPI is running."
                )

            except Exception as exc:

                st.error(
                    f"Unexpected error: {exc}"
                )


# --------------------------------------------------
# Stored receipts
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">'
    'Previously Extracted Receipts'
    '</div>',
    unsafe_allow_html=True,
)


try:

    response = requests.get(
        f"{API_URL}/receipts",
        timeout=10,
    )

    if response.status_code == 200:

        receipts = response.json()

        if receipts:

            table_data = [
                {
                    "ID": receipt["id"],
                    "Filename": receipt["filename"],
                    "Merchant": (
                        receipt["merchant_name"]
                        or "Unknown"
                    ),
                    "Date": (
                        receipt["date"]
                        or "Unknown"
                    ),
                    "Total": (
                        f"${receipt['total_amount']:,.2f}"
                        if receipt["total_amount"]
                        is not None
                        else "Unknown"
                    ),
                }
                for receipt in receipts
            ]

            st.dataframe(
                table_data,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No receipts have been processed yet."
            )

    else:

        st.warning(
            "Could not load stored receipts."
        )


except requests.exceptions.ConnectionError:

    st.warning(
        "Backend is not available. "
        "Start FastAPI to view stored receipts."
    )

except Exception as exc:

    st.warning(
        f"Could not load receipts: {exc}"
    )

# --------------------------------------------------
# Expense Report
# --------------------------------------------------

st.divider()

st.markdown(
    '<div class="section-title">'
    'Expense Report'
    '</div>',
    unsafe_allow_html=True,
)

st.write(
    "Generate an expense summary from all stored receipts "
    "and send the Excel report by email."
)

recipient_email = st.text_input(
    "Recipient Email",
    placeholder="example@gmail.com",
    help="Enter the email address that should receive the expense report.",
)

if st.button(
    "Generate & Send Expense Report",
    type="primary",
    use_container_width=True,
):
    if not recipient_email.strip():
        st.error("Please enter a recipient email address.")
    else:
        with st.spinner(
            "Generating report and sending email..."
        ):
            try:
                response = requests.post(
                    f"{API_URL}/expense-report",
                    json={
                        "recipient_email": recipient_email.strip(),
                    },
                    timeout=60,
                )

                if response.status_code == 200:
                    report = response.json()

                    st.success(
                        "Expense report generated and sent successfully."
                    )

                    # ----------------------------------
                    # Report summary
                    # ----------------------------------

                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric(
                            "Receipts Processed",
                            report.get("receipt_count", 0),
                        )

                    with col2:
                        total = report.get("total_amount")

                        st.metric(
                            "Total Expenses",
                            (
                                f"${total:,.2f}"
                                if total is not None
                                else "N/A"
                            ),
                        )

                    # ----------------------------------
                    # Category totals
                    # ----------------------------------

                    category_totals = report.get(
                        "category_totals",
                        {},
                    )

                    if category_totals:
                        st.markdown(
                            '<div class="section-title">'
                            'Category Totals'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        category_data = [
                            {
                                "Category": category,
                                "Total": f"${amount:,.2f}",
                            }
                            for category, amount
                            in category_totals.items()
                        ]

                        st.dataframe(
                            category_data,
                            use_container_width=True,
                            hide_index=True,
                        )

                    # ----------------------------------
                    # Email status
                    # ----------------------------------

                    email_result = report.get(
                        "email_result"
                    )

                    if email_result:
                        st.markdown(
                            '<div class="section-title">'
                            'Email Delivery'
                            '</div>',
                            unsafe_allow_html=True,
                        )

                        if email_result.get("sent"):
                            st.success(
                                "Report sent successfully to "
                                f"{report.get('recipient_email')}."
                            )
                        else:
                            st.warning(
                                email_result.get(
                                    "message",
                                    "Email was not sent.",
                                )
                            )

                    # ----------------------------------
                    # Download report
                    # ----------------------------------

                    download_response = requests.get(
                        f"{API_URL}/expense-report/download",
                        timeout=30,
                    )

                    if download_response.status_code == 200:
                        st.download_button(
                            label="Download Expense Report",
                            data=download_response.content,
                            file_name="expense_report.xlsx",
                            mime=(
                                "application/vnd.openxmlformats-officedocument."
                                "spreadsheetml.sheet"
                            ),
                            use_container_width=True,
                        )
                    else:
                        st.warning(
                            "Report was generated, but the download "
                            "file could not be retrieved."
                        )

                else:
                    try:
                        error = response.json()
                    except Exception:
                        error = response.text

                    st.error(
                        f"Report generation failed: {error}"
                    )

            except requests.exceptions.Timeout:
                st.error(
                    "The report generation request timed out."
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to the backend. "
                    "Make sure FastAPI is running."
                )

            except Exception as exc:
                st.error(
                    f"Unexpected error: {exc}"
                )